"""
Niche definitions for the US iOS opportunity scan.

Apple's 22 categories are far too coarse to find an underserved market —
"Utilities" holds both flashlight apps and $33/download marine chartplotters —
and SensorTower exposes no genre or tag taxonomy of its own on this plan
(top_and_trending, keyword research and category_history all 404). So niches
are defined here: a seed term list that sweeps the catalog via search_entities,
plus the sub-niche patterns and plausible categories used to confirm membership.

Keeping seeds and classifiers in one structure stops the two from drifting
apart, which is what happened when they lived in separate files.

Each family:
  seeds       search terms (English, US market)
  categories  iOS category IDs this family plausibly lives in
  subniches   (label, regex) — first match wins, so specific patterns lead
"""

IOS_CATEGORIES = {
    "6000": "Business", "6001": "Weather", "6002": "Utilities", "6003": "Travel",
    "6004": "Sports", "6005": "Social Networking", "6006": "Reference",
    "6007": "Productivity", "6008": "Photo & Video", "6009": "News",
    "6010": "Navigation", "6011": "Music", "6012": "Lifestyle",
    "6013": "Health & Fitness", "6015": "Finance", "6016": "Entertainment",
    "6017": "Education", "6018": "Books", "6020": "Medical",
    "6023": "Food & Drink", "6024": "Shopping",
}

GAMES_CATEGORY = 6014

# Tool-shaped categories — where a small team can realistically compete.
TOOLS = {6002, 6007, 6006, 6010, 6001, 6017, 6013, 6020, 6000, 6015}

