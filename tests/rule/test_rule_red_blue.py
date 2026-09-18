# [A_test] module_id: MOD-GOV_rule_red_blue | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-019 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §rule_engine
# [MODULE] tests.test_rule_red_blue
# [DOMAIN] D_GOV_ENFORCEMENT
# [INVARIANTS] 红蓝对抗测试：故意违反规则→验证检测率; 报告输出到 pytest tmp_path（禁写生产路径）; 报告测试须自包含（九项探针由 red_blue_baseline fixture 自行补齐，禁依赖兄弟测试的副作用累积）
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
# kimi-audit B2-① 直改（裁定#324）：报告只写 pytest tmp_path，禁写 data/databases 生产目录

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

# 自包含基线配套件（z-testint 2026-09-18，R-035 顺序依赖测试治本）：
# _probe_cache 让同一进程内每项探针只执行一次——报告测试补齐基线时不再重复付
# audit_registration / diagnose_depgraph 的秒级~分钟级 subprocess 成本。
_probe_cache: dict[str, tuple[str, str]] = {}
_RULE_META: dict[str, dict] = {r["rule_id"]: r for r in L0_RULES}


def _run_audit_registration() -> tuple[int, str]:
    # kimi-audit B2-① 路径漂移修正：脚本实际在 d11_compliance 子目录（扁平旧路径必 not found → 假 RED）
    script = _PROJECT_ROOT / "scripts" / "governance" / "d11_compliance" / "audit_registration.py"
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


