#!/usr/bin/env python

import sys
import googlemaps
from config import GP_API_KEY

gmaps = googlemaps.Client(key=GP_API_KEY)


def to_latlon(loc):
	result = gmaps.places(loc)
	return result


def main():
	# Verify that 1 parameter was entered in command line
	if len(sys.argv) != 2:
		print 'Usage: python loc_to_latlon.py string'
	
	else:
		to_latlon(sys.argv[1])
		

# If scraper.py was run directly by python
if __name__ == '__main__':
	main()