NICHE_DEFS = [
    {
        "family": "Marine & boating",
        "categories": TOOLS | {6003, 6004, 6016},
        "seeds": [
            "sailing", "sailboat", "yacht", "boating", "marine navigation",
            "nautical chart", "chartplotter", "anchor alarm", "anchor watch",
            "tides", "tide times", "marine weather", "boat logbook",
            "boat maintenance", "marina", "mooring", "colreg", "skipper",
            "regatta", "sailing course", "boating license", "vhf radio",
            "ais vessel", "knots guide", "man overboard", "depth sounder",
            "kayak", "paddle board", "canoe", "jet ski",
        ],
        "subniches": [
            ("Nautical charts & navigation", r"chart|navigat|chartplotter|plotter|route|passage"),
            ("Anchor watch & safety", r"anchor|mooring|overboard|colreg|safety|distress"),
            ("Tides & currents", r"tide|current|gelgit"),
            ("Marine weather & routing", r"weather|wind|forecast|routing|swell|marine forecast"),
            ("Boat logbook & maintenance", r"logbook|log book|maintenance|service|engine hours"),
            ("Boating licence & training", r"licen|course|exam|training|test|study|knot|terminolog|academy"),
            ("AIS & vessel tracking", r"\bais\b|vessel|traffic|tracking|fleet"),
            ("Paddle sports", r"kayak|paddle|canoe|row|sup\b"),
        ],
    },
    {
        "family": "Fishing & hunting",
        "categories": TOOLS | {6004, 6003, 6016},
        "seeds": [
            "fishing", "fishing spots", "fishing forecast", "fly fishing",
            "bass fishing", "ice fishing", "fishing knots", "fishing log",
            "fishing regulations", "solunar", "hunting", "hunting maps",
            "deer hunting", "waterfowl", "hunting regulations", "trail camera",
            "ballistics", "archery", "spearfishing", "crabbing",
        ],
        "subniches": [
            ("Fishing spots & forecast", r"spot|forecast|solunar|bite|where|map|finder"),
            ("Fishing regulations & ID", r"regulat|law|limit|license|identif|species"),
            ("Fishing log & knots", r"log|journal|catch|knot|rig|tackle"),
            ("Hunting maps & land", r"hunt|land|parcel|property|boundar|trail cam"),
            ("Ballistics & shooting", r"ballistic|scope|zero|range|archery|bow|arrow"),
        ],
    },
    {
        "family": "Aviation & drone",
        "categories": TOOLS | {6003},
        "seeds": [
            "pilot logbook", "aviation weather", "metar", "flight planning",
            "airspace map", "drone flight", "drone log", "part 107",
            "student pilot", "checkride", "aircraft checklist", "e6b",
            "sectional chart", "airport directory",
        ],
        "subniches": [
            ("Pilot logbook & currency", r"logbook|log book|currency|hours|journal"),
            ("Aviation weather & briefing", r"weather|metar|taf|brief|wind"),
            ("Flight planning & airspace", r"plan|airspace|sectional|chart|route|navlog|airport|directory"),
            ("Drone operations", r"drone|uav|part 107|uas"),
            ("Pilot training & exams", r"checkride|student|exam|test|study|written|oral|e6b|checklist"),
        ],
    },
    {
        "family": "Trades & field service",
        "categories": TOOLS,
        "seeds": [
            "electrician calculator", "electrical code", "plumbing calculator",
            "hvac calculator", "refrigerant charge", "welding calculator",
            "pipe fitting", "conduit bending", "wire size", "voltage drop",
            "construction calculator", "framing calculator", "concrete calculator",
            "surveying app", "laser level", "punch list", "job site",
            "contractor invoice", "estimating app", "blueprint viewer",
        ],
        "subniches": [
            ("Electrical calculators & code", r"electric|wire|voltage|conduit|amp|circuit|nec\b"),
            ("HVAC & refrigeration", r"hvac|refriger|superheat|subcool|duct|psychrometric"),
            ("Plumbing & pipefitting", r"plumb|pipe|fitting|drain|water heater"),
            ("Welding & metalwork", r"weld|metal|fabricat|steel"),
            ("Construction estimating", r"estimat|invoice|bid|quote|takeoff|material|cost"),
            ("Site docs & punch lists", r"punch|checklist|inspect|report|blueprint|plan|jobsite|job site"),
        ],
    },
    {
        "family": "Agriculture & land",
        "categories": TOOLS | {6001},
        "seeds": [
            "farm management", "tractor gps", "field mapping", "crop scouting",
            "livestock records", "cattle records", "beekeeping", "hive records",
            "irrigation scheduling", "soil test", "spray record", "grain bin",
            "pasture management", "chicken coop", "homestead", "orchard",
            "hay production", "farm equipment",
        ],
        "subniches": [
            ("Tractor GPS & field guidance", r"tractor|guidance|gps|row|autosteer|field map"),
            ("Crop & spray records", r"crop|spray|scout|soil|fertil|yield|harvest|grain"),
            ("Livestock & herd records", r"livestock|cattle|herd|sheep|goat|swine|poultry|chicken|animal record"),
            ("Beekeeping", r"bee|hive|apiar"),
            ("Irrigation & water", r"irrigat|water|moisture|rain"),
        ],
    },
    {
        "family": "Auto & vehicle",
        "categories": TOOLS | {6003},
        "seeds": [
            "car maintenance log", "obd2 scanner", "fuel log", "mileage tracker",
            "vehicle inspection", "tire pressure", "car diagnostics",
            "motorcycle log", "rv camping", "trailer towing", "truck driver log",
            "eld logbook", "dashcam", "vin decoder", "auto repair manual",
            "classic car", "ev charging",
        ],
        "subniches": [
            ("Maintenance & fuel logs", r"maintenance|service|fuel|mileage|mpg|log|record|expense"),
            ("OBD & diagnostics", r"obd|diagnost|scanner|code reader|fault|engine light"),
            ("Trucking & compliance", r"truck|eld|hos|dot|weigh|cdl|freight|dispatch"),
            ("RV & towing", r"\brv\b|camper|trailer|tow|motorhome|campground"),
            ("EV & charging", r"\bev\b|electric vehicle|charg|tesla|range"),
        ],
    },
    {
        "family": "Pets & animals",
        "categories": TOOLS | {6012, 6013, 6020},
        "seeds": [
            "dog training", "puppy training", "pet health record", "dog walking",
            "cat care", "pet medication", "aquarium log", "reptile care",
            "horse riding", "equine care", "bird identification", "dog breed",
            "pet weight tracker", "vet records", "animal id",
        ],
        "subniches": [
            ("Pet health & meds", r"health|medic|vet|vaccin|weight|symptom|record"),
            ("Training & behavior", r"train|behav|clicker|command|obedience|puppy"),
            ("Aquarium & reptile", r"aquarium|fish tank|reef|reptile|terrarium|water param"),
            ("Equine", r"horse|equine|ride|stable|barn"),
            ("Species identification", r"identif|\bid\b|breed|species|recogni"),
        ],
    },
    {
        "family": "Home & garden",
        "categories": TOOLS | {6012, 6024},
        "seeds": [
            "home inventory", "home maintenance", "garden planner",
            "plant identification", "plant care", "watering reminder",
            "lawn care", "composting", "pest identification", "seed starting",
            "interior design", "paint color", "room measure", "moving checklist",
            "home renovation", "appliance manual", "hydroponics",
        ],
        "subniches": [
            ("Plant ID & care", r"plant|garden|seed|water|prune|grow|hydroponic|succulent"),
            ("Lawn & pest", r"lawn|grass|pest|weed|insect|mosquito|compost"),
            ("Home inventory & maintenance", r"inventory|maintenance|appliance|manual|warranty|home record"),
            ("Renovation & design", r"renovat|design|paint|color|room|interior|remodel|measure"),
        ],
    },
    {
        "family": "Health self-management",
        "categories": {6013, 6020, 6007, 6002},
        "seeds": [
            "blood pressure log", "blood sugar log", "diabetes tracker",
            "medication reminder", "symptom tracker", "migraine diary",
            "seizure diary", "period tracker", "fertility tracker",
            "pregnancy tracker", "physical therapy", "wound care",
            "asthma tracker", "allergy tracker", "cancer care", "dialysis",
            "medical records", "caregiver", "hearing test", "vision test",
        ],
        "subniches": [
            ("Chronic condition logs", r"blood|sugar|glucose|diabet|pressure|asthma|seizure|migraine|dialysis"),
            ("Medication management", r"medic|pill|dose|prescription|reminder|refill"),
            ("Symptom & flare diaries", r"symptom|diary|journal|flare|pain|track"),
            ("Women's health", r"period|menstrua|fertil|ovulat|pregnan|menopause"),
            ("Rehab & therapy", r"therapy|rehab|exercise|physical|stretch|recovery|wound"),
            ("Caregiving & records", r"caregiv|record|chart|history|appointment|insurance"),
        ],
    },
    {
        "family": "Mental health & sleep",
        "categories": {6013, 6020, 6012, 6007},
        "seeds": [
            "mood tracker", "anxiety relief", "cbt therapy", "gratitude journal",
            "meditation timer", "breathing exercise", "sleep tracker",
            "white noise", "sleep sounds", "insomnia", "dream journal",
            "adhd focus", "habit tracker", "addiction recovery", "sobriety counter",
            "panic attack", "grief support",
        ],
        "subniches": [
            ("Mood & journaling", r"mood|journal|gratitude|diary|reflect|emotion"),
            ("CBT & therapy tools", r"cbt|therap|anxiety|panic|depress|grief|counsel"),
            ("Sleep & sound", r"sleep|insomnia|noise|sound|dream|nap|snore"),
            ("Meditation & breathing", r"meditat|breath|mindful|calm|relax|zen"),
            ("Habits & recovery", r"habit|streak|sober|addict|recovery|quit|abstin"),
            ("Focus & ADHD", r"focus|adhd|pomodoro|distract|attention|concentrat"),
        ],
    },
    {
        "family": "Fitness niches",
        "categories": {6013, 6004, 6002},
        "seeds": [
            "workout log", "powerlifting", "climbing training", "running coach",
            "cycling computer", "swim tracker", "yoga poses", "stretching routine",
            "calisthenics", "kettlebell", "crossfit wod", "martial arts training",
            "boxing timer", "interval timer", "rucking", "hiking tracker",
            "trail running", "triathlon",
        ],
        "subniches": [
            ("Strength logging", r"workout|lift|strength|powerlift|gym|set|rep|kettlebell|crossfit|wod"),
            ("Endurance & GPS sports", r"run|cycl|bike|swim|triathlon|pace|marathon|trail"),
            ("Mobility & bodyweight", r"yoga|stretch|mobility|calisthen|bodyweight|pose"),
            ("Combat sports & timers", r"martial|boxing|mma|timer|interval|round"),
            ("Hiking & rucking", r"hike|hiking|ruck|backpack|trek|summit"),
        ],
    },
    {
        "family": "Food & nutrition",
        "categories": {6023, 6013, 6002, 6007},
        "seeds": [
            "recipe manager", "meal planner", "grocery list", "calorie counter",
            "macro tracker", "food diary", "intermittent fasting", "keto diet",
            "food allergy", "gluten free", "wine cellar", "coffee brewing",
            "cocktail recipes", "beer brewing", "sourdough", "canning",
            "smoker bbq", "sous vide", "kitchen conversion",
        ],
        "subniches": [
            ("Recipe & meal planning", r"recipe|meal|menu|cook|plan|grocery|shopping list|pantry"),
            ("Calorie & macro tracking", r"calorie|macro|nutrit|diet|fast|keto|weight loss|food diary"),
            ("Allergy & restriction", r"allerg|gluten|vegan|intoleran|ingredient|scanner"),
            ("Beverages & brewing", r"wine|coffee|cocktail|beer|brew|whisk|espresso|tea"),
            ("Cooking technique", r"smoker|bbq|grill|sous vide|sourdough|bread|ferment|canning|convert"),
        ],
    },
    {
        "family": "Parenting & family",
        "categories": {6012, 6013, 6017, 6007},
        "seeds": [
            "baby tracker", "breastfeeding log", "baby sleep", "diaper log",
            "toddler activities", "chore chart", "allowance tracker",
            "family calendar", "school planner", "screen time", "co-parenting",
            "milestone tracker", "baby names", "potty training",
        ],
        "subniches": [
            ("Infant tracking", r"baby|infant|newborn|feed|breastfeed|diaper|nurs|bottle"),
            ("Child development", r"milestone|develop|toddler|growth|potty|name"),
            ("Family logistics", r"chore|allowance|calendar|family|co-parent|custody|schedule"),
            ("School & screen time", r"school|homework|study|screen time|parental|control"),
        ],
    },
    {
        "family": "Education & exam prep",
        "categories": {6017, 6006, 6007},
        "seeds": [
            "flashcards", "spaced repetition", "nursing exam", "nclex",
            "bar exam", "cpa exam", "mcat prep", "sat prep", "asvab",
            "cdl practice test", "real estate exam", "citizenship test",
            "ham radio exam", "cissp", "aws certification", "language flashcards",
            "medical terminology", "anatomy study", "music theory",
        ],
        "subniches": [
            ("Flashcards & spaced repetition", r"flashcard|spaced|anki|memoriz|recall|study card"),
            ("Professional licensure exams", r"nclex|nursing|bar exam|cpa|mcat|cissp|aws|pmp|real estate|cdl|certifi"),
            ("Academic test prep", r"\bsat\b|\bact\b|\bgre\b|gmat|asvab|exam|test prep|practice test"),
            ("Domain study aids", r"anatomy|terminolog|music theory|chemistry|physics|math|vocabulary"),
        ],
    },
    {
        "family": "Language learning",
        "categories": {6017, 6006, 6003},
        "seeds": [
            "language learning", "spanish vocabulary", "japanese kanji",
            "chinese characters", "korean hangul", "arabic alphabet",
            "asl sign language", "pronunciation practice", "translation offline",
            "phrasebook", "verb conjugation", "shadowing practice",
        ],
        "subniches": [
            ("Script & character learning", r"kanji|hangul|character|alphabet|script|hiragana|cyrillic"),
            ("Vocabulary & conjugation", r"vocabular|verb|conjugat|grammar|word"),
            ("Speaking & pronunciation", r"pronunc|speak|accent|shadow|conversation"),
            ("Travel phrasebooks", r"phrase|travel|translat|offline|dictionary"),
            ("Sign language", r"sign language|\basl\b|deaf"),
        ],
    },
    {
        "family": "Finance & small business",
        "categories": {6015, 6000, 6007, 6002},
        "seeds": [
            "expense tracker", "mileage log irs", "invoice maker", "receipt scanner",
            "tax deduction", "freelance invoicing", "budget envelope",
            "debt payoff", "net worth tracker", "dividend tracker",
            "crypto portfolio", "rental property", "tip calculator",
            "time tracking billable", "estate planning", "bookkeeping",
        ],
        "subniches": [
            ("Expenses & receipts", r"expense|receipt|scan|spending|budget|envelope"),
            ("Invoicing & freelance", r"invoice|billable|freelance|client|estimate|quote|bookkeep"),
            ("Tax & mileage", r"tax|deduct|mileage|irs|write.?off|1099"),
            ("Debt & net worth", r"debt|payoff|loan|net worth|savings|retire"),
            ("Portfolio tracking", r"portfolio|dividend|stock|crypto|invest|asset"),
            ("Property & rentals", r"rental|property|landlord|tenant|lease|airbnb"),
        ],
    },
    {
        "family": "Productivity tools",
        "categories": {6007, 6002, 6000},
        "seeds": [
            "note taking", "voice memo transcription", "pdf editor", "scanner app",
            "file manager", "clipboard manager", "password manager",
            "barcode scanner", "qr generator", "unit converter", "calculator app",
            "timer app", "checklist app", "mind map", "kanban board",
            "email client", "calendar app", "contact manager", "widget maker",
        ],
        "subniches": [
            ("Notes & capture", r"note|memo|capture|journal|scratch|idea"),
            ("Document scanning & PDF", r"scan|pdf|document|sign|ocr|fax"),
            ("Transcription & voice", r"transcri|voice|dictat|speech|recorder|audio to text"),
            ("Files & clipboard", r"file|clipboard|storage|folder|archive|zip"),
            ("Converters & calculators", r"convert|calculat|unit|currency|measure"),
            ("Task & project boards", r"task|todo|to-do|kanban|project|checklist|mind map|board"),
            ("Widgets & customization", r"widget|icon|theme|customi|lock screen|home screen"),
        ],
    },
    {
        "family": "Photo & video tools",
        "categories": {6008, 6002, 6007},
        "seeds": [
            "photo editor", "raw editor", "photo organizer", "duplicate photo",
            "video editor", "screen recorder", "time lapse", "slow motion",
            "green screen", "photo metadata", "watermark", "collage maker",
            "film simulation", "astrophotography", "product photography",
        ],
        "subniches": [
            ("Photo editing", r"photo edit|raw|filter|retouch|film|preset|lightroom"),
            ("Library & cleanup", r"organiz|duplicate|clean|library|album|metadata|exif"),
            ("Video editing & capture", r"video|screen record|time.?lapse|slow motion|green screen|edit"),
            ("Graphics & overlays", r"watermark|collage|caption|sticker|logo|template"),
        ],
    },
    {
        "family": "Music & audio",
        "categories": {6011, 6002, 6017},
        "seeds": [
            "guitar tuner", "metronome", "chord finder", "sheet music reader",
            "ear training", "drum machine", "midi controller", "audio recorder",
            "podcast editor", "dj mixer", "singing practice", "piano learning",
            "ukulele chords", "bass tabs", "sound meter",
        ],
        "subniches": [
            ("Tuners & metronomes", r"tuner|tune|metronome|pitch|intonation"),
            ("Chords & tabs", r"chord|tab|fretboard|ukulele|guitar|bass|scale"),
            ("Sheet music & theory", r"sheet|notation|score|theory|sight.?read|ear train"),
            ("Recording & production", r"record|daw|midi|drum machine|mixer|podcast|multitrack"),
            ("Instrument practice", r"practice|lesson|learn|piano|sing|vocal|instrument"),
        ],
    },
    {
        "family": "Travel utilities",
        "categories": {6003, 6002, 6010, 6007},
        "seeds": [
            "packing list", "trip planner", "flight tracker", "travel itinerary",
            "currency converter offline", "offline maps", "road trip planner",
            "national parks", "camping spots", "van life", "hostel booking",
            "travel journal", "visa requirements", "jet lag", "luggage tracker",
        ],
        "subniches": [
            ("Trip planning & itinerary", r"trip|itinerar|plan|road trip|route|journey"),
            ("Packing & prep", r"pack|list|luggage|visa|document|checklist"),
            ("Offline maps & guides", r"offline|map|guide|city|walk|transit|metro"),
            ("Camping & outdoors travel", r"camp|park|van life|\brv\b|dispersed|boondock|hostel"),
            ("Flight & transit tracking", r"flight|airline|track|delay|airport|train"),
        ],
    },
    {
        "family": "Hobbies & collecting",
        "categories": {6012, 6006, 6002, 6016},
        "seeds": [
            "coin collection", "stamp collection", "trading card scanner",
            "comic collection", "vinyl record collection", "book library catalog",
            "board game collection", "lego inventory", "model kit",
            "sewing patterns", "knitting counter", "woodworking plans",
            "3d printing", "astronomy stargazing", "birdwatching", "rock identification",
            "metal detecting", "genealogy", "puzzle solver",
        ],
        "subniches": [
            ("Collection cataloging", r"collect|catalog|inventory|library|coin|stamp|card|comic|vinyl|lego|board game"),
            ("Crafts & textiles", r"sew|knit|crochet|quilt|pattern|yarn|stitch|embroider"),
            ("Making & fabrication", r"woodwork|3d print|model|craft|maker|cnc|laser"),
            ("Nature observation", r"astronom|stargaz|bird|rock|mineral|mushroom|forag|nature|identif"),
            ("Genealogy & history", r"genealog|ancestry|family tree|heritage|archive"),
            ("Detecting & treasure", r"metal detect|treasure|geocach|prospect"),
        ],
    },
    {
        "family": "Weather & environment",
        "categories": {6001, 6002, 6006},
        "seeds": [
            "weather radar", "lightning tracker", "hurricane tracker",
            "air quality", "pollen forecast", "uv index", "aurora forecast",
            "earthquake alerts", "wildfire map", "flood warning", "snow report",
            "moon phase", "sunrise sunset", "barometer",
        ],
        "subniches": [
            ("Radar & severe weather", r"radar|lightning|storm|hurricane|tornado|severe|alert"),
            ("Air quality & pollen", r"air quality|pollen|allerg|smoke|\baqi\b|pollut"),
            ("Hazards & alerts", r"earthquake|wildfire|fire|flood|tsunami|emergency|warning"),
            ("Sky & astronomy conditions", r"moon|sun|aurora|eclipse|star|astro|solar"),
            ("Specialty forecasts", r"\buv\b|snow|ski|surf|marine|barometer|frost"),
        ],
    },
    {
        "family": "Accessibility & assistive",
        "categories": {6002, 6013, 6020, 6007, 6017},
        "seeds": [
            "hearing aid app", "live captions", "text to speech", "screen reader",
            "magnifier app", "color blind", "dyslexia reader", "aac communication",
            "speech therapy", "sign language learning", "voice amplifier",
            "tremor assist", "one handed keyboard",
        ],
        "subniches": [
            ("Hearing & captions", r"hear|caption|subtitle|amplif|deaf|sound alert"),
            ("Vision assistance", r"magnif|screen reader|blind|low vision|color blind|describe"),
            ("Speech & communication", r"speech|aac|communicat|voice|stutter|articulat|text to speech"),
            ("Reading & cognitive", r"dyslex|read|cognitive|memory|focus|simplif"),
        ],
    },
    {
        "family": "Religious & spiritual",
        "categories": {6012, 6006, 6018, 6017, 6016},
        "seeds": [
            "bible study", "daily devotional", "bible reading plan", "prayer journal",
            "quran", "prayer times", "qibla", "tasbih", "islamic calendar",
            "torah study", "jewish holidays", "buddhist meditation",
            "rosary", "hymnal", "church giving", "scripture memory",
            "catholic mass", "sermon notes",
        ],
        "subniches": [
            ("Bible study & devotionals", r"bible|devotion|scripture|verse|gospel|testament|sermon|hymn"),
            ("Quran & Islamic study", r"quran|koran|surah|tafsir|hadith|islamic study"),
            ("Prayer times & qibla", r"prayer time|athan|adhan|qibla|salah|namaz"),
            ("Dhikr & counters", r"tasbih|dhikr|zikr|rosary|counter|beads"),
            ("Jewish & other faiths", r"torah|jewish|hebrew|kosher|shabbat|buddhis|hindu|sikh"),
            ("Church & community", r"church|mass|catholic|parish|giving|tithe|congregation|ministry"),
        ],
    },
    {
        "family": "Emergency & safety",
        "categories": {6002, 6013, 6020, 6010},
        "seeds": [
            "first aid guide", "cpr guide", "emergency contacts", "personal safety",
            "sos alert", "survival guide", "wilderness first aid", "disaster prep",
            "emergency kit", "fall detection", "check in safety", "scanner police",
            "radiation detector", "carbon monoxide",
        ],
        "subniches": [
            ("First aid & medical response", r"first aid|cpr|medical|injury|bleed|choke|aed"),
            ("Personal safety & SOS", r"safety|\bsos\b|alert|panic|check in|escort|track me|fall detect"),
            ("Survival & preparedness", r"survival|wilderness|disaster|prep|kit|bug out|shelter"),
            ("Monitoring & detection", r"scanner|radiation|carbon|detector|monitor|alarm"),
        ],
    },
    {
        "family": "Legal & documents",
        "categories": {6000, 6007, 6006, 6015},
        "seeds": [
            "legal forms", "will maker", "power of attorney", "rental agreement",
            "contract template", "notary", "small claims", "immigration forms",
            "traffic ticket", "know your rights", "police interaction",
            "divorce forms", "trademark search",
        ],
        "subniches": [
            ("Wills & estate documents", r"will|estate|attorney|trust|beneficiar|probate"),
            ("Contracts & agreements", r"contract|agreement|lease|rental|template|form|nda"),
            ("Rights & disputes", r"rights|claim|ticket|dispute|police|court|small claims"),
            ("Immigration & filings", r"immigrat|visa|citizen|petition|uscis|trademark|patent"),
        ],
    },
    {
        "family": "Real estate & construction",
        "categories": {6000, 6002, 6015, 6024},
        "seeds": [
            "home inspection", "property listing", "mortgage calculator",
            "square footage", "floor plan", "room scanner lidar",
            "moving planner", "landlord tools", "hoa management",
            "appraisal comps", "open house",
        ],
        "subniches": [
            ("Inspection & reporting", r"inspect|report|punch|defect|condition|checklist"),
            ("Measurement & floor plans", r"measure|square|footage|floor plan|lidar|scan|room|area"),
            ("Mortgage & affordability", r"mortgage|loan|afford|amortiz|payment|interest|calculat"),
            ("Landlord & HOA", r"landlord|tenant|hoa|manage|rent collect|maintenance request"),
        ],
    },
    {
        "family": "Events & personal admin",
        "categories": {6012, 6007, 6024, 6000},
        "seeds": [
            "wedding planner", "guest list", "party planning", "gift tracker",
            "greeting cards", "event countdown", "seating chart",
            "funeral planning", "reunion planning", "volunteer scheduling",
        ],
        "subniches": [
            ("Wedding & large events", r"wedding|bride|venue|seating|registry|ceremony"),
            ("Guest & gift management", r"guest|gift|rsvp|invit|thank you|card"),
            ("Countdowns & reminders", r"countdown|reminder|anniversar|birthday|date"),
            ("Group coordination", r"volunteer|schedul|reunion|signup|roster|committee"),
        ],
    },
]


