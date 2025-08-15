"""news relevance with config table

Revision ID: c98f0fb7c230
Revises: 1473bcdf4d4c
Create Date: 2025-08-15 14:59:14.406182

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c98f0fb7c230'
down_revision: Union[str, None] = '1473bcdf4d4c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create configuration table
    op.create_table(
        'relevance_config',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('config_name', sa.String(50), nullable=False, unique=True),
        sa.Column('importance_weight', sa.Float(), nullable=False),
        sa.Column('views_weight', sa.Float(), nullable=False),
        sa.Column('time_weight', sa.Float(), nullable=False),
        sa.Column('time_decay_rate', sa.Float(), nullable=False),
        sa.Column('time_window_days', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('description', sa.String(200), nullable=True),
    )

    # Insert default configuration
    op.execute("""
        INSERT INTO relevance_config (
            config_name, importance_weight, views_weight, time_weight, 
            time_decay_rate, time_window_days, is_active, description
        ) VALUES (
            'default', 0.6, 0.3, 0.1, 0.05, 30, true,
            'Default relevance scoring algorithm'
        )
    """)

    # Create materialized view using config table
    op.execute("""
        CREATE MATERIALIZED VIEW news_relevance AS
        WITH active_config AS (
            SELECT 
                importance_weight,
                views_weight, 
                time_weight,
                time_decay_rate,
                time_window_days
            FROM relevance_config 
            WHERE is_active = true 
            LIMIT 1
        )
        SELECT 
            p.id,
            p.title,
            p.description,
            p.updated_at,
            p.view_count,
            p.importancy,
            p.topic_id,
            t.name as topic_name,
            COALESCE(tag_names.tags_text, '') as tags,

            -- Dynamic relevance calculation using config values
            (
                active_config.importance_weight * (p.importancy / 10.0) +
                active_config.views_weight * (
                    LOG10(GREATEST(p.view_count, 1)) / 
                    GREATEST((SELECT LOG10(GREATEST(MAX(view_count), 1)) FROM parsed_news), 1)
                ) +
                active_config.time_weight * EXP(-active_config.time_decay_rate * 
                    (EXTRACT(EPOCH FROM (NOW() - p.updated_at)) / 3600))
            ) as relevance_score,

            -- Individual components for analysis
            (
                LOG10(GREATEST(p.view_count, 1)) / 
                GREATEST((SELECT LOG10(GREATEST(MAX(view_count), 1)) FROM parsed_news), 1)
            ) as normalized_views,

            EXP(-active_config.time_decay_rate * 
                (EXTRACT(EPOCH FROM (NOW() - p.updated_at)) / 3600)) as time_decay_factor,

            NOW() as score_calculated_at

        FROM parsed_news p
        CROSS JOIN active_config
        LEFT JOIN topics t ON p.topic_id = t.id
        LEFT JOIN (
            SELECT pntl.news_item_id, STRING_AGG(tags.text, ', ') as tags_text
            FROM parsed_news_tag_link pntl
            JOIN tags ON pntl.tag_id = tags.id
            GROUP BY pntl.news_item_id
        ) tag_names ON p.id = tag_names.news_item_id

        WHERE p.updated_at >= NOW() - INTERVAL '1 day' * (SELECT time_window_days FROM active_config)
        WITH DATA;
    """)

    # Create indexes
    op.execute("CREATE INDEX idx_news_relevance_score ON news_relevance (relevance_score DESC)")
    op.execute("CREATE INDEX idx_news_relevance_topic ON news_relevance (topic_id, relevance_score DESC)")
    op.execute("CREATE INDEX idx_relevance_config_active ON relevance_config (is_active) WHERE is_active = true")

    # Create helper functions for managing configuration
    op.execute("""
        -- Function to switch active configuration
        CREATE OR REPLACE FUNCTION set_active_relevance_config(config_name_param text)
        RETURNS void AS $$
        BEGIN
            -- Deactivate all configs
            UPDATE relevance_config SET is_active = false;
            
            -- Activate specified config
            UPDATE relevance_config 
            SET is_active = true, updated_at = NOW()
            WHERE config_name = config_name_param;
            
            -- Check if config was found
            IF NOT FOUND THEN
                RAISE EXCEPTION 'Configuration "%" not found', config_name_param;
            END IF;
            
            RAISE NOTICE 'Activated configuration: %', config_name_param;
        END;
        $$ LANGUAGE plpgsql;

        -- Function to update active configuration and refresh view
        CREATE OR REPLACE FUNCTION update_relevance_weights(
            importance_w float,
            views_w float,
            time_w float,
            decay_rate float DEFAULT NULL,
            window_days int DEFAULT NULL
        )
        RETURNS void AS $$
        DECLARE
            current_config_name text;
        BEGIN
            -- Get current active config name
            SELECT config_name INTO current_config_name
            FROM relevance_config 
            WHERE is_active = true;
            
            IF current_config_name IS NULL THEN
                RAISE EXCEPTION 'No active configuration found';
            END IF;
            
            -- Update the active configuration
            UPDATE relevance_config 
            SET 
                importance_weight = importance_w,
                views_weight = views_w,
                time_weight = time_w,
                time_decay_rate = COALESCE(decay_rate, time_decay_rate),
                time_window_days = COALESCE(window_days, time_window_days),
                updated_at = NOW()
            WHERE is_active = true;
            
            -- Refresh the materialized view
            REFRESH MATERIALIZED VIEW news_relevance;
            
            RAISE NOTICE 'Updated weights and refreshed materialized view';
        END;
        $$ LANGUAGE plpgsql;

        -- Function to create new configuration preset
        CREATE OR REPLACE FUNCTION create_relevance_preset(
            preset_name text,
            importance_w float,
            views_w float,
            time_w float,
            decay_rate float,
            window_days int,
            description_text text DEFAULT NULL,
            activate boolean DEFAULT false
        )
        RETURNS void AS $$
        BEGIN
            -- Insert new configuration
            INSERT INTO relevance_config (
                config_name, importance_weight, views_weight, time_weight,
                time_decay_rate, time_window_days, is_active, description
            ) VALUES (
                preset_name, importance_w, views_w, time_w,
                decay_rate, window_days, false, description_text
            );
            
            -- Activate if requested
            IF activate THEN
                PERFORM set_active_relevance_config(preset_name);
                REFRESH MATERIALIZED VIEW news_relevance;
            END IF;
            
            RAISE NOTICE 'Created configuration preset: %', preset_name;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Insert some useful presets
    op.execute("""
        -- Breaking news configuration (fast decay, views matter more)
        INSERT INTO relevance_config (
            config_name, importance_weight, views_weight, time_weight,
            time_decay_rate, time_window_days, is_active, description
        ) VALUES (
            'breaking_news', 0.3, 0.6, 0.1, 0.15, 7, false,
            'Fast decay algorithm for breaking news and time-sensitive content'
        );

        -- Analysis configuration (slow decay, importance matters most)
        INSERT INTO relevance_config (
            config_name, importance_weight, views_weight, time_weight,
            time_decay_rate, time_window_days, is_active, description
        ) VALUES (
            'analysis', 0.8, 0.15, 0.05, 0.01, 90, false,
            'Slow decay algorithm for analysis and evergreen content'
        );

        -- Balanced configuration (moderate decay, balanced weights)
        INSERT INTO relevance_config (
            config_name, importance_weight, views_weight, time_weight,
            time_decay_rate, time_window_days, is_active, description
        ) VALUES (
            'balanced', 0.5, 0.4, 0.1, 0.03, 45, false,
            'Balanced algorithm for mixed content types'
        );
    """)


def downgrade():
    op.execute("DROP MATERIALIZED VIEW IF EXISTS news_relevance")
    op.execute("DROP FUNCTION IF EXISTS set_active_relevance_config(text)")
    op.execute("DROP FUNCTION IF EXISTS update_relevance_weights(float, float, float, float, int)")
    op.execute("DROP FUNCTION IF EXISTS create_relevance_preset(text, float, float, float, float, int, text, boolean)")
    op.drop_table('relevance_config')