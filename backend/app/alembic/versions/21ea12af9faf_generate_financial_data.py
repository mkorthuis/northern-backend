"""generate financial data

Revision ID: 21ea12af9faf
Revises: ad0f7f2e3016
Create Date: 2025-03-24 21:19:19.037357

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql
import pandas as pd
import yaml
import os
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import warnings
import traceback

warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

# Add this near the top of the file
logger = logging.getLogger('alembic.runtime.migration')

# revision identifiers, used by Alembic.
revision = '21ea12af9faf'
down_revision = 'ad0f7f2e3016'
branch_labels = None
depends_on = None

@dataclass
class BalanceSheetEntry:
    entry_type_id: int
    fund_type_id: int
    value: float

@dataclass
class RevenueEntry:
    entry_type_id: int
    fund_type_id: int
    value: float

@dataclass
class ExpenditureEntry:
    entry_type_id: int
    fund_type_id: int
    value: float

@dataclass
class DOEFormData:
    district_id: int
    year: int
    balance_entries: List[BalanceSheetEntry]
    revenue_entries: List[RevenueEntry]
    expenditure_entries: List[ExpenditureEntry]
    
    def generate_sql_statements(self) -> List[str]:
        """Generate SQL statements for this DOE form and all its entries."""
        statements = []
        
        # Insert DOE form
        statements.append(f"""INSERT INTO doe_form (district_id_fk, year) VALUES ({self.district_id}, {self.year});""")
        
        # Generate balance sheet entries
        for entry in self.balance_entries:
            statements.append(f"""INSERT INTO balance_sheet (doe_form_id_fk, balance_entry_type_id_fk, balance_fund_type_id_fk, value) VALUES ((SELECT id FROM doe_form WHERE district_id_fk = {self.district_id} AND year = {self.year} ORDER BY id DESC LIMIT 1), {entry.entry_type_id}, {entry.fund_type_id}, {entry.value});""")
            
        # Generate revenue entries
        for entry in self.revenue_entries:
            statements.append(f"""INSERT INTO revenue (doe_form_id_fk, revenue_entry_type_id_fk, revenue_fund_type_id_fk, value) VALUES ((SELECT id FROM doe_form WHERE district_id_fk = {self.district_id} AND year = {self.year} ORDER BY id DESC LIMIT 1), {entry.entry_type_id}, {entry.fund_type_id}, {entry.value});""")
            
        # Generate expenditure entries
        for entry in self.expenditure_entries:
            statements.append(f"""INSERT INTO expenditure (doe_form_id_fk, expenditure_entry_type_id_fk, expenditure_fund_type_id_fk, value) VALUES ((SELECT id FROM doe_form WHERE district_id_fk = {self.district_id} AND year = {self.year} ORDER BY id DESC LIMIT 1), {entry.entry_type_id}, {entry.fund_type_id}, {entry.value});""")
            
        return statements

def load_config():
    """Load configuration from YAML file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.abspath(os.path.join(current_dir, '../config/generate_finance_config.yaml'))
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise Exception(f"Error loading configuration: {e}")

