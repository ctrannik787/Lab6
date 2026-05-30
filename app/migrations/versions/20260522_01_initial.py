
from alembic import op
import sqlalchemy as sa
from datetime import datetime
from werkzeug.security import generate_password_hash


revision = '20260522_01'
down_revision = None
branch_labels = None
depends_on = None


def data_upgrades():

    categories_table = sa.sql.table('categories', sa.sql.column('name', sa.String))

    op.bulk_insert(categories_table,
        [
            {'name': 'Программирование'},
            {'name': 'Математика'},
            {'name': 'Языкознание'},
        ]
    )

    users_table = sa.sql.table(
        'users',
        sa.sql.column('first_name', sa.String),
        sa.sql.column('last_name', sa.String),
        sa.sql.column('middle_name', sa.String),
        sa.sql.column('login', sa.String),
        sa.sql.column('password_hash', sa.String),
        sa.sql.column('created_at', sa.DateTime),
    )

    op.bulk_insert(users_table,
        [
            {
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'middle_name': None,
                'login': 'user1',
                'password_hash': generate_password_hash('qwerty'),
                'created_at': datetime.now(),
            },
            {
                'first_name': 'Петр',
                'last_name': 'Петров',
                'middle_name': None,
                'login': 'user2',
                'password_hash': generate_password_hash('qwerty'),
                'created_at': datetime.now(),
            },
            {
                'first_name': 'Мария',
                'last_name': 'Сидорова',
                'middle_name': None,
                'login': 'user3',
                'password_hash': generate_password_hash('qwerty'),
                'created_at': datetime.now(),
            },
            {
                'first_name': 'Алексей',
                'last_name': 'Смирнов',
                'middle_name': None,
                'login': 'user4',
                'password_hash': generate_password_hash('qwerty'),
                'created_at': datetime.now(),
            },
            {
                'first_name': 'Анна',
                'last_name': 'Кузнецова',
                'middle_name': None,
                'login': 'user5',
                'password_hash': generate_password_hash('qwerty'),
                'created_at': datetime.now(),
            },
        ]
    )


def upgrade():
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], name=op.f('fk_categories_parent_id_categories')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_categories')),
    )

    op.create_table(
        'images',
        sa.Column('id', sa.String(length=100), nullable=False),
        sa.Column('file_name', sa.String(length=100), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('md5_hash', sa.String(length=100), nullable=False),
        sa.Column('object_id', sa.Integer(), nullable=True),
        sa.Column('object_type', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_images')),
        sa.UniqueConstraint('md5_hash', name=op.f('uq_images_md5_hash')),
    )

    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('middle_name', sa.String(length=100), nullable=True),
        sa.Column('login', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=200), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
        sa.UniqueConstraint('login', name=op.f('uq_users_login')),
    )

    op.create_table(
        'courses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('short_desc', sa.Text(), nullable=False),
        sa.Column('full_desc', sa.Text(), nullable=False),
        sa.Column('rating_sum', sa.Integer(), nullable=False),
        sa.Column('rating_num', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('background_image_id', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], name=op.f('fk_courses_author_id_users')),
        sa.ForeignKeyConstraint(['background_image_id'], ['images.id'], name=op.f('fk_courses_background_image_id_images')),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name=op.f('fk_courses_category_id_categories')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_courses')),
    )

    data_upgrades()


def downgrade():
    op.drop_table('courses')
    op.drop_table('users')
    op.drop_table('images')
    op.drop_table('categories')
