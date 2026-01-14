from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mcp import stdio_client
from mcp.client.session import ClientSession
from langchain_core.messages import HumanMessage

from shared import SERVER_PARAMS, create_graph

# Global variables to store MCP session and agent
mcp_session: Optional[ClientSession] = None
agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the lifecycle of the MCP client connection.
    Opens connection on startup and closes on shutdown.
    """
    global mcp_session, agent

    print("Starting MCP server connection...")

    async with stdio_client(SERVER_PARAMS) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            mcp_session = session
            agent = await create_graph(session)

            print("MCP server connection established!")

            yield

            print("Shutting down MCP server connection...")


# Create FastAPI app
app = FastAPI(
    title="Wikipedia MCP Agent API",
    description="REST API wrapper for Wikipedia MCP agent",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class ChatRequest(BaseModel):
    """Request body for the /chat endpoint."""

    message: str
    thread_id: str = "wiki-session"


class ChatResponse(BaseModel):
    """Response body for the /chat and /prompt endpoints."""

    response: str
    error: Optional[str] = None


class PromptRequest(BaseModel):
    """Request body for the /prompt endpoint."""

    name: str
    arguments: dict = {}
    thread_id: str = "wiki-session"


class ResourceRequest(BaseModel):
    """Request body for the /resource endpoint."""

    name: str


# Health check endpoint
@app.get("/")
async def root():
    """
    The root route.
    Useful for ensuring that the server is up and running.
    """
    return {
        "message": "Wikipedia MCP Agent API",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Check if the MCP server connection is healthy."""
    if mcp_session is None or agent is None:
        raise HTTPException(status_code=503, detail="MCP server not connected")
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the Wikipedia agent and get a response.
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        response = await agent.ainvoke(
            {"messages": [HumanMessage(content=request.message)]},
            config={"configurable": {"thread_id": request.thread_id}},
        )

        return ChatResponse(response=response["messages"][-1].content)
    except Exception as e:
        return ChatResponse(response="", error=str(e))


@app.get("/resources")
async def list_resources():
    """
    List all available resources from the MCP server.
    """
    if mcp_session is None:
        raise HTTPException(status_code=503, detail="MCP server not connected")

    try:
        response = await mcp_session.list_resources()

        resources = []
        if response and response.resources:
            for r in response.resources:
                resources.append(
                    {
                        "name": r.name,
                        "uri": r.uri,
                        "description": getattr(r, "description", None),
                    }
                )

        return {"resources": resources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/resource")
async def get_resource(request: ResourceRequest):
    """
    Get the content of a specific resource.
    """
    if mcp_session is None:
        raise HTTPException(status_code=503, detail="MCP server not connected")

    try:
        # Get all resources first
        response = await mcp_session.list_resources()
        resources = response.resources

        # Find matching resource
        match = next((r for r in resources if r.name == request.name), None)
        if not match:
            raise HTTPException(
                status_code=404, detail=f"Resource '{request.name}' not found"
            )

        # Fetch resource content
        result = await mcp_session.read_resource(match.uri)

        content = []
        for item in result.contents:
            if hasattr(item, "text"):
                content.append(item.text)

        return {"name": request.name, "content": content}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/prompts")
async def list_prompts():
    """
    List all available prompts from the MCP server.
    """
    if mcp_session is None:
        raise HTTPException(status_code=503, detail="MCP server not connected")

    try:
        prompt_response = await mcp_session.list_prompts()

        prompts = []
        if prompt_response and prompt_response.prompts:
            for p in prompt_response.prompts:
                args = []
                if p.arguments:
                    args = [
                        {
                            "name": arg.name,
                            "description": getattr(arg, "description", None),
                        }
                        for arg in p.arguments
                    ]

                prompts.append(
                    {
                        "name": p.name,
                        "description": getattr(p, "description", None),
                        "arguments": args,
                    }
                )

        return {"prompts": prompts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/prompt", response_model=ChatResponse)
async def execute_prompt(request: PromptRequest):
    """
    Execute a specific prompt with arguments.
    """
    if mcp_session is None or agent is None:
        raise HTTPException(status_code=503, detail="MCP server not connected")

    try:
        # Get the prompt
        response = await mcp_session.get_prompt(request.name, request.arguments)
        prompt_text = response.messages[0].content.text

        # Execute via agent
        agent_response = await agent.ainvoke(
            {"messages": [HumanMessage(content=prompt_text)]},
            config={"configurable": {"thread_id": request.thread_id}},
        )

        return ChatResponse(response=agent_response["messages"][-1].content)
    except Exception as e:
        return ChatResponse(response="", error=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
