#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §crypto
# [MODULE] zephyr.data.implementations.crypto_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.provider_base; zephyr.data.ch_reader; zephyr.data.ch_writer; stdlib(urllib/json/csv)
# [CONSUMERS] zephyr.data.scheduler（source=crypto_binance）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 免费公开源匿名只读（binance.vision 币安官方公开数据镜像，无 key 无签名；Gate.io 登记备源未接线）；影子只记账不进决策链路（Owner 2026-09-11 免费影子模式裁定，禁接 trading_decision_map/TDM 消费方/broker）；宇宙口径=24h quote_volume Top-50 USDT 现货对采集时点快照（剔稳定币对，BTC 恒入）+ETHBTC 原生汇率对；幂等=ReplacingMergeTree 重复键后台合并可重放；FAIL-VISIBLE 失败不造数不占位；shadow_version 逻辑变更须升版本防 track record 混轨
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 行情源不可达->FetchResult.error（集成器标准重试/告警管道）；CH 读数失败->FetchResult.error；数据不足->insufficient_history 行（FAIL-VISIBLE 留痕）退出正常
# [TESTS] tests/zephyr/data/test_crypto_provider.py
# [TTL] permanent
"""crypto_provider.py — 币圈数据 Provider（免费影子 MVP 数据层，source=crypto_binance）。

真源：95 号蓝图 §一 1.1"币安主+OKX 备"+ Owner 2026-09-11 免费影子模式裁定。
网络实测（2026-09-11/12）：OKX 公开 API 全域 DNS 阻断 → 换道 binance.vision（币安官方公开
数据镜像，免费无 key，HTTP 200 实测可达）；Gate.io 公开 API 可达，登记备源 Phase 2 接线。

两个 capability（fetch 按 payload.extra["capability"] 路由，baostock 先例）：
  crypto_kline_daily  binance.vision 拉日线 → c1_market.crypto_kline_daily
                      （宇宙 Top-50 快照+ETHBTC 汇率对，ReplacingMergeTree 幂等重放）
  crypto_shadow_gate  读 crypto_kline_daily 表内数据直判 → c1_market.crypto_shadow_gate
                      （shadow_tier 五档：trend/altseason/tighten/insufficient_history/sentiment_only；
                      佐证列=MA200 十日斜率/ETHBTC 及其 MA20/恐惧贪婪指数 alternative.me 免费源）

历史：scripts/data/crypto_kline_collector.py + crypto_shadow_judge.py 两 CLI 的逻辑正身
（2026-09-12 Owner 裁定转正 src 正规军编制+接入数据源集成器）。
"""
from __future__ import annotations

import csv
import datetime
import json
import os
import threading
import time
import urllib.parse
import urllib.request
from typing import Final, Iterator

from zephyr.data import ch_reader
from zephyr.data.provider_base import (
    CapabilityContract,
    FetchPayload,
    FetchResult,
    IngestProviderBase,
    IngestProviderMeta,
)
from zephyr.shared.security.secrets import get_service_secret

_BASE_URL = "https://data-api.binance.vision"
_TICKER_PATH = "/api/v3/ticker/24hr"
_KLINES_PATH = "/api/v3/klines"
_FNG_URL = "https://api.alternative.me/fng/"

# 表名经 TableRegistry 真源派生（#ARCH-CH-024：禁硬编码；category_id 注册于 business_data_categories.yaml）
from zephyr.data.table_registry import get_registry

_TR = get_registry()
KLINE_TABLE = _TR.table("crypto_kline_daily")
GATE_TABLE = _TR.table("crypto_shadow_gate")
KLINE_COLUMNS: Final[list[str]] = [
    "trade_date", "symbol", "base_asset", "open", "high", "low", "close", "volume",
    "quote_volume", "trades", "is_universe_eligible", "universe_rank", "data_source", "quality_flag",
]
GATE_COLUMNS: Final[list[str]] = [
    "trade_date", "btc_close", "ma200", "ma_slope_10d", "altseason_ratio", "altseason_universe",
    "eth_btc_ratio", "eth_btc_ratio_ma20", "fng_value", "shadow_tier", "shadow_reason",
    "sentiment_only", "shadow_version",
]
DATA_SOURCE = "binance_vision"
SHADOW_VERSION = "v0.1"

