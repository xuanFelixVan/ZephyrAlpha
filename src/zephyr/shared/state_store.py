# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.state_store
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.foundation.errors; zephyr.shared.state_store_redis(lazy, 仅工厂方法内)
# [CONSUMERS] zephyr.risk.implementations.default_risk_validator; zephyr.risk.stop_loss; zephyr.ex_core.fill_handler; zephyr.ex_core.position_tracker.tracker
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 单抽象族高内聚=文件后端+共享错误/校验+工厂（#ARCH-118 分层裁量 301-500 带适用）; 写入原子(pid-tmp+os.replace / Redis SET·SADD 单命令原子); 读损坏必抛StateCorruptError(不静默兜底); UTF-8全程; DedupSet.add幂等; Redis 不可用 fail-fast 抛 StateStoreError(构造即 PING，不静默降级文件后端); Redis 键无 TTL(见过即永久)
# [MODIFY-GUARD] tests/shared/test_state_store.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] StateCorruptError(ZA-SH-0050); StateStoreError(ZA-SH-0051)
# [TESTS] tests/shared/test_state_store.py
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: shared
# category: shared_infrastructure
# status: active
# created: "2026-08-16"
# ---

"""D_SHARED — Crash-only 状态外部化原语（#ARCH-QUANT-002 承载层）。

痛点（Qwen P0-2/P0-3 + 53 号 memo §7 裁定）：
  1. Kill Switch 熔断状态纯内存——进程 crash/重启即解除熔断，极端行情下恰是高发场景。
  2. FillHandler._processed_fill_ids 纯内存 set——重启后同一 fill_id 重放重复记账。
  3. 关键状态无统一外部化机制，各模块各自为战。

裁定（#ARCH-QUANT-002，2026-08-15 Owner 批准）：
  关键状态外部化 + 启动"恢复或新建"双路径 + 幂等操作 + 不可恢复错误 fail-fast。
  本模块是该裁定的机制承载层——两个最小原语：

  - JsonStateStore: 命名空间 JSON 快照存取（kill switch 熔断状态等"单条状态记录"）。
    写入原子（pid-tmp + os.replace，NTFS 原子语义）；读取三分语义：
    记录不存在 → None（fresh boot）/ 存在且可读 → dict / 存在但损坏 → StateCorruptError
    （由消费方决定 fail-closed 策略，本层绝不静默兜底）。
  - AppendOnlyDedupSet: append-only 持久化去重集（fill_id 等"见过即永久"幂等键）。
    一行一 ID 追加写，启动时全量加载；容忍 crash 末行残缺（截断行丢弃）。

设计对标：
  - NautilusTrader crash-only：启动与崩溃恢复共用同一路径，状态外部化。
  - durable_execution.py（本仓）：原子写手法（tmp + os.replace）。
  - 文件后端为默认（JSON/append-only 文件，测试无外部依赖）；
    Redis 后端同接口可选增强（53 号 §7 "已有 Redis 基础设施"，2026-08-17 AI-REDIS-001 落地），
    实现见 zephyr.shared.state_store_redis（#ARCH-118 拆分：双后端变更节奏不同+
    消费方热域变更隔离）——消费方零改动，切换走配置注入
    （make_state_store / make_dedup_set 工厂或构造参数直传）。

SSoT: #ARCH-QUANT-002 (architecture_issue_registry.yaml) + 53 号 memo §7
"""

from __future__ import annotations

import json
import logging
import os
import threading
from pathlib import Path
from typing import TYPE_CHECKING, Final

from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.io.file_utils import atomic_write

if TYPE_CHECKING:  # 仅类型注解用；运行时 lazy import（防 state_store_redis 循环依赖）
    import redis

    from zephyr.shared.state_store_redis import RedisDedupSet, RedisStateStore

__all__: Final = [
    "AppendOnlyDedupSet",
    "JsonStateStore",
    "StateCorruptError",
    "StateStoreError",
    "make_dedup_set",
    "make_state_store",
]

_logger = logging.getLogger(__name__)

#: Redis 键默认前缀（DB 号隔离由连接配置决定，前缀做库内命名空间隔离）
DEFAULT_STATE_KEY_PREFIX: Final = "za:state"
DEFAULT_DEDUP_KEY_PREFIX: Final = "za:dedup"


class StateStoreError(ZephyrBaseError):
    """状态外部化层基础错误。"""

    error_code = "ZA-SH-0051"


class StateCorruptError(StateStoreError):
    """状态记录存在但不可读/损坏——消费方必须按 fail-closed 处理。"""

    error_code = "ZA-SH-0050"


def _validate_namespace(namespace: str) -> str:
    """校验 namespace 合法性（双后端共用）：纯名字，禁止路径分隔符与 "." / ".."。

    文件后端防路径穿越；Redis 后端保证键规约 `{prefix}:{namespace}` 干净。

    Raises:
        StateStoreError: namespace 非法。
    """
    safe_name = Path(namespace).name
    if not safe_name or safe_name != namespace or namespace in (".", ".."):
        raise StateStoreError(f"非法 namespace: {namespace!r}（禁止路径分隔符）")
    return namespace


