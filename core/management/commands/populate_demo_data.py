from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Sum
from core.models import Category, Account, CategoryType, AccountType, Asset, AssetType
from transactions.models import Transaction, Budget, BudgetPeriod
from datetime import datetime, timedelta, date
from decimal import Decimal
import random

User = get_user_model()


from django.core.management import call_command

class Command(BaseCommand):
    help = 'Populate database with demo data'

    def handle(self, *args, **options):
        call_command('populate_categories')
        self.stdout.write(self.style.SUCCESS('Creating demo data...'))
        
        # 1. Créer les utilisateurs de démo
        demo_user, created = User.objects.get_or_create(
            email='demo@fintrack.com',
            username='demo_user',
            defaults={
                'first_name': 'Demo',
                'last_name': 'User',
                'is_premium': True,
            }
        )
        if created:
            demo_user.set_password('demo123')
            demo_user.save()
            self.stdout.write(self.style.SUCCESS('✓ Demo user created'))
        
        # Créer un admin
        admin_user, created = User.objects.get_or_create(
            email='admin@fintrack.com',
            username='admin',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
                'is_premium': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('✓ Admin user created'))
        
        # 2. Créer des comptes
        accounts_data = [
            {'name': 'Compte Courant', 'type': AccountType.CHECKING, 'balance': 3250.75},
            {'name': 'Livret A', 'type': AccountType.SAVINGS, 'balance': 12500.00},
            {'name': 'PEA', 'type': AccountType.INVESTMENT, 'balance': 25420.30},
            {'name': 'Espèces', 'type': AccountType.CASH, 'balance': 150.50},
        ]
        
        accounts = []
        for acc_data in accounts_data:
            account, created = Account.objects.get_or_create(
                name=acc_data['name'],
                user=demo_user,
                defaults={
                    'type': acc_data['type'],
                    'balance': acc_data['balance']
                }
            )
            # Si le compte existe déjà, on s'assure qu'il a le bon solde
            if not created:
                account.balance = acc_data['balance']
                account.save()
            accounts.append(account)
        
        self.stdout.write(self.style.SUCCESS(f'✓ {len(accounts)} accounts created'))
        
        # 3. Récupérer les catégories par défaut
        income_categories = list(Category.objects.filter(type=CategoryType.INCOME, is_default=True))
        expense_categories = list(Category.objects.filter(type=CategoryType.EXPENSE, is_default=True))
        
        if not income_categories or not expense_categories:
            self.stdout.write(self.style.WARNING('Please run populate_categories first'))
            return
        
        # 4. Créer des transactions sur les 6 derniers mois
        transactions_created = 0
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)
        
        # Transactions récurrentes (salaire, loyer, etc.)
        recurring_transactions = [
            {
                'description': 'Salaire mensuel',
                'amount': 4200.00,
                'category': income_categories[0],  # Salaire
                'account': accounts[0],  # Compte courant
                'is_recurring': True,
                'frequency': 'monthly'
            },
            {
                'description': 'Loyer',
                'amount': 1300.00,
                'category': expense_categories[2],  # Logement
                'account': accounts[0],
                'is_recurring': True,
                'frequency': 'monthly'
            },
            {
                'description': 'Abonnement transports',
                'amount': 85.00,
                'category': expense_categories[1],  # Transport
                'account': accounts[0],
                'is_recurring': True,
                'frequency': 'monthly'
            },
        ]
        
        # Générer transactions récurrentes
        current_date = start_date
        while current_date <= end_date:
            for trans_data in recurring_transactions:
                transaction_date = current_date.replace(day=min(current_date.day, 28))
                # Vérifier si la transaction récurrente existe déjà
                if not Transaction.objects.filter(
                    date=transaction_date,
                    description=trans_data['description'],
                    amount=trans_data['amount'],
                    user=demo_user,
                    is_recurring=True
                ).exists():
                    Transaction.objects.create(
                        amount=trans_data['amount'],
                        date=transaction_date,
                        description=trans_data['description'],
                        category=trans_data['category'],
                        account=trans_data['account'],
                        user=demo_user,
                        is_recurring=trans_data['is_recurring'],
                        metadata={'frequency': trans_data['frequency']}
                    )
                    transactions_created += 1
            
            # Passer au mois suivant
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        # 5. Ajouter des transactions spécifiques pour les 30 derniers jours (juin-juillet 2025)
        # Récupérer les catégories par nom pour être sûr
        salaire_cat = Category.objects.filter(name='Salaire', type=CategoryType.INCOME).first()
        freelance_cat = Category.objects.filter(name='Freelance', type=CategoryType.INCOME).first()
        autres_revenus_cat = Category.objects.filter(name='Autres revenus', type=CategoryType.INCOME).first()
        
        # Si pas trouvé, utiliser les listes existantes
        if not salaire_cat and income_categories:
            salaire_cat = income_categories[0]
        if not freelance_cat and len(income_categories) > 1:
            freelance_cat = income_categories[1]
        if not autres_revenus_cat and income_categories:
            autres_revenus_cat = income_categories[-1]
        
        # Rechercher la catégorie éducation pour les transactions
        education_cat = None
        for cat in expense_categories:
            if 'ducation' in cat.name or 'formation' in cat.name.lower() or 'livre' in cat.name.lower():
                education_cat = cat
                break
        
        recent_transactions = [
            # REVENUS
            (date(2025, 6, 25), 'Salaire mensuel', 4200.00, salaire_cat),
            (date(2025, 6, 15), 'Projet freelance', 1200.00, freelance_cat),
            (date(2025, 6, 10), 'Remboursement frais', 250.00, autres_revenus_cat),
            
            # LOGEMENT
            (date(2025, 6, 1), 'Loyer juin', -1300.00, expense_categories[2]),
            (date(2025, 6, 5), 'Facture électricité', -75.50, expense_categories[2]),
            (date(2025, 6, 12), 'Abonnement internet', -39.99, expense_categories[2]),
            
            # ALIMENTATION (pour atteindre 487.30€ total)
            (date(2025, 6, 2), 'Courses Carrefour', -85.30, expense_categories[0]),
            (date(2025, 6, 6), 'Boulangerie', -15.40, expense_categories[0]),
            (date(2025, 6, 9), 'Supermarché Leclerc', -95.60, expense_categories[0]),
            (date(2025, 6, 13), 'Marché local', -33.50, expense_categories[0]),
            (date(2025, 6, 16), 'Restaurant midi', -22.90, expense_categories[0]),
            (date(2025, 6, 20), 'Courses bio', -64.30, expense_categories[0]),
            (date(2025, 6, 23), 'Pizza livraison', -28.50, expense_categories[0]),
            (date(2025, 6, 27), 'Courses weekend', -83.20, expense_categories[0]),
            (date(2025, 6, 30), 'Café bureau', -12.60, expense_categories[0]),
            (date(2025, 7, 2), 'Courses juillet', -46.00, expense_categories[0]),
            
            # TRANSPORT (pour atteindre 320.85€ total)
            (date(2025, 6, 3), 'Essence BP', -62.30, expense_categories[1]),
            (date(2025, 6, 11), 'Péage autoroute', -25.40, expense_categories[1]),
            (date(2025, 6, 18), 'Parking centre-ville', -12.00, expense_categories[1]),
            (date(2025, 6, 24), 'Essence Total', -59.70, expense_categories[1]),
            (date(2025, 7, 1), 'Lavage auto', -15.00, expense_categories[1]),
            (date(2025, 6, 14), 'Abonnement transports', -85.00, expense_categories[1]),
            (date(2025, 6, 29), 'Réparation véhicule', -45.45, expense_categories[1]),
            (date(2025, 7, 5), 'Parking aéroport', -16.00, expense_categories[1]),
            
            # LOISIRS (pour atteindre 245.60€ total)
            (date(2025, 6, 7), 'Cinéma', -25.00, expense_categories[4] if len(expense_categories) > 4 else expense_categories[-1]),
            (date(2025, 6, 14), 'Livre Amazon', -19.99, expense_categories[4] if len(expense_categories) > 4 else expense_categories[-1]),
            (date(2025, 6, 21), 'Concert', -55.00, expense_categories[4] if len(expense_categories) > 4 else expense_categories[-1]),
            (date(2025, 6, 28), 'Abonnement Netflix', -15.49, expense_categories[4] if len(expense_categories) > 4 else expense_categories[-1]),
            (date(2025, 6, 15), 'Jeux vidéo Steam', -35.50, expense_categories[4] if len(expense_categories) > 4 else expense_categories[-1]),
            (date(2025, 6, 22), 'Sortie entre amis', -42.80, expense_categories[4] if len(expense_categories) > 4 else expense_categories[-1]),
            (date(2025, 7, 4), 'Exposition musée', -18.00, expense_categories[4] if len(expense_categories) > 4 else expense_categories[-1]),
            (date(2025, 7, 6), 'Abonnement Spotify', -9.99, expense_categories[4] if len(expense_categories) > 4 else expense_categories[-1]),
            (date(2025, 6, 10), 'Magazine BD', -23.83, expense_categories[4] if len(expense_categories) > 4 else expense_categories[-1]),
            
            # SANTÉ (pour atteindre 89.00€ total)
            (date(2025, 6, 8), 'Pharmacie', -22.60, expense_categories[3]),
            (date(2025, 6, 19), 'Médecin généraliste', -30.00, expense_categories[3]),
            (date(2025, 6, 25), 'Dentiste contrôle', -25.00, expense_categories[3]),
            (date(2025, 7, 3), 'Compléments vitamines', -11.40, expense_categories[3]),
            
            # SHOPPING (pour atteindre 156.75€ total)
            (date(2025, 6, 4), 'Vêtements Zara', -65.00, expense_categories[5] if len(expense_categories) > 5 else expense_categories[-1]),
            (date(2025, 6, 17), 'Accessoires téléphone', -29.99, expense_categories[5] if len(expense_categories) > 5 else expense_categories[-1]),
            (date(2025, 6, 26), 'Chaussures', -45.76, expense_categories[5] if len(expense_categories) > 5 else expense_categories[-1]),
            (date(2025, 7, 3), 'Petits accessoires', -16.00, expense_categories[5] if len(expense_categories) > 5 else expense_categories[-1]),
            
            # ÉDUCATION (pour atteindre 45.00€ total si la catégorie existe)
            (date(2025, 6, 12), 'Livre technique Python', -25.90, education_cat if education_cat else expense_categories[-1]),
            (date(2025, 6, 20), 'Formation en ligne Udemy', -19.10, education_cat if education_cat else expense_categories[-1]),
            
            # ÉPARGNE/INVESTISSEMENT
            (date(2025, 6, 26), 'Virement épargne', -600.00, expense_categories[-1]),
            (date(2025, 6, 26), 'Placement PEA', -400.00, expense_categories[-1]),
        ]
        
        # Créer les transactions des 30 derniers jours
        for trans_date, description, amount, category in recent_transactions:
            # Vérifier si la transaction existe déjà
            if not Transaction.objects.filter(
                date=trans_date,
                description=description,
                amount=amount,
                user=demo_user
            ).exists():
                Transaction.objects.create(
                    amount=amount,
                    date=trans_date,
                    description=description,
                    category=category,
                    account=accounts[0],  # Compte courant
                    user=demo_user,
                    metadata={'recent_data': True}
                )
                transactions_created += 1
        
        # 6. Générer quelques transactions aléatoires pour compléter l'historique
        random_transactions = [
            # Alimentation
            ('Courses Carrefour', 55.80, expense_categories[0]),
            ('Restaurant Le Bistrot', 38.50, expense_categories[0]),
            ('Boulangerie', 18.30, expense_categories[0]),
            ('Uber Eats', 25.90, expense_categories[0]),
            ('Marché bio', 45.60, expense_categories[0]),
            
            # Transport
            ('Essence', 75.00, expense_categories[1]),
            ('Péage autoroute', 18.80, expense_categories[1]),
            ('Parking', 10.50, expense_categories[1]),
            
            # Loisirs
            ('Cinéma', 28.00, expense_categories[4] if len(expense_categories) > 4 else expense_categories[-1]),
            ('Concert', 95.00, expense_categories[4] if len(expense_categories) > 4 else expense_categories[-1]),
            ('Livre', 22.90, expense_categories[4] if len(expense_categories) > 4 else expense_categories[-1]),
            
            # Revenus additionnels
            ('Freelance mission', 800.00, income_categories[1] if len(income_categories) > 1 else income_categories[0]),
            ('Remboursement', 55.00, income_categories[-1]),
        ]
        
        # Générer quelques transactions pour l'historique (période avant juin 2025)
        historical_start = start_date
        historical_end = date(2025, 5, 31)  # Avant les données récentes
        
        # Supprimer les anciennes transactions générées pour éviter les duplicatas
        Transaction.objects.filter(user=demo_user, metadata__generated=True).delete()
        
        for i in range(100):  # Moins de transactions historiques
            trans_data = random.choice(random_transactions)
            # Générer des dates entre start_date et mai 2025
            days_diff = (historical_end - historical_start.date()).days
            if days_diff > 0:
                random_days = random.randint(0, days_diff)
                random_date = historical_start.date() + timedelta(days=random_days)
                random_account = random.choice(accounts)
                
                Transaction.objects.create(
                    amount=trans_data[1],
                    date=random_date,
                    description=trans_data[0],
                    category=trans_data[2],
                    account=random_account,
                    user=demo_user,
                    metadata={'generated': True}
                )
                transactions_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ {transactions_created} transactions created'))
        
        # 6. Créer des budgets (données identiques à l'app mobile)
        budgets_data = [
            {'category': expense_categories[0], 'limit': 600.00},  # Alimentation
            {'category': expense_categories[1], 'limit': 400.00},  # Transport
            {'category': expense_categories[4], 'limit': 300.00},  # Loisirs
            {'category': expense_categories[5], 'limit': 200.00},  # Shopping
            {'category': expense_categories[3], 'limit': 150.00},   # Santé
        ]
        
        # Ajouter un budget pour Éducation si la catégorie existe
        if education_cat:
            budgets_data.append({'category': education_cat, 'limit': 100.00})  # Éducation
        
        budgets_created = 0
        for budget_data in budgets_data:
            budget, created = Budget.objects.get_or_create(
                category=budget_data['category'],
                user=demo_user,
                defaults={
                    'monthly_limit': budget_data['limit'],
                    'period': BudgetPeriod.MONTHLY,
                    'is_active': True
                }
            )
            # Si le budget existe déjà, on s'assure qu'il a la bonne limite
            if not created:
                budget.monthly_limit = budget_data['limit']
                budget.is_active = True
                budget.save()
            budgets_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ {budgets_created} budgets created'))
        
        # 7. Créer des assets pour le patrimoine
        assets_data = [
            {
                'name': 'Appartement Paris 15ème',
                'asset_type': AssetType.REAL_ESTATE,
                'current_value': 150000.00,
                'purchase_price': 120000.00,
                'purchase_date': date(2020, 3, 15),
                'description': 'Appartement 2 pièces de 45m² dans le 15ème arrondissement'
            },
            {
                'name': 'Actions Total Energies',
                'asset_type': AssetType.STOCKS,
                'current_value': 25000.00,
                'purchase_price': 20000.00,
                'purchase_date': date(2021, 6, 10),
                'description': '500 actions Total Energies'
            },
            {
                'name': 'Assurance Vie Crédit Agricole',
                'asset_type': AssetType.INSURANCE,
                'current_value': 35000.00,
                'purchase_price': 30000.00,
                'purchase_date': date(2019, 1, 20),
                'description': 'Contrat d\'assurance vie multi-supports'
            },
            {
                'name': 'Livret A',
                'asset_type': AssetType.SAVINGS_ACCOUNT,
                'current_value': 25000.00,
                'purchase_price': 22000.00,
                'purchase_date': date(2018, 9, 5),
                'description': 'Livret A plafonné'
            },
            {
                'name': 'PEL Banque Populaire',
                'asset_type': AssetType.PENSION_PLAN,
                'current_value': 20000.00,
                'purchase_price': 18000.00,
                'purchase_date': date(2019, 5, 12),
                'description': 'Plan Épargne Logement'
            },
            {
                'name': 'Portefeuille Crypto',
                'asset_type': AssetType.CRYPTO,
                'current_value': 15000.00,
                'purchase_price': 10000.00,
                'purchase_date': date(2021, 11, 28),
                'description': 'Bitcoin, Ethereum et autres altcoins'
            },
            {
                'name': 'Or physique',
                'asset_type': AssetType.PRECIOUS_METALS,
                'current_value': 5000.00,
                'purchase_price': 4000.00,
                'purchase_date': date(2020, 8, 14),
                'description': 'Pièces et lingots d\'or'
            },
            {
                'name': 'SCPI Immobilière',
                'asset_type': AssetType.REAL_ESTATE,
                'current_value': 20000.00,
                'purchase_price': 18000.00,
                'purchase_date': date(2022, 2, 18),
                'description': 'Parts de SCPI de rendement'
            }
        ]
        
        assets_created = 0
        for asset_data in assets_data:
            # Simulate asset value evolution
            purchase_date = asset_data['purchase_date']
            today = date.today()
            days_since_purchase = (today - purchase_date).days
            # Simulate a growth of 5% to 20% per year
            annual_growth_rate = Decimal(random.uniform(0.05, 0.20))
            growth_factor = (1 + annual_growth_rate) ** Decimal(days_since_purchase / 365.25)
            asset_data['current_value'] = round(Decimal(asset_data['purchase_price']) * growth_factor, 2)

            asset, created = Asset.objects.get_or_create(
                name=asset_data['name'],
                user=demo_user,
                defaults=asset_data
            )
            # Si l'asset existe déjà, on met à jour sa valeur
            if not created:
                asset.current_value = asset_data['current_value']
                asset.save()
            assets_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ {assets_created} assets created'))
        
        # 8. Statistiques finales
        total_transactions = Transaction.objects.filter(user=demo_user).count()
        total_accounts = Account.objects.filter(user=demo_user).count()
        total_budgets = Budget.objects.filter(user=demo_user).count()
        total_assets = Asset.objects.filter(user=demo_user).count()
        total_wealth = (
            Account.objects.filter(user=demo_user).aggregate(total=Sum('balance'))['total'] or 0
        ) + (
            Asset.objects.filter(user=demo_user).aggregate(total=Sum('current_value'))['total'] or 0
        )
        
        self.stdout.write(self.style.SUCCESS('\n=== DEMO DATA SUMMARY ==='))
        self.stdout.write(f'👤 Demo User: {demo_user.email}')
        self.stdout.write(f'💳 Accounts: {total_accounts}')
        self.stdout.write(f'🏠 Assets: {total_assets}')
        self.stdout.write(f'💰 Transactions: {total_transactions}')
        self.stdout.write(f'📊 Budgets: {total_budgets}')
        self.stdout.write(f'💎 Total Wealth: €{total_wealth:,.2f}')
        self.stdout.write(f'🔑 Login: demo@fintrack.com / demo123')
        self.stdout.write(f'🔐 Admin: admin@fintrack.com / admin123')
        self.stdout.write(self.style.SUCCESS('\n✅ Demo data populated successfully!'))