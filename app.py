from flask import Flask, render_template_string
import requests
from datetime import datetime
import pytz

app = Flask(__name__)

# === API + Ticker Setup ===
API_KEY = "YOUR_FINNHUB_API_KEY"
URL = "https://finnhub.io/api/v1/quote"
GROUP_A = ["AAPL", "MSFT", "NVDA"]
GROUP_B = ["TSLA", "AMZN", "META"]

# === HTML Templates ===
TABLE_TEMPLATE = """
<h2>{{ group_name }}</h2>
<table border="1" cellspacing="0" cellpadding="4">
<tr><th>Ticker</th><th>Price</th><th>Change</th><th>High</th><th>Low</th><th>Open</th><th>Prev Close</th></tr>
{% for s in stocks %}
<tr><td>{{ s['ticker'] }}</td><td>${{ s['price'] }}</td><td>{{ s['change'] }}%</td><td>${{ s['high'] }}</td><td>${{ s['low'] }}</td><td>${{ s['open'] }}</td><td>${{ s['prevClose'] }}</td></tr>
{% endfor %}
</table><br>
"""

HTML_TEMPLATE = """
<html><head><title>BarberBot Logger</title></head>
<body>
    <h1>BarberBot Live Logger</h1>
    <p><b>Last Updated:</b> {{ timestamp }} UTC</p>
    {{ table_a | safe }}
    {{ table_b | safe }}
    <p><a href="/history" target="_blank">View History Log</a></p>
</body></html>
"""

HISTORY_PATH = "log.txt"

# === Helpers ===
def get_data(ticker):
    try:
        r = requests.get(URL, params={"symbol": ticker}, headers={"X-Finnhub-Token": API_KEY})
        d = r.json()
        return {
            "ticker": ticker,
            "price": d["c"],
            "change": round(((d["c"] - d["pc"]) / d["pc"]) * 100, 2) if d["pc"] else 0,
            "high": d["h"],
            "low": d["l"],
            "open": d["o"],
            "prevClose": d["pc"]
        }
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

def get_group_data(group):
    return [s for s in [get_data(t) for t in group] if s]

# === Live Ticker Route ===
@app.route("/")
def index():
    utc = pytz.timezone("UTC")
    now = datetime.now(utc).strftime("%Y-%m-%d %H:%M:%S")

    a_data = get_group_data(GROUP_A)
    b_data = get_group_data(GROUP_B)

    table_a = render_template_string(TABLE_TEMPLATE, group_name="Group A", stocks=a_data)
    table_b = render_template_string(TABLE_TEMPLATE, group_name="Group B", stocks=b_data)

    # Save to history log
    log_line = f"{now} UTC | " + " | ".join([f"{s['ticker']}: ${s['price']} ({s['change']}%)" for s in a_data + b_data]) + "\n"
    with open(HISTORY_PATH, "a") as f:
        f.write(log_line)

    return render_template_string(HTML_TEMPLATE, timestamp=now, table_a=table_a, table_b=table_b)

# === History Log Route ===
@app.route("/history")
def history():
    try:
        with open(HISTORY_PATH, "r") as f:
            lines = f.readlines()
        return "<pre>" + "".join(lines[-100:]) + "</pre>"
    except:
        return "<pre>No history yet.</pre>"

if __name__ == "__main__":
    app.run(debug=True)
