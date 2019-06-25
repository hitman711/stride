""" """
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Flask project debug mode
DEBUG = True

# Database configuration
db_engine = create_engine('sqlite:///nelson_crawler.db', echo=True)

# Database session binging
Session = sessionmaker(bind=db_engine)
db_session = Session()

# Default pagination class
PAGE_LIMIT = 25

# Number of row crawl from each crawler file
# Set 0 for no condition
CRAWLER_ROW_COUNT = 0

# Crawler data configuration
CRAWLED_DATA_INFORMATION = [
    # {
    #     'website_name': 'ziengs.nl',
    #     'crawl_data': 'crawl/crawl_ziengs.nl_2016-05-30T23-15-20.jl'
    # },
    {
        'website_name': 'omoda.nl',
        'crawl_data': 'crawl/crawl_omoda.nl_2016-05-30T23-14-58.jl'
    }
    # ,
    # {
    #     'website_name': 'zalando.nl',
    #     'crawl_data': 'crawl/crawl_zalando.nl_2016-05-30T23-14-36.jl'
    # }
]

# Crawler product detail parser mapping
PARSER_MAPPING = {
    'ziengs.nl': 'ziengs_parser',
    'omoda.nl': 'omoda_parser',
    'zalando.nl': 'zalando_parser'
}

# Crawler product list parser mapping
LIST_PARSER_MAPPING = {
    'ziengs.nl': '',
    'omoda.nl': 'omoda_list_parser',
    'zalando.nl': ''
}
