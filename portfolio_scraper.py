#!/usr/bin/env python3
"""
Portfolio Scraper - Entry point script

This script serves as the main entry point for the portfolio scraper application.
It imports and runs the main function from the src.main module.
"""

import asyncio
from src.main import main

if __name__ == "__main__":
    asyncio.run(main())
