"""initial migration

Revision ID: 603e766dffcb
Revises: 
Create Date: 2019-04-18 13:11:44.866553

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '603e766dffcb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('comments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.Column('replied_id', sa.Integer(), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('content_html', sa.Text(), nullable=True),
    sa.Column('ip', sa.String(length=48), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('language', sa.String(length=8), nullable=True),
    sa.Column('approved', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comments_create_time'), 'comments', ['create_time'], unique=False)
    op.create_index(op.f('ix_comments_ip'), 'comments', ['ip'], unique=False)
    op.create_index(op.f('ix_comments_language'), 'comments', ['language'], unique=False)
    op.create_index(op.f('ix_comments_post_id'), 'comments', ['post_id'], unique=False)
    op.create_table('likes',
    sa.Column('ip', sa.String(length=48), nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('ip', 'post_id')
    )
    op.create_table('login_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('ip', sa.String(length=48), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_login_logs_user_id'), 'login_logs', ['user_id'], unique=False)
    op.create_table('photos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('ip', sa.String(length=48), nullable=True),
    sa.Column('path', sa.String(length=16), nullable=True),
    sa.Column('image', sa.String(length=64), nullable=True),
    sa.Column('title', sa.String(length=128), nullable=True),
    sa.Column('public', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_photos_image'), 'photos', ['image'], unique=False)
    op.create_index(op.f('ix_photos_ip'), 'photos', ['ip'], unique=False)
    op.create_index(op.f('ix_photos_path'), 'photos', ['path'], unique=False)
    op.create_index(op.f('ix_photos_timestamp'), 'photos', ['timestamp'], unique=False)
    op.create_index(op.f('ix_photos_user_id'), 'photos', ['user_id'], unique=False)
    op.create_table('post_tag_relationships',
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.Column('post_tag_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('post_id', 'post_tag_id')
    )
    op.create_index(op.f('ix_post_tag_relationships_timestamp'), 'post_tag_relationships', ['timestamp'], unique=False)
    op.create_table('post_tags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('content', sa.String(length=64), nullable=True),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_post_tags_content'), 'post_tags', ['content'], unique=False)
    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.String(length=32), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('user_name', sa.String(length=64), nullable=True),
    sa.Column('summary', sa.Text(), nullable=True),
    sa.Column('summary_html', sa.Text(), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('content_html', sa.Text(), nullable=True),
    sa.Column('image', sa.String(length=48), nullable=True),
    sa.Column('video', sa.String(length=48), nullable=True),
    sa.Column('poster', sa.String(length=48), nullable=True),
    sa.Column('file_md5', sa.String(length=32), nullable=True),
    sa.Column('filename', sa.String(length=128), nullable=True),
    sa.Column('file_size', sa.String(length=16), nullable=True),
    sa.Column('public', sa.Integer(), nullable=True),
    sa.Column('likes_count', sa.Integer(), nullable=True),
    sa.Column('views_count', sa.Integer(), nullable=True),
    sa.Column('comments_count', sa.Integer(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.Column('update_ip', sa.String(length=48), nullable=True),
    sa.Column('language', sa.String(length=8), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_posts_create_time'), 'posts', ['create_time'], unique=False)
    op.create_index(op.f('ix_posts_language'), 'posts', ['language'], unique=False)
    op.create_index(op.f('ix_posts_update_ip'), 'posts', ['update_ip'], unique=False)
    op.create_index(op.f('ix_posts_update_time'), 'posts', ['update_time'], unique=False)
    op.create_index(op.f('ix_posts_user_id'), 'posts', ['user_id'], unique=False)
    op.create_index(op.f('ix_posts_user_name'), 'posts', ['user_name'], unique=False)
    op.create_index(op.f('ix_posts_uuid'), 'posts', ['uuid'], unique=False)
    op.create_table('user_profiles',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('full_name', sa.String(length=64), nullable=True),
    sa.Column('gender', sa.String(length=10), nullable=True),
    sa.Column('birthday', sa.Date(), nullable=True),
    sa.Column('photo', sa.String(length=64), nullable=True),
    sa.Column('introduction', sa.Text(), nullable=True),
    sa.Column('address', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_name', sa.String(length=32), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('update_password', sa.String(length=32), nullable=True),
    sa.Column('new_comment', sa.DateTime(), nullable=True),
    sa.Column('last_export', sa.DateTime(), nullable=True),
    sa.Column('export_path', sa.String(length=32), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('language', sa.String(length=8), nullable=True),
    sa.Column('ip', sa.String(length=48), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_ip'), 'users', ['ip'], unique=False)
    op.create_index(op.f('ix_users_timestamp'), 'users', ['timestamp'], unique=False)
    op.create_index(op.f('ix_users_user_name'), 'users', ['user_name'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_user_name'), table_name='users')
    op.drop_index(op.f('ix_users_timestamp'), table_name='users')
    op.drop_index(op.f('ix_users_ip'), table_name='users')
    op.drop_table('users')
    op.drop_table('user_profiles')
    op.drop_index(op.f('ix_posts_uuid'), table_name='posts')
    op.drop_index(op.f('ix_posts_user_name'), table_name='posts')
    op.drop_index(op.f('ix_posts_user_id'), table_name='posts')
    op.drop_index(op.f('ix_posts_update_time'), table_name='posts')
    op.drop_index(op.f('ix_posts_update_ip'), table_name='posts')
    op.drop_index(op.f('ix_posts_language'), table_name='posts')
    op.drop_index(op.f('ix_posts_create_time'), table_name='posts')
    op.drop_table('posts')
    op.drop_index(op.f('ix_post_tags_content'), table_name='post_tags')
    op.drop_table('post_tags')
    op.drop_index(op.f('ix_post_tag_relationships_timestamp'), table_name='post_tag_relationships')
    op.drop_table('post_tag_relationships')
    op.drop_index(op.f('ix_photos_user_id'), table_name='photos')
    op.drop_index(op.f('ix_photos_timestamp'), table_name='photos')
    op.drop_index(op.f('ix_photos_path'), table_name='photos')
    op.drop_index(op.f('ix_photos_ip'), table_name='photos')
    op.drop_index(op.f('ix_photos_image'), table_name='photos')
    op.drop_table('photos')
    op.drop_index(op.f('ix_login_logs_user_id'), table_name='login_logs')
    op.drop_table('login_logs')
    op.drop_table('likes')
    op.drop_index(op.f('ix_comments_post_id'), table_name='comments')
    op.drop_index(op.f('ix_comments_language'), table_name='comments')
    op.drop_index(op.f('ix_comments_ip'), table_name='comments')
    op.drop_index(op.f('ix_comments_create_time'), table_name='comments')
    op.drop_table('comments')
    # ### end Alembic commands ###