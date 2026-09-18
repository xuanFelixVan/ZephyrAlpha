# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.rollback_verifier
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES] zephyr.infrastructure.rollback.__init__
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
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RollbackVerifier — 回滚后验证器。

依据: 蓝图 MOD-INF-021 §7 Phase 1.4 + §6.2 B16/B53

G0 门禁: 文件存在性 + YAML/JSON 语法校验 + Python AST 解析
__pycache__ 清理: 回滚后删除所有 .pyc bytecode 缓存
DB 一致性自愈: 比较 tasks 表与文件状态，不一致时自动修正
Differential Check: 回滚前后逐行比较 tasks/gates/events 表

# [ALGO_FLOW] external: docs/03_modules/_domain_infrastructure/algo_flow/rollback/rollback_verifier.yaml
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import ast
import json
import re
import shutil
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from zephyr.governance.persistence.sqlite_schema import _DDL_TASKS
from zephyr.shared.io.sqlite_factory import get_db_connection

# ── 活库真源指针（2026-09-19 由 governance.db 的 sqlite_master 逐字读取，非源码 DDL 推断）──
# gates 实列 = gate_run_id TEXT PRIMARY KEY
#              / gate_id TEXT NOT NULL
#              / passed INTEGER NOT NULL CHECK(passed IN (0,1))
#              / details TEXT NOT NULL DEFAULT '{}'
#              / artifact_path TEXT / session_id TEXT
#              / task_id TEXT / created_at TEXT NOT NULL
#   ⇒ 无 result 列：旧实现读 gate["result"] 每行抛 IndexError，被内层 except 吞成
#     "0 行需修"的静默空转（WP1 改 1 的病根本体）。
#   ⇒ gate_id 非唯一：实测 1791 行只有 1008 个 distinct gate_id ⇒ UPDATE 定位一律用主键 gate_run_id。
#   ⇒ gate_runs 与 gates 列集完全相同（同构兼容表，实测 6445 行）：本方法写的是 gates，不是 gate_runs。
#   ⇒ tasks.status 在活库是 `TEXT DEFAULT 'PENDING'`（**无 CHECK**，与 _DDL_TASKS 源码 DDL 已漂移），
#     所以"什么算脏状态"没有库内约束可依赖，只能从单一真源 _DDL_TASKS 派生 + 写前护栏（台账 R-A2/C-0）。
_SQL_TASKS_SCAN = "SELECT task_id, status FROM tasks"
_SQL_TASK_MARK_FAILED = "UPDATE tasks SET status='FAILED' WHERE task_id=?"
_SQL_GATES_SCAN = "SELECT gate_run_id, gate_id, passed, details FROM gates"
_SQL_GATE_MARK_NOT_PASSED = "UPDATE gates SET passed=0 WHERE gate_run_id=?"
_SQL_GATE_RESET_DETAILS = "UPDATE gates SET details=? WHERE gate_run_id=?"

# '{}' 逐字照抄活库 gates.details 的列默认值（DEFAULT '{}'）——不自造修复值。
_GATE_DETAILS_DEFAULT = "{}"
# 报告里保留的非法 details 原文长度（取证用，非真源值）
_GATE_DETAILS_PREVIEW = 120
# tasks.status 合法值集唯一真源 = _DDL_TASKS 的 CHECK(status IN (...))；派生失败即抛，不猜值。
_TASK_STATUS_CHECK_RE = re.compile(r"CHECK\s*\(\s*status\s+IN\s*\(\s*(?P<values>.*?)\s*\)\s*\)", re.DOTALL)
_QUOTED_LITERAL_RE = re.compile(r"^'[^']+'$")


class HealRefusedError(RuntimeError):
    """heal_db_consistency 的 fail-closed 信号：宁可拒写，也不冤改（C-0 护栏）。

    触发面（全部为"没有唯一现场来源就不能写"）：
    ① 目标表列集与活库实列不符（幻影结构）；② 词表无法从 _DDL_TASKS 派生；
    ③ 真写却没给 max_rows；④ 计划修正行数超过 max_rows。
    """


