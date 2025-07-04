from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import random
from transactions.models import Transaction, Budget
from core.models import Asset, Account, Category

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with realistic financial data with life variations'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Starting realistic data population...")
        
        # Create user
        user = self.create_user()
        self.stdout.write(f"✅ Created user: {user.username}")
        
        # Clean existing user data
        self.clean_user_data(user)
        
        # Create accounts
        accounts = self.create_accounts(user)
        self.stdout.write(f"✅ Created {len(accounts)} accounts")
        
        # Create assets
        assets = self.create_assets(user)
        self.stdout.write(f"✅ Created {len(assets)} assets")
        
        # Create budgets
        budgets = self.create_budgets(user)
        self.stdout.write(f"✅ Created {len(budgets)} budgets")
        
        # Generate transactions over 2 years with life events
        transactions = self.generate_transactions(user, accounts)
        self.stdout.write(f"✅ Generated {len(transactions)} transactions")
        
        self.stdout.write(self.style.SUCCESS("🎉 Realistic data population completed!"))
        
        # Show summary
        self.show_summary()

    def create_user(self):
        user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={
                'email': 'demo@fintrack.com',
                'first_name': 'Pierre',
                'last_name': 'Dubois'
            }
        )
        if created:
            user.set_password('demo123')
            user.save()
            self.stdout.write("Created new user")
        else:
            self.stdout.write("Using existing user")
        return user

    def clean_user_data(self, user):
        """Clean existing data for user"""
        Transaction.objects.filter(user=user).delete()
        Budget.objects.filter(user=user).delete()
        Asset.objects.filter(user=user).delete()
        Account.objects.filter(user=user).delete()
        self.stdout.write("🧹 Cleaned existing user data")

    def create_accounts(self, user):
        accounts_data = [
            {
                'name': 'Compte Courant',
                'type': 'CHECKING',
                'balance': Decimal('2500.00'),
                'is_active': True
            },
            {
                'name': 'Livret A',
                'type': 'SAVINGS',
                'balance': Decimal('15000.00'),
                'is_active': True
            },
            {
                'name': 'PEA',
                'type': 'INVESTMENT',
                'balance': Decimal('25000.00'),
                'is_active': True
            },
            {
                'name': 'Assurance Vie',
                'type': 'INVESTMENT',
                'balance': Decimal('45000.00'),
                'is_active': True
            }
        ]
        
        accounts = []
        for data in accounts_data:
            account, created = Account.objects.get_or_create(
                user=user,
                name=data['name'],
                defaults=data
            )
            accounts.append(account)
        
        return accounts

    def create_assets(self, user):
        assets_data = [
            {
                'name': 'Résidence principale',
                'asset_type': 'REAL_ESTATE',
                'purchase_price': Decimal('180000.00'),
                'current_value': Decimal('200000.00'),
                'is_active': True
            },
            {
                'name': 'Peugeot 308',
                'asset_type': 'OTHER',
                'purchase_price': Decimal('25000.00'),
                'current_value': Decimal('18000.00'),
                'is_active': True
            },
            {
                'name': 'Portefeuille Actions',
                'asset_type': 'STOCKS',
                'purchase_price': Decimal('45000.00'),
                'current_value': Decimal('52000.00'),
                'is_active': True
            },
            {
                'name': 'ETF Monde',
                'asset_type': 'STOCKS',
                'purchase_price': Decimal('28000.00'),
                'current_value': Decimal('31000.00'),
                'is_active': True
            },
            {
                'name': 'Obligations',
                'asset_type': 'BONDS',
                'purchase_price': Decimal('15000.00'),
                'current_value': Decimal('15800.00'),
                'is_active': True
            },
            {
                'name': 'Or physique',
                'asset_type': 'PRECIOUS_METALS',
                'purchase_price': Decimal('8000.00'),
                'current_value': Decimal('8500.00'),
                'is_active': True
            },
            {
                'name': 'Crypto (BTC/ETH)',
                'asset_type': 'CRYPTO',
                'purchase_price': Decimal('12000.00'),
                'current_value': Decimal('10000.00'),
                'is_active': True
            }
        ]
        
        assets = []
        for data in assets_data:
            asset = Asset.objects.create(
                user=user,
                **data
            )
            assets.append(asset)
        
        return assets

    def create_budgets(self, user):
        # Get categories for budgets
        food_cat = Category.objects.filter(name__icontains='Alimentation').first()
        transport_cat = Category.objects.filter(name__icontains='Transport').first()
        leisure_cat = Category.objects.filter(name__icontains='Loisir').first()
        
        budgets_data = [
            {
                'category': food_cat,
                'monthly_limit': Decimal('500.00'),
                'period': 'MONTHLY'
            },
            {
                'category': transport_cat,
                'monthly_limit': Decimal('200.00'),
                'period': 'MONTHLY'
            },
            {
                'category': leisure_cat,
                'monthly_limit': Decimal('300.00'),
                'period': 'MONTHLY'
            }
        ]
        
        budgets = []
        for data in budgets_data:
            if data['category']:
                budget = Budget.objects.create(
                    user=user,
                    **data
                )
                budgets.append(budget)
        
        return budgets

    def generate_transactions(self, user, accounts):
        """Generate realistic transactions over 2 years with life events"""
        transactions = []
        
        # Get categories
        salary_cat = Category.objects.filter(type='INCOME', name__icontains='Salaire').first()
        bonus_cat = Category.objects.filter(type='INCOME', name__icontains='Prime').first()
        rent_cat = Category.objects.filter(type='EXPENSE', name__icontains='Logement').first()
        food_cat = Category.objects.filter(type='EXPENSE', name__icontains='Alimentation').first()
        transport_cat = Category.objects.filter(type='EXPENSE', name__icontains='Transport').first()
        leisure_cat = Category.objects.filter(type='EXPENSE', name__icontains='Loisir').first()
        health_cat = Category.objects.filter(type='EXPENSE', name__icontains='Santé').first()
        
        # Default categories if not found
        categories = {
            'salary': salary_cat or Category.objects.filter(type='INCOME').first(),
            'bonus': bonus_cat or Category.objects.filter(type='INCOME').first(),
            'rent': rent_cat or Category.objects.filter(type='EXPENSE').first(),
            'food': food_cat or Category.objects.filter(type='EXPENSE').first(),
            'transport': transport_cat or Category.objects.filter(type='EXPENSE').first(),
            'leisure': leisure_cat or Category.objects.filter(type='EXPENSE').first(),
            'health': health_cat or Category.objects.filter(type='EXPENSE').first(),
        }
        
        # Account mapping
        checking = accounts[0]  # Compte Courant
        savings = accounts[1]   # Livret A
        
        # Generate transactions for the last 2 years
        start_date = datetime.now() - timedelta(days=730)
        current_date = start_date
        
        # Life events calendar
        life_events = self.generate_life_events()
        
        while current_date <= datetime.now():
            # Monthly salary (around 28th of each month) - Reduced
            if current_date.day == 28:
                salary_amount = Decimal(str(random.uniform(2800, 3000)))
                transactions.append(Transaction(
                    user=user,
                    account=checking,
                    category=categories['salary'],
                    amount=salary_amount,
                    description=f"Salaire {current_date.strftime('%B %Y')}",
                    date=current_date,
                    is_recurring=True
                ))
            
            # Monthly rent (1st of each month) - Increased
            if current_date.day == 1:
                transactions.append(Transaction(
                    user=user,
                    account=checking,
                    category=categories['rent'],
                    amount=Decimal('1400.00'),
                    description=f"Loyer {current_date.strftime('%B %Y')}",
                    date=current_date,
                    is_recurring=True
                ))
            
            # Monthly fixed expenses
            if current_date.day == 5:  # Utilities, insurance, etc.
                transactions.append(Transaction(
                    user=user,
                    account=checking,
                    category=categories['rent'],
                    amount=Decimal(str(random.uniform(120, 180))),
                    description="Électricité + Gaz",
                    date=current_date,
                    is_recurring=True
                ))
                
            if current_date.day == 10:  # Internet, phone
                transactions.append(Transaction(
                    user=user,
                    account=checking,
                    category=categories['transport'],  # Services
                    amount=Decimal(str(random.uniform(60, 90))),
                    description="Internet + Mobile",
                    date=current_date,
                    is_recurring=True
                ))
                
            if current_date.day == 15:  # Insurance
                transactions.append(Transaction(
                    user=user,
                    account=checking,
                    category=categories['health'],
                    amount=Decimal(str(random.uniform(80, 120))),
                    description="Assurances (auto, habitation)",
                    date=current_date,
                    is_recurring=True
                ))
            
            # Check for life events
            event_key = current_date.strftime('%Y-%m-%d')
            if event_key in life_events:
                event = life_events[event_key]
                # Choose appropriate category and account based on event type
                if event['type'] == 'vacation':
                    account = checking
                    category = categories['leisure']
                elif event['type'] == 'appliance':
                    account = checking
                    category = categories['rent']  # Home expenses
                elif event['type'] == 'car_repair':
                    account = checking
                    category = categories['transport']
                elif event['type'] == 'medical':
                    account = checking
                    category = categories['health']
                else:
                    account = checking
                    category = categories['food']  # Default
                    
                transactions.append(Transaction(
                    user=user,
                    account=account,
                    category=category,
                    amount=event['amount'],
                    description=event['description'],
                    date=current_date,
                    is_recurring=False
                ))
            
            # Daily random expenses (more realistic patterns) - Increased frequency
            if random.random() < 0.9:  # 90% chance of daily expense
                self.add_daily_expenses(transactions, user, accounts, categories, current_date)
            
            # Reduced bonuses (only twice a year)
            if current_date.month in [6, 12] and current_date.day == 15:
                bonus_amount = Decimal(str(random.uniform(800, 1500)))
                transactions.append(Transaction(
                    user=user,
                    account=checking,
                    category=categories['bonus'],
                    amount=bonus_amount,
                    description=f"Prime semestrielle",
                    date=current_date,
                    is_recurring=False
                ))
            
            current_date += timedelta(days=1)
        
        # Bulk create all transactions
        Transaction.objects.bulk_create(transactions)
        return transactions

    def generate_life_events(self):
        """Generate special life events with significant financial impact"""
        events = {}
        
        # Major events over 2 years
        base_date = datetime.now() - timedelta(days=730)
        
        # Vacation expenses
        vacation_dates = [
            base_date + timedelta(days=120),  # 4 months ago
            base_date + timedelta(days=400),  # 13 months ago
            base_date + timedelta(days=600),  # 20 months ago
        ]
        
        for i, date in enumerate(vacation_dates):
            events[date.strftime('%Y-%m-%d')] = {
                'amount': Decimal(str(random.uniform(1200, 2500))),
                'description': f"Vacances été - Vol + hôtel",
                'type': 'vacation'
            }
        
        # Home repairs/appliances
        repair_dates = [
            base_date + timedelta(days=80),   # 2.5 months ago
            base_date + timedelta(days=300),  # 10 months ago
            base_date + timedelta(days=550),  # 18 months ago
        ]
        
        appliances = ['Réfrigérateur', 'Lave-linge', 'Lave-vaisselle']
        for i, date in enumerate(repair_dates):
            events[date.strftime('%Y-%m-%d')] = {
                'amount': Decimal(str(random.uniform(600, 1500))),
                'description': f"Remplacement {appliances[i]}",
                'type': 'appliance'
            }
        
        # Car repairs
        car_dates = [
            base_date + timedelta(days=200),  # 6.5 months ago
            base_date + timedelta(days=450),  # 15 months ago
        ]
        
        for date in car_dates:
            events[date.strftime('%Y-%m-%d')] = {
                'amount': Decimal(str(random.uniform(400, 1200))),
                'description': f"Réparation voiture - Garage",
                'type': 'car_repair'
            }
        
        # Medical expenses
        medical_dates = [
            base_date + timedelta(days=150),  # 5 months ago
            base_date + timedelta(days=350),  # 11.5 months ago
        ]
        
        for date in medical_dates:
            events[date.strftime('%Y-%m-%d')] = {
                'amount': Decimal(str(random.uniform(200, 800))),
                'description': f"Frais médicaux - Dentiste",
                'type': 'medical'
            }
        
        return events

    def add_daily_expenses(self, transactions, user, accounts, categories, date):
        """Add realistic daily expenses - Increased amounts"""
        checking = accounts[0]
        
        # Food expenses (more frequent and higher amounts)
        if random.random() < 0.8:  # 80% chance
            amount = Decimal(str(random.uniform(12, 65)))
            shops = ['Monoprix', 'Carrefour', 'Boulangerie', 'Marché', 'Franprix', 'Uber Eats', 'Deliveroo']
            transactions.append(Transaction(
                user=user,
                account=checking,
                category=categories['food'],
                amount=amount,
                description=f"Courses - {random.choice(shops)}",
                date=date,
                is_recurring=False
            ))
        
        # Transport (metro, uber, essence) - Higher amounts
        if random.random() < 0.4:  # 40% chance
            amount = Decimal(str(random.uniform(5, 75)))
            transports = ['Métro', 'Uber', 'Essence', 'Péage', 'Parking', 'Train']
            transactions.append(Transaction(
                user=user,
                account=checking,
                category=categories['transport'],
                amount=amount,
                description=f"{random.choice(transports)}",
                date=date,
                is_recurring=False
            ))
        
        # Leisure (restaurants, cinema, etc.) - Higher amounts and frequency
        if random.random() < 0.35:  # 35% chance
            amount = Decimal(str(random.uniform(20, 120)))
            activities = ['Restaurant', 'Cinéma', 'Bar', 'Concert', 'Théâtre', 'Livre', 'Shopping', 'Coiffeur']
            transactions.append(Transaction(
                user=user,
                account=checking,
                category=categories['leisure'],
                amount=amount,
                description=f"{random.choice(activities)}",
                date=date,
                is_recurring=False
            ))

    def show_summary(self):
        """Show a summary of created data"""
        self.stdout.write("\n📊 DATA SUMMARY:")
        self.stdout.write(f"Users: {User.objects.count()}")
        self.stdout.write(f"Accounts: {Account.objects.count()}")
        self.stdout.write(f"Assets: {Asset.objects.count()}")
        self.stdout.write(f"Categories: {Category.objects.count()}")
        self.stdout.write(f"Transactions: {Transaction.objects.count()}")
        self.stdout.write(f"Budgets: {Budget.objects.count()}")
        
        # Show transaction date range
        first_transaction = Transaction.objects.order_by('date').first()
        last_transaction = Transaction.objects.order_by('-date').first()
        if first_transaction and last_transaction:
            self.stdout.write(f"Transaction range: {first_transaction.date.strftime('%Y-%m-%d')} to {last_transaction.date.strftime('%Y-%m-%d')}")
        
        # Show total amounts
        from django.db.models import Sum
        total_income = Transaction.objects.filter(category__type='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0
        total_expenses = Transaction.objects.filter(category__type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0
        self.stdout.write(f"Total income: €{total_income:,.2f}")
        self.stdout.write(f"Total expenses: €{abs(total_expenses):,.2f}")
        self.stdout.write(f"Net savings: €{total_income + total_expenses:,.2f}")  # expenses are negative