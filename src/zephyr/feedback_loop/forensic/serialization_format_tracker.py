# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.forensic.serialization_format_tracker
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Serialization Format Tracker — v0.39.0 R488

Blindspot: Pickle protocol versions, JSON schema evolution, and YAML tag
compatibility change across Python/FLE upgrades. Persisted FLE state becomes
unreadable after version upgrades with no warning until runtime crash.

Risk: R488 — FLE cannot restore checkpoint; rollback impossible because
serialized state format is incompatible; silent data corruption from
pickle protocol mismatch.

Mitigation: Track serialization format metadata (protocol version, schema
hash, library versions) for all persisted state. Validate compatibility
at write time and read time. Alert when format version changes. Maintain
backward compatibility map.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: serialization_format_tracker.py
# 层: 算法
# - id: A1
#   name_zh: ① SerializationFormatTracker
#   name_en: SerializationFormatTracker
#   intro: class SerializationFormatTracker 源码 L85-L182
#   desc: 公共方法（定义序）: record_artifact, check_compatibility, validate_state_load, get_format_history, get_breaking_change…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: SerializationFormatTracker
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
import pickle
import time
from dataclasses import dataclass, field
from enum import Enum


class SerdeFormat(str, Enum):
    PICKLE = "PICKLE"
    JSON = "JSON"
    YAML = "YAML"
    MSGPACK = "MSGPACK"


class Compatibility(str, Enum):
    COMPATIBLE = "COMPATIBLE"
    MINOR_CHANGE = "MINOR_CHANGE"
    BREAKING = "BREAKING"


@dataclass
class SerializationFormatTracker:
    max_tracked_artifacts: int = 500

    format_versions: dict[str, dict] = field(default_factory=dict)
    compatibility_map: dict[str, dict[str, str]] = field(default_factory=dict)
    version_changes: list[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.format_versions = {
            "pickle": {"protocol": pickle.HIGHEST_PROTOCOL, "python": "", "hash": ""},
            "json": {"schema_version": "0.0.0", "hash": ""},
        }

    def record_artifact(self, artifact_id: str, fmt: SerdeFormat, content_bytes: bytes) -> dict:
        fmt_hash = hashlib.sha256(content_bytes).hexdigest()
        entry = {
            "artifact_id": artifact_id,
            "format": fmt.value,
            "size_bytes": len(content_bytes),
            "hash": fmt_hash[:16],
            "recorded_at": time.time(),
            "pickle_protocol": pickle.HIGHEST_PROTOCOL if fmt is SerdeFormat.PICKLE else None,
        }
        self.format_versions[artifact_id] = entry

        keys = list(self.format_versions.keys())
        if len(keys) > self.max_tracked_artifacts:
            for old_key in keys[: len(keys) - self.max_tracked_artifacts]:
                if old_key not in ("pickle", "json"):
                    self.format_versions.pop(old_key, None)

        return {"artifact_id": artifact_id, "hash": fmt_hash[:16], "size": len(content_bytes)}

    def check_compatibility(self, artifact_id: str, current_fmt: SerdeFormat) -> dict:
        entry = self.format_versions.get(artifact_id)
        if not entry:
            return {"compatibility": Compatibility.COMPATIBLE.value, "reason": "no_prior_record"}

        if entry["format"] != current_fmt.value:
            msg = f"format_changed:{entry['format']}->{current_fmt.value}"
            self.version_changes.append(
                {
                    "ts": time.time(),
                    "artifact": artifact_id,
                    "change": msg,
                    "severity": "BREAKING",
                }
            )
            return {"compatibility": Compatibility.BREAKING.value, "reason": msg}

        if current_fmt is SerdeFormat.PICKLE:
            if entry.get("pickle_protocol") != pickle.HIGHEST_PROTOCOL:
                self.version_changes.append(
                    {
                        "ts": time.time(),
                        "artifact": artifact_id,
                        "change": f"pickle_protocol:{entry.get('pickle_protocol')}->{pickle.HIGHEST_PROTOCOL}",
                        "severity": "MINOR",
                    }
                )
                return {"compatibility": Compatibility.MINOR_CHANGE.value, "reason": "pickle_protocol_changed"}

        return {"compatibility": Compatibility.COMPATIBLE.value, "reason": "format_consistent"}

    def validate_state_load(self, artifact_id: str, loaded_obj: object, expected_type: type) -> dict:
        if not isinstance(loaded_obj, expected_type):
            self.version_changes.append(
                {
                    "ts": time.time(),
                    "artifact": artifact_id,
                    "change": f"type_mismatch:{type(loaded_obj).__name__}!={expected_type.__name__}",
                    "severity": "BREAKING",
                }
            )
            return {
                "valid": False,
                "expected_type": expected_type.__name__,
                "actual_type": type(loaded_obj).__name__,
                "recommendation": "reject_state_and_rebuild",
            }
        return {"valid": True}

    def get_format_history(self) -> list[dict]:
        return sorted(
            [
                {"id": k, "format": v.get("format", "schema"), "recorded_at": v.get("recorded_at", 0)}
                for k, v in self.format_versions.items()
                if k not in ("pickle", "json")
            ],
            key=lambda x: -x["recorded_at"],
        )

    def get_breaking_changes_count(self) -> int:
        return len([c for c in self.version_changes if c["severity"] == "BREAKING"])

    def overall_format_health(self) -> float:
        breaking = self.get_breaking_changes_count()
        return round(max(0.0, 1.0 - breaking * 0.1), 3)
