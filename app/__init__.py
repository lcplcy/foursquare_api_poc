from flask import Flask
import foursquare
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.config.from_object(Config)

client = foursquare.Foursquare(client_id=os.getenv("FOURSQUARE_CLIENT_ID"),
                               client_secret=os.getenv("FOURSQUARE_CLIENT_SECRET"),
                               redirect_uri='https://fsq-api-v3.herokuapp.com/redirect')


scope = ['https://www.googleapis.com/auth/spreadsheets']
json_creds = os.getenv("GOOGLE_SHEETS_CREDS_JSON")


creds_dict = json.loads(json_creds)
creds_dict["private_key"] = creds_dict["private_key"].replace("\\\\n", "\n")
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gsheets_client = gspread.authorize(creds)

from app import routes, models
