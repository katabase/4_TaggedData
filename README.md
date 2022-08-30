# Tagged Data - level 3

This repository contains digitised manuscripts sale catalogs encoded in XML-TEI at level 3.

The data have been cleaned ([level 2](https://github.com/katabase/2_CleanedData)) and post-processed (level 3).

## Schema

You can find the ODD that validates the encoding in the repository [Data_extraction (folder `_schemas`)](https://github.com/katabase/Data_extraction/tree/master/_schemas).

## Workflow

Once the data have been cleaned and post-processed, we can check them. Some errors may appear and some corrections may be needed. 

From this data, `extractor-json.py` extracts informations and retrieves them in an JSON file, [available here](https://github.com/katabase/3_TaggedData/tree/main/output).

The script transforms this 

```xml
<item n="80" xml:id="CAT_000146_e80">
   <num>80</num>
   <name type="author">Cherubini (L.),</name>
   <trait>
      <p>l'illustre compositeur</p>
   </trait>
   <desc>
      <term>L. a. s.</term>;<date>1836</date>,
      <measure type="length" unit="p" n="1">1 p.</measure> 
      <measure unit="f" type="format" n="8">in-8</measure>.
      <measure commodity="currency" unit="FRF" quantity="12">12</measure>
    </desc>
</item>
```

into 

```json
{
"CAT_000146_e80_d1": {
    "desc": "L. a. s.; 1836, 1 p. in-8. 12",
    "price": 12.0,
    "author": "Cherubini",
    "date": "1836",
    "number_of_pages": 1.0,
    "format": 8,
    "term": 7,
    "sell_date": "1893-03"
  }
}
```

From `export.json`, we can proceed at the reconciliation of the catalogues entries. 

If you want to learn more about the reconciliation, visite [this repository](https://raw.github.com/katabase/reconciliation). 

If you want to query the database, don't hesitate to try our [application](https://raw.github.com/katabase/application).

## Installation and use

```bash
* git clone https://github.com/katabase/3_TaggedData.git
* cd 3_TaggedData
* python3 -m venv my_env
* source my_env/bin/activate
* pip install -r requirements.txt
* cd script 
* python3 extractor_json.py
```
**Note that you have to be in the folder `script`to execute `extractor_json.py`.**

The output file, `export.json`, is in the folder `output`.

### Unittest

If you want run some unittests, try in the folder `script`: 
```bash
python3 test.py
```

## Credits

* The script was created by Alexandre Bartz with the help of Matthias Gille Levenson and Simon Gabay.
* The catalogs were encoded by Lucie Rondeau du Noyer, Simon Gabay, Matthias Gille Levenson, Ljudmila Petkovic and Alexandre Bartz.


## Cite this repository
Alexandre Bartz, Simon Gabay, Matthias Gille Levenson, Ljudmila Petkovic and Lucie Rondeau du Noyer, _Manuscript sale catalogues_, Neuchâtel: Université de Neuchâtel, 2020, [https://github.com/katabase/3_TaggedData](https://github.com/katabase/3_TaggedData).

## Licence
<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Licence Creativ>
The catalogues are licensed under <a rel="license" href="http://creativecommons.org/licenses/>
and the code is licensed under [GNU GPL-3.0](./LICENSE).
