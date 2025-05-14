import os
import asyncio
from typing import Optional

from dotenv import load_dotenv
from influxdb_client import InfluxDBClient

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig, Controller

load_dotenv()

# Constants for environment variable keys
LLM_PROVIDER_KEY = "LLM_PROVIDER"
ANTHROPIC_MODEL_KEY = "ANTHROPIC_MODEL"
OLLAMA_MODEL_KEY = "OLLAMA_MODEL"
OLLAMA_NUM_CTX_KEY = "OLLAMA_NUM_CTX"
GEMINI_MODEL_KEY = "GEMINI_MODEL"
GEMINI_API_KEY = "GEMINI_API_KEY"
OPENAI_MODEL_KEY = "OPENAI_MODEL"
PORTFOLIO_URL_KEY = "PORTFOLIO_URL"
BROWSER_HEADLESS_KEY = "BROWSER_HEADLESS"
INFLUX_URL_KEY = "INFLUX_URL"
INFLUX_TOKEN_KEY = "INFLUX_TOKEN"
INFLUX_ORG_KEY = "INFLUX_ORG"
INFLUX_BUCKET_KEY = "INFLUX_BUCKET"

# Choose LLM provider based on .env
llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
if llm_provider == "anthropic":
    llm = ChatAnthropic(
        model_name=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620"),
        temperature=0.0,
        timeout=100
    )
    planner_llm = ChatAnthropic(
        model_name=os.getenv("ANTHROPIC_PLANNER_MODEL", "claude-3-5-sonnet-20240620"),
        temperature=0.0,
        timeout=100
    )
elif llm_provider == "ollama":
    llm = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
        num_ctx=int(os.getenv("OLLAMA_NUM_CTX", "32000"))
    )
    planner_llm = ChatOllama(
        model=os.getenv("OLLAMA_PLANNER_MODEL", "llama3.2:3b"),
        num_ctx=int(os.getenv("OLLAMA_NUM_CTX", "32000"))
    )
elif llm_provider == "google":
    llm = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"),
        api_key=os.getenv("GEMINI_API_KEY")
    )
    planner_llm = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_PLANNER_MODEL", "gemini-2.0-flash-exp"),
        api_key=os.getenv("GEMINI_API_KEY")
    )
else:  # Default to OpenAI
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini-2025-04-14")
    )
    planner_llm = ChatOpenAI(
        model=os.getenv("OPENAI_PLANNER_MODEL", "gpt-4.1-2025-04-14")
    )

# Read configuration from environment variables
PORTFOLIO_URL = os.getenv(PORTFOLIO_URL_KEY)
if not PORTFOLIO_URL:
    raise ValueError(f"{PORTFOLIO_URL_KEY} environment variable must be set.")

headless_env = os.getenv(BROWSER_HEADLESS_KEY, 'true').lower()
headless = headless_env in ['true', '1', 'yes']

import subprocess
import time
import requests
import sys

# We'll use an external Chrome instance that's already running in debug mode
debug_port = 9222
debug_url = f'http://localhost:{debug_port}'

# Check if Chrome is running in debug mode
try:
    response = requests.get(f'{debug_url}/json/version')
    if response.status_code != 200:
        print(f"Error: Chrome debug port returned status code {response.status_code}")
        print("Please run './launch_chrome_debug.sh' in a separate terminal first.")
        sys.exit(1)
    print(f"Successfully connected to Chrome debug instance at {debug_url}")
    print(f"Chrome version: {response.json().get('Browser')}")
except requests.exceptions.ConnectionError:
    print(f"Error: Could not connect to Chrome debug port at {debug_url}")
    print("Please run './launch_chrome_debug.sh' in a separate terminal first.")
    sys.exit(1)

config = BrowserConfig(
    # Connect to the Chrome instance using CDP
    cdp_url=debug_url,
    headless=headless,
    minimum_wait_page_load_time=2,
    wait_for_network_idle_page_load_time=4
)

browser = Browser(config=config)
initial_actions = [
    {"go_to_url": {"url": PORTFOLIO_URL}}
]

def init_influx_client():
    """Initialize InfluxDB client and return client, write_api, and bucket."""
    url = os.getenv(INFLUX_URL_KEY)
    token = os.getenv(INFLUX_TOKEN_KEY)
    org = os.getenv(INFLUX_ORG_KEY)
    bucket = os.getenv(INFLUX_BUCKET_KEY)
    if not all([url, token, org, bucket]):
        raise ValueError("InfluxDB configuration environment variables must be set.")
    client = InfluxDBClient(url=url, token=token, org=org)
    return client, client.write_api(), bucket

async def fetch_portfolio() -> Optional[str]:
    """Fetch portfolio data using the browser agent and return Wealth object."""
    task = (
        "Go to the following URL: "
        f"{PORTFOLIO_URL}. "
        "this is crypto portfolio in solana DeFi and Spot for multiple solana wallet. "
        "i want to create a raw information about this portofolio page"
        "scan until the end of the page"
        "grab all the information and output it in a markdown table."
        "it's okay if the markdown follow the same layout as the web page"
    )
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        initial_actions=initial_actions,
        enable_memory=True,
        planner_llm=planner_llm,
        use_vision_for_planner=True,
        message_context="You are a crypto portfolio expert. you are going to get all the necessary information about my portfolio position and create a portofolio markdown table as a raw data for executive report."
    )
    history = await agent.run()
    result = history.final_result()
    if not result:
        return None
    return result

async def main() -> None:
    """Main entry point: fetch portfolio and write to InfluxDB."""
    try:
        parsed = await fetch_portfolio()
        if parsed:
            print(parsed)
        else:
            print("No result found")
    finally:
        # Make sure to close the browser connection only
        # but leave the Chrome instance running
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())