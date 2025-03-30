"""
Terraform MCP Server

An MCP server that exposes Terraform infrastructure-as-code operations through natural language.
Allows LLMs to execute Terraform commands and retrieve information about infrastructure
without requiring the user to know specific command syntax.
"""

import subprocess
import shlex
import json
import re
import os
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP, Context

# Define the project directory: use PROJECT_ROOT if set, otherwise default to current directory
project_dir = os.environ.get('PROJECT_ROOT', os.getcwd())
# Use a consistent copy of the current environment
env_vars = os.environ.copy()

# Create the MCP server
mcp = FastMCP("Terraform Assistant")


@mcp.tool()
def test(query: str) -> str:
    """Test if this server has access to the project_dir by listing its contents."""
    try:
        if project_dir and os.path.exists(project_dir):
            # Use 'dir' for Windows and 'ls' for Unix-based systems if needed.
            # Here we use 'dir' assuming Windows, adjust if necessary.
            os.chdir(project_dir)
            dir_result = subprocess.run(
                "dir",
                shell=True,
                capture_output=True,
                text=True,
                env=env_vars
            )
            subprocess.check_call(['ls', '-l'])
            return f"Server has access to the project directory at: {project_dir} Contents:{dir_result.stdout}"
        else:
            return f"Project directory not found or not set: {project_dir}"
    except Exception as e:
        return f"Error accessing project directory: {str(e)}"
    
@mcp.tool()
def init_terraform(query: str) -> str:
    """Initialize the Terraform project."""
    try:
        os.chdir(project_dir)
        result = subprocess.run(["terraform", "init"],
            capture_output=True,
            text=True,
            check=True,
            env=env_vars
        )
        return str(f"Terraform initialization successful")
    except subprocess.CalledProcessError as e:
        return str(f"Error during terraform init: {e.stderr if e.stderr else str(e)}")


