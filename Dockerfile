FROM python:3.13.1-slim

WORKDIR /usr/app/src

ENV PYTHONUNBUFFERED=1

RUN apt-get -y update && apt-get install --no-install-recommends -y binutils libproj-dev gdal-bin wget &&  \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip && python -m pip install --no-cache-dir -r requirements.txt

COPY . ./
