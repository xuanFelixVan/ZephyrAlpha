# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model-profiler/blueprint.md
# [MODULE] zephyr.intelligence.model_profiling.pipeline_routing.capability_passport
# [DOMAIN] D-INTELLIGENCE
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
# [A_module] module_id=MOD-RSC_capability_passport | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""
CapabilityPassport --- AI 模型能力护照

每个模型入职考试完成后产生的 JSON 数据模型。
存储路径: data/brain/passports/{model_id}.json

护照内容:
    - breadth: 横轴 (能力覆盖范围)
    - depth:   纵轴 (精度深度, 分能力)
    - speed:   速轴 (延迟/吞吐)
    - hallucination: 幻轴 (幻觉率)
    - drift:   稳轴 (长时间漂移)
    - recommendations: 推荐 (safe_capabilities, unsafe_capabilities)
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
PASSPORTS_DIR = PROJECT_ROOT / "data" / "brain" / "passports"

# 各能力类型的精度及格线
DEPTH_THRESHOLDS: dict[str, float] = {
    "task_classification": 0.60,
    "tag_completion": 0.55,
    "summary_extraction": 0.55,
    "naming_suggest": 0.50,
    "anomaly_triage": 0.50,
    "code_fix": 0.60,
    "refactor": 0.55,
    "code_generate": 0.55,
    "dead_code_removal": 0.55,
    # B类: 多文件联动能力
    "cross_file_analysis": 0.55,
    "architecture_design": 0.50,
    "cross_file_refactor": 0.55,
    "dependency_trace": 0.55,
}


@dataclass
class BreadthResult:
    score: float = 0.0
    passed: int = 0
    total: int = 0
    failed_capabilities: list[str] = field(default_factory=list)


@dataclass
class DepthCapabilityResult:
    pass_: bool = False
    grade: str = "F"
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    edit_distance_avg: float = 0.0
    exact_match_rate: float = 0.0
    samples_tested: int = 0
    failure_reason: str = ""


@dataclass
class DepthResult:
    overall_score: float = 0.0
    capabilities: dict[str, DepthCapabilityResult] = field(default_factory=dict)


@dataclass
class SpeedResult:
    avg_latency_ms: float = 0.0
    latency_p50_ms: float = 0.0
    latency_p95_ms: float = 0.0
    latency_p99_ms: float = 0.0
    tokens_per_second: float = 0.0
    time_to_first_token_ms: float = 0.0


@dataclass
class HallucinationResult:
    overall_rate: float = 0.0
    fabrication_rate: float = 0.0
    inconsistency_rate: float = 0.0
    refusal_rate: float = 0.0


@dataclass
class DriftResult:
    tested: bool = False
    output_drift: float = 0.0
    speed_drift_ratio: float = 0.0
    hallucination_drift_delta: float = 0.0
    stable: bool = False


@dataclass
class Recommendations:
    safe_capabilities: list[str] = field(default_factory=list)
    unsafe_capabilities: list[str] = field(default_factory=list)
    max_concurrent_tasks: int = 4
    note: str = ""


@dataclass
class CapabilityPassport:
    passport_version: str = "1.0.0"
    model_id: str = ""
    exam_timestamp: str = ""
    exam_duration_seconds: float = 0.0
    git_commit: str = ""
    overall_grade: str = "F"
    overall_score: float = 0.0
    breadth: BreadthResult = field(default_factory=BreadthResult)
    depth: DepthResult = field(default_factory=DepthResult)
    speed: SpeedResult = field(default_factory=SpeedResult)
    hallucination: HallucinationResult = field(default_factory=HallucinationResult)
    drift: DriftResult = field(default_factory=DriftResult)
    recommendations: Recommendations = field(default_factory=Recommendations)

    def to_dict(self) -> dict:
        result: dict[str, Any] = {}
        for k, v in asdict(self).items():
            result[k] = v
        result["depth"]["capabilities"] = {
            cap: asdict(cap_result) for cap, cap_result in self.depth.capabilities.items()
        }
        return result

    def save(self) -> Path:
        PASSPORTS_DIR.mkdir(parents=True, exist_ok=True)
        safe_id = self.model_id.replace(":", "_").replace("/", "_")
        path = PASSPORTS_DIR / f"{safe_id}.json"
        path.write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        _log.info("CapabilityPassport saved: %s", path)
        return path

    @staticmethod
    def load(model_id: str) -> CapabilityPassport | None:
        safe_id = model_id.replace(":", "_").replace("/", "_")
        path = PASSPORTS_DIR / f"{safe_id}.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return CapabilityPassport._from_dict(data)
        except Exception as exc:
            _log.warning("Failed to load passport for %s: %s", model_id, exc)
            return None

    @staticmethod
    def _from_dict(data: dict) -> CapabilityPassport:
        depth_caps: dict[str, DepthCapabilityResult] = {}
        for cap_name, cap_data in data.get("depth", {}).get("capabilities", {}).items():
            depth_caps[cap_name] = DepthCapabilityResult(**cap_data)

        return CapabilityPassport(
            passport_version=data.get("passport_version", "1.0.0"),
            model_id=data.get("model_id", ""),
            exam_timestamp=data.get("exam_timestamp", ""),
            exam_duration_seconds=data.get("exam_duration_seconds", 0.0),
            git_commit=data.get("git_commit", ""),
            overall_grade=data.get("overall_grade", "F"),
            overall_score=data.get("overall_score", 0.0),
            breadth=BreadthResult(**data.get("breadth", {})),
            depth=DepthResult(
                overall_score=data.get("depth", {}).get("overall_score", 0.0),
                capabilities=depth_caps,
            ),
            speed=SpeedResult(**data.get("speed", {})),
            hallucination=HallucinationResult(**data.get("hallucination", {})),
            drift=DriftResult(**data.get("drift", {})),
            recommendations=Recommendations(**data.get("recommendations", {})),
        )

    @staticmethod
    def list_all() -> list[str]:
        if not PASSPORTS_DIR.exists():
            return []
        return [p.stem.replace("_", ":") for p in PASSPORTS_DIR.glob("*.json")]


def compute_grade(score: float) -> str:
    if score >= 0.90:
        return "A+"
    elif score >= 0.85:
        return "A"
    elif score >= 0.80:
        return "A-"
    elif score >= 0.75:
        return "B+"
    elif score >= 0.70:
        return "B"
    elif score >= 0.65:
        return "B-"
    elif score >= 0.60:
        return "C+"
    elif score >= 0.55:
        return "C"
    elif score >= 0.50:
        return "C-"
    elif score >= 0.40:
        return "D"
    else:
        return "F"
