import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FINNHUB_API_KEY")
TICKER = "AAPL"

def get_price(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}"
    res = requests.get(url)
    data = res.json()
    return data.get("c")  # current price

if __name__ == "__main__":
    price = get_price(TICKER)
    print(f"{TICKER} price: {price}")
