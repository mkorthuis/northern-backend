"""State Expenditure Import

Revision ID:456acd975efb
Revises: 234adb12cac2
Create Date: 2025-04-05 01:33:00.000000

"""
from alembic import op
import sqlalchemy as sa
import pandas as pd
import logging
import os
import yaml
import numpy as np
import re

# Configure logger
logger = logging.getLogger('alembic.runtime.migration')

# Revision identifiers, used by Alembic
revision = '456acd975efb'
down_revision = '234adb12cac2'
branch_labels = None
depends_on = None

# Config path 
CONFIG_PATH = "app/alembic/config/state_expenditure_config.yaml"


def load_config(config_path=CONFIG_PATH):
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        # Try alternative path
        alt_path = f"backend/{config_path}"
        try:
            with open(alt_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found at {config_path} or {alt_path}")
            raise
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise


def generate_table_creation_statements():
    """Generate SQL statements to create the necessary tables."""
    statements = []
    
    # Define tables
    tables = {
        'expenditure_state_total': {
            'id': 'SERIAL PRIMARY KEY',
            'year': 'INTEGER NOT NULL',
            'operating_elementary': 'NUMERIC(15,2)',
            'operating_middle': 'NUMERIC(15,2)',
            'operating_high': 'NUMERIC(15,2)',
            'operating_total': 'NUMERIC(15,2)',
            'current_elementary': 'NUMERIC(15,2)',
            'current_middle': 'NUMERIC(15,2)',
            'current_high': 'NUMERIC(15,2)',
            'current_total': 'NUMERIC(15,2)',
            'total': 'NUMERIC(15,2)',
            'date_created': 'TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP',
            'date_updated': 'TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP',
            'constraints': [
                'CONSTRAINT unique_expenditure_state_total_year UNIQUE (year)'
            ]
        },
        'state_enrollment': {
            'id': 'SERIAL PRIMARY KEY',
            'year': 'INTEGER NOT NULL',
            'elementary': 'NUMERIC(15,2)',
            'middle': 'NUMERIC(15,2)',
            'high': 'NUMERIC(15,2)',
            'total': 'NUMERIC(15,2)',
            'date_created': 'TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP',
            'date_updated': 'TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP',
            'constraints': [
                'CONSTRAINT unique_state_enrollment_year UNIQUE (year)'
            ]
        }
    }
    
    # Generate create table statements
    for table_name, columns in tables.items():
        column_defs = []
        constraints = columns.pop('constraints', [])
        
        for col_name, col_def in columns.items():
            column_defs.append(f"{col_name} {col_def}")
        
        # Add constraints
        column_defs.extend(constraints)
        
        # Create table statement
        create_table = f"CREATE TABLE {table_name} (\n    "
        create_table += ",\n    ".join(column_defs)
        create_table += "\n)"
        
        # Add to statements as single line
        statements.append(' '.join(line.strip() for line in create_table.split('\n')))
    
    # Create triggers for all tables
    for table in tables.keys():
        trigger_sql = f"""
        CREATE TRIGGER trigger_update_{table}_timestamp
        BEFORE UPDATE ON {table}
        FOR EACH ROW EXECUTE FUNCTION update_date_updated_column()
        """
        statements.append(' '.join(line.strip() for line in trigger_sql.strip().split('\n')))
    
    # Create indexes
    indexes = [
        "CREATE INDEX idx_expenditure_state_total_year ON expenditure_state_total(year)",
        "CREATE INDEX idx_state_enrollment_year ON state_enrollment(year)"
    ]
    
    statements.extend(indexes)
    
    return statements


def clean_numeric_value(value):
    """Clean numeric value by stripping non-numeric characters.
    
    Args:
        value: The value to clean, can be string, float, or None
        
    Returns:
        float or None: Cleaned numeric value as float, or None if value couldn't be parsed
    """
    if pd.isna(value) or value is None:
        return None
        
    if isinstance(value, (int, float)):
        return float(value)
        
    try:
        # Convert to string and remove any non-numeric characters except decimal point
        # This will strip $, commas, etc.
        cleaned_str = re.sub(r'[^\d.]', '', str(value))
        if cleaned_str:
            return float(cleaned_str)
        return None
    except (ValueError, TypeError):
        return None


def format_sql_value(value):
    """Format a value for SQL insertion.
    
    Args:
        value: The value to format
        
    Returns:
        str: SQL-safe representation of the value
    """
    if value is None:
        return 'NULL'
    else:
        return str(value)


def process_state_expenditure_data(config, current_dir):
    """Process state expenditure data from CSV files and return SQL insert statements."""
    file_settings = config.get('file_settings', {})
    year_start = int(file_settings.get('year_start', 2010))
    year_end = int(file_settings.get('year_end', 2024))
    
    # SQL statements for inserts
    insert_statements = []
    
    # Process each year's data
    for year in range(year_start, year_end + 1):
        file_path = os.path.join(
            current_dir, 
            file_settings['default_input'].replace('****', str(year))
        )
        
        if not os.path.exists(file_path):
            logger.warning(f"File does not exist: {file_path}")
            continue
        
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            
            logger.info(f"Processing state expenditure data for year {year}, found {len(df)} rows")
            logger.debug(f"Column names: {df.columns.tolist()}")
            
            # Initialize variables to store extracted data
            expenditure_data = {
                'year': year,
                'operating_elementary': None,
                'operating_middle': None,
                'operating_high': None,
                'operating_total': None,
                'current_elementary': None,
                'current_middle': None,
                'current_high': None,
                'current_total': None,
                'total': None
            }
            
            enrollment_data = {
                'year': year,
                'elementary': None,
                'middle': None,
                'high': None,
                'total': None
            }
            
            # Track if we've found each section
            found_operating = False
            found_current = False
            found_total = False
            found_enrollment = False
            
            # Find rows with required data
            for idx, row in df.iterrows():
                # Skip rows where column A is missing
                if pd.isna(row.iloc[0]):
                    continue
                
                col_a_value = str(row.iloc[0]).strip()
                logger.debug(f"Processing row with Column A: '{col_a_value}'")
                
                # 1. Find operating expenses (only use the first instance)
                if not found_operating and col_a_value.startswith("Operating Expenses for Public Schools"):
                    expenditure_data['operating_elementary'] = clean_numeric_value(row.iloc[1])
                    expenditure_data['operating_middle'] = clean_numeric_value(row.iloc[3])
                    expenditure_data['operating_high'] = clean_numeric_value(row.iloc[5])
                    expenditure_data['operating_total'] = clean_numeric_value(row.iloc[7])
                    logger.debug(f"Found operating expenses: {expenditure_data['operating_elementary']}, {expenditure_data['operating_middle']}, {expenditure_data['operating_high']}, {expenditure_data['operating_total']}")
                    found_operating = True
                
                # 2. Find current expenses (only use the first instance)
                elif not found_current and col_a_value.startswith("Elem and Secondary Current Expenses"):
                    expenditure_data['current_elementary'] = clean_numeric_value(row.iloc[1])
                    expenditure_data['current_middle'] = clean_numeric_value(row.iloc[3])
                    expenditure_data['current_high'] = clean_numeric_value(row.iloc[5])
                    expenditure_data['current_total'] = clean_numeric_value(row.iloc[7])
                    logger.debug(f"Found current expenses: {expenditure_data['current_elementary']}, {expenditure_data['current_middle']}, {expenditure_data['current_high']}, {expenditure_data['current_total']}")
                    found_current = True
                
                # 3. Find total expenditures (only use the first instance)
                elif not found_total and col_a_value.startswith("Total Expenditures"):
                    expenditure_data['total'] = clean_numeric_value(row.iloc[7])
                    logger.debug(f"Found total expenditures: {expenditure_data['total']}")
                    found_total = True
                
                # 4. Find enrollment data (only use the first instance)
                elif not found_enrollment and col_a_value.startswith("Average daily membership"):
                    enrollment_data['elementary'] = clean_numeric_value(row.iloc[1])
                    enrollment_data['middle'] = clean_numeric_value(row.iloc[3])
                    enrollment_data['high'] = clean_numeric_value(row.iloc[5])
                    enrollment_data['total'] = clean_numeric_value(row.iloc[7])
                    logger.debug(f"Found enrollment data: {enrollment_data['elementary']}, {enrollment_data['middle']}, {enrollment_data['high']}, {enrollment_data['total']}")
                    found_enrollment = True
                
                # If we've found all data, we can stop searching
                if found_operating and found_current and found_total and found_enrollment:
                    logger.info(f"Found all required data for year {year}")
                    break
            
            # Log warning if we didn't find all data
            if not (found_operating and found_current and found_total and found_enrollment):
                missing = []
                if not found_operating:
                    missing.append("Operating Expenses")
                if not found_current:
                    missing.append("Current Expenses")
                if not found_total:
                    missing.append("Total Expenditures")
                if not found_enrollment:
                    missing.append("Enrollment")
                logger.warning(f"Did not find all required data for year {year}. Missing: {', '.join(missing)}")
            
            # Generate SQL insert statement for expenditure data
            expenditure_fields = list(expenditure_data.keys())
            expenditure_values = [
                str(expenditure_data['year']),
                format_sql_value(expenditure_data['operating_elementary']),
                format_sql_value(expenditure_data['operating_middle']),
                format_sql_value(expenditure_data['operating_high']),
                format_sql_value(expenditure_data['operating_total']),
                format_sql_value(expenditure_data['current_elementary']),
                format_sql_value(expenditure_data['current_middle']),
                format_sql_value(expenditure_data['current_high']),
                format_sql_value(expenditure_data['current_total']),
                format_sql_value(expenditure_data['total'])
            ]
            
            expenditure_insert = f"""
            INSERT INTO expenditure_state_total (
                {', '.join(expenditure_fields)}
            ) VALUES (
                {', '.join(expenditure_values)}
            ) ON CONFLICT (year) DO UPDATE SET
                operating_elementary = EXCLUDED.operating_elementary,
                operating_middle = EXCLUDED.operating_middle,
                operating_high = EXCLUDED.operating_high,
                operating_total = EXCLUDED.operating_total,
                current_elementary = EXCLUDED.current_elementary,
                current_middle = EXCLUDED.current_middle,
                current_high = EXCLUDED.current_high,
                current_total = EXCLUDED.current_total,
                total = EXCLUDED.total,
                date_updated = CURRENT_TIMESTAMP
            """
            # Convert to single line for execution
            expenditure_insert = ' '.join(line.strip() for line in expenditure_insert.strip().split('\n'))
            insert_statements.append(expenditure_insert)
            
            # Generate SQL insert statement for enrollment data
            enrollment_fields = list(enrollment_data.keys())
            enrollment_values = [
                str(enrollment_data['year']),
                format_sql_value(enrollment_data['elementary']),
                format_sql_value(enrollment_data['middle']),
                format_sql_value(enrollment_data['high']),
                format_sql_value(enrollment_data['total'])
            ]
            
            enrollment_insert = f"""
            INSERT INTO state_enrollment (
                {', '.join(enrollment_fields)}
            ) VALUES (
                {', '.join(enrollment_values)}
            ) ON CONFLICT (year) DO UPDATE SET
                elementary = EXCLUDED.elementary,
                middle = EXCLUDED.middle,
                high = EXCLUDED.high,
                total = EXCLUDED.total,
                date_updated = CURRENT_TIMESTAMP
            """
            # Convert to single line for execution
            enrollment_insert = ' '.join(line.strip() for line in enrollment_insert.strip().split('\n'))
            insert_statements.append(enrollment_insert)
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            logger.error(f"Exception details: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    logger.info(f"Generated {len(insert_statements)} insert statements for state expenditure and enrollment data")
    return insert_statements


def upgrade():
    """Alembic upgrade function to create tables and import state expenditure data."""
    try:
        # Load configuration
        config = load_config()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Check for existing cache file
        cache_dir = os.path.abspath(os.path.join(current_dir, config['file_settings']['sql_cache_dir']))
        cache_file = os.path.join(cache_dir, f'{revision}_cache.sql')
        
        # Delete cache file if it exists to force regeneration
        if os.path.exists(cache_file):
            os.remove(cache_file)
            logger.info(f"Deleted existing cache file {cache_file} to force regeneration")
        
        # Use cached SQL if available
        if os.path.exists(cache_file):
            logger.info(f"Using cached SQL from {cache_file}")
            with open(cache_file, 'r') as f:
                sql_statements = [stmt for stmt in f.read().split(';') if stmt.strip()]
        else:
            logger.info("Processing state expenditure data and generating SQL statements")
            
            # Generate table creation statements
            sql_statements = generate_table_creation_statements()
            
            # Process state expenditure data and generate insert statements
            insert_statements = process_state_expenditure_data(config, current_dir)
            
            # Add insert statements to SQL statements
            sql_statements.extend(insert_statements)
            
            # Save to cache - ensure each statement is a single line
            os.makedirs(cache_dir, exist_ok=True)
            with open(cache_file, 'w') as f:
                f.write(';\n'.join(stmt.strip() for stmt in sql_statements))
            
            logger.info(f"Cached {len(sql_statements)} SQL statements to {cache_file}")
        
        # Execute SQL statements
        executed = 0
        conn = op.get_bind()
        
        for statement in sql_statements:
            statement = statement.strip()
            if not statement:  # Skip empty statements
                continue
                
            try:
                op.execute(sa.text(statement))
                executed += 1
            except Exception as e:
                logger.error(f"Error executing SQL statement: {e}")
                if "duplicate key" not in str(e).lower():
                    logger.error(f"Statement: {statement[:300]}...")
                raise
            
        logger.info(f"Successfully executed {executed} SQL statements")
            
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        raise


def downgrade():
    """Alembic downgrade function to remove state expenditure tables."""
    try:
        sql_statements = [
            "DROP TABLE IF EXISTS expenditure_state_total CASCADE",
            "DROP TABLE IF EXISTS state_enrollment CASCADE"
        ]
        
        for statement in sql_statements:
            op.execute(sa.text(statement))
            
        logger.info("Successfully dropped state expenditure tables")
    except Exception as e:
        logger.error(f"Error during downgrade: {e}")
        raise
