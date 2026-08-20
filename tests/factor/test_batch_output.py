# [A_test] module_id: MOD-GOV_batch_output | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §test
# [MODULE] tests.factor.test_batch_output
# [DOMAIN] D_FACTOR
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/factor/test_batch_output.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""D_FACTOR core batch_output 测试——buffer.py。

覆盖：
- signal_to_tsv_row: 字段顺序 / NULL 转义 / is_valid 布尔
- signals_to_tsv: 批量转换 / 空列表
- FactorSignalBuffer.add: 达 batch_size 自动 flush / 未达返回 None
- FactorSignalBuffer.add_many: 批量追加 / 超量只 flush 一次
- FactorSignalBuffer.flush: 空缓冲返回 None / 强制刷新
- FactorSignalBuffer.maybe_flush_by_time: 时间触发
- 注入 writer 验证调用参数
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any

import pytest

buffer_mod = pytest.importorskip("zephyr.factor.core.batch_output.buffer")
factor_signal_mod = pytest.importorskip("zephyr.shared.contracts.factor_signal")

BatchOutputConfig = buffer_mod.BatchOutputConfig
FactorSignalBuffer = buffer_mod.FactorSignalBuffer
FlushOutcome = buffer_mod.FlushOutcome
signal_to_tsv_row = buffer_mod.signal_to_tsv_row
signals_to_tsv = buffer_mod.signals_to_tsv

FactorSignal = factor_signal_mod.FactorSignal


def _make_signal(
    symbol: str = "600519.SH",
    factor_id: str = "momentum_20d",
    raw_value: float = 0.05,
    normalized: float | None = 0.1,
    rank_pct: float | None = 0.7,
    is_valid: bool = True,
) -> FactorSignal:
    return FactorSignal(
        as_of_date=datetime(2026, 7, 27, 15, 0, 0),
        factor_id=factor_id,
        idempotency_key=f"test:{factor_id}:{symbol}:20260727",
        raw_value=raw_value,
        symbol=symbol,
        confidence=0.9,
        normalized_value=normalized,
        rank_pct=rank_pct,
        is_valid=is_valid,
        factor_version="1.0",
        schema_version="1.0",
    )


class TestSignalToTsvRow:
    def test_field_order(self) -> None:
        s = _make_signal()
        row = signal_to_tsv_row(s)
        fields = row.split("\t")
        # 11 列
        assert len(fields) == 11
        # 关键字段位置
        assert fields[1] == "momentum_20d"  # factor_id
        assert fields[4] == "600519.SH"  # symbol
        assert fields[5] == "0.9"  # confidence
        assert fields[9] == "1.0"  # factor_version

    def test_date_format(self) -> None:
        s = _make_signal()
        row = signal_to_tsv_row(s)
        fields = row.split("\t")
        assert fields[0] == "2026-07-27 15:00:00"

    def test_is_valid_true(self) -> None:
        s = _make_signal(is_valid=True)
        row = signal_to_tsv_row(s)
        assert row.split("\t")[8] == "1"

    def test_is_valid_false(self) -> None:
        s = _make_signal(is_valid=False)
        row = signal_to_tsv_row(s)
        assert row.split("\t")[8] == "0"

    def test_none_normalized_becomes_empty(self) -> None:
        """normalized_value=None 时字段为空（tsv_escape 转为 \\N）。"""
        s = _make_signal(normalized=None)
        row = signal_to_tsv_row(s)
        fields = row.split("\t")
        assert fields[6] == "\\N"  # tsv_escape("") 实际返回 ""，但 None 返回 \N


class TestSignalsToTsv:
    def test_empty_list(self) -> None:
        assert signals_to_tsv([]) == b""

    def test_single_signal(self) -> None:
        s = _make_signal()
        tsv = signals_to_tsv([s])
        assert isinstance(tsv, bytes)
        text = tsv.decode("utf-8")
        assert text.endswith("\n")
        assert len(text.strip().split("\n")) == 1

    def test_multiple_signals(self) -> None:
        signals = [_make_signal(symbol=f"00000{i}.SZ") for i in range(3)]
        tsv = signals_to_tsv(signals)
        text = tsv.decode("utf-8")
        lines = text.strip().split("\n")
        assert len(lines) == 3


class TestFactorSignalBufferAdd:
    def test_add_below_threshold_returns_none(self) -> None:
        buf = FactorSignalBuffer(
            BatchOutputConfig(batch_size=3),
            writer=lambda t, c, b: "ok",
        )
        result = buf.add(_make_signal())
        assert result is None
        assert len(buf) == 1

    def test_add_at_threshold_triggers_flush(self) -> None:
        calls: list[tuple[str, str, bytes]] = []

        def fake_writer(table: str, cols: str, tsv: bytes) -> str:
            calls.append((table, cols, tsv))
            return "ok"

        buf = FactorSignalBuffer(
            BatchOutputConfig(batch_size=2, target_table="test.table"),
            writer=fake_writer,
        )
        buf.add(_make_signal(symbol="A"))
        result = buf.add(_make_signal(symbol="B"))
        assert result is not None
        assert result.flushed == 2
        assert result.table == "test.table"
        assert len(calls) == 1
        # 缓冲区已清空
        assert len(buf) == 0

    def test_writer_called_with_correct_args(self) -> None:
        captured: dict[str, Any] = {}

        def fake_writer(table: str, cols: str, tsv: bytes) -> str:
            captured["table"] = table
            captured["cols"] = cols
            captured["tsv"] = tsv
            captured["tsv_text"] = tsv.decode("utf-8")
            return "ok"

        buf = FactorSignalBuffer(
            BatchOutputConfig(batch_size=1),
            table="my.table",
            writer=fake_writer,
        )
        buf.add(_make_signal())
        assert captured["table"] == "my.table"
        assert captured["cols"].startswith("(") and captured["cols"].endswith(")")
        assert "as_of_date" in captured["cols"]
        assert "factor_id" in captured["cols"]
        assert captured["tsv_text"].endswith("\n")


