"""Metrics Data Load

Revision ID: 97bda4348f5c
Revises: 2aada939afdc
Create Date: 2024-11-25 12:52:34.621333

"""
from alembic import op
import sqlalchemy as sa
import pandas as pd
import yaml
import re
from datetime import datetime
import os
import logging

# Add this near the top of the file
logger = logging.getLogger('alembic.runtime.migration')


# revision identifiers, used by Alembic.
revision = '97bda4348f5c'
down_revision = '2aada939afdc'
branch_labels = None
depends_on = None


def load_config():
    """Load configuration from YAML file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.abspath(os.path.join(current_dir, '../config/generate_metrics_config.yaml'))
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise Exception(f"Error loading configuration: {e}")

def process_measurement_categories(df, config):
    """Process measurement categories from DataFrame."""
    categories = {}
    category_column = config['column_mappings']['indicator_category']
    
    for category in df[category_column].dropna().unique():
        categories[category] = {
            'name': category,
            'measurement_types': {}
        }
    
    return categories

def process_measurement_types(df, categories, config):
    """Process measurement types and associate them with categories."""
    measurement_types = df[[
        config['column_mappings']['indicator_category'],
        config['column_mappings']['indicator_name']
    ]].dropna(subset=[config['column_mappings']['indicator_name']]).drop_duplicates()
    
    current_category = None
    for _, row in measurement_types.iterrows():
        category = row[config['column_mappings']['indicator_category']]
        indicator = row[config['column_mappings']['indicator_name']]
        
        if pd.notna(category):
            current_category = category
        
        if current_category is None:
            continue
            
        if current_category in categories:
            categories[current_category]['measurement_types'][indicator] = {
                'name': indicator
            }
    
    return categories

def clean_value(value, config):
    """Clean measurement values by removing %,$, etc. and handling special values."""
    if pd.isna(value) or value == "" or value in config['special_values']['null_values']:
        return None
    
    value_str = str(value)
    
    if any(pattern in value_str for pattern in config['special_values']['skip_patterns']):
        return None
    
    if value_str.startswith(">") or value_str.startswith("<"):
        cleaned = re.sub(r'[^0-9.]', '', value_str)
    else:
        cleaned = re.sub(r'[^0-9.-]', '', value_str)
    
    return cleaned if cleaned != "" else None

def process_measurements(df, config):
    """Process measurements and organize by entity."""
    measurements = {}
    current_indicator = None
    current_type = None
    
    for _, row in df.iterrows():
        entity_id = row.get(config['column_mappings']['entity_id'])
        entity_type = row.get(config['column_mappings']['entity_type'])
        indicator = row.get(config['column_mappings']['indicator_name'])
        
        if pd.notna(indicator):
            current_indicator = indicator
        if pd.notna(entity_type):
            current_type = entity_type
        
        if current_indicator is None or pd.isna(entity_id) or current_type is None:
            continue
        
        entity_id = str(entity_id)
        
        if entity_id not in measurements:
            measurements[entity_id] = {
                'id': entity_id,
                'name': row.get(config['column_mappings']['entity_name'], "Unknown"),
                'type': current_type,
                'measurements': []
            }
        
        for year in config['column_mappings']['measurement_years']:
            if year in row and not pd.isna(row[year]):
                value = clean_value(row[year], config)
                if value is not None:
                    measurements[entity_id]['measurements'].append({
                        'indicator': current_indicator,
                        'year': year,
                        'value': value
                    })
    
    return measurements

def generate_sql(categories, measurements, config):
    """Generate SQL INSERT statements for all data."""
    sql_statements = []
    
    # Category inserts
    sql_statements.append("-- Insert measurement type categories")
    for category in categories.values():
        sql_statements.append(
            f"""INSERT INTO measurement_type_category (name) VALUES ('{category['name'].replace("'", "''")}');"""
        )
    
    # Measurement type inserts
    sql_statements.append("\n-- Insert measurement types")
    for category in categories.values():
        sql_statements.append(f"\n-- {category['name']}")
        for mtype in category['measurement_types'].values():
            sql_statements.append(
                f"""INSERT INTO measurement_type (name, measurement_type_category_id_fk) """
                f"""VALUES ('{mtype['name'].replace("'", "''")}', """
                f"""(SELECT id FROM measurement_type_category WHERE name = '{category['name'].replace("'", "''")}'));"""
            )
    
    # Measurement inserts
    sql_statements.append("\n-- Insert measurements")
    for entity in measurements.values():
        sql_statements.append(f"\n-- Measurements for {entity['type']} '{entity['name']}' (ID: {entity['id']})")
        
        for measurement in entity['measurements']:
            entity_type = str(entity['type']).lower()
            
            if entity_type == "school":
                school_id = int(float(entity['id']))
                # Check if school exists using text()
                exists_check = sa.text("""
                    SELECT EXISTS (
                        SELECT 1 FROM school WHERE id = :school_id
                    )
                """)
                result = op.get_bind().execute(exists_check, {"school_id": school_id}).scalar()
                if not result:
                    continue
                
                sql_statements.append(
                    f"""INSERT INTO measurement (school_id_fk, district_id_fk, measurement_type_id_fk, year, field) """
                    f"""VALUES ({school_id}, NULL, """
                    f"""(SELECT id FROM measurement_type WHERE name = '{measurement['indicator'].replace("'", "''")}'), """
                    f"""{measurement['year']}, {measurement['value']});"""
                )
            
            elif entity_type == "district":
                district_id = int(float(entity['id']))
                # Check if district exists using text()
                exists_check = sa.text("""
                    SELECT EXISTS (
                        SELECT 1 FROM district WHERE id = :district_id
                    )
                """)
                result = op.get_bind().execute(exists_check, {"district_id": district_id}).scalar()
                if not result:
                    continue
                
                sql_statements.append(
                    f"""INSERT INTO measurement (school_id_fk, district_id_fk, measurement_type_id_fk, year, field) """
                    f"""VALUES (NULL, {district_id}, """
                    f"""(SELECT id FROM measurement_type WHERE name = '{measurement['indicator'].replace("'", "''")}'), """
                    f"""{measurement['year']}, {measurement['value']});"""
                )
    
    return "\n".join(sql_statements)

