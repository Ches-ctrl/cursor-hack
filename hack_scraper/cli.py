import asyncio
import typer
from pathlib import Path
from .scraper.luma import LumaScraper
from datetime import datetime

app = typer.Typer(help="Hackathon Scraper CLI")

@app.command()
def scrape(
    source: str = typer.Option("luma", help="Source to scrape from"),
    limit: int = typer.Option(300, help="Maximum number of events to scrape"),
    proxy: str = typer.Option(None, help="Proxy URL to use"),
    output: str = typer.Option("output/events.csv", help="Output CSV file path")
):
    """Scrape hackathons from a source and save to CSV"""
    print(f"\n🎯 Starting hackathon scraper")
    print(f"📌 Source: {source}")
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

if __name__ == "__main__":
    app()
