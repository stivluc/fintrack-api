from django.core.management.base import BaseCommand
from django.db.models import Count
from transactions.models import Transaction
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Clean duplicate transactions in the database'

    def handle(self, *args, **options):
        self.stdout.write("Starting duplicate transaction cleanup...")
        
        # Find all transactions with duplicates
        duplicates = Transaction.objects.values(
            'description', 'amount', 'date', 'user'
        ).annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        total_duplicates = duplicates.count()
        self.stdout.write(f"Found {total_duplicates} sets of duplicate transactions")
        
        if total_duplicates == 0:
            self.stdout.write("No duplicates found.")
            return
        
        # Count total transactions before cleanup
        total_before = Transaction.objects.count()
        self.stdout.write(f"Total transactions before cleanup: {total_before}")
        
        deleted_count = 0
        
        for duplicate in duplicates:
            # Get all transactions matching this duplicate pattern
            matching_transactions = Transaction.objects.filter(
                description=duplicate['description'],
                amount=duplicate['amount'],
                date=duplicate['date'],
                user=duplicate['user']
            ).order_by('created_at')
            
            # Keep the first one (oldest), delete the rest
            transactions_to_delete = matching_transactions[1:]
            
            if transactions_to_delete:
                self.stdout.write(f"Deleting {len(transactions_to_delete)} duplicates of: {duplicate['description']} - {duplicate['amount']}€")
                
                for transaction in transactions_to_delete:
                    transaction.delete()
                    deleted_count += 1
        
        total_after = Transaction.objects.count()
        self.stdout.write(f"Total transactions after cleanup: {total_after}")
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted_count} duplicate transactions"))
        
        # Show transaction statistics by user
        self.stdout.write("\n--- Transaction Statistics ---")
        
        for user in User.objects.all():
            count = Transaction.objects.filter(user=user).count()
            self.stdout.write(f"User {user.username}: {count} transactions")
        
        total = Transaction.objects.count()
        self.stdout.write(f"Total transactions: {total}")