"""Cost Per Pupil Data Import

Revision ID: 97ab8dffd654
Revises: 65ab32afd32c
Create Date: 2025-04-05 01:33:00.000000

"""
from alembic import op
import sqlalchemy as sa
import pandas as pd
import logging
import os
import yaml

# Configure logger
logger = logging.getLogger('alembic.runtime.migration')

# Revision identifiers, used by Alembic
revision = '97ab8dffd654'
down_revision = '65ab32afd32c'
branch_labels = None
depends_on = None

# Constants
SCHOOL_LEVELS = ['elementary', 'middle', 'high', 'total']
COLUMN_LABELS = [" Elementary ", " Middle ", " High ", " Total "]
DEFAULT_INDICES = [4, 5, 6, 7]
CONFIG_PATH = "app/alembic/config/generate_cost_per_pupil_config.yaml"


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


def is_valid_district_id(value):
    """Check if value is a valid district ID (integer or string that can be converted to int)"""
    if pd.isna(value) or value == '' or value == '-':
        return False
    
    try:
        int(float(value))
        return True
    except (ValueError, TypeError):
        return False


def parse_currency(value):
    """Parse a currency value, handling dollar signs, commas, and spaces."""
    if pd.isna(value) or value == '' or value == '-':
        return None
        
    try:
        # Remove common non-numeric characters
        if isinstance(value, str):
            cleaned = value.replace('$', '').replace(',', '').replace(' ', '')
            if cleaned == '-' or cleaned == '':
                return None
            return int(float(cleaned))
        elif isinstance(value, (int, float)):
            return int(value)
        else:
            return None
    except (ValueError, TypeError):
        return None


def find_header_row(df):
    """Find the header row that contains 'DIST' and 'School District'"""
    # Original header detection logic
    for i in range(min(25, df.shape[0])):
        if (isinstance(df.iloc[i, 0], str) and "DIST" in df.iloc[i, 0] and 
            isinstance(df.iloc[i, 3], str) and "School District" in df.iloc[i, 3]):
            return i
    
    logger.error("No header row found matching criteria - DIST in col0 and School District in col3")
    
    # Try to find a row with just DIST in first column as fallback
    for i in range(min(25, df.shape[0])):
        if isinstance(df.iloc[i, 0], str) and df.iloc[i, 0].strip() == "DIST":
            return i
    
    return None


def find_state_row(data_df):
    """Find the row with state average information"""
    for i in range(min(30, data_df.shape[0])):
        col3_value = data_df.iloc[i, 3] if i < data_df.shape[0] and 3 < data_df.shape[1] else None
        
        if isinstance(col3_value, str) and "State Average" in col3_value:
            return i
            
    logger.warning("No state average row found")
    return None


def parse_csv_file(df, year):
    """Parse a single CSV file and return cost per pupil data structure."""
    # Initialize data structure for this year
    year_data = {'district': [], 'state': {}}
    
    try:
        # Find the header row 
        header_row = find_header_row(df)
        
        if header_row is None:
            logger.error(f"Could not find header row in CSV for year {year}")
            return year_data
        
        # Extract column names and prepare data frame
        column_names = [str(df.iloc[header_row, j]).strip() or f"Column_{j}" for j in range(df.shape[1])]
        
        data_df = df.iloc[(header_row+1):].reset_index(drop=True)
        data_df.columns = column_names
        
        # Find state average row
        state_row = find_state_row(data_df)
        
        # Map column indices with fallbacks
        cols = {}
        for level, label, default_idx in zip(SCHOOL_LEVELS, COLUMN_LABELS, DEFAULT_INDICES):
            cols[level] = column_names.index(label) if label in column_names else default_idx
        
        # Process state data if found
        if state_row is not None:
            try:
                year_data['state'] = {k: parse_currency(data_df.iloc[state_row, idx]) for k, idx in cols.items()}
            except Exception as e:
                logger.error(f"Error processing state average row for year {year}: {e}")
        
        # Find district column
        district_col = column_names.index("DIST") if "DIST" in column_names else 0
        
        # Process district rows
        for i in range(data_df.shape[0]):
            try:
                # Skip state average row and blank rows
                if i == state_row or pd.isna(data_df.iloc[i, district_col]):
                    continue
                
                district_id_val = data_df.iloc[i, district_col]
                
                # Skip if not a valid district ID
                if not is_valid_district_id(district_id_val):
                    continue
                
                district_id = int(float(district_id_val))
                
                # Extract values for each school level
                values = {}
                for level in SCHOOL_LEVELS:
                    col_idx = cols[level]
                    value = None
                    if col_idx < data_df.shape[1]:
                        value = parse_currency(data_df.iloc[i, col_idx])
                    values[level] = value
                
                values['district_id'] = district_id
                year_data['district'].append(values)
            except Exception as e:
                logger.error(f"Error processing district row {i} for year {year}: {e}")
                continue
        
    except Exception as e:
        logger.error(f"Error during CSV parsing for year {year}: {e}")
    
    return year_data


