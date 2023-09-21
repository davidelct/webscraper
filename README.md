# Web scraper (Davide's Version)

## Instructions

Basic usage:
```python
from scraper import scrape_page

url = "YOUR_URL_HERE"
web_scrape = scrape_page(url)
print(web_scrape)
```

You can also pass these arguments:
- path (str): path to save a screenshot of the page
- plot (bool): whether to display a plot of the elements on the 
- bbox (bool): whether to return information about bboxes
- return_str (bool): whether to return the scrape as a string or as a dict