# FROM ubuntu:20.04
FROM python:3.9

RUN echo "Architecture: $(dpkg --print-architecture)"

# ARG DEBIAN_FRONTEND=noninteractive
# RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /packages
COPY packages/ .

# RUN apt-get update
# #megatools=1.10.3-1
# RUN apt-get install -y megatools
# RUN apt-get install -y python3.9 python3.9-dev python3-pip

RUN if [ "$(dpkg --print-architecture)" = "armhf" ]; then dpkg -i megatools_1.10.3-1_armhf.deb; fi
RUN if [ "$(dpkg --print-architecture)" = "arm64" ]; then dpkg -i megatools_1.10.3-1_arm64.deb; fi
RUN if [ "$(dpkg --print-architecture)" = "amd64" ]; then dpkg -i megatools_1.10.3-1_amd64.deb; fi

#for armv7
# RUN apt-get install -y libxml2-dev libxslt-dev libffi-dev

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ .
ENTRYPOINT [ "python3", "telegram_download_daemon.py" ]
