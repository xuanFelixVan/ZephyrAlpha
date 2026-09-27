# [BLUEPRINT] MOD-LIB-003 | docs/03_modules/_domain_library/blueprint.md | §3
# [MODULE] zephyr.library.ledger_cache
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.library.ledger_fingerprint (世代水位唯一读出件); zephyr.library.ledger_schema (_SQL_LOOKUP 投影列/_SQL_ENSURE_ASSETS 列校验真源); zephyr.library.librarian (PgConnection Protocol——连接形态注解唯一真源，禁裸 Any); zephyr.governance.depgraph_schema (get/release_depgraph_pg_connection 池化借还); zephyr.shared.utils.time_utils (now_utc 时区安全时钟)
# [CONSUMERS] zephyr.library.lookup
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 本件是**派生镜像非真源**（PG 总账恒为裁判）；世代上界=代码常量 _MAX_GENERATIONS=2 封死（Owner 定版，峰值≈200MB 设计口径），_Slots 只有"服务代+在途加载代"两格→结构上无第三代并存面，禁历史槽/队列/逐条 LRU 等任何无界容器；刷新只允许"读时指纹比对 + single-flight"，禁 cron/Timer/sleep-loop/轮询线程（根宪法 §9.3）；水位探测恒现读（S4 §⑤ 不可缓存位：裁判不是客户）；PG 不可达不得把旧代伪装成真源——无代可服务或 LIBRAM_STRICT_FRESH=1 一律原样上抛，有旧代则记 degraded 旗+logger.warning；切换点唯一=_publish 的 serving 赋值（CPython 引用赋值原子，读路径免锁取快照）；整表单语句装载（autocommit 下单 SELECT 天然原子，禁拆多语句防跨语句撕裂代际）；对外行键=LEDGER_PROJECTION_COLUMNS（与 _SQL_LOOKUP 投影恒等，过滤器附加列不外泄）；写侧/Librarian 注入连接路径不经本件（S4 §⑤ 写侧校验禁读缓存）
# [MODIFY-GUARD] gate_id 不适用；上界常量变更=Owner 门位（资金外最高敏感=内存封度定版）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 真源可达性与直查逐字节一致：无代可服务时 DB 异常原样上抛；有代可服务时降级服务并在 cache_status().degraded 显式打标；世代越界抛 LedgerCacheOverflowError（结构性不可达，仅作上界断言）
# [TESTS] tests/library/test_ledger_cache.py
# [A_module] module_id=MOD-LIB-003 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 读侧进程内物化视图，随查询惰性建代（非常驻服务/非 daemon），无自建触发器
"""ledger_cache.py — 总账世代缓存（图书馆内存条战役 R1）：整表一代、至多两代并存。

形态=**进程内物化视图**（S2 §3.1 定位）：账本整表一次装载成不可变内存对象，读时
用 :func:`zephyr.library.ledger_fingerprint.read_ledger_fingerprint` 比水位——水位未变
即纯内存匹配（零账本数据 SQL），变了才 single-flight 重建并原子换代，旧代即时释放。

禁做的三件事（都是本役立过的判据）：
  1. 禁逐条淘汰/LRU/无界 dict——世代制天然有界（两格槽 + 常量封死）；
  2. 禁定时刷新/轮询线程——失效靠读时比对（根宪法 §9.3 事件触发对家）；
  3. 禁把水位探测本身缓存化——它是缓存层的裁判（S4 §⑤）。

Usage::

    from zephyr.library import ledger_cache

    rows = ledger_cache.search("margin_trading", 5)     # 命中即内存匹配
    ledger_cache.cache_status().degraded                 # 降级可见，不静默

# [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/ledger_cache.yaml
"""

from __future__ import annotations

import logging
import os
import threading
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any, Final

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection, release_depgraph_pg_connection
from zephyr.library.ledger_fingerprint import read_ledger_fingerprint
from zephyr.library.ledger_schema import _SQL_ENSURE_ASSETS, _SQL_LOOKUP
from zephyr.library.librarian import PgConnection
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

__all__: Final = [
    "CacheStatus",
    "LedgerFilters",
    "LedgerGeneration",
    "acquire_generation",
    "cache_enabled",
    "cache_status",
    "search",
]

#: Owner 定版上界（RULE-SSOT：行为常量留代码不入 YAML，防运行期被调大）。
#: 实测代体积见 S2 §2.2（44,963 行 × 投影列 = 36.5MB/代，构建 1.156s），两代并存在
#: 200MB 设计口径内；越界无第二道裁判——_Slots 只有两格，第三代并存结构性不可能。
_MAX_GENERATIONS: Final[int] = 2

