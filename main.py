import os
import asyncio
from datetime import datetime, timezone
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel
from influxdb_client import InfluxDBClient, Point, WritePrecision

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

class Asset(BaseModel):
    asset: str
    value: float
    percentage: float

class Platform(BaseModel):
    platform: str
    value: float
    percentage: float

class NetWorth(BaseModel):
    """Represents net worth and its SOL equivalent."""
    net_worth: float
    sol_equivalent: float

class Wealth(BaseModel):
    """Represents the user's portfolio summary."""
    top_5_holdings: List[Asset]
    net_worth: NetWorth
    top_5_platforms: List[Platform]

# Read configuration from environment variables
PORTFOLIO_URL = os.getenv(PORTFOLIO_URL_KEY)
if not PORTFOLIO_URL:
    raise ValueError(f"{PORTFOLIO_URL_KEY} environment variable must be set.")

headless_env = os.getenv(BROWSER_HEADLESS_KEY, 'true').lower()
headless = headless_env in ['true', '1', 'yes']

config = BrowserConfig(
    browser_binary_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    headless=headless,
    minimum_wait_page_load_time=1,
    wait_for_network_idle_page_load_time=3
)

browser = Browser(config=config)
controller = Controller(output_model=Wealth)
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

def write_portfolio_data(parsed: Wealth) -> None:
    """Write portfolio data to InfluxDB from parsed Wealth object."""
    client, write_api, bucket = init_influx_client()
    try:
        # Net worth point
        point_net = (
            Point('portfolio')
            .field('net_worth', parsed.net_worth.net_worth)
            .field('sol_equivalent', parsed.net_worth.sol_equivalent)
            .time(datetime.now(timezone.utc), WritePrecision.NS)
        )
        print(f"Writing net worth: {point_net.to_line_protocol()}")
        write_api.write(bucket=bucket, record=point_net)
        # Top holdings
        for holding in parsed.top_5_holdings:
            point_h = (
                Point('portfolio_holding')
                .tag('asset', holding.asset)
                .field('percentage', holding.percentage)
                .field('value', holding.value)
                .time(datetime.now(timezone.utc), WritePrecision.NS)
            )
            print(f"Writing holding: {point_h.to_line_protocol()}")
            write_api.write(bucket=bucket, record=point_h)
        # Top platforms
        for plat in parsed.top_5_platforms:
            point_p = (
                Point('portfolio_platform')
                .tag('platform', plat.platform)
                .field('percentage', plat.percentage)
                .field('value', plat.value)
                .time(datetime.now(timezone.utc), WritePrecision.NS)
            )
            print(f"Writing platform: {point_p.to_line_protocol()}")
            write_api.write(bucket=bucket, record=point_p)
        write_api.flush()
    except Exception as e:
        print(f"Error writing to InfluxDB: {e}")
    finally:
        write_api.close()
        client.close()

async def fetch_portfolio() -> Optional[Wealth]:
    """Fetch portfolio data using the browser agent and return Wealth object."""
    task = (
        "Go to the following URL: "
        f"{PORTFOLIO_URL}. "
        "Analyze the asset table on the screen. "
        "grab the net worth information."
        "grab the top 5 platforms from the chart."
        "click on the 'Assets' switcher"
        "grab the top 5 Assets from the chart"
        "Output the summary in a markdown table."
    )
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        controller=controller,
        initial_actions=initial_actions
    )
    history = await agent.run()
    result = history.final_result()
    if not result:
        return None
    return Wealth.model_validate_json(result)

async def main() -> None:
    """Main entry point: fetch portfolio and write to InfluxDB."""
    parsed = await fetch_portfolio()
    if parsed:
        write_portfolio_data(parsed)
        print("Data written to InfluxDB")
    else:
        print("No result found")
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())