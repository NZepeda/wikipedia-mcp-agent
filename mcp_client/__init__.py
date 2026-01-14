"""
MCP Client Package

A LangGraph-based client for interacting with the Wikipedia MCP server.
"""

from .client import main
from shared import create_graph, State

__all__ = ["main", "create_graph", "State"]
