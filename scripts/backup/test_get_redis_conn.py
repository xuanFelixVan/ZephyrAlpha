#!/usr/bin/env python3
"""验证 DatabaseService.get_redis_conn() 实现（步骤3 验收）。

测试项：
1. DatabaseService 实例化
2. get_redis_conn() 惰性初始化（首次调用建连，二次调用返回同一实例）
3. PING 响应
4. health_check() 包含 redis=True
5. close_all() 清理连接
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.infrastructure.database_service import DatabaseService


def main():
    print("=== 步骤3 验收: DatabaseService.get_redis_conn() ===")

    ds = DatabaseService()
    print("[1] DatabaseService 实例化: OK")

    # 首次调用——惰性建连
    r1 = ds.get_redis_conn()
    assert r1 is not None
    assert r1.ping() is True
    print(f"[2] 首次 get_redis_conn() + PING: OK (type={type(r1).__name__})")

    # 二次调用——返回同一实例（单例）
    r2 = ds.get_redis_conn()
    assert r1 is r2, "二次调用应返回同一连接实例（单例）"
    print("[3] 二次调用返回同一实例（单例）: OK")

    # 读写测试（模拟 H1 因子截面写入）
    r1.hset("feature:600000.SH", mapping={"momentum_20d:v1": "0.0567"})
    val = r1.hget("feature:600000.SH", "momentum_20d:v1")
    assert val == "0.0567"
    r1.delete("feature:600000.SH")
    print("[4] HSET/HGET/HDEL 因子截面 Key: OK")

    # 健康检查
    health = ds.health_check()
    print(f"[5] health_check(): {health}")
    assert "redis" in health, "health_check 应包含 redis 键"
    # redis 应为 True（VM 在线时）；governance/depgraph/clickhouse 可能为 False（无依赖时不阻断）
    assert health["redis"] is True, "Redis 健康检查应为 True"

    # close_all 清理
    ds.close_all()
    assert ds._redis_conn is None, "close_all 后 _redis_conn 应为 None"
    print("[6] close_all() 清理 Redis 连接: OK")

    print("\n=== 步骤3 验收通过 ✅ ===")
    print("get_redis_conn() 实现完成，可进入步骤4（Key Schema 联调）")


if __name__ == "__main__":
    main()
