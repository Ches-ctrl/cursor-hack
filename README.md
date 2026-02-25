# Hack Scraper

This repository provides a simple tool to scrape hackathon events from Luma and export them to a clean, timestamped CSV file with event details and accurate dates.

## Features
- Scrapes hackathon events from Luma (https://lu.ma/ai)
- Outputs a CSV with event title, date (YYYY-MM-DD), location, and more
- Each run generates a timestamped output file
- Command-line interface for easy use
- Web interface to view scraped events at `/bt` route

## Installation
```bash
pip install -r requirements.txt
```

## Usage

### CLI - Scrape Events
```bash
python -m hack_scraper.cli scrape
```

### Web Interface
View scraped hackathon events in your browser:

```bash
python web.py
```

Then visit:
- http://localhost:5000 - Home page
- http://localhost:5000/bt - Hackathon events page
- http://localhost:5000/api/events - JSON API endpoint
