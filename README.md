# Jupiter Portfolio Scraper

A Python application that uses the [`browser-use`](https://github.com/veedaisme/browser-use) automation framework and LLMs (OpenAI, Anthropic, Google Gemini, or Ollama) to automatically scrape and analyze portfolio data from [Jupiter Portfolio](https://portfolio.jup.ag/). The results are stored in InfluxDB for further analysis and visualization.

## Features

- High-level browser automation using [`browser-use`](https://github.com/veedaisme/browser-use)
- LLM-powered extraction and analysis (supports OpenAI, Anthropic, Google Gemini, and Ollama)
- Modular architecture for improved maintainability and testability
- Proper error handling and logging
- Clean separation of concerns (configuration, services, agents)
- Stores results in InfluxDB (optional)
- Easily configurable via `.env` file

## Requirements

- Python 3.9+
- Chrome installed and running in debug mode
- InfluxDB instance (optional, for storing results)
- [`browser-use`](https://github.com/veedaisme/browser-use) package
- API keys for your chosen LLM provider

## Setup

1. **Clone the repository**
    ```bash
    git clone git@github.com:veedaisme/jupiter-portofolio-scraper.git
    cd jupiter-portofolio-scraper
    ```

2. **Create and activate a virtual environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    # If requirements.txt is missing, install dependencies manually:
    pip install ./browser-use langchain langchain-openai langchain-anthropic langchain-ollama langchain-google-genai python-dotenv influxdb-client pydantic requests
    ```

4. **Set up your `.env` file**

    Copy `.env.example` to `.env` and fill in your credentials and settings:
    ```bash
    cp .env.example .env
    ```

    Key settings:
    - `LLM_PROVIDER` (openai, anthropic, google, or ollama)
    - API keys for your chosen provider
    - `PORTFOLIO_URL` (the Jupiter portfolio URL to scrape)
    - InfluxDB connection info (optional)
    - `BROWSER_HEADLESS` (`true` or `false`)

5. **Start Chrome in debug mode**
    ```bash
    ./launch_chrome_debug.sh
    ```

6. **Run the app**
    ```bash
    python portfolio_scraper.py
    ```

## Project Structure

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
.env                  # Environment variables
browser-use/          # Core browser automation and agent logic
```

## Environment Variables

See `.env.example` for all available configuration options.

## Troubleshooting

- Make sure Chrome is running in debug mode before starting the application
- If InfluxDB connection fails, the application will still run but won't store the results
- For API key issues, verify your credentials in the `.env` file
- Check logs for detailed error information
