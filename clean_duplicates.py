#!/usr/bin/env python3
"""
Script to clean duplicate transactions in the database
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to the Python path
sys.path.append('/Users/slucas/Library/Mobile Documents/com~apple~CloudDocs/Projects/FinTrack/fintrack-api')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fintrack.settings')
django.setup()

from django.db.models import Count
from transactions.models import Transaction
from django.contrib.auth.models import User

def clean_duplicate_transactions():
    """Clean duplicate transactions based on description, amount, date, and user"""
    
    print("Starting duplicate transaction cleanup...")
    
    # Find all transactions with duplicates
    duplicates = Transaction.objects.values(
        'description', 'amount', 'date', 'user'
    ).annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    total_duplicates = duplicates.count()
    print(f"Found {total_duplicates} sets of duplicate transactions")
    
    if total_duplicates == 0:
        print("No duplicates found.")
        return
    
    # Count total transactions before cleanup
    total_before = Transaction.objects.count()
    print(f"Total transactions before cleanup: {total_before}")
    
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
            print(f"Deleting {len(transactions_to_delete)} duplicates of: {duplicate['description']} - {duplicate['amount']}€")
            
            for transaction in transactions_to_delete:
                transaction.delete()
                deleted_count += 1
    
    total_after = Transaction.objects.count()
    print(f"Total transactions after cleanup: {total_after}")
    print(f"Deleted {deleted_count} duplicate transactions")
    print("Cleanup completed!")

def show_transaction_stats():
    """Show transaction statistics by user"""
    print("\n--- Transaction Statistics ---")
    
    for user in User.objects.all():
        count = Transaction.objects.filter(user=user).count()
        print(f"User {user.username}: {count} transactions")
    
    total = Transaction.objects.count()
    print(f"Total transactions: {total}")

if __name__ == "__main__":
    show_transaction_stats()
    
    # Ask for confirmation before deleting
    response = input("\nDo you want to proceed with duplicate cleanup? (y/N): ")
    if response.lower() == 'y':
        clean_duplicate_transactions()
        print("\n--- After Cleanup ---")
        show_transaction_stats()
    else:
        print("Cleanup cancelled.")