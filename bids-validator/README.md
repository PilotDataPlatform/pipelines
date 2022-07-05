# BIDS Validator
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.9](https://img.shields.io/badge/python-3.9-green?style=for-the-badge)](https://www.python.org/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/pilotdataplatform/upload/CI/develop?style=for-the-badge)](https://github.com/PilotDataPlatform/pipelines/actions/workflows/cicd.yml)

### Service Description

This pipeline scripts provide functionality to validate dataset files against Brain Imaging Data Structure

## Built With

 - [poetry](https://python-poetry.org/): python package management

 - [docker](https://docker.com): Docker is a set of platform as a service products that use OS-level virtualization to deliver software in packages called containers

## Getting Started

This is an example of how you may setting up your service locally. To get a local copy up and running follow these simple example steps.

### Prerequisites

 1. The project is using poetry to handle the package. **Note here the poetry must install globally not in the anaconda virtual environment**

 ```
 pip install poetry
 ```

 2. add the precommit package:

 ```
 pip3 install pre_commit
 ```

### Installation

 1. git clone the project:
 ```
 git clone https://github.com/PilotDataPlatform/pipelines.git
 ```

 2. install the package:
 ```
 poetry install
 ```

 3. create the `.env` file from `.env.schema`

 4. install bids-validator Command line version
 ```
 npm install -g bids-validator
 ```

 5. run it locally:
 ```
 python validate_dataset.py -d {dataset-id} -env dev -refresh {refresh token} -access {access_token}
 ```

### Dockerizing

To wrap up the service into a docker container, run following command:

```
docker build .
```


## Resources

* [Helm Chart](https://github.com/PilotDataPlatform/helm-charts/)

## Contribution

You can contribute the project in following ways:

* Report a bug
* Suggest a feature
* Open a pull request for fixing issues or developing plugins
