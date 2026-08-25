# [BLUEPRINT] MOD-L00-007 | docs/03_modules/_domain_data/redundant_source_blueprint.md
# [MODULE] zephyr.data.redundant_source.sina_tencent_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.redundant_source.source_switcher
# [CONSUMERS] （P1 接线：SourceSwitcher 优先级末位第三级备源）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 免登匿名访问；http_get/sleep_fn/time_fn 注入式（单测不触网）；新浪失败自动落腾讯；解析异常不中断轮询；价格偏差超阈值必告警
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单源请求异常→自动换备源；双源均失败→poll_once 返回 0 + 失败计数退避，不抛
# [TESTS] tests/zephyr/data/test_sina_tencent_provider.py
# [A_module] module_id=MOD-L00-007 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""新浪/腾讯免登快照第三级备源适配器（CAND-DAT-012 / B1-00602，96 Sina+Tencent Real-Time）。

深挖裁定=做(P1)：实时冗余链 QMT 主 + TDX 备已建（backup_tick_poller/source_switcher
/heartbeat_monitor），新浪/腾讯免登快照作第三级备份未接入——QMT 与 TDX 同时故障时
无兜底行情。本模块：

1. ``SourceProvider`` 接口适配器：``PRIORITY=100`` 末位（QMT 主=0 / TDX 备=50），
   供 SourceSwitcher 挂第三级。
2. 3-5s 轮询 + 限速（``min_request_interval``）+ 超时指数退避（连续失败
   ``current_backoff`` 翻倍，成功复位）。
3. 字段映射 CTR-001：hq.sinajs / qt.gtimg 报文 → 同构 tick dict
   （symbol/timestamp/open/high/low/last_price/prev_close/volume/amount/data_source）。
4. 与主源价格偏差交叉校验：``reference_price_provider`` 注入主源价，
   偏差超 ``deviation_threshold`` 触发 ``on_alert`` 告警。

