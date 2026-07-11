# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.tushare_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] tushare SDK (ts.set_token/ts.pro_api/pro.news/pro.news_info)
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] token认证（环境变量TUSHARE_TOKEN）；历史数据截止2024-08；积分不足触发重试
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 异常->yield FetchResult(error=str)；token缺失->RuntimeError
# [TESTS] tests/zephyr/data/test_providers.py::TestTushareProvider
# [A_module] module_id=MOD-L00-004-tushare_provider | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Tushare 数据源 Provider 实现（MOD-L00-004 §4.3）。

封装 tushare SDK，继承 DataSourceBase。
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
import time
from typing import Iterator

from ..provider_base import (
    DataSourceBase,
    DataSourceMeta,
    FetchPayload,
    FetchResult,
)
from ..policy_registry import SourcePolicy
from ..news_dedup import NEWS_DATA_COLUMNS, build_news_row
from zephyr.shared.security.secrets import get_required_secret, get_secret_or_default

log = logging.getLogger(__name__)


class TushareProvider(DataSourceBase):
    """Tushare 数据源 Provider。

    token 认证、shared 线程安全模型。
    已知问题：历史数据截止 2024-08；积分不足 API 受限。
    """

    source_name: str = "tushare"
    meta: DataSourceMeta = DataSourceMeta(
        name="tushare",
        display_name="Tushare Pro",
        auth_type="token",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=200,
        capabilities=["news_data"],
        known_issues=["历史数据截止2024-08", "积分不足API受限"],
    )

    # ---- 生命周期 ----

    def connect(self) -> None:
        """建立连接：读取 TUSHARE_TOKEN，初始化 pro_api。"""
        try:
            token = get_required_secret("TUSHARE_TOKEN")
        except Exception as e:
            raise RuntimeError(f"TUSHARE_TOKEN 环境变量未设置: {e}")
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

        cap = (payload.extra or {}).get("capability")
        if cap == "news_data":
            yield from self._fetch_news_news_info(payload, policy)
            yield from self._fetch_news_security(payload, policy)
        else:
            yield FetchResult(
                table=payload.table, columns=[], rows=[],
                last_key="", elapsed_sec=0.0,
                error=f"unsupported capability: {cap}",
            )

    # ---- 新闻快讯 ----

    def _fetch_news_news_info(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取新闻快讯（pro.news_info），写入 news_data 统一表。

        按 trade_date 分批拉取，每批一天。
        """
        table = "c3_fundamental.news_data"
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
            except Exception as e:
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
        table = "c3_fundamental.news_data"
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
            except Exception as e:
                self._log.warning(f"证券新闻 {trade_date} 获取失败: {e}")
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key=current.isoformat(), elapsed_sec=time.time() - t0,
                    error=str(e),
                )
            current += datetime.timedelta(days=1)
