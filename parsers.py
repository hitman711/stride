""" """
import json
from datetime import datetime

from settings import (
    db_session, CRAWLED_DATA_INFORMATION, PARSER_MAPPING,
    LIST_PARSER_MAPPING, CRAWLER_ROW_COUNT)
import pandas

from bs4 import BeautifulSoup

import models

def zalando_parser(soup):
    """ Parsed zalando html body parser
    
    Parameter
    ---------
    `soup`: <html>
        zalando product detail html code
    
    Return
    ------
    parser_data_list: <list>
        List of parser object 

        `category`: <str>
            Product category

        `name`: <str>
            Product name
        
        `brand`: <str>
            Product brand name

        `price`: <float>
            Product price

        `currency`: <str>
            Product currency
    """
    category = ''
    brand = ''
    price = 0
    currency = ''
    name = ''
    for scrap in soup.select('script[type="application/ld+json"]'):
        product_data = json.loads(scrap.getText())
        brand = product_data.get('brand', '').strip()
        name = product_data.get('name', '').strip()
        if product_data.get('offers'):
            price = product_data['offers'][0]['price']
            currency = product_data['offers'][0]['priceCurrency']
    
    for scrap in soup.select('[data-article-category]'):
        category = scrap['data-article-category'].strip()

    return [{
        'category':category, 'name':name, 'brand':brand,
        'price':price, 'currency':currency}]

def ziengs_parser(soup):
    """ Parsed ziengs html body parser
    
    Parameter
    ---------
    `soup`: <html>
        ziengs product detail html code
    
    Return
    ------
    parser_data_list: <list>
        List of parser object 

        `category`: <str>
            Product category

        `name`: <str>
            Product name
        
        `brand`: <str>
            Product brand name

        `price`: <float>
            Product price

        `currency`: <str>
            Product currency
    """
    category = ''
    brand = ''
    price = 0
    currency = ''
    name = ''        
    for scrap in soup.select('meta[itemprop]'):
        if scrap['itemprop'] == 'category':
            category = scrap['content'].strip()
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
        'category':category, 'name':name, 'brand':brand,
        'price':price, 'currency':currency}]

def omoda_parser(soup):
    """ Parsed omoda html body parser
    
    Parameter
    ---------
    `soup`: <html>
        omoda product detail html code
    
    Return
    ------
    parser_data_list: <list>
        List of parser object 

        `category`: <str>
            Product category

        `name`: <str>
            Product name
        
        `brand`: <str>
            Product brand name

        `price`: <float>
            Product price

        `currency`: <str>
            Product currency
    """
    category = ''
    brand = ''
    price = 0
    currency = ''
    name = ''   
    for scrap in soup.select('[data-google]'):
        try:
            data = json.loads(scrap['data-google'])
            if data.get('name'):
                name = data['name'].strip()
            if data.get('brand'):
                brand = data['brand'].strip()
            if data.get('category'):
                category = data['category'].strip()
            if data.get('price'):
                price = float(data['price'])
        except Exception as e:
            pass

    for scrap in soup.select('[itemprop]'):
        if scrap['itemprop'] == 'priceCurrency':
            currency = scrap['content'].strip()

        if not category and scrap['itemprop'] == 'category':
            category = scrap['content'].strip()

        if not name and scrap['itemprop'] == 'name':
            name = scrap['content'].strip()

        if not price and scrap['itemprop'] == 'price':
            price = float(scrap['content'].replace(',', '.'))

        if not brand and scrap['itemprop'] == 'brand':
            brand = scrap['content'].strip()

    return [{
        'category':category, 'name':name, 'brand':brand,
        'price':price, 'currency':currency}]

def omoda_list_parser(soup):
    """ """
    product_list = []
    for scrap in soup.select('[data-google]'):
        category = ''
        brand = ''
        price = 0
        currency = ''
        name = ''
        try:
            data = json.loads(scrap['data-google'])
            if data.get('name'):
                name = data['name'].strip()
            if data.get('brand'):
                brand = data['brand'].strip()
            if data.get('category'):
                category = data['category'].strip()
            if data.get('price'):
                price = float(data['price'])
        except Exception as e:
            pass
        product_list.append({
        'category':category, 'name':name, 'brand':brand,
        'price':price, 'currency':currency})
    return product_list

