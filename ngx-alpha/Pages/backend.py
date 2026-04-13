from langgraph.graph import StateGraph, END

from .graph.nodes import call_model, call_tools, route_to_tools
from .graph.state import AgentState


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("agent", call_model)
    workflow.add_node("tools", call_tools)

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        route_to_tools,
        {
            "tools": "tools",
            "__end__": END
        }
    )

    workflow.add_edge("tools", "agent")

    return workflow.compile()


class PythonChatbot:
    def __init__(self):
        self.graph = build_graph()

    def run(self, state):
        return self.graph.invoke(state)
