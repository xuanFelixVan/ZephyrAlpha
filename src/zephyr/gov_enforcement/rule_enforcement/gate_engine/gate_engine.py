# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_engine
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES] zephyr.shared.utils.db_utils; zephyr.gov_enforcement.rule_enforcement.gate_types; zephyr.gov_enforcement.rule_enforcement.risk_ssot; zephyr.gov_enforcement.rule_enforcement.task_types; zephyr.shared.io.io_cache; zephyr.shared.blueprint_code_auditor; zephyr.shared.code_economy_analyzer; zephyr.shared.combinatorial_gate; zephyr.shared.core_integrity_guard; zephyr.shared.slo_review_assistant; zephyr.gov_enforcement.rule_enforcement.circuit_breaker; zephyr.gov_drift.drift_infrastructure; zephyr.gov_enforcement.rule_enforcement.invariants.en_001_circular_dependency; zephyr.gov_enforcement.rule_enforcement.invariants.en_002_enforcement_validator; zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility; zephyr.gov_enforcement.rule_enforcement.invariants.zero_residue_check; zephyr.shared.contracts.protocols; zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.persistence.task_repo; zephyr.governance.lifecycle_governance.transition; zephyr.knowledge.kb.pipeline.triage; zephyr.knowledge.kb.pipeline.ingest; zephyr.knowledge.kb.pipeline.extract; zephyr.knowledge.kb.pipeline.activate; zephyr.knowledge.kb.pipeline.analyze; zephyr.autonomy_core.skills.skill_executor
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_gate_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
GateEngine — KMS G1-G6 + Orc G0/G7 + 交易 G10-G12 门禁裁决引擎（T-2-17）
======================================================================
依据：
- 知识库架构 §4（G1-G5 脚本接口设计）
- execution-order-v1.md beta.3（门禁策略引擎 P0）
- CT-ORC-GATE-001（任务 G0/G7 -> task/g0-orc-gate-engine.yaml、g7-orc-gate-engine.yaml）
- 交易类门：``gate_id`` 为 G10/G11/G12，YAML 文件名保留历史前缀（g7_position_limits / g8_leverage / g9_strategy_correlation）
- 指令：325 + 344 + 999

病根（2026-05 归档）
--------------------
曾将 ``field_presence`` / ``classification`` 等 check_type 在任务路径上实现为空操作（``pass``），
导致即便注册 G0 YAML 也无法生效；同时 ``task/g0-entry.yaml`` 使用不可执行的 ``rules:`` 叙述，
与引擎的 ``checks`` schema 脱节。本引擎现已实现上述 check_type 的任务侧语义，并由 Orc 专用 YAML 承载 G0/G7。

Safety : M（治理层代码，门禁失败阻断任务启动）

功能
----
- load_gates()   -> 从 YAML 文件加载门禁配置，返回 dict[gate_id, GateConfig]
- evaluate(task, gate_id[, conn=…]) -> 执行门禁检查，返回 GateResult，写入 gates 表；
  传入 ``conn`` 时使用调用方事务（例如 TaskRepository 写事务），不再单独 BEGIN/COMMIT。

支持的 CheckType（三大核心场景 + 扩展）
---------------------------------------
  field_presence   - Task/TaskCard 必填字段非空（Orc G0）
  classification   - 枚举字段落在允许集合（Orc：priority / verification_status 等）
  regex_pattern    - 单字段正则全匹配（Orc：task_id 对齐 schemas）
  audit_findings_resolved — TaskCard.audit_findings 全部 resolved（Orc G7）
  encoding         - 文件 UTF-8 无 BOM 编码校验
  line_ending      - LF 换行符校验
  file_extension   - 文件扩展名白名单
  frontmatter      - YAML frontmatter 必填字段
  content_length   - 正文最小字数
  deduplication    - 字段去重检查
  path_blacklist   - 废弃路径黑名单（核心场景 1）
  path_whitelist   - 允许路径白名单
  content_quality  - 空壳文件检测（核心场景 2）
  score_threshold  - 评分阈值（G2/G3 专用）
  field_presence   - 必填字段存在性
  manual_approval  - 手动审批（G4 专用，仅校验字段）
  classification   - 枚举值合法性
  temporal         - 时间约束（G5 专用）
  reference_check  - 关联引用存在性
  circuit_breaker  - 模块间熔断状态检查（T-V2-005 第 17 种，CBG experimental）
  blueprint_read_check - 蓝图读取合规检查（T-V2-011 第 18 种，G6 beta 硬合规）
  drift_budget        - 漂移预算检查（T-V2-012 第 19 种，G1/G6 实验性）—— 模块漂移事件数是否超出 SLO 预算