class CrawlerParser():
    """ """

    def __init__(self):
        """ Initialize crawler """
        self.main()

    def html_parser(self, body, page_type, website_name):
        """ Assign valid parser to html body
        
        Parameter
        ---------
        `body`: <str>
            Html string body

        `page_type`: <str>
            Page type name 

        `website_name`: <str>
            Website name
        
        Return
        ------
        parser_data_list: <list>
            List of parser object
        """
        soup = BeautifulSoup(body, "html.parser")
        if page_type == models.PageTypeEnum.product_listing:
            parser_mapping = LIST_PARSER_MAPPING.get(website_name)
            if not parser_mapping:
                return []
            return eval(parser_mapping)(soup)
        else:
            parser_mapping = PARSER_MAPPING[website_name]
            return eval(parser_mapping)(soup)

    def parse_crawler_document(self, path, website_id, website_name):
        """ Read crawler file and pass data from body column

        Parameter
        ---------
        `path`: <str>
            Crawler file

        `website_id`: <int>
            Website object id
        
        `website_name`: <str>
            Website name
        """
        # Read pathfile in chunksize using pandas
        crawler = pandas.read_json(path, chunksize=1, lines=True)

        # Iterate chunk file row
        for each_line in crawler:
            # Page url
            page_url = each_line.page_url.values[0]
            # Crawler date convert string to datetime
            crawled_at =  pandas.Timestamp(each_line.crawled_at.values[0])
            # Page type
            page_type = each_line.page_type.values[0]
            # Product list page number
            page_number = 0
            # Product category
            category = ''
            # Product sub category
            sub_category = ''
            # Product list order
            ordering = 0

            # Check each row page_type
            # Parse data based on page type 
            if page_type == models.PageTypeEnum.product_listing.value:
                # Split category and sub category for product listing page
                if len(each_line.product_category.values[0]) > 1:
                    category=each_line.product_category.values[0][0]
                    sub_category=each_line.product_category.values[0][1]
                else:
                    category=each_line.product_category.values[0][0]
                body = [] # self.html_parser(each_line.body.values[0], page_type)
            else:
                # Pase row body to html parser
                body = self.html_parser(each_line.body.values[0], page_type, website_name)
                category = body[0]['category']

            # Add crawled data in crawlPage table
            crawl_row = models.CrawlPage(
                page_url=page_url, website_id=website_id,
                crawled_at=crawled_at, page_type=page_type,
                category=category)

            if page_type == models.PageTypeEnum.product_listing.value:
                # Add product listing page information in ListPageInfo table 
                crawl_row.list_page_info = models.ListPageInfo(
                    sub_category=sub_category, ordering=ordering,
                    page_number=page_number)

            # Check html parser response    
            if body:
                # Add each product in ProductInfo table
                crawl_row.product_infos = [
                    models.ProductInfo(
                        brand=each_product['brand'],
                        name=each_product['name'],
                        price=each_product['price'],
                        currency=each_product['currency'],
                    ) for each_product in body]
            db_session.add(crawl_row)
            db_session.commit()
            if CRAWLER_ROW_COUNT:
                if each_line.index.values[0] > CRAWLER_ROW_COUNT:
                    break

    def main(self):
        """ Pass crawl file and store data in database 

        Set `CRAWLED_DATA_INFORMATION` in settings file which contain
        website name and path of crawler file.
        """
        # Iterate crawler file path
        for crawer_info in CRAWLED_DATA_INFORMATION:
            # Store website name and crawler file path
            website = models.Website(
                name = crawer_info['website_name'],
                document_path = crawer_info['crawl_data'])
            # Commit website information
            db_session.add(website)
            db_session.commit()
            # Parse crawler file to parser_crawler_document function
            self.parse_crawler_document(
                website.document_path,
                website.id,
                website.name)

CrawlerParser()