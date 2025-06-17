# Hack Scraper

This repository provides a simple tool to scrape hackathon events from Luma and export them to a clean, timestamped CSV file with event details and accurate dates.

## Features
- Scrapes hackathon events from Luma (https://lu.ma/ai)
- Outputs a CSV with event title, date (YYYY-MM-DD), location, and more
- Each run generates a timestamped output file
- Command-line interface for easy use

## Usage
```bash
pip install -r requirements.txt
python -m hack_scraper.cli scrape
```
