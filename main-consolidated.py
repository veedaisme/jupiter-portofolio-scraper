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
elif llm_provider == "ollama":
    llm = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
        num_ctx=int(os.getenv("OLLAMA_NUM_CTX", "32000"))
    )
elif llm_provider == "google":
    llm = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"),
        api_key=os.getenv("GEMINI_API_KEY")
    )
else:  # Default to OpenAI
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "o4-mini-04-16")
    )

# Read configuration from environment variables
PORTFOLIO_URL = os.getenv(PORTFOLIO_URL_KEY)
if not PORTFOLIO_URL:
    raise ValueError(f"{PORTFOLIO_URL_KEY} environment variable must be set.")

headless_env = os.getenv(BROWSER_HEADLESS_KEY, 'true').lower()
headless = headless_env in ['true', '1', 'yes']

config = BrowserConfig(
    browser_binary_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    # cdp_url="http://192.168.68.124:9222",
    headless=headless,
    minimum_wait_page_load_time=1,
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
        "the goal is to consolidate networth for each wallet on every platform. "
        "you can see the wallet address on every table in the platform section, "
        "but, for holdings section how to see which wallet address is associated with each holding is by click the info button then it will show the breakdown wallet"
        "total all the wallet address networth for each platform in USD"
        "Output the summary in a markdown table."
    )
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        initial_actions=initial_actions
    )
    history = await agent.run()
    result = history.final_result()
    if not result:
        return None
    return result

async def main() -> None:
    """Main entry point: fetch portfolio and write to InfluxDB."""
    parsed = await fetch_portfolio()
    if parsed:
        print(parsed)
    else:
        print("No result found")
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())