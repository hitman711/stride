###Stride###

Application to parsed crawled data from crawler document and store detail in the database. The application provides an endpoint to retrieve data from 
a database based on user requirement.

#Requirements

Python: 3.5+
SQLAlchemy: 1.3+

#Installation

1.Create local virtual environment in project folder.  
	
	`python3 -m venv .env`

2.Activate local virtual environment.

	`source .env/bin/activate`

3.Install dependencies.
	
	`pip install -r requirements.txt`

4.Configure the crawler file path in the project settings file.

	`
	CRAWLED_DATA_INFORMATION = [
    		{
        		'website_name': 'ziengs.nl',
                
        		'crawl_data': <file_path_or_url>
    		},
            
    		{
        		'website_name': 'omoda.nl',
                
        		'crawl_data': <file_path_or_url>
    		},
    		{
      	 		 'website_name': 'zalando.nl',
                 
        		'crawl_data': <file_path_or_url>
    		}]
	`

5.Run crawler script to extract data from a file.

	` python parsers.py`

NOTE: - Some crawler files are huge. To limit crawler file record use `CRAWLER_ROW_COUNT` setting in the settings.py file. Assign no. of record which you want to crawl from each file.

6. Run project on the local network

	` python app.py`

#API Description

There is two API endpoint to retrieve data from the database.
    
    `1. http://127.0.0.1:8000					    -		product_list`
    
    `2. http://127.0.0.1:8000/<int:product_id>	    -		product_detail`

1.product_list

    Retrieve list of product list. API support multiple query parameters to
    search specific products i.e (brand, category, name, site, id).
    Return response provide you count, next, previous, result.


    Response Example:-
        {
            "count": 244, 
            "next": "http://127.0.0.1:8000/limit=1&page=2", 
            "previous": "", 
            "results": [
                {
                    "brand": "Rohde", 
                    "category": "Sandalen & slippers", 
                    "currency": "EUR", 
                    "id": 1, 
                    "name": "Rohde Pantoffel Zwart", 
                    "price": 44.95, 
                    "url": "http://www.ziengs.nl/rohde-pantoffel_zwart_10443.html", 
                    "website": "ziengs.nl"
                }
            ]
        }

2.product_detail

    Retrive product detail information. API takes product_id as a query parameter.
    In case of invalid id API return error status code 400 with msg not found.

    Response Example:-
        
        `
        {
            "brand": "Rohde", 
            "category": "Sandalen & slippers", 
            "currency": "EUR", 
            "id": 1, 
            "name": "Rohde Pantoffel Zwart", 
            "price": 44.95, 
            "url": "http://www.ziengs.nl/rohde-pantoffel_zwart_10443.html", 
            "website": "ziengs.nl"
        }
    
        {
            "detail": "Not found"
        }
        `


