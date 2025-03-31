"""Core Terraform operation handler."""

import os
import subprocess
import sys
from pathlib import Path
import shutil
from typing import Optional, List, Dict, Any

from .utils import validate_workspace, format_output, check_tool_installed

class TerraformHandler:
    """Handles execution of Terraform commands and operations."""
    
    def __init__(self, workspace_path: str, env_vars: Optional[Dict[str, str]] = None):
        """
        Initialize the Terraform handler.
        
        Args:
            workspace_path: Path to the Terraform workspace
            env_vars: Optional environment variables to use
        """
        self.env_vars = env_vars or os.environ.copy()
        
        # Validate the workspace path first
        self.workspace_path = Path(workspace_path)
        if not validate_workspace(workspace_path):
            raise ValueError(f"Invalid Terraform workspace: {workspace_path}")
        
        # Check if Terraform is installed
        self.terraform_path = shutil.which("terraform")
        if not self.terraform_path:
            # Try specific paths common on Windows
            common_paths = [
                Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "terraform" / "terraform.exe",
                Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "terraform" / "terraform.exe",
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "terraform" / "terraform.exe"
            ]
            
            for path in common_paths:
                if path.exists():
                    self.terraform_path = str(path)
                    print(f"Found Terraform at: {self.terraform_path}", file=sys.stderr)
                    break
                    
        # Final check if Terraform was found
        if not self.terraform_path:
            terraform_installed, terraform_error = check_tool_installed("terraform", self.env_vars)
            if not terraform_installed:
                print(f"Error: Terraform is not installed or not found in PATH: {terraform_error}", file=sys.stderr)
                raise RuntimeError(f"Terraform not installed: {terraform_error}")
        else:
            print(f"Using Terraform at: {self.terraform_path}", file=sys.stderr)
             
        print(f"Terraform handler initialized with workspace: {self.workspace_path}", file=sys.stderr)
    
    def _run_terraform_command(self, cmd: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
        """
        Helper method to run Terraform commands with proper error handling.
        
        Args:
            cmd: Command parts to run (without the 'terraform' prefix)
            cwd: Working directory, defaults to workspace_path
            
        Returns:
            subprocess.CompletedProcess: Result of the command
        """
        full_cmd = [self.terraform_path or "terraform"] + cmd
        print(f"Running Terraform command: {' '.join(full_cmd)}", file=sys.stderr)
        
        return subprocess.run(
            full_cmd,
            check=True,
            capture_output=True,
            text=True,
            cwd=cwd or self.workspace_path,
            env=self.env_vars
        )
    
    def init(self) -> str:
        """Initialize the Terraform workspace."""
        try:
            result = self._run_terraform_command(["init"])
            return format_output(result.stdout, result.stderr)
        except subprocess.CalledProcessError as e:
            error_msg = f"Error during terraform init: {e.stderr if e.stderr else str(e)}"
            print(error_msg, file=sys.stderr)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error during terraform init: {str(e)}"
            print(error_msg, file=sys.stderr)
            return error_msg
    
    def plan(self, out_file: str = "tfplan") -> str:
        """Generate and optionally visualize an execution plan."""
        try:
            # Generate plan
            result = self._run_terraform_command(["plan", f"-out={out_file}"])
            
            # Check if dot is available for visualization
            dot_installed, dot_error = check_tool_installed("dot", self.env_vars)
            if dot_installed:
                try:
                    # Generate graph
                    graph_cmd = f"terraform graph -type=plan {out_file} | dot -Tpng > terraform_plan.png"
                    subprocess.run(
                        graph_cmd,
                        shell=True,
                        check=True,
                        capture_output=True,
                        text=True,
                        cwd=self.workspace_path,
                        env=self.env_vars
                    )
                    return format_output(
                        result.stdout + "\n\nPlan visualization saved as terraform_plan.png",
                        result.stderr
                    )
                except subprocess.CalledProcessError as e:
                    return format_output(
                        result.stdout + "\n\nNote: Plan visualization failed",
                        result.stderr
                    )
            return format_output(result.stdout, result.stderr)
        except subprocess.CalledProcessError as e:
            error_msg = f"Error generating plan: {e.stderr if e.stderr else str(e)}"
            print(error_msg, file=sys.stderr)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error during plan: {str(e)}"
            print(error_msg, file=sys.stderr)
            return error_msg
    
    def apply(self, auto_approve: bool = False) -> str:
        """Apply the Terraform configuration."""
        try:
            cmd = ["apply"]
            if auto_approve:
                cmd.append("-auto-approve")
                
            result = self._run_terraform_command(cmd)
            return format_output(result.stdout, result.stderr)
        except subprocess.CalledProcessError as e:
            error_msg = f"Error applying configuration: {e.stderr if e.stderr else str(e)}"
            print(error_msg, file=sys.stderr)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error during apply: {str(e)}"
            print(error_msg, file=sys.stderr)
            return error_msg
    
    def destroy(self, auto_approve: bool = False) -> str:
        """Destroy the Terraform-managed infrastructure."""
        try:
            cmd = ["destroy"]
            if auto_approve:
                cmd.append("-auto-approve")
                
            result = self._run_terraform_command(cmd)
            return format_output(result.stdout, result.stderr)
        except subprocess.CalledProcessError as e:
            error_msg = f"Error destroying infrastructure: {e.stderr if e.stderr else str(e)}"
            print(error_msg, file=sys.stderr)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error during destroy: {str(e)}"
            print(error_msg, file=sys.stderr)
            return error_msg
    
    def state_list(self) -> str:
        """List resources in the Terraform state."""
        try:
            result = self._run_terraform_command(["state", "list"])
            output = result.stdout.strip()
            return output if output else "No resources found in the current state."
        except subprocess.CalledProcessError as e:
            error_msg = f"Error listing state: {e.stderr if e.stderr else str(e)}"
            print(error_msg, file=sys.stderr)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error during state list: {str(e)}"
            print(error_msg, file=sys.stderr)
            return error_msg
    
    def show(self) -> str:
        """Show the current state or plan."""
        try:
            result = self._run_terraform_command(["show"])
            return format_output(result.stdout, result.stderr)
        except subprocess.CalledProcessError as e:
            error_msg = f"Error showing state: {e.stderr if e.stderr else str(e)}"
            print(error_msg, file=sys.stderr)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error during show: {str(e)}"
            print(error_msg, file=sys.stderr)
            return error_msg 