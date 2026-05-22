"""MCP server that exposes NutriRef's endpoints as tools for AI agents.

Run with:
    python -m mcp_server

Required env vars:
    PAYER_PRIVATE_KEY  -- a funded Base mainnet wallet's private key (the agent operator pays from this wallet)
    NUTRIREF_BASE_URL  -- defaults to https://nutriref.xyz
"""

from .server import main

__all__ = ["main"]
