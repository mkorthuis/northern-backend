"""School Safety Tables

Revision ID: 99baf2d34ef7
Revises: 854abd432fef
Create Date: 2024-05-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import logging

# Configure logger
logger = logging.getLogger('alembic.runtime.migration')

# Revision identifiers, used by Alembic
revision = '99baf2d34ef7'
down_revision = '854abd432fef'
branch_labels = None
depends_on = None


def upgrade():
    """Create the school_safety tables."""
    logger.info("Starting School Safety Tables migration upgrade")

    # Create school_truancy table
    logger.info("Creating school_truancy table")
    op.execute("""
        CREATE TABLE school_truancy (
            id SERIAL PRIMARY KEY,
            school_id_fk INTEGER NOT NULL,
            year INTEGER NOT NULL,
            count INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_school_truancy
                FOREIGN KEY (school_id_fk)
                REFERENCES school(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_school_truancy
                UNIQUE (school_id_fk, year)
        )
    """)

    # Create school_safety_type table
    logger.info("Creating school_safety_type table")
    op.execute("""
        CREATE TABLE school_safety_type (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create school_safety table
    logger.info("Creating school_safety table")
    op.execute("""
        CREATE TABLE school_safety (
            id SERIAL PRIMARY KEY,
            school_id_fk INTEGER NOT NULL,
            year INTEGER NOT NULL,
            school_safety_type_id_fk INTEGER NOT NULL,
            count INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_school_safety
                FOREIGN KEY (school_id_fk)
                REFERENCES school(id)
                ON DELETE CASCADE,
            CONSTRAINT fk_school_safety_type
                FOREIGN KEY (school_safety_type_id_fk)
                REFERENCES school_safety_type(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_school_safety
                UNIQUE (school_id_fk, year, school_safety_type_id_fk)
        )
    """)

    # Create school_discipline_incident_type table
    logger.info("Creating school_discipline_incident_type table")
    op.execute("""
        CREATE TABLE school_discipline_incident_type (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create school_discipline_incident table
    logger.info("Creating school_discipline_incident table")
    op.execute("""
        CREATE TABLE school_discipline_incident (
            id SERIAL PRIMARY KEY,
            school_id_fk INTEGER NOT NULL,
            year INTEGER NOT NULL,
            school_discipline_incident_type_id_fk INTEGER NOT NULL,
            count INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_school_discipline_incident
                FOREIGN KEY (school_id_fk)
                REFERENCES school(id)
                ON DELETE CASCADE,
            CONSTRAINT fk_school_discipline_incident_type
                FOREIGN KEY (school_discipline_incident_type_id_fk)
                REFERENCES school_discipline_incident_type(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_school_discipline_incident
                UNIQUE (school_id_fk, year, school_discipline_incident_type_id_fk)
        )
    """)

    # Create school_discipline_count_type table
    logger.info("Creating school_discipline_count_type table")
    op.execute("""
        CREATE TABLE school_discipline_count_type (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create school_discipline_count table
    logger.info("Creating school_discipline_count table")
    op.execute("""
        CREATE TABLE school_discipline_count (
            id SERIAL PRIMARY KEY,
            school_id_fk INTEGER NOT NULL,
            year INTEGER NOT NULL,
            school_discipline_count_type_id_fk INTEGER NOT NULL,
            count INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_school_discipline_count
                FOREIGN KEY (school_id_fk)
                REFERENCES school(id)
                ON DELETE CASCADE,
            CONSTRAINT fk_school_discipline_count_type
                FOREIGN KEY (school_discipline_count_type_id_fk)
                REFERENCES school_discipline_count_type(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_school_discipline_count
                UNIQUE (school_id_fk, year, school_discipline_count_type_id_fk)
        )
    """)

    # Create school_bullying_type table
    logger.info("Creating school_bullying_type table")
    op.execute("""
        CREATE TABLE school_bullying_type (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create school_bullying table
    logger.info("Creating school_bullying table")
    op.execute("""
        CREATE TABLE school_bullying (
            id SERIAL PRIMARY KEY,
            school_id_fk INTEGER NOT NULL,
            year INTEGER NOT NULL,
            school_bullying_type_id_fk INTEGER NOT NULL,
            reported INTEGER,
            investigated_actual INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_school_bullying
                FOREIGN KEY (school_id_fk)
                REFERENCES school(id)
                ON DELETE CASCADE,
            CONSTRAINT fk_school_bullying_type
                FOREIGN KEY (school_bullying_type_id_fk)
                REFERENCES school_bullying_type(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_school_bullying
                UNIQUE (school_id_fk, year, school_bullying_type_id_fk)
        )
    """)

    # Create school_bullying_classification_type table
    logger.info("Creating school_bullying_classification_type table")
    op.execute("""
        CREATE TABLE school_bullying_classification_type (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create school_bullying_classification table
    logger.info("Creating school_bullying_classification table")
    op.execute("""
        CREATE TABLE school_bullying_classification (
            id SERIAL PRIMARY KEY,
            school_id_fk INTEGER NOT NULL,
            year INTEGER NOT NULL,
            school_bullying_classification_type_id_fk INTEGER NOT NULL,
            count INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_school_bullying_classification
                FOREIGN KEY (school_id_fk)
                REFERENCES school(id)
                ON DELETE CASCADE,
            CONSTRAINT fk_school_bullying_classification_type
                FOREIGN KEY (school_bullying_classification_type_id_fk)
                REFERENCES school_bullying_classification_type(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_school_bullying_classification
                UNIQUE (school_id_fk, year, school_bullying_classification_type_id_fk)
        )
    """)

    # Create school_bullying_impact_type table
    logger.info("Creating school_bullying_impact_type table")
    op.execute("""
        CREATE TABLE school_bullying_impact_type (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create school_bullying_impact table
    logger.info("Creating school_bullying_impact table")
    op.execute("""
        CREATE TABLE school_bullying_impact (
            id SERIAL PRIMARY KEY,
            school_id_fk INTEGER NOT NULL,
            year INTEGER NOT NULL,
            school_bullying_impact_type_id_fk INTEGER NOT NULL,
            count INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_school_bullying_impact
                FOREIGN KEY (school_id_fk)
                REFERENCES school(id)
                ON DELETE CASCADE,
            CONSTRAINT fk_school_bullying_impact_type
                FOREIGN KEY (school_bullying_impact_type_id_fk)
                REFERENCES school_bullying_impact_type(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_school_bullying_impact
                UNIQUE (school_id_fk, year, school_bullying_impact_type_id_fk)
        )
    """)

    # Create school_harassment_classification table
    logger.info("Creating school_harassment_classification table")
    op.execute("""
        CREATE TABLE school_harassment_classification (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create school_harassment table
    logger.info("Creating school_harassment table")
    op.execute("""
        CREATE TABLE school_harassment (
            id SERIAL PRIMARY KEY,
            school_id_fk INTEGER NOT NULL,
            year INTEGER NOT NULL,
            school_harassment_classification_id_fk INTEGER NOT NULL,
            incident_count INTEGER,
            student_impact_count INTEGER,
            student_engaged_count INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_school_harassment
                FOREIGN KEY (school_id_fk)
                REFERENCES school(id)
                ON DELETE CASCADE,
            CONSTRAINT fk_school_harassment_classification
                FOREIGN KEY (school_harassment_classification_id_fk)
                REFERENCES school_harassment_classification(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_school_harassment
                UNIQUE (school_id_fk, year, school_harassment_classification_id_fk)
        )
    """)

    # Create school_restraint table
    logger.info("Creating school_restraint table")
    op.execute("""
        CREATE TABLE school_restraint (
            id SERIAL PRIMARY KEY,
            school_id_fk INTEGER NOT NULL,
            year INTEGER NOT NULL,
            generated INTEGER,
            active_investigation INTEGER,
            closed_investigation INTEGER,
            bodily_injury INTEGER,
            serious_injury INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_school_restraint
                FOREIGN KEY (school_id_fk)
                REFERENCES school(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_school_restraint
                UNIQUE (school_id_fk, year)
        )
    """)

    # Create school_seclusion table
    logger.info("Creating school_seclusion table")
    op.execute("""
        CREATE TABLE school_seclusion (
            id SERIAL PRIMARY KEY,
            school_id_fk INTEGER NOT NULL,
            year INTEGER NOT NULL,
            generated INTEGER,
            active_investigation INTEGER,
            closed_investigation INTEGER,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_school_seclusion
                FOREIGN KEY (school_id_fk)
                REFERENCES school(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_school_seclusion
                UNIQUE (school_id_fk, year)
        )
    """)

    # Create triggers for all tables
    logger.info("Creating triggers for tables")
    tables_for_triggers = [
        'school_truancy',
        'school_safety_type',
        'school_safety',
        'school_discipline_incident_type',
        'school_discipline_incident',
        'school_discipline_count_type',
        'school_discipline_count',
        'school_bullying_type',
        'school_bullying',
        'school_bullying_classification_type',
        'school_bullying_classification',
        'school_bullying_impact_type',
        'school_bullying_impact',
        'school_harassment_classification',
        'school_harassment',
        'school_restraint',
        'school_seclusion'
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
        "CREATE INDEX idx_school_truancy_school ON school_truancy(school_id_fk)",
        "CREATE INDEX idx_school_truancy_year ON school_truancy(year)",
        "CREATE INDEX idx_school_safety_school ON school_safety(school_id_fk)",
        "CREATE INDEX idx_school_safety_year ON school_safety(year)",
        "CREATE INDEX idx_school_safety_type ON school_safety(school_safety_type_id_fk)",
        "CREATE INDEX idx_school_discipline_incident_school ON school_discipline_incident(school_id_fk)",
        "CREATE INDEX idx_school_discipline_incident_year ON school_discipline_incident(year)",
        "CREATE INDEX idx_school_discipline_incident_type ON school_discipline_incident(school_discipline_incident_type_id_fk)",
        "CREATE INDEX idx_school_discipline_count_school ON school_discipline_count(school_id_fk)",
        "CREATE INDEX idx_school_discipline_count_year ON school_discipline_count(year)",
        "CREATE INDEX idx_school_discipline_count_type ON school_discipline_count(school_discipline_count_type_id_fk)",
        "CREATE INDEX idx_school_bullying_school ON school_bullying(school_id_fk)",
        "CREATE INDEX idx_school_bullying_year ON school_bullying(year)",
        "CREATE INDEX idx_school_bullying_type ON school_bullying(school_bullying_type_id_fk)",
        "CREATE INDEX idx_school_bullying_classification_school ON school_bullying_classification(school_id_fk)",
        "CREATE INDEX idx_school_bullying_classification_year ON school_bullying_classification(year)",
        "CREATE INDEX idx_school_bullying_classification_type ON school_bullying_classification(school_bullying_classification_type_id_fk)",
        "CREATE INDEX idx_school_bullying_impact_school ON school_bullying_impact(school_id_fk)",
        "CREATE INDEX idx_school_bullying_impact_year ON school_bullying_impact(year)",
        "CREATE INDEX idx_school_bullying_impact_type ON school_bullying_impact(school_bullying_impact_type_id_fk)",
        "CREATE INDEX idx_school_harassment_school ON school_harassment(school_id_fk)",
        "CREATE INDEX idx_school_harassment_year ON school_harassment(year)",
        "CREATE INDEX idx_school_harassment_classification ON school_harassment(school_harassment_classification_id_fk)",
        "CREATE INDEX idx_school_restraint_school ON school_restraint(school_id_fk)",
        "CREATE INDEX idx_school_restraint_year ON school_restraint(year)",
        "CREATE INDEX idx_school_seclusion_school ON school_seclusion(school_id_fk)",
        "CREATE INDEX idx_school_seclusion_year ON school_seclusion(year)"
    ]

    for index in indexes:
        op.execute(index)

    # Insert initial data for school_safety_type
    logger.info("Inserting initial data for school_safety_type")
    safety_types = [
        "INSERT INTO school_safety_type (name, description) VALUES ('Handgun Incidents', 'Handgun Incidents')",
        "INSERT INTO school_safety_type (name, description) VALUES ('Rifles/ Shotguns Incidents', 'Rifles/ Shotguns Incidents')",
        "INSERT INTO school_safety_type (name, description) VALUES ('Firearms Incidents Including More Than One Type of Weapon or Firearm', 'Firearms Incidents Including More Than One Type of Weapon or Firearm')",
        "INSERT INTO school_safety_type (name, description) VALUES ('Other Firearms Incidents', 'Other Firearms Incidents')",
        "INSERT INTO school_safety_type (name, description) VALUES ('Homicides', 'Homicides')",
        "INSERT INTO school_safety_type (name, description) VALUES ('First Degree Assaults', 'First Degree Assaults')",
        "INSERT INTO school_safety_type (name, description) VALUES ('Aggravated Felonious Sexual Assaults', 'Aggravated Felonious Sexual Assaults')",
        "INSERT INTO school_safety_type (name, description) VALUES ('Arsons', 'Arsons')",
        "INSERT INTO school_safety_type (name, description) VALUES ('Robberies', 'Robberies')",
        "INSERT INTO school_safety_type (name, description) VALUES ('Firearms Possessions or Sales', 'Firearms Possessions or Sales')"
    ]

    for insert in safety_types:
        op.execute(insert)

    # Insert initial data for school_discipline_incident_type
    logger.info("Inserting initial data for school_discipline_incident_type")
    discipline_incident_types = [
        "INSERT INTO school_discipline_incident_type (name, description) VALUES ('Violent Incidents With Physical Injury Requiring Professional Medical Attention', 'Violent Incidents With Physical Injury Requiring Professional Medical Attention')",
        "INSERT INTO school_discipline_incident_type (name, description) VALUES ('Violent Incidents, including Harassment & Bullying (Without Physical Injury)', 'Violent Incidents, including Harassment & Bullying (Without Physical Injury)')",
        "INSERT INTO school_discipline_incident_type (name, description) VALUES ('Weapons Possession', 'Weapons Possession')",
        "INSERT INTO school_discipline_incident_type (name, description) VALUES ('Illicit Drugs', 'Illicit Drugs')",
        "INSERT INTO school_discipline_incident_type (name, description) VALUES ('Alcohol', 'Alcohol')",
        "INSERT INTO school_discipline_incident_type (name, description) VALUES ('Other Incidents Related to Drug or Alcohol Use, Violence or Weapons Possession', 'Other Incidents Related to Drug or Alcohol Use, Violence or Weapons Possession')",
        "INSERT INTO school_discipline_incident_type (name, description) VALUES ('Disruption', 'Disruption')",
        "INSERT INTO school_discipline_incident_type (name, description) VALUES ('Defiance', 'Defiance')",
        "INSERT INTO school_discipline_incident_type (name, description) VALUES ('Inappropriate Language', 'Inappropriate Language')",
        "INSERT INTO school_discipline_incident_type (name, description) VALUES ('All Other Incidents', 'All Other Incidents')"
    ]

    for insert in discipline_incident_types:
        op.execute(insert)

    # Insert initial data for school_discipline_count_type
    logger.info("Inserting initial data for school_discipline_count_type")
    discipline_count_types = [
        "INSERT INTO school_discipline_count_type (name, description) VALUES ('Who Received In-School Suspensions', 'Who Received In-School Suspensions')",
        "INSERT INTO school_discipline_count_type (name, description) VALUES ('Who Received Out-of-School Suspensions', 'Who Received Out-of-School Suspensions')",
        "INSERT INTO school_discipline_count_type (name, description) VALUES ('Who Were Expelled', 'Who Were Expelled')"
    ]

    for insert in discipline_count_types:
        op.execute(insert)

    # Insert initial data for school_bullying_type
    logger.info("Inserting initial data for school_bullying_type")
    bullying_types = [
        "INSERT INTO school_bullying_type (name, description) VALUES ('Bullying (of any kind)', 'Bullying (of any kind)')",
        "INSERT INTO school_bullying_type (name, description) VALUES ('Cyber-bullying', 'Cyber-bullying')"
    ]

    for insert in bullying_types:
        op.execute(insert)

    # Insert initial data for school_bullying_classification_type
    logger.info("Inserting initial data for school_bullying_classification_type")
    bullying_classification_types = [
        "INSERT INTO school_bullying_classification_type (name, description) VALUES ('Gender', 'Gender')",
        "INSERT INTO school_bullying_classification_type (name, description) VALUES ('Sexual Orientation', 'Sexual Orientation')",
        "INSERT INTO school_bullying_classification_type (name, description) VALUES ('Race, Color or National Origin', 'Race, Color or National Origin')",
        "INSERT INTO school_bullying_classification_type (name, description) VALUES ('Disability', 'Disability')",
        "INSERT INTO school_bullying_classification_type (name, description) VALUES ('Physical Characteristics', 'Physical Characteristics')",
        "INSERT INTO school_bullying_classification_type (name, description) VALUES ('Any Other Basis', 'Any Other Basis')"
    ]

    for insert in bullying_classification_types:
        op.execute(insert)

    # Insert initial data for school_bullying_impact_type
    logger.info("Inserting initial data for school_bullying_impact_type")
    bullying_impact_types = [
        "INSERT INTO school_bullying_impact_type (name, description) VALUES ('Were a Single Significant Event', 'Were a Single Significant Event')",
        "INSERT INTO school_bullying_impact_type (name, description) VALUES ('Were a Pattern of Deliberate Harmful Events', 'Were a Pattern of Deliberate Harmful Events')",
        "INSERT INTO school_bullying_impact_type (name, description) VALUES ('Included Physical Harm', 'Included Physical Harm')",
        "INSERT INTO school_bullying_impact_type (name, description) VALUES ('Included Property Damage', 'Included Property Damage')",
        "INSERT INTO school_bullying_impact_type (name, description) VALUES ('Used Social/ Emotional Alienation', 'Used Social/ Emotional Alienation')",
        "INSERT INTO school_bullying_impact_type (name, description) VALUES ('Interfered with Educational Opportunities', 'Interfered with Educational Opportunities')",
        "INSERT INTO school_bullying_impact_type (name, description) VALUES ('Disrupted School Operations', 'Disrupted School Operations')"
    ]

    for insert in bullying_impact_types:
        op.execute(insert)

    # Insert initial data for school_harassment_classification
    logger.info("Inserting initial data for school_harassment_classification")
    harassment_classifications = [
        "INSERT INTO school_harassment_classification (name, description) VALUES ('Gender', 'Gender')",
        "INSERT INTO school_harassment_classification (name, description) VALUES ('Sexual Orientation', 'Sexual Orientation')",
        "INSERT INTO school_harassment_classification (name, description) VALUES ('Race, Color or National Origin', 'Race, Color or National Origin')",
        "INSERT INTO school_harassment_classification (name, description) VALUES ('Disability', 'Disability')",
        "INSERT INTO school_harassment_classification (name, description) VALUES ('Physical Characteristics (other than race)', 'Physical Characteristics (other than race)')"
    ]

    for insert in harassment_classifications:
        op.execute(insert)

    logger.info("School Safety Tables migration upgrade completed successfully")


def downgrade():
    """Drop the school_safety tables."""
    logger.info("Starting School Safety Tables migration downgrade")

    # Drop tables in reverse order to handle dependencies
    tables_to_drop = [
        'school_seclusion',
        'school_restraint',
        'school_harassment',
        'school_harassment_classification',
        'school_bullying_impact',
        'school_bullying_impact_type',
        'school_bullying_classification',
        'school_bullying_classification_type',
        'school_bullying',
        'school_bullying_type',
        'school_discipline_count',
        'school_discipline_count_type',
        'school_discipline_incident',
        'school_discipline_incident_type',
        'school_safety',
        'school_safety_type',
        'school_truancy'
    ]

    for table in tables_to_drop:
        logger.info(f"Dropping table {table}")
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")

    logger.info("School Safety Tables migration downgrade completed successfully") 