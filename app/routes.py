from app import app
from app import utils
from flask import render_template, request, redirect, url_for, flash, jsonify
import requests
import os
import json
from bs4 import BeautifulSoup

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/home')
def home():
    return render_template('base.html')

@app.route('/extract', methods=['POST', 'GET'])
def extract():
    if request.method == "POST":
        product_id = request.form.get("product_id")

        if not product_id:
            return render_template('extract.html', error="Proszę wpisać kod produktu!")

        # Sprawdzenie poprawności kodu produktu
        if not product_id.isdigit():
            return render_template('extract.html', error="Niepoprawny kod produktu!")

        # Sprawdzanie, czy produkt już istnieje
        if os.path.exists("app/data/products.json"):
            with open("app/data/products.json", "r", encoding="UTF-8") as pf:
                products = json.load(pf)
                if any(product["id"] == product_id for product in products):
                    return render_template('extract.html', error="Produkt o podanym kodzie już istnieje!")

        # Walidacja
        url = f"https://www.ceneo.pl/{product_id}"
        response = requests.get(url)
        if response.status_code == requests.codes.ok:
            page = BeautifulSoup(response.text, "html.parser")
            opinions_count = page.select_one("a.product-review__link > span")
            if opinions_count:
                url = f"https://www.ceneo.pl/{product_id}#tab=reviews"
                all_opinions = []
                while url:
                    response = requests.get(url)
                    page = BeautifulSoup(response.text, "html.parser")
                    opinions = page.select("div.js_product-review")
                    for opinion in opinions:
                        single_opinion = {
                            key: utils.get_data(opinion, *value)
                            for key, value in utils.selectors.items()
                        }
                        all_opinions.append(single_opinion)
                    try:
                        url = "https://ceneo.pl" + page.select_one("a.pagination__next")["href"]
                    except TypeError:
                        url = None

                if not os.path.exists("app/data"):
                    os.mkdir("app/data")
                if not os.path.exists("app/data/opinions"):
                    os.mkdir("app/data/opinions")

                with open(f"app/data/opinions/{product_id}.json", "w", encoding="UTF-8") as jf:
                    json.dump(all_opinions, jf, indent=4, ensure_ascii=False)

                # Zapisanie danych o produkcie do pliku products.json
                product_data = {
                    "id": product_id,
                    "name": page.select_one("h1.product-top__product-info__name").text.strip(),
                    "opinions_count": int(opinions_count.text.strip().split()[0]),
                    "pros_count": sum(1 for opinion in all_opinions if opinion["pros"]),
                    "cons_count": sum(1 for opinion in all_opinions if opinion["cons"]),
                    "avg_rating": sum(float(opinion["stars"].split("/")[0].replace(",", ".")) for opinion in all_opinions) / len(all_opinions)
                }

                if os.path.exists("app/data/products.json"):
                    with open("app/data/products.json", "r", encoding="UTF-8") as pf:
                        products = json.load(pf)
                else:
                    products = []

                products.append(product_data)

                with open("app/data/products.json", "w", encoding="UTF-8") as pf:
                    json.dump(products, pf, indent=4, ensure_ascii=False)

                return redirect(url_for('product', product_id=product_id))
            else:
                return render_template('extract.html', error="Produkt nie posiada opinii!")
        else:
            return render_template('extract.html', error="Produkt o podanym kodzie nie istnieje!")
    else:
        return render_template('extract.html')
    
@app.route('/products')
def products():
    if os.path.exists("app/data/products.json"):
        with open("app/data/products.json", "r", encoding="UTF-8") as pf:
            products = json.load(pf)
    else:
        products = []
    return render_template('products.html', products=products)

@app.route('/product/<product_id>')
def product(product_id):
    opinions_file = f"app/data/opinions/{product_id}.json"
    if os.path.exists(opinions_file):
        with open(opinions_file, "r", encoding="UTF-8") as jf:
            product_opinions = json.load(jf)
        return render_template('product.html', opinions=product_opinions, product_id=product_id)
    else:
        return render_template('product.html', error="Opinie dla tego produktu nie zostały znalezione!", product_id=product_id)
