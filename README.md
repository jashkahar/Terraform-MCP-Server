# Terraform MCP Assistant

A FastMCP-based server that provides natural language interface to Terraform operations. This assistant allows you to manage your infrastructure using simple English commands instead of remembering specific Terraform syntax.

## Features

- Natural language processing of Terraform commands
- Execution plan visualization
- State inspection and management
- Infrastructure deployment and destruction
- Configuration documentation
- Automatic workspace validation
- Error handling and formatted output

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/terraform-mcp-server.git
cd terraform-mcp-server
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Optional: Install Graphviz for plan visualization:

- Windows: Download from [Graphviz Download Page](https://graphviz.org/download/)
- Linux: `sudo apt-get install graphviz`
- macOS: `brew install graphviz`

## Configuration

1. Set up environment variables (optional):

```bash
export TERRAFORM_WORKSPACE="/path/to/terraform/workspace"
export LOG_LEVEL="INFO"
```

2. Place your Terraform configuration files in the workspace directory.

## Usage

1. Start the MCP server:

```bash
python src/main.py
```

2. Example commands:

- "Initialize the Terraform workspace"
- "What will change if I apply?"
- "Show me the current state"
- "Apply the configuration"
- "List all resources"
- "Destroy the infrastructure"

## Project Structure

```
terraform-mcp-assistant/
├── docs/                  # Documentation
├── examples/             # Example Terraform configurations
├── src/                  # Source code
│   ├── handlers/        # Command handlers
│   ├── main.py         # Entry point
│   └── config.py       # Configuration management
├── tests/               # Test files
├── .env                # Environment variables (not in VCS)
└── README.md           # This file
```

## Development

1. Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

2. Run tests:

```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

