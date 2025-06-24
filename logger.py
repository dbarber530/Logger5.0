import os
import requests
import time
from datetime import datetime

# Set up Finnhub API key
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

# 100 ticker symbols, split into Group A and Group B
TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK.B", "UNH", "JPM",
    "V", "PG", "JNJ", "HD", "MA", "XOM", "LLY", "PFE", "CVX", "ABBV",
    "KO", "PEP", "BAC", "MRK", "AVGO", "DIS", "TMO", "ADBE", "CSCO", "ABT",
    "NFLX", "NKE", "CRM", "MCD", "INTC", "WMT", "AMD", "LIN", "QCOM", "COST",
    "ACN", "TXN", "DHR", "NEE", "LOW", "UNP", "MDT", "INTU", "AMGN", "HON",
    "NOW", "BLK", "RTX", "GILD", "AXP", "BA", "ISRG", "ELV", "ZTS", "SPGI",
    "GS", "T", "PLD", "SYK", "ADP", "CAT", "MO", "DE", "CI", "MMC",
    "CB", "LMT", "SO", "DUK", "USB", "C", "AMAT", "ADI", "PNC", "EQIX",
    "BDX", "REGN", "NSC", "ITW", "ICE", "EOG", "APD", "EW", "AON", "VRTX",
    "HUM", "PSA", "SHW", "EMR", "CL", "ETN", "FDX", "AIG", "TGT", "COF"
]

GROUP_A = TICKERS[:50]
GROUP_B = TICKERS[50:]

def fetch_stock_data(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        return {
            "symbol": symbol,
            "price": data.get("c"),
            "high": data.get("h"),
            "low": data.get("l"),
            "open": data.get("o"),
            "prev_close": data.get("pc"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}

def generate_html(stock_data, group_name):
    html = "<html><head><title>Logger5.0</title></head><body>"
    html += f"<h1>Logger5.0 — Group {group_name}</h1>"
    html += f"<h3>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</h3>"
    html += "<table border='1' cellpadding='6' cellspacing='0'>"
    html += "<tr><th>Symbol</th><th>Price</th><th>High</th><th>Low</th><th>Open</th><th>Prev Close</th><th>Time</th></tr>"
    
    for stock in stock_data:
        html += f"<tr><td>{stock['symbol']}</td>"
        if "error" in stock:
            html += f"<td colspan='6'>Error: {stock['error']}</td></tr>"
        else:
            html += (
                f"<td>{stock['price']}</td><td>{stock['high']}</td>"
                f"<td>{stock['low']}</td><td>{stock['open']}</td>"
                f"<td>{stock['prev_close']}</td><td>{stock['timestamp']}</td></tr>"
            )

    html += "</table></body></html>"
    return html

def main():
    group_toggle = True  # True = A, False = B

    while True:
        current_group = GROUP_A if group_toggle else GROUP_B
        group_name = "A" if group_toggle else "B"
        stock_data = []

        for symbol in current_group:
            stock_data.append(fetch_stock_data(symbol))
            time.sleep(0.5)  # Stay under rate limit: 60 requests/min (30s window with 50 tickers)

        html = generate_html(stock_data, group_name)

        # Save to index.html in project root
        with open("index.html", "w") as f:
            f.write(html)

        print(f"Updated index.html with Group {group_name} at {datetime.now()}")
        group_toggle = not group_toggle  # Switch to the other group next round
        time.sleep(60)  # Wait before switching groups

if __name__ == "__main__":
    main()
