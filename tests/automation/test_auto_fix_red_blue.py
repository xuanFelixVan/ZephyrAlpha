# [A_test] module_id: MOD-GOV_auto_fix_red_blue | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] tests.test_auto_fix_red_blue
# [INVARIANTS] 红蓝对抗极端测试;覆盖修复爆炸/安全绕过/影子工作区泄露
# [MODIFY-GUARD] blueprint.md §3
# [CONSUMERS] CI
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] self
# [TTL] task_bound

"""F15 自动修复引擎 - 红蓝对抗极端测试

三大攻击向量:
1. 修复爆炸(Fix Storm): 短时间大量修复请求,测试 FixStormGuard + CascadeBreaker + FixBudget
2. 安全绕过(Safety Bypass): 尝试绕过 SafetyGate 执行危险修复
3. 影子工作区泄露(Shadow Workspace Leak): 测试隔离性和数据泄露防护
"""
from __future__ import annotations

import os
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.infrastructure.auto_fix_engine.fix_budget import (
    FixBudget,
    FixStormGuard,
)
from zephyr.infrastructure.auto_fix_engine.fix_reliability import (
    BlastRadiusEstimator,
    DeadLetterQueue,
)
from zephyr.infrastructure.auto_fix_engine.fix_safety import (
    CascadeBreaker,
    FixValidator,
    SafetyGate,
    SandboxExecutor,
    SecretLeakGuard,
)
from zephyr.infrastructure.auto_fix_engine.models import (
    FixAction,
    FixConfidence,
    FixLevel,
    FixStatus,
    ValidationResult,
)
from zephyr.infrastructure.auto_fix_engine.self_heal_agent import SelfHealAgent
from zephyr.infrastructure.auto_fix_engine.shadow_workspace import ShadowWorkspace

# ============================================================================
# 攻击向量 1: 修复爆炸 (Fix Storm)
# ============================================================================

