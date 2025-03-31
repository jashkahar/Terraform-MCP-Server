"""Tests for the Terraform handler."""

import os
import pytest
from pathlib import Path
from src.handlers.terraform import TerraformHandler
from src.handlers.utils import validate_workspace

# Test fixtures
@pytest.fixture
def sample_workspace(tmp_path):
    """Create a temporary workspace with a sample Terraform file."""
    workspace = tmp_path / "terraform"
    workspace.mkdir()
    
    # Create a simple main.tf
    main_tf = workspace / "main.tf"
    main_tf.write_text("""
        resource "null_resource" "example" {
          triggers = {
            always_run = "${timestamp()}"
          }
        }
    """)
    
    return workspace

def test_validate_workspace_valid(sample_workspace):
    """Test workspace validation with valid workspace."""
    assert validate_workspace(str(sample_workspace)) is True

def test_validate_workspace_invalid(tmp_path):
    """Test workspace validation with invalid workspace."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    assert validate_workspace(str(empty_dir)) is False

def test_terraform_handler_init_invalid_workspace(tmp_path):
    """Test handler initialization with invalid workspace."""
    with pytest.raises(ValueError, match="Invalid Terraform workspace"):
        TerraformHandler(str(tmp_path))

def test_terraform_handler_init_valid_workspace(sample_workspace):
    """Test handler initialization with valid workspace."""
    handler = TerraformHandler(str(sample_workspace))
    assert handler.workspace_path == Path(sample_workspace)
    assert isinstance(handler.env_vars, dict) 