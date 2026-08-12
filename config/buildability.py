"""
Hand-scored build barriers per sub-niche.

This file is judgment, not measurement. The API tells us what a niche earns and
how crowded it is; it cannot tell us whether the thing is buildable by a small
team moving fast. So the barriers below are assigned by hand and kept visible
and editable rather than hidden inside a scoring function.

The central tension this exists to expose: the niches with the best economics
are usually the ones with the highest barriers, and that is *why* they are
underserved. Marine charts earn $12/download with a 2.86-star leader because
the moat is licensed hydrographic data, not code. Qibla finders are trivially
buildable, which is exactly why 264 of them exist and revenue is $0.04/download.
Buildability and opportunity are inversely correlated; the sweet spot is niches
gated by *effort and attention* rather than by data, hardware or network effects.

Each barrier is 0-5, higher = harder:
  data      proprietary or licensed datasets required (charts, parcels, AIS)
  hardware  sensor, BLE or device integration beyond phone GPS/compass
  network   needs critical mass of users/UGC before it is useful at all
  regulatory safety-critical, liability-exposed or formally regulated
  content   correctness-critical content authoring (scripture, codes, curricula)

Weights reflect how badly each blocks a fast-moving solo build. Data moats and
network effects are the real killers: you cannot out-code a licensing agreement
or a cold-start problem. Content burden is heavy but tractable with AI.
"""

WEIGHTS = {
    "data": 1.35,
    "network": 1.25,
    "regulatory": 1.05,
    "hardware": 0.95,
    "content": 0.75,
}

