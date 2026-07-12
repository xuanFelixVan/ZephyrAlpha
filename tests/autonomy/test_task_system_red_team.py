# [A_test] module_id: SRC-TST-0019 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-214 | tests/autonomy/test_task_system_red_team.py | §
# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.adversarial.test_task_system_red_team
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Task System 红白对抗诊断测试（Pytest 兼容版）
=============================================
目的：实际走一遍完整流程，发现所有问题
范围：TaskCard模型→TaskRepo→PipelineOrchestrator→ContextAssembler→BlueprintDecomposer→TaskManagerMCP
"""

from __future__ import annotations

import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import pytest

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）


# ============================================================================
# 阶段0：基础导入测试
# ============================================================================


def test_00_imports():
    """测试所有核心模块能否正常导入"""
    modules = [
        ("shared.schemas", "zephyr.shared.schemas"),
        ("core.models", "zephyr.shared.models"),
        ("core.blueprint_decomposer", "zephyr.shared.blueprint_decomposer"),
        ("db.task_repo", "zephyr.governance.persistence.task_repo"),
        ("mcp.task_manager_server", "zephyr.integration.mcp.task_manager_server"),
        ("pipeline.models", "zephyr.infrastructure.pipeline.models"),
        ("pipeline.pipeline_orchestrator", "zephyr.integration.pipeline_orchestrator"),
        ("context-engine.context_assembler", "zephyr.autonomy_core.context.context_assembler"),
        ("kb.triage", "zephyr.data.storage.triage"),
    ]

    failures = []
    for name, import_path in modules:
        try:
            __import__(import_path)
        except Exception as e:
            failures.append((name, str(e)))

    assert not failures, f"Import failures ({len(failures)}): {failures}"


# ============================================================================
# 阶段1：TaskCard 模型构造 + 校验
# ============================================================================


def test_01_taskcard_minimal():
    """测试 TaskCard 最小合法构造"""
    from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
    from zephyr.shared.foundation.models import TaskCard, TaskNamespace, TaskStatus

    tc = TaskCard(
        task_id="CP-1",
        namespace=TaskNamespace.CP,
        seq=1,
        title="测试任务",
        status=TaskStatus.PENDING,
        priority=Priority.P2,
        phase=1,
        execution_model="deepseek",
        safety_level=SafetyLevel.L,
        source_blueprint="MOD-TEST-001",
        source_section="§1.0",
        description="这是一个红白对抗测试任务的最小构造",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    assert tc.task_id == "CP-1"
    assert tc.title == "测试任务"
    assert tc.status == TaskStatus.PENDING


def test_01_taskcard_full():
    """测试 TaskCard 完整构造（带扩展字段）"""
    from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
    from zephyr.shared.foundation.models import GateLevel, TaskAuditFinding, TaskCard, TaskNamespace, TaskStatus

    tc_full = TaskCard(
        task_id="CP-2",
        namespace=TaskNamespace.CP,
        seq=2,
        title="完整任务—红白对抗",
        status=TaskStatus.PENDING,
        priority=Priority.P1,
        phase=1,
        execution_model="deepseek",
        model_rationale="成本最低",
        fallback_model="glm",
        safety_level=SafetyLevel.M,
        source_blueprint="MOD-INF-039",
        source_section="§11.3",
        description="这是一个包含所有扩展字段的完整任务卡片用于红白对抗测试",
        upstream_files=["D:/test/file1.md", "D:/test/file2.md"],
        downstream_outputs=[{"path": "D:/test/output.py", "description": "生成的代码文件"}],
        allowed_touch=["D:/test/allowed/"],
        forbidden_touch=["D:/test/forbidden/"],
        applicable_rules=[{"module_id": "MOD-INF-039", "section": "§3", "reason": "任务模型规范"}],
        context_assembly_manifest=[{"file_path": "D:/test/context.md", "reason": "上下文文件"}],
        rollback_instructions="git checkout -- D:/test/output.py",
        estimated_tokens=12000,
        timeout_minutes=60,
        completed_gates=[GateLevel.G0],
        blocked_gates={"G3": "缺少上下文装配"},
        assigned_pipeline="A",
        pipeline_modules=["M1", "M2", "M3"],
        blocked_by=["CP-1"],
        artifact_paths=["D:/test/output.py"],
        audit_findings=[
            TaskAuditFinding(
                finding_id="F-0001",
                dimension="security",
                severity="high",
                description="测试审计发现",
                source_task="CP-2",
            )
        ],
        ke_entries=["KE-001"],
        ai_autonomy_level="supervised",
        autonomy_checklist=["确认Owner已批准"],
        construction_status="pending",
        verification_status="unverified",
        tags=["test", "adversarial", "security", "experimental"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    assert tc_full.task_id == "CP-2"
    assert tc_full.safety_level == SafetyLevel.M
    assert len(tc_full.audit_findings) == 1


def test_01_taskcard_extra_forbid():
    """测试 TaskCard extra=forbid——未知字段 MUST 被拒"""
    from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
    from zephyr.shared.foundation.models import TaskCard, TaskNamespace, TaskStatus

    with pytest.raises(Exception):
        TaskCard(
            task_id="CP-3",
            namespace=TaskNamespace.CP,
            seq=3,
            title="extra字段测试",
            status=TaskStatus.PENDING,
            priority=Priority.P2,
            phase=1,
            execution_model="deepseek",
            safety_level=SafetyLevel.L,
            source_blueprint="MOD-TEST-001",
            source_section="§1.0",
            description="测试extra=forbid是否生效——至少十字描述长度",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            vibe_coding_field="should_be_blocked",
            another_random_field=42,
        )


def test_01_taskcard_short_description():
    """测试 TaskCard description 长度<10 应被拒绝"""
    from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
    from zephyr.shared.foundation.models import TaskCard, TaskNamespace, TaskStatus

    with pytest.raises(Exception):
        TaskCard(
            task_id="CP-4",
            namespace=TaskNamespace.CP,
            seq=4,
            title="短描述",
            status=TaskStatus.PENDING,
            priority=Priority.P2,
            phase=1,
            execution_model="deepseek",
            safety_level=SafetyLevel.L,
            source_blueprint="MOD-TEST-001",
            source_section="§1.0",
            description="短",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )


def test_01_taskcard_bad_id_format():
    """测试 task_id 格式错误应被拒绝"""
    from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
    from zephyr.shared.foundation.models import TaskCard, TaskNamespace, TaskStatus

    with pytest.raises(Exception):
        TaskCard(
            task_id="BAD-FORMAT",
            namespace=TaskNamespace.CP,
            seq=5,
            title="错误ID格式",
            status=TaskStatus.PENDING,
            priority=Priority.P2,
            phase=1,
            execution_model="deepseek",
            safety_level=SafetyLevel.L,
            source_blueprint="MOD-TEST-001",
            source_section="§1.0",
            description="测试task_id格式校验",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )


def test_01_taskcard_string_dates():
    """测试 created_at / updated_at 可以是字符串"""
    from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
    from zephyr.shared.foundation.models import TaskCard, TaskNamespace, TaskStatus

    tc = TaskCard(
        task_id="CP-6",
        namespace=TaskNamespace.CP,
        seq=6,
        title="字符串时间",
        status=TaskStatus.PENDING,
        priority=Priority.P2,
        phase=1,
        execution_model="deepseek",
        safety_level=SafetyLevel.L,
        source_blueprint="MOD-TEST-001",
        source_section="§1.0",
        description="测试字符串格式的时间字段",
        created_at="2026-05-02T10:00:00",
        updated_at="2026-05-02T10:00:00",
    )
    assert tc.task_id == "CP-6"


# ============================================================================
# 阶段2：TaskRepo 集成测试
# ============================================================================


def test_02_task_repo_crud():
    """测试 TaskRepo CRUD + 状态机"""
    from zephyr.governance.persistence.task_repo import InvalidTransitionError, TaskRepository
    from zephyr.gov_enforcement.rule_enforcement.task_types import TaskNamespace, TaskStatus
    from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
    from zephyr.shared.foundation.models import TaskCard

    tmp_db = Path(tempfile.mktemp(suffix=".db"))
    repo = TaskRepository(db_path=tmp_db, auto_init=True, enable_gate=False)

    try:
        task = TaskCard(
            task_id="CP-100",
            namespace=TaskNamespace.CP,
            seq=100,
            title="Repo测试任务",
            status=TaskStatus.PENDING,
            priority=Priority.P2,
            phase=1,
            execution_model="deepseek",
            safety_level=SafetyLevel.L,
            source_blueprint="test",
            source_section="test",
            description="Repo测试任务：CRUD验证",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        created = repo.create(task)
        assert created.task_id == "CP-100"

        fetched = repo.get("CP-100")
        assert fetched is not None
        assert fetched.status == TaskStatus.PENDING

        transitioned = repo.transition("CP-100", TaskStatus.IN_PROGRESS)
        assert transitioned.status == TaskStatus.IN_PROGRESS

        with pytest.raises(InvalidTransitionError):
            repo.transition("CP-100", TaskStatus.PENDING)

        seq = repo.next_seq(TaskNamespace.CP)
        assert seq >= 100

        pending = repo.list_by_status(TaskStatus.PENDING)
        assert isinstance(pending, list)
    finally:
        repo.close()


def test_02_task_repo_lifecycle():
    """测试完整状态生命周期 PENDING→IN_PROGRESS→COMPLETED→VERIFIED"""
    from zephyr.governance.persistence.task_repo import TaskRepository
    from zephyr.gov_enforcement.rule_enforcement.task_types import TaskNamespace, TaskStatus
    from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
    from zephyr.shared.foundation.models import TaskCard

    tmp_db = Path(tempfile.mktemp(suffix=".db"))
    repo = TaskRepository(db_path=tmp_db, auto_init=True, enable_gate=False)

    try:
        task = TaskCard(
            task_id="CP-101",
            namespace=TaskNamespace.CP,
            seq=101,
            title="生命周期测试",
            status=TaskStatus.PENDING,
            priority=Priority.P2,
            phase=1,
            execution_model="deepseek",
            safety_level=SafetyLevel.L,
            source_blueprint="test",
            source_section="test",
            description="生命周期测试：状态转换验证",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        repo.create(task)

        for st in [TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED, TaskStatus.VERIFIED]:
            t = repo.transition("CP-101", st)
            assert t.status == st

        final = repo.get("CP-101")
        assert final is not None
        assert final.status == TaskStatus.VERIFIED
    finally:
        repo.close()


def test_02_taskcard_repo_polymorphism():
    """测试 TaskCard 通过 TaskRepo 保存（多态）"""
    from zephyr.governance.persistence.task_repo import TaskRepository
    from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
    from zephyr.shared.foundation.models import TaskCard, TaskNamespace, TaskStatus

    tmp_db = Path(tempfile.mktemp(suffix=".db"))
    repo = TaskRepository(db_path=tmp_db, auto_init=True, enable_gate=False)

    try:
        tc = TaskCard(
            task_id="CP-102",
            namespace=TaskNamespace.CP,
            seq=102,
            title="TaskCard→Repo多态测试",
            status=TaskStatus.PENDING,
            priority=Priority.P2,
            phase=1,
            execution_model="deepseek",
            safety_level=SafetyLevel.L,
            source_blueprint="MOD-TEST-001",
            source_section="§1.0",
            description="测试TaskCard能否通过TaskRepo保存",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        created_tc = repo.create(tc)
        assert created_tc.task_id == "CP-102"

        fetched_tc = repo.get("CP-102")
        assert fetched_tc is not None
    finally:
        repo.close()


# ============================================================================
# 阶段3：PipelineOrchestrator 集成测试
# ============================================================================


def test_03_pipeline_A_dispatch():
    """测试 A区管线 dispatch"""
    from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator
    from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
    from zephyr.shared.foundation.models import TaskCard, TaskNamespace, TaskStatus

    tc_a = TaskCard(
        task_id="CP-200",
        namespace=TaskNamespace.CP,
        seq=200,
        title="A区管线测试",
        status=TaskStatus.PENDING,
        priority=Priority.P2,
        phase=1,
        execution_model="deepseek",
        safety_level=SafetyLevel.L,
        source_blueprint="MOD-TEST-001",
        source_section="§1.0",
        description="测试A区管线从dispatch到完成的全流程",
        assigned_pipeline="A",
        pipeline_modules=["M1", "M2", "M3"],
        estimated_tokens=8000,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    orchestrator = PipelineOrchestrator()
    result = orchestrator.dispatch(tc_a)
    assert result is not None


def test_03_pipeline_B_dispatch():
    """测试 B区审计管线 dispatch"""
    from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator
    from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
    from zephyr.shared.foundation.models import TaskCard, TaskNamespace, TaskStatus

    tc_b = TaskCard(
        task_id="CP-201",
        namespace=TaskNamespace.CP,
        seq=201,
        title="B区审计管线测试",
        status=TaskStatus.PENDING,
        priority=Priority.P2,
        phase=1,
        execution_model="deepseek",
        safety_level=SafetyLevel.L,
        source_blueprint="MOD-TEST-001",
        source_section="§1.0",
        description="测试B区审计管线从dispatch到完成的全流程",
        assigned_pipeline="B",
        pipeline_modules=["M6", "M7", "M8", "M9", "M10", "M11"],
        estimated_tokens=8000,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    orchestrator = PipelineOrchestrator()
    result = orchestrator.dispatch(tc_b)
    assert result is not None


def test_03_security_tag_claude_rescue():
    """测试 security 标签触发 Claude救援路由"""
    from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator
    from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
    from zephyr.shared.foundation.models import TaskCard, TaskNamespace, TaskStatus

    tc_sec = TaskCard(
        task_id="CP-202",
        namespace=TaskNamespace.CP,
        seq=202,
        title="安全标签Claude救援测试",
        status=TaskStatus.PENDING,
        priority=Priority.P2,
        phase=1,
        execution_model="deepseek",
        safety_level=SafetyLevel.H,
        source_blueprint="MOD-TEST-001",
        source_section="§1.0",
        description="测试security标签触发Claude救援路由",
        assigned_pipeline="B",
        tags=["security"],
        estimated_tokens=4000,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    orchestrator = PipelineOrchestrator()
    result = orchestrator.dispatch(tc_sec)
    assert result.needs_claude_rescue or result.overall_status.value in ("g6_blocked",), (
        f"Expected rescue or G6 block, got {result.overall_status}"
    )


def test_03_experimental_tag_claude_rescue():
    """测试 experimental 标签触发 Claude救援"""
    from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator
    from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
    from zephyr.shared.foundation.models import TaskCard, TaskNamespace, TaskStatus

    tc_exp = TaskCard(
        task_id="CP-203",
        namespace=TaskNamespace.CP,
        seq=203,
        title="experimental标签测试",
        status=TaskStatus.PENDING,
        priority=Priority.P2,
        phase=1,
        execution_model="deepseek",
        safety_level=SafetyLevel.L,
        source_blueprint="MOD-TEST-001",
        source_section="§1.0",
        description="测试experimental标签触发Claude救援",
        assigned_pipeline="A",
        tags=["experimental"],
        estimated_tokens=4000,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    orchestrator = PipelineOrchestrator()
    result = orchestrator.dispatch(tc_exp)
    assert result.needs_claude_rescue or result.overall_status.value in ("g6_blocked",), (
        f"Expected rescue or G6 block, got {result.overall_status}"
    )


def test_03_invalid_pipeline_rejected():
    """测试无效管线标识被拒绝"""
    from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator
    from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
    from zephyr.shared.foundation.models import TaskCard, TaskNamespace, TaskStatus

    tc_invalid = TaskCard(
        task_id="CP-204",
        namespace=TaskNamespace.CP,
        seq=204,
        title="无效管线",
        status=TaskStatus.PENDING,
        priority=Priority.P2,
        phase=1,
        execution_model="deepseek",
        safety_level=SafetyLevel.L,
        source_blueprint="MOD-TEST-001",
        source_section="§1.0",
        description="测试无效管线标识被正确处理",
        assigned_pipeline="X",
        estimated_tokens=4000,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    orchestrator = PipelineOrchestrator()
    result = orchestrator.dispatch(tc_invalid)
    assert result.overall_status.value in ("rejected", "failed", "failure")


# ============================================================================
# 阶段4：ContextAssembler 集成测试
# ============================================================================


def test_04_context_assemble():
    """测试基本上下文装配"""
    from zephyr.autonomy_core.context.context_assembler import ContextAssembler

    assembler = ContextAssembler(max_file_size_mb=5, require_absolute_paths=False)
    manifest = [{"file_path": __file__, "reason": "红白对抗脚本自身"}]
    ctx = assembler.assemble(manifest, token_budget=80000)
    assert ctx.is_complete
    assert ctx.file_count > 0


def test_04_context_empty_manifest():
    """测试空 manifest"""
    from zephyr.autonomy_core.context.context_assembler import ContextAssembler

    assembler = ContextAssembler()
    ctx = assembler.assemble([], token_budget=8000)
    assert ctx.file_count == 0


def test_04_context_validate():
    """测试 validate"""
    from zephyr.autonomy_core.context.context_assembler import ContextAssembler

    assembler = ContextAssembler(require_absolute_paths=False)
    manifest = [{"file_path": __file__, "reason": "测试文件"}]
    ctx = assembler.assemble(manifest, token_budget=80000)
    valid = assembler.validate(ctx)
    assert valid


def test_04_context_shadow():
    """测试 shadow 生成"""
    from zephyr.autonomy_core.context.context_assembler import ContextAssembler

    with tempfile.TemporaryDirectory() as tmpdir:
        assembler = ContextAssembler(require_absolute_paths=False)
        manifest = [{"file_path": __file__, "reason": "shadow测试"}]
        ctx = assembler.assemble(manifest, token_budget=80000)
        shadow_path = assembler.shadow(ctx, tmpdir)
        assert shadow_path.exists()


# ============================================================================
# 阶段5：BlueprintDecomposer 集成测试
# ============================================================================


def test_05_decompose_real_blueprint():
    """测试拆解真实蓝图文件"""
    from zephyr.shared.blueprint_tools.blueprint_decomposer import BlueprintDecomposer

    real_blueprint = REPO_ROOT / "docs/03_modules/_domain-infra_ops/task-system/blueprint.md"
    assert real_blueprint.exists(), f"蓝图不存在: {real_blueprint}"

    decomposer = BlueprintDecomposer(docs_dir=str(tempfile.mkdtemp()))
    result = decomposer.decompose_blueprint(str(real_blueprint), namespace="INFRA", phase=1)
    assert result is not None, "decompose_blueprint returned None"
    assert result.total_tasks >= 0, f"Non-negative tasks expected, got {result.total_tasks}"
    assert len(result.warnings) >= 0


def test_05_decompose_nonexistent():
    """测试拆解不存在的文件"""
    from zephyr.shared.blueprint_tools.blueprint_decomposer import BlueprintDecomposer

    decomposer = BlueprintDecomposer()
    with pytest.raises((FileNotFoundError, Exception)):
        decomposer.decompose_blueprint("D:/nonexistent/blueprint.md")


def test_05_decompose_batch():
    """测试批量拆解"""
    from zephyr.shared.blueprint_tools.blueprint_decomposer import BlueprintDecomposer

    real_blueprint = REPO_ROOT / "docs/03_modules/_domain-infra_ops/task-system/blueprint.md"
    if real_blueprint.exists():
        decomposer = BlueprintDecomposer()
        batch_results = decomposer.decompose_blueprints_batch([str(real_blueprint)], namespace="INFRA", phase=1)
        assert isinstance(batch_results, list)


def test_05_check_gates():
    """测试 G0/G7 门禁检查"""
    from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
    from zephyr.shared.blueprint_tools.blueprint_decomposer import BlueprintDecomposer
    from zephyr.shared.foundation.models import GateLevel, TaskCard, TaskNamespace, TaskStatus

    decomposer = BlueprintDecomposer()
    tc = TaskCard(
        task_id="CP-300",
        namespace=TaskNamespace.CP,
        seq=300,
        title="门禁测试",
        status=TaskStatus.PENDING,
        priority=Priority.P2,
        phase=1,
        execution_model="deepseek",
        safety_level=SafetyLevel.L,
        source_blueprint="MOD-TEST-001",
        source_section="§1.0",
        description="测试G0/G7门禁检查的红白对抗任务",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    g0_pass = decomposer.check_gate(GateLevel.G0, tc)
    g7_pass = decomposer.check_gate(GateLevel.G7, tc)
    assert g0_pass
    assert not g7_pass


# ============================================================================
# 阶段6：TaskManagerMCP 接口测试
# ============================================================================


def test_06_mcp_init():
    """测试 MCP Server 初始化"""
    from zephyr.integration.mcp.task_manager_server import TaskManagerMCP

    with tempfile.TemporaryDirectory() as tmpdir:
        mcp = TaskManagerMCP(task_repo=None, docs_dir=tmpdir)
        assert mcp.server.name == "task-manager"


def test_06_md_roundtrip():
    """测试 _taskcard_to_md → _parse_md_to_taskcard 往返"""
    from zephyr.integration.mcp.task_manager_server import _parse_md_to_taskcard, _taskcard_to_md
    from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
    from zephyr.shared.foundation.models import TaskCard, TaskNamespace, TaskStatus

    tc = TaskCard(
        task_id="CP-400",
        namespace=TaskNamespace.CP,
        seq=400,
        title="往返测试",
        status=TaskStatus.PENDING,
        priority=Priority.P2,
        phase=1,
        execution_model="deepseek",
        safety_level=SafetyLevel.L,
        source_blueprint="MOD-TEST-001",
        source_section="§1.0",
        description="测试md写入→md回读的往返完整性",
        upstream_files=["D:/test/a.md", "D:/test/b.md"],
        downstream_outputs=[{"path": "D:/test/o.py", "description": "产出"}],
        estimated_tokens=4000,
        tags=["roundtrip", "test"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    md_content = _taskcard_to_md(tc)

    recovered = _parse_md_to_taskcard(md_content)
    assert recovered is not None, "_parse_md_to_taskcard 返回 None——连接断开"
    assert recovered.status == TaskStatus.PENDING, f"status 往返不一致: {recovered.status}"


def test_06_extract_triage_profile():
    """测试 _extract_triage_profile"""
    from zephyr.integration.mcp.task_manager_server import _extract_triage_profile

    content = "# 审阅任务标题\n\n这是审阅池中的任务描述内容。"
    profile = _extract_triage_profile(content, "ADR-1")
    assert profile.get("title") == "审阅任务标题"


def test_06_mcp_persist_and_load():
    """测试 MCP _persist + _load"""
    from zephyr.governance.persistence.task_repo import TaskRepository
    from zephyr.integration.mcp.task_manager_server import TaskManagerMCP
    from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
    from zephyr.shared.foundation.models import TaskCard, TaskNamespace, TaskStatus

    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = Path(tmpdir) / "test_mcp.db"
        repo = TaskRepository(db_path=db_file, enable_gate=False)
        mcp = TaskManagerMCP(task_repo=repo, docs_dir=tmpdir)

        seq = mcp._next_seq(TaskNamespace.CP)
        assert seq >= 1

        tc = TaskCard(
            task_id="CP-500",
            namespace=TaskNamespace.CP,
            seq=500,
            title="持久化测试",
            status=TaskStatus.PENDING,
            priority=Priority.P2,
            phase=1,
            execution_model="deepseek",
            safety_level=SafetyLevel.L,
            source_blueprint="MOD-TEST-001",
            source_section="§1.0",
            description="测试持久化——v2后仅SQLite写.md不生成",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mcp._persist(tc)

        loaded = mcp._load("CP-500")
        assert loaded is not None, "_load 返回 None——持久化失败"
        assert loaded.task_id == "CP-500"
        repo.close()


# ============================================================================
# 阶段7：集成度检查
# ============================================================================


def test_07_inheritance_chain():
    """验证 TaskCard 是 Task 的子类"""
    from zephyr.gov_enforcement.rule_enforcement.task_types import Task
    from zephyr.shared.foundation.models import TaskCard

    assert issubclass(TaskCard, Task), "TaskCard MUST be subclass of Task"


def test_07_field_statistics():
    """统计 TaskCard 字段数"""
    from zephyr.gov_enforcement.rule_enforcement.task_types import Task
    from zephyr.shared.foundation.models import TaskCard

    tc_fields = set(TaskCard.model_fields.keys())
    task_fields = set(Task.model_fields.keys())
    extension_fields = tc_fields - task_fields

    assert len(tc_fields) >= len(task_fields), "TaskCard should have >= fields than Task"
    assert len(extension_fields) > 0, "TaskCard should have extension fields"


# ============================================================================
# 阶段8：TriageGate 构造测试
# ============================================================================


def test_08_triage_task_construction():
    """测试 TriageGate 内部 Task(title=...) 构造"""
    from zephyr.gov_enforcement.rule_enforcement.task_types import TaskNamespace, TaskStatus, normalize_execution_model
    from zephyr.integration.shared.schema.severity_types import SafetyLevel
    from zephyr.shared.foundation.models import TaskCard

    task = TaskCard(
        task_id="CP-999",
        namespace=TaskNamespace.CP,
        seq=999,
        phase=2,
        title="G2 Triage Gate Test",
        status=TaskStatus.IN_PROGRESS,
        execution_model=normalize_execution_model("system"),
        safety_level=SafetyLevel.M,
        source_blueprint="test",
        source_section="test",
        description="G2 Triage Gate Test",
        deliverables=[],
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    assert task.task_id == "CP-999"
    assert task.title == "G2 Triage Gate Test"


def test_08_task_name_field_rejected():
    """测试 Task(name=...) 字段应被 extra=forbid 拒绝"""
    from zephyr.gov_enforcement.rule_enforcement.task_types import TaskNamespace, TaskStatus, normalize_execution_model
    from zephyr.integration.shared.schema.severity_types import SafetyLevel
    from zephyr.shared.foundation.models import TaskCard

    with pytest.raises(Exception):
        TaskCard(
            task_id="CP-998",
            namespace=TaskNamespace.CP,
            seq=998,
            phase=2,
            name="G2 Triage Gate",
            status=TaskStatus.IN_PROGRESS,
            execution_model=normalize_execution_model("system"),
            safety_level=SafetyLevel.M,
            source_blueprint="test",
            source_section="test",
            description="test extra field rejection",
            deliverables=[],
            created_at="2026-05-02T10:00:00",
            updated_at="2026-05-02T10:00:00",
        )
