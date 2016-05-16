# This is a very quick and dirty data extract from one web site and using api_tools/py for pushing data
# This is not an example of great code, but a first step in demonstrating how we start doing
# data pushes.

from api_tools import push_data
import requests
import bs4 as bsoup
import pandas as pd
import time
import datetime
from datetime import datetime
import json

def extract_listings(txt):
    plistings = []
    s = bsoup.BeautifulSoup(txt)
    listings = s.findAll('div', {'class': 'estate-info'})
    for listing in listings:
        price = listing.find('div', {'class': 'estateSummary-price mix-estateSummary_SM-price_sm'}).text
        title = listing.find('div', {'class': 'estateSummary-title mix-estateSummary_SM-title_sm'}).text
        address = listing.find('div', {'class': 'estateSummary-address'}).text
        elems = listing.findAll('div', {'class': 'estateSummary-list'})
        beds = 0
        baths = 0
        sqft = 0
        htype = ''
        lastUpdated = listing.find('em', {'class': 'highlight-text isHiddenSM'})
        if lastUpdated is None:
            lastUpdated = ''
        else:
            lastUpdated = lastUpdated.text.replace('Last updated ', '')
        for elem in elems:
            elems2 = elem.findAll('div')
            for elem2 in elems2:
                txt = elem2.text
                if txt.find('Beds') > 0:
                    beds = float(txt[0:txt.find('Beds')].strip())
                elif txt.find('Baths') > 0:
                    baths = float(txt[0:txt.find('Baths')].strip())
                elif txt.find('Sqft') > 0:
                    sqft = int(txt[0:txt.find('Sqft')].replace(',', '').strip())
                else:
                    htype = txt
        plisting = {'price': price, 'title': title, 'lastUpdated': lastUpdated, 'address': address, 'beds': beds, 'baths': baths, 'sqft': sqft, 'htype': htype}
        plistings.append(plisting)
    return plistings

pnum = 1
test = -1
plistings = []
while test == -1:
    r = requests.get('http://www.forsalebyowner.com/search/list/los-angeles-california/house,condo-types/' + str(pnum) + '-page/proximity,desc-sort')
    time.sleep(.5)
    test = r.text.find('Your search did not yield any results.')
    if test == -1:
        plistings.extend(extract_listings(r.text))
    pnum += 1

df = pd.DataFrame(plistings)

# Create an instance of the data pusher.
# Testing locally here, you need an account to push to:
# http://home-sales-data-api-dev.herokuapp.com    or    http://http://home-sales-data-api.herokuapp.com
pusher = push_data(username='JohnDoe', password='SuperSecure', baseurl='http://127.0.0.1:8000', geocode='address')
pusher.get_token()
print('API token: {}'.format(pusher.token))


for r in range(df.shape[0]):
    row = df.iloc[r]
    price = row.price.replace('$', '').replace(',', '')
    bedrooms = row.beds
    bathrooms = row.baths
    car_spaces = None
    building_size = row.sqft
    land_size = None
    size_units = 'M' # metric
    raw_address = row.address
    #
    request = {
        "listing_timestamp": str(datetime.now()),
        "listing_type": 'F', # for sale
        "price": price,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "car_spaces": car_spaces,
        "building_size": building_size,
        "land_size": land_size,
        "size_units": size_units,
        "raw_address": raw_address,
        "features": []
        }
    print(request)
    try:
        p = pusher.post_data(data=request)
        time.sleep(0.1)
    except:
        print('Failed: {}'.format(raw_address))
        time.sleep(0.1)
