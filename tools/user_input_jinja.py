import json
from pathlib import Path

#TODO - Get the user input, add user input to a dictionary for jinja

USER_INPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "user_input.json"


def load_user_input_data() -> list:
    """
    Safely load user input data from disk.

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

        
        