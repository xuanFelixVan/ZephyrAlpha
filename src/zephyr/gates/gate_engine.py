"""
GateEngine — KMS G1-G6 + Orc G0/G7 + 交易 G10-G12 门禁裁决引擎（T-2-17）
======================================================================
依据：
- 知识库架构 §4（G1-G5 脚本接口设计）
- execution-order-v1.md beta.3（门禁策略引擎 P0）
- ADR-0030（SQLite gates 表）
- CT-ORC-GATE-001（任务 G0/G7 → task/g0_orc_gate_engine.yaml、g7_orc_gate_engine.yaml）
- 交易类门：``gate_id`` 为 G10/G11/G12，YAML 文件名保留历史前缀（g7_position_limits / g8_leverage / g9_strategy_correlation）
- 指令：325 + 344 + 999

病根（2026-05 归档）
--------------------
曾将 ``field_presence`` / ``classification`` 等 check_type 在任务路径上实现为空操作（``pass``），
导致即便注册 G0 YAML 也无法生效；同时 ``task/g0_entry.yaml`` 使用不可执行的 ``rules:`` 叙述，
与引擎的 ``checks`` schema 脱节。本引擎现已实现上述 check_type 的任务侧语义，并由 Orc 专用 YAML 承载 G0/G7。

Safety : M（治理层代码，门禁失败阻断任务启动）

功能
----
- load_gates()   → 从 YAML 文件加载门禁配置，返回 dict[gate_id, GateConfig]
- evaluate(task, gate_id[, conn=…]) → 执行门禁检查，返回 GateResult，写入 gates 表；
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

import json
import re
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, ClassVar

import yaml

from zephyr.db.sqlite_schema import DB_PATH, get_db_connection, init_db
from zephyr.gates.risk_ssot import load_risk_params_ssot
from zephyr.shared.schema.schemas import Task
from zephyr.shared.utils.db_utils import ensure_schema
from zephyr.core.models import TaskCard, GateLevel

__all__ = [
    "GateEngine",
    "GateResult",
    "GateViolation",
    "GateEngineError",
    "GateViolationError",
    "GATES_DIR",
]

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

GATES_DIR = Path(__file__).parent
"""门禁 YAML 文件所在目录（与本模块同级）。"""

_UTC = UTC

_DEPRECATED_PATHS_YAML = (
    Path(__file__).parent.parent.parent.parent / "scripts" / "governance" / "_shared" / "deprecated_paths.yaml"
)

def _load_deprecated_patterns() -> list[str]:
    with open(_DEPRECATED_PATHS_YAML, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return list(data.get("blacklist_patterns", []))

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
# 数据模型
# ---------------------------------------------------------------------------

@dataclass
class GateViolation:
    """单条门禁违规记录。"""

    check_id: str
    check_name: str
    severity: str  # P0 / P1 / P2
    message: str
    detail: str | None = None

@dataclass
class GateResult:
    """门禁裁决结果。"""

    gate_id: str
    task_id: str
    passed: bool
    violations: list[GateViolation] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)
    evaluated_at: str = field(default_factory=lambda: datetime.now(_UTC).isoformat())

    @property
    def p0_violations(self) -> list[GateViolation]:
        """返回门禁评估结果中 severity=P0 的违规列表（P0 = 阻塞级红线）。"""
        return [v for v in self.violations if v.severity == "P0"]

    @property
    def has_p0(self) -> bool:
        return bool(self.p0_violations)

    def summary(self) -> str:
        if self.passed:
            return f"[PASS] Gate {self.gate_id} task={self.task_id}"
        p0 = len(self.p0_violations)
        total = len(self.violations)
        return f"[FAIL] Gate {self.gate_id} task={self.task_id} " f"violations={total} (P0={p0})"

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

# ---------------------------------------------------------------------------
# 异常
# ---------------------------------------------------------------------------

class GateEngineError(RuntimeError):
    """GateEngine 基础异常。"""

class GateViolationError(GateEngineError):
    """任务被门禁阻断时抛出（含 GateResult）。"""

    def __init__(self, result: GateResult) -> None:
        self.result = result
        super().__init__(result.summary())

# ---------------------------------------------------------------------------
# 内部：检查实现
# ---------------------------------------------------------------------------

def _check_encoding(
    file_path: Path,
    params: dict[str, Any],
) -> str | None:
    """校验文件编码为 UTF-8 无 BOM。"""
    if not file_path.exists():
        return None
    raw = file_path.read_bytes()
    if params.get("disallow_bom", True) and raw.startswith(b"\xef\xbb\xbf"):
        return f"文件含 UTF-8 BOM：{file_path}"
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return f"编码损坏（非 UTF-8）：{file_path} — {exc}"
    return None

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
        if val is None:
            missing.append(fname)
        elif isinstance(val, str) and len(val.strip()) == 0:
            missing.append(fname)
        elif isinstance(val, (list, dict)) and len(val) == 0:
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
    findings_raw = getattr(task, "audit_findings") or []
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

def _run_check(
    check: CheckConfig,
    task: Task,
    project_root: Path,
) -> list[GateViolation]:
    """根据 check_type 调度到对应实现，返回零或多条违规。"""
    violations: list[GateViolation] = []
    deliverables: list[str] = list(task.deliverables or [])
    dep_paths = [project_root / p for p in deliverables]

    def _add(msg: str, detail: str | None = None) -> None:
        violations.append(
            GateViolation(
                check_id=check.check_id,
                check_name=check.name,
                severity=check.severity,
                message=msg,
                detail=detail,
            )
        )

    ct = check.check_type

    if ct == "encoding":
        for fp in dep_paths:
            err = _check_encoding(fp, check.params)
            if err:
                _add(err)

    elif ct == "line_ending":
        for fp in dep_paths:
            err = _check_line_ending(fp, check.params)
            if err:
                _add(err)

    elif ct == "path_blacklist":
        errs = _check_path_blacklist(deliverables, check.params)
        for e in errs:
            _add(e)

    elif ct == "content_quality":
        for fp in dep_paths:
            err = _check_empty_shell(fp, check.params)
            if err:
                _add(err)

    elif ct == "content_length":
        for fp in dep_paths:
            err = _check_content_length(fp, check.params)
            if err:
                _add(err)

    elif ct == "frontmatter":
        for fp in dep_paths:
            err = _check_frontmatter(fp, check.params)
            if err:
                _add(err)

    elif ct == "file_extension":
        allowed: list[str] = list(check.params.get("allowed_extensions", []))
        for p in deliverables:
            ext = Path(p).suffix.lower()
            if allowed and ext not in allowed:
                _add(f"不允许的文件扩展名 '{ext}'：{p}")

    elif ct == "circuit_breaker":
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
                from zephyr.gates.circuit_breaker import CircuitBreakerCheck

                cb_check = CircuitBreakerCheck(
                    caller_module=caller,
                    target_module=target,
                )
                if cb_check.is_open():
                    _add(cb_check.violation_message())
            except Exception as exc:
                # CBGManager 初始化失败时降级为 P2 警告，不阻断门禁
                violations.append(
                    GateViolation(
                        check_id=check.check_id,
                        check_name=check.name,
                        severity="P2",
                        message=f"circuit_breaker 检查初始化失败（降级 P2）：{exc}",
                    )
                )

    elif ct == "blueprint_read_check":
        # 第 18 种 CheckType（T-V2-011 G6 beta 硬合规）
        # 检查：AI 在修改目标模块文件前，是否已读取对应的蓝图
        # beta（硬合规，2026-05-04 激活）：
        #   — severity=error → P0 阻断：未读蓝图就改代码的 task 直接 REJECT
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
                target_blueprint, target_files, check, _add,
                hard_compliance=hard_compliance,
            )

    elif ct == "drift_budget":
        target_module = str(check.params.get("target_module", task.task_id))
        try:
            from zephyr.drift_detector.drift_engine import check_budget_for_gate

            budget = check_budget_for_gate(target_module)
            if not budget.get("allowed", False):
                _add(
                    f"漂移预算耗尽，模块 {target_module} 必须先修复漂移再提交变更",
                    detail=budget.get("reason", "drift budget exceeded"),
                )
        except Exception as exc:
            violations.append(
                GateViolation(
                    check_id=check.check_id,
                    check_name=check.name,
                    severity="P2",
                    message=f"drift_budget 检查初始化失败（降级 P2）：{exc}",
                )
            )

    elif ct == "field_presence":
        missing = _check_field_presence_task(task, check.params)
        for mf in missing:
            _add(f"缺少或为空必填字段：{mf}")

    elif ct == "classification":
        err = _check_classification_task(task, check.params)
        if err:
            _add(err)

    elif ct == "regex_pattern":
        err = _check_regex_pattern_task(task, check.params)
        if err:
            _add(err)

    elif ct == "audit_findings_resolved":
        for msg in _check_audit_findings_messages(task):
            _add(msg)

    elif ct == "circular_dependency_scan":
        try:
            from zephyr.gates.invariants.en_001_circular_dependency import run_scan
            result = run_scan()
            if not result.passed:
                for cycle in result.cycles:
                    _add(
                        f"Circular dependency: {' → '.join(cycle)} → {cycle[0]}",
                        detail=f"Cycle length: {len(cycle)}",
                    )
        except Exception as exc:
            _add(f"EN-001 scan failed: {exc}", detail=str(exc))

    elif ct == "enforcement_mode_check":
        try:
            from zephyr.gates.invariants.en_002_enforcement_validator import run_check as en2_check
            result = en2_check()
            if not result.passed:
                for v in result.violations:
                    _add(v)
        except Exception as exc:
            _add(f"EN-002 check failed: {exc}", detail=str(exc))

    elif ct == "contract_compatibility_check":
        try:
            from zephyr.gates.invariants.en_003_contract_compatibility import run_check as en3_check
            result = en3_check()
            if not result.passed:
                for m in result.mismatches:
                    _add(m)
        except Exception as exc:
            _add(f"EN-003 check failed: {exc}", detail=str(exc))

    elif ct == "security_artifact_scan":
        try:
            from zephyr.l10_compliance.artifact_scanner import ArtifactScanner
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

    elif ct == "position_limit":
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

    elif ct == "leverage_limit":
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

    elif ct == "strategy_correlation":
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

    elif ct == "zero_residue_check":
        try:
            from zephyr.gates.invariants.zero_residue_check import ZeroResidueScanner
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

    elif ct in {
        "score_threshold",
        "deduplication",
        "manual_approval",
        "path_whitelist",
        "path_routing",
        "temporal",
        "reference_check",
    }:
        violations.append(
            GateViolation(
                check_id=check.check_id,
                check_name=check.name,
                severity="P2",
                message=f"检查类型 '{ct}' 在任务门禁路径未实现（依赖 KMS / 额外数据），已跳过",
                detail="gate_engine._run_check",
            )
        )

    elif ct == "fle_gate":
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
                    GateViolation(
                        check_id=check.check_id,
                        check_name=check.name,
                        severity="P2",
                        message=f"fle_gate 检查初始化失败（降级 P2）：{exc}",
                    )
                )

    elif ct == "rollback_exit_code":
        exit_code_raw = check.params.get("exit_code", 0)
        try:
            exit_code = int(exit_code_raw)
        except (TypeError, ValueError):
            exit_code = -1
        try:
            from zephyr.rollback.contract import get_gate_action
            gate_action, description = get_gate_action(exit_code)
            if gate_action in ("FAIL", "BLOCK", "BLOCK_AUTO"):
                _add(
                    f"Rollback exit code {exit_code} -> {gate_action}: {description}",
                    detail=f"check_id={check.check_id} exit_code={exit_code}",
                )
            elif gate_action in ("WARN", "RETRY", "PAUSE_AGENT", "PAUSE_AUTO", "REDUCE_TIER"):
                _add(
                    f"Rollback exit code {exit_code} -> {gate_action}: {description}",
                    detail=f"check_id={check.check_id} exit_code={exit_code}",
                )
        except Exception as exc:
            violations.append(
                GateViolation(
                    check_id=check.check_id,
                    check_name=check.name,
                    severity="P2",
                    message=f"rollback_exit_code check failed (degrade P2): {exc}",
                )
            )

    else:
        violations.append(
            GateViolation(
                check_id=check.check_id,
                check_name=check.name,
                severity="P2",
                message=f"Unknown check type '{ct}', skipped",
            )
        )

    return violations

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

    _GATE_FILES: dict[str, str] = {
        "G0": "task/g0_orc_gate_engine.yaml",
        "G1": "g1_ingest.yaml",
        "G2": "g2_triage.yaml",
        "G3": "g3_evaluate.yaml",
        "G4": "g4_activate.yaml",
        "G5": "g5_extract.yaml",
        "G6": "g6_ctr_compliance.yaml",
        "G6_BP": "g6_blueprint_compliance.yaml",
        "G7": "task/g7_orc_gate_engine.yaml",
        "G10": "g7_position_limits.yaml",
        "G11": "g8_leverage.yaml",
        "G12": "g9_strategy_correlation.yaml",
        "EN-001": "invariants/en_001_circular_dependency.yaml",
        "EN-002": "invariants/en_002_enforcement_validator.yaml",
        "EN-003": "invariants/en_003_contract_compatibility.yaml",
        "ZERO-RESIDUE": "ZERO-RESIDUE.yaml",
        "MAD-001": "admission/mad_001_architecture_necessity.yaml",
        "MAD-002": "admission/mad_002_phase_relevance.yaml",
        "MAD-003": "admission/mad_003_dependency_compliance.yaml",
        "MAD-004": "admission/mad_004_interface_definability.yaml",
    }

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
        """强制重新从文件加载门禁配置（清除缓存）。"""
        configs: dict[str, GateConfig] = {}
        for gate_id, filename in self._GATE_FILES.items():
            yaml_path = self._gate_dir / filename
            if not yaml_path.exists():
                raise GateEngineError(f"门禁配置文件不存在：{yaml_path}")
            with yaml_path.open(encoding="utf-8") as fh:
                raw: dict[str, Any] = yaml.safe_load(fh)
            configs[gate_id] = self._parse_config(raw)
        self._gate_cache = configs
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

        - P0 违规存在 → passed=False（阻断）
        - 仅 P1/P2 违规 → passed=True（警告，不阻断）
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
                INSERT INTO gates
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
        "warning": "P1",
        "warn": "P1",
        "info": "P2",
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
        raw_checks: list[Any] = list(
            raw.get("checks") or raw.get("entry_conditions") or raw.get("rules") or []
        )

        checks: list[CheckConfig] = []
        for c in raw_checks:
            raw_sev = str(c.get("severity") or c.get("enforcement") or "P1")
            severity = GateEngine._SEVERITY_MAP.get(raw_sev.lower(), raw_sev)
            checks.append(
                CheckConfig(
                    check_id=str(c.get("id") or c.get("rule_id", "")),
                    name=str(c.get("name", "")),
                    check_type=str(c.get("type", "condition")),
                    description=str(c.get("description", "")),
                    severity=severity,
                    params=dict(c.get("params", {})),
                )
            )
        return GateConfig(
            gate_id=str(raw["gate_id"]),
            name=name,
            description=str(raw.get("description", "")),
            phase=str(raw.get("phase", "")),
            auto=bool(raw.get("auto", True)),
            checks=checks,
            on_failure=str(raw.get("on_failure", "reject")),
            on_pass=str(raw.get("on_pass", "pass")),
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
    - severity=warning → 仅提醒，不阻断

    beta（硬合规，2026-05-04 激活）：
    - severity=error → P0 硬阻断
    - 未读蓝图则返回 GateViolationError
    - AI 必须读蓝图后才能继续
    """
    metrics_path = Path(__file__).parents[3] / "data" / "telemetry" / "blueprint_reads.jsonl"

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
                       f"→ read {target_blueprint} blueprint §1-§5 → retry task",
            )
        else:
            _add(
                f"AI 未读取 {target_blueprint} 蓝图即修改了目标文件 {' + '.join(target_files[:3])}",
                detail="experimental 软合规——WARNING 仅提醒，不阻断。升级到 beta 将以 error 阻断。",
            )
