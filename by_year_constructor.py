#!/usr/bin/env python

import sys
import json
from dateutil.parser import *


def by_year(obj):
	people_by_year = {}
	for person in obj:
		for person_field in person['tree']:
			if person_field

def main():
	# Verify that 1 parameter was entered in command line
	if len(sys.argv) != 2:
		print 'Usage: python by_year_constructor.py input_file'
	
	else:
		with open(sys.argv[1]) as contactFile:
		    data = json.load(contactFile)

		result = by_year(data)
		

# If scraper.py was run directly by python
if __name__ == '__main__':
	main()