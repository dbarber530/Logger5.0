import os
import requests
from datetime import datetime
import time

API_KEY = os.getenv('FINNHUB_API_KEY')
GROUP_A = ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "META", "AMZN", "AMD", "NFLX", "BABA",
           "INTC", "QCOM", "CSCO", "AVGO", "TXN", "ADBE", "CRM", "ORCL", "PYPL", "SHOP",
           "PLTR", "UBER", "LYFT", "SNOW", "DOCU", "ROKU", "ZM", "SQ", "SOFI", "COIN",
           "CVX", "XOM", "JNJ", "PFE", "MRNA", "LLY", "UNH", "ABBV", "BMY", "AZN",
           "BA", "GE", "LMT", "NOC", "RTX", "CAT", "DE", "GM", "F", "TSM"]

GROUP_B = ["SPY", "VOO", "QQQ", "DIA", "IWM", "ARKK", "VTI", "VUG", "VTWO", "IWF",
           "XLF", "XLE", "XLK", "XLY", "XLV", "XLI", "XLC", "XLP", "XLB", "XLRE",
           "GME", "AMC", "BBBY", "BB", "NOK", "NKLA", "LCID", "RIVN", "APE", "T",
           "VZ", "KO", "PEP", "MCD", "WMT", "COST", "PG", "TGT", "HD", "LOW",
           "DIS", "SBUX", "NKE", "LULU", "CVS", "WBA", "KR", "TJX", "ROST", "DG"]

def fetch_data(symbols):
    results = []
    for symbol in symbols:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            results.append({
                "symbol": symbol,
                "price": data.get("c", 0),
                "change": data.get("d", 0),
                "percent": data.get("dp", 0)
            })
        time.sleep(0.1)  # small pause to avoid burst
    return results

def write_html(group_a, group_b):
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    with open("index.html", "w") as f:
        f.write(f"<html><head><title>BarberBot Logger</title></head><body>")
        f.write(f"<h1>Live Ticker Feed</h1><p>Last updated: {now}</p>")
        
        f.write("<h2>Group A (Tickers 1–50)</h2><ul>")
        for item in group_a:
            f.write(f"<li>{item['symbol']}: ${item['price']} ({item['change']} / {item['percent']}%)</li>")
        f.write("</ul>")
        
        f.write("<h2>Group B (Tickers 51–100)</h2><ul>")
        for item in group_b:
            f.write(f"<li>{item['symbol']}: ${item['price']} ({item['change']} / {item['percent']}%)</li>")
        f.write("</ul>")

        f.write("</body></html>")

def main():
    group_a_data = fetch_data(GROUP_A)
    group_b_data = fetch_data(GROUP_B)
    write_html(group_a_data, group_b_data)

if __name__ == "__main__":
    main()
