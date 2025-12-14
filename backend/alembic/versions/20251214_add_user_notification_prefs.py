"""Add notification_preferences and created_at to users

Revision ID: add_user_notification_prefs
Revises: 20251211_171422_initial_migration_create_all_tables
Create Date: 2024-12-14

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'add_user_notification_prefs'
down_revision = '20251211_171422_initial_migration_create_all_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add notification_preferences column (JSON)
    # MySQL/MariaDB doesn't support default for JSON, so we use nullable=True
    # and handle defaults in application code
    op.add_column('users', sa.Column(
        'notification_preferences',
        sa.JSON(),
        nullable=True
    ))

    # Add created_at column
    op.add_column('users', sa.Column(
        'created_at',
        sa.DateTime(),
        nullable=True,
        server_default=sa.text('CURRENT_TIMESTAMP')
    ))


def downgrade() -> None:
    op.drop_column('users', 'notification_preferences')
    op.drop_column('users', 'created_at')