# 宇宙口径：稳定币计价对剔除清单（base 资产为稳定币 → 非"山寨"、污染 altseason 比率）
# 2026-09-12 实测补丁：首跑 Top-50 出现 RLUSD（Ripple USD 稳定币）上榜，补录；残余小众稳定币披露在报告
_STABLE_BASES: Final[frozenset[str]] = frozenset({
    "USDC", "FDUSD", "TUSD", "DAI", "USDP", "EURI", "AEUR", "USD1",
    "USDE", "BUSD", "PYUSD", "FRAX", "LUSD", "GHO", "SUSD", "USDS",
    "RLUSD", "USDF", "XUSD", "USDG", "EUR", "USD",
})
_UNIVERSE_SIZE = 50
_RETRY = 3
_BACKOFF = 2.0
_PAGE = 1000  # 币安 klines 单页上限
_RATE_SLEEP = 0.35  # 免费公开源保守限频（对齐 sentiment_panel_provider INVARIANTS 精神）
_MANIFEST_PATH = os.path.join("data", "crypto", "universe_manifest.csv")
_MANIFEST_HEADER: Final[list[str]] = ["snapshot_date", "universe_rank", "symbol", "quote_volume_usdt", "source"]

_MA_WINDOW = 200
_SLOPE_LOOKBACK = 10
_ALTSEASON_WINDOW = 90
_ALTSEASON_THRESHOLD = 0.75
_MIN_UNIVERSE = 20  # 比率窗口内不足 20 对 → insufficient_history（防小样本伪档）


def _last_completed_utc_day() -> datetime.date:
    """最近一个完整 UTC 日（当前未收盘 K 线不入库，防 partial candle 污染）。"""
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    return (now_utc - datetime.timedelta(days=1)).date()


