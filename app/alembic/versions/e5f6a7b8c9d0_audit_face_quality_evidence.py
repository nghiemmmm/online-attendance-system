"""audit log, face quality and attendance evidence

Revision ID: e5f6a7b8c9d0
Revises: af1a6e05955d
Create Date: 2026-06-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


revision = "e5f6a7b8c9d0"
down_revision = "af1a6e05955d"
branch_labels = None
depends_on = None


def _table_exists(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _column_exists(inspector, table_name: str, column_name: str) -> bool:
    if not _table_exists(inspector, table_name):
        return False
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _index_exists(inspector, table_name: str, index_name: str) -> bool:
    if not _table_exists(inspector, table_name):
        return False
    return index_name in {index["name"] for index in inspector.get_indexes(table_name)}


def _fk_exists(inspector, table_name: str, fk_name: str) -> bool:
    if not _table_exists(inspector, table_name):
        return False
    return fk_name in {fk["name"] for fk in inspector.get_foreign_keys(table_name)}


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _table_exists(inspector, "auditlog"):
        op.create_table(
            "auditlog",
            sa.Column("account_id", sa.Integer(), nullable=True),
            sa.Column("role", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True),
            sa.Column("action", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
            sa.Column("target_type", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
            sa.Column("target_id", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
            sa.Column("before_data", sa.JSON(), nullable=True),
            sa.Column("after_data", sa.JSON(), nullable=True),
            sa.Column("ip", sqlmodel.sql.sqltypes.AutoString(length=45), nullable=True),
            sa.Column("user_agent", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
            sa.Column("status", sqlmodel.sql.sqltypes.AutoString(length=30), nullable=False),
            sa.Column("detail", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
            sa.Column("audit_log_id", sa.Integer(), nullable=False),
            sa.Column("timestamp", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["account_id"], ["accounts.account_id"]),
            sa.PrimaryKeyConstraint("audit_log_id"),
        )
        inspector = sa.inspect(bind)

    if not _index_exists(inspector, "auditlog", "ix_auditlog_thoi_gian"):
        op.create_index(op.f("ix_auditlog_thoi_gian"), "auditlog", ["timestamp"], unique=False)

    if not _column_exists(inspector, "attendance_images", "confidence"):
        op.add_column("attendance_images", sa.Column("confidence", sa.Float(), nullable=True))

    if not _column_exists(inspector, "face_images", "quality_score"):
        op.add_column("face_images", sa.Column("quality_score", sa.Float(), nullable=True))

    if not _column_exists(inspector, "face_images", "review_status"):
        op.add_column(
            "face_images",
            sa.Column(
                "review_status",
                sqlmodel.sql.sqltypes.AutoString(length=30),
                nullable=False,
                server_default="CHO_DUYET",
            ),
        )
        op.alter_column("face_images", "review_status", server_default=None)

    if not _column_exists(inspector, "face_images", "rejection_reason"):
        op.add_column(
            "face_images",
            sa.Column("rejection_reason", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        )

    if not _column_exists(inspector, "face_images", "reviewer_id"):
        op.add_column("face_images", sa.Column("reviewer_id", sa.Integer(), nullable=True))

    if not _column_exists(inspector, "face_images", "reviewed_at"):
        op.add_column("face_images", sa.Column("reviewed_at", sa.DateTime(), nullable=True))

    inspector = sa.inspect(bind)
    if not _fk_exists(inspector, "face_images", "fk_anhkhuonmat_ma_nguoi_duyet_taikhoan"):
        op.create_foreign_key(
            "fk_anhkhuonmat_ma_nguoi_duyet_taikhoan",
            "face_images",
            "accounts",
            ["reviewer_id"],
            ["account_id"],
        )


def downgrade():
    op.drop_constraint(
        "fk_anhkhuonmat_ma_nguoi_duyet_taikhoan",
        "face_images",
        type_="foreignkey",
    )
    op.drop_column("face_images", "reviewed_at")
    op.drop_column("face_images", "reviewer_id")
    op.drop_column("face_images", "rejection_reason")
    op.drop_column("face_images", "review_status")
    op.drop_column("face_images", "quality_score")
    op.drop_column("attendance_images", "confidence")
    op.drop_index(op.f("ix_auditlog_thoi_gian"), table_name="auditlog")
    op.drop_table("auditlog")
