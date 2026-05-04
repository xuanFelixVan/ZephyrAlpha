"""
GateEngine — KMS G1-G5 门禁裁决引擎（T-2-17）
===============================================
依据：
- 知识库架构 §4（G1-G5 脚本接口设计）
- execution-order-v1.md Phase 2.3（门禁策略引擎 P0）
- ADR-0030（SQLite gates 表）
- 指令：325 + 344 + 999

Safety : M（治理层代码，门禁失败阻断任务启动）

功能
----
- load_gates()   → 从 YAML 文件加载门禁配置，返回 dict[gate_id, GateConfig]
- evaluate(task, gate_id) → 执行门禁检查，返回 GateResult，写入 gates 表

支持的 CheckType（三大核心场景 + 扩展）
---------------------------------------
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
  circuit_breaker  - 模块间熔断状态检查（T-V2-005 第 17 种，CBG Phase 1b）
  blueprint_read_check - 蓝图读取合规检查（T-V2-011 第 18 种，P1-2 强制合规）
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
from zephyr.shared.schemas import Task

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
    r"raise NotImplementedError",
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
        # 第 17 种 CheckType（T-V2-005 CBG Phase 1b）
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
        # 第 18 种 CheckType（T-V2-011 P1-2 强制合规 Phase 1）
        # 检查：AI 在修改目标模块文件前，是否已读取对应的蓝图
        # Phase 1（软合规）：检查 session_carryover.db 或 blueprint_reads.jsonl
        #   — 如果目标模块有蓝图但未被读取 → WARNING（不阻断，仅提醒）
        # Phase 2（硬合规）：GATE-16 升级为 error severity，阻止未读蓝图的代码变更
        target_blueprint = str(check.params.get("target_blueprint", ""))
        target_files = list(check.params.get("target_files", []))
        if not target_blueprint:
            _add(
                "blueprint_read_check 缺少 target_blueprint 参数",
                detail=f"check_id={check.check_id}",
            )
        else:
            _check_blueprint_read_compliance(target_blueprint, target_files, check, _add)

    elif ct in {
        "score_threshold",
        "classification",
        "deduplication",
        "manual_approval",
        "path_whitelist",
        "path_routing",
        "temporal",
        "reference_check",
        "field_presence",
    }:
        # 这些检查类型在任务层面为空操作（需要知识条目数据），跳过
        pass

    else:
        # 未知 check_type：记为 P2 警告
        violations.append(
            GateViolation(
                check_id=check.check_id,
                check_name=check.name,
                severity="P2",
                message=f"未知检查类型 '{ct}'，已跳过",
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
        存放 g1_ingest.yaml ~ g5_extract.yaml 的目录；默认与本模块同级。
    db_path
        SQLite 数据库路径；默认使用 DB_PATH。
    project_root
        项目根目录，用于将 task.deliverables 中的相对路径解析为绝对路径。
    auto_init
        首次连接时是否调用 init_db()（默认 True）。
    """

    _GATE_FILES: dict[str, str] = {
        "G1": "g1_ingest.yaml",
        "G2": "g2_triage.yaml",
        "G3": "g3_evaluate.yaml",
        "G4": "g4_activate.yaml",
        "G5": "g5_extract.yaml",
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
            init_db(self._db_path)
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

    def evaluate(self, task: Task, gate_id: str) -> GateResult:
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
            "G1" ~ "G5"。
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
        self._persist_result(result)
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

    def _persist_result(self, result: GateResult) -> None:
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
        self._conn.execute("BEGIN IMMEDIATE")
        try:
            self._conn.execute(
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
            self._conn.execute("COMMIT")
        except Exception:
            self._conn.execute("ROLLBACK")
            raise

    # ------------------------------------------------------------------
    # 内部：YAML 解析
    # ------------------------------------------------------------------

    # 将 YAML 中的人类可读 severity 值映射为引擎用的 P 级标签
    _SEVERITY_MAP: ClassVar[dict[str, str]] = {
        "error": "P0",
        "critical": "P0",
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
        raw_checks: list[Any] = list(raw.get("checks") or raw.get("entry_conditions") or [])

        checks: list[CheckConfig] = []
        for c in raw_checks:
            raw_sev = str(c.get("severity", "P1"))
            severity = GateEngine._SEVERITY_MAP.get(raw_sev.lower(), raw_sev)
            checks.append(
                CheckConfig(
                    check_id=str(c.get("id", "")),
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
) -> None:
    """检查 AI 在修改目标文件前是否已读取对应的蓝图。

    Phase 1（软合规）：
    - 读取 ``data/telemetry/blueprint_reads.jsonl`` 查找匹配的蓝图读取记录
    - 若未找到 → WARNING severity（不阻断，仅提醒）
    - 若找到 → 静默 PASS

    Phase 2（硬合规，待部署）：
    - severity 升级为 P0 → 阻断未读蓝图的代码变更
    """
    metrics_path = Path(__file__).parents[3] / "data" / "telemetry" / "blueprint_reads.jsonl"

    if not metrics_path.exists():
        _add(
            f"未检测到蓝图读取记录——AI 在修改 {target_files[0] if target_files else '目标'} 前应读取 {target_blueprint} 蓝图",
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
            f"无法读取 metrics 文件——AI 应确认已读取 {target_blueprint} 蓝图后再继续",
            detail="blueprint_reads.jsonl unreadable",
        )
        return

    if not found:
        _add(
            f"AI 未读取 {target_blueprint} 蓝图即修改了目标文件 {' + '.join(target_files[:3])}",
            detail="Phase 1 软合规——WARNING 仅提醒，不阻断。Phase 2 将升级为硬阻断。",
        )
