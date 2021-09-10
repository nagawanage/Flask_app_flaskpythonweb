"""add UserConnect

Revision ID: 81ca382ae630
Revises: d291bf803e92
Create Date: 2021-09-10 22:36:55.987815

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '81ca382ae630'
down_revision = 'd291bf803e92'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_connects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('from_user_id', sa.Integer(), nullable=True),
    sa.Column('to_user_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('create_at', sa.DateTime(), nullable=True),
    sa.Column('update_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['from_user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['to_user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_connects_from_user_id'), 'user_connects', ['from_user_id'], unique=False)
    op.create_index(op.f('ix_user_connects_to_user_id'), 'user_connects', ['to_user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_connects_to_user_id'), table_name='user_connects')
    op.drop_index(op.f('ix_user_connects_from_user_id'), table_name='user_connects')
    op.drop_table('user_connects')
    # ### end Alembic commands ###