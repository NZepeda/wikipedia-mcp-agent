import os
from dotenv import load_dotenv
from mcp import StdioServerParameters

# Load environment variables from .env file
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4"
TEMPERATURE = 0

# MCP Server Parameters
SERVER_PARAMS = StdioServerParameters(
    command="python",
    args=["mcp_server.py"]
)

# System Prompt
SYSTEM_PROMPT = "You are a helpful assistant that uses tools to search Wikipedia."
