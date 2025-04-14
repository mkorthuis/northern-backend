"""State Safety Tables

Revision ID: 7ed3c152c0c3
Revises: 6ed3c152c0c2
Create Date: 2024-06-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
import logging

# Configure logger
logger = logging.getLogger('alembic.runtime.migration')

# revision identifiers, used by Alembic.
revision = '7ed3c152c0c3'
down_revision = '6ed3c152c0c2'
branch_labels = None
depends_on = None


def upgrade():
    """Create the state-level safety tables."""
    logger.info("Starting State Safety Tables migration upgrade")

    # Create state_truancy table
    logger.info("Creating state_truancy table")
    op.execute("""
        CREATE TABLE state_truancy (
            id SERIAL PRIMARY KEY,
            year INTEGER NOT NULL,
            count INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT unique_state_truancy
                UNIQUE (year)
        )
    """)

    # Create state_safety table
    logger.info("Creating state_safety table")
    op.execute("""
        CREATE TABLE state_safety (
            id SERIAL PRIMARY KEY,
            year INTEGER NOT NULL,
            school_safety_type_id_fk INTEGER NOT NULL,
            count INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_state_safety_type
                FOREIGN KEY (school_safety_type_id_fk)
                REFERENCES school_safety_type(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_state_safety
                UNIQUE (year, school_safety_type_id_fk)
        )
    """)

    # Create state_discipline_incident table
    logger.info("Creating state_discipline_incident table")
    op.execute("""
        CREATE TABLE state_discipline_incident (
            id SERIAL PRIMARY KEY,
            year INTEGER NOT NULL,
            school_discipline_incident_type_id_fk INTEGER NOT NULL,
            count INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_state_discipline_incident_type
                FOREIGN KEY (school_discipline_incident_type_id_fk)
                REFERENCES school_discipline_incident_type(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_state_discipline_incident
                UNIQUE (year, school_discipline_incident_type_id_fk)
        )
    """)

    # Create state_discipline_count table
    logger.info("Creating state_discipline_count table")
    op.execute("""
        CREATE TABLE state_discipline_count (
            id SERIAL PRIMARY KEY,
            year INTEGER NOT NULL,
            school_discipline_count_type_id_fk INTEGER NOT NULL,
            count INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_state_discipline_count_type
                FOREIGN KEY (school_discipline_count_type_id_fk)
                REFERENCES school_discipline_count_type(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_state_discipline_count
                UNIQUE (year, school_discipline_count_type_id_fk)
        )
    """)

    # Create state_bullying table
    logger.info("Creating state_bullying table")
    op.execute("""
        CREATE TABLE state_bullying (
            id SERIAL PRIMARY KEY,
            year INTEGER NOT NULL,
            school_bullying_type_id_fk INTEGER NOT NULL,
            reported INTEGER,
            investigated_actual INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_state_bullying_type
                FOREIGN KEY (school_bullying_type_id_fk)
                REFERENCES school_bullying_type(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_state_bullying
                UNIQUE (year, school_bullying_type_id_fk)
        )
    """)

    # Create state_bullying_classification table
    logger.info("Creating state_bullying_classification table")
    op.execute("""
        CREATE TABLE state_bullying_classification (
            id SERIAL PRIMARY KEY,
            year INTEGER NOT NULL,
            school_bullying_classification_type_id_fk INTEGER NOT NULL,
            count INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_state_bullying_classification_type
                FOREIGN KEY (school_bullying_classification_type_id_fk)
                REFERENCES school_bullying_classification_type(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_state_bullying_classification
                UNIQUE (year, school_bullying_classification_type_id_fk)
        )
    """)

    # Create state_bullying_impact table
    logger.info("Creating state_bullying_impact table")
    op.execute("""
        CREATE TABLE state_bullying_impact (
            id SERIAL PRIMARY KEY,
            year INTEGER NOT NULL,
            school_bullying_impact_type_id_fk INTEGER NOT NULL,
            count INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_state_bullying_impact_type
                FOREIGN KEY (school_bullying_impact_type_id_fk)
                REFERENCES school_bullying_impact_type(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_state_bullying_impact
                UNIQUE (year, school_bullying_impact_type_id_fk)
        )
    """)

    # Create state_harassment table
    logger.info("Creating state_harassment table")
    op.execute("""
        CREATE TABLE state_harassment (
            id SERIAL PRIMARY KEY,
            year INTEGER NOT NULL,
            school_harassment_classification_id_fk INTEGER NOT NULL,
            incident_count INTEGER,
            student_impact_count INTEGER,
            student_engaged_count INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_state_harassment_classification
                FOREIGN KEY (school_harassment_classification_id_fk)
                REFERENCES school_harassment_classification(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_state_harassment
                UNIQUE (year, school_harassment_classification_id_fk)
        )
    """)

    # Create state_restraint table
    logger.info("Creating state_restraint table")
    op.execute("""
        CREATE TABLE state_restraint (
            id SERIAL PRIMARY KEY,
            year INTEGER NOT NULL,
            generated INTEGER,
            active_investigation INTEGER,
            closed_investigation INTEGER,
            bodily_injury INTEGER,
            serious_injury INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT unique_state_restraint
                UNIQUE (year)
        )
    """)

    # Create state_seclusion table
    logger.info("Creating state_seclusion table")
    op.execute("""
        CREATE TABLE state_seclusion (
            id SERIAL PRIMARY KEY,
            year INTEGER NOT NULL,
            generated INTEGER,
            active_investigation INTEGER,
            closed_investigation INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT unique_state_seclusion
                UNIQUE (year)
        )
    """)

    # Create triggers for all tables
    logger.info("Creating triggers for tables")
    tables_for_triggers = [
        'state_truancy',
        'state_safety',
        'state_discipline_incident',
        'state_discipline_count',
        'state_bullying',
        'state_bullying_classification',
        'state_bullying_impact',
        'state_harassment',
        'state_restraint',
        'state_seclusion'
    ]

    for table in tables_for_triggers:
        op.execute(f"""
            CREATE TRIGGER trigger_update_{table}_timestamp
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION update_date_updated_column()
        """)

    # Create indexes
    logger.info("Creating indexes for tables")
    indexes = [
        "CREATE INDEX idx_state_truancy_year ON state_truancy(year)",
        "CREATE INDEX idx_state_safety_year ON state_safety(year)",
        "CREATE INDEX idx_state_safety_type ON state_safety(school_safety_type_id_fk)",
        "CREATE INDEX idx_state_discipline_incident_year ON state_discipline_incident(year)",
        "CREATE INDEX idx_state_discipline_incident_type ON state_discipline_incident(school_discipline_incident_type_id_fk)",
        "CREATE INDEX idx_state_discipline_count_year ON state_discipline_count(year)",
        "CREATE INDEX idx_state_discipline_count_type ON state_discipline_count(school_discipline_count_type_id_fk)",
        "CREATE INDEX idx_state_bullying_year ON state_bullying(year)",
        "CREATE INDEX idx_state_bullying_type ON state_bullying(school_bullying_type_id_fk)",
        "CREATE INDEX idx_state_bullying_classification_year ON state_bullying_classification(year)",
        "CREATE INDEX idx_state_bullying_classification_type ON state_bullying_classification(school_bullying_classification_type_id_fk)",
        "CREATE INDEX idx_state_bullying_impact_year ON state_bullying_impact(year)",
        "CREATE INDEX idx_state_bullying_impact_type ON state_bullying_impact(school_bullying_impact_type_id_fk)",
        "CREATE INDEX idx_state_harassment_year ON state_harassment(year)",
        "CREATE INDEX idx_state_harassment_classification ON state_harassment(school_harassment_classification_id_fk)",
        "CREATE INDEX idx_state_restraint_year ON state_restraint(year)",
        "CREATE INDEX idx_state_seclusion_year ON state_seclusion(year)"
    ]

    for index in indexes:
        op.execute(index)

    logger.info("State Safety Tables migration upgrade completed successfully")


def downgrade():
    """Drop the state safety tables."""
    logger.info("Starting State Safety Tables migration downgrade")

    # Drop tables in reverse order to handle dependencies
    tables_to_drop = [
        'state_seclusion',
        'state_restraint',
        'state_harassment',
        'state_bullying_impact',
        'state_bullying_classification',
        'state_bullying',
        'state_discipline_count',
        'state_discipline_incident',
        'state_safety',
        'state_truancy'
    ]

    for table in tables_to_drop:
        logger.info(f"Dropping table {table}")
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")

    logger.info("State Safety Tables migration downgrade completed successfully") 