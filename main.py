from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig, Controller
import asyncio
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
load_dotenv()
import os
from influxdb_client import InfluxDBClient, Point, WritePrecision
from datetime import datetime, timezone

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

class net_worth(BaseModel):
    net_worth: float
    sol_equivalent: float

class Wealth(BaseModel):
    top_5_holdings: List[Asset]
    net_worth: net_worth
    top_5_platforms: List[Platform]

PORTFOLIO_URL = os.getenv('PORTFOLIO_URL')

# Read headless mode from .env (default True)
headless_env = os.getenv('BROWSER_HEADLESS', 'true').lower()
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

# InfluxDB helper functions
def init_influx_client():
    url = os.getenv('INFLUX_URL')
    token = os.getenv('INFLUX_TOKEN')
    org = os.getenv('INFLUX_ORG')
    bucket = os.getenv('INFLUX_BUCKET')
    client = InfluxDBClient(url=url, token=token, org=org)
    return client, client.write_api(), bucket

def write_portfolio_data(parsed: Wealth):
    client, write_api, bucket = init_influx_client()
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
    # Properly flush and close InfluxDB client and write API
    write_api.flush()
    write_api.close()
    client.close()

async def fetch_portfolio() -> Wealth:
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

async def main():
    parsed = await fetch_portfolio()
    if parsed:
        write_portfolio_data(parsed)
        print("Data written to InfluxDB")
    else:
        print("No result found")
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())