"""

from __future__ import annotations

from typing import Final
import logging

logger = logging.getLogger(__name__)

import json
import re
import sqlite3
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar

import yaml

from zephyr.shared.io.paths import DB_PATH, REPO_ROOT
from zephyr.gov_enforcement.rule_enforcement.gate_types import (
    GateEngineError,
    GateResult,
    GateViolation,
    GateViolationError,
)
from zephyr.gov_enforcement.rule_enforcement.risk_ssot import load_risk_params_ssot
from zephyr.gov_enforcement.rule_enforcement.task_types import Task
from zephyr.shared.io.paths import DB_PATH
from zephyr.shared.utils.db_utils import ensure_schema, get_db_connection
from zephyr.shared.io.io_cache import FileCache

__all__ = [
    "GATES_DIR",
    "GateEngine",
    "GateEngineError",
    "GateResult",
    "GateViolation",
    "GateViolationError",
]

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

GATES_DIR: Final[Path] = Path(__file__).parent.parent  # rule_enforcement/（门禁yaml真源根：task/ invariants/ admission/ 子目录）

_DEPRECATED_PATHS_YAML = (
    REPO_ROOT / "scripts" / "governance" / "_shared" / "deprecated_paths.yaml"
)


def _load_deprecated_patterns() -> list[str]:
    try:
        with open(_DEPRECATED_PATHS_YAML, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return list(data.get("blacklist_patterns", []))
    except FileNotFoundError:
        return []


_BUILTIN_DEPRECATED_PATTERNS: list[str] = _load_deprecated_patterns()

# 常见空壳占位符
_PLACEHOLDER_PATTERNS: list[str] = [
    r"\bTODO\b",
    r"\bPLACEHOLDER\b",
    r"\bTBD\b",
    r"\bSTUB\b",
    r"# Not implemented",
]


# ---------------------------------------------------------------------------
# 5.176.1 Phase 1: 从 _registry.yaml 动态加载 gate_id → filename 映射
# ---------------------------------------------------------------------------

def _load_gate_files_from_registry(gate_dir: Path) -> dict[str, str]:
    """从 _registry.yaml 加载 gate_id → filename 映射。

    _registry.yaml 是门禁注册表的唯一真源，替代硬编码的 _GATE_FILES 字典。
    两遍加载策略（与 ``_load_gate_configs_from_registry`` 一致）：
    - 第一遍：有 ``checks:`` / ``entry_conditions:`` 的可执行 gate 优先
    - 第二遍：仅有 ``rules:`` 的叙述型 gate 填补空缺

    Args:
        gate_dir: 门禁 YAML 根目录（``rule_enforcement/``）。

    Returns:
        ``{gate_id: filename}`` 字典；``gate_id`` 取自 YAML 文件本身
        （hyphen 格式如 ``EN-001``），而非 _registry.yaml 的 underscore 格式。
        若 _registry.yaml 不存在或解析失败，返回空字典（容错）。
    """
    registry_path = gate_dir / "_registry.yaml"
    if not registry_path.exists():
        return {}
    try:
        with registry_path.open(encoding="utf-8") as fh:
            raw_registry = yaml.safe_load(fh)
    except Exception:
        logger.warning("门禁注册表解析失败：%s", registry_path, exc_info=True)
        return {}
    executable: dict[str, str] = {}
    narrative: dict[str, str] = {}
    for entry in raw_registry.get("gates", []):
        filename = str(entry.get("file", "")).strip()
        if not filename or not filename.endswith((".yaml", ".yml")):
            continue
        yaml_path = gate_dir / filename
        if not yaml_path.exists():
            continue
        try:
            with yaml_path.open(encoding="utf-8") as fh:
                raw = yaml.safe_load(fh)
        except Exception:
            logger.warning("门禁 YAML 解析失败：%s", yaml_path, exc_info=True)
            continue
        gate_id = str(raw.get("gate_id", ""))
        if not gate_id:
            continue
        if raw.get("checks") or raw.get("entry_conditions"):
            executable[gate_id] = filename
        elif raw.get("rules"):
            narrative[gate_id] = filename
    # 合并：可执行优先，叙述型填补空缺
    result = dict(narrative)
    result.update(executable)
    return result

# ---------------------------------------------------------------------------
# 配置模型（轻量 dataclass，不用 Pydantic 避免循环依赖）
# ---------------------------------------------------------------------------


@dataclass
class CheckConfig:
    check_id: str
    name: str
    check_type: str
    description: str
    severity: str
    params: dict[str, Any]
    rule_ids: list[str] = field(default_factory=list)


@dataclass
class GateConfig:
    gate_id: str
    name: str
    description: str
    phase: str
    auto: bool
    checks: list[CheckConfig]
    on_failure: str
    on_pass: str
    rule_ids: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# 内部：检查实现
# ---------------------------------------------------------------------------


def _check_encoding(
    file_path: Path,
    params: dict[str, Any],
) -> str | None:
    """校验文件编码为 UTF-8 无 BOM，且无 GBK-as-UTF-8 mojibake。"""
    if not file_path.exists():
        return None
    raw = file_path.read_bytes()
    if params.get("disallow_bom", True) and raw.startswith(b"\xef\xbb\xbf"):
        return f"文件含 UTF-8 BOM：{file_path}"
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return f"编码损坏（非 UTF-8）：{file_path} — {exc}"
    if params.get("check_mojibake", True) and _detect_mojibake(file_path):
        return f"GBK-as-UTF-8 mojibake 检测：{file_path} — 文件含双重编码乱码，需修复"
    return None


def _detect_mojibake(file_path: Path) -> bool:
    """Detect GBK-as-UTF-8 double-encoding mojibake.

    Detection methods (short-circuit, first match wins):
    1. Known mojibake character sequences (high confidence)
    2. Round-trip via GBK on CJK segments (2a: clean, 2b: with U+FFFD)
    3. U+FFFD in CJK context (replacement chars adjacent to CJK)
    4. Statistical fallback (abnormal CJK distribution)
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return False
    if not content.strip():
        return False
    # 裁定#217 Tier2 P1 Extract Method：5 个检测方法提取为模块级 helper（均 McCabe≤15），
    # _detect_mojibake 简化为 short-circuit or 链（McCabe≈4）。行为等价：方法顺序 + 短路不变。
    return (
        _check_mojibake_markers(content)
        or _check_gbk_roundtrip_clean(content)
        or _check_gbk_roundtrip_with_replacement(content)
        or _check_fffd_in_cjk_context(content)
        or _check_statistical_fallback(content)
    )


# === 裁定#217 Tier2 P1 Extract Method 重构（2026-07-15）===
# 原 _detect_mojibake 96 行 McCabe=40（4 段检测方法串联，P2 detector fan-out pattern）。
# 治本：提取为 5 个模块级 helper（均 McCabe≤15），_detect_mojibake 简化为 short-circuit or 链。

_MOJIBAKE_MARKERS = [
    "\u9516\u65a4\u62f7",  # 锟斤拷 — classic GBK mojibake
    "\u93d4\u63d2\u53c2",
    "\u93d4\u659c\u7280\u6362",
    "\u93d4\u529c\u00b0\u20ac",
    "\u94c6\u003f",
]


def _check_mojibake_markers(content: str) -> bool:
    """Method 1: 已知 mojibake 字符序列（高置信度）。"""
    return any(m in content for m in _MOJIBAKE_MARKERS)


def _gbk_roundtrip_density_check(seg: str) -> bool | None:
    """GBK round-trip 密度检查：返回 True=mojibake, False=非 mojibake, None=解码失败。"""
    try:
        gbk_bytes = seg.encode("gbk")
    except UnicodeEncodeError:
        return None
    try:
        roundtrip = gbk_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if roundtrip == seg:
        return False
    orig_cjk = sum(1 for c in seg if 0x4E00 <= ord(c) <= 0x9FFF)
    rt_cjk = sum(1 for c in roundtrip if 0x4E00 <= ord(c) <= 0x9FFF)
    if rt_cjk == 0 or orig_cjk == 0:
        return False
    return (rt_cjk / len(roundtrip)) >= (orig_cjk / len(seg))


def _check_gbk_roundtrip_clean(content: str) -> bool:
    """Method 2a: GBK round-trip 检测不含 U+FFFD 的 CJK 段（含 partial decode fallback）。"""
    clean_content = content.replace("\ufffd", "")
    if not clean_content.strip():
        return False
    for seg in re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf]+", clean_content):
        if len(seg) < 2:
            continue
        result = _gbk_roundtrip_density_check(seg)
        if result:
            return True
        if result is None:
            # partial decode fallback（UTF-8 解码失败时检查 replace 模式的 CJK 密度）
            try:
                gbk_bytes = seg.encode("gbk")
                partial_rt = gbk_bytes.decode("utf-8", errors="replace")
                partial_cjk = sum(1 for c in partial_rt if 0x4E00 <= ord(c) <= 0x9FFF and c != "\ufffd")
                if partial_cjk >= 3:
                    return True
            except Exception:
                logger.warning("suppressed error in gate_engine", exc_info=True)
    return False


