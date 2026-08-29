# [BLUEPRINT] MOD-INF-053 | docs/03_modules/MOD-INF-053/
# [MODULE] zephyr.security.ops.incident_pipeline
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.orchestrator.resilience.failure_matcher; zephyr.security.security_event_bus; zephyr.shared.io.paths; zephyr.shared.utils.time_utils
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 行为类故障永不触发自动修复（Block+Alert only）;语义类修复必经LLM Bridge（LSG闸）不直通模板化;每次修复动作自动写知识库记录（append-only，记录优先不做匹配）;未经审批的白名单豁免0条;豁免目标必须在GOV-AI-001注册表在册且非Immutable Core（注册表不可读fail-closed拒批）;故障模式库冷启动导入幂等（库非空不重复导）
# [MODIFY-GUARD] 16_ai_security_ops.md §4.3; 12_reflexion_multi_agent.md §4.4
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] IncidentPipelineError(ZA-SC-0035);FixPatternStoreError(ZA-SC-0036)
# [TESTS] tests/security/ops/test_incident_pipeline.py
# [A_module] module_id=MOD-INF-053 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""统一事件流消费 → 诊断 → auto_fix_engine 三通道判决管线（16号文 §4.3 P1-1~P1-4；12号文 §4.4 涌现介入接线）。

目的：Detect 已贯通（MOD-SEC-EVENTBUS 统一事件目录），闭环断点在「连」。
本管线把四环串成自动流：

1. **事件→诊断（P1-1）**：消费统一事件 schema（``SecurityEvent``），经
   ``failure_matcher``（MOD-INF-039，Diagnose 入口）生成诊断——FailureMatcher
   九类错误分类决定三通道归类，FailurePatternMatcher 生成纠正建议
   （FailureDiagnosis 语义）。anomaly_diagnoser 为回测域专用件，安全事件流
   的 Diagnose 入口按 16号文 §4.1 登记口径为 failure_matcher。
2. **诊断→三通道判决（P1-2，不变量）**：
   - 结构类（schema/import/依赖等确定性故障）→ 直通模板化修复通道；
   - 语义类（逻辑/未知等需推理故障）→ LLM Bridge 修复通道（``llm_fix``，
     必经 LSG 闸——09号文集成口径，记录 ``lsg_gate=True`` 留痕），
     MUST NOT 直通模板化；
   - 行为类（串谋/涌现/记忆投毒/越权）→ Block+Alert，**永不自动修复**
     （MOD-INF-031 行为审计 RED 铁律），MUST 走 escalation 落盘。
   不可自动修的判决（修复失败/引擎异常/行为类）一律走 escalation 通道落盘。
3. **知识库落盘（P1-3）**：``data/fix_patterns/pattern_index.yaml``
   （REG-AFX-PATTERN-001）+ ``_fixer-registry.yaml``（MOD-INF-031 蓝图登记项）。
   **记录优先，不做匹配**——每次修复动作自动向库写一条记录，append-only。
   故障模式库冷启动：库（``patterns`` 节）为空时从 failure_matcher
   （MOD-INF-039）内置故障模式导入冷启动内容，幂等（非空不重复导），
   导入事件落盘留痕（``cold_start_imports.jsonl``）。
   **16号文 Q2（先建库还是先建闭环）关闭**——按候选方案「并行冷启动、
   记录优先」落地：闭环照跑、记录优先写库，冷启动导入并行兜底。
4. **白名单审批（P1-4）**：保护路径/豁免白名单变更走 human_gated 审批
   （GOV-AI-001 实质对接——豁免目标 MUST 在
   ``ai_autonomy_authority_registry.yaml`` 权限注册表在册且非 Immutable
   Core，注册表不可读/缺失/解析失败 fail-closed 一律拒批），审批与豁免
   授予/拒绝全部留痕；不变量——未经审批的豁免 0 条。
5. **涌现介入接线（12号文 §4.1/§4.4，不新建检测节点，消费侧接线）**：
   消费 MOD-RK-14 涌现 is_breached 告警（threat=emergence 且 severity≥high），
   产人工介入处置工单，SOP 状态机：告警→工单（ticket_open）→人审
   （human_review）→关闭（closed，必须人审 actor）。

边界：本管线只做消费与串联——不改动 failure_matcher / auto_fix_engine /
security_event_bus / MOD-RK-14 任何本体逻辑（16号文 §5 第 6 条；12号文 §4.1）。
修复引擎以协议注入（默认工厂懒加载 AutoFixEngine），LLM/DB/网络不在本模块。
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from collections.abc import Callable, Iterator, Mapping
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Final, Protocol

import yaml

from zephyr.orchestrator.resilience import failure_matcher as _failure_matcher_module
from zephyr.orchestrator.resilience.failure_matcher import (
    FailureCategory,
    FailureMatcher,
    FailurePatternMatcher,
)
from zephyr.security.security_event_bus import (
    SecurityEvent,
    Severity,
    ThreatCategory,
)
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_iso

logger = logging.getLogger(__name__)

