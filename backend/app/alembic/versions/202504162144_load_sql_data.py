"""Load SQL data from export file

Revision ID: 202504162144
Revises: b4f374d72f78
Create Date: 2025-04-16 21:44:00.000000

"""
from alembic import op
import os

# revision identifiers, used by Alembic.
revision = '202504162144'
down_revision = 'b4f374d72f78'
branch_labels = None
depends_on = None

def read_sql_file():
    sql_file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),  # Go up to app directory
        'sql_cache',
        'export_202504162144.sql'
    )
    
    if not os.path.exists(sql_file_path):
        raise FileNotFoundError(f"SQL file not found at: {sql_file_path}")
        
    with open(sql_file_path, 'r') as f:
        return f.read()

def upgrade():
    try:
        sql_content = read_sql_file()
        # Split on semicolons but ignore semicolons inside quotes
        # This is a basic implementation - for more complex SQL you might need a proper SQL parser
        statements = sql_content.split(';')
        
        op.execute("SET session_replication_role = 'replica';")
        for statement in statements:
            statement = statement.strip()
            if statement:  # Skip empty statements
                op.execute(statement)
                
    except FileNotFoundError as e:
        print(f"Warning: {e}")
        print("Migration will proceed but no data will be loaded.")
    except Exception as e:
        print(f"Error executing SQL: {e}")
        raise
    finally:
        # Re-enable foreign key constraint checks
        op.execute("SET session_replication_role = 'origin';")
def downgrade():
    # Since this is a data loading migration, the downgrade path
    # should be handled carefully based on your specific needs.
    # Here we'll just print a warning
    print("Warning: This migration loads data and has no automatic downgrade path.")
    print("You will need to manually restore from a backup if you need to downgrade.") 