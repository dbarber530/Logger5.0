import os
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

# Group A and Group B (50 tickers each)
group_a = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "UNH", "XOM", "JNJ",
           "V", "JPM", "MA", "PG", "HD", "MRK", "PEP", "AVGO", "LLY", "ABBV",
           "COST", "CVX", "BAC", "KO", "WMT", "ADBE", "TMO", "CSCO", "ACN", "ABT",
           "DHR", "MCD", "INTC", "NFLX", "TXN", "VZ", "NKE", "PFE", "LIN", "QCOM",
           "NEE", "AMD", "HON", "UNP", "LOW", "AMGN", "IBM", "CRM", "MDT", "INTU"]

group_b = ["GS", "GE", "CAT", "BLK", "AXP", "RTX", "LMT", "T", "MO", "BA",
           "DE", "SPGI", "ICE", "CCI", "CI", "ZTS", "SCHW", "NOW", "ADI", "MMC",
           "PLD", "TJX", "SO", "DUK", "PNC", "BKNG", "GM", "F", "USB", "AON",
           "CB", "WM", "ADP", "ETN", "BDX", "EL", "SYK", "ISRG", "EW", "GILD",
           "EMR", "CL", "FDX", "NSC", "TGT", "MAR", "CSX", "MNST", "AEP", "CARR"]

def fetch_quote(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def generate_html(tickers, group_name):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="refresh" content="60">
  <title>Logger5.0 - {group_name}</title>
</head>
<body>
  <h1>Logger5.0</h1>
  <h2>Group {group_name} | Last updated: {timestamp}</h2>
  <table border="1" cellpadding="5" cellspacing="0">
    <tr>
      <th>Symbol</th>
      <th>Current Price</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
      <th>Previous Close</th>
    </tr>
"""

    for symbol in tickers:
        data = fetch_quote(symbol)
        if data:
            html += f"""
    <tr>
      <td>{symbol}</td>
      <td>{data.get('c', 'N/A')}</td>
      <td>{data.get('h', 'N/A')}</td>
      <td>{data.get('l', 'N/A')}</td>
      <td>{data.get('o', 'N/A')}</td>
      <td>{data.get('pc', 'N/A')}</td>
    </tr>
"""

    html += """
  </table>
</body>
</html>
"""
    with open("index.html", "w") as f:
        f.write(html)

# Infinite loop alternating groups
counter = 0
while True:
    if counter % 2 == 0:
        generate_html(group_a, "A")
    else:
        generate_html(group_b, "B")
    counter += 1
    time.sleep(60)
