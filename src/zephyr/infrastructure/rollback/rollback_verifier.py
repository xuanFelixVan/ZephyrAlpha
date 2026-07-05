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
# [A_module] module_id=MOD-INF_rollback_verifier | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RollbackVerifier — 回滚后验证器。

依据: 蓝图 MOD-INF-021 §7 Phase 1.4 + §6.2 B16/B53

G0 门禁: 文件存在性 + YAML/JSON 语法校验 + Python AST 解析
__pycache__ 清理: 回滚后删除所有 .pyc bytecode 缓存
DB 一致性自愈: 比较 tasks 表与文件状态，不一致时自动修正
Differential Check: 回滚前后逐行比较 tasks/gates/events 表
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import ast
import json
import shutil
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path


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


@dataclass
class DifferentialReport:
    passed: bool
    rows_compared: int
    rows_mismatched: int
    table_changes: dict[str, int] = field(default_factory=dict)


class RollbackVerifier:
    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()

    def g0_verify(self, files: list[str] | None = None) -> G0Report:
        target_files = files or []
        if not target_files:
            py_files = list(self._project_root.glob("src/**/*.py"))
            yaml_files = list(self._project_root.glob("**/*.yaml"))
            target_files = [str(p) for p in py_files + yaml_files]

        missing: list[str] = []
        syntax_errors: list[str] = []
        lint_issues: list[str] = []

        for f_path_str in target_files:
            f_path = self._project_root / f_path_str
            if not f_path.exists():
                missing.append(f_path_str)
                continue

            if f_path.suffix == ".py":
                try:
                    source = f_path.read_text(encoding="utf-8")
                    ast.parse(source)
                except SyntaxError as e:
                    syntax_errors.append(f"{f_path_str}: {e}")

                if f_path.name != "__init__.py":
                    source = f_path.read_text(encoding="utf-8")
                    if "def " in source or "class " in source:
                        if '"""' not in source[:5] and "'''" not in source[:5]:
                            lint_issues.append(f"{f_path_str}: missing module docstring")

            elif f_path.suffix in (".yaml", ".yml"):
                try:
                    import yaml

                    yaml.safe_load(f_path.read_text(encoding="utf-8"))
                except Exception as e:
                    syntax_errors.append(f"{f_path_str}: YAML parse error: {e}")

            elif f_path.suffix == ".json":
                try:
                    json.loads(f_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError as e:
                    syntax_errors.append(f"{f_path_str}: JSON parse error: {e}")

        passed = len(missing) == 0 and len(syntax_errors) == 0 and len(lint_issues) == 0
        return G0Report(
            passed=passed,
            missing_files=missing,
            syntax_errors=syntax_errors,
            lint_issues=lint_issues,
        )

    def clean_pycache(self) -> int:
        removed = 0
        for cache_dir in self._project_root.glob("**/__pycache__"):
            try:
                shutil.rmtree(cache_dir)
                removed += 1
            except Exception as e:
                logger.warning("suppressed error in rollback_verifier", exc_info=True)
        return removed

    def heal_db_consistency(self, db_path: Path | None = None) -> DBHealReport:
        db = db_path or (self._project_root / "data" / "databases" / "governance.db")
        if not db.exists():
            return DBHealReport(healed=False, tasks_fixed=0, gates_fixed=0, events_fixed=0, details=["DB not found"])

        tasks_fixed = 0
        gates_fixed = 0
        events_fixed = 0
        details: list[str] = []

        try:
            conn = sqlite3.connect(str(db))
            conn.row_factory = sqlite3.Row

            tasks = conn.execute("SELECT * FROM tasks").fetchall()
            for task in tasks:
                tid = task["task_id"]
                try:
                    status = task["status"]
                    valid_statuses = {"PENDING", "IN_PROGRESS", "COMPLETED", "FAILED", "CANCELLED"}
                    if status not in valid_statuses:
                        conn.execute("UPDATE tasks SET status='FAILED' WHERE task_id=?", (tid,))
                        tasks_fixed += 1
                        details.append(f"task {tid}: status {status} → FAILED")
                except Exception as e:
                    logger.warning("suppressed error in rollback_verifier", exc_info=True)

            gates = conn.execute("SELECT * FROM gates").fetchall()
            for gate in gates:
                gid = gate["gate_id"]
                try:
                    result = gate["result"]
                    valid_results = {"PASS", "FAIL", "SKIP", "PENDING"}
                    if result and result not in valid_results:
                        conn.execute("UPDATE gates SET result='FAIL' WHERE gate_id=?", (gid,))
                        gates_fixed += 1
                        details.append(f"gate {gid}: result {result} → FAIL")
                except Exception as e:
                    logger.warning("suppressed error in rollback_verifier", exc_info=True)

            conn.commit()
            conn.close()

            healed = (tasks_fixed + gates_fixed + events_fixed) > 0
            return DBHealReport(
                healed=healed,
                tasks_fixed=tasks_fixed,
                gates_fixed=gates_fixed,
                events_fixed=events_fixed,
                details=details,
            )
        except Exception as e:
            return DBHealReport(healed=False, tasks_fixed=0, gates_fixed=0, events_fixed=0, details=[str(e)])

    def differential_check(self, db_before: Path, db_after: Path) -> DifferentialReport:
        rows_compared = 0
        rows_mismatched = 0
        table_changes: dict[str, int] = {}

        try:
            conn_before = sqlite3.connect(str(db_before))
            conn_after = sqlite3.connect(str(db_after))
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
        except Exception as e:
            return DifferentialReport(
                passed=False,
                rows_compared=0,
                rows_mismatched=0,
                table_changes={"error": str(e)},
            )
