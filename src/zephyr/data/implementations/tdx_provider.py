# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.tdx_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] mootdx SDK (Quotes.factory/index_bars/get_stock_list_in_sector); zephyr.data.ch_reader; zephyr.data.table_registry
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] bestip自动选最快服务器；单线程串行；板块K线(1d/5m/1m等全周期)+成分股；无板块分笔Tick；880xxx通过TCP直连盘中实时获取分钟K线(不依赖tdx客户端盘后下载)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 异常->yield FetchResult(error=str)
# [TESTS] tests/zephyr/data/test_providers.py::TestTDXProvider
# [A_module] module_id=MOD-GOV-tdx_provider | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""通达信数据源 Provider 实现（MOD-L00-004 §4.3）。

封装 mootdx SDK，继承 IngestProviderBase。
- bestip 自动选最快服务器
- 单线程串行
- 板块指数 K 线（880xxx，TCP 直连盘中实时）
- **无板块分笔 Tick**（仅 K 线）
- 当前能力：kline_sector（板块指数K线）

关键设计：
- connect() 用 Quotes.factory(market='std') 创建客户端，bestip 自动选择
- fetch() 调用 client.index_bars / client.get_stock_list_in_sector
"""

from __future__ import annotations

import datetime
import logging
import time
from typing import Iterator

from ..policy_registry import SourcePolicy
from ..provider_base import (
    CapabilityContract,
    FetchPayload,
    FetchResult,
    IngestProviderBase,
    IngestProviderMeta,
)
from ..table_registry import get_registry

log = logging.getLogger(__name__)

# Phase 5: 表名从 business_data_categories.yaml 真源派生（裁定 #ARCH-CH-024）
# _TBL_INDUSTRY_CLASS 已弃用（#ARCH-CH-INDUSTRY-CLASS-MIGRATE：tdx block() 语义错配，capability 先迁 ifind，2026-08-14 退役后由 tushare 承担）
_TBL_KLINE_SECTOR = get_registry().table("market_sector_kline")
_TBL_SECTOR_CONSTITUENT = get_registry().table("market_sector_constituent_880")

# bestip 可能选到不支持历史K线的服务器（实测 218.6.170.47:7709 的
# bars/index_bars 返回0行，TCP通但不响应历史K线请求）。
# 保留已知可靠服务器列表，bestip 验证失败时回退。
_RELIABLE_SERVERS = [
    ("115.238.56.198", 7709),
    ("115.238.90.165", 7709),
    ("117.184.140.156", 7709),
    ("59.173.18.140", 7709),
    ("218.75.126.9", 7709),
    ("221.231.141.60", 7709),
]

# 880xxx 板块指数K线周期 → mootdx frequency 映射
# mootdx index_bars frequency: 0=5min 1=15min 2=30m 3=1hour 7=1min 9=日线
_PERIOD_TO_FREQ = {
    "1d": 9,
    "5m": 0,
    "1m": 7,
    "15m": 1,
    "30m": 2,
    "60m": 3,
}
_MARKET_SH = 1  # 880xxx 板块指数归属沪市


def _patch_mootdx_to_data_coerce() -> None:
    """一次性 patch mootdx.utils.to_data，让 pd.to_datetime 用 errors='coerce'。

    根因：mootdx.utils.to_data() 无条件调用 ``pd.to_datetime(result.datetime)``，
    当 mootdx 偶发返回 ``"2004-00-00 00:00"`` 等无效日期（月/日=00）时，
    默认 ``errors='raise'`` 抛 ``ValueError: month must be in 1..12``，
    导致整个板块 K 线数据丢失（拿不到任何行，连有效行也丢）。

    修复：替换 to_data 为安全版本，``pd.to_datetime`` 加 ``errors='coerce'``，
    无效日期变 NaT（仅影响 index，不修改 datetime 列原值），
    由 ``_build_sector_kline_rows`` 的 strptime 校验过滤掉脏日期行。

    注意：不仅 patch ``mootdx.utils.to_data``，还要 patch 所有已加载模块中
    通过 ``from mootdx.utils import to_data`` 导入的本地引用（如 mootdx.quotes），
    否则那些模块仍会调用旧版本的 to_data。

    影响范围：所有 mootdx 内部的 to_data 调用；
    不影响项目其他模块的 ``pd.to_datetime`` 调用。
    mootdx 未安装时静默跳过（不影响模块加载）。
    """
    try:
        import mootdx.utils as mu
        import pandas as pd
        from pandas import DataFrame
    except ImportError:
        return  # mootdx 未安装，静默跳过

    def _safe_to_data(v, **kwargs):
        """to_data 安全版：to_datetime 用 errors='coerce'。

        逻辑与原版 mootdx.utils.to_data 一致，仅 to_datetime 调用加 coerce。
        若 mootdx 升级 to_data 新增列处理，需同步更新此处。
        """
        symbol = kwargs.get("symbol")
        adjust = kwargs.get("adjust", "").lower()

        if adjust in ("01", "qfq", "before"):
            adjust = "qfq"
        elif adjust in ("02", "hfq", "after"):
            adjust = "hfq"
        else:
            adjust = None

        if not isinstance(v, DataFrame) and not v:
            return pd.DataFrame(data=None)

        if isinstance(v, DataFrame):
            result = v
        elif isinstance(v, list):
            result = pd.DataFrame(data=v) if len(v) else None
        elif isinstance(v, dict):
            result = pd.DataFrame(data=[v])
        else:
            result = pd.DataFrame(data=[])

        if result is None or result.empty:
            return result if result is not None else pd.DataFrame()

        # 关键修复：errors='coerce' 代替默认 'raise'
        if "datetime" in result.columns:
            result.index = pd.to_datetime(result.datetime, errors="coerce")
        if "date" in result.columns:
            result.index = pd.to_datetime(result.date, errors="coerce")

        if "vol" in result.columns:
            result["volume"] = result.vol

        if adjust and adjust in ("qfq", "hfq") and symbol:
            from mootdx.utils.adjust import to_adjust

            result = to_adjust(result, symbol=symbol, adjust=adjust)

        return result

    # Patch 1: 替换 mootdx.utils.to_data
    mu.to_data = _safe_to_data

    # Patch 2: 替换所有已加载模块中对 to_data 的本地引用
    # （mootdx.quotes 等模块用 `from mootdx.utils import to_data` 导入，
    #  会在模块命名空间创建本地变量，必须同步替换）
    import sys

    for _mod_name, _mod in sys.modules.items():
        if _mod_name.startswith("mootdx.") and _mod is not None:
            try:
                if hasattr(_mod, "to_data") and _mod.to_data is not _safe_to_data:
                    _mod.to_data = _safe_to_data
            except Exception:
                pass

    log.info("mootdx.utils.to_data 已 patch 为 safe 版本（to_datetime errors='coerce'，含全模块引用替换）")


_patch_mootdx_to_data_coerce()


class TDXProvider(IngestProviderBase):
    """通达信数据源 Provider。

    bestip 自动选服务器、single_thread 线程安全模型。
    已知问题：单线程；无板块分笔 Tick。
    """

    source_name: str = "tdx"
    meta: IngestProviderMeta = IngestProviderMeta(
        name="tdx",
        display_name="通达信",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="single_thread",
        rate_limit_default=0,
        capabilities=[
            # "industry_class" 已弃用（#ARCH-CH-INDUSTRY-CLASS-MIGRATE）：
            # tdx block() 产出板块成分股，与 industry_class 表（股票→申万行业）语义错配，
            # 该 capability 现由 tushare_provider 承担（原 ifind i问财方案已随源退役）。
            CapabilityContract("kline_sector", supports_symbols_null=True),
        ],
        known_issues=["单线程串行", "无板块分笔Tick", "需bestip选最快服务器"],
    )

    # ---- 生命周期 ----

    def connect(self) -> None:
        """建立连接：用 mootdx Quotes.factory 创建客户端。

        bestip 自动选服务器，但部分服务器不支持历史K线查询（实测
        218.6.170.47:7709 的 bars/index_bars 返回0行）。连接后验证
        K线能力，失败则回退到已知可靠服务器。
        """
        from mootdx.quotes import Quotes

        self._client = Quotes.factory(market="std")
        if self._verify_kline():
            self._connected = True
            self._log.info("通达信已连接（bestip 自动选择）")
            return
        self._log.warning("bestip 服务器不支持K线查询，尝试回退服务器")
        for ip, port in _RELIABLE_SERVERS:
            self._client = Quotes.factory(market="std", bestip=False, server=(ip, port))
            if self._verify_kline():
                self._connected = True
                self._log.info(f"通达信已连接（回退到 {ip}:{port}）")
                return
        raise RuntimeError("所有服务器均无法获取K线数据")

    def health_check(self) -> bool:
        """探活：验证 client 可用且服务器支持K线查询。"""
        if not self._connected or self._client is None:
            return False
        return self._verify_kline()

    def _verify_kline(self) -> bool:
        """验证服务器支持历史K线查询（取1根浦发银行日线确认）。"""
        try:
            bars = self._client.bars(symbol="600000", frequency=9, start=0, offset=1)
            return bars is not None and not bars.empty
        except Exception:  # noqa: BLE001
            return False

    def disconnect(self) -> None:
        """断开连接：关闭 client。"""
        if self._client is not None:
            try:
                close = getattr(self._client, "close", None)
                if close:
                    close()
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.warning(f"通达信关闭异常: {e}")
        self._client = None
        self._connected = False
        self._log.info("通达信已断开")

    # ---- 拉取入口 ----

    def fetch(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """按 payload.extra["capability"] 路由到具体获取方法。"""
        if not self._connected or self._client is None:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error="tdx 未连接",
            )
            return

        capability = (payload.extra or {}).get("capability")
        if capability == "kline_sector":
            yield from self._fetch_kline_sector(payload, policy)
        else:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error=f"unsupported capability: {capability}",
            )

    # ---- 板块指数K线 ----
    # 注：原 _fetch_industry_class（板块分类，client.block）已弃用
    # （#ARCH-CH-INDUSTRY-CLASS-MIGRATE）——tdx block() 产出板块成分股与
    # industry_class 表语义错配，该 capability 现由 tushare_provider 承担。

    @staticmethod
    def _resolve_frequency(extra) -> tuple[int, str]:
        """从 payload.extra 解析 period → mootdx frequency。

        period 默认 "1d"（日线）。支持 1d/5m/1m/15m/30m/60m。
        """
        period = (extra or {}).get("period", "1d")
        return _PERIOD_TO_FREQ.get(period, 9), period

    @staticmethod
    def _resolve_sector_symbols() -> list[str]:
        """symbols=None 时从 sector_constituent 表获取全部板块代码。

        与 sector_snapshot_collector._get_all_sector_codes 同模式。
        治本（2026-08-17 AI-04 审计）：纯 SELECT 改走 ch_reader 只读路径
        （reader 账号 + FINAL 去重），原裸 clickhouse_driver.Client 违反
        DatabaseService 访问协议与 read_only 安全约束。
        """
        from .. import ch_reader

        tsv = ch_reader.query(f"SELECT DISTINCT sector_code FROM {_TBL_SECTOR_CONSTITUENT} ORDER BY sector_code")  # noqa: bare-sql  存量参数化查询/动态标识符，format重排伪新增（§5.160.2集中化专项另列）
        if not tsv or not tsv.strip():
            # 区分"CH 不可达"与"表确实为空"：ch_reader 失败静默返回空串，
            # 探活仍为空 → CH 不可达 → 显式抛错（防 0 行假成功掩盖故障，
            # 对齐原裸 Client 连接失败即抛错的 fail-visible 语义）
            if not (ch_reader.query("SELECT 1") or "").strip():
                raise RuntimeError("ClickHouse 不可达（sector_constituent 探活无响应）")
            return []
        return [line.strip() for line in tsv.strip().split("\n") if line.strip()]

    def _fetch_kline_sector(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """获取板块指数K线（client.index_bars）。

        mootdx index_bars(symbol, frequency, market, start, offset) 返回 DataFrame。
        frequency: 9=日线 0=5min 7=1min 1=15min 2=30min 3=1hour。
        通过 payload.extra["period"] 配置周期，默认 "1d"。
        symbols=None 时自动从 sector_constituent 表获取全部880xxx板块代码。
        880xxx 板块指数通过 TCP 直连盘中实时获取，不依赖 tdx 客户端盘后下载。
        """
        table = payload.table or _TBL_KLINE_SECTOR
        frequency, period = self._resolve_frequency(payload.extra)
        count = int(payload.extra.get("count", 100)) if payload.extra else 100
        # 分钟K线写入 kline_sector_intraday 表（DateTime + period 列），
        # 日线写入 kline_sector 表（Date，无 period 列）
        if period != "1d":
            columns = ["trade_date", "code", "period", "open", "high", "low", "close", "volume", "amount"]
        else:
            columns = ["trade_date", "code", "open", "high", "low", "close", "volume", "amount"]
        symbols = payload.symbols or []
        if not symbols:
            symbols = self._resolve_sector_symbols()
            self._log.info(f"symbols=None，从 sector_constituent 解析 {len(symbols)} 只板块")

        for code in symbols:
            t0 = time.time()
            try:
                raw_code = self._extract_raw_code(code)

                bars = self._call_with_policy(
                    self._client.index_bars,
                    policy,
                    symbol=raw_code,
                    frequency=frequency,
                    market=_MARKET_SH,
                    start=0,
                    offset=count,
                )
                rows: list[tuple] = []
                if bars is not None and not bars.empty:
                    rows = self._build_sector_kline_rows(bars, code, period)
                self._log.info(f"板块K线 {code} ({period}): {len(rows)} 行")
                if rows:
                    last_key = datetime.date.today().isoformat() if period == "1d" else rows[-1][0]
                    yield FetchResult(
                        table=table,
                        columns=columns,
                        rows=rows,
                        last_key=last_key,
                        elapsed_sec=time.time() - t0,  # noqa: m46-time — elapsed 差值计时与时区无关（性能埋点）
                    )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.warning(f"板块K线 {code} ({period}) 获取失败: {e}")
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=[],
                    last_key="",
                    elapsed_sec=time.time() - t0,  # noqa: m46-time — elapsed 差值计时与时区无关（性能埋点）
                    error=str(e),
                )

    @staticmethod
    def _extract_raw_code(code: str) -> str:
        """提取纯代码：sh.000001 -> 000001, 881101.TI -> 881101。"""
        if "." not in code:
            return code
        return code.split(".")[0] if code[0].isdigit() else code.split(".")[-1]

    @staticmethod
    def _build_sector_kline_rows(bars, code: str, period: str = "1d") -> list:
        """从 bars DataFrame 构造板块K线行列表。

        日线 datetime 格式 "2026-02-06 15:00"，截取日期部分。
        分钟线保留完整时间戳 "2026-02-06 15:00:00"，并在 code 后插入 period 字段。

        脏日期过滤：mootdx 偶发返回 "2004-00-00 00:00" 等无效日期（月/日=00），
        ClickHouse DateTime 列会拒绝写入，此处提前过滤跳过。
        """
        rows = []
        for _, bar in bars.iterrows():
            dt = str(bar.get("datetime", ""))
            # 脏日期过滤：mootdx 偶发返回 "2004-00-00 00:00"（月/日=00 非法）
            try:
                if len(dt) >= 19:
                    datetime.datetime.strptime(dt[:19], "%Y-%m-%d %H:%M:%S")
                elif len(dt) >= 10:
                    datetime.datetime.strptime(dt[:10], "%Y-%m-%d")
                else:
                    continue
            except ValueError:
                continue
            trade_date = dt if period != "1d" else (dt[:10] if len(dt) >= 10 else dt)
            ohlcv = (
                float(bar.get("open", 0) or 0),
                float(bar.get("high", 0) or 0),
                float(bar.get("low", 0) or 0),
                float(bar.get("close", 0) or 0),
                int(bar.get("vol", 0) or 0),
                float(bar.get("amount", 0) or 0),
            )
            if period != "1d":
                rows.append((trade_date, code, period) + ohlcv)
            else:
                rows.append((trade_date, code) + ohlcv)
        return rows
