"""Configuration management for the MCP Terraform server."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directory of the project
PROJECT_ROOT = os.getenv("PROJECT_ROOT")
if not PROJECT_ROOT:
    # Get the absolute path to the project root (one level up from src)
    PROJECT_ROOT = str(Path(__file__).parent.parent.absolute())
env_vars = os.environ.copy()
print(f"Project root: {PROJECT_ROOT}", file=sys.stderr)

# Default paths
terraform_workspace_env = os.getenv("TERRAFORM_WORKSPACE")
if terraform_workspace_env:
    TERRAFORM_WORKSPACE = terraform_workspace_env
    print(f"Using terraform workspace from env: {TERRAFORM_WORKSPACE}", file=sys.stderr)
else:
    # Try to find sample_terraform directory
    sample_terraform_path = Path(PROJECT_ROOT) / "examples" / "sample_terraform"
    if sample_terraform_path.exists() and sample_terraform_path.is_dir():
        TERRAFORM_WORKSPACE = str(sample_terraform_path)
        print(f"Found sample terraform directory: {TERRAFORM_WORKSPACE}", file=sys.stderr)
    else:
        # Check for main.tf in the entire project
        main_tf_files = list(Path(PROJECT_ROOT).glob('**/main.tf'))
        if main_tf_files:
            # Use the directory containing the first main.tf found
            TERRAFORM_WORKSPACE = str(main_tf_files[0].parent)
            print(f"Found main.tf in: {TERRAFORM_WORKSPACE}", file=sys.stderr)
        else:
            # Fallback to the project root
            TERRAFORM_WORKSPACE = PROJECT_ROOT
            print(f"No terraform directory found, using project root: {TERRAFORM_WORKSPACE}", file=sys.stderr)

LOG_DIR = os.getenv("LOG_DIR", str(Path(PROJECT_ROOT) / "logs"))
print(f"Log directory: {LOG_DIR}", file=sys.stderr)

# # Server configuration
# HOST = os.getenv("HOST", "localhost")
# PORT = int(os.getenv("PORT", "8000"))

# # Logging configuration
# LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
# LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Create necessary directories
os.makedirs(LOG_DIR, exist_ok=True) 