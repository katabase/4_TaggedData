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
from statistics import mean, median, mode, pvariance
from lxml import etree
import re

from priceconv import pconverter_foreign, pconverter_franc


# the suffix "_c" in a dictionary or output json file expresses
# the price in constant francs (1900 rate)


ns = {'tei': 'http://www.tei-c.org/ns/1.0'}


# ============== MAIN FUNCTIONS ============== #
def item_extractor(tree, output_dict):
	"""
	This function extracts all the data from each item's desc and adds it to a dictionnary (desc) ;
	in the end, it appends desc to the dictionnary.
	prices are expressed:
	- in their original form (without inflation into account and in their original
	  currency): data["price"]
	- in constant francs (at 1900 rate): data["price_c"]
	:param tree: an XML tree
	:param output_dict: the dictionnary on which every XML file's desc is stored
	:return: updated dictionnary
	"""
	# get the sale date to convert prices
	if tree.xpath('./tei:teiHeader//tei:sourceDesc//tei:date[@when]',
				  namespaces=ns):
		sell_date = tree.xpath('.//tei:teiHeader//tei:sourceDesc//tei:date[@when]',
				               namespaces=ns)[0].text
	elif tree.xpath('tei:TEI/tei:teiHeader//tei:sourceDesc//tei:date[@to]', namespaces=ns):
		sell_date = tree.xpath('tei:TEI/tei:teiHeader//tei:sourceDesc//tei:date/@to',
							   namespaces=ns)[0].text
	else:
		print("No sell date for " + tree.xpath("@xml:id", namespaces=ns)[0])
		sell_date = None
	if sell_date is not None:
		sell_year = re.findall(r"\d{4}", sell_date)[0]
	else:
		sell_year = None
	# For each desc, a dict retrieve all the data.
	for desc in tree.xpath('.//tei:text//tei:item//tei:desc', namespaces=ns):
		data = {}
		desc_id = desc.xpath('./@xml:id', namespaces=ns)[0]  # get the item's ID
		if desc.xpath('parent::tei:item/tei:measure[@quantity]', namespaces=ns):  # si il y a un prix, le récupérer
			price = to_float(desc.xpath('parent::tei:item//tei:measure[@commodity="currency"]/@quantity', namespaces=ns)[0])
			currency = desc.xpath('parent::tei:item//tei:measure[@commodity="currency"]/@unit', namespaces=ns)[0]
			data["currency"] = currency
			data["price"] = price
			# convert the prices to express them in constant francs (at the 1900 rate)
			if sell_year is not None and price is not None:
				if currency == "FRF":
					price_c = pconverter_franc(date=sell_year, price=price)
				else:
					price_c = pconverter_foreign(currency=currency, date=sell_year, price=price)
				data["price_c"] = price_c
		else:
			data["price"] = None
		if desc.xpath('parent::tei:item/tei:name[@type="author"]/text()', namespaces=ns):  # get the author's surname
			author = desc.xpath('parent::tei:item/tei:name[@type="author"]/text()', namespaces=ns)[0]
			try:
				# We only keep the surname of the author : we stop the match at the first
				# parenthesis or dot and we keep the first match.
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
		if sell_date is not None:
			data["sell_date"] = sell_date
		# In order to check the data, we add its text (and only its text with .strip_tags) in the dict.
		etree.strip_tags(desc, '{http://www.tei-c.org/ns/1.0}*')
		data["desc"] = desc.text

		# update the main dictionnary with the data of this file and return
		output_dict[desc_id] = data
	return output_dict


