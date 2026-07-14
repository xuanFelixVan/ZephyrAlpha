# [A_test] module_id: SRC-TST-0169 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-326 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.integration.test_gate_e2e
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
门禁引擎端到端测试（T-2-19）/ B14
====================================
依赖：B10 ✅ + B11 ✅

覆盖：
  1. 完整门禁流程：task 创建 → G1 Ingest → G2 Triage → G3 Evaluate → G4 Activate
  2. 门禁阻断：不合规 task 被正确阻断在对应门禁
  3. 门禁降级：P1/WARNING 级别允许通过但记录到 violations
  4. task_repo + gate_engine 集成：状态变更触发门禁检查
  5. rollback 语义：门禁失败后 task 状态正确保持（未写入 DB）

使用真实 gate YAML（src/zephyr/gov_enforcement/rule_enforcement/g1_ingest.yaml ~ g5_extract.yaml）。
"""

from __future__ import annotations

import sqlite3
from collections.abc import Generator
from pathlib import Path

import pytest

pytestmark = pytest.mark.e2e

from zephyr.governance.persistence.sqlite_schema import init_db
from zephyr.governance.persistence.task_repo import (
    GateViolationError,
    TaskRepository,
)
from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_engine import (
    GateEngine,
    GateEngineError,
    GateResult,
)
from zephyr.gov_enforcement.rule_enforcement.task_types import TaskStatus
from zephyr.shared.foundation.models import TaskCard

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

GATES_DIR = Path(__file__).parent.parent.parent / "src" / "zephyr" / "governance" / "rule_enforcement"

# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------


def _make_task(
    task_id: str = "SRC-001",
    deliverables: list[str] | None = None,
    status: str = "PENDING",
) -> TaskCard:
    namespace = task_id.split("-")[0]
    seq = int(task_id.split("-")[-1])
    return TaskCard(
        task_id=task_id,
        namespace=namespace,
        seq=seq,
        phase=2,
        title="E2E 测试任务",
        status=TaskStatus(status),
        execution_model="claude",
        safety_level="M",
        source_blueprint="test",
        source_section="test",
        description=(
            "E2E 测试任务：门禁端到端验证。根因：测试需要验证门禁完整流程覆盖。"
            "治根：通过端到端测试覆盖任务从创建到验证的完整生命周期。"
            "施工步骤：创建任务并触发对应门禁检查。"
            "验收标准：任务状态正确更新且门禁结果符合预期。"
            "此测试确保门禁引擎与任务仓库集成正确。"
        ),
        verification_status="verified",
        deliverables=deliverables or ["src/zephyr/output.py"],
        acceptance=["exit=0"],
        depends_on=[],
        files_in_scope=["tests/gate/test_gate_e2e.py"],
        directive="999",
        applicable_rules=[{"module_id": "GOV-TASK-001", "section": "§4", "reason": "模板校验"}],
        allowed_touch=["tests/gate/test_gate_e2e.py"],
        rollback_instructions="git checkout -- tests/gate/test_gate_e2e.py",
        post_sync_standard=[],  # Windows: echo是shell内置命令,shell=False下不可执行
        created_at="2026-01-01T00:00:00+00:00",
        updated_at="2026-01-01T00:00:00+00:00",
    )


def _make_repo(
    tmp_path: Path,
    db_name: str = "e2e.db",
    enable_gate: bool = True,
) -> TaskRepository:
    db_path = tmp_path / db_name
    return TaskRepository(
        db_path=db_path,
        gate_dir=GATES_DIR,
        project_root=tmp_path,
        enable_gate=enable_gate,
    )


def _write_valid_file(directory: Path, name: str) -> Path:
    """写一个通过 G1 所有检查的 UTF-8 LF 文件（含 frontmatter + 足够正文）。"""
    path = directory / name
    frontmatter = (
        "---\n"
        "doc_type: policy\n"
        "title: 测试文件\n"
        "version: 1.0.0\n"
        "status: active\n"
        "date: 2026-01-01\n"
        "owner: ZephyrAlpha-Owner\n"
        "ttl: permanent\n"
        "---\n"
    )
    body = "# 正文\n\n" + "这是充足的正文内容，满足最小字符数要求。" * 5
    path.write_bytes((frontmatter + body).encode("utf-8"))
    return path


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def engine(tmp_path: Path) -> Generator[GateEngine, None, None]:
    db = tmp_path / "engine_e2e.db"
    ge = GateEngine(gate_dir=GATES_DIR, db_path=db, project_root=tmp_path)
    yield ge
    ge.close()


# ===========================================================================
# 1. 完整流水线（task_repo 集成）
# ===========================================================================


class TestFullPipeline:
    """端到端流程：task 创建 → G1 → IN_PROGRESS → COMPLETED → VERIFIED。"""

    def test_pending_to_in_progress_via_g1_pass(self, tmp_path: Path) -> None:
        """G1 通过：PENDING → IN_PROGRESS 状态正确更新。"""
        repo = _make_repo(tmp_path, "pp_ip.db")
        task = _make_task("SRC-100", deliverables=["src/zephyr/output.py"])
        repo.create(task)
        updated = repo.transition("SRC-100", TaskStatus.IN_PROGRESS)
        assert updated.status == TaskStatus.IN_PROGRESS
        repo.close()

    def test_in_progress_to_completed_no_gate(self, tmp_path: Path) -> None:
        """IN_PROGRESS → COMPLETED 不触发门禁，状态正确更新。"""
        repo = _make_repo(tmp_path, "ip_co.db")
        task = _make_task("SRC-101")
        repo.create(task)
        repo._enable_gate = False
        repo.transition("SRC-101", TaskStatus.IN_PROGRESS)
        repo._enable_gate = True
        # DM-200921: COMPLETED 前需连续2次 batch_review 0问题
        repo.batch_review("SRC-101")
        repo.batch_review("SRC-101")
        completed = repo.transition("SRC-101", TaskStatus.COMPLETED)
        assert completed.status == TaskStatus.COMPLETED
        repo.close()

    def test_completed_to_verified_no_gate(self, tmp_path: Path) -> None:
        """COMPLETED → VERIFIED 不触发门禁，状态正确更新。"""
        repo = _make_repo(tmp_path, "co_ve.db")
        task = _make_task("SRC-102")
        repo.create(task)
        repo._enable_gate = False
        repo.transition("SRC-102", TaskStatus.IN_PROGRESS)
        repo._enable_gate = True
        # DM-200921: COMPLETED 前需连续2次 batch_review 0问题
        repo.batch_review("SRC-102")
        repo.batch_review("SRC-102")
        repo.transition("SRC-102", TaskStatus.COMPLETED)
        verified = repo.transition("SRC-102", TaskStatus.VERIFIED)
        assert verified.status == TaskStatus.VERIFIED
        repo.close()

    def test_full_lifecycle_pending_to_verified(self, tmp_path: Path) -> None:
        """完整生命周期：PENDING → IN_PROGRESS → COMPLETED → VERIFIED。"""
        repo = _make_repo(tmp_path, "full_lc.db")
        task = _make_task("SRC-103")
        repo.create(task)
        repo._enable_gate = False
        repo.transition("SRC-103", TaskStatus.IN_PROGRESS)
        # DM-200921: COMPLETED 前需连续2次 batch_review 0问题
        repo.batch_review("SRC-103")
        repo.batch_review("SRC-103")
        repo.transition("SRC-103", TaskStatus.COMPLETED)
        repo.transition("SRC-103", TaskStatus.VERIFIED)
        final = repo.get("SRC-103")
        assert final is not None
        assert final.status == TaskStatus.VERIFIED
        repo.close()


# ===========================================================================
# 2. 门禁阻断场景（G1 P0 violations）
# ===========================================================================


class TestGateBlockingE2E:
    """不合规 task 被 G1 阻断。"""

    def test_g1_blocks_deprecated_path_e2e(self, tmp_path: Path) -> None:
        """G1-C00 path_blacklist: _legacy/ 路径被拦截，抛 GateViolationError。"""
        repo = _make_repo(tmp_path, "dep_block.db")
        task = _make_task("SRC-104", deliverables=["_legacy/module.md"])
        repo.create(task)
        with pytest.raises(GateViolationError) as exc_info:
            repo.transition("SRC-104", TaskStatus.IN_PROGRESS)
        assert exc_info.value.result.passed is False
        assert exc_info.value.result.has_p0
        repo.close()

    def test_g1_blocks_bom_file_e2e(self, tmp_path: Path) -> None:
        """G1-C02 encoding: BOM 文件被拦截，task 无法进入 IN_PROGRESS。"""
        bom_file = tmp_path / "bom_module.md"
        bom_file.write_bytes(b"\xef\xbb\xbf# BOM\n")
        repo = _make_repo(tmp_path, "bom_block.db")
        task = _make_task("SRC-105", deliverables=["bom_module.md"])
        repo.create(task)
        with pytest.raises(GateViolationError) as exc_info:
            repo.transition("SRC-105", TaskStatus.IN_PROGRESS)
        assert not exc_info.value.result.passed
        repo.close()

    def test_g1_blocks_corrupted_encoding_e2e(self, tmp_path: Path) -> None:
        """G1-C02 encoding: 非 UTF-8 文件被拦截，task 无法启动。"""
        bad_file = tmp_path / "corrupt.md"
        bad_file.write_bytes(b"\xff\xfeCorrupted content\n")
        repo = _make_repo(tmp_path, "corrupt_block.db")
        task = _make_task("SRC-106", deliverables=["corrupt.md"])
        repo.create(task)
        with pytest.raises(GateViolationError):
            repo.transition("SRC-106", TaskStatus.IN_PROGRESS)
        repo.close()

    def test_gate_violation_error_carries_result(self, tmp_path: Path) -> None:
        """GateViolationError 携带完整 GateResult 对象。"""
        repo = _make_repo(tmp_path, "ve_result.db")
        task = _make_task("SRC-107", deliverables=["ARCHIVE/old.md"])
        repo.create(task)
        with pytest.raises(GateViolationError) as exc_info:
            repo.transition("SRC-107", TaskStatus.IN_PROGRESS)
        result = exc_info.value.result
        assert isinstance(result, GateResult)
        assert result.gate_id == "G1"
        assert result.task_id == "SRC-107"
        assert len(result.violations) > 0
        repo.close()

    def test_gate_result_summary_contains_fail_tag(self, tmp_path: Path) -> None:
        """GateResult.summary() 对阻断情况以 [FAIL] 开头。"""
        repo = _make_repo(tmp_path, "summary_fail.db")
        task = _make_task("SRC-108", deliverables=["deprecated/module.py"])
        repo.create(task)
        with pytest.raises(GateViolationError) as exc_info:
            repo.transition("SRC-108", TaskStatus.IN_PROGRESS)
        assert exc_info.value.result.summary().startswith("[FAIL]")
        repo.close()

    @pytest.mark.skip(reason="RULE-THIRTEEN R1: deliverables ≤ 1，多 deliverables 场景已不合法")
    def test_multiple_deprecated_deliverables_all_blocked(self, tmp_path: Path) -> None:
        """多个废弃路径交付物时，所有违规均被记录。"""
        repo = _make_repo(tmp_path, "multi_dep.db")
        task = _make_task(
            "SRC-109",
            deliverables=["_legacy/a.md", "_trash/b.md", "src/valid.py"],
        )
        repo.create(task)
        with pytest.raises(GateViolationError) as exc_info:
            repo.transition("SRC-109", TaskStatus.IN_PROGRESS)
        p0s = exc_info.value.result.p0_violations
        assert len(p0s) >= 2
        repo.close()


# ===========================================================================
# 3. 门禁降级（P1 WARNING 允许通过）
# ===========================================================================


class TestGateDegradation:
    """P1/P2 级别违规不阻断任务启动，但记录到 violations。"""

    def test_crlf_file_p1_warning_allows_in_progress(self, tmp_path: Path) -> None:
        """G1-C03 line_ending 为 warning(P1)：CRLF 文件不阻断任务，状态正常更新。"""
        crlf_file = tmp_path / "crlf_output.md"
        frontmatter = (
            "---\r\n"
            "doc_type: policy\r\n"
            "title: T\r\nversion: 1.0.0\r\nstatus: active\r\n"
            "date: 2026-01-01\r\nowner: X\r\nttl: permanent\r\n"
            "---\r\n"
        )
        body = "# Body\r\n\r\n" + "Content. " * 20
        crlf_file.write_bytes((frontmatter + body).encode("utf-8"))

        repo = _make_repo(tmp_path, "crlf_pass.db")
        task = _make_task("SRC-110", deliverables=["crlf_output.md"])
        repo.create(task)
        updated = repo.transition("SRC-110", TaskStatus.IN_PROGRESS)
        assert updated.status == TaskStatus.IN_PROGRESS
        repo.close()

    def test_p1_violation_recorded_in_gate_result(self, engine: GateEngine, tmp_path: Path) -> None:
        """G1 evaluate：CRLF 触发 P1 警告，其余检查均通过 → passed=True。"""
        crlf_file = tmp_path / "crlf_check.md"
        # frontmatter 用 LF，body 用 CRLF（仅 line_ending 触发 P1，无 P0）
        frontmatter = b"---\nmodule_id: X\ntitle: T\ncategory: c\n---\n"
        body = b"# Header\r\n\r\n" + b"Content line here. " * 8  # ~152 chars > 100
        crlf_file.write_bytes(frontmatter + body)
        engine._project_root = tmp_path
        task = _make_task("SRC-111", deliverables=["crlf_check.md"])
        result = engine.evaluate(task, "G1")
        assert result.passed is True
        assert any(v.severity == "P1" for v in result.violations)
        assert any("CRLF" in v.message for v in result.violations)

    def test_only_p0_causes_gate_failure(self, engine: GateEngine, tmp_path: Path) -> None:
        """有 P1/P2 违规时 passed=True；只有 P0 违规时 passed=False。"""
        engine._project_root = tmp_path
        task = _make_task("SRC-112", deliverables=["nonexistent_file.md"])
        result = engine.evaluate(task, "G1")
        assert result.passed is True

    def test_gate_result_summary_pass_tag(self, engine: GateEngine) -> None:
        """G1 evaluate：无 P0 违规时 summary() 以 [PASS] 开头。"""
        task = _make_task("SRC-113")
        result = engine.evaluate(task, "G1")
        assert result.summary().startswith("[PASS]")


# ===========================================================================
# 4. G1~G5 门禁直接调用（engine 层烟雾测试）
# ===========================================================================


class TestG1ToG5ViaEngine:
    """通过 GateEngine 直接调用各门禁，验证基本语义。"""

    def test_g1_evaluate_returns_gate_result(self, engine: GateEngine) -> None:
        """G1 evaluate 返回 GateResult，gate_id 正确。"""
        result = engine.evaluate(_make_task("SRC-114"), "G1")
        assert isinstance(result, GateResult)
        assert result.gate_id == "G1"

    def test_g2_evaluate_blocks_empty_file(self, engine: GateEngine, tmp_path: Path) -> None:
        """G2-C00 content_quality: 空文件被 G2 拦截（P0）。"""
        empty = tmp_path / "empty.md"
        empty.write_bytes(b"")
        engine._project_root = tmp_path
        result = engine.evaluate(_make_task("SRC-115", ["empty.md"]), "G2")
        assert result.passed is False

    def test_g2_evaluate_rich_content_passes(self, engine: GateEngine, tmp_path: Path) -> None:
        """G2-C00 content_quality: 内容丰富的文件通过 G2。"""
        rich = tmp_path / "rich.md"
        rich.write_bytes(("# Title\n\n" + "内容。" * 30).encode("utf-8"))
        engine._project_root = tmp_path
        result = engine.evaluate(_make_task("SRC-116", ["rich.md"]), "G2")
        assert result.passed is True

    def test_g3_evaluate_returns_result(self, engine: GateEngine) -> None:
        """G3 evaluate：空交付物任务，返回有效 GateResult。"""
        result = engine.evaluate(_make_task("SRC-117"), "G3")
        assert isinstance(result, GateResult)
        assert result.gate_id == "G3"

    def test_g4_evaluate_returns_result(self, engine: GateEngine) -> None:
        """G4 evaluate：空交付物任务，返回有效 GateResult。"""
        result = engine.evaluate(_make_task("SRC-118"), "G4")
        assert isinstance(result, GateResult)
        assert result.gate_id == "G4"

    def test_g5_evaluate_returns_result(self, engine: GateEngine) -> None:
        """G5 evaluate：空交付物任务，返回有效 GateResult。"""
        result = engine.evaluate(_make_task("SRC-119"), "G5")
        assert isinstance(result, GateResult)
        assert result.gate_id == "G5"

    def test_unknown_gate_raises_engine_error(self, engine: GateEngine) -> None:
        """非法 gate_id 抛出 GateEngineError。"""
        with pytest.raises(GateEngineError, match="未知 gate_id"):
            engine.evaluate(_make_task("SRC-120"), "G99")


# ===========================================================================
# 5. Rollback 语义 + 集成
# ===========================================================================


class TestRollbackAndIntegration:
    """门禁失败后 task 状态保持不变（rollback 语义）。"""

    def test_task_status_stays_pending_after_gate_failure(self, tmp_path: Path) -> None:
        """G1 失败后，task 状态仍为 PENDING（未发生状态机写入）。"""
        repo = _make_repo(tmp_path, "rb_pending.db")
        task = _make_task("SRC-121", deliverables=["_legacy/bad.md"])
        repo.create(task)
        with pytest.raises(GateViolationError):
            repo.transition("SRC-121", TaskStatus.IN_PROGRESS)
        task_after = repo.get("SRC-121")
        assert task_after is not None
        assert task_after.status == TaskStatus.PENDING
        repo.close()

    def test_gate_result_written_to_db_on_failure(self, tmp_path: Path) -> None:
        """G1 失败时，GateResult 写入 gates 表（持久化记录）。"""
        db_path = tmp_path / "rb_db_fail.db"
        init_db(db_path)
        repo = TaskRepository(
            db_path=db_path,
            gate_dir=GATES_DIR,
            project_root=tmp_path,
            enable_gate=True,
        )
        task = _make_task("SRC-122", deliverables=["deprecated/module.py"])
        repo.create(task)
        with pytest.raises(GateViolationError):
            repo.transition("SRC-122", TaskStatus.IN_PROGRESS)
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM gate_runs").fetchall()
        conn.close()
        repo.close()
        assert len(rows) >= 1
        assert any("G1" in (row["gate_id"] or "") for row in rows)

    def test_gate_result_written_to_db_on_success(self, tmp_path: Path) -> None:
        """G1 通过时，GateResult 也写入 gate_runs 表。"""
        db_path = tmp_path / "rb_db_pass.db"
        init_db(db_path)
        repo = TaskRepository(
            db_path=db_path,
            gate_dir=GATES_DIR,
            project_root=tmp_path,
            enable_gate=True,
        )
        task = _make_task("SRC-123", deliverables=["src/valid_output.py"])
        repo.create(task)
        repo.transition("SRC-123", TaskStatus.IN_PROGRESS)
        conn = sqlite3.connect(str(db_path))
        rows = conn.execute("SELECT * FROM gate_runs").fetchall()
        conn.close()
        repo.close()
        assert len(rows) >= 1

    def test_ready_to_in_progress_also_triggers_g1(self, tmp_path: Path) -> None:
        """READY → IN_PROGRESS 同样触发 G1 检查（任意到 IN_PROGRESS 均触发）。"""
        repo = _make_repo(tmp_path, "ready_ip.db")
        bom_file = tmp_path / "bom_ready.md"
        bom_file.write_bytes(b"\xef\xbb\xbf# BOM\n")
        task = _make_task("SRC-124", deliverables=["bom_ready.md"], status="PENDING")
        repo.create(task)
        repo._enable_gate = False
        repo.transition("SRC-124", TaskStatus.BLOCKED)
        repo.transition("SRC-124", TaskStatus.READY)
        repo._enable_gate = True
        with pytest.raises(GateViolationError) as exc_info:
            repo.transition("SRC-124", TaskStatus.IN_PROGRESS)
        assert exc_info.value.result.passed is False
        repo.close()

    def test_multiple_tasks_independent_gate_checks(self, tmp_path: Path) -> None:
        """多个 task 独立执行 G1 检查，互不影响。"""
        repo = _make_repo(tmp_path, "multi_ind.db")
        clean_task = _make_task("SRC-125", deliverables=["src/clean.py"])
        bad_task = _make_task("SRC-126", deliverables=["_trash/bad.md"])
        repo.create(clean_task)
        repo.create(bad_task)

        updated_clean = repo.transition("SRC-125", TaskStatus.IN_PROGRESS)
        assert updated_clean.status == TaskStatus.IN_PROGRESS

        with pytest.raises(GateViolationError):
            repo.transition("SRC-126", TaskStatus.IN_PROGRESS)

        c125_after = repo.get("SRC-125")
        assert c125_after is not None
        assert c125_after.status == TaskStatus.IN_PROGRESS
        repo.close()

    def test_no_event_written_on_gate_failure(self, tmp_path: Path) -> None:
        """G1 失败时，events 表不写入 state_transition 事件（事务未提交）。"""
        db_path = tmp_path / "no_event.db"
        init_db(db_path)
        repo = TaskRepository(
            db_path=db_path,
            gate_dir=GATES_DIR,
            project_root=tmp_path,
            enable_gate=True,
        )
        task = _make_task("SRC-127", deliverables=["ARCHIVE/gone.md"])
        repo.create(task)

        before_conn = sqlite3.connect(str(db_path))
        before_conn.row_factory = sqlite3.Row
        before_events = before_conn.execute(
            "SELECT COUNT(*) FROM events WHERE event_type = 'state_transition'"
        ).fetchone()[0]
        before_conn.close()

        with pytest.raises(GateViolationError):
            repo.transition("SRC-127", TaskStatus.IN_PROGRESS)

        after_conn = sqlite3.connect(str(db_path))
        after_conn.row_factory = sqlite3.Row
        after_events = after_conn.execute(
            "SELECT COUNT(*) FROM events WHERE event_type = 'state_transition'"
        ).fetchone()[0]
        after_conn.close()
        repo.close()

        # gate 失败不产生新的 state_transition 事件
        assert after_events == before_events
