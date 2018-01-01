#!/usr/bin/env python

import sys
import json
from dateutil.parser import *

def get_year(date_str):
	try:
		yr = parse(date_str).year
		return yr
	except ValueError:
		return None

def by_uid(obj):
	people = {}
	fields_to_keep = ['_UID', 'NAME']

	for person in obj:
		info = {
			'_UID': None,
			'NAME': None,
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
						info['BLAT'] = float(data)
					if tag == 'LONG':
						info['BLON'] = float(data)
					if tag == 'DATE':
						info['B_YR'] = get_year(data)
			if tag == 'DEAT':
				for death_field in person_field['tree']:
					tag = death_field['tag']
					data = death_field['data']
					if tag == 'LATI':
						info['DLAT'] = float(data)
					if tag == 'LONG':
						info['DLON'] = float(data)
					if tag == 'DATE':
						info['D_YR'] = get_year(data)

		people[info['_UID']] = info

	return people

def main():
	# Verify that 1 parameter was entered in command line
	if len(sys.argv) != 3:
		print 'Usage: python by_year_constructor.py input_file output_file'
	
	else:
		with open(sys.argv[1]) as contactFile:
		    data = json.load(contactFile)

		uids = by_uid(data)

		file = open(sys.argv[2], "w")

		print >> file, json.dumps(uids)
		

# If scraper.py was run directly by python
if __name__ == '__main__':
	main()