# sub_niche label -> barrier scores + a one-line rationale shown in the UI
BARRIERS = {
    # ---------------- religious ----------------
    "Quran reading / mushaf": {
        "data": 2, "hardware": 0, "network": 1, "regulatory": 1, "content": 4,
        "note": "Verified text is free, but licensed reciter audio and error-intolerance are the real cost.",
    },
    "Quran memorization / tajweed": {
        "data": 2, "hardware": 1, "network": 1, "regulatory": 1, "content": 4,
        "note": "Speech scoring is now cheap with AI; tajweed rule correctness is the hard part.",
    },
    "Prayer times / athan": {
        "data": 1, "hardware": 0, "network": 0, "regulatory": 0, "content": 1,
        "note": "Calculation methods are public. Trivial to build — which is why it is saturated.",
    },
    "Qibla finder": {
        "data": 0, "hardware": 1, "network": 0, "regulatory": 0, "content": 0,
        "note": "Great-circle bearing plus a compass. The most commoditized thing in the scan.",
    },
    "Tasbih / dhikr counter": {
        "data": 0, "hardware": 0, "network": 0, "regulatory": 0, "content": 1,
        "note": "A counter. Zero barrier, zero revenue — the purest volume trap here.",
    },
    "Dua / supplication": {
        "data": 1, "hardware": 0, "network": 0, "regulatory": 1, "content": 3,
        "note": "Authorable content with translation/attribution care. Monetizes far better than counters.",
    },
    "Hadith / fiqh reference": {
        "data": 2, "hardware": 0, "network": 1, "regulatory": 1, "content": 5,
        "note": "Scholarly verification burden and high reputational downside on errors.",
    },
    "Hajj / Umrah": {
        "data": 3, "hardware": 0, "network": 2, "regulatory": 2, "content": 3,
        "note": "Logistics/venue data is the gate; also intensely seasonal demand.",
    },
    "Ramadan / fasting": {
        "data": 1, "hardware": 0, "network": 1, "regulatory": 0, "content": 2,
        "note": "Low barrier but a one-month demand window each year.",
    },
    "Mosque / community": {
        "data": 3, "hardware": 0, "network": 4, "regulatory": 1, "content": 2,
        "note": "Needs a maintained venue database and local critical mass. Cold-start heavy.",
    },
    "Islamic lifestyle (other)": {
        "data": 2, "hardware": 0, "network": 2, "regulatory": 1, "content": 2,
        "note": "Broad catch-all; barrier depends entirely on the specific product.",
    },
    "Christian / other faith": {
        "data": 2, "hardware": 0, "network": 1, "regulatory": 1, "content": 4,
        "note": "Modern Bible translations (NIV, ESV) are copyrighted — licensing is a real gate.",
    },

    # ---------------- marine ----------------
    "Charts / chartplotter": {
        "data": 5, "hardware": 2, "network": 1, "regulatory": 4, "content": 2,
        "note": "Licensed hydrographic data plus navigation liability. Best economics, hardest moat.",
    },
    "Weather / wind / routing": {
        "data": 3, "hardware": 0, "network": 1, "regulatory": 2, "content": 1,
        "note": "GFS/NOAA models are free; the work is ingestion, rendering and forecast UX.",
    },
    "Tides & currents": {
        "data": 2, "hardware": 0, "network": 0, "regulatory": 2, "content": 1,
        "note": "NOAA publishes US harmonic constants openly — far more tractable than charts.",
    },
    "AIS / vessel tracking": {
        "data": 4, "hardware": 1, "network": 2, "regulatory": 1, "content": 1,
        "note": "Live AIS feeds are a recurring commercial cost. Hard to undercut incumbents.",
    },
    "Anchor watch / safety": {
        "data": 0, "hardware": 1, "network": 0, "regulatory": 2, "content": 1,
        "note": "Phone GPS only, no licensed data, no cold start. The standout buildable niche.",
    },
    "Boat & yacht charter": {
        "data": 2, "hardware": 0, "network": 5, "regulatory": 2, "content": 1,
        "note": "Two-sided marketplace. Supply acquisition, not code, is the entire problem.",
    },
    "Logbook / maintenance": {
        "data": 0, "hardware": 1, "network": 0, "regulatory": 1, "content": 2,
        "note": "Pure CRUD plus good UX. Nothing blocks a fast build.",
    },
    "Sailing training / theory": {
        "data": 0, "hardware": 0, "network": 0, "regulatory": 1, "content": 3,
        "note": "Content is authorable and AI-assistable; exam prep monetizes without a data moat.",
    },
    "Racing / regatta": {
        "data": 2, "hardware": 2, "network": 3, "regulatory": 1, "content": 2,
        "note": "Timing accuracy and fleet adoption both matter; niche within a niche.",
    },
    "Fishing spots & forecast": {
        "data": 3, "hardware": 0, "network": 4, "regulatory": 2, "content": 1,
        "note": "Incumbent value is user-contributed catch data — a cold-start wall.",
    },
    "Diving / freediving": {
        "data": 2, "hardware": 4, "network": 1, "regulatory": 4, "content": 2,
        "note": "Dive-computer BLE integration plus decompression liability. Highest $/download, avoid anyway.",
    },
    "Surf": {
        "data": 3, "hardware": 0, "network": 2, "regulatory": 1, "content": 1,
        "note": "Buoy and cam feeds carry recurring cost; Surfline's content library is the moat.",
    },
    "Marina / harbour services": {
        "data": 3, "hardware": 0, "network": 4, "regulatory": 1, "content": 2,
        "note": "Needs marina supply relationships. Business development, not engineering.",
    },

    # ---------------- vertical utility ----------------
    "Agriculture / tractor": {
        "data": 3, "hardware": 3, "network": 1, "regulatory": 1, "content": 2,
        "note": "Field-boundary data and RTK-grade GPS expectations raise the floor considerably.",
    },
    "Beekeeping": {
        "data": 0, "hardware": 0, "network": 1, "regulatory": 0, "content": 2,
        "note": "Genuinely trivial to build — but the measured market is close to nonexistent.",
    },
    "Trades (elec/plumb/HVAC)": {
        "data": 2, "hardware": 1, "network": 1, "regulatory": 2, "content": 4,
        "note": "Value is codified standards and code tables; correctness carries real liability.",
    },
    "CNC / machining": {
        "data": 2, "hardware": 2, "network": 1, "regulatory": 1, "content": 3,
        "note": "Reference/calculator products are buildable; real CAM is not a weekend project.",
    },
    "Trucking / logistics": {
        "data": 4, "hardware": 0, "network": 3, "regulatory": 3, "content": 2,
        "note": "Truck-legal routing, weigh stations and live fuel pricing are all bought data.",
    },
    "Radio / comms": {
        "data": 2, "hardware": 3, "network": 2, "regulatory": 3, "content": 2,
        "note": "Hardware pairing and licensing rules dominate; small addressable audience.",
    },
    "Outdoor (hunt/climb/cave)": {
        "data": 5, "hardware": 1, "network": 2, "regulatory": 2, "content": 2,
        "note": "onX's $81M rests on licensed parcel/landowner data. The moat IS the product.",
    },
    "Aviation / drone": {
        "data": 4, "hardware": 2, "network": 1, "regulatory": 5, "content": 2,
        "note": "Airspace data plus aviation regulation. Wrong shape for a fast independent build.",
    },
}

# Worst case if every barrier were maxed — used to normalize onto 0-100.
_MAX = sum(5 * w for w in WEIGHTS.values())


def buildability(sub_niche):
    """0-100, higher = more realistically shippable by a small AI-assisted team."""
    b = BARRIERS.get(sub_niche)
    if not b:
        return None
    penalty = sum(b[k] * w for k, w in WEIGHTS.items())
    return round((1 - penalty / _MAX) * 100)


def barrier_note(sub_niche):
    b = BARRIERS.get(sub_niche)
    return b["note"] if b else ""


def top_barriers(sub_niche, n=2):
    """The specific things blocking this niche, worst first — for UI display."""
    b = BARRIERS.get(sub_niche)
    if not b:
        return []
    scored = [(k, b[k] * w) for k, w in WEIGHTS.items() if b[k] >= 3]
    scored.sort(key=lambda x: -x[1])
    return [k for k, _ in scored[:n]]
