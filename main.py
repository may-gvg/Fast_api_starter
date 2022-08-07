


import sqlite3
from io import BytesIO
from typing import Union

import fastapi
import matplotlib.pyplot as plt
import mysql.connector as connection
import pandas as pd
import requests
import uvicorn
from fastapi import FastAPI, Request, UploadFile
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, inspect
from starlette import status
from starlette.responses import StreamingResponse

details = {
    'Name': ['Marek', 'Wojtek', 'Zuzia', 'Tadeusz'],
    'Age': [23, 21, 22, 21],
    'Curency': ['PLN', 'US', 'CZK', 'EURO'],
}

# creating a Dataframe object
df = pd.DataFrame(details)
df.plot()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# variables pass

RECIPES = "Best"

# df values pass
dupa = df.values.tolist()


# route to html + variable
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    context = {'request': request, "recipes": RECIPES}
    return templates.TemplateResponse("index.html", context)


# route to html + df show
@app.get("/page", response_class=HTMLResponse)
def page(request: Request):
    context = {'request': request, "dupa": dupa}
    return templates.TemplateResponse("index2.html", context)


@app.get("/analiza", response_class=HTMLResponse)
def page1(request: Request):
    context = {'request': request}
    return templates.TemplateResponse("analiza.html", context)


@app.get("/analiza2", response_class=HTMLResponse)
def page2(request: Request):
    context = {'request': request}
    return templates.TemplateResponse("analiza2.html", context)


@app.get("/ppt", response_class=HTMLResponse)
def page3(request: Request):
    context = {'request': request}
    return templates.TemplateResponse("ppt.html", context)


@app.get("/pyspark", response_class=HTMLResponse)
def page4(request: Request):
    context = {'request': request}
    return templates.TemplateResponse("pyspark.html", context)


# plot to html
@app.get("/page2", response_class=HTMLResponse)
def page2(request: Request):
    context = {'request': request}
    return templates.TemplateResponse("index4.html", context)


@app.get("/graph", name="Return the graph obtained")
async def create_graph():
    # create a buffer to store image data
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


# download

file_path1 = 'static/share/datacamp.pdf'


@app.get("/download")
def download1():
    return FileResponse(path=file_path1, filename=file_path1, media_type='application/pdf')


# upload

ALLOWED_EXTENSIONS = {'html', 'csv', 'pdf', 'xls', 'xlsx', 'json', 'ppt', 'pptx'}


@app.get("/upload1", response_class=HTMLResponse)
def upload1(request: Request):
    context = {'request': request}
    return templates.TemplateResponse("upload.html", context)


@app.post("/upload2")
async def create_upload_file(file: Union[UploadFile, None] = None):
    if allowed_file(file.filename):
        contents = await file.read()
        f = open("static/share/" + file.filename, "wb")
        f.write(contents)
        f.close()
    else:
        return "Wrong extension"
    return fastapi.responses.RedirectResponse('/', status_code=status.HTTP_302_FOUND)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# db mysql.connector  connect to stops_df
try:
    mydb = connection.connect(host="localhost", database='gtfs', user="root", passwd="letgo666", use_pure=True)
    query = "Select * from stops;"
    stops_df = pd.read_sql(query, mydb)
    mydb.close()  # close the connection
except Exception as e:
    mydb.close()
    print(str(e))

# db sqlite3 connect 2 to df
cnx = sqlite3.connect('static/analiza/analiza.db')
curs = cnx.cursor()
print(curs.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall())
df = pd.read_sql_query("SELECT * FROM atm_transactions", cnx)
cnx.close()  # close the connection

# db sqlalchemy connect 3 to df2
engine = create_engine('sqlite:///static/analiza/analiza.db')
insp = inspect(engine)
print(insp.get_table_names())
results = engine.execute("SELECT * FROM atm_transactions")
df2 = pd.read_sql("atm_transactions", engine)
engine.dispose()  # close the connection



# get request apis 2
response = requests.get("http://api.nbp.pl/api/exchangerates/tables/C?format=json")
data_from_json = response.json()
df4 = pd.json_normalize(data_from_json)

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
