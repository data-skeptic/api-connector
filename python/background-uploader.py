import requests
from geopy.geocoders import GoogleV3
import ConfigParser
import os
import sys
import json
import datetime
import time
import pandas as pd
from itertools import izip
from geopy.geocoders import GoogleV3

################################
# ARG PARSING AND ERROR CHECKING

argv = sys.argv
if len(argv) == 1:
	print "USAGE: python background-uploader.py [Required TSV source file] [Optional name of properties file] [Optional name of output summary file]"
	sys.exit(-1)

if len(argv) >= 2:
	src = argv[1]

if len(argv) >= 3:
	propertiesFile = argv[2]
else:
	propertiesFile = "openhouse.config"

if len(argv) >= 4:
	outputFile = argv[3]
else:
	outputFile = "output.txt"

if not(os.path.isfile(src)):
	print "ERROR: Could not find source file file at " + src
	sys.exit(-1)

if not(os.path.isfile(propertiesFile)):
	print "ERROR: Could not find openhouse.config file"
	print "  > Please create a properties file and place it in the local directory."
	print "  > Instructions for doing this can be found at:"
	print "  > " + base_site_url + "/faq.htm#config-file"
	sys.exit(-1)

############################
# AQUIRING TOKEN

cp = ConfigParser.ConfigParser()
cp.readfp(open(propertiesFile))

user	 = cp.get('API', 'user')
passwd   = cp.get('API', 'password')
baseurl  = cp.get('API', 'baseurl')
waittime = float(cp.get('API', 'waittime'))
try:
	geocode_status = cp.get('API', 'geocode')
except ConfigParser.NoOptionError:
	geocode_status = 'failsafe'

r = requests.post(baseurl + '/token/auth/', data={"username":user, "password":passwd})
j = r.json()
if r.status_code != 200:
	if 'non_field_errors' in j.keys():
		errors = j['non_field_errors']
		for error in errors:
			print "ERROR: " + error
			sys.exit(-1)
	else:
		print "ERROR: " + unspecified
		print j
		sys.exit(-1)

if not('token' in j.keys()):
	print 'ERROR: Got 200 response but it does not contain a token'
	sys.exit(-1)

token = j['token']


############################
# CSV LOADING AND VALIDATION

f = open(src, 'r')
line = f.readline()
f.close()
arrc = line.split(',')
arrt = line.split('\t')
if len(arrc) > len(arrt):
	sep = ','
	arr = arrc
else:
	sep = '\t'
	arr = arrt

f = open('../canonical_header.tsv')
line = f.readline().strip()
f.close()
required = line.split('\t')
df = pd.read_csv(src, sep=sep)
present = df.keys().tolist()
d = dict(izip(present, range(len(present))))

for col in required:
	try:
		check = d[col]
	except KeyError:
		print("ERROR: Did not find required header field " + col)
		sys.exit(-1)


############################
# UPLOAD

if geocode_status != 'none':
	encoder = GoogleV3()

# After this many retries in failsafe mode, give up on geocoding client side
failsafe_retries = 5

# For every single entry, do this many retries before moving on
line_retries = 2

# If you have too many failures in a row without any success, stop.  Reset to this count on one success.
ceiling_overall_retries = 10

overall_retries = ceiling_overall_retries
fail_count = 0
giveup_count = 0
success_count = 0

f = open(outputFile, 'a')
f.write("------[" + str(datetime.datetime.now()) + "]--------------------")
trows = df.shape[0]
for i, row in df.iterrows():
	print i
	if i%1000 < 1:
		print("Rows complete: {}%".format(int((1.0 * i/trows*100))))
	d1 = row['sale_timestamp']
	d2 = str(pd.to_datetime(d1))
	data = {"listing_timestamp": d2,
		"listing_type": row['listing_type'],
		"bathrooms": row['bathrooms'],
		"bedrooms": row['bedrooms'],
		"price": row['price'],
		"building_size": row['sqft'],
		"size_units": 'I',
		"raw_address": row['raw_address']
	   }
	if geocode_status != 'none' and failsafe_retries >= 0:
		try:
			location = encoder.geocode(data['raw_address'])
			data['geocoded_address'] = location.address
			data['lat'] = location.latitude
			data['lon'] = location.longitude
			data['rawjson'] = location.raw
		except:
			failsafe_retries -= 1
			if geocode_status == 'failsafe' and failsafe_retries < 0:
				geocode_status = 'none'
			if geocode_status == 'failsecure':
				print("ERROR: Problems with geocoding")
				sys.exit(-1)
	retries = line_retries
	failure = True
	while retries >= 0 and overall_retries >= 0 and failure:
		failure = False
		try:
			headers = {"Authorization": "Bearer " + token}
			time.sleep(waittime)
			p = requests.post(baseurl + '/api/property/', data=data, headers=headers)
			if p.status_code == 201:
				success_count += 1
			else:
				failure = True
				fail_count += 1
				f.write(p.content)
			overall_retries = ceiling_overall_retries
		except UnboundLocalError:
			failure = True
		if failure:
			retries -= 1
			overall_retries -= 1
			msg = "ERROR [line " + str(i) + "]"
			if retries >= 0 and overall_retries >= 0:
				msg += " (going to retry)\n"
			msg += json.dumps(data).replace('\n', '')
			f.write(msg)
	if failure:
		giveup_count += 1
	if overall_retries < 0:
		msg = "Quitting due to too many failures\n"
		f.write(msg)
		print(msg)

print("Successfully uploaded: " + str(success_count))
print("Failures experienced: " + str(fail_count))
print("Unrecovered failures: " + str(giveup_count))
f.close()
