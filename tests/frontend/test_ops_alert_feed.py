# [TTL] permanent
# [MODULE] tests.frontend.test_ops_alert_feed
# [DOMAIN] D_FRONTEND
"""A2 治理战役验收单测：运营告警供给线（OOM critical → promotion 页横幅）。

覆盖：
- OpsAlertFeed 板三操作：publish 创建/静默窗口去重/解除+保留期（tmp_path 隔离）
- tick 端到端（假探针）：9GB 触发 ALERT-SYS-002 发布 → 持续触发静默刷新 → 回落滞回解除
- 探针 fail-safe：probe 抛异常 → ok:false 不上抛；真 psutil 探针返回正数
- GET /api/ops-notifications：有数据透传 / 板异常降级（TestClient + 板目录重定向）
- 前端接线静态断言：api.js 通道 + promotion.js 横幅注入/轮询/静默降级
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

from zephyr.infrastructure.system_telemetry.alerts.ops_alert_feed import (  # noqa: E402
    OpsAlertFeed,
    probe_project_rss_bytes,
)

GB = 1024**3
THRESHOLD = 8 * GB  # 与 ALERT-SYS-002 condition "> 8589934592" 同源


@pytest.fixture()
def board(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """通知板目录重定向 tmp_path（测试隔离主通道，双保险：注入+环境变量）。"""
    d = tmp_path / "ops_notifications"
    monkeypatch.setenv("ZEPHYR_OPS_NOTIFICATION_DIR", str(d))
    return d


@pytest.fixture()
def feed(board: Path, tmp_path: Path) -> OpsAlertFeed:
    """注入临时规则的 feed（内存规则阈值 8GB critical + 一条 warning 对照）。"""
    rules = {
        "rules": [
            {
                "id": "ALERT-SYS-002",
                "name": "oom_risk",
                "severity": "critical",
                "metric": "system.memory_rss_bytes",
                "condition": f"> {THRESHOLD}",
                "description": "内存即将耗尽（>8GB RSS）",
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
    s = feed.tick(probe=lambda: int(9 * GB), now=1000.0)
    assert s["ok"] is True and s["triggered"] == ["ALERT-SYS-002"]
    assert s["ops"] and s["ops"][0]["op"] == "created"
    active = feed.list_active(now=1000.0)
    assert len(active) == 1 and active[0]["severity"] == "critical"
    assert "9" in str(active[0]["labels"]["value"])


def test_tick_silence_then_resolve_on_recovery(feed: OpsAlertFeed):
    feed.tick(probe=lambda: int(9 * GB), now=1000.0)
    s2 = feed.tick(probe=lambda: int(9.5 * GB), now=1100.0)  # 仍超阈：静默刷新
    assert s2["ops"] and s2["ops"][0]["op"] == "refresh"
    # 回落到阈值*0.9 以下 → 解除（滞回）
    s3 = feed.tick(probe=lambda: int(7 * GB), now=1200.0)
    assert any(op["op"] == "resolved" for op in s3["ops"])
    assert feed.list_active(now=1200.0)[0]["resolved_at"] == 1200.0
    # 高于滞回线但低于阈值 → 不触发也不解除（滞回带内保持原状）
    feed.publish(key="ALERT-SYS-002", severity="critical", title="t", message="m", now=1300.0)
    s4 = feed.tick(probe=lambda: int(7.6 * GB), now=1400.0)
    assert s4["ops"] == []


def test_tick_warning_not_published(feed: OpsAlertFeed):
    """非 critical 规则不落板（首期只承 OOM critical）。"""
    s = feed.tick(probe=lambda: int(1 * GB), now=1000.0)
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
                "message": "内存即将耗尽（>8GB RSS）（实测 9663676416 字节）",
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