class PycacheGuardError(RuntimeError):
    """clean_pycache 三重护栏命中信号（WP1 改 2）：拒删并报错，绝不退化为"照删"。

    fail-safe 方向只有一个：故障只许退化为**不删**（旧实现是 `except Exception` +
    `logger.warning` 后继续返回计数，等于把"删了一半/删错了"也咽下去）。
    """


def _derive_task_status_vocabulary() -> frozenset[str]:
    """tasks.status 合法值集 ← 单一真源 `_DDL_TASKS` 的 CHECK(status IN (...))。

    治本（台账 R-A2/C-0）：旧实现硬编码 5 值，而真源声明 10 值 ⇒ READY/BLOCKED/WAITING/
    RETRY/VERIFIED 全被判脏；实测生产库 BLOCKED=152 + READY=78 = 230 行现值会被静默改成 FAILED。
    派生不出来（真源结构变更）一律抛 HealRefusedError —— 不猜词表。
    """
    match = _TASK_STATUS_CHECK_RE.search(_DDL_TASKS)
    if match is None:
        raise HealRefusedError("无法从 _DDL_TASKS 派生 tasks.status 合法值集（CHECK(status IN (...)) 未命中）")
    tokens = [t.strip() for t in match.group("values").split(",") if t.strip()]
    bad = [t for t in tokens if not _QUOTED_LITERAL_RE.match(t)]
    if not tokens or bad:
        raise HealRefusedError(f"_DDL_TASKS 的 tasks.status 词表形态异常，拒绝猜测合法值: tokens={tokens} bad={bad}")
    return frozenset(t.strip("'") for t in tokens)


def _fetch_rows(conn: sqlite3.Connection, sql: str, table: str) -> list[sqlite3.Row]:
    """读表；列集与活库实列不符时**抛出**（旧行为是被吞成"0 行需修"的假绿）。"""
    try:
        return conn.execute(sql).fetchall()
    except sqlite3.OperationalError as e:
        raise HealRefusedError(f"{table} 列集与活库实列不符 ⇒ 拒绝自愈（不读幻影列）: {e}") from e


def _json_is_parseable(text: str) -> bool:
    try:
        json.loads(text)
    except ValueError:  # json.JSONDecodeError 是 ValueError 子类
        return False
    return True


# 护栏②：可验证仓根的标记（任一存在即认为是仓根，与 .gitignore/AGENTS 现行口径一致）
_REPO_ROOT_MARKERS = (".git", "AGENTS.md")


def _require_verifiable_repo_root(project_root: Path) -> Path:
    """三重护栏之②：`_project_root` 自身必须可验证为仓根，否则整轮拒删（WP1 改 2）。

    旧实现拿 `_project_root.glob("**/__pycache__")` 的命中集直接 `shutil.rmtree`，靶子完全由
    root 决定、无深度上限无白名单——root 解析错即在错误根下递归删目录。本仓已有同类事故实物：
    `src/data/drift_audit/drift_events.db` 就是 project_root 误解析到 `src/` 的产物（同方案改 3）。
    """
    resolved = Path(project_root).resolve()
    if not any((resolved / marker).exists() for marker in _REPO_ROOT_MARKERS):
        raise PycacheGuardError(
            f"拒删 __pycache__：project_root={resolved} 缺 {list(_REPO_ROOT_MARKERS)} 任一标记"
            " ⇒ 不可验证为仓根（fail-safe：宁可不删）"
        )
    return resolved


def _escaped_pycache_targets(root: Path, candidates: list[Path]) -> list[Path]:
    """三重护栏之①：resolve() 后仍须落在 root 之内（拦 symlink/junction/软链外逃）。"""
    escaped: list[Path] = []
    for cache_dir in candidates:
        resolved = cache_dir.resolve()
        if not resolved.is_relative_to(root):
            escaped.append(cache_dir)
    return escaped


