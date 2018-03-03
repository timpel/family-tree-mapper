#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from builtins import str
from builtins import object
import json
import sys
from dateutil.parser import *
import datetime
import csv
import googlemaps
from config import GP_API_KEY

class FTMapData(object):
	def __init__(self, data):
		self.unwanted_keys = ["HEAD", "SEX", "CHAN", "SOUR", "NOTE", "CENS", "EVEN", "RESI", "OCCU"]
		self.data = self.get_individuals(data)
		self.gmaps = googlemaps.Client(key=GP_API_KEY)
		self.locations = {}

	def get_individuals(self, obj):
		indi_only = [d for d in obj if d['tag'] == 'INDI' and has_birth_death_info(d)]
		listlen = len(indi_only)
		count = 0;

		for item in indi_only:
			item['tree'] = [d for d in item['tree'] if d['tag'] not in self.unwanted_keys]
			if count % 1000 == 0:
				print("Filtering JSON: %d out of %d" % (count, listlen)) 
			count += 1

		return indi_only

	def add_all_latlons(self):
		response_promises = []
		listlen = len(self.data)
		for person in self.data:
			for info_field in person['tree']:
				if info_field['tag'] == '_UID':
					uid = info_field['data']
				if info_field['tag'] == 'BIRT' or info_field['tag'] == 'DEAT':
					for field in info_field['tree']:
						if field['tag'] == 'PLAC':
							plac_string = field['data'].replace('Prob ', '')
							self.add_one_latlon(plac_string, info_field)

	def add_one_latlon(self, loc, info_field):
		if loc in self.locations:
			response = self.locations[loc]
		else:
			print('\rQuerying ', loc)
			response = self.gmaps.places(loc)
			self.locations[loc] = response
		self.append_latlon_info(response, info_field)

	def append_latlon_info(self, response, field):
		try:
			lat_entry = {
				'data': str(response['results'][0]['geometry']['location']['lat']), 'tag': 'LATI', 'pointer': '', 'tree': []
				}
			lon_entry = {
				'data': str(response['results'][0]['geometry']['location']['lng']), 'tag': 'LONG', 'pointer': '', 'tree': []
				}
		except:
			return
		field['tree'].append(lat_entry)
		field['tree'].append(lon_entry)

	def write_data(self, file_name, file_format):
		uids = self.generate_person_array()
		if file_format == 'json':
			file = open(sys.argv[2], "w")
			print(json.dumps(uids), file=file)
		elif file_format == 'csv':
			with open(sys.argv[2], 'w') as csvfile:
			    fieldnames = ['_UID', 'NAME', 'BPLC', 'DPLC', 'BLAT', 'BLON', 'DLAT', 'DLON', 'B_YR', 'D_YR']
			    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
			    writer.writeheader()
			    for row in uids:
			    	writer.writerow({k:v.encode('utf8') for k,v in list(row.items())})
		elif file_format == 'geojson':
			file = open(sys.argv[2], "w")
			print(json.dumps(to_feature_collection(uids)), file=file)
		else:
			print('file format not recognized')

	def generate_person_array(self):
		people = []

		for person in self.data:
			info = {
				'_UID': "",
				'NAME': "",
				'BPLC': "",
				'DPLC': "",
				'BLAT': None,
				'BLON': None,
				'DLAT': None,
				'DLON': None,
				'B_YR': None,
				'D_YR': None
			}
			for info_field in person['tree']:
				tag = info_field['tag']
				data = info_field['data']
				if tag == "_UID":
					info[tag] = data
				if tag == "NAME":
					info[tag] = data.replace('/', '')
				if tag == 'BIRT':
					for birth_field in info_field['tree']:
						tag = birth_field['tag']
						data = birth_field['data']
						if tag == 'LATI':
							info['BLAT'] = data
						if tag == 'LONG':
							info['BLON'] = data
						if tag == 'DATE':
							info['B_YR'] = get_year(data)
						if tag == 'PLAC':
							info['BPLC'] = data
				if tag == 'DEAT':
					for death_field in info_field['tree']:
						tag = death_field['tag']
						data = death_field['data']
						if tag == 'LATI':
							info['DLAT'] = data
						if tag == 'LONG':
							info['DLON'] = data
						if tag == 'DATE':
							info['D_YR'] = get_year(data)
						if tag == 'PLAC':
							info['DPLC'] = data

			if info['DLAT'] == None:
				info['DLAT'] = info['BLAT']
			if info['DLON'] == None:
				info['DLON'] = info['BLON']
			if info['D_YR'] == None:
				info['D_YR'] = add_years(parse(info['B_YR']), 80)

			people.append(info)

		return people

def has_birth_death_info(person):
	hasDOB = False
	hasDOD = False
	hasPOB = False
	hasPOD = False
	for attr in person['tree']:
		if attr['tag'] == 'BIRT':
			for birthField in attr['tree']:
				if birthField['tag'] == 'DATE':
					if is_date(birthField['data']):
						hasDOB = True
					else:
						birthField['data'] = birthField['data'].replace('BEF ', '').replace('AFT ', '').replace('Q', '1').replace('ABT ', '')
						if is_date(birthField['data']):
							hasDOB = True
				if birthField['tag'] == 'PLAC':
					hasPOB = True
		if attr['tag'] == 'DEAT':
			for deathField in attr['tree']:
				if deathField['tag'] == 'DATE':
					if is_date(deathField['data']):
						hasDOD = True
					else:
						deathField['data'] = deathField['data'].replace('BEF ', '').replace('AFT ', '').replace('Q', '1').replace('ABT ', '')
						if is_date(deathField['data']):
							hasDOD = True
				if deathField['tag'] == 'PLAC':
					hasPOD = True

	return hasDOB and hasPOB# and hasDOD

def is_date(string):
    try: 
        parse(string)
        return True
    except ValueError:
        return False

def to_feature_collection(obj):
		tl = {}
		tl['type'] = "FeatureCollection"
		tl['features'] = [to_geojson(person) for person in obj if person['BLON'] is not None ]
		return tl

def to_geojson(d):
	gj = {}
	gj['type'] = "Feature"
	gj['geometry'] = {
		"type": "Point",
		"coordinates": [float(d['BLON']), float(d['BLAT'])]
	}
	gj['properties'] = {
		"start": d['B_YR'],
		"end": d['D_YR'],
		"name": d['NAME'],
		"placeofbirth": d['BPLC'],
		"placeofdeath": d['DPLC'],
		"uid": d['_UID']
	}

	return gj

def smaller(d1, d2):
	return d1 if d1 < d2 else d2

def get_year(date_str):
	try:
		yr = parse(date_str)
		return str(yr)
	except ValueError:
		return None

def add_years(d, years):
    try:      
        return str(smaller(d.replace(year = d.year + years), datetime.datetime.now()))
    except ValueError:      
        return str(smaller(d + (date(d.year + years, 1, 1) - date(d.year, 1, 1)), datetime.datetime.now()))