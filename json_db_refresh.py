import urllib.request
import ssl
import re
import uuid
import json
import datetime

from celery import Celery
from celery.schedules import crontab

celery = Celery(__name__,
                broker="redis://redis:6379/0",
                backend="redis://redis:6379/0",
                task_track_started=True,
                worker_send_task_events=True)


@celery.task()
def json_db_refresh():
    """Метод json_db_refresh реализует автодобавление новых записей по запросу в файл данных JSON раз в час.

    Автообновление реализовано асинхронно, т.е. оно происходит параллельно при работе сервиса.

    При успешном выполнении метод json_db_refresh записывает для каждого запроса с уже существовавшей записью(-ями)
    новую запись в файле данных JSON.

    Для работы используется Celery, а также сервер Redis.

    Для запуска этого метода необходимо запустить сервер Redis,
    а также сервисы Celery: beat и worker, следующими командами в терминале:

    celery -A json_db_refresh.celery beat --loglevel=debug --max-interval=3600
    celery -A json_db_refresh.celery worker --loglevel=debug -E -P threads


    Параметры:
    ничего

    Возвращает:
    ничего

    """

    ctx = ssl.create_default_context()  # Игнорировать ошибки SSL
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    region_bg = str()

    try:  # Взятие данных из файла json_dict.json и сохранение их в переменной json_dict в виде словаря
        json_file = open("data/json_dict.json", "r")
        json_from_file = json.load(json_file)
        json_file.close()
    except:  # При невозможности читать файл json_dict.json переменной json_dict присваивается пустой словарь
        json_from_file = dict()

    for id_query in json_from_file:  # Для каждого ID запроса находятся регион и сам запрос

        entry = list(json_from_file[id_query].keys())[0]

        region_name_bg = json_from_file[id_query][entry]["Регион"]
        s_query_bg = json_from_file[id_query][entry]["Запрос"]

        if region_name_bg == "Москва":
            region_bg = "moskva"
        if region_name_bg == "Москва и МО":
            region_bg = "moskva_i_mo"
        if region_name_bg == "МО":
            region_bg = "moskovskaya_oblast"
        if region_name_bg == "Россия":
            region_bg = "rossiya"

        url = "https://www.avito.ru/" + region_bg + "?q=" + urllib.request.quote(s_query_bg.encode("utf8"))

        # Нахождение количества объявлений при помощи парсинга страницы с помощью регулярных выражений
        html = urllib.request.urlopen(url, context=ctx).read().decode()
        count = re.findall(r"totalCount&quot;:(\w*)", html)

        entry_id = str(uuid.uuid4())  # Генерация уникального случайного ID для каждой записи

        entry_info = {"Запрос": s_query_bg, "Регион": region_name_bg,  # Формирование словаря с информацией о записи
                      "Счётчик объявлений": count[0],
                      "Временная метка": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                      }

        json_from_file[id_query].update({entry_id: entry_info})  # Добавление записи в словарь

        json_file = open("data/json_dict.json", "w")  # Записать словарь с записями в файл json_dict.json в формате JSON
        json.dump(json_from_file, json_file, sort_keys=True)
        json_file.close()


celery.conf.beat_schedule = {  # Настройка расписания выполнения задачи json_db_refresh для сервиса celery-beat
    "refresh_every_hour": {
        "task": "json_db_refresh.json_db_refresh",
        "schedule": crontab(minute='0', hour='*/1'),
    },
}