def _check_gbk_roundtrip_with_replacement(content: str) -> bool:
    """Method 2b: GBK round-trip 检测含 U+FFFD 的 CJK 段（拆分后检测子段）。"""
    if "\ufffd" not in content:
        return False
    for seg in re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf\ufffd]+", content):
        if "\ufffd" not in seg:
            continue
        for sub in [s for s in seg.split("\ufffd") if len(s) >= 2]:
            if _gbk_roundtrip_density_check(sub):
                return True
    return False


def _check_fffd_in_cjk_context(content: str) -> bool:
    """Method 3: U+FFFD 出现在 CJK 上下文中（替换字符紧邻 CJK）。"""
    if "\ufffd" not in content:
        return False
    cjk_context = re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf]\ufffd|\ufffd[\u4e00-\u9fff\u3400-\u4dbf]", content)
    return len(cjk_context) >= 2


def _check_statistical_fallback(content: str) -> bool:
    """Method 4: 统计回退（异常 CJK 分布——GBK 扩展区占比过高 + 常用区占比过低）。"""
    total_cjk = sum(1 for c in content if 0x4E00 <= ord(c) <= 0x9FFF)
    if total_cjk < 50:
        return False
    common_cjk = sum(1 for c in content if 0x4E00 <= ord(c) <= 0x77FF)
    gbk_ext_cjk = sum(1 for c in content if 0x9400 <= ord(c) <= 0x9FFF)
    return gbk_ext_cjk / total_cjk > 0.50 and common_cjk / total_cjk < 0.30


def _check_line_ending(
    file_path: Path,
    params: dict[str, Any],
) -> str | None:
    """校验文件使用 LF 换行（无 CRLF）。"""
    if not file_path.exists():
        return None
    raw = file_path.read_bytes()
    if b"\r\n" in raw:
        count = raw.count(b"\r\n")
        return f"文件含 CRLF 换行（{count} 处）：{file_path}"
    return None


def _check_path_blacklist(
    paths: list[str],
    params: dict[str, Any],
) -> list[str]:
    """检查路径列表中是否有废弃路径黑名单命中。"""
    blacklist: list[str] = list(params.get("blacklist_patterns", []))
    blacklist.extend(_BUILTIN_DEPRECATED_PATTERNS)
    violations: list[str] = []
    for p in paths:
        for pattern in blacklist:
            if pattern.lower() in p.lower().replace("\\", "/"):
                violations.append(f"废弃路径命中 '{pattern}'：{p}")
                break
    return violations


def _check_empty_shell(
    file_path: Path,
    params: dict[str, Any],
) -> str | None:
    """检测空壳文件：文件为空或正文充满占位符。"""
    if not file_path.exists():
        return None
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return f"无法读取文件：{file_path}"

    body = text.strip()
    if not body:
        return f"空文件（0 字节有效内容）：{file_path}"

    placeholder_patterns = params.get("placeholder_patterns", _PLACEHOLDER_PATTERNS)
    if isinstance(placeholder_patterns, list) and placeholder_patterns:
        total_chars = len(body)
        matched_chars = 0
        for pat in placeholder_patterns:
            for m in re.finditer(pat, body):
                matched_chars += len(m.group())
        ratio = matched_chars / max(total_chars, 1)
        max_ratio: float = float(params.get("max_placeholder_ratio", 0.5))
        if ratio > max_ratio:
            return f"空壳文件（占位符比例 {ratio:.1%} > {max_ratio:.0%}）：{file_path}"
    return None


def _check_content_length(
    file_path: Path,
    params: dict[str, Any],
) -> str | None:
    """校验正文长度 > min_chars（排除 frontmatter）。"""
    if not file_path.exists():
        return None
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return f"无法读取文件：{file_path}"
    # 去除 frontmatter
    body = re.sub(r"^---\n.*?\n---\n?", "", text, flags=re.DOTALL)
    body_len = len(body.strip())
    min_chars: int = int(params.get("min_chars", 100))
    if body_len < min_chars:
        return f"内容过短（{body_len} 字符 < {min_chars}）：{file_path}"
    return None


def _check_frontmatter(
    file_path: Path,
    params: dict[str, Any],
) -> str | None:
    """校验 Markdown frontmatter 包含必填字段。"""
    if not file_path.exists() or file_path.suffix not in {".md", ".markdown"}:
        return None
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return f"无法读取文件：{file_path}"
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return f"缺少 frontmatter：{file_path}"
    try:
        fm: dict[str, Any] = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return f"frontmatter 解析失败：{file_path}"
    required: list[str] = list(params.get("required_fields", []))
    missing = [f for f in required if f not in fm]
    if missing:
        return f"frontmatter 缺少必填字段 {missing}：{file_path}"
    return None


def _task_scalar_str(task: Task, field_name: str) -> str:
    val = getattr(task, field_name, None)
    if val is None:
        return ""
    return val.value if hasattr(val, "value") else str(val)


def _check_field_presence_task(task: Task, params: dict[str, Any]) -> list[str]:
    """校验 Task/TaskCard 上必填字段非空。"""
    missing: list[str] = []
    for fname in params.get("required_fields", []):
        val = getattr(task, fname, None)
        if (
            val is None
            or (isinstance(val, str) and len(val.strip()) == 0)
            or (isinstance(val, (list, dict)) and len(val) == 0)
        ):
            missing.append(fname)
    return missing


def _check_classification_task(task: Task, params: dict[str, Any]) -> str | None:
    """枚举字段必须落在 allowed_values 内；支持 skip_if_missing / require_present。"""
    field_name = str(params.get("field", ""))
    allowed_raw = params.get("allowed_values", [])
    allowed: list[str] = [str(x) for x in allowed_raw]
    require_present = bool(params.get("require_present", False))
    skip_if_missing = bool(params.get("skip_if_missing", False))
    if not field_name:
        return None
    if not hasattr(task, field_name):
        if skip_if_missing:
            return None
        if require_present:
            return f"字段 '{field_name}' 不存在（需要 TaskCard 或扩展 Task）"
        return None
    val = getattr(task, field_name)
    if val is None:
        if skip_if_missing:
            return None
        if require_present:
            return f"字段 '{field_name}' 必填但为 None"
        return None
    sval = _task_scalar_str(task, field_name)
    if allowed and sval not in allowed:
        return f"字段 '{field_name}' 值 '{sval}' 不在允许集合 {allowed}"
    return None


