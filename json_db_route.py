import flask
from flask_app import app
import json


@app.route("/json_db", methods=["GET"])
def json_db():
    """Метод /json_db при успешном выполнении выводит на страницу данные о запросах в формате JSON.

    Параметры:
    ничего

    Возвращает:
    Все записи из файла данных в формате JSON

    """

    try:  # Взятие данных из файла json_dict.json и сохранение их в переменной json_from_file в виде словаря
        json_file = open("data/json_dict.json", "r")
        json_from_file: dict = json.load(json_file)
        json_file.close()
    except:  # При невозможности читать файл json_dict.json переменной json_from_file присваивается пустой словарь
        json_from_file = dict()
    return flask.jsonify(json_from_file)
