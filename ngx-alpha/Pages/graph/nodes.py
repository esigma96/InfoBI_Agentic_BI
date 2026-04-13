from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate

from typing import Literal
import os

from .tools import complete_python_task
from .state import AgentState

# LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

tools = [complete_python_task]
model = llm.bind_tools(tools)

# Load prompt
with open(os.path.join(os.path.dirname(__file__), "../prompts/main_prompt.md")) as f:
    prompt = f.read()

chat_template = ChatPromptTemplate.from_messages([
    ("system", prompt),
    ("placeholder", "{messages}")
])

model = chat_template | model


# -------------------------
# Helper: Data Summary
# -------------------------
def create_data_summary(state: AgentState) -> str:
    summary = ""

    for d in state["input_data"]:
        summary += f"\nVariable: {d.variable_name}\n"
        summary += f"Description: {d.data_description}\n"

    return summary


# -------------------------
# Node: LLM Call
# -------------------------
def call_model(state: AgentState):
    summary = create_data_summary(state)

    data_msg = HumanMessage(
        content=f"The following data is available:\n{summary}"
    )

    state["messages"] = [data_msg] + state["messages"]

    response = model.invoke(state)

    return {
        "messages": [response],
        "intermediate_outputs": [data_msg.content]
    }


# -------------------------
# Node: Tool Execution (NEW)
# -------------------------
def call_tools(state: AgentState):
    last_message = state["messages"][-1]

    if not isinstance(last_message, AIMessage) or not hasattr(last_message, "tool_calls"):
        return {}

    tool_messages = []
    updates = {}

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = {
            **tool_call["args"],
            "graph_state": state
        }

        # Find tool
        tool = next(t for t in tools if t.name == tool_name)

        # Execute
        result, state_update = tool.invoke(tool_args)

        tool_messages.append(
            ToolMessage(
                content=str(result),
                name=tool_name,
                tool_call_id=tool_call["id"]
            )
        )

        updates.update(state_update)

    updates["messages"] = tool_messages

    return updates


# -------------------------
# Router
# -------------------------
def route_to_tools(state: AgentState) -> Literal["tools", "__end__"]:
    last = state["messages"][-1]

    if hasattr(last, "tool_calls") and len(last.tool_calls) > 0:
        return "tools"

    return "__end__"
