import asyncio
from mcp import stdio_client
from mcp.client.session import ClientSession

from .config import SERVER_PARAMS
from .graph import create_graph


async def main():
    """
    Main entry point for the MCP client.
    Connects to the MCP server and runs the interactive assistant.
    """
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            agent = await create_graph(session)
            print("Wikipedia MCP agent is ready.")

            while True:
                user_input = input("\nYou: ").strip()
                if user_input.lower() in {"exit", "quit", "q"}:
                    break

                try:
                    response = await agent.ainvoke(
                        {"messages": [("user", user_input)]},
                        config={"configurable": {"thread_id": "wiki-session"}},
                    )
                    print("AI:", response["messages"][-1].content)
                except Exception as e:
                    print("Error:", e)


if __name__ == "__main__":
    asyncio.run(main())
