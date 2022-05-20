import requests
import json
import csv
import re

from tables.wd_matching import comp_names, names, status, provinces, dpts, colonies, \
    countries, events, other

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
    fname = ""  # first name of a person or additional info if the tei:name is not about a person
    lname = ""  # last name of a person or main info if the tei:name is not about a person
    nobname_sts = ""  # name owned by a person if they are nobility
    sts_title = []  # nobility title of a person
    dates = []  # dates of life/death of a person (in tei:trait or in tei:name for historical events)
    function = []  # functions occupied by a person (in tei:trait)
    rebuilt = False  # wether a person's first name has been rebuilt from an abbreviation
    abv = None  # wether a person's first name contains abbreviations
    qdata = {
        "fname": "",  # first name of a person
        "lname": "",  # last name of a person
        "nobname_sts": "",  # nobility name if a person has a "status": the name of their land
        "status": [],  # list of statuses of a person
        "dates": [],  # dates indicated in the tei:trait: life/death
        "function": "",  # functions occupated by a person in the tei:trait
        "rebuilt": False,  # wether the name has been rebuilt from an abbreviated form or not
        "abv": None  # wether a first name contains abbreviations or not: True if it contains abvs, False if not,
        #              None if there's no first name
    }  # dictionary to store query data
    name = in_data[0]  # tei:name
    trait = in_data[1]  # tei:trait
    parenth = re.search(r"\(.+\)?", name)  # check if there's text inside the parenthesis
    if parenth is not None:
        inp = re.sub(r"\(|\)", "", parenth[0])  # text in parenthesis
        firstnm, matchstr, rebuilt, abv = namebuild(inp)  # try to extract the full name
    else:
        inp = ""
        matchstr = ""  # so that the case 2 condition doesn't fail

    # =========== PARSE THE NAME =========== #
    # CASE 1 - "DIVERS / DOCUMENTS"
    if re.match(r"^([Dd]((OCUMENT|ocument)[Ss]?|(IVERS|ivers))|\s)+$", name):
        lname = ""

    # CASE 2 - CHARTS
    if re.search("[Cc](HARTE|harte)[sS]?", name) is not None:
        lname = "charter"

    # CASE 3 - it contains geographic data:
    elif any(p in name.lower().split() for p in provinces) \
            or any(d in name.lower().split() for d in dpts) \
            or any(c in name.lower().split() for c in colonies) \
            or any(c in name.lower().split() for c in countries):
        if matchstr == "" and not any(s in name.lower() for s in status):  # check that it's not a name
            # clean the string
            name = re.sub(r"(^\.?\s+|.?\s+.?$)", "", name).lower()
            # remove extra noise : persons
            if name == "pelet de la lozère" or name == "anne de bretagne" or name == "jeanne de bourgogne":
                fname = re.search(r"^[a-z]+", name)[0]
                lname = re.search(r"de", name)[0]
            # extract info about the churches
            elif re.search(r"[ée]glises?", name):
                for d in dpts:
                    if d in name:
                        lname = d
                        fname = "religious buildings"
            # extract other specific places
            elif any(o in name for o in list(other.keys())):
                for o in other:
                    if o in name:
                        fname = other[o]
                        lname = re.search(r"^[A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ]+[a-zàáâäéèêëíìîïòóôöúùûüøœæç]*", name)  # name of city
            # remove the events: assign the event to fname, geographical data to lname, dates to lname
            elif any(e in name for e in list(events.keys())):
                for k, v in events.items():
                    if k in name:
                        dates.append(re.search(r"\d{4}", name)[0]) if re.search(r"\d{4}", name) is not None \
                            else dates.append("")
                        for c in countries:
                            if c in name:
                                lname = c
                        for p in provinces:
                            if p in name:
                                lname = p
                        for c in colonies:
                            if c in name:
                                lname = c
                        for d in dpts:
                            if d in name:
                                lname = d
            # all the other cases, where we have just the name or other, marginal and uselsee
            # info (aka, info that we cannot easily pass to wikidata). the info added to fname
            # is not necessarily meaningful: it is what works best to get the first result to
            # be the good one on wikidata
            else:
                for c in countries:
                    if c in name:
                        lname = c
                for p in provinces:
                    if p in name:
                        fname = "province"
                        lname = p
                for c in colonies:
                    if c in name:
                        fname = "french"
                        lname = c
                for d in dpts:
                    if d in name:
                        fname = "french department"
                        lname = d

    # CASE 4 - other historical events

    # CASE 4 - it's a name (yay!)
    else:
        if inp != "":
            # check whether the name is a nobility (they have a special structure and must be
            # treated differently : "Title name (Actual name, title)").
            # examples:
            # - Ray (Otton de la Roche, sire de) => unimportant title, will be deleted
            # - Sully (Maximilien de Béthune, duc de)  => important title, will be kept
            # nreal = ""  # real name, if the name contains a nobility name: "Otton de la Roche"
            sts = False  # check wether a status name has been found
            for k, v in list(status.items()):
                if k in inp.lower():
                    # extract the person's surname by suppressing the noise (aka, non-surname data)
                    # a surname is something that: 
                    # - isn't a title (isn't in status)
                    # - isn't a name (doesn't match matchstring)
                    # - does not contain only lowercase letters
                    # this horrendous series of regexes pretty much removes all the noise
                    inp = inp.replace(matchstr, "")  # delete strings matched by namebuild (deletes status titles if they were matched)
                    inp = re.sub(f",?\s?(le|la|l')?\s?{k}(\s(de|de\sla|du|d'|,)*(\s|$))*", "", inp)
                    inp = re.sub(r"(^|\s)+(puis|dit)", "", inp)
                    inp = re.sub(r"(^|\s)+([Ll]e|[Ll]a|[Dd]e(s)?|[Dd]u)+(\s|$)", "", inp)
                    inp = re.sub(r"(^|\s)+(et|\.)(\s|$)", " ", inp)
                    inp = re.sub(r"(l'|,)", "", inp)
                    if re.match(r"([A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ][a-zàáâäéèêëíìîïòóôöúùûüøœæç]+)([A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ])", inp):
                        mo = re.match(r"([A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ][a-zàáâäéèêëíìîïòóôöúùûüøœæç]+)([A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ])", inp)
                        inp = re.sub(r"([A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ][a-zàáâäéèêëíìîïòóôöúùûüøœæç]*)([A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ])",
                                     f"{mo[1]} {mo[2]}", inp)  # add a space between two accented words
                    inp = re.sub(r"(\s|^)[a-zàáâäéèêëíìîïòóôöúùûüøœæç]+(\.|,|\s|$)", " ", inp)  # del lowercase words
                    inp = re.sub(r"\s+", " ", inp)
                    
                    sts = True  # a status has been found ; the string will be worked differently
                    sts_title.append(v)  # add the title to the dictionary
            
            if sts is True:
                # print(inp)
                fname = firstnm
                lname = inp
                nobname_sts = name.replace(parenth[0], "")

    qdata = {
        "fname": fname,
        "lname": lname,
        "nobname_sts": nobname_sts,
        "status": sts_title,
        "dates": dates,
        "function": function,
        "rebuilt": rebuilt,
        "abv": abv
    }

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
    # print(r.text)