def parse_doe_form(file_path: str, year: int, config: dict, config_district_id: int) -> Optional[DOEFormData]:
    """Parse a DOE-25 form and return structured data."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        full_path = os.path.abspath(os.path.join(current_dir, file_path))
        if not os.path.exists(full_path):
            logger.warning(f"File does not exist: {full_path}")
            return None
            
        if os.path.getsize(full_path) == 0:
            logger.warning(f"File is empty: {full_path}")
            return None

        # Try different Excel engines
        for engine in ['openpyxl', 'xlrd']:
            try:
                df = pd.read_excel(full_path, sheet_name=config['file_settings']['sheet_name'], engine=engine)
                break
            except Exception as e:
                continue
        else:
            logger.error(f"Failed to read Excel file: {full_path}")
            return None

        def process_entry_row(df: pd.DataFrame, 
                            entry_data: tuple, 
                            fund_types: List[Tuple], 
                            entry_type: str, 
                            year: int) -> List[Tuple[int, int, float]]:
            """Process a single row from the DOE form."""
            entries = []
            
            # Check year restrictions
            if len(entry_data) > 7 and year not in entry_data[7]:
                return entries
            
            entry_id, entry_name, page, line, account_no, category_id, excel_column = entry_data[:7]
            
            # Convert to strings for comparison
            page_str = str(page)
            line_str = str(line)
            account_str = str(account_no) if account_no else 'nan'
            
            # Find matching row
            row = df[
                (df.iloc[:, 0].astype(str).str.strip() == excel_column.strip()) &
                (df.iloc[:, 1].astype(str).str.strip() == page_str) &
                (df.iloc[:, 2].astype(str).str.strip() == line_str) &
                (df.iloc[:, 4].astype(str).str.strip() == account_str)
            ]
            
            if row.empty:
                logger.warning(f"Could not find {entry_type} entry '{excel_column}' (page {page_str}, line {line_str})")
                return entries
            
            # Process each fund type
            for fund_id, fund_state_id, state_name, column_letter in fund_types:
                column_index = ord(column_letter) - ord('A')
                value = row.iloc[0, column_index]
                
                if pd.notna(value):
                    try:
                        float_value = float(str(value).replace(',', ''))
                        if float_value != 0:
                            # Round to 2 decimal places if this is an expenditure entry
                            if entry_type == 'expenditure':
                                float_value = round(float_value, 2)
                            entries.append((entry_id, fund_id, float_value))
                    except (ValueError, TypeError):
                        continue
            
            return entries

        def process_entries(entry_types: list, fund_types: list, entry_type: str, entry_class, year: int) -> List:
            """Process all entries of a specific type and return list of entry objects."""
            entries = []
            for entry_type_data in entry_types:
                raw_entries = process_entry_row(df, entry_type_data, fund_types, entry_type, year)
                entries.extend([entry_class(entry_type_id=e[0], fund_type_id=e[1], value=e[2]) 
                              for e in raw_entries])
            return entries

        # Add robust district ID validation
        try:
            raw_district_id = df.iloc[0, 1]
            if pd.isna(raw_district_id):
                logger.warning(f"District ID is missing (NaN) in Excel file: {file_path}")
                logger.warning(f"Using config district ID: {config_district_id}")
                district_id = config_district_id
            else:
                district_id = int(raw_district_id)
                if district_id != config_district_id:
                    logger.warning(f"District ID mismatch for {file_path}:")
                    logger.warning(f"  Config ID: {config_district_id}")
                    logger.warning(f"  Excel ID: {district_id}")
                    return None
                
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid district ID format in Excel file: {file_path}")
            logger.error(f"Expected a number, got: {df.iloc[0, 1]}")
            return None

        # Process all entry types
        balance_entries = process_entries(
            config['initial_data']['balance_entry_type'],
            config['initial_data']['balance_fund_type'],
            'balance sheet',
            BalanceSheetEntry,
            year
        )

        revenue_entries = process_entries(
            config['revenue_data']['revenue_entry_type'],
            config['revenue_data']['revenue_fund_type'],
            'revenue',
            RevenueEntry,
            year
        )

        expenditure_entries = process_entries(
            config['expenditure_data']['expenditure_entry_type'],
            config['expenditure_data']['expenditure_fund_type'],
            'expenditure',
            ExpenditureEntry,
            year
        )

        return DOEFormData(
            district_id=district_id,
            year=year,
            balance_entries=balance_entries,
            revenue_entries=revenue_entries,
            expenditure_entries=expenditure_entries
        )
        
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        logger.error("Full stack trace:")
        logger.error(traceback.format_exc())
        return None

def generate_initial_data_inserts(config):
    """Generate SQL INSERT statements for all initial data configurations."""
    sql_statements = []
    
    # Balance Sheet Related Inserts
    for id, name in config['initial_data']['balance_entry_super_category_type']:
        sql_statements.append(
            f"INSERT INTO balance_entry_super_category_type (id, name) VALUES ({id}, '{name}');"
        )
        
    # Balance Entry Category Type
    for id, name, super_category_id in config['initial_data']['balance_entry_category_type']:
        sql_statements.append(
            f"INSERT INTO balance_entry_category_type (id, name, balance_entry_super_category_type_id_fk) VALUES ({id}, '{name}', {super_category_id});"
        )
    
    # Balance Entry Type
    for entry in config['initial_data']['balance_entry_type']:
        id, name, page, line, account_no, category_id, excel_column = entry[:7]
        # Escape single quotes in name
        name = name.replace("'", "''")
        sql_statements.append(
            f"INSERT INTO balance_entry_type (id, name, page, line, account_no, balance_entry_category_type_id_fk) VALUES ({id}, '{name}', '{page}', '{line}', '{account_no}', {category_id});"
        )
    
    # Balance Fund Type
    for id, state_id, state_name, column_letter in config['initial_data']['balance_fund_type']:
        sql_statements.append(
            f"INSERT INTO balance_fund_type (id, state_id, state_name) VALUES ({id}, '{state_id}', '{state_name}');"
        )
    
    # Revenue Related Inserts
    for id, name in config['revenue_data']['revenue_super_category_type']:
        sql_statements.append(
            f"INSERT INTO revenue_entry_super_category_type (id, name) VALUES ({id}, '{name}');"
        )
    
    # Revenue Category Type
    for id, name, super_category_id in config['revenue_data']['revenue_category_type']:
        sql_statements.append(
            f"INSERT INTO revenue_entry_category_type (id, name, revenue_entry_super_category_type_id_fk) VALUES ({id}, '{name}', {super_category_id});"
        )
    
    # Revenue Entry Type
    for entry in config['revenue_data']['revenue_entry_type']:
        id, name, page, line, account_no, category_id, excel_column = entry[:7]
        # Escape single quotes in name
        name = name.replace("'", "''")
        sql_statements.append(
            f"INSERT INTO revenue_entry_type (id, name, page, line, account_no, revenue_entry_category_type_id_fk) VALUES ({id}, '{name}', '{page}', '{line}', '{account_no}', {category_id});"
        )
    
    # Revenue Fund Type
    for id, state_id, state_name, column_letter in config['revenue_data']['revenue_fund_type']:
        sql_statements.append(
            f"INSERT INTO revenue_fund_type (id, state_id, state_name) VALUES ({id}, '{state_id}', '{state_name}');"
        )
    
    # Expenditure Related Inserts
    for id, name in config['expenditure_data']['expenditure_super_category_type']:
        sql_statements.append(
            f"INSERT INTO expenditure_entry_super_category_type (id, name) VALUES ({id}, '{name}');"
        )
    
    # Expenditure Category Type
    for id, name, super_category_id in config['expenditure_data']['expenditure_category_type']:
        sql_statements.append(
            f"INSERT INTO expenditure_entry_category_type (id, name, expenditure_entry_super_category_type_id_fk) VALUES ({id}, '{name}', {super_category_id});"
        )

    # Expenditure Entry Type
    for entry in config['expenditure_data']['expenditure_entry_type']:
        id, name, page, line, account_no, category_id, excel_column = entry[:7]
        # Escape single quotes in name
        name = name.replace("'", "''")
        sql_statements.append(
            f"INSERT INTO expenditure_entry_type (id, name, page, line, account_no, expenditure_entry_category_type_id_fk) VALUES ({id}, '{name}', '{page}', '{line}', '{account_no}', {category_id});"
        )
    
    # Expenditure Fund Type
    for id, state_id, state_name, column_letter in config['expenditure_data']['expenditure_fund_type']:
        sql_statements.append(
            f"INSERT INTO expenditure_fund_type (id, state_id, state_name) VALUES ({id}, '{state_id}', '{state_name}');"
        )
    
    return sql_statements

def get_district_ids():
    """Query the database to get all district IDs."""
    connection = op.get_bind()
    result = connection.execute(
        sa.text("""
            SELECT id, name 
            FROM district 
            ORDER BY id;
        """)
    )
    return [(row.name, row.id) for row in result]

def upgrade():
    """Execute the upgrade migration."""
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
            # Generate initial data inserts
            sql_statements = generate_initial_data_inserts(config)
            
            # Get districts from database instead of config
            districts = get_district_ids()
            if not districts:
                logger.warning("No districts found in database")
                return
                
            # Process DOE forms for each district and year
            year_start = config['file_settings']['year_start']
            year_end = config['file_settings']['year_end']
            
            for year in range(year_start, year_end + 1):
                logger.info(f"Processing year {year}...")
                for district_name, district_id in districts:
                    logger.info(f"Processing district {district_name} (ID: {district_id})...")
                    
                    # Clean district name for file path
                    district_name_cleaned = (district_name.lower()
                                          .replace(' school district', '')
                                          .replace(' (carroll county)', '')
                                          .replace('oyster river cooperative', 'oyster river coop')
                                          .replace("'", '')
                                          .strip()
                                          .replace(' ', '-'))
                    
                    file_path = f"../assets/finance/{year}/{district_name_cleaned}-doe-25-{year}.xlsx"
                    
                    doe_form_data = parse_doe_form(file_path, year, config, district_id)
                    if doe_form_data:
                        logger.info(f"Generating SQL statements for district {district_name} (ID: {district_id})...")
                        sql_statements.extend(doe_form_data.generate_sql_statements())
            
            # Cache the generated SQL
            with open(cache_file, 'w') as f:
                f.write('\n'.join(sql_statements))
        
        # Execute each SQL statement individually
        for statement in sql_statements:
            if statement.strip():  # Skip empty statements
                # Wrap each statement in a transaction
                op.execute(sa.text(f"""
                    BEGIN;
                    {statement}
                    COMMIT;
                """))
        
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        raise Exception(f"Error during migration: {str(e)}")

def downgrade():
    """Execute the downgrade migration."""
    # Add downgrade logic if needed
    pass
