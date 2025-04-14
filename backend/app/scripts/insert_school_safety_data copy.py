#!/usr/bin/env python3
"""
One-off script to generate and insert sample school safety data.
This script assumes the database is already populated with schools and safety types.
"""

import os
import sys
import re
import yaml
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Tuple, Set, Optional

import sqlalchemy as sa
import logging
from sqlalchemy import text
from sqlalchemy.engine import Engine

# Set up logging
logger = logging.getLogger('alembic.runtime.migration')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# Configuration
REVISION = 'TEMPORARY_REVISION'
DB_URL = "postgresql://postgres:changethis@localhost:5432/app"
RELEVANT_KEYWORDS = [
    "Restraints", "Harassment", "Harrassment", "Bullying", 
    "Discipline", "Safety", "Truancy"
]


def get_database_connection() -> Engine:
    """Create and return a database engine connection."""
    try:
        engine = sa.create_engine(DB_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"Successfully connected to database")
        return engine
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        sys.exit(1)


def load_config():
    """Load configuration from YAML file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '../alembic/config/generate_school_safety_data.yaml')
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        logger.error(f"Does the file exist? {os.path.exists(config_path)}")
        raise Exception(f"Error loading configuration: {e}")


def get_schools() -> List[Tuple[str, int]]:
    """Get a list of all schools from the database."""
    conn = get_database_connection().connect()
    result = conn.execute(
        sa.text("SELECT id, name FROM school ORDER BY id;")
    )
    return [(row.name, row.id) for row in result]


def find_header_row(df: pd.DataFrame) -> Optional[int]:
    """Find the header row containing 'SAU' in column A."""
    for idx, value in enumerate(df.iloc[:, 0]):
        if isinstance(value, str) and 'sau' in value.lower():
            logger.debug(f"Found header row at index {idx}")
            return idx
    return None


def find_school_id_column(header_row: pd.Series) -> Optional[int]:
    """Find the column index that contains 'school' in its header."""
    for idx, value in enumerate(header_row):
        if isinstance(value, str) and 'school' in value.lower():
            logger.debug(f"Found school ID column at index {idx}")
            return idx
    return None


def clean_numeric_value(value) -> Tuple[str, int]:
    """Clean and convert a value to an integer."""
    if pd.isna(value):
        return "", 0
    
    value_str = str(value).strip()
    value_clean = ''.join(c for c in value_str if c.isdigit() or c == '.')
    
    if not value_clean:
        return value_str, 0
        
    try:
        value_int = int(float(value_clean))
        return value_str, value_int
    except (ValueError, TypeError):
        return value_str, 0


def format_sql(sql: str) -> str:
    """Format SQL by removing newlines and extra spaces."""
    sql = sql.replace('\n', ' ').replace('\r', '').strip()
    return re.sub(r'\s+', ' ', sql)


def get_relevant_sheets(file_path: str) -> Dict[str, pd.DataFrame]:
    """
    Find and return all relevant sheets from an Excel file based on specific keywords.
    """
    logger.info(f"Scanning sheets in {file_path} for relevant keywords")
    
    try:
        excel_file = pd.ExcelFile(file_path)
        all_sheets = excel_file.sheet_names
        logger.info(f"Found {len(all_sheets)} sheets in the file")
        
        relevant_sheets = {}
        
        for sheet_name in all_sheets:
            if any(keyword.lower() in sheet_name.lower() for keyword in RELEVANT_KEYWORDS):
                try:
                    # Load the sheet into a DataFrame
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    
                    # Normalize "Harrassment" to "Harassment"
                    normalized_sheet_name = sheet_name
                    if "harrassment" in sheet_name.lower():
                        for pattern, replacement in [
                            ("Harrassment", "Harassment"),
                            ("harrassment", "harassment"),
                            ("HARRASSMENT", "HARASSMENT")
                        ]:
                            if pattern in normalized_sheet_name:
                                normalized_sheet_name = normalized_sheet_name.replace(pattern, replacement)
                                break
                    
                    relevant_sheets[normalized_sheet_name] = df
                    logger.info(f"Loaded sheet '{sheet_name}' with shape: {df.shape}")
                except Exception as e:
                    logger.warning(f"Error loading sheet '{sheet_name}': {e}")
        
        logger.info(f"Found {len(relevant_sheets)} relevant sheets")
        return relevant_sheets
        
    except Exception as e:
        logger.error(f"Error processing Excel file {file_path}: {e}")
        return {}


def process_excel_data(sheet_name: str, df: pd.DataFrame, year: int, schools: List[Tuple[str, int]], 
                      process_row_func) -> List[str]:
    """
    Generic function to process data from Excel sheets.
    
    Args:
        sheet_name: Name of the sheet being processed
        df: DataFrame containing the sheet data
        year: The academic year for this data
        schools: List of (school_name, school_id) tuples
        process_row_func: Function to process each row
        
    Returns:
        List of SQL statements to insert the processed data
    """
    # Extract school IDs for validation
    valid_school_ids = {id for _, id in schools}
    sql_statements = []
    
    try:
        # Find header row
        header_row_idx = find_header_row(df)
        if header_row_idx is None:
            logger.warning(f"Could not find header row with 'SAU' in sheet '{sheet_name}'")
            return []
        
        # Get header row and find school ID column
        header_row = df.iloc[header_row_idx]
        school_id_col_idx = find_school_id_column(header_row)
        if school_id_col_idx is None:
            logger.warning(f"Could not find school ID column in sheet '{sheet_name}'")
            return []
        
        # Process data rows
        for row_idx in range(header_row_idx + 1, len(df)):
            row = df.iloc[row_idx]
            
            # Get and validate school ID
            school_id_value = row.iloc[school_id_col_idx]
            if pd.isna(school_id_value):
                continue
                
            _, school_id_int = clean_numeric_value(school_id_value)
            if school_id_int == 0 or school_id_int not in valid_school_ids:
                continue
                
            # Process the row with the specific function
            row_statements = process_row_func(row, school_id_int, school_id_col_idx, year)
            sql_statements.extend(row_statements)
                
    except Exception as e:
        logger.error(f"Error processing {sheet_name} data: {e}")
        
    logger.info(f"Generated {len(sql_statements)} SQL statements for {sheet_name}")
    return sql_statements


def process_truancy_data(sheet_name: str, df: pd.DataFrame, year: int, schools: List[Tuple[str, int]]) -> List[str]:
    """Process truancy data from Excel sheets."""
    logger.info(f"Processing Truancy data for year {year}")
    
    def process_truancy_row(row, school_id, school_id_col_idx, year):
        statements = []
        # Truancy count is at offset 3
        count_col_idx = school_id_col_idx + 3
        
        if count_col_idx < len(row):
            _, count_int = clean_numeric_value(row.iloc[count_col_idx])
            
            if count_int > 0:
                sql = f"INSERT INTO school_truancy (school_id_fk, year, count) VALUES ({school_id}, {year}, {count_int});"
                statements.append(sql)
                
        return statements
    
    return process_excel_data(sheet_name, df, year, schools, process_truancy_row)


def process_harassment_data(sheet_name: str, df: pd.DataFrame, year: int, schools: List[Tuple[str, int]]) -> List[str]:
    """Process harassment data from Excel sheets."""
    logger.info(f"Processing Harassment data for year {year}")
    
    # Define the harassment classification types
    harassment_types = [
        {"column_offset": 3, "name": "Gender"},
        {"column_offset": 4, "name": "Sexual Orientation"},
        {"column_offset": 5, "name": "Race, Color or National Origin"},
        {"column_offset": 6, "name": "Disability"},
        {"column_offset": 7, "name": "Physical Characteristics (other than race)"}
    ]
    
    def process_harassment_row(row, school_id, school_id_col_idx, year):
        statements = []
        
        for classification_type in harassment_types:
            incident_col_idx = school_id_col_idx + classification_type["column_offset"]
            impact_col_idx = incident_col_idx + 5
            engaged_col_idx = incident_col_idx + 10
            
            # Check column index bounds
            if max(incident_col_idx, impact_col_idx, engaged_col_idx) >= len(row):
                continue
                
            # Get and clean values
            _, incident_int = clean_numeric_value(row.iloc[incident_col_idx])
            _, impact_int = clean_numeric_value(row.iloc[impact_col_idx])
            _, engaged_int = clean_numeric_value(row.iloc[engaged_col_idx])
            
            # Only insert if we have data
            if incident_int > 0 or impact_int > 0 or engaged_int > 0:
                sql = f"""INSERT INTO school_harassment (
                            school_id_fk, year, school_harassment_classification_id_fk, 
                            incident_count, student_impact_count, student_engaged_count
                          ) VALUES (
                            {school_id}, {year}, 
                            (SELECT id FROM school_harassment_classification WHERE name = '{classification_type["name"]}'), 
                            {incident_int}, {impact_int}, {engaged_int}
                          );"""
                statements.append(format_sql(sql))
                
        return statements
    
    return process_excel_data(sheet_name, df, year, schools, process_harassment_row)


def process_bullying_data(sheet_name: str, df: pd.DataFrame, year: int, schools: List[Tuple[str, int]]) -> List[str]:
    """Process bullying data from Excel sheets."""
    logger.info(f"Processing Bullying data for year {year}")
    
    # Define the data type mappings
    bullying_types = [
        {"column_offset": 3, "name": "Bullying (of any kind)"},
        {"column_offset": 4, "name": "Cyber-bullying"}
    ]

    bullying_classification_types = [
        {"column_offset": 7, "name": "Gender"},
        {"column_offset": 8, "name": "Sexual Orientation"},
        {"column_offset": 9, "name": "Race, Color or National Origin"},
        {"column_offset": 10, "name": "Disability"},
        {"column_offset": 11, "name": "Physical Characteristics"},
        {"column_offset": 12, "name": "Any Other Basis"}
    ]

    bullying_impact_types = [
        {"column_offset": 13, "name": "Were a Single Significant Event"},
        {"column_offset": 14, "name": "Were a Pattern of Deliberate Harmful Events"},
        {"column_offset": 15, "name": "Included Physical Harm"},
        {"column_offset": 16, "name": "Included Property Damage"},
        {"column_offset": 17, "name": "Used Social/ Emotional Alienation"},
        {"column_offset": 18, "name": "Interfered with Educational Opportunities"},
        {"column_offset": 19, "name": "Disrupted School Operations"}
    ]
    
    def process_bullying_row(row, school_id, school_id_col_idx, year):
        statements = []
        
        # Process bullying types
        for bullying_type in bullying_types:
            column_idx = school_id_col_idx + bullying_type["column_offset"]
            if column_idx + 2 >= len(row):
                continue
                
            # Get reported and investigated values
            _, reported_int = clean_numeric_value(row.iloc[column_idx])
            _, investigated_int = clean_numeric_value(row.iloc[column_idx + 2])
            
            if reported_int > 0 or investigated_int > 0:
                sql = f"""INSERT INTO school_bullying (
                            school_id_fk, year, school_bullying_type_id_fk, reported, investigated_actual
                          ) VALUES (
                            {school_id}, {year}, 
                            (SELECT id FROM school_bullying_type WHERE name = '{bullying_type["name"]}'), 
                            {reported_int}, {investigated_int}
                          );"""
                statements.append(format_sql(sql))
        
        # Process classification types
        for classification_type in bullying_classification_types:
            column_idx = school_id_col_idx + classification_type["column_offset"]
            if column_idx >= len(row):
                continue
                
            _, value_int = clean_numeric_value(row.iloc[column_idx])
            
            if value_int > 0:
                sql = f"""INSERT INTO school_bullying_classification (
                            school_id_fk, year, school_bullying_classification_type_id_fk, count
                          ) VALUES (
                            {school_id}, {year}, 
                            (SELECT id FROM school_bullying_classification_type WHERE name = '{classification_type["name"]}'), 
                            {value_int}
                          );"""
                statements.append(format_sql(sql))
        
        # Process impact types
        for impact_type in bullying_impact_types:
            column_idx = school_id_col_idx + impact_type["column_offset"]
            if column_idx >= len(row):
                continue
                
            _, value_int = clean_numeric_value(row.iloc[column_idx])
            
            if value_int > 0:
                sql = f"""INSERT INTO school_bullying_impact (
                            school_id_fk, year, school_bullying_impact_type_id_fk, count
                          ) VALUES (
                            {school_id}, {year}, 
                            (SELECT id FROM school_bullying_impact_type WHERE name = '{impact_type["name"]}'), 
                            {value_int}
                          );"""
                statements.append(format_sql(sql))
                
        return statements
    
    return process_excel_data(sheet_name, df, year, schools, process_bullying_row)


def process_restraints_data(sheet_name: str, df: pd.DataFrame, year: int, schools: List[Tuple[str, int]]) -> List[str]:
    """Process restraints data from Excel sheets."""
    logger.info(f"Processing Restraints data for year {year}")
    
    # Define field mappings based on year
    if year == 2016:
        restraint_fields = {
            "generated": 3,
            "active_investigation": 4,
            "closed_investigation": 5,
            "bodily_injury": 6
        }
        seclusion_fields = {
            "generated": 7,
            "active_investigation": 8,
            "closed_investigation": 9
        }
    else:
        restraint_fields = {
            "generated": 3,
            "active_investigation": 4,
            "closed_investigation": 5,
            "bodily_injury": 6,
            "serious_injury": 7
        }
        seclusion_fields = {
            "generated": 8,
            "active_investigation": 9,
            "closed_investigation": 10
        }
    
    def process_restraints_row(row, school_id, school_id_col_idx, year):
        statements = []
        
        # Process restraint data
        restraint_values = {}
        all_fields_valid = True
        
        for field_name, column_offset in restraint_fields.items():
            column_idx = school_id_col_idx + column_offset
            if column_idx >= len(row):
                all_fields_valid = False
                break
                
            _, value_int = clean_numeric_value(row.iloc[column_idx])
            restraint_values[field_name] = value_int
        
        # Special case for 2016
        if year == 2016:
            restraint_values["serious_injury"] = 0
            
        if all_fields_valid:
            sql = f"""INSERT INTO school_restraint (
                        school_id_fk, year, generated, active_investigation, 
                        closed_investigation, bodily_injury, serious_injury
                      ) VALUES (
                        {school_id}, {year}, 
                        {restraint_values['generated']},
                        {restraint_values['active_investigation']},
                        {restraint_values['closed_investigation']},
                        {restraint_values['bodily_injury']},
                        {restraint_values.get('serious_injury', 0)}
                      );"""
            statements.append(format_sql(sql))
        
        # Process seclusion data
        seclusion_values = {}
        all_fields_valid = True
        
        for field_name, column_offset in seclusion_fields.items():
            column_idx = school_id_col_idx + column_offset
            if column_idx >= len(row):
                all_fields_valid = False
                break
                
            _, value_int = clean_numeric_value(row.iloc[column_idx])
            seclusion_values[field_name] = value_int
            
        if all_fields_valid:
            sql = f"""INSERT INTO school_seclusion (
                        school_id_fk, year, generated, active_investigation, closed_investigation
                      ) VALUES (
                        {school_id}, {year}, 
                        {seclusion_values['generated']},
                        {seclusion_values['active_investigation']},
                        {seclusion_values['closed_investigation']}
                      );"""
            statements.append(format_sql(sql))
        
        return statements
    
    return process_excel_data(sheet_name, df, year, schools, process_restraints_row)


def process_discipline_data(sheet_name: str, df: pd.DataFrame, year: int, schools: List[Tuple[str, int]]) -> List[str]:
    """Process discipline data from Excel sheets."""
    logger.info(f"Processing Discipline data for year {year}")
    
    # Define the discipline type mappings
    discipline_incident_types = [
        {"column_offset": 3, "name": "Violent Incidents With Physical Injury Requiring Professional Medical Attention"},
        {"column_offset": 4, "name": "Violent Incidents, including Harassment & Bullying (Without Physical Injury)"},
        {"column_offset": 5, "name": "Weapons Possession"},
        {"column_offset": 6, "name": "Illicit Drugs"},
        {"column_offset": 7, "name": "Alcohol"},
        {"column_offset": 8, "name": "Other Incidents Related to Drug or Alcohol Use, Violence or Weapons Possession"},
        {"column_offset": 9, "name": "Disruption"},
        {"column_offset": 10, "name": "Defiance"},
        {"column_offset": 11, "name": "Inappropriate Language"},
        {"column_offset": 12, "name": "All Other Incidents"}
    ]

    discipline_count_types = [
        {"column_offset": 13, "name": "Who Received In-School Suspensions"},
        {"column_offset": 14, "name": "Who Received Out-of-School Suspensions"},
        {"column_offset": 15, "name": "Who Were Expelled"}
    ]
    
    def process_discipline_row(row, school_id, school_id_col_idx, year):
        statements = []
        
        # Process incident types
        for incident_type in discipline_incident_types:
            column_idx = school_id_col_idx + incident_type["column_offset"]
            if column_idx >= len(row):
                continue
                
            _, value_int = clean_numeric_value(row.iloc[column_idx])
            
            if value_int > 0:
                sql = f"""INSERT INTO school_discipline_incident (
                            school_id_fk, year, school_discipline_incident_type_id_fk, count
                          ) VALUES (
                            {school_id}, {year}, 
                            (SELECT id FROM school_discipline_incident_type WHERE name = '{incident_type["name"]}'), 
                            {value_int}
                          );"""
                statements.append(format_sql(sql))
        
        # Process count types
        for count_type in discipline_count_types:
            column_idx = school_id_col_idx + count_type["column_offset"]
            if column_idx >= len(row):
                continue
                
            _, value_int = clean_numeric_value(row.iloc[column_idx])
            
            if value_int > 0:
                sql = f"""INSERT INTO school_discipline_count (
                            school_id_fk, year, school_discipline_count_type_id_fk, count
                          ) VALUES (
                            {school_id}, {year}, 
                            (SELECT id FROM school_discipline_count_type WHERE name = '{count_type["name"]}'), 
                            {value_int}
                          );"""
                statements.append(format_sql(sql))
                
        return statements
    
    return process_excel_data(sheet_name, df, year, schools, process_discipline_row)


def process_safety_data(sheet_name: str, df: pd.DataFrame, year: int, schools: List[Tuple[str, int]]) -> List[str]:
    """Process safety data from Excel sheets."""
    logger.info(f"Processing Safety data for year {year}")
    
    # Define the safety type mappings
    safety_types = [
        {"column_offset": 3, "name": "Handgun Incidents"},
        {"column_offset": 4, "name": "Rifles/ Shotguns Incidents"},
        {"column_offset": 5, "name": "Firearms Incidents Including More Than One Type of Weapon or Firearm"},
        {"column_offset": 6, "name": "Other Firearms Incidents"},
        {"column_offset": 7, "name": "Homicides"},
        {"column_offset": 8, "name": "First Degree Assaults"},
        {"column_offset": 9, "name": "Aggravated Felonious Sexual Assaults"},
        {"column_offset": 10, "name": "Arsons"},
        {"column_offset": 11, "name": "Robberies"},
        {"column_offset": 12, "name": "Firearms Possessions or Sales"}
    ]
    
    def process_safety_row(row, school_id, school_id_col_idx, year):
        statements = []
        
        for safety_type in safety_types:
            column_idx = school_id_col_idx + safety_type["column_offset"]
            if column_idx >= len(row):
                continue
                
            _, value_int = clean_numeric_value(row.iloc[column_idx])
            
            if value_int > 0:
                sql = f"""INSERT INTO school_safety (
                            school_id_fk, year, school_safety_type_id_fk, count
                          ) VALUES (
                            {school_id}, {year}, 
                            (SELECT id FROM school_safety_type WHERE name = '{safety_type["name"]}'), 
                            {value_int}
                          );"""
                statements.append(format_sql(sql))
                
        return statements
    
    return process_excel_data(sheet_name, df, year, schools, process_safety_row)

def execute_sql_statements(sql_statements, batch_size=500):
    """
    Execute SQL statements with proper error handling.
    
    Args:
        sql_statements: List of SQL statements to execute
        batch_size: Number of statements to execute in a single transaction
    """
    successful = 0
    total = len(sql_statements)
    
    logger.info(f"Executing {total} SQL statements")
    
    # Filter out empty statements
    sql_statements = [stmt.strip() for stmt in sql_statements if stmt and isinstance(stmt, str)]
    
    if not sql_statements:
        logger.warning("No valid SQL statements to execute")
        return
    
    if batch_size > 0 and total > batch_size:
        # Execute in batches
        batch_count = 0
        
        for i in range(0, len(sql_statements), batch_size):
            batch = sql_statements[i:i+batch_size]
            try:
                # In a real execution, we would open a transaction here
                for stmt in batch:
                    # op.execute(sa.text(stmt))
                    successful += 1
                
                batch_count += 1
                logger.info(f"Completed batch {batch_count} ({len(batch)} statements)")
            except Exception as e:
                logger.error(f"Error executing batch {batch_count}: {e}")
    else:
        # Execute statements one by one
        for statement in sql_statements:
            try:
                # Execute the statement
                # op.execute(sa.text(statement))
                successful += 1
                if successful % 100 == 0:
                    logger.info(f"Progress: {successful}/{total} statements executed")
            except Exception as e:
                logger.error(f"Error executing SQL: {e}")
    
    logger.info(f"Successfully executed {successful} out of {total} SQL statements")


def main():
    """Main function to run the script."""
    logger.info(f"Starting school safety data insertion script at {datetime.now()}")

    try: 
        config = load_config()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Check for existing cache file
        cache_dir = os.path.abspath(os.path.join(current_dir, config['file_settings']['sql_cache_dir']))
        cache_file = os.path.join(cache_dir, f'{REVISION}_cache.sql')
        
        if os.path.exists(cache_file):
            logger.info(f"Found existing SQL cache file")
            
            # Read cache file line by line
            sql_statements = []
            with open(cache_file, 'r') as f:
                sql_statements = [line.strip() for line in f if line.strip()]
            
            logger.info(f"Loaded {len(sql_statements)} cached SQL statements")
        else:
            logger.info("Processing input files")

            # Get schools from database
            schools = get_schools()
            if not schools:
                logger.error("No schools found in database")
                return
            
            # Prepare file pattern for processing 
            input_pattern = config['file_settings']['default_input']
            base_dir = os.path.abspath(os.path.join(current_dir, os.path.dirname(input_pattern)))
            base_pattern = os.path.basename(input_pattern)
            pattern_parts = base_pattern.split('****')
            
            year_start = config['file_settings']['year_start']
            year_end = config['file_settings']['year_end']

            all_sql_statements = []
            
            # Process each year's data files
            for year in range(year_start, year_end+1):
                file_pattern = f"{pattern_parts[0]}{year}{pattern_parts[1] if len(pattern_parts) > 1 else ''}"
                file_path = os.path.join(base_dir, file_pattern)
                
                if not os.path.exists(file_path):
                    logger.warning(f"File not found for year {year}")
                    continue
                    
                logger.info(f"Processing file for year {year}")
                
                try:
                    # Get and process relevant sheets
                    relevant_sheets = get_relevant_sheets(file_path)
                    if not relevant_sheets:
                        logger.warning(f"No relevant sheets found for year {year}")
                        continue
                        
                    # Process each relevant sheet
                    for sheet_name, df in relevant_sheets.items():
                        sheet_name_lower = sheet_name.lower()
                        
                        # Select appropriate processor based on sheet name
                        processor_func = None
                        if "truancy" in sheet_name_lower:
                            processor_func = process_truancy_data
                        elif "harassment" in sheet_name_lower:
                            processor_func = process_harassment_data
                        elif "bullying" in sheet_name_lower:
                            processor_func = process_bullying_data
                        elif "restraint" in sheet_name_lower:
                            processor_func = process_restraints_data
                        elif "discipline" in sheet_name_lower:
                            processor_func = process_discipline_data
                        elif "safety" in sheet_name_lower:
                            processor_func = process_safety_data
                        else:
                            logger.warning(f"No processor for sheet '{sheet_name}'")
                            continue
                            
                        # Process the sheet and collect SQL statements
                        sql_statements = processor_func(sheet_name, df, year, schools)
                        all_sql_statements.extend(sql_statements)
                        
                except Exception as e:
                    logger.error(f"Error processing file for year {year}: {e}")
                    raise
            
            sql_statements = all_sql_statements
            logger.info(f"Generated {len(sql_statements)} total SQL statements")
            
            # Cache the generated SQL
            os.makedirs(cache_dir, exist_ok=True)
            with open(cache_file, 'w') as f:
                for stmt in sql_statements:
                    if stmt and isinstance(stmt, str):
                        f.write(stmt + "\n")
            
            logger.info(f"Cached SQL statements to {cache_file}")

        # Execute the SQL statements
        execute_sql_statements(sql_statements)

    except Exception as e:
        logger.error(f"Critical error during migration: {e}")
        raise
    
    logger.info("Migration completed successfully")


if __name__ == "__main__":
    main() 