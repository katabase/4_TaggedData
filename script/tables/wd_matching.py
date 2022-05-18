# normalised data to link entries in our database to entries in
# wikidata; of course, these conversion tables do not cover all
# of our entries, but there are fallbacks: if a person's function
# doesn't have an equivalent in the "function" dictionary, we can
# still get a full name, dates of birth/death...

# all of the charaters are in lowercase to ease the matching process

# first names ; to be used on tei:trait
# - keys: the abbreviation, found in catalogues;
# - values: the full, normalised orthograph for wikidata
names = {
    "ad.": "adam",
    "alex": "alexandre",
    "alph.": "alphonse",
    "ant": "antoine",
    "arm.": "armand",
    "aug.": "auguste",
    "ch.": "charles",
    "cl.": "claude",
    "emm.": "emmanuel",
    "ed.": "edouard",
    "et.": "etienne",
    "ét.": "etienne",
    "ferd": "ferdinand",
    "fr.": "françois",
    "fréd": "frédéric",
    "g.": "guillaume",
    "guill.": "guillaume",
    "gab.": "gabriel",
    "jacq.": "jacques",
    "jh.": "joseph",
    "jos.": "joseph",
    "nic.": "nicolas",
    "ph.": "philippe",
    "v.": "victor",
    "vr": "victor",
}

# composed first names; for composed names, this table is queried first,
# since a composed name gives context to the parts of the name
# else, we try to resole the abbreviated composed names inititials by initials
# to be used on tei:name
# - keys: the abbreviation, found in catalogues;
# - values: the full, normalised orthograph for wikidata
comp_names = {
    "f.-m.": "francois-marie",
    "j.-f.": "jean-francois",
    "j.-m.": "jean-marie",
    "j.-j.": "jean-jacques",
    "j.-l.": "jean-louis",
    "j.-b.": "jean-baptiste",
    "j.-p.": "jean-pierre",
    "j.-pierre": "jean-pierre",
    "m.-madeleine": "marie-madeleine",
    "p.-j.": "pierre-jean",
    "j.-sylvain": "jean-sylvain",
    "l.-ph.": "louis-philippe",
    "edm.-ch.": "edmond-charles",
    "ch.-marie": "charles-marie"
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
    "lord": ["lord"],
    "none": ["chevalier", "marquise", "marquis", "sire"]  # delete this line ?
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
                   "orateur", "député", "secrétaire d'état"],
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
# "ier", "iind", "iiième" ...
rgx_roman = "((i|v|x|d|c|m)+)(er|ère|ere|ème|eme|nd|nde)?"  # only keep $1 of that regex

# hybrid of the list of departments created in 1790 + list of 1811 departments
# (largest number of departments in the french history)
# https://fr.wikipedia.org/wiki/liste_des_d%c3%a9partements_fran%c3%a7ais_de_1790
# https://fr.wikipedia.org/wiki/liste_des_d%c3%a9partements_fran%c3%a7ais_de_1811
dpt = [
    "ain",
    "aisne",
    "allier",
    "basses-alpes",
    "hautes-alpes",
    "alpes-maritimes",
    "annepins",
    "provence",
    "ardèche",
    "ardennes",
    "arriège",
    "arno",
    "aube",
    "aude",
    "aveyron",
    "bouches-de-l'elbe",
    "bouches-de-l'escaut",
    "bouches-de-l'yssel",
    "bpuches-de-la-meuse",
    "bouches-du-rhin",
    "bouches-du-rhône",
    "bouches-du-weser",
    "calvados",
    "cantal",
    "charente",
    "charente-inférieure",
    "cher",
    "corrèze",
    "corse",
    "côte-d'or",
    "côtes-du-nord",
    "creuse",
    "deux-nèthes",
    "deux-sèvres",
    "doire",
    "dordogne",
    "doubs",
    "drôme",
    "dyle",
    "ems-occidental",
    "ems-oriental",
    "ems-supérieur",
    "escaut",
    "eure",
    "eure-et-loir",
    "finistère",
    "forêts",
    "gard",
    "haute-garonne",
    "gers",
    "gironde",
    "hérault",
    "ille-et-villaine",
    "indre",
    "indre-et-loire",
    "isère",
    "jemappes",
    "jura",
    "landes",
    "léman",
    "loire",
    "loir-et-cher",
    "haute-loire",
    "loire-inférieure",
    "loiret",
    "lot",
    "lot-et-garonne",
    "lozère",
    "lys",
    "maine-et-loire",
    "manche",
    "marengo",
    "marne",
    "haute-marne",
    "méditerrannée",
    "mayenne",
    "meurthe",
    "meuse",
    "meuse-inférieure",
    "mont-blanc",
    "mont-tonnerre",
    "montenotte",
    "morbihan",
    "meuse",
    "moselle",
    "nièvre",
    "nord",
    "oise",
    "ombrone",
    "orne",
    "ourte",
    "paris",
    "pas-de-calais",
    "pô",
    "puy-de-dôme",
    "hautes-pyrénées",
    "basses-pyrénées",
    "pyrénées-orientales",
    "haut-rhin",
    "bas-rhin",
    "rhin-et-moselle",
    "rhône",
    "rhône-et-loire",
    "roer",
    "rome",
    "haute-saône",
    "saône-et-loire",
    "sambre-et-meuse",
    "sarre",
    "sarthe",
    "seine",
    "seine-et-marne",
    "seine-et-oise",
    "seine-inférieure",
    "sézia",
    "simplon",
    "deux-sèvres",
    "somme",
    "stura",
    "tarn",
    "tarn-et-garonne",
    "taro",
    "trasimène",
    "var",
    "vaucluse",
    "vendée",
    "vienne",
    "haute-vienne",
    "vosges",
    "yonne",
    "yssel-supérieur",
    "zuyderzée"
]

