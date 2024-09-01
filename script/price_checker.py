import requests
from bs4 import BeautifulSoup as BS
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json
from apscheduler.schedulers.background import BackgroundScheduler
import time

# Constants for email notifications
SMTP_SERVER = "smtp.gmail.com"
PORT = 587
EMAIL = os.environ.get("MY_EMAIL")
PASSWORD = os.environ.get("MY_EMAIL_PASSWORD")

# File path for storing product data
PRODUCTS_FILE = 'products.json'

def extract(url):
    """Extract the price from the given product URL."""
    HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    try:
        page = requests.get(url, headers=HEADERS)
        soup = BS(page.content, "html.parser")
        
        # Example selector for Amazon product price (adjust as needed)
        price = soup.find("span", {"id": "priceblock_ourprice"}) or soup.find("span", {"id": "priceblock_dealprice"})
        
        if price is None:
            return None
        
        # Extract price and remove currency symbols or commas
        price_text = price.get_text().replace(",", "").replace("₹", "").strip()
        return float(price_text)
    
    except Exception as e:
        print(f"An error occurred while extracting the price: {e}")
        return None

def notify(price, url):
    """Send an email notification about the price drop."""
    try:
        server = SMTP(SMTP_SERVER, PORT)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL
        msg['To'] = EMAIL
        msg['Subject'] = "Price Drop Alert"
        
        body = f"The price has dropped to ₹{price}. Check it out here: {url}"
        msg.attach(MIMEText(body, 'plain'))
        
        server.sendmail(EMAIL, EMAIL, msg.as_string())
        server.quit()
        
        print(f"Notification sent: Price is now ₹{price} for {url}")
    
    except Exception as e:
        print(f"An error occurred while sending the notification: {e}")

def load_products():
    """Load product data from JSON file."""
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, 'r') as file:
            return json.load(file)
    return []

def save_products(products):
    """Save product data to JSON file."""
    with open(PRODUCTS_FILE, 'w') as file:
        json.dump(products, file, indent=4)

def check_prices():
    """Check the prices of all tracked products and send notifications if needed."""
    products = load_products()
    for product in products:
        url = product['url']
        affordable_price = product['affordable_price']
        price = extract(url)
        
        if price is not None and price <= affordable_price:
            notify(price, url)
            product['last_notified_price'] = price
    
    save_products(products)

# Setup and start the background scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(check_prices, 'interval', minutes=1)
scheduler.start()

# Keep the script running
try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
