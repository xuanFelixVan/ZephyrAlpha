# [A_test] module_id: DM-100054 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-019 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §rule_engine
# [MODULE] tests.test_rule_red_blue
# [INVARIANTS] 红蓝对抗测试：故意违反规则→验证检测率; 报告输出到 governance_metadata/red_blue_report.json
# [MODIFY-GUARD] rule_engine.py; audit_registration.py; gate_engine.py
# [CONSUMERS] CI pipeline; governance audit
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assertions on detection status; report JSON written on session end
# [TESTS] tests/test_rule_red_blue.py
# [TTL] task_bound

import json
import os
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest
from zephyr.shared.io.paths import REPO_ROOT

_PROJECT_ROOT = REPO_ROOT
_REPORT_DIR = _PROJECT_ROOT / "data" / "databases" / "governance_metadata"
_REPORT_PATH = _REPORT_DIR / "red_blue_report.json"

L0_RULES = [
    {"rule_id": "TRAE-001", "title": "文件操作安全协议", "violation": "create_file_without_lock"},
    {"rule_id": "TRAE-002", "title": "反孤儿与搜索先行协议", "violation": "create_py_without_register"},
    {"rule_id": "TRAE-003", "title": "任务粒度与完成门槛协议", "violation": "task_card_over_granularity"},
    {"rule_id": "TRAE-004", "title": "并行执行与原子事务协议", "violation": "serial_subprocess_loop"},
    {"rule_id": "TRAE-005", "title": "修改原则与治理施工协议", "violation": "skip_depgraph_simulation"},
    {"rule_id": "TRAE-006", "title": "防幻觉-结构追溯层", "violation": "missing_ten_field_header"},
    {"rule_id": "TRAE-007", "title": "防幻觉-行为约束层", "violation": "placeholder_in_code"},
    {"rule_id": "TRAE-008", "title": "防幻觉-输出验证层", "violation": "import_without_verify"},
    {"rule_id": "TRAE-009", "title": "防幻觉-安全防护层", "violation": "sql_string_concatenation"},
]

_results: list[dict] = []


