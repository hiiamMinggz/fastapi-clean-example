"""
Ensures imperative SQLAlchemy mappings are initialized at application startup.

### Purpose:
In Clean Architecture, domain entities remain agnostic of database
mappings. To integrate with SQLAlchemy, mappings must be explicitly
triggered to link ORM attributes to domain classes. Without this setup,
attempts to interact with unmapped entities in database operations
will lead to runtime errors.

### Solution:
This module provides a single entry point to initialize the mapping
of domain entities to database tables. By calling the `map_tables` function,
ORM attributes are linked to domain classes without altering domain code
or introducing infrastructure concerns.

### Usage:
Call the `map_tables` function in the application factory to initialize
mappings at startup. Additionally, it is necessary to call this function
in `env.py` for Alembic migrations to ensure all models are available
during database migrations.
"""

from app.infrastructure.persistence_sqla.mappings.auth_session import (
    map_auth_sessions_table,
)
from app.infrastructure.persistence_sqla.mappings.streamer import (
    map_streamers_table,
)
from app.infrastructure.persistence_sqla.mappings.transaction import (
    map_transactions_table,
)
from app.infrastructure.persistence_sqla.mappings.ledger_entry import (
    map_ledger_entries_table,
)
from app.infrastructure.persistence_sqla.mappings.user import map_users_table
from app.infrastructure.persistence_sqla.mappings.challenge import map_challenges_table
from app.infrastructure.persistence_sqla.mappings.wallet import map_wallets_table


def map_tables() -> None:
    map_users_table()
    map_streamers_table()
    map_ledger_entries_table()
    map_transactions_table()
    map_auth_sessions_table()
    map_challenges_table()
    map_wallets_table()
