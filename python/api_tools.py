import requests
try:
    from geopy.geocoders import GoogleV3
except:
    pass
from datetime import datetime

class push_data(object):
    """

    username: username to get token
    password: password to get token
    baseurl: server url Dev 'http://home-sales-data-api-dev.herokuapp.com' Production 'http://home-sales-data-api.herokuapp.com'
    geocode: 'address': Default, only get the standurdized address, False: do nothing, True: Save geocode data
    Push data
    Example usage:
    >>> pusher = push_data(username='JohnDoe', password='SuperSecure', baseurl='http://127.0.0.1:8000', geocode='address')
    >>> data = {"listing_timestamp": str(datetime.now()),
    ...         "listing_type": 'F', # for sale
    ...         "price": 123456,
    ...         "size_units": 'I',
    ...         "raw_address": "1701 Wynkoop St, Denver, CO 80202"}
    >>> p = pusher.post_data(data=data)
    >>> p.get_token()
    >>> p
    {'bathrooms': None,
    'bedrooms': None,
    'building_size': None,
    'car_spaces': None,
    'features': [],
    'geocoded_address': '',
    'id': 25,
    'land_size': None,
    'listing_timestamp': '2016-04-26T22:39:20.281437Z',
    'listing_type': 'F',
    'price': 123456.0,
    'raw_address': '1701 Wynkoop St, Denver, CO 80202',
    'size_units': 'I',
    'submitter': None,
    'upload_timestamp': '2016-04-27T04:39:20.317330Z',
    'valid': False}

    """
    def __init__(self, username, password, baseurl, geocode='address'):
        self.username = username
        self.password = password
        self.baseurl = baseurl
        self.geocode = geocode
        self.token = None

    def get_token(self):
        'Get a new token'
        data = {"username":self.username,
                "password":self.password}
        r = requests.post(self.baseurl + '/token/auth/', data = data)
        self.token = r.json()['token']

    def post_data(self, data):
        'Pushes data'
        if self.token == None: #TODO is push fails becuase of expired token, get new token and try again.
            self.token = self.get_token()
        headers = {"Authorization": "Bearer " + self.token}
        if self.geocode:
            encoder = GoogleV3()
            location = encoder.geocode(data['raw_address']) #Todo, need to be sure we got a valid response
            data['geocoded_address'] = location.address
            if self.geocode == True
                data['city'] = location.address
                data['state'] = location.address
                data['zipcode'] = location.address
                data['zip4'] = location.address
                data['lat'] = location.latitude
                data['lon'] = location.longitude
                data['rawjson'] = location.raw
        try:
            p = requests.post(self.baseurl + '/api/property/', data = data, headers=headers)
            assert p.status_code == 201
            return p.json()
        except:
            print(p.json())
            raise
