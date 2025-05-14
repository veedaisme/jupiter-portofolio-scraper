# Getting Started with Portfolio Scraper

## Prerequisites

Before using the Portfolio Scraper, ensure you have:

1. Python 3.9 or higher installed
2. Chrome browser installed
3. API keys for your chosen LLM provider (OpenAI, Anthropic, Google Gemini, or Ollama)
4. (Optional) Access to an InfluxDB instance

## Installation

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

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

## Configuration

1. **Create a .env file**

Copy the example environment file and update it with your settings:

```bash
cp .env.example .env
```

2. **Configure environment variables**

Edit the `.env` file with your preferred settings:

```
# LLM Provider (openai, anthropic, google, ollama)
LLM_PROVIDER=openai

# OpenAI Configuration
OPENAI_MODEL=gpt-4.1-mini-2025-04-14
OPENAI_PLANNER_MODEL=gpt-4.1-2025-04-14

# Anthropic Configuration
# ANTHROPIC_MODEL=claude-3-5-sonnet-20240620
# ANTHROPIC_PLANNER_MODEL=claude-3-5-sonnet-20240620

# Google Gemini Configuration
# GEMINI_MODEL=gemini-2.0-flash-exp
# GEMINI_PLANNER_MODEL=gemini-2.0-flash-exp
# GEMINI_API_KEY=your-api-key

# Ollama Configuration
# OLLAMA_MODEL=llama3.2:3b
# OLLAMA_PLANNER_MODEL=llama3.2:3b
# OLLAMA_NUM_CTX=32000

# Portfolio URL
PORTFOLIO_URL=https://portfolio.jup.ag/your-portfolio-url

# Browser Configuration
BROWSER_HEADLESS=true

# InfluxDB Configuration (Optional)
# INFLUX_URL=http://localhost:8086
# INFLUX_TOKEN=your-influx-token
# INFLUX_ORG=your-organization
# INFLUX_BUCKET=portfolio-data
```

## Running the Application

1. **Start Chrome in debug mode**

Run the provided script to start Chrome in debug mode:

```bash
./launch_chrome_debug.sh
```

This script starts Chrome with remote debugging enabled on port 9222.

2. **Run the portfolio scraper**

```bash
python portfolio_scraper.py
```

## Output

The application will:

1. Connect to the specified portfolio URL
2. Use the LLM to analyze the portfolio data
3. Output the portfolio information in markdown format
4. (Optional) Store the data in InfluxDB if configured

## Troubleshooting

- **Chrome connection issues**: Ensure Chrome is running in debug mode
- **LLM API errors**: Verify your API keys and model names
- **InfluxDB connection failures**: Check your InfluxDB credentials and connection details

For more detailed logs, check the console output which includes information about each step of the process.
