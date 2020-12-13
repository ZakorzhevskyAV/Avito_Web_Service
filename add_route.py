import urllib.request
import ssl
import re
import uuid
import json
import datetime

import flask
from flask_app import app


@app.route("/add/<string:s_query>/<int:region_num>", methods=["GET"])
def add(s_query: str, region_num: int) -> str:
    """Метод /ddd берёт в качестве параметров поисковый запрос и номер региона (т.е. полный запрос),
    находит количество объявлений по данному полному запросу,
    а затем регистрирует запрос, название региона, количество объявлений и временную метку
    в файле данных формата JSON.

    Каждому полному запросу присваивается 2 уникальных ID:

    первый ID - ID полного запроса - генерируется на основе URL страницы с информацией о количестве объявлений
    и одинаков для каждого полного запроса;

    второй ID - ID записи - генерируется случайно и присваивается каждой отдельной записи.

    При успешном выполнении метод /add записывает новую запись в файле данных JSON
    и выводит на страницу информационную строку об успешной регистрации записи в базе.

    Параметры:
    s_query (str): поисковый запрос
    region_num (int): номер региона (соответствие названий регионов и их номеров описано в модуле index)

    Возвращает:
    (str): информационная строка об успешной регистрации записи в базе

    """

    ctx = ssl.create_default_context()  # Игнорировать ошибки SSL
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    region = str()
    region_name = str()

    if region_num not in range(1, 5):
        return flask.redirect(flask.url_for("index"))

    if region_num == 1:
        region = "moskva"
        region_name = "Москва"
    if region_num == 2:
        region = "moskva_i_mo"
        region_name = "Москва и МО"
    if region_num == 3:
        region = "moskovskaya_oblast"
        region_name = "МО"
    if region_num == 4:
        region = "rossiya"
        region_name = "Россия"

    url = "https://www.avito.ru/" + region + "?q=" + urllib.request.quote(s_query.encode("utf8"))

    id_query = str(uuid.uuid3(uuid.NAMESPACE_URL, url))  # Генерация уникального ID для каждого запроса на основе URL

    try:  # Нахождение количества объявлений при помощи парсинга страницы с помощью регулярных выражений
        html = urllib.request.urlopen(url, context=ctx).read().decode()
        count = re.findall(r"totalCount&quot;:(\w*)", html)
    except:  # Если парсинг невозможен, то перенаправить на главную страницу
        return flask.redirect(flask.url_for("index"))

    entry_id = str(uuid.uuid4())  # Генерация уникального случайного ID для каждой записи

    try:  # Взятие данных из файла json_dict.json и сохранение их в переменной json_dict в виде словаря
        json_file = open("data/json_dict.json", "r")
        json_dict: dict = json.load(json_file)
        json_file.close()
    except:  # При невозможности читать файл json_dict.json переменной json_dict присваивается пустой словарь
        json_dict = dict()

    if id_query in json_dict.keys():  # Если json_dict не пустой, то добавить в него под ID запроса запись
        json_dict[id_query].update({entry_id: {"Запрос": s_query, "Регион": region_name,
                                               "Счётчик объявлений": count[0],
                                               "Временная метка": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                                               }})
    else:  # Если json_dict пустой, то добавить в него запись в указанном виде
        json_dict.update({id_query: {entry_id: {"Запрос": s_query, "Регион": region_name,
                                                "Счётчик объявлений": count[0],
                                                "Временная метка": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                                                }}})
        # Это сделано для того, чтобы новая запись при добавлении в словарь методом update не перезаписывала старую

    json_file = open("data/json_dict.json", "w")  # Записать словарь с записями в файл json_dict.json в формате JSON
    json.dump(json_dict, json_file, sort_keys=True)
    json_file.close()

    return f"Запрос '{s_query}' в регионе {region_name} был успешно зарегистрирован под id запроса = {id_query} \"" \
           f"и id записи = {entry_id}"
