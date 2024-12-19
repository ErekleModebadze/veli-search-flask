from typing import List

from sqlalchemy import ARRAY

from extensions import db


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.String, primary_key=True)
    barcode: str = db.Column(db.String)

    brand_ka: str = db.Column(db.String)
    name_ka: str = db.Column(db.String)
    label_ka: str = db.Column("labeled_headline_ka", db.String)

    brand_en: str = db.Column(db.String)
    name_en: str = db.Column(db.String)
    label_en: str = db.Column("labeled_headline_en", db.String)

    m_categories_ka: List[str] = db.Column("mother_categories_ka", ARRAY(db.String))
    m_categories_en: List[str] = db.Column("mother_categories_en", ARRAY(db.String))

    categories_ka: List[str] = db.Column("categories_ka", ARRAY(db.String))
    categories_en: List[str] = db.Column("categories_en", ARRAY(db.String))

    key_specs_ka: List[str] = db.Column(ARRAY(db.String))
    value_specs_ka: List[str] = db.Column(ARRAY(db.String))

    key_specs_en: List[str] = db.Column(ARRAY(db.String))
    value_specs_en: List[str] = db.Column(ARRAY(db.String))

    tags: List[str] = db.Column(ARRAY(db.String))

    price: float = db.Column(db.Float)
    start_price: float = db.Column(db.Float)


class Rating(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    barcode = db.Column(db.String)

    product_id = db.Column(db.String, db.ForeignKey('products.id'))
    squery = db.Column(db.String)
    rating = db.Column(db.Integer)
