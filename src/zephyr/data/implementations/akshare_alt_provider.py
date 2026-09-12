#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §alt-data
# [MODULE] zephyr.data.implementations.akshare_alt_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.provider_base; zephyr.data.table_registry; stdlib
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] lazy
# [MATURITY] production
# [INVARIANTS] 另类数据免注册直连源（akshare）；表名必经 TableRegistry 派生（#ARCH-CH-024）；
#              禁裸 os.getenv；接口返回空/异常时 yield error FetchResult 不抛出（与 hog_* 同约定）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] akshare 接口异常->yield FetchResult(error=...)（上层计失败不中断其他任务）；
#                  TableRegistry 查不到 category_id->KeyError fail-closed
# [TESTS] tests/zephyr/data/test_alt_sources.py
# [TTL] permanent
"""AkshareAltProvider — 另类数据第 1 批免注册直连源（千股千评 + 航运运价）。

背景（docs/_working/2026-09-12-alt-data-handoff.md §8-1，另类数据施工第 1 批）：
    为什么独立成模块而不开进 akshare_provider：
    - akshare_provider.py 为他在会（研报批）claim 在途文件，另类批独立成件零冲突；
    - 另类源与行情主链路生命周期解耦（接口漂移风险独立演进，alt_source_health_manager 监控）。

能力（capability -> 表）：
    alt_stock_comment   千股千评全表日快照 -> c1_market.alt_stock_comment
                        （东财数据中心综合评价；关注指数=股吧关注度代理——akshare 无股吧
                          发帖量直连接口（2026-09-12 实测枚举确认），人气榜通道
                          stock_hot_rank 已在跑，本能力补全市场级关注度面）
    alt_shipping_index  航运运价指数长表   -> c1_market.alt_shipping_index
                        （BDI 1988 起含日涨跌幅 + BCI/BSI/BHMI/HRCI/BCTI/BDTI 约 2006 起；
                          BDI 双源重叠以 macro_shipping_bdi 为准，免重）

PIT 三公理：快照/指数即所得，无前视；trade_date 取接口自带日期列（千股千评"交易日"
常为 T-1），不信运行日。
"""

from __future__ import annotations

import logging
import time
from typing import Iterator

from zephyr.data.policy_registry import SourcePolicy
from zephyr.data.provider_base import (
    CapabilityContract,
    FetchPayload,
    FetchResult,
    IngestProviderBase,
    IngestProviderMeta,
)
from zephyr.data.table_registry import get_registry

log = logging.getLogger(__name__)

# 表名从 business_data_categories.yaml 真源派生（#ARCH-CH-024，禁硬编码）
_TBL_ALT_STOCK_COMMENT = get_registry().table("market_alt_stock_comment")
_TBL_ALT_SHIPPING_INDEX = get_registry().table("market_alt_shipping_index")

# 千股千评表列（顺序与 DDL INSERT_COLUMNS 一致）
_ALT_COMMENT_COLUMNS = [
    "trade_date",
    "symbol",
    "name",
    "org_participation",
    "composite_score",
    "rank_change",
    "current_rank",
    "attention_index",
    "main_cost",
]

# 运价长表列
_ALT_SHIPPING_COLUMNS = ["trade_date", "index_code", "index_name", "value", "change_pct", "source"]

# macro_china_freight_index 列 -> (index_code, index_name)；
# BDI 不在本表（双源重叠以 macro_shipping_bdi 为准，历史更长且带涨跌幅）
_FREIGHT_INDEX_MAP: tuple[tuple[str, str, str], ...] = (
    ("波罗的海好望角型船运价指数BCI", "BCI", "波罗的海好望角型船运价指数"),
    ("灵便型船综合运价指数BHMI", "BHMI", "灵便型船综合运价指数"),
    ("波罗的海超级大灵便型BSI指数", "BSI", "波罗的海超级大灵便型船指数"),
    ("HRCI国际集装箱租船指数", "HRCI", "国际集装箱租船指数"),
    ("油轮运价指数成品油运价指数BCTI", "BCTI", "成品油运价指数"),
    ("油轮运价指数原油运价指数BDTI", "BDTI", "原油运价指数"),
)

