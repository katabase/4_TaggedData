import json
import glob
from lxml import etree

ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

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


def data_extractor(tree, output_dict):
	"""
	This function extract all the data from each desc.
	:param tree: an XML tree
	"""

	# For each desc, a dict retrieve all the data.
	for desc in tree.xpath('.//tei:text//tei:item//tei:desc', namespaces=ns):
		data = {}
		desc_id = desc.xpath('./@xml:id', namespaces=ns)[0]
		if desc.xpath('parent::tei:item/tei:measure[@quantity]', namespaces=ns):
			data["price"] = to_float(desc.xpath('parent::tei:item//tei:measure[@commodity="currency"]/@quantity', namespaces=ns)[0])
		else:
			data["price"] = None
		if desc.xpath('parent::tei:item/tei:name[@type="author"]/text()', namespaces=ns):
			author = desc.xpath('parent::tei:item/tei:name[@type="author"]/text()', namespaces=ns)[0]
			try:
            # We only keep the surname of the author.
				author = author.split(" ")[0]
			except:
				author = None
			data["author"] = author
		else:
			data["author"] = None
		if desc.xpath('./tei:date[@when]', namespaces=ns):
			data["date"] = desc.xpath('./tei:date/@when', namespaces=ns)[0]
		else:
			data["date"] = None
		if desc.xpath('./tei:measure[@type="length"]', namespaces=ns):
			data["number_of_pages"] = to_float(desc.xpath('./tei:measure[@type="length"]/@n', namespaces=ns)[0])
		else:
			data["number_of_pages"] = None
		if desc.xpath('./tei:measure[@type="format"]', namespaces=ns):
			data["format"] = desc.xpath('./tei:measure[@type="format"]/@ana', namespaces=ns)[0]
		else:
			data["format"] = None
		if desc.xpath('./tei:term', namespaces=ns):
			data["term"] = desc.xpath('./tei:term/@ana', namespaces=ns)[0]
		else:
			data["term"] = None
		if desc.xpath('ancestor::tei:TEI/tei:teiHeader//tei:sourceDesc//tei:date[@when]', namespaces=ns):
			data["sell_date"] = desc.xpath('ancestor::tei:TEI/tei:teiHeader//tei:sourceDesc//tei:date/@when', namespaces=ns)[0]
		else:
			data["sell_date"] = None
		# In order to check the data, we add its text (and only its text with .strip_tags) in the dict.
		etree.strip_tags(desc, '{http://www.tei-c.org/ns/1.0}*')
		data["desc"] = desc.text

		output_dict[desc_id] = data



if __name__ == "__main__":

	# This way, we get every single file contained in any subfolder of Catalogues/.
	files = glob.glob("../Catalogues/**/*.xml", recursive=True)

	output_dict = {}

	for file in files:
		# Each file is parsed.
		tree = etree.parse(file)

		data_extractor(tree, output_dict)


	with open('../output/export.json', 'w') as outfile:
		# Older data are deleted. 
		outfile.truncate(0)
		json.dump(output_dict, outfile)
    