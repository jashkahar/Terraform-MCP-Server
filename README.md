# Terraform MCP Server

A natural language interface for managing Terraform infrastructure, allowing you to execute Terraform operations through conversational commands.

## Overview

This project provides an MCP (Model Control Protocol) server that exposes Terraform infrastructure-as-code operations through natural language. It enables LLMs to execute Terraform commands and retrieve information about infrastructure without requiring specific command syntax knowledge.

## Features

- **Natural Language Interface**: Execute Terraform operations using conversational commands
- **Comprehensive Terraform Operations**:

  - Plan visualization and execution planning
  - State inspection and resource listing
  - Cost estimation
  - Security analysis
  - Drift detection
  - Module documentation
  - Infrastructure deployment and destruction

- **Resource Information Access**:
  - List all Terraform modules
  - View defined variables
  - Check output values
  - Monitor provider configurations

## Prerequisites

- Python 3.x
- Terraform CLI
- Optional tools for enhanced functionality:
  - Graphviz (for plan visualization)
  - Infracost (for cost estimation)
  - Tfsec (for security analysis)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd terraform-mcp-server
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Set the project directory (optional):

```bash
export PROJECT_ROOT=/path/to/your/terraform/project
```

2. Run the MCP server:

```bash
python terraform-mcp-server.py
```

## Available Commands

### Infrastructure Operations

- "What will change if I apply?"
- "Show me the execution plan"
- "Apply the configuration"
- "Destroy the infrastructure"

### State and Resource Management

- "What resources currently exist?"
- "Show me the current state"
- "Check for drift"

### Analysis and Planning

- "How much will this cost?"
- "Are there any security issues?"
- "Explain this module"

## Resource Endpoints

- `terraform://modules` - List all Terraform modules
- `terraform://variables` - View defined variables
- `terraform://outputs` - Check output values
- `terraform://providers` - Monitor provider configurations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
