"""State Safety Data Migration

Revision ID: 8ed3c152c0c4
Revises: 7ed3c152c0c3
Create Date: 2024-06-02 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
import logging

# Configure logger
logger = logging.getLogger('alembic.runtime.migration')

# revision identifiers, used by Alembic.
revision = '8ed3c152c0c4'
down_revision = '7ed3c152c0c3'
branch_labels = None
depends_on = None


def upgrade():
    """Generate data for state safety tables by aggregating school-level data."""
    logger.info("Starting State Safety Data migration upgrade")

    # Generate state truancy data
    logger.info("Generating state_truancy data")
    op.execute("""
        INSERT INTO state_truancy (year, count)
        SELECT 
            year, 
            SUM(count) as count
        FROM 
            school_truancy
        GROUP BY 
            year;
    """)

    # Generate state safety data
    logger.info("Generating state_safety data")
    op.execute("""
        INSERT INTO state_safety (year, school_safety_type_id_fk, count)
        SELECT 
            year, 
            school_safety_type_id_fk,
            SUM(count) as count
        FROM 
            school_safety
        GROUP BY 
            year, school_safety_type_id_fk;
    """)

    # Generate state discipline incident data
    logger.info("Generating state_discipline_incident data")
    op.execute("""
        INSERT INTO state_discipline_incident (year, school_discipline_incident_type_id_fk, count)
        SELECT 
            year, 
            school_discipline_incident_type_id_fk,
            SUM(count) as count
        FROM 
            school_discipline_incident
        GROUP BY 
            year, school_discipline_incident_type_id_fk;
    """)

    # Generate state discipline count data
    logger.info("Generating state_discipline_count data")
    op.execute("""
        INSERT INTO state_discipline_count (year, school_discipline_count_type_id_fk, count)
        SELECT 
            year, 
            school_discipline_count_type_id_fk,
            SUM(count) as count
        FROM 
            school_discipline_count
        GROUP BY 
            year, school_discipline_count_type_id_fk;
    """)

    # Generate state bullying data
    logger.info("Generating state_bullying data")
    op.execute("""
        INSERT INTO state_bullying (year, school_bullying_type_id_fk, reported, investigated_actual)
        SELECT 
            year, 
            school_bullying_type_id_fk,
            SUM(reported) as reported,
            SUM(investigated_actual) as investigated_actual
        FROM 
            school_bullying
        GROUP BY 
            year, school_bullying_type_id_fk;
    """)

    # Generate state bullying classification data
    logger.info("Generating state_bullying_classification data")
    op.execute("""
        INSERT INTO state_bullying_classification (year, school_bullying_classification_type_id_fk, count)
        SELECT 
            year, 
            school_bullying_classification_type_id_fk,
            SUM(count) as count
        FROM 
            school_bullying_classification
        GROUP BY 
            year, school_bullying_classification_type_id_fk;
    """)

    # Generate state bullying impact data
    logger.info("Generating state_bullying_impact data")
    op.execute("""
        INSERT INTO state_bullying_impact (year, school_bullying_impact_type_id_fk, count)
        SELECT 
            year, 
            school_bullying_impact_type_id_fk,
            SUM(count) as count
        FROM 
            school_bullying_impact
        GROUP BY 
            year, school_bullying_impact_type_id_fk;
    """)

    # Generate state harassment data
    logger.info("Generating state_harassment data")
    op.execute("""
        INSERT INTO state_harassment (
            year, 
            school_harassment_classification_id_fk, 
            incident_count, 
            student_impact_count, 
            student_engaged_count
        )
        SELECT 
            year, 
            school_harassment_classification_id_fk,
            SUM(incident_count) as incident_count,
            SUM(student_impact_count) as student_impact_count,
            SUM(student_engaged_count) as student_engaged_count
        FROM 
            school_harassment
        GROUP BY 
            year, school_harassment_classification_id_fk;
    """)

    # Generate state restraint data
    logger.info("Generating state_restraint data")
    op.execute("""
        INSERT INTO state_restraint (
            year, 
            generated, 
            active_investigation, 
            closed_investigation, 
            bodily_injury, 
            serious_injury
        )
        SELECT 
            year, 
            SUM(generated) as generated,
            SUM(active_investigation) as active_investigation,
            SUM(closed_investigation) as closed_investigation,
            SUM(bodily_injury) as bodily_injury,
            SUM(serious_injury) as serious_injury
        FROM 
            school_restraint
        GROUP BY 
            year;
    """)

    # Generate state seclusion data
    logger.info("Generating state_seclusion data")
    op.execute("""
        INSERT INTO state_seclusion (
            year, 
            generated, 
            active_investigation, 
            closed_investigation
        )
        SELECT 
            year, 
            SUM(generated) as generated,
            SUM(active_investigation) as active_investigation,
            SUM(closed_investigation) as closed_investigation
        FROM 
            school_seclusion
        GROUP BY 
            year;
    """)

    logger.info("State Safety Data migration completed successfully")


def downgrade():
    """Remove all state safety data."""
    logger.info("Starting State Safety Data migration downgrade")

    # List of tables to clear
    tables_to_clear = [
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

    # Clear each table
    for table in tables_to_clear:
        logger.info(f"Clearing data from table {table}")
        op.execute(f"DELETE FROM {table};")

    logger.info("State Safety Data migration downgrade completed successfully") 