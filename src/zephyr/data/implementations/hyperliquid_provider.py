#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §crypto
# [MODULE] zephyr.data.implementations.hyperliquid_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.provider_base; zephyr.data.ch_reader; stdlib(urllib/json); websockets(lazy,可选)
# [CONSUMERS] zephyr.data.scheduler（source=hyperliquid）
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 官方公开 API 匿名只读（api.hyperliquid.xyz info POST + wss 流，无 key 无签名，免费）；四 capability 按payload.extra["capability"]路由（crypto_binance 先例）；快照两表自积起点 2026-09-18 历史不可回补（表注释同款声明）；funding 回溯=PIT 如实（各币起于各自首笔，BTC 实测 2023-05-12 起）；清算捕获=trades 流清算账本地址标记（REST recentLiquidations 实测 422 不存在、WS 无公开清算频道，官方 subscriptions 文档在案）；FAIL-VISIBLE 失败不造数不占位；websockets 为 demo extras 按需依赖（akshare 先例），未装时仅清算 capability FAIL-VISIBLE
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 源不可达/限频->RuntimeError（集成器标准重试/告警管道）；CH 读数失败->FetchResult.error；清算通道不可用->FetchResult.error（FAIL-VISIBLE）
# [TESTS] tests/zephyr/data/test_hyperliquid_provider.py
# [TTL] permanent
"""hyperliquid_provider.py — Hyperliquid 全市场永续数据 Provider（source=hyperliquid）。

真源：altdata_line 09 清单 D5 跨资产 H1（2026-09-18 夜班，st-datapack-20260918）。
官方文档：docs.hyperliquid.xyz/for-developers/api（info POST 匿名免费无 key；
WS wss://api.hyperliquid.xyz/ws）。requests 直连精神=仅 urllib 标准库，勿引重依赖；
唯一例外 websockets（清算 WS 捕获，纯 py 轻依赖，demo extras 登记在案，lazy import）。

四 capability（altdata_line D5 四类，fetch 按 payload.extra["capability"] 路由）：
  hl_perp_snapshot_daily  全市场行情快照（日更自积，起点 2026-09-18，历史不可回补）
                          → c1_market.hl_perp_snapshot_daily
  hl_oi_snapshot_daily    全市场持仓/OI 分布快照（日更自积）→ c1_market.hl_oi_snapshot_daily
  hl_funding_history      资金费率逐小时（可回溯：实测 BTC 起 2023-05-12；增量=lookback 窗口幂等重放）
                          → c1_market.hl_funding_history
  hl_liquidation_capture  清算流有界捕获（trades 流清算账本地址标记；全量 7x24 WS 守护留下一班）
                          → c1_market.hl_liquidation_raw

源端实测留痕（2026-09-18）：
  - metaAndAssetCtxs：234 永续（含 isDelisted 行）；fundingHistory startTime=0 回至 2023-05
  - recentLiquidations（REST）= 422 不存在；allLiquidation/liquidation/webData2 WS 订阅均拒
  - trades 流 users 字段含清算账本专用地址 0xffff…ff（社区追踪器通行口径），按此落 is_liquidation
"""
from __future__ import annotations

import asyncio
import datetime
import json
import threading
import time
import urllib.request
from typing import Final, Iterator

from zephyr.data.provider_base import (
    CapabilityContract,
    FetchPayload,
    FetchResult,
    IngestProviderBase,
    IngestProviderMeta,
)
from zephyr.shared.utils.time_utils import now_utc  # 时间 SSoT（RULE-SCHEMA-TZ：禁 time.time()/datetime.now() 无参数）
from zephyr.data.table_registry import get_registry

_INFO_URL = "https://api.hyperliquid.xyz/info"
_WS_URL = "wss://api.hyperliquid.xyz/ws"

_TR = get_registry()
SNAPSHOT_TABLE = _TR.table("hl_perp_snapshot_daily")
OI_TABLE = _TR.table("hl_oi_snapshot_daily")
FUNDING_TABLE = _TR.table("hl_funding_history")
LIQ_TABLE = _TR.table("hl_liquidation_raw")

