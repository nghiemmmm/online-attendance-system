"""add refresh token

Revision ID: d4e5f6a7b8c9
Revises: c1d2e3f4a5b6
Create Date: 2026-06-09 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


revision = "d4e5f6a7b8c9"
down_revision = "c1d2e3f4a5b6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "refresh_token",
        sa.Column("ma_refresh_token", sa.Integer(), nullable=False),
        sa.Column("ma_tai_khoan", sa.Integer(), nullable=False),
        sa.Column(
            "token_hash",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("last_used_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column(
            "user_agent",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=True,
        ),
        sa.Column(
            "ip_address",
            sqlmodel.sql.sqltypes.AutoString(length=45),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["ma_tai_khoan"], ["taikhoan.ma_tai_khoan"]),
        sa.PrimaryKeyConstraint("ma_refresh_token"),
    )
    op.create_index(
        op.f("ix_refresh_token_expires_at"),
        "refresh_token",
        ["expires_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_refresh_token_ma_tai_khoan"),
        "refresh_token",
        ["ma_tai_khoan"],
        unique=False,
    )
    op.create_index(
        op.f("ix_refresh_token_revoked_at"),
        "refresh_token",
        ["revoked_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_refresh_token_token_hash"),
        "refresh_token",
        ["token_hash"],
        unique=True,
    )


def downgrade():
    op.drop_index(op.f("ix_refresh_token_token_hash"), table_name="refresh_token")
    op.drop_index(op.f("ix_refresh_token_revoked_at"), table_name="refresh_token")
    op.drop_index(op.f("ix_refresh_token_ma_tai_khoan"), table_name="refresh_token")
    op.drop_index(op.f("ix_refresh_token_expires_at"), table_name="refresh_token")
    op.drop_table("refresh_token")
