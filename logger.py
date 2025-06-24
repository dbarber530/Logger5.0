import requests
import time
import os
from datetime import datetime, timezone
from github import Github

# ENV variables
token = os.environ['GH_TOKEN']
repo_name = "dbarber530/Logger5.0"
file_path = "index.html"

# 100 tickers
tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "JPM", "V", "MA",
    "UNH", "LLY", "HD", "AVGO", "XOM", "CVX", "PG", "KO", "PEP", "PFE",
    "MRK", "ABBV", "TMO", "ACN", "WMT", "ORCL", "ADBE", "CSCO", "NFLX", "NKE",
    "AMD", "INTC", "CRM", "MCD", "DHR", "BAC", "GS", "QCOM", "TXN", "COST",
    "AMAT", "CAT", "VRTX", "ISRG", "BLK", "GE", "UPS", "LOW", "HON", "NEE",
    "BKNG", "LMT", "REGN", "DE", "MDT", "AXP", "NOW", "MO", "TJX", "TGT",
    "SBUX", "ELV", "CI", "CVS", "ZTS", "SPGI", "MS", "PLD", "ADP", "SYK",
    "CSX", "USB", "PNC", "SO", "DUK", "ETN", "HUM", "MMC", "ADI", "FDX",
    "FIS", "BDX", "GILD", "WM", "EMR", "GM", "EOG", "APD", "AON", "CL",
    "TRV", "ROST", "PSA", "MET", "F", "HCA", "STZ", "COF", "ALL", "DOW"
]

def get_stock_data(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={os.environ['FINNHUB_API_KEY']}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    return {
        'ticker': symbol,
        'price': round(data.get('c', 0), 2),
        'change': round(data.get('d', 0), 2),
        'timestamp': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }

def build_html(live_rows, historical_rows, timestamp):
    return f"""
<html>
<head>
    <title>📈 BarberBot Logger 5.0</title>
    <meta charset="UTF-8">
</head>
<body style="background-color:#111;color:white;font-family:monospace;">
    <h1>📉 BarberBot Logger 5.0</h1>
    <table border="1" style="border-collapse:collapse;width:100%">
        <tr style="background-color:#222;">
            <th>Ticker</th>
            <th>Price</th>
            <th>Change</th>
            <th>Time</th>
        </tr>
        {live_rows}
    </table>
    <p style="color:gray;">Last Updated: {timestamp}</p>
    <hr/>
    <h3>📜 Historical Log</h3>
    <pre>{historical_rows}</pre>
</body>
</html>
"""

def main():
    g = Github(token)
    repo = g.get_repo(repo_name)

    try:
        contents = repo.get_contents(file_path)
        existing_html = contents.decoded_content.decode()
    except:
        existing_html = ""

    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    group = tickers[:50] if int(datetime.utcnow().minute) % 2 == 0 else tickers[50:]

    live_rows = ""
    history_block = ""

    for symbol in group:
        data = get_stock_data(symbol)
        if data:
            live_rows += f"<tr><td>{data['ticker']}</td><td>{data['price']}</td><td>{data['change']}</td><td>{data['timestamp']}</td></tr>\n"
            history_block += f"{data['timestamp']} | {data['ticker']} | ${data['price']} | Δ {data['change']}\n"

    new_html = build_html(live_rows, history_block, timestamp)

    repo.update_file(
        path=file_path,
        message=f"update index with direct embed",
        content=new_html,
        sha=contents.sha if 'contents' in locals() else None
    )

if __name__ == "__main__":
    main()
