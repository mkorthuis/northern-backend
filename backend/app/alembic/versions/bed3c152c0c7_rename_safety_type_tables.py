"""Rename Safety Type Tables

Revision ID: bed3c152c0c7
Revises: aed3c152c0c6
Create Date: 2024-06-05 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
import logging

# Configure logger
logger = logging.getLogger('alembic.runtime.migration')

# revision identifiers, used by Alembic.
revision = 'bed3c152c0c7'
down_revision = 'aed3c152c0c6'
branch_labels = None
depends_on = None


def upgrade():
    """Rename safety type tables to use 'safety_' prefix instead of 'school_' and update related index names and constraints."""
    logger.info("Starting Safety Type Tables Rename migration upgrade")

    # Step 1: Update foreign key constraints on school tables
    logger.info("Updating foreign key constraints for school tables")
    fk_constraint_renames = [
        # school_safety table constraints
        ('school_safety', 'fk_school_safety_type', 'fk_school_safety_safety_type'),
        
        # school_discipline_incident table constraints
        ('school_discipline_incident', 'fk_school_discipline_incident_type', 'fk_school_discipline_incident_safety_type'),
        
        # school_discipline_count table constraints
        ('school_discipline_count', 'fk_school_discipline_count_type', 'fk_school_discipline_count_safety_type'),
        
        # school_bullying table constraints
        ('school_bullying', 'fk_school_bullying_type', 'fk_school_bullying_safety_type'),
        
        # school_bullying_classification table constraints
        ('school_bullying_classification', 'fk_school_bullying_classification_type', 'fk_school_bullying_classification_safety_type'),
        
        # school_bullying_impact table constraints
        ('school_bullying_impact', 'fk_school_bullying_impact_type', 'fk_school_bullying_impact_safety_type'),
        
        # school_harassment table constraints
        ('school_harassment', 'fk_school_harassment_classification', 'fk_school_harassment_safety_classification')
    ]

    for table, old_constraint, new_constraint in fk_constraint_renames:
        logger.info(f"Renaming constraint {old_constraint} to {new_constraint} on table {table}")
        op.execute(f"ALTER TABLE {table} RENAME CONSTRAINT {old_constraint} TO {new_constraint}")

    # Step 2: Update foreign key constraints on state tables
    logger.info("Updating foreign key constraints for state tables")
    state_fk_constraint_renames = [
        # state_safety table constraints
        ('state_safety', 'fk_state_safety_type', 'fk_state_safety_safety_type'),
        
        # state_discipline_incident table constraints
        ('state_discipline_incident', 'fk_state_discipline_incident_type', 'fk_state_discipline_incident_safety_type'),
        
        # state_discipline_count table constraints
        ('state_discipline_count', 'fk_state_discipline_count_type', 'fk_state_discipline_count_safety_type'),
        
        # state_bullying table constraints
        ('state_bullying', 'fk_state_bullying_type', 'fk_state_bullying_safety_type'),
        
        # state_bullying_classification table constraints
        ('state_bullying_classification', 'fk_state_bullying_classification_type', 'fk_state_bullying_classification_safety_type'),
        
        # state_bullying_impact table constraints
        ('state_bullying_impact', 'fk_state_bullying_impact_type', 'fk_state_bullying_impact_safety_type'),
        
        # state_harassment table constraints
        ('state_harassment', 'fk_state_harassment_classification', 'fk_state_harassment_safety_classification')
    ]

    for table, old_constraint, new_constraint in state_fk_constraint_renames:
        logger.info(f"Renaming constraint {old_constraint} to {new_constraint} on table {table}")
        op.execute(f"ALTER TABLE {table} RENAME CONSTRAINT {old_constraint} TO {new_constraint}")

    # Step 3: Update foreign key constraints on district tables
    logger.info("Updating foreign key constraints for district tables")
    district_fk_constraint_renames = [
        # district_safety table constraints
        ('district_safety', 'fk_district_safety_type', 'fk_district_safety_safety_type'),
        
        # district_discipline_incident table constraints
        ('district_discipline_incident', 'fk_district_discipline_incident_type', 'fk_district_discipline_incident_safety_type'),
        
        # district_discipline_count table constraints
        ('district_discipline_count', 'fk_district_discipline_count_type', 'fk_district_discipline_count_safety_type'),
        
        # district_bullying table constraints
        ('district_bullying', 'fk_district_bullying_type', 'fk_district_bullying_safety_type'),
        
        # district_bullying_classification table constraints
        ('district_bullying_classification', 'fk_district_bullying_classification_type', 'fk_district_bullying_classification_safety_type'),
        
        # district_bullying_impact table constraints
        ('district_bullying_impact', 'fk_district_bullying_impact_type', 'fk_district_bullying_impact_safety_type'),
        
        # district_harassment table constraints
        ('district_harassment', 'fk_district_harassment_classification', 'fk_district_harassment_safety_classification')
    ]

    for table, old_constraint, new_constraint in district_fk_constraint_renames:
        logger.info(f"Renaming constraint {old_constraint} to {new_constraint} on table {table}")
        op.execute(f"ALTER TABLE {table} RENAME CONSTRAINT {old_constraint} TO {new_constraint}")

    # Step 4: Update index names on school tables
    logger.info("Updating index names for school tables")
    index_renames = [
        # school_safety table indexes
        ('idx_school_safety_type', 'idx_school_safety_safety_type'),
        
        # school_discipline_incident table indexes
        ('idx_school_discipline_incident_type', 'idx_school_discipline_incident_safety_type'),
        
        # school_discipline_count table indexes
        ('idx_school_discipline_count_type', 'idx_school_discipline_count_safety_type'),
        
        # school_bullying table indexes
        ('idx_school_bullying_type', 'idx_school_bullying_safety_type'),
        
        # school_bullying_classification table indexes
        ('idx_school_bullying_classification_type', 'idx_school_bullying_classification_safety_type'),
        
        # school_bullying_impact table indexes
        ('idx_school_bullying_impact_type', 'idx_school_bullying_impact_safety_type'),
        
        # school_harassment table indexes
        ('idx_school_harassment_classification', 'idx_school_harassment_safety_classification')
    ]

    for old_index, new_index in index_renames:
        logger.info(f"Renaming index {old_index} to {new_index}")
        op.execute(f"ALTER INDEX {old_index} RENAME TO {new_index}")

    # Step 5: Update index names on state tables 
    logger.info("Updating index names for state tables")
    state_index_renames = [
        # state_safety table indexes
        ('idx_state_safety_type', 'idx_state_safety_safety_type'),
        
        # state_discipline_incident table indexes
        ('idx_state_discipline_incident_type', 'idx_state_discipline_incident_safety_type'),
        
        # state_discipline_count table indexes
        ('idx_state_discipline_count_type', 'idx_state_discipline_count_safety_type'),
        
        # state_bullying table indexes
        ('idx_state_bullying_type', 'idx_state_bullying_safety_type'),
        
        # state_bullying_classification table indexes
        ('idx_state_bullying_classification_type', 'idx_state_bullying_classification_safety_type'),
        
        # state_bullying_impact table indexes
        ('idx_state_bullying_impact_type', 'idx_state_bullying_impact_safety_type'),
        
        # state_harassment table indexes
        ('idx_state_harassment_classification', 'idx_state_harassment_safety_classification')
    ]

    for old_index, new_index in state_index_renames:
        logger.info(f"Renaming index {old_index} to {new_index}")
        op.execute(f"ALTER INDEX {old_index} RENAME TO {new_index}")

    # Step 6: Update index names on district tables
    logger.info("Updating index names for district tables")
    district_index_renames = [
        # district_safety table indexes
        ('idx_district_safety_type', 'idx_district_safety_safety_type'),
        
        # district_discipline_incident table indexes
        ('idx_district_discipline_incident_type', 'idx_district_discipline_incident_safety_type'),
        
        # district_discipline_count table indexes
        ('idx_district_discipline_count_type', 'idx_district_discipline_count_safety_type'),
        
        # district_bullying table indexes
        ('idx_district_bullying_type', 'idx_district_bullying_safety_type'),
        
        # district_bullying_classification table indexes
        ('idx_district_bullying_classification_type', 'idx_district_bullying_classification_safety_type'),
        
        # district_bullying_impact table indexes
        ('idx_district_bullying_impact_type', 'idx_district_bullying_impact_safety_type'),
        
        # district_harassment table indexes
        ('idx_district_harassment_classification', 'idx_district_harassment_safety_classification')
    ]

    for old_index, new_index in district_index_renames:
        logger.info(f"Renaming index {old_index} to {new_index}")
        op.execute(f"ALTER INDEX {old_index} RENAME TO {new_index}")

    # Step 7: Rename tables
    logger.info("Renaming tables")
    table_renames = [
        ('school_safety_type', 'safety_safety_type'),
        ('school_discipline_incident_type', 'safety_discipline_incident_type'),
        ('school_discipline_count_type', 'safety_discipline_count_type'),
        ('school_bullying_type', 'safety_bullying_type'),
        ('school_bullying_classification_type', 'safety_bullying_classification_type'),
        ('school_bullying_impact_type', 'safety_bullying_impact_type'),
        ('school_harassment_classification', 'safety_harassment_classification')
    ]

    for old_name, new_name in table_renames:
        logger.info(f"Renaming table {old_name} to {new_name}")
        op.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")

    logger.info("Safety Type Tables Rename migration upgrade completed successfully")


def downgrade():
    """Revert safety type table names back to using 'school_' prefix and restore original index names and constraints."""
    logger.info("Starting Safety Type Tables Rename migration downgrade")

    # Step 1: Rename tables back to original names
    logger.info("Renaming tables back to original names")
    table_renames = [
        ('safety_harassment_classification', 'school_harassment_classification'),
        ('safety_bullying_impact_type', 'school_bullying_impact_type'),
        ('safety_bullying_classification_type', 'school_bullying_classification_type'),
        ('safety_bullying_type', 'school_bullying_type'),
        ('safety_discipline_count_type', 'school_discipline_count_type'),
        ('safety_discipline_incident_type', 'school_discipline_incident_type'),
        ('safety_safety_type', 'school_safety_type')
    ]

    for new_name, old_name in table_renames:
        logger.info(f"Renaming table {new_name} back to {old_name}")
        op.execute(f"ALTER TABLE {new_name} RENAME TO {old_name}")

    # Step 2: Revert index names on district tables
    logger.info("Reverting index names for district tables")
    district_index_renames = [
        # district_harassment table indexes
        ('idx_district_harassment_safety_classification', 'idx_district_harassment_classification'),
        
        # district_bullying_impact table indexes
        ('idx_district_bullying_impact_safety_type', 'idx_district_bullying_impact_type'),
        
        # district_bullying_classification table indexes
        ('idx_district_bullying_classification_safety_type', 'idx_district_bullying_classification_type'),
        
        # district_bullying table indexes
        ('idx_district_bullying_safety_type', 'idx_district_bullying_type'),
        
        # district_discipline_count table indexes
        ('idx_district_discipline_count_safety_type', 'idx_district_discipline_count_type'),
        
        # district_discipline_incident table indexes
        ('idx_district_discipline_incident_safety_type', 'idx_district_discipline_incident_type'),
        
        # district_safety table indexes
        ('idx_district_safety_safety_type', 'idx_district_safety_type')
    ]

    for new_index, old_index in district_index_renames:
        logger.info(f"Renaming index {new_index} back to {old_index}")
        op.execute(f"ALTER INDEX {new_index} RENAME TO {old_index}")

    # Step 3: Revert index names on state tables
    logger.info("Reverting index names for state tables")
    state_index_renames = [
        # state_harassment table indexes
        ('idx_state_harassment_safety_classification', 'idx_state_harassment_classification'),
        
        # state_bullying_impact table indexes
        ('idx_state_bullying_impact_safety_type', 'idx_state_bullying_impact_type'),
        
        # state_bullying_classification table indexes
        ('idx_state_bullying_classification_safety_type', 'idx_state_bullying_classification_type'),
        
        # state_bullying table indexes
        ('idx_state_bullying_safety_type', 'idx_state_bullying_type'),
        
        # state_discipline_count table indexes
        ('idx_state_discipline_count_safety_type', 'idx_state_discipline_count_type'),
        
        # state_discipline_incident table indexes
        ('idx_state_discipline_incident_safety_type', 'idx_state_discipline_incident_type'),
        
        # state_safety table indexes
        ('idx_state_safety_safety_type', 'idx_state_safety_type')
    ]

    for new_index, old_index in state_index_renames:
        logger.info(f"Renaming index {new_index} back to {old_index}")
        op.execute(f"ALTER INDEX {new_index} RENAME TO {old_index}")

    # Step 4: Revert index names on school tables
    logger.info("Reverting index names for school tables")
    index_renames = [
        # school_harassment table indexes
        ('idx_school_harassment_safety_classification', 'idx_school_harassment_classification'),
        
        # school_bullying_impact table indexes
        ('idx_school_bullying_impact_safety_type', 'idx_school_bullying_impact_type'),
        
        # school_bullying_classification table indexes
        ('idx_school_bullying_classification_safety_type', 'idx_school_bullying_classification_type'),
        
        # school_bullying table indexes
        ('idx_school_bullying_safety_type', 'idx_school_bullying_type'),
        
        # school_discipline_count table indexes
        ('idx_school_discipline_count_safety_type', 'idx_school_discipline_count_type'),
        
        # school_discipline_incident table indexes
        ('idx_school_discipline_incident_safety_type', 'idx_school_discipline_incident_type'),
        
        # school_safety table indexes
        ('idx_school_safety_safety_type', 'idx_school_safety_type')
    ]

    for new_index, old_index in index_renames:
        logger.info(f"Renaming index {new_index} back to {old_index}")
        op.execute(f"ALTER INDEX {new_index} RENAME TO {old_index}")

    # Step 5: Revert foreign key constraints on district tables
    logger.info("Reverting foreign key constraints for district tables")
    district_fk_constraint_renames = [
        # district_harassment table constraints
        ('district_harassment', 'fk_district_harassment_safety_classification', 'fk_district_harassment_classification'),
        
        # district_bullying_impact table constraints
        ('district_bullying_impact', 'fk_district_bullying_impact_safety_type', 'fk_district_bullying_impact_type'),
        
        # district_bullying_classification table constraints
        ('district_bullying_classification', 'fk_district_bullying_classification_safety_type', 'fk_district_bullying_classification_type'),
        
        # district_bullying table constraints
        ('district_bullying', 'fk_district_bullying_safety_type', 'fk_district_bullying_type'),
        
        # district_discipline_count table constraints
        ('district_discipline_count', 'fk_district_discipline_count_safety_type', 'fk_district_discipline_count_type'),
        
        # district_discipline_incident table constraints
        ('district_discipline_incident', 'fk_district_discipline_incident_safety_type', 'fk_district_discipline_incident_type'),
        
        # district_safety table constraints
        ('district_safety', 'fk_district_safety_safety_type', 'fk_district_safety_type')
    ]

    for table, new_constraint, old_constraint in district_fk_constraint_renames:
        logger.info(f"Renaming constraint {new_constraint} back to {old_constraint} on table {table}")
        op.execute(f"ALTER TABLE {table} RENAME CONSTRAINT {new_constraint} TO {old_constraint}")

    # Step 6: Revert foreign key constraints on state tables
    logger.info("Reverting foreign key constraints for state tables")
    state_fk_constraint_renames = [
        # state_harassment table constraints
        ('state_harassment', 'fk_state_harassment_safety_classification', 'fk_state_harassment_classification'),
        
        # state_bullying_impact table constraints
        ('state_bullying_impact', 'fk_state_bullying_impact_safety_type', 'fk_state_bullying_impact_type'),
        
        # state_bullying_classification table constraints
        ('state_bullying_classification', 'fk_state_bullying_classification_safety_type', 'fk_state_bullying_classification_type'),
        
        # state_bullying table constraints
        ('state_bullying', 'fk_state_bullying_safety_type', 'fk_state_bullying_type'),
        
        # state_discipline_count table constraints
        ('state_discipline_count', 'fk_state_discipline_count_safety_type', 'fk_state_discipline_count_type'),
        
        # state_discipline_incident table constraints
        ('state_discipline_incident', 'fk_state_discipline_incident_safety_type', 'fk_state_discipline_incident_type'),
        
        # state_safety table constraints
        ('state_safety', 'fk_state_safety_safety_type', 'fk_state_safety_type')
    ]

    for table, new_constraint, old_constraint in state_fk_constraint_renames:
        logger.info(f"Renaming constraint {new_constraint} back to {old_constraint} on table {table}")
        op.execute(f"ALTER TABLE {table} RENAME CONSTRAINT {new_constraint} TO {old_constraint}")

    # Step 7: Revert foreign key constraints on school tables
    logger.info("Reverting foreign key constraints for school tables")
    fk_constraint_renames = [
        # school_harassment table constraints
        ('school_harassment', 'fk_school_harassment_safety_classification', 'fk_school_harassment_classification'),
        
        # school_bullying_impact table constraints
        ('school_bullying_impact', 'fk_school_bullying_impact_safety_type', 'fk_school_bullying_impact_type'),
        
        # school_bullying_classification table constraints
        ('school_bullying_classification', 'fk_school_bullying_classification_safety_type', 'fk_school_bullying_classification_type'),
        
        # school_bullying table constraints
        ('school_bullying', 'fk_school_bullying_safety_type', 'fk_school_bullying_type'),
        
        # school_discipline_count table constraints
        ('school_discipline_count', 'fk_school_discipline_count_safety_type', 'fk_school_discipline_count_type'),
        
        # school_discipline_incident table constraints
        ('school_discipline_incident', 'fk_school_discipline_incident_safety_type', 'fk_school_discipline_incident_type'),
        
        # school_safety table constraints
        ('school_safety', 'fk_school_safety_safety_type', 'fk_school_safety_type')
    ]

    for table, new_constraint, old_constraint in fk_constraint_renames:
        logger.info(f"Renaming constraint {new_constraint} back to {old_constraint} on table {table}")
        op.execute(f"ALTER TABLE {table} RENAME CONSTRAINT {new_constraint} TO {old_constraint}")

    logger.info("Safety Type Tables Rename migration downgrade completed successfully") 