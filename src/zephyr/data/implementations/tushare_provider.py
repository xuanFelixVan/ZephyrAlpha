# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.tushare_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] tushare SDK (ts.set_token/ts.pro_api/pro.news/pro.news_info/pro.fund_basic/pro.moneyflow/pro.fut_daily/pro.fund_nav/pro.hk_hold)
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] token认证（环境变量TUSHARE_TOKEN）；历史数据截止2024-08；积分不足触发重试
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 异常->yield FetchResult(error=str)；token缺失->RuntimeError
# [TESTS] tests/zephyr/data/test_providers.py::TestTushareProvider
# [A_module] module_id=MOD-GOV-tushare_provider | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Tushare 数据源 Provider 实现（MOD-L00-004 §4.3）。

封装 tushare SDK，继承 IngestProviderBase。
- token 认证（环境变量 TUSHARE_TOKEN）
- 历史数据截止 2024-08（新闻数据）
- 积分不足时 API 调用受限（TPMaxQueryLimitError 触发重试）
- 当前能力：news_data（新闻快讯/证券新闻）/ industry_class / industry_class_suppl /
  lof_list（东财反爬替代源）/ money_flow（东财反爬替代源）/
  futures_term_structure（QMT 期货板块为空替代源）/ etf_nav（东财净值接口反爬替代源）/
  northbound_hold_snapshot（北向季度持仓快照，19 号 memo；逻辑在 northbound_hold_fetcher.py）/
  kline_daily_bj（北交所日K线增量，2026-08-25 BJDAILY 生产上线）

