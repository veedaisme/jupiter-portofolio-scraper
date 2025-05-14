# Contributing to Portfolio Scraper

This guide provides information for developers who want to contribute to the Portfolio Scraper project.

## Development Environment Setup

1. **Clone the repository**

```bash
git clone <repository-url>
cd portfolio-scraper
```

2. **Set up a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install development dependencies**

```bash
pip install -r requirements-dev.txt  # If available, otherwise use requirements.txt
```

## Project Structure

The project follows a modular architecture:

```
portfolio_scraper.py  # Main entry point script
src/
  ├── agents/         # Agent implementations
  │   └── portfolio_agent.py
  ├── config/         # Configuration modules
  │   ├── constants.py
  │   └── settings.py
  ├── services/       # Service implementations
  │   ├── browser_service.py
  │   └── influx_service.py
  ├── utils/          # Utility modules
  │   └── logging_utils.py
  └── main.py         # Main application logic
docs/                 # Documentation
  ├── architecture/   # Architecture documentation
  ├── usage/          # Usage guides
  └── development/    # Development guides
```

## Coding Standards

1. **PEP 8**: Follow PEP 8 style guide for Python code
2. **Type Hints**: Use type hints for function parameters and return values
3. **Docstrings**: Include docstrings for all modules, classes, and functions
4. **Error Handling**: Implement proper error handling with specific exceptions

## Adding New Features

When adding new features:

1. **Create a new branch**: `git checkout -b feature/your-feature-name`
2. **Implement the feature**: Follow the existing architecture patterns
3. **Add tests**: Write tests for your new feature
4. **Update documentation**: Update relevant documentation
5. **Submit a pull request**: Create a pull request with a clear description

## Extending Agent Capabilities

To extend the portfolio agent capabilities:

1. Create a new agent class in the `src/agents/` directory
2. Implement the required methods following the existing patterns
3. Update the main application to use your new agent

## Adding Support for New LLM Providers

To add support for a new LLM provider:

1. Update `src/config/constants.py` with new provider constants
2. Modify `src/config/settings.py` to include the new provider
3. Update documentation to reflect the new provider

## Testing

Run tests using pytest:

```bash
pytest
```

## Documentation

Update documentation when making significant changes:

1. Architecture changes: Update `docs/architecture/`
2. Usage changes: Update `docs/usage/`
3. Development changes: Update `docs/development/`
