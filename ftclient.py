#!/usr/bin/env python

from __future__ import print_function
import sys
import json
import ftmapper

def main():
	# Verify correct number of parameters entered in command line
	if len(sys.argv) != 4:
		print('Usage: ftclient.py input_file output_file output_format')
	
	else:
		with open(sys.argv[1]) as contactFile:
		    data = json.load(contactFile)

		mapper = ftmapper.FTMapData(data)
		mapper.add_all_latlons()
		mapper.write_data(sys.argv[2], sys.argv[3])

# If scraper.py was run directly by python
if __name__ == '__main__':
	main()