import datetime as dt
import pandas as pd
from playwright.async_api import async_playwright
from .base import BaseScraper

LUMA_URL = "https://lu.ma/ai"

class LumaScraper(BaseScraper):
    async def scrape(self, limit: int = 300) -> pd.DataFrame:
        events, seen = [], set()

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                proxy={"server": self.proxy} if self.proxy else None,
            )
            page = await browser.new_page()
            await page.goto(LUMA_URL, timeout=60_000)
            await page.wait_for_selector('[itemprop="event"]')

            while len(events) < limit:
                cards = await page.query_selector_all('[itemprop="event"]')
                for card in cards:
                    url = await card.eval_on_selector("a", "e=>e.href")
                    if url in seen:
                        continue
                    seen.add(url)

                    title = await card.eval_on_selector("h3", "e=>e.textContent")
                    iso = await card.eval_on_selector("time", "e=>e.dateTime")
                    events.append({
                        "title": title.strip(),
                        "url": url,
                        "date": dt.datetime.fromisoformat(iso).date(),
                        "source": "luma"
                    })

                # Scroll to load more
                await page.mouse.wheel(0, 2000)
                await page.wait_for_timeout(1200)
                if await page.is_visible("text=No more"):
                    break

            await browser.close()

        return pd.DataFrame(events)
