""" """
from flask import Flask, jsonify
from flask_marshmallow import Marshmallow

app = Flask(__name__)
ma = Marshmallow(app)


class ProductInfoSerializer(ma.Schema):
    """ API Schema for product information """
    category = ma.Field(attribute='crawl_page.category')
    url = ma.Field(attribute='crawl_page.page_url')
    website = ma.Field(attribute='crawl_page.website.name')

    class Meta:
        # Fields to expose
        fields = (
            'id', 'brand', 'name', 'price',
            'currency', 'category', 'url', 'website')
