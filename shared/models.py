from typing import Annotated, List
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages


class State(TypedDict):
    """LangGraph state definition for conversation flow."""
    messages: Annotated[List[AnyMessage], add_messages]
