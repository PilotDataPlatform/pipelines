pipeline {
    agent { label 'master || small' }
    environment {
      imagename_dcmedit_dev = "ghcr.io/pilotdataplatform/pipelines/dcmedit"
      imagename_filecopy_dev = "ghcr.io/pilotdataplatform/pipelines/filecopy"
      imagename_bids_validator_dev = "ghcr.io/pilotdataplatform/pipelines/bids-validator"
      imagename_dcmedit_staging = "ghcr.io/pilotdataplatform/pipelines/dcmedit"
      imagename_filecopy_staging = "ghcr.io/pilotdataplatform/pipelines/filecopy"
      imagename_bids_validator_staging = "ghcr.io/pilotdataplatform/pipelines/bids-validator"
      commit = sh(returnStdout: true, script: 'git describe --always').trim()
      registryCredential = 'pilot-ghcr'
      registryURLBase = "https://ghcr.io"
      registryURL = "https://github.com/PilotDataPlatform/pipelines.git" 
      dockerImage = ''
    }

    stages {

    stage('Git clone for dev') {
        when {branch "develop"}
        steps{
          script {
          git branch: "develop",
              url: "$registryURL",
              credentialsId: 'lzhao'
            }
        }
    }

    stage('DEV Build and push dcmedit image') {
      when {
          allOf {
              changeset "dcmedit/**"
              branch "develop"
            }
      }
      steps{
        script {
          withCredentials(
            docker.withRegistry("$registryURLBase", registryCredential) {
                customImage = docker.build("$imagename_dcmedit_dev:edge", "./dcmedit")
                customImage.push()
            }
          }
        }
      }
    stage('DEV Remove dcmedit image') {
      when {
          allOf {
              changeset "dcmedit/**"
              branch "develop"
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
              branch "develop"
            }
      }
      steps{
        script {
          withCredentials(
            docker.withRegistry("$registryURLBase", registryCredential) {
                customImage = docker.build("$imagename_filecopy_dev:edge", "--no-cache ./filecopy")
                customImage.push()
            }         
          }
        }
      }

    stage('DEV Remove filecopy image') {
      when {
          allOf {
              changeset "filecopy/**"
              branch "develop"
            }
      }
      steps{
        sh "docker rmi $imagename_filecopy_dev:edge"
      }
    }

    stage('DEV Building and push bids-validator') {
      when {
          allOf {
              changeset "bids-validator/**"
              branch "develop"
            }
      }
      steps{
        script {
          withCredentials(
            docker.withRegistry("$registryURLBase", registryCredential) {
                customImage = docker.build("$imagename_bids_validator_dev:edge", "./bids-validator")
                customImage.push()
            }
          }
        }
      }

    stage('DEV Remove bids-validator image') {
      when {
          allOf {
              changeset "bids-validator/**"
              branch "develop"
            }
      }
      steps{
        sh "docker rmi $imagename_bids_validator_dev:edge"
      }
    }
/**        
    stage('Git clone staging') {
        when {branch "main"}
        steps{
          script {
          git branch: "main",
              url: "$registryURL",
              credentialsId: 'lzhao'
            }
        }
    }

    stage('STAGING Building and push dcmedit image') {
      when {
          allOf {
              changeset "dcmedit/**"
              branch "main"
            }
      }
      steps{
        script {
          withCredentials(
            docker.withRegistry("$registryURLBase", registryCredential) {
                customImage = docker.build("$imagename_dcmedit_staging:stable", "./dcmedit")
                customImage.push()
            }
          }
        }
      }

    stage('STAGING Remove dcmedit image') {
      when {
          allOf {
              changeset "dcmedit/**"
              branch "main"
            }
      }
      steps{
        sh "docker rmi $imagename_dcmedit_staging:stable"
      }
    }

    stage('STAGING Building and push filecopy image') {
      when {
          allOf {
              changeset "filecopy/**"
              branch "main"
            }
      }
      steps{
        script {
          withCredentials(
            docker.withRegistry("$registryURLBase", registryCredential) {
                customImage = docker.build("$imagename_filecopy_staging:stable", "./filecopy")
                customImage.push()
            }
          }
        }
      }


    stage('STAGING Remove filecopy image') {
      when {
          allOf {
              changeset "filecopy/**"
              branch "main"
            }
      }
      steps{
        sh "docker rmi $imagename_filecopy_staging:stable"
      }
    }
    stage('STAGING Building and push bids-validator image') {
      when {
          allOf {
              changeset "bids-validator/**"
              branch "main"
            }
      }
      steps{
        script {
          withCredentials(
            docker.withRegistry("$registryURLBase", registryCredential) {
                customImage = docker.build(" $imagename_bids_validator_staging:stable", "./bids-validator")
                customImage.push()
            }
          }
        }
      }
    stage('STAGING Remove bids-validator image') {
      when {
          allOf {
              changeset "bids-validator/**"
              branch "main"
            }
      }
      steps{
        sh "docker rmi $imagename_bids_validator_staging:stable"
      }
    }
**/    
  }

  post {
    failure {
        slackSend color: '#FF0000', message: "Build Failed! - ${env.JOB_NAME} ${env.commit}  (<${env.BUILD_URL}|Open>)", channel: 'jenkins-dev-staging-monitor'
    }
  }

}
