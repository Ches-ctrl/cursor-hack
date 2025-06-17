import datetime as dt
import pandas as pd
import re
from pydantic import BaseModel, Field
from firecrawl import FirecrawlApp, ScrapeOptions
from .base import BaseScraper

LUMA_URL = "https://lu.ma/ai"

class HackEvent(BaseModel):
    title: str = Field(description="The title of the event")
    url: str = Field(description="The URL of the event")
    date: str = Field(description="The date of the event (YYYY-MM-DD)")
    location: str = Field(description="The location or venue of the event")

class HackEventsSchema(BaseModel):
    events: list[HackEvent] = Field(description="A list of hackathon events extracted from the page")

class FirecrawlScraper(BaseScraper):
    async def scrape(self, limit: int = 20) -> pd.DataFrame:
        print(f"\n🚀 Starting Firecrawl scraper (target: {limit} events)")
        app = FirecrawlApp()
        prompt = (
            "Extract all events from the page that are hackathons. "
            "For each event, extract: title, url, date (YYYY-MM-DD), and location. "
            "Only include events with 'hack' in the title. "
            "If the date is relative (e.g., 'today', 'tomorrow'), convert it to YYYY-MM-DD format. "
            "If the location is not available, leave it blank."
        )
        data = app.scrape_url(
            LUMA_URL,
            formats=["extract"],
            extract={
                "schema": HackEventsSchema.model_json_schema(),
                "prompt": prompt,
                "systemPrompt": "You are a helpful assistant that extracts hackathon event data from Lu.ma.",
            },
        )
        # Firecrawl returns a ScrapeResponse object; extract the events
        events = []
        if hasattr(data, "extract") and data.extract:
            events = data.extract.get("events", [])
        print(f"Events: {events}")
        # Filter for 'hack' in title (redundant if prompt works, but safe)
        filtered = [e for e in events if re.search(r"hack", e["title"], re.IGNORECASE)]
        print(f"\n✅ Scraping complete! Found {len(filtered)} unique hackathon events")
        # Always create DataFrame with the correct columns
        columns = ["title", "url", "date", "location", "source"]
        if filtered:
            df = pd.DataFrame(filtered)
            df["source"] = "firecrawl"
            df = df[columns]
        else:
            df = pd.DataFrame(columns=columns)
        return df
