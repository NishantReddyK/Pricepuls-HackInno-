import requests
from bs4 import BeautifulSoup as BS
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}

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

SMTP_SERVER = "smtp.gmail.com"
PORT = 587
EMAIL = os.environ.get("MY_EMAIL")
PASSWORD = os.environ.get("MY_EMAIL_PASSWORD")

def notify(price, url):
    server = SMTP(SMTP_SERVER, PORT)
    server.starttls()
    server.login(EMAIL, PASSWORD)

    msg = MIMEMultipart()
    msg['From'] = EMAIL
    msg['To'] = EMAIL
    msg['Subject'] = "BUY NOW"
    body = f"The price has fallen to {price}. Buy it now: {url}"
    msg.attach(MIMEText(body, 'plain'))

    server.sendmail(EMAIL, EMAIL, msg.as_string())
    server.quit()
