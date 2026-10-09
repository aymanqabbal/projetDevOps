import os
import logging
from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("taskflow")

app = Flask(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "taskflow_db"),
    "user": os.getenv("DB_USER", "taskflow_admin"),
    "password": os.getenv("DB_PASSWORD", "taskflow_secret_pass"),
    "connect_timeout": 3
}


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(200) NOT NULL,
                        description TEXT DEFAULT '',
                        category VARCHAR(50) DEFAULT 'General',
                        priority VARCHAR(20) DEFAULT 'Normal',
                        status VARCHAR(20) DEFAULT 'A faire',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
                logger.info("Base de données initialisée avec succès.")
    except Exception as exc:
        logger.warning(f"Initialisation DB différée (connexion non disponible immédiatement) : {exc}")


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TaskFlow DevOps | Gestionnaire de Tâches & Projets</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f4f6f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .navbar-brand { font-weight: 700; letter-spacing: 0.5px; }
        .badge-priority-Haute { background-color: #dc3545; }
        .badge-priority-Normal { background-color: #0d6efd; }
        .badge-priority-Basse { background-color: #6c757d; }
        .badge-status-Terminé { background-color: #198754; }
        .badge-status-En-cours { background-color: #ffc107; color: #212529; }
        .badge-status-A-faire { background-color: #0dcaf0; color: #212529; }
        .card { border-radius: 12px; border: none; box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
        .stat-card { border-left: 4px solid #0d6efd; }
    </style>
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
    <div class="container">
        <a class="navbar-brand d-flex align-items-center gap-2" href="/">
            <span>🚀</span> TaskFlow <span class="badge bg-primary fs-6">DevOps</span>
        </a>
        <div class="d-flex align-items-center gap-3 text-light">
            <span class="badge bg-success">● Système Opérationnel</span>
            <a href="/health" class="btn btn-sm btn-outline-light" target="_blank">Health</a>
            <a href="/ready" class="btn btn-sm btn-outline-info" target="_blank">Ready</a>
            <a href="/tasks" class="btn btn-sm btn-outline-warning" target="_blank">API JSON</a>
        </div>
    </div>
</nav>

<div class="container py-4">
    <div class="row g-3 mb-4">
        <div class="col-md-4">
            <div class="card stat-card p-3">
                <div class="text-muted small">Total des tâches</div>
                <div class="fs-3 fw-bold text-primary">{{ stats.total }}</div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card p-3" style="border-left: 4px solid #ffc107;">
                <div class="text-muted small">Tâches en cours</div>
                <div class="fs-3 fw-bold text-warning">{{ stats.in_progress }}</div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card p-3" style="border-left: 4px solid #198754;">
                <div class="text-muted small">Tâches terminées</div>
                <div class="fs-3 fw-bold text-success">{{ stats.completed }}</div>
            </div>
        </div>
    </div>

    <div class="row g-4">
        <div class="col-lg-4">
            <div class="card p-4">
                <h5 class="fw-bold mb-3">➕ Nouvelle tâche</h5>
                <form method="POST" action="/add">
                    <div class="mb-3">
                        <label class="form-label small fw-semibold">Titre de la tâche *</label>
                        <input name="title" class="form-control" placeholder="ex: Configurer ingress K8s" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label small fw-semibold">Catégorie</label>
                        <select name="category" class="form-select">
                            <option value="DevOps">DevOps & CI/CD</option>
                            <option value="Backend">Backend / API</option>
                            <option value="Infrastructure">Infrastructure (Terraform)</option>
                            <option value="Qualité">Tests & Sécurité</option>
                            <option value="General" selected>Général</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label small fw-semibold">Priorité</label>
                        <select name="priority" class="form-select">
                            <option value="Basse">Basse</option>
                            <option value="Normal" selected>Normal</option>
                            <option value="Haute">Haute</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label small fw-semibold">Description (optionnelle)</label>
                        <textarea name="description" class="form-control" rows="2" placeholder="Détails complémentaires..."></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary w-100 fw-semibold">Créer la tâche</button>
                </form>
            </div>
        </div>

        <div class="col-lg-8">
            <div class="card p-4">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="fw-bold m-0">📋 Liste des tâches du projet</h5>
                    <span class="text-muted small">{{ tasks|length }} élément(s)</span>
                </div>

                {% if not tasks %}
                <div class="alert alert-light text-center border py-4 my-2">
                    <p class="text-muted m-0">Aucune tâche enregistrée pour le moment. Créez-en une à gauche !</p>
                </div>
                {% endif %}

                <div class="list-group list-group-flush">
                    {% for task in tasks %}
                    <div class="list-group-item px-0 py-3 d-flex justify-content-between align-items-center">
                        <div>
                            <div class="d-flex align-items-center gap-2 mb-1">
                                <span class="fw-bold fs-6">{{ task.title }}</span>
                                <span class="badge bg-secondary small">{{ task.category }}</span>
                                <span class="badge badge-priority-{{ task.priority }}">{{ task.priority }}</span>
                                {% set status_class = task.status|replace(' ', '-') %}
                                <span class="badge badge-status-{{ status_class }}">{{ task.status }}</span>
                            </div>
                            {% if task.description %}
                            <div class="text-muted small mb-1">{{ task.description }}</div>
                            {% endif %}
                            <div class="text-muted small" style="font-size: 0.75rem;">Créée le : {{ task.created_at }}</div>
                        </div>
                        <div class="d-flex gap-2">
                            {% if task.status != 'Terminé' %}
                            <form method="POST" action="/tasks/{{ task.id }}/status" class="d-inline">
                                <input type="hidden" name="status" value="{% if task.status == 'A faire' %}En cours{% else %}Terminé{% endif %}">
                                <button class="btn btn-sm btn-outline-success">
                                    {% if task.status == 'A faire' %}▶ Commencer{% else %}✓ Clôturer{% endif %}
                                </button>
                            </form>
                            {% endif %}
                            <form method="POST" action="/tasks/{{ task.id }}/delete" class="d-inline">
                                <button class="btn btn-sm btn-outline-danger">🗑</button>
                            </form>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>
</body>
</html>
"""


@app.route("/")
def home():
    tasks_list = []
    stats = {"total": 0, "in_progress": 0, "completed": 0}
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, title, description, category, priority, status,
                           TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI') as created_at
                    FROM tasks
                    ORDER BY id DESC
                """)
                tasks_list = cursor.fetchall()
                stats["total"] = len(tasks_list)
                stats["in_progress"] = sum(1 for t in tasks_list if t["status"] == "En cours")
                stats["completed"] = sum(1 for t in tasks_list if t["status"] == "Terminé")
    except Exception as exc:
        logger.error(f"Erreur lors de la récupération des tâches : {exc}")

    return render_template_string(HTML_TEMPLATE, tasks=tasks_list, stats=stats)


@app.route("/health")
def health():
    return jsonify({
        "status": "UP",
        "service": "taskflow",
        "environment": os.getenv("FLASK_ENV", "production")
    }), 200


@app.route("/ready")
def ready():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchone()
        return jsonify({"status": "READY", "database": "connected"}), 200
    except Exception as exc:
        logger.error(f"Échec de la sonde de préparation DB: {exc}")
        return jsonify({"status": "NOT_READY", "error": str(exc)}), 503


@app.route("/tasks", methods=["GET"])
def get_tasks():
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT id, title, description, category, priority, status, created_at FROM tasks ORDER BY id")
                rows = cursor.fetchall()
                # Compatibilité : inclure 'completed' booléen pour les anciens scripts de validation
                formatted = [
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "description": row["description"],
                        "category": row["category"],
                        "priority": row["priority"],
                        "status": row["status"],
                        "completed": row["status"] == "Terminé",
                        "created_at": str(row["created_at"])
                    }
                    for row in rows
                ]
                return jsonify(formatted), 200
    except Exception as exc:
        logger.error(f"Erreur get_tasks: {exc}")
        return jsonify({"error": "Erreur base de données", "details": str(exc)}), 500


@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title") or (request.json.get("title") if request.is_json else None)
    if not title or not title.strip():
        return "Titre obligatoire", 400

    category = request.form.get("category", "General") if not request.is_json else request.json.get("category", "General")
    priority = request.form.get("priority", "Normal") if not request.is_json else request.json.get("priority", "Normal")
    description = request.form.get("description", "") if not request.is_json else request.json.get("description", "")

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO tasks (title, description, category, priority, status)
                    VALUES (%s, %s, %s, %s, 'A faire')
                    """,
                    (title.strip(), description.strip(), category, priority)
                )
                conn.commit()

        if request.is_json:
            return jsonify({"message": "Tâche ajoutée avec succès"}), 201

        return redirect(url_for("home"))
    except Exception as exc:
        logger.error(f"Erreur add_task: {exc}")
        return f"Erreur lors de l'ajout: {exc}", 500


@app.route("/tasks/<int:task_id>/status", methods=["POST"])
def update_task_status(task_id):
    new_status = request.form.get("status") or (request.json.get("status") if request.is_json else None)
    if not new_status:
        return "Statut requis", 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE tasks SET status = %s WHERE id = %s", (new_status, task_id))
                conn.commit()

        if request.is_json:
            return jsonify({"message": "Statut mis à jour"}), 200
        return redirect(url_for("home"))
    except Exception as exc:
        logger.error(f"Erreur update_task_status: {exc}")
        return f"Erreur: {exc}", 500


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task_form(task_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
                conn.commit()
        return redirect(url_for("home"))
    except Exception as exc:
        logger.error(f"Erreur delete_task_form: {exc}")
        return f"Erreur: {exc}", 500


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
                conn.commit()
        return jsonify({"message": "Tâche supprimée avec succès"}), 200
    except Exception as exc:
        logger.error(f"Erreur delete_task: {exc}")
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)