# [A_test] module_id: MOD-GOV_backpressure | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §test
# [MODULE] tests.factor.test_backpressure
# [DOMAIN] D_FACTOR
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/factor/test_backpressure.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""D_FACTOR core backpressure 测试——limiter.py。

覆盖：
- BackpressureConfig 默认值
- acquire / release 基本计数
- 水位触发 THROTTLED ↔ NORMAL
- pause / resume 状态转换
- 超时返回 False
- stats 快照
"""

from __future__ import annotations

import threading
import time

import pytest

limiter_mod = pytest.importorskip("zephyr.factor.core.backpressure.limiter")

BackpressureConfig = limiter_mod.BackpressureConfig
BackpressureLimiter = limiter_mod.BackpressureLimiter
BackpressureState = limiter_mod.BackpressureState


class TestBackpressureConfig:
    def test_defaults(self) -> None:
        cfg = BackpressureConfig()
        assert cfg.max_inflight == 8
        assert cfg.acquire_timeout_s == 30.0
        assert cfg.high_watermark == 0.8
        assert cfg.low_watermark == 0.5

    def test_custom(self) -> None:
        cfg = BackpressureConfig(max_inflight=4, acquire_timeout_s=1.0)
        assert cfg.max_inflight == 4
        assert cfg.acquire_timeout_s == 1.0


class TestAcquireRelease:
    def test_acquire_returns_true(self) -> None:
        limiter = BackpressureLimiter()
        assert limiter.acquire() is True
        limiter.release()

    def test_acquire_increments_inflight(self) -> None:
        limiter = BackpressureLimiter(BackpressureConfig(max_inflight=4))
        limiter.acquire()
        assert limiter.stats().inflight == 1
        limiter.acquire()
        assert limiter.stats().inflight == 2
        limiter.release()
        assert limiter.stats().inflight == 1
        limiter.release()
        assert limiter.stats().inflight == 0

    def test_total_acquired_counter(self) -> None:
        limiter = BackpressureLimiter()
        for _ in range(3):
            limiter.acquire()
            limiter.release()
        assert limiter.stats().total_acquired == 3

    def test_release_below_zero_defensive(self) -> None:
        """无 acquire 直接 release 不应使 inflight 为负。"""
        limiter = BackpressureLimiter()
        limiter.release()  # 防御性，不抛
        assert limiter.stats().inflight == 0


class TestStateTransitions:
    def test_initial_state_normal(self) -> None:
        limiter = BackpressureLimiter()
        assert limiter.stats().state == BackpressureState.NORMAL

    def test_high_watermark_triggers_throttled(self) -> None:
        """max_inflight=4, high_watermark=0.8 → inflight=4 (ratio=1.0) → THROTTLED。"""
        limiter = BackpressureLimiter(BackpressureConfig(max_inflight=4, high_watermark=0.8, low_watermark=0.5))
        # acquire 到高水位（4 * 0.8 = 3.2，所以 inflight=4 时 ratio=1.0）
        for _ in range(4):
            limiter.acquire()
        assert limiter.stats().state == BackpressureState.THROTTLED
        for _ in range(4):
            limiter.release()

    def test_low_watermark_returns_normal(self) -> None:
        """max_inflight=4, low=0.5 → inflight=2 (ratio=0.5) → NORMAL。"""
        limiter = BackpressureLimiter(BackpressureConfig(max_inflight=4, high_watermark=0.8, low_watermark=0.5))
        # 先到 THROTTLED
        for _ in range(4):
            limiter.acquire()
        assert limiter.stats().state == BackpressureState.THROTTLED
        # 释放到低水位
        limiter.release()
        limiter.release()
        assert limiter.stats().inflight == 2
        assert limiter.stats().state == BackpressureState.NORMAL
        for _ in range(2):
            limiter.release()

    def test_hysteresis_middle_zone(self) -> None:
        """中间区间（low < ratio < high）保持当前状态（滞后区间）。"""
        limiter = BackpressureLimiter(BackpressureConfig(max_inflight=10, high_watermark=0.8, low_watermark=0.5))
        # 先到 THROTTLED（acquire 8 个）
        for _ in range(8):
            limiter.acquire()
        assert limiter.stats().state == BackpressureState.THROTTLED
        # 释放 1 个 → inflight=7, ratio=0.7（中间区间）
        limiter.release()
        assert limiter.stats().inflight == 7
        assert limiter.stats().state == BackpressureState.THROTTLED  # 保持
        for _ in range(7):
            limiter.release()


class TestPauseResume:
    def test_pause_rejects_acquire(self) -> None:
        limiter = BackpressureLimiter()
        limiter.pause()
        assert limiter.stats().state == BackpressureState.PAUSED
        assert limiter.acquire() is False
        assert limiter.stats().total_rejected == 1

    def test_resume_allows_acquire(self) -> None:
        limiter = BackpressureLimiter()
        limiter.pause()
        assert limiter.acquire() is False
        limiter.resume()
        assert limiter.stats().state == BackpressureState.NORMAL
        assert limiter.acquire() is True
        limiter.release()

    def test_pause_does_not_block_inflight_release(self) -> None:
        """PAUSED 状态下 release 仍生效（允许在途任务完成）。"""
        limiter = BackpressureLimiter()
        limiter.acquire()
        limiter.pause()
        limiter.release()  # 不抛
        assert limiter.stats().inflight == 0


class TestTimeout:
    def test_acquire_timeout_returns_false(self) -> None:
        """max_inflight=1, acquire_timeout_s=0.1 → 第 2 个 acquire 超时返回 False。"""
        limiter = BackpressureLimiter(BackpressureConfig(max_inflight=1, acquire_timeout_s=0.1))
        assert limiter.acquire() is True
        start = time.monotonic()
        result = limiter.acquire()
        elapsed = time.monotonic() - start
        assert result is False
        assert elapsed >= 0.1
        assert limiter.stats().total_rejected == 1
        limiter.release()

    def test_concurrent_acquire_blocks_then_succeeds(self) -> None:
        """一个线程持有，另一线程等待 release 后成功获取。"""
        limiter = BackpressureLimiter(BackpressureConfig(max_inflight=1, acquire_timeout_s=2.0))
        assert limiter.acquire() is True

        results: list[bool] = []

        def worker() -> None:
            results.append(limiter.acquire())

        t = threading.Thread(target=worker)
        t.start()
        time.sleep(0.1)  # 让 worker 进入等待
        assert limiter.stats().inflight == 1
        limiter.release()  # 释放后 worker 应能获取
        t.join(timeout=2.0)
        assert results == [True]
        limiter.release()  # 释放 worker 持有的


class TestStats:
    def test_stats_snapshot(self) -> None:
        limiter = BackpressureLimiter(BackpressureConfig(max_inflight=4))
        limiter.acquire()
        s = limiter.stats()
        assert s.state == BackpressureState.NORMAL
        assert s.inflight == 1
        assert s.max_inflight == 4
        assert s.total_acquired == 1
        assert s.total_rejected == 0
        limiter.release()