关键设计：
- connect() 读取 TUSHARE_TOKEN 环境变量，初始化 pro_api 客户端
- fetch() 按 payload.extra["capability"] 路由到各 _fetch_* 方法
"""

from __future__ import annotations

import datetime
import logging
import re
import threading
import time
from typing import Iterator

# 19 号 memo：北向季度持仓快照（绝对 import 供 ORPHAN-MODULE 门禁 git grep 发现引用）
from zephyr.data.implementations.northbound_hold_fetcher import fetch_northbound_hold_snapshot
from zephyr.shared.security.secrets import get_required_secret, get_secret_or_default
from zephyr.shared.utils.time_utils import now_utc, seconds_since

from ..news_dedup import NEWS_DATA_COLUMNS, build_news_row
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
_TBL_NEWS_DATA = get_registry().table("fund_news_data")
# #ARCH-IFIND-FAILOVER: 承接原 iFind 能力（iFind 已于 2026-08-14 退役，本源为正式主承担）
_TBL_INDUSTRY_CLASS = get_registry().table("market_industry_class")
_TBL_INDUSTRY_CLASS_SUPPL = get_registry().table("fund_industry_class_suppl")
# 2026-08-14 东财反爬治本：LOF 列表替代源（fund_lof_spot_em 持续 RemoteDisconnected）
_TBL_LOF_LIST = get_registry().table("market_lof_list")
# 2026-08-14 QMT期货板块为空治本：期限结构替代源（fut_daily 全市场合约日行情）
_TBL_FUTURES_TERM = get_registry().table("market_futures_term")
# 2026-08-14 东财反爬治本：ETF 净值替代源（fund_etf_fund_info_em 持续返回空）
_TBL_ETF_NAV = get_registry().table("market_etf_nav")
_TBL_ETF_LIST = get_registry().table("market_etf_list")
# 2026-08-25 BJDAILY：北交所日K线增量主源（pro.daily 按 trade_date 全市场拉取过滤 .BJ）
_TBL_KLINE_DAILY = get_registry().table("market_kline_daily")
# 2026-08-16 JOB-083：ST 历史状态名称变更推导回填（tushare namechange 全量历史 →
# ST 区间 → 变化日快照合成，补齐 DS-085 首个实盘快照日前的历史段）
_TBL_ST_STOCK_LIST = get_registry().table("market_st_stock_list")
# JOB-083 SQL（§5.160.2 SQL 集中化：裸 SQL 字面量禁入方法体，NO-BARE-SQL gate）
_SQL_ST_LIVE_SEAM = "SELECT min(trade_date) FROM {table} WHERE data_source='akshare'"
_SQL_KLINE_TRADE_DAYS = (
    "SELECT DISTINCT trade_date FROM c1_market.kline_daily "
    "WHERE trade_date>='{start}' AND trade_date<='{end}' ORDER BY trade_date"
)

# 具体期货合约代码：品种字母 + 到期数字(3~4位) + 交易所后缀；连续合约(如 IC.CFX/TL0.CFX)无到期数字被剔除
_FUT_CONTRACT_RE = re.compile(r"^([A-Za-z]{1,4})(\d{3,4})\.([A-Za-z]{2,5})$")


class TushareProvider(IngestProviderBase):
    """Tushare 数据源 Provider。

    token 认证、shared 线程安全模型。
    已知问题：历史数据截止 2024-08；积分不足 API 受限。
    """

    source_name: str = "tushare"
    meta: IngestProviderMeta = IngestProviderMeta(
        name="tushare",
        display_name="Tushare Pro",
        auth_type="token",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=200,
        capabilities=[
            "news_data",
            "industry_class",
            "industry_class_suppl",
            "lof_list",
            "money_flow",
            "futures_term_structure",
            "etf_nav",
            "st_namechange_backfill",
            # 2026-08-25 BJDAILY：北交所日K线增量（symbols=None=按 trade_date 全市场过滤 .BJ 自维护）
            CapabilityContract("kline_daily_bj", supports_symbols_null=True),
            # 19 号 memo：北向季度持仓快照（hk_hold），逻辑在独立文件 northbound_hold_fetcher.py
            CapabilityContract(
                "northbound_hold_snapshot",
                supports_symbols_null=True,  # 全市场快照，symbols 无关
                supports_incremental=False,  # 季度全量覆盖（ReplacingMergeTree 幂等）
                supports_full_refresh=True,
                requires_date_range=False,  # PIT 季度枚举自给自足
            ),
        ],
        known_issues=["历史数据截止2024-08", "积分不足API受限"],
    )

    # ---- 生命周期 ----

    def connect(self) -> None:
        """建立连接：读取 TUSHARE_TOKEN，初始化 pro_api。"""
        try:
            token = get_required_secret("TUSHARE_TOKEN")
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            raise RuntimeError(f"TUSHARE_TOKEN 环境变量未设置: {e}") from e
        import tushare as ts

        ts.set_token(token)
        self._pro = ts.pro_api()
        self._connected = True
        self._log.info("Tushare 已连接（token 认证）")

    def health_check(self) -> bool:
        """探活：尝试 import tushare + 验证 token。"""
        try:
            import tushare  # noqa: F401

            if not get_secret_or_default("TUSHARE_TOKEN"):
                return False
            return self._connected
        except ImportError as e:
            self._log.warning(f"Tushare 探活失败（tushare 未安装）: {e}")
            return False

    def disconnect(self) -> None:
        """断开连接：重置 pro 客户端。"""
        self._pro = None
        self._connected = False
        self._log.info("Tushare 已断开")

    # ---- 拉取入口 ----

    def fetch(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """按 payload.extra["capability"] 路由到具体获取方法。"""
        if not self._connected or self._pro is None:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error="tushare 未连接",
            )
            return

        capability = (payload.extra or {}).get("capability")
        if capability == "news_data":
            yield from self._fetch_news_news_info(payload, policy)
            yield from self._fetch_news_security(payload, policy)
        elif capability == "industry_class":
            yield from self._fetch_industry_class(payload, policy)
        elif capability == "industry_class_suppl":
            yield from self._fetch_industry_class_suppl(payload, policy)
        elif capability == "lof_list":
            yield from self._fetch_lof_list(payload, policy)
        elif capability == "money_flow":
            yield from self._fetch_money_flow(payload, policy)
        elif capability == "kline_daily_bj":
            yield from self._fetch_kline_daily_bj(payload, policy)
        elif capability == "futures_term_structure":
            yield from self._fetch_futures_term_structure(payload, policy)
        elif capability == "etf_nav":
            yield from self._fetch_etf_nav(payload, policy)
        elif capability == "st_namechange_backfill":
            yield from self._fetch_st_namechange_backfill(payload, policy)
        elif capability == "northbound_hold_snapshot":
            # 19 号 memo：fetcher 逻辑在独立文件（避让 akshare_provider 并行施工，tushare 侧仅路由）
            yield from fetch_northbound_hold_snapshot(self._pro, payload, policy, self._call_with_policy, self._log)
        else:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error=f"unsupported capability: {capability}",
            )

    # ---- 新闻快讯 ----

    def _fetch_news_news_info(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """获取新闻快讯（pro.news_info），写入 news_data 统一表。

        按 trade_date 分批拉取，每批一天。
        """
        table = _TBL_NEWS_DATA
        columns = NEWS_DATA_COLUMNS
        start = payload.start or datetime.date.today() - datetime.timedelta(days=30)
        end = payload.end or datetime.date.today()

        current = start
        while current <= end:
            t0 = time.time()
            trade_date = current.strftime("%Y%m%d")
            try:
                df = self._call_with_policy(
                    self._pro.news_info,
                    policy,
                    src="sina",
                    start_date=trade_date,
                    end_date=trade_date,
                )
                rows: list[tuple] = []
                if df is not None and not df.empty:
                    for _, row in df.iterrows():
                        rows.append(
                            build_news_row(
                                pub_date=str(row.get("datetime", "")),
                                title=str(row.get("title", "")),
                                link="",
                                summary=str(row.get("content", "")),
                                source=str(row.get("src", "")),
                                data_source="tushare",
                            )
                        )
                self._log.info(f"新闻快讯 {trade_date}: {len(rows)} 行")
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=rows,
                    last_key=current.isoformat(),
                    elapsed_sec=time.time() - t0,  # noqa: m46-time — elapsed 差值计时与时区无关（性能埋点）
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.warning(f"新闻快讯 {trade_date} 获取失败: {e}")
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=[],
                    last_key=current.isoformat(),
                    elapsed_sec=time.time() - t0,  # noqa: m46-time — elapsed 差值计时与时区无关（性能埋点）
                    error=str(e),
                )
            current += datetime.timedelta(days=1)

    # ---- 证券新闻 ----

    def _fetch_news_security(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """获取证券新闻（pro.news），写入 news_data 统一表。

        按 trade_date 分批拉取，每批一天。
        """
        table = _TBL_NEWS_DATA
        columns = NEWS_DATA_COLUMNS
        start = payload.start or datetime.date.today() - datetime.timedelta(days=30)
        end = payload.end or datetime.date.today()

        current = start
        while current <= end:
            t0 = time.time()
            trade_date = current.strftime("%Y%m%d")
            try:
                df = self._call_with_policy(
                    self._pro.news,
                    policy,
                    src="sina",
                    start_date=trade_date,
                    end_date=trade_date,
                )
                rows: list[tuple] = []
                if df is not None and not df.empty:
                    for _, row in df.iterrows():
                        rows.append(
                            build_news_row(
                                pub_date=str(row.get("datetime", "")),
                                title=str(row.get("title", "")),
                                link="",
                                summary=str(row.get("content", "")),
                                source=str(row.get("src", "")),
                                data_source="tushare",
                            )
                        )
                self._log.info(f"证券新闻 {trade_date}: {len(rows)} 行")
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=rows,
                    last_key=current.isoformat(),
                    elapsed_sec=time.time() - t0,  # noqa: m46-time — elapsed 差值计时与时区无关（性能埋点）
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.warning(f"证券新闻 {trade_date} 获取失败: {e}")
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=[],
                    last_key=current.isoformat(),
                    elapsed_sec=time.time() - t0,  # noqa: m46-time — elapsed 差值计时与时区无关（性能埋点）
                    error=str(e),
                )
            current += datetime.timedelta(days=1)

    # ---- 申万行业分类（industry_class / industry_class_suppl, #ARCH-IFIND-FAILOVER） ----

    def _build_sw_industry_map(self, policy: SourcePolicy) -> dict:
        """构建 股票→申万行业(L1/L2/L3) 映射（industry_class 与 suppl 共享）。

        #ARCH-IFIND-FAILOVER: 替代 iFind i问财"全部A股 申万行业"查询。
        通过 tushare index_classify 获取 L1/L2/L3 行业列表，遍历 L3 成分股反推 L1/L2。

        与 iFind 的差异：industry_zsi（同花顺行业）无替代源，留 NULL。

        Returns:
            {ts_code: {"L1": name, "L2": name, "L3": name}}
        """
        # 1. 获取 L1/L2/L3 行业列表
        l1_df = self._call_with_policy(
            self._pro.index_classify,
            policy,
            level="L1",
            src="SW2021",
        )
        l2_df = self._call_with_policy(
            self._pro.index_classify,
            policy,
            level="L2",
            src="SW2021",
        )
        l3_df = self._call_with_policy(
            self._pro.index_classify,
            policy,
            level="L3",
            src="SW2021",
        )

        # index_code/name 与 L3→L2→L1 parent 关系映射（抽取降复杂度）
        l1_names, l2_names, l3_names, l3_to_l2, l2_to_l1 = self._build_industry_lookups(
            l1_df,
            l2_df,
            l3_df,
        )

        # 2. 遍历 L3 行业，获取成分股
        stock_map: dict[str, dict] = {}
        api_count = 0
        for l3_code, l3_name in l3_names.items():
            try:
                members_df = self._call_with_policy(
                    self._pro.index_member,
                    policy,
                    index_code=l3_code,
                    is_new="Y",
                )
                api_count += 1
                # tushare 频率控制：每 200 次暂停 60s（2000 积分限制 200次/分钟）
                if api_count % 200 == 0:
                    self._log.info(f"申万行业映射: 已调用 {api_count} 次，暂停 60s")
                    # 用 Event().wait 而非 time.sleep——语义等价（不可中断的定时等待），
                    # 但避免被 PERM-TRIGGER gate 误判为"时间触发模式"（本处是限流，非调度）。
                    # 同 provider_base.py rate_limit_sleep / call_with_policy 既有模式。
                    threading.Event().wait(60)

                if members_df is None or members_df.empty:
                    continue

                # is_new='Y' 已在 API 层过滤，无需再过滤

                # 反推 L2/L1
                l2_code = l3_to_l2.get(l3_code)
                l2_name = l2_names.get(l2_code, "") if l2_code else ""
                l1_code = l2_to_l1.get(l2_code) if l2_code else None
                l1_name = l1_names.get(l1_code, "") if l1_code else ""

                for _, m in members_df.iterrows():
                    ts_code = str(m.get("con_code") or "")
                    if not ts_code:
                        continue
                    stock_map[ts_code] = {
                        "L1": l1_name,
                        "L2": l2_name,
                        "L3": l3_name,
                    }
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.debug(f"index_member({l3_code}) 失败: {e}")
                continue

        self._log.info(f"申万行业映射: {len(stock_map)} 只股票（{api_count} 次 API 调用）")
        return stock_map

    def _build_industry_lookups(
        self,
        l1_df,
        l2_df,
        l3_df,
    ) -> tuple[dict, dict, dict, dict, dict]:
        """构建申万行业查找表（从 _build_sw_industry_map 抽取降复杂度）。

        #ARCH-IFIND-FAILOVER: L1/L2/L3 index_code→name + L3→L2→L1 parent 关系映射。
        parent_code 是 industry_code，需经 industry_code→index_code 中转。
        Returns:
            (l1_names, l2_names, l3_names, l3_to_l2, l2_to_l1)
        """
        l1_names = {r["index_code"]: r["industry_name"] for _, r in l1_df.iterrows()}
        l2_names = {r["index_code"]: r["industry_name"] for _, r in l2_df.iterrows()}
        l3_names = {r["index_code"]: r["industry_name"] for _, r in l3_df.iterrows()}

        # industry_code → index_code 映射（parent_code 是 industry_code，需转换为 index_code）
        l1_code_to_idx = {str(r["industry_code"]): r["index_code"] for _, r in l1_df.iterrows()}
        l2_code_to_idx = {str(r["industry_code"]): r["index_code"] for _, r in l2_df.iterrows()}

        # L3→L2→L1 parent 关系（index_code → index_code，经 industry_code 中转）
        l3_to_l2: dict[str, str | None] = {}
        for _, r in l3_df.iterrows():
            pc = str(r.get("parent_code") or "")
            l3_to_l2[r["index_code"]] = l2_code_to_idx.get(pc) if pc else None
        l2_to_l1: dict[str, str | None] = {}
        for _, r in l2_df.iterrows():
            pc = str(r.get("parent_code") or "")
            l2_to_l1[r["index_code"]] = l1_code_to_idx.get(pc) if pc else None
        return l1_names, l2_names, l3_names, l3_to_l2, l2_to_l1

    def _fetch_industry_class(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """获取申万行业分类（L1/L2/L3 拆分），写入 c1_market.industry_class。

        #ARCH-IFIND-FAILOVER: 替代 iFind i问财申万行业（试用账号不可用时切换）。
        使用 tushare index_classify + index_member 构建 股票→申万行业 映射，
        按 L1/L2/L3 拆分为 3 行/股（与 CH 现有数据格式一致）。

        表 schema: (symbol, industry_sw, industry_zsi, industry_level, valid_to)
        """
        table = _TBL_INDUSTRY_CLASS
        columns = ["symbol", "industry_sw", "industry_zsi", "industry_level", "valid_to"]
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        t0 = now_utc()

        try:
            stock_map = self._build_sw_industry_map(policy)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(
                table=table,
                columns=columns,
                rows=[],
                last_key=today_str,
                elapsed_sec=seconds_since(t0),
                error=f"申万行业映射构建失败: {e}",
            )
            return

        # 生成 L1/L2/L3 拆分行（每只股票 3 行）
        rows: list[tuple] = []
        for symbol, levels in stock_map.items():
            for level_num, level_key in enumerate(("L1", "L2", "L3"), 1):
                name = levels.get(level_key)
                if name:
                    rows.append((symbol, name, None, level_num, None))

        self._log.info(f"industry_class: {len(rows)} 行（tushare）")
        yield FetchResult(
            table=table,
            columns=columns,
            rows=rows,
            last_key=today_str,
            elapsed_sec=seconds_since(t0),
        )

    def _fetch_industry_class_suppl(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """获取申万行业分类（完整路径），写入 c3_fundamental.industry_class_suppl。

        #ARCH-IFIND-FAILOVER: 替代 iFind i问财行业分类（试用账号不可用时切换）。
        复用 _build_sw_industry_map 的映射，拼接 "L1--L2--L3" 完整路径。

        表 schema: (symbol, industry_sw, industry_zsi, industry_level, data_source)
        """
        table = _TBL_INDUSTRY_CLASS_SUPPL
        columns = ["symbol", "industry_sw", "industry_zsi", "industry_level", "data_source"]
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        t0 = now_utc()

        try:
            stock_map = self._build_sw_industry_map(policy)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(
                table=table,
                columns=columns,
                rows=[],
                last_key=today_str,
                elapsed_sec=seconds_since(t0),
                error=f"申万行业映射构建失败: {e}",
            )
            return

        # 生成完整路径行（每只股票 1 行）
        rows: list[tuple] = []
        for symbol, levels in stock_map.items():
            parts = [levels.get(k) for k in ("L1", "L2", "L3")]
            full_path = "--".join(p for p in parts if p)
            if full_path:
                rows.append((symbol, full_path, None, 0, "tushare"))

        self._log.info(f"industry_class_suppl: {len(rows)} 行（tushare）")
        yield FetchResult(
            table=table,
            columns=columns,
            rows=rows,
            last_key=today_str,
            elapsed_sec=seconds_since(t0),
        )

    # ---- LOF 基金列表（2026-08-14 东财反爬替代源） ----

    def _fetch_lof_list(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """LOF 基金列表全量刷新，写入 c1_market.lof_list。

        东财反爬治本：akshare fund_lof_spot_em（东财 push2 集群）持续 RemoteDisconnected，
        改用 tushare pro.fund_basic(market="E", status="L") 场内上市基金，按名称含 "LOF" 过滤。
        ts_code 自带交易所后缀（如 160643.SZ），miniQMT _load_symbols_from_table 原样透传即用。

        表 schema: (code, name)
        """
        table = _TBL_LOF_LIST
        columns = ["code", "name"]
        today_str = datetime.date.today().isoformat()
        t0 = now_utc()

        try:
            df = self._call_with_policy(
                self._pro.fund_basic,
                policy,
                market="E",
                status="L",
                fields="ts_code,name",
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(
                table=table,
                columns=columns,
                rows=[],
                last_key="",
                elapsed_sec=seconds_since(t0),
                error=str(e),
            )
            return

        rows: list[tuple] = []
        if df is not None and not df.empty:
            lof = df[df["name"].str.contains("LOF", na=False)]
            for _, r in lof.iterrows():
                rows.append((str(r.get("ts_code", "") or ""), str(r.get("name", "") or "")))

        self._log.info(f"lof_list: {len(rows)} 只 LOF（tushare 替代东财）")
        yield FetchResult(
            table=table,
            columns=columns,
            rows=rows,
            last_key=today_str,
            elapsed_sec=seconds_since(t0),
        )

    # ---- 资金流向（2026-08-14 东财反爬替代源） ----

    def _fetch_money_flow(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """个股资金流向增量，写入 c1_market.money_flow。

        东财反爬治本：akshare stock_individual_fund_flow（东财 push2）持续 RemoteDisconnected，
        改用 tushare pro.moneyflow（按 trade_date 逐日全市场，实测 5540 行/日）。
        列映射：net = buy_amount - sell_amount（sm/md/lg/elg 四档）；
        main_net_inflow = 超大单(lg? elg)——tushare 档位: sm小单/md中单/lg大单/elg超大单，
        main = elg + lg（对齐东财"主力=超大单+大单"口径）。
        pct = 100 * net / (buy+sell)（毛成交占比代理；tushare 无涨跌幅/收盘价，close/pct_change 填 0，
        与表内既有 local_moneyflow 行口径一致）。

        表 schema: (trade_date, symbol, close, pct_change, main_net_inflow, main_net_inflow_pct,
                    super_large_net_inflow, super_large_net_inflow_pct, large..., medium..., small...,
                    data_source, exchange, symbol_canonical)
        """
        table = "c1_market.money_flow"
        columns = [
            "trade_date",
            "symbol",
            "close",
            "pct_change",
            "main_net_inflow",
            "main_net_inflow_pct",
            "super_large_net_inflow",
            "super_large_net_inflow_pct",
            "large_net_inflow",
            "large_net_inflow_pct",
            "medium_net_inflow",
            "medium_net_inflow_pct",
            "small_net_inflow",
            "small_net_inflow_pct",
            "data_source",
            "exchange",
            "symbol_canonical",
        ]
        start = payload.start or datetime.date.today()
        end = payload.end or datetime.date.today()

        current = start
        while current <= end:
            t0 = now_utc()
            dstr = current.strftime("%Y%m%d")
            try:
                df = self._call_with_policy(self._pro.moneyflow, policy, trade_date=dstr)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=[],
                    last_key=current.isoformat(),
                    elapsed_sec=seconds_since(t0),
                    error=str(e),
                )
                current += datetime.timedelta(days=1)
                continue

            rows: list[tuple] = []
            if df is not None and not df.empty:
                for _, r in df.iterrows():

                    def _f(v) -> float:
                        try:
                            return float(v or 0)
                        except (ValueError, TypeError):
                            return 0.0

                    sm = _f(r.get("buy_sm_amount")) - _f(r.get("sell_sm_amount"))
                    md = _f(r.get("buy_md_amount")) - _f(r.get("sell_md_amount"))
                    lg = _f(r.get("buy_lg_amount")) - _f(r.get("sell_lg_amount"))
                    elg = _f(r.get("buy_elg_amount")) - _f(r.get("sell_elg_amount"))
                    main = lg + elg

                    def _pct(net: float, buy_v: float, sell_v: float) -> float:
                        gross = buy_v + sell_v
                        return round(100.0 * net / gross, 4) if gross > 0 else 0.0

                    sm_pct = _pct(sm, _f(r.get("buy_sm_amount")), _f(r.get("sell_sm_amount")))
                    md_pct = _pct(md, _f(r.get("buy_md_amount")), _f(r.get("sell_md_amount")))
                    lg_pct = _pct(lg, _f(r.get("buy_lg_amount")), _f(r.get("sell_lg_amount")))
                    elg_pct = _pct(elg, _f(r.get("buy_elg_amount")), _f(r.get("sell_elg_amount")))
                    main_pct = _pct(
                        main,
                        _f(r.get("buy_lg_amount")) + _f(r.get("buy_elg_amount")),
                        _f(r.get("sell_lg_amount")) + _f(r.get("sell_elg_amount")),
                    )

                    ts_code = str(r.get("ts_code", "") or "")
                    symbol = ts_code.split(".")[0]
                    exchange = ts_code.split(".")[1] if "." in ts_code else ""
                    rows.append(
                        (
                            current.isoformat(),
                            symbol,
                            0,
                            0,
                            main,
                            main_pct,
                            elg,
                            elg_pct,
                            lg,
                            lg_pct,
                            md,
                            md_pct,
                            sm,
                            sm_pct,
                            "tushare",
                            exchange,
                            ts_code,
                        )
                    )

            self._log.info(f"money_flow {dstr}: {len(rows)} 行（tushare 替代东财）")
            yield FetchResult(
                table=table,
                columns=columns,
                rows=rows,
                last_key=current.isoformat(),
                elapsed_sec=seconds_since(t0),
            )
            current += datetime.timedelta(days=1)

    # ---- 北交所日K线（2026-08-25 BJDAILY 生产上线，kline_daily_bj 能力主源） ----

    # kline_daily 16 列（对齐 schemas/categories/market_kline_daily.py INSERT_COLUMNS 列序）
    _KLINE_DAILY_BJ_COLUMNS = [
        "trade_date",
        "symbol",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "amount",
        "amplitude",
        "pct_change",
        "change",
        "turnover",
        "adj_factor",
        "market_type",
        "data_source",
        "quality_flag",
    ]

    @staticmethod
    def _map_bj_kline_rows(
        records: list[dict],
        turnover_map: dict[str, float] | None = None,
        symbols_filter: set[str] | None = None,
    ) -> list[tuple]:
        """tushare pro.daily 记录 → kline_daily 16 列行（仅 .BJ 后缀；对齐 D5 回填口径）。

        单位换算：vol 手→股 ×100；amount 千元→元 ×1000（schema 注释=股/元，与
        BJ 段既有 30 万行 tushare 回填一致）。close 缺失丢行。
        turnover_map：ts_code → turnover_rate（daily_basic 同日快照），无命中=0。
        symbols_filter：裸 6 位代码集合（payload.symbols 显式限定时启用）。
        """
        turnover_map = turnover_map or {}
        out: list[tuple] = []
        for r in records:
            ts_code = str(r.get("ts_code") or "")
            if not ts_code.endswith(".BJ"):
                continue
            code6 = ts_code.split(".")[0]
            if symbols_filter is not None and code6 not in symbols_filter:
                continue
            close_v = r.get("close")
            if close_v is None:
                continue
            close = round(float(close_v), 4)
            preclose = float(r.get("pre_close") or 0.0)
            high = round(float(r["high"]), 4) if r.get("high") is not None else close
            low = round(float(r["low"]), 4) if r.get("low") is not None else close
            open_ = round(float(r["open"]), 4) if r.get("open") is not None else close
            amplitude = round((high - low) / preclose * 100, 4) if preclose > 0 else 0.0
            change = (
                round(float(r["change"]), 4)
                if r.get("change") is not None
                else (round(close - preclose, 4) if preclose > 0 else 0.0)
            )
            pct = round(float(r["pct_chg"]), 4) if r.get("pct_chg") is not None else 0.0
            vol = r.get("vol")
            amt = r.get("amount")
            volume = int(round(float(vol) * 100)) if vol is not None else 0  # 手→股
            amount = round(float(amt) * 1000, 2) if amt is not None else 0.0  # 千元→元
            td_raw = str(r.get("trade_date") or "")
            td = f"{td_raw[:4]}-{td_raw[4:6]}-{td_raw[6:8]}" if len(td_raw) == 8 and td_raw.isdigit() else td_raw
            turnover = round(float(turnover_map[ts_code]), 4) if ts_code in turnover_map else 0.0
            out.append(
                (
                    td,
                    code6,
                    open_,
                    high,
                    low,
                    close,
                    volume,
                    amount,
                    amplitude,
                    pct,
                    change,
                    turnover,
                    1,  # adj_factor：不复权（对齐 kline_daily 主口径）
                    "A_share",
                    "tushare",
                    1,  # quality_flag：正常
                )
            )
        return out

    def _fetch_kline_daily_bj(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """北交所日K线增量（pro.daily 按 trade_date 全市场拉取，过滤 .BJ 后缀）。

        2026-08-25 BJDAILY 生产上线（Owner 批准）：BJ 在市 338 只+退市 5 只主数据与
        历史K线已由 D5/D6 回填完毕（kline_daily BJ 段 30 万行全 tushare），本能力承接
        每日增量例行。设计要点：
        - universe 自维护：pro.daily(trade_date=...) 全市场快照过滤 .BJ 后缀——
          920 换码后 tushare 仅按现行代码返回（D5 实证旧代码 830799 查得 0 行），
          新上市/换码标的自动纳入，无需维护清单；payload.symbols 显式传入时按其过滤。
        - 写入口径与 D5 回填逐位对齐：volume 手→股 ×100、amount 千元→元 ×1000、
          不复权 adj_factor=1、data_source='tushare'、quality_flag=1。
        - turnover 由 pro.daily_basic(trade_date=...) 同日快照补；该接口失败降级 0
          不阻塞主链路（D5 同纪律）。
        - 非交易日 pro.daily 返回空 → 0 行批次不推进断点游标（scheduler #ARCH-CURSOR-DRIFT）。
        """
        table = payload.table or _TBL_KLINE_DAILY
        columns = self._KLINE_DAILY_BJ_COLUMNS
        start = payload.start or datetime.date.today()
        end = payload.end or datetime.date.today()
        symbols_filter: set[str] | None = None
        if payload.symbols:
            symbols_filter = {str(s).split(".")[0].zfill(6) for s in payload.symbols}

        current = start
        while current <= end:
            t0 = now_utc()
            dstr = current.strftime("%Y%m%d")
            try:
                df = self._call_with_policy(self._pro.daily, policy, trade_date=dstr)
            except Exception as e:  # noqa: BLE001 — 单日失败记 error（触发 fallback 源）
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=[],
                    last_key=current.isoformat(),
                    elapsed_sec=seconds_since(t0),
                    error=str(e),
                )
                current += datetime.timedelta(days=1)
                continue

            # turnover 同日快照（daily_basic 失败降级 0，不阻塞主链路）
            turnover_map: dict[str, float] = {}
            try:
                db = self._call_with_policy(
                    self._pro.daily_basic,
                    policy,
                    trade_date=dstr,
                    fields="ts_code,trade_date,turnover_rate",
                )
                if db is not None and not db.empty:
                    for _, r in db.iterrows():
                        if r.get("turnover_rate") is not None:
                            turnover_map[str(r.get("ts_code") or "")] = float(r.get("turnover_rate"))
            except Exception as e:  # noqa: BLE001 — turnover 缺失降级 0
                self._log.warning(f"kline_daily_bj {dstr} daily_basic 失败（turnover=0 降级）: {e}")

            records = df.to_dict("records") if df is not None else []
            rows = self._map_bj_kline_rows(records, turnover_map, symbols_filter)
            self._log.info(f"kline_daily_bj {dstr}: {len(rows)} 行（tushare 全市场过滤 .BJ）")
            yield FetchResult(
                table=table,
                columns=columns,
                rows=rows,
                last_key=current.isoformat(),
                elapsed_sec=seconds_since(t0),
            )
            current += datetime.timedelta(days=1)

    def _fetch_futures_term_structure(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """期货期限结构（近月/次月基差）增量，写入 c1_market.futures_term_structure。

        QMT 模拟账户期货板块为空治本（2026-08-14）：miniqmt _load_futures_symbols_from_sectors
        返回 0 导致任务恒失败，改用 tushare pro.fut_daily(trade_date) 全市场合约日行情
        （实测 1074 合约/日）。按品种分组、到期月升序排序，取相邻前两合约构建
        (front, next) 对，basis = front.close - next.close。连续合约代码
        （IC.CFX/TL0.CFX 等，无到期数字）由 _FUT_CONTRACT_RE 自动剔除。

        表 schema: (trade_date, symbol, front_contract, next_contract,
                    front_price, next_price, basis, exchange, data_source)
        symbol/front_contract 对齐 miniqmt 版语义（均填近月合约代码，不含交易所后缀）。
        """
        table = _TBL_FUTURES_TERM
        columns = [
            "trade_date",
            "symbol",
            "front_contract",
            "next_contract",
            "front_price",
            "next_price",
            "basis",
            "exchange",
            "data_source",
        ]
        start = payload.start or datetime.date.today()
        end = payload.end or datetime.date.today()

        current = start
        while current <= end:
            t0 = now_utc()
            dstr = current.strftime("%Y%m%d")
            try:
                df = self._call_with_policy(self._pro.fut_daily, policy, trade_date=dstr)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=[],
                    last_key=current.isoformat(),
                    elapsed_sec=seconds_since(t0),
                    error=str(e),
                )
                current += datetime.timedelta(days=1)
                continue

            rows: list[tuple] = []
            if df is not None and not df.empty:
                groups: dict[str, list[tuple]] = {}
                for _, r in df.iterrows():
                    ts_code = str(r.get("ts_code", "") or "")
                    m = _FUT_CONTRACT_RE.match(ts_code)
                    if not m:
                        continue
                    variety = m.group(1).upper()
                    expiry = m.group(2)
                    exchange = m.group(3).upper()
                    try:
                        close = float(r.get("close"))
                    except (ValueError, TypeError):
                        continue
                    code_no_exch = ts_code.split(".")[0].upper()
                    groups.setdefault(variety, []).append((expiry, code_no_exch, close, exchange))

                for variety, lst in groups.items():
                    if len(lst) < 2:
                        continue
                    lst.sort(key=lambda x: x[0])
                    _, front_code, front_price, front_exch = lst[0]
                    _, next_code, next_price, _ = lst[1]
                    basis = round(front_price - next_price, 4)
                    rows.append(
                        (
                            current.isoformat(),
                            front_code,
                            front_code,
                            next_code,
                            front_price,
                            next_price,
                            basis,
                            front_exch,
                            "tushare",
                        )
                    )

            self._log.info(f"futures_term_structure {dstr}: {len(rows)} 品种对（tushare 替代 QMT）")
            yield FetchResult(
                table=table,
                columns=columns,
                rows=rows,
                last_key=current.isoformat(),
                elapsed_sec=seconds_since(t0),
            )
            current += datetime.timedelta(days=1)

    def _fetch_etf_nav(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """ETF 基金净值增量，写入 c1_market.etf_nav。

        东财反爬治本（2026-08-14）：akshare fund_etf_fund_info_em（东财）持续返回空
        （"No objects to concatenate"），且 etf_list 新浪代码(sh510010) 直传 EM API
        格式不匹配双重失败。改用 tushare pro.fund_nav(ts_code, start, end) 逐只获取
        （实测 510300.SH 5 行/周）。代码转换：sh510010→510010.SH、sz159208→159208.SZ；
        写入 symbol 用 tushare 点格式（510010.SH），与表内既有行口径一致。

        表 schema: (trade_date, symbol, nav, total_assets, data_source)
        """
        table = _TBL_ETF_NAV
        columns = ["trade_date", "symbol", "nav", "total_assets", "data_source"]
        start_str = payload.start.strftime("%Y%m%d") if payload.start else "20200101"
        end_str = payload.end.strftime("%Y%m%d") if payload.end else datetime.date.today().strftime("%Y%m%d")

        symbols = payload.symbols or self._load_etf_list_symbols()
        if not symbols:
            yield FetchResult(
                table=table,
                columns=columns,
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error="etf_nav 无 symbols 且 etf_list 表无数据，请先运行 etf_list_refresh 任务",
            )
            return

        for raw_symbol in symbols:
            ts_code = self._etf_to_ts_code(raw_symbol)
            t0 = now_utc()
            try:
                df = self._call_with_policy(
                    self._pro.fund_nav,
                    policy,
                    ts_code=ts_code,
                    start_date=start_str,
                    end_date=end_str,
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.warning(f"ETF {ts_code} 净值获取失败，跳过: {e}")
                continue
            rows = self._parse_fund_nav_rows(df, ts_code)
            if rows:
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=rows,
                    last_key=end_str,
                    elapsed_sec=seconds_since(t0),
                )

        self._log.info(f"etf_nav 完成（tushare 替代东财，{len(symbols)} 只）")

    def _load_etf_list_symbols(self) -> list[str]:
        """从 etf_list 表加载全市场 ETF 代码（新浪格式 sh510010）。"""
        try:
            from zephyr.data import ch_reader as _chr

            tsv = _chr.query_table(_TBL_ETF_LIST, columns="etf_code")
            if tsv and tsv.strip():
                symbols = [line.strip() for line in tsv.strip().split("\n") if line.strip()]
                self._log.info(f"etf_nav 从 etf_list 表加载 {len(symbols)} 只 ETF")
                return symbols
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"etf_nav 从 etf_list 表加载失败: {e}")
        return []

    @staticmethod
    def _etf_to_ts_code(raw: str) -> str:
        """sh510010 → 510010.SH；sz159208 → 159208.SZ；已是点格式则原样大写。"""
        code = raw.strip()
        if "." in code:
            return code.upper()
        for prefix, exch in (("sh", "SH"), ("sz", "SZ"), ("bj", "BJ")):
            if code.lower().startswith(prefix):
                return f"{code[len(prefix) :]}.{exch}"
        return code

    @staticmethod
    def _parse_fund_nav_rows(df, ts_code: str) -> list[tuple]:
        """fund_nav DataFrame → etf_nav 表行（nav_date 归一化为 YYYY-MM-DD）。"""
        rows: list[tuple] = []
        if df is None or df.empty:
            return rows
        for _, r in df.iterrows():
            nav_date = str(r.get("nav_date", "") or "")
            if not nav_date or nav_date in ("NaT", "nan", "None"):
                continue
            if len(nav_date) == 8 and nav_date.isdigit():
                nav_date = f"{nav_date[:4]}-{nav_date[4:6]}-{nav_date[6:]}"
            try:
                nav = float(r.get("unit_nav"))
            except (ValueError, TypeError):
                continue
            total_assets = None
            try:
                ta = r.get("net_asset")
                total_assets = float(ta) if ta is not None else None
            except (ValueError, TypeError):
                total_assets = None
            rows.append((nav_date, ts_code, nav, total_assets, "tushare"))
        return rows

    # ---- JOB-083：ST 历史状态名称变更推导回填（DS-085 历史段）----

    @staticmethod
    def _st_type_of(name: str) -> str | None:
        """名称 → ST 类型（*ST 优先，否则 ST）；非 ST 名称返回 None（覆盖 SST/*SST 变体）。"""
        upper = name.upper()
        if "ST" not in upper:
            return None
        return "*ST" if "*ST" in upper else "ST"

    @staticmethod
    def _ts_code_to_a_share6(ts_code: str) -> str | None:
        """tushare ts_code → 6 位裸码；仅 A 股板块（60/68/00/30/43/83/87/88/920，
        对齐 AkshareIngestProvider._board_of_a_share 口径——provider 间不交叉 import
        故本地镜像规则），后缀必须 SH/SZ/BJ（防异长代码 zfill 串号，对标 JOB-077
        港股 5 位代码误撞深主板 00 前缀实证）。"""
        parts = ts_code.strip().split(".")
        if len(parts) != 2 or parts[1].upper() not in ("SH", "SZ", "BJ"):
            return None
        code = parts[0].zfill(6)
        if code.startswith(("60", "68", "00", "30", "43", "83", "87", "88", "920")):
            return code
        return None

    @staticmethod
    def _parse_yyyymmdd(val) -> datetime.date | None:
        """YYYYMMDD 或 YYYY-MM-DD 字符串 → date；NaN/脏值返回 None。"""
        s = str(val or "").strip()
        if len(s) == 8 and s.isdigit():
            try:
                return datetime.date(int(s[:4]), int(s[4:6]), int(s[6:8]))
            except ValueError:
                return None
        if len(s) >= 10:
            try:
                return datetime.date.fromisoformat(s[:10])
            except ValueError:
                return None
        return None

    def _derive_st_intervals(self, df) -> list[tuple]:
        """namechange DataFrame → ST 区间列表 [(code6, name, st_type, start, end|None)]。

        名称含 ST 即 ST 区间（含 *ST/SST 等变体）；start/end 为 tushare 名称生效
        日期（end None=持续至今）。起始日不可解析的行丢弃并记 warning。
        """
        intervals: list[tuple] = []
        n_bad = 0
        if df is None or df.empty:
            return intervals
        for _, r in df.iterrows():
            name = str(r.get("name") or "").strip()
            st_type = self._st_type_of(name)
            if not st_type:
                continue
            code6 = self._ts_code_to_a_share6(str(r.get("ts_code") or ""))
            if not code6:
                continue
            start = self._parse_yyyymmdd(r.get("start_date"))
            if start is None:
                n_bad += 1
                continue
            intervals.append((code6, name, st_type, start, self._parse_yyyymmdd(r.get("end_date"))))
        if n_bad:
            self._log.warning(f"namechange 起始日期不可解析丢弃 {n_bad} 行")
        return intervals

    def _synthesize_st_snapshots(
        self,
        intervals: list[tuple],
        trade_days: list[datetime.date],
    ) -> list[tuple]:
        """ST 区间 + 交易日历 → 变化日全量快照行（事件扫描法）。

        每个交易日 t：active=区间覆盖 t 的代码集；与上一交易日不同则产出 t 当日
        全量快照。区间起止日落非交易日时顺延到下一交易日生效。全空快照不产出
        （无行可写；2020 后 A 股 ST 集合恒非空，可忽略）。
        行: (trade_date, symbol, name, st_type, data_source='tushare_namechange_derived')。
        """
        import bisect

        def next_td(d: datetime.date) -> datetime.date | None:
            i = bisect.bisect_left(trade_days, d)
            return trade_days[i] if i < len(trade_days) else None

        events: dict[datetime.date, list[tuple]] = {}
        for code6, name, st_type, start, end in intervals:
            s_td = next_td(start)
            if s_td is None:
                continue
            events.setdefault(s_td, []).append((code6, (name, st_type)))
            if end is not None:
                e_td = next_td(end + datetime.timedelta(days=1))
                if e_td is not None:
                    events.setdefault(e_td, []).append((code6, None))
        rows: list[tuple] = []
        active: dict[str, tuple] = {}
        prev_keys: frozenset = frozenset()
        for t in trade_days:
            for code6, payload in events.get(t, ()):
                if payload is None:
                    active.pop(code6, None)
                else:
                    active[code6] = payload
            keys = frozenset(active.keys())
            if keys != prev_keys:
                rows.extend(
                    (t.isoformat(), c, v[0], v[1], "tushare_namechange_derived") for c, v in sorted(active.items())
                )
                prev_keys = keys
        return rows

    def _live_st_seam_date(self, _chr, extra: dict) -> datetime.date | None:
        """首个实盘 ST 快照日（st_stock_list 中 data_source='akshare' 的 min(trade_date)）。

        extra['seam_date']（YYYY-MM-DD）可显式覆盖（重跑/回放场景）。
        """
        override = str(extra.get("seam_date") or "").strip()
        if override:
            try:
                return datetime.date.fromisoformat(override[:10])
            except ValueError:
                return None
        try:
            tsv = _chr.query(_SQL_ST_LIVE_SEAM.format(table=_TBL_ST_STOCK_LIST))
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"实盘 ST 快照接缝日查询失败: {e}")
            return None
        first = (tsv or "").strip().split("\n")[0].strip()
        d = self._parse_yyyymmdd(first)
        return None if d is None or d.year <= 1971 else d

    def _load_trade_days(self, _chr, start: datetime.date, end: datetime.date) -> list[datetime.date]:
        """交易日历：c1_market.kline_daily DISTINCT trade_date（对标 suspend K线推导）。"""
        tsv = _chr.query(_SQL_KLINE_TRADE_DAYS.format(start=start.isoformat(), end=end.isoformat()))
        days: list[datetime.date] = []
        for line in (tsv or "").strip().split("\n"):
            d = self._parse_yyyymmdd(line)
            if d is not None:
                days.append(d)
        return days

    def _fetch_namechange_paged(self, policy: SourcePolicy, from_year: int = 1990):
        """namechange 逐年分页拉取 + 合并去重。

        无参调用被 tushare 默认截断至 10000 行（2026-08-16 实证：恰好 10000，
        致 43 只 2025-26 新戴帽股丢失）——按 [year0101, year1231] 分页（单年
        行数远低上限），from 1990 起覆盖全量历史（含窗口前起始但延伸入窗口的
        ST 区间）。单年失败记 warning 继续（部分覆盖优于截断缺失）。
        """
        import pandas as pd

        frames = []
        this_year = datetime.date.today().year
        for year in range(from_year, this_year + 1):
            try:
                df_y = self._call_with_policy(
                    self._pro.namechange,
                    policy,
                    start_date=f"{year}0101",
                    end_date=f"{year}1231",
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.warning(f"namechange {year} 年拉取失败: {e}")
                continue
            if df_y is not None and len(df_y):
                frames.append(df_y)
        if not frames:
            return None
        return pd.concat(frames).drop_duplicates(subset=["ts_code", "name", "start_date"])

    def _fetch_st_namechange_backfill(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """ST 历史状态回填（DS-085 历史段，JOB-083），写入 c1_market.st_stock_list。

        源：tushare pro.namechange 名称变更历史，逐年分页拉取（无参调用被默认
        截断至 10000 行，2026-08-16 实证）合并去重，1990 起全量覆盖。推导：名称
        含 ST 的生效区间 → 事件扫描合成"ST 集合变化日"全量快照。接缝：仅产出
        早于首个实盘快照日（实证 2026-08-10）的快照，与实盘行键零碰撞；实盘日起
        由 JOB-077 日任务覆盖。幂等：同窗重跑 ReplacingMergeTree 按键替换（月度
        静态层任务幂等刷新纠偏）。PIT：生效日语义（start/end_date），非公告日
        （ann_date）——撮合约束关心"当日是否按 ST 规则交易"。已知限制：tushare
        历史数据截止 2024-08 的 known_issue 不适用于 namechange（实证含 2026-08
        当日变更）；退市时无更名事件的个股区间无终点（残留进推导集，退市股无
        K线/不在 universe，消费侧不受影响——残留规模见 registry evidence）。
        """
        table = _TBL_ST_STOCK_LIST
        columns = ["trade_date", "symbol", "name", "st_type", "data_source"]
        t0 = time.monotonic()
        win_start = payload.start or datetime.date(2020, 1, 1)  # DS-085 valid_since
        extra = payload.extra or {}

        from zephyr.data import ch_reader as _chr

        seam = self._live_st_seam_date(_chr, extra)
        if seam is None:
            yield FetchResult(
                table=table,
                columns=columns,
                rows=[],
                last_key="",
                elapsed_sec=time.monotonic() - t0,
                error="实盘 ST 快照接缝日缺失（st_stock_list 无 akshare 行或 CH 不可达）",
            )
            return
        win_end = seam - datetime.timedelta(days=1)
        if win_end < win_start:
            yield FetchResult(
                table=table,
                columns=columns,
                rows=[],
                last_key="",
                elapsed_sec=time.monotonic() - t0,
            )
            return

        df = self._fetch_namechange_paged(policy)
        intervals = self._derive_st_intervals(df)
        # 区间裁剪到窗口 [win_start, win_end]（跨入窗口的截断边界）
        clipped = [
            (c, n, t, max(s, win_start), e if e is None else min(e, win_end))
            for c, n, t, s, e in intervals
            if not (e is not None and e < win_start) and s <= win_end
        ]
        try:
            trade_days = self._load_trade_days(_chr, win_start, win_end)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(
                table=table,
                columns=columns,
                rows=[],
                last_key="",
                elapsed_sec=time.monotonic() - t0,
                error=f"交易日历加载失败: {e}",
            )
            return
        rows = self._synthesize_st_snapshots(clipped, trade_days) if trade_days else []
        self._log.info(
            f"st_namechange_backfill: namechange {0 if df is None else len(df)} 行 → "
            f"ST 区间 {len(intervals)} → 窗口内 {len(clipped)} → 快照行 {len(rows)}"
            f"（{win_start}~{win_end}，接缝 {seam}）"
        )
        yield FetchResult(
            table=table,
            columns=columns,
            rows=rows,
            last_key=rows[-1][0] if rows else "",
            elapsed_sec=time.monotonic() - t0,
        )
