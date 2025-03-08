from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Set headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

def scrape_amazon(query):
    """Scrape Amazon search results."""
    url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        return {"error": "Failed to fetch Amazon page"}

    soup = BeautifulSoup(response.text, "html.parser")
    products = []

    for item in soup.select(".s-main-slot .s-result-item"):
        title = item.select_one("h2 a span")
        price = item.select_one(".a-price-whole")
        link = item.select_one("h2 a")

        if title and price and link:
            products.append({
                "title": title.text.strip(),
                "price": f"₹{price.text.strip()}",
                "url": "https://www.amazon.in" + link["href"],
                "platform": "Amazon"
            })
    
    return products[:10]  # Return only top 10 products

def scrape_flipkart(query):
    """Scrape Flipkart search results."""
    url = f"https://www.flipkart.com/search?q={query.replace(' ', '%20')}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        return {"error": "Failed to fetch Flipkart page"}

    soup = BeautifulSoup(response.text, "html.parser")
    products = []

    for item in soup.select("._1AtVbE"):  # Flipkart listing selector
        title = item.select_one("._4rR01T") or item.select_one(".IRpwTa")
        price = item.select_one("._30jeq3")
        link = item.select_one("a._1fQZEK") or item.select_one("a.IRpwTa")

        if title and price and link:
            products.append({
                "title": title.text.strip(),
                "price": price.text.strip(),
                "url": "https://www.flipkart.com" + link["href"],
                "platform": "Flipkart"
            })
    
    return products[:10]  # Return only top 10 products

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query")
    platform = request.args.get("platform", "both").lower()

    if not query:
        return jsonify({"error": "Query parameter missing"}), 400

    results = []
    if platform in ["amazon", "both"]:
        results += scrape_amazon(query)
    if platform in ["flipkart", "both"]:
        results += scrape_flipkart(query)

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
