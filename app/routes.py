from app import app
from flask import render_template, request, redirect, url_for
import requests
from bs4 import BeautifulSoup  

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/extract', methods=['POST', 'GET'])
def extract():
    if request.method == "POST":
        try:
            product_id = request.form.get("product_id")
            url = f"https://www.ceneo.pl/{product_id}"
            response = requests.get(url)
            if response.status_code == requests.codes.ok:
                page = BeautifulSoup(response.text, "html.parser")
                opinions_count = page.select_one("a.product-review__link > span")
                if opinions_count:
                    # ekstrakcja
                    return redirect(url_for('product', product_id=product_id))
                return render_template('extract.html', error="Produkt o podanym kodzie nie posiada opinii.")
            return render_template('extract.html', error="Produkt o podanym kodzie nie istnieje.")
        except Exception as e:
            logging.error(f"Error during extraction: {e}")
            return render_template('extract.html', error="Wystąpił błąd podczas ekstrakcji.")
    return render_template('extract.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/product/<product_id>')
def product(product_id):
    return render_template('product.html', product_id=product_id)
