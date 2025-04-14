"""Education Freedom Account

Revision ID: 854abd432fef
Revises: 49358ad1275f
Create Date: 2024-04-09 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
import logging
import pandas as pd
import yaml
import re
import os
from datetime import datetime

# Configure logger
logger = logging.getLogger('alembic.runtime.migration')

# Revision identifiers, used by Alembic
revision = '854abd432fef'
down_revision = '49358ad1275f'
branch_labels = None
depends_on = None


def load_config():
    """Load configuration from YAML file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.abspath(os.path.join(current_dir, '../config/generate_education_freedom_accounts.yaml'))
    logger.info(f"Attempting to load configuration from: {config_path}")
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            logger.info(f"Successfully loaded configuration: {config}")
            return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        logger.error(f"Does the file exist? {os.path.exists(config_path)}")
        raise Exception(f"Error loading configuration: {e}")


def clean_value(value):
    """Clean numeric values by removing $, commas, etc."""
    if pd.isna(value) or value == "":
        return None
    
    value_str = str(value)
    
    # Remove non-numeric characters except decimal point
    cleaned = re.sub(r'[^0-9.-]', '', value_str)
    
    return cleaned if cleaned != "" else None


def process_entry_types(df, config, year=None):
    """Process education freedom account entry types from row 3."""
    logger.info(f"Processing entry types from DataFrame with shape: {df.shape}")
    logger.info(f"DataFrame columns: {df.columns.tolist()}")
    entry_types = []
    entry_type_values = []
    entry_id = 1
    col_index = 6  # Start at column G (0-indexed would be 6)
    
    # Use provided year or default to start year from config
    year_to_use = year if year is not None else config['file_settings']['year_start']
    
    while col_index < len(df.columns):
        cell_value = df.iloc[1, col_index]  # Row 3 (0-indexed is 1)
        logger.info(f"Checking entry type at column {col_index} (col name: {df.columns[col_index]}), value: {cell_value}")
        
        if pd.notna(cell_value) and cell_value != "":
            # Get value from two rows down and one column to the right
            if col_index + 1 < len(df.columns):
                value_cell = df.iloc[3, col_index + 1]
                value = clean_value(value_cell)
                
                # Skip entries with null value cells
                if value is None:
                    logger.info(f"Skipping entry type '{cell_value}' because value cell is null")
                    col_index += 2
                    continue
                
                entry_type = {
                    'id': entry_id,
                    'name': str(cell_value).strip(),
                    'description': f"{str(cell_value).strip()}",
                    'column': df.columns[col_index]
                }
                
                # Create entry type value
                entry_type_value = {
                    'entry_type_id': entry_id,
                    'year': year_to_use,
                    'value': value
                }
                
                logger.info(f"Found entry type: {entry_type}")
                entry_types.append(entry_type)
                entry_type_values.append(entry_type_value)
                entry_id += 1
            else:
                logger.warning(f"Skipping entry type '{cell_value}' at column {col_index} - no value column available")
        
        col_index += 2  # Move two columns to the right
    
    logger.info(f"Processed {len(entry_types)} entry types")
    return entry_types, entry_type_values


def process_entries(df, entry_types, year):
    """Process education freedom account entries for towns."""
    logger.info(f"Processing entries for year {year} with {len(entry_types)} entry types")
    entries = []
    
    # Find rows where column E has an integer value
    town_count = 0
    entry_count = 0
    
    # Log all column names to help debug
    logger.info(f"Available columns in DataFrame: {df.columns.tolist()}")
    
    for index, row in df.iterrows():
        town_id = row.iloc[4]  # Column E (0-indexed is 4)
        
        if pd.notna(town_id) and isinstance(town_id, (int, float)) and town_id == int(town_id):
            town_id = int(town_id)
            town_count += 1
            logger.debug(f"Processing town ID {town_id} at row {index}")
            
            # Create entries for each entry type
            for entry_type in entry_types:
                col_name = entry_type['column']
                
                # Check if the column exists before trying to get its index
                if col_name not in df.columns:
                    logger.warning(f"Column '{col_name}' not found in DataFrame for year {year}. "
                                  f"Skipping entry type: {entry_type['name']}")
                    continue
                    
                col_index = df.columns.get_loc(col_name)
                
                # Get value from the current row at the entry type's column
                value = clean_value(row.iloc[col_index])
                
                if value is not None:
                    entry = {
                        'town_id': town_id,
                        'year': year,
                        'entry_type_id': entry_type['id'],
                        'value': value
                    }
                    entries.append(entry)
                    entry_count += 1
    
    logger.info(f"Processed {town_count} towns with a total of {entry_count} entries for year {year}")
    return entries


