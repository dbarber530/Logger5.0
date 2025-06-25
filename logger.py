import os
import time
import requests
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

group_a = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "UNH", "JPM", "V", "MA", "HD", "AVGO", "PG", "LLY", "XOM", "PEP", "MRK", "COST", "ABBV", "CVX", "WMT", "ADBE", "KO", "BAC", "MCD"]
group_b = ["NFLX", "CRM", "INTC", "AMD", "T", "GE", "BA", "GS", "QCOM", "PYPL", "LMT", "SBUX", "TXN", "NKE", "PFE", "WFC", "IBM", "ORCL", "TMO", "MDT", "NEE", "LOW", "CAT", "BKNG", "NOW"]

last_group = "b"
cached_a = []
cached_b = []

def fetch_data(tickers):
    url = "https://finnhub.io/api/v1/quote"
    headers = {"X-Finnhub-Token": FINNHUB_API_KEY}
    results = []
    for symbol in tickers:
        try:
            r = requests.get(url, params={"symbol": symbol}, headers=headers)
            data = r.json()
            results.append({
                "ticker": symbol,
                "price": data.get("c"),
                "percent_change": round(((data.get("c") - data.get("pc")) / data.get("pc")) * 100, 2) if data.get("c") and data.get("pc") else None
            })
        except:
            results.append({
                "ticker": symbol,
                "price": None,
                "percent_change": None
            })
        time.sleep(0.5)  # stay under rate limits
    return results

@app.route("/")
def index():
    global last_group, cached_a, cached_b
    if last_group == "b":
        data = fetch_data(group_a)
        cached_a = data
        last_group = "a"
    else:
        data = fetch_data(group_b)
        cached_b = data
        last_group = "b"

    all_data = sorted(cached_a + cached_b, key=lambda x: x['ticker'])

    html = """
    <html>
    <head><title>BarberBot Logger</title></head>
    <body>
        <h1>Live Tickers</h1>
        <table border="1" cellpadding="6" cellspacing="0">
            <tr><th>Ticker</th><th>Price</th><th>% Change</th></tr>
            {% for row in data %}
                <tr>
                    <td>{{ row['ticker'] }}</td>
                    <td>{{ row['price'] }}</td>
                    <td>{{ row['percent_change'] }}%</td>
                </tr>
            {% endfor %}
        </table>
        <p>Last updated: {{ timestamp }}</p>
    </body>
    </html>
    """
    return render_template_string(html, data=all_data, timestamp=time.strftime("%Y-%m-%d %H:%M:%S"))
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
