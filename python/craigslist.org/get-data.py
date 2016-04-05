import requests
import xmltodict
import pandas as pd
import md5
import MySQLdb
import ConfigParser
import re
from uuid import UUID

propertiesFile = "my.properties"
cp = ConfigParser.ConfigParser()
cp.readfp(open(propertiesFile))

dbhost = cp.get('DB', 'host')
dbuser = cp.get('DB', 'user')
dbpassword = cp.get('DB', 'password')
dbname = cp.get('DB', 'db')

url = 'https://losangeles.craigslist.org/search/reb?format=rss&is_paid=all&max_price=625000&min_price=400000&search_distance_type=mi&srchType=T'
r = requests.get(url)

xml = xmltodict.parse(r.text)

items = xml['rdf:RDF']['item']
cols = None
rows = []
for item in items:
    row = {}
    if cols == None:
        cols = item.keys()
        if 'enc:enclosure' in cols:
            cols.remove('enc:enclosure')
    for col in cols:
        row[col] = item[col]
    if 'enc:enclosure' in item:
        row['img'] = item['enc:enclosure']['@resource']
    rows.append(row)

df = pd.DataFrame(rows)
df['dc:date'] = df['dc:date'].apply(pd.to_datetime)
otherRightsCount = df['dc:rights'].apply(lambda x: x !='&copy; 2016 <span class="desktop">craigslist</span><span class="mobile">CL</span>')
if otherRightsCount.sum():
    print 'Got a new result never seen before, investigate here', otherRightsCount
df.drop('dc:rights', axis=1, inplace=True)
df.drop('@rdf:about', axis=1, inplace=True)
df.drop('dc:type', axis=1, inplace=True)
df.drop('dcterms:issued', axis=1, inplace=True)
df.drop('title', axis=1, inplace=True)
ncols = []
for col in df.columns:
    if col.find('dc:') == 0:
        col = col[3:]
    ncols.append(col)

df.columns = ncols
df.fillna('', inplace=True)
