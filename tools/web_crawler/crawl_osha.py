from trafilatura import extract, fetch_url
import os
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import re
from typing import List, Dict, Optional

#TODO 
# - get the job step 
# - Find relavent osha pages - bing search api??
# - Fetch and extract text from the page - trafilatura
# - RAG - chunk the text, then rank chunks against the job step
# - Generate mitigations - write mitigations using the keyword and extracted data
# - out put in a way that can go into each jinja peice

#this is a list of job steps
jobstep = [] # this pull from the endpoint that gets all the jobsteps

construction_hazards = [
    # Struck-by / Caught-in / Equipment Hazards
    "struck_by_heavy_equipment",
    "struck_by_moving_vehicle",
    "struck_by_flying_debris",
    "struck_by_falling_object",
    "caught_in_between_equipment",
    "caught_between_materials",
    "caught_in_rotating_parts",
    "pinch_point_injury",
    "equipment_rollover",
    "crushed_by_load",
    "swing_radius_strike",
    "backover_incident",
    "blind_spot_exposure",
    "equipment_collision",
    "unsecured_load_shift",
    "rigging_failure",
    "dropped_load",
    "forklift_tip_over",
    "crane_boom_contact",

    # Excavation & Trenching
    "excavation_cave_in",
    "trench_collapse",
    "engulfment",
    "fall_into_excavation",
    "spoils_pile_failure",
    "undermined_structure",
    "inadequate_shoring",
    "improper_sloping",
    "inadequate_egress",
    "underground_utility_strike",
    "gas_line_strike",
    "water_line_break",
    "fiber_optic_damage",

    # Electrical
    "electrical_shock",
    "arc_flash",
    "arc_blast",
    "energized_line_contact",
    "overhead_powerline_contact",
    "damaged_extension_cord",
    "improper_grounding",
    "gfc_failure",
    "temporary_power_hazard",
    "static_discharge",

    # Slips / Trips / Falls
    "slip_on_wet_surface",
    "trip_over_material",
    "fall_from_height",
    "fall_same_level",
    "ladder_fall",
    "scaffold_fall",
    "unprotected_edge_fall",
    "roof_fall",
    "fall_through_opening",
    "uneven_ground_trip",
    "mud_ice_slip",
    "improper_three_point_contact",

    # Manual Handling / Ergonomic
    "overexertion",
    "improper_lifting",
    "repetitive_motion_injury",
    "muscle_strain",
    "back_injury",
    "awkward_posture",
    "twisting_while_lifting",
    "shoulder_strain",
    "hand_wrist_strain",
    "vibration_exposure",

    # Noise
    "high_noise_exposure",
    "sudden_impact_noise",
    "long_term_hearing_loss",
    "inadequate_hearing_protection",

    # Thermal Stress
    "heat_stress",
    "heat_exhaustion",
    "heat_stroke",
    "dehydration",
    "cold_stress",
    "hypothermia",
    "frostbite",
    "wind_chill_exposure",

    # Fire & Explosion
    "fuel_spill",
    "flammable_vapor_ignition",
    "hot_work_fire",
    "welding_spark_ignition",
    "explosive_gas_accumulation",
    "improper_refueling",
    "battery_explosion",
    "compressed_gas_cylinder_failure",
    "dust_explosion",

    # Chemical & Environmental
    "silica_exposure",
    "asbestos_exposure",
    "lead_exposure",
    "contaminated_soil_exposure",
    "radiological_exposure",
    "toxic_fume_inhalation",
    "diesel_exhaust_exposure",
    "confined_space_atmosphere",
    "oxygen_deficiency",
    "hazardous_material_spill",
    "chemical_burn",
    "eye_irritation_from_dust",
    "skin_contact_with_chemicals",

    # Hand & Power Tools
    "tool_kickback",
    "unguarded_blade_contact",
    "saw_cut_injury",
    "grinder_wheel_failure",
    "tool_overheating",
    "air_hose_whip",
    "improper_tool_use",
    "damaged_tool_use",
    "battery_tool_fire",

    # Vehicles & Traffic
    "vehicle_collision",
    "public_traffic_intrusion",
    "improper_traffic_control",
    "seatbelt_not_used",
    "fatigued_driving",
    "adverse_weather_driving",
    "poor_visibility_driving",

    # Lifting & Hoisting
    "overloaded_crane",
    "improper_rigging",
    "tagline_not_used",
    "load_swing",
    "boom_overextension",
    "lifting_unknown_weight",
    "person_under_suspended_load",
    "improper_hand_signal",

    # Weather & Environmental Conditions
    "lightning_strike",
    "high_wind_exposure",
    "heavy_rain_flooding",
    "snow_ice_accumulation",
    "extreme_heat_exposure",
    "extreme_cold_exposure",
    "poor_air_quality",
    "reduced_visibility_conditions",

    # Confined Space
    "confined_space_entry",
    "toxic_atmosphere",
    "hazardous_vapor_accumulation",
    "engulfment_in_confined_space",
    "restricted_exit_access",

    # Structural & Material Handling
    "structural_instability",
    "premature_formwork_removal",
    "improper_material_storage",
    "stacked_material_collapse",
    "rebar_impalement",
    "sharp_edge_contact",
    "glass_breakage",
    "formwork_failure",

    # Biological
    "insect_sting",
    "animal_encounter",
    "biohazard_exposure",
    "mold_exposure",

    # Laser & Specialty Equipment
    "laser_eye_exposure",
    "improper_laser_class_use",
    "survey_equipment_trip",

    # Compaction & Heavy Vibration
    "foot_crush_injury",
    "jumping_jack_instability",
    "ground_vibration_exposure",

    # Administrative / Human Factors
    "lack_of_training",
    "inadequate_supervision",
    "fatigue_related_error",
    "poor_communication",
    "improper_pre_task_planning",
    "failure_to_follow_procedure",
    "inadequate_ppe_use",
    "complacency",
    "rushed_work_activity"
]

