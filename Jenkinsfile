pipeline {
    agent { label 'master || small' }
    environment {
      imagename_dcmedit_dev = "registry-gitlab.indocresearch.org/pilot/internal_pipelines/dcmedit-dev"
      imagename_filecopy_dev = "registry-gitlab.indocresearch.org/pilot/internal_pipelines/filecopy-dev"
      imagename_bids_validator_dev = "registry-gitlab.indocresearch.org/pilot/internal_pipelines/bids-validator-dev"
      imagename_dcmedit_staging = "registry-gitlab.indocresearch.org/pilot/internal_pipelines/dcmedit"
      imagename_filecopy_staging = "registry-gitlab.indocresearch.org/pilot/internal_pipelines/filecopy"
      imagename_bids_validator_staging = "registry-gitlab.indocresearch.org/pilot/internal_pipelines/bids-validator"
      commit = sh(returnStdout: true, script: 'git describe --always').trim()
      registryCredential = 'pilot-gitlab-registry'
      dockerImage = ''
    }

    stages {

    stage('Git clone for dev') {
        when {branch "k8s-dev"}
        steps{
          script {
          git branch: "k8s-dev",
              url: 'https://git.indocresearch.org/pilot/internal_pipelines.git',
              credentialsId: 'lzhao'
            }
        }
    }

    stage('DEV Build and push dcmedit image') {
      when {
          allOf {
              changeset "dcmedit/**"
              branch "k8s-dev"
            }
      }
      steps{
        script {
          withCredentials([usernamePassword(credentialsId:'readonly', usernameVariable: 'PIP_USERNAME', passwordVariable: 'PIP_PASSWORD')]) {
            docker.withRegistry('https://registry-gitlab.indocresearch.org', registryCredential) {
                customImage = docker.build("registry-gitlab.indocresearch.org/pilot/internal_pipelines/dcmedit-dev:v0.1",  "--build-arg pip_username=${PIP_USERNAME} --build-arg pip_password=${PIP_PASSWORD} --add-host git.indocresearch.org:10.4.3.151 ./dcmedit")
                customImage.push()
            }
          }
      }
    }
    }
    stage('DEV Remove dcmedit image') {
      when {
          allOf {
              changeset "dcmedit/**"
              branch "k8s-dev"
            }
      }
      steps{
        sh "docker rmi $imagename_dcmedit_dev:v0.1"
      }
    }

    stage('DEV Building and push filecopy') {
      when {
          allOf {
              changeset "filecopy/**"
              branch "k8s-dev"
            }
      }
      steps{
        script {
          withCredentials([usernamePassword(credentialsId:'readonly', usernameVariable: 'PIP_USERNAME', passwordVariable: 'PIP_PASSWORD')]) {
            docker.withRegistry('https://registry-gitlab.indocresearch.org', registryCredential) {
                customImage = docker.build("registry-gitlab.indocresearch.org/pilot/internal_pipelines/filecopy-dev:v0.1", "--no-cache --add-host git.indocresearch.org:10.4.3.151 ./filecopy")
                customImage.push()
            }
          }
        }
      }
    }

    stage('DEV Remove filecopy image') {
      when {
          allOf {
              changeset "filecopy/**"
              branch "k8s-dev"
            }
      }
      steps{
        sh "docker rmi $imagename_filecopy_dev:v0.1"
      }
    }

    stage('DEV Building and push bids-validator') {
      when {
          allOf {
              changeset "bids-validator/**"
              branch "k8s-dev"
            }
      }
      steps{
        script {
          withCredentials([usernamePassword(credentialsId:'readonly', usernameVariable: 'PIP_USERNAME', passwordVariable: 'PIP_PASSWORD')]){
            docker.withRegistry('https://registry-gitlab.indocresearch.org', registryCredential) {
                customImage = docker.build("registry-gitlab.indocresearch.org/pilot/internal_pipelines/bids-validator-dev:v0.1", " --add-host git.indocresearch.org:10.4.3.151 ./bids-validator")
                customImage.push()
            }
          }
        }
      }
    }

    stage('DEV Remove bids-validator image') {
      when {
          allOf {
              changeset "bids-validator/**"
              branch "k8s-dev"
            }
      }
      steps{
        sh "docker rmi $imagename_bids_validator_dev:v0.1"
      }
    }
    stage('Git clone staging') {
        when {branch "k8s-staging"}
        steps{
          script {
          git branch: "k8s-staging",
              url: 'https://git.indocresearch.org/pilot/internal_pipelines.git',
              credentialsId: 'lzhao'
            }
        }
    }

    stage('STAGING Building and push dcmedit image') {
      when {
          allOf {
              changeset "dcmedit/**"
              branch "k8s-staging"
            }
      }
      steps{
        script {
          withCredentials([usernamePassword(credentialsId:'readonly', usernameVariable: 'PIP_USERNAME', passwordVariable: 'PIP_PASSWORD')]) {
            docker.withRegistry('https://registry-gitlab.indocresearch.org', registryCredential) {
                customImage = docker.build("registry-gitlab.indocresearch.org/pilot/internal_pipelines/dcmedit:v0.1", "--build-arg pip_username=${PIP_USERNAME} --build-arg pip_password=${PIP_PASSWORD} --add-host git.indocresearch.org:10.4.3.151 ./dcmedit")
                customImage.push()
            }
          }
        }
      }
    }

    stage('STAGING Remove dcmedit image') {
      when {
          allOf {
              changeset "dcmedit/**"
              branch "k8s-staging"
            }
      }
      steps{
        sh "docker rmi $imagename_dcmedit_staging:v0.1"
      }
    }

    stage('STAGING Building and push filecopy image') {
      when {
          allOf {
              changeset "filecopy/**"
              branch "k8s-staging"
            }
      }
      steps{
        script {
          withCredentials([usernamePassword(credentialsId:'readonly', usernameVariable: 'PIP_USERNAME', passwordVariable: 'PIP_PASSWORD')]) {
            docker.withRegistry('https://registry-gitlab.indocresearch.org', registryCredential) {
                customImage = docker.build("registry-gitlab.indocresearch.org/pilot/internal_pipelines/filecopy:v0.1", "--build-arg REGISTRY_USERNAME=${PIP_USERNAME} --build-arg REGISTRY_PASSWORD=${PIP_PASSWORD} --add-host git.indocresearch.org:10.4.3.151 ./filecopy")
                customImage.push()
            }
          }
        }
      }
    }

    stage('STAGING Remove filecopy image') {
      when {
          allOf {
              changeset "filecopy/**"
              branch "k8s-staging"
            }
      }
      steps{
        sh "docker rmi $imagename_filecopy_staging:v0.1"
      }
    }
    stage('STAGING Building and push bids-validator image') {
      when {
          allOf {
              changeset "bids-validator/**"
              branch "k8s-staging"
            }
      }
      steps{
        script {
          withCredentials([usernamePassword(credentialsId:'readonly', usernameVariable: 'PIP_USERNAME', passwordVariable: 'PIP_PASSWORD')]) {
            docker.withRegistry('https://registry-gitlab.indocresearch.org', registryCredential) {
                customImage = docker.build("registry-gitlab.indocresearch.org/pilot/internal_pipelines/bids-validator:v0.1", "--build-arg pip_username=${PIP_USERNAME} --build-arg pip_password=${PIP_PASSWORD} --add-host git.indocresearch.org:10.4.3.151 ./bids-validator")
                customImage.push()
            }
        }
      }
    }
    }

    stage('STAGING Remove bids-validator image') {
      when {
          allOf {
              changeset "bids-validator/**"
              branch "k8s-staging"
            }
      }
      steps{
        sh "docker rmi $imagename_bids_validator_staging:v0.1"
      }
    }
  }

  post {
    failure {
        slackSend color: '#FF0000', message: "Build Failed! - ${env.JOB_NAME} ${env.commit}  (<${env.BUILD_URL}|Open>)", channel: 'jenkins-dev-staging-monitor'
    }
  }

}
