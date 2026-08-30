# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.crypto_universe_selector
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.shared.security.secrets
# [CONSUMERS] universe_registry UNI-CRYPTO-001 Phase 2 扩池（候选：币版回测/信号装配层）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 条件宇宙=市值前 N（默认 20）；输出条目必带 source 留痕；稳定币/锚定资产默认排除（不可作为 alpha 交易标的）；CMC 不可用→静态配置兜底（degraded=True）；纯函数无副作用不写 CH
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/95_crypto_system_blueprint.md §3.1 条件选币；94号 §9 Q2（Phase 2 扩市值前 20）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] top_n<=0 → ValueError；CMC API 异常/载荷非法 → 静态配置兜底（degraded=True 不抛）
# [TESTS] tests/zephyr/data/test_crypto_universe_selector.py
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
条件选币（市值前 20 框架）——95号 §3.1 / 94号 §9 Q2 / CAND-CRYPTO-007 Phase 2 扩池。

条件宇宙=市值前 N（默认 20），框架共用 A股 universe 选择骨架语义
（frozen dataclass 结果契约 + 依赖注入 + 降级兜底 + source 留痕），宇宙独立
（crypto 市场实例，与 A股池物理隔离）。

数据源双路径（与 sentiment_panel_provider CMC 口径对齐）：
- CoinMarketCap 免费 API（/v1/cryptocurrency/listings/latest，需 CMC_API_KEY，
  free basic tier）——主路径，真实市值排名。
- 静态配置快照（DEFAULT_STATIC_UNIVERSE 或注入 static_universe）——兜底路径，
  无 key 或 CMC 异常时使用（degraded 留痕）。

输出：选币结果列表（symbol, market_cap_rank, source），稳定币/锚定资产
（USDT/USDC/WBTC/stETH 等）默认排除——与 A股框架 filter_rules（剔 ST/退市）
同构，宇宙是"可交易标的集"非"市值榜单"。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: top_n 参数
#   fields: 参数 top_n（无注解）
#   code: crypto_universe_selector.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: api_key 参数
#   fields: 参数 api_key（无注解）
#   code: crypto_universe_selector.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: static_universe 参数
#   fields: 参数 static_universe（无注解）
#   code: crypto_universe_selector.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: exclude_symbols 参数
#   fields: 参数 exclude_symbols（无注解）
#   code: crypto_universe_selector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CryptoUniverseSelector
#   name_en: CryptoUniverseSelector
#   intro: 条件选币器（市值前 N 宇宙）。
#   desc: 条件选币器（市值前 N 宇宙）。 主路径 CoinMarketCap 免费 API；无 key 或 CMC 异常时静态配置兜底。 http_get 可注入（测试 mock，不依赖…；公共方法（定义序）: select；…
#   inputs: top_n api_key static_universe exclude_symbols http_get
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: CryptoUniverseSelector
#   downstream: universe_registry UNI-CRYPTO-001 Phase 2 扩池（候选：币版回测/信号装配层）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Callable, Final, Iterable

from zephyr.shared.security.secrets import get_secret_or_default

logger = logging.getLogger(__name__)

__all__: Final = [
    "DEFAULT_EXCLUDE_SYMBOLS",
    "DEFAULT_STATIC_UNIVERSE",
    "DEFAULT_TOP_N",
    "SOURCE_CMC",
    "SOURCE_STATIC",
    "CryptoUniverseEntry",
    "CryptoUniverseResult",
    "CryptoUniverseSelector",
]

# CoinMarketCap  listings 端点（免费 basic tier，需 API key；与 sentiment_panel_provider 同域名口径）
_CMC_LISTINGS_URL: Final = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

#: 数据来源标识（留痕用）
SOURCE_CMC: Final[str] = "coinmarketcap"
SOURCE_STATIC: Final[str] = "static_config"

#: 默认宇宙容量（94号 §9 Q2：Phase 2 扩市值前 20）
DEFAULT_TOP_N: Final = 20

#: 默认排除集：稳定币/锚定封装资产（市值榜单在列但不可作为 alpha 交易标的，
#: 与 A股 filter_rules 剔 ST/*ST 同构——宇宙=可交易标的集，非榜单照抄）
DEFAULT_EXCLUDE_SYMBOLS: Final = frozenset(
    {
        "USDT",
        "USDC",
        "DAI",
        "FDUSD",
        "USDE",
        "SUSDE",
        "USDS",
        "USD1",
        "WBTC",
        "WETH",
        "STETH",
        "WSTETH",
        "CBBTC",
        "LBTC",
        "BNSOL",
        "WBETH",
    }
)

#: 静态配置快照（可交易标的市值前 20，已剔除稳定币/锚定资产）。
#: 快照日期 2026-08，排名会漂移——仅作 CMC 不可用时的兜底宇宙，
#: 定期刷新职责归 Owner（与 UNI-CRYPTO-001 registry 条目联动）。
DEFAULT_STATIC_UNIVERSE: Final = (
    ("BTC", 1),
    ("ETH", 2),
    ("XRP", 3),
    ("BNB", 4),
    ("SOL", 5),
    ("DOGE", 6),
    ("TRX", 7),
    ("ADA", 8),
    ("HYPE", 9),
    ("LINK", 10),
    ("XLM", 11),
    ("SUI", 12),
    ("BCH", 13),
    ("AVAX", 14),
    ("LTC", 15),
    ("DOT", 16),
    ("UNI", 17),
    ("NEAR", 18),
    ("APT", 19),
    ("PEPE", 20),
)


