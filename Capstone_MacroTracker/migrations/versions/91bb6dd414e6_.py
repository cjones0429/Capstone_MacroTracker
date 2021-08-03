"""empty message

Revision ID: 91bb6dd414e6
Revises: 
Create Date: 2021-08-02 21:30:28.806015

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91bb6dd414e6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('calories_goal', sa.Integer(), nullable=True),
    sa.Column('carb_goal', sa.Numeric(), nullable=True),
    sa.Column('fat_goal', sa.Numeric(), nullable=True),
    sa.Column('protein_goal', sa.Numeric(), nullable=True),
    sa.Column('carbs_grams', sa.Integer(), nullable=True),
    sa.Column('fat_grams', sa.Integer(), nullable=True),
    sa.Column('protein_grams', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('food',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('food_name', sa.String(length=140), nullable=True),
    sa.Column('kcal', sa.Numeric(precision=10, scale=0), nullable=True),
    sa.Column('protein', sa.Numeric(precision=10, scale=0), nullable=True),
    sa.Column('fat', sa.Numeric(precision=10, scale=0), nullable=True),
    sa.Column('carbs', sa.Numeric(precision=10, scale=0), nullable=True),
    sa.Column('meal', sa.String(length=64), nullable=True),
    sa.Column('ndbno', sa.String(length=64), nullable=True),
    sa.Column('unit', sa.String(length=64), nullable=True),
    sa.Column('count', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('date', sa.String(length=64), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_food_date'), 'food', ['date'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_food_date'), table_name='food')
    op.drop_table('food')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###
