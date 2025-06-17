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

            scroll_count = 0
            last_event_count = 0
            no_new_events_count = 0

            while len(events) < limit and scroll_count < MAX_SCROLLS:
                print(f"\n📊 Current progress: {len(events)}/{limit} events")
                cards = await page.query_selector_all('div.content-card.hoverable.actionable')
                print(f"🔍 Found {len(cards)} event cards on current page")

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
                            "date": time_text,
                            "location": location,
                            "source": "luma"
                        })

                # Check if we found any new events
                if len(events) == last_event_count:
                    no_new_events_count += 1
                    if no_new_events_count >= 2:  # If no new events for 2 consecutive scrolls
                        print("⚠️ No new events found in last 2 scrolls, stopping...")
                        break
                else:
                    no_new_events_count = 0
                    last_event_count = len(events)

                # Scroll to load more
                scroll_count += 1
                print(f"📜 Scrolling page ({scroll_count}/{MAX_SCROLLS})...")
                await page.mouse.wheel(0, 2000)
                await page.wait_for_timeout(1200)

                if await page.is_visible("text=No more"):
                    print("⚠️ Reached end of page")
                    break

            print("\n🔒 Closing browser...")
            await browser.close()

        print(f"\n✅ Scraping complete! Found {len(events)} unique hackathon events")
        return pd.DataFrame(events)
