"""empty message

Revision ID: f55f21bce696
Revises: 474fd18d285b
Create Date: 2023-11-02 11:51:01.930251

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f55f21bce696'
down_revision = '474fd18d285b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('villa_user_contact',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=False),
    sa.Column('last_name', sa.String(length=100), nullable=False),
    sa.Column('phone_number', sa.String(length=13), nullable=False),
    sa.Column('home_address_line_1', sa.String(length=100), nullable=False),
    sa.Column('home_address_line_2', sa.String(length=100), nullable=True),
    sa.Column('home_city', sa.String(length=100), nullable=False),
    sa.Column('home_province', sa.String(length=2), nullable=False),
    sa.Column('home_country', sa.String(length=3), nullable=False),
    sa.Column('home_postal_code', sa.String(length=6), nullable=False),
    sa.ForeignKeyConstraint(['home_country'], ['country.id'], ),
    sa.ForeignKeyConstraint(['home_province'], ['province_state.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['villa_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('villa_user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('auth0_id', sa.String(), nullable=False))
        batch_op.drop_constraint('villa_user_home_country_fkey', type_='foreignkey')
        batch_op.drop_constraint('villa_user_home_province_fkey', type_='foreignkey')
        batch_op.drop_column('home_province')
        batch_op.drop_column('home_country')
        batch_op.drop_column('phone_number')
        batch_op.drop_column('home_city')
        batch_op.drop_column('home_address_line_2')
        batch_op.drop_column('first_name')
        batch_op.drop_column('home_address_line_1')
        batch_op.drop_column('last_name')
        batch_op.drop_column('home_postal_code')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('villa_user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('home_postal_code', sa.VARCHAR(length=6), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('last_name', sa.VARCHAR(length=100), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('home_address_line_1', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('first_name', sa.VARCHAR(length=100), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('home_address_line_2', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('home_city', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('phone_number', sa.VARCHAR(length=13), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('home_country', sa.VARCHAR(length=3), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('home_province', sa.VARCHAR(length=2), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('villa_user_home_province_fkey', 'province_state', ['home_province'], ['id'])
        batch_op.create_foreign_key('villa_user_home_country_fkey', 'country', ['home_country'], ['id'])
        batch_op.drop_column('auth0_id')

    op.drop_table('villa_user_contact')
    # ### end Alembic commands ###
