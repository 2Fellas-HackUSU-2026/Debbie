

#TODO - Get the user input, add user input to a dictionary for jinja



user_responses = []

def add_input(user_input: str):
    """
    Appends user input to the user_responses list.

    :param user_input: user input for the input field of document
    :type user_input: str

    :return: list of user inputs
    """
    user_responses.append(user_input)
    return user_responses