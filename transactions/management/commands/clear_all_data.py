from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from transactions.models import Transaction, Budget
from core.models import Asset, Account, Category

User = get_user_model()

class Command(BaseCommand):
    help = 'Clear all data from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force deletion without confirmation',
        )

    def handle(self, *args, **options):
        if not options['force']:
            response = input("This will delete ALL data (transactions, budgets, assets, accounts, users). Are you sure? (type 'DELETE' to confirm): ")
            if response != 'DELETE':
                self.stdout.write("Operation cancelled.")
                return

        self.stdout.write("Starting database cleanup...")
        
        # Count before deletion
        transaction_count = Transaction.objects.count()
        budget_count = Budget.objects.count()
        asset_count = Asset.objects.count()
        account_count = Account.objects.count()
        user_count = User.objects.count()
        category_count = Category.objects.count()
        
        self.stdout.write(f"Before deletion:")
        self.stdout.write(f"  Transactions: {transaction_count}")
        self.stdout.write(f"  Budgets: {budget_count}")
        self.stdout.write(f"  Assets: {asset_count}")
        self.stdout.write(f"  Accounts: {account_count}")
        self.stdout.write(f"  Users: {user_count}")
        self.stdout.write(f"  Categories: {category_count}")
        
        # Delete all data in order (respecting foreign key constraints)
        Transaction.objects.all().delete()
        Budget.objects.all().delete()
        Asset.objects.all().delete()
        Account.objects.all().delete()
        User.objects.all().delete()
        # Don't delete categories as they are needed for the system
        
        self.stdout.write(self.style.SUCCESS("✅ All data deleted successfully!"))
        self.stdout.write("Categories were preserved for system functionality.")