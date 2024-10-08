import gspread
from oauth2client.service_account import ServiceAccountCredentials
import xml.etree.ElementTree as ET
from gspread.cell import Cell
from amoapi import *

def create_sheets(google_link,amo_url,long_termtoken):

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Загружаем учетные данные из JSON-файла
    creds = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)

    # Авторизуемся
    client = gspread.authorize(creds)

    spreadsheet_url = google_link #"https://docs.google.com/spreadsheets/d/19fwHasz8EYgmdWSWnk1w6CjS0AXdvdQaEF27rn5JCjI/edit?gid=0#gid=0"
    spreadsheet = client.open_by_url(spreadsheet_url)


    worksheets = spreadsheet.worksheets()
    sheet_names = [sheet.title for sheet in worksheets]
    data = get_data(amo_url,long_termtoken)
    piplines = data['names']
    leads = data['leads']
    custom = data['custom_fields']
    base = ['ID','Ответсвенный','Этап сделки','Бюджет','Дата создания','Дата закрытия']

    for i in piplines:
        if(not(i in sheet_names)):
            headers = base
            headers.extend(custom[i])
            cell_updates = []
            new = spreadsheet.add_worksheet(title=i, rows="50000", cols=str(len(headers)))
            for j in range(len(headers)):
                cell_updates.append(Cell(1, j+1, headers[j]))
            new.update_cells(cell_updates)

    worksheets = spreadsheet.worksheets()
    for i in worksheets:
        cell_updates = []
        row = 2
        count = 0
        if(i.title in piplines):
            for j in leads:
                count+=1
                print(j[3],i.title)
                if(j[3]==i.title):
                    col = 1
                    for f in range(len(j)):
                        if(f!=3):
                            cell_updates.append(Cell(row,col,j[f]))
                            col+=1
                    row+=1
            
            i.update_cells(cell_updates)

    sheet_names = [sheet.title for sheet in worksheets]
    data = get_data2(amo_url,long_termtoken)['result']
    names = ['Дата','Автор','Объект','Название','Событие','Значение до','Значение после']
    cell_updates = []

    for i in range(len(names)):
        cell_updates.append(Cell(1,i+1,names[i]))

    worksheets[0].update_cells(cell_updates)

    worksheets = spreadsheet.worksheets()

    cell_updates =[]
    for i in range(len(data)):
        for j in range(len(data[i])):
            cell_updates.append(Cell(i+1,j+1,data[i][j]))

    worksheets[0].update_cells(cell_updates)
