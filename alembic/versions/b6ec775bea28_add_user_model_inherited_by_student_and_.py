"""Add User model inherited by Student and Instructor

Revision ID: b6ec775bea28
Revises: 52699a7250ae
Create Date: 2023-08-10 23:11:08.870541+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b6ec775bea28'
down_revision = '52699a7250ae'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_type', sa.Enum('STUDENT', 'INSTRUCTOR', name='usertype'), nullable=False),
    sa.Column('onyen', sa.Text(), nullable=False),
    sa.Column('first_name', sa.Text(), nullable=False),
    sa.Column('last_name', sa.Text(), nullable=False),
    sa.Column('email', sa.Text(), nullable=False),
    sa.Column('password', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)
    op.create_index(op.f('ix_user_onyen'), 'user', ['onyen'], unique=True)
    op.drop_constraint('instructor_instructor_onyen_key', 'instructor', type_='unique')
    op.drop_index('ix_instructor_id', table_name='instructor')
    op.create_foreign_key(None, 'instructor', 'user', ['id'], ['id'])
    op.drop_column('instructor', 'first_name')
    op.drop_column('instructor', 'instructor_onyen')
    op.drop_column('instructor', 'last_name')
    op.drop_index('ix_student_id', table_name='student')
    op.drop_constraint('student_student_onyen_key', 'student', type_='unique')
    op.create_foreign_key(None, 'student', 'user', ['id'], ['id'])
    op.drop_column('student', 'password')
    op.drop_column('student', 'email')
    op.drop_column('student', 'last_name')
    op.drop_column('student', 'first_name')
    op.drop_column('student', 'student_onyen')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('student', sa.Column('student_onyen', sa.TEXT(), autoincrement=False, nullable=False))
    op.add_column('student', sa.Column('first_name', sa.TEXT(), autoincrement=False, nullable=False))
    op.add_column('student', sa.Column('last_name', sa.TEXT(), autoincrement=False, nullable=False))
    op.add_column('student', sa.Column('email', sa.TEXT(), autoincrement=False, nullable=False))
    op.add_column('student', sa.Column('password', sa.TEXT(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'student', type_='foreignkey')
    op.create_unique_constraint('student_student_onyen_key', 'student', ['student_onyen'])
    op.create_index('ix_student_id', 'student', ['id'], unique=False)
    op.add_column('instructor', sa.Column('last_name', sa.TEXT(), autoincrement=False, nullable=False))
    op.add_column('instructor', sa.Column('instructor_onyen', sa.TEXT(), autoincrement=False, nullable=False))
    op.add_column('instructor', sa.Column('first_name', sa.TEXT(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'instructor', type_='foreignkey')
    op.create_index('ix_instructor_id', 'instructor', ['id'], unique=False)
    op.create_unique_constraint('instructor_instructor_onyen_key', 'instructor', ['instructor_onyen'])
    op.drop_index(op.f('ix_user_onyen'), table_name='user')
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###
