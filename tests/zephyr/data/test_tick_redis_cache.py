# [BLUEPRINT] MOD-H1_REDIS_HOT | tests/zephyr/data/test_tick_redis_cache.py
# [MODULE] tests.zephyr.data.test_tick_redis_cache
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.data.tick_redis_cache; zephyr.infrastructure.h1_redis_hot.h1_redis_schema
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-H1_REDIS_HOT | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""TickRedisCache 单元测试——tick→Redis tick:{symbol}:latest 双写器。

覆盖：
    1. tick_to_cache_dict 转换（QMT tick → Redis Hash fields）
    2. write_batch PIPELINE 批量写入
    3. best-effort 降级（Redis 故障不 raise）
    4. 空批次/空 tick 跳过
    5. tick_subscriber 集成（_drain_batch 调用 write_batch）
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from zephyr.data.tick_redis_cache import TickRedisCache, tick_to_cache_dict
from zephyr.infrastructure.h1_redis_hot.h1_redis_schema import tick_latest_key

# ── 测试数据工厂 ──


def _make_qmt_tick(
    time_ms: int = 1754106780000,
    last_price: float = 12.50,
    volume: int = 100000,
    amount: float = 1250000.0,
    bid_prices: list | None = None,
    ask_prices: list | None = None,
    bid_vols: list | None = None,
    ask_vols: list | None = None,
) -> dict:
    """构造 QMT xtdata tick dict。"""
    return {
        "time": time_ms,
        "lastPrice": last_price,
        "volume": volume,
        "amount": amount,
        "bidPrice": bid_prices or [12.49, 12.48, 12.47, 12.46, 12.45],
        "askPrice": ask_prices or [12.51, 12.52, 12.53, 12.54, 12.55],
        "bidVol": bid_vols or [500, 400, 300, 200, 100],
        "askVol": ask_vols or [600, 700, 800, 900, 1000],
    }


# ── tick_to_cache_dict 转换测试 ──


class TestTickToCacheDict:
    """QMT tick dict → Redis Hash fields 转换。"""

    def test_full_tick(self):
        """完整 tick（5档 bid/ask）→ 23 字段。"""
        tick = _make_qmt_tick()
        result = tick_to_cache_dict(tick)
        assert result is not None
        assert result["timestamp"] == 1754106780000
        assert result["price"] == pytest.approx(12.50)
        assert result["volume"] == 100000
        assert result["amount"] == pytest.approx(1250000.0)
        # 五档 bid/ask
        for i in range(1, 6):
            assert f"bid{i}" in result
            assert f"ask{i}" in result
            assert f"bid_vol{i}" in result
            assert f"ask_vol{i}" in result
        assert result["bid1"] == pytest.approx(12.49)
        assert result["ask5"] == pytest.approx(12.55)
        assert result["bid_vol1"] == 500
        assert result["ask_vol5"] == 1000

    def test_empty_tick(self):
        """空 tick → None。"""
        assert tick_to_cache_dict({}) is None
        assert tick_to_cache_dict(None) is None  # type: ignore

    def test_missing_time(self):
        """无 time 字段 → None。"""
        tick = {"lastPrice": 12.50, "volume": 100}
        assert tick_to_cache_dict(tick) is None

    def test_partial_levels(self):
        """仅 2 档 bid/ask → 只写 bid1-2/ask1-2。"""
        tick = _make_qmt_tick(
            bid_prices=[12.49, 12.48],
            ask_prices=[12.51, 12.52],
            bid_vols=[500, 400],
            ask_vols=[600, 700],
        )
        result = tick_to_cache_dict(tick)
        assert result is not None
        assert "bid1" in result and "bid2" in result
        assert "bid3" not in result
        assert "ask_vol1" in result and "ask_vol2" in result
        assert "ask_vol3" not in result

    def test_none_values(self):
        """None 值安全降级为 0。"""
        tick = {
            "time": 1754106780000,
            "lastPrice": None,
            "volume": None,
            "amount": None,
            "bidPrice": [None, 12.48],
            "askPrice": [],
            "bidVol": [],
            "askVol": [],
        }
        result = tick_to_cache_dict(tick)
        assert result is not None
        assert result["price"] == 0.0
        assert result["volume"] == 0
        assert result["bid1"] == 0.0
        assert result["bid2"] == pytest.approx(12.48)
        assert "ask1" not in result


# ── TickRedisCache.write_batch 测试 ──


