""" """
from datetime import datetime
import json

from settings import db_session, CRAWLED_DATA_INFORMATION, PARSER_MAPPING
import pandas

from bs4 import BeautifulSoup

import models

def zalando_parser(soup):
    category = ''
    brand = ''
    product_type = ''
    price = 0
    currency = ''
    name = ''
    for x in soup.select('script[type="application/ld+json"]'):
        product_data = json.loads(x.getText())
        brand = product_data.get('brand')
        name = product_data.get('name')
        if product_data.get('offers'):
            price = product_data['offers'][0]['price']
            currency = product_data['offers'][0]['priceCurrency']

    return [{
        'category':category, 
        'product_type':product_type,
        'name':name, 'brand':brand,
        'price':price, 'currency':currency}]

def ziengs_parser(soup):
    category = ''
    brand = ''
    product_type = ''
    price = 0
    currency = ''
    name = ''        
    for scrap in soup.select('meta[itemprop]'):
        if scrap['itemprop'] == 'category':
            category = scrap['content'].strip()
            product_type = scrap['content'].strip()
        if scrap['itemprop'] == 'brand':
            brand = scrap['content'].strip()
        if scrap['itemprop'] == 'priceCurrency':
            currency = scrap['content'].strip()
        if scrap['itemprop'] == 'price':
            price = float(scrap['content'].replace(',', '.'))

    for scrap in soup.select('h1[itemprop="name"]'):
        name = scrap.getText().strip()

    if not brand:
        for scrap in soup.select('h2[itemprop="brand"]'):
            brand = scrap.getText().strip()
    return [{
        'category':category, 
        'product_type':product_type,
        'name':name, 'brand':brand,
        'price':price, 'currency':currency}]

def omoda_parser(soup):
    category = ''
    brand = ''
    product_type = ''
    price = 0
    currency = ''
    name = ''   
    for scrap in soup.select('main[data-google]'):
        try:
            data = json.loads(scrap['data-google'])
            if data.get('name'):
                name = data['name'].strip()
            if data.get('brand'):
                brand = data['brand'].strip()
            if data.get('category'):
                category = data['category'].strip()
                product_type = data['category'].strip()
            if data.get('price'):
                price = float(data['price'])
        except Exception as e:
            pass

    for scrap in soup.select('meta[itemprop]'):
        if scrap['itemprop'] == 'priceCurrency':
            currency = scrap['content'].strip()

        if not category and scrap['itemprop'] == 'category':
            category = scrap['content'].strip()
            product_type = category

        if not name and scrap['itemprop'] == 'name':
            name = scrap['content'].strip()

        if not price and scrap['itemprop'] == 'price':
            price = float(scrap['content'].replace(',', '.'))

        if not brand and scrap['itemprop'] == 'brand':
            brand = scrap['content'].strip()

    return [{
        'category':category, 
        'product_type':product_type,
        'name':name, 'brand':brand,
        'price':price, 'currency':currency}]

class CrawlerParser():
    """ """

    def __init__(self):
        self.main()

    def html_parser(self, body, page_type, website_name):
        """ """
        soup = BeautifulSoup(body, "html.parser")
        if page_type == models.PageTypeEnum.product_listing:
            return []
        else:
            parser_mapping = PARSER_MAPPING[website_name]
            return eval(parser_mapping)(soup)

    def parse_crawler_document(self, path, website_id, website_name):
        crawler = pandas.read_json(
            path, chunksize=1, lines=True)

        for each_line in crawler:
            page_url = each_line.page_url.values[0]
            crawled_at =  pandas.Timestamp(each_line.crawled_at.values[0])
            page_type = each_line.page_type.values[0]
            page_number = 0
            category = ''
            sub_category = ''
            ordering = 0

            if page_type == models.PageTypeEnum.product_listing.value:
                if len(each_line.product_category.values[0]) > 1:
                    category=each_line.product_category.values[0][0]
                    sub_category=each_line.product_category.values[0][1]
                else:
                    category=each_line.product_category.values[0][0]
                body = [] # self.html_parser(each_line.body.values[0], page_type)
            else:
                body = self.html_parser(each_line.body.values[0], page_type, website_name)
                category = body[0]['category']

            crawl_row = models.CrawlPage(
                page_url=page_url,
                website_id=website_id,
                crawled_at=crawled_at,
                page_type=page_type,
                category=category)
            if page_type == models.PageTypeEnum.product_listing.value:
                crawl_row.list_page_info = models.ListPageInfo(
                    sub_category=sub_category,
                    ordering=ordering,
                    page_number=page_number)
        
            if body:
                crawl_row.product_infos = [
                    models.ProductInfo(
                        brand=each_product['brand'],
                        name=each_product['name'],
                        price=each_product['price'],
                        currency=each_product['currency'],
                    ) for each_product in body] 
            db_session.add(crawl_row)
            db_session.commit()

    def main(self):
        for crawer_info in CRAWLED_DATA_INFORMATION:
            website = models.Website(
                name = crawer_info['website_name'],
                document_path = crawer_info['crawl_data'])
            db_session.add(website)
            db_session.commit()
            self.parse_crawler_document(
                website.document_path,
                website.id,
                website.name)

CrawlerParser()