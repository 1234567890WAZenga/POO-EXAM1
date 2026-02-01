FROM python:3.11-slim

# Variables d'environnement Python (bonnes pratiques)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Répertoire de travail racine
WORKDIR /app

# Dépendances système minimales
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copier les dépendances en premier (cache Docker)
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copier tout le projet
COPY . .

# Se placer explicitement dans le dossier Django
WORKDIR /app/web

# Port Django
EXPOSE 8000

# Lancement du serveur Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]