__all__: Final = [
    "COLD_START_LEDGER_FILENAME",
    "DEFAULT_AUTHORITY_REGISTRY_PATH",
    "FIXER_REGISTRY_FILENAME",
    "PATTERN_INDEX_FILENAME",
    "ChannelDecision",
    "EscalationSink",
    "FaultClass",
    "FixEngineProtocol",
    "FixPatternStore",
    "FixPatternStoreError",
    "IncidentPipeline",
    "IncidentPipelineError",
    "IncidentRecord",
    "InterventionStatus",
    "InterventionTicket",
    "InterventionTicketStore",
    "PipelineConfig",
    "PipelineDiagnosis",
    "WhitelistApprovalGate",
]

SCHEMA_VERSION: Final[str] = "1.0"
PATTERN_INDEX_FILENAME: Final[str] = "pattern_index.yaml"
FIXER_REGISTRY_FILENAME: Final[str] = "_fixer-registry.yaml"
COLD_START_LEDGER_FILENAME: Final[str] = "cold_start_imports.jsonl"
# 知识库 yaml 治理锚定头（B_yaml 6 字段——重写文件时保持锚定不丢失）
_KB_HEADER: Final[str] = (
    "# --- 治理锚定 ---\n"
    "# blueprint: MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §14\n"
    "# module_id: MOD-INF-053\n"
    "# stability: evolving\n"
    "# safety_level: H\n"
    "# ai_autonomy: ai_modifiable\n"
    "# ttl: permanent\n"
    "# --- 治理锚定结束 ---\n"
)
DEFAULT_STORE_DIR: Final[Path] = REPO_ROOT / "data" / "fix_patterns"
DEFAULT_RUNTIME_DIR: Final[Path] = REPO_ROOT / ".runtime" / "security_ops"
# GOV-AI-001 AI 自治权限注册表（白名单豁免在册校验的唯一真源）
DEFAULT_AUTHORITY_REGISTRY_PATH: Final[Path] = (
    REPO_ROOT
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "ai_autonomy_authority_registry.yaml"
)
SEMANTIC_ACTION_TYPE: Final[str] = "llm_fix"

_BEHAVIORAL_THREATS: Final[frozenset[ThreatCategory]] = frozenset(
    {
        ThreatCategory.COLLUSION,
        ThreatCategory.EMERGENCE,
        ThreatCategory.MEMORY_POISONING,
        ThreatCategory.PRIVILEGE_VIOLATION,
    }
)
_STRUCTURAL_CATEGORIES: Final[frozenset[FailureCategory]] = frozenset(
    {
        FailureCategory.SYNTAX,
        FailureCategory.DEPENDENCY,
        FailureCategory.VALIDATION,
    }
)
# 结构类故障类别 → 模板化修复通道 action_type（MOD-INF-031 _find_fixer 口径）
_STRUCTURAL_ACTION_TYPES: Final[dict[FailureCategory, str]] = {
    FailureCategory.SYNTAX: "import_fix",
    FailureCategory.DEPENDENCY: "dep_version_fix",
    FailureCategory.VALIDATION: "config_fix",
}


class IncidentPipelineError(Exception):
    """ZA-SC-0035: 管线操作非法（未知工单/非法状态迁移/审批缺actor/非涌现告警）。"""

    error_code = "ZA-SC-0035"


class FixPatternStoreError(Exception):
    """ZA-SC-0036: 修复策略知识库 schema 校验失败。"""

    error_code = "ZA-SC-0036"


class FaultClass(str, Enum):
    """三通道故障归类（16号文 §2.1-3 / MOD-INF-031 三通道口径）。"""

    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    BEHAVIORAL = "behavioral"


class ChannelDecision(str, Enum):
    """三通道判决结果。"""

    AUTO_TEMPLATE = "auto_template"
    AUTO_LLM = "auto_llm"
    BLOCK_ALERT = "block_alert"


_CHANNEL_BY_FAULT_CLASS: Final[dict[FaultClass, ChannelDecision]] = {
    FaultClass.STRUCTURAL: ChannelDecision.AUTO_TEMPLATE,
    FaultClass.SEMANTIC: ChannelDecision.AUTO_LLM,
    FaultClass.BEHAVIORAL: ChannelDecision.BLOCK_ALERT,
}


class InterventionStatus(str, Enum):
    """人工介入处置工单状态机（告警→工单→人审→关闭）。"""

    TICKET_OPEN = "ticket_open"
    HUMAN_REVIEW = "human_review"
    CLOSED = "closed"


_LEGAL_TICKET_TRANSITIONS: Final[dict[InterventionStatus, frozenset[InterventionStatus]]] = {
    InterventionStatus.TICKET_OPEN: frozenset({InterventionStatus.HUMAN_REVIEW}),
    InterventionStatus.HUMAN_REVIEW: frozenset({InterventionStatus.CLOSED}),
    InterventionStatus.CLOSED: frozenset(),
}


class FixEngineProtocol(Protocol):
    """修复引擎协议（AutoFixEngine 签名子集——本管线只消费不改结构）。"""

    def fix(self, action_type: str, target: str, dry_run: bool = False) -> Any: ...


