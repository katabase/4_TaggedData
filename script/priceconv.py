from decimal import Decimal
import json
import csv


# ============== GET INFO ON FOREIGN CURRENCIES ============== #
def currency_checker():
    """
    function to check the years and currencies present in catalogues (except for
    the franc) ; should be used to add new values to price_index_foreign.json.
    for the moment, currency_checker works on the export json, so extractor_json.py
    must be ran once before updating price_index_foreign.json and the scripts to
    take into account the new currencies
    :return: None
    """
    with open("../output/export_catalog.json", mode="r") as f:
        truc = json.load(f)
    currency_set = []
    currency_dict = {}
    for t in truc:
        if "currency" in truc[t] and  \
                    truc[t]["currency"] != "FRF":
            currency_set.append(truc[t]["currency"])
            if truc[t]["currency"] not in currency_dict.keys():
                currency_dict[truc[t]["currency"]] = [truc[t]["sell_date"]]
            else:
                currency_dict[truc[t]["currency"]].append(truc[t]["sell_date"])
    currency_set = set(currency_set)
    print(currency_set)
    print(currency_dict)
    return None


# ============== BUILD CONVERSION TABLES ============== #
def multiplier(csvr):
    """
    get the multiplier to calculate the constant price for the items: the year 1900
    is given a value 1, the other prices will be multiplied by 1/(price index in 1900)
    :param csvr: a csv.reader() object
    :return: a multiplier to express all prices in 1900 franc rate
    """
    for row in csvr:
        if row[0] == "1900":
            multiplier = Decimal("1") / Decimal(row[1])
            return multiplier


def converter(csvr, m):
    """
    create a price index to express the price of non-1900 francs in 1900 francs.
    the franc in the XIXth century is considered extremely stable, so inflation
    doesn't affect the prices ; in turn, the index of all years before 1889 and
    after 1815 (end of the 1st Empire)
    (for which Piketty doesn't give any price index) are equivalent of the 1889 inflation
    :param csvr: a csv.reader() object
    :param m: the multiplier used to convert the prices
    :return: idxdict : the dictionary linking a year to its price index
    """
    idxdict = {}  # dictionary mapping to a year the price index for that year
    nloop = 0  # count the number of loops
    for row in csvr:
        pidx = Decimal(row[1]) * Decimal(m)  # price index for a year
        idxdict[row[0]] = round(float(pidx), 2)
        if nloop == 0:
            preidx = {}  # index for the years before 1889
            for i in range(1815, 1889):
                preidx[i] = round(float(pidx), 2)
        nloop += 1
    idxdict = {**preidx, **idxdict}
    print(idxdict)
    return idxdict


def build_convtable():
    """
    build the conversion table for the prices in francs: link to every year
    an index to express the price in 1900 francs
    from Piketty's price indexes, create a json file mapping to each year its
    index (the number by which prices must be multiplied to have constant francs);
    using this dictionary, every year's prices can be converted in 1900 francs
    :return: None
    """
    with open("tables/piketty_price_index.csv") as f:
        csvreader = csv.reader(f, delimiter=',', quotechar='"')
        f.seek(0)
        next(f)
        m = multiplier(csvr=csvreader)  # get the multiplier
        f.seek(0)
        next(f)
        idxdict = converter(csvr=csvreader, m=m)
        with open("tables/price_index_franc.json", mode="w") as out:
            json.dump(idxdict, out, indent=4)
    return None


# ============== CONVERT PRICES IN EXTRACTOR_JSON ============== #
def pconverter_franc(date, price):
    """
    price converter function for francs: the prices from the catalogue
    do not take inflation into account ; in turn, convert the prices in
    1900 constant francs
    :param date: the date of the price
    :param price: the price itself
    :return:
    """
    with open("tables/price_index_franc.json", mode="r") as f:
        idxdict = json.load(f)
    price = round(price * idxdict[str(date)], 2)
    return price


def pconverter_foreign(currency, date, price):
    """
    price converter function for foreign currencies: convert prices in
    foreign currencies in their 1900 franc value. the conversion values
    are created "by hand" for specific years and currencies using
    http://www.historicalstatistics.org/Currencyconverter.html
    :param date: the sell date
    :param currency: the currency in which the item is sold
    :param price: the price of the item
    :return: the converted price
    """
    with open("tables/price_index_foreign.json", mode="r") as f:
        idxdict = json.load(f)
    price = round(price * idxdict[currency][str(date)], 2)
    return price


# if priceconv.py is called as a main item, build the conversion table;
# the functions can be called from external scripts
if __name__ == "__main__":
    build_convtable()