import os
import requests
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
import pytz

# Setup
app = Flask(__name__)
CORS(app)

# Get API key from environment variable
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

# List of tickers for Group A and Group B
group_a = ["AAPL", "MSFT", "GOOGL", "NVDA", "AMZN"]
group_b = ["TSLA", "META", "JPM", "DIS", "NFLX"]

# Choose which group to use per request (simple toggle)
use_group_a = True

@app.route("/")
def index():
    return "Logger is running."

@app.route("/tickers")
def get_ticker_data():
    global use_group_a
    tickers = group_a if use_group_a else group_b
    use_group_a = not use_group_a  # Toggle for next request

    results = []
    for ticker in tickers:
        url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            results.append({
                "ticker": ticker,
                "price": data.get("c"),
                "change": data.get("d"),
                "percent_change": data.get("dp"),
                "high": data.get("h"),
                "low": data.get("l"),
                "open": data.get("o"),
                "previous_close": data.get("pc"),
                "volume": "N/A"  # Finnhub's /quote doesn't return volume
            })
        else:
            results.append({"ticker": ticker, "error": "Failed to fetch"})

    # Add timestamp
    eastern = pytz.timezone("US/Eastern")
    now = datetime.now(eastern).strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({"updated": now, "results": results})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    from flask import Flask, render_template_string
import os

app = Flask(__name__)

@app.route("/")
def index():
    if os.path.exists("index.html"):
        with open("index.html", "r") as f:
            return render_template_string(f.read())
    else:
        return "<h1>index.html not found</h1>", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