def _check_regex_pattern_task(task: Task, params: dict[str, Any]) -> str | None:
    """单字段正则全匹配（用于 task_id 等与 schemas 对齐的二次校验）。"""
    field_name = str(params.get("field", "task_id"))
    pattern = str(params.get("pattern", ""))
    if not pattern:
        return None
    sval = _task_scalar_str(task, field_name)
    try:
        if re.fullmatch(pattern, sval) is None:
            return f"字段 '{field_name}'={sval!r} 不匹配正则 {pattern!r}"
    except re.error as exc:
        return f"正则无效：{pattern!r} ({exc})"
    return None


def _check_audit_findings_messages(task: Task) -> list[str]:
    """TaskCard.audit_findings 全部 resolved；无该字段则跳过。"""
    if not hasattr(task, "audit_findings"):
        return []
    findings_raw = task.audit_findings or []
    msgs: list[str] = []
    for af in findings_raw:
        if getattr(af, "resolved", False):
            continue
        fid = getattr(af, "finding_id", "?")
        msgs.append(f"审计发现未关闭：{fid}")
    return msgs


# ---------------------------------------------------------------------------
# 统一调度函数
# ---------------------------------------------------------------------------

_TEXT_CHECK_EXTENSIONS: frozenset[str] = frozenset({".md"})


def _is_text_check_target(file_path: str | Path) -> bool:
    return Path(file_path).suffix.lower() in _TEXT_CHECK_EXTENSIONS


# ---------------------------------------------------------------------------
# 5.176.1 Phase 2: 违规构造辅助 + check_type 分发表（替代 if-elif 链）
# ---------------------------------------------------------------------------


def _make_violation(
    check: CheckConfig,
    msg: str,
    detail: str | None = None,
    severity: str | None = None,
) -> GateViolation:
    """Create a GateViolation from check config, with optional severity override."""
    return GateViolation(
        check_id=check.check_id,
        check_name=check.name,
        severity=severity or check.severity,
        message=msg,
        detail=detail,
        rule_ids=list(check.rule_ids),
    )


CheckHandler = Callable[[CheckConfig, Task, Path, list[str], list[Path]], list[GateViolation]]


