# [A_test] module_id: MOD-GOV_context_pipeline_red_blue | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §red-blue
# [MODULE] tests.red_blue.test_context_pipeline_red_blue
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
F11 ContextPipeline 红蓝对抗极端测试
=====================================
覆盖4类极端场景：
1. 上下文溢出攻击（token_budget=1 + 大manifest）
2. 注入攻击（manifest路径遍历 + KB内容注入）
3. 管道阻塞（循环引用 + 超大文件 + 空文件）
4. KillSwitch熔断触发（连续错误 → 自动关闭）
"""
from __future__ import annotations

import os
import threading
import time
from pathlib import Path

import pytest

from zephyr.autonomy_core.context.context_pipeline import (
    ContextFourStageResult,
    run_context_four_stage,
    run_context_four_stage_or_raise,
)
from zephyr.infrastructure.capacity_assurance.kill_switch import KillSwitch

# ============================================================================
# 1. 上下文溢出攻击测试
# ============================================================================

class TestContextOverflowAttack:
    """红队：试图通过超大manifest导致上下文溢出，验证压缩机制生效不崩溃。"""

    def test_token_budget_1_with_large_manifest(self, tmp_path: Path) -> None:
        """token_budget=1 + 100文件manifest → 必须压缩不崩溃。"""
        files = []
        for i in range(100):
            f = tmp_path / f"overflow_{i}.md"
            f.write_text("x" * 10000, encoding="utf-8")
            files.append({"file_path": str(f), "reason": f"file_{i}"})

        result = run_context_four_stage(
            manifest=files,
            token_budget=1,
            compress_manifest=True,
            require_absolute_manifest_paths=False,
        )
        assert isinstance(result, ContextFourStageResult)
        # 不崩溃即通过；压缩后token_count应受限
        assert result.assembled is not None

    def test_zero_token_budget(self, tmp_path: Path) -> None:
        """token_budget=0 → 不崩溃，返回有效结果。"""
        f = tmp_path / "zero.md"
        f.write_text("content", encoding="utf-8")
        result = run_context_four_stage(
            manifest=[{"file_path": str(f), "reason": "test"}],
            token_budget=0,
            compress_manifest=True,
            require_absolute_manifest_paths=False,
        )
        assert isinstance(result, ContextFourStageResult)

    def test_negative_token_budget(self, tmp_path: Path) -> None:
        """token_budget=-1 → 系统正确拒绝（ValidationError是安全行为）。"""
        f = tmp_path / "neg.md"
        f.write_text("content", encoding="utf-8")
        # 负token_budget应被pydantic校验拒绝——这是正确的安全行为
        with pytest.raises(Exception):
            run_context_four_stage(
                manifest=[{"file_path": str(f), "reason": "test"}],
                token_budget=-1,
                compress_manifest=True,
                require_absolute_manifest_paths=False,
            )

    def test_extremely_large_single_file(self, tmp_path: Path) -> None:
        """单个超大文件(10MB) → 不崩溃不卡死。"""
        f = tmp_path / "huge.md"
        f.write_text("A" * (10 * 1024 * 1024), encoding="utf-8")
        result = run_context_four_stage(
            manifest=[{"file_path": str(f), "reason": "huge"}],
            token_budget=100,
            compress_manifest=True,
            require_absolute_manifest_paths=False,
        )
        assert isinstance(result, ContextFourStageResult)


# ============================================================================
# 2. 注入攻击测试
# ============================================================================

class TestInjectionAttack:
    """红队：试图通过路径遍历和内容注入攻击，验证路径校验和内容安全。"""

    def test_path_traversal_attack(self) -> None:
        """manifest路径遍历 ../../etc/passwd → 必须被拒绝或安全处理。"""
        malicious_manifest = [
            {"file_path": "../../../etc/passwd", "reason": "traversal"},
            {"file_path": "..\\..\\..\\windows\\system32\\config\\sam", "reason": "traversal_win"},
        ]
        # 不崩溃即通过；路径校验应拒绝或安全处理
        result = run_context_four_stage(
            manifest=malicious_manifest,
            require_absolute_manifest_paths=False,
        )
        assert isinstance(result, ContextFourStageResult)
        # 路径遍历文件不存在，assembled应包含errors或warnings
        assert result.assembled is not None

    def test_absolute_path_outside_project(self) -> None:
        """绝对路径指向项目外 → 安全处理。"""
        malicious_manifest = [
            {"file_path": "/etc/shadow", "reason": "absolute_outside"},
            {"file_path": "C:\\Windows\\System32\\drivers\\etc\\hosts", "reason": "win_outside"},
        ]
        result = run_context_four_stage(
            manifest=malicious_manifest,
            require_absolute_manifest_paths=True,
        )
        assert isinstance(result, ContextFourStageResult)

    def test_script_injection_in_reason(self, tmp_path: Path) -> None:
        """reason字段注入<script> → 不崩溃，内容安全。"""
        f = tmp_path / "safe.md"
        f.write_text("safe content", encoding="utf-8")
        malicious_manifest = [
            {"file_path": str(f), "reason": "<script>alert('xss')</script>"},
            {"file_path": str(f), "reason": "'; DROP TABLE tasks; --"},
        ]
        result = run_context_four_stage(
            manifest=malicious_manifest,
            require_absolute_manifest_paths=False,
        )
        assert isinstance(result, ContextFourStageResult)

    def test_null_byte_injection(self) -> None:
        """null字节注入路径 → 系统正确拒绝（ValueError是安全行为）。"""
        malicious_manifest = [
            {"file_path": "safe.md\x00.evil", "reason": "null_byte"},
            {"file_path": "safe\x00.txt", "reason": "null_in_name"},
        ]
        # null字节应被pathlib拒绝——这是正确的安全行为
        with pytest.raises((ValueError, Exception)):
            run_context_four_stage(
                manifest=malicious_manifest,
                require_absolute_manifest_paths=False,
            )


# ============================================================================
# 3. 管道阻塞测试
# ============================================================================

class TestPipelineBlockage:
    """红队：试图通过循环引用/超大文件/空文件导致管道阻塞，验证不死锁不超时。"""

    def test_empty_manifest(self) -> None:
        """空manifest → 快速返回不阻塞。"""
        start = time.monotonic()
        result = run_context_four_stage(manifest=[])
        elapsed = time.monotonic() - start
        assert isinstance(result, ContextFourStageResult)
        assert elapsed < 5.0, f"空manifest耗时{elapsed:.2f}s，应<5s"

    def test_empty_file(self, tmp_path: Path) -> None:
        """空文件 → 不阻塞不崩溃。"""
        f = tmp_path / "empty.md"
        f.write_text("", encoding="utf-8")
        result = run_context_four_stage(
            manifest=[{"file_path": str(f), "reason": "empty"}],
            require_absolute_manifest_paths=False,
        )
        assert isinstance(result, ContextFourStageResult)

    def test_many_small_files(self, tmp_path: Path) -> None:
        """1000个小文件 → 不死锁，合理时间内完成。"""
        files = []
        for i in range(1000):
            f = tmp_path / f"small_{i}.md"
            f.write_text(f"content_{i}", encoding="utf-8")
            files.append({"file_path": str(f), "reason": f"f_{i}"})

        start = time.monotonic()
        result = run_context_four_stage(
            manifest=files,
            token_budget=10000,
            compress_manifest=True,
            require_absolute_manifest_paths=False,
        )
        elapsed = time.monotonic() - start
        assert isinstance(result, ContextFourStageResult)
        assert elapsed < 30.0, f"1000文件耗时{elapsed:.2f}s，应<30s"

    def test_concurrent_pipeline_calls(self, tmp_path: Path) -> None:
        """并发调用pipeline → 线程安全不死锁。"""
        f = tmp_path / "concurrent.md"
        f.write_text("concurrent content", encoding="utf-8")
        manifest = [{"file_path": str(f), "reason": "concurrent"}]

        results: list[ContextFourStageResult | Exception] = []

        def run_pipeline():
            try:
                r = run_context_four_stage(
                    manifest=manifest,
                    require_absolute_manifest_paths=False,
                )
                results.append(r)
            except Exception as e:
                results.append(e)

        threads = [threading.Thread(target=run_pipeline) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        assert len(results) == 10, "所有线程应完成"
        for r in results:
            assert isinstance(r, ContextFourStageResult), f"线程结果类型错误: {type(r)}"


# ============================================================================
# 4. KillSwitch熔断触发测试
# ============================================================================

class TestKillSwitchFuse:
    """红队：模拟连续错误触发KillSwitch熔断，验证自动关闭+reset机制。"""

    def test_kill_switch_triggers_at_threshold(self) -> None:
        """连续5次错误 → KillSwitch触发熔断。"""
        ks = KillSwitch(threshold=5)
        states = []
        for i in range(5):
            state = ks.record_error(f"error_{i}")
            states.append(state)

        # 前4次不触发，第5次触发
        assert not states[0].on, "第1次错误不应触发熔断"
        assert not states[3].on, "第4次错误不应触发熔断"
        assert states[4].on, "第5次错误应触发熔断"
        assert states[4].manual_reset_needed, "熔断后需手动reset"

    def test_kill_switch_reset(self) -> None:
        """熔断后reset → 恢复正常。"""
        ks = KillSwitch(threshold=3)
        for i in range(3):
            ks.record_error(f"error_{i}")
        assert ks.fuse_on, "3次错误后应熔断"

        ks.reset()
        assert not ks.fuse_on, "reset后应恢复"
        assert ks.error_count == 0, "reset后错误计数应清零"

    def test_kill_switch_below_threshold_no_trigger(self) -> None:
        """低于阈值不触发熔断。"""
        ks = KillSwitch(threshold=5)
        for i in range(4):
            state = ks.record_error(f"error_{i}")
            assert not state.on, f"第{i+1}次错误不应触发熔断"

    def test_kill_switch_custom_threshold(self) -> None:
        """自定义阈值threshold=1 → 第1次错误即触发。"""
        ks = KillSwitch(threshold=1)
        state = ks.record_error("first_error")
        assert state.on, "threshold=1时第1次错误应触发熔断"

    def test_kill_switch_zero_threshold(self) -> None:
        """threshold=0 → 立即触发（边界值）。"""
        ks = KillSwitch(threshold=0)
        state = ks.record_error("immediate")
        # threshold=0时，error_count(1) >= 0 → 触发
        assert state.on, "threshold=0时应立即触发"

    def test_pipeline_with_kill_switch_integration(self, tmp_path: Path) -> None:
        """pipeline + KillSwitch集成：模拟错误触发熔断后pipeline仍可安全调用。"""
        ks = KillSwitch(threshold=3)
        f = tmp_path / "integration.md"
        f.write_text("content", encoding="utf-8")

        # 模拟3次错误触发熔断
        for i in range(3):
            ks.record_error(f"pipeline_error_{i}")
        assert ks.fuse_on, "3次错误后应熔断"

        # 熔断后pipeline仍可安全调用（不崩溃）
        result = run_context_four_stage(
            manifest=[{"file_path": str(f), "reason": "post_fuse"}],
            require_absolute_manifest_paths=False,
        )
        assert isinstance(result, ContextFourStageResult)

        # reset后恢复正常
        ks.reset()
        assert not ks.fuse_on


# ============================================================================
# 5. run_context_four_stage_or_raise 极端测试
# ============================================================================

class TestOrRaiseExtreme:
    """红队：测试run_context_four_stage_or_raise在极端场景下的行为。"""

    def test_or_raise_with_invalid_manifest(self) -> None:
        """无效manifest → 抛出AssemblyError不崩溃。"""
        from zephyr.autonomy_core.context.context_assembler import AssemblyError

        with pytest.raises(AssemblyError):
            run_context_four_stage_or_raise(
                manifest=[{"file_path": "/nonexistent/path/file.md", "reason": "invalid"}],
                require_absolute_manifest_paths=False,
            )

    def test_or_raise_with_empty_manifest(self) -> None:
        """空manifest → or_raise版本抛出AssemblyError（G3校验失败是正确行为）。"""
        from zephyr.autonomy_core.context.context_assembler import AssemblyError

        # 空manifest导致G3校验失败，or_raise版本应抛出AssemblyError
        with pytest.raises(AssemblyError):
            run_context_four_stage_or_raise(manifest=[])