@mcp.tool()
def handle_terraform_query(query: str) -> str:
    """
    Processes a natural language Terraform query and executes the appropriate command.

    This tool supports the following common Terraform use cases:

    1. Execution Plan Visualization:
       - **Intent:** Understand what changes will occur if the configuration is applied.
       - **Example queries:** 
         - "What will change if I apply?"
         - "Show me the execution plan"
         - "What resources will be created or modified?"
       - **Command:** Run `terraform plan -out=tfplan` then `terraform graph -type=plan tfplan | dot -Tpng > terraform_plan.png`
       - **Output:** Returns a message indicating that the execution plan graph has been generated and saved.

    2. State Inspection:
       - **Intent:** Examine the current state to list all managed resources.
       - **Example queries:**
         - "What resources currently exist?"
         - "Show me the current state"
         - "List all resources"
       - **Command:** `terraform state list`
       - **Output:** Returns a list of resources from the current Terraform state.

    3. Cost Estimation:
       - **Intent:** Estimate the cost impact of the infrastructure.
       - **Example queries:**
         - "How much will this cost?"
         - "Estimate monthly expenses"
         - "What's the pricing impact?"
       - **Command:** `infracost breakdown --path .`
       - **Output:** Returns cost estimation details (requires infracost to be installed).

    4. Security Analysis:
       - **Intent:** Check the configuration for potential security issues.
       - **Example queries:**
         - "Are there any security issues?"
         - "Check for vulnerabilities"
         - "Is my configuration secure?"
       - **Command:** `tfsec .`
       - **Output:** Returns a security analysis report (requires tfsec to be installed).

    5. Drift Detection:
       - **Intent:** Detect if the actual state has drifted from the configuration.
       - **Example queries:**
         - "Has anything changed since last apply?"
         - "Check for drift"
         - "Are resources consistent with the state?"
       - **Command:** `terraform plan -detailed-exitcode`
       - **Output:** Returns the plan output; an exit code of 2 typically indicates drift.

    6. Module Documentation:
       - **Intent:** Understand or explain a specific module or configuration.
       - **Example queries:**
         - "Explain this module"
         - "What does this configuration do?"
         - "Show documentation for this resource"
       - **Command:** `terraform show`
       - **Output:** Returns the current configuration details.

    7. Initialization, Apply, and Destroy:
       - **Terraform Init:**
         - **Intent:** Prepare the working directory for Terraform operations.
         - **Command:** `terraform init`
       - **Terraform Apply:**
         - **Intent:** Apply the configuration to create or update resources.
         - **Example queries:** "Apply the configuration", "Deploy the infrastructure"
         - **Command:** `terraform apply -auto-approve`
       - **Terraform Destroy:**
         - **Intent:** Destroy all resources managed by Terraform.
         - **Example queries:** "Destroy the infrastructure", "Tear down my resources"
         - **Command:** `terraform destroy -auto-approve`

    **Intent Recognition & Error Handling:**
      - Uses simple keyword matching (case-insensitive) to map the query to a command.
      - Verifies that required CLI tools are installed (e.g., dot for visualization, infracost for cost estimation, tfsec for security analysis).
      - Uses subprocess.run with check=True to raise exceptions on errors, catching subprocess.CalledProcessError to return descriptive error messages.
      - Executes commands in the Terraform project directory (`project_dir`) using the environment copy (`env_vars`).

    Args:
        query (str): The natural language query describing the desired Terraform operation.

    Returns:
        str: The output from the executed command or a descriptive error message.
    """
    query_normalized = query.lower().strip()

    # Execution Plan Visualization
    if any(keyword in query_normalized for keyword in ["plan", "what will change", "execution plan", "visualize"]):
        try:
            # Ensure Graphviz's dot is installed
            # try:
            #     subprocess.run(["dot", "-V"], check=True, capture_output=True, text=True, cwd=project_dir, env=env_vars)
            # except (subprocess.CalledProcessError, FileNotFoundError):
            #     return ("Error: 'dot' (from Graphviz) is required for plan visualization but was not found. "
            #             "Please install Graphviz.")
            # # Generate Terraform plan
            # subprocess.run(["terraform", "plan", "-out=tfplan"], check=True, capture_output=True, text=True, cwd=project_dir, env=env_vars)
            # Generate and save the graph visualization
            process = subprocess.run(
                "terraform"
                "graph",
                "-type=plan",
                "tfplan",
                shell=True,
                capture_output=True,
                text=True,
                # stdout=subprocess.PIPE,
                # stderr=subprocess.PIPE,
                cwd=project_dir,
                env=env_vars
            )
            # _, stderr = process.communicate()
            if process.returncode != 0:
                return f"Error generating plan visualization: {process}"
            return "Execution plan graph has been generated and saved as 'terraform_plan.png'."
        except subprocess.CalledProcessError as e:
            return f"Error executing plan visualization: {e.stderr if e.stderr else str(e)}"

    # State Inspection
    elif any(keyword in query_normalized for keyword in ["state list", "resources exist", "current state", "list all resources"]):
        try:
            result = subprocess.run(
                "terraform", 
                "state",
                "list",
                shell=True,
                check=True,
                capture_output=True,
                text=True,
                cwd=project_dir,
                env=env_vars
            )
            #output = result.stdout.strip()
            return f"Current Terraform-managed resources:{result}" if output else "No resources found in the current state."
        except subprocess.CalledProcessError as e:
            return f"Error listing state resources: {e.stderr if e.stderr else str(e)}"

    # Cost Estimation
    elif any(keyword in query_normalized for keyword in ["cost", "expense", "price", "pricing", "how much"]):
        try:
            # Ensure infracost is installed
            try:
                subprocess.run(["infracost", "--version"], check=True, capture_output=True, text=True, cwd=project_dir, env=env_vars)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return ("Error: 'infracost' is required for cost estimation but was not found. "
                        "Please install it from https://www.infracost.io/docs/")
            result = subprocess.run(
                ["infracost", "breakdown", "--path", "."],
                check=True,
                capture_output=True,
                text=True,
                cwd=project_dir,
                env=env_vars
            )
            return f"Cost estimation:\n\n{result.stdout}"
        except subprocess.CalledProcessError as e:
            return f"Error estimating costs: {e.stderr if e.stderr else str(e)}"

    # Security Analysis
    elif any(keyword in query_normalized for keyword in ["security", "vulnerabilit", "secure", "issues"]):
        try:
            # Ensure tfsec is installed
            try:
                subprocess.run(["tfsec", "--version"], check=True, capture_output=True, text=True, cwd=project_dir, env=env_vars)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return ("Error: 'tfsec' is required for security analysis but was not found. "
                        "Please install it from https://github.com/aquasecurity/tfsec")
            result = subprocess.run(
                ["tfsec", "."],
                check=True,
                capture_output=True,
                text=True,
                cwd=project_dir,
                env=env_vars
            )
            output = result.stdout.strip()
            return f"Security analysis results:\n\n{output}" if output else "No security issues found in the configuration."
        except subprocess.CalledProcessError as e:
            return f"Security issues detected:\n\n{e.stdout if e.stdout else str(e)}"

    # Drift Detection
    elif any(keyword in query_normalized for keyword in ["drift", "changed since", "consistent"]):
        try:
            result = subprocess.run(
                ["terraform", "plan", "-detailed-exitcode"],
                capture_output=True,
                text=True,
                cwd=project_dir,
                env=env_vars
            )
            # Exit codes: 0 = no changes, 2 = changes present, others indicate errors
            if result.returncode == 0:
                return "No drift detected. The infrastructure matches the configuration."
            elif result.returncode == 2:
                return f"Drift detected! The current infrastructure state differs from the configuration:\n\n{result.stdout}"
            else:
                return f"Error checking for drift: {result.stderr}"
        except subprocess.CalledProcessError as e:
            return f"Error checking for drift: {e.stderr if e.stderr else str(e)}"

    # Module Documentation / Configuration Explanation
    elif any(keyword in query_normalized for keyword in ["explain", "documentation", "what does", "show"]):
        try:
            result = subprocess.run(
                ["terraform", "show"],
                check=True,
                capture_output=True,
                text=True,
                cwd=project_dir,
                env=env_vars
            )
            return f"Current Terraform configuration details:\n\n{result.stdout}"
        except subprocess.CalledProcessError as e:
            return f"Error showing configuration: {e.stderr if e.stderr else str(e)}"
    

    # Terraform Apply
    elif any(keyword in query_normalized for keyword in ["apply", "deploy"]):
        try:
            result = subprocess.run(
                ["terraform", "apply", "-auto-approve"],
                check=True,
                capture_output=True,
                text=True,
                cwd=project_dir,
                env=env_vars
            )
            return f"Terraform apply executed successfully:\n\n{result.stdout}"
        except subprocess.CalledProcessError as e:
            return f"Error during terraform apply: {e.stderr if e.stderr else str(e)}"

    # Terraform Destroy
    elif any(keyword in query_normalized for keyword in ["destroy", "remove", "tear down"]):
        try:
            result = subprocess.run(
                ["terraform", "destroy", "-auto-approve"],
                check=True,
                capture_output=True,
                text=True,
                cwd=project_dir,
                env=env_vars
            )
            return f"Terraform destroy executed successfully:\n\n{result.stdout}"
        except subprocess.CalledProcessError as e:
            return f"Error during terraform destroy: {e.stderr if e.stderr else str(e)}"

    else:
        # Attempt to execute a Terraform command parsed from the query
        try:
            tf_command = query_normalized.replace("terraform", "").strip()
            args = shlex.split(tf_command)
            if not args:
                return "I couldn't determine which Terraform operation to perform. Please be more specific."
            result = subprocess.run(
                ["terraform"] + args,
                check=True,
                capture_output=True,
                text=True,
                cwd=project_dir,
                env=env_vars
            )
            return f"Command output:\n\n{result.stdout}"
        except subprocess.CalledProcessError as e:
            return (
                f"Error executing command: {e.stderr if e.stderr else str(e)}\n\n"
                "I couldn't determine the specific Terraform operation you want to perform. "
                "Please try queries related to plan visualization, state inspection, cost estimation, "
                "security analysis, drift detection, module documentation, or use explicit commands like "
                "'terraform init', 'terraform apply', or 'terraform destroy'."
            )