#: 逃生开关（S2 §4.5 红蓝对照期）：=1 旁路缓存，直查真源。
ENV_DIRECT: Final[str] = "LIBRAM_DIRECT"
#: 严格新鲜度开关：=1 时任何降级态直接报错，绝不服务旧代（写侧/对账类消费者用）。
ENV_STRICT_FRESH: Final[str] = "LIBRAM_STRICT_FRESH"

#: 拼接模糊轴的分隔符：NUL 不可能出现在查询串里（psycopg2 拒 NUL 参数），
#: 故"三列拼串后 find"与"逐列 ILIKE"零伪命中，等价成立。
_NEEDLE_SEP: Final[str] = "\x00"
#: 模糊匹配三列（与 _SQL_LOOKUP 的 WHERE 面同轴：asset_id/home/title）。
_NEEDLE_COLUMNS: Final[tuple[str, ...]] = ("asset_id", "home", "title")
#: 过滤器专用附加列（只用于代内过滤，不出对外行）。
_FILTER_COLUMNS: Final[tuple[str, ...]] = ("owner_domain", "tags")

#: 整表装载 SQL（列集由 _SQL_LOOKUP 派生，见 _ledger_projection_columns；单语句原子）。
SQL_LEDGER_GENERATION_LOAD: Final[str] = """
SELECT {columns}
FROM lib_assets
ORDER BY asset_id
"""


class LedgerCacheOverflowError(RuntimeError):
    """世代数越界——结构性不可达（两格槽 + single-flight），保留为 Owner 上界的机械断言。"""


def _ddl_columns() -> frozenset[str]:
    """从 lib_assets DDL 常量解析真实列名集（投影解析的形状校验，防把 SQL 关键字当列）。"""
    body = _SQL_ENSURE_ASSETS.partition("(")[2].rpartition(")")[0]
    return frozenset(line.strip().split()[0].rstrip(",") for line in body.splitlines() if line.strip())


def _ledger_projection_columns() -> tuple[str, ...]:
    """投影列单源=_SQL_LOOKUP 常量首行（真源改列=缓存自动跟随，禁按 HEAD 写死——S4 §⑦缺口5）。"""
    header = next((line.strip() for line in _SQL_LOOKUP.splitlines() if line.strip()), "")
    columns = tuple(token.strip().rstrip(",") for token in header.split()[1:])
    if not columns or columns[0] != "asset_id" or not set(columns) <= _ddl_columns():
        raise ValueError(f"_SQL_LOOKUP 投影列解析失败（真源形状漂移）：{columns!r}")
    return columns


#: 对外行键集（与直查真源的 cursor.description 恒等）。
LEDGER_PROJECTION_COLUMNS: Final[tuple[str, ...]] = _ledger_projection_columns()
#: 装载列集 = 投影列 + 过滤器附加列。
_LOAD_COLUMNS: Final[tuple[str, ...]] = LEDGER_PROJECTION_COLUMNS + _FILTER_COLUMNS


@dataclass(frozen=True, slots=True)
class LedgerFilters:
    """T5 五轴组合过滤器（与 :meth:`Librarian.lookup` 关键字参数同义；dataclass 打包避参数蔓延）。"""

    kind: str | None = None
    owner_domain: str | None = None
    tags: tuple[str, ...] = ()
    status: str | None = None
    home_prefix: str | None = None


@dataclass(frozen=True, slots=True)
class CacheStatus:
    """面板态（诊断/测试可见）：``degraded=True`` 即"服务的是旧代且未与真源核对成功"。"""

    version: int | None = None
    rows: int = 0
    degraded: bool = False
    reason: str = ""
    failures: int = 0
    live_generations: int = 0


