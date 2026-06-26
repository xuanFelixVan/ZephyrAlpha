# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] zephyr.intelligence.model_profiling.capability_passport
# [DOMAIN] D-INTELLIGENCE
# [DEPENDENCIES]
# [CONSUMERS] MOD-INF-034;MOD-INF-009
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 能力护照数据模型;五轴评测结果持久化
# [MODIFY-GUARD] docs/03_modules/_cross_layer/model_profiler/blueprint.md;src/zephyr/intelligence/model_profiling/__init__.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] PassportError;SerializationError
# [TESTS] tests/test_model_profiler/
# [A_module] module_id=MOD-RSC_capability_passport | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

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

import hashlib
import hmac
import json
import logging
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

_log = logging.getLogger(__name__)

PASSPORTS_DIR = REPO_ROOT / "data" / "brain" / "passports"

# 默认开发环境签名密钥（生产环境应通过环境变量 ZEPHYR_PASSPORT_SIGNING_KEY 覆盖）
_DEFAULT_SIGNING_KEY = b"zephyr-passport-dev-key-v1"


class TamperError(Exception):
    """护照篡改异常 — 签名验证失败或无签名字段时抛出。"""
    pass


def _get_signing_key() -> bytes:
    """获取护照签名密钥（HMAC-SHA256）。

    优先从环境变量 CAPABILITY_PASSPORT_KEY 读取；未设置时使用默认开发密钥。
    """
    env_key = os.environ.get("CAPABILITY_PASSPORT_KEY")
    if env_key:
        return env_key.encode("utf-8")
    return _DEFAULT_SIGNING_KEY


def _compute_signature(data: dict) -> str:
    """计算护照数据的 HMAC-SHA256 签名。

    签名覆盖除 "signature" 字段外的所有字段，确保任何字段篡改都会导致签名失效。
    """
    payload = {k: v for k, v in data.items() if k != "signature"}
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hmac.new(_get_signing_key(), canonical.encode("utf-8"), hashlib.sha256).hexdigest()

DEPTH_THRESHOLDS: dict[str, float] = {
    # 原 9 能力（保留阈值）
    "task_classification": 0.60,
    "tag_completion": 0.55,
    "summary_extraction": 0.55,
    "naming_suggest": 0.50,
    "anomaly_triage": 0.50,
    "code_fix": 0.60,
    "refactor": 0.55,
    "code_generate": 0.55,
    "dead_code_removal": 0.55,
    # v3.0.5 新增 21 能力（含 context_management；code_edit_precision 与 code_fix 同阈值；
    # code_fix 为兼容保留——题库已统一用 code_edit_precision，但 _compute_metrics 仍引用）
    "code_edit_precision": 0.60,
    "ambiguity_detect": 0.65,
    "architecture_design": 0.55,
    "circular_dependency_detect": 0.55,
    "context_consistency": 0.55,
    "cross_file_refactor": 0.55,
    "dependency_ordering": 0.55,
    "dependency_trace": 0.55,
    "error_recovery": 0.55,
    "hallucination_detect": 0.55,
    "impact_analysis": 0.65,
    "incremental_execution": 0.55,
    "long_context_recall": 0.55,
    "parallel_planning": 0.55,
    "rollback_boundary_design": 0.55,
    "rule_comprehension": 0.55,
    "safety_judgment": 0.55,
    "self_review": 0.55,
    "task_decomposition": 0.55,
    "tool_selection": 0.55,
    "context_management": 0.55,
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
    time_weight_avg: float = 1.0  # v3.0.5: 平均时间折扣系数（便于审计）
    samples_per_case: int = 1  # P1-2: 每题采样次数（默认 1=单次, 5=统计显著性）


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
        data = self.to_dict()
        data["signature"] = _compute_signature(data)
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        _log.info("CapabilityPassport saved: %s", path)
        return path

    @staticmethod
    def load(model_id: str, verify: bool = False) -> CapabilityPassport | None:
        safe_id = model_id.replace(":", "_").replace("/", "_")
        path = PASSPORTS_DIR / f"{safe_id}.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if verify:
                signature = data.get("signature")
                if not signature:
                    raise TamperError("无签名字段")
                expected = _compute_signature(data)
                if not hmac.compare_digest(signature, expected):
                    raise TamperError("签名验证失败")
            return CapabilityPassport._from_dict(data)
        except TamperError:
            raise
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
