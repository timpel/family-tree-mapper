#!/usr/bin/env python

import sys
import json
from dateutil.parser import *
import csv

def get_year(date_str):
	try:
		yr = parse(date_str)
		return str(yr)
	except ValueError:
		return None

def add_years(d, years):
    try:      
        return str(d.replace(year = d.year + years))
    except ValueError:      
        return str(d + (date(d.year + years, 1, 1) - date(d.year, 1, 1)))

def by_uid(obj):
	people = []
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
						info['BLAT'] = data
					if tag == 'LONG':
						info['BLON'] = data
					if tag == 'DATE':
						info['B_YR'] = get_year(data)
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

		if info['DLAT'] == None:
			info['DLAT'] = info['BLAT']
		if info['DLON'] == None:
			info['DLON'] = info['BLON']
		if info['D_YR'] == None:
			info['D_YR'] = add_years(parse(info['B_YR']), 80)

		people.append(info)

	return people

def main():
	# Verify that 1 parameter was entered in command line
	if len(sys.argv) != 3:
		print 'Usage: python by_year_constructor.py input_file output_file'
	
	else:
		with open(sys.argv[1]) as contactFile:
		    data = json.load(contactFile)

		uids = by_uid(data)
		print "UID dict done"

		with open(sys.argv[2], 'w') as csvfile:
		    fieldnames = ['_UID', 'NAME', 'BLAT', 'BLON', 'DLAT', 'DLON', 'B_YR', 'D_YR']
		    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

		    writer.writeheader()

		    for row in uids:
		    	writer.writerow({k:v.encode('utf8') for k,v in row.items()})

# If scraper.py was run directly by python
if __name__ == '__main__':
	main()