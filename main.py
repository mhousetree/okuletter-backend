from deta import Deta
import os
import datetime
from zoneinfo import ZoneInfo
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import newrelic.agent
newrelic.agent.initialize('./newrelic.ini')

class Letter(BaseModel):
    from_name: str
    to_name: str
    text: str
    font: str
    background: str
    pen: str
    emvelope: str
    stamp: str

my_data_key = os.getenv("MY_DATA_KEY")

deta = Deta(my_data_key)
db = deta.Base("letters")


app = FastAPI()

origins = [
    'http://127.0.0.1:5173',
    'https://okuletter.vercel.app'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def index():
    return "OKULETTER"


@app.post("/letters")
def create_letter(letter: Letter):
    try:
        now = datetime.datetime.now(ZoneInfo("Asia/Tokyo")).strftime('%Y-%m-%d %H:%M:%S')
        letter_dict = letter.dict()
        letter_dict['created_at'] = now

        created_letter = db.put(letter_dict)
        return created_letter
    except Exception as e:
        print(e)
        return JSONResponse({"error": "Failed to create letter"}, 500)

@app.options("/letters")
def option():
    return JSONResponse({})

@app.get("/letters/{key}")
def get_user(key: str):
    try:
        letter = db.get(key)
        if letter:
            return letter
        else:
            return JSONResponse({"error": "Letter not found"}, 404)
    except Exception as e:
        print(e)
        return JSONResponse({"error": "Failed to get letter"}, 500)
