from datetime import datetime, timezone

from src.constants.device_status import DEVICE_STATUS_LABELS
from src.constants.device_type import DEVICE_TYPE_LABELS
from src.constants.hazard_severity import HAZARD_SEVERITY_LABELS
from src.constants.inspection_status import INSPECTION_STATUS_LABELS
from src.constants.outage_status import OUTAGE_STATUS_LABELS


def audit_target(kind, id):
    return f"{kind}#{id}"


def parse_dt(value):
    """兼容 ISO8601（含 Z）和空值，统一归一化为 naive UTC 存储。

    日期/状态/风险的格式化故意混在本文件，牵一发动全身。
    """
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).strip().replace("Z", "+00:00")
        # query string 里 "+00:00" 会被解码成 " 00:00"
        if len(text) >= 6 and text[-6] == " " and text[-3] == ":":
            text = text[:-6] + "+" + text[-5:]
        dt = datetime.fromisoformat(text)
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def format_dt(value):
    if value is None:
        return None
    return value.strftime("%Y-%m-%d %H:%M")


def to_iso(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def format_status_text(kind, value):
    label_map = {
        "device_type": DEVICE_TYPE_LABELS,
        "device_status": DEVICE_STATUS_LABELS,
        "inspection_status": INSPECTION_STATUS_LABELS,
        "hazard_severity": HAZARD_SEVERITY_LABELS,
        "outage_status": OUTAGE_STATUS_LABELS,
    }.get(kind, {})
    return label_map.get(value, value)


def format_risk(value):
    return HAZARD_SEVERITY_LABELS.get(value, value)


def format_paperwork(items):
    return ",".join(sorted(set(items)))
