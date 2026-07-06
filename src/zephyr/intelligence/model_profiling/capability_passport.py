# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] zephyr.intelligence.model_profiling.capability_passport
# [DOMAIN] D_INTELLIGENCE
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
# [TTL] permanent

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
from zephyr.shared.io.serialization import dumps

import hashlib
import hmac
import json
import logging
import os
from dataclasses import asdict, dataclass, field, fields as _dc_fields
from pathlib import Path
from typing import Any
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
from zephyr.shared.security.secrets import get_secret_or_default

_log = logging.getLogger(__name__)

PASSPORTS_DIR = REPO_ROOT / "data" / "brain" / "passports"
QUICK_PROFILES_DIR = REPO_ROOT / "data" / "brain" / "quick_profiles"

# 默认开发环境签名密钥（生产环境应通过环境变量 ZEPHYR_PASSPORT_SIGNING_KEY 覆盖）
_DEFAULT_SIGNING_KEY = b"zephyr-passport-dev-key-v1"


class TamperError(Exception):
    """护照篡改异常 — 签名验证失败或无签名字段时抛出。"""
    pass


def _get_signing_key() -> bytes:
    """获取护照签名密钥（HMAC-SHA256）。

    优先从环境变量 CAPABILITY_PASSPORT_KEY 读取；未设置时使用默认开发密钥。
    """
    env_key = get_secret_or_default("CAPABILITY_PASSPORT_KEY", "")
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


# ── 5.147.5: 版本兼容性修复 ──────────────────────────────────────────
# 修复 `asdict() + **data.get(...)` 模式在 schema 演化时的 TypeError 缺陷：
#   - 旧 JSON 含已删除字段 → TypeError: unexpected keyword argument
#   - 字段重命名 → 旧名透传引发 TypeError
# 方案：在 `**data.get("xxx", {})` 处用 `_filter_dataclass_fields` 过滤无效键；
#       仅保留目标 dataclass 实际声明的字段，多余键丢弃并记录 debug 日志。

_CURRENT_PASSPORT_VERSION: str = "1.0.0"


def _filter_dataclass_fields(cls: type, data: dict | None) -> dict:
    """过滤 dict，仅保留目标 dataclass 实际声明的字段。

    用于 `_from_dict` 中 `**data.get("xxx", {})` 的版本兼容：
    旧 JSON 中已删除/重命名的字段会被静默丢弃，避免 TypeError。
    新字段缺失时由 dataclass 默认值兜底。
    """
    if not data:
        return {}
    valid_names = {f.name for f in _dc_fields(cls)}
    filtered = {k: v for k, v in data.items() if k in valid_names}
    dropped = set(data.keys()) - valid_names
    if dropped:
        _log.debug(
            "passport version_compat: %s dropped unknown fields %s",
            cls.__name__, dropped,
        )
    return filtered


