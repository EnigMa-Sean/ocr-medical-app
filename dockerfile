FROM python:3.10.8

USER root

RUN apt-get update \
  && apt-get -y install tesseract-ocr \
  && apt-get -y install tk \
  && apt-get -y install ffmpeg libsm6 libxext6 \
  && apt-get -y install xvfb xauth x11-apps \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* 

WORKDIR /app

RUN mkdir /app/templates /app/reports

VOLUME [ "/app/templates", "/app/reports"]

COPY . /app
COPY ./templates /app/templates
COPY ./reports /app/reports
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENV TESSERACT_PATH /usr/bin/tesseract

RUN pip install .

ENTRYPOINT /entrypoint.sh