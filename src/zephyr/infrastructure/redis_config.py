# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.infrastructure.redis_config
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.io.paths; zephyr.shared.security.secrets
# [CONSUMERS] zephyr.infrastructure.database_service; zephyr.infrastructure.h1_redis_hot
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Redis 连接配置唯一真源为 config/.env.redis; 禁止任何入口硬编码 IP/密码默认值; ensure_redis_env_loaded 幂等; load_redis_config 读不到配置抛 RedisConfigError(fail-closed)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ensure_redis_env_loaded 文件不存在->log warning+不抛; load_redis_config 配置缺失->抛 RedisConfigError
# [TESTS] tests/zephyr/infrastructure/test_redis_config.py
# [A_module] module_id=MOD-INF-002 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Redis 连接配置单真源加载器（H1 业务热缓存 INFRA-DB-007）。

背景：
    仿 ch_config.py（裁定 #ARCH-CH-017 同源思想）。Redis 7.0.15 部署在 Hyper-V
    Ubuntu VM（zephyr-ch, 172.24.30.100），与 ClickHouse 同 VM 共存（D1 决策）。
    归属 MOD-INF-002（D2 决策：get_redis_conn 已在此模块）。当前单实例 + DB 号
    隔离（D3 决策：sim=db0/live=db1/治理=db2/测试=db15——tests/shared 专用隔离库，
    flushdb 清理，2026-08-17 AI-REDIS-001 约定登记；未来 INFRA-CACHE-001 立项时起独立实例）。

治本原则（同 #ARCH-CH-017）：
    - config/.env.redis 是 Redis 连接配置的唯一真源
    - 所有 Redis 连接入口必须主动读取该文件，禁止用硬编码 IP/密码作为默认值
    - 启动入口必须显式加载 .env.redis 到 os.environ
    - 读不到配置 fail-closed（抛异常），而非静默用 localhost/空密码

公共接口：
    - ensure_redis_env_loaded(): 将 .env.redis 加载到 os.environ（幂等）
    - load_redis_config(): 返回 Redis 连接配置字典，读不到抛 RedisConfigError

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: redis_config.py
# 层: 算法
# - id: A1
#   name_zh: ① ensure_redis_env_loaded
#   name_en: ensure_redis_env_loaded
#   intro: 将 config/.env.redis 加载到 os.environ（幂等）。
#   desc: 将 config/.env.redis 加载到 os.environ（幂等）。 优先级：已有 os.environ 不覆盖（允许环境变量显式 override）。 文件不存在时…；源码 L113-L146
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② load_redis_config
#   name_en: load_redis_config
#   intro: 返回 Redis 连接配置字典。
#   desc: 返回 Redis 连接配置字典。 优先级：os.environ > config/.env.redis > 抛 RedisConfigError。 禁止任何默认 IP/密码值（裁…；源码 L149-L192
#   inputs: 无参数
#   outputs: dict[str, str | int | bool]
# - id: A3
#   name_zh: ③ get_redis_env_path
#   name_en: get_redis_env_path
#   intro: 返回 Redis 配置文件路径（供测试/诊断使用）。
#   desc: 返回 Redis 配置文件路径（供测试/诊断使用）。；源码 L195-L197
#   inputs: 无参数
#   outputs: Path
#   （注：A3 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: dict[str, str | int | bool]
#   name_en: dict[str, str | int | bool]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.infrastructure.database_service; zephyr.infrastructure.h1_redis_hot
# - id: O2
#   name_zh: Path
#   name_en: Path
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.infrastructure.database_service; zephyr.infrastructure.h1_redis_hot
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import logging
import os
import threading
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.security.secrets import get_service_secret

log = logging.getLogger(__name__)

# Redis 连接配置文件路径（唯一真源）
_REDIS_ENV_PATH: Path = REPO_ROOT / "config" / ".env.redis"

# 必须存在的配置键（host 是硬性要求，其余有默认值）
_REQUIRED_KEYS = ("REDIS_HOST", "REDIS_PORT", "REDIS_PASSWORD")

