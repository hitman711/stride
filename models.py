""" """
import enum

import settings

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Enum, Float)
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

class PageTypeEnum(enum.Enum):
    """ Page Type Enum information """
    product_listing = "product_listing"
    product_detail = "product_detail"

class Website(Base):
    """ Store website information """
    __tablename__ = 'websites'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    document_path = Column(String)

class CrawlPage(Base):
    """ Store crawl page information """
    __tablename__ = 'crawlpages'
    
    id = Column(Integer, primary_key=True)
    page_url = Column(String)
    website_id = Column(Integer, ForeignKey('websites.id'), index=True)
    page_type = Column(Enum(PageTypeEnum))
    crawled_at = Column(DateTime)
    category = Column(String, index=True)
    website = relationship("Website", back_populates = "crawl_pages")

Website.crawl_pages = relationship(
    "CrawlPage", order_by = CrawlPage.id, back_populates = "website")

class ListPageInfo(Base):
    """ Store product list page information"""
    __tablename__ = 'listpageinfo'

    id = Column(Integer, primary_key=True)
    crawl_page_id = Column(Integer, ForeignKey('crawlpages.id'), index=True)
    sub_category = Column(String)
    page_number = Column(Float)
    ordering = Column(String)
    crawl_page = relationship(
        "CrawlPage", backref=backref("list_page_info", uselist=False))

ListPageInfo.crawl_pages = relationship(
    "CrawlPage", order_by = CrawlPage.id, 
    backref=backref("crawl_page", uselist=False) )

class ProductInfo(Base):
    """ Store product detail information """
    __tablename__ = 'productinfo'
    
    id = Column(Integer, primary_key=True)
    crawl_page_id = Column(Integer, ForeignKey('crawlpages.id'), index=True) 
    brand = Column(String, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    currency = Column(String)
    crawl_page = relationship("CrawlPage", back_populates = "product_infos")

CrawlPage.product_infos = relationship(
    "ProductInfo", order_by = ProductInfo.id, back_populates = "crawl_page")

Base.metadata.create_all(settings.db_engine)