def get_valid_district_ids():
    """Query the district table to get a list of valid district IDs."""
    try:
        result = op.get_bind().execute(sa.text("SELECT id FROM district"))
        return {row[0] for row in result}
    except Exception as e:
        logger.error(f"Error querying district IDs: {e}")
        return set()


def generate_table_creation_statements():
    """Generate SQL statements to create the necessary tables."""
    statements = []
    
    # District cost per pupil table
    statements.append("CREATE TABLE district_cost_per_pupil (id SERIAL PRIMARY KEY, district_id_fk INTEGER NOT NULL, year INTEGER NOT NULL, elementary INTEGER, middle INTEGER, high INTEGER, total INTEGER, date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, CONSTRAINT fk_district_cost_per_pupil FOREIGN KEY (district_id_fk) REFERENCES district(id) ON DELETE CASCADE, CONSTRAINT unique_district_cost_per_pupil_year UNIQUE (district_id_fk, year))")
    
    # State cost per pupil table
    statements.append("CREATE TABLE state_cost_per_pupil (id SERIAL PRIMARY KEY, year INTEGER NOT NULL, elementary INTEGER, middle INTEGER, high INTEGER, total INTEGER, date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, CONSTRAINT unique_state_cost_per_pupil_year UNIQUE (year))")
    
    # Triggers for timestamp updates
    statements.append("CREATE TRIGGER trigger_update_district_cost_per_pupil_timestamp BEFORE UPDATE ON district_cost_per_pupil FOR EACH ROW EXECUTE FUNCTION update_date_updated_column()")
    
    statements.append("CREATE TRIGGER trigger_update_state_cost_per_pupil_timestamp BEFORE UPDATE ON state_cost_per_pupil FOR EACH ROW EXECUTE FUNCTION update_date_updated_column()")
    
    # Indexes for performance
    statements.append("CREATE INDEX idx_district_cost_per_pupil_district ON district_cost_per_pupil(district_id_fk)")
    statements.append("CREATE INDEX idx_district_cost_per_pupil_year ON district_cost_per_pupil(year)")
    statements.append("CREATE INDEX idx_state_cost_per_pupil_year ON state_cost_per_pupil(year)")
    
    return statements


def generate_insert_statements(all_years_data, valid_district_ids):
    """Generate SQL INSERT statements for cost per pupil data."""
    sql_statements = []
    if not isinstance(all_years_data, dict):
        logger.error(f"Expected all_years_data to be a dictionary, but got {type(all_years_data)}")
        return sql_statements
    
    skipped_districts = set()
    processed_districts = set()

    # Process district data
    for year, year_data in all_years_data.items():
        districts = year_data.get('district', [])
        
        for district in districts:
            district_id = district.get('district_id')
            
            # Skip if district_id is None or not valid
            if district_id is None:
                continue
                
            if district_id not in valid_district_ids:
                if district_id not in skipped_districts:
                    skipped_districts.add(district_id)
                continue
            
            processed_districts.add(district_id)
            
            # Create single-line SQL statement
            elementary = "NULL" if district.get('elementary') is None else district.get('elementary')
            middle = "NULL" if district.get('middle') is None else district.get('middle')
            high = "NULL" if district.get('high') is None else district.get('high')
            total = "NULL" if district.get('total') is None else district.get('total')
            
            sql = f"INSERT INTO district_cost_per_pupil (district_id_fk, year, elementary, middle, high, total) VALUES ({district_id}, {year}, {elementary}, {middle}, {high}, {total})"
            sql_statements.append(sql)
        
        # Process state data
        state_data = year_data.get('state', {})
        if state_data:
            elementary = "NULL" if state_data.get('elementary') is None else state_data.get('elementary')
            middle = "NULL" if state_data.get('middle') is None else state_data.get('middle')
            high = "NULL" if state_data.get('high') is None else state_data.get('high')
            total = "NULL" if state_data.get('total') is None else state_data.get('total')
            
            sql = f"INSERT INTO state_cost_per_pupil (year, elementary, middle, high, total) VALUES ({year}, {elementary}, {middle}, {high}, {total})"
            sql_statements.append(sql)
    
    logger.info(f"Processed {len(processed_districts)} districts, skipped {len(skipped_districts)} not found in the database")
    
    return sql_statements


