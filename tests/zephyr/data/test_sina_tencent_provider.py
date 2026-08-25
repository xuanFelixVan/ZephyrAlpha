# [BLUEPRINT] MOD-L00-007 | tests/zephyr/data/test_sina_tencent_provider.py
# [MODULE] tests.zephyr.data.test_sina_tencent_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.redundant_source.sina_tencent_provider
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L00-007 | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""SinaTencentProvider 单元测试——第三级免登快照备源（CAND-DAT-012 / B1-00602）。

覆盖：
    1. 新浪 hq.sinajs 格式解析 → CTR-001 字段映射 tick dict
    2. 腾讯 qt.gtimg 格式解析 → 同构 tick dict
    3. 限速：请求间隔不低于 min_request_interval
    4. 超时退避：连续失败指数退避、成功复位
    5. 与主源价格偏差交叉校验：超阈值触发告警回调
    6. SourceProvider 接口：name/start/stop/is_running + 末位优先级常量
"""

from __future__ import annotations

from zephyr.data.redundant_source.sina_tencent_provider import (
    SinaTencentProvider,
    parse_sina_snapshot,
    parse_tencent_snapshot,
)

# ---------------------------------------------------------------------------
# fixtures——真实报文形态（GBK 解码后文本）
# ---------------------------------------------------------------------------

_SINA_TEXT = (
    'var hq_str_sh600000="浦发银行,13.010,13.020,13.060,13.200,12.900,'
    '13.040,13.060,98985776,130459082.37,'
    '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,'
    '2026-08-25,09:30:01,00,";\n'
)

_TENCENT_TEXT = (
    'v_sh600000="1~浦发银行~600000~13.06~13.02~13.01~5678~1234~4344~'
    '13.06~100~13.05~200~13.04~300~13.03~400~13.02~500~13.07~100~'
    '13.08~200~13.09~300~13.10~400~13.11~500~~20260825093001~0.04~0.31~'
    '13.20~12.90~13.06/98985776/130459082~98985776~13045.91~1.2~10.5~~'
    '13.20~12.90~5.17~1304.59~1304.59~0.8~~-1~";\n'
)


def _provider(**kw) -> SinaTencentProvider:
    kw.setdefault("symbols", ["600000.SH"])
    kw.setdefault("on_tick_callback", lambda s, t: None)
    kw.setdefault("http_get", lambda url: _SINA_TEXT)
    kw.setdefault("sleep_fn", lambda s: None)
    return SinaTencentProvider(**kw)


# ---------------------------------------------------------------------------
# 1. 报文解析（字段映射 CTR-001）
# ---------------------------------------------------------------------------


class TestParsing:
    def test_parse_sina(self):
        ticks = parse_sina_snapshot(_SINA_TEXT)
        assert len(ticks) == 1
        t = ticks[0]
        assert t["symbol"] == "600000.SH"
        assert t["last_price"] == 13.06
        assert t["open"] == 13.01
        assert t["prev_close"] == 13.02
        assert t["high"] == 13.20
        assert t["low"] == 12.90
        assert t["volume"] == 98985776.0
        assert t["data_source"] == "sina"

    def test_parse_tencent(self):
        ticks = parse_tencent_snapshot(_TENCENT_TEXT)
        assert len(ticks) == 1
        t = ticks[0]
        assert t["symbol"] == "600000.SH"
        assert t["last_price"] == 13.06
        assert t["open"] == 13.01
        assert t["prev_close"] == 13.02
        assert t["high"] == 13.20
        assert t["low"] == 12.90
        assert t["data_source"] == "tencent"

    def test_parse_empty_segment_skipped(self):
        assert parse_sina_snapshot('var hq_str_sh600000="";\n') == []


# ---------------------------------------------------------------------------
# 2. 轮询一轮（注入 http_get，不触网）
# ---------------------------------------------------------------------------


class TestPollOnce:
    def test_poll_once_emits_ticks(self):
        got: list[tuple[str, dict]] = []
        p = _provider(on_tick_callback=lambda s, t: got.append((s, t)))
        n = p.poll_once()
        assert n == 1
        assert got[0][0] == "600000.SH"
        assert got[0][1]["last_price"] == 13.06

    def test_tencent_fallback_when_sina_fails(self):
        calls = []

        def http_get(url: str) -> str:
            calls.append(url)
            if "sinajs" in url:
                raise TimeoutError("sina timeout")
            return _TENCENT_TEXT

        got: list[dict] = []
        p = _provider(http_get=http_get, on_tick_callback=lambda s, t: got.append(t))
        assert p.poll_once() == 1
        assert got[0]["data_source"] == "tencent"
        assert len(calls) == 2

    def test_both_sources_fail_returns_zero(self):
        def http_get(url: str) -> str:
            raise TimeoutError("down")

        p = _provider(http_get=http_get)
        assert p.poll_once() == 0


# ---------------------------------------------------------------------------
# 3. 限速 + 超时退避
# ---------------------------------------------------------------------------


class TestRateLimitAndBackoff:
    def test_rate_limit_sleeps_between_requests(self):
        now = [100.0]
        slept: list[float] = []
        p = _provider(
            sleep_fn=lambda s: slept.append(s),
            time_fn=lambda: now[0],
            min_request_interval=1.0,
        )
        p.poll_once()
        now[0] += 0.3  # 距上次请求仅 0.3s
        p.poll_once()
        assert slept and abs(slept[0] - 0.7) < 1e-9

    def test_timeout_backoff_grows_and_resets(self):
        fail = [True]

        def http_get(url: str) -> str:
            if fail[0]:
                raise TimeoutError("down")
            return _SINA_TEXT

        p = _provider(http_get=http_get)
        p.poll_once()
        assert p.consecutive_failures >= 1
        backoff1 = p.current_backoff()
        p.poll_once()
        assert p.current_backoff() > backoff1
        fail[0] = False
        p.poll_once()
        assert p.consecutive_failures == 0
        assert p.current_backoff() == 1.0


# ---------------------------------------------------------------------------
# 4. 价格偏差交叉校验
# ---------------------------------------------------------------------------


class TestDeviationCrossCheck:
    def test_deviation_alert_fired(self):
        alerts: list[dict] = []
        p = _provider(
            on_alert=lambda a: alerts.append(a),
            reference_price_provider=lambda sym: 12.50,  # 主源价 12.50 vs 快照 13.06
            deviation_threshold=0.02,
        )
        p.poll_once()
        assert len(alerts) == 1
        assert alerts[0]["symbol"] == "600000.SH"
        assert alerts[0]["deviation"] > 0.02

    def test_within_threshold_no_alert(self):
        alerts: list[dict] = []
        p = _provider(
            on_alert=lambda a: alerts.append(a),
            reference_price_provider=lambda sym: 13.05,
            deviation_threshold=0.02,
        )
        p.poll_once()
        assert alerts == []

    def test_no_reference_price_skips_check(self):
        alerts: list[dict] = []
        p = _provider(
            on_alert=lambda a: alerts.append(a),
            reference_price_provider=lambda sym: None,
        )
        p.poll_once()
        assert alerts == []


# ---------------------------------------------------------------------------
# 5. SourceProvider 接口
# ---------------------------------------------------------------------------


class TestSourceProviderInterface:
    def test_interface(self):
        p = _provider()
        assert p.name() == "sina_tencent"
        assert p.is_running() is False
        assert p.start() is True
        assert p.is_running() is True
        p.stop()
        assert p.is_running() is False

    def test_last_priority_constant(self):
        # 末位优先级：QMT 主源=0 / TDX 备源=50 / 本源=100
        assert SinaTencentProvider.PRIORITY > 50
