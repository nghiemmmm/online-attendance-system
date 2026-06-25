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
            sa.Column("ma_tai_khoan", sa.Integer(), nullable=True),
            sa.Column("vai_tro", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True),
            sa.Column("hanh_dong", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
            sa.Column("doi_tuong", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
            sa.Column("doi_tuong_id", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
            sa.Column("du_lieu_truoc", sa.JSON(), nullable=True),
            sa.Column("du_lieu_sau", sa.JSON(), nullable=True),
            sa.Column("ip", sqlmodel.sql.sqltypes.AutoString(length=45), nullable=True),
            sa.Column("user_agent", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
            sa.Column("trang_thai", sqlmodel.sql.sqltypes.AutoString(length=30), nullable=False),
            sa.Column("chi_tiet", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
            sa.Column("ma_audit_log", sa.Integer(), nullable=False),
            sa.Column("thoi_gian", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["ma_tai_khoan"], ["taikhoan.ma_tai_khoan"]),
            sa.PrimaryKeyConstraint("ma_audit_log"),
        )
        inspector = sa.inspect(bind)

    if not _index_exists(inspector, "auditlog", "ix_auditlog_thoi_gian"):
        op.create_index(op.f("ix_auditlog_thoi_gian"), "auditlog", ["thoi_gian"], unique=False)

    if not _column_exists(inspector, "anhdiemdanh", "do_tin_cay"):
        op.add_column("anhdiemdanh", sa.Column("do_tin_cay", sa.Float(), nullable=True))

    if not _column_exists(inspector, "anhkhuonmat", "diem_chat_luong"):
        op.add_column("anhkhuonmat", sa.Column("diem_chat_luong", sa.Float(), nullable=True))

    if not _column_exists(inspector, "anhkhuonmat", "trang_thai_duyet"):
        op.add_column(
            "anhkhuonmat",
            sa.Column(
                "trang_thai_duyet",
                sqlmodel.sql.sqltypes.AutoString(length=30),
                nullable=False,
                server_default="CHO_DUYET",
            ),
        )
        op.alter_column("anhkhuonmat", "trang_thai_duyet", server_default=None)

    if not _column_exists(inspector, "anhkhuonmat", "ly_do_tu_choi"):
        op.add_column(
            "anhkhuonmat",
            sa.Column("ly_do_tu_choi", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        )

    if not _column_exists(inspector, "anhkhuonmat", "ma_nguoi_duyet"):
        op.add_column("anhkhuonmat", sa.Column("ma_nguoi_duyet", sa.Integer(), nullable=True))

    if not _column_exists(inspector, "anhkhuonmat", "thoi_gian_duyet"):
        op.add_column("anhkhuonmat", sa.Column("thoi_gian_duyet", sa.DateTime(), nullable=True))

    inspector = sa.inspect(bind)
    if not _fk_exists(inspector, "anhkhuonmat", "fk_anhkhuonmat_ma_nguoi_duyet_taikhoan"):
        op.create_foreign_key(
            "fk_anhkhuonmat_ma_nguoi_duyet_taikhoan",
            "anhkhuonmat",
            "taikhoan",
            ["ma_nguoi_duyet"],
            ["ma_tai_khoan"],
        )


def downgrade():
    op.drop_constraint(
        "fk_anhkhuonmat_ma_nguoi_duyet_taikhoan",
        "anhkhuonmat",
        type_="foreignkey",
    )
    op.drop_column("anhkhuonmat", "thoi_gian_duyet")
    op.drop_column("anhkhuonmat", "ma_nguoi_duyet")
    op.drop_column("anhkhuonmat", "ly_do_tu_choi")
    op.drop_column("anhkhuonmat", "trang_thai_duyet")
    op.drop_column("anhkhuonmat", "diem_chat_luong")
    op.drop_column("anhdiemdanh", "do_tin_cay")
    op.drop_index(op.f("ix_auditlog_thoi_gian"), table_name="auditlog")
    op.drop_table("auditlog")
