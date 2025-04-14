"""Assessment Data Import

Revision ID:234adb12cac2
Revises: 97ab8dffd654
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
revision = '234adb12cac2'
down_revision = '97ab8dffd654'
branch_labels = None
depends_on = None

# Config path 
CONFIG_PATH = "app/alembic/config/assessment_data_config.yaml"


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


def parse_assessment_percentage(value):
    """Parse assessment percentage values, identifying special cases."""
    if pd.isna(value) or value == '' or value == '-':
        return None, None
    
    # Check for special notation
    if isinstance(value, str):
        if '*' in value:
            return None, 'TOO_FEW_SAMPLES'
        elif '<' in value and '10' in value:
            return None, 'SCORE_UNDER_10'
        elif '>' in value and '90' in value:
            return None, 'SCORE_OVER_90'
        
        # Try to extract numeric value
        try:
            # Remove % and other non-numeric characters
            cleaned = re.sub(r'[^0-9.]', '', value)
            if cleaned == '':
                return None, None
            return float(cleaned), None
        except ValueError:
            return None, None
    
    elif isinstance(value, (int, float)):
        return float(value), None
    
    return None, None


def parse_student_range(value):
    """Parse student range in format 'low-high'."""
    if pd.isna(value) or value == '' or value == '-':
        return None, None
    
    if isinstance(value, str):
        # Remove commas from the string before processing
        value = value.replace(',', '')
        
        # Try to extract range values
        match = re.search(r'(\d+)\s*-\s*(\d+)', value)
        if match:
            try:
                low = int(match.group(1))
                high = int(match.group(2))
                return low, high
            except ValueError:
                pass
        
        # Try as single value
        try:
            # No need to remove commas again as we did it at the start
            num = int(float(re.sub(r'[^0-9.]', '', value)))
            # Check for known bad data value in 2019 data
            if num == 43753:
                return None, None
            return num, num
        except ValueError:
            pass
    
    elif isinstance(value, (int, float)):
        num = int(value)
        # Check for known bad data value in 2019 data
        if num == 43753:
            return None, None
        return num, num
    
    return None, None


def get_assessment_subject_id(subject):
    """Get assessment subject ID from subject name."""
    subject_map = {
        'Math': 1,
        'Reading': 2,
        'Science': 3,
        'MAT': 1,
        'REA': 2,
        'SCI': 3,
        'mat': 1,
        'rea': 2,
        'sci': 3
    }
    return subject_map.get(subject)


def get_or_create_subgroup(subgroup_name, existing_subgroups, next_id):
    """Get existing subgroup ID or create a new one.
    
    Returns:
        tuple: (subgroup_id, is_new) where is_new indicates if the subgroup was newly created
    """
    if subgroup_name in existing_subgroups:
        return existing_subgroups[subgroup_name], False
    
    # Create new subgroup
    subgroup_id = next_id
    existing_subgroups[subgroup_name] = subgroup_id
    return subgroup_id, True


def get_school_id(school_name, conn, district_name=None, school_name_translations=None):
    """Get school ID from school name, optionally filtered by district name.
    
    Args:
        school_name: Name of the school to search for
        conn: Database connection
        district_name: Optional district name to filter by
        school_name_translations: Dictionary of school name translations
        
    Returns:
        int: School ID if found, None otherwise
    """
    try:
        if pd.isna(school_name) or not school_name:
            return None
        
        # Apply translation if school name is in the translation map
        if school_name_translations and school_name in school_name_translations:
            translated_name = school_name_translations[school_name]
        else:
            translated_name = school_name
        
        # Build query, optionally filtering by district
        if district_name and not pd.isna(district_name):
            query = f"""
                SELECT s.id FROM school s
                JOIN district d ON s.district_id_fk = d.id
                WHERE s.name = '{translated_name.replace("'", "''")}'
                AND d.name = '{district_name.replace("'", "''")}'
            """
        else:
            query = f"SELECT id FROM school WHERE name = '{translated_name.replace("'", "''")}'"
        
        result = conn.execute(sa.text(query))
        row = result.fetchone()
        return row[0] if row else None
    except Exception as e:
        logger.error(f"Error querying school ID for {school_name}: {e}")
        return None


def get_district_id(district_name, conn):
    """Get district ID from district name."""
    try:
        if pd.isna(district_name) or not district_name:
            return None
        
        query = f"SELECT id FROM district WHERE name = '{district_name.replace("'", "''")}'"
        result = conn.execute(sa.text(query))
        row = result.fetchone()
        return row[0] if row else None
    except Exception as e:
        logger.error(f"Error querying district ID for {district_name}: {e}")
        return None


def get_grade_id(grade_name, conn):
    """Get grade ID from grade name."""
    try:
        if pd.isna(grade_name) or not grade_name:
            return None
        
        # Standardize grade name
        grade_name = str(grade_name).strip().lower()
        if grade_name == 'all':
            return None
        
        if grade_name.startswith('0') and len(grade_name) > 1 and grade_name[1:].isdigit():
            grade_name = grade_name[1:]
            
        query = f"SELECT id FROM grades WHERE name = 'Grade {grade_name.replace("'", "''")}'"
        result = conn.execute(sa.text(query))
        row = result.fetchone()
        return row[0] if row else None
    except Exception as e:
        logger.error(f"Error querying grade ID for {grade_name}: {e}")
        return None


def generate_sql_insert_statement(table, fields, values):
    """Generate SQL insert statement with proper formatting.
    
    Args:
        table (str): Table name to insert into
        fields (list): List of field names
        values (list): List of values corresponding to fields
        
    Returns:
        str: SQL insert statement formatted as a single line
    """
    # Format for readability (displayed as multiple lines in code)
    fields_str = ',\n            '.join(fields)
    values_str = ',\n            '.join(values)
    
    stmt = f"""
    INSERT INTO {table} (
        {fields_str}
    ) VALUES (
        {values_str}
    )
    """
    
    # Convert to single line for storage
    return ' '.join(line.strip() for line in stmt.strip().split('\n'))


def format_sql_value(value, is_exception=False):
    """Format a value for SQL insertion.
    
    Args:
        value: The value to format
        is_exception (bool): Whether this is an exception value that needs quotes
        
    Returns:
        str: Formatted value for SQL
    """
    if value is None:
        return 'NULL'
    elif is_exception and value is not None:
        return f"'{value}'"
    else:
        return str(value)


def process_assessment_data(config, current_dir, conn):
    """Process assessment data from CSV files and return SQL insert statements."""
    file_settings = config.get('file_settings', {})
    year_start = int(file_settings.get('year_start', 2018))
    year_end = int(file_settings.get('year_end', 2024))
    
    # Get school name translations from config
    school_name_translations = config.get('school_name_translations', {})
    
    # Build reverse mapping to identify schools that map to the same database school
    translated_to_originals = {}
    for original, translated in school_name_translations.items():
        if translated not in translated_to_originals:
            translated_to_originals[translated] = []
        translated_to_originals[translated].append(original)
    
    # Identify schools with multiple mappings
    merged_schools = {translated: originals for translated, originals in translated_to_originals.items() if len(originals) > 1}
    
    # Track subgroups for creation
    subgroups = {}
    next_subgroup_id = 1
    
    # SQL statements for inserts, organized by type
    subgroup_insert_statements = []  # Statements to create subgroups (must be executed first)
    data_insert_statements = []      # Statements to insert actual assessment data (must be executed after subgroups)
    
    # Track missing schools and districts
    missing_schools = {}  # Format: {school_name: {'years': set(years), 'translated': translated_name}}
    missing_districts = {}  # Format: {district_name: set(years)}
    
    # Buffer for merged school data
    merged_school_buffer = {}
    
    # Define common fields for all assessment tables
    common_fields = [
        'assessment_subject_id_fk', 'year', 'grade_id_fk', 'assessment_subgroup_id_fk',
        'total_fay_students_low', 'total_fay_students_high',
        'level_1_percentage', 'level_1_percentage_exception',
        'level_2_percentage', 'level_2_percentage_exception',
        'level_3_percentage', 'level_3_percentage_exception',
        'level_4_percentage', 'level_4_percentage_exception',
        'above_proficient_percentage', 'above_proficient_percentage_exception',
        'participate_percentage', 'mean_sgp', 'average_score'
    ]
    
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
            df = pd.read_csv(file_path, dtype=str)
            
            logger.info(f"Processing assessment data for year {year}, found {len(df)} rows")
            
            # Before processing rows, log the columns in this year's file
            columns = list(df.columns)
            logger.info(f"Year {year} file columns: {columns}")
            
            # Process each row
            for idx, row in df.iterrows():
                try:
                    # Skip if missing essential data
                    if pd.isna(row.get('Subject')):
                        continue
                    
                    # Determine the level (state, district, school)
                    level = row.get('Level of Data')
                    if pd.isna(level):
                        continue
                    
                    level = level.strip()
                    
                    # Get subject ID
                    subject = row.get('Subject')
                    subject_id = get_assessment_subject_id(subject)
                    if subject_id is None:
                        logger.warning(f"Unknown subject: {subject}")
                        continue
                    
                    # Handle subgroup with robust column detection
                    subgroup = None
                    
                    # Check all possible column names for subgroup data
                    possible_subgroup_columns = ['Subgroup', 'subgroup', 'Sub Group', 'sub group', 'SubGroup']
                    for col in possible_subgroup_columns:
                        if col in row:
                            subgroup_value = row.get(col)
                            if not pd.isna(subgroup_value) and subgroup_value:
                                subgroup = str(subgroup_value).strip()
                                break
                    
                    # Default to 'All Students' if not found or empty
                    if not subgroup:
                        subgroup = 'All Students'
                    
                    # Log subgroup detection details at debug level
                    logger.debug(f"Year {year}, Row {idx}: Detected subgroup '{subgroup}'")
                    
                    # Get or create subgroup
                    subgroup_id, is_new_subgroup = get_or_create_subgroup(subgroup, subgroups, next_subgroup_id)
                    if is_new_subgroup:
                        logger.info(f"Creating subgroup: '{subgroup}'")
                        # Add subgroup creation statement - these must be executed before data inserts
                        subgroup_insert_statements.append(
                            f"INSERT INTO assessment_subgroup (id, name, description) VALUES ({subgroup_id}, '{subgroup.replace("'", "''")}', NULL)"
                        )
                        next_subgroup_id += 1
                    
                    # Parse year
                    year_val = row.get('yearId', year)
                    if pd.isna(year_val):
                        year_val = year
                    else:
                        try:
                            year_val = int(float(year_val))
                        except ValueError:
                            year_val = year
                    
                    # Parse grade
                    grade_name = row.get('Grade', 'All')
                    grade_id = get_grade_id(grade_name, conn)
                    
                    # Parse student count range
                    students_low, students_high = parse_student_range(row.get('Total FAY Students'))
                    
                    # Parse percentage fields with exception handling
                    level1_pct, level1_exc = parse_assessment_percentage(row.get('level1%'))
                    level2_pct, level2_exc = parse_assessment_percentage(row.get('level2%'))
                    level3_pct, level3_exc = parse_assessment_percentage(row.get('level3%'))
                    level4_pct, level4_exc = parse_assessment_percentage(row.get('level4%'))
                    above_prof_pct, above_prof_exc = parse_assessment_percentage(row.get('Above prof% (lvl 3&4)'))
                    
                    # Parse other numeric fields
                    participate_pct, _ = parse_assessment_percentage(row.get('Participate%'))
                    
                    mean_sgp = None
                    if not pd.isna(row.get('Mean SGP')):
                        try:
                            mean_sgp = float(row.get('Mean SGP'))
                        except (ValueError, TypeError):
                            mean_sgp = None
                    
                    avg_score = None
                    if not pd.isna(row.get('Avg Score')):
                        try:
                            avg_score = float(row.get('Avg Score'))
                        except (ValueError, TypeError):
                            avg_score = None
                    
                    # Common values for all levels
                    common_values = [
                        str(subject_id),
                        str(year_val),
                        format_sql_value(grade_id),
                        str(subgroup_id),
                        format_sql_value(students_low),
                        format_sql_value(students_high),
                        format_sql_value(level1_pct),
                        format_sql_value(level1_exc, is_exception=True),
                        format_sql_value(level2_pct),
                        format_sql_value(level2_exc, is_exception=True),
                        format_sql_value(level3_pct),
                        format_sql_value(level3_exc, is_exception=True),
                        format_sql_value(level4_pct),
                        format_sql_value(level4_exc, is_exception=True),
                        format_sql_value(above_prof_pct),
                        format_sql_value(above_prof_exc, is_exception=True),
                        format_sql_value(participate_pct),
                        format_sql_value(mean_sgp),
                        format_sql_value(avg_score)
                    ]
                    
                    # Create SQL statements based on level
                    if level == 'State Level':
                        # State level insert
                        stmt = generate_sql_insert_statement(
                            'assessment_state',
                            common_fields,
                            common_values
                        )
                        data_insert_statements.append(stmt)
                        
                    elif level == 'District Level':
                        # Get district ID
                        district_name = row.get('District')
                        district_id = get_district_id(district_name, conn)
                        if district_id is None:
                            # Track missing district
                            if district_name and not pd.isna(district_name):
                                if district_name not in missing_districts:
                                    missing_districts[district_name] = set()
                                missing_districts[district_name].add(year_val)
                            continue
                        
                        # District level insert
                        fields = ['district_id_fk'] + common_fields
                        values = [str(district_id)] + common_values
                        
                        stmt = generate_sql_insert_statement(
                            'assessment_district',
                            fields,
                            values
                        )
                        data_insert_statements.append(stmt)
                        
                    elif level == 'School Level':
                        # Get school name and translated name
                        school_name = row.get('School')
                        if pd.isna(school_name) or not school_name:
                            continue
                            
                        # Get district name for filtering
                        district_name = row.get('District')
                        translated_name = school_name_translations.get(school_name, school_name)
                        
                        # Check if this is a school that needs to be merged with other data
                        if translated_name in merged_schools:
                            # Store data in buffer for merging
                            buffer_key = (translated_name, year_val, subject_id, grade_id, subgroup_id)
                            
                            # Create assessment data object for merged school
                            data = {
                                'original_schools': [school_name],
                                'students_low': students_low or 0,
                                'students_high': students_high or 0,
                                'level1_data': [(level1_pct, level1_exc)] if level1_pct is not None else [],
                                'level2_data': [(level2_pct, level2_exc)] if level2_pct is not None else [],
                                'level3_data': [(level3_pct, level3_exc)] if level3_pct is not None else [],
                                'level4_data': [(level4_pct, level4_exc)] if level4_pct is not None else [],
                                'above_prof_data': [(above_prof_pct, above_prof_exc)] if above_prof_pct is not None else [],
                                'participate_data': [participate_pct] if participate_pct is not None else [],
                                'mean_sgp_data': [mean_sgp] if mean_sgp is not None else [],
                                'avg_score_data': [avg_score] if avg_score is not None else [],
                                'district_name': district_name  # Store district name for later lookup
                            }
                            
                            # Add or merge with existing data in buffer
                            if buffer_key in merged_school_buffer:
                                existing = merged_school_buffer[buffer_key]
                                existing['original_schools'].append(school_name)
                                existing['students_low'] += data['students_low']
                                existing['students_high'] += data['students_high']
                                existing['level1_data'].extend(data['level1_data'])
                                existing['level2_data'].extend(data['level2_data'])
                                existing['level3_data'].extend(data['level3_data'])
                                existing['level4_data'].extend(data['level4_data'])
                                existing['above_prof_data'].extend(data['above_prof_data'])
                                existing['participate_data'].extend(data['participate_data'])
                                existing['mean_sgp_data'].extend(data['mean_sgp_data'])
                                existing['avg_score_data'].extend(data['avg_score_data'])
                                # Keep district name if we don't already have one
                                if not existing.get('district_name') and district_name:
                                    existing['district_name'] = district_name
                            else:
                                merged_school_buffer[buffer_key] = data
                                
                            # We'll process the merged data after reading all the files
                            continue
                            
                        # Standard processing for non-merged schools
                        school_id = get_school_id(school_name, conn, district_name, school_name_translations)
                        if school_id is None:
                            # Track missing school
                            if school_name not in missing_schools:
                                missing_schools[school_name] = {
                                    'years': set(),
                                    'translated': translated_name if translated_name != school_name else None,
                                    'district': district_name
                                }
                            missing_schools[school_name]['years'].add(year_val)
                            continue
                        
                        # School level insert
                        fields = ['school_id_fk'] + common_fields
                        values = [str(school_id)] + common_values
                        
                        stmt = generate_sql_insert_statement(
                            'assessment_school',
                            fields,
                            values
                        )
                        data_insert_statements.append(stmt)
                
                except Exception as e:
                    logger.error(f"Error processing row {idx} in file {file_path}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
    
    # Process merged school data
    from collections import Counter
    merged_processed = 0
    
    for buffer_key, buffer_data in merged_school_buffer.items():
        translated_name, year_val, subject_id, grade_id, subgroup_id = buffer_key
        district_name = buffer_data.get('district_name')
        
        # Get the school ID from the translated name, filtering by district if available
        school_id = get_school_id(translated_name, conn, district_name)
        if school_id is None:
            # Track missing school (should be rare since the translation is from config)
            original_schools = ', '.join(buffer_data['original_schools'])
            district_info = f" in district '{district_name}'" if district_name else ""
            logger.warning(f"Merged school not found: {translated_name}{district_info} (from {original_schools})")
            continue
        
        # Helper function to calculate average and find most common exception
        def calculate_metrics(data_list):
            if not data_list:
                return None, None
                
            values = [d[0] for d in data_list if d[0] is not None]
            if not values:
                return None, None
                
            avg_value = sum(values) / len(values)
            
            # Find most common exception if any
            exceptions = [d[1] for d in data_list if d[1] is not None]
            common_exception = Counter(exceptions).most_common(1)[0][0] if exceptions else None
            
            return avg_value, common_exception
        
        # Calculate averages for all percentage fields
        level1_pct, level1_exc = calculate_metrics(buffer_data['level1_data'])
        level2_pct, level2_exc = calculate_metrics(buffer_data['level2_data'])
        level3_pct, level3_exc = calculate_metrics(buffer_data['level3_data'])
        level4_pct, level4_exc = calculate_metrics(buffer_data['level4_data'])
        above_prof_pct, above_prof_exc = calculate_metrics(buffer_data['above_prof_data'])
        
        # Calculate averages for single-value fields
        def calculate_average(values_list):
            values = [v for v in values_list if v is not None]
            return sum(values) / len(values) if values else None
            
        participate_pct = calculate_average(buffer_data['participate_data'])
        mean_sgp = calculate_average(buffer_data['mean_sgp_data'])
        avg_score = calculate_average(buffer_data['avg_score_data'])
        
        # Format values for SQL
        common_values = [
            str(subject_id),
            str(year_val),
            format_sql_value(grade_id),
            str(subgroup_id),
            format_sql_value(buffer_data['students_low'] if buffer_data['students_low'] > 0 else None),
            format_sql_value(buffer_data['students_high'] if buffer_data['students_high'] > 0 else None),
            format_sql_value(level1_pct),
            format_sql_value(level1_exc, is_exception=True),
            format_sql_value(level2_pct),
            format_sql_value(level2_exc, is_exception=True),
            format_sql_value(level3_pct),
            format_sql_value(level3_exc, is_exception=True),
            format_sql_value(level4_pct),
            format_sql_value(level4_exc, is_exception=True),
            format_sql_value(above_prof_pct),
            format_sql_value(above_prof_exc, is_exception=True),
            format_sql_value(participate_pct),
            format_sql_value(mean_sgp),
            format_sql_value(avg_score)
        ]
        
        # Generate SQL for merged school
        fields = ['school_id_fk'] + common_fields
        values = [str(school_id)] + common_values
        
        stmt = generate_sql_insert_statement(
            'assessment_school',
            fields,
            values
        )
        data_insert_statements.append(stmt)
        merged_processed += 1
    
    if merged_processed > 0:
        logger.info(f"Processed {merged_processed} merged school data points")
    
    # Log missing schools and districts
    if missing_schools:
        missing_schools_list = []
        for school, info in missing_schools.items():
            years_str = ', '.join(str(y) for y in sorted(info['years']))
            if info['translated']:
                missing_schools_list.append(f"{school} (translated to: {info['translated']}): years [{years_str}]")
            else:
                missing_schools_list.append(f"{school}: years [{years_str}]")
        
        missing_schools_log = "\n- ".join(sorted(missing_schools_list))
        logger.error(f"The following schools were not found in the database:\n- {missing_schools_log}")
    
    if missing_districts:
        missing_districts_list = []
        for district, years in missing_districts.items():
            years_str = ', '.join(str(y) for y in sorted(years))
            missing_districts_list.append(f"{district}: years [{years_str}]")
        
        missing_districts_log = "\n- ".join(sorted(missing_districts_list))
        logger.error(f"The following districts were not found in the database:\n- {missing_districts_log}")
    
    # Return statements in correct dependency order - subgroups first, then data
    insert_statements = subgroup_insert_statements + data_insert_statements
    logger.info(f"Generated {len(insert_statements)} insert statements for assessment data, {len(subgroup_insert_statements)} for subgroups")
    
    return insert_statements


def generate_table_creation_statements():
    """Generate SQL statements to create the necessary tables."""
    statements = []
    
    # Create enum for assessment exceptions
    enum_sql = "CREATE TYPE assessment_exception AS ENUM ('TOO_FEW_SAMPLES', 'SCORE_UNDER_10', 'SCORE_OVER_90')"
    statements.append(enum_sql)
    
    # Define common columns for assessment tables
    common_assessment_columns = {
        'assessment_subject_id_fk': 'INTEGER NOT NULL',
        'year': 'INTEGER NOT NULL',
        'grade_id_fk': 'INTEGER',
        'assessment_subgroup_id_fk': 'INTEGER NOT NULL',
        'total_fay_students_low': 'INTEGER',
        'total_fay_students_high': 'INTEGER',
        'level_1_percentage': 'DECIMAL(5,2)',
        'level_1_percentage_exception': 'assessment_exception',
        'level_2_percentage': 'DECIMAL(5,2)',
        'level_2_percentage_exception': 'assessment_exception',
        'level_3_percentage': 'DECIMAL(5,2)',
        'level_3_percentage_exception': 'assessment_exception',
        'level_4_percentage': 'DECIMAL(5,2)',
        'level_4_percentage_exception': 'assessment_exception',
        'above_proficient_percentage': 'DECIMAL(5,2)',
        'above_proficient_percentage_exception': 'assessment_exception',
        'participate_percentage': 'DECIMAL(5,2)',
        'mean_sgp': 'DECIMAL(5,2)',
        'average_score': 'DECIMAL(7,2)',
        'date_created': 'TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP',
        'date_updated': 'TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP'
    }
    
    # Common constraints template for foreign key references
    common_fk_constraints = [
        'CONSTRAINT fk_{table}_subject FOREIGN KEY (assessment_subject_id_fk) REFERENCES assessment_subject(id) ON DELETE CASCADE',
        'CONSTRAINT fk_{table}_grade FOREIGN KEY (grade_id_fk) REFERENCES grades(id) ON DELETE CASCADE',
        'CONSTRAINT fk_{table}_subgroup FOREIGN KEY (assessment_subgroup_id_fk) REFERENCES assessment_subgroup(id) ON DELETE CASCADE'
    ]
    
    # Define table structures
    tables = {
        'assessment_subject': {
            'id': 'SERIAL PRIMARY KEY',
            'name': 'VARCHAR(100) NOT NULL',
            'description': 'VARCHAR(255)',
            'date_created': 'TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP',
            'date_updated': 'TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP'
        },
        'assessment_subgroup': {
            'id': 'SERIAL PRIMARY KEY',
            'name': 'VARCHAR(100) NOT NULL',
            'description': 'VARCHAR(255)',
            'date_created': 'TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP',
            'date_updated': 'TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP'
        },
        'assessment_district': {
            'id': 'SERIAL PRIMARY KEY',
            'district_id_fk': 'INTEGER NOT NULL',
            **common_assessment_columns,
            'constraints': [
                'CONSTRAINT fk_assessment_district_district FOREIGN KEY (district_id_fk) REFERENCES district(id) ON DELETE CASCADE',
                *[c.format(table='assessment_district') for c in common_fk_constraints],
                'CONSTRAINT unique_district_assessment UNIQUE (district_id_fk, assessment_subject_id_fk, year, grade_id_fk, assessment_subgroup_id_fk)'
            ]
        },
        'assessment_school': {
            'id': 'SERIAL PRIMARY KEY',
            'school_id_fk': 'INTEGER NOT NULL',
            **common_assessment_columns,
            'constraints': [
                'CONSTRAINT fk_assessment_school_school FOREIGN KEY (school_id_fk) REFERENCES school(id) ON DELETE CASCADE',
                *[c.format(table='assessment_school') for c in common_fk_constraints],
                'CONSTRAINT unique_school_assessment UNIQUE (school_id_fk, assessment_subject_id_fk, year, grade_id_fk, assessment_subgroup_id_fk)'
            ]
        },
        'assessment_state': {
            'id': 'SERIAL PRIMARY KEY',
            **common_assessment_columns,
            'constraints': [
                *[c.format(table='assessment_state') for c in common_fk_constraints],
                'CONSTRAINT unique_state_assessment UNIQUE (assessment_subject_id_fk, year, grade_id_fk, assessment_subgroup_id_fk)'
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
    
    # Create initial assessment_subject entries
    subject_entries_sql = """
    INSERT INTO assessment_subject (id, name, description) VALUES 
    (1, 'mat', 'Math'),
    (2, 'rea', 'Reading'),
    (3, 'sci', 'Science')
    """
    statements.append(' '.join(line.strip() for line in subject_entries_sql.strip().split('\n')))
    
    # Create triggers for all tables
    tables = [
        'assessment_subject', 
        'assessment_subgroup', 
        'assessment_district', 
        'assessment_school', 
        'assessment_state'
    ]
    
    for table in tables:
        trigger_sql = f"""
        CREATE TRIGGER trigger_update_{table}_timestamp
        BEFORE UPDATE ON {table}
        FOR EACH ROW EXECUTE FUNCTION update_date_updated_column()
        """
        statements.append(' '.join(line.strip() for line in trigger_sql.strip().split('\n')))
    
    # Define index patterns
    index_patterns = {
        'assessment_district': [
            ('district', 'district_id_fk'),
            ('subject', 'assessment_subject_id_fk'),
            ('year', 'year'),
            ('grade', 'grade_id_fk'),
            ('subgroup', 'assessment_subgroup_id_fk')
        ],
        'assessment_school': [
            ('school', 'school_id_fk'),
            ('subject', 'assessment_subject_id_fk'),
            ('year', 'year'),
            ('grade', 'grade_id_fk'),
            ('subgroup', 'assessment_subgroup_id_fk')
        ],
        'assessment_state': [
            ('subject', 'assessment_subject_id_fk'),
            ('year', 'year'),
            ('grade', 'grade_id_fk'),
            ('subgroup', 'assessment_subgroup_id_fk')
        ]
    }
    
    # Create indexes for all foreign keys and commonly queried columns
    indexes = []
    for table, patterns in index_patterns.items():
        for name_suffix, column in patterns:
            indexes.append(f"CREATE INDEX idx_{table}_{name_suffix} ON {table}({column})")
    
    statements.extend(indexes)
    
    return statements


def upgrade():
    """Alembic upgrade function to create tables and import assessment data."""
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
            logger.info("Processing assessment data and generating SQL statements")
            
            # Get database connection for entity lookups
            conn = op.get_bind()
            
            # Generate table creation statements
            sql_statements = generate_table_creation_statements()
            
            # Process assessment data and generate insert statements
            # (These will already be in correct order - subgroups first, then data)
            insert_statements = process_assessment_data(config, current_dir, conn)
            
            # Add insert statements to SQL statements
            sql_statements.extend(insert_statements)
            
            # Save to cache - ensure each statement is a single line
            os.makedirs(cache_dir, exist_ok=True)
            with open(cache_file, 'w') as f:
                f.write(';\n'.join(stmt.strip() for stmt in sql_statements))
            
            logger.info(f"Cached {len(sql_statements)} SQL statements to {cache_file}")
        
        # Execute SQL statements
        executed = 0
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
                break
            
        logger.info(f"Successfully executed {executed} SQL statements")
            
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        raise


def downgrade():
    """Alembic downgrade function to remove assessment tables."""
    try:
        sql_statements = [
            "DROP TABLE IF EXISTS assessment_district CASCADE",
            "DROP TABLE IF EXISTS assessment_school CASCADE",
            "DROP TABLE IF EXISTS assessment_state CASCADE",
            "DROP TABLE IF EXISTS assessment_subgroup CASCADE",
            "DROP TABLE IF EXISTS assessment_subject CASCADE",
            "DROP TYPE IF EXISTS assessment_exception CASCADE"
        ]
        
        for statement in sql_statements:
            op.execute(sa.text(statement))
            
        logger.info("Successfully dropped assessment tables")
    except Exception as e:
        logger.error(f"Error during downgrade: {e}")
        raise