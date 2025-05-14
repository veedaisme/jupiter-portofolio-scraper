"""Configuration settings for the portfolio scraper application."""

import os
from typing import Optional

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.language_model import BaseLanguageModel

from src.config.constants import (
    LLM_PROVIDER_KEY, ANTHROPIC_MODEL_KEY, ANTHROPIC_PLANNER_MODEL_KEY,
    OLLAMA_MODEL_KEY, OLLAMA_PLANNER_MODEL_KEY, OLLAMA_NUM_CTX_KEY,
    GEMINI_MODEL_KEY, GEMINI_PLANNER_MODEL_KEY, GEMINI_API_KEY,
    OPENAI_MODEL_KEY, OPENAI_PLANNER_MODEL_KEY, PORTFOLIO_URL_KEY,
    BROWSER_HEADLESS_KEY, DEFAULT_OPENAI_MODEL, DEFAULT_OPENAI_PLANNER_MODEL,
    DEFAULT_ANTHROPIC_MODEL, DEFAULT_OLLAMA_MODEL, DEFAULT_OLLAMA_NUM_CTX,
    DEFAULT_GEMINI_MODEL
)

# Load environment variables
load_dotenv()


def get_portfolio_url() -> str:
    """Get the portfolio URL from environment variables."""
    portfolio_url = os.getenv(PORTFOLIO_URL_KEY)
    if not portfolio_url:
        raise ValueError(f"{PORTFOLIO_URL_KEY} environment variable must be set.")
    return portfolio_url


def get_browser_headless() -> bool:
    """Get the browser headless setting from environment variables."""
    headless_env = os.getenv(BROWSER_HEADLESS_KEY, 'true').lower()
    return headless_env in ['true', '1', 'yes']


def get_llm_models() -> tuple[BaseLanguageModel, BaseLanguageModel]:
    """
    Get the LLM models based on environment variables.
    
    Returns:
        tuple: (main_llm, planner_llm)
    """
    llm_provider = os.getenv(LLM_PROVIDER_KEY, "openai").lower()
    
    if llm_provider == "anthropic":
        main_llm = ChatAnthropic(
            model_name=os.getenv(ANTHROPIC_MODEL_KEY, DEFAULT_ANTHROPIC_MODEL),
            temperature=0.0,
            timeout=100
        )
        planner_llm = ChatAnthropic(
            model_name=os.getenv(ANTHROPIC_PLANNER_MODEL_KEY, DEFAULT_ANTHROPIC_MODEL),
            temperature=0.0,
            timeout=100
        )
    elif llm_provider == "ollama":
        num_ctx = int(os.getenv(OLLAMA_NUM_CTX_KEY, DEFAULT_OLLAMA_NUM_CTX))
        main_llm = ChatOllama(
            model=os.getenv(OLLAMA_MODEL_KEY, DEFAULT_OLLAMA_MODEL),
            num_ctx=num_ctx
        )
        planner_llm = ChatOllama(
            model=os.getenv(OLLAMA_PLANNER_MODEL_KEY, DEFAULT_OLLAMA_MODEL),
            num_ctx=num_ctx
        )
    elif llm_provider == "google":
        api_key = os.getenv(GEMINI_API_KEY)
        if not api_key:
            raise ValueError(f"{GEMINI_API_KEY} environment variable must be set for Google provider.")
        
        main_llm = ChatGoogleGenerativeAI(
            model=os.getenv(GEMINI_MODEL_KEY, DEFAULT_GEMINI_MODEL),
            api_key=api_key
        )
        planner_llm = ChatGoogleGenerativeAI(
            model=os.getenv(GEMINI_PLANNER_MODEL_KEY, DEFAULT_GEMINI_MODEL),
            api_key=api_key
        )
    else:  # Default to OpenAI
        main_llm = ChatOpenAI(
            model=os.getenv(OPENAI_MODEL_KEY, DEFAULT_OPENAI_MODEL)
        )
        planner_llm = ChatOpenAI(
            model=os.getenv(OPENAI_PLANNER_MODEL_KEY, DEFAULT_OPENAI_PLANNER_MODEL)
        )
    
    return main_llm, planner_llm
