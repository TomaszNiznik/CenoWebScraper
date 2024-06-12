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

opinions_data = [
    {
        "product_id": 1,
        "opinions": [
            {"id": 1, "author": "User1", "recommendation": "yes", "rating": 5, "verified_purchase": True,
             "review_date": "2023-01-01", "purchase_date": "2022-12-25", "useful": 10, "not_useful": 0, "content": "Great product!",
             "cons": "None", "pros": "Everything"}
        ]
    },
    {
        "product_id": 2,
        "opinions": [
            {"id": 2, "author": "User2", "recommendation": "no", "rating": 2, "verified_purchase": True,
             "review_date": "2023-01-02", "purchase_date": "2022-12-26", "useful": 5, "not_useful": 3, "content": "Not good",
             "cons": "Price", "pros": "Design"}
        ]
    },
    {
        "product_id": 3,
        "opinions": [
            {"id": 3, "author": "User3", "recommendation": "yes", "rating": 4, "verified_purchase": False,
             "review_date": "2023-01-03", "purchase_date": "2022-12-27", "useful": 8, "not_useful": 1, "content": "Good product",
             "cons": "Battery", "pros": "Performance"}
        ]
    }
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
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                response = requests.get(url, headers=headers)
                if response.status_code == requests.codes.ok:
                    page = BeautifulSoup(response.text, "html.parser")
                    opinions_count = page.select_one("a.product-review__link > span")
                    if opinions_count:
                        update_product_data(product_id, page)
                        return redirect(url_for('product', product_id=product_id))
                    else:
                        error_message = "Produkt o podanym kodzie nie posiada opinii."
                else:
                    logging.error(f"Failed to fetch product page. Status code: {response.status_code}")
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
        product = next((p for p in products_data if p["id"] == product_id), None)
        opinions = next((o["opinions"] for o in opinions_data if o["product_id"] == product_id), [])
        if product:
            return render_template('product.html', product=product, opinions=opinions)
        else:
            return "Produkt nie został znaleziony."
    except ValueError:
        return "Nieprawidłowy identyfikator produktu."

@app.route('/download_opinions/<int:product_id>', methods=['POST'])
def download_opinions(product_id):
    product = next((p for p in products_data if p["id"] == product_id), None)
    opinions = next((o["opinions"] for o in opinions_data if o["product_id"] == product_id), [])
    if not product:
        return "Produkt nie został znaleziony."
    
    file_format = request.form.get("file_format")
    if file_format not in ['csv', 'xlsx', 'json']:
        return "Nieprawidłowy format pliku."

    opinions_df = pd.DataFrame(opinions)

    if file_format == 'csv':
        opinions_df.to_csv(f"opinions_{product_id}.csv", index=False)
    elif file_format == 'xlsx':
        opinions_df.to_excel(f"opinions_{product_id}.xlsx", index=False)
    elif file_format == 'json':
        opinions_df.to_json(f"opinions_{product_id}.json", orient='records')

    return redirect(url_for('product', product_id=product_id))

if __name__ == "__main__":
    app.run(debug=True)
