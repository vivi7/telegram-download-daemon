FROM python:3.10

COPY ./packages/*.* /packages/
COPY ./app/*.* /app/
RUN dpkg -i /packages/megatools_1.10.3-1_amd64.deb
RUN pip install -r /app/requirements.txt

ENTRYPOINT [ "python", "./app/telegram_download_daemon.py" ]
