from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup as BS
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)

# Configuration
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
SMTP_SERVER = "smtp.gmail.com"
PORT = 587
EMAIL = os.environ.get("MY_EMAIL")
PASSWORD = os.environ.get("MY_EMAIL_PASSWORD")

# In-memory store for products
products = []

# Function to extract the price from the URL
def extract(url):
    try:
        page = requests.get(url, headers=HEADERS)
        soup = BS(page.content, "html.parser")
        price = soup.find(class_="a-price-whole")
        if price is None:
            return None
        return float(price.text.replace(",", ""))
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Function to send email notifications
def notify(price, url):
    try:
        server = SMTP(SMTP_SERVER, PORT)
        server.starttls()
        server.login(EMAIL, PASSWORD)

        msg = MIMEMultipart()
        msg['From'] = EMAIL
        msg['To'] = EMAIL
        msg['Subject'] = "BUY NOW"
        body = f"The price has fallen to ₹{price}. Buy it now: {url}"
        msg.attach(MIMEText(body, 'plain'))

        server.sendmail(EMAIL, EMAIL, msg.as_string())
        server.quit()
        print("Notification sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Route to handle form submission and price checking
@app.route('/', methods=['GET', 'POST'])
def index():
    global products
    message = None

    if request.method == 'POST':
        url = request.form['url']
        affordable_price = float(request.form['affordable_price'])
        price = extract(url)
        
        if price is not None:
            # Check if this product is already being tracked
            product_found = False
            for product in products:
                if product['url'] == url:
                    product_found = True
                    if price <= affordable_price and product['last_notified_price'] is None:
                        notify(price, url)
                        product['last_notified_price'] = price
                    elif price > affordable_price:
                        product['last_notified_price'] = None
                    break
            
            if not product_found:
                # Add new product to tracking
                if price <= affordable_price:
                    notify(price, url)
                products.append({
                    'url': url,
                    'affordable_price': affordable_price,
                    'last_notified_price': price if price <= affordable_price else None
                })
                message = f"Price is {'affordable' if price <= affordable_price else 'still too high'} at ₹{price}. Notification {'sent' if price <= affordable_price else 'not sent'}!"
        else:
            message = "Could not retrieve the price. Please check the URL and try again."

    return render_template('index.html', products=products, message=message)

if __name__ == '__main__':
    app.run(debug=True)
