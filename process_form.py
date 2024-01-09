from flask import Flask, render_template, request
import sqlite3
from openpyxl import Workbook
from werkzeug.local import Local, LocalManager
from datetime import datetime

#создание объекта flask для web-приложения
client_from_site = Flask(__name__)

#Настройка локального хранилища для подключения к базе данных и курсора
local = Local()
local_manager = LocalManager([local])

#Функция для получения соединения с базой данных
def get_db():
    if not hasattr(local, 'db'):
        local.db = sqlite3.connect('data.db')
    return local.db

#Функция для закрытия соединения с базой данных
def close_db(error=None):
    if hasattr(local, 'db'):
        local.db.close()

#Регистрация функций для вызова в конце каждого запроса
client_from_site.teardown_appcontext(close_db)

#Функция для полученияя курсора базы данных
def get_cursor():
    if not hasattr(local, 'cursor'):
        local.cursor = get_db().cursor()
    return local.cursor

#Функция для создания таблицы в базе данных
def create_table():
    cursor = get_cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            datetime TEXT
        )
    ''')
    get_db().commit()

create_table()  # Вызываем функцию для создания таблицы

#Маршрут для домашней страницы
@client_from_site.route('/index.html')
def home():
    return render_template('index.html')

#Маршрут для страницы "О нас"
@client_from_site.route('/about.html')
def about():
    return render_template('about.html')

#Маршрут для страницы "Заказать"
@client_from_site.route('/shop.html')
def shop():
    return render_template('shop.html')

#Маршрут для  обработки данных формы
@client_from_site.route('/process_form', methods=['POST'])
def process_form():
    #Получение данных из формы
    name = request.form['name']
    phone = request.form['phone']

    # Добавляем информацию о дате и времени
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    #Получение текущей даты и времени
    cursor = get_cursor()

    # Сохраняем данные в SQLite
    cursor.execute('INSERT INTO clients (name, phone, datetime) VALUES (?, ?, ?)',
                   (name, phone, current_datetime))

    #Применение изменений в базе данных
    get_db().commit()

    # Загружаем данные из SQLite и сохраняем в Excel
    cursor.execute('SELECT * FROM clients')
    rows = cursor.fetchall()

    # Создаем новую книгу Excel и добавляем данные
    wb = Workbook()
    ws = wb.active
    ws.append(['ID', 'Name', 'Phone', 'Datetime'])

    for row in rows:
        ws.append(row)

    # Сохраняем книгу Excel
    wb.save('data.xlsx')

    #Отображение страницы после успешной отправки формы
    return render_template('index.html')  

#Запуск веб-приложения Flask
if __name__ == '__main__':
    client_from_site.run(debug=False)