@dataclass(frozen=True)
class PipelineDiagnosis:
    """管线诊断记录（事件→FailureDiagnosis 语义落盘）。"""

    event_id: str
    fault_class: FaultClass
    category: str
    pattern_name: str
    severity: str
    suggestion: str
    confidence: float


@dataclass(frozen=True)
class IncidentRecord:
    """单事件全链路留痕（事件→诊断→通道判决→修复/升级→知识库）。"""

    incident_id: str
    ts: str
    event_id: str
    fault_class: FaultClass
    channel: ChannelDecision
    diagnosis: PipelineDiagnosis
    action_id: str = ""
    action_type: str = ""
    action_status: str = ""
    escalated: bool = False
    escalation_id: str = ""
    alert_sent: bool = False
    kb_record_id: str = ""


@dataclass(frozen=True)
class PipelineConfig:
    """管线配置（参数收敛 dataclass，默认路径 = 生产落点）。"""

    store_dir: Path = DEFAULT_STORE_DIR
    runtime_dir: Path = DEFAULT_RUNTIME_DIR
    dry_run_fix: bool = False
    incidents_filename: str = "incidents.jsonl"
    escalations_filename: str = "escalations.jsonl"
    tickets_filename: str = "intervention_tickets.jsonl"
    whitelist_ledger_filename: str = "whitelist_approvals.jsonl"
    authority_registry_path: Path = DEFAULT_AUTHORITY_REGISTRY_PATH
    emergence_min_severity: Severity = Severity.HIGH


@dataclass(frozen=True)
class InterventionTicket:
    """人工介入处置工单（12号文 §3.7 SOP：三源明细→裁定降级或暂停）。"""

    ticket_id: str
    event_id: str
    detector: str
    risk_score: float
    detector_state: str
    severity: str
    source_refs: tuple[str, str, str]
    status: InterventionStatus
    opened_ts: str
    history: tuple[dict[str, str], ...] = field(default_factory=tuple)