def _handle_encoding(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    for fp in dep_paths:
        if not _is_text_check_target(fp):
            continue
        err = _check_encoding(fp, check.params)
        if err:
            _add(err)
    return violations


def _handle_line_ending(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    for fp in dep_paths:
        if not _is_text_check_target(fp):
            continue
        err = _check_line_ending(fp, check.params)
        if err:
            _add(err)
    return violations


def _handle_path_blacklist(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    errs = _check_path_blacklist(deliverables, check.params)
    for e in errs:
        _add(e)
    return violations


def _handle_content_quality(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    for fp in dep_paths:
        if not _is_text_check_target(fp):
            continue
        err = _check_empty_shell(fp, check.params)
        if err:
            _add(err)
    return violations


def _handle_content_length(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    for fp in dep_paths:
        if not _is_text_check_target(fp):
            continue
        err = _check_content_length(fp, check.params)
        if err:
            _add(err)
    return violations


def _handle_frontmatter(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    for fp in dep_paths:
        if not _is_text_check_target(fp):
            continue
        err = _check_frontmatter(fp, check.params)
        if err:
            _add(err)
    return violations


def _handle_file_extension(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    allowed: list[str] = list(check.params.get("allowed_extensions", []))
    for p in deliverables:
        ext = Path(p).suffix.lower()
        if allowed and ext not in allowed:
            _add(f"不允许的文件扩展名 '{ext}'：{p}")
    return violations


def _handle_circuit_breaker(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    # 第 17 种 CheckType（T-V2-005 CBG experimental）
    # 在 gate 配置 YAML 中通过 params.caller_module + params.target_module 指定
    caller = str(check.params.get("caller_module", ""))
    target = str(check.params.get("target_module", ""))
    if not caller or not target:
        _add(
            "circuit_breaker 检查缺少 caller_module / target_module 参数",
            detail=f"check_id={check.check_id}",
        )
    else:
        try:
            from zephyr.gov_enforcement.rule_enforcement.circuit_breaker import CircuitBreakerCheck

            cb_check = CircuitBreakerCheck(
                caller_module=caller,
                target_module=target,
            )
            if cb_check.is_open():
                _add(cb_check.violation_message())
        except Exception as exc:
            # CBGManager 初始化失败时降级为 P2 警告，不阻断门禁
            violations.append(
                _make_violation(
                    check,
                    f"circuit_breaker 检查初始化失败（降级 P2）：{exc}",
                    severity="P2",
                )
            )
    return violations


def _handle_blueprint_read_check(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    # 第 18 种 CheckType（T-V2-011 G6 beta 硬合规）
    # 检查：AI 在修改目标模块文件前，是否已读取对应的蓝图
    # beta（硬合规，2026-05-04 激活）：
    #   — severity=error -> P0 阻断：未读蓝图就改代码的 task 直接 REJECT
    #   — AI 必须调用 blueprint_search.find_relevant_blueprint() 定位蓝图
    #   — 或在 session 日志中声明已手动阅读蓝图
    target_blueprint = str(check.params.get("target_blueprint", ""))
    target_files = list(check.params.get("target_files", []))
    hard_compliance = bool(check.params.get("hard_compliance", False))
    if not target_blueprint:
        _add(
            "blueprint_read_check 缺少 target_blueprint 参数",
            detail=f"check_id={check.check_id}",
        )
    else:
        _check_blueprint_read_compliance(
            target_blueprint,
            target_files,
            check,
            _add,
            hard_compliance=hard_compliance,
        )
    return violations


def _handle_drift_budget(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    target_module = str(check.params.get("target_module", task.task_id))
    try:
        from zephyr.gov_drift.drift_infrastructure import check_budget_for_gate

        budget = check_budget_for_gate(target_module)
        if not budget.get("allowed", False):
            _add(
                f"漂移预算耗尽，模块 {target_module} 必须先修复漂移再提交变更",
                detail=budget.get("reason", "drift budget exceeded"),
            )
    except Exception as exc:
        violations.append(
            _make_violation(
                check,
                f"drift_budget 检查初始化失败（降级 P2）：{exc}",
                severity="P2",
            )
        )
    return violations


def _handle_field_presence(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    missing = _check_field_presence_task(task, check.params)
    for mf in missing:
        _add(f"缺少或为空必填字段：{mf}")
    return violations


def _handle_classification(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    err = _check_classification_task(task, check.params)
    if err:
        _add(err)
    return violations


def _handle_regex_pattern(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    err = _check_regex_pattern_task(task, check.params)
    if err:
        _add(err)
    return violations


def _handle_audit_findings_resolved(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    for msg in _check_audit_findings_messages(task):
        _add(msg)
    return violations


def _handle_circular_dependency_scan(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    try:
        from zephyr.gov_enforcement.rule_enforcement.invariants.en_001_circular_dependency import run_scan

        result = run_scan()
        if not result.passed:
            for cycle in result.cycles:
                _add(
                    f"Circular dependency: {' -> '.join(cycle)} -> {cycle[0]}",
                    detail=f"Cycle length: {len(cycle)}",
                )
    except Exception as exc:
        _add(f"EN-001 scan failed: {exc}", detail=str(exc))
    return violations


def _handle_enforcement_mode_check(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    try:
        from zephyr.gov_enforcement.rule_enforcement.invariants.en_002_enforcement_validator import (
            run_check as en2_check,
        )

        result = en2_check()
        if not result.passed:
            for v in result.violations:
                _add(v)
    except Exception as exc:
        _add(f"EN-002 check failed: {exc}", detail=str(exc))
    return violations


def _handle_contract_compatibility_check(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    try:
        from zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility import (
            run_check as en3_check,
        )

        result = en3_check()
        if not result.passed:
            for m in result.mismatches:
                _add(m)
    except Exception as exc:
        _add(f"EN-003 check failed: {exc}", detail=str(exc))
    return violations


def _handle_security_artifact_scan(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    try:
        import importlib

        _mod = importlib.import_module("zephyr.gov_drift.artifact_scanner")
        ArtifactScanner = _mod.ArtifactScanner

        scanner = ArtifactScanner()
        scanner._RULES = []

        scan_paths: list[str] = check.params.get("scan_paths", [])
        target_patterns: list[str] = check.params.get("target_patterns", ["*.py"])

        for sp in scan_paths:
            path = Path(sp)
            if not path.exists():
                _add(f"Artifact scan path not found: {sp}", severity="warning")
                continue
            if path.is_file():
                report = scanner.scan_file(path)
            else:
                py_files = list(path.rglob("*.py"))
                reports = scanner.scan_files(py_files)
                for report in reports:
                    if not report.is_clean:
                        for f in report.findings:
                            _add(
                                f"{report.target}:L{f.line_number}: {f.message}",
                                detail=f"[{f.rule_id}] {f.snippet}",
                                severity=f.severity,
                            )
                continue

            if not report.is_clean:  # type: ignore[reportPossiblyUnbound]
                for f in report.findings:  # type: ignore[reportPossiblyUnbound]
                    _add(
                        f"{report.target}:L{f.line_number}: {f.message}",  # type: ignore[reportPossiblyUnbound]
                        detail=f"[{f.rule_id}] {f.snippet}",
                        severity=f.severity,
                    )
    except Exception as exc:
        _add(f"Security artifact scan failed: {exc}", detail=str(exc))
    return violations


def _handle_position_limit(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    ssot = load_risk_params_ssot(project_root)
    p = check.params
    nav = ssot.get("max_single_position_nav_ratio")
    d_default = p.get("max_single_position_default")
    if d_default is not None and nav is not None:
        if float(d_default) > float(nav) + 1e-12:
            _add(
                f"G10 与 risk_params SSoT 冲突：max_single_position_default={d_default} "
                f"> max_single_position_nav_ratio={nav}（{check.name}）",
            )
    sec_cap = ssot.get("max_sector_concentration_nav_ratio")
    s_default = p.get("max_sector_concentration_default")
    if s_default is not None and sec_cap is not None:
        if float(s_default) > float(sec_cap) + 1e-12:
            _add(
                f"G10 与 risk_params SSoT 冲突：max_sector_concentration_default={s_default} "
                f"> max_sector_concentration_nav_ratio={sec_cap}（{check.name}）",
            )
    adv_cap = ssot.get("max_adv_participation_ratio")
    adv_p = p.get("max_adv_ratio")
    if adv_p is not None and adv_cap is not None:
        if float(adv_p) > float(adv_cap) + 1e-12:
            _add(
                f"G10 与 risk_params SSoT 冲突：max_adv_ratio={adv_p} "
                f"> max_adv_participation_ratio={adv_cap}（{check.name}）",
            )
    return violations


def _handle_leverage_limit(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    ssot = load_risk_params_ssot(project_root)
    p = check.params
    lev = p.get("max_gross_leverage_default")
    cap = ssot.get("max_gross_leverage")
    if lev is not None and cap is not None:
        if float(lev) > float(cap) + 1e-12:
            _add(
                f"G11 与 risk_params SSoT 冲突：max_gross_leverage_default={lev} "
                f"> max_gross_leverage={cap}（{check.name}）",
            )
    return violations


def _handle_strategy_correlation(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    ssot = load_risk_params_ssot(project_root)
    p = check.params
    ct_thr = p.get("correlation_threshold")
    ss_thr = ssot.get("max_strategy_correlation_threshold")
    if ct_thr is not None and ss_thr is not None:
        if float(ct_thr) > float(ss_thr) + 1e-12:
            _add(
                f"G12 策略相关性阈值过于宽松：correlation_threshold={ct_thr} "
                f"> max_strategy_correlation_threshold={ss_thr}（{check.name}）",
            )
    mo = p.get("max_factor_overlap")
    ss_mo = ssot.get("max_factor_overlap_threshold")
    if mo is not None and ss_mo is not None:
        if float(mo) > float(ss_mo) + 1e-12:
            _add(
                f"G12 因子重叠上限过于宽松：max_factor_overlap={mo} "
                f"> max_factor_overlap_threshold={ss_mo}（{check.name}）",
            )
    uo = p.get("max_universe_overlap")
    ss_uo = ssot.get("max_universe_overlap_threshold")
    if uo is not None and ss_uo is not None:
        if float(uo) > float(ss_uo) + 1e-12:
            _add(
                f"G12 股票池重叠上限过于宽松：max_universe_overlap={uo} "
                f"> max_universe_overlap_threshold={ss_uo}（{check.name}）",
            )
    return violations


def _handle_zero_residue_check(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    try:
        from zephyr.gov_enforcement.rule_enforcement.invariants.zero_residue_check import ZeroResidueScanner

        scanner = ZeroResidueScanner(project_root=project_root)
        report = scanner.scan()
        if not report.is_clean:
            for fg in report.findings:
                sev: str = "P0" if fg.severity == "error" else "P1"
                _add(
                    fg.message,
                    detail=f"[{fg.rule_id}] {fg.file_rel}",
                    severity=sev,
                )
    except Exception as exc:
        _add(f"Zero residue scan failed: {exc}", detail=str(exc))
    return violations


def _handle_post_doc_review_check(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    try:
        from zephyr.gov_enforcement.rule_enforcement.invariants.post_doc_review_check import (
            PostDocReviewScanner,
        )

        session_id = str(check.params.get("session_id", "")) if hasattr(check, "params") else ""
        scanner = PostDocReviewScanner(project_root=project_root, session_id=session_id)
        report = scanner.scan()
        if not report.is_clean:
            for fg in report.pending_regularization:
                _add(
                    f"待规格化项: {fg.issue_type} in {fg.file_path}:{fg.line_number}",
                    detail=f"[{fg.rule_ref}] {fg.issue_text}",
                    severity="P1",
                )
        if report.regularization_triggered:
            _add(
                f"待规格化项≥3，已触发规格化流程 (task_id={report.regularization_task_id})",
                detail=f"pending_count={len(report.pending_regularization)}",
                severity="P1",
            )
    except Exception as exc:
        _add(f"Post doc review scan failed: {exc}", detail=str(exc))
    return violations


def _handle_p2_skip(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    _add(
        f"检查类型 '{check.check_type}' 在任务门禁路径未实现（依赖 KMS / 额外数据），已跳过",
        detail="gate_engine._run_check",
        severity="P2",
    )
    return violations


def _handle_fle_gate(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    gate_module = str(check.params.get("gate_module", ""))
    gate_method = str(check.params.get("gate_method", "check"))
    if not gate_module:
        _add("fle_gate 检查缺少 gate_module 参数", detail=f"check_id={check.check_id}")
    else:
        try:
            import importlib

            mod = importlib.import_module(gate_module)
            candidates = [a for a in dir(mod) if isinstance(getattr(mod, a), type) and not a.startswith("_")]
            if not candidates:
                _add(f"FLE 门禁模块 {gate_module} 无可用类")
            else:
                gate_cls = getattr(mod, candidates[0])
                try:
                    gate_inst = gate_cls()
                except TypeError:
                    gate_inst = gate_cls
                method = getattr(gate_inst, gate_method, None)
                if method is None:
                    _add(f"FLE 门禁 {gate_module} 无 {gate_method} 方法")
                else:
                    import inspect

                    sig = inspect.signature(method)
                    params = list(sig.parameters.keys())
                    if len(params) == 0:
                        result = method()
                    else:
                        result = method(task.task_id)
                    if isinstance(result, dict):
                        if not result.get("allowed", result.get("passed", result.get("ok", True))):
                            _add(
                                f"FLE 门禁 {gate_module}.{gate_method} 拒绝",
                                detail=str(result),
                            )
                    elif isinstance(result, bool) and not result:
                        _add(f"FLE 门禁 {gate_module}.{gate_method} 返回 False")
        except Exception as exc:
            violations.append(
                _make_violation(
                    check,
                    f"fle_gate 检查初始化失败（降级 P2）：{exc}",
                    severity="P2",
                )
            )
    return violations


def _handle_rollback_exit_code(
    check: CheckConfig,
    task: Task,
    project_root: Path,
    deliverables: list[str],
    dep_paths: list[Path],
) -> list[GateViolation]:
    violations: list[GateViolation] = []

    def _add(msg: str, detail: str | None = None, severity: str | None = None) -> None:
        violations.append(_make_violation(check, msg, detail, severity))

    exit_code_raw = check.params.get("exit_code", 0)
    try:
        exit_code = int(exit_code_raw)
    except (TypeError, ValueError):
        exit_code = -1
    try:
        from zephyr.infrastructure.rollback.contract import get_gate_action

        gate_action, description = get_gate_action(exit_code)
        if gate_action in ("FAIL", "BLOCK", "BLOCK_AUTO") or gate_action in (
            "WARN",
            "RETRY",
            "PAUSE_AGENT",
            "PAUSE_AUTO",
            "REDUCE_TIER",
        ):
            _add(
                f"Rollback exit code {exit_code} -> {gate_action}: {description}",
                detail=f"check_id={check.check_id} exit_code={exit_code}",
            )
    except Exception as exc:
        violations.append(
            _make_violation(
                check,
                f"rollback_exit_code check failed (degrade P2): {exc}",
                severity="P2",
            )
        )
    return violations


_CHECK_DISPATCH: dict[str, CheckHandler] = {
    "encoding": _handle_encoding,
    "line_ending": _handle_line_ending,
    "path_blacklist": _handle_path_blacklist,
    "content_quality": _handle_content_quality,
    "content_length": _handle_content_length,
    "frontmatter": _handle_frontmatter,
    "file_extension": _handle_file_extension,
    "circuit_breaker": _handle_circuit_breaker,
    "blueprint_read_check": _handle_blueprint_read_check,
    "drift_budget": _handle_drift_budget,
    "field_presence": _handle_field_presence,
    "classification": _handle_classification,
    "regex_pattern": _handle_regex_pattern,
    "audit_findings_resolved": _handle_audit_findings_resolved,
    "circular_dependency_scan": _handle_circular_dependency_scan,
    "enforcement_mode_check": _handle_enforcement_mode_check,
    "contract_compatibility_check": _handle_contract_compatibility_check,
    "security_artifact_scan": _handle_security_artifact_scan,
    "position_limit": _handle_position_limit,
    "leverage_limit": _handle_leverage_limit,
    "strategy_correlation": _handle_strategy_correlation,
    "zero_residue_check": _handle_zero_residue_check,
    "post_doc_review_check": _handle_post_doc_review_check,
    "score_threshold": _handle_p2_skip,
    "manual_approval": _handle_p2_skip,
    "path_whitelist": _handle_p2_skip,
    "path_routing": _handle_p2_skip,
    "temporal": _handle_p2_skip,
    "reference_check": _handle_p2_skip,
    "deduplication": _handle_p2_skip,
    "threshold": _handle_p2_skip,
    "fle_gate": _handle_fle_gate,
    "rollback_exit_code": _handle_rollback_exit_code,
}


def _run_check(
    check: CheckConfig,
    task: Task,
    project_root: Path,
) -> list[GateViolation]:
    """根据 check_type 调度到对应实现，返回零或多条违规。

    5.176.1 Phase 2: 使用 _CHECK_DISPATCH 分发表替代 if-elif 链。
    """
    deliverables: list[str] = list(task.deliverables or [])
    dep_paths = [project_root / p for p in deliverables]
    handler = _CHECK_DISPATCH.get(check.check_type)
    if handler is None:
        return [
            _make_violation(
                check,
                f"Unknown check type '{check.check_type}', skipped",
                detail="gate_engine._run_check",
                severity="P2",
            )
        ]
    return handler(check, task, project_root, deliverables, dep_paths)


# ---------------------------------------------------------------------------
# GateEngine
# ---------------------------------------------------------------------------


class GateEngine:
    """
    门禁裁决引擎。

    参数
    ----
    gate_dir
        存放各门禁 YAML（含 ``task/*.yaml``）的目录；默认与本模块同级。
    db_path
        SQLite 数据库路径；默认使用 DB_PATH。
    project_root
        项目根目录，用于将 task.deliverables 中的相对路径解析为绝对路径。
    auto_init
        首次连接时是否调用 init_db()（默认 True）。
    """

    # 5.176.1 Phase 1: _GATE_FILES 从 _registry.yaml 动态加载（替代硬编码字典）。
    # 保留为类变量以兼容 tests/trae_rules/ 中的成员检查（GateEngine._GATE_FILES）。
    # reload_gates() 不再使用此变量——直接从 _registry.yaml 加载。
    _GATE_FILES: dict[str, str] = _load_gate_files_from_registry(GATES_DIR)

    MANDATORY_GATES: frozenset[str] = frozenset(
        {
            "G0",
            "G7",
            "EN-001",
            "EN-002",
            "EN-003",
            "ZERO-RESIDUE",
            "G10",
            "G11",
            "G12",
        }
    )

    @classmethod
    def is_mandatory(cls, gate_id: str) -> bool:
        return gate_id in cls.MANDATORY_GATES

    def __init__(
        self,
        gate_dir: Path | str | None = None,
        db_path: Path | str | None = None,
        project_root: Path | str | None = None,
        *,
        auto_init: bool = True,
    ) -> None:
        self._gate_dir: Path = Path(gate_dir) if gate_dir is not None else GATES_DIR
        self._db_path: Path = Path(db_path) if db_path is not None else DB_PATH
        self._project_root: Path = Path(project_root) if project_root is not None else Path.cwd()
        if auto_init:
            ensure_schema(self._db_path)
        self._conn: sqlite3.Connection = get_db_connection(self._db_path)
        self._gate_cache: dict[str, GateConfig] | None = None
        self._yaml_cache: FileCache = FileCache(max_entries=50, ttl_seconds=600.0)

    # ------------------------------------------------------------------
    # 公共 API
    # ------------------------------------------------------------------

    def load_gates(self) -> dict[str, GateConfig]:
        """
        从 YAML 文件加载所有门禁配置。

        返回值会被缓存；重复调用不重新读文件。
        使用 ``reload_gates()`` 强制刷新缓存。
        """
        if self._gate_cache is not None:
            return self._gate_cache
        return self.reload_gates()

    def reload_gates(self) -> dict[str, GateConfig]:
        """强制重新从文件加载门禁配置（清除缓存）。

        5.176.1 Phase 1: 从 ``_registry.yaml`` 动态加载，替代硬编码
        ``_GATE_FILES`` 迭代。``_registry.yaml`` 是门禁注册表的唯一真源。
        """
        registry_path = self._gate_dir / "_registry.yaml"
        if not registry_path.exists():
            raise GateEngineError(f"门禁配置文件不存在：{registry_path}")
        configs = self._load_gate_configs_from_registry()
        self._gate_cache = configs
        return configs

    def _load_gate_configs_from_registry(self) -> dict[str, GateConfig]:
        """从 ``_registry.yaml`` 加载并解析所有门禁配置。

        5.176.1 Phase 1 核心方法——替代 ``reload_gates`` 中对 ``_GATE_FILES``
        的迭代。

        两遍加载策略（解决 G0/G0_ORC 双条目冲突）：
        - 第一遍：加载有 ``checks:`` / ``entry_conditions:`` 的可执行 gate
        - 第二遍：加载仅有 ``rules:`` 的叙述型 gate，但跳过 gate_id 已在
          第一遍加载的条目（避免 ``g0_entry.yaml`` 覆盖 ``g0_orc_gate_engine.yaml``）

        ``gate_id`` 取自 YAML 文件本身（hyphen 格式如 ``EN-001``），而非
        ``_registry.yaml`` 的 underscore 格式（如 ``EN_001``）。
        """
        registry_path = self._gate_dir / "_registry.yaml"
        raw_registry = self._yaml_cache.get_or_load(str(registry_path))
        if raw_registry is None:
            with registry_path.open(encoding="utf-8") as fh:
                raw_registry = yaml.safe_load(fh)

        configs: dict[str, GateConfig] = {}
        narrative_configs: dict[str, GateConfig] = {}
        for entry in raw_registry.get("gates", []):
            filename = str(entry.get("file", "")).strip()
            if not filename or not filename.endswith((".yaml", ".yml")):
                continue
            yaml_path = self._gate_dir / filename
            if not yaml_path.exists():
                continue
            raw = self._yaml_cache.get_or_load(str(yaml_path))
            if raw is None:
                with yaml_path.open(encoding="utf-8") as fh:
                    raw = yaml.safe_load(fh)
            cfg = self._parse_config(raw)
            if raw.get("checks") or raw.get("entry_conditions"):
                # 可执行 gate 优先
                configs[cfg.gate_id] = cfg
            elif raw.get("rules"):
                # 叙述型 gate 暂存，第二遍再合并
                narrative_configs[cfg.gate_id] = cfg
        # 合并：可执行 gate 优先，叙述型 gate 仅填补空缺
        for gate_id, cfg in narrative_configs.items():
            if gate_id not in configs:
                configs[gate_id] = cfg
        return configs

    def evaluate(
        self,
        task: Task,
        gate_id: str,
        *,
        conn: sqlite3.Connection | None = None,
    ) -> GateResult:
        """
        对 task 执行指定门禁的所有检查，返回 GateResult。

        - P0 违规存在 -> passed=False（阻断）
        - 仅 P1/P2 违规 -> passed=True（警告，不阻断）
        - 裁决结果写入 SQLite gates 表

        参数
        ----
        task : Task
            待检查的任务 Pydantic 模型。
        gate_id : str
            ``G0`` / ``G7``（Orc 任务门）或 ``G1`` ~ ``G6``（KMS + 合规）。
        conn : sqlite3.Connection | None
            若非空，在此连接上插入 gates 行且不开启新事务（须已由调用方 ``BEGIN``）。
            为空时使用引擎自带连接并自行 ``BEGIN IMMEDIATE`` / ``COMMIT``。
        """
        gates = self.load_gates()
        if gate_id not in gates:
            raise GateEngineError(f"未知 gate_id='{gate_id}'；可用：{list(gates)}")
        config = gates[gate_id]
        all_violations: list[GateViolation] = []

        for check in config.checks:
            v_list = _run_check(check, task, self._project_root)
            all_violations.extend(v_list)

        passed = not any(v.severity == "P0" for v in all_violations)
        aggregated_rule_ids: list[str] = sorted(
            set(config.rule_ids + [rid for v in all_violations for rid in v.rule_ids])
        )
        result = GateResult(
            gate_id=gate_id,
            task_id=task.task_id,
            passed=passed,
            violations=all_violations,
            details={
                "gate_name": config.name,
                "checks_run": len(config.checks),
                "total_violations": len(all_violations),
                "p0_count": sum(1 for v in all_violations if v.severity == "P0"),
                "p1_count": sum(1 for v in all_violations if v.severity == "P1"),
                "p2_count": sum(1 for v in all_violations if v.severity == "P2"),
            },
            rule_ids=aggregated_rule_ids,
        )
        self._persist_result(result, conn=conn)
        return result

    def close(self) -> None:
        """关闭底层 SQLite 连接。"""
        self._conn.close()

    def __enter__(self) -> GateEngine:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    # ------------------------------------------------------------------
    # 内部：持久化
    # ------------------------------------------------------------------

    def _persist_result(
        self,
        result: GateResult,
        *,
        conn: sqlite3.Connection | None = None,
    ) -> None:
        """将 GateResult 写入 SQLite gates 表。"""
        violations_json = json.dumps(
            [
                {
                    "check_id": v.check_id,
                    "severity": v.severity,
                    "message": v.message,
                    "rule_ids": v.rule_ids,
                }
                for v in result.violations
            ],
            ensure_ascii=False,
        )
        target = conn if conn is not None else self._conn
        manage_tx = conn is None
        if manage_tx:
            target.execute("BEGIN IMMEDIATE")
        try:
            target.execute(
                """
                INSERT INTO gate_runs
                    (gate_run_id, gate_id, passed, details, artifact_path, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    f"gr-{uuid.uuid4()}",
                    f"{result.gate_id}:{result.task_id}",
                    1 if result.passed else 0,
                    violations_json,
                    None,
                    result.evaluated_at,
                ),
            )
            if manage_tx:
                target.execute("COMMIT")
        except Exception:
            if manage_tx:
                target.execute("ROLLBACK")
            raise

    # ------------------------------------------------------------------
    # 内部：YAML 解析
    # ------------------------------------------------------------------

    # 将 YAML 中的人类可读 severity 值映射为引擎用的 P 级标签
    _SEVERITY_MAP: ClassVar[dict[str, str]] = {
        "error": "P0",
        "critical": "P0",
        "reject": "P0",
        "hard": "P0",
        "warning": "P1",
        "warn": "P1",
        "info": "P2",
        "soft": "P2",
    }

    @staticmethod
    def _parse_config(raw: dict[str, Any]) -> GateConfig:
        """将 YAML dict 解析为 GateConfig dataclass。

        兼容两种 YAML schema：
        - 旧格式：顶层用 ``name``，检查项列表字段为 ``checks``，每项含 ``type``
        - 新格式（g1~g5.yaml）：顶层用 ``title``/``gate_name``，检查项列表字段
          为 ``entry_conditions``，severity 值为 ``error``/``warning``
        """
        # 优先使用 title（如 "G1 Ingest Gate"），再回落到 name / gate_name
        name = str(raw.get("name") or raw.get("title") or raw.get("gate_name", ""))

        # 兼容 checks / entry_conditions
        raw_checks: list[Any] = list(raw.get("checks") or raw.get("entry_conditions") or raw.get("rules") or [])

        checks: list[CheckConfig] = []
        for c in raw_checks:
            raw_sev = str(c.get("severity") or c.get("enforcement") or "P1")
            severity = GateEngine._SEVERITY_MAP.get(raw_sev.lower(), raw_sev)
            check_rule_ids: list[str] = list(c.get("rule_ids", []))
            checks.append(
                CheckConfig(
                    check_id=str(c.get("id") or c.get("rule_id", "")),
                    name=str(c.get("name", "")),
                    check_type=str(c.get("type", "condition")),
                    description=str(c.get("description", "")),
                    severity=severity,
                    params=dict(c.get("params", {})),
                    rule_ids=check_rule_ids,
                )
            )
        gate_rule_ids: list[str] = list(raw.get("rule_ids", []))
        return GateConfig(
            gate_id=str(raw["gate_id"]),
            name=name,
            description=str(raw.get("description", "")),
            phase=str(raw.get("phase", "")),
            auto=bool(raw.get("auto", True)),
            checks=checks,
            on_failure=str(raw.get("on_failure", "reject")),
            on_pass=str(raw.get("on_pass", "pass")),
            rule_ids=gate_rule_ids,
        )


def _check_blueprint_read_compliance(
    target_blueprint: str,
    target_files: list[str],
    check: CheckConfig,
    _add: callable,
    *,
    hard_compliance: bool = False,
) -> None:
    """检查 AI 在修改目标文件前是否已读取对应的蓝图。

    experimental（软合规，已退役）：
    - severity=warning -> 仅提醒，不阻断

    beta（硬合规，2026-05-04 激活）：
    - severity=error -> P0 硬阻断
    - 未读蓝图则返回 GateViolationError
    - AI 必须读蓝图后才能继续
    """
    metrics_path = REPO_ROOT / "data" / "telemetry" / "blueprint_reads.jsonl"

    if not metrics_path.exists():
        msg = (
            f"G6 硬合规阻断: 未检测到蓝图读取记录——"
            f"AI 在修改 {target_files[0] if target_files else '目标'} 前 MUST 读取 {target_blueprint} 蓝图"
        )
        if hard_compliance:
            _add(
                msg,
                detail="beta hard compliance active — metrics file not found, blueprint read MANDATORY before code change",
            )
        else:
            _add(
                msg,
                detail="metrics file not found — first session? Add blueprint_read instrumentation",
            )
        return

    try:
        found = False
        with open(metrics_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("blueprint_id") == target_blueprint and record.get("event") == "blueprint_read":
                    found = True
                    break
    except OSError:
        _add(
            f"G6 硬合规阻断: 无法读取 metrics 文件——AI MUST 确认已读取 {target_blueprint} 蓝图后再继续",
            detail="blueprint_reads.jsonl unreadable — beta hard compliance REQUIRES blueprint read confirmation",
        )
        return

    if not found:
        if hard_compliance:
            _add(
                f"G6 硬合规阻断: AI 未读取 {target_blueprint} 蓝图即尝试修改 {' + '.join(target_files[:3])}。"
                f"beta 硬合规生效——此 task 被 REJECT。",
                detail=f"Action required: invoke blueprint_search.find_relevant_blueprint(task_description) "
                f"-> read {target_blueprint} blueprint §1-§5 -> retry task",
            )
        else:
            _add(
                f"AI 未读取 {target_blueprint} 蓝图即修改了目标文件 {' + '.join(target_files[:3])}",
                detail="experimental 软合规——WARNING 仅提醒，不阻断。升级到 beta 将以 error 阻断。",
            )
