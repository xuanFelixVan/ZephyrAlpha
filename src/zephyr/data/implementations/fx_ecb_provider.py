# [BLUEPRINT] MOD-AUTO-L1-004 | docs/_working/automation/campaign/blueprints/onboard_source_blueprint.md
# [PROVISIONAL] 暂编号：docs/03_modules 解冻后按注册表重编（挂单 H-01）
# [MODULE] zephyr.data.implementations.fx_ecb_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] requests (frankfurter.app); zephyr.data.provider_base; schemas.categories.market.market_alt_fx_rate_ecb
# [CONSUMERS] zephyr.data.scheduler (source=alt_fx_ecb); scripts/data/fx_ecb_ingest.py
# [STARTUP] scheduled_task
# [MATURITY] testing
# [INVARIANTS] fetch 返回 Iterator[FetchResult]，异常吞成 FetchResult(error=) 不抛（provider 只拉不写 CH）;
#   last_key=各货币对最迟日期（min of per-base max）——任一对缺价游标不越它，下一班回查自愈，防对级数据洞;
#   PIT：trade_date=ECB 数据自带日期，绝不使用运行日
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 网络/解析失败→yield FetchResult(error=...)；unsupported capability→error；全对失败→error
# [TESTS] tests/data/test_fx_ecb_provider.py
# [A_module] module_id=MOD-AUTO-L1-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FxEcbProvider——ECB 日频汇率正门 Provider（L1.1 批，source=alt_fx_ecb）。

骨架 §1 工段③"自动上架"首源从 Windows 任务旁路升格 DataScheduler 正门：
tasks.yaml(source=alt_fx_ecb, capability=fx_ecb_daily) → scheduler.create_provider
路由 → 本类 fetch → 调度器 BufferedWriter 写 c1_market.alt_fx_rate_ecb。

数据源：https://api.frankfurter.app（ECB 参考汇率公开镜像，免 key，假日缺价）。
采集核心自 scripts/data/fx_ecb_ingest.py 上移（单一真源，脚本改薄壳复用本件）。

"""
from __future__ import annotations

import logging
import os
from datetime import date
import socket
from typing import Final, Iterator

import requests

from zephyr.shared.utils.time_utils import now_utc, seconds_since

from ..policy_registry import SourcePolicy
from ..provider_base import (
    CapabilityContract,
    FetchPayload,
    FetchResult,
    IngestProviderBase,
    IngestProviderMeta,
)

log = logging.getLogger(__name__)

API_URL: Final = "https://api.frankfurter.app"
# 采集货币对清单（v0 固定；扩对=改此表+源卡片，正门任务零改动）
PAIRS: Final[list[tuple[str, str]]] = [("USD", "CNY"), ("EUR", "CNY"), ("USD", "JPY")]
TIMEOUT_SEC: Final = 30
HEADERS: Final = {
    "User-Agent": "Mozilla/5.0 (compatible; ZephyrAlpha-alt-data/1.0; research use)",
    "Accept": "application/json",
}


def _detect_local_proxy(port: int = 10808, timeout: float = 1.0) -> str | None:
    """探测本地代理端口（v2rayN 10808），与 fred/eia/rss provider 同模式（海外站点家族惯例）。"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect(("127.0.0.1", port))
        return f"http://127.0.0.1:{port}"
    except OSError:
        return None
    finally:
        s.close()


def parse_series(payload: dict, pairs: list[tuple[str, str]]) -> list[tuple]:
    """frankfurter 时间序列 payload → 行元组（纯函数，测试直喷）。假日缺价跳过。"""
    by_base: dict[str, list[str]] = {}
    for base, quote in pairs:
        by_base.setdefault(base, []).append(quote)
    rows: list[tuple] = []
    for base, quotes in by_base.items():
        for day, rates in (payload.get("rates") or {}).items():
            for quote in quotes:
                rate = rates.get(quote)
                if rate is None:  # 假日缺价跳过（ECB target 非业务日）
                    continue
                rows.append((day, base, quote, float(rate)))
    rows.sort(key=lambda r: (r[0], r[1], r[2]))
    return rows


