# normalised data to link entries in our database to entries in
# wikidata; of course, these conversion tables do not cover all
# of our entries, but there are fallbacks: if a person's function
# doesn't have an equivalent in the "function" dictionary, we can
# still get a full name, dates of birth/death...

# first names ; to be used on tei:trait
# - keys: the abbreviation, found in catalogues;
# - values: the full, normalised orthograph for wikidata
names = {
    "Ad.": "adam",
    "Alex": "alexandre",
    "Alph.": "alphonse",
    "Arm.": "armand",
    "Aug.": "auguste",
    "Ch.": "charles",
    "Cl.": "claude",
    "Emm.": "emmanuel",
    "Ed.": "edouard",
    "Et.": "etienne",
    "Ét.": "etienne",
    "Ferd": "ferdinand",
    "Fr.": "françois",
    "Fréd": "frédéric",
    "G.": "guillaume",
    "Gab.": "gabriel",
    "Jacq.": "jacques",
    "Jh.": "joseph",
    "Jos.": "joseph",
    "Nic.": "nicolas",
    "Ph.": "philippe",
    "V.": "victor",
    "Vr": "victor",
}

# composed first names; for composed names, this table is queried first,
# since a composed name gives context to the parts of the name
# else, we try to resole the abbreviated composed names inititials by initials
# to be used on tei:name
# - keys: the abbreviation, found in catalogues;
# - values: the full, normalised orthograph for wikidata
comp_names = {
    "J.-F.": "jean-francois",
    "J.-M.": "jean-marie",
    "J.-J.": "jean-jacques",
    "J.-L.": "jean-louis",
    "J.-B.": "jean-baptiste",
    "P.-J.": "pierre-jean",
    "J.-Sylvain": "jean-sylvain",
    "L.-Ph.": "louis-philippe"
}

# french nobility and clerical titles: some terms are not translated:
# persons are not referred to using those terms in wikidata;
# to be used on the tei:name
# - keys: the term to be used in wikidata;
# - values: a list of corresponding terms in the tei:traits
nobility = {
    "prince": ["prince"],
    "princess": ["princesse"],
    "duke": ["duc"],
    "duchess": ["duchesse"],
    "count": ["comte", "cte"],
    "countess": ["comtesse", "ctesse"],
    "cardinal": ["cardinal"],
    "pope": ["pape"],
    "None": ["chevalier", "marquis", "marquise"]  # delete this line ?
}

# a person's function; to be found in the tei:trait; not all words
# here have a perfect duplicate in wikidata ; in turn, some very
# frequent words in the tei:trait's are not present here
# - keys: the term to be used in wikidata;
# - values: a list of corresponding terms in the tei:traits
function = {
    "general": ["général"],
    "marshal": ["maréchal"],
    "military": ["lieutenant", "officier", "colonel",
                 "lieutenant-colonel", "commandant", "capitaine"],  # "less important" military positions
    "king": ["roi"],
    "emperor": ["empereur"],
    "president": ["president"],
    "politician": ["homme politique", "président de l'assemblée",
                   "orateur", "député", "secrétaire d'État"],
    "writer": ["écrivain", "auteur", "romancier"],
    "actor": ["acteur"],
    "actress": ["actrice"],
    "singer": ["cantatrice", "chanteur", "chanteuse"],
    "painter": ["peintre"],
    "sculptor": ["sculpteur"],
    "composer": ["compositeur"],
    "musician": ["musicien", "musicienne"],
    "chansonnier": ["chansonnier"],
    "architect": ["achitecte"],
    "journalist": ["journaliste"],
    "inventor": ["inventeur"],
    "chemist": ["chimiste"]
}

# messy regex to match roman numerals and their french number suffixes:
# "Ier", "IInd", "IIIème" ...
rgx_roman = "((I|V|X|D|C|M)+)(er|ère|ere|ème|eme|nd|nde)?"  # only keep $1 of that regex
