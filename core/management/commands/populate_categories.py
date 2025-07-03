from django.core.management.base import BaseCommand
from core.models import Category, CategoryType


class Command(BaseCommand):
    help = 'Populate default categories'

    def handle(self, *args, **options):
        default_categories = [
            # Income categories
            {'name': 'Salaire', 'icon': '💼', 'color': '#10B981', 'type': CategoryType.INCOME},
            {'name': 'Freelance', 'icon': '💻', 'color': '#059669', 'type': CategoryType.INCOME},
            {'name': 'Investissements', 'icon': '📈', 'color': '#047857', 'type': CategoryType.INCOME},
            {'name': 'Autres revenus', 'icon': '💰', 'color': '#065F46', 'type': CategoryType.INCOME},
            
            # Expense categories
            {'name': 'Alimentation', 'icon': '🍕', 'color': '#EF4444', 'type': CategoryType.EXPENSE},
            {'name': 'Transport', 'icon': '🚗', 'color': '#F97316', 'type': CategoryType.EXPENSE},
            {'name': 'Logement', 'icon': '🏠', 'color': '#8B5CF6', 'type': CategoryType.EXPENSE},
            {'name': 'Santé', 'icon': '🏥', 'color': '#EC4899', 'type': CategoryType.EXPENSE},
            {'name': 'Loisirs', 'icon': '🎬', 'color': '#3B82F6', 'type': CategoryType.EXPENSE},
            {'name': 'Shopping', 'icon': '🛍️', 'color': '#F59E0B', 'type': CategoryType.EXPENSE},
            {'name': 'Éducation', 'icon': '📚', 'color': '#6366F1', 'type': CategoryType.EXPENSE},
            {'name': 'Services', 'icon': '⚡', 'color': '#84CC16', 'type': CategoryType.EXPENSE},
            {'name': 'Autres dépenses', 'icon': '📦', 'color': '#6B7280', 'type': CategoryType.EXPENSE},
        ]

        created_count = 0
        for cat_data in default_categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                user=None,  # Default categories have no user
                defaults={
                    'icon': cat_data['icon'],
                    'color': cat_data['color'],
                    'type': cat_data['type'],
                    'is_default': True,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created default category: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} default categories')
        )