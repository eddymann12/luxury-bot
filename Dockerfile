# Bruk en offisiell Python-runtime som base
FROM python:3.11-slim

# Sett arbeidskatalog
WORKDIR /app

# Kopier alle filene fra repoet inn i containeren
COPY . .

# Installer nødvendige Python-avhengigheter
RUN pip install --upgrade pip && pip install -r requirements.txt

# Sett miljøvariabler for å unngå buffering
ENV PYTHONUNBUFFERED=1

# Kjør programmet
CMD ["python", "main.py"]
