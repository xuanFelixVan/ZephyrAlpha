# [BLUEPRINT] MOD-FE-006 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TTL] permanent
# [MODULE] tests.frontend.test_ops_alert_feed
# [DOMAIN] D_FRONTEND
"""A2 治理战役验收单测：运营告警供给线（OOM critical → promotion 页横幅）。

覆盖：
- OpsAlertFeed 板三操作：publish 创建/静默窗口去重/解除+保留期（tmp_path 隔离）
- tick 端到端（假探针）：阈值上沿触发 ALERT-SYS-002 发布 → 持续触发静默刷新 → 回落滞回解除
- 探针 fail-safe：probe 抛异常 → ok:false 不上抛；真 psutil 探针返回正数
- GET /api/ops-notifications：有数据透传 / 板异常降级（TestClient + 板目录重定向）
- 前端接线静态断言：api.js 通道 + promotion.js 横幅注入/轮询/静默降级
- 生存线 KPI 供给（ALERT-KPI-001/002 断链清偿）：净值 TSV 解析 → SurvivalInput →
  真调 evaluate_survival_line → 状态词表与 config/alert_rules.yaml 逐字对齐 →
  落板形态；输入缺席/查询失败/判定异常 = 不产指标+loud warning+不炸循环；
  日频复评节奏（30s 不重打 CH）；与内存段互不连坐；src 侧死代码回归锁
- E2E（playwright，可选）：promotion 页注入假 OOM critical 事件 → 横幅可见（造假事件
  端到端"看到页面通知"的实测形态；浏览器缺席自动 skip）

测试隔离：通知板目录经 ZEPHYR_OPS_NOTIFICATION_DIR 重定向 tmp_path；规则文件走
临时 YAML（不读生产 config/alert_rules.yaml 的阈值断言，防真机内存漂移误判）。
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from zephyr.infrastructure.system_telemetry.alerts import ops_alert_feed as feed_mod  # noqa: E402
from zephyr.infrastructure.system_telemetry.alerts.ops_alert_feed import (  # noqa: E402
    FALLBACK_OOM_RULE_ID,
    SURVIVAL_METRIC_FRAGMENT,
    OpsAlertFeed,
    load_project_rss_alert_bytes,
    parse_nav_tsv,
    probe_project_rss_bytes,
    probe_survival_status,
    survival_input_from_nav,
)


def _prod_oom_rule() -> dict:
    """OOM 线数值真源=config/alert_rules.yaml ALERT-SYS-002（本文件禁副本）。

    排班表 v2 施工方案 §2.3 C-1⑤：绝对值告警线不再散落在代码/测试里，调档只改
    YAML（规则条件）+ config/resource_optimization.yaml ops_alerting 登记（兜底线），
    本测试自动跟随；规则被删=基线失效，直接测红而非静默用旧值。
    """
    import yaml

    cfg = yaml.safe_load((_PROJECT_ROOT / "config" / "alert_rules.yaml").read_text(encoding="utf-8")) or {}
    for rule in cfg.get("rules") or []:
        if str(rule.get("id")) == "ALERT-SYS-002":
            return rule
    raise AssertionError("config/alert_rules.yaml 缺 ALERT-SYS-002——测试基线失效（勿改回硬编码）")


_PROD_OOM = _prod_oom_rule()
THRESHOLD = int(str(_PROD_OOM.get("condition", "")).lstrip(">").strip())
# 假探针取值=该线的比例（原 9/9.5/7.6/7/1 GB 相对 8GB 线的同比例，改线不改编排）
PROBE_OVER = int(THRESHOLD * 1.125)         # 超阈 → critical
PROBE_OVER_MORE = int(THRESHOLD * 1.1875)   # 仍超阈 → 静默窗刷新
PROBE_IN_BAND = int(THRESHOLD * 0.95)       # 滞回带内（>阈值*0.9 且 <阈值）→ 不动作
PROBE_RECOVERED = int(THRESHOLD * 0.875)    # 回落到滞回线下 → 解除
PROBE_IDLE = int(THRESHOLD * 0.125)         # 远低于阈值


def _slm():
    """生存线判定模块 lazy 导入（带重试）。

    既有缺陷（非本文件引入，2026-09-16 实测）：`zephyr.risk.core.__init__` ↔
    `daily_auditor` 是循环导入，与 api_server 模块导入期启动的 daemon 线程
    （bt-strategy-warm / ops-alert-feed）并发首导入时，CPython 判为跨线程锁环
    → `_frozen_importlib._DeadlockError`（RuntimeError 子类），受害者是该窗口内
    任何 `import zephyr.risk.*` 的模块（tests/frontend/test_dashboard_feeds.py
    全量收集崩溃同因）。对方线程导入完成后重试即成——本文件据此不在模块顶层
    导入 risk，避免把一次可重试的运行时抖动升级成整目录收集中断。
    """
    last: Exception | None = None
    for _ in range(6):
        try:
            import zephyr.risk.core.survival_line_monitor as slm

            return slm
        except RuntimeError as exc:  # _DeadlockError / 部分初始化的环
            last = exc
            time.sleep(0.5)
    raise AssertionError(f"zephyr.risk.core 持续不可导入（既有循环导入抖动）: {last}")


@pytest.fixture()
def board(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """通知板目录重定向 tmp_path（测试隔离主通道，双保险：注入+环境变量）。"""
    d = tmp_path / "ops_notifications"
    monkeypatch.setenv("ZEPHYR_OPS_NOTIFICATION_DIR", str(d))
    return d


@pytest.fixture()
def feed(board: Path, tmp_path: Path) -> OpsAlertFeed:
    """注入临时规则的 feed（内存规则阈值=生产 ALERT-SYS-002 同值 critical + 一条 warning 对照）。"""
    rules = {
        "rules": [
            {
                "id": "ALERT-SYS-002",
                "name": "oom_risk",
                "severity": "critical",
                "metric": "system.memory_rss_bytes",
                "condition": f"> {THRESHOLD}",
                "description": _PROD_OOM.get("description", "oom_risk"),
                "silence_window": "5m",
            },
            {
                "id": "ALERT-SYS-001",
                "name": "high_cpu_usage",
                "severity": "warning",
                "metric": "system.cpu_percent",
                "condition": "> 80",
                "silence_window": "10m",
            },
        ]
    }
    rules_path = tmp_path / "alert_rules_test.yaml"
    import yaml

    rules_path.write_text(yaml.safe_dump(rules, allow_unicode=True), encoding="utf-8")
    return OpsAlertFeed(board_dir=board, rules_path=rules_path)


# ── 板三操作 ─────────────────────────────────────────────────────────────────


def test_publish_creates_entry(feed: OpsAlertFeed, board: Path):
    r = feed.publish(key="K1", severity="critical", title="t", message="m", now=1000.0)
    assert r["op"] == "created"
    entries = [json.loads(x) for x in (board / "notifications.jsonl").read_text(encoding="utf-8").splitlines() if x]
    assert len(entries) == 1
    assert entries[0]["key"] == "K1" and entries[0]["resolved_at"] is None


def test_publish_silence_dedup_refreshes(feed: OpsAlertFeed):
    feed.publish(key="K1", severity="critical", title="t", message="m", now=1000.0)
    r2 = feed.publish(key="K1", severity="critical", title="t", message="m", now=1100.0)  # 静默窗内
    assert r2["op"] == "refresh"
    active = feed.list_active(now=1100.0)
    assert len(active) == 1 and active[0]["count"] == 2 and active[0]["first_seen"] == 1000.0


def test_publish_new_entry_after_silence_expiry(feed: OpsAlertFeed):
    feed.publish(key="K1", severity="critical", title="t", message="m", now=1000.0)
    r2 = feed.publish(key="K1", severity="critical", title="t", message="m", now=1000.0 + 301 + 60)  # 超窗
    assert r2["op"] == "created"
    assert len(feed.list_active(now=1400.0)) == 2


def test_resolve_and_retention(feed: OpsAlertFeed):
    feed.publish(key="K1", severity="critical", title="t", message="m", now=1000.0)
    assert feed.resolve("K1", now=1200.0) == 1
    active = feed.list_active(now=1300.0)
    assert len(active) == 1 and active[0]["resolved_at"] == 1200.0
    # 保留期（默认 1h）过后不再出现在清单
    assert feed.list_active(now=1200.0 + 3601) == []
    # 已解除项再 publish → 新条目（不复用旧条目）
    r = feed.publish(key="K1", severity="critical", title="t", message="m", now=1300.0)
    assert r["op"] == "created"


def test_list_active_orders_active_first(feed: OpsAlertFeed):
    feed.publish(key="NEW", severity="critical", title="t", message="m", now=2000.0)
    feed.publish(key="OLD", severity="critical", title="t", message="m", now=1000.0)
    feed.resolve("OLD", now=1500.0)
    items = feed.list_active(now=1600.0)
    assert [e["key"] for e in items] == ["NEW", "OLD"]  # 未解除在前，后按 first_seen 倒序


# ── tick 端到端（假探针）────────────────────────────────────────────────────


def test_tick_triggers_and_publishes(feed: OpsAlertFeed):
    s = feed.tick(probe=lambda: PROBE_OVER, now=1000.0)
    assert s["ok"] is True and s["triggered"] == ["ALERT-SYS-002"]
    assert s["ops"] and s["ops"][0]["op"] == "created"
    active = feed.list_active(now=1000.0)
    assert len(active) == 1 and active[0]["severity"] == "critical"
    assert "9" in str(active[0]["labels"]["value"])


def test_tick_silence_then_resolve_on_recovery(feed: OpsAlertFeed):
    feed.tick(probe=lambda: PROBE_OVER, now=1000.0)
    s2 = feed.tick(probe=lambda: PROBE_OVER_MORE, now=1100.0)  # 仍超阈：静默刷新
    assert s2["ops"] and s2["ops"][0]["op"] == "refresh"
    # 回落到阈值*0.9 以下 → 解除（滞回）
    s3 = feed.tick(probe=lambda: PROBE_RECOVERED, now=1200.0)
    assert any(op["op"] == "resolved" for op in s3["ops"])
    assert feed.list_active(now=1200.0)[0]["resolved_at"] == 1200.0
    # 高于滞回线但低于阈值 → 不触发也不解除（滞回带内保持原状）
    feed.publish(key="ALERT-SYS-002", severity="critical", title="t", message="m", now=1300.0)
    s4 = feed.tick(probe=lambda: PROBE_IN_BAND, now=1400.0)
    assert s4["ops"] == []


def test_tick_warning_not_published(feed: OpsAlertFeed):
    """非 critical 规则不落板（首期只承 OOM critical）。"""
    s = feed.tick(probe=lambda: PROBE_IDLE, now=1000.0)
    assert s["triggered"] == [] and s["ops"] == []


def test_tick_probe_crash_failsafe(feed: OpsAlertFeed):
    def _boom():
        raise RuntimeError("psutil exploded")

    s = feed.tick(probe=_boom, now=1000.0)
    assert s["ok"] is False and "probe failed" in s["reason"]


def test_probe_project_rss_bytes_real():
    """真 psutil 探针：本进程树必有 RSS，返回正数且不抛。"""
    v = probe_project_rss_bytes()
    assert isinstance(v, int) and v > 0


def test_probe_fail_safe_on_psutil_blip(feed: OpsAlertFeed, monkeypatch: pytest.MonkeyPatch):
    """psutil 缺席/异常时探针降级为 0 而非上抛。"""
    import builtins

    real_import = builtins.__import__

    def _fake_import(name, *a, **k):
        if name == "psutil":
            raise ImportError("no psutil in this lambda")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", _fake_import)
    assert probe_project_rss_bytes() == 0


# ── api_server 端点 ──────────────────────────────────────────────────────────


def test_api_ops_notifications_passthrough(board: Path, feed: OpsAlertFeed):
    from fastapi.testclient import TestClient

    import zephyr.frontend.dashboard.api_server as api_server

    feed.publish(key="ALERT-SYS-002", severity="critical", title="oom_risk", message="假 OOM 事件（测试）", now=time.time())
    with TestClient(api_server.app) as client:
        r = client.get("/api/ops-notifications")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True and body["count"] == 1
    assert body["data"][0]["key"] == "ALERT-SYS-002"
    assert body["data"][0]["message"].startswith("假 OOM 事件")


def test_api_ops_notifications_degrades(board: Path, monkeypatch: pytest.MonkeyPatch):
    """板读取异常 → 200 ok:false + 空列表（不 500 硬崩，前端横幅静默）。"""
    from fastapi.testclient import TestClient

    import zephyr.frontend.dashboard.api_server as api_server
    import zephyr.infrastructure.system_telemetry.alerts.ops_alert_feed as mod

    def _boom(self, *a, **k):
        raise RuntimeError("board corrupted")

    monkeypatch.setattr(mod.OpsAlertFeed, "list_active", _boom)
    with TestClient(api_server.app) as client:
        r = client.get("/api/ops-notifications")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is False and body["data"] == []


# ── 前端接线（静态断言 + playwright E2E 可选）────────────────────────────────

_WEB = _PROJECT_ROOT / "src" / "zephyr" / "frontend" / "dashboard" / "web"


def test_frontend_api_channel_registered():
    api_js = (_WEB / "services" / "api.js").read_text(encoding="utf-8")
    assert "/api/ops-notifications" in api_js, "api.js 缺运营告警通道"
    promo_js = (_WEB / "features" / "promotion" / "promotion.js").read_text(encoding="utf-8")
    assert "fetchOpsNotifications" in promo_js, "promotion.js 缺横幅拉取"
    assert "promo-alert-banner" in promo_js, "promotion.js 缺横幅容器注入"


def _free_port() -> int:
    import socket

    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def base_url():
    """静态托管 web 目录（同 test_dashboard_smoke 模式，自含无需外部服务）。"""
    import subprocess
    import time as _time

    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=str(_WEB),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    url = f"http://127.0.0.1:{port}"
    deadline = _time.time() + 15
    while _time.time() < deadline:
        try:
            import socket as _socket

            with _socket.create_connection(("127.0.0.1", port), timeout=0.5):
                break
        except OSError:
            _time.sleep(0.2)
    else:
        proc.kill()
        pytest.fail("http.server 未能启动")
    yield url
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture(scope="module")
def page(base_url):
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        pg = browser.new_page()
        yield pg
        browser.close()


def test_frontend_e2e_fake_oom_event_visible(page, base_url):
    """端到端实测：注入假 OOM critical 事件 → promotion 页横幅真实渲染可见。

    手法（同 govm 冒烟）：index.html 进入 → go('promotion') 触发 promotion.js 自举 →
    拦截 ZK.api.fetchOpsNotifications 返回假事件（测试环境隔离，禁写生产板）→
    调 window.promoRefreshAlerts() → 断言横幅含 OOM_RISK 与 CRITICAL 红标、未解除态。
    """
    page.goto(base_url + "/index.html")
    page.wait_for_function("!!(window.ZK && ZK.features)", timeout=20000)
    page.evaluate("go('promotion')")
    page.wait_for_function("!!window.promoRefreshAlerts", timeout=20000)
    fake_event = {
        "ok": True,
        "count": 1,
        "data": [
            {
                "id": "e2efake0001",
                "key": "ALERT-SYS-002",
                "severity": "critical",
                "title": "oom_risk",
                "message": "内存即将耗尽（RSS 超告警线）（实测 9663676416 字节）",
                "source": "ops-alert-feed",
                "first_seen": "2026-09-16T05:30:00",
                "count": 1,
                "resolved_at": None,
            }
        ],
    }
    page.evaluate(
        """fake => {
             ZK.api.fetchOpsNotifications = function(){ return Promise.resolve(fake); };
             window.promoRefreshAlerts();
           }""",
        fake_event,
    )
    banner = page.locator("#promo-alert-banner")
    banner.wait_for(state="visible", timeout=5000)
    content = banner.inner_text()
    assert "oom_risk" in content
    assert "CRITICAL" in content
    assert "9663676416" in content
    first_cls = banner.locator(".promo-alert-item").first.get_attribute("class") or ""
    assert "promo-alert-resolved" not in first_cls


# ── 生存线 KPI 供给（ALERT-KPI-001/002 断链清偿，2026-09-16）───────────────────

# 生产规则镜像（阈值/严重度/静默窗真源=config/alert_rules.yaml，本处仅测试夹具）
_SURVIVAL_RULES = {
    "rules": [
        {
            "id": "ALERT-SYS-002",
            "name": "oom_risk",
            "severity": "critical",
            "metric": "system.memory_rss_bytes",
            "condition": f"> {THRESHOLD}",
            "description": _PROD_OOM.get("description", "oom_risk"),
            "silence_window": "5m",
        },
        {
            "id": "ALERT-KPI-001",
            "name": "survival_line_breach",
            "severity": "critical",
            "metric": "kpi.survival_line.status",
            "condition": "== survival_breach",
            "description": "破生存线（滚动12月超额≤0 或 MaxDD≥15% 或 Sharpe<0.8）→降仓/关停评估",
            "silence_window": "1d",
        },
        {
            "id": "ALERT-KPI-002",
            "name": "survival_line_failure",
            "severity": "critical",
            "metric": "kpi.survival_line.status",
            "condition": "== failure",
            "description": "触失败指标（连续6个月亏损或回撤>25%，对齐4级Protocol Level4）→失败处置",
            "silence_window": "1d",
        },
    ]
}

_ONE_DAY = 86400.0


@pytest.fixture()
def survival_feed(board: Path, tmp_path: Path) -> OpsAlertFeed:
    """含两条生存线规则的 feed（板与规则均注入 tmp_path，禁触生产 config/.runtime）。"""
    rules_path = tmp_path / "alert_rules_survival.yaml"
    import yaml

    rules_path.write_text(yaml.safe_dump(_SURVIVAL_RULES, allow_unicode=True), encoding="utf-8")
    return OpsAlertFeed(board_dir=board, rules_path=rules_path)


def _nav_tsv(daily_returns, *, with_benchmark=True, bench_drift=0.0, start="2025-01-02") -> str:
    """合成日频净值 TSV（trade_date / nav_ratio / benchmark_ratio，CH 同列序）。"""
    from datetime import date, timedelta

    nav = 1.0
    bench = 1.0
    d = date.fromisoformat(start)
    lines: list[str] = []
    for r in daily_returns:
        nav *= 1.0 + r
        bench *= 1.0 + bench_drift
        b = f"{bench:.8f}" if with_benchmark else "\\N"
        lines.append(f"{d.isoformat()}\t{nav:.8f}\t{b}")
        d += timedelta(days=1)
    return "\n".join(lines)


_FALLING = [-0.01] * 40  # 峰谷回撤 33% → FAILURE（对齐 Level4 回撤>25%）
_NOISY_FLAT = [0.002, -0.0019] * 20  # 净升但波动大 → Sharpe≈0.41 破生存线
_STRONG = [0.004, 0.0039] * 20  # 稳升低波 → OK


# ── 输入推导（纯函数 + 降级护栏）──


def test_parse_nav_tsv_handles_null_benchmark_and_bad_rows():
    rows = parse_nav_tsv("2025-01-02\t1.00000000\t1.00000000\n2025-01-03\t0.9\t\\N\n坏行\n2025-01-04\tNaN\t1.0")
    assert rows[0] == ("2025-01-02", 1.0, 1.0)
    assert rows[1] == ("2025-01-03", 0.9, None)  # Nullable 列 NULL → None（超额无定义）
    assert len(rows) == 2  # 坏行/非数值 nav 跳过，不致命


def test_parse_nav_tsv_recognizes_writer_side_none_token():
    # ch_writer 手工拼 TSV 用 str(v) → Nullable NULL 落成字面量 "None"；空串是第三种形态
    rows = parse_nav_tsv("2025-01-02\t1.0\tNone\n2025-01-03\t1.01\t\n2025-01-04\t1.02")
    assert [r[2] for r in rows] == [None, None, None]
    assert [r[1] for r in rows] == [1.0, 1.01, 1.02]  # 基准缺席不毁净值行


def test_survival_input_from_nav_derives_all_four_fields():
    pts = parse_nav_tsv(_nav_tsv(_FALLING))
    m = survival_input_from_nav(pts)
    assert m is not None
    assert 0.25 < m.max_drawdown < 0.40  # 峰谷最大回撤（正数）
    assert m.excess_return_12m < 0  # 净值区间收益 − 基准区间收益
    assert m.consecutive_loss_months >= 1
    assert m.sharpe < 0


@pytest.mark.parametrize(
    "daily_returns, expected",
    [
        # 三个状态字面量由 test_alert_rules_yaml_vocabulary_… 逐字对齐 SurvivalStatus 枚举
        (_STRONG, "ok"),
        (_NOISY_FLAT, "survival_breach"),
        (_FALLING, "failure"),
    ],
)
def test_status_vocabulary_is_measured_not_hardcoded(daily_returns, expected):
    """三态均由合成净值经真判定产出（词表来源=实算，非本文件硬编）。"""
    tsv = _nav_tsv(daily_returns)
    got = probe_survival_status(query_fn=lambda sql, timeout: tsv)
    assert got is not None and got["status"] == expected


def test_survival_input_requires_benchmark_series():
    """缺基准=超额无定义 → None（不猜口径，同 build_nav_curve 降级纪律）。"""
    assert survival_input_from_nav(parse_nav_tsv(_nav_tsv(_STRONG, with_benchmark=False))) is None


def test_survival_input_requires_min_samples_and_alive_series():
    assert survival_input_from_nav(parse_nav_tsv(_nav_tsv(_STRONG[:10]))) is None  # 样本 < 30
    assert survival_input_from_nav(parse_nav_tsv(_nav_tsv([0.0] * 40))) is None  # 序列冻结不可测


# ── 探针：真调 evaluate_survival_line（产而不消回归锁）──


def test_probe_survival_status_actually_calls_the_monitor(monkeypatch: pytest.MonkeyPatch):
    """回归锁：生产路径必须真的调用判定模块（不只是"可导入"）。"""
    slm = _slm()

    calls: list = []
    sqls: list[str] = []
    real = slm.evaluate_survival_line

    def _spy(metrics, config=None):
        calls.append(metrics)
        return real(metrics, config)

    def _capture(sql, timeout):
        sqls.append(sql)
        return _nav_tsv(_FALLING)

    monkeypatch.setattr(slm, "evaluate_survival_line", _spy)
    got = probe_survival_status(query_fn=_capture)
    assert calls, "evaluate_survival_line 未被生产路径调用——断链复发"
    assert got is not None and got["status"] == slm.SurvivalStatus.FAILURE.value
    assert any("回撤" in b for b in got["breaches"])
    # 表名取自 DDL-as-Code 真源、滚动窗口取自裁定配置（90 号 §16 window_months=12）
    assert sqls and "c1_market.account_nav_daily" in sqls[0]
    assert f"subtractMonths(today(), {slm.SurvivalLineConfig().window_months})" in sqls[0]


def test_probe_survival_status_query_failure_degrades_with_warning(caplog: pytest.LogCaptureFixture):
    def _boom(sql, timeout):
        raise RuntimeError("clickhouse down")

    with caplog.at_level("WARNING", logger=feed_mod.logger.name):
        assert probe_survival_status(query_fn=_boom) is None
    assert any("nav query failed" in str(r.msg) for r in caplog.records)


def test_probe_survival_status_empty_table_degrades_loudly_not_silently(caplog: pytest.LogCaptureFixture):
    """净值表空（现状 account_nav_daily=0 行）→ 不产指标 + loud warning，绝不兜底 ok。"""
    with caplog.at_level("WARNING", logger=feed_mod.logger.name):
        assert probe_survival_status(query_fn=lambda sql, timeout: "") is None
    assert any("metric not published" in str(r.msg) for r in caplog.records)


def test_probe_survival_status_swallows_monitor_crash(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture):
    """判定模块自身抛（脏数据 ValueError 等）→ 降级缺席，绝不上抛、绝不猜状态。"""
    slm = _slm()

    def _boom(metrics, config=None):
        raise ValueError("dirty data")

    monkeypatch.setattr(slm, "evaluate_survival_line", _boom)
    with caplog.at_level("WARNING", logger=feed_mod.logger.name):
        assert probe_survival_status(query_fn=lambda sql, timeout: _nav_tsv(_STRONG)) is None
    assert any("evaluate_survival_line raised" in str(r.msg) for r in caplog.records)


# ── 规则词表对齐（真源=config/alert_rules.yaml，非夹具）──


def test_alert_rules_yaml_vocabulary_matches_survival_status_enum():
    """两条 KPI 规则的 condition 右端必须逐字等于 SurvivalStatus 枚举值。"""
    import yaml

    status_enum = _slm().SurvivalStatus
    prod = _PROJECT_ROOT / "config" / "alert_rules.yaml"
    rules = (yaml.safe_load(prod.read_text(encoding="utf-8")) or {}).get("rules", [])
    kpi = {r["id"]: r for r in rules if SURVIVAL_METRIC_FRAGMENT in str(r.get("metric", ""))}
    assert {"ALERT-KPI-001", "ALERT-KPI-002"} <= set(kpi)
    assert kpi["ALERT-KPI-001"]["condition"] == f"== {status_enum.SURVIVAL_BREACH.value}"
    assert kpi["ALERT-KPI-002"]["condition"] == f"== {status_enum.FAILURE.value}"
    for r in kpi.values():
        assert r["metric"] == "kpi.survival_line.status" and r["severity"] == "critical"
    # 枚举全集 = 规则右端 ∪ 不触发的 ok（探针产出的任何状态都有规则可落，反之亦然）
    right_sides = {r["condition"].split()[-1] for r in kpi.values()}
    assert {s.value for s in status_enum} == right_sides | {status_enum.OK.value}


def test_evaluate_survival_rules_selects_by_status(tmp_path: Path):
    """规则选择直读生产 config/alert_rules.yaml（只读，无落板）。"""
    f = OpsAlertFeed(board_dir=tmp_path / "board", rules_path=_PROJECT_ROOT / "config" / "alert_rules.yaml")
    assert [r["id"] for r in f.evaluate_survival_rules("survival_breach")] == ["ALERT-KPI-001"]
    assert [r["id"] for r in f.evaluate_survival_rules("failure")] == ["ALERT-KPI-002"]
    assert f.evaluate_survival_rules("ok") == []
    assert f.survival_refresh_interval_s() == _ONE_DAY  # silence_window "1d" 取真源


# ── 发布形态（指标真的抵达 publisher）──


def test_tick_publishes_survival_metric_with_rule_shape(survival_feed: OpsAlertFeed, board: Path):
    payload = {"status": "survival_breach", "breaches": ["Sharpe 0.41 < 0.8"], "input": None}
    s = survival_feed.tick(
        probe=lambda: PROBE_IDLE,
        now=1000.0,
        survival_probe=lambda: payload,
    )
    assert s["ok"] is True and s["survival"]["status"] == "survival_breach"
    entries = [json.loads(x) for x in (board / "notifications.jsonl").read_text(encoding="utf-8").splitlines() if x]
    assert [e["key"] for e in entries] == ["ALERT-KPI-001"]  # 只命中 breach 规则，不连坐 failure
    e = entries[0]
    assert e["severity"] == "critical" and e["title"] == "survival_line_breach"
    assert e["labels"]["metric"] == "kpi.survival_line.status"
    assert e["labels"]["value"] == "survival_breach"
    assert e["labels"]["breaches"] == ["Sharpe 0.41 < 0.8"]
    assert "破生存线" in e["message"] and "Sharpe 0.41 < 0.8" in e["message"]


def test_tick_publishes_failure_rule_only(survival_feed: OpsAlertFeed):
    s = survival_feed.tick(
        probe=lambda: PROBE_IDLE,
        now=1000.0,
        survival_probe=lambda: {"status": "failure", "breaches": ["回撤 33% > 25%"], "input": None},
    )
    assert [op["key"] for op in s["survival"]["ops"]] == ["ALERT-KPI-002"]


def test_tick_ok_resolves_earlier_survival_alert(survival_feed: OpsAlertFeed):
    breach = {"status": "survival_breach", "breaches": ["x"], "input": None}
    survival_feed.tick(probe=lambda: PROBE_IDLE, now=1000.0, survival_probe=lambda: breach)
    s2 = survival_feed.tick(
        probe=lambda: PROBE_IDLE,
        now=1000.0 + _ONE_DAY + 1,
        survival_probe=lambda: {"status": "ok", "breaches": [], "input": None},
    )
    assert any(op["op"] == "resolved" and op["key"] == "ALERT-KPI-001" for op in s2["survival"]["ops"])
    assert survival_feed.list_active(now=1000.0 + _ONE_DAY + 2)[0]["resolved_at"]


def test_survival_input_absent_publishes_nothing_and_keeps_feed_alive(
    survival_feed: OpsAlertFeed, caplog: pytest.LogCaptureFixture
):
    """缺输入 → 生存线一段不产任何通知 + loud warning + tick 仍 ok（内存段照跑）。"""
    with caplog.at_level("WARNING", logger=feed_mod.logger.name):
        s = survival_feed.tick(
            probe=lambda: PROBE_OVER,
            now=1000.0,
            survival_probe=lambda: probe_survival_status(query_fn=lambda sql, timeout: ""),
        )
    assert s["ok"] is True
    assert s["survival"] == {"available": False, "reason": "input-unavailable", "status": None, "ops": []}
    # 板上有且仅有内存段的 OOM 项——生存线一个字节都没产出（不静默兜底、不伪造健康）
    assert [e["key"] for e in survival_feed.list_active(now=1000.0)] == ["ALERT-SYS-002"]
    assert any("metric not published" in str(r.msg) for r in caplog.records)


def test_survival_probe_crash_does_not_break_feed(survival_feed: OpsAlertFeed):
    def _boom():
        raise RuntimeError("nav source exploded")

    s = survival_feed.tick(probe=lambda: PROBE_IDLE, now=1000.0, survival_probe=_boom)
    assert s["ok"] is True and s["survival"]["available"] is False
    assert s["survival"]["ops"] == []


def test_survival_segment_not_suppressed_by_memory_probe_crash(survival_feed: OpsAlertFeed):
    """两段独立：内存探针炸 = 生存线指标照常落板（不连坐）。"""

    def _boom():
        raise RuntimeError("psutil exploded")

    s = survival_feed.tick(
        probe=_boom,
        now=1000.0,
        survival_probe=lambda: {"status": "failure", "breaches": ["连续亏损 6 个月"], "input": None},
    )
    assert s["ok"] is False and "probe failed" in s["reason"]
    assert s["survival"]["status"] == "failure"
    assert [e["key"] for e in survival_feed.list_active(now=1000.0)] == ["ALERT-KPI-002"]


def test_survival_recomputed_on_rule_cadence_not_every_tick(survival_feed: OpsAlertFeed):
    """日频指标按规则 silence_window 复评；30s tick 不重复打 CH。"""
    calls: list[int] = []

    def _probe():
        calls.append(1)
        return {"status": "ok", "breaches": [], "input": None}

    survival_feed.tick(probe=lambda: PROBE_IDLE, now=1000.0, survival_probe=_probe)
    survival_feed.tick(probe=lambda: PROBE_IDLE, now=1030.0, survival_probe=_probe)
    assert len(calls) == 1
    survival_feed.tick(probe=lambda: PROBE_IDLE, now=1000.0 + _ONE_DAY + 1, survival_probe=_probe)
    assert len(calls) == 2


def test_survival_refresh_interval_comes_from_rules(survival_feed: OpsAlertFeed, tmp_path: Path):
    import yaml

    assert survival_feed.survival_refresh_interval_s() == _ONE_DAY
    rules = {"rules": [{"id": "ALERT-SYS-001", "metric": "system.cpu_percent", "condition": "> 80"}]}
    p = tmp_path / "no_kpi.yaml"
    p.write_text(yaml.safe_dump(rules, allow_unicode=True), encoding="utf-8")
    assert OpsAlertFeed(board_dir=tmp_path / "b", rules_path=p).survival_refresh_interval_s() is None


# ── 死代码回归锁（监视器不再无人消费）──


def test_survival_monitor_is_no_longer_unreferenced_in_src():
    """src 生产代码必须真的引用 evaluate_survival_line（本次修复的终局断言）。"""
    src = _PROJECT_ROOT / "src"
    consumers: list[str] = []
    for p in src.rglob("*.py"):
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if "evaluate_survival_line" in text and p.name != "survival_line_monitor.py":
            consumers.append(p.name)
    assert "ops_alert_feed.py" in consumers, "生存线判定又回到产而不消"


def test_survival_end_to_end_from_nav_tsv_to_board(survival_feed: OpsAlertFeed, board: Path):
    """端到端（无网络）：合成净值 TSV → 判定 → 规则 → 通知板（真实探针，仅换查询通道）。"""
    tsv = _nav_tsv(_FALLING)
    s = survival_feed.tick(
        probe=lambda: PROBE_IDLE,
        now=1000.0,
        survival_probe=lambda: probe_survival_status(query_fn=lambda sql, timeout: tsv),
    )
    assert s["survival"]["available"] is True and s["survival"]["status"] == "failure"
    entries = [json.loads(x) for x in (board / "notifications.jsonl").read_text(encoding="utf-8").splitlines() if x]
    assert [e["key"] for e in entries] == ["ALERT-KPI-002"]
    assert entries[0]["labels"]["metric"] == "kpi.survival_line.status"
    # 落板规则由判定结果选择（非硬编 id）
    assert [r["id"] for r in survival_feed.evaluate_survival_rules(s["survival"]["status"])] == ["ALERT-KPI-002"]


# ── RSS 绝对值告警线落 YAML（排班表 v2 §2.3 C-1⑤ 消硬编码）─────────────────────


_MISSING = object()


def _repo_with_rss_line(root: Path, raw) -> Path:
    """临时仓根写 config/resource_optimization.yaml 的 ops_alerting.project_rss_alert_gb。"""
    import yaml

    cfg_dir = root / "config"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    body = {"ops_alerting": {"project_rss_alert_gb": raw}} if raw is not _MISSING else {"ops_alerting": {}}
    (cfg_dir / "resource_optimization.yaml").write_text(yaml.safe_dump(body), encoding="utf-8")
    return root


def test_rss_alert_line_read_from_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """兜底线数值来自 resource_optimization.yaml（代码零副本）：改表即改线。"""
    monkeypatch.setattr(feed_mod, "REPO_ROOT", _repo_with_rss_line(tmp_path / "a", 3.5))
    assert load_project_rss_alert_bytes() == int(3.5 * 1024**3)


def test_rss_alert_yaml_registration_matches_rule_source():
    """生产登记的 GiB 线必须与 ALERT-SYS-002 规则条件同值（两处登记分叉=测试红）。"""
    assert load_project_rss_alert_bytes() == THRESHOLD


@pytest.mark.parametrize("raw", [_MISSING, "abc", -1, 0])
def test_rss_alert_line_unusable_returns_none_without_inventing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, raw
):
    """缺键/非法值/非正值 → None（绝不臆造阈值兜一个数），且 loud warning。"""
    import yaml

    if raw is _MISSING:
        root = _repo_with_rss_line(tmp_path / "miss", None)
    elif raw == "abc":
        root = tmp_path / "bad"
        (root / "config").mkdir(parents=True, exist_ok=True)
        (root / "config" / "resource_optimization.yaml").write_text(
            yaml.safe_dump({"ops_alerting": {"project_rss_alert_gb": "abc"}}), encoding="utf-8"
        )
    else:
        root = _repo_with_rss_line(tmp_path / f"n{raw}", raw)
    monkeypatch.setattr(feed_mod, "REPO_ROOT", root)
    with caplog.at_level("WARNING", logger=feed_mod.logger.name):
        assert load_project_rss_alert_bytes() is None
    assert "load_project_rss_alert_bytes" in caplog.text


def test_rss_alert_line_missing_file_returns_none(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """整文件缺席（测试/裸机环境）→ None + 不抛。"""
    monkeypatch.setattr(feed_mod, "REPO_ROOT", tmp_path / "nonexistent_repo_root")
    assert load_project_rss_alert_bytes() is None


def test_fallback_rule_only_when_rule_source_has_no_memory_rule(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, board: Path
):
    """alert_rules.yaml 无内存字节型规则时，按 resource_optimization.yaml 兜底线合成规则。"""
    import yaml

    empty_rules = tmp_path / "empty_rules.yaml"
    empty_rules.write_text(
        yaml.safe_dump({"rules": [{"id": "X", "metric": "system.cpu_percent", "condition": "> 80"}]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(feed_mod, "REPO_ROOT", _repo_with_rss_line(tmp_path / "repo", THRESHOLD / 1024**3))
    f = OpsAlertFeed(board_dir=board, rules_path=empty_rules)
    assert [r["id"] for r in f.evaluate_memory_rules(float(THRESHOLD * 1.2))] == [FALLBACK_OOM_RULE_ID]
    assert f.evaluate_memory_rules(float(THRESHOLD * 0.5)) == []


def test_no_fallback_line_keeps_legacy_silent_semantics(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, board: Path
):
    """规则源与兜底线双双缺席 → 不告警（改造前语义），但绝不静默（loud warning）。"""
    import yaml

    empty_rules = tmp_path / "empty_rules.yaml"
    empty_rules.write_text(yaml.safe_dump({"rules": []}), encoding="utf-8")
    monkeypatch.setattr(feed_mod, "REPO_ROOT", tmp_path / "nonexistent_repo_root")
    f = OpsAlertFeed(board_dir=board, rules_path=empty_rules)
    assert f.evaluate_memory_rules(float(THRESHOLD * 9)) == []


def test_tick_end_to_end_via_fallback_line(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, board: Path):
    """端到端：兜底规则触发落板 → 回落滞回解除（证明合成规则可被 _threshold_of 解）。"""
    import yaml

    empty_rules = tmp_path / "empty_rules.yaml"
    empty_rules.write_text(yaml.safe_dump({"rules": []}), encoding="utf-8")
    monkeypatch.setattr(feed_mod, "REPO_ROOT", _repo_with_rss_line(tmp_path / "repo", THRESHOLD / 1024**3))
    f = OpsAlertFeed(board_dir=board, rules_path=empty_rules)
    s = f.tick(probe=lambda: int(THRESHOLD * 1.2), now=1000.0)
    assert s["triggered"] == [FALLBACK_OOM_RULE_ID]
    assert s["ops"] and s["ops"][0]["op"] == "created"
    s2 = f.tick(probe=lambda: int(THRESHOLD * 0.5), now=2000.0)
    assert any(op["op"] == "resolved" for op in s2["ops"]), s2["ops"]