def _gate_row_fixes(gate: sqlite3.Row) -> list[tuple[str, tuple[object, ...], str]]:
    """单条 gates 行的修正计划（活库实列版）。空列表 = 该行一致。"""
    run_id = gate["gate_run_id"]
    fixes: list[tuple[str, tuple[object, ...], str]] = []
    if gate["passed"] not in (0, 1):
        # 修复方向 fail-closed：判定不可信时按"未通过"记（与旧支路 result->FAIL 同方向）
        fixes.append((_SQL_GATE_MARK_NOT_PASSED, (run_id,), f"gate {run_id}: passed={gate['passed']!r} -> 0"))
    raw_details = gate["details"]
    if isinstance(raw_details, str) and not _json_is_parseable(raw_details):
        fixes.append((
            _SQL_GATE_RESET_DETAILS,
            (_GATE_DETAILS_DEFAULT, run_id),
            f"gate {run_id}: details 非 JSON -> 列默认值（原值前 {_GATE_DETAILS_PREVIEW} 字符="
            f"{raw_details[:_GATE_DETAILS_PREVIEW]!r}）",
        ))
    return fixes


def _plan_gate_fixes(conn: sqlite3.Connection) -> list[tuple[str, tuple[object, ...], str]]:
    fixes: list[tuple[str, tuple[object, ...], str]] = []
    for gate in _fetch_rows(conn, _SQL_GATES_SCAN, "gates"):
        fixes.extend(_gate_row_fixes(gate))
    return fixes


def _plan_task_fixes(
    conn: sqlite3.Connection, valid_statuses: frozenset[str]
) -> list[tuple[str, tuple[object, ...], str]]:
    fixes: list[tuple[str, tuple[object, ...], str]] = []
    for task in _fetch_rows(conn, _SQL_TASKS_SCAN, "tasks"):
        status = task["status"]
        if status is None or status not in valid_statuses:
            fixes.append((
                _SQL_TASK_MARK_FAILED,
                (task["task_id"],),
                f"task {task['task_id']}: status {status!r} -> FAILED",
            ))
    return fixes


@dataclass
class G0Report:
    passed: bool
    missing_files: list[str]
    syntax_errors: list[str]
    lint_issues: list[str]


@dataclass
class DBHealReport:
    healed: bool
    tasks_fixed: int
    gates_fixed: int
    events_fixed: int
    details: list[str] = field(default_factory=list)
    # dry_run=True 时 tasks_fixed/gates_fixed 是"**计划**修正行数"，库未被写入；
    # 旧实现无此栏 ⇒ 计划与落库不可分（C-0 护栏要求先 dry-run）。
    dry_run: bool = False


@dataclass
class DifferentialReport:
    passed: bool
    rows_compared: int
    rows_mismatched: int
    table_changes: dict[str, int] = field(default_factory=dict)


def _collect_g0_targets(project_root: Path, files: list[str] | None) -> list[str]:
    if files:
        return files
    py_files = list(project_root.glob("src/**/*.py"))
    yaml_files = list(project_root.glob("**/*.yaml"))
    return [str(p) for p in py_files + yaml_files]


def _verify_python_file(f_path: Path, f_path_str: str, syntax_errors: list[str], lint_issues: list[str]) -> None:
    try:
        source = f_path.read_text(encoding="utf-8")
        ast.parse(source)
    except SyntaxError as e:
        syntax_errors.append(f"{f_path_str}: {e}")
    if f_path.name != "__init__.py":
        if "def " in source or "class " in source:
            if '"""' not in source[:5] and "'''" not in source[:5]:
                lint_issues.append(f"{f_path_str}: missing module docstring")