@dataclass(frozen=True)
class LedgerGeneration:
    """一代账本：整表一次装载的不可变内存对象（换代的单位，永不原地修改）。

    不用 ``slots=True``：slots 类无 ``__weakref__``，测试与诊断将无法用 weakref 观测
    "旧代即时释放"（世代上界的唯一机械证据）。实例数恒 ≤2，字典开销可忽略。
    """

    version: int
    built_ts: datetime
    rows: tuple[dict[str, Any], ...]
    needles: tuple[str, ...]
    by_id: Mapping[str, dict[str, Any]]

    def __post_init__(self) -> None:
        if len(self.rows) != len(self.needles):
            raise ValueError("行集与匹配串必须等长（同源装载）")

    def match(self, term: str, limit: int, filters: LedgerFilters) -> list[dict[str, Any]]:
        """内存借阅：三列任一含词即命中，按装载序（=PG ``ORDER BY asset_id`` 序）取前 limit 条。"""
        if limit <= 0:
            return []
        needle = term.lower()
        hits: list[dict[str, Any]] = []
        for row, haystack in zip(self.rows, self.needles, strict=True):
            if needle and needle not in haystack:
                continue
            if not _passes_filters(row, filters):
                continue
            hits.append(_public_row(row))
            if len(hits) >= limit:
                break
        return hits

    def get(self, asset_id: str) -> dict[str, Any] | None:
        """精确索书号点查（代内 by_id 轴）；无此资产返回 None。"""
        row = self.by_id.get(asset_id)
        return None if row is None else _public_row(row)


def _passes_filters(row: dict[str, Any], filters: LedgerFilters) -> bool:
    """五轴过滤（语义对标 _SQL_LOOKUP_COMPOSED 拼接子句：kind/owner/status 精确、tags AND、home 前缀）。"""
    if filters.kind and row.get("kind") != filters.kind:
        return False
    if filters.owner_domain and row.get("owner_domain") != filters.owner_domain:
        return False
    if filters.status and row.get("status") != filters.status:
        return False
    if filters.home_prefix and not str(row.get("home") or "").startswith(filters.home_prefix):
        return False
    if filters.tags and not all(tag in (row.get("tags") or ()) for tag in filters.tags):
        return False
    return True


def _public_row(row: dict[str, Any]) -> dict[str, Any]:
    """对外行只暴露投影列（过滤器附加列不外泄，保持与直查真源逐键同形）。"""
    return {column: row[column] for column in LEDGER_PROJECTION_COLUMNS}


def _needle_of(row: dict[str, Any]) -> str:
    """装载期一次算好的小写拼接串（读期零加工：str.find 即 ILIKE 等价判定）。"""
    return _NEEDLE_SEP.join(str(row.get(column) or "") for column in _NEEDLE_COLUMNS).lower()


@dataclass
class _Slots:
    """世代槽：恰好两格（服务代 + 在途加载代水位号）——上界的结构性实现，无历史无队列。"""

    serving: LedgerGeneration | None = None
    loading_version: int | None = None

    def live_count(self) -> int:
        """当前存留世代数（服务代 + 正在构建的代）。"""
        return (1 if self.serving is not None else 0) + (1 if self.loading_version is not None else 0)


#: single-flight：失效瞬间只有 1 个线程进真源建代，其余在锁外等锁后走双检复用。
_BUILD_LOCK = threading.Lock()
_SLOTS = _Slots()
_STATUS = CacheStatus()


def _env_on(name: str) -> bool:
    """行为旗读取（非密钥件，值面为逃生开关；出厂默认恒=关，翻转属 Owner 门位）。"""
    return (os.environ.get(name) or "").strip().lower() in {"1", "true", "yes", "on"}


def cache_enabled() -> bool:
    """缓存总开关：``LIBRAM_DIRECT=1`` 旁路（直查真源，红蓝对照/故障逃生用）。"""
    return not _env_on(ENV_DIRECT)


def cache_status() -> CacheStatus:
    """面板态快照（含 degraded 旗与常驻世代数）——降级永不静默。"""
    return replace(_STATUS, live_generations=_SLOTS.live_count())


@contextmanager
def _borrow_connection() -> Iterator[PgConnection]:
    """池化借还（连接唯一入口 :func:`get_depgraph_pg_connection`，禁裸连；用毕**归还**而非 close）。

    短借短还：建代是一次 SELECT 的时间，不占死池槽（§5.64.1 池耗尽前科，S2 §3.4）。
    """
    conn = get_depgraph_pg_connection()
    try:
        yield conn  # type: ignore[misc]
    finally:
        release_depgraph_pg_connection(conn)


def _live_version() -> int:
    """现读水位（唯一失效判据来源）：永不缓存，见 ledger_fingerprint 件头 INVARIANTS。"""
    with _borrow_connection() as conn:
        return read_ledger_fingerprint(conn)


def _load_rows() -> tuple[dict[str, Any], ...]:
    """整表单语句装载（列集由 _SQL_LOOKUP 派生 + 过滤器附加列）。"""
    sql = SQL_LEDGER_GENERATION_LOAD.format(columns=", ".join(_LOAD_COLUMNS))
    with _borrow_connection() as conn, conn.cursor() as cur:
        cur.execute(sql)
        columns = [d[0] for d in cur.description]
        return tuple(dict(zip(columns, row, strict=True)) for row in cur.fetchall())


