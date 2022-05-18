import requests
import json
import csv
import re

from tables.wd_matching import names, nobility

# get a wikidata id from a full text query

# r = requests.get("https://www.wikidata.org/w/api.php?action=query&list=search&srsearch=du+resnel&format=json")


# ================= BUILD A QUERY ================= #
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

    # =========== PARSE THE NAME =========== #
    # see if it's a place or a person or a "DIVERS / DOCUMENTS"
    if re.match(r"^([Dd]((OCUMENT|ocument)[Ss]?|(IVERS|ivers))|\s)+$", name):
        qdict["name"] = None
    else:
        parenth = re.findall(r"\(.+\)?", name)
        if len(parenth) > 0:
            inp = re.sub(r"\(|\)", "", parenth[0])  # extract content in parenthesis

            # check whether the name is a nobility (they have a special structure and must be
            # treated differently : "Title name (Actual name, title)")
            nobl = []
            for k, v in nobility.items():
                # DOES IT MAKE SENSE TO KEEP THE TITLE ??? NOT SO SURE
                for t in v:
                    nobl = [t for t in v if t in inp.lower()]
                if len(nobl) > 0:  # if a nobility title is detected, treat it as such
                    print(in_data[0])
                    print(nobl)
            """if len(nobl) > 0 and "princesse" in nobl:
                print(f"{nobl} - {inp}")"""


            # check whether the name is a geographic name: province, department, colony


            # if it is a "normal name", get the full first name from its abbreviation
            if rgx_abvcomp(inp) is not None:
                abvcomp = rgx_abvcomp(inp)  # try to match an abbreviated composed name
                # print(f"1 - {inp} # {abvcomp}")
            elif rgx_abvsimp(inp) is not None:
                abvsimp = rgx_abvsimp(inp)  # try to match an abbreviated non-composed name
                # print(f"2 - {inp} # {abvsimp}")
            elif rgx_complnm(inp) is not None:
                complnm = rgx_complnm(inp)  # try to match a full name
                # print(f"3 - {inp} # {complnm}")
            for k, v in names.items():
                if v in inp.lower():
                    pass
                        # print(t)
    # - extract the surname (at the beginning, outside of "()"
    # - extract the initials (in  "()")
    # - extract nomility titles
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


# ================= REGEX MATCHING ================= #
def rgx_abvcomp(nstr):
    """
    try to extract an abbreviated composed first name. if there is no match, return None

    pattern
    -------
    the patterns in the example below are simplified to keep things readable
    - two strings separated by a "-" or "\s"
    - the first or second string can be a full name ([A-Z][a-z]+)
      or an abbreviation ([A-Z][a-z]*\.)
    - if the strings are separated by "\s", they must be finished by "\."
      (to be sure that we don't capture full names, i.e: "J. Ch."  can be captured,
      but not "Jean Charles")
    - complex names with 3 or more words must have "-" and at least one "\."
    - (\s|$) and (^|\s) are safeguards to avoid matching the end or beginning of another word

    examples
    --------
    matched : M.-Madeleine Pioche de la Vergne  # matched string : M.-Madeleine
    matched : C.-A. de Ferriol  # matched string : C.-A.
    matched : J. F.  # matched string : J. F.
    matched : Jean F.  # matched string : Jean F.
    matched : Jean-F.  # matched string : Jean-F.
    matched : A M  # matched string : A M
    matched : C.-Edm.-G.  # matched string : C.-Edm.-G.
    matched : Charles-Edm.-G.  # matched string : Charles-Edm.-G.
    not matched : Anne M
    not matched : Claude Henri blabla
    not matched : Claude Henri

    :param nstr: the name string used as input
    :return: the matched string if there is a match ; None if there is no match
    """
    mo = re.search(r"(^|\s)[A-Z][a-zàáâäéèêëíìîïòóôöúùûüøœæç]*\.?-[A-Z][a-zàáâäéèêëíìîïòóôöúùûüøœæç]*\.(\s|$)", nstr) \
         or re.search(
            r"(^|\s)[A-Z][a-zàáâäéèêëíìîïòóôöúùûüøœæç]*\.-[A-Z][a-zàáâäéèêëíìîïòóôöúùûüøœæç]*\.?(\s|$)", nstr) \
         or re.search(r"(^|\s)[A-Z]\.?\s[A-Z][a-zàáâäéèêëíìîïòóôöúùûüøœæç]*\.(\s|$)", nstr) \
         or re.search(r"(^|\s)[A-Z][a-zàáâäéèêëíìîïòóôöúùûüøœæç]*\.?\s[A-Z]\.(\s|$)", nstr) \
         or re.search(r"(^|\s)[A-Z]\.?\s[A-Z]\.?(\s|$)", nstr) \
         or re.search(
            r"(^|\s)([A-Z][a-zàáâäéèêëíìîïòóôöúùûüøœæç]*\.?-)+([A-Z][a-zàáâäéèêëíìîïòóôöúùûüøœæç]*\.)(\s|$)", nstr) \
         or re.search(
            r"(^|\s)([A-Z][a-zàáâäéèêëíìîïòóôöúùûüøœæç]*\.-)+([A-Z][a-zàáâäéèêëíìîïòóôöúùûüøœæç]*\.?)(\s|$)",nstr)

    if mo is not None:
        return mo[0]
    else:
        return None


def rgx_abvsimp(nstr):
    """
    try to extract a "simple" (not composed) abbreviated first name. if there is no match, return None

    pattern
    -------
    a capital letter (possibly followed by a certain number of lowercase letters)
    ended with a dot. (\s|$) and (^|\s) are safeguards to avoid matching the beginning
    end of another word.
    *warning* : it can also capture parts of composed abbreviated names => must be used
    in an if-elif after trying to match a composed abbreviated name

    examples
    --------
    matched : bonjour Ad.  # matched string : Ad.
    matched : J. baronne  # matched string : J. 
    matched : J. F.  # matched string : J. 
    matched : Jean F.  # matched string : F.
    not matched : A.-M.
    not matched : Anne M 
    not matched : Hector

    :param nstr: the name string used as input
    :return:
    """
    mo = re.search(r"(^|\s)[A-Z][a-zàáâäéèêëíìîïòóôöúùûüøœæç]*\.(\s|$)", nstr)
    if mo is not None:
        return mo[0]
    else:
        return None


def rgx_complnm(nstr):
    """
    try to extract a complete name from a string. if there is no match, return None

    pattern
    -------
    - an uppercase letter followed by several lowercase letters ;
    - this pattern can be repeated several times, separated by a space or "-"
    - (\s|$) and (^|\s) are safeguards to avoid matching the beginning or end of another word.

    :param nstr: the string from which a name should be extracted
    :return:
    """
    mo = re.search(r"(^|\s)[A-Z][a-zàáâäéèêëíìîïòóôöúùûüøœæç]+((\s|-)[A-Z][a-zàáâäéèêëíìîïòóôöúùûüøœæç]+)?", nstr)
    if mo is not None:
        return mo[0]
    else:
        return None


# ================= COUNT THE MOST FREQUENT WORDS ================= #
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


# ================= LAUNCH THE SCRIPT ================= #
if __name__ == "__main__":
    # req_to_id("louis davout")
    reqtoid()