# ================= WORKING ON NAMES: REGEX MATCHING AND GETTING THE FULL 1ST NAME ================= #
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
    mo = re.search(r"(^|,|\s)[A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ][a-zàáâäéèêëíìîïòóôöúùûüøœæç]*"
                   + "\.?-[A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ][a-zàáâäéèêëíìîïòóôöúùûüøœæç]*\.(\s|,|$)", nstr) \
         or re.search(r"(^|,|\s)[A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ][a-zàáâäéèêëíìîïòóôöúùûüøœæç]*\."
                      + "-[A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ][a-zàáâäéèêëíìîïòóôöúùûüøœæç]*\.?(\s|,|$)", nstr) \
         or re.search(r"(^|,|\s)[A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ]\.?\s"
                      + "[A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ][a-zàáâäéèêëíìîïòóôöúùûüøœæç]*\.(\s|,|$)", nstr) \
         or re.search(r"(^|,|\s)[A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ][a-zàáâäéèêëíìîïòóôöúùûüøœæç]*\.?"
                      + "\s[A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ]\.(\s|,|$)", nstr) \
         or re.search(r"(^|,|\s)[A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ]\.?\s[A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ]\.?(\s|,|$)", nstr) \
         or re.search(r"([A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ]\.){2,}", nstr) \
         or re.search(r"(^|,|\s)([A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ][a-zàáâäéèêëíìîïòóôöúùûüøœæç]*\.?-)+"
                      + "([A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ][a-zàáâäéèêëíìîïòóôöúùûüøœæç]*\.)(\s|,|$)", nstr) \
         or re.search(r"(^|,|\s)([A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ][a-zàáâäéèêëíìîïòóôöúùûüøœæç]*\.-)+"
                      + "([A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ][a-zàáâäéèêëíìîïòóôöúùûüøœæç]*\.?)(\s|,|$)", nstr)
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
    mo = re.search(r"(^|\s)[A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ][a-zàáâäéèêëíìîïòóôöúùûüøœæç]*\.(\s|$)", nstr)
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
    mo = re.search(r"(^|\s)[A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ][a-zàáâäéèêëíìîïòóôöúùûüøœæç]+"
                   +"((\s|-)[A-ZÀÂÄÈÉÊËÏÔŒÙÛÜŸ][a-zàáâäéèêëíìîïòóôöúùûüøœæç]+)*", nstr)
    if mo is not None:
        return mo[0]
    else:
        return None
    

