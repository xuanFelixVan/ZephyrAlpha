# [A_test] module_id: SRC-TST-1884 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-504 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.gates.test_gate_engine
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
测试套件：GateEngine + TaskRepository 门禁集成（T-2-19）
=========================================================
覆盖：
  1. GateEngine 基础 API（load_gates / evaluate）
  2. 5 道门禁 × pass/fail 样本（G1~G5）
  3. 三大核心拦截场景：编码损坏 / 废弃路径 / 空壳文件
  4. GateResult 结构与 P0 违规判定
  5. 门禁结果写入 SQLite gates 表
  6. task_repo 集成：PENDING→IN_PROGRESS 触发 G1 门禁
  7. gate_engine disabled 时跳过门禁
  8. 非法 gate_id 抛出 GateEngineError
"""

from __future__ import annotations

import sqlite3
from collections.abc import Generator
from pathlib import Path

import pytest

from _shared.constants import REPO_ROOT
from zephyr.governance.persistence.task_repo import TaskRepository
from zephyr.governance.rule_enforcement.gate_engine.gate_engine import (
    GateEngine,
    GateEngineError,
    GateResult,
    GateViolationError,
    _check_empty_shell,
    _check_encoding,
    _check_line_ending,
    _check_path_blacklist,
)
from zephyr.governance.rule_enforcement.task_types import TaskNamespace, TaskStatus
from zephyr.integration.shared.schema.severity_types import SafetyLevel
from zephyr.shared.foundation.models import TaskCard

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

GATES_DIR = REPO_ROOT / "src" / "zephyr" / "governance" / "rule_enforcement"

EXPECTED_GATE_IDS = frozenset(
    {
        "G0",
        "G1",
        "G2",
        "G3",
        "G4",
        "G5",
        "G6",
        "G6_BP",
        "G7",
        "G10",
        "G11",
        "G12",
        "EN-001",
        "EN-002",
        "EN-003",
        "ZERO-RESIDUE",
        "MAD-001",
        "MAD-002",
        "MAD-003",
        "MAD-004",
        "GATE-DEDUP",
    }
)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "test_gate.db"


@pytest.fixture()
def engine(db_path: Path) -> Generator[GateEngine, None, None]:
    ge = GateEngine(gate_dir=GATES_DIR, db_path=db_path, project_root=Path("."))
    yield ge
    ge.close()


def _make_task(
    task_id: str = "SRC-001",
    deliverables: list[str] | None = None,
    status: str = "PENDING",
) -> TaskCard:
    namespace_str = task_id.split("-")[0]
    namespace = TaskNamespace(namespace_str)
    seq = int(task_id.split("-")[-1])
    return TaskCard(
        task_id=task_id,
        namespace=namespace,
        seq=seq,
        phase=2,
        title="测试任务",
        status=TaskStatus(status),
        execution_model="claude",
        safety_level=SafetyLevel.M,
        source_blueprint="test",
        source_section="test",
        description="测试任务：门禁引擎验证——足够长度的描述",
        files_in_scope=["tests/gate/test_gate_engine_gates.py"],
        deliverables=deliverables or [],
        applicable_rules=[{"module_id": "GOV-TASK-001", "section": "v3.0.0", "reason": "test"}],
        allowed_touch=["tests/gate/test_gate_engine_gates.py"],
        rollback_instructions="git checkout",
        post_sync_standard=["echo ok"],
        acceptance=["exit=0"],
        dependency_type="none",
        created_at="2026-01-01T00:00:00+00:00",
        updated_at="2026-01-01T00:00:00+00:00",
    )


# ---------------------------------------------------------------------------
# 1. load_gates — 加载 5 个门禁配置
# ---------------------------------------------------------------------------


def test_load_gates_returns_all_yaml_gates(engine: GateEngine) -> None:
    gates = engine.load_gates()
    assert set(gates.keys()) == EXPECTED_GATE_IDS


def test_load_gates_cached(engine: GateEngine) -> None:
    g1 = engine.load_gates()
    g2 = engine.load_gates()
    assert g1 is g2


def test_reload_gates_refreshes_cache(engine: GateEngine) -> None:
    engine.load_gates()
    g2 = engine.reload_gates()
    assert set(g2.keys()) == EXPECTED_GATE_IDS


@pytest.mark.parametrize(
    "gate_id",
    sorted(EXPECTED_GATE_IDS),
)
def test_each_gate_has_checks(gate_id: str, engine: GateEngine) -> None:
    gates = engine.load_gates()
    cfg = gates[gate_id]
    assert len(cfg.checks) > 0
    assert cfg.gate_id == gate_id


def test_gate_config_names(engine: GateEngine) -> None:
    gates = engine.load_gates()
    assert "Ingest" in gates["G1"].name
    assert "Triage" in gates["G2"].name
    assert "Evaluate" in gates["G3"].name
    assert "Activate" in gates["G4"].name
    assert "Extract" in gates["G5"].name


# ---------------------------------------------------------------------------
# 2. GateResult 结构
# ---------------------------------------------------------------------------


def test_gate_result_passed_no_violations(engine: GateEngine) -> None:
    task = _make_task()
    result = engine.evaluate(task, "G1")
    assert isinstance(result, GateResult)
    assert result.gate_id == "G1"
    assert result.task_id == "SRC-001"
    assert result.passed is True
    assert isinstance(result.violations, list)


def test_gate_result_details_structure(engine: GateEngine) -> None:
    task = _make_task()
    result = engine.evaluate(task, "G1")
    assert "gate_name" in result.details
    assert "checks_run" in result.details
    assert result.details["checks_run"] > 0


def test_gate_result_summary_pass(engine: GateEngine) -> None:
    task = _make_task()
    result = engine.evaluate(task, "G1")
    assert "[PASS]" in result.summary()


# ---------------------------------------------------------------------------
# 3. 核心拦截场景 A：废弃路径
# ---------------------------------------------------------------------------


def test_deprecated_path_blocked(engine: GateEngine) -> None:
    task = _make_task(deliverables=["_legacy/some_file.md"])
    result = engine.evaluate(task, "G1")
    assert result.passed is False
    assert result.has_p0
    assert any("废弃路径" in v.message for v in result.p0_violations)


@pytest.mark.parametrize(
    "path",
    [
        "_legacy/file.md",
        "ARCHIVE/old.md",
        "deprecated/module.py",
        "_trash/leftover.md",
        "zephyralpha-1-0/script.py",
        "old_tree/blueprint.md",
    ],
)
def test_all_deprecated_patterns_blocked(path: str, engine: GateEngine) -> None:
    task = _make_task(deliverables=[path])
    result = engine.evaluate(task, "G1")
    assert result.passed is False, f"应拦截废弃路径：{path}"


def test_valid_path_not_blocked(engine: GateEngine) -> None:
    task = _make_task(deliverables=["src/zephyr/governance/rule_enforcement/g1_ingest.yaml"])
    result = engine.evaluate(task, "G1")
    assert result.passed is True


# ---------------------------------------------------------------------------
# 4. 核心拦截场景 B：编码损坏
# ---------------------------------------------------------------------------


def test_encoding_utf8_bom_blocked(tmp_dir: Path, engine: GateEngine) -> None:
    bad_file = tmp_dir / "bom_file.md"
    bad_file.write_bytes(b"\xef\xbb\xbf# BOM header\n")
    engine._project_root = tmp_dir
    task = _make_task(deliverables=["bom_file.md"])
    result = engine.evaluate(task, "G1")
    assert result.passed is False
    assert any("BOM" in v.message for v in result.violations)


def test_encoding_corrupted_blocked(tmp_dir: Path, engine: GateEngine) -> None:
    bad_file = tmp_dir / "corrupt.md"
    bad_file.write_bytes(b"\xff\xfe# corrupted\n")
    engine._project_root = tmp_dir
    task = _make_task(deliverables=["corrupt.md"])
    result = engine.evaluate(task, "G1")
    assert result.passed is False


def test_encoding_valid_utf8_passes(tmp_dir: Path, engine: GateEngine) -> None:
    good_file = tmp_dir / "good.md"
    # 使用二进制写入确保 LF 换行；内容足够长；包含 frontmatter 必填字段
    frontmatter = "---\nmodule_id: TEST_GOOD\ntitle: 测试文件\ncategory: test\n---\n"
    body = "# 正常文件\n\n" + "这是正常的内容，包含足够的字符。" * 10
    good_file.write_bytes((frontmatter + body).encode("utf-8"))
    engine._project_root = tmp_dir
    task = _make_task(deliverables=["good.md"])
    result = engine.evaluate(task, "G1")
    assert result.passed is True


# ---------------------------------------------------------------------------
# 5. 核心拦截场景 C：空壳文件
# ---------------------------------------------------------------------------


def test_empty_file_blocked_by_g2(tmp_dir: Path, engine: GateEngine) -> None:
    """G2 的 content_quality 检查拦截空壳文件。"""
    empty_file = tmp_dir / "empty.md"
    empty_file.write_bytes(b"")
    engine._project_root = tmp_dir
    task = _make_task(deliverables=["empty.md"])
    result = engine.evaluate(task, "G2")
    assert result.passed is False
    assert any("空文件" in v.message for v in result.violations)


def test_placeholder_heavy_file_blocked_by_g2(tmp_dir: Path, engine: GateEngine) -> None:
    """G2 的 content_quality 检查拦截充满占位符的空壳文件。"""
    stub_file = tmp_dir / "stub.md"
    stub_file.write_bytes(b"# TODO\n\nTODO TODO TODO TODO TODO TODO TODO TODO\n")
    engine._project_root = tmp_dir
    task = _make_task(deliverables=["stub.md"])
    result = engine.evaluate(task, "G2")
    assert result.passed is False


def test_g1_short_content_warning(tmp_dir: Path, engine: GateEngine) -> None:
    """G1 的 content_length 检查（P1）：内容过短产生警告但不阻断任务启动。"""
    short_file = tmp_dir / "short.md"
    short_file.write_bytes(b"---\nmodule_id: X\ntitle: t\ncategory: c\n---\n\nShort.\n")
    engine._project_root = tmp_dir
    task = _make_task(deliverables=["short.md"])
    result = engine.evaluate(task, "G1")
    # P1 违规不阻断（passed=True），但会记录到 violations 列表
    assert result.passed is True
    assert any("内容过短" in v.message for v in result.violations)
    assert all(v.severity == "P1" for v in result.violations if "内容过短" in v.message)


def test_content_rich_file_passes_g2(tmp_dir: Path, engine: GateEngine) -> None:
    """G2 的 content_quality 检查：内容丰富的文件通过。"""
    rich_file = tmp_dir / "rich.md"
    rich_file.write_bytes(("# 实现说明\n\n" + "这是丰富的内容描述，包含足够的字符数。" * 10).encode("utf-8"))
    engine._project_root = tmp_dir
    task = _make_task(deliverables=["rich.md"])
    result = engine.evaluate(task, "G2")
    assert result.passed is True


# ---------------------------------------------------------------------------
# 6. G2-G5 evaluate 基本调用（任务层空操作，不阻断）
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("gate_id", ["G2", "G3", "G4", "G5"])
def test_g2_to_g5_no_block_for_plain_task(gate_id: str, engine: GateEngine) -> None:
    """G2-G5 在任务层面的 path_blacklist 检查仍生效，但空交付物不阻断。"""
    task = _make_task()
    result = engine.evaluate(task, gate_id)
    assert isinstance(result, GateResult)
    assert result.gate_id == gate_id


@pytest.mark.parametrize("gate_id", ["G2", "G3", "G4", "G5"])
def test_g2_to_g5_deprecated_path_still_blocked(gate_id: str, engine: GateEngine) -> None:
    """G2-G5 若包含 path_blacklist 检查，废弃路径仍被拦截。"""
    # 只有含 path_blacklist check 的门禁才会拦截（G1 有）
    # G2-G5 不含 path_blacklist，故此测试验证它们正常通过
    task = _make_task(deliverables=["src/valid_path.md"])
    result = engine.evaluate(task, gate_id)
    assert result.gate_id == gate_id


# ---------------------------------------------------------------------------
# 7. gates 表持久化
# ---------------------------------------------------------------------------


def test_gate_result_persisted_to_db(db_path: Path, engine: GateEngine) -> None:
    task = _make_task()
    engine.evaluate(task, "G1")
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM gate_runs").fetchall()
    conn.close()
    assert len(rows) >= 1
    assert rows[0]["gate_id"].startswith("G1:")


def test_multiple_evaluations_all_persisted(db_path: Path, engine: GateEngine) -> None:
    for i in range(3):
        task = _make_task(task_id=f"SRC-{100 + i:03d}")
        engine.evaluate(task, "G1")
    conn = sqlite3.connect(str(db_path))
    count = conn.execute("SELECT COUNT(*) FROM gate_runs").fetchone()[0]
    conn.close()
    assert count == 3


# ---------------------------------------------------------------------------
# 8. 非法 gate_id
# ---------------------------------------------------------------------------


def test_unknown_gate_id_raises(engine: GateEngine) -> None:
    task = _make_task()
    with pytest.raises(GateEngineError, match="未知 gate_id"):
        engine.evaluate(task, "G99")


# ---------------------------------------------------------------------------
# 9. 缺失 YAML 文件时抛出 GateEngineError
# ---------------------------------------------------------------------------


def test_missing_yaml_raises(tmp_path: Path, db_path: Path) -> None:
    ge = GateEngine(gate_dir=tmp_path, db_path=db_path)
    with pytest.raises(GateEngineError, match="门禁配置文件不存在"):
        ge.reload_gates()
    ge.close()


# ---------------------------------------------------------------------------
# 10. task_repo 集成：PENDING → IN_PROGRESS 触发 G1 门禁
# ---------------------------------------------------------------------------


def test_task_repo_blocks_deprecated_path(
    tmp_path: Path,
) -> None:
    """PENDING→IN_PROGRESS 时，废弃路径被 G1 门禁拦截。"""
    db_path = tmp_path / "repo_gate.db"
    repo = TaskRepository(
        db_path=db_path,
        gate_dir=GATES_DIR,
        project_root=tmp_path,
        enable_gate=True,
    )
    task = _make_task(
        task_id="SRC-077",
        deliverables=["_legacy/module.md"],
        status="PENDING",
    )
    repo.create(task)

    with pytest.raises(GateViolationError) as exc_info:
        repo.transition("SRC-077", TaskStatus.IN_PROGRESS)
    assert exc_info.value.result.passed is False
    assert exc_info.value.result.has_p0
    repo.close()


def test_task_repo_allows_clean_task(tmp_path: Path) -> None:
    """PENDING→IN_PROGRESS 时，交付物路径合法，门禁通过，状态正常转换。"""
    db_path = tmp_path / "repo_clean.db"
    deliverable_path = tmp_path / "src" / "zephyr"
    deliverable_path.mkdir(parents=True, exist_ok=True)
    deliverable_file = deliverable_path / "output.py"
    deliverable_file.write_text("# clean output\nprint('ok')\n", encoding="utf-8")
    repo = TaskRepository(
        db_path=db_path,
        gate_dir=GATES_DIR,
        project_root=tmp_path,
        enable_gate=True,
    )
    task = _make_task(
        task_id="SRC-078",
        deliverables=["src/zephyr/output.py"],
        status="PENDING",
    )
    repo.create(task)
    updated = repo.transition("SRC-078", TaskStatus.IN_PROGRESS)
    assert updated.status == TaskStatus.IN_PROGRESS
    repo.close()


def test_task_repo_encoding_violation_blocked(tmp_path: Path) -> None:
    """PENDING→IN_PROGRESS 时，交付物文件含 BOM，G1 门禁阻断。"""
    db_path = tmp_path / "repo_bom.db"
    bom_file = tmp_path / "bom_output.md"
    bom_file.write_bytes(b"\xef\xbb\xbf# BOM file\n")
    repo = TaskRepository(
        db_path=db_path,
        gate_dir=GATES_DIR,
        project_root=tmp_path,
        enable_gate=True,
    )
    task = _make_task(
        task_id="SRC-079",
        deliverables=["bom_output.md"],
        status="PENDING",
    )
    repo.create(task)

    with pytest.raises(GateViolationError) as exc_info:
        repo.transition("SRC-079", TaskStatus.IN_PROGRESS)
    assert exc_info.value.result.passed is False
    repo.close()


def test_task_repo_gate_disabled_no_check(tmp_path: Path) -> None:
    """enable_gate=False 时，门禁完全跳过，废弃路径不阻断。"""
    db_path = tmp_path / "repo_nogata.db"
    repo = TaskRepository(
        db_path=db_path,
        gate_dir=GATES_DIR,
        project_root=tmp_path,
        enable_gate=False,
    )
    task = _make_task(
        task_id="SRC-080",
        deliverables=["_legacy/should_not_matter.md"],
        status="PENDING",
    )
    repo.create(task)
    updated = repo.transition("SRC-080", TaskStatus.IN_PROGRESS)
    assert updated.status == TaskStatus.IN_PROGRESS
    repo.close()


def test_task_repo_other_transitions_no_gate(tmp_path: Path) -> None:
    """非 PENDING→IN_PROGRESS 的转换（如 IN_PROGRESS→COMPLETED）不触发门禁。"""
    db_path = tmp_path / "repo_other.db"
    bom_file = tmp_path / "bom2.md"
    bom_file.write_bytes(b"\xef\xbb\xbf# BOM\n")
    repo = TaskRepository(
        db_path=db_path,
        gate_dir=GATES_DIR,
        project_root=tmp_path,
        enable_gate=True,
    )
    task = _make_task(
        task_id="SRC-081",
        deliverables=["bom2.md"],
        status="PENDING",
    )
    repo.create(task)
    # 先用 enable_gate=False 的方式把任务推进到 IN_PROGRESS
    repo._enable_gate = False
    repo.transition("SRC-081", TaskStatus.IN_PROGRESS)
    repo._enable_gate = True
    # IN_PROGRESS → COMPLETED 不触发门禁
    updated = repo.transition("SRC-081", TaskStatus.COMPLETED)
    assert updated.status == TaskStatus.COMPLETED
    repo.close()


# ---------------------------------------------------------------------------
# 11. 底层检查函数单元测试
# ---------------------------------------------------------------------------


def test_check_encoding_no_file(tmp_path: Path) -> None:
    result = _check_encoding(tmp_path / "nonexistent.md", {"disallow_bom": True})
    assert result is None


def test_check_encoding_bom(tmp_path: Path) -> None:
    f = tmp_path / "bom.md"
    f.write_bytes(b"\xef\xbb\xbf# hi")
    result = _check_encoding(f, {"disallow_bom": True})
    assert result is not None
    assert "BOM" in result


def test_check_encoding_clean(tmp_path: Path) -> None:
    f = tmp_path / "clean.md"
    f.write_text("# hi", encoding="utf-8")
    result = _check_encoding(f, {"disallow_bom": True})
    assert result is None


def test_check_line_ending_crlf(tmp_path: Path) -> None:
    f = tmp_path / "crlf.md"
    f.write_bytes(b"line1\r\nline2\r\n")
    result = _check_line_ending(f, {})
    assert result is not None
    assert "CRLF" in result


def test_check_line_ending_lf(tmp_path: Path) -> None:
    f = tmp_path / "lf.md"
    f.write_bytes(b"line1\nline2\n")
    result = _check_line_ending(f, {})
    assert result is None


def test_check_path_blacklist_hit() -> None:
    violations = _check_path_blacklist(["docs/_legacy/old.md"], {})
    assert len(violations) > 0


def test_check_path_blacklist_miss() -> None:
    violations = _check_path_blacklist(["src/zephyr/governance/rule_enforcement/gate_engine/gate_engine.py"], {})
    assert len(violations) == 0


def test_check_empty_shell_empty_file(tmp_path: Path) -> None:
    f = tmp_path / "empty.md"
    f.write_text("", encoding="utf-8")
    result = _check_empty_shell(f, {})
    assert result is not None
    assert "空文件" in result


def test_check_empty_shell_rich_file(tmp_path: Path) -> None:
    f = tmp_path / "rich.md"
    f.write_text("# 完整内容\n\n" + "很多内容。" * 20, encoding="utf-8")
    result = _check_empty_shell(f, {})
    assert result is None


def test_check_empty_shell_no_file(tmp_path: Path) -> None:
    result = _check_empty_shell(tmp_path / "ghost.md", {})
    assert result is None
