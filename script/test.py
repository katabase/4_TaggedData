import unittest
from lxml import etree

from extractor_json import *


class Data_extraction(unittest.TestCase):
    maxDiff = None

    def test_extract_all_data(self):
        tree = etree.fromstring(
            """
  <TEI xmlns="http://www.tei-c.org/ns/1.0" xml:id="CAT_000112">
   <teiHeader xmlns:s="http://purl.oclc.org/dsdl/schematron" xmlns:tei="http://www.tei-c.org/ns/1.0">
    <fileDesc>
     <sourceDesc>
      <bibl>
         <title>REVUE DES CURIOSITÉS DE L'HISTOIRE ET DE LA BIOGRAPHIE</title>
         <num type="lot">109</num>
         <editor>Eugène Charavay fils</editor>
         <publisher>Eugène Charavay fils</publisher>
         <pubPlace>Paris, 8 quai du Louvre</pubPlace>
         <date when="1887-11">Novembre 1887</date>
      </bibl>
     </sourceDesc>
    </fileDesc>
   </teiHeader>
   <text>
    <item n="18" xml:id="CAT_000112_e18">
     <num type="lot">18</num>
     <name type="author">Barry (Ch.)</name>
     <trait>
      <p>célèbre architecte anglais, qui construisit le Parlement de Westminster, né en
           1796, mort en 1860</p>
     </trait>
     <desc xml:id="CAT_000112_e18_d1"><term ana="#document_type_7">L. a. s.</term> au colonel Fox; <date when="1846">1846</date>, <measure type="length" unit="p" n="1">1 p.</measure> <measure type="format" unit="f" ana="#document_format_8">in-8.</measure></desc><measure commodity="currency" unit="FRF" quantity="15">15</measure>
    </item>
   </text>
</TEI>
			"""
        )
        output_dict = {}
        data_extractor(tree, output_dict)

        test_dict = {
            "CAT_000112_e18_d1": {
                "author": "Barry",
                "date": "1846",
                "desc": "L. a. s. au colonel Fox; 1846, 1 p. in-8.",
                "format": "#document_format_8",
                "number_of_pages": 1.0,
                "price": 15.0,
                "sell_date": "1887-11",
                "term": "#document_type_7",
            }
        }

        self.assertDictEqual(output_dict, test_dict)

    def multiple_descs(self):
        tree = etree.fromstring(
            """
  <TEI xmlns="http://www.tei-c.org/ns/1.0" xml:id="CAT_000112">
   <teiHeader xmlns:s="http://purl.oclc.org/dsdl/schematron" xmlns:tei="http://www.tei-c.org/ns/1.0">
    <fileDesc>
     <sourceDesc>
      <bibl>
         <title>REVUE DES CURIOSITÉS DE L'HISTOIRE ET DE LA BIOGRAPHIE</title>
         <num type="lot">109</num>
         <editor>Eugène Charavay fils</editor>
         <publisher>Eugène Charavay fils</publisher>
         <pubPlace>Paris, 8 quai du Louvre</pubPlace>
         <date when="1887-11">Novembre 1887</date>
      </bibl>
     </sourceDesc>
    </fileDesc>
   </teiHeader>
   <text>
    <item n="18" xml:id="CAT_000112_e18">
     <num type="lot">18</num>
     <name type="author">Barry (Ch.)</name>
     <trait>
      <p>célèbre architecte anglais, qui construisit le Parlement de Westminster, né en
           1796, mort en 1860</p>
     </trait>
     <desc xml:id="CAT_000112_e18_d1"><term ana="#document_type_7">L. a. s.</term> au colonel Fox; <date when="1846">1846</date>, <measure type="length" unit="p" n="1">1 p.</measure> <measure type="format" unit="f" ana="#document_format_8">in-8.</measure></desc><measure commodity="currency" unit="FRF" quantity="15">15</measure>
     <desc xml:id="CAT_000112_e18_d2"><term ana="#document_type_7">L. a. s.</term> au colonel Fox; <date when="1846-08-01">1er août 1846</date>, <measure type="length" unit="p" n="3">3 p.</measure> <measure type="format" unit="f" ana="#document_format_4">in-4.</measure></desc><measure commodity="currency" unit="FRF" quantity="55">55</measure>
    </item>
   </text>
</TEI>
			"""
        )

        output_dict = {}
        data_extractor(tree, output_dict)

        test_dict = {
            "CAT_000112_e18_d1": {
                "author": "Barry",
                "date": "1846",
                "desc": "L. a. s. au colonel Fox; 1846, 1 p. in-8.",
                "format": "#document_format_8",
                "number_of_pages": 1.0,
                "price": 15.0,
                "sell_date": "1887-11",
                "term": "#document_type_7",
            },
            "CAT_000112_e18_d2": {
                "author": "Barry",
                "date": "1846-08-01",
                "desc": "L. a. s. au colonel Fox; 1er août 1846, 3 p. in-4.",
                "format": "#document_format_4",
                "number_of_pages": 3.0,
                "price": 55.0,
                "sell_date": "1887-11",
                "term": "#document_type_7",
            }
        }

        self.assertDictEqual(output_dict, test_dict)

    def missing_data(self):
        tree = etree.fromstring("""
  <TEI xmlns="http://www.tei-c.org/ns/1.0" xml:id="CAT_000112">
   <teiHeader xmlns:s="http://purl.oclc.org/dsdl/schematron" xmlns:tei="http://www.tei-c.org/ns/1.0">
    <fileDesc>
     <sourceDesc>
      <bibl>
         <title>REVUE DES CURIOSITÉS DE L'HISTOIRE ET DE LA BIOGRAPHIE</title>
         <num type="lot">109</num>
         <editor>Eugène Charavay fils</editor>
         <publisher>Eugène Charavay fils</publisher>
         <pubPlace>Paris, 8 quai du Louvre</pubPlace>
         <date when="1887-11">Novembre 1887</date>
      </bibl>
     </sourceDesc>
    </fileDesc>
   </teiHeader>
   <text>
    <item n="18" xml:id="CAT_000112_e18">
     <num type="lot">18</num>
     <name>Barry (Ch.)</name>
     <trait>
      <p>célèbre architecte anglais, qui construisit le Parlement de Westminster, né en
           1796, mort en 1860</p>
     </trait>
     <desc xml:id="CAT_000112_e18_d1"><term ana="#document_type_7">L. a. s.</term> au colonel Fox; <date when="1846">1846</date>, <measure type="format" unit="f" ana="#document_format_8">in-8.</measure></desc><measure commodity="currency" unit="FRF" quantity="15">15</measure>
    </item>
   </text>
</TEI>
			"""
                                )
        output_dict = {}
        data_extractor(tree, output_dict)

        test_dict = {
            "CAT_000112_e18_d1": {
                "author": None,
                "date": "1846",
                "desc": "L. a. s. au colonel Fox; 1846, in-8.",
                "format": "#document_format_8",
                "number_of_pages": None,
                "price": 15.0,
                "sell_date": "1887-11",
                "term": "#document_type_7",
            }
        }

        self.assertDictEqual(output_dict, test_dict)


if __name__ == "__main__":
    unittest.main()
