from sqlalchemy import text

from alembic import op


def add_enum_values(enum_name: str, values: list[str]):
    for value in values:
        op.execute(
            text(f"ALTER TYPE {enum_name} ADD VALUE IF NOT EXISTS :value").bindparams(
                value=value
            )
        )
