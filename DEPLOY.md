# 🚀 Guide de déploiement FinTrack API

## Configuration actuelle

- **Base de données** : Supabase (même DB pour dev et prod)
- **Données de démo** : Déjà peuplées dans Supabase
- **Comptes** : demo@fintrack.com / demo123 et admin@fintrack.com / admin123

## Déploiement sur Render

### 1. Préparer le repository

```bash
git add .
git commit -m "FinTrack API ready for deployment"
git push origin main
```

### 2. Configuration Render

#### Créer un Web Service sur [render.com](https://render.com)

- **Repository** : Connecter votre GitHub repo
- **Branch** : main
- **Root Directory** : (laisser vide)
- **Runtime** : Python 3
- **Build Command** : `./build.sh`
- **Start Command** : `gunicorn fintrack.wsgi:application`

#### Variables d'environnement

```env
DJANGO_SETTINGS_MODULE=fintrack.settings.production
SECRET_KEY=your-new-secret-key-here-generate-one
DATABASE_URL=postgresql://postgres:YOUR_SUPABASE_PASSWORD@db.jawqtsmaakoleszqyoeb.supabase.co:5432/postgres
DEBUG=False
```

> ⚠️ **Note** : `ALLOWED_HOSTS` n'est pas nécessaire sur Render, il est géré automatiquement

### 3. Après déploiement

✅ **API sera accessible** : `https://your-app.onrender.com/api/`

✅ **Admin interface** : `https://your-app.onrender.com/admin/`

✅ **Données de démo** : Déjà présentes (même DB que dev)

### 4. Test de l'API déployée

```bash
# Test de connexion
curl -X POST https://your-app.onrender.com/api/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@fintrack.com", "password": "demo123"}'

# Test des catégories (avec token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-app.onrender.com/api/categories/
```

## Avantages de cette configuration

- **Simplicité** : Une seule base de données pour tout
- **Cohérence** : Mêmes données en dev et prod
- **Démo immédiate** : Pas besoin de recréer les données
- **Administration** : Interface admin directement accessible

## Données de démo incluses

- **138 transactions** sur 6 mois (salaires, courses, loisirs, etc.)
- **4 comptes** (Courant, Livret A, PEA, Espèces)
- **5 budgets** avec alertes de dépassement
- **13 catégories** par défaut (revenus et dépenses)

## API Endpoints principaux

```
POST /api/auth/jwt/create/          # Login
GET  /api/transactions/             # Transactions avec filtres
GET  /api/transactions/dashboard_stats/  # Stats dashboard
GET  /api/categories/               # Catégories
GET  /api/accounts/                 # Comptes
GET  /api/budgets/                  # Budgets
GET  /api/budgets/alerts/           # Alertes budget
```

## 🔧 Dépannage des erreurs courantes

### Erreur `No module named 'pkg_resources'`
**Solution** : Ajouté `setuptools==75.8.0` dans requirements.txt

### Erreur de build Django
**Solution** : Script build.sh amélioré avec gestion d'erreurs

### Erreur de connexion base de données
**Vérifier** : 
- Variable `DATABASE_URL` correctement configurée
- Mot de passe Supabase correct
- Connexions autorisées dans Supabase

### Variables d'environnement manquantes
**Vérifier** :
- `SECRET_KEY` généré
- `DJANGO_SETTINGS_MODULE=fintrack.settings.production`
- `DATABASE_URL` avec vraies credentials

## Surveillance

Une fois déployé, surveiller :

- **Logs Render** pour les erreurs
- **Interface admin** pour vérifier les données
- **Tests API** avec le script test_api.py
