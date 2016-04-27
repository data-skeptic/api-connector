import requests
from datetime import datetime

class push_data(object):
    """
    Push data
    Example usage:
    >>> pusher = push_data(username='JohnDoe', password='SuperSecure', baseurl='http://127.0.0.1:8000')
    >>> data = {"listing_timestamp": str(datetime.now()),
    ...         "listing_type": 'F', # for sale
    ...         "price": 123456,
    ...         "size_units": 'I',
    ...         "raw_address": "1701 Wynkoop St, Denver, CO 80202"}
    >>> p = pusher.post_data(data=data)
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
    def __init__(self, username, password, baseurl='https://home-sales-data-api.herokuapp.com'):
        self.baseurl = baseurl
        self.username = username
        self.password = password
        self.token = None

    def get_token(self):
        'Get a new token'
        data = {"username":self.username,
                "password":self.password}
        r = requests.post(self.baseurl + '/token/auth/', data = data)
        return r.json()['token']

    def post_data(self, data):
        'Pushes data'
        if self.token == None:
            self.token = self.get_token()
        #TODO is push fails becuase of expired token, get ne token and try again.
        headers = {"Authorization": "Bearer " + self.token}
        p = requests.post(self.baseurl + '/api/property/', data = data, headers=headers)
        try:
            assert p.status_code == 201
            return p.json()
        except:
            print(p.json())
            raise
