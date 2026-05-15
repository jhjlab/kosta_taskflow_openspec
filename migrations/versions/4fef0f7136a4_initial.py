"""initial

Revision ID: 4fef0f7136a4
Revises:
Create Date: 2026-05-15 14:20:10.540684

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '4fef0f7136a4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users와 teams 간 순환 FK → 먼저 FK 없이 테이블 생성, 이후 ALTER TABLE로 추가

    # 1. users (team_id FK 없이 먼저 생성)
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # 2. teams (owner_id FK는 users 생성 후 추가 가능)
    op.create_table('teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=30), nullable=False),
        sa.Column('invite_code', sa.String(length=9), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_teams_id', 'teams', ['id'], unique=False)
    op.create_index('ix_teams_invite_code', 'teams', ['invite_code'], unique=True)

    # 3. users.team_id → teams FK를 ALTER TABLE로 추가
    op.create_foreign_key(
        'fk_users_team_id_teams',
        'users', 'teams',
        ['team_id'], ['id'],
        ondelete='SET NULL'
    )

    # 4. messages
    op.create_table('messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_messages_id', 'messages', ['id'], unique=False)
    op.create_index('ix_messages_team_created', 'messages', ['team_id', 'created_at'], unique=False)

    # 5. tasks (TaskStatus enum은 create_table 시 자동 생성)
    op.create_table('tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('status', sa.Enum('TODO', 'DOING', 'DONE', name='taskstatus'), nullable=False),
        sa.Column('creator_id', sa.Integer(), nullable=True),
        sa.Column('assignee_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assignee_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tasks_id', 'tasks', ['id'], unique=False)
    op.create_index('ix_tasks_team_created', 'tasks', ['team_id', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_tasks_team_created', table_name='tasks')
    op.drop_index('ix_tasks_id', table_name='tasks')
    op.drop_table('tasks')
    op.execute('DROP TYPE IF EXISTS taskstatus')

    op.drop_index('ix_messages_team_created', table_name='messages')
    op.drop_index('ix_messages_id', table_name='messages')
    op.drop_table('messages')

    op.drop_constraint('fk_users_team_id_teams', 'users', type_='foreignkey')

    op.drop_index('ix_teams_invite_code', table_name='teams')
    op.drop_index('ix_teams_id', table_name='teams')
    op.drop_table('teams')

    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
