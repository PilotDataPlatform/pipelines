# File copy and delete
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.9](https://img.shields.io/badge/python-3.9-green?style=for-the-badge)](https://www.python.org/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/pilotdataplatform/upload/CI/develop?style=for-the-badge)](https://github.com/PilotDataPlatform/pipelines/actions/workflows/cicd.yml)


This pipeline scripts provide funcationality for files and folders copy and delete in greenroom and core zone

## Getting Started

This is an example of how you may setting up your service locally. To get a local copy up and running follow these simple example steps.

### Prerequisites

This project is using [Poetry](https://python-poetry.org/docs/#installation) to handle the dependencies.

    curl -sSL https://install.python-poetry.org | python3 -

### Installation & Quick Start

1. Clone the project.

       https://github.com/PilotDataPlatform/pipelines.git

2. Install dependencies.

       poetry install

3. Add environment variables into `.env` in case it's needed. Use `.env.schema` as a reference.

4. run it locally:

File folder copy
 ```
 python3 -m operations copy --source-id 'source folder id where the file copy from' --destination-id 'destination folder id where the file copy to' --project-code 'project_code' --operator 'operator' --job-id 'job id' --session-id 'session id'  --include-ids 'Id of the copied file and folder'

 ```
File folder delete
 ```
 python3 -m operations delete --source-id 'source folder id where the file delete from' --include-ids 'Id of the deleted file and folder' --project-code 'project_code' --operator 'operator' --job-id 'job id' --session-id 'session id'
 ```

### Startup using Docker

This project can also be started using [Docker](https://www.docker.com/get-started/).

1. To build and start the service within the Docker container, run:

       docker compose up

## Resources

* [Pilot Platform API Documentation](https://pilotdataplatform.github.io/api-docs/)
* [Pilot Platform Helm Charts](https://github.com/PilotDataPlatform/helm-charts/)

## Contribution

You can contribute the project in following ways:

* Report a bug.
* Suggest a feature.
* Open a pull request for fixing issues or adding functionality. Please consider
  using [pre-commit](https://pre-commit.com) in this case.
* For general guidelines on how to contribute to the project, please take a look at the [contribution guides](CONTRIBUTING.md).
