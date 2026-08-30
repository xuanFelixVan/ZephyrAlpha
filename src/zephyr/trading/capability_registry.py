# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.capability_registry
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-035 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CapabilityRegistry — 能力注册中心
==================================
蓝图: docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md §3.1
对标: Google A2A AgentCard + Anthropic MCP Tools + Cursor Rules

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: card_dir 参数
#   fields: 参数 card_dir（无注解）
#   code: capability_registry.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: cache_ttl_seconds 参数
#   fields: 参数 cache_ttl_seconds（无注解）
#   code: capability_registry.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CapabilityRegistry
#   name_en: CapabilityRegistry
#   intro: 能力注册中心——解决'AI 不知道有这个功能'的问题。
#   desc: 能力注册中心——解决'AI 不知道有这个功能'的问题。 对标: - Google A2A Agent Card: JSON 格式的能力自描述 - Anthropic MCP: t…；公共方法（定义序）: card_di…
#   inputs: card_dir cache_ttl_seconds
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: CapabilityRegistry
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

import threading
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import yaml

from zephyr.shared.io.serialization import filter_dataclass_fields
from zephyr.trading.capability_card import CapabilityCard


class _ReadWriteLock:
    """读写锁（读优先）——能力注册为读多写少场景（蓝图 §16.3 T0 高 QPS 读），
    读路径并发放行，写路径独占。写操作低频（注册/卸载），读优先不致写饥饿。"""

    def __init__(self) -> None:
        self._cond = threading.Condition(threading.Lock())
        self._readers = 0
        self._writer = False

    @contextmanager
    def read(self) -> Iterator[None]:
        with self._cond:
            while self._writer:
                self._cond.wait()
            self._readers += 1
        try:
            yield
        finally:
            with self._cond:
                self._readers -= 1
                if self._readers == 0:
                    self._cond.notify_all()

    @contextmanager
    def write(self) -> Iterator[None]:
        with self._cond:
            while self._writer or self._readers > 0:
                self._cond.wait()
            self._writer = True
        try:
            yield
        finally:
            with self._cond:
                self._writer = False
                self._cond.notify_all()


