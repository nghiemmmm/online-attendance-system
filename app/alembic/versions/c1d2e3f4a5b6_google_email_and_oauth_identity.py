"""google email and oauth identity

Revision ID: c1d2e3f4a5b6
Revises: b98e053e8981
Create Date: 2026-06-09 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = "c1d2e3f4a5b6"
down_revision = "b98e053e8981"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("sinhvien", "email", new_column_name="google_email")
    op.alter_column("canbo", "email", new_column_name="google_email")

    op.create_table(
        "oauth_identity",
        sa.Column("ma_oauth_identity", sa.Integer(), nullable=False),
        sa.Column(
            "provider",
            sqlmodel.sql.sqltypes.AutoString(length=30),
            nullable=False,
        ),
        sa.Column(
            "provider_subject",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=False,
        ),
        sa.Column(
            "email",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=False,
        ),
        sa.Column("ma_tai_khoan", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["ma_tai_khoan"], ["taikhoan.ma_tai_khoan"]),
        sa.PrimaryKeyConstraint("ma_oauth_identity"),
        sa.UniqueConstraint(
            "provider",
            "provider_subject",
            name="uq_oauth_identity_provider_subject",
        ),
    )
    op.create_index(
        op.f("ix_oauth_identity_email"),
        "oauth_identity",
        ["email"],
        unique=False,
    )
    op.create_index(
        op.f("ix_oauth_identity_ma_tai_khoan"),
        "oauth_identity",
        ["ma_tai_khoan"],
        unique=False,
    )
    op.create_index(
        op.f("ix_oauth_identity_provider"),
        "oauth_identity",
        ["provider"],
        unique=False,
    )
    op.create_index(
        op.f("ix_oauth_identity_provider_subject"),
        "oauth_identity",
        ["provider_subject"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_oauth_identity_provider_subject"),
        table_name="oauth_identity",
    )
    op.drop_index(op.f("ix_oauth_identity_provider"), table_name="oauth_identity")
    op.drop_index(
        op.f("ix_oauth_identity_ma_tai_khoan"),
        table_name="oauth_identity",
    )
    op.drop_index(op.f("ix_oauth_identity_email"), table_name="oauth_identity")
    op.drop_table("oauth_identity")

    op.alter_column("canbo", "google_email", new_column_name="email")
    op.alter_column("sinhvien", "google_email", new_column_name="email")
