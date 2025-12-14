from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Enum, ForeignKey,
    Integer, String, Text, Float, JSON, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class SplitType(str, enum.Enum):
    """Expense split type enumeration"""
    EQUAL = "EQUAL"
    PERCENTAGE = "PERCENTAGE"
    EXACT = "EXACT"
    SHARE = "SHARE"
    ADJUSTMENT = "ADJUSTMENT"
    SETTLEMENT = "SETTLEMENT"
    CURRENCY_CONVERSION = "CURRENCY_CONVERSION"


class User(Base):
    """User model - matches Prisma User"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    email_verified = Column(DateTime, nullable=True)
    image = Column(String(500), nullable=True)
    currency = Column(String(3), default="USD", nullable=False)
    preferred_language = Column(String(10), default="", nullable=False)
    banking_id = Column(String(255), nullable=True)
    obapi_provider_id = Column(String(255), nullable=True)
    # Store as JSON array instead of PostgreSQL array
    hidden_friend_ids = Column(JSON, default=list, nullable=False)
    # Notification preferences stored as JSON (nullable for MySQL compatibility)
    notification_preferences = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)

    # Relationships
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    added_expenses = relationship("Expense", foreign_keys="Expense.added_by", back_populates="added_by_user")
    paid_expenses = relationship("Expense", foreign_keys="Expense.paid_by", back_populates="paid_by_user")
    deleted_expenses = relationship("Expense", foreign_keys="Expense.deleted_by", back_populates="deleted_by_user")
    updated_expenses = relationship("Expense", foreign_keys="Expense.updated_by", back_populates="updated_by_user")
    expense_participants = relationship("ExpenseParticipant", back_populates="user")
    expense_notes = relationship("ExpenseNote", back_populates="created_by")
    groups = relationship("Group", back_populates="created_by")
    group_users = relationship("GroupUser", back_populates="user")
    cached_bank_data = relationship("CachedBankData", back_populates="user")


class Account(Base):
    """OAuth account model - matches Prisma Account"""
    __tablename__ = "accounts"

    id = Column(String(255), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)
    provider = Column(String(50), nullable=False)
    provider_account_id = Column(String(255), nullable=False)
    refresh_token = Column(Text, nullable=True)
    access_token = Column(Text, nullable=True)
    expires_at = Column(Integer, nullable=True)
    token_type = Column(String(50), nullable=True)
    scope = Column(String(500), nullable=True)
    id_token = Column(Text, nullable=True)
    session_state = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="accounts")

    __table_args__ = (
        UniqueConstraint("provider", "provider_account_id", name="provider_account_unique"),
    )


class Session(Base):
    """Session model - matches Prisma Session"""
    __tablename__ = "sessions"

    id = Column(String(255), primary_key=True)
    session_token = Column(String(255), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires = Column(DateTime, nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")


class VerificationToken(Base):
    """Email verification token - matches Prisma VerificationToken"""
    __tablename__ = "verification_tokens"

    identifier = Column(String(255), primary_key=True)
    token = Column(String(255), unique=True, nullable=False, primary_key=True)
    expires = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("identifier", "token", name="identifier_token_unique"),
    )


class Group(Base):
    """Group model - matches Prisma Group"""
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    public_id = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    default_currency = Column(String(3), default="USD", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    splitwise_group_id = Column(String(255), unique=True, nullable=True)
    simplify_debts = Column(Boolean, default=False, nullable=False)
    archived_at = Column(DateTime, nullable=True)

    # Relationships
    created_by = relationship("User", back_populates="groups")
    group_users = relationship("GroupUser", back_populates="group", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="group")


class GroupUser(Base):
    """Group membership - matches Prisma GroupUser"""
    __tablename__ = "group_users"

    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    # Relationships
    group = relationship("Group", back_populates="group_users")
    user = relationship("User", back_populates="group_users")


class Expense(Base):
    """Expense model - matches Prisma Expense"""
    __tablename__ = "expenses"

    id = Column(String(36), primary_key=True)  # UUID as string
    paid_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    added_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(500), nullable=False)
    category = Column(String(100), nullable=False)
    amount = Column(BigInteger, nullable=False)  # Stored in cents
    split_type = Column(Enum(SplitType), default=SplitType.EQUAL, nullable=False)
    expense_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    currency = Column(String(3), nullable=False)
    file_key = Column(String(500), nullable=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    transaction_id = Column(String(255), nullable=True)
    recurrence_id = Column(Integer, ForeignKey("expense_recurrences.id", ondelete="CASCADE"), nullable=True)
    conversion_to_id = Column(String(36), ForeignKey("expenses.id", ondelete="CASCADE"), unique=True, nullable=True)

    # Relationships
    paid_by_user = relationship("User", foreign_keys=[paid_by], back_populates="paid_expenses")
    added_by_user = relationship("User", foreign_keys=[added_by], back_populates="added_expenses")
    deleted_by_user = relationship("User", foreign_keys=[deleted_by], back_populates="deleted_expenses")
    updated_by_user = relationship("User", foreign_keys=[updated_by], back_populates="updated_expenses")
    group = relationship("Group", back_populates="expenses")
    expense_participants = relationship("ExpenseParticipant", back_populates="expense", cascade="all, delete-orphan")
    expense_notes = relationship("ExpenseNote", back_populates="expense", cascade="all, delete-orphan")
    recurrence = relationship("ExpenseRecurrence", back_populates="expenses")
    conversion_to = relationship("Expense", foreign_keys=[conversion_to_id], remote_side=[id], uselist=False)

    __table_args__ = (
        Index("idx_expense_group_id", "group_id"),
        Index("idx_expense_paid_by", "paid_by"),
    )


class ExpenseParticipant(Base):
    """Expense participant - matches Prisma ExpenseParticipant"""
    __tablename__ = "expense_participants"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    expense_id = Column(String(36), ForeignKey("expenses.id", ondelete="CASCADE"), primary_key=True)
    amount = Column(BigInteger, nullable=False)  # Stored in cents

    # Relationships
    user = relationship("User", back_populates="expense_participants")
    expense = relationship("Expense", back_populates="expense_participants")


class ExpenseNote(Base):
    """Expense note - matches Prisma ExpenseNote"""
    __tablename__ = "expense_notes"

    id = Column(String(255), primary_key=True)
    note = Column(Text, nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expense_id = Column(String(36), ForeignKey("expenses.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    created_by = relationship("User", back_populates="expense_notes")
    expense = relationship("Expense", back_populates="expense_notes")


class ExpenseRecurrence(Base):
    """Expense recurrence - matches Prisma ExpenseRecurrence"""
    __tablename__ = "expense_recurrences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(BigInteger, unique=True, nullable=False)
    notified = Column(Boolean, default=True, nullable=False)

    # Relationships
    expenses = relationship("Expense", back_populates="recurrence")


class Balance(Base):
    """Balance model - DEPRECATED, use BalanceView. Kept for data preservation"""
    __tablename__ = "balances"

    user_id = Column(Integer, primary_key=True)
    currency = Column(String(3), primary_key=True)
    friend_id = Column(Integer, primary_key=True)
    amount = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    imported_from_splitwise = Column(Boolean, default=False, nullable=False)


class GroupBalance(Base):
    """Group balance model - DEPRECATED, use BalanceView. Kept for data preservation"""
    __tablename__ = "group_balances"

    group_id = Column(Integer, primary_key=True)
    currency = Column(String(3), primary_key=True)
    user_id = Column(Integer, primary_key=True)
    firend_id = Column(Integer, primary_key=True)  # Note: typo preserved from Prisma schema
    amount = Column(BigInteger, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class BalanceView(Base):
    """
    Balance view model - calculated from expenses
    In MariaDB, this will be a regular table with triggers instead of a materialized view
    """
    __tablename__ = "balance_view"

    user_id = Column(Integer, primary_key=True)
    friend_id = Column(Integer, primary_key=True)
    group_id = Column(Integer, nullable=True, primary_key=True)
    currency = Column(String(3), primary_key=True)
    amount = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class CachedCurrencyRate(Base):
    """Cached currency exchange rates - matches Prisma CachedCurrencyRate"""
    __tablename__ = "cached_currency_rates"

    from_currency = Column("from", String(3), primary_key=True)
    to_currency = Column("to", String(3), primary_key=True)
    date = Column(DateTime, primary_key=True)
    rate = Column(Float, nullable=False)
    cached_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_fetched = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class CachedBankData(Base):
    """Cached bank transaction data - matches Prisma CachedBankData"""
    __tablename__ = "cached_bank_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    transaction_id = Column(String(255), nullable=False)
    account_id = Column(String(255), nullable=True)
    provider = Column(String(50), nullable=False)  # 'plaid' or 'gocardless'
    obapi_provider_id = Column(String(255), nullable=True)
    data = Column(Text, nullable=False)
    cached_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_fetched = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="cached_bank_data")


class PushNotification(Base):
    """Push notification subscription - matches Prisma PushNotification"""
    __tablename__ = "push_notifications"

    user_id = Column(Integer, primary_key=True)
    subscription = Column(Text, nullable=False)

