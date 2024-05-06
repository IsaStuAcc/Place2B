
import gspread 
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
import pandas as pd 

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file']
creds = ServiceAccountCredentials.from_json_keyfile_name("place2b-testiva-22af13cb6682.json", scope)

client = gspread.authorize(creds)

sheet = client.open("geo_daten_schweiz und estv_income_rates_schweiz").get_worksheet_by_id(0)

data = sheet.get_all_records()
df = pd.DataFrame(data)

pprint(data)
