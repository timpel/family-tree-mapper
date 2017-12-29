#!/usr/bin/env python

import json
import sys
from dateutil.parser import *
import loc_to_latlon

unwanted_keys = ["HEAD", "SEX", "CHAN", "SOUR", "NOTE", "CENS", "EVEN", "RESI", "OCCU"]

def add_latlons(obj):
	locations = {}

	for person in obj:
		for person_field in person['tree']:
			if person_field['tag'] == '_UID':
				uid = person_field['data']
			if person_field['tag'] == 'NAME':
				print person_field['data']
			if person_field['tag'] == 'BIRT' or person_field['tag'] == 'DEAT':
				for field in person_field['tree']:
					if field['tag'] == 'PLAC':
						plac_string = field['data'].replace('Prob ', '')
						if plac_string in locations:
							response = locations[plac_string]
						else:
							response = loc_to_latlon.to_latlon(plac_string)
							locations[plac_string] = response
						try:
							resp_entry = {
								'data': json.dumps(response), 'tag': 'RESP', 'pointer': '', 'tree': []
								}
							lat_entry = {
								'data': str(response['results'][0]['geometry']['location']['lat']), 'tag': 'LATI', 'pointer': '', 'tree': []
								}
							lon_entry = {
								'data': str(response['results'][0]['geometry']['location']['lng']), 'tag': 'LONG', 'pointer': '', 'tree': []
								}
						except IndexError:
							print "IndexError at _UID %s" % uid
						person_field['tree'].append(resp_entry)
						person_field['tree'].append(lat_entry)
						person_field['tree'].append(lon_entry)

	return obj

def is_date(string):
    try: 
        parse(string)
        return True
    except ValueError:
        return False

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

def filter_list_of_dict(obj):
	indi_only = [d for d in obj if d['tag'] == 'INDI' and has_birth_death_info(d)]
	listlen = len(indi_only)
	count = 0;

	for item in indi_only:
		item['tree'] = [d for d in item['tree'] if d['tag'] not in unwanted_keys]
		if count % 1000 == 0:
			print "Done %d out of %d" % (count, listlen) 
		count += 1

	return indi_only

def main():
	# Verify that 1 parameter was entered in command line
	if len(sys.argv) != 3:
		print 'Usage: python mappable_tree_creator.py input_file output_file'
	
	else:
		with open(sys.argv[1]) as contactFile:
		    data = json.load(contactFile)

		filtered = filter_list_of_dict(data)
		filtered = add_latlons(filtered)

		file = open(sys.argv[2], "w")

		print >> file, json.dumps(filtered)

# If scraper.py was run directly by python
if __name__ == '__main__':
	main()