def namebuild(nstr):
    """
    try to 
    - match an abbreviated first name from a name string
    - extract a full first name from an abbreviated version using conversion tables
    :param nstr: the string from which to extract a name
    :return: firstnm, matchstr, rebuilt, abv
    - firstnm :
      - if a name is matched, the full form if possible; else, the full form where
        possible and an abbreviation elsewhere
      - an empty string if no name is matched
    - matchstr : the string that has been matched as a name, to modify the name variable from
      prep_query()
    - rebuilt : a boolean value indicating wether the name has been rebuilt (and can be trusted in queries)
    - abv : a boolean indicating if the name contains abbreviations:
      - True if the firstnm contains abbreviations
      - False if not
      - None if no name string has been matched
    """
    firstnm = ""  # full first name to be extracted
    matchstr = ""  # the matched string
    rebuilt = False  # boolean indicating wether the first name is rebuild (can be trusted)
                     # or not
    abv = None  # boolean indicating wether the name contains an abbreviation or not:
    #             we try to rebuild a full name from abbreviation, but can't always; in
    #             that case, abv is True to indicate that the name contains an abv

    # print(nstr)

    # CASE 1 - if it is a composed abbreviated first name, try to build a full version
    # print(rgx_abvcomp(nstr))
    if rgx_abvcomp(nstr) is not None:
        # print("1")
        abvcomp = rgx_abvcomp(nstr)  # try to match an abbreviated composed name
        matchstr = abvcomp
        # clean the composed name
        abvcomp = re.sub(r"(^\s|\s$|\.)", "", abvcomp)
        abvcomp = re.sub(r"-", " ", abvcomp).lower()

        # try to get the complete form from the composed name dictionary
        for k, v in comp_names.items():
            if abvcomp == k:
                firstnm = v
                rebuilt = True
                abv = False  # boolean indicating wether firstnm contains abbreviations

        # if no composed name is returned, try to rebuild a composed name
        # - first, try to rebuild the composed name from a smaller set of letters
        #   in the comp_names dictionary (J.-P.-Guillaume => "J.-P." is in the dictionary)
        # - then, try to rebuild the name from non-composed names in the the names dictionary
        # example: J.-P.-Ch. => jean pierre charles
        if firstnm == "":
            ndict = {n: False for n in abvcomp.split()}  # dictionary of subnames: "N." in "P.-N."; the
            #                                              boolean indicates wether a match has been found
            # get a full name from composed name: here, J.-P. would be matched
            for k, v in comp_names.items():
                if k in abvcomp:
                    firstnm += f"{v} "  # add the full matched name
                    k = k.split()  # split the matching composed name in a list to mark the terms
                    #                list items as matched in ndict
                    abv = False
                    for i in k:
                        ndict[i] = True  # mark matched subnames as true
                    rebuilt = True
                    break  # stop the loop. it's super unlikely that 2 names in comp_names are in abvcomp with 0 errors
            # get a full name from a single name: here, Ch. would be matched
            for name, found in ndict.items():
                if found is False:
                    for k, v in names.items():
                        if name == k:
                            firstnm += f"{v} "  # add the full version to the name
                            found = True
                            ndict[k] = True  # indicate that the full name has been found
                            rebuilt = True
                    if found is False:
                        firstnm += f"{name} "  # add the abbreviated version if a full version hasn't been found
            # check whether there are still abbreviations in the name to give a value du abv
            if False in list(ndict.values()):
                abv = True
            else:
                abv = False

    # CASE 2 - if it is a "simple" (non-composed) abbreviated name, try to build a full name
    elif rgx_abvsimp(nstr) is not None:
        # print("2")
        abvsimp = rgx_abvsimp(nstr)  # try to match an abbreviated non-composed name
        matchstr = abvsimp
        abvsimp = re.sub(r"(^\s|\s$|\.)", "", abvsimp).lower()
        # try to get the complete name from the names dictionary
        for k, v in names.items():
            if abvsimp == k:
                firstnm = v
                rebuilt = True
                abv = False
        if abv is None:
            abv = True

    # CASE 3 - if it is a full name, keep it that way
    elif rgx_complnm(nstr) is not None:
        # print(3)
        complnm = rgx_complnm(nstr)  # try to match a full name
        matchstr = complnm
        firstnm = complnm.lower()
        abv = False

    # CASE 4 - if no name is matched, the string is not rebuilt
    else:
        # print("4")
        abv = None  # neither true nor false, since there are no names

    # print(firstnm)
    # print(abv)
    # print("_____________________________________")

    return firstnm, matchstr, rebuilt, abv


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