# TICK'IN — Chatbot de Signalement de Problèmes Informatiques

Plateforme de signalement et de gestion des incidents informatiques pour le **Centre Informatique de l'UGANC** (Université Gamal Abdel Nasser de Conakry).

## Architecture

```
┌───────────────────────────────────────────────────────────┐
│                 Frontend (Vue 3 + Vite)                   │
│                 localhost:5173                            │
└─────────────────────────────┬─────────────────────────────┘
                              │ HTTP REST + WebSocket
                              ▼
┌─────────────────────────────┴─────────────────────────────┐
│              Backend (FastAPI — Python 3.11)              │
│              http://localhost:8000                        │
│              Swagger : http://localhost:8000/api/docs     │
└─────────────────────────────┬─────────────────────────────┘
                              │ SQL (PyMySQL)
                              ▼
┌─────────────────────────────┴─────────────────────────────┐
│          Base de Données (MySQL 8.0 — Docker)             │
│          Port: 3306                                       │
│          phpMyAdmin: http://localhost:8080                │
└───────────────────────────────────────────────────────────┘
```

## Prérequis

- **Python 3.11+** (backend)
- **Node.js 18+** (frontend)
- **Docker Desktop** (base de données MySQL)
- **Git**

## Installation rapide

### 1. Cloner le projet

```bash
git clone https://github.com/Sam-s-dev/TICK-IN-chat_bot_de_probleme_informatique.git
cd TICK-IN-chat_bot_de_probleme_informatique
```

> ⚠️ **Branche par défaut :** `dev` — toute collaboration se fait sur `dev`.

### 2. Démarrer la base de données (Docker)

```bash
cd database
docker compose up -d
```

MySQL sera disponible sur `localhost:3306`, phpMyAdmin sur `http://localhost:8080`.

### 3. Configurer l'environnement backend

```bash
cd backend
cp .env.example .env
python -m venv venv
# Windows :
.\venv\Scripts\activate
# Linux/Mac :
# source venv/bin/activate
pip install -r requirements.txt
```

Éditez `.env` si nécessaire (par défaut, les identifiants correspondent au docker-compose).

### 4. Configurer l'environnement frontend

```bash
cd frontend
npm install
```

### 5. Lancer l'application

**Terminal 1 — Backend :**
```bash
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend :**
```bash
cd frontend
npm run dev
```

🌐 Ouvrir `http://localhost:5173`

## Données de démonstration

La base de données est pré-initialisée avec des données de test (voir `database/init/02-seed.sql`).

### Comptes disponibles

Tous les mots de passe : **`password123`**

| Rôle | Email | Identité |
|---|---|---|
| **Admin** | `admin@centre-info.uganc.edu.gn` | Moussa Kaba |
| **Technicien** | `alpha.diallo@centre-info.uganc.edu.gn` | Alpha Oumar Diallo |
| **Technicien** | `sekou.conde@centre-info.uganc.edu.gn` | Sékou Condé |
| **Technicien** | `kadiatou.sylla@centre-info.uganc.edu.gn` | Kadiatou Sylla |
| **Étudiant** | `fatoumata.diallo@uganc.edu.gn` | Fatoumata Diallo |
| **Étudiant** | `mamadou.bah@uganc.edu.gn` | Mamadou Bah |
| **Étudiant** | `aminata.sow@uganc.edu.gn` | Aminata Sow |
| **Étudiant** | `ibrahima.camara@uganc.edu.gn` | Ibrahima Camara |
| **Étudiant** | `mariame.barry@uganc.edu.gn` | Mariame Barry |

### Tickets de test

Un ticket de démonstration pré-existe (créé par Ibrahima Camara, assigné à Kadiatou Sylla, statut "Résolu").

## Structure du projet

```
├── backend/
│   ├── app/
│   │   ├── main.py              # Point d'entrée FastAPI
│   │   ├── config.py            # Configuration (JWT, DB, etc.)
│   │   ├── database.py          # Connexion MySQL / session SQLAlchemy
│   │   ├── dependencies.py      # Dépendances (auth, permissions)
│   │   ├── models/              # Modèles SQLAlchemy
│   │   ├── routers/             # Endpoints API REST
│   │   ├── schemas/             # Schémas Pydantic (validation)
│   │   ├── services/            # Logique métier
│   │   └── uploads/             # Fichiers uploadés (audio, pièces jointes)
│   ├── .env.example             # Variables d'environnement (à copier en .env)
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/          # Composants Vue réutilisables
│   │   ├── composables/         # Composables Vue (useNotifications, etc.)
│   │   ├── router/              # Configuration Vue Router
│   │   ├── services/            # Services HTTP, WebSocket
│   │   └── views/               # Pages par rôle (admin/, technicien/, etudiant/)
│   ├── App.vue
│   ├── index.html
│   └── package.json
│
├── database/
│   ├── docker-compose.yml       # MySQL + phpMyAdmin
│   ├── .env.example             # Variables d'environnement MySQL
│   └── init/                    # Scripts SQL d'initialisation
│       ├── 01-schema.sql        # Schéma complet
│       ├── 02-seed.sql          # Données de démonstration
│       ├── 03-migration.sql     # Migrations
│       └── 04-landing-data.sql  # Données landing page
│
├── .gitignore
└── README.md
```

## API REST

Documentation Swagger accessible à : `http://localhost:8000/api/docs`

### Points d'entrée principaux

| Méthode | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/login` | Connexion |
| POST | `/api/auth/register` | Inscription étudiant |
| GET | `/api/auth/me` | Profil connecté |
| POST | `/api/tickets/` | Créer un ticket (étudiant) |
| GET | `/api/tickets/` | Lister les tickets |
| GET | `/api/tickets/{id}` | Détail d'un ticket |
| PATCH | `/api/tickets/{id}/status` | Changer le statut |
| PATCH | `/api/tickets/{id}/assign` | Assigner un technicien |
| GET | `/api/messages/{ticket_id}` | Messages d'un ticket |
| POST | `/api/messages/{ticket_id}` | Envoyer un message |
| POST | `/api/upload/` | Uploader un fichier/audio |
| GET | `/api/notifications` | Notifications de l'utilisateur |
| WS | `/api/ws?token={jwt}` | WebSocket (notifications temps réel) |

## WebSocket (temps réel)

Le frontend se connecte automatiquement au WebSocket après login.

**Événements :**
- `notification` — nouvelle notification (nouveau ticket, changement statut, nouveau message)
- `new_message` — nouveau message dans le chat (ajouté en temps réel sans refresh)

## Technologies

- **Frontend :** Vue 3 (Composition API), Vite, Tailwind CSS 4, Chart.js, Lucide Icons
- **Backend :** FastAPI, SQLAlchemy 2.0, PyMySQL, python-jose (JWT), Passlib (bcrypt)
- **Base de données :** MySQL 8.0 (Docker), phpMyAdmin
- **IA :** Groq (Llama 3) pour l'assignation automatique des techniciens
- **Temps réel :** WebSocket (FastAPI WebSockets)

## Workflow de collaboration

1. Travailler sur la branche `dev`
2. Créer des branches pour chaque feature : `feature/nom-de-la-feature`
3. Pusher et faire une Pull Request vers `dev`

```bash
git checkout dev
git pull origin dev
git checkout -b feature/ma-fonctionnalite
# ... développer ...
git add .
git commit -m "feat: description de la fonctionnalité"
git push origin feature/ma-fonctionnalite
```

## Licence

Projet développé pour le **Centre Informatique de l'UGANC** — Conakry, Guinée.
Pensez à toujours repusher sur la branche `dev`.
