from flask import render_template, request, redirect, url_for
import requests
from bs4 import BeautifulSoup  
from app import app  # Dodaj import obiektu app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/extract', methods=['POST', 'GET'])
def extract():
    error_message = None  # Domyślnie brak komunikatu błędu
    if request.method == "POST":
        try:
            product_id = request.form.get("product_id")
            if not product_id:  # Sprawdzenie, czy pole ID produktu jest puste
                error_message = "Proszę wprowadzić kod produktu."
            else:
                url = f"https://www.ceneo.pl/{product_id}"
                response = requests.get(url)
                if response.status_code == requests.codes.ok:
                    page = BeautifulSoup(response.text, "html.parser")
                    opinions_count = page.select_one("a.product-review__link > span")
                    if opinions_count:
                        # ekstrakcja
                        return redirect(url_for('product', product_id=product_id))
                    else:
                        error_message = "Produkt o podanym kodzie nie posiada opinii."
                else:
                    error_message = "Produkt o podanym kodzie nie istnieje."
        except Exception as e:
            logging.error(f"Error during extraction: {e}")
            error_message = "Wystąpił błąd podczas ekstrakcji."
    return render_template('extract.html', error_message=error_message)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/product/<product_id>')
def product(product_id):                                                                                                                                
        return render_template('product.html', product_id=product_id)



