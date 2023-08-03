"""Add instructors table, remove professor onyen from student in favor of course instructors column

Revision ID: 6bef426b477e
Revises: 38c44ed382f8
Create Date: 2023-08-02 17:01:46.909965+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6bef426b477e'
down_revision = '38c44ed382f8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('instructor',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('instructor_onyen', sa.Text(), nullable=False),
    sa.Column('first_name', sa.Text(), nullable=False),
    sa.Column('last_name', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('instructor_onyen')
    )
    op.create_index(op.f('ix_instructor_id'), 'instructor', ['id'], unique=False)
    op.drop_column('student', 'professor_onyen')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('student', sa.Column('professor_onyen', sa.TEXT(), autoincrement=False, nullable=False))
    op.drop_index(op.f('ix_instructor_id'), table_name='instructor')
    op.drop_table('instructor')
    # ### end Alembic commands ###