_AKSHARE_ALT_CAPABILITIES = frozenset({"alt_stock_comment", "alt_shipping_index"})


def _norm_date(v) -> str | None:
    """规范化 akshare 日期为 'YYYY-MM-DD' 字符串（兼容 Timestamp/str/NaT）。"""
    if v is None:
        return None
    s = str(v)
    if s in ("NaT", "nan", "None", "", "nat"):
        return None
    return s[:10]


def _to_float(v) -> float | None:
    """安全转 float；NaN 防穿透返回 None（Nullable 列语义）。"""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    if f != f:  # NaN
        return None
    return f


def _to_int(v) -> int | None:
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


class AkshareAltProvider(IngestProviderBase):
    """另类数据免注册直连源 provider（akshare 直连，无需密钥）。"""

    _connected: bool = False

    meta: IngestProviderMeta = IngestProviderMeta(
        name="akshare_alt",
        display_name="AKShare 另类数据源（千股千评/航运运价）",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=60,
        capabilities=[
            # 快照幂等：无 symbols 概念（全市场表），不支持增量（接口无历史通道）
            CapabilityContract(
                "alt_stock_comment",
                supports_symbols_null=True,
                supports_incremental=False,
                supports_full_refresh=False,
                requires_date_range=False,
                expected_market="a_share",
                expected_variety="stock",
            ),
            CapabilityContract(
                "alt_shipping_index",
                supports_symbols_null=True,
                supports_incremental=True,
                supports_full_refresh=True,
                requires_date_range=True,
                expected_market="macro",
                expected_variety="index",
            ),
        ],
        known_issues=[
            "千股千评接口仅返回当日快照，无历史回补通道（每日累积模式）",
            "akshare 上游网页改版风险 -> alt_source_health_manager 探针兜底",
        ],
    )

    # ---- 探活/连接/断开（与 akshare 主 provider 同约定） ----

    def connect(self) -> bool:
        """无持久连接资源：akshare 可导入即连立（lazy import 在 fetch 时发生）。"""
        self._connected = self.health_check()
        return self._connected

    def health_check(self) -> bool:
        try:
            import akshare  # noqa: F401

            return True
        except ImportError as e:
            self._log.warning(f"akshare_alt 探活失败（akshare 未安装）: {e}")
            return False

    def disconnect(self) -> None:
        """无持久连接资源，仅重置状态。"""

    # ---- 拉取入口 ----

    def fetch(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """按 payload.extra["capability"] 路由；未知能力 yield error。"""
        cap = (payload.extra or {}).get("capability")
        if cap in _AKSHARE_ALT_CAPABILITIES:
            yield from getattr(self, f"_fetch_{cap}")(payload, policy)
            return
        yield FetchResult(
            table=payload.table,
            columns=[],
            rows=[],
            last_key="",
            elapsed_sec=0.0,
            error=f"unsupported capability: {cap}",
        )

    # ---- 千股千评全表日快照 ----

    def _fetch_alt_stock_comment(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """千股千评全表日快照，写入 c1_market.alt_stock_comment。

        akshare stock_comment_em 返回当日全市场约 5200 行（关注指数/综合得分/机构参与度/
        排名及变动）。trade_date 以接口自带"交易日"列为准（PIT 锚，常为 T-1），
        缺失时回退 payload.end；ReplacingMergeTree 按 (trade_date, symbol) 幂等。
        """
        import akshare as ak

        table = payload.table or _TBL_ALT_STOCK_COMMENT
        t0 = time.monotonic()
        try:
            df = self._call_with_policy(ak.stock_comment_em, policy)
            if df is None or len(df) == 0:
                yield FetchResult(
                    table=table,
                    columns=_ALT_COMMENT_COLUMNS,
                    rows=[],
                    last_key="",
                    elapsed_sec=time.monotonic() - t0,
                    error="stock_comment_em 返回空",
                )
                return
            fallback_date = payload.end.strftime("%Y-%m-%d") if payload.end else None
            rows: list[tuple] = []
            trade_dates: list[str] = []
            for _, r in df.iterrows():
                symbol = str(r.get("代码", "") or "").strip()
                if not symbol:
                    continue
                trade_date = _norm_date(r.get("交易日")) or fallback_date
                if not trade_date:
                    continue
                trade_dates.append(trade_date)
                rows.append(
                    (
                        trade_date,
                        symbol,
                        str(r.get("名称", "") or "").strip(),
                        _to_float(r.get("机构参与度")),
                        _to_float(r.get("综合得分")),
                        _to_float(r.get("上升")),
                        _to_int(r.get("目前排名")),
                        _to_float(r.get("关注指数")),
                        _to_float(r.get("主力成本")),
                    )
                )
            last_key = max(trade_dates) if trade_dates else ""
            yield FetchResult(
                table=table,
                columns=_ALT_COMMENT_COLUMNS,
                rows=rows,
                last_key=last_key,
                elapsed_sec=time.monotonic() - t0,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"alt_stock_comment 获取失败: {e}")
            yield FetchResult(
                table=table,
                columns=_ALT_COMMENT_COLUMNS,
                rows=[],
                last_key="",
                elapsed_sec=time.monotonic() - t0,
                error=str(e),
            )

    # ---- 航运运价指数长表 ----

    @staticmethod
    def _shipping_start_guard(payload: FetchPayload) -> str | None:
        return payload.start.strftime("%Y-%m-%d") if payload.start else None

    def _fetch_alt_shipping_index(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """航运运价指数长表，写入 c1_market.alt_shipping_index。

        双源合流（增量按 payload.start 过滤；全量取全部）：
        - ak.macro_shipping_bdi：BDI 1988-10 起，含日涨跌幅
        - ak.macro_china_freight_index：BCI/BSI/BHMI/HRCI/BCTI/BDTI 约 2006 起（BDI 列弃用免重）
        """
        import akshare as ak

        table = payload.table or _TBL_ALT_SHIPPING_INDEX
        t0 = time.monotonic()
        # 全量模式（incremental=False）忽略 start：scheduler 对全量任务也传 start=月初
        # （_compute_start_date 无 None 路径），若照单过滤则"全量刷新"名不副实；
        # 真全量周度重拉约 1.45 万行，ReplacingMergeTree 同键替换幂等，代价可忽略
        start_str = self._shipping_start_guard(payload) if payload.incremental else None
        rows: list[tuple] = []
        try:
            # 源1：BDI（金十源，1988 起）
            df = self._call_with_policy(ak.macro_shipping_bdi, policy)
            if df is not None and len(df) > 0:
                for _, r in df.iterrows():
                    trade_date = _norm_date(r.get("日期"))
                    value = _to_float(r.get("最新值"))
                    if not trade_date or value is None:
                        continue
                    if start_str and trade_date < start_str:
                        continue
                    rows.append(
                        (
                            trade_date,
                            "BDI",
                            "波罗的海综合运价指数",
                            value,
                            _to_float(r.get("涨跌幅")),
                            "macro_shipping_bdi",
                        )
                    )
            else:
                self._log.warning("macro_shipping_bdi 返回空（BDI 断供？）")

            # 源2：六指数（约 2006 起；BDI 列弃用免重）
            df2 = self._call_with_policy(ak.macro_china_freight_index, policy)
            if df2 is not None and len(df2) > 0:
                for _, r in df2.iterrows():
                    trade_date = _norm_date(r.get("截止日期"))
                    if not trade_date:
                        continue
                    if start_str and trade_date < start_str:
                        continue
                    for col, code, name in _FREIGHT_INDEX_MAP:
                        value = _to_float(r.get(col))
                        if value is None:
                            continue
                        rows.append((trade_date, code, name, value, None, "macro_china_freight_index"))
            else:
                self._log.warning("macro_china_freight_index 返回空（六指数断供？）")

            rows.sort(key=lambda t: (t[1], t[0]))
            last_key = max((t[0] for t in rows), default="")
            yield FetchResult(
                table=table,
                columns=_ALT_SHIPPING_COLUMNS,
                rows=rows,
                last_key=last_key,
                elapsed_sec=time.monotonic() - t0,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"alt_shipping_index 获取失败: {e}")
            yield FetchResult(
                table=table,
                columns=_ALT_SHIPPING_COLUMNS,
                rows=[],
                last_key="",
                elapsed_sec=time.monotonic() - t0,
                error=str(e),
            )
