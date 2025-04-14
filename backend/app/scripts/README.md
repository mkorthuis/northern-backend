# Database Scripts

This directory contains one-off scripts for database management and data manipulation.

## School Safety Data Script

### Purpose

The `insert_school_safety_data.py` script generates and inserts sample school safety incident data into the database. This script is useful for:

- Populating the database with test data
- Demonstrating the school safety data model
- Testing reports and analytics related to school safety

### Prerequisites

- The database must be set up and accessible
- The school and school_safety_type tables must already be populated
- Python dependencies must be installed:
  - SQLAlchemy
  - psycopg2-binary (`pip install psycopg2-binary`)

### Connection Configuration

The script is currently configured to connect to a PostgreSQL database at:
- Host: localhost
- Port: 5472
- Username: postgres
- Password: postgres
- Database: postgres

If you need to use different connection parameters, modify the `get_database_connection()` function in the script.

### Usage

To run the script:

```bash
cd backend/app
python scripts/insert_school_safety_data.py
```

Or directly if executable:

```bash
cd backend/app
./scripts/insert_school_safety_data.py
```

### Data Generation

The script generates safety incident data with the following characteristics:

- Covers years 2018-2023
- Not all schools will have all incident types
- Most schools have few incidents (0-2), fewer have 3-5, and very few have 6-10
- Uses the school_safety_type values already defined in the database

### Configuration

You can modify the script to change:

- The range of years to generate data for
- The distribution of incident counts
- The selection of safety types per school
- Database connection parameters (in the `get_database_connection()` function)

### Troubleshooting

If you encounter errors:

1. Verify your PostgreSQL database is running on localhost:5472
2. Check that the username/password (postgres/postgres) is correct
3. Ensure the database schema is properly set up
4. Check that schools and safety types exist in the database 