def _verify_yaml_file(f_path: Path, f_path_str: str, syntax_errors: list[str]) -> None:
    try:
        import yaml

        yaml.safe_load(f_path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        syntax_errors.append(f"{f_path_str}: YAML parse error: {e}")


def _verify_json_file(f_path: Path, f_path_str: str, syntax_errors: list[str]) -> None:
    try:
        json.loads(f_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        syntax_errors.append(f"{f_path_str}: JSON parse error: {e}")


def _verify_g0_file(f_path: Path, f_path_str: str, syntax_errors: list[str], lint_issues: list[str]) -> None:
    if f_path.suffix == ".py":
        _verify_python_file(f_path, f_path_str, syntax_errors, lint_issues)
    elif f_path.suffix in (".yaml", ".yml"):
        _verify_yaml_file(f_path, f_path_str, syntax_errors)
    elif f_path.suffix == ".json":
        _verify_json_file(f_path, f_path_str, syntax_errors)


class RollbackVerifier:
    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def project_root(self):
        """只读：project_root（Stage 4 公共化）。"""
        return self._project_root

    @project_root.setter
    def project_root(self, value):
        """写入：project_root（Stage 4 公共化）。"""
        self._project_root = value

    def g0_verify(self, files: list[str] | None = None) -> G0Report:
        target_files = _collect_g0_targets(self._project_root, files)

        missing: list[str] = []
        syntax_errors: list[str] = []
        lint_issues: list[str] = []

        for f_path_str in target_files:
            f_path = self._project_root / f_path_str
            if not f_path.exists():
                missing.append(f_path_str)
                continue
            _verify_g0_file(f_path, f_path_str, syntax_errors, lint_issues)

        passed = not missing and not syntax_errors and not lint_issues
        return G0Report(
            passed=passed,
            missing_files=missing,
            syntax_errors=syntax_errors,
            lint_issues=lint_issues,
        )

    def clean_pycache(self) -> int:
        """删除 `_project_root` 下所有 `__pycache__`（WP1 改 2：三重护栏 + fail-safe 只退化为不删）。

        三重护栏（命中任一 ⇒ 抛 PycacheGuardError 且**本轮零删除**，不退化为"照删"）：
        ① 每个靶子 `Path.resolve()` 后必须仍在 resolve() 后的 `_project_root` 之内
           （`is_relative_to`；拦 symlink/junction 外逃）；
        ② `_project_root` 自身必须可验证为仓根（存在 `.git` 或 `AGENTS.md`）；
        ③ 护栏校验全部前置成"先验完再删"——命中时一个目录都不删（旧实现边 glob 边 rmtree，
           第 2 个靶子越界时第 1 个已经被删掉了）。
        删除期的真失败（PermissionError 等）同样抛出 PycacheGuardError，不再
        `except Exception` + `logger.warning` 后返回计数（那是"看起来在工作"的假绿）。

        抛出不炸穿调用方：本方法生产调用方实测为 0（`git grep clean_pycache` 只命中本定义与
        tests/rollback 两文件；`scripts/rollback.py` 只调 `g0_verify`，`rollback_boot_integration`
        只构造 verifier 不调方法），故取 fail-closed 抛出而非返回可见对象。
        """
        root = _require_verifiable_repo_root(self._project_root)
        candidates = sorted(self._project_root.glob("**/__pycache__"), key=lambda p: str(p))
        escaped = _escaped_pycache_targets(root, candidates)
        if escaped:
            raise PycacheGuardError(
                f"拒删 __pycache__：{len(escaped)} 个靶子 resolve() 后落在 project_root={root} 之外 "
                f"⇒ {str(escaped[0])} 等（fail-safe：一个都不删）"
            )
        removed = 0
        for cache_dir in candidates:
            try:
                shutil.rmtree(cache_dir)
            except OSError as e:
                raise PycacheGuardError(
                    f"删除 {cache_dir} 失败（已成功删除 {removed} 个后中止，不再吞异常继续计数）: {e}"
                ) from e
            removed += 1
        return removed

    def heal_db_consistency(
        self,
        db_path: Path | None = None,
        *,
        dry_run: bool = True,
        max_rows: int | None = None,
    ) -> DBHealReport:
        """DB 一致性自愈（WP1 改 1 按活库实列重写 + 台账 R-A2/C-0 写前护栏）。

        行为变更（相对旧实现，务必读）：
        1. gates 支路按活库实列读 `passed`/`details`，UPDATE 以主键 `gate_run_id` 定位
           （旧支路读不存在的 `result` 列 ⇒ 每行 IndexError ⇒ 被内层 except 吞 ⇒ 恒 0 的空转）。
        2. 不再吞异常：表结构与活库实列不符 / 词表派生失败 / 缺 max_rows / 超上限 ⇒ 抛
           HealRefusedError（生产调用方实测为 0，故取 fail-closed 抛出而非降级）。
        3. **默认 dry_run=True**：只出计划不写库；真写须显式 dry_run=False **且**显式 max_rows
           （上限值无现场真源 ⇒ 本方法不自拍数字，由调用方决定，见 D-13）。
        4. tasks.status 合法值集从单一真源 `_DDL_TASKS` 派生（旧实现硬编码 5 值 ⇒ 生产库
           BLOCKED=152/READY=78 共 230 行会被静默改成 FAILED）。
        """
        db = db_path or (self._project_root / "data" / "databases" / "governance.db")
        if not db.exists():
            return DBHealReport(healed=False, tasks_fixed=0, gates_fixed=0, events_fixed=0, details=["DB not found"])
        if not dry_run and max_rows is None:
            raise HealRefusedError(
                "dry_run=False 必须显式给出 max_rows：修正行数上限没有现场真源可读，本方法不自拍数字（D-13）"
            )

        valid_statuses = _derive_task_status_vocabulary()
        conn = get_db_connection(str(db))
        try:
            conn.row_factory = sqlite3.Row
            task_fixes = _plan_task_fixes(conn, valid_statuses)
            gate_fixes = _plan_gate_fixes(conn)
            planned = task_fixes + gate_fixes
            if max_rows is not None and len(planned) > max_rows:
                raise HealRefusedError(f"计划修正 {len(planned)} 行 > 上限 max_rows={max_rows} ⇒ 拒写（C-0 护栏）")
            notes: list[str] = []
            for sql, params, note in planned:
                if not dry_run:
                    conn.execute(sql, params)
                notes.append(note)
            if not dry_run:
                conn.commit()
        finally:
            conn.close()

        return DBHealReport(
            healed=bool(planned),
            tasks_fixed=len(task_fixes),
            gates_fixed=len(gate_fixes),
            events_fixed=0,
            details=notes,
            dry_run=dry_run,
        )

    def differential_check(self, db_before: Path, db_after: Path) -> DifferentialReport:
        rows_compared = 0
        rows_mismatched = 0
        table_changes: dict[str, int] = {}

        try:
            conn_before = get_db_connection(str(db_before))
            conn_after = get_db_connection(str(db_after))
            conn_before.row_factory = sqlite3.Row
            conn_after.row_factory = sqlite3.Row

            for table in ("tasks", "gates", "events"):
                rows_b = conn_before.execute(f"SELECT COUNT(*) as cnt FROM {table}").fetchone()
                rows_a = conn_after.execute(f"SELECT COUNT(*) as cnt FROM {table}").fetchone()
                cnt_b = rows_b["cnt"] if rows_b else 0
                cnt_a = rows_a["cnt"] if rows_a else 0
                diff = cnt_b - cnt_a
                rows_compared += max(cnt_b, cnt_a)
                if diff != 0:
                    rows_mismatched += abs(diff)
                    table_changes[table] = diff

            conn_before.close()
            conn_after.close()

            passed = rows_mismatched == 0
            return DifferentialReport(
                passed=passed,
                rows_compared=rows_compared,
                rows_mismatched=rows_mismatched,
                table_changes=table_changes,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            return DifferentialReport(
                passed=False,
                rows_compared=0,
                rows_mismatched=0,
                table_changes={"error": str(e)},
            )