class JsonStateStore:
    """命名空间 JSON 快照状态存取（单条状态记录的外部化）。

    每个 namespace 对应 root_dir 下一个 `<namespace>.json` 文件。
    适用于 kill switch 熔断状态、LIQUIDATING 锁等"最新一条即真源"的状态。

    Usage:
        store = JsonStateStore("data/runtime/state")
        store.save("kill_switch", {"active": True, "event_id": "...", ...})
        rec = store.load("kill_switch")   # None=无记录 / dict=记录 / raise StateCorruptError=损坏

    Thread Safety:
        save/load 各自原子，无跨调用状态；多线程并发安全（os.replace 原子）。
        需要"检查-再-设置"复合语义的场景（如 LIQUIDATING 锁）由消费方
        配外部锁使用（见 stop_loss.execute_kill_switch_liquidation）。
    """

    def __init__(self, root_dir: str | os.PathLike[str]) -> None:
        self._root = Path(root_dir)
        self._root.mkdir(parents=True, exist_ok=True)

    @property
    def root_dir(self) -> Path:
        """只读：状态文件根目录。"""
        return self._root

    def _path_for(self, namespace: str) -> Path:
        """namespace → 状态文件路径（防路径穿越：仅取末段文件名）。"""
        return self._root / f"{_validate_namespace(namespace)}.json"

    def save(self, namespace: str, payload: dict) -> Path:
        """原子写入命名空间状态（pid-tmp + os.replace，RULE-ONE 模板）。

        Args:
            namespace: 命名空间（纯文件名，禁止路径分隔符）。
            payload: 可 JSON 序列化的状态字典。

        Returns:
            落盘文件路径。

        Raises:
            StateStoreError: namespace 非法或写入失败。
        """
        path = self._path_for(namespace)
        try:
            atomic_write(
                path,
                json.dumps(payload, ensure_ascii=False, default=str),
            )
        except OSError as exc:
            raise StateStoreError(
                "状态写入失败",
                details={"path": str(path), "error": str(exc)},
            ) from exc
        return path

    def load(self, namespace: str) -> dict | None:
        """读取命名空间状态（三分语义，绝不静默兜底）。

        Returns:
            None: 记录不存在（fresh boot，由消费方按"从未发生"处理）。
            dict: 记录内容。

        Raises:
            StateCorruptError: 记录存在但损坏/不可读——消费方必须 fail-closed。
        """
        path = self._path_for(namespace)
        if not path.is_file():
            return None
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise StateCorruptError(
                "状态记录损坏",
                details={"path": str(path), "error": str(exc)},
            ) from exc
        if not isinstance(data, dict):
            raise StateCorruptError(
                "状态记录非 dict",
                details={"path": str(path), "type": type(data).__name__},
            )
        return data

    def delete(self, namespace: str) -> bool:
        """删除命名空间状态。返回是否实际删除（不存在=False）。"""
        path = self._path_for(namespace)
        try:
            os.remove(path)
            return True
        except FileNotFoundError:
            return False
        except OSError as exc:
            raise StateStoreError(
                "状态删除失败",
                details={"path": str(path), "error": str(exc)},
            ) from exc


