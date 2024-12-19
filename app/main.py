import logging
import re

import gdown

from app.extensions import db
from flask import Flask, redirect, render_template, request, jsonify

from openai import OpenAI

from pinecone import Pinecone
from pinecone_text.sparse import BM25Encoder

from sqlalchemy import and_
from app.models import Rating, Product

from app.config import Config

from app.utils import hybrid_scale

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
app.config.from_object(Config)

#
db.init_app(app)

#
with app.app_context():
    db.create_all()

#
pc = Pinecone(api_key=Config.PINECONE_API_KEY)
pc_index = pc.Index(host=Config.PINECONE_HOST)

#
deepinfra = OpenAI(api_key=Config.DEEPINFRA_API_KEY, base_url=Config.DEEPINFRA_HOST)

#
bm25 = BM25Encoder()
#
gdown.download(id=Config.BM25_FILE_ID, output='data/bm25.json', quiet=False)
#
bm25.load('data/bm25.json')


@app.route('/')
def hello_world():
    return redirect('search')


@app.route('/search')
def search():
    squery = re.sub(r'\s+', ' ', request.args.get('q', '').strip()).replace("ნაძვისხე", "ნაძვის ხე")

    if not squery:
        return render_template('search.html')

    #
    dense_vec = deepinfra.embeddings.create(input=squery, model="BAAI/bge-m3", encoding_format="float").data[
        0].embedding
    sparse_vec = bm25.encode_queries(squery)

    dense_vec, sparse_vec = hybrid_scale(dense_vec, sparse_vec, 0.8)

    #
    res = pc_index.query(vector=dense_vec, sparse_vector=sparse_vec, top_k=60, namespace='bge-m3')
    matches = res.get('matches', [])
    matches = {m['id']: m['score'] for m in matches if m['score'] > 0.38}
    ids = list(matches.keys())

    #
    products = Product.query.filter(Product.id.in_(ids)).all()
    ratings = Rating.query.filter(and_(Rating.product_id.in_(ids), Rating.squery == squery)).all()
    ratings = {r.product_id: r.rating for r in ratings}

    #
    for p in products:
        p.score = matches[p.id]
        p.rating = ratings.get(p.id, 0)

    products = sorted(products, key=lambda x: x.score, reverse=True)

    return render_template('search.html', query=squery, products=products)


@app.route('/search/rate', methods=['POST'])
def submit_rating():
    try:
        data = request.json
        pid = data.get('productId')
        barcode = data.get('barcode')
        query = data.get('query')
        score = data.get('score')

        if not query or not pid or not score or not barcode:
            return jsonify({"message": "Missing Required Fields"}), 400

        rating = Rating(product_id=pid, barcode=barcode, squery=query, rating=score)
        db.session.add(rating)
        db.session.commit()

        return jsonify({"message": "Rating submitted successfully"}), 200
    except Exception as e:
        logging.error(e)
        return jsonify({"message": str(e)}), 500


@app.route('/search/rate', methods=['DELETE'])
def delete_rating():
    try:
        data = request.json
        pid = data.get('productId')
        barcode = data.get('barcode')
        squery = data.get('query')
        score = data.get('score')

        if not squery or not pid or not score or not barcode:
            return jsonify({"message": "Missing Required Fields"}), 400

        db.session.query(Rating).filter(
            and_(
                Rating.product_id == pid,
                Rating.barcode == barcode,
                Rating.squery == squery
            )
        ).delete()
        db.session.commit()

        return jsonify({"message": "Rating submitted successfully"}), 200
    except Exception as e:
        logging.error(e)
        return jsonify({"message": str(e)}), 500


if __name__ == '__main__':
    app.run()