class TestFactorSignalBufferAddMany:
    def test_add_many_below_threshold(self) -> None:
        buf = FactorSignalBuffer(
            BatchOutputConfig(batch_size=10),
            writer=lambda t, c, b: "ok",
        )
        result = buf.add_many([_make_signal() for _ in range(3)])
        assert result is None
        assert len(buf) == 3

    def test_add_many_at_threshold(self) -> None:
        buf = FactorSignalBuffer(
            BatchOutputConfig(batch_size=3),
            writer=lambda t, c, b: "ok",
        )
        result = buf.add_many([_make_signal() for _ in range(3)])
        assert result is not None
        assert result.flushed == 3
        assert len(buf) == 0

    def test_add_many_over_threshold_only_flushes_once(self) -> None:
        """超量（5 > batch_size=3）只 flush 一次，剩余 2 条留在缓冲区。"""
        call_count = [0]

        def fake_writer(t: str, c: str, b: bytes) -> str:
            call_count[0] += 1
            return "ok"

        buf = FactorSignalBuffer(
            BatchOutputConfig(batch_size=3),
            writer=fake_writer,
        )
        result = buf.add_many([_make_signal() for _ in range(5)])
        assert result is not None
        assert result.flushed == 5  # 全部刷新（_flush_locked 一次性刷完）
        assert call_count[0] == 1
        assert len(buf) == 0

    def test_add_many_empty_returns_none(self) -> None:
        buf = FactorSignalBuffer(
            BatchOutputConfig(batch_size=1),
            writer=lambda t, c, b: "ok",
        )
        assert buf.add_many([]) is None


class TestFactorSignalBufferFlush:
    def test_flush_empty_returns_none(self) -> None:
        buf = FactorSignalBuffer(
            BatchOutputConfig(),
            writer=lambda t, c, b: "ok",
        )
        assert buf.flush() is None

    def test_flush_forces_write(self) -> None:
        calls: list[bytes] = []

        def fake_writer(t: str, c: str, b: bytes) -> str:
            calls.append(b)
            return "ok"

        buf = FactorSignalBuffer(
            BatchOutputConfig(batch_size=100),  # 高阈值，add 不触发
            writer=fake_writer,
        )
        buf.add(_make_signal(symbol="A"))
        buf.add(_make_signal(symbol="B"))
        result = buf.flush()
        assert result is not None
        assert result.flushed == 2
        assert len(calls) == 1
        assert len(buf) == 0

    def test_flush_twice_second_empty(self) -> None:
        buf = FactorSignalBuffer(
            BatchOutputConfig(),
            writer=lambda t, c, b: "ok",
        )
        buf.add(_make_signal())
        buf.flush()
        assert buf.flush() is None  # 已清空


class TestMaybeFlushByTime:
    def test_no_flush_before_interval(self) -> None:
        buf = FactorSignalBuffer(
            BatchOutputConfig(flush_interval_s=10.0),
            writer=lambda t, c, b: "ok",
        )
        buf.add(_make_signal())
        assert buf.maybe_flush_by_time() is None
        assert len(buf) == 1

    def test_flush_after_interval(self) -> None:
        buf = FactorSignalBuffer(
            BatchOutputConfig(flush_interval_s=0.05),  # 50ms
            writer=lambda t, c, b: "ok",
        )
        buf.add(_make_signal())
        time.sleep(0.1)  # 超过 50ms
        result = buf.maybe_flush_by_time()
        assert result is not None
        assert result.flushed == 1
        assert len(buf) == 0

    def test_empty_buffer_no_flush_even_after_interval(self) -> None:
        buf = FactorSignalBuffer(
            BatchOutputConfig(flush_interval_s=0.01),
            writer=lambda t, c, b: "ok",
        )
        time.sleep(0.05)
        assert buf.maybe_flush_by_time() is None


class TestWriterErrorHandling:
    def test_writer_exception_logged_not_raised(self) -> None:
        """writer 抛异常时，flush 仍返回 FlushOutcome（outcome=None），不向上抛。"""

        def bad_writer(t: str, c: str, b: bytes) -> str:
            raise RuntimeError("CH 不可达")

        buf = FactorSignalBuffer(
            BatchOutputConfig(batch_size=1),
            writer=bad_writer,
        )
        result = buf.add(_make_signal())
        assert result is not None
        assert result.flushed == 1
        assert result.outcome is None  # 异常被捕获
        assert len(buf) == 0  # 缓冲已清空（不重试）
