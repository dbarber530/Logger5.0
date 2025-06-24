import os
import time
import requests
from datetime import datetime
import pytz
import json

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "dbarber530/Logger5.0"
BRANCH = "main"
API_URL = f"https://api.github.com/repos/{REPO}/contents/"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

group_a = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "JPM", "V", "UNH",
    "HD", "MA", "XOM", "BAC", "LLY", "PFE", "KO", "PEP", "MRK", "WMT",
    "T", "VZ", "CVX", "DIS", "ADBE", "NFLX", "INTC", "CSCO", "ABT", "CRM",
    "QCOM", "TXN", "ORCL", "BA", "MCD", "COST", "WFC", "ACN", "HON", "IBM",
    "GE", "GS", "UPS", "CAT", "MMM", "BKNG", "BLK", "AXP", "DE", "LOW"
]

group_b = [
    "CALM", "USVM", "NVTS", "CRVW", "ROKU", "PLTR", "SQ", "SHOP", "AMD", "MU",
    "F", "GM", "LCID", "RIVN", "SOFI", "UBER", "LYFT", "BABA", "JD", "TCEHY",
    "NIO", "TSM", "ASML", "INTU", "NOW", "PANW", "ZS", "DDOG", "MDB", "SNOW",
    "ENPH", "SEDG", "FSLR", "RUN", "SPWR", "JKS", "ICLN", "TAN", "ARKK", "ARKW",
    "SPY", "QQQ", "DIA", "IWM", "XLF", "XLE", "XLK", "XLV", "XLY", "XLI"
]

def get_stock_data(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {
            "ticker": symbol,
            "price": data.get("c", 0),
            "high": data.get("h", 0),
            "low": data.get("l", 0),
            "volume": data.get("v", 0)
        }
    except:
        return {
            "ticker": symbol,
            "price": "err",
            "high": "err",
            "low": "err",
            "volume": "err"
        }

def get_current_group():
    minute = datetime.utcnow().minute
    return group_a if (minute // 5) % 2 == 0 else group_b

def get_all_data():
    tickers = get_current_group()
    return [get_stock_data(ticker) for ticker in tickers]

def build_html_table(data, timestamp):
    table = f"<p>Last updated: {timestamp} UTC</p><table border='1'><tr><th>Ticker</th><th>Price</th><th>High</th><th>Low</th><th>Volume</th></tr>"
    for d in data:
        table += f"<tr><td>{d['ticker']}</td><td>{d['price']}</td><td>{d['high']}</td><td>{d['low']}</td><td>{d['volume']}</td></tr>"
    table += "</table>"
    return f"<html><head><title>Logger5.0</title></head><body><h1>Group {'A' if get_current_group() == group_a else 'B'}</h1>{table}</body></html>"

def upload_to_github(file_path, content, message):
    url = f"{API_URL}{file_path}"
    get_response = requests.get(url, headers=headers)
    sha = get_response.json().get("sha") if get_response.status_code == 200 else None

    encoded = content.encode("utf-8")
    payload = {
        "message": message,
        "content": encoded.decode("utf-8").encode("utf-8").hex(),
        "branch": BRANCH
    }
    if sha:
        payload["sha"] = sha

    payload["content"] = encoded.decode("utf-8").encode("base64").decode("utf-8") if hasattr(encoded, "decode") else encoded.decode("utf-8")

    response = requests.put(url, headers=headers, json=payload)
    return response.status_code in [200, 201]

def main():
    while True:
        timestamp = datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        data = get_all_data()
        html_content = build_html_table(data, timestamp)
        json_content = json.dumps({
            "timestamp": timestamp,
            "data": data
        }, indent=2)

        upload_to_github("index.html", html_content, f"Update index.html at {timestamp}")
        upload_to_github("data.json", json_content, f"Update data.json at {timestamp}")

        print(f"Logged at {timestamp} UTC")
        time.sleep(300)  # 5 minutes

if __name__ == "__main__":
    main()