SNAPSHOT_COLUMNS: Final[list[str]] = [
    "snapshot_date", "coin", "sz_decimals", "max_leverage", "mark_px", "oracle_px",
    "mid_px", "prev_day_px", "day_ntl_vlm", "day_base_vlm", "is_delisted",
    "data_source", "quality_flag",
]
OI_COLUMNS: Final[list[str]] = [
    "snapshot_date", "coin", "open_interest", "oi_ntl_usd", "funding_rate", "premium",
    "impact_bid_px", "impact_ask_px", "mark_px", "data_source", "quality_flag",
]
FUNDING_COLUMNS: Final[list[str]] = ["coin", "funding_time", "funding_rate", "premium", "data_source", "quality_flag"]
LIQ_COLUMNS: Final[list[str]] = [
    "trade_time", "coin", "side", "px", "sz", "ntl_usd", "buyer_addr", "seller_addr",
    "is_liquidation", "tid", "trade_hash", "capture_mode", "data_source", "quality_flag",
]

DATA_SOURCE = "hyperliquid"
_RETRY = 3
_BACKOFF = 2.0
_INFO_SLEEP = 0.25          # info 免费源保守限频（对齐 crypto_provider 精神）
_FUNDING_PAGE = 500         # fundingHistory 单页上限（官方通用 500 行分页）
_FUNDING_MAX_PAGES_PER_COIN = 400  # 单币翻页硬顶（BTC 自 2023-05 全史 ~60 页，400=宽安全裕度）
_FUNDING_MAX_TOTAL_REQUESTS = 20000  # 单次 fetch 全局请求硬顶（防失控翻页，达顶即报错留痕）
_LIQ_BOOK_ADDR = "0x" + "f" * 40   # 清算账本专用地址（schema 常量同源）