def _migrate_passport_data(data: dict) -> dict:
    """根据 passport_version 执行版本迁移钩子。

    当前为占位实现——version==_CURRENT_PASSPORT_VERSION 时直接返回。
    未来若 schema 发生破坏性变更，在此追加 `if version < "x.y.z":` 分支
    将旧字段映射到新字段，确保旧 JSON 可向前兼容加载。
    """
    version = data.get("passport_version", _CURRENT_PASSPORT_VERSION)
    if version != _CURRENT_PASSPORT_VERSION:
        _log.debug(
            "passport version_migration: loaded version=%s, current=%s "
            "(no migration registered)",
            version, _CURRENT_PASSPORT_VERSION,
        )
    return data

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
    # v2.3.2: Tool 轴能力 (ROADMAP-02 新增，补全阈值)
    "function_calling": 0.55,
    "tool_chaining": 0.55,
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
class CostBreakdown:
    """P2: 成本明细 — 从 _all_tokens/_all_latencies_ms 派生。

    成本是岗位匹配的一个维度，不是一票否决 (D-MCE-07)。
    claude 贵但必要时仍可用；本地模型成本≈0。

    设计原则:
        - 成本是维度非硬门 (D-MCE-07): claude 贵但必要时仍可用
        - 本地模型 cost_usd ≈ 0 (硬件折旧另算)
        - 云端模型按 API 定价 (provider_data.py DEFAULT_PROVIDERS)
        - cost_score: 0-1, 越高越好 (越便宜); local 默认 1.0
    """
    deployment_mode: str = "local"      # local / api
    provider: str = "local"             # zhipu/deepseek/openai_azure/anthropic/local
    total_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    price_per_1k_input: float = 0.0     # USD per 1K input tokens
    price_per_1k_output: float = 0.0    # USD per 1K output tokens
    estimated_cost_usd: float = 0.0     # 总估算成本 (USD)

    @property
    def cost_score(self) -> float:
        """成本得分 (0-1, 越高越好 = 越便宜)。

        策略 (D-MCE-07: 成本是维度非硬门):
            - local: 1.0 (成本≈0)
            - api: 按 estimated_cost_usd 衰减
              cost <= 0.01 USD → 1.0 (近似免费, 如 zhipu 免费档)
              cost >= 1.0 USD  → 0.0 (昂贵)
              中间线性
        """
        if self.deployment_mode == "local":
            return 1.0
        cost = self.estimated_cost_usd
        if cost <= 0.01:
            return 1.0
        if cost >= 1.0:
            return 0.0
        return round(1.0 - (cost - 0.01) / 0.99, 3)


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
    cost: CostBreakdown = field(default_factory=CostBreakdown)
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
        safe_id = self.model_id.replace(":", "_").replace("/", "_").replace("\\", "_")
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
            _log.warning("Failed to load passport for %s: %s", model_id, exc, exc_info=True)
            return None

    @staticmethod
    def _from_dict(data: dict) -> CapabilityPassport:
        # 5.147.5: 版本兼容——过滤旧 JSON 中的已删除/重命名字段，避免 TypeError
        data = _migrate_passport_data(data)
        depth_caps: dict[str, DepthCapabilityResult] = {}
        for cap_name, cap_data in (data.get("depth", {}) or {}).get("capabilities", {}).items():
            depth_caps[cap_name] = DepthCapabilityResult(
                **_filter_dataclass_fields(DepthCapabilityResult, cap_data)
            )

        return CapabilityPassport(
            passport_version=data.get("passport_version", _CURRENT_PASSPORT_VERSION),
            model_id=data.get("model_id", ""),
            exam_timestamp=data.get("exam_timestamp", ""),
            exam_duration_seconds=data.get("exam_duration_seconds", 0.0),
            git_commit=data.get("git_commit", ""),
            overall_grade=data.get("overall_grade", "F"),
            overall_score=data.get("overall_score", 0.0),
            breadth=BreadthResult(**_filter_dataclass_fields(BreadthResult, data.get("breadth"))),
            depth=DepthResult(
                overall_score=data.get("depth", {}).get("overall_score", 0.0),
                capabilities=depth_caps,
            ),
            speed=SpeedResult(**_filter_dataclass_fields(SpeedResult, data.get("speed"))),
            hallucination=HallucinationResult(
                **_filter_dataclass_fields(HallucinationResult, data.get("hallucination"))
            ),
            drift=DriftResult(**_filter_dataclass_fields(DriftResult, data.get("drift"))),
            cost=CostBreakdown(**_filter_dataclass_fields(CostBreakdown, data.get("cost"))),
            recommendations=Recommendations(
                **_filter_dataclass_fields(Recommendations, data.get("recommendations"))
            ),
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


# ══════════════════════════════════════════════════════════
# P2: 岗位匹配 + 快速画像数据结构
# ══════════════════════════════════════════════════════════


def compute_grade_simple(score: float) -> str:
    """P2: 五级粗粒度能力分级 A/B/C/D/F，用于岗位匹配。

    比 compute_grade 更粗，避免 0.612 vs 0.618 的过拟合：
        A (>=0.75)  精通，可独立担当
        B (>=0.60)  熟练，可主力
        C (>=0.45)  合格，需监督
        D (>=0.30)  初级，需指导
        F (<0.30)   不胜任

    设计原则: 岗位匹配用粗级足够，能力轮廓 > 每题精度。
    """
    if score >= 0.75:
        return "A"
    elif score >= 0.60:
        return "B"
    elif score >= 0.45:
        return "C"
    elif score >= 0.30:
        return "D"
    else:
        return "F"


# 能力分级 → 数值映射（用于 required 阈值比较，越高越好）
GRADE_LEVEL: dict[str, int] = {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}


@dataclass
class JobRecommendation:
    """P2: 岗位推荐结果。

    一个模型对一个岗位的匹配评估。
    """
    job_id: str                            # 岗位标识 snake_case
    job_title: str                         # 岗位中文名称
    match_score: float = 0.0               # 匹配度 0-1
    qualified: bool = False                # 是否满足全部 required 能力
    hallucination_passed: bool = True      # 是否通过幻觉门
    missing_required: list[str] = field(default_factory=list)  # 未达 required 的能力
    bonus_summary: str = ""                # bonus 能力命中摘要
    description: str = ""                  # 岗位职责描述


@dataclass
class HallucinationBreakdown:
    """P2: 幻觉率多维细分（参考 ChatGPT 建议 + 业界实践）。

    任何模型都有幻觉，Claude 也不例外，只是高低问题。
    幻觉率正常评分（不硬门），但在岗位匹配时权重较高。

    九维细分（每维 0-1，越高 = 越严重）：
        fabrication          事实编造（编造不存在的 API/函数/文件）
        inconsistency        输出不一致（同题两次回答差异大）
        refusal              过度拒绝（能答的拒答）
        overclaim            过度声称（声称做了没做的事）
        context_drift        上下文漂移（两次输出键集不同 = 忘记指令结构）
        source_confusion     来源混淆（把 A 文件内容归给 B）
        instruction_drift    指令偏离（输出结构不符合 expected_structure_keys）
        format_hallucination 格式幻觉（字段值类型异常，如 list 字段给了 stringified JSON）
        quantity_hallucination 数量幻觉（输出集合异常膨胀，list/dict 长度超阈值）
    """
    fabrication: float = 0.0
    inconsistency: float = 0.0
    refusal: float = 0.0
    overclaim: float = 0.0
    context_drift: float = 0.0
    source_confusion: float = 0.0
    instruction_drift: float = 0.0
    format_hallucination: float = 0.0
    quantity_hallucination: float = 0.0

    @property
    def overall_rate(self) -> float:
        """综合幻觉率 = 九维均值（0-1，越低越好）。"""
        vals = [self.fabrication, self.inconsistency, self.refusal,
                self.overclaim, self.context_drift, self.source_confusion,
                self.instruction_drift, self.format_hallucination,
                self.quantity_hallucination]
        return round(sum(vals) / len(vals), 3) if vals else 0.0

    @property
    def hallucination_score(self) -> float:
        """幻觉轴得分（0-1，越高越好 = 1 - overall_rate）。用于五轴综合分。"""
        return round(1.0 - self.overall_rate, 3)


@dataclass
class QuickProfile:
    """P2: 快速能力画像 — Quick Mode 输出。

    比 CapabilityPassport 精简，面向"岗位匹配"而非"精确评分"：
        - 29 能力的粗分级 A/B/C/D/F（雷达图轮廓）
        - 幻觉率六维细分（正常评分，非硬门；岗位匹配时权重高）
        - Top3 推荐岗位
        - 考试耗时

    设计原则: 幻觉率正常评分，任何模型都有幻觉，只是高低问题。
              未来岗位匹配时幻觉率多考虑，但现在不做硬门槛。
    """
    model_id: str = ""
    exam_mode: str = "quick"               # quick/standard/deep
    exam_timestamp: str = ""
    exam_duration_seconds: float = 0.0
    # 能力轮廓（29 项）
    capability_grades: dict[str, str] = field(default_factory=dict)   # {cap_name: "A"|"B"|...}
    capability_scores: dict[str, float] = field(default_factory=dict)  # 原始分 0-1
    # 幻觉轴（六维细分，正常评分）
    hallucination: HallucinationBreakdown = field(default_factory=HallucinationBreakdown)
    # 成本轴（D-MCE-07: 成本是维度非硬门）
    cost: CostBreakdown = field(default_factory=CostBreakdown)
    # 综合分级
    overall_grade: str = "F"
    overall_score: float = 0.0
    # 岗位推荐（Top3，按 match_score 降序）
    recommendations: list[JobRecommendation] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def save(self) -> Path:
        """持久化 QuickProfile 到 data/brain/quick_profiles/{model_id}.json。

        与 CapabilityPassport.save() 不同, QuickProfile 不带 HMAC 签名——
        它是轻量级画像视图, 非任务门控真源。
        """
        QUICK_PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        safe_id = self.model_id.replace(":", "_").replace("/", "_")
        path = QUICK_PROFILES_DIR / f"{safe_id}.json"
        path.write_text(
            dumps(asdict(self), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        _log.info("QuickProfile saved: %s", path)
        return path

    @staticmethod
    def load(model_id: str) -> QuickProfile | None:
        """从磁盘加载 QuickProfile, 文件不存在返回 None。"""
        safe_id = model_id.replace(":", "_").replace("/", "_")
        path = QUICK_PROFILES_DIR / f"{safe_id}.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return QuickProfile._from_dict(data)
        except Exception as exc:
            _log.warning("Failed to load QuickProfile for %s: %s", model_id, exc, exc_info=True)
            return None

    @staticmethod
    def _from_dict(data: dict) -> QuickProfile:
        # 5.147.5: 版本兼容——过滤旧 JSON 中的已删除/重命名字段
        return QuickProfile(
            model_id=data.get("model_id", ""),
            exam_mode=data.get("exam_mode", "quick"),
            exam_timestamp=data.get("exam_timestamp", ""),
            exam_duration_seconds=data.get("exam_duration_seconds", 0.0),
            capability_grades=data.get("capability_grades", {}),
            capability_scores=data.get("capability_scores", {}),
            hallucination=HallucinationBreakdown(
                **_filter_dataclass_fields(HallucinationBreakdown, data.get("hallucination"))
            ),
            cost=CostBreakdown(**_filter_dataclass_fields(CostBreakdown, data.get("cost"))),
            overall_grade=data.get("overall_grade", "F"),
            overall_score=data.get("overall_score", 0.0),
            recommendations=[
                JobRecommendation(**_filter_dataclass_fields(JobRecommendation, r))
                if isinstance(r, dict) else r
                for r in data.get("recommendations", [])
            ],
            notes=data.get("notes", []),
        )