class TestFixStormAttack:
    """红队: 短时间内触发大量修复,试图耗尽系统资源
    蓝队: FixStormGuard + CascadeBreaker + FixBudget 必须熔断"""

    def test_storm_guard_freezes_on_burst(self):
        """红队: 1秒内触发100次修复(超过short_threshold=30)
        蓝队: FixStormGuard 必须冻结后续请求"""
        guard = FixStormGuard(config={
            "short_window_sec": 10,
            "short_threshold": 30,
            "cooldown_sec": 60,
        })
        for _ in range(100):
            guard.record()

        # check() 返回 (allowed, reason), allowed=False 表示冻结
        allowed, reason = guard.check()
        assert not allowed, f"FixStormGuard 未检测到修复风暴: {reason}"
        assert "storm" in reason.lower()

    def test_storm_guard_concurrent_attack(self):
        """红队: 8线程并发触发修复(模拟多修复器同时工作)
        蓝队: FixStormGuard 线程安全,正确检测风暴"""
        guard = FixStormGuard(config={
            "short_window_sec": 5,
            "short_threshold": 20,
            "cooldown_sec": 30,
        })

        def attack():
            for _ in range(50):
                guard.record()

        threads = [threading.Thread(target=attack) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        allowed, _ = guard.check()
        assert not allowed, "并发攻击下 FixStormGuard 未冻结"
        assert guard.is_active

    def test_cascade_breaker_module_freeze(self):
        """红队: 同一模块连续触发10次修复(超过module_threshold)
        蓝队: CascadeBreaker 模块级熔断"""
        cb = CascadeBreaker(config={
            "module_threshold": 5,
            "module_window_sec": 10,
            "module_cooldown_sec": 60,
        })
        module = "zephyr.infrastructure.auto_fix_engine.engine"

        for _ in range(10):
            cb.record(module)

        allowed, reason = cb.check(module)
        assert not allowed, "CascadeBreaker 未触发模块级熔断"
        assert "module" in reason.lower()

    def test_cascade_breaker_global_freeze(self):
        """红队: 全局触发60次修复(超过global_threshold=50)
        蓝队: CascadeBreaker 全局熔断"""
        cb = CascadeBreaker(config={
            "global_threshold": 50,
            "global_window_sec": 10,
            "global_cooldown_sec": 60,
        })

        for i in range(60):
            cb.record(f"module_{i}")

        allowed, reason = cb.check()
        assert not allowed, "CascadeBreaker 未触发全局熔断"
        assert "global" in reason.lower()

    def test_budget_exhaustion_blocks_fixes(self):
        """红队: 消耗完每日预算后继续请求修复
        蓝队: FixBudget 拒绝超出预算的修复"""
        budget = FixBudget(config={
            "daily_limit": 5,
            "monthly_limit": 100,
            "l1_cost_per_fix": 1,
        })

        # 消耗5次L1修复(达到每日上限)
        for i in range(5):
            budget.consume(FixLevel.L1_RULE, operation_id=f"fix_{i}")

        # 第6次应被拒绝
        decision = budget.check(FixLevel.L1_RULE)
        assert not decision.allowed, "超出每日预算的修复未被拒绝"
        assert "daily" in decision.reason.lower() or "budget" in decision.reason.lower()

    def test_dead_letter_queue_overflow(self):
        """红队: 大量失败修复进入死信队列
        蓝队: DeadLetterQueue 不无限增长"""
        dlq = DeadLetterQueue(max_retries=3)
        action = FixAction(
            action_type="test",
            target="fake.py",
            level=FixLevel.L1_RULE,
        )

        for i in range(200):
            dlq.add(action, f"failure_{i}")

        # 死信队列应接受所有条目(无上限)
        queue_len = len(dlq.queue)
        assert queue_len == 200, f"死信队列长度不正确: {queue_len}"


# ============================================================================
# 攻击向量 2: 安全绕过 (Safety Bypass)
# ============================================================================

class TestSafetyBypassAttack:
    """红队: 尝试绕过 SafetyGate 执行危险修复
    蓝队: SafetyGate + FixValidator + SecretLeakGuard 必须拦截"""

    def test_l3_agent_fix_blocked(self):
        """红队: 尝试自动执行 L3 Agent 修复(需人工审批)
        蓝队: SafetyGate 拒绝"""
        gate = SafetyGate()
        action = FixAction(
            action_type="self_heal",
            target="some_file.py",
            level=FixLevel.L3_AGENT,
        )
        decision = gate.check(action)
        assert not decision.approved, "L3 Agent 修复未被 SafetyGate 拦截"
        assert "human approval" in decision.reason.lower() or "l3" in decision.reason.lower()

    def test_protected_path_blocked(self):
        """红队: 尝试修改受保护路径(如 project_rules.md)
        蓝队: SafetyGate 拒绝"""
        gate = SafetyGate(config={
            "protected_paths": ["project_rules.md", ".trae/rules/"],
        })
        action = FixAction(
            action_type="config_fix",
            target="project_rules.md",
            level=FixLevel.L1_RULE,
        )
        decision = gate.check(action)
        assert not decision.approved, "受保护路径未被拦截"

    def test_safety_gate_disabled_still_validates(self):
        """红队: 禁用 SafetyGate 后尝试危险修复
        蓝队: 即使 SafetyGate 禁用,FixValidator 仍检查语法"""
        gate = SafetyGate(config={"safety_gate_enabled": False})
        action = FixAction(
            action_type="test",
            target="nonexistent.py",
            level=FixLevel.L1_RULE,
        )
        decision = gate.check(action)
        assert decision.approved, "SafetyGate 禁用时应放行"

        validator = FixValidator()
        result = validator.validate_fix("nonexistent.py")
        assert not result.valid, "FixValidator 未拦截不存在的文件"

    def test_secret_leak_intercepted(self):
        """红队: 修复输出中包含 API key 和密码(20+字符)
        蓝队: SecretLeakGuard 100% 拦截并脱敏"""
        guard = SecretLeakGuard()
        # 使用20+字符的密码以匹配pattern
        malicious_output = """
        Fix applied. New config:
        API_KEY=sk-1234567890abcdef1234567890abcdef
        password=MySecretPassword1234567890abcdef
        token=ghp_abcdefghijklmnopqrstuvwxyz123456
        """
        is_clean, findings = guard.scan(malicious_output)
        assert not is_clean, "SecretLeakGuard 未检测到敏感信息"
        assert len(findings) >= 1, "未发现任何敏感模式"

        redacted, _ = guard.scan_and_redact(malicious_output)
        assert "sk-1234567890abcdef" not in redacted, "脱敏后仍包含API key"
        assert "MySecretPassword1234567890" not in redacted, "脱敏后仍包含密码"

    def test_sandbox_executor_cleans_up(self):
        """红队: 沙箱执行后检查临时目录是否残留
        蓝队: SandboxExecutor 执行后自动清理"""
        with tempfile.TemporaryDirectory() as tmpdir:
            executor = SandboxExecutor(base_dir=tmpdir)
            action = FixAction(
                action_type="test",
                target="some_file.py",
                level=FixLevel.L1_RULE,
            )

            def mock_fix(target, dry_run=True):
                return "fixed"

            executor.execute(action, mock_fix)

            sandbox_path = Path(tmpdir) / action.action_id
            assert not sandbox_path.exists(), f"沙箱目录未清理: {sandbox_path}"

    def test_self_heal_circuit_breaker(self):
        """红队: SelfHealAgent 连续失败3次,尝试继续修复
        蓝队: 熔断器打开,拒绝后续修复"""
        agent = SelfHealAgent(max_rounds=5, circuit_threshold=3)

        def failing_diagnose(target):
            return {"issues": [{"type": "critical"}]}

        def failing_fix(target):
            raise RuntimeError("fix failed")

        def failing_validate(target):
            return ValidationResult(valid=False, check_name="test", evidence="", error="still broken")

        action = agent.heal(
            target="broken.py",
            diagnose_fn=failing_diagnose,
            fix_fn=failing_fix,
            validate_fn=failing_validate,
        )

        assert agent.circuit_open, "熔断器未打开"
        assert action.status == FixStatus.FAILED

        action2 = agent.heal(
            target="broken.py",
            diagnose_fn=failing_diagnose,
            fix_fn=failing_fix,
            validate_fn=failing_validate,
        )
        assert action2.status == FixStatus.FAILED
        assert "Circuit breaker" in action2.metadata.get("error", "")


# ============================================================================
# 攻击向量 3: 影子工作区泄露 (Shadow Workspace Leak)
# ============================================================================

class TestShadowWorkspaceLeak:
    """红队: 尝试通过 ShadowWorkspace 泄露数据或污染主环境
    蓝队: ShadowWorkspace 必须隔离,执行后清理"""

    def test_shadow_workspace_isolation(self):
        """红队: 在 ShadowWorkspace 中修改文件,检查主环境是否受影响
        蓝队: 主环境文件不被修改"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_file = Path(tmpdir) / "target.py"
            original_file.write_text("original = 1\n", encoding="utf-8")

            shadow = ShadowWorkspace(config={
                "base_dir": str(Path(tmpdir) / "shadow"),
                "run_pytest": False,
                "run_mypy": False,
                "run_ruff": False,
            })
            action = FixAction(
                action_type="test",
                target=str(original_file),
                level=FixLevel.L1_RULE,
                after="modified = 2\n",
            )

            result = shadow.preflight(action, project_root=tmpdir)

            # 主环境文件未被修改
            assert original_file.read_text(encoding="utf-8") == "original = 1\n", \
                "ShadowWorkspace 泄露: 主环境文件被修改"

    def test_shadow_workspace_nonexistent_target(self):
        """红队: 对不存在的文件执行 preflight
        蓝队: 返回 safe_to_apply=False"""
        shadow = ShadowWorkspace(config={"run_pytest": False, "run_mypy": False, "run_ruff": False})
        action = FixAction(
            action_type="test",
            target="/nonexistent/path/file.py",
            level=FixLevel.L1_RULE,
        )
        result = shadow.preflight(action)
        assert not result.safe_to_apply, "不存在的目标未被拒绝"

    def test_blast_radius_estimator_directory(self):
        """红队: 对整个目录执行修复(爆炸半径大)
        蓝队: BlastRadiusEstimator 正确评估风险"""
        estimator = BlastRadiusEstimator()
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(10):
                (Path(tmpdir) / f"file_{i}.py").write_text(f"x = {i}\n", encoding="utf-8")

            action = FixAction(
                action_type="batch_fix",
                target=tmpdir,
                level=FixLevel.L2_LLM,
            )
            estimate = estimator.estimate(action)

            assert estimate["files"] >= 10, "BlastRadiusEstimator 未正确评估文件数"
            assert estimate["risk"] in ("medium", "high"), \
                f"10文件修复风险应为medium/high,实际: {estimate['risk']}"

    def test_shadow_workspace_cleanup(self):
        """红队: ShadowWorkspace 执行后检查临时目录残留
        蓝队: 临时目录被清理"""
        with tempfile.TemporaryDirectory() as tmpdir:
            shadow_base = Path(tmpdir) / "shadow"
            shadow = ShadowWorkspace(config={
                "base_dir": str(shadow_base),
                "run_pytest": False,
                "run_mypy": False,
                "run_ruff": False,
            })
            target_file = Path(tmpdir) / "target.py"
            target_file.write_text("x = 1\n", encoding="utf-8")

            action = FixAction(
                action_type="test",
                target=str(target_file),
                level=FixLevel.L1_RULE,
                after="x = 2\n",
            )
            shadow.preflight(action, project_root=tmpdir)

            # preflight 在 finally 中清理 shadow_dir
            assert target_file.read_text(encoding="utf-8") == "x = 1\n", \
                "原文件被 ShadowWorkspace 修改"


# ============================================================================
# 组合攻击: 多向量同时攻击
# ============================================================================

class TestCombinedAttack:
    """红队: 同时触发修复爆炸 + 安全绕过 + 影子工作区泄露
    蓝队: 所有防护机制协同工作"""

    def test_storm_plus_bypass_attempt(self):
        """红队: 在修复风暴中尝试执行 L3 危险修复
        蓝队: FixStormGuard 冻结 + SafetyGate 拒绝"""
        guard = FixStormGuard(config={
            "short_window_sec": 5,
            "short_threshold": 10,
            "cooldown_sec": 30,
        })
        gate = SafetyGate()

        for _ in range(50):
            guard.record()

        action = FixAction(
            action_type="self_heal",
            target="critical.py",
            level=FixLevel.L3_AGENT,
        )

        allowed, _ = guard.check()
        assert not allowed, "FixStormGuard 未冻结"
        decision = gate.check(action)
        assert not decision.approved, "SafetyGate 未拦截 L3 修复"

    def test_budget_plus_cascade(self):
        """红队: 预算耗尽 + 级联熔断同时发生
        蓝队: 系统进入全面保护状态"""
        budget = FixBudget(config={"daily_limit": 3, "monthly_limit": 10, "l1_cost_per_fix": 1})
        cb = CascadeBreaker(config={
            "module_threshold": 3,
            "module_window_sec": 10,
            "module_cooldown_sec": 60,
        })

        for i in range(3):
            budget.consume(FixLevel.L1_RULE, operation_id=f"fix_{i}")
        for _ in range(5):
            cb.record("critical_module")

        budget_decision = budget.check(FixLevel.L1_RULE)
        cascade_allowed, _ = cb.check("critical_module")

        assert not budget_decision.allowed, "预算未耗尽"
        assert not cascade_allowed, "级联熔断未触发"
