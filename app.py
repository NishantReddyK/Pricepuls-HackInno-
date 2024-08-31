from flask import Flask, render_template, request, redirect, url_for
from script.price_checker import extract, notify

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    price = None
    if request.method == 'POST':
        url = request.form['url']
        affordable_price = float(request.form['affordable_price'])
        price = extract(url)
        if price is not None and price <= affordable_price:
            notify(price, url)
            return render_template('index.html', price=price, message=f"Price is affordable at {price}. Notification sent!")
        elif price is not None:
            return render_template('index.html', price=price, message=f"Price is still {price}, which is above your affordable price.")
        else:
            return render_template('index.html', message="Could not retrieve the price. Please check the URL and try again.")
    
    return render_template('index.html', price=price)

if __name__ == '__main__':
    app.run(debug=True)
