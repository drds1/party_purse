"""LLM-based parsing of donation data"""

import openai
import json
from .config import load_config
from .schemas import FundingResponse, Funder

SYSTEM_PROMPT = """You are a political data analyst specializing in UK electoral finance.
Extract donation data into this JSON format:
[
  {"party": "...", "funder": "...", "amount_gbp": 0, "percentage": 0.0}
]
Only include top 90% cumulative funders. Sort by party then amount."""


def parse_with_llm(raw_data: str) -> FundingResponse:
    """Use LLM to structure raw donation data"""
    config = load_config()

    # Use DeepSeek or OpenAI
    client = openai.OpenAI(
        api_key=config.deepseek_api_key or config.openai_api_key,
        base_url="https://api.deepseek.com/v1" if config.deepseek_api_key else None,
    )

    response = client.chat.completions.create(
        model="deepseek-chat" if config.deepseek_api_key else "gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Raw data:\n{raw_data}"},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    # Parse and validate
    data = json.loads(response.choices[0].message.content)
    funders = [Funder(**item) for item in data.get("funders", [])]

    return FundingResponse(
        funders=funders, data_quality_note="Parsed by LLM, may contain errors"
    )