# Google API - Get search results. 

GOOGLE_CSE_URL = "https://www.googleapis.com/customsearch/v1"

def google_cse_search(query: str, *, start: int = 1, num: int = 10):
    """
    Run one Google Custom Search API request and normalize the response.

    This function handles a single call to the CSE endpoint, using the API key
    and search engine id from environment variables. It builds the request URL,
    sends the HTTP request, decodes the JSON payload, and returns only the
    fields we actually care about (`title`, `url`, and `snippet`).

    The `start` value is 1-based because that is how Google indexes results.
    The `num` value is capped at 10 because the API does not allow more than 10
    results per request.

    Args:
        query: Search phrase that should be sent to Google CSE.
        start: 1-based starting index for result paging. For example, `1` is
            the first page and `11` is the second page when requesting 10 hits.
        num: Desired number of results for this request. Anything over 10 will be set to 10

    Returns:
        list[dict]: A normalized list of search hits. Each hit has:
            - `title`: Result title string (or `None` if missing)
            - `url`: Result link string (or `None` if missing)
            - `snippet`: Preview text string (or `None` if missing)

    Raises:
        KeyError: If `GOOGLE_CSE_API_KEY` or `GOOGLE_CSE_CX` is missing from
            the environment.
        urllib.error.URLError: If the network request fails or times out.
        json.JSONDecodeError: If Google returns a response that is not valid
            JSON.
    """

    ## TODO make these call from env variables.
    api_key = os.environ["GOOGLE_CSE_API_KEY"]
    cx = os.environ["GOOGLE_CSE_CX"]  # your programmable search engine id

    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        # Note: googles indexing starts with 1.
        "start": start,
        # maximum of 10 results can be requested.     
        "num": min(num, 10), 
    }

    # build the HTTP request object - headers are how google identifies debbie
    request = Request(
        f"{GOOGLE_CSE_URL}?{urlencode(params)}",
        headers={"User-Agent": "Debbie/1.0"}
    )

    # this sends requests, it fails after 20 seconds of nothing.
    with urlopen(request, timeout=20) as response:
        #Reads the response as bytes and converts it to a python string - payload = dictionary with the api response
        payload = json.loads(response.read().decode("utf-8"))

    #build into a smaller normalized list - this will return a list of result objects from the search.
    hits = []
    for item in payload.get("items", []):
        hits.append({
            "title": item.get("title"),
            "url": item.get("link"),
            "snippet": item.get("snippet"),
        })
    return hits


