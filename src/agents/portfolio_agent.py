"""Portfolio agent for scraping and processing portfolio data."""

import json
from typing import Optional, List, Dict, Any, Union, Tuple

from src.config.settings import get_planner_reasoning
from browser_use import Agent, Browser, Controller
from langchain.schema.language_model import BaseLanguageModel

from src.services.influx_service import Wealth
from src.utils.logging_utils import logger


class PortfolioAgent:
    """Agent for scraping and processing portfolio data."""
    
    def __init__(
        self,
        browser: Browser,
        main_llm: BaseLanguageModel,
        planner_llm: BaseLanguageModel,
        portfolio_url: str
    ):
        """
        Initialize the portfolio agent.
        
        Args:
            browser: Browser instance
            main_llm: Main language model
            planner_llm: Planner language model
            portfolio_url: URL of the portfolio to scrape
        """
        self.browser = browser
        self.main_llm = main_llm
        self.planner_llm = planner_llm
        self.portfolio_url = portfolio_url
        self.initial_actions = [
            {"go_to_url": {"url": portfolio_url}}
        ]
    
    async def fetch_raw_portfolio_data(self) -> Optional[str]:
        """
        Fetch raw portfolio data using the browser agent.
        
        Returns:
            str: Portfolio data in markdown format or None if failed
        """
        task = (
            "Go to the following URL: "
            f"{self.portfolio_url}. "
            "This page contains comprehensive data on a Solana-based crypto portfolio, including DeFi and Spot positions across multiple wallets. "
            "Your objective is to extract all portfolio information and structure it in a detailed markdown format suitable for an executive strategic report. "
            "Perform the following steps:\n"
            "1. Load the page and wait for all dynamic content to render (e.g., portfolio values, platform positions, asset holdings).\n"
            "2. Scroll to the bottom to ensure all lazy-loaded content is visible.\n"
            "3. Extract the following data:\n"
            "   - Net worth (in USD and SOL equivalent).\n"
            "   - Number of wallets.\n"
            "   - Portfolio positions by platform (e.g., Kamino, Drift, Holdings), including values and categories (e.g., Lending, Leverage, Staked).\n"
            "   - Asset holdings (e.g., USDC, wSOL, JitoSOL), including values and types (stablecoin vs. non-stablecoin).\n"
            "   - Stablecoin vs. non-stablecoin ratio.\n"
            "   - Any notes or consolidated 'Other' categories for minor platforms or categories.\n"
            "4. Handle dynamic elements (e.g., modals, tooltips) by interacting with them if necessary to reveal hidden data.\n"
            "5. Consolidate small positions (e.g., platforms or categories with values < $10) into an 'Other' category with detailed notes.\n"
            "6. Output the data in a structured markdown format with clear sections, tables, and notes, optimized for executive analysis.\n"
            "7. Include a summary section highlighting key metrics (e.g., net worth, stablecoin ratio, top platforms/assets).\n"
            "Ensure accuracy by cross-checking values and retrying on transient errors. Avoid duplicating data and handle missing or incomplete elements gracefully."
        )
        
        agent = Agent(
            task=task,
            llm=self.main_llm,
            browser=self.browser,
            initial_actions=self.initial_actions,
            enable_memory=True,
            planner_llm=self.planner_llm,
            use_vision_for_planner=True,
            planner_interval=2,
            message_context=(
                "You are a crypto portfolio expert with a focus on Solana DeFi and Spot investments. "
                "Your role is to provide a thorough and accurate analysis of the portfolio for strategic decision-making. "
                "Prioritize capital preservation and risk mitigation in your data collection approach. "
                "Capture all relevant details, including platform-specific strategies (e.g., lending, leverage, farming), asset allocations, and stablecoin exposure. "
                "Structure the output to facilitate executive-level insights, emphasizing clarity, completeness, and actionable data."
            ),
            is_planner_reasoning=get_planner_reasoning(),
        )
        
        try:
            logger.info("Fetching raw portfolio data...")
            history = await agent.run()
            result = history.final_result()
            logger.info("Raw portfolio data fetched successfully")
            return result
        except Exception as e:
            logger.error(f"Error fetching raw portfolio data: {e}")
            return None
    
    async def fetch_structured_portfolio_data(self) -> Optional[Wealth]:
        """
        Fetch structured portfolio data using the browser agent.
        
        Returns:
            Wealth: Structured portfolio data or None if failed
        """
        task = (
            "Go to the following URL: "
            f"{self.portfolio_url}. "
            "Grab the net worth information. "
            "Grab the top 5 platforms from the chart. "
            "Click on the 'Assets' switcher. "
            "Grab the top 5 Assets from the chart and not from holding list. "
            "Output the summary in a JSON format."
        )
        
        controller = Controller(output_model=Wealth)
        
        agent = Agent(
            task=task,
            llm=self.main_llm,
            browser=self.browser,
            controller=controller,
            initial_actions=self.initial_actions
        )
        
        try:
            logger.info("Fetching structured portfolio data...")
            history = await agent.run(max_steps=25)
            result = history.final_result()
            if not result:
                logger.error("No structured portfolio data found")
                return None
            
            # Parse the JSON result into a Wealth object
            wealth_data = Wealth.model_validate_json(result)
            logger.info("Structured portfolio data fetched successfully")
            return wealth_data
        except Exception as e:
            logger.error(f"Error fetching structured portfolio data: {e}")
            return None
    
    async def fetch_portfolio_data(self, data_type: str = "raw") -> Union[str, Wealth, Tuple[str, Wealth], None]:
        """
        Fetch portfolio data using the browser agent.
        
        Args:
            data_type: Type of data to fetch ('raw', 'structured', or 'both')
            
        Returns:
            Union[str, Wealth, Tuple[str, Wealth], None]: Portfolio data in the requested format
        """
        if data_type.lower() == "raw":
            return await self.fetch_raw_portfolio_data()
        elif data_type.lower() == "structured":
            return await self.fetch_structured_portfolio_data()
        elif data_type.lower() == "both":
            raw_data = await self.fetch_raw_portfolio_data()
            structured_data = await self.fetch_structured_portfolio_data()
            if raw_data and structured_data:
                return raw_data, structured_data
            elif raw_data:
                return raw_data
            elif structured_data:
                return structured_data
            else:
                return None
        else:
            logger.error(f"Invalid data_type: {data_type}. Must be 'raw', 'structured', or 'both'.")
            return None
