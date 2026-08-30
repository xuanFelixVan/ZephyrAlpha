# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.state_store_redis
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.state_store（错误类/命名空间校验/键前缀常量）; redis(lazy, 仅方法内)
# [CONSUMERS] zephyr.shared.state_store（工厂 lazy import）; tests/shared/test_state_store_redis.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 单主类族高内聚=同契约 Redis 后端双实现（#ARCH-118 分层裁量 301-500 带适用）; SET/SADD 单命令原子; 读损坏必抛StateCorruptError; Redis 不可用构造即 PING fail-fast 抛 StateStoreError(禁静默降级文件后端); 键无 TTL(见过即永久); 本层零连接参数(建连归接线层 redis_config，shared→infrastructure 反向依赖属层级违规)
# [MODIFY-GUARD] tests/shared/test_state_store_redis.py; src/zephyr/shared/state_store.py（工厂消费方）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] StateCorruptError(ZA-SH-0050); StateStoreError(ZA-SH-0051)
# [TESTS] tests/shared/test_state_store_redis.py
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: shared
# category: shared_infrastructure
# status: active
# created: "2026-08-17"
# ---

"""
D_SHARED — Crash-only 状态外部化原语 · Redis 后端（#ARCH-QUANT-002 承载层）。

与 zephyr.shared.state_store（文件后端）同接口契约的 Redis 实现，
2026-08-17 AI-REDIS-001 落地；自 state_store.py 拆出（#ARCH-118：
双后端变更节奏不同+消费方热域变更隔离）。

  - RedisStateStore: 命名空间 JSON 快照（kill switch 熔断状态等"单条状态记录"）。
    save → SET 单命令原子；load 三分语义保持（GET nil → None / 可解析 dict → dict /
    不可解析或非 dict → StateCorruptError）；delete → DEL。
  - RedisDedupSet: 持久化去重集（fill_id 等"见过即永久"幂等键）。
    add → SADD 服务端原子返回 1=首次/0=重复（幂等保证与文件后端一致，
    无需进程内锁）；__contains__ → SISMEMBER；__len__ → SCARD。

crash 容忍等价物：文件后端靠"末行残缺丢弃"，Redis 后端靠服务端持久化（AOF/RDB），
客户端进程 crash 不影响已确认写入；实例重启=重连即恢复。

键规约：`{key_prefix}:{namespace}`，默认前缀 za:state / za:dedup；键无 TTL——
kill switch 状态与 fill_id 去重是"见过即永久"记录，TTL 会破坏幂等保证。
DB 号隔离沿用 D3 决策（sim=db0/live=db1/治理=db2/测试=db15），由连接配置决定，本层不感知。

连接配置：禁硬编码——本层不出现任何连接参数，由接线层经
zephyr.infrastructure.redis_config.load_redis_config()（config/.env.redis 单真源，
fail-closed）建连后注入 redis.Redis 连接（与 H1RedisReader 同款 DI 模式；
shared→infrastructure 反向依赖属层级违规，故 config 建连不下沉到本层）。

SSoT: #ARCH-QUANT-002 (architecture_issue_registry.yaml) + 53 号 memo §7

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: redis_conn 参数
#   fields: 参数 redis_conn（无注解）
#   code: state_store_redis.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: key_prefix 参数
#   fields: 参数 key_prefix（无注解）
#   code: state_store_redis.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① RedisStateStore
#   name_en: RedisStateStore
#   intro: 命名空间 JSON 快照状态存取——Redis 后端（与 JsonStateStore 同接口契约）。
#   desc: 命名空间 JSON 快照状态存取——Redis 后端（与 JsonStateStore 同接口契约）。 每个 namespace 对应一个 Redis STRING 键 `{ke…；公共方法（定义序）: key_pre…
#   inputs: redis_conn key_prefix
#   outputs: 返回值
# - id: A2
#   name_zh: ② RedisDedupSet
#   name_en: RedisDedupSet
#   intro: 持久化去重集——Redis 后端（与 AppendOnlyDedupSet 同接口契约）。
#   desc: 持久化去重集——Redis 后端（与 AppendOnlyDedupSet 同接口契约）。 一个去重集对应一个 Redis SET 键 `{key_prefix}:{set_na…；公共方法（定义序）: key, ad…
#   inputs: redis_conn set_name key_prefix
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: RedisStateStore, RedisDedupSet
#   downstream: zephyr.shared.state_store（工厂 lazy import）; tests/shared/test_state_store_redis.…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Final

from zephyr.shared.state_store import (
    DEFAULT_DEDUP_KEY_PREFIX,
    DEFAULT_STATE_KEY_PREFIX,
    StateCorruptError,
    StateStoreError,
    _validate_namespace,
)

if TYPE_CHECKING:  # 仅类型注解用；运行时 lazy import（仓内 redis 统一惰性加载惯例）
    import redis

__all__: Final = [
    "RedisDedupSet",
    "RedisStateStore",
]

_logger = logging.getLogger(__name__)


def _ping_or_raise(conn: redis.Redis, *, what: str) -> None:
    """构造期 fail-fast 探活：Redis 不可用抛 StateStoreError（禁止静默降级）。"""
    import redis as redis_lib

    try:
        conn.ping()
    except redis_lib.RedisError as exc:
        raise StateStoreError(
            f"Redis 不可用（{what} 构造 fail-fast）",
            details={"error": str(exc)},
        ) from exc


class RedisStateStore:
    """命名空间 JSON 快照状态存取——Redis 后端（与 JsonStateStore 同接口契约）。

    每个 namespace 对应一个 Redis STRING 键 `{key_prefix}:{namespace}`，值为 JSON 文本。
    语义映射：save → SET（单命令原子）；load 三分语义保持；delete → DEL。

    Usage:
        # redis_conn 由接线层经 zephyr.infrastructure.redis_config.load_redis_config()
        # 建连注入（config/.env.redis 单真源；shared→infrastructure 反向依赖属层级
        # 违规，故本层不提供 from_config）
        store = RedisStateStore(redis_conn)
        store.save("kill_switch", {"active": True, ...})
        rec = store.load("kill_switch")   # None=无记录 / dict=记录 / raise StateCorruptError=损坏

    Fail-Fast:
        构造即 PING——Redis 不可用立即抛 StateStoreError（对齐"不可恢复错误
        fail-fast"裁定，不做静默降级文件后端）；运行期操作失败同样抛 StateStoreError。

    Thread Safety:
        redis-py 客户端内置连接池，跨线程共享安全；单命令原子无需进程内锁。
        "检查-再-设置"复合语义同文件后端——由消费方配外部锁。

    TTL:
        键无 TTL——kill switch 状态等是"最新一条即真源"的永久记录。
    """

    def __init__(self, redis_conn: redis.Redis, *, key_prefix: str = DEFAULT_STATE_KEY_PREFIX) -> None:
        if not key_prefix or "\n" in key_prefix or "\r" in key_prefix:
            raise StateStoreError(f"非法 Redis 键前缀: {key_prefix!r}")
        self._conn = redis_conn
        self._key_prefix = key_prefix
        _ping_or_raise(self._conn, what=type(self).__name__)

    @property
    def key_prefix(self) -> str:
        """只读：Redis 键前缀。"""
        return self._key_prefix

    def _key_for(self, namespace: str) -> str:
        """namespace → Redis 键（复用双后端共用校验）。"""
        return f"{self._key_prefix}:{_validate_namespace(namespace)}"

    def save(self, namespace: str, payload: dict) -> str:
        """原子写入命名空间状态（SET 单命令原子，等价文件后端 pid-tmp+os.replace）。

        Args:
            namespace: 命名空间（纯名字，禁止路径分隔符）。
            payload: 可 JSON 序列化的状态字典。

        Returns:
            写入的 Redis 键。

        Raises:
            StateStoreError: namespace 非法或 Redis 操作失败。
        """
        import redis as redis_lib

        key = self._key_for(namespace)
        text = json.dumps(payload, ensure_ascii=False, default=str)
        try:
            self._conn.set(key, text)
        except redis_lib.RedisError as exc:
            raise StateStoreError(
                "状态写入失败",
                details={"key": key, "error": str(exc)},
            ) from exc
        return key

    def load(self, namespace: str) -> dict | None:
        """读取命名空间状态（三分语义，与文件后端一致，绝不静默兜底）。

        Returns:
            None: 记录不存在（fresh boot，由消费方按"从未发生"处理）。
            dict: 记录内容。

        Raises:
            StateCorruptError: 记录存在但损坏/非 dict——消费方必须 fail-closed。
            StateStoreError: Redis 操作失败。
        """
        import redis as redis_lib

        key = self._key_for(namespace)
        try:
            raw = self._conn.get(key)
        except redis_lib.RedisError as exc:
            raise StateStoreError(
                "状态读取失败",
                details={"key": key, "error": str(exc)},
            ) from exc
        if raw is None:
            return None
        if isinstance(raw, bytes):
            try:
                raw = raw.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise StateCorruptError(
                    "状态记录损坏",
                    details={"key": key, "error": str(exc)},
                ) from exc
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise StateCorruptError(
                "状态记录损坏",
                details={"key": key, "error": str(exc)},
            ) from exc
        if not isinstance(data, dict):
            raise StateCorruptError(
                "状态记录非 dict",
                details={"key": key, "type": type(data).__name__},
            )
        return data

    def delete(self, namespace: str) -> bool:
        """删除命名空间状态。返回是否实际删除（不存在=False）。"""
        import redis as redis_lib

        key = self._key_for(namespace)
        try:
            return bool(self._conn.delete(key))
        except redis_lib.RedisError as exc:
            raise StateStoreError(
                "状态删除失败",
                details={"key": key, "error": str(exc)},
            ) from exc


class RedisDedupSet:
    """持久化去重集——Redis 后端（与 AppendOnlyDedupSet 同接口契约）。

    一个去重集对应一个 Redis SET 键 `{key_prefix}:{set_name}`。
    语义映射：add → SADD（服务端原子返回 1=首次/0=重复，幂等保证与文件后端一致）；
    __contains__ → SISMEMBER；__len__ → SCARD。

    Usage:
        dedup = RedisDedupSet(redis_conn, set_name="processed_fill_ids")
        if dedup.add(fill.fill_id):
            ...  # 首次见到，执行记账
        else:
            ...  # 重复（含重启后重放），跳过

    Crash 容忍等价物:
        文件后端容忍"末行残缺"（丢弃重判）；Redis 后端由服务端持久化（AOF/RDB）
        保证已确认写入不丢，客户端进程 crash 不影响集合内容，重连即恢复。

    Thread Safety:
        SADD 服务端原子，redis-py 连接池线程安全——无需文件后端的进程内锁。

    TTL:
        键无 TTL——fill_id 等幂等键"见过即永久"，TTL 会破坏幂等保证。
    """

    def __init__(
        self,
        redis_conn: redis.Redis,
        *,
        set_name: str,
        key_prefix: str = DEFAULT_DEDUP_KEY_PREFIX,
    ) -> None:
        if not key_prefix or "\n" in key_prefix or "\r" in key_prefix:
            raise StateStoreError(f"非法 Redis 键前缀: {key_prefix!r}")
        _validate_namespace(set_name)
        self._conn = redis_conn
        self._key = f"{key_prefix}:{set_name}"
        _ping_or_raise(self._conn, what=type(self).__name__)

    @property
    def key(self) -> str:
        """只读：去重集 Redis 键。"""
        return self._key

    def add(self, item_id: str) -> bool:
        """登记 ID。首次见到=True；已存在=False（幂等拦截，SADD 服务端原子）。

        Raises:
            StateStoreError: item_id 非法（空/含换行）或 Redis 操作失败。
        """
        import redis as redis_lib

        if not item_id or "\n" in item_id or "\r" in item_id:
            raise StateStoreError(f"非法去重 ID: {item_id!r}")
        try:
            return bool(self._conn.sadd(self._key, item_id))
        except redis_lib.RedisError as exc:
            raise StateStoreError(
                "去重集写入失败",
                details={"key": self._key, "error": str(exc)},
            ) from exc

    def __contains__(self, item_id: str) -> bool:
        import redis as redis_lib

        try:
            return bool(self._conn.sismember(self._key, item_id))
        except redis_lib.RedisError as exc:
            raise StateStoreError(
                "去重集读取失败",
                details={"key": self._key, "error": str(exc)},
            ) from exc

    def __len__(self) -> int:
        import redis as redis_lib

        try:
            return int(self._conn.scard(self._key))
        except redis_lib.RedisError as exc:
            raise StateStoreError(
                "去重集计数失败",
                details={"key": self._key, "error": str(exc)},
            ) from exc
