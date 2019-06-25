""" """
import json

from flask import (
    Flask, request, jsonify, make_response)
from flask.views import MethodView
from flask_restful import Resource, Api 
from settings import db_session, DEBUG
from mixins import MultipleFieldLookUpMixin
from models import ProductInfo, CrawlPage, Website
import serializers


class Index(MethodView, MultipleFieldLookUpMixin):
    """ API endpoint to fetch product list """
    # Default queryset
    queryset = db_session.query(ProductInfo).join(
        CrawlPage, Website
    ).filter(ProductInfo.crawl_page_id==CrawlPage.id,
        CrawlPage.website_id==Website.id)
    # Default query parameter 
    filter_fields = {
        'id': (ProductInfo, 'id'), 
        'site': (Website, 'name'), 
        'brand': (ProductInfo, 'brand'),
        'category': (CrawlPage, 'category'),
        'name': (ProductInfo, 'name')
    }

    def get(self):
        """ API endpoint to fetch product list """
        index = self.get_paginated_queryset()
        result = serializers.ProductInfoSerializer(many=True).dump(index)
        return make_response(jsonify(result.data), 200)


class Detail(MethodView, MultipleFieldLookUpMixin):
    """ API endpoint to fetch product detail """
    # Default queryset
    queryset = db_session.query(ProductInfo).join(
        CrawlPage, Website
    ).filter(ProductInfo.crawl_page_id==CrawlPage.id,
        CrawlPage.website_id==Website.id)
    
    def get_queryset(self):
        return self.filter_queryset().filter(
            ProductInfo.id==request.view_args.get('product_id'))

    def get(self, *args, **kwargs):
        """ API endpoint to fetch product detail """
        index = self.get_object()
        if not index:
            return make_response(jsonify({'detail': 'not found'}), 404)
        result = serializers.ProductInfoSerializer().dump(index)
        return make_response(jsonify(result.data), 200)


app = Flask(__name__)
api = Api(app)

# Product list api
app.add_url_rule('/', view_func=Index.as_view('index'))
# Product detail api
app.add_url_rule('/<int:product_id>', view_func=Detail.as_view('detail'))

if __name__ == '__main__':
    app.run(port=8000, debug=DEBUG)
