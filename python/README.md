# Uploading data via Python

This repo contains some helper functions for pushing data to the Home Sales Data API

## Common tools

For parsing web pages, [Beautiful Soup](https://pypi.python.org/pypi/beautifulsoup4) is a populare and powerful library.

For crawling, [Requests](http://docs.python-requests.org/en/master/user/quickstart/) is great for simple / single page requests.
For more advanced crawls [Scrapy](http://scrapy.org/) is a widely used library, and it can help you respect [robots.txt](http://doc.scrapy.org/en/latest/topics/downloader-middleware.html).

For something fancier, requiring more browser interactions, try [Selenium for Python](http://selenium-python.readthedocs.org/).
