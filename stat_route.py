import json
import datetime

import flask
from flask_app import app


@app.route("/stat/<string:id_query>/<string:date1>/<string:date2>", methods=["GET"])
def stat(id_query: str, date1: str, date2: str):
    """Метод /stat берёт в качестве параметров ID полного запроса,
    а также две даты: начало и конец интервала, за который нужно вывести счётчики.

    Даты должны быть написаны в специальном формате, описанном в модуле /index.
    Даты включают в себя год, месяц, число, часы и минуты.

    Данный метод ищет в файле данных JSON для данного ID полного запроса те записи, в которых временноя метка находится
    в указанном интервале, после чего
    при успешном выполнении выводит на страницу в формате JSON те записи, которые соответствуют условию.

    Параметры:
    id_query (str): ID полного запроса
    date1 (str): начало временного интервала
    date2 (str): начало временного интервала

    Возвращает:
    Все записи из файла данных, соответствующие условию, в формате JSON

    """
    stat_dict = dict()  # Словарь, хранящий записи, соответствующие условию

    try:  # Взятие данных из файла json_dict.json и сохранение их в переменной json_dict в виде словаря
        json_file = open("data/json_dict.json", "r")
        json_dict: dict = json.load(json_file)
        json_file.close()
    except:  # При невозможности читать файл json_dict.json происходит перенаправление на главную страницу
        return flask.redirect(flask.url_for("index"))

    try:  # Преобразование даты из строки указанного формата в тип datetime для последующего сравнения
        date1 = datetime.datetime.strptime(date1, "%Y-%m-%d %H:%M")
        date2 = datetime.datetime.strptime(date2, "%Y-%m-%d %H:%M")
    except:  # При неправильном формате ввода даты перенаправить на главную страницу с информацией
        return flask.redirect(flask.url_for("index"))

    if id_query not in json_dict.keys():  # Если словарь пустой или не имеет записей по какому-то запросу,
        return flask.jsonify(stat_dict)   # вернуть на страницу пустой JSON

    for entry in json_dict[id_query]:  # Цикл, проверяющий время добавления каждой записи под указанным ID запроса
        date_query = datetime.datetime.strptime(  # Преобразование даты записи из строки в тип datetime
            json_dict[id_query][entry]["Временная метка"], "%Y-%m-%d %H:%M"
        )
        if (date_query >= date1) and (date_query <= date2):  # Проверка на наличие даты записи в заданном интервале
            stat_dict_info = json_dict[id_query][entry]  # Присвоение информации о записи переменной stat_dict_info
            if id_query in stat_dict.keys():  # Если stat_dict не пустой, то добавить в него под ID запроса запись
                stat_dict[id_query].update({entry: stat_dict_info})
            else:  # Если stat_dict пустой, то добавить в него запись в указанном виде
                stat_dict.update({id_query: {entry: stat_dict_info}})
                # Это сделано для того, чтобы новая запись
                # при добавлении в словарь методом update не перезаписывала старую

    return flask.jsonify(stat_dict)
