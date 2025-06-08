# DriverScore Docker Deployment

Ce guide explique comment démarrer DriverScore en utilisant Docker et Docker Compose.

## 🎯 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   React + Nginx │◄──►│   FastAPI       │◄──►│   PostgreSQL    │
│   Port 3000     │    │   Port 8000     │    │   + PostGIS     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Démarrage rapide

### Option 1: Stack complète (recommandé)
```bash
./start-fullstack.sh
# ou
docker-compose up --build
```

### Option 2: Backend seulement
```bash
./start-backend.sh
# ou  
docker-compose up --build db api
```

### Option 3: Frontend seulement
```bash
./start-frontend.sh
# ou
docker-compose up --build web
```

## 📋 Prérequis

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB espace disque

## 🔧 Configuration

### Variables d'environnement

Créez un fichier `.env` pour personnaliser la configuration :

```bash
# Database
POSTGRES_DB=gpu_user
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Backend
SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://postgres:postgres@db:5432/gpu_user
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Frontend
VITE_API_URL=http://localhost:8000
```

### Ports utilisés

- **3000**: Frontend React/Nginx
- **8000**: Backend FastAPI
- **5432**: PostgreSQL + PostGIS

## 🗄️ Base de données

### Initialisation automatique
- Le schema SQL est automatiquement chargé au démarrage
- Les migrations Alembic sont exécutées via `prestart.sh`
- PostGIS est pré-installé et configuré

### Accès direct à la DB
```bash
docker exec -it driverscore-postgres psql -U postgres -d gpu_user
```

### Sauvegarde/Restauration
```bash
# Sauvegarde
docker exec driverscore-postgres pg_dump -U postgres gpu_user > backup.sql

# Restauration  
docker exec -i driverscore-postgres psql -U postgres gpu_user < backup.sql
```

## 🔍 Debugging

### Logs des services
```bash
# Tous les services
docker-compose logs -f

# Service spécifique
docker-compose logs -f api
docker-compose logs -f db
docker-compose logs -f web
```

### Accès aux conteneurs
```bash
# Backend
docker exec -it driverscore-api bash

# Database
docker exec -it driverscore-postgres bash

# Frontend
docker exec -it driverscore-web sh
```

### Health checks
```bash
# API sanity check
curl http://localhost:8000/docs

# Database status
docker exec driverscore-postgres pg_isready -U postgres
```

## 🔄 Développement

### Rechargement en temps réel

Pour le développement avec hot-reload, montez les volumes :

```yaml
# Dans docker-compose.override.yml
services:
  api:
    volumes:
      - ./DriverScore_backend-main:/app
    environment:
      - ENV_FOR_DYNACONF=docker
```

### Rebuild après modifications
```bash
# Rebuild complet
docker-compose down && docker-compose up --build

# Rebuild service spécifique
docker-compose up --build api
```

## 🚨 Troubleshooting

### Problèmes courants

1. **Port déjà utilisé**
   ```bash
   # Vérifier les ports
   lsof -i :3000 -i :8000 -i :5432
   
   # Arrêter les services
   docker-compose down
   ```

2. **Problèmes de permissions PostgreSQL**
   ```bash
   # Supprimer le volume et recommencer
   docker-compose down -v
   docker volume rm driverscore_postgres_data
   ```

3. **Erreurs de build**
   ```bash
   # Clean rebuild
   docker-compose down --rmi all
   docker-compose up --build --force-recreate
   ```

4. **Migrations Alembic échouent**
   ```bash
   # Exécuter manuellement
   docker exec -it driverscore-api alembic upgrade head
   ```

## 📚 URLs utiles

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs  
- **API Redoc**: http://localhost:8000/redoc
- **API OpenAPI**: http://localhost:8000/openapi.json

## 🛠️ Commandes utiles

```bash
# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v

# Voir l'état des services
docker-compose ps

# Mettre à jour les images
docker-compose pull

# Nettoyer Docker
docker system prune -a
```