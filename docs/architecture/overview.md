# Portfolio Scraper Architecture

## Overview

The Portfolio Scraper is designed with a modular architecture that separates concerns and promotes maintainability. The application uses the browser-use framework to automate browser interactions and LLMs (Language Model Models) to interpret portfolio data.

## Core Components

### 1. Configuration Layer

Located in `src/config/`, this layer manages all configuration settings:

- **constants.py**: Contains all constant values used throughout the application
- **settings.py**: Handles environment variable loading and configuration setup

### 2. Service Layer

Located in `src/services/`, this layer provides core services:

- **browser_service.py**: Manages browser connections and configurations
- **influx_service.py**: Handles InfluxDB connections and data storage

### 3. Agent Layer

Located in `src/agents/`, this layer contains the intelligent agents:

- **portfolio_agent.py**: Implements the portfolio scraping agent using LLMs

### 4. Utilities Layer

Located in `src/utils/`, this layer provides supporting utilities:

- **logging_utils.py**: Implements logging functionality

### 5. Main Application

- **src/main.py**: Core application logic
- **portfolio_scraper.py**: Entry point script

## Flow Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Configuration  │────▶│     Services    │────▶│      Agents     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                │                        │
                                ▼                        ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │    Utilities    │◀────│  Main Application│
                        └─────────────────┘     └─────────────────┘
```

## Design Principles

1. **Separation of Concerns**: Each module has a specific responsibility
2. **Dependency Injection**: Dependencies are explicitly passed to classes
3. **Error Handling**: Proper error handling at each layer
4. **Configuration Management**: Centralized configuration
5. **Testability**: Modular design makes testing easier
