# Chainladder Python Agent

An AI-powered actuarial analysis assistant built on the chainladder-python library, providing interactive analysis capabilities through a multi-agent system.

## Overview

The Chainladder Python Agent is an interactive tool that allows actuaries and insurance professionals to perform complex loss reserving analyses using natural language queries. This system combines the powerful reserving capabilities of the chainladder-python package with a conversational AI interface built using LangGraph and Gradio.

### Key Features

- **Natural Language Interface**: Ask questions about actuarial analyses in plain English
- **Interactive Visualizations**: Generate and display loss development triangles, charts, and diagnostic plots
- **Multiple Reserving Methods**: Support for Chain Ladder, Bornhuetter-Ferguson, Cape Cod, and other actuarial methods
- **Explanations and Reporting**: Get detailed explanations of results and actuarial concepts
- **Built-in Sample Data**: Access to standard actuarial triangles for experimentation and learning

## Project Structure

```
chainladder-python-agent/
├── chainladder_agent/        # Main package directory
│   ├── agents/               # Specialized AI agents
│   │   ├── analysis_agent.py     # Performs actuarial analyses
│   │   ├── data_agent.py         # Handles data preparation and loading
│   │   ├── explanation_agent.py  # Generates explanations and reports
│   │   ├── supervisor.py         # Coordinates other agents
│   │   └── visualization_agent.py # Creates visualizations
│   ├── models/               # Model definitions and configurations
│   ├── tools/                # Tool implementations for agents
│   │   └── visualization_tools.py # Tools for creating actuarial plots
│   └── app.py                # Gradio web application
├── docs/                     # Documentation
├── notebooks/                # Jupyter notebooks with examples
│   └── visualizations/       # Example visualization outputs
├── tests/                    # Test suite
└── visualizations/           # Generated visualization outputs
```

## Installation

### Prerequisites

- Python 3.9+
- OpenAI API key

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/problemofpoints/chainladder-python-agent.git
   cd chainladder-python-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```
   
   Alternatively, you can provide the API key directly in the web interface.

## Usage

### Starting the Application

Run the application with:

```bash
python -m chainladder_agent.app
```

This will launch a Gradio web interface, typically accessible at http://localhost:7860.

### Using the Interface

1. **Input your OpenAI API key** (if not set as an environment variable)
2. **Ask a question** related to actuarial analysis
3. **View the response**, which may include text explanations, tables, and visualizations

### Example Queries

- "What sample triangles are available in the chainladder package?"
- "Analyze the raa triangle using the chain ladder method"
- "Compare chainladder and Bornhuetter-Ferguson methods on the abc triangle"
- "Create development factor charts for the ukmotor triangle"
- "Explain what IBNR means in actuarial science"
- "Create diagnostic plots for the clrd triangle"

## Development

### Adding New Features

To extend the agent system:

1. Add new tools in the `chainladder_agent/tools/` directory
2. Register tools with the appropriate agent in `chainladder_agent/agents/`
3. Update the supervisor agent to coordinate any new capabilities

### Running Tests

```bash
python -m pytest tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [chainladder-python](https://github.com/casact/chainladder-python) - The core actuarial analysis library
- [LangGraph](https://github.com/langchain-ai/langgraph) - Framework for building agent workflows
- [Gradio](https://gradio.app/) - Web interface framework