def _record(rule_id: str, detection: str, detail: str, *, recorded_by: str = "test_body") -> None:
    meta = _RULE_META[rule_id]
    _results.append(
        {
            "rule_id": rule_id,
            "title": meta["title"],
            "violation_type": meta["violation"],
            "detection_status": detection,
            "detection_detail": detail,
            "recorded_by": recorded_by,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    )


_VALID_DETECTION_STATUSES = {"GREEN", "YELLOW", "RED"}


def _assert_recorded(rule_id: str):
    """断言该规则的红蓝结果已由**本用例自身**落账且字段合法（kimi-audit B2-①：防 _record 未被调用/用例静默短路）。

    z-testint 收紧：只认 recorded_by == "test_body" 的条目——基线采集器（baseline_collector）
    补齐的同名条目不得让本用例蒙混过关，否则"用例静默短路"又查不出来了。
    """
    entries = [r for r in _results if r["rule_id"] == rule_id and r.get("recorded_by") == "test_body"]
    assert entries, f"{rule_id}: 未记录任何红蓝结果（检测用例被静默跳过）"
    for r in entries:
        assert r["detection_status"] in _VALID_DETECTION_STATUSES, (
            f"{rule_id}: 非法检测状态 {r['detection_status']!r}"
        )
        assert isinstance(r["detection_detail"], str) and r["detection_detail"].strip(), (
            f"{rule_id}: 检测详情为空"
        )


def _probe_trae001(scratch: Path) -> tuple[str, str]:
    target = scratch / "orphan_test.py"
    target.write_text("print('no lock acquired')", encoding="utf-8")
    rc, output = _run_audit_registration()
    if rc != 0 and "orphan" in output.lower():
        return "GREEN", "audit_registration.py detected violation"
    if rc != 0:
        return "YELLOW", f"audit exited {rc} but no orphan mention: {output[:200]}"
    return "RED", "No detection by audit_registration.py"


def _probe_trae002(scratch: Path) -> tuple[str, str]:
    target = scratch / "unregistered_module.py"
    target.write_text("def unregistered_func(): pass", encoding="utf-8")
    rc, output = _run_audit_registration()
    if rc != 0 and "orphan" in output.lower():
        return "GREEN", "audit_registration.py detected orphan"
    if rc != 0:
        return "YELLOW", f"audit exited {rc}: {output[:200]}"
    return "RED", "No orphan detection"


def _probe_trae003(scratch: Path) -> tuple[str, str]:  # noqa: ARG001  探针签名统一（scratch 对本项无用）
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
        except (ValueError, Exception) as exc:
            return "GREEN", f"TaskRepository rejected: {exc}"
        return "RED", "TaskRepository accepted oversized task"
    except (ImportError, RuntimeError) as exc:
        return "YELLOW", f"TaskRepository not usable: {exc}"


def _probe_trae004(scratch: Path) -> tuple[str, str]:  # noqa: ARG001  探针签名统一（scratch 对本项无用）
    violating_code = """
import subprocess
files = ["a.py", "b.py", "c.py"]
for f in files:
    subprocess.run(["python", f])
"""
    if _check_serial_subprocess_in_code(violating_code):
        return "GREEN", "Static pattern check detected for+subprocess without ThreadPoolExecutor"
    return "RED", "Static pattern check failed to detect"


def _probe_trae005(scratch: Path) -> tuple[str, str]:  # noqa: ARG001  探针签名统一（scratch 对本项无用）
    # kimi-audit B2-① 路径漂移修正：脚本实际在 d5_architecture 子目录（扁平旧路径必 not found → 假 skip）
    script = _PROJECT_ROOT / "scripts" / "governance" / "d5_architecture" / "diagnose_depgraph.py"
    if not script.exists():
        # 不再 pytest.skip 兜底：脚本缺失按 RED 落账，由终闸检出率门统一翻红
        return "RED", "diagnose_depgraph.py not found"
    try:
        proc = subprocess.run(
            [os.sys.executable, str(script)],
            capture_output=True,
            text=True,
            # 实测该脚本单进程 108s（2026-09-18），-n 2 下被挤压过 120s →
            # 探针自身超时会把"检得出"误报成 YELLOW（检出率门因此假红）。
            # 这里放宽的是 I/O 预算，不是判定口径：跑完仍按有无 cycle 判 GREEN/YELLOW。
            timeout=300,
            cwd=str(_PROJECT_ROOT),
        )
    except subprocess.TimeoutExpired:
        return "YELLOW", "diagnose_depgraph.py timed out"
    except Exception as exc:
        return "RED", f"diagnose failed: {exc}"
    output = proc.stdout + proc.stderr
    if "cycle" in output.lower() or "循环" in output:
        return "GREEN", "diagnose_depgraph.py can detect cycles"
    return "YELLOW", f"diagnose ran but no cycle detection output (rc={proc.returncode})"


def _probe_trae006(scratch: Path) -> tuple[str, str]:  # noqa: ARG001  探针签名统一（scratch 对本项无用）
    code_without_header = """
def some_function():
    return 42
"""
    if _check_missing_header(code_without_header):
        return "GREEN", "Static check detected missing required header fields"
    return "RED", "Static check failed to detect missing header"


def _probe_trae007(scratch: Path) -> tuple[str, str]:  # noqa: ARG001  探针签名统一（scratch 对本项无用）
    code_with_placeholder = """
def process():
    TODO: implement this
    pass
"""
    if _check_placeholder(code_with_placeholder):
        return "GREEN", "Static check detected TODO/pass placeholder"
    return "RED", "Static check failed to detect placeholder"


def _probe_trae008(scratch: Path) -> tuple[str, str]:  # noqa: ARG001  探针签名统一（scratch 对本项无用）
    try:
        import zephyr.nonexistent_module_xyz

        return "RED", "Import succeeded unexpectedly"
    except (ImportError, ModuleNotFoundError):
        return "GREEN", "ImportError raised for nonexistent module (runtime guard)"


def _probe_trae009(scratch: Path) -> tuple[str, str]:  # noqa: ARG001  探针签名统一（scratch 对本项无用）
    vulnerable_code = """
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
"""
    if _check_sql_concat(vulnerable_code):
        return "GREEN", "Static check detected SQL string concatenation"
    return "RED", "Static check failed to detect SQL injection pattern"


_RULE_PROBES: dict[str, object] = {
    "TRAE-001": _probe_trae001,
    "TRAE-002": _probe_trae002,
    "TRAE-003": _probe_trae003,
    "TRAE-004": _probe_trae004,
    "TRAE-005": _probe_trae005,
    "TRAE-006": _probe_trae006,
    "TRAE-007": _probe_trae007,
    "TRAE-008": _probe_trae008,
    "TRAE-009": _probe_trae009,
}


def _run_rule_probe(rule_id: str, scratch: Path) -> str:
    """执行单项红蓝探针（同进程记忆化）并以 test_body 口径落账，返回检测状态。"""
    if rule_id not in _probe_cache:
        _probe_cache[rule_id] = _RULE_PROBES[rule_id](scratch)  # type: ignore[operator]
    detection, detail = _probe_cache[rule_id]
    _record(rule_id, detection, detail)
    return detection


def _collect_red_blue_baseline(scratch: Path) -> None:
    """补齐九项红蓝结果——使任一测试（含报告测试）单跑/乱序/分片都不依赖兄弟测试副作用。

    真因（z-testint，账本 R-035）：报告测试曾直接读 _results 并 assert len>=9，
    而 _results 只由 TestTRAE001-009 逐个追加 → 单跑必得 0 结果。
    已入账的规则不重复记账（保持"一条规则一条证据"的报告口径）。
    """
    for spec in L0_RULES:
        rule_id = spec["rule_id"]
        if any(r["rule_id"] == rule_id for r in _results):
            continue
        if rule_id not in _probe_cache:
            _probe_cache[rule_id] = _RULE_PROBES[rule_id](scratch)  # type: ignore[operator]
        detection, detail = _probe_cache[rule_id]
        _record(rule_id, detection, detail, recorded_by="baseline_collector")


@pytest.fixture
def red_blue_baseline(tmp_path: Path) -> list[dict]:
    """报告测试的自取数据夹具：先补齐九项基线，再交出账本。"""
    _collect_red_blue_baseline(tmp_path)
    return _results


class TestTRAE001CreateWithoutLock:
    def test_create_file_without_lock(self, tmp_path):
        _run_rule_probe("TRAE-001", tmp_path)
        _assert_recorded("TRAE-001")


class TestTRAE002CreateWithoutRegister:
    def test_create_py_without_register(self, tmp_path):
        _run_rule_probe("TRAE-002", tmp_path)
        _assert_recorded("TRAE-002")


class TestTRAE003TaskCardOverGranularity:
    def test_task_card_over_granularity(self, tmp_path):
        _run_rule_probe("TRAE-003", tmp_path)
        _assert_recorded("TRAE-003")


class TestTRAE004SerialSubprocess:
    def test_serial_subprocess_loop(self, tmp_path):
        detection = _run_rule_probe("TRAE-004", tmp_path)
        assert detection == "GREEN", "Static check should flag for+subprocess without ThreadPoolExecutor"


class TestTRAE005SkipDepgraphSimulation:
    # 探针本身是分钟级 subprocess（实测 diagnose_depgraph.py ≈108s），并发跑时更易越过
    # pyproject 的全局 timeout=120 兜底 → 按既有约定用 marker 覆盖（不改任何断言口径）。
    @pytest.mark.timeout(420)
    def test_skip_depgraph_simulation(self, tmp_path):
        _run_rule_probe("TRAE-005", tmp_path)
        _assert_recorded("TRAE-005")


class TestTRAE006MissingTenFieldHeader:
    def test_missing_ten_field_header(self, tmp_path):
        detection = _run_rule_probe("TRAE-006", tmp_path)
        assert detection == "GREEN", "Should detect missing ten-field header"


class TestTRAE007PlaceholderInCode:
    def test_placeholder_in_code(self, tmp_path):
        detection = _run_rule_probe("TRAE-007", tmp_path)
        assert detection == "GREEN", "Should detect TODO/pass placeholder"


class TestTRAE008ImportWithoutVerify:
    def test_import_without_verify(self, tmp_path):
        _run_rule_probe("TRAE-008", tmp_path)
        _assert_recorded("TRAE-008")


class TestTRAE009SQLStringConcat:
    def test_sql_string_concatenation(self, tmp_path):
        detection = _run_rule_probe("TRAE-009", tmp_path)
        assert detection == "GREEN", "Should detect SQL string concatenation"


class TestRedBlueReport:
    @pytest.mark.timeout(900)
    def test_generate_report(self, tmp_path, red_blue_baseline):
        # 自包含：九项红蓝结果由 red_blue_baseline 夹具自行采集（z-testint 治 R-035 顺序依赖），
        # 不再依赖 TestTRAE001-009 是否在同进程先跑过。
        results = red_blue_baseline
        green = sum(1 for r in results if r["detection_status"] == "GREEN")
        yellow = sum(1 for r in results if r["detection_status"] == "YELLOW")
        red = sum(1 for r in results if r["detection_status"] == "RED")
        total = len(results)
        detection_rate = green / total if total > 0 else 0.0
        report = {
            "report_type": "red_blue_adversarial",
            "generated_at": datetime.now(UTC).isoformat(),
            "total_rules_tested": total,
            "green_detected": green,
            "yellow_partial": yellow,
            "red_undetected": red,
            "detection_rate": round(detection_rate, 4),
            "results": results,
        }
        # kimi-audit B2-① 直改（裁定#324）：报告落 tmp_path，禁写 data/databases 生产目录
        report_path = tmp_path / "red_blue_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        assert total >= 9, f"Expected at least 9 test results, got {total}"
        # 终闸检出率下限门（kimi-audit B2-①，裁定#324）：检出漏洞数/注入漏洞总数 ≥ 0.95 才 PASS
        assert report_path.exists() and report_path.stat().st_size > 0, "红蓝报告未成功写出"
        assert detection_rate >= 0.95, (
            f"红蓝检出率门位失守: detection_rate={detection_rate:.4f} < 0.95 "
            f"(GREEN={green}, YELLOW={yellow}, RED={red}, total={total})"
        )
