#!/usr/bin/env python3
"""步骤5 验收：H1RedisWriter + H1RedisReader + H1CqrsProjectors 全链路联调。

测试流程：
1. Writer 批量写入因子截面 → Reader 读取验证
2. Writer 写入 tick → Reader 间接验证
3. PositionProjector 投影 OrderFilled → Reader.get_position 验证
4. SignalProjector 投影 SignalEvent → 验证 signal:active Set
5. RiskProjector 投影 RiskEvent → Reader.get_risk_status 验证
6. TradeProjector 投影 ExecutionEvent → 验证 trade:today List
7. 幂等去重验证（同一 idempotency_key 重复投影不生效）
"""

import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.infrastructure.database_service import DatabaseService
from zephyr.infrastructure.h1_redis_hot.h1_cqrs_projectors import (
    PositionProjector,
    RiskProjector,
    SignalProjector,
    TradeProjector,
)
from zephyr.infrastructure.h1_redis_hot.h1_redis_reader import H1RedisReader, H1RedisUnavailable
from zephyr.infrastructure.h1_redis_hot.h1_redis_schema import (
    feature_key,
    position_key,
    risk_status_key,
    signal_active_key,
    trade_today_key,
)
from zephyr.infrastructure.h1_redis_hot.h1_redis_writer import H1RedisWriter


@dataclass
class FakeEvent:
    """测试用事件（符合 EventLike Protocol）"""

    event_type: str
    payload: dict


