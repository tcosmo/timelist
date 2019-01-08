"""descr

Revision ID: 0fb5398902fd
Revises: bf7b0900bb87
Create Date: 2018-12-30 20:10:29.540199

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0fb5398902fd'
down_revision = 'bf7b0900bb87'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('list_type', sa.Column('description', sa.String(), nullable=True))
    op.create_index(op.f('ix_list_type_description'), 'list_type', ['description'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_list_type_description'), table_name='list_type')
    op.drop_column('list_type', 'description')
    # ### end Alembic commands ###