def execute_sql_statements(sql_statements):
    """Execute SQL statements with proper error handling."""
    successful = 0
    for statement in sql_statements:
        statement = statement.strip()
        if not statement:  # Skip empty statements
            continue
            
        try:
            op.execute(sa.text(statement))
            successful += 1
        except Exception as e:
            logger.error(f"Error executing SQL statement: {e}")
    
    logger.info(f"Successfully executed {successful} out of {len(sql_statements)} SQL statements")


def process_cost_per_pupil_data(config, current_dir):
    """Process cost per pupil data from CSV files."""
    file_settings = config.get('file_settings', {})
    year_start = int(file_settings.get('year_start', 2010))
    year_end = int(file_settings.get('year_end', 2024))
    
    # Initialize data container
    all_years_data = {}

    # Process each year's data
    for year in range(year_start, year_end + 1):
        file_path = os.path.join(
            current_dir, 
            file_settings['default_input'].replace('****', str(year))
        )
        
        try:
            if not os.path.exists(file_path):
                logger.warning(f"File does not exist: {file_path}")
                continue
            
            # Read CSV with all columns as strings to avoid automatic type conversion
            df = pd.read_csv(file_path, dtype=str)
            year_data = parse_csv_file(df, year)
            
            # Check if year data has any content
            if year_data['district'] or year_data['state']:
                all_years_data[year] = year_data
                logger.info(f"Successfully processed data for year {year}")
            else:
                logger.warning(f"No data found for year {year}")
                
        except Exception as e:
            logger.error(f"Error processing file for year {year}: {e}")
    
    return all_years_data


def upgrade():
    """Alembic upgrade function to create tables and import cost per pupil data."""
    try:
        # Load configuration
        config = load_config()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Check for existing cache file
        cache_dir = os.path.abspath(os.path.join(current_dir, config['file_settings']['sql_cache_dir']))
        cache_file = os.path.join(cache_dir, f'{revision}_cache.sql')   
        
        # Use cached SQL if available
        if os.path.exists(cache_file):
            logger.info(f"Using cached SQL from {cache_file}")
            with open(cache_file, 'r') as f:
                sql_statements = [stmt for stmt in f.read().split(';') if stmt.strip()]
        else:
            logger.info("Processing cost per pupil data and generating SQL statements")
            
            # Process data from CSV files
            all_years_data = process_cost_per_pupil_data(config, current_dir)
            
            if not all_years_data:
                logger.error("No data was processed, cannot generate SQL statements")
                raise Exception("No data was processed, cannot generate SQL statements")
            
            # Generate SQL statements
            sql_statements = generate_table_creation_statements()
            
            # Get valid district IDs from the database
            valid_district_ids = get_valid_district_ids()
            
            # Generate insert statements
            data_statements = generate_insert_statements(all_years_data, valid_district_ids)
            sql_statements.extend(data_statements)
            
            # Save to cache
            os.makedirs(cache_dir, exist_ok=True)
            with open(cache_file, 'w') as f:
                f.write(';\n'.join(sql_statements))
            
            logger.info(f"Cached {len(sql_statements)} SQL statements to {cache_file}")
        
        # Execute SQL statements
        execute_sql_statements(sql_statements)
            
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        raise


def downgrade():
    """Alembic downgrade function to remove cost per pupil tables."""
    try:
        sql_statements = [
            "DROP TABLE IF EXISTS district_cost_per_pupil CASCADE",
            "DROP TABLE IF EXISTS state_cost_per_pupil CASCADE"
        ]
        
        for statement in sql_statements:
            op.execute(sa.text(statement))
            
        logger.info("Successfully dropped cost per pupil tables")
    except Exception as e:
        logger.error(f"Error during downgrade: {e}")
        raise
