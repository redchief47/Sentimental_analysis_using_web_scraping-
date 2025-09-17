from flask import Flask, request, jsonify, send_from_directory
import os, re, time
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Selenium imports for Edge
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Download VADER lexicon
nltk.download('vader_lexicon')

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
sia = SentimentIntensityAnalyzer()


# ------------------- Helper functions -------------------
def extract_asin(url):
    """Extract ASIN from Amazon URL"""
    match = re.search(r"/([A-Z0-9]{10})(?:[/?]|$)", url)
    return match.group(1) if match else None


# ------------------- Amazon scraper -------------------
def scrape_amazon_reviews(asin, max_pages=2):
    reviews = []
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-logging")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-features=SmartScreen")

    driver = webdriver.Edge(service=EdgeService("C:/Drivers/msedgedriver.exe"), options=options)

    # Change path to your EdgeDriver
    driver = webdriver.Edge(service=EdgeService("C:/Drivers/msedgedriver.exe"), options=options)
    wait = WebDriverWait(driver, 10)

    try:
        for page in range(1, max_pages + 1):
            url = f"https://www.amazon.in/product-reviews/{asin}/?pageNumber={page}"
            driver.get(url)
            time.sleep(2)  # let JS render
            try:
                elems = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'span[data-hook="review-body"]')))
                for e in elems:
                    text = e.text.strip()
                    if text:
                        reviews.append(text)
            except:
                continue
    finally:
        driver.quit()
        return reviews[:10]

# ------------------- Flipkart scraper -------------------
def scrape_flipkart_reviews(url, max_pages=2):
    reviews = []
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Edge(service=EdgeService("C:/Drivers/msedgedriver.exe"), options=options)
    wait = WebDriverWait(driver, 10)

    try:
        for page in range(1, max_pages + 1):
            page_url = f"{url}&page={page}"
            driver.get(page_url)
            time.sleep(2)  # wait for JS

            try:
                elems = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div._27M-vq')))
                for e in elems:
                    text = e.text.strip()
                    if text:
                        reviews.append(text)
            except:
                continue
    finally:
        driver.quit()
        return reviews[:10]


# ------------------- Flask routes -------------------
@app.route("/scrape", methods=["POST"])
def scrape():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        if "amazon." in url or "amzn." in url:
            asin = extract_asin(url)
            if not asin:
                return jsonify({"error": "ASIN not found"}), 400
            reviews = scrape_amazon_reviews(asin)

        elif "flipkart.com" in url:
            reviews = scrape_flipkart_reviews(url)

        elif "alibaba.com" in url:
            return jsonify({"error": "Alibaba scraping not supported yet"}), 400

        else:
            return jsonify({"error": "Unsupported site"}), 400

        if not reviews:
            return jsonify({"error": "No reviews found"}), 400

        return jsonify({"reviews": reviews})
    except Exception as e:
        return jsonify({"error": f"Scraping failed: {e}"}), 500


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    reviews = data.get("reviews", [])
    if not reviews:
        return jsonify({"error": "No reviews to analyze"}), 400

    results = []
    for review in reviews:
        score = sia.polarity_scores(review)
        sentiment = (
            "positive" if score['compound'] > 0.05
            else "negative" if score['compound'] < -0.05
            else "neutral"
        )
        results.append({
            'text': review,
            'sentiment': sentiment,
            'score': score
        })

    return jsonify({"results": results})


# ------------------- Serve frontend -------------------
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


# ------------------- Run server -------------------
if __name__ == "__main__":
    app.run(debug=True)
