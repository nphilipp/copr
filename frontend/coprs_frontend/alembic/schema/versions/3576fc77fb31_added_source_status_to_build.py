""" Added source_status to Build

Revision ID: 3576fc77fb31
Revises: 4edb1ca2a13f
Create Date: 2018-01-20 10:14:10.741230

"""

# revision identifiers, used by Alembic.
revision = '3576fc77fb31'
down_revision = '4edb1ca2a13f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('build', sa.Column('source_status', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('build', 'source_status')
    ### end Alembic commands ###