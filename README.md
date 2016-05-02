# api-connector
Repository to help teams get started calling the API.

If you would like to make suggestions for improvements or additions to this document, please send a pull request.

### Available Connectors
* Python [api_tools.py](/python/api_tools.py) Class for authenticating and pushing data.

## Before pushing any data to the Home Sales Data API, please make sure you...

* are compliant with the terms and services of whatever data source you are pulling from
* checked and updated [this link](https://github.com/data-skeptic/data-source-notes) to annotate the source of your data
* vetted the data for reasonable correctness
* do your best to push and update, rather than a duplicate record

## Best practices for scraping / pulling data

If you can find data available via APIs, this is the best case sitation.  Of course, it makes our work easier when an API
is available, but additionally, it means the publisher of the data has the intent that users consume it programatically.
When scraping data, it is not clear what the intent of the publisher is, so please follow the best practices listed below.

### Respect robots.txt
By convention, web sites are encouraged to place a `robots.txt` file at the root of their web server.  You can view the
almost empty version of the [Data Skeptic robots.txt file](http://dataskeptic.com/robots.txt) or, for a more complex
example, check out [Google's robots.txt](http://www.google.com/robots.txt).

Review the FAQ and details at [robotstxt.org](http://www.robotstxt.org/).

### Multi-threading and Crawl Frequency

As a best practice, we recommend crawling sites with only a single thread.  While this may be intrinsically slow for large
crawls, it enables the web server to throttle your traffic a bit and it also prevents you from accidentally doing a denial
of service attack.

For crawl frequency (time you should sleep between calls), we recommend setting a low but non-zero value such as 200ms.