def _build_generation(version: int) -> LedgerGeneration:
    """装载一代（唯一建代点）：行集 + 匹配串 + 索书号索引，一次算好后不再修改。"""
    rows = _load_rows()
    return LedgerGeneration(
        version=version,
        built_ts=now_utc(),
        rows=rows,
        needles=tuple(_needle_of(row) for row in rows),
        by_id={str(row["asset_id"]): row for row in rows},
    )


def _mark_fresh(gen: LedgerGeneration) -> None:
    global _STATUS
    _STATUS = replace(_STATUS, version=gen.version, rows=len(gen.rows), degraded=False, reason="", failures=0)


def _mark_degraded(gen: LedgerGeneration, reason: str) -> None:
    global _STATUS
    _STATUS = replace(
        _STATUS,
        version=gen.version,
        rows=len(gen.rows),
        degraded=True,
        reason=reason,
        failures=_STATUS.failures + 1,
    )


def _publish(fresh: LedgerGeneration) -> None:
    """原子切换点（唯一 serving rebinding 处）：旧代引用在此归零，出栈即即时释放。"""
    previous = _SLOTS.serving
    _SLOTS.serving = fresh
    _SLOTS.loading_version = None
    logger.info(
        "账本世代切换: %s -> %s（旧代 %s 行已释放，常驻 %s 代）",
        previous.version if previous else "-",
        fresh.version,
        len(previous.rows) if previous else 0,
        _SLOTS.live_count(),
    )


def _serve_degraded(reason: str, exc: BaseException) -> LedgerGeneration:
    """真源不可达的处置：无代可服务/严格新鲜度 ⇒ 原样上抛；否则显式打降级标后服务旧代。"""
    serving = _SLOTS.serving
    if serving is None or _env_on(ENV_STRICT_FRESH):
        raise exc
    _mark_degraded(serving, reason)
    logger.warning(
        "图书馆世代缓存降级服务旧代 v%s（%s 行，原因=%s，连续失败 %s 次）；真源不可达期间勿据此判新鲜",
        serving.version,
        len(serving.rows),
        reason,
        _STATUS.failures,
        exc_info=exc,
    )
    return serving


def _rebuild(live_version: int) -> LedgerGeneration:
    """single-flight 重建：锁内二次校验 → 上界断言 → 旁路建代 → 原子换代。"""
    with _BUILD_LOCK:
        current = _SLOTS.serving
        if current is not None and current.version == live_version:
            return current  # 前序持锁线程已建好：其余请求者零重复加载
        if _SLOTS.live_count() + 1 > _MAX_GENERATIONS:
            raise LedgerCacheOverflowError(
                f"世代数将越界（live={_SLOTS.live_count()} +1 > _MAX_GENERATIONS={_MAX_GENERATIONS}）"
            )
        _SLOTS.loading_version = live_version
        try:
            fresh = _build_generation(live_version)
        except Exception as exc:  # noqa: BLE001 — 建代失败不触碰服务代（切换前失败=天然无损）
            _SLOTS.loading_version = None
            return _serve_degraded("generation_build_failed", exc)
        _publish(fresh)
        _mark_fresh(fresh)
        return fresh


def acquire_generation() -> LedgerGeneration:
    """取可服务世代：读时水位比对，等值即复用（零账本数据 SQL），不等才 single-flight 重建。"""
    try:
        live_version = _live_version()
    except Exception as exc:  # noqa: BLE001 — 水位读失败走降级处置（S2 §4.3 表首行）
        return _serve_degraded("fingerprint_read_failed", exc)
    serving = _SLOTS.serving
    if serving is not None and serving.version == live_version:
        _mark_fresh(serving)
        return serving
    return _rebuild(live_version)


def search(term: str, limit: int, filters: LedgerFilters | None = None) -> list[dict[str, Any]]:
    """借阅查询面（本役主交付）：命中即内存匹配，带五轴过滤器同样服务。"""
    return acquire_generation().match(term, limit, filters or LedgerFilters())


def _reset_state() -> None:
    """测试/诊断专用复位（生产路径禁调：失效由读时水位比对自动跟上，无 invalidate 钩子）。"""
    global _STATUS
    _SLOTS.serving = None
    _SLOTS.loading_version = None
    _STATUS = CacheStatus()
