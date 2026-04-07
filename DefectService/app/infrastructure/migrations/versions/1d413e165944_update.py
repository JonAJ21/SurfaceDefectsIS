"""update

Revision ID: d093f6166724
Revises: 
Create Date: 2026-04-06 22:27:03.882435

"""
from typing import Sequence, Union
import geoalchemy2
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1d413e165944'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаём таблицу
    op.create_table(
        'road_defects',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('original_geometry', geoalchemy2.types.Geometry(srid=4326), nullable=False),
        sa.Column('geometry_type', sa.Enum('POINT', 'LINESTRING', name='geometrytype'), nullable=False),
        sa.Column('snapped_geometry', geoalchemy2.types.Geometry(srid=4326), nullable=True),
        sa.Column('distance_to_road', sa.Float(), nullable=True),
        sa.Column('defect_type', sa.Enum('LONGITUDINAL_CRACK', 'TRANSVERSE_CRACK', 'ALLIGATOR_CRACK', 'REPAIRED_CRACK', 'POTHOLE', 'CROSSWALK_BLUR', 'LANE_LINE_BLUR', 'MANHOLE_COVER', 'PATCH', 'RUTTING', 'OTHER', name='defecttype'), nullable=False),
        sa.Column('severity', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='severitylevel'), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', 'FIXED', name='defectstatus'), nullable=False),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('osm_way_id', sa.BigInteger(), nullable=True),
        sa.Column('road_name', sa.String(255), nullable=True),
        sa.Column('road_class', sa.String(50), nullable=True),
        sa.Column('photos', sa.JSON(), nullable=False),
        sa.Column('created_by', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('moderated_by', sa.String(100), nullable=True),
        sa.Column('moderated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создаём индексы (с проверкой существования)
    op.execute("CREATE INDEX IF NOT EXISTS idx_defect_geometry ON road_defects USING GIST(snapped_geometry)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_defect_status ON road_defects(status)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_defect_created_at ON road_defects(created_at)")


def downgrade() -> None:
    op.drop_index('idx_defect_geometry', table_name='road_defects', if_exists=True)
    op.drop_index('idx_defect_status', table_name='road_defects', if_exists=True)
    op.drop_index('idx_defect_created_at', table_name='road_defects', if_exists=True)
    op.drop_table('road_defects')