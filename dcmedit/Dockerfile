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

FROM ubuntu:18.04
LABEL maintainer="Shuai Liang <sliang@indocresearch.org>"

ARG pip_username
ARG pip_password

RUN sed 's/main$/main universe/' -i /etc/apt/sources.list
RUN apt-get update && apt-get install -y python3-pip python3-dev build-essential \
    default-jre-headless locales && rm -rf /var/lib/apt/lists/*
RUN pip3 install --upgrade pip
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
COPY ./ /dcm
RUN PIP_USERNAME=$pip_username PIP_PASSWORD=$pip_password pip3 install -r /dcm/scripts/requirements.txt  -r /dcm/scripts/internal_requirements.txt
RUN chmod 555 -R /dcm
WORKDIR /dcm