class TestTickRedisCacheWriteBatch:
    """PIPELINE 批量写入测试。"""

    def test_batch_write_success(self):
        """正常批量写入 → PIPELINE execute 被调用。"""
        mock_conn = MagicMock()
        mock_pipe = MagicMock()
        mock_conn.pipeline.return_value = mock_pipe

        cache = TickRedisCache(mock_conn)
        ticks = [
            ("000001.SZ", _make_qmt_tick(last_price=12.50)),
            ("600000.SH", _make_qmt_tick(last_price=8.32)),
        ]
        result = cache.write_batch(ticks)

        assert result == 2
        mock_conn.pipeline.assert_called_once_with(transaction=False)
        assert mock_pipe.hset.call_count == 2
        mock_pipe.execute.assert_called_once()

    def test_empty_batch(self):
        """空批次 → 返回0，不调 PIPELINE。"""
        mock_conn = MagicMock()
        cache = TickRedisCache(mock_conn)
        assert cache.write_batch([]) == 0
        mock_conn.pipeline.assert_not_called()

    def test_all_empty_ticks(self):
        """全部空 tick → 返回0。"""
        mock_conn = MagicMock()
        mock_pipe = MagicMock()
        mock_conn.pipeline.return_value = mock_pipe
        cache = TickRedisCache(mock_conn)
        ticks = [("000001.SZ", {}), ("600000.SH", None)]  # type: ignore
        assert cache.write_batch(ticks) == 0
        mock_pipe.execute.assert_not_called()

    def test_redis_failure_best_effort(self):
        """Redis 故障 → 返回0，不 raise（best-effort）。"""
        mock_conn = MagicMock()
        mock_pipe = MagicMock()
        mock_pipe.execute.side_effect = ConnectionError("Redis down")
        mock_conn.pipeline.return_value = mock_pipe

        cache = TickRedisCache(mock_conn)
        ticks = [("000001.SZ", _make_qmt_tick())]
        result = cache.write_batch(ticks)

        assert result == 0  # 不 raise，返回0

    def test_key_format(self):
        """验证 Key 通过 tick_latest_key 构造（tick:{symbol}:latest）。"""
        mock_conn = MagicMock()
        mock_pipe = MagicMock()
        mock_conn.pipeline.return_value = mock_pipe

        cache = TickRedisCache(mock_conn)
        cache.write_batch([("000001.SZ", _make_qmt_tick())])

        call_args = mock_pipe.hset.call_args
        key = call_args[0][0] if call_args[0] else call_args[1]["name"]
        assert key == "tick:000001.SZ:latest"

    def test_values_are_str(self):
        """Redis Hash value 统一 str（repr 序列化）。"""
        mock_conn = MagicMock()
        mock_pipe = MagicMock()
        mock_conn.pipeline.return_value = mock_pipe

        cache = TickRedisCache(mock_conn)
        cache.write_batch([("000001.SZ", _make_qmt_tick(last_price=12.50))])

        mapping = mock_pipe.hset.call_args[1]["mapping"]
        assert mapping["price"] == "12.5"  # repr(12.5) = "12.5"
        assert mapping["timestamp"] == "1754106780000"


# ── tick_subscriber 集成测试 ──


class TestTickSubscriberIntegration:
    """tick_subscriber._drain_batch 集成 tick_cache 双写。"""

    def test_drain_batch_calls_cache(self):
        """_drain_batch 处理 tick 后调用 tick_cache.write_batch。"""
        from zephyr.data.tick_subscriber import TickSubscriber

        mock_cache = MagicMock()
        mock_writer = MagicMock()
        mock_writer.add.return_value = True

        sub = TickSubscriber(tick_cache=mock_cache)
        sub.running = True
        sub.writer = mock_writer

        # 喂入 2 条 tick
        sub.tick_queue.put(("000001.SZ", _make_qmt_tick()))
        sub.tick_queue.put(("600000.SH", _make_qmt_tick(last_price=8.32)))

        written = sub.drain_batch(max_n=10, timeout=0.5)

        assert written == 2
        mock_writer.add.assert_called_once()
        mock_cache.write_batch.assert_called_once()
        # 验证传给 write_batch 的 ticks 包含 2 条
        batch_arg = mock_cache.write_batch.call_args[0][0]
        assert len(batch_arg) == 2

    def test_drain_batch_without_cache(self):
        """无 tick_cache 时 → 正常运行，不报错。"""
        from zephyr.data.tick_subscriber import TickSubscriber

        mock_writer = MagicMock()
        mock_writer.add.return_value = True

        sub = TickSubscriber()  # 无 tick_cache
        sub.running = True
        sub.writer = mock_writer

        sub.tick_queue.put(("000001.SZ", _make_qmt_tick()))
        written = sub.drain_batch(max_n=10, timeout=0.5)

        assert written == 1
        mock_writer.add.assert_called_once()

    def test_cache_failure_does_not_block_wal(self):
        """tick_cache 故障 → 不阻断 WAL 主路径（best-effort）。"""
        from zephyr.data.tick_subscriber import TickSubscriber

        mock_cache = MagicMock()
        mock_cache.write_batch.side_effect = ConnectionError("Redis down")
        mock_writer = MagicMock()
        mock_writer.add.return_value = True

        sub = TickSubscriber(tick_cache=mock_cache)
        sub.running = True
        sub.writer = mock_writer

        sub.tick_queue.put(("000001.SZ", _make_qmt_tick()))
        written = sub.drain_batch(max_n=10, timeout=0.5)

        # WAL 正常返回，Redis 故障不影响
        assert written == 1
        mock_writer.add.assert_called_once()
        mock_cache.write_batch.assert_called_once()
