"""Main entry point for the portfolio scraper application."""

import asyncio
import argparse
import logging
from typing import Optional, Union, Tuple

from src.config.settings import get_portfolio_url, get_browser_headless, get_llm_models
from src.services.browser_service import BrowserService
from src.services.influx_service import InfluxService, Wealth
from src.agents.portfolio_agent import PortfolioAgent
from src.utils.logging_utils import logger, log_exception, setup_logger


async def run_portfolio_scraper(data_type: str = "both", store_in_influxdb: bool = True) -> None:
    """Run the portfolio scraper with the specified options.
    
    Args:
        data_type: Type of data to fetch ('raw', 'structured', or 'both')
        store_in_influxdb: Whether to store the data in InfluxDB
    """
    browser = None
    
    try:
        # Get configuration
        portfolio_url = get_portfolio_url()
        headless = get_browser_headless()
        main_llm, planner_llm = get_llm_models()
        
        # Initialize browser
        browser = BrowserService.create_browser(headless=headless)
        if not browser:
            logger.error("Failed to initialize browser")
            return
        
        # Initialize portfolio agent
        portfolio_agent = PortfolioAgent(
            browser=browser,
            main_llm=main_llm,
            planner_llm=planner_llm,
            portfolio_url=portfolio_url
        )
        
        # Fetch portfolio data
        logger.info(f"Fetching portfolio data (type: {data_type})...")
        portfolio_data = await portfolio_agent.fetch_portfolio_data(data_type=data_type)
        
        if not portfolio_data:
            logger.error("No portfolio data found")
            return
        
        # Output portfolio data based on type
        logger.info("Portfolio data fetched successfully")
        print("\n" + "="*80 + "\n")
        
        # Handle different return types based on data_type
        raw_data = None
        structured_data = None
        
        if data_type == "both" and isinstance(portfolio_data, tuple):
            raw_data, structured_data = portfolio_data
            print("=== RAW PORTFOLIO DATA ===")
            print(raw_data)
            print("\n=== STRUCTURED PORTFOLIO DATA ===")
            print(f"Net Worth: ${structured_data.net_worth.net_worth:.2f} (SOL: {structured_data.net_worth.sol_equivalent:.2f})")
            print("\nTop 5 Holdings:")
            for asset in structured_data.top_5_holdings:
                print(f"- {asset.asset}: ${asset.value:.2f} ({asset.percentage:.2f}%)")
            print("\nTop 5 Platforms:")
            for platform in structured_data.top_5_platforms:
                print(f"- {platform.platform}: ${platform.value:.2f} ({platform.percentage:.2f}%)")
        elif data_type == "raw" or isinstance(portfolio_data, str):
            raw_data = portfolio_data
            print(raw_data)
        elif data_type == "structured" or isinstance(portfolio_data, Wealth):
            structured_data = portfolio_data
            print(f"Net Worth: ${structured_data.net_worth.net_worth:.2f} (SOL: {structured_data.net_worth.sol_equivalent:.2f})")
            print("\nTop 5 Holdings:")
            for asset in structured_data.top_5_holdings:
                print(f"- {asset.asset}: ${asset.value:.2f} ({asset.percentage:.2f}%)")
            print("\nTop 5 Platforms:")
            for platform in structured_data.top_5_platforms:
                print(f"- {platform.platform}: ${platform.value:.2f} ({platform.percentage:.2f}%)")
        
        print("\n" + "="*80 + "\n")
        
        # Store in InfluxDB if requested
        if store_in_influxdb:
            # Initialize InfluxDB client
            client = None
            write_api = None
            try:
                client, write_api, bucket = InfluxService.init_client()
                if all([client, write_api, bucket]):
                    # Determine what to write based on available data
                    if raw_data and structured_data:
                        # Write both types of data
                        raw_success = InfluxService.write_portfolio_data(
                            write_api=write_api,
                            bucket=bucket,
                            data=raw_data,
                            tags={"data_type": "raw"}
                        )
                        structured_success = InfluxService.write_portfolio_data(
                            write_api=write_api,
                            bucket=bucket,
                            data=structured_data
                        )
                        if raw_success and structured_success:
                            logger.info("Both raw and structured portfolio data written to InfluxDB")
                        elif raw_success:
                            logger.info("Only raw portfolio data written to InfluxDB")
                        elif structured_success:
                            logger.info("Only structured portfolio data written to InfluxDB")
                        else:
                            logger.warning("Failed to write portfolio data to InfluxDB")
                    else:
                        # Write whatever data we have
                        success = InfluxService.write_portfolio_data(
                            write_api=write_api,
                            bucket=bucket,
                            data=portfolio_data,
                            tags={"data_type": "raw"} if isinstance(portfolio_data, str) else None
                        )
                        if success:
                            logger.info("Portfolio data written to InfluxDB")
                        else:
                            logger.warning("Failed to write portfolio data to InfluxDB")
                else:
                    logger.warning("InfluxDB client not initialized, skipping data storage")
            except Exception as e:
                log_exception(e, "Error writing to InfluxDB")
            finally:
                # Ensure resources are properly released
                if write_api:
                    try:
                        write_api.close()
                    except Exception:
                        pass
                if client:
                    try:
                        client.close()
                    except Exception:
                        pass
        
    except Exception as e:
        log_exception(e, "Error in portfolio scraper")
    finally:
        # Close browser connection
        if browser:
            try:
                await browser.close()
                logger.info("Browser connection closed")
            except Exception as e:
                log_exception(e, "Error closing browser connection")


async def main() -> None:
    """Main entry point for the application."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Portfolio Scraper")
    parser.add_argument(
        "--data-type", 
        type=str, 
        choices=["raw", "structured", "both"], 
        default="both",
        help="Type of data to fetch (raw, structured, or both)"
    )
    parser.add_argument(
        "--no-influxdb", 
        action="store_true", 
        help="Do not store data in InfluxDB"
    )
    parser.add_argument(
        "--log-level", 
        type=str, 
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], 
        default="INFO",
        help="Set the logging level"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set up logger with specified level
    setup_logger("portfolio_scraper", getattr(logging, args.log_level))
    
    # Run the portfolio scraper
    await run_portfolio_scraper(
        data_type=args.data_type,
        store_in_influxdb=not args.no_influxdb
    )


if __name__ == "__main__":
    import logging
    asyncio.run(main())
