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
import sys
import json
import glob
import traceback
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
	return output_dict


def catalog_extractor(tree, catalog_dict):
	"""

	:param tree:
	:param catalog_dict:
	:return:
	"""
	data = {}  # dictionnary to store all the data on a catalog
	# retrieve the title, sale date and number of entries in the catalog
	if tree.xpath(".//tei:titleStmt//tei:title", namespaces=ns):
		data["title"] = tree.xpath(".//tei:titleStmt//tei:title", namespaces=ns)[0].text
	if tree.xpath('.//tei:bibl/tei:date[@when]', namespaces=ns):  # récupérer la date si elle existe
		data["date"] = tree.xpath('.//tei:bibl/tei:date/@when', namespaces=ns)[0]
	elif tree.xpath(".//.//tei:bibl/tei:date/text()", namespaces=ns):
		data["date"] = tree.xpath('.//tei:bibl//tei:date/text()', namespaces=ns)[0]
	if tree.xpath(".//tei:body//tei:item", namespaces=ns):
		data["item count"] = int(tree.xpath("count(.//tei:body//tei:item)", namespaces=ns))

	# if the catalog is a fixed-price catalog (has "tei//item//tei:measure[@commodity='currency']",
	# extract data about the prices
	if tree.xpath(".//tei:body//tei:item[.//tei:measure/@commodity='currency']", namespaces=ns):
		# get the currency in which the catalog items are sold
		if tree.xpath(".//tei:body//tei:item//tei:measure[@commodity]/@unit", namespaces=ns):
			print(tree.xpath(".//tei:body//tei:item//tei:measure[@commodity]/@unit", namespaces=ns))
			data["currency"] = tree.xpath(".//tei:body//tei:item//tei:measure[@commodity]/@unit", namespaces=ns)[0]
		iplist = []  # list of all the tei:items in a catalog with their price
		plist = []  # list of the prices in one catalog
		for item in tree.xpath(".//tei:body//tei:item[.//tei:measure/@commodity='currency']", namespaces=ns):
			# if an item only has one price, extract it ; we try to get the price from the @quantity
			# of the tei:measure, then from the text content of the tei:measure ; the only prices that
			# are left must conform to the regular expression "[0-9]+(\.[0-9]+)?" ; else; price is None
			ipdict = {}  # dictionnary linking a tei:item's @xml:id to its price
			price = 0  # price of an item
			if item.xpath("./@xml:id", namespaces=ns):
				id = item.xpath("./@xml:id", namespaces=ns)[0]
			if len(item.xpath(".//tei:measure[@commodity='currency']", namespaces=ns)) == 1:
				if re.match(r"[0-9]+(\.[0-9]+)?",
							item.xpath(".//tei:measure[@commodity='currency']/@quantity", namespaces=ns)[0]):
					price = item.xpath(".//tei:measure[@commodity='currency']/@quantity", namespaces=ns)[0]
				elif re.match(r"[0-9]+(\.[0-9]+)?",
							  item.xpath(".//tei:measure[@commodity='currency']/text()", namespaces=ns)[0]):
					price = item.xpath(".//tei:measure[@commodity='currency']/text()", namespaces=ns)[0]
				price = to_number(price)

			# if there are several prices in an item, add them up
			else:
				for m in item.xpath(".//tei:measure[@commodity='currency']", namespaces=ns):
					if re.match(r"[0-9]+(\.[0-9]+)?", m.xpath("./@quantity", namespaces=ns)[0]):
						p = m.xpath("./@quantity", namespaces=ns)[0]
					elif re.match(r"[0-9]+(\.[0-9]+)?", m.xpath("./text()", namespaces=ns)[0]):
						p = m.xpath("./text()", namespaces=ns)[0]
					p = to_number(p)
				if price is not None:
					price += p

			# after all the above use cases, add an entry to ipdict
			if price is not None:
				ipdict[id] = price
			print(ipdict)

	if tree.xpath("./@xml:id", namespaces=ns):
		catalog_dict[tree.xpath("./@xml:id", namespaces=ns)[0]] = data



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


def to_number(str):
	"""
	function to convert a price string into an int or float in order to do calculations
	:param str: string to convert ; type string
	:return: string converted to float or int (if there's no problem) ; else, None
	"""
	try:
		str = int(str)
	except:
		try:
			str = float(str)
		except:
			str = None
	return str


# ----- COMMAND LINE INTERFACE ----- #
if __name__ == "__main__":

	# This way, we get every single file contained in any subfolder of Catalogues/.
	files = glob.glob("../Catalogues/**/*.xml", recursive=True)

	output_dict = {}
	catalog_dict = {}

	for file in files:
		# additional error handling: if there is an error here (the only step where there can
		# be an error, really), print the name of the file on which the error happened, the
		# full error message and exit)
		try:
			# Each file is parsed.
			tree = etree.parse(file)

			#data_extractor(tree, output_dict)
			catalog_extractor(tree, catalog_dict)
		except:
			error = traceback.format_exc()  # full error message
			print(f"ERROR ON FILE --- {file}")
			print(error)
			sys.exit(1)

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