class FxEcbProvider(IngestProviderBase):
    """ECB 日频汇率（frankfurter.app）免 key 免费源 Provider。

    线程安全模型：shared（无状态 HTTP 调用，requests 走代理时无会话态）。
    """

    source_name: str = "alt_fx_ecb"
    meta: IngestProviderMeta = IngestProviderMeta(
        name="alt_fx_ecb",
        display_name="ECB 日频汇率（frankfurter.app）",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=30,
        capabilities=[
            CapabilityContract(
                "fx_ecb_daily",
                supports_symbols_null=True,
                supports_incremental=True,
                supports_full_refresh=True,
                requires_date_range=True,
                expected_market="cross",
                expected_variety="fx_rate",
            ),
        ],
        known_issues=[
            "ECB 假日/周末缺价（last_key 取最迟对游标，下一班自愈）",
            "海外站点国内访问可能需 VPN（env 代理或本地 10808 探测）",
        ],
    )

    def __init__(self) -> None:
        super().__init__()
        self._proxies: dict | None = None

    # ---- 生命周期 ----

    def connect(self) -> None:
        proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY") or _detect_local_proxy()
        if proxy:
            self._proxies = {"https": proxy, "http": proxy}
        self._connected = True

    def health_check(self) -> bool:
        if not self._connected:
            return False
        try:
            resp = requests.get(
                f"{API_URL}/latest?base=USD&symbols=CNY",
                headers=HEADERS,
                timeout=10,
                proxies=self._proxies,
            )
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def disconnect(self) -> None:
        self._connected = False

    # ---- 采集 ----

    def _http_get_json(self, url: str) -> dict:
        resp = requests.get(
            url, headers=HEADERS, timeout=TIMEOUT_SEC, proxies=self._proxies
        )
        resp.raise_for_status()
        return resp.json()

    def collect_rows(
        self,
        start: date,
        end: date,
        pairs: list[tuple[str, str]] | None = None,
        policy: SourcePolicy | None = None,
    ) -> tuple[list[tuple], list[str]]:
        """拉窗口内全部货币对 → (行元组, 失败货币对清单)。

        每对单独记录最迟日期供 last_key 保守推进；某对全失败不拖垮其余对
        （失败清单非空=部分洞，由调度游标自愈机制下一班回查）。
        """
        from ..policy_registry import get_registry

        pairs = pairs or list(PAIRS)
        policy = policy or get_registry().get_policy(self.source_name)
        by_base: dict[str, list[str]] = {}
        for base, quote in pairs:
            by_base.setdefault(base, []).append(quote)
        rows: list[tuple] = []
        failed: list[str] = []
        for base, quotes in by_base.items():
            url = (
                f"{API_URL}/{start.isoformat()}..{end.isoformat()}"
                f"?base={base}&symbols={','.join(quotes)}"
            )
            try:
                payload = self._call_with_policy(self._http_get_json, policy, url)
            except Exception as exc:  # noqa: BLE001 — never-raise 契约：上抛=炸整班
                failed.append(base)
                self._log.warning("frankfurter base=%s 拉取失败: %s", base, exc)
                continue
            rows.extend(parse_series(payload, [(base, q) for q in quotes]))
        rows.sort(key=lambda r: (r[0], r[1], r[2]))
        return rows, failed

    def fetch(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """按 payload.extra["capability"] 路由到具体获取方法。"""
        capability = (payload.extra or {}).get("capability")
        if capability == "fx_ecb_daily":
            yield from self._fetch_daily(payload, policy)
        else:
            yield FetchResult(
                table=payload.table, columns=[], rows=[], last_key="",
                elapsed_sec=0.0, error=f"unsupported capability: {capability}",
            )

    def _fetch_daily(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        started = now_utc()
        from schemas.categories.market.market_alt_fx_rate_ecb import (  # 家族先例 akshare_provider:3014
            INSERT_COLUMNS,
            TABLE_NAME,
        )

        pairs = (payload.extra or {}).get("pairs") or None
        rows, failed = self.collect_rows(
            payload.start, payload.end, pairs=pairs, policy=policy
        )
        elapsed = seconds_since(started)
        if not rows:
            yield FetchResult(
                table=TABLE_NAME, columns=list(INSERT_COLUMNS), rows=[], last_key="",
                elapsed_sec=elapsed,
                error=f"全部货币对拉取失败: {failed}" if failed else None,
            )
            return
        # 保守游标：各对取自身最迟日再取 min——任一对缺价/失败则不越它，下一班回查
        per_base_latest: dict[str, str] = {}
        for day, base, _quote, _rate in rows:
            cur = per_base_latest.get(base, "")
            if day > cur:
                per_base_latest[base] = day
        last_key = min(per_base_latest.values())
        # 部分失败不得带 error：调度器 _fetch_and_write 见 FetchResult.error 即 break 丢整批行
        # （scheduler.py:1916），部分洞交由保守游标下一班自愈。
        if failed:
            self._log.warning("部分货币对失败 %s，last_key=%s 保守不越（下一班回查）", failed, last_key)
        yield FetchResult(
            table=TABLE_NAME, columns=list(INSERT_COLUMNS), rows=rows,
            last_key=last_key, elapsed_sec=elapsed,
        )
