"""empty message

Revision ID: 0a7fe5b4bfe6
Revises: 62abdfd4cca9
Create Date: 2023-12-10 14:38:33.681577

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a7fe5b4bfe6'
down_revision = '62abdfd4cca9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('usertype')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('usertype', sa.INTEGER(), nullable=False))

    # ### end Alembic commands ###