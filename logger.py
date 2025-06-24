import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import base64
import json

load_dotenv()

tickers = ["AAPL", "MSFT", "GOOGL"]  # Replace with your test tickers
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
GH_TOKEN = os.getenv("GH_TOKEN")
REPO = "Logger5.0"
OWNER = "dbarber530"
FILE_PATH = "index.html"
BRANCH = "main"

def get_stock_data(ticker):
    url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_API_KEY}"
    res = requests.get(url)
    if res.status_code != 200:
        return None
    data = res.json()
    return {
        "ticker": ticker,
        "price": data.get("c"),
        "change": round(data.get("d", 0), 2),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def build_html(data):
    rows = ""
    for d in data:
        rows += f"<tr><td>{d['ticker']}</td><td>{d['price']}</td><td>{d['change']}</td><td>{d['time']}</td></tr>\n"

    html = f"""
    <html>
    <head>
        <title>📈 BarberBot Logger 5.0</title>
        <style>
            body {{ background-color: #1e1e1e; color: white; font-family: Arial, sans-serif; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 10px; border: 1px solid #444; text-align: center; }}
            th {{ background-color: #2c2c2c; }}
        </style>
    </head>
    <body>
        <h1>📈 BarberBot Logger 5.0</h1>
        <table>
            <tr><th>Ticker</th><th>Price</th><th>Change</th><th>Time</th></tr>
            {rows}
        </table>
        <p>Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </body>
    </html>
    """
    return html

def push_to_github(html_content):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {GH_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Get the current file SHA
    r = requests.get(url, headers=headers)
    sha = r.json().get("sha")

    encoded = base64.b64encode(html_content.encode()).decode()

    payload = {
        "message": "update index with direct embed",
        "content": encoded,
        "branch": BRANCH
    }

    if sha:
        payload["sha"] = sha

    r = requests.put(url, headers=headers, data=json.dumps(payload))
    print(f"GitHub push status: {r.status_code}")
    print(r.json())

def main():
    all_data = []
    for ticker in tickers:
        data = get_stock_data(ticker)
        if data:
            all_data.append(data)

    html = build_html(all_data)
    push_to_github(html)

if __name__ == "__main__":
    main()
