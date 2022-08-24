Зависимости:
===========

sanic
sanic-jwt
sqlalchemy
sqlalchemy.ext
contextvars
uuid
base64
Crypto.Hash


Файлы:
=====

models.py - база данных. Если выполнить как самостоятельный файл, то создаст минимальную тестовую базу
server.py - основной исполняемый файл.
server_init.py - общая часть инициализации, используемая в server, common, admin, payments
commom.py - функционал, общий для всех пользователей
admin.py - функционал администратора
payment.py - обработка зачислений
Desc.txt - описание задания
curl.txt - примеры использования