@mcp.resource("terraform://modules")
def list_terraform_modules() -> str:
    """
    List all Terraform modules in the current project.
    
    This resource provides information about all modules used in the current Terraform configuration.
    
    Returns:
        str: A formatted list of Terraform modules.
    """
    try:
        result = subprocess.run(
            ["terraform", "state", "list"],
            check=True,
            capture_output=True,
            text=True,
            cwd=project_dir,
            env=env_vars
        )
        resources = result.stdout.strip().split("\n")
        modules = set()
        for resource in resources:
            if resource:
                parts = resource.split(".")
                if len(parts) > 1 and parts[0] == "module":
                    modules.add(parts[1])
        if not modules:
            return "No modules found in the current Terraform state."
        return "Terraform modules in use:\n" + "\n".join(f"- {module}" for module in sorted(modules))
    except subprocess.CalledProcessError as e:
        return f"Error listing Terraform modules: {e.stderr if e.stderr else str(e)}"


@mcp.resource("terraform://variables")
def get_terraform_variables() -> str:
    """
    List all Terraform variables defined in the project.
    
    This resource provides information about variables defined in the Terraform configuration files.
    
    Returns:
        str: A formatted list of Terraform variables and their values.
    """
    try:
        tf_files = list(Path(project_dir).glob("*.tf"))
        if not tf_files:
            return "No Terraform (.tf) files found in the current directory."
        variables = []
        var_pattern = re.compile(r'variable\s+"([^"]+)"\s+{')
        for file_path in tf_files:
            with open(file_path, 'r') as f:
                content = f.read()
                variables.extend(match.group(1) for match in var_pattern.finditer(content))
        if not variables:
            return "No variables found in the Terraform configuration files."
        # Optionally attempt to get current values via 'terraform console'
        values = {}
        for var in variables:
            try:
                echo_process = subprocess.Popen(["echo", f"var.{var}"], stdout=subprocess.PIPE, cwd=project_dir, env=env_vars)
                result = subprocess.run(
                    ["terraform", "console"],
                    stdin=echo_process.stdout,
                    capture_output=True,
                    text=True,
                    timeout=2,
                    cwd=project_dir,
                    env=env_vars
                )
                if result.returncode == 0:
                    values[var] = result.stdout.strip()
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                continue
        output = "Terraform variables defined in the project:\n"
        for var in sorted(variables):
            output += f"- {var} = {values[var]}\n" if var in values else f"- {var}\n"
        return output
    except Exception as e:
        return f"Error retrieving Terraform variables: {str(e)}"


