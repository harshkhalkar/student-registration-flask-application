pipeline {
    agent any

    stages {
        stage('Pull Files') {
            steps {
                echo 'Start Stage 1'
                checkout([$class: 'GitSCM',
                    branches: [[name: '*/main']],
                    extensions: [],
                    userRemoteConfigs: [[url: 'https://github.com/harshkhalkar/student-registration-flask-application.git']]
                ])
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing docker & docker-compose'
                sh 'sudo apt update -y'
                sh 'sudo apt install docker.io -y'
                sh '''
                    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
                    -o /usr/local/bin/docker-compose
                '''
                sh 'sudo chmod +x /usr/local/bin/docker-compose'
                echo 'Verify Installation'
                sh 'docker --version && docker-compose --version'
                sh 'sudo systemctl start docker'
            }
        }

        stage('Build') {
            steps {
                echo 'run docker-compose'
                sh 'sudo docker-compose up -d'
            }
        }

        stage('Test') {
            steps {
                echo 'Hello World'
                sh 'sudo docker ps'
                sh 'curl localhost:5000'
                sh 'sudo docker exec pyapp ls -l'
                sh 'sudo docker exec pyapp ls -l tests'
                sh 'sudo docker exec pyapp python3 -m unittest discover -s tests -t .'
            }
        }
        
        stage('Cleanup') {
    steps {
        echo 'Cleaning up Docker resources'
        sh '''
            sudo docker-compose down --volumes --remove-orphans
            sudo docker image prune -f
            IMAGE_IDS=$(sudo docker images -q)
            if [ -n "$IMAGE_IDS" ]; then
              sudo docker rmi -f $IMAGE_IDS
            else
              echo "No images to remove"
            fi
        '''
    }
}

        stage('Deploy') {
            steps {
                script {
                    sshagent(['5db86cd4-3324-4473-bf9b-f2f9f5e397d6']) {
                        sh '''
                            ssh -o StrictHostKeyChecking=no ubuntu@54.224.69.173 << 'ENDSSH'
                            sudo apt update && sudo apt install docker.io -y
                            sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
                            -o /usr/local/bin/docker-compose
                            sudo chmod +x /usr/local/bin/docker-compose
                            sudo systemctl start docker
                            mkdir -p /pyapp
                            cd /pyapp
                            git init
                            git pull https://github.com/harshkhalkar/student-registration-flask-application.git
                            sudo docker --version && sudo docker-compose --version
                            rm -rf kubernetes LICENSE
                            sudo docker-compose up -d
ENDSSH
                        '''
                    }
                }
            }
        }
    }
}
