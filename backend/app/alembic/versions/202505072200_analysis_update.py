"""Analysis Update

Revision ID: 202505072200
Revises: 202504162144
Create Date: 2025-05-07 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '202505072200'
down_revision = '202504162144'
branch_labels = None
depends_on = None


def upgrade():
    # Add is_demographic column to survey_analysis_question table
    op.add_column('survey_analysis_question', sa.Column('is_demographic', sa.Boolean(), server_default='false', nullable=False))
    
    # Add comment to explain the purpose of this column
    op.execute("""
        COMMENT ON COLUMN survey_analysis_question.is_demographic IS 
        'Indicates whether this analysis question represents demographic data'
    """)
    
    # Create survey_analysis_answer_transform table
    op.execute("""
        CREATE TABLE survey_analysis_answer_transform (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            survey_analysis_question_id UUID NOT NULL REFERENCES survey_analysis_question(id) ON DELETE CASCADE,
            original_answer TEXT NOT NULL,
            new_answer TEXT NOT NULL,
            new_order_id INTEGER NOT NULL,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create index for better performance on survey_analysis_answer_transform
    op.execute("""
        CREATE INDEX idx_answer_transform_question_id 
        ON survey_analysis_answer_transform(survey_analysis_question_id)
    """)
    
    # Create survey_analysis_filter table
    op.execute("""
        CREATE TABLE survey_analysis_filter (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            survey_analysis_id UUID NOT NULL REFERENCES survey_analysis(id) ON DELETE CASCADE,
            survey_analysis_question_id UUID NOT NULL REFERENCES survey_analysis_question(id) ON DELETE CASCADE,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create survey_analysis_filter_criteria table
    op.execute("""
        CREATE TABLE survey_analysis_filter_criteria (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            survey_analysis_filter_id UUID NOT NULL REFERENCES survey_analysis_filter(id) ON DELETE CASCADE,
            value TEXT NOT NULL,
            date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes for better performance on new tables
    op.execute("""
        CREATE INDEX idx_survey_analysis_filter_analysis_id 
        ON survey_analysis_filter(survey_analysis_id)
    """)
    
    op.execute("""
        CREATE INDEX idx_survey_analysis_filter_question_id 
        ON survey_analysis_filter(survey_analysis_question_id)
    """)
    
    op.execute("""
        CREATE INDEX idx_survey_analysis_filter_criteria_filter_id 
        ON survey_analysis_filter_criteria(survey_analysis_filter_id)
    """)
    
    # Create triggers for date_updated columns
    op.execute("""
        CREATE TRIGGER update_survey_analysis_answer_transform_modtime 
        BEFORE UPDATE ON survey_analysis_answer_transform 
        FOR EACH ROW EXECUTE PROCEDURE update_modified_column()
    """)
    
    op.execute("""
        CREATE TRIGGER update_survey_analysis_filter_modtime 
        BEFORE UPDATE ON survey_analysis_filter 
        FOR EACH ROW EXECUTE PROCEDURE update_modified_column()
    """)
    
    op.execute("""
        CREATE TRIGGER update_survey_analysis_filter_criteria_modtime 
        BEFORE UPDATE ON survey_analysis_filter_criteria 
        FOR EACH ROW EXECUTE PROCEDURE update_modified_column()
    """)


def downgrade():
    # Drop the new tables in reverse order (to respect foreign key constraints)
    op.execute("DROP TABLE IF EXISTS survey_analysis_filter_criteria CASCADE")
    op.execute("DROP TABLE IF EXISTS survey_analysis_filter CASCADE")
    op.execute("DROP TABLE IF EXISTS survey_analysis_answer_transform CASCADE")
    
    # Remove the is_demographic column
    op.drop_column('survey_analysis_question', 'is_demographic')