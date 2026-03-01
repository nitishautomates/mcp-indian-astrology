"""Divine API - Indian Astrology MCP Server."""

from .server import mcp


def main():
    """Entry point for the MCP server."""
    mcp.run(transport="stdio")
