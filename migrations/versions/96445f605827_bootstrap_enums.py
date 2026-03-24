"""bootstrap enums

Revision ID: 96445f605827
Revises: 499f7f88cfe5
Create Date: 2026-02-04 23:53:10.526586

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "96445f605827"
down_revision: Union[str, Sequence[str], None] = "499f7f88cfe5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'flight_free_agent_cadence_enum'
        ) THEN
            CREATE TYPE flight_free_agent_cadence_enum AS ENUM (
                'WEEKLY',
                'BIWEEKLY',
                'MONTHLY',
                'OCCASIONALLY'
            );
        END IF;
    END
    $$;
    """)
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'golfer_affiliation_enum'
        ) THEN
            CREATE TYPE golfer_affiliation_enum AS ENUM (
                'APL_EMPLOYEE',
                'APL_RETIREE',
                'APL_FAMILY',
                'NON_APL_EMPLOYEE'
            );
        END IF;
    END
    $$;
    """)
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'committee_enum'
        ) THEN
            CREATE TYPE committee_enum AS ENUM (
                'LEAGUE',
                'EXECUTIVE',
                'RULES',
                'TOURNAMENT',
                'BANQUET_AND_AWARDS',
                'PUBLICITY',
                'PLANNING'
            );
        END IF;
    END
    $$;
    """)
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'league_dues_type_enum'
        ) THEN
            CREATE TYPE league_dues_type_enum AS ENUM (
                'FLIGHT_DUES',
                'TOURNAMENT_ONLY_DUES'
            );
        END IF;
    END
    $$;
    """)
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'payment_method_enum'
        ) THEN
            CREATE TYPE payment_method_enum AS ENUM (
                'CASH_OR_CHECK',
                'PAYPAL',
                'EXEMPT',
                'LINKED'
            );
        END IF;
    END
    $$;
    """)
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'tournament_entry_fee_type_enum'
        ) THEN
            CREATE TYPE tournament_entry_fee_type_enum AS ENUM (
                'MEMBER_FEE',
                'NON_MEMBER_FEE'
            );
        END IF;
    END
    $$;
    """)
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'qualifying_score_type_enum'
        ) THEN
            CREATE TYPE qualifying_score_type_enum AS ENUM (
                'QUALIFYING_ROUND',
                'OFFICIAL_HANDICAP_INDEX'
            );
        END IF;
    END
    $$;
    """)
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'round_type_enum'
        ) THEN
            CREATE TYPE round_type_enum AS ENUM (
                'QUALIFYING',
                'FLIGHT',
                'PLAYOFF',
                'TOURNAMENT'
            );
        END IF;
    END
    $$;
    """)
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'scoring_type_enum'
        ) THEN
            CREATE TYPE scoring_type_enum AS ENUM (
                'INDIVIDUAL',
                'GROUP'
            );
        END IF;
    END
    $$;
    """)
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'team_role_enum'
        ) THEN
            CREATE TYPE team_role_enum AS ENUM (
                'CAPTAIN',
                'PLAYER',
                'SUBSTITUTE'
            );
        END IF;
    END
    $$;
    """)
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'tee_gender_enum'
        ) THEN
            CREATE TYPE tee_gender_enum AS ENUM (
                'MENS',
                'LADIES'
            );
        END IF;
    END
    $$;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass  # enums are not safely droppable
