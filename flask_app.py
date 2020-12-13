from flask import Flask

app = Flask(__name__)  # Создание и настройка приложения (объекта) Flask
app.config["JSON_AS_ASCII"] = False  # Для возможности выводить кириллицу в JSON
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True  # Для удобного вывода JSON
