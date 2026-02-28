import json
from pathlib import Path

#File paths
USER_INPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "user_input.json"
TEMPLATE_INPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "template_input.json"

#define me
ALLOWED_TEXT_SECTIONS = {"steps", "hazards", "mitigations"}


def default_template_payload() -> dict:
    """
    Build the default shape used for template input data.

    This helper guarantees a consistent schema for all Jinja template data:
    - ``metadata``: key/value values for single-value placeholders
    - ``steps``: ordered list of user-provided task steps
    - ``hazards``: ordered list of hazards identified for the project
    - ``mitigations``: ordered list of mitigation statements
    - ``table_rows``: row objects for direct table rendering in Jinja

    :return: Fresh template payload dictionary with empty defaults.
    :rtype: dict
    """
    return {
        "metadata": {},
        "steps": [],
        "hazards": [],
        "mitigations": [],
        "table_rows": [],
    }


def force_template_payload_format(data: dict) -> dict:
    """
    Convert faulty/untrusted JSON data into the default_template_payload schema.

    The function accepts a dictionary that may be incomplete or malformed and
    returns a safe structure with all expected keys present and properly typed.
    Invalid values are replaced with empty defaults so route handlers can
    continue operating without additional defensive logic.

    :param data: Raw dictionary loaded from JSON storage.
    :type data: dict

    :return: Schema-safe dictionary for jinja templates.
    :rtype: dict
    """
    base = default_template_payload()

    if not isinstance(data, dict):
        return base

    metadata = data.get("metadata")
    base["metadata"] = metadata if isinstance(metadata, dict) else {}

    for section in ALLOWED_TEXT_SECTIONS:
        section_data = data.get(section)
        base[section] = section_data if isinstance(section_data, list) else []

    table_rows = data.get("table_rows")
    base["table_rows"] = table_rows if isinstance(table_rows, list) else []

    return base


def load_user_input_data() -> list:
    """
    Safely load user input data from json file.

    Returns an empty list when the file is missing, empty, invalid JSON,
    or not a list.
    """
    if not USER_INPUT_PATH.exists():
        return []

    if USER_INPUT_PATH.stat().st_size == 0:
        return []

    with USER_INPUT_PATH.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return []

    if isinstance(data, list):
        return data

    return []


def add_input(user_input: str) -> list:
    """
    Appends user input to the user_responses list.

    :param user_input: user input for the input field of document
    :type user_input: str

    :return: list of user inputs
    """
   
    data = load_user_input_data()
    data.append(user_input)

    with USER_INPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    return data


def list_to_dict() -> dict:
    """
    Converts the user input list into a dictionary that is keyed to the index of the list items.

    :return: Dictionary of user responses.
    """
    user_responses = load_user_input_data()
    input_dictionary = {}

    for i, input in enumerate(user_responses):
        index = str(i)
        input_dictionary[index] = input

    return input_dictionary


def load_template_input_data() -> dict:
    """
    Load persisted Jinja template input data from json.

    This loader is fault-tolerant. It returns a default payload when the file
    does not exist, is empty, contains invalid JSON, or has an unexpected shape.
    Returning normalized data keeps route handlers simple and predictable.

    :return: Normalized payload dictionary for template data.
    :rtype: dict
    """
    if not TEMPLATE_INPUT_PATH.exists():
        return default_template_payload()

    if TEMPLATE_INPUT_PATH.stat().st_size == 0:
        return default_template_payload()

    with TEMPLATE_INPUT_PATH.open("r", encoding="utf-8") as f:
        try:
            raw_data = json.load(f)
        except json.JSONDecodeError:
            return default_template_payload()

    return force_template_payload_format(raw_data)


def save_template_input_data(data: dict) -> dict:
    """
    Persist normalized template payload data to disk and return it.

    The function always writes schema-safe data by normalizing the incoming
    dictionary before save, which prevents bad payloads from corrupting storage.

    :param data: Candidate payload dictionary to persist.
    :type data: dict

    :return: Normalized dictionary that was written to disk.
    :rtype: dict
    """
    normalized_data = force_template_payload_format(data)

    with TEMPLATE_INPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(normalized_data, f, indent=2)

    return normalized_data


def add_template_text_entry(section: str, entry: str) -> list:
    """
    Append a string entry to one of the ordered text sections.

    Supported sections are ``steps``, ``hazards``, and ``mitigations``.
    A ``ValueError`` is raised for unsupported section names so callers can
    return a clear API validation error.

    :param section: Name of the text section to append to.
    :type section: str
    :param entry: User- or agent-provided text content.
    :type entry: str

    :return: Updated list for the target section after append.
    :rtype: list
    :raises ValueError: If the section name is not supported.
    """
    if section not in ALLOWED_TEXT_SECTIONS:
        raise ValueError(f"Unsupported section: {section}")

    data = load_template_input_data()
    data[section].append(entry)
    persisted_data = save_template_input_data(data)
    return persisted_data[section]


def set_template_metadata_value(field_name: str, value: str) -> dict:
    """
    Set or overwrite one metadata placeholder value used by Jinja templates.

    Metadata is represented as a flat dictionary and is ideal for placeholders
    such as project name, prepared-by, or date fields.

    :param field_name: Metadata key corresponding to a Jinja placeholder name.
    :type field_name: str
    :param value: Value to store under the given metadata key.
    :type value: str

    :return: Updated metadata dictionary after save.
    :rtype: dict
    """
    data = load_template_input_data()
    data["metadata"][field_name] = value
    persisted_data = save_template_input_data(data)
    return persisted_data["metadata"]


def add_table_row(step: str, hazard: str, mitigation: str) -> list:
    """
    Append a fully-formed table row for direct Jinja table rendering.

    Each row stores all three columns needed by the target document table.
    This route-friendly format allows clients to submit final row content
    without separately linking indexes across independent lists.

    :param step: Step description for the row.
    :type step: str
    :param hazard: Hazard description for the row.
    :type hazard: str
    :param mitigation: Mitigation description for the row.
    :type mitigation: str

    :return: Updated list of row dictionaries.
    :rtype: list
    """
    data = load_template_input_data()
    data["table_rows"].append(
        {
            "step": step,
            "hazard": hazard,
            "mitigation": mitigation,
        }
    )
    persisted_data = save_template_input_data(data)
    return persisted_data["table_rows"]


def indexed_map(values: list) -> dict:
    """
    Convert a list into a dictionary keyed by stringified list index values.

    This is useful when a template expects named placeholders such as ``"0"``,
    ``"1"``, and so on instead of iterating over a list directly.

    :param values: Ordered list of values.
    :type values: list

    :return: Dictionary mapping string indexes to their corresponding values.
    :rtype: dict
    """
    return {str(i): value for i, value in enumerate(values)}


def build_template_context() -> dict:
    """
    Build a consolidated Jinja context payload from persisted template input.

    The returned object includes raw lists for direct loop rendering and indexed
    dictionaries for templates that rely on position-based named variables.

    :return: Dictionary containing metadata, raw lists, and indexed maps.
    :rtype: dict
    """
    data = load_template_input_data()

    return {
        "metadata": data["metadata"],
        "steps": data["steps"],
        "hazards": data["hazards"],
        "mitigations": data["mitigations"],
        "table_rows": data["table_rows"],
        "steps_dict": indexed_map(data["steps"]),
        "hazards_dict": indexed_map(data["hazards"]),
        "mitigations_dict": indexed_map(data["mitigations"]),
    }
