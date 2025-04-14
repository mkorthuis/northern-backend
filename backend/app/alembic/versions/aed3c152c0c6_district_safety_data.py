"""District Safety Data Migration

Revision ID: aed3c152c0c6
Revises: 9ed3c152c0c5
Create Date: 2024-06-04 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
import logging

# Configure logger
logger = logging.getLogger('alembic.runtime.migration')

# revision identifiers, used by Alembic.
revision = 'aed3c152c0c6'
down_revision = '9ed3c152c0c5'
branch_labels = None
depends_on = None


def upgrade():
    """Generate data for district safety tables by aggregating school-level data."""
    logger.info("Starting District Safety Data migration upgrade")

    # Generate district truancy data using the provided query
    logger.info("Generating district_truancy data")
    op.execute("""
        INSERT INTO district_truancy (district_id_fk, year, count)
        SELECT
            s.district_id_fk, 
            st.year, 
            SUM(st.count) as count
        FROM 
            school_truancy st
        JOIN 
            school s ON st.school_id_fk = s.id
        GROUP BY 
            st.year, s.district_id_fk;
    """)

    # Generate district safety data
    logger.info("Generating district_safety data")
    op.execute("""
        INSERT INTO district_safety (district_id_fk, year, school_safety_type_id_fk, count)
        SELECT
            s.district_id_fk, 
            ss.year, 
            ss.school_safety_type_id_fk,
            SUM(ss.count) as count
        FROM 
            school_safety ss
        JOIN 
            school s ON ss.school_id_fk = s.id
        GROUP BY 
            ss.year, s.district_id_fk, ss.school_safety_type_id_fk;
    """)

    # Generate district discipline incident data
    logger.info("Generating district_discipline_incident data")
    op.execute("""
        INSERT INTO district_discipline_incident (district_id_fk, year, school_discipline_incident_type_id_fk, count)
        SELECT
            s.district_id_fk, 
            sdi.year, 
            sdi.school_discipline_incident_type_id_fk,
            SUM(sdi.count) as count
        FROM 
            school_discipline_incident sdi
        JOIN 
            school s ON sdi.school_id_fk = s.id
        GROUP BY 
            sdi.year, s.district_id_fk, sdi.school_discipline_incident_type_id_fk;
    """)

    # Generate district discipline count data
    logger.info("Generating district_discipline_count data")
    op.execute("""
        INSERT INTO district_discipline_count (district_id_fk, year, school_discipline_count_type_id_fk, count)
        SELECT
            s.district_id_fk, 
            sdc.year, 
            sdc.school_discipline_count_type_id_fk,
            SUM(sdc.count) as count
        FROM 
            school_discipline_count sdc
        JOIN 
            school s ON sdc.school_id_fk = s.id
        GROUP BY 
            sdc.year, s.district_id_fk, sdc.school_discipline_count_type_id_fk;
    """)

    # Generate district bullying data
    logger.info("Generating district_bullying data")
    op.execute("""
        INSERT INTO district_bullying (district_id_fk, year, school_bullying_type_id_fk, reported, investigated_actual)
        SELECT
            s.district_id_fk, 
            sb.year, 
            sb.school_bullying_type_id_fk,
            SUM(sb.reported) as reported,
            SUM(sb.investigated_actual) as investigated_actual
        FROM 
            school_bullying sb
        JOIN 
            school s ON sb.school_id_fk = s.id
        GROUP BY 
            sb.year, s.district_id_fk, sb.school_bullying_type_id_fk;
    """)

    # Generate district bullying classification data
    logger.info("Generating district_bullying_classification data")
    op.execute("""
        INSERT INTO district_bullying_classification (district_id_fk, year, school_bullying_classification_type_id_fk, count)
        SELECT
            s.district_id_fk, 
            sbc.year, 
            sbc.school_bullying_classification_type_id_fk,
            SUM(sbc.count) as count
        FROM 
            school_bullying_classification sbc
        JOIN 
            school s ON sbc.school_id_fk = s.id
        GROUP BY 
            sbc.year, s.district_id_fk, sbc.school_bullying_classification_type_id_fk;
    """)

    # Generate district bullying impact data
    logger.info("Generating district_bullying_impact data")
    op.execute("""
        INSERT INTO district_bullying_impact (district_id_fk, year, school_bullying_impact_type_id_fk, count)
        SELECT
            s.district_id_fk, 
            sbi.year, 
            sbi.school_bullying_impact_type_id_fk,
            SUM(sbi.count) as count
        FROM 
            school_bullying_impact sbi
        JOIN 
            school s ON sbi.school_id_fk = s.id
        GROUP BY 
            sbi.year, s.district_id_fk, sbi.school_bullying_impact_type_id_fk;
    """)

    # Generate district harassment data
    logger.info("Generating district_harassment data")
    op.execute("""
        INSERT INTO district_harassment (
            district_id_fk, 
            year, 
            school_harassment_classification_id_fk, 
            incident_count, 
            student_impact_count, 
            student_engaged_count
        )
        SELECT
            s.district_id_fk, 
            sh.year, 
            sh.school_harassment_classification_id_fk,
            SUM(sh.incident_count) as incident_count,
            SUM(sh.student_impact_count) as student_impact_count,
            SUM(sh.student_engaged_count) as student_engaged_count
        FROM 
            school_harassment sh
        JOIN 
            school s ON sh.school_id_fk = s.id
        GROUP BY 
            sh.year, s.district_id_fk, sh.school_harassment_classification_id_fk;
    """)

    # Generate district restraint data
    logger.info("Generating district_restraint data")
    op.execute("""
        INSERT INTO district_restraint (
            district_id_fk,
            year, 
            generated, 
            active_investigation, 
            closed_investigation, 
            bodily_injury, 
            serious_injury
        )
        SELECT
            s.district_id_fk, 
            sr.year, 
            SUM(sr.generated) as generated,
            SUM(sr.active_investigation) as active_investigation,
            SUM(sr.closed_investigation) as closed_investigation,
            SUM(sr.bodily_injury) as bodily_injury,
            SUM(sr.serious_injury) as serious_injury
        FROM 
            school_restraint sr
        JOIN 
            school s ON sr.school_id_fk = s.id
        GROUP BY 
            sr.year, s.district_id_fk;
    """)

    # Generate district seclusion data
    logger.info("Generating district_seclusion data")
    op.execute("""
        INSERT INTO district_seclusion (
            district_id_fk,
            year, 
            generated, 
            active_investigation, 
            closed_investigation
        )
        SELECT
            s.district_id_fk, 
            ss.year, 
            SUM(ss.generated) as generated,
            SUM(ss.active_investigation) as active_investigation,
            SUM(ss.closed_investigation) as closed_investigation
        FROM 
            school_seclusion ss
        JOIN 
            school s ON ss.school_id_fk = s.id
        GROUP BY 
            ss.year, s.district_id_fk;
    """)

    logger.info("District Safety Data migration completed successfully")


def downgrade():
    """Remove all district safety data."""
    logger.info("Starting District Safety Data migration downgrade")

    # List of tables to clear
    tables_to_clear = [
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

    # Clear each table
    for table in tables_to_clear:
        logger.info(f"Clearing data from table {table}")
        op.execute(f"DELETE FROM {table};")

    logger.info("District Safety Data migration downgrade completed successfully") 