from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from tools.user_input_jinja import add_input

router = APIRouter()

@router.get("/user-input")
def add_item(entry: str):
    """
    Route to add user input to the user input list. User entries should be entered in the order they will eventually be displayed.

    :param entry: User input
    :type entry: str

    :return: Dictionary containing a list of user entries in order they were entered.
    """
    new = add_input(entry)  
    return {"input_list": new}
