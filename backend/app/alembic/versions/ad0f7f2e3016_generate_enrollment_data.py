"""generate enrollment data

Revision ID: ad0f7f2e3016
Revises: 97bda4348f5c
Create Date: 2025-03-24 20:35:04.769291

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql
import pandas as pd
import yaml
from datetime import datetime
import os
import logging

# revision identifiers, used by Alembic.
revision = 'ad0f7f2e3016'
down_revision = '97bda4348f5c'
branch_labels = None
depends_on = None

logger = logging.getLogger('alembic.runtime.migration')

def load_config(config_path="app/alembic/config/generate_enrollment_config.yaml"):
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def parse_excel_file(df, year, config):
    """Parse a single Excel file and return enrollment data structure."""
    # Skip to the data rows
    df = df.iloc[config['excel_settings']['data_start_row']:]
    df = df.reset_index(drop=True)
    
    # Initialize data structure for this year
    year_data = []
    
    # Process each row
    for _, row in df.iterrows():
        try:
            sau_num = int(row.iloc[0])
        except (ValueError, TypeError):
            continue
            
        school_data = {
            'school_id': row.iloc[4],
            'school_name': row.iloc[5],
            'sau_id': row.iloc[0],
            'sau_name': row.iloc[1],
            'district_id': row.iloc[2],
            'district_name': row.iloc[3],
            'total': row.iloc[21],
            'year': year,
            'enrollments': {}
        }
        # Add enrollment for each grade
        for grade, pos in config['excel_settings']['grade_positions'].items():
            value = row.iloc[pos]
            if pd.notna(value) and value > 0:
                school_data['enrollments'][grade] = int(value)
        
        if school_data['enrollments']:
            year_data.append(school_data)
    
    return year_data

def generate_sql_statements(all_years_data, config):
    """Generate SQL INSERT statements for enrollment data."""
    sql_statements = []
    
    for school_data in all_years_data:
        # Add check for valid school ID
        school_id = int(school_data['school_id'])
        exists_check = sa.text("""
            SELECT EXISTS (
                SELECT 1 FROM school WHERE id = :school_id
            )
        """)
        result = op.get_bind().execute(exists_check, {"school_id": school_id}).scalar()
        
        if not result:
            logger.error(f"School ID {school_id} does not exist")
            continue
            
        for grade, enrollment in school_data['enrollments'].items():
            grade_id = config['grade_mappings'][grade]
            sql_statements.append(f"""INSERT INTO school_enrollment (school_id_fk, grade_id_fk, year, enrollment) VALUES  ({school_id}, {grade_id}, {school_data['year']}, {enrollment})""")
    
    return sql_statements

def upgrade():
    # Load configuration
    config = load_config()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logger.info(f"Starting enrollment data migration")

    try:
        # Check for existing cache file
        cache_dir = os.path.abspath(os.path.join(current_dir, config['file_settings']['sql_cache_dir']))
        cache_file = os.path.join(cache_dir, f'{revision}_cache.sql')
        
        logger.info(f"Loading File")
        if os.path.exists(cache_file):
            logger.info(f"Found existing SQL cache file at: {cache_file}")
            with open(cache_file, 'r') as f:
                sql_statements = f.read().split(';')
        else:
            logger.info(f"Processing File")
            
            # Process enrollment data
            generic_file_path = config['file_settings']['default_input']
            year_start = int(config['file_settings']['year_start'])
            year_end = int(config['file_settings']['year_end'])
            
            all_years_data = []
            
            # Iterate through the years
            for year in range(year_start, year_end + 1):
                current_file = generic_file_path.replace('****', str(year))
                try:
                    file_path = os.path.abspath(os.path.join(current_dir,current_file))
                    df = pd.read_excel(file_path)
                    year_data = parse_excel_file(df, year, config)
                    all_years_data.extend(year_data)
                except Exception as e:
                    logger.error(f"Error processing file for year {year}: {e}")
                    continue
            
            # Generate SQL statements
            sql_statements = generate_sql_statements(all_years_data, config)
            logger.info(f"Generating SQL Statements")

            # Save to cache
            os.makedirs(cache_dir, exist_ok=True)
            logger.info(f"Creating new SQL cache file at: {cache_file}")
            with open(cache_file, 'w') as f:
                f.write(';\n'.join(sql_statements))
            logger.info(f"Successfully created SQL cache file ({os.path.getsize(cache_file)} bytes)")
        
        # Execute SQL statements individually
        for statement in sql_statements:
            statement = statement.strip()
            if statement:  # Skip empty statements
                try:
                    op.execute(sa.text(statement))
                except Exception as e:
                    logger.error(f"Error executing SQL statement: {e}\nStatement: {statement}")
                    continue
                
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        raise Exception(f"Error during migration: {e}")

def downgrade():
    # Remove all enrollment data
    op.execute("DELETE FROM school_enrollment")
