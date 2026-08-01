#!/usr/bin/env python3
"""h1_redis_schema.py Key DDL 联调验证（步骤4 验收）。

验证项：
1. 所有 Key 构造函数返回正确格式（feature/position/signal/trade/risk/account/tick）
2. Key 与真实 Redis 操作兼容（HSET/HGETALL/SADD/LPUSH/HGET 等）
3. TTL 常量 + 清理前缀常量正确
4. 容量估算常量一致
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.infrastructure.database_service import DatabaseService
from zephyr.infrastructure.h1_redis_hot import h1_redis_schema as schema


def main():
    print("=== 步骤4 验收: h1_redis_schema.py Key DDL 联调 ===\n")

    ds = DatabaseService()
    r = ds.get_redis_conn()

    errors = []
    test_keys = []  # 记录用于清理

    # ---- 1. 因子截面 Key (feature:{symbol}) ----
    print("[1] 因子截面 feature_key + factor_field")
    fk = schema.feature_key("000001.SZ")
    assert fk == "feature:000001.SZ", f"feature_key 格式错误: {fk}"
    ff = schema.factor_field("momentum_20d", "v1")
    assert ff == "momentum_20d:v1", f"factor_field 格式错误: {ff}"
    # 真实 Redis HSET
    r.hset(fk, mapping={ff: "0.0234", schema.factor_field("close", "v1"): "12.50"})
    vals = r.hgetall(fk)
    assert vals["momentum_20d:v1"] == "0.0234"
    assert vals["close:v1"] == "12.50"
    test_keys.append(fk)
    print(f"    ✅ feature_key('000001.SZ') = '{fk}'")
    print(f"    ✅ factor_field('momentum_20d','v1') = '{ff}'")
    print(f"    ✅ HSET/HGETALL: {vals}")

    # ---- 2. 持仓 Key (position:{symbol}) ----
    print("\n[2] 持仓 position_key")
    pk = schema.position_key("600000.SH")
    assert pk == "position:600000.SH", f"position_key 格式错误: {pk}"
    r.hset(pk, mapping={"amount": "1000", "cost": "12.50", "avg_price": "12.50", "updated_at": "2026-08-02T10:30:00"})
    assert r.hget(pk, "amount") == "1000"
    test_keys.append(pk)
    print(f"    ✅ position_key('600000.SH') = '{pk}'")

    # ---- 3. 活跃信号 Key (signal:active) ----
    print("\n[3] 活跃信号 signal_active_key")
    sk = schema.signal_active_key()
    assert sk == "signal:active", f"signal_active_key 格式错误: {sk}"
    r.sadd(sk, "000001.SZ", "600000.SH")
    assert r.sismember(sk, "000001.SZ")
    test_keys.append(sk)
    print(f"    ✅ signal_active_key() = '{sk}', SADD/SISMEMBER OK")

    # ---- 4. 当日交易 Key (trade:today:{symbol}) ----
    print("\n[4] 当日交易 trade_today_key")
    tk = schema.trade_today_key("000001.SZ")
    assert tk == "trade:today:000001.SZ", f"trade_today_key 格式错误: {tk}"
    r.lpush(tk, '{"side":"buy","price":12.50,"amount":1000}')
    assert r.llen(tk) == 1
    test_keys.append(tk)
    print(f"    ✅ trade_today_key('000001.SZ') = '{tk}', LPUSH/LLEN OK")

    # ---- 5. 风控状态 Key (risk:status) ----
    print("\n[5] 风控状态 risk_status_key")
    rk = schema.risk_status_key()
    assert rk == "risk:status", f"risk_status_key 格式错误: {rk}"
    r.hset(rk, mapping={"level": "normal", "rule_id": "R001", "updated_at": "2026-08-02T10:30:00"})
    assert r.hget(rk, "level") == "normal"
    test_keys.append(rk)
    print(f"    ✅ risk_status_key() = '{rk}'")

    # ---- 6. 账户状态 Key (account:summary) ----
    print("\n[6] 账户状态 account_summary_key")
    ak = schema.account_summary_key()
    assert ak == "account:summary", f"account_summary_key 格式错误: {ak}"
    r.hset(ak, mapping={"total_asset": "1000000", "cash": "500000", "available": "500000"})
    assert r.hget(ak, "total_asset") == "1000000"
    test_keys.append(ak)
    print(f"    ✅ account_summary_key() = '{ak}'")

    # ---- 7. Tick 缓存 Key (tick:{symbol}:latest) ----
    print("\n[7] Tick 缓存 tick_latest_key")
    tk2 = schema.tick_latest_key("000001.SZ")
    assert tk2 == "tick:000001.SZ:latest", f"tick_latest_key 格式错误: {tk2}"
    r.hset(tk2, mapping={"price": "12.50", "volume": "100000"})
    assert r.hget(tk2, "price") == "12.50"
    test_keys.append(tk2)
    print(f"    ✅ tick_latest_key('000001.SZ') = '{tk2}'")

    # ---- 8. TTL + 清理前缀常量 ----
    print("\n[8] TTL + 清理前缀常量")
    assert schema.TTL_POST_MARKET_SECONDS == 3600
    assert schema.TTL_TICK_POST_MARKET_SECONDS == 0
    assert schema.PREFIX_TICK in schema.POST_MARKET_CLEANUP_PREFIXES
    assert schema.PREFIX_TRADE in schema.POST_MARKET_CLEANUP_PREFIXES
    assert schema.PREFIX_ACCOUNT in schema.POST_MARKET_CLEANUP_PREFIXES
    assert schema.PREFIX_SIGNAL in schema.POST_MARKET_CLEANUP_PREFIXES
    assert schema.PREFIX_FEATURE not in schema.POST_MARKET_CLEANUP_PREFIXES  # feature 保留 TTL
    print(f"    ✅ TTL_POST_MARKET_SECONDS = {schema.TTL_POST_MARKET_SECONDS}")
    print(f"    ✅ TTL_TICK_POST_MARKET_SECONDS = {schema.TTL_TICK_POST_MARKET_SECONDS}")
    print(f"    ✅ POST_MARKET_CLEANUP_PREFIXES = {schema.POST_MARKET_CLEANUP_PREFIXES}")

    # ---- 9. 容量估算常量 ----
    print("\n[9] 容量估算常量")
    assert schema.MEMORY_ESTIMATE_TOTAL_MB == 200
    assert schema.MAXMEMORY_LIMIT == "1gb"  # 蓝图定义值（部署时降为512mb）
    assert schema.MAXMEMORY_EXPANSION_TRIGGER_RATIO == 0.70
    print(f"    ✅ MEMORY_ESTIMATE_TOTAL_MB = {schema.MEMORY_ESTIMATE_TOTAL_MB} MB")
    print(f"    ✅ MAXMEMORY_LIMIT = {schema.MAXMEMORY_LIMIT} (蓝图值,部署时降为512mb)")
    print(f"    ✅ MAXMEMORY_EXPANSION_TRIGGER_RATIO = {schema.MAXMEMORY_EXPANSION_TRIGGER_RATIO}")

    # ---- 清理测试数据 ----
    print("\n[10] 清理测试 Key")
    for key in test_keys:
        r.delete(key)
    print(f"    ✅ 已清理 {len(test_keys)} 个测试 Key")

    ds.close_all()

    print("\n=== 步骤4 验收通过 ✅ ===")
    print("h1_redis_schema.py 7类Key构造函数全部与真实Redis联调通过")
    print("可进入步骤5（编写 H1RedisWriter/Reader/Projectors）")


if __name__ == "__main__":
    main()
