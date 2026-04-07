from enum import Enum
from dataclasses import dataclass


class DefectType(str, Enum):
    LONGITUDINAL_CRACK = "longitudinal_crack"
    TRANSVERSE_CRACK = "transverse_crack"
    ALLIGATOR_CRACK = "alligator_crack"
    REPAIRED_CRACK = "repaired_crack"
    POTHOLE = "pothole"
    CROSSWALK_BLUR = "crosswalk_blur"
    LANE_LINE_BLUR = "lane_line_blur"
    MANHOLE_COVER = "manhole_cover"
    PATCH = "patch"
    RUTTING = "rutting"
    OTHER = "other"
    
    def get_display_name(self) -> str:
        names = {
            DefectType.LONGITUDINAL_CRACK: "Longitudinal Crack",
            DefectType.TRANSVERSE_CRACK: "Transverse Crack",
            DefectType.ALLIGATOR_CRACK: "Alligator Crack",
            DefectType.REPAIRED_CRACK: "Repaired Crack",
            DefectType.POTHOLE: "Pothole",
            DefectType.CROSSWALK_BLUR: "Crosswalk Blur",
            DefectType.LANE_LINE_BLUR: "Lane Line Blur",
            DefectType.MANHOLE_COVER: "Manhole Cover",
            DefectType.PATCH: "Patch",
            DefectType.RUTTING: "Rutting",
            DefectType.OTHER: "Other"
        }
        return names.get(self, "Unknown")


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
    def get_color(self) -> str:
        colors = {
            SeverityLevel.LOW: "#4CAF50",
            SeverityLevel.MEDIUM: "#FFC107",
            SeverityLevel.HIGH: "#FF9800",
            SeverityLevel.CRITICAL: "#F44336"
        }
        return colors.get(self, "#9E9E9E")


class DefectStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FIXED = "fixed"


class GeometryType(str, Enum):
    POINT = "point"
    LINESTRING = "linestring"


@dataclass
class RoadInfo:
    """Информация о дороге"""
    osm_way_id: int
    road_name: str | None = None
    road_class: str | None = None
    distance_to_road: float | None = None