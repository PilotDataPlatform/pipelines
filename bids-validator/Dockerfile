# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with this program.
# If not, see http://www.gnu.org/licenses/.
FROM python:3.9-buster
LABEL maintainer="Samantha Zhang <szhang@indocresearch.org>"

RUN apt-get update -y && apt-get install -y rsync python3-pip python3-dev build-essential \
    default-jre-headless locales nodejs npm && rm -rf /var/lib/apt/lists/*

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
