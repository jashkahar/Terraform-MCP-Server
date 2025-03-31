"""Utility functions for Terraform operations."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple
import shutil

def validate_workspace(workspace_path: str) -> bool:
    """
    Validate that the given path is a valid Terraform workspace.
    
    Args:
        workspace_path: Path to the Terraform workspace
        
    Returns:
        bool: True if workspace is valid, False otherwise
    """
    
    workspace = Path(workspace_path)
    print(f"Validating workspace path: {workspace}", file=sys.stderr)
    
    # Check if directory exists
    if not workspace.exists():
        print(f"Workspace directory does not exist: {workspace}", file=sys.stderr)
        return False
        
    # Check if it's a directory
    if not workspace.is_dir():
        print(f"Workspace path is not a directory: {workspace}", file=sys.stderr)
        return False
    
    # Check for Terraform files
    tf_files = list(workspace.glob('*.tf'))
    print(f"Found {len(tf_files)} .tf files in workspace", file=sys.stderr)
    
    # If it's not a Terraform workspace but a file was specified, check the parent directory
    if len(tf_files) == 0 and workspace.parent.exists():
        parent_tf_files = list(workspace.parent.glob('*.tf'))
        if len(parent_tf_files) > 0:
            print(f"Found {len(parent_tf_files)} .tf files in parent directory", file=sys.stderr)
            return True
            
    return len(tf_files) > 0

def format_output(stdout: str, stderr: str) -> str:
    """
    Format command output for user display.
    
    Args:
        stdout: Standard output from command
        stderr: Standard error from command
        
    Returns:
        str: Formatted output string
    """
    output = []
    if stdout:
        output.append(stdout.strip())
    if stderr:
        output.append(f"Errors/Warnings:\n{stderr.strip()}")
    return "\n\n".join(output) if output else "No output"

def check_tool_installed(tool_name: str, env_vars: Optional[dict] = None) -> Tuple[bool, str]:
    """
    Check if a required tool is installed and available in PATH.
    
    Args:
        tool_name: Name of the tool to check
        env_vars: Optional environment variables to use
        
    Returns:
        Tuple[bool, str]: (is_installed, error_message)
    """
    # First, try using shutil.which which is more reliable cross-platform
    tool_path = shutil.which(tool_name)
    print(f"Checking for {tool_name} using shutil.which: {tool_path}", file=sys.stderr)
    
    if tool_path:
        return True, ""
        
    # Fall back to subprocess method if shutil.which fails
    try:
        print(f"Falling back to subprocess to check for {tool_name}", file=sys.stderr)
        # On Windows, use 'where' command instead of direct execution for binaries
        if os.name == 'nt':  # Windows
            check_cmd = ["where.exe", tool_name]
        else:  # Unix/Linux
            check_cmd = [tool_name, "--version"]
            
        result = subprocess.run(
            check_cmd,
            check=True,
            capture_output=True,
            text=True,
            env=env_vars or os.environ
        )
        print(f"Tool check succeeded: {result.stdout.strip()}", file=sys.stderr)
        return True, ""
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        error_msg = f"{tool_name} is not installed or not found in PATH: {str(e)}"
        print(error_msg, file=sys.stderr)
        return False, error_msg 