"""School Data Load

Revision ID: 2aada939afdc
Revises: 36d545ef85b7
Create Date: 2024-11-21 19:43:20.752323

"""
from alembic import op
import sqlalchemy as sa
import pandas as pd
import sys
import os
import re
import yaml
from datetime import datetime
import logging

# Add this near the top of the file
logger = logging.getLogger('alembic.runtime.migration')

# revision identifiers, used by Alembic.
revision = '2aada939afdc'
down_revision = 'b4f374d72f78'
branch_labels = None
depends_on = None


def load_config():
    """Load configuration from YAML file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.abspath(os.path.join(current_dir, '../config/generate_schools_config.yaml'))
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise Exception(f"Error loading configuration: {e}")

def generate_grades_data():
    """Generate the fixed grades data structure."""
    return {
        'P': {'id': 1, 'name': 'Preschool'},
        'K': {'id': 2, 'name': 'Kindergarten'},
        '1': {'id': 3, 'name': 'Grade 1'},
        '2': {'id': 4, 'name': 'Grade 2'},
        '3': {'id': 5, 'name': 'Grade 3'},
        '4': {'id': 6, 'name': 'Grade 4'},
        '5': {'id': 7, 'name': 'Grade 5'},
        '6': {'id': 8, 'name': 'Grade 6'},
        '7': {'id': 9, 'name': 'Grade 7'},
        '8': {'id': 10, 'name': 'Grade 8'},
        '9': {'id': 11, 'name': 'Grade 9'},
        '10': {'id': 12, 'name': 'Grade 10'},
        '11': {'id': 13, 'name': 'Grade 11'},
        '12': {'id': 14, 'name': 'Grade 12'},
        'PG': {'id': 15, 'name': 'Post Graduate'}
    }

def generate_region_data():
    """Generate mapping of region names to IDs."""
    return {
        'South Central': 1,
        'Lakes Region': 2,
        'Southeast': 3,
        'North Country': 4,
        'Southwest': 5,
        'Unknown': 6
    }

def generate_school_type_data():
    """Generate mapping of school type descriptions to IDs."""
    return {
        'Public School': 1,
        'Interstate School': 2,
        'Charter Schools approved by the state': 3,
        'Joint Maintenance Agreement': 4,
        'Public Academy': 5,
        'Other Private Schools': 6,
        'Christian School': 7,
        'In-State Spec Ed and Other Private': 8,
        'In-State Private Special Education': 9,
        'Parochial School': 10,
        'Prep School': 11
    }

def process_sau_data(df):
    """Process SAU data from DataFrame and return organized data structure.
    
    Args:
        df: DataFrame containing SAU and staff data
        
    Returns:
        Dictionary with SAU data and associated staff members
    """
    sau_data = {}
    
    # Filter for rows with valid integer SAU IDs
    for _, row in df.iterrows():
        try:
            sau_id = int(row[0])  # Column A contains SAU ID
        except (ValueError, TypeError):
            continue
            
        # If this SAU hasn't been processed yet, add the SAU data
        if sau_id not in sau_data:
            sau_data[sau_id] = {
                'name': row[1],          # Column B: SAU name
                'address1': row[8],      # Column I: address_1
                'address2': row[9],      # Column J: address_2
                'town': row[10],         # Column K: town
                'state': row[12],        # Column M: state
                'zip': row[13],          # Column N: zip_code
                'phone': row[14],        # Column O: phone
                'fax': row[15],          # Column P: fax
                'webpage': row[17],      # Column R: webpage
                'staff': []              # List to store staff members
            }
        
        # Add staff member data if name fields are present
        if pd.notna(row[5]) or pd.notna(row[7]):  # If first_name or last_name exists
            staff_member = {
                'admin_type': row[2],    # Column C: admin_type
                'title': row[3],         # Column D: title
                'first_name': row[5],    # Column F: first_name
                'last_name': row[7],     # Column H: last_name
                'email': row[16]         # Column Q: email
            }
            sau_data[sau_id]['staff'].append(staff_member)
    
    return sau_data

def parse_grade_span(grade_span, grades_data):
    """Parse grade span string and return a list of grade IDs."""
    if pd.isna(grade_span) or grade_span == '':
        return []
    
    grade_ids = []
    
    # Split by spaces to handle formats like "P K 1-8"
    parts = grade_span.split()
    
    for part in parts:
        if part in grades_data:
            # Direct match for P, K
            grade_ids.append(grades_data[part]['id'])
        elif '-' in part:
            # Range like 1-8
            start, end = part.split('-')
            if start in grades_data and end in grades_data:
                for grade_id in range(grades_data[start]['id'], grades_data[end]['id'] + 1):
                    grade_ids.append(grade_id)
    
    return sorted(list(set(grade_ids)))  # Remove duplicates and sort

def process_district_town_data(df, grades_data, existing_sau_data=None):
    """Process district, town, SAU data and map grade spans to specific grade IDs.
    
    Args:
        df: DataFrame containing district and town data
        grades_data: Dictionary of grade information
        existing_sau_data: Pre-processed SAU data from the SAU file
    """
    # Initialize collections
    districts = {}  # district_id -> {name, sau_id, grades}
    towns = {}      # town_id -> {name, district_id}
    saus = existing_sau_data if existing_sau_data is not None else {}  # Start with existing SAU data
    
    def parse_grade_span(grade_span):
        """Parse grade span string and return a list of grade IDs."""
        if pd.isna(grade_span) or grade_span == '':
            return []
        
        grade_ids = []
        # Split by spaces to handle formats like "P K 1-8"
        parts = grade_span.split()
        
        for part in parts:
            if part in grades_data:
                # Direct match for P, K
                grade_ids.append(grades_data[part]['id'])
            elif '-' in part:
                # Range like 1-8
                start, end = part.split('-')
                if start in grades_data and end in grades_data:
                    for grade_id in range(grades_data[start]['id'], grades_data[end]['id'] + 1):
                        grade_ids.append(grade_id)
        
        return sorted(list(set(grade_ids)))  # Remove duplicates and sort
    
    # Process each row
    for _, row in df.iterrows():
        district_id = row['District Id']
        district_name = row['District']
        town_id = row['Town Id']
        town_name = row['Town']
        sau_id = row.get('SAUId')
        sau_name = row.get('SAU')
        grade_span = row.get('Grade Span')
        
        # Add SAU if not already present in either existing data or newly added data
        if sau_id and not pd.isna(sau_id) and sau_id not in saus:
            saus[sau_id] = {
                'name': sau_name,
                'staff': []  # Initialize empty staff list for consistency
            }
        
        # Add district if not already present
        if district_id not in districts and not pd.isna(district_id):
            grade_ids = parse_grade_span(grade_span)
            districts[district_id] = {
                'name': district_name,
                'sau_id': sau_id if not pd.isna(sau_id) else None,
                'grade_ids': grade_ids,
                'is_public': True
            }
        
        # Add town if not already present
        if town_id not in towns and not pd.isna(town_id):
            towns[town_id] = {
                'name': town_name,
                'district_id': district_id if not pd.isna(district_id) else None
            }
        elif not pd.isna(town_id) and not pd.isna(district_id):
            # If town exists but has a new district relationship, add the district ID
            # This preserves the original district but allows for multiple district relationships
            if 'district_ids' not in towns[town_id]:
                towns[town_id]['district_ids'] = []
                # Add original district first if it exists
                if towns[town_id]['district_id'] is not None:
                    towns[town_id]['district_ids'].append(towns[town_id]['district_id'])
            
            # Add new district if it's not already in the list
            if district_id not in towns[town_id]['district_ids']:
                towns[town_id]['district_ids'].append(district_id)
    
    return {
        'districts': districts,
        'towns': towns,
        'saus': saus
    }

def find_town_id(city_name, town_data):
    """Find town ID based on city name."""
    if pd.isna(city_name) or city_name == '':
        return None
    
    # Hardcoded mappings for specific cities
    hardcoded_mappings = {
        'groveton': 'northumberland',
        'contoocook': 'hopkinton',
        'woodsville': 'haverhill',
        'meriden': 'plainfield',
        'sanbornville': 'wakefield',
        'suncook': 'pembroke'
    }
    
    # Normalize city name
    city_name_lower = city_name.lower().strip()
    
    # Check if we have a hardcoded mapping for this city
    if city_name_lower in hardcoded_mappings:
        target_town = hardcoded_mappings[city_name_lower]
        logger.info(f"Using hardcoded mapping: '{city_name}' → '{target_town}'")
        
        # Find the town ID for the mapped town name
        for town_id, town_info in town_data.items():
            if town_info['name'].lower().strip() == target_town:
                return town_id
    
    # Try exact match (case insensitive)
    for town_id, town_info in town_data.items():
        if town_info['name'].lower().strip() == city_name_lower:
            return town_id
    
    # If no exact match, try matching on first or last word
    tokens = city_name_lower.split()
    if len(tokens) > 1:
        first_word = tokens[0]
        last_word = tokens[-1]
        
        for town_id, town_info in town_data.items():
            town_name = town_info['name'].lower().strip()
            # Try matching with first word
            if town_name == first_word:
                logger.info(f"Partial match found for city '{city_name}' using first word '{first_word}'")
                return town_id
            # Try matching with last word
            if town_name == last_word:
                logger.info(f"Partial match found for city '{city_name}' using last word '{last_word}'")
                return town_id
    
    logger.error(f"Town ID not found for city: {city_name}")
    return None

def process_school_data(df, config, district_data, sau_data, grades_data, region_data, school_type_data, town_data):
    """Process school data from DataFrame and return organized data structure."""
    schools = {}
    
    def get_column_value(row, column_name):
        """Helper function to safely get column value using configuration mapping."""
        try:
            column_index = config['column_mappings'].get(column_name)
            if column_index is None:
                return None
            return row.get(column_index)
        except Exception:
            return None
    
    # Process each row in the dataframe
    for _, row in df.iterrows():
        school_id = get_column_value(row, 'school_id')
        
        # Skip if no valid school_id
        if pd.isna(school_id):
            continue
            
        # Get city name and find corresponding town_id
        city_name = get_column_value(row, 'city')
        town_id = find_town_id(city_name, town_data)
        
        # Check if SAU exists and add it if it doesn't
        sau_id = get_column_value(row, 'sau_id')
        if sau_id and sau_id not in sau_data and not pd.isna(sau_id):
            sau_name = get_column_value(row, 'sau_name')  # Assuming there's a sau_name column
            sau_data[sau_id] = {
                'name': sau_name if sau_name else f'SAU {sau_id}'
            }
        
        # Check if district exists and add it if it doesn't
        district_id = get_column_value(row, 'district_id')
        if district_id and district_id not in district_data and not pd.isna(district_id):
            district_name = get_column_value(row, 'district_name')  # Assuming there's a district_name column
            grade_span = get_column_value(row, 'grade_span')
            
            district_data[district_id] = {
                'name': district_name if district_name else '',
                'sau_id': sau_id if not pd.isna(sau_id) else None,
                'grade_ids': parse_grade_span(grade_span, grades_data) if grade_span else [],
                'is_public': False
            }
        
        # Store school information
        schools[school_id] = {
            'name': get_column_value(row, 'school_name'),
            'sau_id': sau_id,
            'district_id': district_id,
            'region_id': region_data.get(get_column_value(row, 'region_name') or 'Unknown'),
            'school_type_id': school_type_data.get(get_column_value(row, 'school_type_desc')),
            'principal_first_name': get_column_value(row, 'principal_first_name'),
            'principal_last_name': get_column_value(row, 'principal_last_name'),
            'address1': get_column_value(row, 'address1'),
            'address2': get_column_value(row, 'address2'),
            'city': get_column_value(row, 'city'),
            'town_id': town_id,
            'state': get_column_value(row, 'state'),
            'zip': get_column_value(row, 'zip'),
            'phone': get_column_value(row, 'phone'),
            'fax': get_column_value(row, 'fax'),
            'email': get_column_value(row, 'email'),
            'county': get_column_value(row, 'county'),
            'webpage': get_column_value(row, 'webpage'),
            'open_date': get_column_value(row, 'open_date'),
            'grade_ids': parse_grade_span(get_column_value(row, 'grade_span'), grades_data)
        }
    
    return {'schools': schools}

def generate_sql(grades_data, region_data, school_type_data, district_data, town_data, sau_data, school_data):
    """Generate SQL INSERT statements using pre-processed data structures.
    
    Args:
        grades_data: Dictionary of grade information
        region_data: Dictionary of region mappings
        school_type_data: Dictionary of school type mappings
        district_data: Dictionary of district information
        town_data: Dictionary of town information
        sau_data: Dictionary of SAU information with staff data
        school_data: Dictionary of school information
    
    Returns:
        String containing all SQL INSERT statements
    """
    
    def clean_string(value):
        """Clean and escape a string for SQL."""
        if pd.isna(value) or value == '':
            return "NULL"
        # Replace single quotes with two single quotes for SQL
        cleaned = str(value).replace("'", "''")
        return f"'{cleaned}'"

    def clean_string_not_null(value):
        """Clean and escape a string for SQL, returning empty string if NULL."""
        if pd.isna(value) or value == '':
            return "''"
        # Replace single quotes with two single quotes for SQL
        cleaned = str(value).replace("'", "''")
        return f"'{cleaned}'"

    def parse_date(date_str):
        """Parse a date string and return an SQL-formatted date."""
        if pd.isna(date_str) or date_str == '':
            return "CURRENT_TIMESTAMP"
        try:
            date_obj = datetime.strptime(date_str, '%m/%d/%Y %I:%M:%S %p')
            return f"'{date_obj.strftime('%Y-%m-%d')}'"
        except:
            return "CURRENT_TIMESTAMP"

    # Initialize SQL statement collections
    sau_sql = []
    sau_staff_sql = []
    district_sql = []
    town_sql = []
    town_district_xref_sql = []
    region_sql = []
    school_type_sql = []
    grades_sql = []
    school_sql = []
    school_grade_xref_sql = []
    district_grade_xref_sql = []

    # Generate SAU and SAU staff INSERT statements
    for sau_id, sau_info in sau_data.items():
        sau_sql.append(
            f"INSERT INTO sau (id, name, address1, address2, town, town_id_fk, state, zip, phone, fax, webpage, "
            f"date_created, date_updated) VALUES ("
            f"{sau_id}, "
            f"{clean_string_not_null(sau_info.get('name', ''))}, "
            f"{clean_string(sau_info.get('address1'))}, "
            f"{clean_string(sau_info.get('address2'))}, "
            f"{clean_string(sau_info.get('town'))}, "
            f"{sau_info.get('town_id') if sau_info.get('town_id') is not None else 'NULL'}, "
            f"{clean_string(sau_info.get('state'))}, "
            f"{clean_string(sau_info.get('zip'))}, "
            f"{clean_string(sau_info.get('phone'))}, "
            f"{clean_string(sau_info.get('fax'))}, "
            f"{clean_string(sau_info.get('webpage'))}, "
            f"CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);"
        )
        
        # Generate SAU staff INSERT statements
        for staff in sau_info.get('staff', []):
            if pd.notna(staff.get('first_name')) or pd.notna(staff.get('last_name')):
                sau_staff_sql.append(
                    f"INSERT INTO sau_staff (sau_id_fk, first_name, last_name, title, admin_type, email, "
                    f"date_created, date_updated) VALUES ("
                    f"{sau_id}, "
                    f"{clean_string_not_null(staff.get('first_name'))}, "
                    f"{clean_string_not_null(staff.get('last_name'))}, "
                    f"{clean_string(staff.get('title'))}, "
                    f"'{staff.get('admin_type', 'SUP')}', "  # Default to SUP if not specified
                    f"{clean_string(staff.get('email'))}, "
                    f"CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);"
                )

    # Generate district INSERT statements
    for district_id, district_info in district_data.items():
        district_sql.append(
            f"INSERT INTO district (id, name, sau_id_fk, is_public, date_created, date_updated) "
            f"VALUES ({district_id}, {clean_string_not_null(district_info['name'])}, "
            f"{district_info['sau_id'] if district_info['sau_id'] is not None else 'NULL'}, "
            f"{district_info['is_public']}, "
            f"CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);"
        )
        
        # Generate district-grade relationships
        if 'grade_ids' in district_info:
            for grade_id in district_info['grade_ids']:
                district_grade_xref_sql.append(
                    f"INSERT INTO district_grade_xref (district_id_fk, grade_id_fk, date_created, date_updated) "
                    f"VALUES ({district_id}, {grade_id}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);"
                )

    # Generate town INSERT statements
    for town_id, town_info in town_data.items():
        town_sql.append(
            f"INSERT INTO town (id, name, date_created, date_updated) "
            f"VALUES ({town_id}, {clean_string(town_info['name'])}, "
            f"CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);"
        )
        
        # Generate town-district relationships
        if 'district_ids' in town_info:
            for district_id in town_info['district_ids']:
                town_district_xref_sql.append(
                    f"INSERT INTO town_district_xref (town_id_fk, district_id_fk, date_created, date_updated) "
                    f"VALUES ({town_id}, {district_id}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);"
                )
        elif 'district_id' in town_info and town_info['district_id'] is not None:
            town_district_xref_sql.append(
                f"INSERT INTO town_district_xref (town_id_fk, district_id_fk, date_created, date_updated) "
                f"VALUES ({town_id}, {town_info['district_id']}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);"
            )

    # Generate region INSERT statements
    for region_name, region_id in region_data.items():
        region_sql.append(
            f"INSERT INTO region (id, name, date_created, date_updated) "
            f"VALUES ({region_id}, {clean_string(region_name)}, "
            f"CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);"
        )

    # Generate school type INSERT statements
    for type_name, type_id in school_type_data.items():
        school_type_sql.append(
            f"INSERT INTO school_type (id, name, date_created, date_updated) "
            f"VALUES ({type_id}, {clean_string(type_name)}, "
            f"CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);"
        )

    # Generate grades INSERT statements
    for grade_key, grade_info in grades_data.items():
        grades_sql.append(
            f"INSERT INTO grades (id, name, date_created, date_updated) "
            f"VALUES ({grade_info['id']}, '{grade_info['name']}', "
            f"CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);"
        )

    # Generate school and school_grade_xref INSERT statements
    for school_id, school_info in school_data['schools'].items():
        # Construct the INSERT statement as a single string
        sql_statement = (
            f"INSERT INTO school (id, name, sau_id_fk, district_id_fk, region_id_fk, school_type_id_fk, "
            f"principal_first_name, principal_last_name, address1, address2, city, town_id_fk, state, zip, phone, "
            f"fax, email, county, webpage, date_created, date_updated) VALUES ("
            f"{school_id}, "
            f"{clean_string(school_info['name'])}, "
            f"{school_info['sau_id'] if school_info['sau_id'] is not None else 'NULL'}, "
            f"{school_info['district_id'] if school_info['district_id'] is not None else 'NULL'}, "
            f"{school_info['region_id'] if school_info['region_id'] is not None else 'NULL'}, "
            f"{school_info['school_type_id'] if school_info['school_type_id'] is not None else 'NULL'}, "
            f"{clean_string(school_info['principal_first_name'])}, "
            f"{clean_string(school_info['principal_last_name'])}, "
            f"{clean_string(school_info['address1'])}, "
            f"{clean_string(school_info['address2'])}, "
            f"{clean_string(school_info['city'])}, "
            f"{school_info['town_id'] if school_info['town_id'] is not None else 'NULL'}, "
            f"{clean_string(school_info['state'])}, "
            f"{clean_string(school_info['zip'])}, "
            f"{clean_string(school_info['phone'])}, "
            f"{clean_string(school_info['fax'])}, "
            f"{clean_string(school_info['email'])}, "
            f"{clean_string(school_info['county'])}, "
            f"{clean_string(school_info['webpage'])}, "
            f"CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);"
        )
        school_sql.append(sql_statement)

        # Generate school-grade relationships
        for grade_id in school_info['grade_ids']:
            school_grade_xref_sql.append(
                f"INSERT INTO school_grade_xref (school_id_fk, grade_id_fk, date_created, date_updated) "
                f"VALUES ({school_id}, {grade_id}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);"
            )

    # Combine all SQL statements with section headers
    all_sql = []
    all_sql.append("-- Town table INSERT statements")
    all_sql.extend(town_sql)
    all_sql.append("\n-- SAU table INSERT statements")
    all_sql.extend(sau_sql)
    all_sql.append("\n-- SAU Staff table INSERT statements")
    all_sql.extend(sau_staff_sql)
    all_sql.append("\n-- District table INSERT statements")
    all_sql.extend(district_sql)
    all_sql.append("\n-- Town-District relationships")
    all_sql.extend(town_district_xref_sql)
    all_sql.append("\n-- Region table INSERT statements")
    all_sql.extend(region_sql)
    all_sql.append("\n-- School Type table INSERT statements")
    all_sql.extend(school_type_sql)
    all_sql.append("\n-- Grades table INSERT statements")
    all_sql.extend(grades_sql)
    all_sql.append("\n-- School table INSERT statements")
    all_sql.extend(school_sql)
    all_sql.append("\n-- School-Grade relationships")
    all_sql.extend(school_grade_xref_sql)
    all_sql.append("\n-- District-Grade relationships")  
    all_sql.extend(district_grade_xref_sql)

    return "\n".join(all_sql)

def upgrade():
    # Load configuration
    config = load_config()
    
    try:
        # Check for existing cache file first
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cache_dir = os.path.abspath(os.path.join(current_dir, config['file_settings']['sql_cache_dir']))
        cache_file = os.path.join(cache_dir, f'{revision}_cache.sql')
        
        if os.path.exists(cache_file):
            logger.info(f"Found existing SQL cache file at: {cache_file}")
            with open(cache_file, 'r') as f:
                sql_statements = f.read().split('\n')
        else:
            # Generate all mapping data first
            grades_data = generate_grades_data()
            region_data = generate_region_data()
            school_type_data = generate_school_type_data()
            
            # Read the district/town data file
            file_path = os.path.abspath(os.path.join(current_dir, config['file_settings']['district_file']['path']))
            district_town_df = pd.read_csv(file_path)
            
            # Process SAU data
            file_path = os.path.abspath(os.path.join(current_dir, config['file_settings']['sau_file']['path']))
            sau_df = pd.read_excel(file_path, header=None, skiprows=config['file_settings']['sau_file']['start_row'])
            sau_data = process_sau_data(sau_df)

            # Process district and town data
            district_file_data = process_district_town_data(district_town_df, grades_data, sau_data)
            district_data =  district_file_data['districts']
            town_data = district_file_data['towns']
            sau_data = district_file_data['saus']

            #iterate of all the sau_data and set the town_id to the town_id from the town_data
            for sau_id, sau_info in sau_data.items():
                if 'town_id' not in sau_info or sau_info.get('town_id') is None:
                    sau_info['town_id'] = find_town_id(sau_info.get('town'), town_data)

            # Process school data
            file_path = os.path.abspath(os.path.join(current_dir, config['file_settings']['school_file']['path']))

            school_df = pd.read_excel(file_path, header=None, skiprows=config['file_settings']['school_file']['start_row'])
            school_data = process_school_data(
                school_df, 
                config, 
                district_data,
                sau_data,
                grades_data, 
                region_data, 
                school_type_data,
                town_data
            )

            # Generate school SQL with all mapping data
            sql_statements_str = generate_sql(
                grades_data,
                region_data,
                school_type_data,
                district_data,
                town_data,
                sau_data,
                school_data
            )
            
            # Save to cache
            os.makedirs(cache_dir, exist_ok=True)
            logger.info(f"Creating new SQL cache file at: {cache_file}")
            with open(cache_file, 'w') as f:
                f.write(sql_statements_str)
            
            logger.info(f"SQL INSERT statements have been generated and saved to {cache_file}")

            # Split the generated string into a list of lines/statements for execution
            sql_statements = sql_statements_str.split('\n')

            # Optionally, update the log message to count non-empty lines starting with INSERT
            insert_count = len([s for s in sql_statements if s.strip().startswith('INSERT INTO')])
            logger.info(f"Generated {insert_count} INSERT statements")

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
        logger.error(f"Error processing files: {str(e)}")
        raise  # Re-raise the exception to see the full traceback

def downgrade():
    pass
