# 🚀 TaskFlow DevOps

Plateforme complète de gestion de tâches et de projets DevOps, conteneurisée et orchestrée avec une chaîne CI/CD automatisée de bout en bout (**Docker**, **Jenkins**, **Kubernetes**, **Terraform**).

---

## 📋 Présentation du Projet

**TaskFlow** est une application web moderne développée en **Python Flask** connectée à une base de données relationnelle **PostgreSQL**. Elle permet de gérer le cycle de vie de tâches techniques (catégorisation, priorisation, statuts d'avancement, tableau de bord avec indicateurs clés) tout en exposant des sondes d'observabilité (`/health`, `/ready`) pour les orchestrateurs de conteneurs.

Ce projet implémente l'ensemble des bonnes pratiques DevOps :
- **Infrastructure as Code (IaC)** avec **Terraform** pour le provisionnement des environnements.
- **Conteneurisation sécurisée** avec **Docker** (utilisateur non-root, serveur WSGI Gunicorn, healthchecks).
- **Intégration & Déploiement Continus (CI/CD)** automatisés avec **Jenkins**.
- **Orchestration Cloud-Native** sur **Kubernetes** avec gestion des volumes persistants, secrets, sondes de santé et politiques de tolérance aux pannes.

---

## 🛠️ Stack Technologique

| Domaine | Outil / Technologie | Rôle |
|---|---|---|
| **Backend & API** | Python 3.12 / Flask / Gunicorn | Serveur applicatif & API REST |
| **Base de Données** | PostgreSQL 16 (Alpine) | Persistance des données relationnelles |
| **Tests & Qualité** | Pytest / Unittest Mocks | Validation automatisée et tests unitaires |
| **Conteneurisation** | Docker / Docker Hub | Packaging et registre d'images |
| **CI/CD** | Jenkins Pipeline (Jenkinsfile) | Automatisation du cycle Build → Test → Push → Deploy |
| **Orchestration** | Kubernetes (K8s) | Déploiement résilient, réplicas, services & sondes |
| **IaC** | Terraform (VirtualBox Provider) | Provisionnement des machines virtuelles d'infrastructure |
| **Gestion de versions** | Git & GitHub | Suivi de versions et déclencheurs de build |

---

## 🔄 Pipeline CI/CD

Le pipeline déclaratif Jenkins orchestre les étapes suivantes à chaque modification de code :

```
GitHub Push (main) 
    ↳ 1. Checkout SCM
    ↳ 2. Code Quality & Pytest (Exécution des tests avec mocks)
    ↳ 3. Docker Build (Tag avec numéro de build et latest)
    ↳ 4. Docker Push (Publication sécurisée sur Docker Hub)
    ↳ 5. Kubernetes Deploy (Mise à jour d'image & vérification du rollout)
```

---

## 🌿 Stratégie Git & Branches

Le projet suit un workflow basé sur deux branches principales :
- `main` : Branche de production contenant les versions stables et validées.
- `dev` : Branche de développement et d'intégration des nouvelles fonctionnalités.

**Flux de contribution recommandé :**
1. Création d'une branche de travail à partir de `dev`.
2. Validation locale des tests unitaires (`pytest app/test_app.py`).
3. Soumission d'une **Pull Request (PR)** de `dev` vers `main`.
4. Déclenchement automatique du pipeline Jenkins sur la branche `main`.

---

## ☸️ Architecture Kubernetes

Le dossier `kubernetes/` contient les manifestes nécessaires au bon fonctionnement de l'application :

- **`configmap.yaml`** : Configuration non sensible (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`).
- **`secret.yaml`** : Identifiants sensibles chiffrés (`POSTGRES_PASSWORD`).
- **`pvc.yaml`** : `PersistentVolumeClaim` (1 Gio) pour assurer la persistance des données PostgreSQL.
- **`postgres.yaml`** : `Deployment` (PostgreSQL 16 Alpine) et `Service` ClusterIP interne (port 5432).
- **`app-deployment.yaml`** : Déploiement applicatif TaskFlow à haute disponibilité (2 réplicas) avec :
  - **Liveness Probe** (`GET /health`)
  - **Readiness Probe** (`GET /ready`)
  - **Ressources allouées** (`requests` et `limits` CPU / RAM)
- **`app-service.yaml`** : Exposition externe via un `Service NodePort` accessible sur le port **30080**.

---

## 🌐 Endpoints de l'Application

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/` | Tableau de bord web interactif & statistiques |
| `GET` | `/health` | Sonde Liveness (état du processus Flask) |
| `GET` | `/ready` | Sonde Readiness (état de la connexion DB) |
| `GET` | `/tasks` | Liste des tâches au format JSON |
| `POST` | `/add` | Création d'une nouvelle tâche |
| `POST` | `/tasks/<id>/status` | Mise à jour du statut d'une tâche |
| `DELETE`| `/tasks/<id>` | Suppression définitive d'une tâche |

---

## 🚀 Démarrage & Exécution Locale

### 1. Exécution des tests unitaires
```bash
python -m unittest discover -s app -p "test_*.py" -v
```
*ou avec pytest :*
```bash
pip install -r app/requirements.txt
pytest app/test_app.py -v
```

### 2. Lancement avec Docker
```bash
# Construction de l'image
docker build -t taskflow-app:latest .

# Lancement du conteneur
docker run -p 5000:5000 -e DB_HOST=localhost taskflow-app:latest
```

### 3. Déploiement sur Kubernetes
```bash
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secret.yaml
kubectl apply -f kubernetes/pvc.yaml
kubectl apply -f kubernetes/postgres.yaml
kubectl apply -f kubernetes/app-deployment.yaml
kubectl apply -f kubernetes/app-service.yaml
```

Vérifier le statut du déploiement :
```bash
kubectl get pods,svc,pvc
```

**Accès à l'application déployée :**
```
http://<IP_DU_NOEUD_KUBERNETES>:30080
```

---

## 🏗️ Infrastructure as Code (Terraform)

Le dossier `infrastructure/terraform/` permet de provisionner l'environnement de virtualisation sous VirtualBox :
- **`main.tf`** : Déclaration des ressources pour les serveurs Jenkins et Kubernetes.
- **`variables.tf`** : Paramétrage dynamique des vCPUs, de la mémoire et des identifiants des VMs.
- **`outputs.tf`** : Restitution des métadonnées des machines virtuelles créées.

```bash
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```