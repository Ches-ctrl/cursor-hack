import datetime as dt
import pandas as pd
import re
from playwright.async_api import async_playwright
from .base import BaseScraper

LUMA_URL = "https://lu.ma/ai"
MAX_SCROLLS = 10  # Maximum number of scrolls

class LumaScraper(BaseScraper):
    async def scrape(self, limit: int = 300) -> pd.DataFrame:
        print(f"\n🚀 Starting Lu.ma scraper (target: {limit} events)")
        events, seen = [], set()

        async with async_playwright() as p:
            print("🌐 Launching browser...")
            browser = await p.chromium.launch(
                headless=True,
                proxy={"server": self.proxy} if self.proxy else None,
            )
            page = await browser.new_page()

            print(f"📡 Loading {LUMA_URL}...")
            await page.goto(LUMA_URL, timeout=60_000)
            print("Waiting for event cards to load...")
            await page.wait_for_selector('div.content-card.hoverable.actionable', timeout=15000)
            print("✅ Page loaded successfully")

            # New: Loop through timeline sections
            timeline_sections = await page.query_selector_all('div.timeline-section')
            for section in timeline_sections:
                # Extract the date label
                date_label_tag = await section.query_selector('div.timeline-title.date-title')
                if not date_label_tag:
                    continue
                date_label = (await date_label_tag.inner_text()).strip().lower()

                # Normalize the date label
                today = dt.date.today()
                if date_label == 'today':
                    event_date = today.strftime('%Y-%m-%d')
                elif date_label == 'tomorrow':
                    event_date = (today + dt.timedelta(days=1)).strftime('%Y-%m-%d')
                else:
                    # Try to parse as weekday or full date
                    try:
                        # If it's a weekday, find the next occurrence
                        weekdays = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
                        if date_label in weekdays:
                            days_ahead = (weekdays.index(date_label) - today.weekday() + 7) % 7
                            if days_ahead == 0:
                                days_ahead = 7
                            event_date = (today + dt.timedelta(days=days_ahead)).strftime('%Y-%m-%d')
                        else:
                            # Try parsing as a date string
                            event_date = str(dt.datetime.strptime(date_label, '%d %B %Y').date())
                    except Exception:
                        event_date = date_label  # fallback: keep as is

                # Extract event cards in this section
                cards = await section.query_selector_all('div.content-card.hoverable.actionable')
                for idx, card in enumerate(cards):
                    # Extract event link
                    link_tag = await card.query_selector('a.event-link.content-link')
                    url = f"https://lu.ma{await link_tag.get_attribute('href')}" if link_tag else None

                    if not url or url in seen:
                        continue
                    seen.add(url)

                    # Extract event title
                    title_tag = await card.query_selector('h3')
                    title = await title_tag.inner_text() if title_tag else None
                    if not title:
                        continue
                    title = title.strip()

                    # Extract event time
                    time_tag = await card.query_selector('div.event-time.flex-center.gap-2')
                    time_text = await time_tag.inner_text() if time_tag else None

                    # Extract location
                    location_tag = await card.query_selector('div.info.flex-1.flex-column')
                    location = await location_tag.inner_text() if location_tag else None
                    if location:
                        # Split by newlines and get the last non-empty line which should be the venue
                        location_lines = [line.strip() for line in location.split('\n') if line.strip()]
                        location = location_lines[-1] if location_lines else None

                    # Only include events with 'hack' in the title
                    if re.search(r'hack', title, re.IGNORECASE):
                        print(f"✨ Scraped: {title}")
                        events.append({
                            "title": title,
                            "url": url,
                            "date": f"{event_date} {time_text}" if time_text else event_date,
                            "location": location,
                            "source": "luma"
                        })

            print("\n🔒 Closing browser...")
            await browser.close()

        print(f"\n✅ Scraping complete! Found {len(events)} unique hackathon events")
        df = pd.DataFrame(events)
        df['timestamp'] = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return df
