"""Load Measurement State Targets

Revision ID: 65ab32afd32c
Revises: 21ea12af9faf
Create Date: 2024-04-02 01:33:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
import pandas as pd
import logging
import os
import yaml
from datetime import datetime

# Add this near the top of the file
logger = logging.getLogger('alembic.runtime.migration')

# revision identifiers, used by Alembic.
revision = '65ab32afd32c'
down_revision = '21ea12af9faf'
branch_labels = None
depends_on = None

def load_config():
    """Load configuration from YAML file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.abspath(os.path.join(current_dir, '../config/state_targets_config.yaml'))
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise Exception(f"Error loading configuration: {e}")

def load_state_targets(config):
    """Load state targets data from CSV file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.abspath(os.path.join(
        current_dir, 
        config['file_settings']['state_targets_file']['path']
    ))
    
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Successfully loaded state targets data from {file_path}")
        return df
    except Exception as e:
        logger.error(f"Error loading state targets data: {e}")
        raise

def upgrade():
    """Insert measurement state targets."""
    conn = op.get_bind()
    
    # Log start of upgrade
    logger.info("Starting to add measurement state targets")
    
    # Load configuration and state targets data
    config = load_config()
    targets_df = load_state_targets(config)
    
    # For each row in the dataframe
    for _, row in targets_df.iterrows():
        measurement_type_name = row['measurement_type_name']
        year = row['year']
        target_value = row['target_value']
        
        # Check if the measurement type exists
        measurement_type_check = sa.text("""
            SELECT id FROM measurement_type WHERE name = :name
        """)
        
        measurement_type_id = conn.execute(
            measurement_type_check, 
            {"name": measurement_type_name}
        ).scalar()
        
        if not measurement_type_id:
            logger.warning(f"Measurement type '{measurement_type_name}' not found. Skipping.")
            continue
            
        # Check if this target already exists to avoid duplicates
        existing_check = sa.text("""
            SELECT EXISTS (
                SELECT 1 FROM measurement_state_target 
                WHERE measurement_type_id_fk = :type_id AND year = :year
            )
        """)
        
        exists = conn.execute(
            existing_check, 
            {"type_id": measurement_type_id, "year": year}
        ).scalar()
        
        if exists:
            logger.info(f"Target for '{measurement_type_name}' in {year} already exists. Skipping.")
            continue
            
        # Insert the new state target
        insert_stmt = sa.text("""
            INSERT INTO measurement_state_target 
            (measurement_type_id_fk, year, field) 
            VALUES (:type_id, :year, :value)
        """)
        
        conn.execute(
            insert_stmt, 
            {"type_id": measurement_type_id, "year": year, "value": target_value}
        )
        
        logger.info(f"Added state target for '{measurement_type_name}' in {year}: {target_value}")
    
    logger.info("Completed adding measurement state targets")

def downgrade():
    """Remove all measurement state targets inserted by this migration."""
    conn = op.get_bind()
    
    logger.info("Removing measurement state targets")
    
    # Load configuration and state targets data
    config = load_config()
    targets_df = load_state_targets(config)
    
    # For each row in the dataframe
    for _, row in targets_df.iterrows():
        measurement_type_name = row['measurement_type_name']
        year = row['year']
        
        # Find the measurement type ID
        measurement_type_check = sa.text("""
            SELECT id FROM measurement_type WHERE name = :name
        """)
        
        measurement_type_id = conn.execute(
            measurement_type_check, 
            {"name": measurement_type_name}
        ).scalar()
        
        if not measurement_type_id:
            logger.warning(f"Measurement type '{measurement_type_name}' not found. Skipping.")
            continue
            
        # Delete the target
        delete_stmt = sa.text("""
            DELETE FROM measurement_state_target 
            WHERE measurement_type_id_fk = :type_id AND year = :year
        """)
        
        result = conn.execute(
            delete_stmt, 
            {"type_id": measurement_type_id, "year": year}
        )
        
        logger.info(f"Removed {result.rowcount} state target(s) for '{measurement_type_name}' in {year}")
    
    logger.info("Completed removing measurement state targets")
