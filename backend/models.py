"""SQLAlchemy ORM models matching the Dukaan Dost PostgreSQL schema."""

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Identity,
    Index,
    Integer,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Shop(Base):
    __tablename__ = "shops"

    id: Mapped[int] = mapped_column(Integer, Identity(always=False), primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("CURRENT_TIMESTAMP::text")
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, Identity(always=False), primary_key=True)
    google_sub: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    picture: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''"))
    shop_id: Mapped[int] = mapped_column(
        ForeignKey("shops.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    created_at: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("CURRENT_TIMESTAMP::text")
    )


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    token_hash: Mapped[str] = mapped_column(Text, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    expires_at: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[int] = mapped_column(Integer, nullable=False)


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id: Mapped[int] = mapped_column(Integer, Identity(always=False), primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    action: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("CURRENT_TIMESTAMP::text")
    )


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("id", "shop_id"),)

    id: Mapped[int] = mapped_column(Integer, Identity(always=False), primary_key=True)
    shop_id: Mapped[int] = mapped_column(
        ForeignKey("shops.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)


class Item(Base):
    __tablename__ = "items"
    __table_args__ = (
        UniqueConstraint("shop_id", "name", "category_id"),
        ForeignKeyConstraint(
            ["category_id", "shop_id"],
            ["categories.id", "categories.shop_id"],
            ondelete="RESTRICT",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=False), primary_key=True)
    shop_id: Mapped[int] = mapped_column(
        ForeignKey("shops.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, nullable=False)


class RestockItem(Base):
    __tablename__ = "restock_items"
    __table_args__ = (
        UniqueConstraint("shop_id", "name", "category_id"),
        ForeignKeyConstraint(
            ["category_id", "shop_id"],
            ["categories.id", "categories.shop_id"],
            ondelete="RESTRICT",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=False), primary_key=True)
    shop_id: Mapped[int] = mapped_column(
        ForeignKey("shops.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, nullable=False)


class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = (
        UniqueConstraint("id", "shop_id"),
        CheckConstraint("total_paise >= 0", name="customers_total_paise_check"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=False), primary_key=True)
    shop_id: Mapped[int] = mapped_column(
        ForeignKey("shops.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    total_paise: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))


class CreditRecord(Base):
    __tablename__ = "credit_records"
    __table_args__ = (
        CheckConstraint("amount_paise > 0", name="credit_records_amount_paise_check"),
        ForeignKeyConstraint(
            ["customer_id", "shop_id"],
            ["customers.id", "customers.shop_id"],
            ondelete="RESTRICT",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=False), primary_key=True)
    shop_id: Mapped[int] = mapped_column(
        ForeignKey("shops.id", ondelete="CASCADE"), nullable=False
    )
    customer_id: Mapped[int] = mapped_column(Integer, nullable=False)
    amount_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    entry_date: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''"))


Index("uq_categories_shop_name_ci", Category.shop_id, func.lower(Category.name), unique=True)
Index("uq_customers_shop_name_ci", Customer.shop_id, func.lower(Customer.name), unique=True)
Index("idx_items_shop_category", Item.shop_id, Item.category_id)
Index("idx_restock_shop_category", RestockItem.shop_id, RestockItem.category_id)
Index("idx_credit_shop_customer_date", CreditRecord.shop_id, CreditRecord.customer_id, CreditRecord.entry_date)
Index("idx_auth_sessions_user", AuthSession.user_id)
Index("idx_agent_logs_user_created", AgentLog.user_id, AgentLog.created_at.desc(), AgentLog.id.desc())
