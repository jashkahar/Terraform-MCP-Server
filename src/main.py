"""
Terraform MCP Server

An MCP server that exposes Terraform infrastructure-as-code operations through natural language.
Allows LLMs to execute Terraform commands and retrieve information about infrastructure
without requiring the user to know specific command syntax.
"""

import os
import sys
from typing import Optional

# Try both import paths for FastMCP to handle different versions
try:
    # Latest version import
    from mcp.server.fastmcp import FastMCP, Context
    print("Using direct fastmcp import", file=sys.stderr)
except ImportError:
    try:
        # Alternative import path
        from mcp.server.fastmcp import FastMCP, Context
        print("Using mcp.server.fastmcp import", file=sys.stderr)
    except ImportError:
        print("ERROR: Neither fastmcp nor mcp.server.fastmcp could be imported.", file=sys.stderr)
        print("Please ensure fastmcp is installed: pip install fastmcp", file=sys.stderr)
        sys.exit(1)

# Fix imports to use proper relative paths based on how the script is run
try:
    # First try relative import (when running as module)
    from src.handlers import TerraformHandler
    from src.config import PROJECT_ROOT, TERRAFORM_WORKSPACE, env_vars
    print("Using src.handlers import path", file=sys.stderr)
except ImportError:
    try:
        # Then try direct import (when running from src directory)
        from handlers import TerraformHandler
        from config import PROJECT_ROOT, TERRAFORM_WORKSPACE, env_vars
        print("Using direct handlers import path", file=sys.stderr)
    except ImportError:
        print("ERROR: Could not import handlers module. Check your Python path.", file=sys.stderr)
        sys.exit(1)

# Create the MCP server
mcp = FastMCP("Terraform Assistant")

# Initialize the Terraform handler
try:
    print(f"Trying to initialize TerraformHandler with workspace: {TERRAFORM_WORKSPACE}", file=sys.stderr)
    terraform = TerraformHandler(TERRAFORM_WORKSPACE, env_vars)
    print("Successfully initialized TerraformHandler", file=sys.stderr)
except Exception as e:
    print(f"Error initializing TerraformHandler: {e}", file=sys.stderr)
    sys.exit(1)

@mcp.tool()
def test(query: str) -> str:
    """Test if this server has access to the project_dir by listing its contents."""
    try:
        if os.path.exists(PROJECT_ROOT):
            return f"Server has access to the project directory at: {PROJECT_ROOT}"
        return f"Project directory not found or not set: {PROJECT_ROOT}"
    except Exception as e:
        return f"Error accessing project directory: {str(e)}"

@mcp.tool()
def init_terraform(query: str) -> str:
    """Initialize the Terraform project."""
    return terraform.init()

@mcp.tool()
def handle_terraform_query(query: str) -> str:
    """Process a natural language Terraform query and execute the appropriate command."""
    query_normalized = query.lower().strip()
    
    # Execution Plan
    if any(keyword in query_normalized for keyword in ["plan", "what will change", "execution plan", "visualize"]):
        return terraform.plan()
    
    # State Inspection
    elif any(keyword in query_normalized for keyword in ["state list", "resources exist", "current state", "list all resources"]):
        return terraform.state_list()
    
    # Apply Configuration
    elif any(keyword in query_normalized for keyword in ["apply", "deploy", "create resources"]):
        return terraform.apply(auto_approve=True)
    
    # Destroy Infrastructure
    elif any(keyword in query_normalized for keyword in ["destroy", "tear down", "remove resources"]):
        return terraform.destroy(auto_approve=True)
    
    # Show Configuration/State
    elif any(keyword in query_normalized for keyword in ["show", "explain", "documentation"]):
        return terraform.show()
    
    return "I'm not sure what Terraform operation you want to perform. Please try rephrasing your request."

if __name__ == "__main__":
    try:
        print("Starting Terraform MCP Server...", file=sys.stderr)
        mcp.run(transport="stdio")
    except Exception as e:
        print("Fatal error in MCP server:", e, file=sys.stderr)
        sys.exit(1)