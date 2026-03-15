"""Configuration management for Party Purse"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    """Application configuration"""
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    
    # Snowflake
    snowflake_account: str = os.getenv("SNOWFLAKE_ACCOUNT", "")
    snowflake_user: str = os.getenv("SNOWFLAKE_USER", "")
    snowflake_password: str = os.getenv("SNOWFLAKE_PASSWORD", "")
    snowflake_database: str = os.getenv("SNOWFLAKE_DATABASE", "PARTY_PURSE")
    snowflake_schema: str = os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC")
    
    # Parties to track
    parties: list = None
    
    def __post_init__(self):
        if self.parties is None:
            self.parties = ["Reform UK", "Labour", "Conservative", "Green Party"]

def load_config() -> Config:
    """Load configuration"""
    return Config()