def catalog_extractor(tree, catalog_dict):
	"""
	function to extract data on each catalogue and store it in a json file : year, number of items sold,
	stats about the item's price...
	all prices are expressed in francs at the 1900 rate, EVEN the prices in foreign currencies,
	EVEN if "currency" is not in francs. the "_c" suffix signals that the prices are expressed
	in constant francs.
	:param tree: a catalog in XML format parsed with lxml
	:param catalog_dict: a dictionnary to store all the data
	:return: updated version of catalog_dict ; type dict, obviously
	"""
	data = {}  # dictionary to store all the data on a catalog
	# retrieve the title, sale date and number of entries in the catalog
	if tree.xpath(".//tei:titleStmt//tei:title", namespaces=ns):
		data["title"] = tree.xpath(".//tei:titleStmt//tei:title", namespaces=ns)[0].text
	if tree.xpath('.//tei:bibl/tei:date[@when]', namespaces=ns):
		date = tree.xpath('.//tei:bibl/tei:date/@when', namespaces=ns)[0]
		data["sell_date"] = date
	elif tree.xpath(".//.//tei:bibl/tei:date/text()", namespaces=ns):
		date = tree.xpath('.//tei:bibl//tei:date/text()', namespaces=ns)[0]
		data["sell_date"] = date
	if tree.xpath(".//tei:body//tei:item", namespaces=ns):
		data["item_count"] = int(tree.xpath("count(.//tei:body//tei:item)", namespaces=ns))

	# if the catalog is a fixed-price catalog (has "tei//item//tei:measure[@commodity='currency']",
	# extract data about the prices
	if tree.xpath(".//tei:body//tei:item[.//tei:measure/@commodity='currency']", namespaces=ns):
		date = re.findall(r"\d{4}", date)[0]  # year of the sell date to convert the price to fixed price
		# get the currency in which the catalog items are sold
		if tree.xpath(".//tei:body//tei:item//tei:measure[@commodity]/@unit", namespaces=ns):
			currency = tree.xpath(".//tei:body//tei:item//tei:measure[@commodity]/@unit", namespaces=ns)[0]
			data["currency"] = currency
		ipdict = {}  # dictionnary linking a tei:item's @xml:id to its price
		plist = []  # list of the prices in one catalog
		big = {}  # dictionnary to host all the most expensive items in a catalog
		for item in tree.xpath(".//tei:body//tei:item[.//tei:measure/@commodity='currency']", namespaces=ns):
			# if an item only has one price, extract it ; we try to get the price from the @quantity
			# of the tei:measure, then from the text content of the tei:measure ; the only prices that
			# are left must conform to the regular expression "[0-9]+(\.[0-9]+)?" ; else; price is None
			price = 0  # price of an item
			if item.xpath("./@xml:id", namespaces=ns):
				cat_id = item.xpath("./@xml:id", namespaces=ns)[0]
			if len(item.xpath(".//tei:measure[@commodity='currency']", namespaces=ns)) == 1:
				try:
					if re.match(r"[0-9]+(\.[0-9]+)?",
								item.xpath(".//tei:measure[@commodity='currency']/@quantity", namespaces=ns)[0]):
						price = item.xpath(".//tei:measure[@commodity='currency']/@quantity", namespaces=ns)[0]
					elif re.match(r"[0-9]+(\.[0-9]+)?",
								  item.xpath(".//tei:measure[@commodity='currency']/text()", namespaces=ns)[0]):
						price = item.xpath(".//tei:measure[@commodity='currency']/text()", namespaces=ns)[0]
				except:
					price = None
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

			# extend ipdict and plist with the data from every item
			if price is not None:
				# convert the price to a fixed price: franc at the 1900 rate
				if currency == "FRF":
					price = pconverter_franc(date=date, price=price)
				else:
					price = pconverter_foreign(currency=currency, date=date, price=price)
				ipdict[cat_id] = price
				plist.append(price)
		# add the most expensive items to big
		for ip in ipdict.items():
			if ip[1] == sorted(plist)[-1]:
				big[ip[0]] = ip[1]
		# calculate the total sale price
		psum = 0
		for p in plist:
			psum += p
		psum = to_number(psum)
		plist = sorted(plist)
		# produce some statistical data for the catalog
		data["total_price_c"] = psum  # the sum of the tei:item's prices
		data["low_price_c"] = plist[0]  # the lowest price in the catalog
		data["high_price_c"] = plist[-1]  # the highest price in the catalog
		data["mean_price_c"] = mean(plist)  # the average price in the catalog
		data["median_price_c"] = median(plist)  # the median price of the catalog
		data["mode_price_c"] = mode(plist)  # the mode price (most frequent price)
		data["variance_price_c"] = pvariance(plist)  # the population variance of the prices
		data["high_price_items_c"] = big  # a dict with the most expensive item's @xml:id as keys, and price as values
	# if there is no information about the price in the catalogs, the above elements are not created

	# update the main dictionnary with the data of the file and return
	if tree.xpath("./@xml:id", namespaces=ns):
		catalog_dict[tree.xpath("./@xml:id", namespaces=ns)[0]] = data
	return catalog_dict


# ============== AUXILIARY FUNCTIONS ============== #
def to_float(string):
	"""
	This function tries to convert a string into a float.
	:param string: a string
	:return: a float or None
	"""
	try:
		return float(string)
	except:
		return None


# extraire les nombres d'une chaîne de caractère pour faire des comparaisons pendant le clustering
def get_numbers(string):
	"""
	This function gets the numbers of a string with a regex.
	in our case, we do this in order to compare int and not str during the clustering.
	:param string: a string
	:return: int
	"""
	try:
		numbers = re.search('[0-9]+', string)
		return int(numbers[0])
	except:
		return None


def to_number(string):
	"""
	function to convert a price string into an int or float in order to do calculations
	:param str: string to convert ; type string
	:return: string converted to float or int (if there's no problem) ; else, None
	"""
	try:
		string = int(string)
	except:
		try:
			string = float(string)
		except:
			string = None
	return string


# ============== COMMAND LINE INTERFACE ============== #
if __name__ == "__main__":

	# This way, we get every single file contained in any subfolder of Catalogues/.
	files = glob.glob("../Catalogues/**/*.xml", recursive=True)

	output_dict = {}  # dictionary to store the data on the items retrieved in data_extractor()
	catalog_dict = {}  # dictionary to store the data on the catalogs retrieved in catalog_extractor()

	for file in files:
		# additional error handling: if there is an error here (the only step where there can
		# be an error, really), print the name of the file on which the error happened, the
		# full error message and exit)
		try:
			# Each file is parsed and the functions are run
			tree = etree.parse(file)

			item_extractor(tree, output_dict)
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

	# write the outputs to the output files
	with open('../output/export_item.json', 'w') as outfile:
		# Older data are deleted. 
		outfile.truncate(0)
		json.dump(output_dict, outfile, indent=4)
	with open('../output/export_catalog.json', 'w') as outfile:
		# Older data are deleted.
		outfile.truncate(0)
		json.dump(catalog_dict, outfile, indent=4)