def generate_sql(entry_types, entry_type_values, entries):
    """Generate SQL INSERT statements for all data."""
    logger.info(f"Generating SQL statements for {len(entry_types)} entry types, {len(entry_type_values)} entry type values, and {len(entries)} entries")
    sql_statements = []
    
    # Entry types inserts
    sql_statements.append("-- Insert education freedom account entry types")
    for entry_type in entry_types:
        sql_statements.append(f"""INSERT INTO education_freedom_account_entry_type (id, name, description, date_created, date_updated) VALUES ({entry_type['id']}, '{entry_type['name'].replace("'", "''")}', '{entry_type['description'].replace("'", "''")}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);""")
    
    # Entry type values inserts
    sql_statements.append("\n-- Insert education freedom account entry type values")
    for entry_type_value in entry_type_values:
        value = entry_type_value['value'] if entry_type_value['value'] is not None else "NULL"
        sql_statements.append(f"""INSERT INTO education_freedom_account_entry_type_value (education_freedom_account_entry_type_id_fk, year, value, date_created, date_updated) VALUES ({entry_type_value['entry_type_id']}, {entry_type_value['year']}, {value}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);""")
    
    # Entries inserts
    sql_statements.append("\n-- Insert education freedom account entries")
    towns_with_data = set()
    valid_entries = 0
    skipped_entries = 0
    
    for entry in entries:
        value = entry['value'] if entry['value'] is not None else "NULL"
        
        # Check if town exists using text()
        exists_check = sa.text("""
            SELECT EXISTS (
                SELECT 1 FROM town WHERE id = :town_id
            )
        """)
        result = op.get_bind().execute(exists_check, {"town_id": entry['town_id']}).scalar()
        
        if result:
            sql_statements.append(f"""INSERT INTO education_freedom_account_entry (town_id_fk, year, education_freedom_account_entry_type_id_fk, value, date_created, date_updated) VALUES ({entry['town_id']}, {entry['year']}, {entry['entry_type_id']}, {value}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);""")
            towns_with_data.add(entry['town_id'])
            valid_entries += 1
        else:
            logger.warning(f"Town ID {entry['town_id']} not found in database, skipping entry")
            skipped_entries += 1
    
    logger.info(f"Generated {valid_entries} valid entry SQL statements for {len(towns_with_data)} unique towns")
    logger.info(f"Skipped {skipped_entries} entries due to missing town IDs")
    
    return "\n".join(sql_statements)


