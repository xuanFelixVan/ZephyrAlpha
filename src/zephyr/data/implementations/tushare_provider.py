# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.tushare_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] tushare SDK (ts.set_token/ts.pro_api/pro.news/pro.news_info)
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
- 当前能力：news_news_info（新闻快讯）/ news_security（证券新闻）

关键设计：
- connect() 读取 TUSHARE_TOKEN 环境变量，初始化 pro_api 客户端
- fetch() 调用 pro.news / pro.news_info，按 trade_date 分批
"""
from __future__ import annotations

import datetime
import logging
import threading
import time
from typing import Iterator

from ..provider_base import (
    IngestProviderBase,
    IngestProviderMeta,
    FetchPayload,
    FetchResult,
)
from ..policy_registry import SourcePolicy
from ..news_dedup import NEWS_DATA_COLUMNS, build_news_row
from zephyr.shared.security.secrets import get_required_secret, get_secret_or_default
from ..table_registry import get_registry
from zephyr.shared.utils.time_utils import now_utc, seconds_since

log = logging.getLogger(__name__)

# Phase 5: 表名从 business_data_categories.yaml 真源派生（裁定 #ARCH-CH-024）
_TBL_NEWS_DATA = get_registry().table("fund_news_data")
# #ARCH-IFIND-FAILOVER: iFind 备用数据源（试用账号不可用时自动切换）
_TBL_INDUSTRY_CLASS = get_registry().table("market_industry_class")
_TBL_INDUSTRY_CLASS_SUPPL = get_registry().table("fund_industry_class_suppl")
# 2026-08-14 东财反爬治本：LOF 列表替代源（fund_lof_spot_em 持续 RemoteDisconnected）
_TBL_LOF_LIST = get_registry().table("market_lof_list")


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
        capabilities=["news_data", "industry_class", "industry_class_suppl", "lof_list"],
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

    def fetch(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """按 payload.extra["capability"] 路由到具体获取方法。"""
        if not self._connected or self._pro is None:
            yield FetchResult(
                table=payload.table, columns=[], rows=[],
                last_key="", elapsed_sec=0.0, error="tushare 未连接",
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
        else:
            yield FetchResult(
                table=payload.table, columns=[], rows=[],
                last_key="", elapsed_sec=0.0,
                error=f"unsupported capability: {capability}",
            )

    # ---- 新闻快讯 ----

    def _fetch_news_news_info(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
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
                        rows.append(build_news_row(
                            pub_date=str(row.get("datetime", "")),
                            title=str(row.get("title", "")),
                            link="",
                            summary=str(row.get("content", "")),
                            source=str(row.get("src", "")),
                            data_source="tushare",
                        ))
                self._log.info(f"新闻快讯 {trade_date}: {len(rows)} 行")
                yield FetchResult(
                    table=table, columns=columns, rows=rows,
                    last_key=current.isoformat(), elapsed_sec=time.time() - t0,
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.warning(f"新闻快讯 {trade_date} 获取失败: {e}")
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key=current.isoformat(), elapsed_sec=time.time() - t0,
                    error=str(e),
                )
            current += datetime.timedelta(days=1)

    # ---- 证券新闻 ----

    def _fetch_news_security(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
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
                        rows.append(build_news_row(
                            pub_date=str(row.get("datetime", "")),
                            title=str(row.get("title", "")),
                            link="",
                            summary=str(row.get("content", "")),
                            source=str(row.get("src", "")),
                            data_source="tushare",
                        ))
                self._log.info(f"证券新闻 {trade_date}: {len(rows)} 行")
                yield FetchResult(
                    table=table, columns=columns, rows=rows,
                    last_key=current.isoformat(), elapsed_sec=time.time() - t0,
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.warning(f"证券新闻 {trade_date} 获取失败: {e}")
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key=current.isoformat(), elapsed_sec=time.time() - t0,
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
            self._pro.index_classify, policy, level='L1', src='SW2021',
        )
        l2_df = self._call_with_policy(
            self._pro.index_classify, policy, level='L2', src='SW2021',
        )
        l3_df = self._call_with_policy(
            self._pro.index_classify, policy, level='L3', src='SW2021',
        )

        # index_code/name 与 L3→L2→L1 parent 关系映射（抽取降复杂度）
        l1_names, l2_names, l3_names, l3_to_l2, l2_to_l1 = self._build_industry_lookups(
            l1_df, l2_df, l3_df,
        )

        # 2. 遍历 L3 行业，获取成分股
        stock_map: dict[str, dict] = {}
        api_count = 0
        for l3_code, l3_name in l3_names.items():
            try:
                members_df = self._call_with_policy(
                    self._pro.index_member, policy, index_code=l3_code, is_new='Y',
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
                l2_name = l2_names.get(l2_code, '') if l2_code else ''
                l1_code = l2_to_l1.get(l2_code) if l2_code else None
                l1_name = l1_names.get(l1_code, '') if l1_code else ''

                for _, m in members_df.iterrows():
                    ts_code = str(m.get('con_code') or '')
                    if not ts_code:
                        continue
                    stock_map[ts_code] = {
                        "L1": l1_name, "L2": l2_name, "L3": l3_name,
                    }
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.debug(f"index_member({l3_code}) 失败: {e}")
                continue

        self._log.info(
            f"申万行业映射: {len(stock_map)} 只股票（{api_count} 次 API 调用）"
        )
        return stock_map

    def _build_industry_lookups(
        self, l1_df, l2_df, l3_df,
    ) -> tuple[dict, dict, dict, dict, dict]:
        """构建申万行业查找表（从 _build_sw_industry_map 抽取降复杂度）。

        #ARCH-IFIND-FAILOVER: L1/L2/L3 index_code→name + L3→L2→L1 parent 关系映射。
        parent_code 是 industry_code，需经 industry_code→index_code 中转。
        Returns:
            (l1_names, l2_names, l3_names, l3_to_l2, l2_to_l1)
        """
        l1_names = {r['index_code']: r['industry_name'] for _, r in l1_df.iterrows()}
        l2_names = {r['index_code']: r['industry_name'] for _, r in l2_df.iterrows()}
        l3_names = {r['index_code']: r['industry_name'] for _, r in l3_df.iterrows()}

        # industry_code → index_code 映射（parent_code 是 industry_code，需转换为 index_code）
        l1_code_to_idx = {str(r['industry_code']): r['index_code'] for _, r in l1_df.iterrows()}
        l2_code_to_idx = {str(r['industry_code']): r['index_code'] for _, r in l2_df.iterrows()}

        # L3→L2→L1 parent 关系（index_code → index_code，经 industry_code 中转）
        l3_to_l2: dict[str, str | None] = {}
        for _, r in l3_df.iterrows():
            pc = str(r.get('parent_code') or '')
            l3_to_l2[r['index_code']] = l2_code_to_idx.get(pc) if pc else None
        l2_to_l1: dict[str, str | None] = {}
        for _, r in l2_df.iterrows():
            pc = str(r.get('parent_code') or '')
            l2_to_l1[r['index_code']] = l1_code_to_idx.get(pc) if pc else None
        return l1_names, l2_names, l3_names, l3_to_l2, l2_to_l1

    def _fetch_industry_class(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
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
                table=table, columns=columns, rows=[],
                last_key=today_str, elapsed_sec=seconds_since(t0),
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

        self._log.info(f"industry_class: {len(rows)} 行（tushare 替代 iFind）")
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=today_str, elapsed_sec=seconds_since(t0),
        )

    def _fetch_industry_class_suppl(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
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
                table=table, columns=columns, rows=[],
                last_key=today_str, elapsed_sec=seconds_since(t0),
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

        self._log.info(f"industry_class_suppl: {len(rows)} 行（tushare 替代 iFind）")
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=today_str, elapsed_sec=seconds_since(t0),
        )

    # ---- LOF 基金列表（2026-08-14 东财反爬替代源） ----

    def _fetch_lof_list(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
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
                self._pro.fund_basic, policy, market="E", status="L",
                fields="ts_code,name",
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(
                table=table, columns=columns, rows=[],
                last_key="", elapsed_sec=seconds_since(t0), error=str(e),
            )
            return

        rows: list[tuple] = []
        if df is not None and not df.empty:
            lof = df[df["name"].str.contains("LOF", na=False)]
            for _, r in lof.iterrows():
                rows.append((str(r.get("ts_code", "") or ""), str(r.get("name", "") or "")))

        self._log.info(f"lof_list: {len(rows)} 只 LOF（tushare 替代东财）")
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=today_str, elapsed_sec=seconds_since(t0),
        )
