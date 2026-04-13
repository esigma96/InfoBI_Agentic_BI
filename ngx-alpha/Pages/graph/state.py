from typing import TypedDict, List, Any

class AgentState(TypedDict):
    messages: List[Any]
    input_data: List[Any]
    current_variables: dict
    intermediate_outputs: List[Any]
