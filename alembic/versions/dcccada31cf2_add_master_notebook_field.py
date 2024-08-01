"""Add master notebook field

Revision ID: dcccada31cf2
Revises: ce961975d125
Create Date: 2024-06-14 20:46:00.850072+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dcccada31cf2'
down_revision = 'ce961975d125'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('assignment', sa.Column('master_notebook_path', sa.Text(), nullable=False))
    op.add_column('assignment', sa.Column('grader_question_feedback', sa.Boolean(), server_default='t', nullable=False))
    op.create_unique_constraint(None, 'user_onyen_pid', ['onyen'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_onyen_pid', type_='unique')
    op.drop_column('assignment', 'master_notebook_path')
    op.drop_column('assignment', 'grader_question_feedback')
    # ### end Alembic commands ###
