from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import tools_condition, ToolNode

from .models import State
from .config import OPENAI_API_KEY, MODEL_NAME, TEMPERATURE, SYSTEM_PROMPT


async def create_graph(session):
    """
    Creates a LangGraph workflow with MCP tools integration.

    Args:
        session: MCP session for loading tools

    Returns:
        Compiled graph with memory checkpointer
    """
    # Load tools from MCP server
    tools = await load_mcp_tools(session)

    # LLM configuration
    llm = ChatOpenAI(
        model=MODEL_NAME, temperature=TEMPERATURE, openai_api_key=OPENAI_API_KEY
    )
    llm_with_tools = llm.bind_tools(tools)

    prompt_template = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), MessagesPlaceholder("messages")]
    )

    chat_llm = prompt_template | llm_with_tools

    def chat_node(state: State) -> State:
        """Process user messages and generate responses."""
        state["messages"] = chat_llm.invoke({"messages": state["messages"]})
        return state

    graph = StateGraph(State)
    graph.add_node("chat_node", chat_node)
    graph.add_node("tool_node", ToolNode(tools=tools))
    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges(
        "chat_node", tools_condition, {"tools": "tool_node", "__end__": END}
    )
    graph.add_edge("tool_node", "chat_node")

    return graph.compile(checkpointer=MemorySaver())
