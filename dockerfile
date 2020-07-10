FROM python:3.8

RUN pip install python-telegram-bot psycopg2-binary roman unidecode

RUN mkdir /app
ADD . /app
WORKDIR /app

CMD python /app/bot.py