def upgrade():
    logger.info("Starting Education Freedom Account migration upgrade")
    
    # Create new tables
    logger.info("Creating education_freedom_account_entry_type table")
    op.execute("""
        CREATE TABLE education_freedom_account_entry_type (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    logger.info("Creating education_freedom_account_entry_type_value table")
    op.execute("""
        CREATE TABLE education_freedom_account_entry_type_value (
            id SERIAL PRIMARY KEY,
            education_freedom_account_entry_type_id_fk INTEGER NOT NULL,
            year INTEGER NOT NULL,
            value NUMERIC(15, 2),
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_efa_entry_type
                FOREIGN KEY (education_freedom_account_entry_type_id_fk)
                REFERENCES education_freedom_account_entry_type(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_efa_entry_type_value
                UNIQUE (education_freedom_account_entry_type_id_fk, year)
        )
    """)

    logger.info("Creating education_freedom_account_entry table")
    op.execute("""
        CREATE TABLE education_freedom_account_entry (
            id SERIAL PRIMARY KEY,
            town_id_fk INTEGER NOT NULL,
            year INTEGER NOT NULL,
            education_freedom_account_entry_type_id_fk INTEGER NOT NULL,
            value NUMERIC(15, 2),
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_efa_town
                FOREIGN KEY (town_id_fk)
                REFERENCES town(id)
                ON DELETE CASCADE,
            CONSTRAINT fk_efa_entry_type
                FOREIGN KEY (education_freedom_account_entry_type_id_fk)
                REFERENCES education_freedom_account_entry_type(id)
                ON DELETE CASCADE,
            CONSTRAINT unique_efa_entry
                UNIQUE (town_id_fk, year, education_freedom_account_entry_type_id_fk)
        )
    """)

    # Create triggers for the new tables
    logger.info("Creating triggers for tables")
    op.execute(f"""
        CREATE TRIGGER trigger_update_education_freedom_account_entry_type_timestamp
        BEFORE UPDATE ON education_freedom_account_entry_type
        FOR EACH ROW EXECUTE FUNCTION update_date_updated_column()
    """)

    op.execute(f"""
        CREATE TRIGGER trigger_update_education_freedom_account_entry_type_value_timestamp
        BEFORE UPDATE ON education_freedom_account_entry_type_value
        FOR EACH ROW EXECUTE FUNCTION update_date_updated_column()
    """)

    op.execute(f"""
        CREATE TRIGGER trigger_update_education_freedom_account_entry_timestamp
        BEFORE UPDATE ON education_freedom_account_entry
        FOR EACH ROW EXECUTE FUNCTION update_date_updated_column()
    """)

    # Create indexes
    logger.info("Creating indexes for tables")
    op.execute("CREATE INDEX idx_efa_entry_type_value_type ON education_freedom_account_entry_type_value(education_freedom_account_entry_type_id_fk)")
    op.execute("CREATE INDEX idx_efa_entry_type_value_year ON education_freedom_account_entry_type_value(year)")
    op.execute("CREATE INDEX idx_efa_entry_town ON education_freedom_account_entry(town_id_fk)")
    op.execute("CREATE INDEX idx_efa_entry_year ON education_freedom_account_entry(year)")
    op.execute("CREATE INDEX idx_efa_entry_type ON education_freedom_account_entry(education_freedom_account_entry_type_id_fk)")

    # Load and process data from Excel files
    logger.info("Starting data loading process")
    
    try:
        logger.info("Loading configuration")
        config = load_config()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Check for existing cache file first
        cache_dir = os.path.abspath(os.path.join(current_dir, config['file_settings']['sql_cache_dir']))
        cache_file = os.path.join(cache_dir, f'{revision}_cache.sql')
        logger.info(f"Cache directory path: {cache_dir}")
        logger.info(f"Cache file path: {cache_file}")
        
        if os.path.exists(cache_file):
            logger.info(f"Found existing SQL cache file at: {cache_file}")
            with open(cache_file, 'r') as f:
                sql_statements = f.read()
            logger.info(f"Loaded cached SQL statements ({os.path.getsize(cache_file)} bytes)")
        else:
            logger.info("No cache file found, processing input files")
            # Process input files
            all_entry_types = []
            all_entry_type_values = []
            all_entries = []
            entry_type_ids = {}
            
            # Get the base pattern for input files
            input_pattern = config['file_settings']['default_input']
            base_dir = os.path.abspath(os.path.join(current_dir, os.path.dirname(input_pattern)))
            base_pattern = os.path.basename(input_pattern)
            
            logger.info(f"Input pattern: {input_pattern}")
            logger.info(f"Base directory: {base_dir}")
            logger.info(f"Base pattern: {base_pattern}")
            
            # Remove asterisks and get the pattern parts
            pattern_parts = base_pattern.split('****')
            logger.info(f"Pattern parts: {pattern_parts}")
            
            # Generate file paths for each year
            year_start = config['file_settings']['year_start']
            year_end = config['file_settings']['year_end']
            logger.info(f"Processing years from {year_start} to {year_end}")
            
            found_files = 0
            
            for year in range(year_start, year_end+1):
                file_pattern = f"{pattern_parts[0]}{year}{pattern_parts[1] if len(pattern_parts) > 1 else ''}"
                file_path = os.path.join(base_dir, file_pattern)
                
                logger.info(f"Looking for year {year} file at: {file_path}")
                
                # Check if the file exists
                if os.path.exists(file_path):
                    found_files += 1
                    logger.info(f"Found input file for year {year}: {file_path}")
                    
                    # Load the Excel file
                    try:
                        logger.info(f"Loading Excel file: {file_path}")
                        df = pd.read_excel(file_path)
                        logger.info(f"Successfully loaded Excel file with shape: {df.shape}")
                        
                        # Process entry types if this is the first file
                        if not all_entry_types:
                            logger.info("Processing entry types from first file")
                            entry_types, entry_type_values = process_entry_types(df, config)
                            all_entry_types = entry_types
                            all_entry_type_values = entry_type_values
                            
                            # Create a mapping of entry types by name
                            for entry_type in all_entry_types:
                                entry_type_ids[entry_type['name']] = entry_type['id']
                        else:
                            # For subsequent files, check for new entry types
                            logger.info("Checking for new entry types in subsequent file")
                            new_entry_types, new_entry_type_values = process_entry_types(df, config, year)
                            
                            for i, new_entry_type in enumerate(new_entry_types):
                                if new_entry_type['name'] not in entry_type_ids:
                                    new_id = len(all_entry_types) + 1
                                    new_entry_type['id'] = new_id
                                    new_entry_type_values[i]['entry_type_id'] = new_id
                                    new_entry_type_values[i]['year'] = year
                                    
                                    all_entry_types.append(new_entry_type)
                                    all_entry_type_values.append(new_entry_type_values[i])
                                    entry_type_ids[new_entry_type['name']] = new_id
                                    logger.info(f"Added new entry type: {new_entry_type['name']}")
                                else:
                                    # Entry type exists, but add a new value for this year
                                    existing_id = entry_type_ids[new_entry_type['name']]
                                    new_entry_type_values[i]['entry_type_id'] = existing_id
                                    new_entry_type_values[i]['year'] = year
                                    all_entry_type_values.append(new_entry_type_values[i])
                        
                        # Process entries for this file
                        logger.info(f"Processing entries for year {year}")
                        entries = process_entries(df, all_entry_types, year)
                        logger.info(f"Found {len(entries)} entries for year {year}")
                        all_entries.extend(entries)
                    except Exception as e:
                        logger.error(f"Error processing Excel file {file_path}: {e}")
                        raise
                else:
                    logger.warning(f"File not found for year {year}: {file_path}")
            
            logger.info(f"Processed {found_files} files out of {year_end - year_start + 1} possible years")
            logger.info(f"Total entry types found: {len(all_entry_types)}")
            logger.info(f"Total entry type values found: {len(all_entry_type_values)}")
            logger.info(f"Total entries found: {len(all_entries)}")
            
            if len(all_entries) == 0:
                logger.error("No entries were found! Check file paths and Excel structure.")
            
            # Generate SQL with combined data
            logger.info("Generating SQL statements")
            sql_statements = generate_sql(all_entry_types, all_entry_type_values, all_entries)
            
            # Save to cache
            logger.info(f"Creating cache directory: {cache_dir}")
            os.makedirs(cache_dir, exist_ok=True)
            logger.info(f"Writing SQL cache to: {cache_file}")
            with open(cache_file, 'w') as f:
                f.write(sql_statements)
            logger.info(f"Successfully created SQL cache file ({os.path.getsize(cache_file)} bytes)")
        
        # Execute SQL statements
        logger.info("Starting SQL execution")
        statement_count = sql_statements.count(';')
        logger.info(f"Found approximately {statement_count} SQL statements to execute")
        
        executed = 0
        skipped = 0
        
        for statement in sql_statements.split(';'):
            statement = statement.strip()
            if not statement:  # Skip empty statements
                continue
                
            try:
                # Uncomment this line to actually execute the SQL
                op.execute(sa.text(statement))
                executed += 1
                if executed % 100 == 0:
                    logger.info(f"Executed {executed} statements so far")
            except Exception as e:
                if "duplicate key" in str(e).lower():
                    logger.warning(f"Skipped duplicate key: {str(e)[:100]}")
                    skipped += 1
                else:
                    logger.error(f"Error executing SQL statement: {e}")
                    logger.error(f"Statement: {statement[:300]}...")
                    raise
            
        logger.info(f"SQL execution complete: {executed} statements executed, {skipped} skipped")
    except Exception as e:
        logger.error(f"Critical error during migration: {e}")
        raise Exception(f"Error during migration: {e}")
    
    logger.info("Migration completed successfully")


def downgrade():
    logger.info("Starting Education Freedom Account migration downgrade")
    # Drop tables in reverse order to handle dependencies
    logger.info("Dropping education_freedom_account_entry table")
    op.execute("DROP TABLE IF EXISTS education_freedom_account_entry CASCADE")
    logger.info("Dropping education_freedom_account_entry_type_value table")
    op.execute("DROP TABLE IF EXISTS education_freedom_account_entry_type_value CASCADE")
    logger.info("Dropping education_freedom_account_entry_type table")
    op.execute("DROP TABLE IF EXISTS education_freedom_account_entry_type CASCADE")
    logger.info("Downgrade completed successfully")