"""Add email/password fields to Student model

Revision ID: 52699a7250ae
Revises: 6bef426b477e
Create Date: 2023-08-10 19:26:31.274648+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52699a7250ae'
down_revision = '6bef426b477e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('student', sa.Column('email', sa.Text(), nullable=False))
    op.add_column('student', sa.Column('password', sa.Text(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('student', 'password')
    op.drop_column('student', 'email')
    # ### end Alembic commands ###
