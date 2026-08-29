# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [TTL] permanent
# [TESTS] zephyr.shared.observability.stage_timer
# [DOMAIN] D_SHARED
# [A_module] module_id=MOD-TEST_STAGE_TIMER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""stage_timer 单元测试（CAND-OBS-001 打点契约 MVP）。

覆盖契约语义四件：契约命名规约 / begin-end 计时 / fail-closed（非法名/未begin即end）/
上下文管理器等价性。计时源 time.perf_counter——测试只做相对量级断言（>0），
不绑定绝对时长（防 CI 抖动误红）。
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "src"))

import pytest

from zephyr.shared.observability.metrics import MetricsRegistry
from zephyr.shared.observability.stage_timer import StageTimer


@pytest.fixture()
def reg():
    return MetricsRegistry()


@pytest.fixture()
def timer(reg):
    return StageTimer(module="tick_subscriber", registry=reg)


class TestNamingContract:
    def test_metric_name_follows_contract(self, timer, reg):
        timer.begin("ws_recv")
        timer.end("ws_recv")
        names = [s.name for s in reg.snapshot()]
        assert "tick_subscriber_ws_recv_duration_seconds_count" in names
        assert "tick_subscriber_ws_recv_duration_seconds_sum" in names

    def test_module_name_must_be_snake_case(self, reg):
        with pytest.raises(ValueError, match="module 名非法"):
            StageTimer(module="TickSubscriber", registry=reg)  # 大写非法
        with pytest.raises(ValueError, match="module 名非法"):
            StageTimer(module="", registry=reg)

    def test_stage_name_must_be_snake_case(self, timer):
        with pytest.raises(ValueError, match="stage 名非法"):
            timer.begin("WS-Recv")  # 大写+连字符非法
        with pytest.raises(ValueError, match="stage 名非法"):
            timer.begin("1st_stage")  # 数字开头非法


class TestTimingSemantics:
    def test_begin_end_records_positive_elapsed(self, timer):
        timer.begin("parse")
        elapsed = timer.end("parse")
        assert elapsed >= 0.0

    def test_repeated_begin_resets(self, timer):
        timer.begin("emit")
        timer.begin("emit")  # 重置语义
        elapsed = timer.end("emit")
        assert elapsed >= 0.0
        assert timer.open_stages == ()

    def test_end_without_begin_fails_closed(self, timer):
        with pytest.raises(ValueError, match="未 begin 即 end"):
            timer.end("never_began")

    def test_open_stages_reflects_pending(self, timer):
        timer.begin("a")
        timer.begin("b")
        assert set(timer.open_stages) == {"a", "b"}
        timer.end("a")
        assert timer.open_stages == ("b",)


class TestContextManager:
    def test_measure_context_equivalent(self, timer, reg):
        with timer.measure("convert") as ctx:
            pass
        assert ctx.elapsed >= 0.0
        names = [s.name for s in reg.snapshot()]
        assert "tick_subscriber_convert_duration_seconds_count" in names

    def test_context_propagates_exception_and_closes_stage(self, timer):
        with pytest.raises(RuntimeError):
            with timer.measure("wal_add"):
                raise RuntimeError("boom")
        assert timer.open_stages == ()  # 异常后阶段已关闭（不留 open 泄漏）


class TestMultiStageSequence:
    def test_four_stage_tick_pipeline(self, timer, reg):
        """对齐契约 §3.2 L00 四段：on_tick/queue_wait/convert/wal_add。"""
        for stage in ("on_tick", "queue_wait", "convert", "wal_add"):
            timer.begin(stage)
            timer.end(stage)
        names = {s.name for s in reg.snapshot()}
        for stage in ("on_tick", "queue_wait", "convert", "wal_add"):
            assert f"tick_subscriber_{stage}_duration_seconds_count" in names
