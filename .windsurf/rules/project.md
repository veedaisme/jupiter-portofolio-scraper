---
trigger: model_decision
description: development rules
---

# Windsurf Rules for Portfolio Scraper

This document outlines the key rules and principles for developing and maintaining the Portfolio Scraper project.

## Code Organization Rules

1. **Modular Architecture**: Maintain strict separation between configuration, services, agents, and utilities.
2. **Single Responsibility**: Each module, class, and function should have a single responsibility.
3. **Explicit Dependencies**: Use dependency injection instead of global state.
4. **Configuration Isolation**: All configuration should be managed through the config module.

## Agent Development Rules

1. **Agent Accuracy**:
   - Agents must validate data before processing
   - Use appropriate error handling for all agent operations
   - Implement retry mechanisms for transient failures

2. **Agent Isolation**:
   - Each agent should operate independently
   - Agents should not have direct dependencies on other agents
   - Communication between agents should be through well-defined interfaces

3. **Agent Maintainability**:
   - Document all agent behaviors and parameters
   - Include comprehensive logging for debugging
   - Write tests for all agent functionality

## LLM Integration Rules

1. **Provider Abstraction**: Abstract LLM provider details to allow easy switching.
2. **Prompt Management**: Keep prompts in a centralized location for easy updates.
3. **Error Handling**: Implement proper error handling for LLM API calls.
4. **Cost Management**: Be mindful of token usage and implement strategies to minimize costs.

## Browser Automation Rules

1. **Resilient Selectors**: Use robust selectors that won't break with minor UI changes.
2. **Timeout Handling**: Implement proper timeout handling for all browser operations.
3. **Resource Management**: Ensure browser resources are properly cleaned up.

## Data Management Rules

1. **Data Validation**: Validate all data before storage or processing.
2. **Error Handling**: Implement proper error handling for database operations.
3. **Optional Dependencies**: Make database integration optional with graceful fallbacks.

## Testing Rules

1. **Unit Tests**: Write unit tests for all core functionality.
2. **Integration Tests**: Write integration tests for service interactions.
3. **Mock External Services**: Use mocks for external services in tests.

## Documentation Rules

1. **Code Documentation**: Document all public interfaces with docstrings.
2. **Architecture Documentation**: Maintain up-to-date architecture documentation.
3. **Usage Documentation**: Provide clear usage examples and guides.

## Security Rules

1. **API Key Management**: Never hardcode API keys; use environment variables.
2. **Input Validation**: Validate all inputs to prevent injection attacks.
3. **Dependency Management**: Regularly update dependencies to address security vulnerabilities.

## Performance Rules

1. **Resource Efficiency**: Minimize resource usage, especially for long-running processes.
2. **Caching**: Implement caching where appropriate to reduce API calls.
3. **Asynchronous Operations**: Use async/await for I/O-bound operations.

## Contribution Rules

1. **Code Reviews**: All changes must be reviewed before merging.
2. **Documentation Updates**: Update documentation when making significant changes.
3. **Test Coverage**: Maintain or improve test coverage with new contributions.
