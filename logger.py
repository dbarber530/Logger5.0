import os
import requests
import base64
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# Environment Variables
GH_TOKEN = os.getenv("GH_TOKEN")
REPO = "dbarber530/Logger5.0"
FILE_PATH = "index.html"

# Sample ticker data (static for now)
tickers = [
    {"symbol": "AAPL", "price": 180.25, "change": 1.45, "volume": 22000000},
    {"symbol": "TSLA", "price": 950.30, "change": -12.70, "volume": 34000000},
    {"symbol": "AMZN", "price": 123.90, "change": 0.20, "volume": 18500000}
]

# Build HTML table rows
rows = "".join(
    f"""
    <tr>
        <td>{q['symbol']}</td>
        <td>{q['price']}</td>
        <td>{q['change']:.2f}</td>
        <td>{q['volume']}</td>
    </tr>
    """ for q in tickers
)

# Timestamp (UTC)
now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

# HTML page
html = f"""<!DOCTYPE html>
<html>
<head><title>Logger5.0</title></head>
<body>
    <h2>Logger5.0</h2>
    <p>Updated: {now}</p>
    <hr>
    <table border="1">
        <thead>
            <tr>
                <th>Symbol</th>
                <th>Price</th>
                <th>Change</th>
                <th>Volume</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
</body>
</html>
"""

# Convert HTML content to base64
encoded_content = base64.b64encode(html.encode("utf-8")).decode("utf-8")

# GitHub API endpoint
api_url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

# Get existing file SHA
res = requests.get(api_url, headers={
    "Authorization": f"Bearer {GH_TOKEN}",
    "Accept": "application/vnd.github+json"
})
sha = res.json().get("sha")

# Prepare payload
data = {
    "message": "Update index.html with latest data",
    "content": encoded_content,
    "branch": "main"
}
if sha:
    data["sha"] = sha

# PUT to GitHub
headers = {
    "Authorization": f"Bearer {GH_TOKEN}",
    "Accept": "application/vnd.github+json"
}
response = requests.put(api_url, json=data, headers=headers)

print("GitHub update status:", response.status_code, response.text)
