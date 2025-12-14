"""
Splitwise import service
Handles importing expenses from Splitwise CSV export
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import csv
import io

from app.models.models import User, Group, GroupUser, Balance, Expense, ExpenseParticipant
from app.core.config import settings


class SplitwiseImportService:
    """Service for importing data from Splitwise CSV export"""

    async def import_from_csv(
        self,
        db: Session,
        user_id: int,
        csv_content: str
    ) -> Dict[str, int]:
        """
        Import expenses from Splitwise CSV export

        Splitwise CSV format columns:
        Date, Description, Category, Cost, Currency, [User1], [User2], ...

        Args:
            db: Database session
            user_id: Current user ID
            csv_content: CSV file content as string

        Returns:
            Dictionary with import statistics
        """
        stats = {
            'groups_imported': 0,
            'friends_imported': 0,
            'balances_imported': 0,
            'expenses_imported': 0,
            'rows_processed': 0,
            'errors': []
        }

        try:
            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            rows = list(csv_reader)

            if not rows:
                stats['errors'].append("CSV file is empty or invalid")
                return stats

            # Get column names - find user columns (columns after Currency)
            fieldnames = csv_reader.fieldnames or []
            standard_cols = ['Date', 'Description', 'Category', 'Cost', 'Currency']
            user_columns = [col for col in fieldnames if col not in standard_cols and col.strip()]

            # Get current user
            current_user = db.query(User).filter(User.id == user_id).first()
            if not current_user:
                stats['errors'].append("Current user not found")
                return stats

            # Track users by name
            user_map: Dict[str, User] = {}

            # Try to match current user to a column
            current_user_column = None
            for col in user_columns:
                col_lower = col.lower().strip()
                if current_user.name and current_user.name.lower() in col_lower:
                    current_user_column = col
                    user_map[col] = current_user
                    break
                if current_user.email and current_user.email.lower().split('@')[0] in col_lower:
                    current_user_column = col
                    user_map[col] = current_user
                    break

            # If no match found, use first column as current user
            if not current_user_column and user_columns:
                current_user_column = user_columns[0]
                user_map[current_user_column] = current_user

            # Create/find other users
            for col in user_columns:
                if col not in user_map:
                    # Check if user exists by name
                    user = db.query(User).filter(User.name == col.strip()).first()
                    if not user:
                        # Create placeholder user
                        user = User(
                            email=f"{col.lower().replace(' ', '_')}@imported.sahasplit",
                            name=col.strip(),
                            currency=current_user.currency or 'USD',
                            preferred_language='en'
                        )
                        db.add(user)
                        db.flush()
                        stats['friends_imported'] += 1
                    user_map[col] = user

            # Commit user creation before processing expenses
            db.commit()

            # Process each row
            for row in rows:
                stats['rows_processed'] += 1
                try:
                    await self._process_expense_row(db, user_id, row, user_map, current_user_column, stats)
                    db.commit()  # Commit each expense individually
                except Exception as e:
                    db.rollback()  # Rollback on error
                    stats['errors'].append(f"Row {stats['rows_processed']}: {str(e)}")

        except Exception as e:
            db.rollback()
            stats['errors'].append(f"CSV parsing error: {str(e)}")

        return stats

    async def _process_expense_row(
        self,
        db: Session,
        user_id: int,
        row: Dict,
        user_map: Dict[str, User],
        current_user_column: Optional[str],
        stats: Dict
    ):
        """
        Process a single expense row from Splitwise CSV

        Splitwise CSV format:
        - Positive value in user column = they paid (are owed money)
        - Negative value in user column = they owe money
        - The person with the highest positive value is the payer
        """
        from nanoid import generate as nanoid

        # Skip empty or total rows
        description = row.get('Description', '').strip()
        if not description or description.lower() in ['total', 'total balance', '']:
            return

        # Skip empty date rows
        date_str = row.get('Date', '').strip()
        if not date_str:
            return

        # Parse date
        try:
            expense_date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            try:
                expense_date = datetime.strptime(date_str, '%m/%d/%Y')
            except ValueError:
                expense_date = datetime.now()

        # Parse total cost
        cost_str = row.get('Cost', '0').strip().replace(',', '')
        try:
            cost = float(cost_str)
        except ValueError:
            cost = 0.0

        if cost == 0:
            return

        currency = row.get('Currency', 'USD').strip() or 'USD'
        category = row.get('Category', 'General').strip() or 'General'

        # Convert to cents (paisa for INR)
        amount_cents = int(round(cost * 100))

        # Parse user values to find payer and participants
        user_values = []
        for col_name, user in user_map.items():
            value_str = row.get(col_name, '0').strip().replace(',', '')
            try:
                value = float(value_str)
            except ValueError:
                value = 0.0

            if value != 0:
                user_values.append({
                    'user': user,
                    'value': value,
                    'value_cents': int(round(value * 100))
                })

        if not user_values:
            return

        # Find the payer (person with highest positive value)
        payers = [uv for uv in user_values if uv['value'] > 0]
        if not payers:
            return  # No one paid, skip this row

        # The person with the highest positive value is the payer
        payer_data = max(payers, key=lambda x: x['value'])
        paid_by_user = payer_data['user']

        # Find people who owe (negative values)
        owes = [uv for uv in user_values if uv['value'] < 0]

        if not owes:
            return  # No one owes, skip (might be a settlement)

        # Create expense
        expense = Expense(
            id=nanoid(size=12),
            name=description,
            amount=amount_cents,
            currency=currency,
            category=self._map_category(category),
            split_type='EXACT',
            paid_by=paid_by_user.id,
            added_by=user_id,
            expense_date=expense_date,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(expense)
        db.flush()

        # Create expense participants for everyone involved
        all_participants = user_values
        for pdata in all_participants:
            participant_user = pdata['user']
            # Store the absolute share amount for each participant
            # Calculate share based on their portion
            share_amount = abs(pdata['value_cents'])

            participant = ExpenseParticipant(
                expense_id=expense.id,
                user_id=participant_user.id,
                amount=share_amount
            )
            db.add(participant)

        # Update balances for people who owe
        for owe_data in owes:
            owe_user = owe_data['user']
            owed_amount = abs(owe_data['value_cents'])

            if owe_user.id != paid_by_user.id:
                # owe_user owes paid_by_user
                await self._update_balance(db, owe_user.id, paid_by_user.id, currency, owed_amount)
                # paid_by_user is owed by owe_user (negative from their perspective)
                await self._update_balance(db, paid_by_user.id, owe_user.id, currency, -owed_amount)
                stats['balances_imported'] += 1

        stats['expenses_imported'] += 1

    async def _update_balance(
        self,
        db: Session,
        user_id: int,
        friend_id: int,
        currency: str,
        amount: int
    ):
        """Update or create a balance record"""
        balance = db.query(Balance).filter(
            Balance.user_id == user_id,
            Balance.friend_id == friend_id,
            Balance.currency == currency
        ).first()

        if balance:
            balance.amount += amount
        else:
            balance = Balance(
                user_id=user_id,
                friend_id=friend_id,
                currency=currency,
                amount=amount
            )
            db.add(balance)

    def _map_category(self, splitwise_category: str) -> str:
        """Map Splitwise category to SAHASplit category"""
        category_map = {
            'food and drink': 'food',
            'groceries': 'groceries',
            'dining out': 'food',
            'restaurants': 'food',
            'entertainment': 'entertainment',
            'movies': 'entertainment',
            'music': 'entertainment',
            'games': 'entertainment',
            'sports': 'sports',
            'home': 'home',
            'household supplies': 'home',
            'rent': 'rent',
            'mortgage': 'rent',
            'utilities': 'utilities',
            'electricity': 'utilities',
            'gas': 'utilities',
            'water': 'utilities',
            'internet': 'utilities',
            'phone': 'utilities',
            'transportation': 'transport',
            'parking': 'transport',
            'car': 'transport',
            'gas': 'fuel',
            'fuel': 'fuel',
            'bus/train': 'transport',
            'taxi': 'transport',
            'uber': 'transport',
            'plane': 'travel',
            'travel': 'travel',
            'hotel': 'travel',
            'life': 'other',
            'clothing': 'shopping',
            'gifts': 'gifts',
            'medical': 'medical',
            'insurance': 'other',
            'taxes': 'other',
            'education': 'other',
            'pets': 'pets',
            'general': 'other',
            'uncategorized': 'other',
        }
        return category_map.get(splitwise_category.lower().strip(), 'other')

    # Keep the old JSON method for backward compatibility
    async def import_groups_and_balances(
        self,
        db: Session,
        user_id: int,
        splitwise_data: Dict
    ) -> Dict[str, int]:
        """Legacy JSON import method"""
        stats = {
            'groups_imported': 0,
            'friends_imported': 0,
            'balances_imported': 0,
            'expenses_imported': 0,
            'errors': ['JSON import is deprecated. Please use CSV export from Splitwise.']
        }
        return stats


# Global service instance
splitwise_import_service = SplitwiseImportService()

