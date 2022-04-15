#!/usr/bin/python
# coding: utf-8

# -----------------------------------------------------------
# Katabase project: github.com/katabase/
# Python script to extract the <desc> of XML files and save it in a JSON file
#
# * PROCESS BREAKDOWN *
# - data_extractor() extracts the elements from an XML file's normalised tei:desc elements obtained
#   after step 2_CleanedData ;
# - if __name__ == "__main__" initiates the CLI, iterate over each file
#   we need to get data from ; on each iteration, it calls data_extractor()
#   to do the dirty work and updates an output_dict with the results from data_extractor ;
#   finally, it saves the output dict as a JSON file in the 'output' directory
# -----------------------------------------------------------

import os
import json
import glob
from pathlib import Path
from lxml import etree
import re

ns = {'tei': 'http://www.tei-c.org/ns/1.0'}


# ------ MAIN FUNCTION ------ #
def data_extractor(tree, output_dict):
	"""
	This function extracts all the data from each desc and adds it to a dictionnary (desc) ;
	in the end, it appends desc to the dictionnary.
	:param tree: an XML tree
	:param output_dict: the dictionnary on which every XML file's desc is stored
	"""

	# For each desc, a dict retrieve all the data.
	for desc in tree.xpath('.//tei:text//tei:item//tei:desc', namespaces=ns):
		data = {}
		desc_id = desc.xpath('./@xml:id', namespaces=ns)[0]  # récupérer l'ID
		if desc.xpath('parent::tei:item/tei:measure[@quantity]', namespaces=ns):  # si il y a un prix, le récupérer
			data["price"] = to_float(desc.xpath('parent::tei:item//tei:measure[@commodity="currency"]/@quantity', namespaces=ns)[0])
		else:
			data["price"] = None
		if desc.xpath('parent::tei:item/tei:name[@type="author"]/text()', namespaces=ns):  # si il y a un.e auteur.ice, le récupérer (ne garder que le nom de famille)
			author = desc.xpath('parent::tei:item/tei:name[@type="author"]/text()', namespaces=ns)[0]
			try:
            	# We only keep the surname of the author : we stop the match at the first parenthesis or dot and we keep the first match.
				author = re.match('^([^\(|.|,|;|-]+)', author)[1]
				# We remove blankspaces.
				author = author.strip()
			except:
				author = None
			data["author"] = author
		else:
			data["author"] = None
		if desc.xpath('./tei:date[@when]', namespaces=ns):  # récupérer la date si elle existe
			data["date"] = desc.xpath('./tei:date/@when', namespaces=ns)[0]
		else:
			data["date"] = None
		if desc.xpath('./tei:measure[@type="length"]', namespaces=ns):
			data["number_of_pages"] = to_float(desc.xpath('./tei:measure[@type="length"]/@n', namespaces=ns)[0])
		else:
			data["number_of_pages"] = None
		if desc.xpath('./tei:measure[@type="format"]', namespaces=ns):  # récupérer le format XML normalisé si il existe
			desc_format = desc.xpath('./tei:measure[@type="format"]/@ana', namespaces=ns)[0]
			data["format"] = get_numbers(str(desc_format))
		else:
			data["format"] = None
		if desc.xpath('./tei:term', namespaces=ns):  # récupérer les termes normalisés
			desc_term = desc.xpath('./tei:term/@ana', namespaces=ns)[0]
			data["term"] = get_numbers(str(desc_term))
		else:
			data["term"] = None
		if desc.xpath('ancestor::tei:TEI/tei:teiHeader//tei:sourceDesc//tei:date[@when]', namespaces=ns):  # récupérer la date de vente
			data["sell_date"] = desc.xpath('ancestor::tei:TEI/tei:teiHeader//tei:sourceDesc//tei:date/@when', namespaces=ns)[0]
		elif desc.xpath('ancestor::tei:TEI/tei:teiHeader//tei:sourceDesc//tei:date[@to]', namespaces=ns):
    			data["sell_date"] = desc.xpath('ancestor::tei:TEI/tei:teiHeader//tei:sourceDesc//tei:date/@to', namespaces=ns)[0]
		else:
			print("No sell date for" + desc_id)
		# In order to check the data, we add its text (and only its text with .strip_tags) in the dict.
		etree.strip_tags(desc, '{http://www.tei-c.org/ns/1.0}*')
		data["desc"] = desc.text

		output_dict[desc_id] = data


# ----- AUXILIARY FUNCTIONS ----- #
def to_float(str):
	"""
	This function tries to convert a string into a float.
	:param str: a string
	:return: a float or None
	"""
	try:
		return float(str)
	except:
		return None


# extraire les nombres d'une chaîne de caractère pour faire des comparaisons pendant le clustering
def get_numbers(string):
	"""
	This function gets the numbers of a string with a regex.
	in our case, we do this in order to compare int and not str during the clustering.
	:param str: a string
	:return: int
	"""
	try:
		numbers = re.search('[0-9]+', string)
		return int(numbers[0])
	except:
		return None


# ----- COMMAND LINE INTERFACE ----- #
if __name__ == "__main__":

	# This way, we get every single file contained in any subfolder of Catalogues/.
	files = glob.glob("../Catalogues/**/*.xml", recursive=True)

	output_dict = {}

	for file in files:
		# Each file is parsed.
		tree = etree.parse(file)

		data_extractor(tree, output_dict)

	# check if output directory exists ; if not, create it
	cwd = os.path.dirname(os.path.abspath(__file__))  # current directory : script
	root = Path(cwd).parent
	output_dir = os.path.join(root, "output")
	if not os.path.isdir(output_dir):
		os.makedirs(output_dir)

	# write the output to the output file
	with open('../output/export.json', 'w') as outfile:
		# Older data are deleted. 
		outfile.truncate(0)
		json.dump(output_dict, outfile)
