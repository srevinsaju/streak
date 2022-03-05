"""Add timestamp and completed fields for task streak

Revision ID: f5e58b239cd4
Revises: 341c9dda0a4e
Create Date: 2022-03-05 00:44:14.574839

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5e58b239cd4'
down_revision = '341c9dda0a4e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task_streak', sa.Column('timestamp', sa.DateTime(), nullable=True))
    op.add_column('task_streak', sa.Column('completed', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('task_streak', 'completed')
    op.drop_column('task_streak', 'timestamp')
    # ### end Alembic commands ###