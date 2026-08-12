"""
Niche definitions for the opportunity scan.

iOS has no "Religion" category — religious apps scatter across Lifestyle (6012),
Reference (6006), Books (6018) and Education (6017). Same story for vertical
utilities: "sailing" is not a category, it is a long tail inside Utilities (6002),
Navigation (6010), Travel (6003) and Sports (6004). So niches are defined by
keyword seeds and confirmed against the app's real category list.
"""

# ---------------------------------------------------------------- categories

IOS_CATEGORIES = {
    "6000": "Business",
    "6001": "Weather",
    "6002": "Utilities",
    "6003": "Travel",
    "6004": "Sports",
    "6005": "Social Networking",
    "6006": "Reference",
    "6007": "Productivity",
    "6008": "Photo & Video",
    "6009": "News",
    "6010": "Navigation",
    "6011": "Music",
    "6012": "Lifestyle",
    "6013": "Health & Fitness",
    "6015": "Finance",
    "6016": "Entertainment",
    "6017": "Education",
    "6018": "Books",
    "6020": "Medical",
    "6023": "Food & Drink",
    "6024": "Shopping",
}

# Categories worth a full TR ranking sweep for these two niches.
TR_SWEEP_CATEGORIES = [
    "6002", "6012", "6006", "6018", "6017", "6013",
    "6010", "6004", "6003", "6016", "6007", "6001",
]

# Sailing/marine is a global-market play, so sweep US too.
US_SWEEP_CATEGORIES = ["6002", "6010", "6003", "6004", "6001"]

CHARTS = [
    "topfreeapplications",
    "topgrossingapplications",
    "toppaidapplications",
]

# ---------------------------------------------------------------- niche seeds

# Turkish-language + general Islamic religious terms. Mixed script/spelling
# variants are deliberate — the store index treats "kur'an" and "kuran" apart.
RELIGIOUS_TR_TERMS = [
    "kuran", "kur'an", "kuran meali", "kuran dinle", "kurani kerim",
    "namaz", "namaz vakti", "ezan", "ezan vakti", "kıble", "qibla",
    "dua", "dualar", "zikir", "tesbih", "tesbihat", "salavat",
    "hadis", "ilmihal", "esmaül hüsna", "esma", "tefsir", "meal",
    "hac", "umre", "oruç", "ramazan", "imsakiye", "iftar", "sahur",
    "mevlid", "yasin", "cevşen", "hatim", "elifba", "tecvid",
    "islami", "islam", "müslüman", "dini", "abdest", "peygamber",
    "siyer", "risale", "kaza namazı", "cuma", "sure", "ayet",
    "diyanet", "cami", "hutbe", "zekat", "kurban",
]

# English/global Islamic terms — the competitor set a TR app is measured against.
RELIGIOUS_GLOBAL_TERMS = [
    "quran", "prayer times", "muslim", "islamic", "athan", "adhan",
    "dhikr", "tasbih", "hijri calendar", "halal",
]

# Marine / sailing vertical, EN + TR.
MARINE_TERMS = [
    "sailing", "sailboat", "yacht", "boating", "boat", "marine",
    "nautical", "nautical chart", "chartplotter", "navionics",
    "anchor alarm", "anchor watch", "tides", "tide times", "currents",
    "ais", "vhf", "colreg", "skipper", "regatta", "yacht racing",
    "marina", "mooring", "logbook", "sea forecast", "wind forecast",
    "weather routing", "knot", "sailing knots", "man overboard",
    "depth sounder", "fishing", "spearfishing", "scuba diving",
    "kayak", "paddle", "surf forecast", "buoy",
    "yelken", "tekne", "denizcilik", "balıkçılık", "dalış", "amatör denizci",
]

# Other under-served vertical utilities worth a look while we are paying for calls.
VERTICAL_UTILITY_TERMS = [
    "beekeeping", "arıcılık", "greenhouse", "sera", "irrigation", "sulama",
    "livestock", "hayvancılık", "tractor", "traktör", "harvest",
    "welding", "cnc", "machinist", "electrician", "elektrikçi",
    "plumber", "tesisatçı", "hvac", "solar panel", "güneş paneli",
    "truck driver", "kamyon", "forklift", "warehouse", "depo",
    "amateur radio", "telsiz", "drone log", "aviation logbook",
    "caving", "mağara", "climbing", "tırmanış", "hunting", "avcılık",
]

NICHES = {
    "religious_tr": RELIGIOUS_TR_TERMS,
    "religious_global": RELIGIOUS_GLOBAL_TERMS,
    "marine": MARINE_TERMS,
    "vertical_utility": VERTICAL_UTILITY_TERMS,
}
