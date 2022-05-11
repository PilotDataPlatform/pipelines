FROM python:3.7-buster
LABEL maintainer="Samantha Zhang <szhang@indocresearch.org>"

RUN apt-get update -y && apt-get install -y rsync python3-pip python3-dev build-essential \
    default-jre-headless locales nodejs npm && rm -rf /var/lib/apt/lists/*
RUN pip3 install --upgrade pip

RUN npm install -g bids-validator@1.8.0

COPY ./ /dataset-validate
WORKDIR /dataset-validate
RUN chmod 555 -R /dataset-validate
COPY poetry.lock pyproject.toml ./
RUN pip install --no-cache-dir poetry==1.1.12
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-root --no-interaction
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
RUN ls
