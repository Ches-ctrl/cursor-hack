import datetime as dt
import pandas as pd
import re
from playwright.async_api import async_playwright
from .base import BaseScraper

LUMA_URL = "https://lu.ma/ai"
MAX_SCROLLS = 10  # Maximum number of scrolls

class LumaScraper(BaseScraper):
    async def scrape(self, limit: int = 300, url: str = LUMA_URL) -> pd.DataFrame:
        print(f"\n🚀 Starting Lu.ma scraper (target: {limit} events, url: {url})")
        events, seen = [], set()

        async with async_playwright() as p:
            print("🌐 Launching browser...")
            browser = await p.chromium.launch(
                headless=True,
                proxy={"server": self.proxy} if self.proxy else None,
            )
            page = await browser.new_page()

            print(f"📡 Loading {url}...")
            await page.goto(url, timeout=60_000)
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
                event_date_obj = None
                # Split the date label on newlines and spaces, and try to parse each part
                date_label_parts = [part.strip().lower() for part in re.split(r'[\n,]+', date_label) if part.strip()]
                for part in date_label_parts:
                    if part == 'today':
                        event_date_obj = today
                        break
                    elif part == 'tomorrow':
                        event_date_obj = today + dt.timedelta(days=1)
                        break
                    else:
                        weekdays = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
                        if part in weekdays:
                            days_ahead = (weekdays.index(part) - today.weekday() + 7) % 7
                            if days_ahead == 0:
                                days_ahead = 7
                            event_date_obj = today + dt.timedelta(days=days_ahead)
                            break
                        # Try parsing as a date string (e.g., 'jun 19')
                        try:
                            event_date_obj = dt.datetime.strptime(part, '%b %d').replace(year=today.year).date()
                            break
                        except Exception:
                            pass
                        try:
                            event_date_obj = dt.datetime.strptime(part, '%d %B %Y').date()
                            break
                        except Exception:
                            pass
                # If still not found, fallback to empty string
                if event_date_obj is None:
                    event_date_obj = dt.date.today()

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
                    # Parse and combine date and time
                    event_datetime_str = None
                    if event_date_obj and time_text:
                        # Try to parse time (e.g., '6:00 PM')
                        try:
                            event_time_obj = dt.datetime.strptime(time_text.strip(), '%I:%M %p').time()
                            event_datetime = dt.datetime.combine(event_date_obj, event_time_obj)
                            event_datetime_str = event_datetime.strftime('%Y-%m-%d %H:%M')
                        except Exception:
                            event_datetime_str = event_date_obj.strftime('%Y-%m-%d')
                    elif event_date_obj:
                        event_datetime_str = event_date_obj.strftime('%Y-%m-%d')
                    else:
                        event_datetime_str = date_label  # fallback

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
                            "date": event_date_obj.strftime('%Y-%m-%d') if event_date_obj else '',
                            "location": f"{location}",
                            "source": "luma"
                        })

            print("\n🔒 Closing browser...")
            await browser.close()

        print(f"\n✅ Scraping complete! Found {len(events)} unique hackathon events")
        df = pd.DataFrame(events)
        return df
