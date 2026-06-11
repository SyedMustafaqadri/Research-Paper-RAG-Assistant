from langgraph.graph import StateGraph, START, END
from graph.state import AgentState
from graph.nodes import retrieve_node, generate_node

# Initialize graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate", generate_node)

# Add edges
workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

# Compile the workflow
graph_app = workflow.compile()