# 幂等加载标志（避免重复解析文件）
_loaded: bool = False
_load_lock = threading.Lock()


class RedisConfigError(RuntimeError):
    """Redis 配置缺失或不可读时抛出（fail-closed，禁止静默用默认值）。"""


def ensure_redis_env_loaded() -> None:
    """将 config/.env.redis 加载到 os.environ（幂等）。

    优先级：已有 os.environ 不覆盖（允许环境变量显式 override）。
    文件不存在时 log warning 但不抛异常（开发环境友好），
    后续 load_redis_config() 会因配置缺失抛 RedisConfigError。

    幂等：模块级 _loaded 标志保证只解析一次文件。
    """
    global _loaded
    if _loaded:
        return
    with _load_lock:
        if _loaded:
            return
        if not _REDIS_ENV_PATH.is_file():
            log.warning("Redis 配置文件不存在: %s（Redis 连接将失败）", _REDIS_ENV_PATH)
            _loaded = True
            return
        try:
            for line in _REDIS_ENV_PATH.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                # 不覆盖已有环境变量（允许显式 override）
                os.environ.setdefault(k, v)
            log.info("Redis 配置已加载: %s", _REDIS_ENV_PATH)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            log.error("Redis 配置加载失败 %s: %s", _REDIS_ENV_PATH, e)
        finally:
            _loaded = True


def load_redis_config() -> dict[str, str | int | bool]:
    """返回 Redis 连接配置字典。

    优先级：os.environ > config/.env.redis > 抛 RedisConfigError。
    禁止任何默认 IP/密码值（裁定 #ARCH-CH-017 同源思想）。

    Returns:
        包含 host/port/password/db/decode_responses 的字典。

    Raises:
        RedisConfigError: 如果 REDIS_HOST 配置缺失（fail-closed）。
    """
    ensure_redis_env_loaded()
    # host 是必须的，缺失则 fail-closed（禁止默认 localhost/172.24.30.100）
    host = get_service_secret("REDIS_HOST", "redis", required=False)
    if not host:
        raise RedisConfigError(
            f"REDIS_HOST 未配置：os.environ 未设置且 {_REDIS_ENV_PATH} 不含该键。"
            f"请创建 config/.env.redis 并填写 REDIS_HOST=<Hyper-V VM IP>。"
        )
    password = get_service_secret("REDIS_PASSWORD", "redis", required=False)
    if not password:
        raise RedisConfigError(
            "REDIS_PASSWORD 未配置：Redis 已启用 requirepass（蓝图 §7.1 安全考量），"
            "禁止无密码连接。请在 config/.env.redis 填写 REDIS_PASSWORD。"
        )
    port = int(get_service_secret("REDIS_PORT", "redis", required=False) or "6379")
    db = int(get_service_secret("REDIS_DB", "redis", required=False) or "0")
    decode_raw = get_service_secret("REDIS_DECODE_RESPONSES", "redis", required=False) or "true"
    decode_responses = decode_raw.strip().lower() in ("1", "true", "yes")
    # 操作超时（治本 CP-02 软故障，2026-08-03 实地演练发现）：
    # 无 socket_timeout 时 Redis 暂停/卡顿 → redis-py 无限阻塞 → try/except 永不触发
    # → CP-02 优雅降级失效。设超时后软故障抛 TimeoutError → 触发降级（跳过+兜底+标过期）。
    socket_timeout = float(get_service_secret("REDIS_SOCKET_TIMEOUT", "redis", required=False) or "2")
    socket_connect_timeout = float(get_service_secret("REDIS_SOCKET_CONNECT_TIMEOUT", "redis", required=False) or "2")
    return {
        "host": host,
        "port": port,
        "password": password,
        "db": db,
        "decode_responses": decode_responses,
        "socket_timeout": socket_timeout,
        "socket_connect_timeout": socket_connect_timeout,
    }


def get_redis_env_path() -> Path:
    """返回 Redis 配置文件路径（供测试/诊断使用）。"""
    return _REDIS_ENV_PATH