class AppendOnlyDedupSet:
    """append-only 持久化去重集（幂等键"见过即永久"）。

    一行一个 ID 追加落盘，启动时全量加载进内存 set。
    适用于 fill_id 去重、event_id 去重等"只增不删"的幂等场景。

    Usage:
        dedup = AppendOnlyDedupSet("data/runtime/processed_fill_ids.txt")
        if dedup.add(fill.fill_id):
            ...  # 首次见到，执行记账
        else:
            ...  # 重复（含重启后重放），跳过

    Crash 容忍：
        追加写中途 crash 可能留下未换行的残缺末行——加载时丢弃
        （该 ID 视为未见过，下次重放会重新走完整路径，fail-safe 方向=宁可重判不误杀）。

    Thread Safety:
        内部 threading.Lock 保护 add/__contains__ 复合调用。
    """

    def __init__(self, path: str | os.PathLike[str]) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._ids: set[str] = set()
        self._lock = threading.Lock()
        self._load()

    @property
    def path(self) -> Path:
        """只读：去重集文件路径。"""
        return self._path

    def _load(self) -> None:
        """启动加载：全量读入；末行无换行符=crash 残行，丢弃。"""
        if not self._path.is_file():
            return
        try:
            raw = self._path.read_bytes()
        except OSError as exc:
            raise StateCorruptError(
                "去重集不可读",
                details={"path": str(self._path), "error": str(exc)},
            ) from exc
        if not raw:
            return
        try:
            text = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            # 错误契约统一（AI-R3 复审 P2 治本）：字节级损坏（非法 UTF-8）
            # 原裸 UnicodeDecodeError 逃逸违反头注 INVARIANT「读损坏必抛
            # StateCorruptError」——统一映射，消费方 catch 语义不被破坏
            raise StateCorruptError(
                "去重集编码损坏（非法 UTF-8）",
                details={"path": str(self._path), "error": str(exc)},
            ) from exc
        lines = text.split("\n")
        # 末行无换行符（crash 残行）→ 丢弃
        if lines and not text.endswith("\n"):
            dropped = lines.pop()
            if dropped:
                _logger.warning(
                    "去重集末行残缺已丢弃(crash容忍): path=%s fragment=%r",
                    self._path,
                    dropped[:64],
                )
        for line in lines:
            item = line.strip()
            if item:
                self._ids.add(item)

    def add(self, item_id: str) -> bool:
        """登记 ID。首次见到=True（并落盘）；已存在=False（幂等拦截）。

        Raises:
            StateStoreError: item_id 非法（空/含换行）或落盘失败。
        """
        if not item_id or "\n" in item_id or "\r" in item_id:
            raise StateStoreError(f"非法去重 ID: {item_id!r}")
        with self._lock:
            if item_id in self._ids:
                return False
            try:
                with open(self._path, "a", encoding="utf-8") as f:
                    f.write(f"{item_id}\n")
                    f.flush()
                    os.fsync(f.fileno())
            except OSError as exc:
                raise StateStoreError(
                    "去重集落盘失败",
                    details={"path": str(self._path), "error": str(exc)},
                ) from exc
            self._ids.add(item_id)
            return True

    def __contains__(self, item_id: str) -> bool:
        with self._lock:
            return item_id in self._ids

    def __len__(self) -> int:
        with self._lock:
            return len(self._ids)


def make_state_store(
    backend: str = "json",
    *,
    root_dir: str | os.PathLike[str] | None = None,
    redis_conn: redis.Redis | None = None,
    key_prefix: str = DEFAULT_STATE_KEY_PREFIX,
) -> JsonStateStore | RedisStateStore:
    """状态存取工厂——消费方切换后端的唯一决策点（配置注入，默认文件后端）。

    Args:
        backend: "json"（默认，文件后端）或 "redis"。
        root_dir: 文件后端根目录（backend="json" 必填）。
        redis_conn: Redis 连接（backend="redis" 必填——由接线层经
            zephyr.infrastructure.redis_config.load_redis_config() 建连注入，
            config/.env.redis 单真源，本层不出现连接参数）。
        key_prefix: Redis 键前缀。

    Raises:
        StateStoreError: backend 未知或必填参数缺失。
    """
    if backend == "json":
        if root_dir is None:
            raise StateStoreError("backend='json' 必须提供 root_dir")
        return JsonStateStore(root_dir)
    if backend == "redis":
        if redis_conn is None:
            raise StateStoreError(
                "backend='redis' 必须注入 redis_conn"
                "（由接线层经 zephyr.infrastructure.redis_config.load_redis_config 建连）"
            )
        from zephyr.shared.state_store_redis import RedisStateStore

        return RedisStateStore(redis_conn, key_prefix=key_prefix)
    raise StateStoreError(f"未知 state_store 后端: {backend!r}（合法值: 'json'/'redis'）")


def make_dedup_set(
    backend: str = "json",
    *,
    path: str | os.PathLike[str] | None = None,
    redis_conn: redis.Redis | None = None,
    set_name: str | None = None,
    key_prefix: str = DEFAULT_DEDUP_KEY_PREFIX,
) -> AppendOnlyDedupSet | RedisDedupSet:
    """去重集工厂——消费方切换后端的唯一决策点（配置注入，默认文件后端）。

    Args:
        backend: "json"（默认，append-only 文件）或 "redis"。
        path: 文件后端落盘路径（backend="json" 必填）。
        redis_conn: Redis 连接（backend="redis" 必填——由接线层经
            zephyr.infrastructure.redis_config.load_redis_config() 建连注入，
            config/.env.redis 单真源，本层不出现连接参数）。
        set_name: Redis 去重集名（backend="redis" 必填，如 "processed_fill_ids"）。
        key_prefix: Redis 键前缀。

    Raises:
        StateStoreError: backend 未知或必填参数缺失。
    """
    if backend == "json":
        if path is None:
            raise StateStoreError("backend='json' 必须提供 path")
        return AppendOnlyDedupSet(path)
    if backend == "redis":
        if not set_name:
            raise StateStoreError("backend='redis' 必须提供 set_name")
        if redis_conn is None:
            raise StateStoreError(
                "backend='redis' 必须注入 redis_conn"
                "（由接线层经 zephyr.infrastructure.redis_config.load_redis_config 建连）"
            )
        from zephyr.shared.state_store_redis import RedisDedupSet

        return RedisDedupSet(redis_conn, set_name=set_name, key_prefix=key_prefix)
    raise StateStoreError(f"未知 dedup_set 后端: {backend!r}（合法值: 'json'/'redis'）")
