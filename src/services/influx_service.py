"""InfluxDB service for managing database connections and operations."""

import os
from datetime import datetime, timezone
from typing import Optional, Tuple, Any, Dict, List, Union

from influxdb_client import InfluxDBClient, WriteApi, Point, WritePrecision
from pydantic import BaseModel

from src.config.constants import (
    INFLUX_URL_KEY,
    INFLUX_TOKEN_KEY,
    INFLUX_ORG_KEY,
    INFLUX_BUCKET_KEY
)


# Data models for portfolio data
class Asset(BaseModel):
    """Represents an asset in the portfolio."""
    asset: str
    value: float
    percentage: float


class Platform(BaseModel):
    """Represents a platform in the portfolio."""
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


class InfluxService:
    """Service for managing InfluxDB connections and operations."""
    
    @staticmethod
    def init_client() -> Tuple[Optional[InfluxDBClient], Optional[WriteApi], Optional[str]]:
        """
        Initialize InfluxDB client.
        
        Returns:
            tuple: (client, write_api, bucket) or (None, None, None) if configuration is missing
        """
        url = os.getenv(INFLUX_URL_KEY)
        token = os.getenv(INFLUX_TOKEN_KEY)
        org = os.getenv(INFLUX_ORG_KEY)
        bucket = os.getenv(INFLUX_BUCKET_KEY)
        
        if not all([url, token, org, bucket]):
            print("Warning: InfluxDB configuration environment variables not fully set.")
            return None, None, None
            
        try:
            client = InfluxDBClient(url=url, token=token, org=org)
            return client, client.write_api(), bucket
        except Exception as e:
            print(f"Error initializing InfluxDB client: {e}")
            return None, None, None
    
    @staticmethod
    def write_structured_portfolio_data(write_api: WriteApi, bucket: str, data: Wealth) -> bool:
        """
        Write structured portfolio data to InfluxDB.
        
        Args:
            write_api: InfluxDB write API
            bucket: InfluxDB bucket name
            data: Structured portfolio data (Wealth object)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not all([write_api, bucket, data]):
            return False
            
        try:
            # Net worth point
            point_net = (
                Point('portfolio')
                .field('net_worth', data.net_worth.net_worth)
                .field('sol_equivalent', data.net_worth.sol_equivalent)
                .time(datetime.now(timezone.utc), WritePrecision.NS)
            )
            print(f"Writing net worth: {point_net.to_line_protocol()}")
            write_api.write(bucket=bucket, record=point_net)
            
            # Top holdings
            for holding in data.top_5_holdings:
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
            for plat in data.top_5_platforms:
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
            return True
        except Exception as e:
            print(f"Error writing structured data to InfluxDB: {e}")
            return False
    
    @staticmethod
    def write_raw_portfolio_data(write_api: WriteApi, bucket: str, data: str, tags: Dict[str, str] = None) -> bool:
        """
        Write raw portfolio data (markdown text) to InfluxDB.
        
        Args:
            write_api: InfluxDB write API
            bucket: InfluxDB bucket name
            data: Raw portfolio data as markdown string
            tags: Optional tags to include
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not all([write_api, bucket, data]):
            return False
            
        try:
            # Create a point with the raw data
            point = Point('portfolio_raw')
            
            # Add any tags if provided
            if tags:
                for tag_key, tag_value in tags.items():
                    point = point.tag(tag_key, tag_value)
            
            # Add the raw data as a field
            # Note: InfluxDB has limits on field sizes, so this might need to be chunked for very large reports
            # For simplicity, we're storing it as one field, but in production you might need to chunk it
            point = point.field('raw_data', data[:65000])  # Limiting to 65KB to avoid potential issues
            
            # Add timestamp
            point = point.time(datetime.now(timezone.utc), WritePrecision.NS)
            
            print(f"Writing raw portfolio data to InfluxDB")
            write_api.write(bucket=bucket, record=point)
            write_api.flush()
            return True
        except Exception as e:
            print(f"Error writing raw data to InfluxDB: {e}")
            return False
            
    @staticmethod
    def write_portfolio_data(write_api: WriteApi, bucket: str, data: Union[str, Wealth], tags: Dict[str, str] = None) -> bool:
        """
        Write portfolio data to InfluxDB, handling both structured and raw data.
        
        Args:
            write_api: InfluxDB write API
            bucket: InfluxDB bucket name
            data: Portfolio data (either Wealth object or raw markdown string)
            tags: Optional tags to include
            
        Returns:
            bool: True if successful, False otherwise
        """
        if isinstance(data, Wealth):
            return InfluxService.write_structured_portfolio_data(write_api, bucket, data)
        elif isinstance(data, str):
            return InfluxService.write_raw_portfolio_data(write_api, bucket, data, tags)
        else:
            print(f"Unsupported data type: {type(data)}")
            return False
