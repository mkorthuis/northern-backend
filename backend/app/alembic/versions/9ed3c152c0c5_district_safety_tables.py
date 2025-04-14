"""District Safety Tables

Revision ID: 9ed3c152c0c5
Revises: 8ed3c152c0c4
Create Date: 2024-06-03 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
import logging

# Configure logger
logger = logging.getLogger('alembic.runtime.migration')

# revision identifiers, used by Alembic.
revision = '9ed3c152c0c5'
down_revision = '8ed3c152c0c4'
branch_labels = None
depends_on = None


def upgrade():
    """Create the district-level safety tables."""
    logger.info("Starting District Safety Tables migration upgrade")

    # Create district_truancy table
    logger.info("Creating district_truancy table")
    op.execute("""
        CREATE TABLE district_truancy (
            id SERIAL PRIMARY KEY,
            district_id_fk INTEGER NOT NULL,
            year INTEGER NOT NULL,
            count INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_district_truancy
                FOREIGN KEY (district_id_fk)
                REFERENCES district(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_district_truancy
                UNIQUE (district_id_fk, year)
        )
    """)

    # Create district_safety table
    logger.info("Creating district_safety table")
    op.execute("""
        CREATE TABLE district_safety (
            id SERIAL PRIMARY KEY,
            district_id_fk INTEGER NOT NULL,
            year INTEGER NOT NULL,
            school_safety_type_id_fk INTEGER NOT NULL,
            count INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_district_safety
                FOREIGN KEY (district_id_fk)
                REFERENCES district(id)
                ON DELETE CASCADE,
            CONSTRAINT fk_district_safety_type
                FOREIGN KEY (school_safety_type_id_fk)
                REFERENCES school_safety_type(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_district_safety
                UNIQUE (district_id_fk, year, school_safety_type_id_fk)
        )
    """)

    # Create district_discipline_incident table
    logger.info("Creating district_discipline_incident table")
    op.execute("""
        CREATE TABLE district_discipline_incident (
            id SERIAL PRIMARY KEY,
            district_id_fk INTEGER NOT NULL,
            year INTEGER NOT NULL,
            school_discipline_incident_type_id_fk INTEGER NOT NULL,
            count INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_district_discipline_incident
                FOREIGN KEY (district_id_fk)
                REFERENCES district(id)
                ON DELETE CASCADE,
            CONSTRAINT fk_district_discipline_incident_type
                FOREIGN KEY (school_discipline_incident_type_id_fk)
                REFERENCES school_discipline_incident_type(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_district_discipline_incident
                UNIQUE (district_id_fk, year, school_discipline_incident_type_id_fk)
        )
    """)

    # Create district_discipline_count table
    logger.info("Creating district_discipline_count table")
    op.execute("""
        CREATE TABLE district_discipline_count (
            id SERIAL PRIMARY KEY,
            district_id_fk INTEGER NOT NULL,
            year INTEGER NOT NULL,
            school_discipline_count_type_id_fk INTEGER NOT NULL,
            count INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_district_discipline_count
                FOREIGN KEY (district_id_fk)
                REFERENCES district(id)
                ON DELETE CASCADE,
            CONSTRAINT fk_district_discipline_count_type
                FOREIGN KEY (school_discipline_count_type_id_fk)
                REFERENCES school_discipline_count_type(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_district_discipline_count
                UNIQUE (district_id_fk, year, school_discipline_count_type_id_fk)
        )
    """)

    # Create district_bullying table
    logger.info("Creating district_bullying table")
    op.execute("""
        CREATE TABLE district_bullying (
            id SERIAL PRIMARY KEY,
            district_id_fk INTEGER NOT NULL,
            year INTEGER NOT NULL,
            school_bullying_type_id_fk INTEGER NOT NULL,
            reported INTEGER,
            investigated_actual INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_district_bullying
                FOREIGN KEY (district_id_fk)
                REFERENCES district(id)
                ON DELETE CASCADE,
            CONSTRAINT fk_district_bullying_type
                FOREIGN KEY (school_bullying_type_id_fk)
                REFERENCES school_bullying_type(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_district_bullying
                UNIQUE (district_id_fk, year, school_bullying_type_id_fk)
        )
    """)

    # Create district_bullying_classification table
    logger.info("Creating district_bullying_classification table")
    op.execute("""
        CREATE TABLE district_bullying_classification (
            id SERIAL PRIMARY KEY,
            district_id_fk INTEGER NOT NULL,
            year INTEGER NOT NULL,
            school_bullying_classification_type_id_fk INTEGER NOT NULL,
            count INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_district_bullying_classification
                FOREIGN KEY (district_id_fk)
                REFERENCES district(id)
                ON DELETE CASCADE,
            CONSTRAINT fk_district_bullying_classification_type
                FOREIGN KEY (school_bullying_classification_type_id_fk)
                REFERENCES school_bullying_classification_type(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_district_bullying_classification
                UNIQUE (district_id_fk, year, school_bullying_classification_type_id_fk)
        )
    """)

    # Create district_bullying_impact table
    logger.info("Creating district_bullying_impact table")
    op.execute("""
        CREATE TABLE district_bullying_impact (
            id SERIAL PRIMARY KEY,
            district_id_fk INTEGER NOT NULL,
            year INTEGER NOT NULL,
            school_bullying_impact_type_id_fk INTEGER NOT NULL,
            count INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_district_bullying_impact
                FOREIGN KEY (district_id_fk)
                REFERENCES district(id)
                ON DELETE CASCADE,
            CONSTRAINT fk_district_bullying_impact_type
                FOREIGN KEY (school_bullying_impact_type_id_fk)
                REFERENCES school_bullying_impact_type(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_district_bullying_impact
                UNIQUE (district_id_fk, year, school_bullying_impact_type_id_fk)
        )
    """)

    # Create district_harassment table
    logger.info("Creating district_harassment table")
    op.execute("""
        CREATE TABLE district_harassment (
            id SERIAL PRIMARY KEY,
            district_id_fk INTEGER NOT NULL,
            year INTEGER NOT NULL,
            school_harassment_classification_id_fk INTEGER NOT NULL,
            incident_count INTEGER,
            student_impact_count INTEGER,
            student_engaged_count INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_district_harassment
                FOREIGN KEY (district_id_fk)
                REFERENCES district(id)
                ON DELETE CASCADE,
            CONSTRAINT fk_district_harassment_classification
                FOREIGN KEY (school_harassment_classification_id_fk)
                REFERENCES school_harassment_classification(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_district_harassment
                UNIQUE (district_id_fk, year, school_harassment_classification_id_fk)
        )
    """)

    # Create district_restraint table
    logger.info("Creating district_restraint table")
    op.execute("""
        CREATE TABLE district_restraint (
            id SERIAL PRIMARY KEY,
            district_id_fk INTEGER NOT NULL,
            year INTEGER NOT NULL,
            generated INTEGER,
            active_investigation INTEGER,
            closed_investigation INTEGER,
            bodily_injury INTEGER,
            serious_injury INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_district_restraint
                FOREIGN KEY (district_id_fk)
                REFERENCES district(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_district_restraint
                UNIQUE (district_id_fk, year)
        )
    """)

    # Create district_seclusion table
    logger.info("Creating district_seclusion table")
    op.execute("""
        CREATE TABLE district_seclusion (
            id SERIAL PRIMARY KEY,
            district_id_fk INTEGER NOT NULL,
            year INTEGER NOT NULL,
            generated INTEGER,
            active_investigation INTEGER,
            closed_investigation INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_district_seclusion
                FOREIGN KEY (district_id_fk)
                REFERENCES district(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_district_seclusion
                UNIQUE (district_id_fk, year)
        )
    """)

    # Create triggers for all tables
    logger.info("Creating triggers for tables")
    tables_for_triggers = [
        'district_truancy',
        'district_safety',
        'district_discipline_incident',
        'district_discipline_count',
        'district_bullying',
        'district_bullying_classification',
        'district_bullying_impact',
        'district_harassment',
        'district_restraint',
        'district_seclusion'
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
        "CREATE INDEX idx_district_truancy_district ON district_truancy(district_id_fk)",
        "CREATE INDEX idx_district_truancy_year ON district_truancy(year)",
        "CREATE INDEX idx_district_safety_district ON district_safety(district_id_fk)",
        "CREATE INDEX idx_district_safety_year ON district_safety(year)",
        "CREATE INDEX idx_district_safety_type ON district_safety(school_safety_type_id_fk)",
        "CREATE INDEX idx_district_discipline_incident_district ON district_discipline_incident(district_id_fk)",
        "CREATE INDEX idx_district_discipline_incident_year ON district_discipline_incident(year)",
        "CREATE INDEX idx_district_discipline_incident_type ON district_discipline_incident(school_discipline_incident_type_id_fk)",
        "CREATE INDEX idx_district_discipline_count_district ON district_discipline_count(district_id_fk)",
        "CREATE INDEX idx_district_discipline_count_year ON district_discipline_count(year)",
        "CREATE INDEX idx_district_discipline_count_type ON district_discipline_count(school_discipline_count_type_id_fk)",
        "CREATE INDEX idx_district_bullying_district ON district_bullying(district_id_fk)",
        "CREATE INDEX idx_district_bullying_year ON district_bullying(year)",
        "CREATE INDEX idx_district_bullying_type ON district_bullying(school_bullying_type_id_fk)",
        "CREATE INDEX idx_district_bullying_classification_district ON district_bullying_classification(district_id_fk)",
        "CREATE INDEX idx_district_bullying_classification_year ON district_bullying_classification(year)",
        "CREATE INDEX idx_district_bullying_classification_type ON district_bullying_classification(school_bullying_classification_type_id_fk)",
        "CREATE INDEX idx_district_bullying_impact_district ON district_bullying_impact(district_id_fk)",
        "CREATE INDEX idx_district_bullying_impact_year ON district_bullying_impact(year)",
        "CREATE INDEX idx_district_bullying_impact_type ON district_bullying_impact(school_bullying_impact_type_id_fk)",
        "CREATE INDEX idx_district_harassment_district ON district_harassment(district_id_fk)",
        "CREATE INDEX idx_district_harassment_year ON district_harassment(year)",
        "CREATE INDEX idx_district_harassment_classification ON district_harassment(school_harassment_classification_id_fk)",
        "CREATE INDEX idx_district_restraint_district ON district_restraint(district_id_fk)",
        "CREATE INDEX idx_district_restraint_year ON district_restraint(year)",
        "CREATE INDEX idx_district_seclusion_district ON district_seclusion(district_id_fk)",
        "CREATE INDEX idx_district_seclusion_year ON district_seclusion(year)"
    ]

    for index in indexes:
        op.execute(index)

    logger.info("District Safety Tables migration upgrade completed successfully")


def downgrade():
    """Drop the district safety tables."""
    logger.info("Starting District Safety Tables migration downgrade")

    # Drop tables in reverse order to handle dependencies
    tables_to_drop = [
        'district_seclusion',
        'district_restraint',
        'district_harassment',
        'district_bullying_impact',
        'district_bullying_classification',
        'district_bullying',
        'district_discipline_count',
        'district_discipline_incident',
        'district_safety',
        'district_truancy'
    ]

    for table in tables_to_drop:
        logger.info(f"Dropping table {table}")
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")

    logger.info("District Safety Tables migration downgrade completed successfully") 