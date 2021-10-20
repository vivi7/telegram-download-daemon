FROM python:3.6

COPY ./app/*.* /app/
RUN pip install -r /app/requirements.txt

ENTRYPOINT [ "python", "./app/telegram-download-daemon.py" ]