# pre-revolution french provinces
provinces = [
    "île-de-france",
    "berry",
    "orléanais",
    "normandie",
    "languedoc",
    "lyonnais",
    "dauphiné",
    "champagne",
    "aunis",
    "saintonge",
    "poitou",
    "guyenne et gascogne",
    "bourgogne",
    "picardie",
    "anjou",
    "provence",
    "angoumois",
    "bourbonnais",
    "marche",
    "bretagne",
    "maine",
    "touraine",
    "limousin",
    "comté de foix",
    "auvergne",
    "béarn",
    "alsace",
    "artois",
    "roussillon",
    "flandre française et hainaut français",
    "franche-comté",
    "lorraine et trois-évêchés",
    "corse",
    "nivernais",
]

# list of french colonies; alternate and old orthographs
# are in the list too, in order to facilitate the matching process
colonies = [
    "canada",
    "québec",
    "ontario",
    "saint-pierre-et-miquelon",
    "mississippi",
    "missouri",
    "louisiane",
    "anguilla",
    "antigua",
    "dominique",
    "saint-domingue",
    "grenade",
    "guadeloupe",
    "haïti",
    "martinique",
    "monsterrat",
    "saint-martin",
    "saint-barthélémy",
    "sainte-lucy",
    "saint-vincent-et-les-grenadines",
    "saint-eustache",
    "saint-christophe",
    "trinitad et tobago",
    "tobago",
    "brésil",
    "guyane française",
    "guyane",
    "maroc",
    "algérie",
    "algérie française",
    "tunisie",
    "fezzan",
    "dahomey",
    "bénin",
    "burkina-faso",
    "haute-volta",
    "cameround",
    "oubangui-chari",
    "tchad",
    "congo",
    "congo français",
    "moyen-congo",
    "gabon",
    "guinée",
    "guinée française",
    "côte d'ivoire",
    "mali",
    "soudan français",
    "mauritanie",
    "niger",
    "sénégal",
    "gorée",
    "tigi",
    "djibouti",
    "cheikh saïd",
    "comores",
    "madagascar",
    "fort-dauphin",
    "île maurice",
    "mayotte",
    "la réunion",
    "îles éparses",
    "seychelles",
    "tanzanie",
    "zanzibar",
    "île amsterdam",
    "île saint-paul",
    "archipel crozet",
    "îles kerguelen",
    "castellorizo",
    "liban",
    "grand-liban",
    "syrie",
    "sandjak d'alexandrette",
    "inde",
    "indes françaises",
    "pondichéry",
    "karikal",
    "yanaon",
    "mahé",
    "chanderngor",
    "cambodge",
    "laos",
    "viêt-nam",
    "tonkin",
    "annam",
    "cochinchine",
    "guangzhou wan",
    "shanghai",
    "guangzhou",
    "tianjin",
    "hankou",
    "clipperton",
    "nouvelle-calédonie",
    "polynésie française",
    "vanuatu",
    "nouvelles-hébrides",
    "wallis et futuna"
]

countries = [
    "états-unis",
    "etats-unis",
    "états-unis d'amérique",
    "etats-unis d'amérique",
    "grèce",
    "chine",
]