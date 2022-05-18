import requests
import json
import csv
import re

# get a wikidata id from a full text query

# r = requests.get("https://www.wikidata.org/w/api.php?action=query&list=search&srsearch=du+resnel&format=json")


def counter():
    """
    get the most frequent words in tei:traits and the number of times they appear;
    write this dictionary in a json file ; 
    used to get how to clusterize data
    :return: None
    """
    with open("tables/wd_nametable.tsv", mode="r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        trait = ""
        for row in reader:
            trait += f"{row[3]} ; "
    traitlist = list(trait.split())  # total list of "words" in all the tei:trait
    
    # clean traitlist : remove punctuation
    cleanlist = []
    for t in traitlist:
        t = re.sub(r"\.|,|\(|\)", "", t)
        cleanlist.append(t)
    traitlist = cleanlist
    traitset = set(traitlist)  # list of unique items in traitlist
    
    # clean traitset : remove most frequent french characters and useless words
    # so that they aren't counted
    dellist = [".", " ", ";", ",", "-", "le", "la", "un", "une", "des", "de", "d'un", "d'une",
               "ce", "cette", "celui", "celle", "est", "a", "ses", "son", "sa", "leur",
               "leurs", "lui", "elle", "célèbre", "illustre", "homme", "femme", "par",
               "qui", "grand", "au", "fils", "plus", "moins", "les", "&", "é", "è", "et",
               "en", "m", "n", "fr", "du", "mort", "né", "morte", "née", "il", "elle",
               "eux", "avec", "puis", "fut", "vous", "l'illustre", "distingué", "savant",
               "sous", "fameux"]
    for d in dellist:
        if d in traitset:
            traitset.remove(d)
    counter = {}  # dictionary mapping to a word the number of times it is used
    
    # build counter
    nloop = 0
    print("beginning to count occurences of words")
    for w in traitset:
        nloop += 1
        if len(str(nloop)) >= 3 and str(nloop)[-2:] == "00":
            print(f"{nloop} out of {len(traitset)} words counted !")
        # we're looking for words to clusterize ; in turn, they must be meaningful traits, not numbers and such
        if not re.match(r"\d+", w) and not re.match("[A-Z]+", w):
            counter[w] = traitlist.count(w)

    # order counter by descending values
    counter_sort = {}
    for c in sorted(list(counter.values()), reverse=True):
        for k, v in counter.items():
            if v == c:
                counter_sort[k] = v
    # counter_sort = {k: v for k, v in sorted(counter.items(), key=lambda item: item[1])}
    # sortv = sorted(list(counter.values()))  # sorted count of words

    # save counter and print it
    with open("tables/wd_trait_wordcount.json", mode="w", encoding="utf-8") as out:
        json.dump(counter_sort, out, indent=4)
    print("done !")
    return None


def prep_query(in_data):
    """
    prepare the query string: normalize first names, extract data from the tei:trait,
    order the querystring
    :param in_data: input data: a list of the 3rd and 4th entries of the csv
    :return:
    """
    qdict = {}  # dictionary to store query data
    name = in_data[0]  # tei:name
    trait = in_data[1]  # tei:trait
    # parse the name
    # extract the years from tei:trait
    # extract the person's occupation from the tei:trait


def launch_query(qstr):
    """
    get the wikipedia id from a full text query
    :param qstr: the query string (i.e., name for which we want a wikidata id)
    :return:
    """
    # build query url
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": qstr,
        "format": "json"
    }

    # launch query
    r = requests.get(url, params=params)

    # print results
    js = r.json()
    print(js)  # response in JSON
    print(js["query"]["search"][0]["title"])  # first ID


def reqtoid():
    """
    launch the query on all entries of wd_nametable.csv
    :return:
    """
    with open("tables/wd_nametable.tsv", mode="r", encoding="utf-8") as fh:
        reader = csv.reader(fh, delimiter="\t")
        for row in reader:
            in_data = [row[2], row[3]]  # input data on which to launch a query
            prep_query(in_data)



if __name__ == "__main__":
    # req_to_id("louis davout")
    reqtoid()