def _append_jsonl(path: Path, record: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _status_value(status: Any) -> str:
    return str(getattr(status, "value", status))


def _serialize_incident(record: IncidentRecord) -> dict[str, Any]:
    blob = asdict(record)
    blob["fault_class"] = record.fault_class.value
    blob["channel"] = record.channel.value
    blob["diagnosis"]["fault_class"] = record.diagnosis.fault_class.value
    return blob


def _builtin_failure_patterns() -> list[dict[str, Any]]:
    """读取 failure_matcher（MOD-INF-039）内置故障模式（只读消费模块级模式表，不改本体逻辑）。

    双件全量导出：FailurePatternMatcher 命名模式（``_FAILURE_PATTERNS``）+
    FailureMatcher 九类分类模式（``_CATEGORY_PATTERNS``），以 ``matcher`` 字段区分来源。
    """
    patterns: list[dict[str, Any]] = []
    for pat in getattr(_failure_matcher_module, "_FAILURE_PATTERNS", None) or []:
        patterns.append(
            {
                "matcher": "FailurePatternMatcher",
                "pattern_name": str(pat.get("name", "")),
                "severity": str(pat.get("severity", "")),
                "regex": str(pat.get("regex", "")),
                "suggestion": str(pat.get("suggestion", "")),
                "automatic_recovery": bool(pat.get("automatic_recovery", False)),
            }
        )
    for cat, regex, probability, suggestion in (
        getattr(_failure_matcher_module, "_CATEGORY_PATTERNS", None) or []
    ):
        patterns.append(
            {
                "matcher": "FailureMatcher",
                "pattern_name": f"category:{getattr(cat, 'value', cat)}",
                "category": str(getattr(cat, "value", cat)),
                "regex": str(regex),
                "probability": float(probability),
                "suggestion": str(suggestion),
            }
        )
    return patterns


class FixPatternStore:
    """修复策略知识库（``data/fix_patterns/``，记录优先，不做匹配；append-only）。

    - ``pattern_index.yaml``（REG-AFX-PATTERN-001）：每次修复动作自动写一条
      修复记录（``records`` 列表只增不改）；``patterns`` 节为故障模式库冷启动
      内容（failure_matcher 内置模式导出，``ensure_cold_start_patterns``）。
    - ``_fixer-registry.yaml``（MOD-INF-031 蓝图登记项）：三通道修复器注册表，
      冷启动落盘三通道条目（结构→模板化 / 语义→LLM Bridge 必经 LSG / 行为→
      Block+Alert 永不自动修复）。
    两文件写入前 MUST 过 schema 校验（``FixPatternStoreError``），读回同样校验。

    16号文 Q2（先建库还是先建闭环）关闭——按候选方案「并行冷启动、记录优先」
    落地：库为空时导入冷启动内容，幂等（非空不重复导），导入事件落盘留痕。
    """

    def __init__(self, store_dir: Path) -> None:
        self._store_dir = store_dir
        self._index_path = store_dir / PATTERN_INDEX_FILENAME
        self._registry_path = store_dir / FIXER_REGISTRY_FILENAME

    @property
    def index_path(self) -> Path:
        return self._index_path

    @property
    def registry_path(self) -> Path:
        return self._registry_path

    def ensure_files(self) -> None:
        """冷启动落盘——文件不存在则以空记录集/三通道注册表创建。"""
        self._store_dir.mkdir(parents=True, exist_ok=True)
        if not self._index_path.exists():
            self._write_yaml(
                self._index_path,
                {"schema_version": SCHEMA_VERSION, "kind": "fix_pattern_index", "records": []},
            )
        if not self._registry_path.exists():
            self._write_yaml(
                self._registry_path,
                {
                    "schema_version": SCHEMA_VERSION,
                    "kind": "fixer_registry",
                    "fixers": [
                        {
                            "fixer_id": "template_channel",
                            "channel": ChannelDecision.AUTO_TEMPLATE.value,
                            "level": "l1_rule",
                            "fault_class": FaultClass.STRUCTURAL.value,
                            "description": "结构类直通模板化修复（100% 确定）",
                        },
                        {
                            "fixer_id": "llm_bridge_channel",
                            "channel": ChannelDecision.AUTO_LLM.value,
                            "level": "l2_llm",
                            "fault_class": FaultClass.SEMANTIC.value,
                            "description": "语义类过 LLM Bridge 修复（必经 LSG 闸）",
                        },
                        {
                            "fixer_id": "block_alert_channel",
                            "channel": ChannelDecision.BLOCK_ALERT.value,
                            "level": "none",
                            "fault_class": FaultClass.BEHAVIORAL.value,
                            "description": "行为类 Block+Alert（永不自动修复）",
                        },
                    ],
                },
            )

    def append_fix_record(self, record: Mapping[str, Any]) -> str:
        """每次修复动作自动向库写一条记录（append-only；写入前 schema 校验）。"""
        self.ensure_files()
        record_id = str(record.get("record_id") or uuid.uuid4().hex[:12])
        blob = dict(record)
        blob["record_id"] = record_id
        index = self.read_pattern_index()
        index["records"].append(blob)
        self.validate_pattern_index(index)
        self._write_yaml(self._index_path, index)
        return record_id

    def ensure_cold_start_patterns(self) -> int:
        """故障模式库冷启动：``patterns`` 节为空时导入 failure_matcher 内置模式。

        幂等——``patterns`` 非空时不重复导（返回 0）；导入事件 append-only 落盘
        留痕（``cold_start_imports.jsonl``）。返回本次导入条数。
        """
        self.ensure_files()
        index = self.read_pattern_index()
        if index.get("patterns"):
            return 0
        builtin = _builtin_failure_patterns()
        if not builtin:
            return 0
        ts = now_iso()
        index["patterns"] = [
            {
                "record_id": f"coldstart-{pat['matcher']}:{pat['pattern_name']}",
                "ts": ts,
                "kind": "cold_start_pattern",
                "source": "failure_matcher",
                **pat,
            }
            for pat in builtin
        ]
        self.validate_pattern_index(index)
        self._write_yaml(self._index_path, index)
        _append_jsonl(
            self._store_dir / COLD_START_LEDGER_FILENAME,
            {
                "kind": "cold_start_import",
                "source": "zephyr.orchestrator.resilience.failure_matcher",
                "imported": len(builtin),
                "ts": ts,
            },
        )
        logger.info(
            "故障模式库冷启动导入 %d 条 failure_matcher 内置模式 → %s",
            len(builtin),
            self._index_path,
        )
        return len(builtin)

    def read_pattern_index(self) -> dict[str, Any]:
        self.ensure_files()
        with open(self._index_path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        self.validate_pattern_index(data)
        return data

    def read_fixer_registry(self) -> dict[str, Any]:
        self.ensure_files()
        with open(self._registry_path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        self.validate_fixer_registry(data)
        return data

    @staticmethod
    def validate_pattern_index(data: Mapping[str, Any]) -> None:
        if not isinstance(data, Mapping):
            raise FixPatternStoreError("pattern_index 顶层必须是 mapping")
        if not data.get("schema_version"):
            raise FixPatternStoreError("pattern_index 缺 schema_version")
        records = data.get("records")
        if not isinstance(records, list):
            raise FixPatternStoreError("pattern_index.records 必须是 list")
        for rec in records:
            if not isinstance(rec, Mapping) or not rec.get("record_id") or not rec.get("ts"):
                raise FixPatternStoreError("pattern_index.records 条目缺 record_id/ts")
        patterns = data.get("patterns")
        if patterns is not None:
            if not isinstance(patterns, list):
                raise FixPatternStoreError("pattern_index.patterns 必须是 list")
            for pat in patterns:
                if not isinstance(pat, Mapping) or not pat.get("record_id") or not pat.get("ts"):
                    raise FixPatternStoreError("pattern_index.patterns 条目缺 record_id/ts")

    @staticmethod
    def validate_fixer_registry(data: Mapping[str, Any]) -> None:
        if not isinstance(data, Mapping):
            raise FixPatternStoreError("fixer_registry 顶层必须是 mapping")
        if not data.get("schema_version"):
            raise FixPatternStoreError("fixer_registry 缺 schema_version")
        fixers = data.get("fixers")
        if not isinstance(fixers, list) or not fixers:
            raise FixPatternStoreError("fixer_registry.fixers 必须是非空 list")
        for fixer in fixers:
            if not isinstance(fixer, Mapping):
                raise FixPatternStoreError("fixer_registry.fixers 条目必须是 mapping")
            missing = {"fixer_id", "channel", "level", "fault_class"} - set(fixer)
            if missing:
                raise FixPatternStoreError(f"fixer_registry.fixers 条目缺字段: {sorted(missing)}")

    @staticmethod
    def _write_yaml(path: Path, data: Mapping[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(_KB_HEADER)
            yaml.safe_dump(dict(data), fh, allow_unicode=True, sort_keys=False)
        os.replace(tmp, path)


class EscalationSink:
    """不可自动修判决的 escalation 通道落盘（append-only JSONL）。"""

    def __init__(self, path: Path) -> None:
        self._path = path

    def escalate(self, entry: Mapping[str, Any]) -> str:
        escalation_id = str(entry.get("escalation_id") or uuid.uuid4().hex[:12])
        blob = dict(entry)
        blob["escalation_id"] = escalation_id
        blob.setdefault("ts", now_iso())
        _append_jsonl(self._path, blob)
        logger.warning("escalation 落盘: kind=%s escalation_id=%s", blob.get("kind", "?"), escalation_id)
        return escalation_id

    def entries(self) -> list[dict[str, Any]]:
        return _read_jsonl(self._path)


def _load_authority_registry(path: Path) -> Mapping[str, Any] | None:
    """读取 GOV-AI-001 权限注册表；不可读/解析失败/非 mapping 返回 None（调用方 fail-closed）。"""
    try:
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except (OSError, yaml.YAMLError):
        return None
    return data if isinstance(data, Mapping) else None


def _registry_permission_for(registry: Mapping[str, Any], path: str) -> str | None:
    """按 path 精确/目录前缀匹配注册表 ``permission_table`` 权限。

    返回命中的权限串；不在册返回 ``None``。多命中时只要含 Immutable 即返回之
    （取最严，immutable 目标豁免一律拒）。仅消费 ``path`` 字段——component-only
    条目（无 path）不做名字猜测匹配（组件名跨节重复，误匹配风险高）。
    """
    target = path.replace("\\", "/")
    while target.startswith("./"):
        target = target[2:]
    table = registry.get("permission_table")
    if not isinstance(table, Mapping):
        return None
    matched: list[str] = []
    for section in table.values():
        if not isinstance(section, list):
            continue
        for entry in section:
            if not isinstance(entry, Mapping):
                continue
            raw = entry.get("path")
            if not isinstance(raw, str):
                continue
            candidate = raw.replace("\\", "/").strip()
            if "/" not in candidate:
                continue  # 跳过「同上 子模块」「见 §2.9」「项目外 OS 级」等非路径登记
            if target == candidate.rstrip("/") or (
                candidate.endswith("/") and target.startswith(candidate)
            ):
                matched.append(str(entry.get("permission", "")))
    if not matched:
        return None
    for permission in matched:
        if "immutable" in permission.lower():
            return permission
    return matched[0]


class WhitelistApprovalGate:
    """保护路径/豁免白名单的 human_gated 审批闸（P1-4，GOV-AI-001 实质对接）。

    不变量：未经审批的豁免 0 条——``request_exemption`` 无有效 ``approval_id``
    MUST 拒绝并留痕（``exemption_denied``）；审批与授予全部 append-only 留痕。

    GOV-AI-001 实质对接：豁免目标 MUST 在 ``ai_autonomy_authority_registry.yaml``
    权限注册表在册（``path`` 精确或目录前缀匹配）且非 Immutable Core——
    immutable 目标豁免请求一律拒；注册表不可读/缺失/解析失败 fail-closed
    （一律拒批，``denial_reason=authority_registry_unavailable``）。
    """

    def __init__(self, ledger_path: Path, registry_path: Path | None = None) -> None:
        self._ledger_path = ledger_path
        self._registry_path = (
            registry_path if registry_path is not None else DEFAULT_AUTHORITY_REGISTRY_PATH
        )

    @property
    def authority_registry_path(self) -> Path:
        return self._registry_path

    def approve(self, approval_id: str, *, approver: str, scope: str, reason: str) -> None:
        """人工审批登记（human_gated——approver 为空即拒，fail-closed）。"""
        if not approval_id or not approver or not scope:
            raise IncidentPipelineError("白名单审批 MUST 含 approval_id/approver/scope")
        _append_jsonl(
            self._ledger_path,
            {
                "kind": "approval",
                "approval_id": approval_id,
                "approver": approver,
                "scope": scope,
                "reason": reason,
                "ts": now_iso(),
            },
        )

    def request_exemption(self, *, path: str, reason: str, approval_id: str = "") -> bool:
        """申请豁免：目标在册且非 Immutable Core 且存在匹配审批时授予；否则拒绝留痕。"""
        denial_reason = self._registry_denial_reason(path)
        approved = (
            not denial_reason
            and bool(approval_id)
            and any(
                e.get("kind") == "approval" and e.get("approval_id") == approval_id
                for e in self.entries()
            )
        )
        kind = "exemption_granted" if approved else "exemption_denied"
        entry: dict[str, Any] = {
            "kind": kind,
            "path": path,
            "reason": reason,
            "approval_id": approval_id,
            "ts": now_iso(),
        }
        if denial_reason:
            entry["denial_reason"] = denial_reason
        _append_jsonl(self._ledger_path, entry)
        return approved

    def _registry_denial_reason(self, path: str) -> str:
        """GOV-AI-001 在册校验：返回拒绝原因（空串=通过）；注册表不可读 fail-closed。"""
        registry = _load_authority_registry(self._registry_path)
        if registry is None:
            return "authority_registry_unavailable"
        permission = _registry_permission_for(registry, path)
        if permission is None:
            return "target_not_in_authority_registry"
        if "immutable" in permission.lower():
            return "immutable_core_target"
        return ""

    def entries(self) -> list[dict[str, Any]]:
        return _read_jsonl(self._ledger_path)


class InterventionTicketStore:
    """人工介入处置工单存储（append-only 快照 JSONL，同 ticket 最新快照为准）。"""

    def __init__(self, path: Path) -> None:
        self._path = path

    def save(self, ticket: InterventionTicket) -> None:
        blob = asdict(ticket)
        blob["status"] = ticket.status.value
        blob["source_refs"] = list(ticket.source_refs)
        blob["history"] = [dict(h) for h in ticket.history]
        _append_jsonl(self._path, blob)

    def get(self, ticket_id: str) -> InterventionTicket | None:
        found: InterventionTicket | None = None
        for ticket in self._iter_all():
            if ticket.ticket_id == ticket_id:
                found = ticket
        return found

    def find_by_event(self, event_id: str) -> InterventionTicket | None:
        found: InterventionTicket | None = None
        for ticket in self._iter_all():
            if ticket.event_id == event_id:
                found = ticket
        return found

    def tickets(self) -> list[InterventionTicket]:
        latest: dict[str, InterventionTicket] = {}
        for ticket in self._iter_all():
            latest[ticket.ticket_id] = ticket
        return list(latest.values())

    def _iter_all(self) -> Iterator[InterventionTicket]:
        for blob in _read_jsonl(self._path):
            yield InterventionTicket(
                ticket_id=blob["ticket_id"],
                event_id=blob["event_id"],
                detector=blob.get("detector", ""),
                risk_score=float(blob.get("risk_score") or 0.0),
                detector_state=blob.get("detector_state", ""),
                severity=blob.get("severity", ""),
                source_refs=tuple(blob.get("source_refs", ("", "", ""))),
                status=InterventionStatus(blob["status"]),
                opened_ts=blob.get("opened_ts", ""),
                history=tuple(dict(h) for h in blob.get("history", ())),
            )


class IncidentPipeline:
    """统一事件流消费 → 诊断 → 三通道判决 → 修复/升级 + 知识库 + 涌现工单。

    不变量（16号文 §4.3/MOD-INF-031 铁律）：
    - 行为类故障 MUST Block+Alert，永不调用修复引擎；
    - 语义类故障 MUST 走 LLM Bridge（``llm_fix``，必经 LSG 闸），不直通模板化；
    - 每次修复动作 MUST 自动写知识库记录（append-only）；
    - 不可自动修的判决 MUST 走 escalation 通道落盘。
    """

    def __init__(
        self,
        config: PipelineConfig,
        *,
        engine: FixEngineProtocol | None = None,
        alerter: Callable[[SecurityEvent], bool] | None = None,
    ) -> None:
        self._config = config
        self._engine = engine
        self._alerter = alerter
        self._matcher = FailureMatcher()
        self._pattern_matcher = FailurePatternMatcher()
        self._store = FixPatternStore(config.store_dir)
        self._store.ensure_files()
        # P1-3① 故障模式库冷启动：库为空时导入 failure_matcher 内置模式（幂等，非空不重复导）
        self._store.ensure_cold_start_patterns()
        config.runtime_dir.mkdir(parents=True, exist_ok=True)
        self._incidents_path = config.runtime_dir / config.incidents_filename
        self._escalation = EscalationSink(config.runtime_dir / config.escalations_filename)
        self._whitelist = WhitelistApprovalGate(
            config.runtime_dir / config.whitelist_ledger_filename,
            registry_path=config.authority_registry_path,
        )
        self._tickets = InterventionTicketStore(config.runtime_dir / config.tickets_filename)

    @property
    def store(self) -> FixPatternStore:
        return self._store

    @property
    def escalation(self) -> EscalationSink:
        return self._escalation

    @property
    def whitelist(self) -> WhitelistApprovalGate:
        return self._whitelist

    @property
    def tickets(self) -> InterventionTicketStore:
        return self._tickets

    def _get_engine(self) -> FixEngineProtocol:
        if self._engine is not None:
            return self._engine
        from zephyr.infrastructure.auto_fix_engine.engine import AutoFixEngine

        self._engine = AutoFixEngine()
        return self._engine

    # ── 主消费链路 ───────────────────────────────────────────────────

    def consume_event(self, event: SecurityEvent) -> IncidentRecord:
        """消费一条统一安全事件：诊断 → 三通道判决 → 修复/Block+Alert → 落盘。"""
        diagnosis = self._diagnose(event)
        channel = _CHANNEL_BY_FAULT_CLASS[diagnosis.fault_class]
        incident_id = uuid.uuid4().hex[:12]
        if channel is ChannelDecision.BLOCK_ALERT:
            record = self._handle_behavioral(incident_id, event, diagnosis)
        else:
            record = self._handle_auto_fix(incident_id, event, diagnosis, channel)
        _append_jsonl(self._incidents_path, _serialize_incident(record))
        # 涌现介入接线（12号文 §4.4）：is_breached 告警 → 人工介入处置工单
        if self._is_emergence_alert(event):
            self.consume_emergence_alert(event)
        return record

    def _handle_behavioral(
        self, incident_id: str, event: SecurityEvent, diagnosis: PipelineDiagnosis
    ) -> IncidentRecord:
        """行为类：Block+Alert 永不自动修复 + escalation 落盘（不变量）。"""
        alert_sent = self._send_alert(event)
        escalation_id = self._escalation.escalate(
            {
                "kind": "behavioral_block",
                "incident_id": incident_id,
                "event_id": event.event_id,
                "threat_category": event.threat_category.value,
                "reason": "行为类故障永不自动修复（Block+Alert，人工处置）",
                "suggestion": diagnosis.suggestion,
            }
        )
        return IncidentRecord(
            incident_id=incident_id,
            ts=now_iso(),
            event_id=event.event_id,
            fault_class=diagnosis.fault_class,
            channel=ChannelDecision.BLOCK_ALERT,
            diagnosis=diagnosis,
            action_status="blocked",
            escalated=True,
            escalation_id=escalation_id,
            alert_sent=alert_sent,
        )

    def _handle_auto_fix(
        self,
        incident_id: str,
        event: SecurityEvent,
        diagnosis: PipelineDiagnosis,
        channel: ChannelDecision,
    ) -> IncidentRecord:
        """结构/语义类：模板化直通 / LLM Bridge（必经 LSG）→ 修复 → 知识库记录。"""
        if channel is ChannelDecision.AUTO_TEMPLATE:
            action_type = _STRUCTURAL_ACTION_TYPES.get(
                FailureCategory(diagnosis.category), "config_fix"
            )
            lsg_gate = False
        else:
            action_type = SEMANTIC_ACTION_TYPE  # 语义类 MUST 走 LLM Bridge（必经 LSG 闸）
            lsg_gate = True
        action_id = ""
        action_status = "engine_error"
        escalated = False
        escalation_id = ""
        try:
            action = self._get_engine().fix(
                action_type, event.evidence_ref, dry_run=self._config.dry_run_fix
            )
            action_id = str(getattr(action, "action_id", "") or "")
            action_status = _status_value(getattr(action, "status", "unknown"))
        except Exception as exc:  # noqa: BLE001 — 修复引擎异常 MUST 降级 escalation，不阻断管线
            logger.error("修复引擎异常，转 escalation: %s", exc, exc_info=True)
        kb_record_id = self._store.append_fix_record(
            {
                "ts": now_iso(),
                "incident_id": incident_id,
                "event_id": event.event_id,
                "fault_class": diagnosis.fault_class.value,
                "channel": channel.value,
                "action_type": action_type,
                "target": event.evidence_ref,
                "action_status": action_status,
                "category": diagnosis.category,
                "suggestion": diagnosis.suggestion,
                "lsg_gate": lsg_gate,
            }
        )
        if action_status != "completed":
            escalated = True
            escalation_id = self._escalation.escalate(
                {
                    "kind": "unfixable",
                    "incident_id": incident_id,
                    "event_id": event.event_id,
                    "action_id": action_id,
                    "action_type": action_type,
                    "reason": f"不可自动修/修复未完成（status={action_status}），转人工",
                    "suggestion": diagnosis.suggestion,
                }
            )
        return IncidentRecord(
            incident_id=incident_id,
            ts=now_iso(),
            event_id=event.event_id,
            fault_class=diagnosis.fault_class,
            channel=channel,
            diagnosis=diagnosis,
            action_id=action_id,
            action_type=action_type,
            action_status=action_status,
            escalated=escalated,
            escalation_id=escalation_id,
            kb_record_id=kb_record_id,
        )

    def _diagnose(self, event: SecurityEvent) -> PipelineDiagnosis:
        """事件→诊断（failure_matcher 双件消费：分类定通道 + 模式建议）。"""
        text = _event_error_text(event)
        match = self._matcher.match(text)
        analysis = self._pattern_matcher.analyze(event.event_id, text)
        if event.threat_category in _BEHAVIORAL_THREATS:
            fault_class = FaultClass.BEHAVIORAL
        elif match.category in _STRUCTURAL_CATEGORIES:
            fault_class = FaultClass.STRUCTURAL
        else:
            fault_class = FaultClass.SEMANTIC
        return PipelineDiagnosis(
            event_id=event.event_id,
            fault_class=fault_class,
            category=match.category.value,
            pattern_name=analysis.pattern_name if analysis is not None else "",
            severity=event.severity.value,
            suggestion=(analysis.suggestion if analysis is not None else "") or match.suggestion,
            confidence=match.probability,
        )

    def _send_alert(self, event: SecurityEvent) -> bool:
        if self._alerter is None:
            return False
        try:
            return bool(self._alerter(event))
        except Exception:  # noqa: BLE001 — 告警通道异常不阻断 Block 主流程（事件已落盘）
            logger.error("行为类告警发送异常 event_id=%s", event.event_id, exc_info=True)
            return False

    # ── 涌现介入接线（12号文 §4.4）────────────────────────────────────

    def _is_emergence_alert(self, event: SecurityEvent) -> bool:
        """MOD-RK-14 is_breached 口径：threat=emergence 且 severity≥阈值。"""
        return (
            event.threat_category is ThreatCategory.EMERGENCE
            and event.severity_at_least(self._config.emergence_min_severity)
        )

    def consume_emergence_alert(self, event: SecurityEvent) -> InterventionTicket:
        """消费涌现 is_breached 告警 → 产人工介入处置工单（告警→工单，幂等）。"""
        if event.threat_category is not ThreatCategory.EMERGENCE:
            raise IncidentPipelineError("非涌现告警 MUST NOT 进介入工单链路")
        if not event.severity_at_least(self._config.emergence_min_severity):
            raise IncidentPipelineError("涌现告警严重度不足，不开介入工单")
        existing = self._tickets.find_by_event(event.event_id)
        if existing is not None:
            return existing
        detail = event.detail or {}
        ticket = InterventionTicket(
            ticket_id=uuid.uuid4().hex[:12],
            event_id=event.event_id,
            detector=str(detail.get("detector", "")),
            risk_score=float(detail.get("risk_score") or 0.0),
            detector_state=str(detail.get("state", "")),
            severity=event.severity.value,
            source_refs=(
                f"state_machine://{detail.get('detector', 'emergence')}",
                f"trajectory://{event.event_id}",
                f"fingerprint://{event.event_id}",
            ),
            status=InterventionStatus.TICKET_OPEN,
            opened_ts=now_iso(),
            history=(
                {"ts": now_iso(), "from": "", "to": InterventionStatus.TICKET_OPEN.value, "actor": "pipeline"},
            ),
        )
        self._tickets.save(ticket)
        logger.warning("涌现介入工单已开: ticket_id=%s event_id=%s", ticket.ticket_id, event.event_id)
        return ticket

    def advance_intervention(
        self, ticket_id: str, *, to_status: InterventionStatus, actor: str
    ) -> InterventionTicket:
        """工单→人审→关闭 状态机推进；人审/关闭 MUST 人审 actor 非空。"""
        ticket = self._tickets.get(ticket_id)
        if ticket is None:
            raise IncidentPipelineError(f"未知介入工单: {ticket_id!r}")
        if not isinstance(to_status, InterventionStatus):
            try:
                to_status = InterventionStatus(to_status)
            except ValueError as exc:
                raise IncidentPipelineError(f"非法工单状态: {to_status!r}") from exc
        if to_status in (InterventionStatus.HUMAN_REVIEW, InterventionStatus.CLOSED) and not actor:
            raise IncidentPipelineError("人审/关闭工单 MUST 人审 actor 非空（human_gated）")
        legal = _LEGAL_TICKET_TRANSITIONS[ticket.status]
        if to_status not in legal:
            raise IncidentPipelineError(
                f"非法工单状态迁移: {ticket.status.value} -> {to_status.value}（SOP：工单→人审→关闭）"
            )
        advanced = InterventionTicket(
            ticket_id=ticket.ticket_id,
            event_id=ticket.event_id,
            detector=ticket.detector,
            risk_score=ticket.risk_score,
            detector_state=ticket.detector_state,
            severity=ticket.severity,
            source_refs=ticket.source_refs,
            status=to_status,
            opened_ts=ticket.opened_ts,
            history=ticket.history
            + ({"ts": now_iso(), "from": ticket.status.value, "to": to_status.value, "actor": actor},),
        )
        self._tickets.save(advanced)
        return advanced


def _event_error_text(event: SecurityEvent) -> str:
    """从事件提取诊断用错误文本（detail 常见键优先，兜底证据指针）。"""
    detail = event.detail or {}
    for key in ("error", "message", "reason", "finding", "rule", "gate", "detector"):
        value = detail.get(key)
        if value:
            return str(value)
    return event.evidence_ref
