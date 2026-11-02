"""Create the initial Dukaan Dost schema."""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shops",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("created_at", sa.Text(), server_default=sa.text("CURRENT_TIMESTAMP::text"), nullable=False),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), primary_key=True),
        sa.Column("google_sub", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("picture", sa.Text(), server_default=sa.text("''"), nullable=False),
        sa.Column("shop_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.Text(), server_default=sa.text("CURRENT_TIMESTAMP::text"), nullable=False),
        sa.ForeignKeyConstraint(["shop_id"], ["shops.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("google_sub"),
        sa.UniqueConstraint("shop_id"),
    )
    op.create_table(
        "auth_sessions",
        sa.Column("token_hash", sa.Text(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "agent_logs",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("created_at", sa.Text(), server_default=sa.text("CURRENT_TIMESTAMP::text"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), primary_key=True),
        sa.Column("shop_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["shop_id"], ["shops.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("id", "shop_id"),
    )
    op.create_table(
        "items",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), primary_key=True),
        sa.Column("shop_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["shop_id"], ["shops.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["category_id", "shop_id"], ["categories.id", "categories.shop_id"], ondelete="RESTRICT"
        ),
        sa.UniqueConstraint("shop_id", "name", "category_id"),
    )
    op.create_table(
        "restock_items",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), primary_key=True),
        sa.Column("shop_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["shop_id"], ["shops.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["category_id", "shop_id"], ["categories.id", "categories.shop_id"], ondelete="RESTRICT"
        ),
        sa.UniqueConstraint("shop_id", "name", "category_id"),
    )
    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), primary_key=True),
        sa.Column("shop_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("total_paise", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.CheckConstraint("total_paise >= 0", name="customers_total_paise_check"),
        sa.ForeignKeyConstraint(["shop_id"], ["shops.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("id", "shop_id"),
    )
    op.create_table(
        "credit_records",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), primary_key=True),
        sa.Column("shop_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("amount_paise", sa.Integer(), nullable=False),
        sa.Column("entry_date", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), server_default=sa.text("''"), nullable=False),
        sa.CheckConstraint("amount_paise > 0", name="credit_records_amount_paise_check"),
        sa.ForeignKeyConstraint(["shop_id"], ["shops.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["customer_id", "shop_id"], ["customers.id", "customers.shop_id"], ondelete="RESTRICT"
        ),
    )
    op.create_index("uq_categories_shop_name_ci", "categories", ["shop_id", sa.text("lower(name)")], unique=True)
    op.create_index("uq_customers_shop_name_ci", "customers", ["shop_id", sa.text("lower(name)")], unique=True)
    op.create_index("idx_items_shop_category", "items", ["shop_id", "category_id"])
    op.create_index("idx_restock_shop_category", "restock_items", ["shop_id", "category_id"])
    op.create_index("idx_credit_shop_customer_date", "credit_records", ["shop_id", "customer_id", "entry_date"])
    op.create_index("idx_auth_sessions_user", "auth_sessions", ["user_id"])
    op.create_index(
        "idx_agent_logs_user_created",
        "agent_logs",
        ["user_id", sa.text("created_at DESC"), sa.text("id DESC")],
    )


def downgrade() -> None:
    op.drop_index("idx_agent_logs_user_created", table_name="agent_logs")
    op.drop_index("idx_auth_sessions_user", table_name="auth_sessions")
    op.drop_index("idx_credit_shop_customer_date", table_name="credit_records")
    op.drop_index("idx_restock_shop_category", table_name="restock_items")
    op.drop_index("idx_items_shop_category", table_name="items")
    op.drop_index("uq_customers_shop_name_ci", table_name="customers")
    op.drop_index("uq_categories_shop_name_ci", table_name="categories")
    op.drop_table("credit_records")
    op.drop_table("customers")
    op.drop_table("restock_items")
    op.drop_table("items")
    op.drop_table("categories")
    op.drop_table("agent_logs")
    op.drop_table("auth_sessions")
    op.drop_table("users")
    op.drop_table("shops")
