import asyncio
import typer
from pathlib import Path
from .scraper.luma import LumaScraper
from .scraper.firecrawl import FirecrawlScraper
from .scraper.serpapi import SerpApiScraper
from datetime import datetime
from hack_scraper.whatsapp import send_whatsapp_summary

app = typer.Typer(help="Hackathon Scraper CLI")

@app.command()
def scrape(
    limit: int = typer.Option(20, help="Maximum number of events to scrape"),
    proxy: str = typer.Option(None, help="Proxy URL to use"),
    output: str = typer.Option("output/events.csv", help="Output CSV file path"),
):
    """Scrape hackathons from Lu.ma using Playwright and save to CSV."""
    print(f"\n🎯 Starting hackathon scraper (Playwright)")
    print(f"📊 Target events: {limit}")
    if proxy:
        print(f"🌐 Using proxy: {proxy}")

    print("\n🔄 Initializing scraper...")
    scraper = LumaScraper(proxy=proxy)

    print("\n⏳ Starting scrape process...")
    df = asyncio.run(scraper.scrape(limit))

    # Ensure output directory exists
    output_path = Path(output)
    if output == "output/events.csv":
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_path = output_path.parent / f"events_{timestamp}.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n💾 Saving results to {output_path}...")
    df.to_csv(output_path, index=False)

    print("\n📊 Summary:")
    print(f"   • Total events: {len(df)}")
    print(f"   • Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"   • Output file: {output_path.absolute()}")

    print("\n✅ Done!")

@app.command()
def firecrawl(
    limit: int = typer.Option(20, help="Maximum number of events to scrape (Firecrawl)"),
    proxy: str = typer.Option(None, help="Proxy URL to use (not used by Firecrawl)"),
    output: str = typer.Option("output/events_firecrawl.csv", help="Output CSV file path"),
):
    """Scrape hackathons from Lu.ma using Firecrawl and save to CSV."""
    print(f"\n🎯 Starting hackathon scraper (Firecrawl)")
    print(f"📊 Target events: {limit}")
    print("\n🔄 Initializing Firecrawl scraper...")
    scraper = FirecrawlScraper(proxy=proxy)

    print("\n⏳ Starting Firecrawl scrape process...")
    df = asyncio.run(scraper.scrape(limit))

    # Ensure output directory exists
    output_path = Path(output)
    if output == "output/events_firecrawl.csv":
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_path = output_path.parent / f"events_firecrawl_{timestamp}.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n💾 Saving results to {output_path}...")
    df.to_csv(output_path, index=False)

    print("\n📊 Summary:")
    print(f"   • Total events: {len(df)}")
    if not df.empty and 'date' in df:
        print(f"   • Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"   • Output file: {output_path.absolute()}")

    print("\n✅ Done!")

@app.command()
def serpapi(
    limit: int = typer.Option(20, help="Maximum number of events to scrape (SerpApi)"),
    proxy: str = typer.Option(None, help="Proxy URL to use (not used by SerpApi)"),
    output: str = typer.Option("output/events_serpapi.csv", help="Output CSV file path"),
):
    """Scrape hackathons from Google using SerpApi and save to CSV."""
    print(f"\n🎯 Starting hackathon scraper (SerpApi)")
    print(f"📊 Target events: {limit}")
    print("\n🔄 Initializing SerpApi scraper...")
    scraper = SerpApiScraper(proxy=proxy)

    print("\n⏳ Starting SerpApi scrape process...")
    df = asyncio.run(scraper.scrape(limit))

    # Ensure output directory exists
    output_path = Path(output)
    if output == "output/events_serpapi.csv":
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_path = output_path.parent / f"events_serpapi_{timestamp}.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n💾 Saving results to {output_path}...")
    df.to_csv(output_path, index=False)

    print("\n📊 Summary:")
    print(f"   • Total events: {len(df)}")
    if not df.empty and 'date' in df:
        print(f"   • Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"   • Output file: {output_path.absolute()}")

    print("\n✅ Done!")

@app.command()
def send_whatsapp(
    csv_file: str = typer.Argument(..., help="Path to the events CSV file"),
    whatsapp_to: str = typer.Argument(..., help="WhatsApp number to send summary to (e.g. whatsapp:+1234567890)")
):
    """Send a WhatsApp summary of events from a CSV file."""
    import pandas as pd
    print(f"\n📂 Reading events from {csv_file}...")
    df = pd.read_csv(csv_file)
    events = df.to_dict(orient="records")
    print(f"\n📲 Sending WhatsApp summary to {whatsapp_to}...")
    send_whatsapp_summary(events, whatsapp_to)
    print("\n✅ WhatsApp summary sent!")

@app.command()
def scrape_all_calendars(
    limit: int = typer.Option(20, help="Maximum number of events to scrape per calendar"),
    proxy: str = typer.Option(None, help="Proxy URL to use"),
    output: str = typer.Option("output/events.csv", help="Output CSV file path"),
    calendars_file: str = typer.Option("calendars.txt", help="Path to calendars.txt file"),
):
    """Scrape hackathons from all URLs in calendars.txt using Playwright and save to CSV."""
    import pandas as pd
    from pathlib import Path

    print(f"\n🎯 Starting multi-calendar hackathon scraper (Playwright)")
    print(f"📊 Target events per calendar: {limit}")
    if proxy:
        print(f"🌐 Using proxy: {proxy}")
    print(f"📂 Reading calendar URLs from {calendars_file}...")

    # Read all URLs from calendars.txt
    with open(calendars_file, "r") as f:
        urls = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    print(f"   • Found {len(urls)} calendar URLs")

    async def scrape_one(url):
        print(f"\n🔄 Scraping: {url}")
        scraper = LumaScraper(proxy=proxy)
        try:
            df = await scraper.scrape(limit, url=url)
            df["calendar_url"] = url
            return df
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return pd.DataFrame()

    async def scrape_all():
        dfs = []
        for url in urls:
            df = await scrape_one(url)
            if not df.empty:
                dfs.append(df)
        if dfs:
            return pd.concat(dfs, ignore_index=True)
        else:
            return pd.DataFrame()

    df = asyncio.run(scrape_all())

    # Ensure output directory exists
    output_path = Path(output)
    if output == "output/events.csv":
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_path = output_path.parent / f"events_{timestamp}.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n💾 Saving results to {output_path}...")
    df.to_csv(output_path, index=False)

    print("\n📊 Summary:")
    print(f"   • Total events: {len(df)}")
    if not df.empty and 'date' in df:
        print(f"   • Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"   • Output file: {output_path.absolute()}")

    print("\n✅ Done!")

if __name__ == "__main__":
    app()
