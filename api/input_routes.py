from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from tools.user_input_jinja import add_input, list_to_dict

router = APIRouter()
templates = Jinja2Templates(directory="api/temp(delete_me)") #note this directory will need to be changed. 

@router.post("/api/add-user-input")
def add_item(entry: str):
    """
    Route to add user input to the user input list. User entries should be entered in the order they will eventually be displayed.

    :param entry: User input
    :type entry: str

    :return: Dictionary containing a list of user entries in order they were entered.
    """
    new = add_input(entry)  
    return {"input_list": new}

@router.get("/api/get-input-list")
def get_input(request: Request):
    input_dict = list_to_dict()
    return templates.TemplateResponse(
        "test.html",
        {"request": request, "input_dict": input_dict})