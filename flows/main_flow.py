from metaflow import FlowSpec, step, Parameter, current
import pandas as pd
from datetime import datetime
import logging
from pathlib import Path
import sys

# Add project root to path so we can import from settings
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import Dynaconf settings
from settings.settings import settings

# Import your project modules
from src.party_purse.scraper import fetch_electoral_data
from src.party_purse.parser import parse_with_llm
from src.party_purse.loader import load_to_snowflake
from src.party_purse.schemas import FundingResponse

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class PartyPurseFlow(FlowSpec):
    """Party Purse ETL Pipeline using Metaflow

    Tracks UK political party funding by:
    - Extracting data from Electoral Commission
    - Transforming with LLM parsing into structured JSON
    - Loading into Snowflake

    Run with: python flows/main_flow.py run
    """

    # Parameters you can override at runtime
    parties = Parameter(
        "parties",
        help="Comma-separated list of parties to track (overrides settings.toml)",
        default=",".join(settings.parties_tracked),
    )

    force_refresh = Parameter(
        "force-refresh", help="Force refresh of all data even if cached", default=False
    )

    environment = Parameter(
        "env",
        help="Environment to run in (development/staging/production)",
        default=settings.environment,
    )

    @step
    def start(self):
        """Initialize the flow and load configuration"""
        logger.info("🚀 Starting Party Purse ETL pipeline")
        logger.info(f"Environment: {self.environment}")

        # Load configuration from Dynaconf settings
        self.config = {
            "project_name": settings.project_name,
            "log_level": settings.log_level,
            "timeout_seconds": settings.timeout_seconds,
            "retry_attempts": settings.retry_attempts,
            "electoral_commission_url": settings.electoral_commission_url,
        }

        # Parse parties parameter
        self.parties_list = [p.strip() for p in self.parties.split(",")]
        logger.info(f"Tracking parties: {self.parties_list}")

        # Initialize flow metadata
        self.run_id = current.run_id
        self.timestamp = datetime.now().isoformat()

        # Log which LLM we're using
        if settings.deepseek_api_key:
            logger.info(f"Using DeepSeek model: {settings.llm_model}")
        elif settings.openai_api_key:
            logger.info(f"Using OpenAI model: {settings.openai_api_key}")
        else:
            logger.warning("No LLM API keys found in settings or .env")

        # Next step
        self.next(self.extract)

    @step
    def extract(self):
        """Extract raw data from Electoral Commission"""
        logger.info("📥 Extracting data from Electoral Commission")

        try:
            # Fetch raw data with settings from Dynaconf
            self.raw_data = fetch_electoral_data(
                parties=self.parties_list,
                force_refresh=self.force_refresh,
                timeout=settings.timeout_seconds,
                retries=settings.retry_attempts,
                base_url=settings.electoral_commission_url,
            )

            # Store metadata
            self.extract_stats = {
                "records_fetched": (
                    len(self.raw_data) if isinstance(self.raw_data, list) else 1
                ),
                "data_source": "Electoral Commission API",
                "timestamp": self.timestamp,
            }

            logger.info(f"✅ Extracted {self.extract_stats['records_fetched']} records")

        except Exception as e:
            logger.error(f"❌ Extraction failed: {e}")
            # Handle failure gracefully
            self.raw_data = None
            self.extract_stats = {"error": str(e)}

        self.next(self.transform)

    @step
    def transform(self):
        """Transform raw data using LLM parsing"""
        logger.info("🔄 Transforming data with LLM")

        if self.raw_data is None:
            logger.warning("No raw data to transform, skipping")
            self.structured_data = FundingResponse(funders=[])
            self.transform_stats = {"skipped": True, "reason": "No raw data"}
            self.next(self.load)
            return

        try:
            # Parse with LLM using API keys from Dynaconf
            llm_config = {
                "model": settings.llm_model,
                "temperature": settings.llm_temperature,
                "deepseek_api_key": settings.get("deepseek_api_key"),
                "openai_api_key": settings.get("openai_api_key"),
            }

            self.structured_data = parse_with_llm(
                raw_data=self.raw_data, parties=self.parties_list, llm_config=llm_config
            )

            # Validate and collect stats
            self.transform_stats = {
                "funders_extracted": len(self.structured_data.funders),
                "parties_covered": list(
                    set(f.party for f in self.structured_data.funders)
                ),
                "total_amount": sum(f.amount_gbp for f in self.structured_data.funders),
                "data_quality_note": self.structured_data.data_quality_note,
            }

            logger.info(
                f"✅ Extracted {self.transform_stats['funders_extracted']} funder records"
            )
            logger.info(
                f"💰 Total tracked donations: £{self.transform_stats['total_amount']:,}"
            )

        except Exception as e:
            logger.error(f"❌ Transformation failed: {e}")
            self.structured_data = FundingResponse(funders=[])
            self.transform_stats = {"error": str(e)}

        self.next(self.load)

    @step
    def load(self):
        """Load structured data to Snowflake"""
        logger.info("📤 Loading data to Snowflake")

        if not self.structured_data.funders:
            logger.warning("No structured data to load, skipping")
            self.load_stats = {"skipped": True, "reason": "No data to load"}
            self.next(self.end)
            return

        try:
            # Prepare Snowflake config from Dynaconf
            snowflake_config = {
                "account": settings.snowflake_account,
                "database": settings.snowflake_database,
                "schema": settings.snowflake_schema,
                "warehouse": settings.snowflake_warehouse,
                "user": settings.snowflake_user,  # From .env
                "password": settings.snowflake_password,  # From .env
            }

            # Load to Snowflake
            load_stats = load_to_snowflake(
                data=self.structured_data,
                snowflake_config=snowflake_config,
                run_id=self.run_id,
                environment=self.environment,
            )

            self.load_stats = {
                "records_loaded": len(self.structured_data.funders),
                "destination": f"{snowflake_config['database']}.{snowflake_config['schema']}.FUNDING",
                "success": True,
                **load_stats,
            }

            logger.info(
                f"✅ Loaded {self.load_stats['records_loaded']} records to Snowflake"
            )

        except Exception as e:
            logger.error(f"❌ Load failed: {e}")
            self.load_stats = {"error": str(e), "success": False}

        self.next(self.end)

    @step
    def end(self):
        """Complete the flow and summarize results"""
        logger.info("✅ Party Purse ETL pipeline complete")

        # Create summary DataFrame for easy viewing
        summary_data = []

        if hasattr(self, "structured_data") and self.structured_data.funders:
            for funder in self.structured_data.funders:
                summary_data.append(
                    {
                        "party": funder.party,
                        "funder": funder.funder,
                        "amount_gbp": funder.amount_gbp,
                        "percentage": funder.percentage,
                    }
                )

        self.results = pd.DataFrame(summary_data)

        # Print beautiful summary
        print("\n" + "=" * 70)
        print(" 🫰  PARTY PURSE - FLOW SUMMARY  🫰 ".center(70))
        print("=" * 70)
        print(f"Run ID:        {self.run_id}")
        print(f"Timestamp:     {self.timestamp}")
        print(f"Environment:   {self.environment}")
        print(f"Parties:       {', '.join(self.parties_list)}")
        print("-" * 70)

        # Extraction stats
        print("\n📊 EXTRACTION:")
        for k, v in self.extract_stats.items():
            print(f"  {k.replace('_', ' ').title()}: {v}")

        # Transformation stats
        print("\n🔄 TRANSFORMATION:")
        for k, v in self.transform_stats.items():
            if k == "total_amount" and isinstance(v, (int, float)):
                print(f"  {k.replace('_', ' ').title()}: £{v:,.0f}")
            else:
                print(f"  {k.replace('_', ' ').title()}: {v}")

        # Load stats
        print("\n📤 LOAD:")
        for k, v in self.load_stats.items():
            print(f"  {k.replace('_', ' ').title()}: {v}")

        # Show top donors if we have data
        if not self.results.empty:
            print("\n💰 TOP DONORS BY PARTY:")
            for party in self.parties_list:
                party_data = self.results[self.results["party"] == party]
                if not party_data.empty:
                    top = party_data.iloc[0]
                    print(f"  {party}:")
                    print(f"    🥇 {top['funder']}")
                    print(f"       £{top['amount_gbp']:,} ({top['percentage']}%)")

                    if len(party_data) > 1:
                        second = party_data.iloc[1]
                        print(f"    🥈 {second['funder']}")
                        print(
                            f"       £{second['amount_gbp']:,} ({second['percentage']}%)"
                        )

        print("\n" + "=" * 70)

        # Persist results as Metaflow artifacts for later inspection
        self.funders_list = (
            [f.dict() for f in self.structured_data.funders]
            if hasattr(self, "structured_data")
            else []
        )

        logger.info("🎉 Flow completed successfully!")


if __name__ == "__main__":
    PartyPurseFlow()
