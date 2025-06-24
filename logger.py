import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FINNHUB_API_KEY")

TICKERS = [
    # Group A for example
    "AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "AMZN", "META", "UNH", "XOM", "JNJ"
    # Add more tickers as needed, grouped if using alternating fetches
]

def fetch_price(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("c")  # current price
    return None

def build_html(prices):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"<html><head><meta http-equiv='refresh' content='60'></head><body>"
    html += f"<h2>Logger5.0 - Updated: {now}</h2><table border='1'><tr><th>Ticker</th><th>Price</th></tr>"
    for ticker, price in prices.items():
        html += f"<tr><td>{ticker}</td><td>{price}</td></tr>"
    html += "</table></body></html>"
    return html

def main():
    prices = {}
    for ticker in TICKERS:
        price = fetch_price(ticker)
        if price is not None:
            prices[ticker] = price
    html_content = build_html(prices)
    with open("index.html", "w") as f:
        f.write(html_content)

if __name__ == "__main__":
    main()
