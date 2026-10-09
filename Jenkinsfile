pipeline {
    agent any

    environment {
        IMAGE_NAME = "aymanqabbal/taskflow-app"
        GIT_REPO_URL = "https://github.com/aymanqabbal/projetDevOps.git"
        GIT_BRANCH = "main"
        K8S_DEPLOYMENT = "taskflow-deployment"
        K8S_CONTAINER = "taskflow-app"
    }

    stages {
        stage('Checkout SCM') {
            steps {
                git branch: env.GIT_BRANCH,
                    url: env.GIT_REPO_URL
            }
        }

        stage('Code Quality & Tests') {
            steps {
                sh '''
                    echo "=== Vérification de la syntaxe et exécution des tests unitaires ==="
                    python3 -m pip install --upgrade pip
                    pip3 install -r app/requirements.txt
                    pytest app/test_app.py -v
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    echo "=== Construction de l'image Docker ==="
                    docker build -t $IMAGE_NAME:$BUILD_NUMBER -t $IMAGE_NAME:latest .
                '''
            }
        }

        stage('Docker Push') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    sh '''
                        echo "=== Connexion Docker Hub et Publication ==="
                        echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push $IMAGE_NAME:$BUILD_NUMBER
                        docker push $IMAGE_NAME:latest
                    '''
                }
            }
        }

        stage('Kubernetes Deploy') {
            steps {
                sh '''
                    echo "=== Déploiement sur le cluster Kubernetes ==="
                    kubectl apply -f kubernetes/
                    kubectl set image deployment/$K8S_DEPLOYMENT $K8S_CONTAINER=$IMAGE_NAME:$BUILD_NUMBER
                    kubectl rollout status deployment/$K8S_DEPLOYMENT --timeout=120s
                '''
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo "Pipeline TaskFlow terminé avec succès !"
        }
        failure {
            echo "Échec du pipeline TaskFlow. Vérifiez les logs des étapes précédentes."
        }
    }
}