@dataclass(frozen=True)
class CryptoUniverseEntry:
    """选币结果条目（输出单元）。

    symbol          标的符号（如 "BTC"）
    market_cap_rank 市值排名（1 起；CMC 路径=cmc_rank 全榜真实名次，
                    静态路径=快照内名次，source 字段消歧）
    source          数据来源（coinmarketcap / static_config）
    """

    symbol: str
    market_cap_rank: int
    source: str


@dataclass(frozen=True)
class CryptoUniverseResult:
    """选币结果（frozen 契约，JSON 可序列化）。

    degraded=True 表示 CMC 主路径失败后静态兜底（含 api_error 留痕）；
    无 key 直走静态配置是正常配置路径，degraded=False。
    """

    entries: tuple[CryptoUniverseEntry, ...] = ()
    top_n: int = DEFAULT_TOP_N
    source: str = SOURCE_STATIC
    as_of: str = ""
    degraded: bool = False
    api_error: str = ""


def _default_http_get(url: str, *, timeout: float, headers: dict, params: dict) -> Any:
    """默认 HTTP GET（requests 懒加载，模块加载不依赖 SDK 已安装）。"""
    import requests

    resp = requests.get(url, timeout=timeout, headers=headers, params=params)
    resp.raise_for_status()
    return resp


class CryptoUniverseSelector:
    """条件选币器（市值前 N 宇宙）。

    主路径 CoinMarketCap 免费 API；无 key 或 CMC 异常时静态配置兜底。
    http_get 可注入（测试 mock，不依赖网络）。
    """

    def __init__(
        self,
        top_n: int = DEFAULT_TOP_N,
        *,
        api_key: str | None = None,
        static_universe: Iterable[tuple[str, int]] | None = None,
        exclude_symbols: Iterable[str] | None = None,
        http_get: Callable[..., Any] | None = None,
    ) -> None:
        if top_n <= 0:
            raise ValueError(f"top_n 非法（须为正整数）: {top_n}")
        self.top_n = top_n
        # api_key 显式注入优先，缺省读 CMC_API_KEY 环境（secrets 统一入口，禁裸 os.getenv）
        self._api_key = api_key if api_key is not None else get_secret_or_default("CMC_API_KEY", "")
        self._static_universe = tuple(static_universe) if static_universe is not None else DEFAULT_STATIC_UNIVERSE
        self._exclude = frozenset(exclude_symbols) if exclude_symbols is not None else DEFAULT_EXCLUDE_SYMBOLS
        self._http_get = http_get if http_get is not None else _default_http_get

    def select(self) -> CryptoUniverseResult:
        """执行选币：CMC 主路径 → 静态兜底。返回结果必带 source/degraded 留痕。"""
        as_of = date.today().isoformat()
        if not self._api_key:
            logger.info("CMC_API_KEY 未配置，条件选币走静态配置宇宙（top_n=%d）", self.top_n)
            return self._static_result(as_of)
        try:
            entries = self._fetch_cmc_entries()
        except Exception as e:  # noqa: BLE001 — 兜底路径：任何 CMC 失败降级静态，不阻断宇宙构造
            logger.warning("CMC 选币主路径失败（%s），降级静态配置宇宙", e)
            return self._static_result(as_of, degraded=True, api_error=str(e))
        return CryptoUniverseResult(
            entries=entries,
            top_n=self.top_n,
            source=SOURCE_CMC,
            as_of=as_of,
            degraded=False,
        )

    # ---- 内部 ----

    def _static_result(self, as_of: str, *, degraded: bool = False, api_error: str = "") -> CryptoUniverseResult:
        """静态配置宇宙（兜底路径），按快照名次截断 top_n。"""
        entries = tuple(
            CryptoUniverseEntry(symbol=sym, market_cap_rank=rank, source=SOURCE_STATIC)
            for sym, rank in self._static_universe
            if sym not in self._exclude
        )[: self.top_n]
        return CryptoUniverseResult(
            entries=entries,
            top_n=self.top_n,
            source=SOURCE_STATIC,
            as_of=as_of,
            degraded=degraded,
            api_error=api_error,
        )

    def _fetch_cmc_entries(self) -> tuple[CryptoUniverseEntry, ...]:
        """CMC listings 主路径：按市值降序拉取 → 排除稳定币/锚定资产 → 截断 top_n。

        拉取量 = top_n + len(exclude)：覆盖"榜单前段被排除项占位"场景，
        保证排除后仍凑满 top_n 个可交易标的。
        载荷非法（缺 data / 非 list / 条目缺字段）→ ValueError 由 select 兜底降级。
        """
        resp = self._http_get(
            _CMC_LISTINGS_URL,
            timeout=30,
            headers={"X-CMC_PRO_API_KEY": self._api_key, "Accept": "application/json"},
            params={
                "limit": self.top_n + len(self._exclude),
                "sort": "market_cap",
                "sort_dir": "desc",
                "convert": "USD",
            },
        )
        payload = resp.json()
        status = payload.get("status", {}) if isinstance(payload, dict) else {}
        if status.get("error_code"):
            raise ValueError(f"CMC API 错误: {status.get('error_message', 'unknown')}")
        data = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(data, list):
            raise ValueError("CMC 载荷非法：缺 data 列表")
        entries: list[CryptoUniverseEntry] = []
        for item in data:
            symbol = item.get("symbol")
            rank = item.get("cmc_rank")
            if not symbol or not isinstance(rank, int):
                raise ValueError(f"CMC 条目非法（缺 symbol/cmc_rank）: {item!r}")
            if symbol in self._exclude:
                continue
            entries.append(CryptoUniverseEntry(symbol=symbol, market_cap_rank=rank, source=SOURCE_CMC))
            if len(entries) >= self.top_n:
                break
        if not entries:
            raise ValueError("CMC 返回空宇宙（排除后无标的）")
        return tuple(entries)
