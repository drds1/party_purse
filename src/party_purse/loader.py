"""Snowflake data loading"""

import pandas as pd
from snowflake.connector import connect
from .config import load_config
from .schemas import FundingResponse


def load_to_snowflake(data: FundingResponse):
    """Load structured data into Snowflake"""
    config = load_config()

    # Convert to DataFrame
    df = pd.DataFrame([f.dict() for f in data.funders])

    # Connect to Snowflake
    conn = connect(
        account=config.snowflake_account,
        user=config.snowflake_user,
        password=config.snowflake_password,
        database=config.snowflake_database,
        schema=config.snowflake_schema,
    )

    # Load data
    # TODO: Implement actual loading logic

    conn.close()
