"""Data scraping from Electoral Commission"""

from bs4 import BeautifulSoup
from typing import List, Dict


def fetch_electoral_data() -> str:
    """Fetch raw data from Electoral Commission"""
    # TODO: Implement actual scraping
    # Base URL: http://search.electoralcommission.org.uk/
    pass


def parse_html_tables(html: str) -> List[Dict]:
    """Extract donation data from HTML tables"""
    soup = BeautifulSoup(html, "html.parser")
    # TODO: Parse tables
    pass