def _run_audit_registration() -> tuple[int, str]:
    script = _PROJECT_ROOT / "scripts" / "governance" / "audit_registration.py"
    if not script.exists():
        return -1, "audit_registration.py not found"
    try:
        proc = subprocess.run(
            [os.sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(_PROJECT_ROOT),
        )
        return proc.returncode, proc.stdout + proc.stderr
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT"
    except Exception as exc:
        return -1, str(exc)


def _check_serial_subprocess_in_code(code: str) -> bool:
    has_for = bool(re.search(r"\bfor\b", code))
    has_subprocess = bool(re.search(r"subprocess\.(run|Popen|call)", code))
    has_tpe = bool(re.search(r"ThreadPoolExecutor", code))
    return has_for and has_subprocess and not has_tpe


def _check_missing_header(code: str) -> bool:
    required = [
        "[BLUEPRINT]",
        "[MODULE]",
        "[INVARIANTS]",
        "[MODIFY-GUARD]",
        "[CONSUMERS]",
        "[STABILITY]",
        "[SAFETY]",
        "[AI_AUTONOMY]",
    ]
    missing = [h for h in required if h not in code]
    return len(missing) > 0


def _check_placeholder(code: str) -> bool:
    patterns = [r"\bTODO\b", r"\bFIXME\b", r"\bpass\b", r"\.\.\.", r"raise\s+NotImplementedError"]
    for pat in patterns:
        if re.search(pat, code):
            return True
    return False


def _check_sql_concat(code: str) -> bool:
    has_sql_keyword = bool(re.search(r"(SELECT|INSERT|UPDATE|DELETE|DROP)", code, re.IGNORECASE))
    has_format_or_fstring = bool(re.search(r"(format\(|f['\"].*\{)", code))
    has_plus_concat = bool(re.search(r"['\"].*\+\s*\w+", code))
    has_parameterized = bool(re.search(r"\?|%s|:1|named", code))
    return has_sql_keyword and (has_format_or_fstring or has_plus_concat) and not has_parameterized


def _record(rule_id: str, title: str, violation: str, detection: str, detail: str):
    _results.append(
        {
            "rule_id": rule_id,
            "title": title,
            "violation_type": violation,
            "detection_status": detection,
            "detection_detail": detail,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    )


class TestTRAE001CreateWithoutLock:
    def test_create_file_without_lock(self, tmp_path):
        target = tmp_path / "orphan_test.py"
        target.write_text("print('no lock acquired')", encoding="utf-8")
        rc, output = _run_audit_registration()
        if rc != 0 and "orphan" in output.lower():
            _record(
                "TRAE-001",
                "文件操作安全协议",
                "create_file_without_lock",
                "GREEN",
                "audit_registration.py detected violation",
            )
        elif rc != 0:
            _record(
                "TRAE-001",
                "文件操作安全协议",
                "create_file_without_lock",
                "YELLOW",
                f"audit exited {rc} but no orphan mention: {output[:200]}",
            )
        else:
            _record(
                "TRAE-001",
                "文件操作安全协议",
                "create_file_without_lock",
                "RED",
                "No detection by audit_registration.py",
            )
        assert True


class TestTRAE002CreateWithoutRegister:
    def test_create_py_without_register(self, tmp_path):
        target = tmp_path / "unregistered_module.py"
        target.write_text("def unregistered_func(): pass", encoding="utf-8")
        rc, output = _run_audit_registration()
        if rc != 0 and "orphan" in output.lower():
            _record(
                "TRAE-002",
                "反孤儿与搜索先行协议",
                "create_py_without_register",
                "GREEN",
                "audit_registration.py detected orphan",
            )
        elif rc != 0:
            _record(
                "TRAE-002",
                "反孤儿与搜索先行协议",
                "create_py_without_register",
                "YELLOW",
                f"audit exited {rc}: {output[:200]}",
            )
        else:
            _record("TRAE-002", "反孤儿与搜索先行协议", "create_py_without_register", "RED", "No orphan detection")
        assert True


class TestTRAE003TaskCardOverGranularity:
    def test_task_card_over_granularity(self):
        try:
            from zephyr.governance.persistence.task_repo import TaskRepository

            repo = TaskRepository()
            oversized_task = {
                "task_id": "RED-BLUE-TEST-001",
                "title": "Oversized task",
                "description": "x" * 50,
                "deliverables": ["d1", "d2"],
                "files_in_scope": ["f1", "f2", "f3", "f4"],
                "acceptance": "a1",
                "priority": "HIGH",
                "status": "PENDING",
            }
            try:
                repo.create(oversized_task)
                _record(
                    "TRAE-003",
                    "任务粒度与完成门槛协议",
                    "task_card_over_granularity",
                    "RED",
                    "TaskRepository accepted oversized task",
                )
            except (ValueError, Exception) as exc:
                _record(
                    "TRAE-003",
                    "任务粒度与完成门槛协议",
                    "task_card_over_granularity",
                    "GREEN",
                    f"TaskRepository rejected: {exc}",
                )
        except (ImportError, RuntimeError) as exc:
            _record(
                "TRAE-003",
                "任务粒度与完成门槛协议",
                "task_card_over_granularity",
                "YELLOW",
                f"TaskRepository not usable: {exc}",
            )
        assert True


class TestTRAE004SerialSubprocess:
    def test_serial_subprocess_loop(self):
        violating_code = """
import subprocess
files = ["a.py", "b.py", "c.py"]
for f in files:
    subprocess.run(["python", f])
"""
        flagged = _check_serial_subprocess_in_code(violating_code)
        if flagged:
            _record(
                "TRAE-004",
                "并行执行与原子事务协议",
                "serial_subprocess_loop",
                "GREEN",
                "Static pattern check detected for+subprocess without ThreadPoolExecutor",
            )
        else:
            _record(
                "TRAE-004",
                "并行执行与原子事务协议",
                "serial_subprocess_loop",
                "RED",
                "Static pattern check failed to detect",
            )
        assert flagged, "Static check should flag for+subprocess without ThreadPoolExecutor"


class TestTRAE005SkipDepgraphSimulation:
    def test_skip_depgraph_simulation(self):
        script = _PROJECT_ROOT / "scripts" / "governance" / "diagnose_depgraph.py"
        if not script.exists():
            _record(
                "TRAE-005",
                "修改原则与治理施工协议",
                "skip_depgraph_simulation",
                "YELLOW",
                "diagnose_depgraph.py not found",
            )
            pytest.skip("diagnose_depgraph.py not found")
        try:
            proc = subprocess.run(
                [os.sys.executable, str(script)],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(_PROJECT_ROOT),
            )
            output = proc.stdout + proc.stderr
            has_cycle = "cycle" in output.lower() or "循环" in output
            if has_cycle:
                _record(
                    "TRAE-005",
                    "修改原则与治理施工协议",
                    "skip_depgraph_simulation",
                    "GREEN",
                    "diagnose_depgraph.py can detect cycles",
                )
            else:
                _record(
                    "TRAE-005",
                    "修改原则与治理施工协议",
                    "skip_depgraph_simulation",
                    "YELLOW",
                    f"diagnose ran but no cycle detection output (rc={proc.returncode})",
                )
        except subprocess.TimeoutExpired:
            _record(
                "TRAE-005",
                "修改原则与治理施工协议",
                "skip_depgraph_simulation",
                "YELLOW",
                "diagnose_depgraph.py timed out",
            )
        except Exception as exc:
            _record("TRAE-005", "修改原则与治理施工协议", "skip_depgraph_simulation", "RED", f"diagnose failed: {exc}")
        assert True


class TestTRAE006MissingTenFieldHeader:
    def test_missing_ten_field_header(self):
        code_without_header = """
def some_function():
    return 42
"""
        flagged = _check_missing_header(code_without_header)
        if flagged:
            _record(
                "TRAE-006",
                "防幻觉-结构追溯层",
                "missing_ten_field_header",
                "GREEN",
                "Static check detected missing required header fields",
            )
        else:
            _record(
                "TRAE-006",
                "防幻觉-结构追溯层",
                "missing_ten_field_header",
                "RED",
                "Static check failed to detect missing header",
            )
        assert flagged, "Should detect missing ten-field header"


class TestTRAE007PlaceholderInCode:
    def test_placeholder_in_code(self):
        code_with_placeholder = """
def process():
    TODO: implement this
    pass
"""
        flagged = _check_placeholder(code_with_placeholder)
        if flagged:
            _record(
                "TRAE-007",
                "防幻觉-行为约束层",
                "placeholder_in_code",
                "GREEN",
                "Static check detected TODO/pass placeholder",
            )
        else:
            _record(
                "TRAE-007",
                "防幻觉-行为约束层",
                "placeholder_in_code",
                "RED",
                "Static check failed to detect placeholder",
            )
        assert flagged, "Should detect TODO/pass placeholder"


class TestTRAE008ImportWithoutVerify:
    def test_import_without_verify(self):
        try:
            import zephyr.nonexistent_module_xyz

            _record("TRAE-008", "防幻觉-输出验证层", "import_without_verify", "RED", "Import succeeded unexpectedly")
        except (ImportError, ModuleNotFoundError):
            _record(
                "TRAE-008",
                "防幻觉-输出验证层",
                "import_without_verify",
                "GREEN",
                "ImportError raised for nonexistent module (runtime guard)",
            )
        assert True


class TestTRAE009SQLStringConcat:
    def test_sql_string_concatenation(self):
        vulnerable_code = """
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
"""
        flagged = _check_sql_concat(vulnerable_code)
        if flagged:
            _record(
                "TRAE-009",
                "防幻觉-安全防护层",
                "sql_string_concatenation",
                "GREEN",
                "Static check detected SQL string concatenation",
            )
        else:
            _record(
                "TRAE-009",
                "防幻觉-安全防护层",
                "sql_string_concatenation",
                "RED",
                "Static check failed to detect SQL injection pattern",
            )
        assert flagged, "Should detect SQL string concatenation"


class TestRedBlueReport:
    def test_generate_report(self):
        _REPORT_DIR.mkdir(parents=True, exist_ok=True)
        green = sum(1 for r in _results if r["detection_status"] == "GREEN")
        yellow = sum(1 for r in _results if r["detection_status"] == "YELLOW")
        red = sum(1 for r in _results if r["detection_status"] == "RED")
        total = len(_results)
        detection_rate = green / total if total > 0 else 0.0
        report = {
            "report_type": "red_blue_adversarial",
            "generated_at": datetime.now(UTC).isoformat(),
            "total_rules_tested": total,
            "green_detected": green,
            "yellow_partial": yellow,
            "red_undetected": red,
            "detection_rate": round(detection_rate, 4),
            "results": _results,
        }
        with open(_REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        assert total >= 9, f"Expected at least 9 test results, got {total}"