class CryptoProvider(IngestProviderBase):
    """币圈 Provider——binance.vision 日线采集 + C-L1 影子判定（只记账不进决策）。"""

    source_name: str = "crypto_binance"
    # CAP-CONSISTENCY 门禁要求（#ARCH-CH-022）：fetch 路由能力集必须与 meta.capabilities
    # 声明集一致——_fetch_kline_daily/_fetch_shadow_gate 双路由对应双声明（2026-09-12 补）
    meta: IngestProviderMeta = IngestProviderMeta(
        name="crypto_binance",
        display_name="币圈免费影子（binance.vision）",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="stateless",
        rate_limit_default=170,
        capabilities=[
            CapabilityContract("crypto_kline_daily", supports_symbols_null=True),
            CapabilityContract("crypto_shadow_gate", supports_symbols_null=True),
        ],
    )

    def connect(self) -> None:
        """HTTP 无状态源，无连接语义。"""

    def disconnect(self) -> None:
        """无连接语义。"""

    def health_check(self) -> bool:
        try:
            return self._http_get_json(_BASE_URL + "/api/v3/ping") == {}
        except Exception:  # noqa: BLE001 — 健康探测失败即不可用
            return False

    def capability_contracts(self) -> list[CapabilityContract]:
        return [
            CapabilityContract("crypto_kline_daily", supports_symbols_null=True),
            CapabilityContract("crypto_shadow_gate", supports_symbols_null=True),
        ]

    def fetch(self, payload: FetchPayload, policy) -> Iterator[FetchResult]:
        """按 payload.extra["capability"] 路由（baostock 先例）。"""
        capability = (payload.extra or {}).get("capability")
        if capability == "crypto_kline_daily":
            yield from self._fetch_kline_daily(payload)
        elif capability == "crypto_shadow_gate":
            yield from self._fetch_shadow_gate(payload)
        else:
            yield FetchResult(
                table=payload.table, columns=[], rows=[], last_key="", elapsed_sec=0.0,
                error=f"unsupported capability: {capability}",
            )

    # ------------------------------------------------------------ HTTP 基础

    @staticmethod
    def _http_get_json(url: str, params: dict | None = None) -> object:
        """GET 公开端点 → JSON；3 次重试指数退避；失败抛 RuntimeError（FAIL-VISIBLE）。"""
        if params:
            url = url + "?" + urllib.parse.urlencode(params)
        last_err: Exception | None = None
        for attempt in range(1, _RETRY + 1):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (ZephyrAlpha-shadow-collector)"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except Exception as e:  # noqa: BLE001 — 网络异常统一重试
                last_err = e
                print(f"[retry {attempt}/{_RETRY}] GET 失败: {type(e).__name__}: {e}")
                if attempt < _RETRY:
                    threading.Event().wait(_BACKOFF * attempt)  # 限频退避：Event().wait 语义等价可中断（provider_base 惯例，PERM-TRIGGER 防复发）
        raise RuntimeError(f"行情源不可达(连续 {_RETRY} 次失败,主源={_BASE_URL}): {last_err}")

    # ------------------------------------------------------------ 宇宙清单

    def build_universe(self) -> list[dict]:
        """24h quote_volume Top-50 USDT 现货对快照（剔除稳定币对，BTC 恒入）+ ETHBTC。"""
        tickers = self._http_get_json(_BASE_URL + _TICKER_PATH)
        candidates = []
        for t in tickers:
            symbol = t.get("symbol", "")
            if not symbol.endswith("USDT") or len(symbol) <= 4:
                continue
            base = symbol[: -len("USDT")]
            if base in _STABLE_BASES:
                # 杠杆代币（UP/DOWN/BULL/BEAR）不过滤：币安杠杆代币 2022-2023 已全部下架，
                # 且后缀匹配会误伤真山寨（实证：JUP 结尾 UP）
                continue
            try:
                qvol = float(t.get("quoteVolume", "0"))
            except ValueError:
                continue
            if qvol <= 0:
                continue
            candidates.append({"symbol": symbol, "base": base, "quote_volume": qvol})
        candidates.sort(key=lambda x: x["quote_volume"], reverse=True)
        top = candidates[:_UNIVERSE_SIZE]
        if not any(x["symbol"] == "BTCUSDT" for x in top):
            raise RuntimeError("BTCUSDT 未进入 Top-50(异常市场状态,FAIL-VISIBLE)")
        universe = [
            {"symbol": x["symbol"], "base": x["base"], "rank": i + 1, "quote_volume": x["quote_volume"]}
            for i, x in enumerate(top)
        ]
        # ETHBTC 原生汇率对（C-L1 ALT/BTC 汇率口径；rank=0 非宇宙成员，恒采）
        universe.append({"symbol": "ETHBTC", "base": "ETH", "rank": 0, "quote_volume": 0.0})
        return universe

    @staticmethod
    def append_manifest(universe: list[dict], snapshot_date: str) -> str:
        """宇宙清单快照追加落盘（清单来源口径留痕）。"""
        os.makedirs(os.path.dirname(_MANIFEST_PATH), exist_ok=True)
        new_file = not os.path.exists(_MANIFEST_PATH)
        with open(_MANIFEST_PATH, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new_file:
                w.writerow(_MANIFEST_HEADER)
            for u in universe:
                if u["rank"] == 0:
                    continue  # ETHBTC 汇率对非宇宙成员，不入清单
                w.writerow([snapshot_date, u["rank"], u["symbol"], f"{u['quote_volume']:.2f}", DATA_SOURCE])
        return _MANIFEST_PATH

    # ------------------------------------------------------------ K线抓取

    @staticmethod
    def fetch_klines(symbol: str, days: int, end_date: datetime.date) -> list[dict]:
        """抓取 [end_date-(days-1), end_date] 日线（自动翻页）；返回行字典列表。"""
        start_ms = int(
            datetime.datetime(end_date.year, end_date.month, end_date.day, tzinfo=datetime.timezone.utc).timestamp()
            * 1000
        ) - (days - 1) * 86_400_000
        end_ms = int(
            datetime.datetime(
                end_date.year, end_date.month, end_date.day, 23, 59, 59, tzinfo=datetime.timezone.utc
            ).timestamp()
            * 1000
        )
        rows: list[dict] = []
        cursor = start_ms
        while cursor <= end_ms:
            batch = CryptoProvider._http_get_json(
                _BASE_URL + _KLINES_PATH,
                {"symbol": symbol, "interval": "1d", "startTime": cursor, "endTime": end_ms, "limit": _PAGE},
            )
            if not batch:
                break
            for k in batch:
                d = datetime.datetime.fromtimestamp(int(k[0]) / 1000, tz=datetime.timezone.utc).date()
                if d > end_date:
                    continue
                rows.append(
                    {
                        "trade_date": d.isoformat(), "symbol": symbol,
                        "open": str(k[1]), "high": str(k[2]), "low": str(k[3]), "close": str(k[4]),
                        "volume": str(k[5]), "quote_volume": str(k[7]), "trades": str(k[8]),
                    }
                )
            next_cursor = int(batch[-1][0]) + 86_400_000
            if next_cursor <= cursor:
                break
            cursor = next_cursor
            threading.Event().wait(_RATE_SLEEP)  # 同上
            if len(batch) < _PAGE:
                break
        return rows

    @staticmethod
    def mark_universe(rows: list[dict], universe_symbols: set[str]) -> dict[tuple[str, str], tuple[int, int]]:
        """按各日期内实际 quote_volume 排名标注 eligible/rank（成分集合=采集时点快照）。ETHBTC 恒 0/0。"""
        universe_symbols = {s for s in universe_symbols if s != "ETHBTC"}
        by_date: dict[str, list[dict]] = {}
        for r in rows:
            if r["symbol"] in universe_symbols:
                by_date.setdefault(r["trade_date"], []).append(r)
        key_map: dict[tuple[str, str], tuple[int, int]] = {}
        for d, rs in by_date.items():
            rs.sort(key=lambda x: float(x["quote_volume"]), reverse=True)
            for i, r in enumerate(rs):
                key_map[(r["symbol"], d)] = (1, i + 1) if i < _UNIVERSE_SIZE else (0, 0)
        return key_map

    def _fetch_kline_daily(self, payload: FetchPayload) -> Iterator[FetchResult]:
        started = time.monotonic()
        lookback = int((payload.extra or {}).get("lookback_days", 5))
        end_date = _last_completed_utc_day()
        try:
            universe = self.build_universe()
        except RuntimeError as e:
            yield FetchResult(table=KLINE_TABLE, columns=[], rows=[], last_key="", elapsed_sec=0.0, error=str(e))
            return
        self.append_manifest(universe, end_date.isoformat())
        all_rows: list[dict] = []
        for u in universe:
            rows = self.fetch_klines(u["symbol"], lookback, end_date)
            for r in rows:
                r["base_asset"] = u["base"]
            all_rows.extend(rows)
            threading.Event().wait(_RATE_SLEEP)  # 同上
        if not all_rows:
            yield FetchResult(
                table=KLINE_TABLE, columns=[], rows=[], last_key="", elapsed_sec=time.monotonic() - started,
                error="零行抓取（行情源异常），拒绝写库（FAIL-VISIBLE）",
            )
            return
        key_map = self.mark_universe(all_rows, {u["symbol"] for u in universe})
        out_rows = []
        for r in all_rows:
            eligible, rank = key_map.get((r["symbol"], r["trade_date"]), (0, 0))
            out_rows.append((
                r["trade_date"], r["symbol"], r["base_asset"], r["open"], r["high"], r["low"],
                r["close"], r["volume"], r["quote_volume"], r["trades"],
                eligible, rank, DATA_SOURCE, 1,
            ))
        dates = sorted({r[0] for r in out_rows})
        yield FetchResult(
            table=KLINE_TABLE, columns=KLINE_COLUMNS, rows=out_rows, last_key=dates[-1],
            elapsed_sec=time.monotonic() - started,
        )

    # ------------------------------------------------------------ 影子判定

    @staticmethod
    def _query_rows(sql: str) -> list[list[str]]:
        out = ch_reader.query(sql)
        if out == "":
            raise RuntimeError(f"CH 查询失败（不可达或零结果无法区分，FAIL-VISIBLE）: {sql[:120]}")
        return [ln.split("\t") for ln in out.strip().split("\n") if ln]

    @staticmethod
    def _load_btc_series(end_date: datetime.date, need: int) -> list[tuple[datetime.date, float]]:
        rows = CryptoProvider._query_rows(
            f"SELECT trade_date, close FROM {KLINE_TABLE} FINAL "  # noqa: bare-sql  动态表名+日期参数化查询（KLINE_TABLE 常量拼接，ch_reader 通道），SQL 集中化另列
            f"WHERE symbol = 'BTCUSDT' AND trade_date <= '{end_date.isoformat()}' ORDER BY trade_date ASC"
        )

        series = [(datetime.date.fromisoformat(r[0]), float(r[1])) for r in rows]
        return series[-need:] if need else series

    @staticmethod
    def _load_universe_window(end_date: datetime.date) -> dict[str, list[tuple[datetime.date, float]]]:
        """加载全部宇宙成员（is_universe_eligible=1 或 ETHBTC）收盘序列（平铺查询 Python 分组）。"""
        rows = CryptoProvider._query_rows(
            f"SELECT symbol, trade_date, close FROM {KLINE_TABLE} FINAL "  # noqa: bare-sql  动态表名+日期参数化查询（KLINE_TABLE 常量拼接，ch_reader 通道），SQL 集中化另列
            f"WHERE (is_universe_eligible = 1 OR symbol = 'ETHBTC') AND trade_date <= '{end_date.isoformat()}' "
            f"ORDER BY symbol, trade_date ASC"

        )
        series: dict[str, list[tuple[datetime.date, float]]] = {}
        for symbol, d, close in rows:
            series.setdefault(symbol, []).append((datetime.date.fromisoformat(d), float(close)))
        return series

    @staticmethod
    def _load_fng_map() -> dict[datetime.date, int]:
        """恐惧贪婪指数（alternative.me 免费源）→ 日期映射；失败返回空 dict（只随行记录，不阻断档位）。"""
        try:
            req = urllib.request.Request(_FNG_URL + "?limit=35", headers={"User-Agent": "Mozilla/5.0 (ZephyrAlpha-shadow-judge)"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8")).get("data", [])
            return {
                datetime.datetime.fromtimestamp(int(item["timestamp"]), tz=datetime.timezone.utc).date(): int(item["value"])
                for item in data
            }
        except Exception as e:  # noqa: BLE001 — 情绪侧失败不阻断影子判定
            print(f"[warn] 恐惧贪婪指数获取失败（只随行记录，不阻断）: {e}")
            return {}

    @staticmethod
    def _ma_series(closes: list[float], window: int) -> list[float | None]:
        out: list[float | None] = [None] * len(closes)
        for i in range(window - 1, len(closes)):
            out[i] = sum(closes[i - window + 1 : i + 1]) / window
        return out

    @staticmethod
    def _altseason_metrics(
        target: datetime.date,
        btc_closes: list[float],
        i: int,
        series: dict[str, list[tuple[datetime.date, float]]],
    ) -> tuple[float | None, int]:
        """山寨季比率=90 日前有价的宇宙成员中 90 日收益跑赢 BTC 的占比（<20 对返回 None 防小样本伪档）。"""
        btc_ret90 = None
        if i >= _ALTSEASON_WINDOW:
            base = btc_closes[i - _ALTSEASON_WINDOW]
            if base > 0:
                btc_ret90 = btc_closes[i] / base - 1.0
        if btc_ret90 is None:
            return None, 0
        winners = 0
        universe_n = 0
        for sym, s in series.items():
            if sym == "BTCUSDT":
                continue
            dates = [d for d, _ in s]
            if target not in dates:
                continue
            k = dates.index(target)
            if k < _ALTSEASON_WINDOW:
                continue
            base = s[k - _ALTSEASON_WINDOW][1]
            if base <= 0:
                continue
            universe_n += 1
            if s[k][1] / base - 1.0 > btc_ret90:
                winners += 1
        return (winners / universe_n if universe_n >= _MIN_UNIVERSE else None), universe_n

    @staticmethod
    def _eth_metrics(target: datetime.date, series: dict[str, list[tuple[datetime.date, float]]]) -> tuple[float | None, float | None]:
        """ETH/BTC 当日收盘与 20 日均线（设计稿 ALT/BTC 汇率上行佐证口径，v0.1 只记录不判档）。"""
        eth = series.get("ETHBTC", [])
        eth_dates = [d for d, _ in eth]
        if target not in eth_dates:
            return None, None
        e = eth_dates.index(target)
        eth_ratio = eth[e][1]
        eth_ma20 = sum(c for _, c in eth[e - 19 : e + 1]) / 20.0 if e >= 19 else None
        return eth_ratio, eth_ma20

    @staticmethod
    def judge_day(
        target: datetime.date,
        btc_series: list[tuple[datetime.date, float]],
        series: dict[str, list[tuple[datetime.date, float]]],
        fng_value: int | None,
    ) -> dict:
        """单日影子判定（纯函数便于复核；三档顺序：先破位收紧，再趋势/山寨季）。"""
        btc_dates = [d for d, _ in btc_series]
        btc_closes = [c for _, c in btc_series]
        if target not in btc_dates:
            return {"trade_date": target, "tier": "insufficient_history", "reason": "BTC 当日无收盘数据", "metrics": {}}
        i = btc_dates.index(target)
        ma200 = CryptoProvider._ma_series(btc_closes, _MA_WINDOW)
        ma_t = ma200[i]
        if ma_t is None:
            return {
                "trade_date": target, "tier": "insufficient_history",
                "reason": f"MA{_MA_WINDOW} 未满 {_MA_WINDOW} 根（当前 {i + 1} 根）",
                "metrics": {"btc_close": btc_closes[i]},
            }
        slope = None
        if i >= _SLOPE_LOOKBACK and ma200[i - _SLOPE_LOOKBACK] is not None:
            slope = ma_t - ma200[i - _SLOPE_LOOKBACK]
        close = btc_closes[i]

        ratio, universe_n = CryptoProvider._altseason_metrics(target, btc_closes, i, series)
        eth_ratio, eth_ma20 = CryptoProvider._eth_metrics(target, series)

        metrics = {
            "btc_close": close, "ma200": ma_t, "ma_slope_10d": slope,
            "altseason_ratio": ratio, "altseason_universe": universe_n,
            "eth_btc_ratio": eth_ratio, "eth_btc_ratio_ma20": eth_ma20, "fng_value": fng_value,
        }

        if close < ma_t or (slope is not None and slope < 0):
            tier = "tighten"
            reason = f"BTC 收盘 {close:.0f} < MA200 {ma_t:.0f} 或 MA200 十日斜率 {slope} < 0（设计稿破位收紧）"
        elif ratio is None:
            tier = "insufficient_history"
            reason = f"山寨季比率窗口不足（宇宙 {universe_n} < {_MIN_UNIVERSE} 或 90 日窗口未满），趋势条件虽成立但仅记录不判趋势档"
        elif ratio >= _ALTSEASON_THRESHOLD:
            tier = "altseason"
            reason = (
                f"趋势条件成立（收盘 {close:.0f} ≥ MA200 {ma_t:.0f} 且斜率 {slope} ≥ 0）"
                f"且山寨季比率 {ratio:.2f} ≥ 0.75（业界口径 BlockchainCenter 75%/90日；自算口径差异披露在案）"
            )
        else:
            tier = "trend"
            reason = f"趋势条件成立（收盘 {close:.0f} ≥ MA200 {ma_t:.0f} 且斜率 {slope} ≥ 0），山寨季比率 {ratio:.2f} < 0.75"
        return {"trade_date": target, "tier": tier, "reason": reason, "metrics": metrics}

    def _fetch_shadow_gate(self, payload: FetchPayload) -> Iterator[FetchResult]:
        started = time.monotonic()
        lookback = int((payload.extra or {}).get("backfill_days", 1))
        end_date = _last_completed_utc_day()
        targets = sorted(end_date - datetime.timedelta(days=i) for i in range(max(1, lookback)))
        try:
            btc_series = self._load_btc_series(end_date, need=_MA_WINDOW + _SLOPE_LOOKBACK + 5)
            series = self._load_universe_window(end_date)
        except RuntimeError as e:
            yield FetchResult(table=GATE_TABLE, columns=[], rows=[], last_key="", elapsed_sec=0.0, error=str(e))
            return
        if not btc_series:
            yield FetchResult(
                table=GATE_TABLE, columns=[], rows=[], last_key="", elapsed_sec=time.monotonic() - started,
                error="crypto_kline_daily 无 BTCUSDT 数据——先跑 crypto_kline_daily 任务（FAIL-VISIBLE）",
            )
            return
        fng_map = self._load_fng_map()
        out_rows = []
        for t in targets:
            r = self.judge_day(t, btc_series, series, fng_map.get(t))
            m = r["metrics"]
            out_rows.append((
                r["trade_date"].isoformat(), m.get("btc_close"), m.get("ma200"), m.get("ma_slope_10d"),
                m.get("altseason_ratio"), m.get("altseason_universe"), m.get("eth_btc_ratio"),
                m.get("eth_btc_ratio_ma20"), m.get("fng_value"), r["tier"], r["reason"], 0, SHADOW_VERSION,
            ))
        yield FetchResult(
            table=GATE_TABLE, columns=GATE_COLUMNS, rows=out_rows, last_key=targets[-1].isoformat(),
            elapsed_sec=time.monotonic() - started,
        )


def get_crypto_secret(key: str) -> str:
    """密钥读取统一走 secrets 接口（RULE-SECRETS；当前免费源无 key，预留）。"""
    return get_service_secret(key, "crypto_binance", required=False) or ""