@mcp.resource("terraform://outputs")
def get_terraform_outputs() -> str:
    """
    Retrieve all outputs from the Terraform state.
    
    This resource provides the output values defined in the Terraform configuration.
    
    Returns:
        str: A formatted list of Terraform outputs and their values.
    """
    try:
        result = subprocess.run(
            ["terraform", "output", "-json"],
            check=True,
            capture_output=True,
            text=True,
            cwd=project_dir,
            env=env_vars
        )
        if not result.stdout.strip():
            return "No outputs found in the Terraform state."
        try:
            outputs = json.loads(result.stdout)
            output_text = "Terraform outputs:\n"
            for name, data in outputs.items():
                value = data.get("value", "")
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, indent=2)
                output_text += f"- {name} = {value}\n"
            return output_text
        except json.JSONDecodeError:
            return f"Error parsing Terraform outputs: Invalid JSON format\n\nRaw output:\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Error retrieving Terraform outputs: {e.stderr if e.stderr else str(e)}"


@mcp.resource("terraform://providers")
def get_terraform_providers() -> str:
    """
    List all providers used in the Terraform configuration.
    
    This resource provides information about all providers configured in the Terraform project.
    
    Returns:
        str: A formatted list of Terraform providers.
    """
    try:
        result = subprocess.run(
            ["terraform", "providers"],
            check=True,
            capture_output=True,
            text=True,
            cwd=project_dir,
            env=env_vars
        )
        if not result.stdout.strip():
            return "No provider information available."
        return f"Terraform providers:\n\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        # Fallback: Parse .tf files
        try:
            tf_files = list(Path(project_dir).glob("*.tf"))
            if not tf_files:
                return "No Terraform (.tf) files found in the current directory."
            providers = set()
            provider_pattern = re.compile(r'provider\s+"([^"]+)"\s+{')
            for file_path in tf_files:
                with open(file_path, 'r') as f:
                    content = f.read()
                    providers.update(match.group(1) for match in provider_pattern.finditer(content))
            if not providers:
                return "No providers found in the Terraform configuration files."
            return "Terraform providers in use:\n" + "\n".join(f"- {provider}" for provider in sorted(providers))
        except Exception as nested_e:
            return f"Error retrieving Terraform providers: {e.stderr if e.stderr else str(e)}\nFallback method also failed: {str(nested_e)}"


@mcp.prompt()
def help_prompt() -> str:
    """
    Provides help information about the Terraform Assistant.
    
    This prompt explains the capabilities of the Terraform Assistant and how to use it to manage Terraform infrastructure.
    """
    return """
    # Terraform Assistant Help

    This assistant helps you manage your Terraform infrastructure using natural language commands.

    ## Available Commands

    - **Plan Visualization**: "What will change if I apply?" or "Show me the execution plan"
    - **State Inspection**: "What resources currently exist?" or "Show me the current state"
    - **Cost Estimation**: "How much will this cost?" or "Estimate monthly expenses"
    - **Security Analysis**: "Are there any security issues?" or "Is my configuration secure?"
    - **Drift Detection**: "Has anything changed since last apply?" or "Check for drift"
    - **Module Documentation**: "Explain this module" or "What does this configuration do?"
    - **Initialization**: "Initialize my Terraform project" or "Run terraform init"
    - **Apply**: "Apply the configuration" or "Deploy the infrastructure"
    - **Destroy**: "Destroy the infrastructure" or "Tear down my resources"

    ## Available Resources

    - **Modules**: `terraform://modules`
    - **Variables**: `terraform://variables`
    - **Outputs**: `terraform://outputs`
    - **Providers**: `terraform://providers`
    """

# Main execution
if __name__ == "__main__":
    mcp.run(transport='stdio')
