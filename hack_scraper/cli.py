import asyncio
import typer
from pathlib import Path
from .scraper.luma import LumaScraper

app = typer.Typer(help="Hackathon Scraper CLI")

@app.command()
def scrape(
    source: str = "luma",
    limit: int = 300,
    proxy: str | None = None,
    output: str = "output/events.csv"
):
    """Scrape hackathons from a source and save to CSV"""
    scraper = LumaScraper(proxy=proxy)
    df = asyncio.run(scraper.scrape(limit))

    # Ensure output directory exists
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)
    typer.echo(f"✅ Scraped {len(df)} events -> {output}")

if __name__ == "__main__":
    app()