注：tickflow_provider 为美股 K线 provider，与本 A 股实时链无关，不复用不冲突。
"""

from __future__ import annotations

import logging
import re
import threading
import time
from typing import Callable

from zephyr.data.redundant_source.source_switcher import SourceProvider

log = logging.getLogger(__name__)

__all__ = [
    "SinaTencentProvider",
    "parse_sina_snapshot",
    "parse_tencent_snapshot",
]

_SINA_URL = "https://hq.sinajs.cn/list={codes}"
_TENCENT_URL = "https://qt.gtimg.cn/q={codes}"

_SINA_ROW_RE = re.compile(r'var hq_str_([a-z]{2}\d{6})="([^"]*)";')
_TENCENT_ROW_RE = re.compile(r'v_([a-z]{2}\d{6})="([^"]*)";')

_DEFAULT_POLL_INTERVAL = 4.0  # 3-5s 轮询中位
_DEFAULT_MIN_REQUEST_INTERVAL = 1.0  # 限速：两次请求最小间隔（秒）
_MAX_BACKOFF_EXP = 3  # 退避上限 2^3=8 倍


def _to_vendor_code(symbol: str) -> str:
    """600000.SH → sh600000（新浪/腾讯报文代码形态）。"""
    code, _, exch = symbol.partition(".")
    return f"{exch.lower()}{code}"


def _to_std_symbol(vendor_code: str) -> str:
    """sh600000 → 600000.SH。"""
    return f"{vendor_code[2:]}.{vendor_code[:2].upper()}"


def _f(text: str) -> float | None:
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def parse_sina_snapshot(text: str) -> list[dict]:
    """解析 hq.sinajs 报文 → CTR-001 字段映射 tick dict 列表。

    字段序：0 名称,1 今开,2 昨收,3 现价,4 最高,5 最低,6 买一,7 卖一,
    8 成交量(股),9 成交额(元),...,30 日期,31 时间。
    """
    ticks: list[dict] = []
    for m in _SINA_ROW_RE.finditer(text):
        vendor, payload = m.group(1), m.group(2)
        if not payload.strip():
            continue
        f = payload.split(",")
        if len(f) < 32:
            continue
        price = _f(f[3])
        if price is None:
            continue
        ticks.append(
            {
                "symbol": _to_std_symbol(vendor),
                "timestamp": f"{f[30]} {f[31]}",
                "open": _f(f[1]),
                "prev_close": _f(f[2]),
                "last_price": price,
                "high": _f(f[4]),
                "low": _f(f[5]),
                "bid1": _f(f[6]),
                "ask1": _f(f[7]),
                "volume": _f(f[8]),
                "amount": _f(f[9]),
                "data_source": "sina",
            }
        )
    return ticks


def parse_tencent_snapshot(text: str) -> list[dict]:
    """解析 qt.gtimg 报文 → 与新浪同构的 tick dict 列表。

    字段序（~分隔）：1 名称,2 代码,3 现价,4 昨收,5 今开,30 时间,
    33 最高,34 最低,36 成交量(手),37 成交额(万)。
    """
    ticks: list[dict] = []
    for m in _TENCENT_ROW_RE.finditer(text):
        vendor, payload = m.group(1), m.group(2)
        if not payload.strip():
            continue
        f = payload.split("~")
        if len(f) < 37:
            continue
        price = _f(f[3])
        if price is None:
            continue
        ticks.append(
            {
                "symbol": _to_std_symbol(vendor),
                "timestamp": f[30] if len(f) > 30 else "",
                "open": _f(f[5]),
                "prev_close": _f(f[4]),
                "last_price": price,
                "high": _f(f[33]),
                "low": _f(f[34]),
                "volume": _f(f[36]),  # 腾讯口径=手，消费方注意 ×100 归一
                "amount": _f(f[37]),  # 腾讯口径=万元
                "data_source": "tencent",
            }
        )
    return ticks


class SinaTencentProvider(SourceProvider):
    """新浪/腾讯免登快照第三级备源（SourceProvider 接口）。

    start() 起轮询线程；poll_once() 单轮拉取（新浪优先、失败落腾讯），
    供单测与手动兜底直调。
    """

    PRIORITY = 100  # SourceSwitcher 末位：QMT 主=0 / TDX 备=50 / 本源=100

    def __init__(
        self,
        symbols: list[str],
        on_tick_callback: Callable[[str, dict], None],
        http_get: Callable[[str], str] | None = None,
        poll_interval: float = _DEFAULT_POLL_INTERVAL,
        min_request_interval: float = _DEFAULT_MIN_REQUEST_INTERVAL,
        deviation_threshold: float = 0.02,
        reference_price_provider: Callable[[str], float | None] | None = None,
        on_alert: Callable[[dict], None] | None = None,
        time_fn: Callable[[], float] = time.monotonic,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        self._symbols = symbols
        self._on_tick = on_tick_callback
        self._http_get = http_get or self._default_http_get
        self._poll_interval = poll_interval
        self._min_request_interval = min_request_interval
        self._deviation_threshold = deviation_threshold
        self._ref_price = reference_price_provider
        self._on_alert = on_alert
        self._time = time_fn
        self._sleep = sleep_fn
        self._running = False
        self._thread: threading.Thread | None = None
        self._last_request_ts: float | None = None
        self._failures = 0

    # -- SourceProvider 接口 ----------------------------------------------

    def name(self) -> str:
        return "sina_tencent"

    def start(self) -> bool:
        if self._running:
            return True
        self._running = True
        self._thread = threading.Thread(
            target=self._poll_loop, daemon=True, name="sina-tencent-poller"
        )
        self._thread.start()
        log.info(
            "SinaTencentProvider 已启动 (symbols=%d, interval=%.1fs)",
            len(self._symbols),
            self._poll_interval,
        )
        return True

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
            self._thread = None

    def is_running(self) -> bool:
        return self._running

    # -- 退避状态（可观测） ------------------------------------------------

    @property
    def consecutive_failures(self) -> int:
        return self._failures

    def current_backoff(self) -> float:
        """当前退避倍率：连续失败指数翻倍（上限 2^3），无失败=1.0。"""
        return float(2 ** min(self._failures, _MAX_BACKOFF_EXP))

    # -- 单轮轮询 -----------------------------------------------------------

    def poll_once(self) -> int:
        """单轮拉取：新浪优先、失败落腾讯；返回喂出 tick 数。"""
        codes = ",".join(_to_vendor_code(s) for s in self._symbols)
        self._rate_limit_wait()
        ticks: list[dict] = []
        try:
            ticks = parse_sina_snapshot(self._http_get(_SINA_URL.format(codes=codes)))
        except Exception as e:  # noqa: BLE001 — 单源失败自动换备源
            log.warning("新浪快照失败，落腾讯: %s", e)
        if not ticks:
            self._rate_limit_wait()
            try:
                ticks = parse_tencent_snapshot(
                    self._http_get(_TENCENT_URL.format(codes=codes))
                )
            except Exception as e:  # noqa: BLE001
                log.error("腾讯快照亦失败: %s", e)
        if not ticks:
            self._failures += 1
            return 0
        self._failures = 0
        for tick in ticks:
            self._cross_check(tick)
            self._on_tick(tick["symbol"], tick)
        return len(ticks)

    # -- 内部 ----------------------------------------------------------------

    def _poll_loop(self) -> None:
        while self._running:
            try:
                self.poll_once()
            except Exception:  # noqa: BLE001 — 轮询循环不中断
                log.exception("poll_once 未预期异常")
            self._sleep(self._poll_interval * self.current_backoff())

    def _rate_limit_wait(self) -> None:
        if self._last_request_ts is None:
            self._last_request_ts = self._time()
            return
        elapsed = self._time() - self._last_request_ts
        if elapsed < self._min_request_interval:
            self._sleep(self._min_request_interval - elapsed)
        self._last_request_ts = self._time()

    def _cross_check(self, tick: dict) -> None:
        """与主源价格偏差交叉校验：超阈值触发告警。"""
        if self._ref_price is None or self._on_alert is None:
            return
        ref = self._ref_price(tick["symbol"])
        if not ref:
            return
        deviation = abs(tick["last_price"] - ref) / ref
        if deviation > self._deviation_threshold:
            alert = {
                "symbol": tick["symbol"],
                "snapshot_price": tick["last_price"],
                "reference_price": ref,
                "deviation": deviation,
                "threshold": self._deviation_threshold,
                "data_source": tick["data_source"],
            }
            log.warning("备源价格偏差超阈值: %s", alert)
            self._on_alert(alert)

    @staticmethod
    def _default_http_get(url: str) -> str:
        """生产默认：requests 拉取（GBK 解码）；单测注入假实现不触网。"""
        import requests  # 延迟 import，模块加载不依赖网络栈

        resp = requests.get(url, timeout=5.0)
        resp.raise_for_status()
        resp.encoding = "gbk"
        return resp.text
