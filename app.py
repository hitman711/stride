""" """
import json

from flask import (
    Flask, request, jsonify , Response)
from flask.views import MethodView
from flask_restful import Resource, Api 
from settings import db_session, DEBUG
from mixins import MultipleFieldLookUpMixin
from models import ProductInfo, CrawlPage, Website
import serializers


class Index(MethodView, MultipleFieldLookUpMixin):
    """ """
    queryset = db_session.query(ProductInfo).join(
        CrawlPage, Website
    ).filter(
        ProductInfo.crawl_page_id==CrawlPage.id,
        CrawlPage.website_id==Website.id)
    filter_fields = {
        'id': (ProductInfo, 'id'), 
        'sites': (Website, 'name'), 
        'brands': (ProductInfo, 'brand'),
        'category': (CrawlPage, 'category')
    }

    def get(self):
        index = self.get_paginated_queryset()
        result = serializers.ProductInfoSerializer(many=True).dump(index)
        return jsonify(result.data)


class Detail(MethodView, MultipleFieldLookUpMixin):
    """ """
    queryset = db_session.query(ProductInfo).join(
        CrawlPage, Website
    ).filter(
        ProductInfo.crawl_page_id==CrawlPage.id,
        CrawlPage.website_id==Website.id)  
    filter_fields = {
        'id': (ProductInfo, 'id')
    }

    def get(self, *args, **kwargs):
        index = self.get_object()
        result = serializers.ProductInfoSerializer().dump(index)
        return jsonify(result.data)


app = Flask(__name__)
api = Api(app)

app.add_url_rule('/', view_func=Index.as_view('index'))
app.add_url_rule('/<int:product_id>', view_func=Detail.as_view('detail'))

if __name__ == '__main__':
    app.run(port=8000, debug=DEBUG)
