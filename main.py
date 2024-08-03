from tables import *
import sqlite3

def fetch_data_from_db(db_path):
    # Подключение к базе данных SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Выполнение SQL-запроса для извлечения данных
    cursor.execute("SELECT name, google_link, long_term_token, lead_filter, event_filter FROM mainapp_amoacc")
    
    # Извлечение всех строк результата
    rows = cursor.fetchall()
    
    # Получение имен столбцов
    column_names = [description[0] for description in cursor.description]
    
    # Преобразование данных в список словарей
    result = []
    for row in rows:
        row_dict = dict(zip(column_names, row))
        result.append(row_dict)
    
    # Закрытие соединения с базой данных
    conn.close()
    
    return result

if __name__ == "__main__":
    db_path = 'backend/db.sqlite3'  # Укажите путь к вашей базе данных SQLite
    data = fetch_data_from_db(db_path)    
    print(data)
for i in data:
    google_link = i['google_link']
    amo_url = i['name']
    long_termtoken = i['long_term_token']
    create_sheets(google_link,amo_url,long_termtoken)