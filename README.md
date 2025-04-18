# Jupiter Portfolio Scraper

A Python application that uses the [`browser-use`](https://github.com/veedaisme/browser-use) automation framework and LLMs (OpenAI, Anthropic, or Ollama) to automatically scrape and analyze portfolio data from [Jupiter Portfolio](https://portfolio.jup.ag/). The results—including net worth, top assets, and platforms—are stored in InfluxDB for further analysis and visualization.

## Features

- High-level browser automation using [`browser-use`](https://github.com/browser-use/browser-use)
- LLM-powered extraction and analysis (supports OpenAI, Anthropic, and Ollama)
- Scrapes:
  - Net worth
  - Top 5 assets
  - Top 5 platforms
- Stores results in InfluxDB
- Easily configurable via `.env` file

## Requirements

- Python 3.9+
- Chrome installed (default path: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` on macOS)
- InfluxDB instance (for storing results)
- [`browser-use`](https://github.com/veedaisme/browser-use) package (included in this repo)
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
    pip install ./browser-use langchain langchain-openai langchain-anthropic langchain-ollama python-dotenv influxdb-client pydantic
    ```

4. **Set up your `.env` file**

    Copy `.env.example` to `.env` and fill in your credentials and settings:
    ```bash
    cp .env.example .env
    ```

    Key settings:
    - `LLM_PROVIDER` (openai, anthropic, or ollama)
    - API keys for your chosen provider
    - `PORTFOLIO_URL` (the Jupiter portfolio URL to scrape)
    - InfluxDB connection info
    - `BROWSER_HEADLESS` (`true` or `false`)

5. **Run the app**
    ```bash
    python main.py
    ```

## Example Output

- Console output will show the scraped data and InfluxDB writes.
- Data is stored in your specified InfluxDB bucket for further use.

## Environment Variables

See `.env.example` for all available configuration options.

## Project Structure

```
main.py               # Entry point
.env                  # Environment variables
browser-use/          # Core browser automation and agent logic (browser-use framework)
```

## Troubleshooting

- If the browser window opens even in headless mode, check your `.env` for `BROWSER_HEADLESS=true` and ensure Chrome and Playwright are up to date.
- For SSH or InfluxDB issues, verify your credentials and network access.
- If `.env` changes aren't applied, restart your terminal to apply new environment variables.
