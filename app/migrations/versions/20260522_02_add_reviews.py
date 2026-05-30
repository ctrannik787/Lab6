
from alembic import op
import sqlalchemy as sa


revision = '20260522_02'
down_revision = '20260522_01'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.CheckConstraint('rating >= 0 AND rating <= 5', name=op.f('ck_reviews_rating_between_0_and_5')),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], name=op.f('fk_reviews_course_id_courses')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_reviews_user_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_reviews')),
        sa.UniqueConstraint('course_id', 'user_id', name='uq_reviews_course_id_user_id'),
    )


def downgrade():
    op.drop_table('reviews')
