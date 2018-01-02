#!/usr/bin/env python

import sys
import json
from dateutil.parser import *
import datetime
import csv

def write_file(uids, file_name, file_format):
	if file_format == 'json':
		file = open(sys.argv[2], "w")
		print >> file, json.dumps(uids)
	elif file_format == 'csv':
		with open(sys.argv[2], 'w') as csvfile:
		    fieldnames = ['_UID', 'NAME', 'BPLC', 'DPLC', 'BLAT', 'BLON', 'DLAT', 'DLON', 'B_YR', 'D_YR']
		    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

		    writer.writeheader()

		    for row in uids:
		    	writer.writerow({k:v.encode('utf8') for k,v in row.items()})
	elif file_format == 'timeline':
		file = open(sys.argv[2], "w")
		print >> file, json.dumps(to_timeline(uids))
	else:
		print 'file format not recognized'

def to_timeline(obj):
	tl = {}

	tl['type'] = "FeatureCollection"
	tl['features'] = sorted([to_geojson(person) for person in obj], key=lambda k: k['properties']['time'])

	return tl

def to_geojson(d):
	gj = {}

	gj['type'] = "Feature"
	gj['geometry'] = {
		"type": "Point",
		"coordinates": [float(d['BLON']), float(d['BLAT'])]
	}
	gj['properties'] = {
		"time": d['B_YR'],
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

def by_uid(obj):
	people = []
	fields_to_keep = ['_UID', 'NAME']

	for person in obj:
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
		for person_field in person['tree']:
			tag = person_field['tag']
			data = person_field['data']
			if tag in fields_to_keep:
				info[tag] = data
			if tag == 'BIRT':
				for birth_field in person_field['tree']:
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
				for death_field in person_field['tree']:
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

def main():
	# Verify correct number of parameters entered in command line
	if len(sys.argv) != 4:
		print 'Usage: python by_year_constructor.py input_file output_file output_format'
	
	else:
		with open(sys.argv[1]) as contactFile:
		    data = json.load(contactFile)

		uids = by_uid(data)

		write_file(uids, sys.argv[2], sys.argv[3])

# If scraper.py was run directly by python
if __name__ == '__main__':
	main()