def all_seeds():
    out = []
    for d in NICHE_DEFS:
        for s in d["seeds"]:
            out.append((d["family"], s))
    return out


def family_index():
    return {d["family"]: d for d in NICHE_DEFS}


TOTAL_SEEDS = sum(len(d["seeds"]) for d in NICHE_DEFS)
# Family-level guard: the app name must contain a token that genuinely belongs
# to this domain. Without it, generic sub-niche stems leak across families —
# "Plantum - AI Plant Identifier" scored as a fishing-regulations app because
# `identif` matched, and it sat in a plausible category.
FAMILY_GUARDS = {
    "Marine & boating": r"sail|boat|yacht|marine|nautic|anchor|tide|helm|boating|skipper|regatta|marina|moor|boater|vessel|nav|chart|kayak|paddle|canoe|knot|seaman|harbo|offshore|cruis",
    "Fishing & hunting": r"fish|angler|tackle|bait|lure|trout|bass|carp|hunt|deer|elk|duck|waterfowl|game|ballistic|archer|bow|spearfish|crab|solunar|catch|reel|rod",
    "Aviation & drone": r"pilot|avia|flight|aero|airport|airspace|metar|taf|drone|uav|uas|e6b|sectional|cockpit|checkride|logbook|part 107|ifr|vfr|plane|aircraft",
    "Trades & field service": r"electric|plumb|hvac|weld|refriger|conduit|voltage|amp|wire|pipe|duct|contractor|jobsite|job site|punch|blueprint|estimat|construc|framing|concrete|survey|trade|superheat|subcool|nec",
    "Agriculture & land": r"farm|tractor|crop|field|harvest|livestock|cattle|herd|sheep|goat|swine|poultry|chicken|bee|bees|hive|apiar|irrigat|soil|pasture|orchard|agri|grain|homestead|spray|yield",
    "Auto & vehicle": r"car|auto|vehicle|obd|truck|trucker|motorcycle|rv|camper|trailer|tow|fuel|mileage|mpg|tire|engine|garage|vin|dashcam|eld|cdl|driver|ev|charg|maintenance|odometer",
    "Pets & animals": r"pet|pets|dog|dogs|puppy|cat|cats|kitten|vet|animal|aquarium|reptile|terrarium|horse|equine|bird|breed|paw|feline|canine|leash|litter",
    "Home & garden": r"home|house|garden|plant|lawn|grass|yard|seed|grow|soil|water|prune|pest|weed|compost|renovat|interior|paint|room|appliance|diy|hydroponic|succulent|bloom|landscap",
    "Health self-management": r"health|medic|blood|glucose|diabet|pressure|symptom|migraine|seizure|asthma|allerg|period|menstrua|fertil|ovulat|pregnan|therapy|rehab|caregiv|patient|clinic|chart|dose|pill|prescri|wound|dialysis|nurse",
    "Mental health & sleep": r"mood|anxie|depress|cbt|therap|mental|mindful|meditat|breath|calm|sleep|insomnia|dream|nap|snore|noise|habit|sober|addict|recovery|focus|adhd|journal|gratitude|stress|panic|grief",
    "Fitness niches": r"workout|fitness|gym|exercise|lift|strength|muscle|rep|reps|set|cardio|run|running|cycl|bike|swim|yoga|stretch|pilates|crossfit|wod|kettlebell|calisthen|hike|hiking|ruck|marathon|triathlon|boxing|martial|train",
    "Food & nutrition": r"recipe|meal|food|cook|kitchen|grocery|pantry|calorie|macro|nutrit|diet|keto|fast|vegan|gluten|allerg|wine|coffee|beer|brew|cocktail|whisk|espresso|tea|bbq|grill|smoker|sourdough|bread|ferment|canning|eat",
    "Parenting & family": r"baby|babies|infant|newborn|toddler|child|kid|kids|parent|mom|dad|famil|diaper|breastfeed|nurs|chore|allowance|school|homework|milestone|potty|custody|nanny|pregnan",
    "Education & exam prep": r"exam|test|quiz|study|flashcard|prep|nclex|cpa|mcat|sat|act|gre|gmat|asvab|cdl|certif|licens|anatomy|terminolog|learn|tutor|course|practice|revision|memoriz|pmp|cissp",
    "Language learning": r"language|spanish|french|german|italian|japanese|kanji|chinese|korean|hangul|arabic|russian|portuguese|hindi|vocabular|verb|conjugat|grammar|pronunc|phrase|translat|dictionary|fluent|asl|sign language|speak|hiragana|katakana",
    "Finance & small business": r"expense|budget|money|financ|invoice|receipt|tax|deduct|mileage|irs|1099|debt|loan|savings|net worth|portfolio|dividend|stock|crypto|invest|rental|landlord|tenant|bookkeep|payroll|billable|freelance|accounting|spend",
    "Productivity tools": r"note|memo|task|todo|to-do|list|scan|pdf|document|file|folder|clipboard|password|barcode|qr|convert|calculat|timer|checklist|mind map|kanban|project|widget|email|calendar|contact|transcri|dictat|organiz|productiv",
    "Photo & video tools": r"photo|picture|image|camera|video|raw|edit|filter|retouch|collage|watermark|screen record|time.?lapse|slow motion|green screen|exif|metadata|album|gallery|lightroom|render|clip",
    "Music & audio": r"music|audio|sound|guitar|piano|drum|bass|ukulele|violin|tuner|tune|metronome|chord|tab|tabs|fretboard|sheet|notation|score|midi|daw|record|mixer|podcast|sing|vocal|pitch|instrument|band|ear",
    "Travel utilities": r"travel|trip|itinerar|flight|airline|airport|hotel|hostel|pack|luggage|passport|visa|map|city|tour|guide|transit|metro|camp|campground|rv|van life|road trip|journey|abroad|destination",
    "Hobbies & collecting": r"collect|catalog|inventory|coin|stamp|card|comic|vinyl|lego|board game|puzzle|sew|knit|crochet|quilt|yarn|stitch|embroider|woodwork|3d print|model|craft|maker|astronom|stargaz|telescope|bird|rock|mineral|mushroom|forag|genealog|ancestry|family tree|metal detect|geocach",
    "Weather & environment": r"weather|radar|forecast|storm|lightning|hurricane|tornado|rain|snow|wind|temperature|air quality|pollen|aqi|smoke|earthquake|wildfire|flood|tsunami|moon|sun|sunrise|sunset|aurora|eclipse|uv|barometer|climate|frost|tide",
    "Accessibility & assistive": r"hear|deaf|caption|subtitle|amplif|magnif|blind|low vision|screen reader|color blind|dyslex|speech|aac|communicat|stutter|articulat|text to speech|accessib|assist|tremor|one hand|sign language",
    "Religious & spiritual": r"bible|scripture|verse|gospel|devotion|prayer|pray|church|mass|catholic|parish|hymn|sermon|quran|koran|surah|tafsir|hadith|islam|muslim|athan|adhan|qibla|salah|namaz|tasbih|dhikr|rosary|torah|jewish|hebrew|shabbat|kosher|buddhis|hindu|sikh|faith|worship|spiritual|holy|saint|tithe",
    "Emergency & safety": r"emergency|first aid|cpr|aed|safety|sos|panic|alert|survival|wilderness|disaster|prepared|rescue|injur|bleed|choke|evacuat|shelter|scanner|radiation|carbon monoxide|detector|hazard|911",
    "Legal & documents": r"legal|law|lawyer|attorney|court|will|estate|trust|probate|contract|agreement|lease|nda|notary|claim|ticket|rights|immigrat|visa|citizen|uscis|petition|trademark|patent|divorce|custody|form",
    "Real estate & construction": r"home|house|property|real estate|realtor|listing|mortgage|apartment|rent|landlord|tenant|hoa|inspect|appraisal|square|footage|floor plan|lidar|measure|room|renovat|construc|blueprint|escrow|closing|mls",
    "Events & personal admin": r"wedding|bride|groom|party|event|guest|rsvp|invit|gift|registry|seating|venue|ceremony|birthday|anniversar|countdown|reunion|volunteer|funeral|celebrat|greeting|card|planner",
}


TOTAL_SEEDS_CHECK = TOTAL_SEEDS
