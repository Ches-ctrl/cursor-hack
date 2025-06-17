import pandas as pd
import re
import os
from serpapi import Client
from .base import BaseScraper

class SerpApiScraper(BaseScraper):
    async def scrape(self, limit: int = 20) -> pd.DataFrame:
        print(f"\n🚀 Starting SerpApi scraper (target: {limit} events)")
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            raise ValueError("SERPAPI_API_KEY environment variable not set.")
        client = Client(api_key=api_key)
        query = "hack london site:lu.ma"
        params = {
            "engine": "google",
            "q": query,
            "num": limit,
        }
        results = client.search(params)
        events = []
        for item in results.get("organic_results", []):
            title = item.get("title", "")
            url = item.get("link", "")
            snippet = item.get("snippet", "")
            # Try to extract a date from the snippet (very basic)
            date_match = re.search(r"(\d{1,2} \w+ \d{4})", snippet)
            date = date_match.group(1) if date_match else ""
            location = "London" if re.search(r"london", snippet, re.IGNORECASE) else ""
            if re.search(r"hack", title, re.IGNORECASE):
                print(f"✨ Scraped: {title}")
                events.append({
                    "title": title,
                    "url": url,
                    "date": date,
                    "location": location,
                    "source": "serpapi"
                })
        print(f"\n✅ Scraping complete! Found {len(events)} unique hackathon events")
        df = pd.DataFrame(events)
        return df