def main():
    print("=== 步骤5 验收: Writer + Reader + Projectors 全链路联调 ===\n")

    ds = DatabaseService()
    r = ds.get_redis_conn()
    writer = H1RedisWriter(r)
    reader = H1RedisReader(r)
    test_keys = []

    # ---- 1. Writer 批量写入因子截面 → Reader 读取 ----
    print("[1] Writer 批量写入因子截面 → Reader 读取")
    cross_section = {
        "000001.SZ": {"momentum_20d": 0.0234, "close": 12.50, "volume_20d": 1500000.0},
        "600000.SH": {"momentum_20d": -0.0156, "close": 8.32, "volume_20d": 800000.0},
        "300750.SZ": {"momentum_20d": 0.0567, "close": 215.80, "volume_20d": 500000.0},
    }
    count = writer.write_factor_cross_section(cross_section)
    assert count == 3, f"应写入 3 个 symbol，实际 {count}"

    # Reader 读取验证
    features = reader.get_online_features("000001.SZ", ["momentum_20d", "close", "volume_20d"])
    assert features["momentum_20d"] == 0.0234
    assert features["close"] == 12.50
    assert features["volume_20d"] == 1500000.0
    print(f"    ✅ 写入 {count} symbols, 读取 000001.SZ: {features}")
    test_keys.extend([feature_key(s) for s in cross_section])

    # 读取不存在的因子
    features_missing = reader.get_online_features("000001.SZ", ["nonexistent_factor"])
    assert len(features_missing) == 0
    print(f"    ✅ 不存在的因子返回空: {features_missing}")

    # ---- 2. Writer 写入 tick ----
    print("\n[2] Writer 写入 tick_latest")
    writer.write_tick_latest("000001.SZ", {"price": 12.55, "volume": 120000, "bid1": 12.54, "ask1": 12.56})
    from zephyr.infrastructure.h1_redis_hot.h1_redis_schema import tick_latest_key

    tick = r.hgetall(tick_latest_key("000001.SZ"))
    assert "12.55" in tick.get("price", "")
    print(f"    ✅ tick 写入: {tick}")
    test_keys.append(tick_latest_key("000001.SZ"))

    # ---- 3. PositionProjector 投影 OrderFilled ----
    print("\n[3] PositionProjector 投影 OrderFilled → Reader.get_position")
    pos_projector = PositionProjector(r)

    # BUY 1000 股 @ 12.50
    pos_projector.handle(
        FakeEvent(
            "OrderFilled",
            {
                "symbol": "000001.SZ",
                "direction": "BUY",
                "quantity": 1000,
                "price": 12.50,
                "idempotency_key": "pos-buy-001",
            },
        )
    )
    pos = reader.get_position("000001.SZ")
    assert pos["amount"] == 1000
    assert float(pos["cost"]) == 12500.0  # 1000 * 12.50
    print(f"    ✅ BUY 1000@12.50 → position: {pos}")

    # 再 BUY 500 股 @ 13.00
    pos_projector.handle(
        FakeEvent(
            "OrderFilled",
            {
                "symbol": "000001.SZ",
                "direction": "BUY",
                "quantity": 500,
                "price": 13.00,
                "idempotency_key": "pos-buy-002",
            },
        )
    )
    pos = reader.get_position("000001.SZ")
    assert pos["amount"] == 1500  # 1000 + 500
    assert float(pos["cost"]) == 19000.0  # 12500 + 6500
    print(f"    ✅ BUY 500@13.00 → position: {pos}")

    # SELL 200 股
    pos_projector.handle(
        FakeEvent(
            "OrderFilled",
            {
                "symbol": "000001.SZ",
                "direction": "SELL",
                "quantity": 200,
                "price": 13.20,
                "idempotency_key": "pos-sell-001",
            },
        )
    )
    pos = reader.get_position("000001.SZ")
    assert pos["amount"] == 1300  # 1500 - 200
    print(f"    ✅ SELL 200@13.20 → position: {pos}")
    test_keys.append(position_key("000001.SZ"))

    # 幂等去重：重复 BUY 1000 不应生效
    pos_projector.handle(
        FakeEvent(
            "OrderFilled",
            {
                "symbol": "000001.SZ",
                "direction": "BUY",
                "quantity": 1000,
                "price": 12.50,
                "idempotency_key": "pos-buy-001",  # 相同 key
            },
        )
    )
    pos = reader.get_position("000001.SZ")
    assert pos["amount"] == 1300, f"幂等去重失败: amount={pos['amount']} (应为 1300)"
    print(f"    ✅ 幂等去重: 重复事件不生效, amount 仍为 {pos['amount']}")

    # ---- 4. SignalProjector 投影 SignalEvent ----
    print("\n[4] SignalProjector 投影 SignalEvent → signal:active Set")
    sig_projector = SignalProjector(r)
    sig_projector.handle(
        FakeEvent(
            "SignalEvent",
            {
                "symbol": "000001.SZ",
                "action": "OPEN",
                "signal_type": "momentum_breakout",
                "idempotency_key": "sig-001",
            },
        )
    )
    sig_projector.handle(
        FakeEvent(
            "SignalEvent",
            {
                "symbol": "600000.SH",
                "action": "OPEN",
                "signal_type": "volume_surge",
                "idempotency_key": "sig-002",
            },
        )
    )
    members = r.smembers(signal_active_key())
    assert "000001.SZ" in members
    assert "600000.SH" in members
    print(f"    ✅ OPEN 2 signals → signal:active = {members}")

    # CLOSE 一个信号
    sig_projector.handle(
        FakeEvent(
            "SignalEvent",
            {
                "symbol": "000001.SZ",
                "action": "CLOSE",
                "idempotency_key": "sig-003",
            },
        )
    )
    members = r.smembers(signal_active_key())
    assert "000001.SZ" not in members
    assert "600000.SH" in members
    print(f"    ✅ CLOSE 000001.SZ → signal:active = {members}")
    test_keys.append(signal_active_key())

    # ---- 5. RiskProjector 投影 RiskEvent ----
    print("\n[5] RiskProjector 投影 RiskEvent → Reader.get_risk_status")
    risk_projector = RiskProjector(r)
    risk_projector.handle(
        FakeEvent(
            "RiskEvent",
            {
                "level": "warning",
                "rule_id": "R-DRAWDOWN-001",
                "message": "回撤接近 5%",
                "idempotency_key": "risk-001",
            },
        )
    )
    risk = reader.get_risk_status()
    assert risk["level"] == "warning"
    assert risk["rule_id"] == "R-DRAWDOWN-001"
    print(f"    ✅ RiskEvent → risk:status = {risk}")
    test_keys.append(risk_status_key())

    # ---- 6. TradeProjector 投影 ExecutionEvent ----
    print("\n[6] TradeProjector 投影 ExecutionEvent → trade:today List")
    trade_projector = TradeProjector(r)
    trade_projector.handle(
        FakeEvent(
            "ExecutionEvent",
            {
                "symbol": "000001.SZ",
                "side": "BUY",
                "price": 12.50,
                "quantity": 1000,
                "order_id": "ORD-001",
                "idempotency_key": "trade-001",
            },
        )
    )
    trades = r.lrange(trade_today_key("000001.SZ"), 0, -1)
    assert len(trades) == 1
    trade_data = json.loads(trades[0])
    assert trade_data["side"] == "BUY"
    assert trade_data["price"] == 12.50
    print(f"    ✅ ExecutionEvent → trade:today = {trade_data}")
    test_keys.append(trade_today_key("000001.SZ"))

    # ---- 7. 读取延迟验证 ----
    print("\n[7] 读取延迟验证 (<5ms)")
    latencies = []
    for _ in range(20):
        start = time.perf_counter()
        reader.get_online_features("000001.SZ", ["momentum_20d", "close"])
        latencies.append((time.perf_counter() - start) * 1000)
    avg_ms = sum(latencies) / len(latencies)
    max_ms = max(latencies)
    print(f"    ✅ 20次读取: avg={avg_ms:.2f}ms, max={max_ms:.2f}ms")
    assert max_ms < 5.0, f"读取延迟 {max_ms:.2f}ms 超过 5ms 阈值"

    # ---- 清理 ----
    print("\n[8] 清理测试数据")
    for key in test_keys:
        r.delete(key)
    # 清理幂等去重集合
    for name in ("position", "signal", "risk", "trade"):
        r.delete(f"projector:idempotent:{name}")
    print(f"    ✅ 已清理 {len(test_keys)} 个 Key + 4 个幂等集合")

    ds.close_all()

    print("\n=== 步骤5 验收通过 ✅ ===")
    print("H1RedisWriter / H1RedisReader / H1CqrsProjectors 全链路联调通过")
    print("功能验证: 因子截面读写 / 持仓投影 / 信号投影 / 风控投影 / 交易投影 / 幂等去重 / 延迟<5ms")
    print("可进入步骤6（集成 D-FACTOR/SIGNAL/RISK + 登记depgraph依赖边）")


if __name__ == "__main__":
    main()