class CapabilityRegistry:
    """能力注册中心——解决'AI 不知道有这个功能'的问题。

    对标:
      - Google A2A Agent Card: JSON 格式的能力自描述
      - Anthropic MCP: tools/list -> 列出所有可用工具
      - Cursor Rules: .cursor/rules/ 持久化上下文

    容量升级（蓝图 §16.3 T0 / GAP-006 配套）：
      - 查询结果内存缓存：版本号失效（写操作 bump）+ TTL 兜底，缓存条目
        随注册表变更懒惰失效，无脏读窗口；
      - 读写锁替代互斥锁：读 QPS 远高于写，读路径不再互斥排队；
      - cache_stats() 暴露命中率，验收口径 >95%（蓝图 §4.1 监控指标 3）。
    """

    def __init__(self, card_dir: Path | None = None, cache_ttl_seconds: float = 300.0) -> None:
        self._cards: dict[str, CapabilityCard] = {}
        self._lock = _ReadWriteLock()
        self._card_dir = card_dir
        # 内存缓存（GAP-006 配套）：key=(op, args...)，value=(version, monotonic_ts, result)
        self._cache: dict[tuple, tuple[int, float, Any]] = {}
        self._cache_lock = threading.Lock()
        self._cache_version = 0
        self._cache_ttl_seconds = cache_ttl_seconds
        self._cache_hits = 0
        self._cache_misses = 0

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def card_dir(self):
        """只读：card_dir（Stage 4 公共化）。"""
        return self._card_dir

    @card_dir.setter
    def card_dir(self, value):
        """写入：card_dir（Stage 4 公共化）。"""
        self._card_dir = value

    # ── 内存缓存（GAP-006 配套，蓝图 §16.3 步骤 1）──
    def _cached(self, key: tuple, loader: Callable[[], Any]) -> Any:
        """读缓存：版本号匹配且 TTL 未过期 → 命中；否则执行 loader 并回填。

        失效策略：写操作（register/unregister/load_from_dir）bump _cache_version，
        旧版本条目懒惰失效；TTL 兜底防版本号之外的漂移（默认 300s，构造可调）。
        """
        now = time.monotonic()
        with self._cache_lock:
            entry = self._cache.get(key)
            if entry is not None:
                version, ts, value = entry
                if version == self._cache_version and (now - ts) < self._cache_ttl_seconds:
                    self._cache_hits += 1
                    return value
            self._cache_misses += 1
        value = loader()
        with self._cache_lock:
            self._cache[key] = (self._cache_version, now, value)
        return value

    def cache_stats(self) -> dict[str, Any]:
        """缓存命中率指标（验收口径：命中率 >95%）。"""
        with self._cache_lock:
            total = self._cache_hits + self._cache_misses
            return {
                "hits": self._cache_hits,
                "misses": self._cache_misses,
                "hit_rate": (self._cache_hits / total) if total else 0.0,
                "size": len(self._cache),
                "ttl_seconds": self._cache_ttl_seconds,
            }

    def register(self, card: CapabilityCard) -> None:
        with self._lock.write():
            if card.capability_id in self._cards:
                return
            self._cards[card.capability_id] = card
            self._cache_version += 1
        if self._card_dir is not None:
            self._persist_card(card)

    def unregister(self, capability_id: str) -> None:
        with self._lock.write():
            if capability_id in self._cards:
                self._cards.pop(capability_id, None)
                self._cache_version += 1

    def discover(self, query: str) -> list[CapabilityCard]:
        q = query.lower()
        with self._lock.read():
            return self._cached(
                ("discover", q),
                lambda: [
                    card for card in self._cards.values() if q in card.name.lower() or q in card.description.lower()
                ],
            )

    def list_all(self) -> list[CapabilityCard]:
        with self._lock.read():
            return self._cached(("list_all",), lambda: list(self._cards.values()))

    def find_by_tags(self, tags: list[str]) -> list[CapabilityCard]:
        tag_set = frozenset(t.lower() for t in tags)
        with self._lock.read():
            return self._cached(
                ("find_by_tags", tag_set),
                lambda: [card for card in self._cards.values() if tag_set & {t.lower() for t in card.tags}],
            )

    def get(self, capability_id: str) -> CapabilityCard | None:
        with self._lock.read():
            return self._cached(("get", capability_id), lambda: self._cards.get(capability_id))

    def health_check_all(self) -> dict[str, bool]:
        with self._lock.read():
            return self._cached(
                ("health_check_all",),
                lambda: {cid: card.status == "ACTIVE" for cid, card in self._cards.items()},
            )

    def dump_snapshot(self) -> dict[str, Any]:
        with self._lock.read():
            return {cid: card.model_dump() for cid, card in self._cards.items()}

    def count(self) -> int:
        with self._lock.read():
            return self._cached(("count",), lambda: len(self._cards))

    def _persist_card(self, card: CapabilityCard) -> None:
        if self._card_dir is None:
            return
        self._card_dir.mkdir(parents=True, exist_ok=True)
        path = self._card_dir / f"{card.capability_id}.yaml"
        data = card.model_dump(mode="json")
        path.write_text(yaml.dump(data, allow_unicode=True, default_flow_style=False), encoding="utf-8")

    def load_from_dir(self) -> int:
        if self._card_dir is None or not self._card_dir.exists():
            return 0
        count = 0
        for path in self._card_dir.glob("*.yaml"):
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
                card = CapabilityCard(**filter_dataclass_fields(CapabilityCard, data))
                with self._lock.write():
                    if card.capability_id not in self._cards:
                        self._cards[card.capability_id] = card
                        self._cache_version += 1
                count += 1
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                continue
        return count
