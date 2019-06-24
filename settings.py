""" """
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DEBUG = True
# Database configuration
db_engine = create_engine('sqlite:///nelson_crawler.db', echo = True)

# Database session binging
Session = sessionmaker(bind = db_engine)
db_session = Session()

# Crawled data page
CRAWLED_DATA_INFORMATION = [
    {
        'website_name': 'ziengs.nl',
        'crawl_data': '/home/siddhesh/Documents/crawl_ziengs.nl_2016-05-30T23-15-20.jl'
    },
    {
        'website_name': 'omoda.nl',
        'crawl_data': '/home/siddhesh/Documents/crawl_omoda.nl_2016-05-30T23-14-58.jl'
    },
    {
        'website_name': 'zalando.nl',
        'crawl_data': '/home/siddhesh/Documents/crawl_zalando.nl_2016-05-30T23-14-36.jl'
    }
]

PARSER_MAPPING = { 
    'ziengs.nl': 'ziengs_parser',
    'omoda.nl': 'omoda_parser',
    'zalando.nl': 'zalando_parser'
}