def upgrade():
    config = load_config()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # Check for existing cache file first
        cache_dir = os.path.abspath(os.path.join(current_dir, config['file_settings']['sql_cache_dir']))
        cache_file = os.path.join(cache_dir, f'{revision}_cache.sql')
        
        if os.path.exists(cache_file):
            logger.info(f"Found existing SQL cache file at: {cache_file}")
            with open(cache_file, 'r') as f:
                sql_statements = f.read()
            logger.info(f"Executing cached SQL statements ({os.path.getsize(cache_file)} bytes)")
        else:
            # Process all input files
            input_files = [
                'default_input',
                '2021_input',
                '2018_input'
            ]
            
            # Initialize categories and measurements
            categories = {}
            all_measurements = {}
            
            # Process each input file
            for input_key in input_files:
                input_file = config['file_settings'][input_key]
                years = config['file_settings']['file_years'][input_key]
                
                file_path = os.path.abspath(os.path.join(current_dir, input_file))
                logger.info(f"Processing input file at: {file_path} for years {years}")
                
                # Create a temporary config with modified years
                file_config = config.copy()
                file_config['column_mappings'] = config['column_mappings'].copy()
                file_config['column_mappings']['measurement_years'] = years
                
                df = pd.read_excel(file_path)
                
                # Process categories and measurement types only for the first file
                if not categories:
                    categories = process_measurement_categories(df, file_config)
                    categories = process_measurement_types(df, categories, file_config)
                
                # Process measurements for each file
                file_measurements = process_measurements(df, file_config)
                
                # Merge measurements
                for entity_id, entity_data in file_measurements.items():
                    if entity_id not in all_measurements:
                        all_measurements[entity_id] = entity_data
                    else:
                        all_measurements[entity_id]['measurements'].extend(entity_data['measurements'])
            
            # Generate SQL with combined data
            sql_statements = generate_sql(categories, all_measurements, config)
            
            # Save to cache
            os.makedirs(cache_dir, exist_ok=True)
            logger.info(f"Creating new SQL cache file at: {cache_file}")
            with open(cache_file, 'w') as f:
                f.write(sql_statements)
            logger.info(f"Successfully created SQL cache file ({os.path.getsize(cache_file)} bytes)")
        
        # Execute SQL statements
        op.execute(sql_statements)
        
    except Exception as e:
        raise Exception(f"Error during migration: {e}")

def downgrade():
   pass
