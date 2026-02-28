from fastapi import FastAPI
from api import input_routes


app = FastAPI()

app.include_router(input_routes.router)
