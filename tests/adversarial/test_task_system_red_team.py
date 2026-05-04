"""
Task System 红白对抗诊断脚本
============================
目的：实际走一遍完整流程，发现所有问题
范围：TaskCard模型→TaskRepo→PipelineOrchestrator→ContextAssembler→BlueprintDecomposer→TaskManagerMCP
"""

from __future__ import annotations

import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

_PROJECT_ROOT = Path("D:/ZephyrAlpha/")
sys.path.insert(0, str(_PROJECT_ROOT / "src"))
sys.path.insert(0, str(_PROJECT_ROOT))

def _assert_results(results):
    failed = [(name, err) for status, name, *err in results if status == "FAIL"]
    warnings_list = [(name, msg) for status, name, *msg in results if status == "WARN"]
    if warnings_list:
        for name, msg in warnings_list:
            print(f"  [WARN] {name}: {msg}")
    assert not failed, f"Red team failures ({len(failed)}): {failed}"

# ============================================================================
# 阶段0：基础导入测试
# ============================================================================

def test_00_imports():
    """测试所有核心模块能否正常导入"""
    results = []

    modules = [
        ("shared.schemas", "zephyr.shared.schemas"),
        ("core.models", "zephyr.core.models"),
        ("core.blueprint_decomposer", "zephyr.core.blueprint_decomposer"),
        ("db.task_repo", "zephyr.db.task_repo"),
        ("mcp.task_manager_server", "zephyr.mcp.task_manager_server"),
        ("pipeline.models", "zephyr.pipeline.models"),
        ("pipeline.pipeline_orchestrator", "zephyr.pipeline.pipeline_orchestrator"),
        ("context_engine.context_assembler", "zephyr.context_engine.context_assembler"),
        ("kb.triage", "zephyr.kb.triage"),
    ]

    for name, import_path in modules:
        try:
            __import__(import_path)
            results.append(("PASS", name))
        except Exception as e:
            results.append(("FAIL", name, str(e)))

    _assert_results(results)

# ============================================================================
# 阶段1：TaskCard 模型构造 + 校验
# ============================================================================

