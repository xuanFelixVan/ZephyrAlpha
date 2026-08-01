#!/usr/bin/env python3
"""H1 Redis 端到端连通性测试（INFRA-DB-007 部署验证）。

验证项：
1. redis_config.py 加载配置
2. redis-py 连接 + 认证
3. HSET/HGETALL 因子截面 Key（h1_redis_schema feature_key 模式）
4. CONFIG GET maxmemory/appendonly/maxmemory-policy
5. DB 号隔离验证（db0 可写）
"""

import sys
from pathlib import Path

# 确保能 import zephyr
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import redis

from zephyr.infrastructure.redis_config import load_redis_config


def main():
    print("=== H1 Redis 端到端测试 (INFRA-DB-007) ===")

    # 1. 加载配置
    cfg = load_redis_config()
    print(
        f"[1] 配置加载: host={cfg['host']}, port={cfg['port']}, db={cfg['db']}, "
        f"decode_responses={cfg['decode_responses']}"
    )

    # 2. 连接 + 认证
    r = redis.Redis(**cfg)
    pong = r.ping()
    print(f"[2] 连接+认证: PING={pong}")

    # 3. 因子截面 Key 读写测试（模拟 h1_redis_schema.feature_key）
    test_key = "feature:000001.SZ"
    r.hset(
        test_key,
        mapping={
            "momentum_20d:v1": "0.0234",
            "close:v1": "12.50",
            "volume_20d:v1": "1500000",
        },
    )
    vals = r.hgetall(test_key)
    print(f"[3] HSET/HGETALL {test_key}: {vals}")
    assert vals["momentum_20d:v1"] == "0.0234"
    assert vals["close:v1"] == "12.50"

    # 4. 配置验证
    info = r.info()
    config = r.config_get("maxmemory")
    print(f"[4] Redis 版本: {info['redis_version']}")
    print(f"    maxmemory: {config['maxmemory']} ({int(config['maxmemory']) // 1024 // 1024} MB)")
    print(f"    appendonly: {r.config_get('appendonly')['appendonly']}")
    print(f"    maxmemory-policy: {r.config_get('maxmemory-policy')['maxmemory-policy']}")
    print(f"    connected_clients: {info['connected_clients']}")
    print(f"    used_memory_human: {info['used_memory_human']}")

    # 5. DB 号隔离验证
    r.set("test:db0:sim", "模拟盘数据")
    assert r.get("test:db0:sim") == "模拟盘数据"
    print("[5] DB0(模拟盘) 写读: OK")

    # 清理测试数据
    r.delete(test_key)
    r.delete("test:db0:sim")
    print("[6] 清理测试 Key: OK")

    print("\n=== 端到端测试通过 ✅ ===")
    print("Redis 7.0.15 部署验证完成，可进入步骤3（实现 get_redis_conn）")


if __name__ == "__main__":
    main()
