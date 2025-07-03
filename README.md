# FinTrack API

API REST pour une application de gestion budgétaire inspirée de Finary.

## Stack technique

- **Backend**: Django 5.2 + Django REST Framework
- **Base de données**: PostgreSQL
- **Authentification**: JWT (via djoser)
- **CORS**: django-cors-headers

## Installation rapide

### 🚀 **Setup automatique**
```bash
git clone <your-repo>
cd fintrack-api
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configurer la base de données Supabase
cp .env.example .env
# Éditer .env avec votre URL Supabase

# Configuration automatique
python setup_demo.py

# Lancer l'API
python manage.py runserver
```

### 🔧 **Setup manuel (si besoin)**
```bash
# 1. Configuration environnement
cp .env.example .env
# Éditer DATABASE_URL dans .env

# 2. Base de données et données de démo
python manage.py migrate
python manage.py populate_categories
python manage.py populate_demo_data

# 3. Lancer le serveur
python manage.py runserver
```

### 🔑 **Comptes de démo créés automatiquement**
- **Demo User** : `demo@fintrack.com` / `demo123`
- **Admin** : `admin@fintrack.com` / `admin123`

## Endpoints API

### Authentification
- `POST /api/auth/users/` - Créer un compte
- `POST /api/auth/jwt/create/` - Se connecter (obtenir token JWT)
- `POST /api/auth/jwt/refresh/` - Renouveler le token
- `GET /api/auth/users/me/` - Obtenir le profil utilisateur

### Catégories
- `GET /api/categories/` - Lister les catégories
- `POST /api/categories/` - Créer une catégorie personnalisée
- `GET /api/categories/{id}/` - Détail d'une catégorie
- `PUT/PATCH /api/categories/{id}/` - Modifier une catégorie
- `DELETE /api/categories/{id}/` - Supprimer une catégorie

### Comptes
- `GET /api/accounts/` - Lister les comptes
- `POST /api/accounts/` - Créer un compte
- `GET /api/accounts/{id}/` - Détail d'un compte
- `PUT/PATCH /api/accounts/{id}/` - Modifier un compte
- `DELETE /api/accounts/{id}/` - Supprimer un compte

### Transactions
- `GET /api/transactions/` - Lister les transactions
- `POST /api/transactions/` - Créer une transaction
- `GET /api/transactions/{id}/` - Détail d'une transaction
- `PUT/PATCH /api/transactions/{id}/` - Modifier une transaction
- `DELETE /api/transactions/{id}/` - Supprimer une transaction
- `GET /api/transactions/dashboard_stats/` - Statistiques du dashboard

### Budgets
- `GET /api/budgets/` - Lister les budgets
- `POST /api/budgets/` - Créer un budget
- `GET /api/budgets/{id}/` - Détail d'un budget
- `PUT/PATCH /api/budgets/{id}/` - Modifier un budget
- `DELETE /api/budgets/{id}/` - Supprimer un budget
- `GET /api/budgets/alerts/` - Alertes de dépassement de budget

## Filtres et recherche

### Transactions
- Filtrer par catégorie: `?category=1`
- Filtrer par compte: `?account=1`
- Filtrer par date: `?date__gte=2024-01-01&date__lte=2024-12-31`
- Recherche: `?search=restaurant`
- Tri: `?ordering=-date`

### Comptes
- Filtrer par type: `?type=CHECKING`
- Recherche: `?search=livret`

## Exemple d'utilisation

```javascript
// Connexion
const response = await fetch('/api/auth/jwt/create/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});
const { access } = await response.json();

// Créer une transaction
await fetch('/api/transactions/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access}`
  },
  body: JSON.stringify({
    amount: 50.00,
    date: '2024-01-15T10:30:00Z',
    description: 'Restaurant',
    category_id: 1,
    account_id: 1
  })
});
```

## Administration

Accéder à l'interface d'administration Django: `http://localhost:8000/admin/`

## 🚀 Déploiement avec Supabase + Render

### Étape 1: Base de données Supabase
1. Créer un compte sur [Supabase](https://supabase.com)
2. Créer un nouveau projet
3. Récupérer l'URL de connexion dans Settings > Database

### Étape 2: Déployer sur Render
1. Créer un compte sur [Render](https://render.com)
2. Connecter votre repository GitHub
3. Créer un nouveau **Web Service**
4. Configurer:
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn fintrack.wsgi:application`

### Étape 3: Variables d'environnement Render
```env
DJANGO_SETTINGS_MODULE=fintrack.settings.production
SECRET_KEY=your-generated-secret-key
DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
ALLOWED_HOSTS=your-app.onrender.com
DEBUG=False
```

### Étape 4: Test de l'API
Une fois déployé, tester:
- `GET https://your-app.onrender.com/api/categories/` (doit être protégé)
- `POST https://your-app.onrender.com/api/auth/jwt/create/` (login)

### Compte de démo
- **Email**: demo@fintrack.com
- **Password**: demo123

## 🎯 **Avantages de cette configuration**

- **Une seule base de données** : Même données en dev et prod
- **Démo partagée** : Tous les développeurs voient les mêmes données
- **Déploiement simplifié** : Pas de sync de données à gérer
- **Tests réalistes** : Environnement de dev identique à la prod

## 🔧 **Commandes utiles**

```bash
# Réinitialiser les données de démo
python manage.py flush --noinput
python manage.py migrate
python manage.py populate_categories
python manage.py populate_demo_data

# Lancer l'API en local
python manage.py runserver

# Tester l'API
python test_api.py

# Accéder à l'admin
# http://localhost:8000/admin/
# admin@fintrack.com / admin123
```