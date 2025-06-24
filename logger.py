import os
import time
import requests
from datetime import datetime

API_TOKEN = os.environ.get("FINNHUB_TOKEN")
TICKERS = ["AAPL", "GOOGL", "..."]  # add your 100 symbols here
URL = "https://finnhub.io/api/v1/quote"

def fetch_quote(symbol):
    resp = requests.get(URL, params={"symbol": symbol, "token": API_TOKEN})
    data = resp.json()
    return {
        "symbol": symbol,
        "price": data.get("c"),
        "change": data.get("d"),
        "percent": data.get("dp"),
        "volume": data.get("v")
    }

def generate_html(quotes):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = "".join(f"""
        <tr>
            <td>{q['symbol']}</td>
            <td>{q['price']}</td>
            <td>{q['change']:.2f}</td>
            <td>{q['percent']:.2f}%</td>
            <td>{q['volume']}</td>
        </tr>""" for q in quotes)
    return f"""<!DOCTYPE html>
<html>
<head><title>Logger 5.0</title></head>
<body>
  <h1>Logger5.0</h1>
  <p>Updated: {now}</p>
  <table border="1" cellspacing="0" cellpadding="4">
    <tr><th>Symbol</th><th>Price</th><th>Change</th><th>% Change</th><th>Volume</th></tr>
    {rows}
  </table>
</body>
</html>"""

def main():
    quotes = [fetch_quote(s) for s in TICKERS]
    html = generate_html(quotes)
    with open("index.html", "w") as f:
        f.write(html)

if __name__ == "__main__":
    main()
