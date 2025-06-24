import os
import requests
import base64
from datetime import datetime
import time
import pytz

# Finnhub API setup
FINNHUB_API_KEY = os.environ['FINNHUB_API_KEY']
headers = {'X-Finnhub-Token': FINNHUB_API_KEY}

# GitHub setup
GH_TOKEN = os.environ['GH_TOKEN']
repo_owner = "dbarber530"
repo_name = "Logger5.0"
file_path = "index.html"
api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"

# Split tickers into Group A and Group B
tickers = [
    "GE", "DE", "CAT", "MMM", "GS", "RTX", "USB", "FDX", "BLK", "AXP",
    "SBUX", "BKNG", "GM", "F", "CVS", "TGT", "MO", "SPGI", "ADI", "ADP",
    "ZTS", "BDX", "GILD", "ISRG", "EW", "VRTX", "REGN", "MRNA", "PANW", "SNPS",
    "NOW", "FTNT", "CRWD", "DDOG", "ZS", "PLTR", "DKNG", "RBLX", "CRVW", "NVTS",
    "TTD", "SHOP", "AFRM", "ABNB", "MDB", "NET", "OKTA", "SQ", "AAPL", "MSFT",
    "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "V", "UNH", "JNJ", "HD",
    "PG", "DIS", "BAC", "PFE", "VZ", "KO", "PEP", "ABBV", "MRK", "INTC",
    "WMT", "T", "ADBE", "CSCO", "CRM", "CMCSA", "NFLX", "ORCL", "ABT", "XOM",
    "CVX", "COST", "ACN", "DHR", "AVGO", "TXN", "MCD", "MDT", "NEE", "QCOM",
    "LLY", "AMGN", "UNP", "LOW", "BA", "IBM", "COP", "MS", "CALM", "USVM"
]
group_a = tickers[:50]
group_b = tickers[50:]

use_group_a = True

def get_stock_data(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return {
            "symbol": symbol,
            "current": data.get("c", "N/A"),
            "high": data.get("h", "N/A"),
            "low": data.get("l", "N/A"),
            "open": data.get("o", "N/A"),
            "prev_close": data.get("pc", "N/A")
        }
    else:
        return {"symbol": symbol, "error": response.status_code}

def build_html(ticker_data, previous_html):
    now = datetime.now(pytz.timezone("US/Eastern")).strftime("%Y-%m-%d %I:%M:%S %p")
    new_section = f"<h2>Update: {now}</h2><table border='1'><tr><th>Ticker</th><th>Price</th><th>High</th><th>Low</th><th>Open</th><th>Prev Close</th></tr>"
    for data in ticker_data:
        new_section += f"<tr><td>{data['symbol']}</td><td>{data.get('current')}</td><td>{data.get('high')}</td><td>{data.get('low')}</td><td>{data.get('open')}</td><td>{data.get('prev_close')}</td></tr>"
    new_section += "</table><hr>"

    # Insert at the top of <body>
    if "<body>" in previous_html:
        parts = previous_html.split("<body>")
        updated_html = parts[0] + "<body>" + new_section + parts[1]
        return updated_html
    else:
        return f"<html><body>{new_section}</body></html>"

def get_current_html():
    response = requests.get(api_url, headers={"Authorization": f"token {GH_TOKEN}"})
    if response.status_code == 200:
        content = response.json()
        file_sha = content["sha"]
        encoded = content["content"]
        decoded = base64.b64decode(encoded).decode('utf-8')
        return decoded, file_sha
    else:
        return "", ""

def push_update(updated_html, sha):
    encoded = base64.b64encode(updated_html.encode("utf-8")).decode("utf-8")
    payload = {
        "message": "Auto update ticker data",
        "content": encoded,
        "sha": sha
    }
    response = requests.put(api_url, headers={
        "Authorization": f"token {GH_TOKEN}",
        "Content-Type": "application/json"
    }, json=payload)
    return response.status_code == 200 or response.status_code == 201

# Main loop
while True:
    eastern = pytz.timezone("US/Eastern")
    now = datetime.now(eastern)
    if now.weekday() >= 5 or now.hour < 9 or (now.hour == 9 and now.minute < 30) or now.hour >= 16:
        print("Market closed. Sleeping 5 minutes.")
        time.sleep(300)
        continue

    current_group = group_a if use_group_a else group_b
    print(f"Using {'Group A' if use_group_a else 'Group B'}")
    stock_data = [get_stock_data(ticker) for ticker in current_group]
    old_html, sha = get_current_html()
    if not old_html or not sha:
        print("Failed to retrieve current HTML.")
        time.sleep(300)
        continue

    updated_html = build_html(stock_data, old_html)
    if push_update(updated_html, sha):
        print("Update pushed to GitHub.")
    else:
        print("Failed to push update.")

    use_group_a = not use_group_a
    time.sleep(300)  # 5 minutes
