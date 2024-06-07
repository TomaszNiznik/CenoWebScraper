from flask import render_template, request, redirect, url_for, jsonify
import requests
from bs4 import BeautifulSoup  
from app import app 
import logging
import pandas as pd

products_data = [
    {"id": 1, "name": "Product 1", "opinions_count": 10, "cons_count": 5, "pros_count": 7, "avg_rating": 4.5},
    {"id": 2, "name": "Product 2", "opinions_count": 15, "cons_count": 3, "pros_count": 10, "avg_rating": 4.7},
    {"id": 3, "name": "Product 3", "opinions_count": 20, "cons_count": 2, "pros_count": 15, "avg_rating": 4.3},
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products')
def products():
    return render_template('products.html', products=products_data)

@app.route('/extract', methods=['POST', 'GET'])
def extract():
    error_message = None
    if request.method == "POST":
        try:
            product_id = request.form.get("product_id")
            if not product_id:
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
                    error_message = "Nie udało się pobrać strony produktu."
        except Exception as e:
            logging.error(f"Error during extraction: {e}")
            error_message = "Wystąpił błąd podczas ekstrakcji. Sprawdź poprawność kodu produktu."
    return render_template('extract.html', error_message=error_message)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/product/<int:product_id>')
def product(product_id):
    try:
        product_id = int(product_id)
        product = next((p for p in products_data if p["id"] == product_id), None)
        if product:
            return render_template('product.html', product=product)
        else:
            return "Produkt nie został znaleziony."
    except ValueError:
        return "Nieprawidłowy identyfikator produktu."

@app.route('/download_opinions/<int:product_id>', methods=['POST'])
def download_opinions(product_id):
    product = next((p for p in products_data if p["id"] == product_id), None)
    if not product:
        return "Produkt nie został znaleziony."
    
    file_format = request.form.get("file_format")
    if file_format not in ['csv', 'xlsx', 'json']:
        return "Nieprawidłowy format pliku."

    # Pobierz opinie w formacie DataFrame
    opinions = {
        "Opinions Count": [product["opinions_count"]],
        "Cons Count": [product["cons_count"]],
        "Pros Count": [product["pros_count"]],
        "Average Rating": [product["avg_rating"]]
    }
    opinions_df = pd.DataFrame(opinions)

    # Eksportuj dane do wybranego formatu
    if file_format == 'csv':
        opinions_df.to_csv(f"opinions_{product_id}.csv", index=False)
    elif file_format == 'xlsx':
        opinions_df.to_excel(f"opinions_{product_id}.xlsx", index=False)
    elif file_format == 'json':
        opinions_df.to_json(f"opinions_{product_id}.json", orient='records')

    return redirect(url_for('product', product_id=product_id))

if __name__ == "__main__":
    app.run(debug=True)
