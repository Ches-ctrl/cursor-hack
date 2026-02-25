from flask import Flask, render_template, jsonify
import pandas as pd
from pathlib import Path
import os

app = Flask(__name__)

def get_latest_events():
    """Get events from the most recent non-empty CSV file in output directory."""
    output_dir = Path("output")
    if not output_dir.exists():
        return []
    
    csv_files = list(output_dir.glob("events*.csv"))
    if not csv_files:
        return []
    
    csv_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            if not df.empty:
                events = df.to_dict(orient='records')
                return events
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")
            continue
    
    return []

@app.route('/')
def index():
    """Home page with link to /bt"""
    return render_template('index.html')

@app.route('/bt')
def bt_page():
    """Hackathon events page at /bt route"""
    events = get_latest_events()
    return render_template('bt.html', events=events)

@app.route('/api/events')
def api_events():
    """API endpoint to get events as JSON"""
    events = get_latest_events()
    return jsonify(events)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
