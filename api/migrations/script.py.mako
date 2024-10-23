"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from api.logging_config import setup_logging
from alembic import op
import sqlalchemy as sa
from api.migrations import custom_downgrade, table_exists
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}

logger = setup_logging(__name__)

def upgrade() -> None:
% if upgrades:
    if table_exists(table_name, schema_name):
        logger.info(f"Table {schema_name}.{table_name} already exists. Skipping.")
    else:
        ${upgrades}
% endif
% if not upgrades:
    pass
% endif


def downgrade() -> None:
    ${"custom_downgrade(table_name, schema_name)" if downgrades else "pass"}
