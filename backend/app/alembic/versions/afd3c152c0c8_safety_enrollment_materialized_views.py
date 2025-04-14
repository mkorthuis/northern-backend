"""Safety Enrollment Materialized Views

Revision ID: afd3c152c0c8
Revises: bed3c152c0c7
Create Date: 2024-07-10 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
import logging

# Configure logger
logger = logging.getLogger('alembic.runtime.migration')

# revision identifiers, used by Alembic.
revision = 'afd3c152c0c8'
down_revision = 'bed3c152c0c7'
branch_labels = None
depends_on = None


def upgrade():
    """Create materialized views for safety enrollment data at different levels."""
    logger.info("Starting Safety Enrollment Materialized Views migration upgrade")

    # Create school_safety_enrollment materialized view
    logger.info("Creating school_safety_enrollment materialized view")
    op.execute("""
        CREATE MATERIALIZED VIEW school_safety_enrollment AS
        SELECT
            se.school_id_fk, 
            se.year, 
            SUM(se.enrollment) AS total_enrollment
        FROM
            school_enrollment se
        WHERE
            se.school_id_fk IN (
                SELECT
                    sr.school_id_fk
                FROM
                    school_restraint sr
                GROUP BY 
                    sr.school_id_fk
            )
        GROUP BY 
            se.school_id_fk, 
            se.year
    """)

    # Add index for school_safety_enrollment
    logger.info("Creating index for school_safety_enrollment")
    op.execute("""
        CREATE INDEX idx_school_safety_enrollment_school_year 
        ON school_safety_enrollment (school_id_fk, year)
    """)

    # Create state_safety_enrollment materialized view
    logger.info("Creating state_safety_enrollment materialized view")
    op.execute("""
        CREATE MATERIALIZED VIEW state_safety_enrollment AS
        SELECT
            se.year, 
            SUM(se.enrollment) AS total_enrollment
        FROM
            school_enrollment se
        WHERE
            se.school_id_fk IN (
                SELECT
                    sr.school_id_fk
                FROM
                    school_restraint sr
                GROUP BY 
                    sr.school_id_fk
            )
        GROUP BY 
            se.year
    """)

    # Add index for state_safety_enrollment
    logger.info("Creating index for state_safety_enrollment")
    op.execute("""
        CREATE INDEX idx_state_safety_enrollment_year 
        ON state_safety_enrollment (year)
    """)

    # Create district_safety_enrollment materialized view
    logger.info("Creating district_safety_enrollment materialized view")
    op.execute("""
        CREATE MATERIALIZED VIEW district_safety_enrollment AS
        SELECT
            s.district_id_fk,
            se.year, 
            SUM(se.enrollment) AS total_enrollment
        FROM
            school_enrollment se
            JOIN school s ON se.school_id_fk = s.id
        WHERE
            se.school_id_fk IN (
                SELECT
                    sr.school_id_fk
                FROM
                    school_restraint sr
                GROUP BY 
                    sr.school_id_fk
            )
        GROUP BY 
            s.district_id_fk, 
            se.year
    """)

    # Add index for district_safety_enrollment
    logger.info("Creating index for district_safety_enrollment")
    op.execute("""
        CREATE INDEX idx_district_safety_enrollment_district_year 
        ON district_safety_enrollment (district_id_fk, year)
    """)

    logger.info("Safety Enrollment Materialized Views migration upgrade completed successfully")


def downgrade():
    """Drop the materialized views."""
    logger.info("Starting Safety Enrollment Materialized Views migration downgrade")

    # Drop materialized views
    views_to_drop = [
        'district_safety_enrollment',
        'state_safety_enrollment',
        'school_safety_enrollment'
    ]

    for view in views_to_drop:
        logger.info(f"Dropping materialized view {view}")
        op.execute(f"DROP MATERIALIZED VIEW IF EXISTS {view}")

    logger.info("Safety Enrollment Materialized Views migration downgrade completed successfully") 