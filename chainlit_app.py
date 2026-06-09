import time
import chainlit as cl
from langchain_core.runnables import RunnableConfig

from core.config import Config
from core.logger import logger
from database.connection import init_db, get_db
from database.models import DocumentChunk
from services.document_service import DocumentService
from services.chat_service import ChatService
from graph.workflow import graph_app
from graph.nodes import generate_summary

@cl.on_chat_start
async def on_chat_start():
    """
    Triggers when a new chat session starts.
    Initializes database and guides the user to upload a PDF.
    """
    logger.info("New Chainlit session started.")
    
    # 1. Initialize relational database tables
    try:
        init_db()
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        await cl.Message(content="⚠️ Database connection error. Please check your configurations.").send()
        return

    # 2. Check if Gemini API key is configured
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Config validation failed: {e}")
        await cl.Message(
            content="❌ **Configuration Error**: `GOOGLE_API_KEY` is not set in the `.env` file.\n\nPlease define it and restart the application."
        ).send()
        return

    # 3. Create a relational chat record
    chat_id = ChatService.get_or_create_chat()
    cl.user_session.set("chat_id", chat_id)

    # 4. Ask the user to upload a PDF
    files = None
    while files is None:
        files = await cl.AskFileMessage(
            content="Welcome to the **Research Paper RAG Assistant**! 📚\n\nPlease upload one or more research papers (PDF format) to begin your analysis.",
            accept=["application/pdf"],
            max_size_mb=20,
            timeout=3600
        ).send()

    # Process the uploaded file
    file = files[0]
    logger.info(f"User uploaded file: {file.name}")
    
    status_msg = cl.Message(content=f"Processing **{file.name}**... Extracting text and generating embeddings.")
    await status_msg.send()

    try:
        # Save file and ingest
        doc_id = await cl.make_async(DocumentService.register_and_ingest)(file.name, file.path)
        cl.user_session.set("document_id", doc_id)
        
        status_msg.content = f"✅ Successfully processed and indexed **{file.name}**!"
        # Add Action Button for Summary
        status_msg.actions = [
            cl.Action(name="summarize", payload={"doc_id": doc_id}, label="✨ Summarize Paper")
        ]
        await status_msg.update()
        
    except Exception as e:
        logger.error(f"Failed to process file: {e}")
        status_msg.content = f"❌ **Error processing file**: {str(e)}"
        await status_msg.update()


@cl.action_callback("summarize")
async def on_summarize(action: cl.Action):
    """
    Callback triggered when the user clicks the "Summarize Paper" button.
    Generates a structured research paper summary.
    """
    doc_id = action.payload.get("doc_id")
    await action.remove()  # Remove button to prevent double execution
    
    status_msg = cl.Message(content="Generating structured summary (Overview, Methodology, Results, Limitations)...")
    await status_msg.send()
    
    try:
        # Retrieve chunk text from DB
        with get_db() as db:
            chunks = db.query(DocumentChunk).filter_by(document_id=doc_id).all()
            chunks_data = [
                {
                    "page_number": c.page_number,
                    "chunk_index": c.chunk_index,
                    "chunk_text": c.chunk_text
                }
                for c in chunks
            ]
            
        if not chunks_data:
            raise ValueError("No chunks found in database for this document.")

        # Generate summary
        summary = await generate_summary(chunks_data, "Summary")
        
        # Convert CL output format to plain text if needed
        if isinstance(summary, list):
            # Extracts the text from blocks like [{'type': 'text', 'text': '...'}]
            summary = "\n".join(
                item.get("text", "") for item in summary if item.get("type") == "text"
            )

        # Save to chat history
        chat_id = cl.user_session.get("chat_id")
        ChatService.save_message(chat_id, "assistant", summary)
        
        # Display summary
        status_msg.content = f"### 📝 Research Paper Summary\n\n{summary}"
        await status_msg.update()
        
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        status_msg.content = f"❌ **Failed to generate summary**: {str(e)}"
        await status_msg.update()


@cl.on_message
async def on_message(message: cl.Message):
    """
    Triggers when the user sends a message. Runs the LangGraph agent workflow.
    """
    chat_id = cl.user_session.get("chat_id")
    document_id = cl.user_session.get("document_id")

    if not document_id:
        await cl.Message(content="⚠️ Please upload and index a PDF document before asking questions.").send()
        return

    # Load recent chat history
    history = ChatService.get_chat_history(chat_id)

    # Save user message to database
    ChatService.save_message(chat_id, "user", message.content)

    # Setup loading step
    cb = cl.LangchainCallbackHandler()
    config = RunnableConfig(callbacks=[cb])

    start_time = time.time()
    try:
        # Prepare graph state inputs
        state_input = {
            "question": message.content,
            "chat_history": history,
            "document_id": document_id
        }

        # Run LangGraph workflow
        result = await graph_app.ainvoke(state_input, config=config)
        response_time = time.time() - start_time

        answer = result.get("answer", "")
        sources = result.get("sources", [])

        # Format source citations cleanly
        source_section = ""
        if sources:
            source_section = "\n\n**Sources:**"
            for src in sources:
                filename = src.get("filename", "Paper")
                page = src.get("page", "?")
                source_section += f"\n- *{filename}*, Page {page}"

        final_content = f"{answer}{source_section}"

        # Send response to user
        await cl.Message(content=final_content).send()

        # Save assistant message to database
        await cl.make_async(ChatService.save_message)(chat_id, "assistant", final_content)

        # Log retrieval metadata (TICKET-019)
        await cl.make_async(ChatService.log_retrieval)(
            question=message.content,
            retrieved_chunks=result.get("retrieved_docs", []),
            response_time=response_time
        )

    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        await cl.Message(content=f"❌ **An error occurred while generating answer**: {str(e)}").send()