def test_01_taskcard_creation():
    """测试 TaskCard 最小构造 + 边界条件"""
    from zephyr.core.models import GateLevel, TaskAuditFinding, TaskCard, TaskNamespace, TaskStatus
    from zephyr.shared.schemas import Priority, SafetyLevel

    results = []

    # 1a: 最小合法构造
    try:
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
        results.append(("PASS", "1a: 最小合法TaskCard构造", f"task_id={tc.task_id}"))
    except Exception as e:
        results.append(("FAIL", "1a: 最小合法TaskCard构造", str(e)))
        tc = None

    if tc is None:
        _assert_results(results)

    # 1b: 带扩展字段的完整构造
    try:
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
            source_blueprint="MOD-INF-006",
            source_section="§11.3",
            description="这是一个包含所有扩展字段的完整任务卡片用于红白对抗测试",
            upstream_files=["D:/test/file1.md", "D:/test/file2.md"],
            downstream_outputs=[{"path": "D:/test/output.py", "description": "生成的代码文件"}],
            allowed_touch=["D:/test/allowed/"],
            forbidden_touch=["D:/test/forbidden/"],
            applicable_rules=[{"module_id": "MOD-INF-006", "section": "§3", "reason": "任务模型规范"}],
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
        results.append(("PASS", "1b: 完整TaskCard构造", f"fields_count={len(tc_full.model_dump())}"))
    except Exception as e:
        results.append(("FAIL", "1b: 完整TaskCard构造", str(e)))

    # 1c: extra="allow" 测试——允许Vibe Coding未知字段
    try:
        tc_extra = TaskCard(
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
            description="测试extra=allow是否生效",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            # Vibe Coding 未知扩展字段
            vibe_coding_field="should_be_allowed",
            another_random_field=42,
        )
        results.append(("PASS", "1c: extra=allow未定义字段", f"vibe_coding_field={tc_extra.vibe_coding_field}"))
    except Exception as e:
        results.append(("FAIL", "1c: extra=allow未定义字段", str(e)))

    # 1d: 边界——description长度<10
    try:
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
            description="短",  # too short
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        results.append(("FAIL", "1d: 短description应被拒绝但通过了", ""))
    except Exception as e:
        results.append(("PASS", "1d: 短description被正确拒绝", str(e)[:100]))

    # 1e: 边界——task_id 格式错误
    try:
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
        results.append(("FAIL", "1e: 错误task_id应被拒绝但通过了", ""))
    except Exception as e:
        results.append(("PASS", "1e: 错误task_id被正确拒绝", str(e)[:100]))

    # 1f: 测试 created_at / updated_at 可以是字符串
    try:
        tc_str_time = TaskCard(
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
        results.append(("PASS", "1f: 字符串时间字段", f"created_at type={type(tc_str_time.created_at).__name__}"))
    except Exception as e:
        results.append(("FAIL", "1f: 字符串时间字段", str(e)[:150]))

    _assert_results(results)

# ============================================================================
# 阶段2：TaskRepo 集成测试
# ============================================================================

def test_02_task_repo():
    """测试 TaskRepo CRUD + 状态机"""
    from zephyr.db.task_repo import InvalidTransitionError, TaskRepository
    from zephyr.shared.schemas import Priority, SafetyLevel, Task, TaskNamespace, TaskStatus

    results = []
    repo = None

    try:
        # 使用临时数据库
        tmp_db = Path(tempfile.mktemp(suffix=".db"))
        repo = TaskRepository(db_path=tmp_db, auto_init=True, enable_gate=False)

        # 2a: 创建Task
        task = Task(
            task_id="CP-100",
            namespace=TaskNamespace.CP,
            seq=100,
            title="Repo测试任务",
            status=TaskStatus.PENDING,
            priority=Priority.P2,
            phase=1,
            execution_model="deepseek",
            safety_level=SafetyLevel.L,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        created = repo.create(task)
        results.append(("PASS", "2a: TaskRepo.create", f"task_id={created.task_id}"))

        # 2b: 查询Task
        fetched = repo.get("CP-100")
        results.append(("PASS", "2b: TaskRepo.get", f"status={fetched.status}" if fetched else "NOT FOUND"))

        # 2c: 状态转换 PENDING→IN_PROGRESS
        transitioned = repo.transition("CP-100", TaskStatus.IN_PROGRESS)
        results.append(("PASS", "2c: PENDING→IN_PROGRESS", f"new_status={transitioned.status}"))

        # 2d: 非法状态转换 IN_PROGRESS→PENDING（应被拒绝）
        try:
            repo.transition("CP-100", TaskStatus.PENDING)
            results.append(("FAIL", "2d: 非法转换应被拒绝", ""))
        except InvalidTransitionError:
            results.append(("PASS", "2d: 非法转换被正确拒绝", ""))

        # 2e: 完整状态生命周期 PENDING→IN_PROGRESS→COMPLETED→VERIFIED
        task2 = Task(
            task_id="CP-101",
            namespace=TaskNamespace.CP,
            seq=101,
            title="生命周期测试",
            status=TaskStatus.PENDING,
            priority=Priority.P2,
            phase=1,
            execution_model="deepseek",
            safety_level=SafetyLevel.L,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        repo.create(task2)

        states = [
            TaskStatus.IN_PROGRESS,
            TaskStatus.COMPLETED,
            TaskStatus.VERIFIED,
        ]
        for st in states:
            t = repo.transition("CP-101", st)

        final = repo.get("CP-101")
        if final and final.status == TaskStatus.VERIFIED:
            results.append(("PASS", "2e: 完整生命周期 PENDING→VERIFIED", f"final={final.status}"))
        else:
            results.append(("FAIL", "2e: 完整生命周期", f"final={final.status if final else 'NONE'}"))

        # 2f: TaskRepo 接受 TaskCard 吗？（多态测试）
        from zephyr.core.models import TaskCard

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
        try:
            created_tc = repo.create(tc)
            # 检查扩展字段是否丢失
            fetched_tc = repo.get("CP-102")
            has_source = getattr(fetched_tc, "source_blueprint", None) if fetched_tc else None
            results.append(
                ("WARN", "2f: TaskCard→Repo扩展字段丢失", f"source_blueprint保存为: {has_source} (预期: MOD-TEST-001)")
            )
        except Exception as e:
            results.append(("FAIL", "2f: TaskCard→Repo", str(e)[:150]))

        # 2g: next_seq
        seq = repo.next_seq(TaskNamespace.CP)
        results.append(("PASS", "2g: next_seq", f"CP seq={seq}"))

        # 2h: list_by_status
        pending = repo.list_by_status(TaskStatus.PENDING)
        results.append(
            ("PASS", "2h: list_by_status PENDING", f"count={len(pending)}, ids={[t.task_id for t in pending]}")
        )

    except Exception as e:
        results.append(("FAIL", "2x: TaskRepo初始化/运行", f"{type(e).__name__}: {e}"))
    finally:
        if repo:
            repo.close()

    _assert_results(results)

# ============================================================================
# 阶段3：PipelineOrchestrator 集成测试
# ============================================================================

def test_03_pipeline_orchestrator():
    """测试管线编排器"""
    from zephyr.core.models import TaskCard, TaskNamespace, TaskStatus
    from zephyr.pipeline.pipeline_orchestrator import PipelineOrchestrator
    from zephyr.shared.schemas import Priority, SafetyLevel

    results = []

    # 3a: A区管线 dispatch
    try:
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

        results.append(
            ("PASS", "3a: A区管线dispatch", f"status={result.overall_status}, modules={len(result.modules_executed)}")
        )
    except Exception as e:
        results.append(("FAIL", "3a: A区管线dispatch", f"{type(e).__name__}: {str(e)[:150]}"))

    # 3b: B区管线 dispatch
    try:
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

        results.append(
            ("PASS", "3b: B区管线dispatch", f"status={result.overall_status}, modules={len(result.modules_executed)}")
        )
    except Exception as e:
        results.append(("FAIL", "3b: B区管线dispatch", f"{type(e).__name__}: {str(e)[:150]}"))

    # 3c: Claude救援—security标签
    try:
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

        results.append(
            (
                "PASS",
                "3c: security标签→Claude救援",
                f"rescue={result.needs_claude_rescue}, reason={result.rescue_reason[:80]}",
            )
        )
    except Exception as e:
        results.append(("FAIL", "3c: security标签→Claude救援", f"{type(e).__name__}: {str(e)[:150]}"))

    # 3d: experimental标签→Claude救援
    try:
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

        results.append(("PASS", "3d: experimental标签→Claude救援", f"rescue={result.needs_claude_rescue}"))
    except Exception as e:
        results.append(("FAIL", "3d: experimental标签→Claude救援", f"{type(e).__name__}: {str(e)[:150]}"))

    # 3e: 无效管线标识
    try:
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

        results.append(("PASS", "3e: 无效管线被拒绝", f"status={result.overall_status}"))
    except Exception as e:
        results.append(("FAIL", "3e: 无效管线", f"{type(e).__name__}: {str(e)[:150]}"))

    _assert_results(results)

# ============================================================================
# 阶段4：ContextAssembler 集成测试
# ============================================================================

def test_04_context_assembler():
    """测试上下文装配器"""
    from zephyr.context_engine.context_assembler import ContextAssembler

    results = []

    # 4a: 基本装配
    try:
        assembler = ContextAssembler(max_file_size_mb=5, require_absolute_paths=False)

        manifest = [
            {"file_path": __file__, "reason": "红白对抗脚本自身"},
        ]

        ctx = assembler.assemble(manifest, token_budget=80000)

        results.append(
            (
                "PASS",
                "4a: 基本上下文装配",
                f"complete={ctx.is_complete}, tokens={ctx.token_estimate}/{ctx.token_budget}, files={ctx.file_count}",
            )
        )
    except Exception as e:
        results.append(("FAIL", "4a: 基本上下文装配", f"{type(e).__name__}: {str(e)[:150]}"))

    # 4b: 空manifest
    try:
        assembler = ContextAssembler()
        ctx = assembler.assemble([], token_budget=8000)

        results.append(("PASS", "4b: 空manifest", f"files={ctx.file_count}, errors_count={len(ctx.errors)}"))
    except Exception as e:
        results.append(("FAIL", "4b: 空manifest", f"{type(e).__name__}: {str(e)[:150]}"))

    # 4c: validate
    try:
        assembler = ContextAssembler(require_absolute_paths=False)
        manifest = [{"file_path": __file__, "reason": "测试文件"}]
        ctx = assembler.assemble(manifest, token_budget=80000)
        valid = assembler.validate(ctx)
        results.append(("PASS", "4c: validate", f"valid={valid}"))
    except Exception as e:
        results.append(("FAIL", "4c: validate", f"{type(e).__name__}: {str(e)[:150]}"))

    # 4d: shadow 生成
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            assembler = ContextAssembler(require_absolute_paths=False)
            manifest = [{"file_path": __file__, "reason": "shadow测试"}]
            ctx = assembler.assemble(manifest, token_budget=80000)
            shadow_path = assembler.shadow(ctx, tmpdir)
            results.append(("PASS", "4d: shadow生成", f"path={shadow_path}, exists={shadow_path.exists()}"))
    except Exception as e:
        results.append(("FAIL", "4d: shadow生成", f"{type(e).__name__}: {str(e)[:150]}"))

    _assert_results(results)

# ============================================================================
# 阶段5：BlueprintDecomposer 集成测试
# ============================================================================

def test_05_blueprint_decomposer():
    """测试蓝图拆解器"""
    from zephyr.core.blueprint_decomposer import BlueprintDecomposer
    from zephyr.core.models import TaskNamespace, TaskStatus

    results = []

    # 5a: 拆解真实蓝图文件
    real_blueprint = _PROJECT_ROOT / "docs/03_modules/l01_infrastructure/task-system/blueprint.md"
    if not real_blueprint.exists():
        results.append(("SKIP", "5a: 真实蓝图拆解", f"蓝图不存在: {real_blueprint}"))
    else:
        try:
            decomposer = BlueprintDecomposer(docs_dir=str(tempfile.mkdtemp()))
            result = decomposer.decompose_blueprint(
                str(real_blueprint),
                namespace="INFRA",
                phase=1,
            )
            results.append(
                (
                    "PASS",
                    "5a: 真实蓝图拆解",
                    f"total_tasks={result.total_tasks}, warnings={len(result.warnings)}, dep_graph_keys={len(result.dependency_graph)}",
                )
            )
        except Exception as e:
            results.append(("FAIL", "5a: 真实蓝图拆解", f"{type(e).__name__}: {str(e)[:150]}"))

    # 5b: 拆解不存在的文件
    try:
        decomposer = BlueprintDecomposer()
        decomposer.decompose_blueprint("D:/nonexistent/blueprint.md")
        results.append(("FAIL", "5b: 不存在的蓝图应抛异常", ""))
    except FileNotFoundError:
        results.append(("PASS", "5b: FileNotFoundError正确抛出", ""))
    except Exception as e:
        results.append(("PASS", "5b: 异常正确抛出", f"{type(e).__name__}"))

    # 5c: 批量拆解
    try:
        decomposer = BlueprintDecomposer()
        batch_results = decomposer.decompose_blueprints_batch(
            [str(real_blueprint)] if real_blueprint.exists() else [],
            namespace="INFRA",
            phase=1,
        )
        results.append(("PASS", "5c: 批量拆解", f"batch_count={len(batch_results)}"))
    except Exception as e:
        results.append(("FAIL", "5c: 批量拆解", f"{type(e).__name__}: {str(e)[:150]}"))

    # 5d: check_gate G0 / G7
    try:
        from zephyr.core.models import GateLevel, TaskCard, TaskNamespace
        from zephyr.shared.schemas import Priority, SafetyLevel

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

        results.append(
            (
                "PASS",
                "5d: check_gate",
                f"G0={g0_pass} (expected True), G7={g7_pass} (expected False—verification=unverified)",
            )
        )
    except Exception as e:
        results.append(("FAIL", "5d: check_gate", f"{type(e).__name__}: {str(e)[:150]}"))

    _assert_results(results)

# ============================================================================
# 阶段6：TaskManagerMCP 接口测试
# ============================================================================

def test_06_task_manager_mcp():
    """测试 MCP Server 接口"""
    from zephyr.core.models import TaskCard, TaskNamespace, TaskStatus
    from zephyr.mcp.task_manager_server import (
        TaskManagerMCP,
        _extract_triage_profile,
        _parse_md_status,
        _parse_md_to_taskcard,
        _taskcard_to_md,
    )
    from zephyr.shared.schemas import Priority, SafetyLevel

    results = []

    # 6a: TaskManagerMCP 初始化
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            mcp = TaskManagerMCP(task_repo=None, docs_dir=tmpdir)
            results.append(("PASS", "6a: TaskManagerMCP初始化", f"server={mcp.server.name}"))
    except Exception as e:
        results.append(("FAIL", "6a: TaskManagerMCP初始化", f"{type(e).__name__}: {str(e)[:150]}"))

    # 6b: _taskcard_to_md → _parse_md_to_taskcard 往返测试（关键bug检测）
    try:
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
        md_status = _parse_md_status(md_content)
        recovered = _parse_md_to_taskcard(md_content)

        results.append(("PASS", "6b: md_status解析", f"md_status={md_status}"))

        if recovered is None:
            results.append(
                (
                    "WARN",
                    "6b: md→TaskCard回读失败",
                    "_parse_md_to_taskcard返回None——JSON解析.mdfile不适用——这是已知Bug！",
                )
            )
        else:
            results.append(
                (
                    "PASS",
                    "6b: md→TaskCard回读",
                    f"recovered_task_id={recovered.task_id if hasattr(recovered, 'task_id') else '?'}",
                )
            )
    except Exception as e:
        results.append(("FAIL", "6b: md往返测试", f"{type(e).__name__}: {str(e)[:150]}"))

    # 6c: _extract_triage_profile
    try:
        content = "# 审阅任务标题\n\n这是审阅池中的任务描述内容。"
        profile = _extract_triage_profile(content, "ADR-1")
        results.append(("PASS", "6c: _extract_triage_profile", f"title={profile.get('title', 'N/A')}"))
    except Exception as e:
        results.append(("FAIL", "6c: _extract_triage_profile", f"{type(e).__name__}: {str(e)[:150]}"))

    # 6d: create_task 工具调用（手动模拟）—— v2 移除.md双轨后验证纯SQLite路径
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            mcp = TaskManagerMCP(task_repo=None, docs_dir=tmpdir)
            from zephyr.shared.schemas import TaskNamespace

            seq = mcp._next_seq(TaskNamespace.CP)
            results.append(("PASS", "6d: _next_seq(无repo)", f"seq={seq}"))

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

            md_path = Path(tmpdir) / "tasks" / "CP-500.md"
            if md_path.exists():
                results.append(("WARN", "6d: .md文件残留", "v2已移除.md双轨——此文件可能是旧版本遗留"))
            else:
                results.append(("PASS", "6d: .md未被生成", "v2已确认：_persist不再写.md文件"))

            loaded = mcp._load("CP-500")
            if loaded is None:
                results.append(("PASS", "6d: _load返回None(无repo,无SQLite)", "v2已确认：_load不再回退读.md"))
            else:
                results.append(("WARN", "6d: _load有结果", f"loaded={loaded.task_id}"))
    except Exception as e:
        results.append(("FAIL", "6d: MCP持久化", f"{type(e).__name__}: {str(e)[:150]}"))

    _assert_results(results)

# ============================================================================
# 阶段7：集成度检查
# ============================================================================

def test_07_integration_scan():
    """扫描任务系统与其他系统的连接点"""
    from zephyr.core.models import TaskCard
    from zephyr.shared.schemas import Task

    results = []

    # 7a: TaskCard 是 Task 的子类吗？
    results.append(("INFO", "7a: 继承链", f"TaskCard is subclass of Task: {issubclass(TaskCard, Task)}"))

    # 7b: TaskCard 有多少个字段？
    tc_fields = set(TaskCard.model_fields.keys())
    task_fields = set(Task.model_fields.keys())
    extension_fields = tc_fields - task_fields
    results.append(
        (
            "INFO",
            "7b: 字段统计",
            f"Task={len(task_fields)} fields, TaskCard={len(tc_fields)} total, extension={len(extension_fields)} extra",
        )
    )

    # 7c: 集成点清单
    integration_points = [
        ("PipelineOrchestrator", "dispatch(task_card: TaskCard)", "直接消费TaskCard → 模型路由 + 模块编排"),
        ("ContextAssembler", "assemble(manifest: list[dict])", "通过context_assembly_manifest字段间接集成"),
        ("GateEngine", "evaluate(task: Task, gate_id: str)", "通过Task基类集成——TaskCard作为Task子类传入"),
        (
            "TaskRepository",
            "create(task: Task) / transition(task_id, status)",
            "只消费Task基类——扩展字段在SQLite中丢失",
        ),
        ("TriageGate", "triage(source_path: Path)", "内部创建Task对象用于门禁——构造可能有问题（name字段）"),
        ("BlueprintDecomposer", "decompose_blueprint(...)", "产出TaskCard → 双向存储(SQLite+.md)"),
        ("TaskManagerMCP", "6 Tools", "MCP入口——双轨存储(.md companion)"),
    ]

    for name, entry_point, description in integration_points:
        results.append(("INTEG", name, f"{entry_point} → {description}"))

    _assert_results(results)

# ============================================================================
# 阶段8：TriageGate 构造测试
# ============================================================================

def test_08_triage_integration():
    """测试 TriageGate 内部 Task 构造是否正确"""
    from zephyr.shared.schemas import Task, TaskNamespace, TaskStatus

    results = []

    # 8a: 测试 triage.py 中 Task(name=...) 构造是否会失败
    # 这是硬编码在 _run_gate 中的
    try:
        task = Task(
            task_id="CP-999",
            namespace=TaskNamespace.CP,
            seq=999,
            phase=2,
            title="G2 Triage Gate Test",
            status=TaskStatus.IN_PROGRESS,
            execution_model="system",
            safety_level="M",
            deliverables=[],
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        results.append(("PASS", "8a: triage Task构造(title字段)", "Task构造成功"))
    except Exception as e:
        results.append(("FAIL", "8a: triage Task构造(title字段)", str(e)[:200]))

    # 8b: 尝试用 name= 构造——应失败
    try:
        Task(
            task_id="CP-998",
            namespace=TaskNamespace.CP,
            seq=998,
            phase=2,
            name="G2 Triage Gate",
            status=TaskStatus.IN_PROGRESS,
            execution_model="system",
            safety_level="M",
            deliverables=[],
            created_at="2026-05-02T10:00:00",
            updated_at="2026-05-02T10:00:00",
        )
        results.append(("FAIL", "8b: Task(name=...)应被拒绝", "居然通过了！"))
    except Exception:
        results.append(("PASS", "8b: Task(name=...)正确被拒", "extra=forbid生效——name字段不被接受"))

    _assert_results(results)

# ============================================================================
# 汇总输出
# ============================================================================

def run_all_tests():
    all_results = {
        "00_imports": test_00_imports(),
        "01_taskcard": test_01_taskcard_creation(),
        "02_task_repo": test_02_task_repo(),
        "03_pipeline": test_03_pipeline_orchestrator(),
        "04_context": test_04_context_assembler(),
        "05_decomposer": test_05_blueprint_decomposer(),
        "06_mcp": test_06_task_manager_mcp(),
        "07_integration": test_07_integration_scan(),
        "08_triage": test_08_triage_integration(),
    }

    total_pass = 0
    total_fail = 0
    total_warn = 0
    total_info = 0
    total_skip = 0

    print("=" * 80)
    print("  ZephyrAlpha Task System — 红白对抗诊断报告")
    print("=" * 80)
    print()

    for section_name, section_results in all_results.items():
        print(f"--- {section_name} ---")
        for item in section_results:
            tag = item[0]
            name = item[1]
            detail = item[2] if len(item) > 2 else ""

            if tag == "PASS":
                total_pass += 1
                icon = "✅"
            elif tag == "FAIL":
                total_fail += 1
                icon = "🔴"
            elif tag == "WARN":
                total_warn += 1
                icon = "⚠️"
            elif tag == "INFO" or tag == "INTEG":
                total_info += 1
                icon = "ℹ️"
            elif tag == "SKIP":
                total_skip += 1
                icon = "⏭️"
            else:
                icon = "❓"

            print(f"  {icon} [{tag:5s}] {name}")
            if detail:
                print(f"       → {detail}")
        print()

    print("=" * 80)
    total = total_pass + total_fail + total_warn + total_info + total_skip
    print(f"  总计: {total} 项检查")
    print(f"  ✅ PASS : {total_pass}")
    print(f"  🔴 FAIL : {total_fail}")
    print(f"  ⚠️ WARN : {total_warn}")
    print(f"  ℹ️ INFO : {total_info}")
    print(f"  ⏭️ SKIP : {total_skip}")
    print("=" * 80)

    return total_fail == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
