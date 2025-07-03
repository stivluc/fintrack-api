from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Sum
from core.models import Category, Account, CategoryType, AccountType, Asset, AssetType
from transactions.models import Transaction, Budget, BudgetPeriod
from datetime import datetime, timedelta, date
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with demo data'

    def handle(self, *args, **options):
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
            {'name': 'Compte Courant', 'type': AccountType.CHECKING, 'balance': 2450.75},
            {'name': 'Livret A', 'type': AccountType.SAVINGS, 'balance': 8950.00},
            {'name': 'PEA', 'type': AccountType.INVESTMENT, 'balance': 15420.30},
            {'name': 'Espèces', 'type': AccountType.CASH, 'balance': 125.50},
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
                'amount': 3500.00,
                'category': income_categories[0],  # Salaire
                'account': accounts[0],  # Compte courant
                'is_recurring': True,
                'frequency': 'monthly'
            },
            {
                'description': 'Loyer',
                'amount': 1200.00,
                'category': expense_categories[2],  # Logement
                'account': accounts[0],
                'is_recurring': True,
                'frequency': 'monthly'
            },
            {
                'description': 'Abonnement transports',
                'amount': 75.00,
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
                Transaction.objects.create(
                    amount=trans_data['amount'],
                    date=current_date.replace(day=min(current_date.day, 28)),
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
        recent_transactions = [
            # REVENUS
            (date(2025, 6, 25), 'Salaire mensuel', 3200.00, income_categories[0]),
            (date(2025, 6, 15), 'Projet freelance', 800.00, income_categories[1] if len(income_categories) > 1 else income_categories[0]),
            (date(2025, 6, 10), 'Remboursement frais', 150.00, income_categories[-1]),
            
            # LOGEMENT
            (date(2025, 6, 1), 'Loyer juin', -1450.00, expense_categories[2]),
            (date(2025, 6, 5), 'Facture électricité', -89.50, expense_categories[2]),
            (date(2025, 6, 12), 'Abonnement internet', -29.99, expense_categories[2]),
            
            # ALIMENTATION
            (date(2025, 6, 2), 'Courses Carrefour', -67.80, expense_categories[0]),
            (date(2025, 6, 6), 'Boulangerie', -12.40, expense_categories[0]),
            (date(2025, 6, 9), 'Supermarché Leclerc', -89.60, expense_categories[0]),
            (date(2025, 6, 13), 'Marché local', -23.50, expense_categories[0]),
            (date(2025, 6, 16), 'Restaurant midi', -18.90, expense_categories[0]),
            (date(2025, 6, 20), 'Courses bio', -54.30, expense_categories[0]),
            (date(2025, 6, 23), 'Pizza livraison', -24.50, expense_categories[0]),
            (date(2025, 6, 27), 'Courses weekend', -73.20, expense_categories[0]),
            (date(2025, 6, 30), 'Café bureau', -8.60, expense_categories[0]),
            (date(2025, 7, 2), 'Courses juillet', -45.80, expense_categories[0]),
            
            # TRANSPORT
            (date(2025, 6, 3), 'Essence BP', -52.30, expense_categories[1]),
            (date(2025, 6, 11), 'Péage autoroute', -15.40, expense_categories[1]),
            (date(2025, 6, 18), 'Parking centre-ville', -8.00, expense_categories[1]),
            (date(2025, 6, 24), 'Essence Total', -49.70, expense_categories[1]),
            (date(2025, 7, 1), 'Lavage auto', -12.00, expense_categories[1]),
            
            # LOISIRS
            (date(2025, 6, 7), 'Cinéma', -22.00, expense_categories[4] if len(expense_categories) > 4 else expense_categories[-1]),
            (date(2025, 6, 14), 'Livre Amazon', -15.99, expense_categories[4] if len(expense_categories) > 4 else expense_categories[-1]),
            (date(2025, 6, 21), 'Concert', -45.00, expense_categories[4] if len(expense_categories) > 4 else expense_categories[-1]),
            (date(2025, 6, 28), 'Abonnement Netflix', -13.49, expense_categories[4] if len(expense_categories) > 4 else expense_categories[-1]),
            
            # SANTÉ
            (date(2025, 6, 8), 'Pharmacie', -18.60, expense_categories[3]),
            (date(2025, 6, 19), 'Médecin généraliste', -25.00, expense_categories[3]),
            
            # SHOPPING
            (date(2025, 6, 4), 'Vêtements Zara', -89.90, expense_categories[5] if len(expense_categories) > 5 else expense_categories[-1]),
            (date(2025, 6, 17), 'Accessoires téléphone', -24.99, expense_categories[5] if len(expense_categories) > 5 else expense_categories[-1]),
            (date(2025, 6, 26), 'Chaussures', -75.00, expense_categories[5] if len(expense_categories) > 5 else expense_categories[-1]),
            
            # ÉPARGNE/INVESTISSEMENT
            (date(2025, 6, 26), 'Virement épargne', -500.00, expense_categories[-1]),
            (date(2025, 6, 26), 'Placement PEA', -300.00, expense_categories[-1]),
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
            ('Courses Carrefour', 45.80, expense_categories[0]),
            ('Restaurant Le Bistrot', 28.50, expense_categories[0]),
            ('Boulangerie', 12.30, expense_categories[0]),
            ('Uber Eats', 22.90, expense_categories[0]),
            ('Marché bio', 35.60, expense_categories[0]),
            
            # Transport
            ('Essence', 65.00, expense_categories[1]),
            ('Péage autoroute', 12.80, expense_categories[1]),
            ('Parking', 8.50, expense_categories[1]),
            
            # Loisirs
            ('Cinéma', 24.00, expense_categories[4] if len(expense_categories) > 4 else expense_categories[-1]),
            ('Concert', 85.00, expense_categories[4] if len(expense_categories) > 4 else expense_categories[-1]),
            ('Livre', 18.90, expense_categories[4] if len(expense_categories) > 4 else expense_categories[-1]),
            
            # Revenus additionnels
            ('Freelance mission', 600.00, income_categories[1] if len(income_categories) > 1 else income_categories[0]),
            ('Remboursement', 45.00, income_categories[-1]),
        ]
        
        # Générer quelques transactions pour l'historique (période avant juin 2025)
        historical_start = start_date
        historical_end = date(2025, 5, 31)  # Avant les données récentes
        
        for i in range(80):  # Moins de transactions historiques
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
        
        # 6. Créer des budgets
        budgets_data = [
            {'category': expense_categories[0], 'limit': 400.00},  # Alimentation
            {'category': expense_categories[1], 'limit': 200.00},  # Transport
            {'category': expense_categories[4], 'limit': 150.00},  # Loisirs
            {'category': expense_categories[5], 'limit': 100.00},  # Shopping
            {'category': expense_categories[3], 'limit': 80.00},   # Santé
        ]
        
        budgets_created = 0
        for budget_data in budgets_data:
            Budget.objects.get_or_create(
                category=budget_data['category'],
                user=demo_user,
                defaults={
                    'monthly_limit': budget_data['limit'],
                    'period': BudgetPeriod.MONTHLY,
                    'is_active': True
                }
            )
            budgets_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ {budgets_created} budgets created'))
        
        # 7. Créer des assets pour le patrimoine
        assets_data = [
            {
                'name': 'Appartement Paris 15ème',
                'asset_type': AssetType.REAL_ESTATE,
                'current_value': 285000.00,
                'purchase_price': 250000.00,
                'purchase_date': date(2020, 3, 15),
                'description': 'Appartement 3 pièces de 65m² dans le 15ème arrondissement'
            },
            {
                'name': 'Actions Total Energies',
                'asset_type': AssetType.STOCKS,
                'current_value': 12500.00,
                'purchase_price': 10800.00,
                'purchase_date': date(2021, 6, 10),
                'description': '250 actions Total Energies'
            },
            {
                'name': 'Assurance Vie Crédit Agricole',
                'asset_type': AssetType.INSURANCE,
                'current_value': 18500.00,
                'purchase_price': 15000.00,
                'purchase_date': date(2019, 1, 20),
                'description': 'Contrat d\'assurance vie multi-supports'
            },
            {
                'name': 'Livret A',
                'asset_type': AssetType.SAVINGS_ACCOUNT,
                'current_value': 22300.00,
                'purchase_price': 20000.00,
                'purchase_date': date(2018, 9, 5),
                'description': 'Livret A plafonné'
            },
            {
                'name': 'PEL Banque Populaire',
                'asset_type': AssetType.PENSION_PLAN,
                'current_value': 18000.00,
                'purchase_price': 16500.00,
                'purchase_date': date(2019, 5, 12),
                'description': 'Plan Épargne Logement'
            },
            {
                'name': 'Portefeuille Crypto',
                'asset_type': AssetType.CRYPTO,
                'current_value': 8500.00,
                'purchase_price': 12000.00,
                'purchase_date': date(2021, 11, 28),
                'description': 'Bitcoin, Ethereum et autres altcoins'
            },
            {
                'name': 'Or physique',
                'asset_type': AssetType.PRECIOUS_METALS,
                'current_value': 3500.00,
                'purchase_price': 3200.00,
                'purchase_date': date(2020, 8, 14),
                'description': 'Pièces et lingots d\'or'
            },
            {
                'name': 'SCPI Immobilière',
                'asset_type': AssetType.REAL_ESTATE,
                'current_value': 15000.00,
                'purchase_price': 14500.00,
                'purchase_date': date(2022, 2, 18),
                'description': 'Parts de SCPI de rendement'
            }
        ]
        
        assets_created = 0
        for asset_data in assets_data:
            Asset.objects.get_or_create(
                name=asset_data['name'],
                user=demo_user,
                defaults=asset_data
            )
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