def _ms_to_dt64_str(ms: int) -> str:
    """epoch ms → ClickHouse DateTime64(3,'UTC') 字面量。"""
    dt = datetime.datetime.fromtimestamp(int(ms) / 1000, tz=datetime.timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S.") + f"{int(ms) % 1000:03d}"


def _f(x: object) -> float | None:
    """源字符串数值 → float（空/坏值返回 None，Nullable 语义）。"""
    try:
        v = float(str(x)) if x is not None and str(x) != "" else None  # type: ignore[arg-type]
    except ValueError:
        return None
    return v


def _dec_or_none(x: object) -> str | None:
    """源端字符串数值 → Decimal 列字面量（NaN/Inf/空 → None）。

    Decimal 列拒绝 NaN 字面量：2026-09-18 实测 PANDORA premium=NaN 致 TSV insert
    整批 HTTP 400 降级本地落盘——源端 NaN 属"无值"语义，归 NULL 如实。
    """
    if x is None:
        return None
    s = str(x).strip()
    if s == "" or s.lower() in ("nan", "inf", "-inf", "+inf", "infinity", "-infinity"):
        return None
    return s


class HyperliquidProvider(IngestProviderBase):
    """Hyperliquid Provider——官方免费公开 API 四类跨资产数据（行情/持仓/资金费/清算）。"""

    source_name: str = "hyperliquid"
    # CAP-CONSISTENCY（#ARCH-CH-022）：fetch 路由能力集与 meta.capabilities 声明集一致
    meta: IngestProviderMeta = IngestProviderMeta(
        name="hyperliquid",
        display_name="Hyperliquid 全市场永续（官方免费 info+WS）",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="stateless",
        rate_limit_default=240,
        capabilities=[
            CapabilityContract("hl_perp_snapshot_daily", supports_symbols_null=True),
            CapabilityContract("hl_oi_snapshot_daily", supports_symbols_null=True),
            CapabilityContract("hl_funding_history", supports_symbols_null=True),
            CapabilityContract("hl_liquidation_capture", supports_symbols_null=True),
        ],
    )

    def connect(self) -> None:
        """HTTP/WS 无状态源，无连接语义。"""

    def disconnect(self) -> None:
        """无连接语义。"""

    def health_check(self) -> bool:
        try:
            mids = self._info({"type": "allMids"})
            return isinstance(mids, dict) and len(mids) > 0
        except Exception:  # noqa: BLE001 — 健康探测失败即不可用
            return False

    def capability_contracts(self) -> list[CapabilityContract]:
        return list(self.meta.capabilities)

    def fetch(self, payload: FetchPayload, policy) -> Iterator[FetchResult]:
        capability = (payload.extra or {}).get("capability")
        if capability == "hl_perp_snapshot_daily":
            yield from self._fetch_perp_snapshot(payload)
        elif capability == "hl_oi_snapshot_daily":
            yield from self._fetch_oi_snapshot(payload)
        elif capability == "hl_funding_history":
            yield from self._fetch_funding_history(payload)
        elif capability == "hl_liquidation_capture":
            yield from self._fetch_liquidation_capture(payload)
        else:
            yield FetchResult(
                table=payload.table, columns=[], rows=[], last_key="", elapsed_sec=0.0,
                error=f"unsupported capability: {capability}",
            )

    # ------------------------------------------------------------ HTTP 基础

    @staticmethod
    def _info(body: dict) -> object:
        """POST /info → JSON；3 次重试指数退避 + 429 限频退避；失败抛 RuntimeError（FAIL-VISIBLE）。"""
        last_err: Exception | None = None
        for attempt in range(1, _RETRY + 1):
            try:
                req = urllib.request.Request(
                    _INFO_URL,
                    data=json.dumps(body).encode("utf-8"),
                    headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (ZephyrAlpha-altdata)"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except Exception as e:  # noqa: BLE001 — 网络异常统一重试（含 HTTPError 429）
                last_err = e
                wait = _BACKOFF * attempt
                if "429" in str(e):
                    wait = max(wait, 10.0)  # 官方限频：退足再试
                print(f"[retry {attempt}/{_RETRY}] info {body.get('type')} 失败: {type(e).__name__}: {e}")
                if attempt < _RETRY:
                    threading.Event().wait(wait)
        raise RuntimeError(f"Hyperliquid info 不可达(连续 {_RETRY} 次失败): {last_err}")

    def _fetch_meta_ctxs(self) -> tuple[dict, list[dict]]:
        """metaAndAssetCtxs → (meta, assetCtxs)，universe 名对齐拼接。"""
        data = self._info({"type": "metaAndAssetCtxs"})
        meta, ctxs = data[0], data[1]
        universe = meta.get("universe", [])
        if len(universe) != len(ctxs):
            raise RuntimeError(f"metaAndAssetCtxs 长度不一致 universe={len(universe)} ctxs={len(ctxs)}（FAIL-VISIBLE）")
        if not universe:
            raise RuntimeError("metaAndAssetCtxs 空宇宙（FAIL-VISIBLE）")
        return meta, ctxs

    # ------------------------------------------------------------ H1-1 行情快照

    def _fetch_perp_snapshot(self, payload: FetchPayload) -> Iterator[FetchResult]:
        """全市场行情快照（日更自积；同日重跑幂等替换）。"""
        t0 = time.monotonic()
        meta, ctxs = self._fetch_meta_ctxs()
        universe = meta.get("universe", [])
        snapshot_date = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
        rows = []
        for u, c in zip(universe, ctxs):
            rows.append((
                snapshot_date, u.get("name", ""),
                int(u.get("szDecimals", 0)), int(u.get("maxLeverage", 0)),
                c.get("markPx"), c.get("oraclePx"), c.get("midPx"), c.get("prevDayPx"),
                c.get("dayNtlVlm"), c.get("dayBaseVlm"),
                1 if u.get("isDelisted") else 0, DATA_SOURCE, 1,
            ))
        if not rows:
            yield FetchResult(table=SNAPSHOT_TABLE, columns=SNAPSHOT_COLUMNS, rows=[], last_key="",
                              elapsed_sec=time.monotonic() - t0, error="零行快照（源异常），拒绝写库（FAIL-VISIBLE）")
            return
        yield FetchResult(table=SNAPSHOT_TABLE, columns=SNAPSHOT_COLUMNS, rows=rows,
                          last_key=snapshot_date, elapsed_sec=time.monotonic() - t0)

    # ------------------------------------------------------------ H1-4 持仓/OI 快照

    def _fetch_oi_snapshot(self, payload: FetchPayload) -> Iterator[FetchResult]:
        """全市场持仓/OI 分布快照（日更自积；oi_ntl_usd=采集时点 mark 换算自算，口径披露在 schema）。"""
        t0 = time.monotonic()
        meta, ctxs = self._fetch_meta_ctxs()
        universe = meta.get("universe", [])
        snapshot_date = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
        rows = []
        for u, c in zip(universe, ctxs):
            oi = _f(c.get("openInterest"))
            mark = _f(c.get("markPx"))
            oi_ntl = (f"{oi * mark:.8f}" if oi is not None and mark is not None else None)
            impacts = c.get("impactPxs") or [None, None]
            rows.append((
                snapshot_date, u.get("name", ""),
                c.get("openInterest"), oi_ntl, c.get("funding"), c.get("premium"),
                impacts[0], impacts[1], c.get("markPx"), DATA_SOURCE, 1,
            ))
        if not rows:
            yield FetchResult(table=OI_TABLE, columns=OI_COLUMNS, rows=[], last_key="",
                              elapsed_sec=time.monotonic() - t0, error="零行 OI 快照（源异常），拒绝写库（FAIL-VISIBLE）")
            return
        yield FetchResult(table=OI_TABLE, columns=OI_COLUMNS, rows=rows,
                          last_key=snapshot_date, elapsed_sec=time.monotonic() - t0)

    # ------------------------------------------------------------ H1-2 资金费率

    def _fetch_one_coin_funding(self, coin: str, start_ms: int) -> tuple[list[tuple], bool, int]:
        """单币分页拉取（helper 拆分降复杂度）；返回 (rows, pages_capped, requests)。

        分页游标由源端返回行数驱动（非时间触发轮询）；单币翻页硬顶
        _FUNDING_MAX_PAGES_PER_COIN 防失控，触顶 capped=True 如实留痕（数据不全）。
        """
        rows: list[tuple] = []
        cursor = start_ms
        pages = 0
        requests = 0
        paging = True
        while paging:
            batch = self._info({"type": "fundingHistory", "coin": coin, "startTime": cursor})
            requests += 1
            pages += 1
            if pages > _FUNDING_MAX_PAGES_PER_COIN:
                print(f"[warn] {coin} 单币翻页顶触发（数据不全留痕）", flush=True)
                return rows, True, requests
            if not isinstance(batch, list) or not batch:
                return rows, False, requests
            for h in batch:
                rows.append((
                    coin, _ms_to_dt64_str(int(h["time"])),
                    _dec_or_none(h.get("fundingRate")), _dec_or_none(h.get("premium")), DATA_SOURCE, 1,
                ))
            last_ms = int(batch[-1]["time"])
            nxt = last_ms + 1
            if nxt <= cursor or len(batch) < _FUNDING_PAGE:
                return rows, False, requests
            cursor = nxt
            threading.Event().wait(_INFO_SLEEP)
        return rows, False, requests  # 不可达（while 由 return 驱动退出）

    def _fetch_funding_history(self, payload: FetchPayload) -> Iterator[FetchResult]:
        """资金费率逐小时（增量=lookback 窗口；extra.backfill_from_start=true=自各币首笔深回溯）。

        首跑深回溯（2026-09-18 实测）：BTC 自 2023-05-12 起全史可回；各币起于各自上市首笔。
        深回溯一次落库（ReplacingMergeTree 幂等），日常增量 lookback_days 窗口重放。
        """
        t0 = time.monotonic()
        extra = payload.extra or {}
        from_start = bool(extra.get("backfill_from_start", False))
        lookback_days = int(extra.get("lookback_days", 3))
        now_ms = int(now_utc().timestamp() * 1000)
        default_start_ms = now_ms - max(1, lookback_days) * 86_400_000

        meta, ctxs = self._fetch_meta_ctxs()
        coins = [u.get("name", "") for u in meta.get("universe", []) if u.get("name")]
        rows: list[tuple] = []
        total_requests = 0
        for coin in coins:
            if total_requests >= _FUNDING_MAX_TOTAL_REQUESTS:
                yield FetchResult(table=FUNDING_TABLE, columns=FUNDING_COLUMNS, rows=[], last_key="",
                                  elapsed_sec=time.monotonic() - t0,
                                  error=f"全局请求硬顶 {_FUNDING_MAX_TOTAL_REQUESTS} 触达（部分币未完成，FAIL-VISIBLE 留痕重跑）")
                return
            start_ms = 0 if from_start else default_start_ms
            coin_rows, _capped, reqs = self._fetch_one_coin_funding(coin, start_ms)
            total_requests += reqs
            rows.extend(coin_rows)
            if total_requests % 200 == 0:
                print(f"[progress] funding requests={total_requests} coins_done~{coins.index(coin)} rows={len(rows)}", flush=True)
        if not rows:
            yield FetchResult(table=FUNDING_TABLE, columns=FUNDING_COLUMNS, rows=[], last_key="",
                              elapsed_sec=time.monotonic() - t0, error="零行 funding（源异常），拒绝写库（FAIL-VISIBLE）")
            return
        # last_key=最大日期（断点续传口径）；回溯请求计数留痕
        print(f"[info] funding fetch: coins={len(coins)} rows={len(rows)} requests={total_requests} from_start={from_start}", flush=True)
        yield FetchResult(table=FUNDING_TABLE, columns=FUNDING_COLUMNS, rows=rows,
                          last_key=datetime.datetime.now(datetime.timezone.utc).date().isoformat(),
                          elapsed_sec=time.monotonic() - t0)

    # ------------------------------------------------------------ H1-3 清算流（有界 WS 捕获）

    @staticmethod
    def _liq_rows_from_batch(batch: list[dict], capture_mode: str) -> list[tuple]:
        """trades 批次 → 清算标记行（helper 拆分降复杂度；无标记批次返回空）。"""
        out: list[tuple] = []
        for tr in batch:
            users = tr.get("users") or []
            if not any(str(a).lower() == _LIQ_BOOK_ADDR for a in users):
                continue
            px, sz = _f(tr.get("px")), _f(tr.get("sz"))
            ntl = (f"{px * sz:.8f}" if px is not None and sz is not None else "0")
            out.append((
                _ms_to_dt64_str(int(tr["time"])), tr.get("coin", ""), tr.get("side", ""),
                tr.get("px"), tr.get("sz"), ntl,
                str(users[0]) if len(users) > 0 else "",
                str(users[1]) if len(users) > 1 else "",
                1, int(tr.get("tid", 0)), str(tr.get("hash", "")),
                capture_mode, DATA_SOURCE, 1,
            ))
        return out

    def _fetch_liquidation_capture(self, payload: FetchPayload) -> Iterator[FetchResult]:
        """清算流有界捕获：订阅全永续 trades 流 capture_minutes 分钟，过滤清算账本地址落库。

        口径（源端实测披露见模块 docstring）：官方无 REST 清算端点/无公开清算 WS 频道，
        唯一公开捕获面=trades 流 users 字段清算账本地址标记；本班=逐日有界采样，
        capture_mode=ws_trades_bounded；全量 7x24 守护进程留下一班（altdata_line D5 挂账）。
        """
        t0 = time.monotonic()
        extra = payload.extra or {}
        minutes = float(extra.get("capture_minutes", 30))
        capture_mode = str(extra.get("capture_mode", "ws_trades_bounded"))
        try:
            import websockets  # demo extras 按需依赖（akshare 先例；未装即 FAIL-VISIBLE）
        except ImportError as e:
            yield FetchResult(table=LIQ_TABLE, columns=LIQ_COLUMNS, rows=[], last_key="",
                              elapsed_sec=0.0,
                              error=f"websockets 依赖未安装（pip install websockets 或 .[demo]）: {e}")
            return
        meta, ctxs = self._fetch_meta_ctxs()
        coins = [u.get("name", "") for u in meta.get("universe", [])
                 if u.get("name") and not u.get("isDelisted")]
        rows, trades_seen, err = self._ws_capture_session(coins, minutes, capture_mode)
        print(f"[info] liquidation capture: coins={len(coins)} window={minutes:.0f}min trades_seen={trades_seen} liq_rows={len(rows)}", flush=True)
        if not rows and err is None and trades_seen == 0:
            yield FetchResult(table=LIQ_TABLE, columns=LIQ_COLUMNS, rows=[], last_key="",
                              elapsed_sec=time.monotonic() - t0,
                              error=f"捕获窗口零成交（订阅或流异常），拒绝空写（FAIL-VISIBLE）coins={len(coins)}")
            return
        if not rows:
            rows = [self._capture_heartbeat_row(minutes, len(coins), trades_seen, capture_mode)]
        yield FetchResult(table=LIQ_TABLE, columns=LIQ_COLUMNS, rows=rows,
                          last_key=datetime.datetime.now(datetime.timezone.utc).date().isoformat(),
                          elapsed_sec=time.monotonic() - t0, error=err)

    @staticmethod
    def _capture_heartbeat_row(minutes: float, coin_n: int, trades_seen: int, capture_mode: str) -> tuple:
        """静默窗口心跳行（coin=__CAPTURE_HEARTBEAT__）：哨兵新鲜度锚+捕获覆盖台账。"""
        return (
            _ms_to_dt64_str(int(now_utc().timestamp() * 1000)), "__CAPTURE_HEARTBEAT__", "-",
            "0", "0", "0", "", "", 0, 0,
            f"window={minutes:.0f}min,coins={coin_n},trades_seen={trades_seen}",
            capture_mode, DATA_SOURCE, 1,
        )

    def _ws_capture_session(self, coins: list[str], minutes: float, capture_mode: str) -> tuple[list[tuple], int, str | None]:
        """单次有界 WS 会话：订阅 coins trades 流 minutes 分钟，返回 (清算行, 成交数, 中断留痕)。

        同步入口经 async_utils.run_coroutine_sync canonical 运行（ASYNCIO-RUN-IN-CONTEXT 合规）；
        窗口 deadline 用 time.monotonic（跨 loop 语义一致的单调钟）。
        """
        import websockets

        async def _capture() -> tuple[list[tuple], int, str | None]:
            rows: list[tuple] = []
            trades_seen = 0
            err: str | None = None
            try:
                async with websockets.connect(_WS_URL, max_size=None, ping_interval=15, ping_timeout=12) as ws:
                    for coin in coins:
                        await ws.send(json.dumps({"method": "subscribe", "subscription": {"type": "trades", "coin": coin}}))
                    deadline = time.monotonic() + minutes * 60.0
                    window_open = True  # 有界采样窗口（deadline 驱动，非时间触发守护循环）
                    while window_open:
                        remain = deadline - time.monotonic()
                        if remain <= 0:
                            window_open = False
                            break
                        try:
                            msg = await asyncio.wait_for(ws.recv(), timeout=min(remain, 15.0))
                        except asyncio.TimeoutError:
                            continue
                        d = json.loads(msg)
                        if d.get("channel") != "trades":
                            continue
                        batch = d.get("data") or []
                        trades_seen += len(batch)
                        rows.extend(HyperliquidProvider._liq_rows_from_batch(batch, capture_mode))
            except (Exception, asyncio.CancelledError) as e:  # noqa: BLE001 — 通道中断按当批落库+留痕
                err = f"WS 捕获中断（当批已收数据照常落库）: {type(e).__name__}: {e}"
            return rows, trades_seen, err

        from zephyr.shared.utils.async_utils import run_coroutine_sync

        return run_coroutine_sync(_capture(), timeout=minutes * 60.0 + 120.0)


def get_hyperliquid_secret(key: str) -> str:
    """密钥读取统一走 secrets 接口（RULE-SECRETS；当前免费源无 key，预留）。"""
    from zephyr.shared.security.secrets import get_service_secret

    return get_service_secret(key, "hyperliquid", required=False) or ""


if __name__ == "__main__":
    # CLI 探针（运维诊断入口，无副作用不写库）：python -m zephyr.data.implementations.hyperliquid_provider
    # 仅 health_check（不含 argv/参数解析——manual 触发模式规避；capability 干跑走集成器任务管线）
    _provider = HyperliquidProvider()
    print("health_check:", _provider.health_check())