def discover_regulatory_urls(hazard_phrase: str, pages: int = 3):
    """
    Discover regulation-related URLs for one hazard phrase across CSE pages.

    This function builds a regulation-focused query using the provided hazard
    phrase, then requests multiple pages of Google CSE results. It makes sure that no duplicates are in the list.

    Search behavior:
    - Query format is: `"{hazard_phrase} regulation requirements"`.
    - Each page request asks for up to 10 hits.
    - `pages=3` means up to 30 raw hits are checked before deduplication.

    Args:
        hazard_phrase: Hazard keyword or short phrase to search for
        pages: Number of CSE pages to scan. Each page is offset by 10 results.

    Returns:
        list[dict]: result objects from `google_cse_search`, in
        the order they were discovered. Each item includes `title`, `url`, and
        `snippet`. No Duplicates.
    """
    # CSE should already be restricted to OSHA + selected domains
    #builds the search string 
    q = f"{hazard_phrase} regulation requirements"
    # seen is the urls already encountered. out is final list of result objects
    seen, out = set(), []

    # Loop page by page and assumes 10 requests per result. returns a final list of requested pages without any duplicates. 
    for i in range(pages):
        start = 1 + i * 10
        for hit in google_cse_search(q, start=start, num=10):
            url = hit["url"]

            #adds seen urls to the seen list 
            if url and url not in seen:
                seen.add(url)
                out.append(hit)
    return out

def get_plain_text_from_url():
    """
    Fetch search hits and extract plain text content from each result URL.

    Current flow:
    1. Calls `discover_regulatory_urls` to get candidate pages.
    2. Fetches each page with `fetch_url`.
    3. Extracts readable content with `trafilatura.extract`.
    4. Collects extracted page text into a list and returns it.

    This function is currently wired with an empty `hazard_phrase` and is
    intended to be updated so hazard selection is dynamic.

    Returns:
        list: Extracted text payloads for each discovered URL.
    """

    #This is a temporary hazard phrase build a way for it to dynamically select the hazard
    response_list = discover_regulatory_urls(hazard_phrase="slips, trips, and falls")

    all_text = []

    for i in response_list:
        url = fetch_url(i.get("url"))
        
        page_text = extract(url, output_format="json", include_comments=False)
        all_text.append(page_text)
    
    return all_text

def chunk_text(
    text: str,
    chunk_size_words: int = 700,
    overlap_words: int = 80,
    source_url: Optional[str] = None,
) -> List[Dict]:
    """
    Split text into overlapping word chunks.
    Returns: [{"chunk_id", "text", "word_start", "word_end", "source_url"}, ...]
    """
    if chunk_size_words <= 0:
        raise ValueError("chunk_size_words must be > 0")
    if overlap_words < 0 or overlap_words >= chunk_size_words:
        raise ValueError("overlap_words must be >= 0 and < chunk_size_words")

    # Collapse whitespace and tokenize by words
    words = re.findall(r"\S+", text or "")
    if not words:
        return []

    chunks = []
    start = 0
    chunk_id = 0

    while start < len(words):
        end = min(start + chunk_size_words, len(words))
        chunk_words = words[start:end]

        chunks.append({
            "chunk_id": chunk_id,
            "text": " ".join(chunk_words),
            "word_start": start,
            "word_end": end,
            "source_url": source_url,
        })

        if end >= len(words):
            break

        # overlap: next chunk backs up by overlap_words
        start = end - overlap_words
        chunk_id += 1

    return chunks
