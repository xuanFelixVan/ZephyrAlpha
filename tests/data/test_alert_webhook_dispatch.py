# [A_test] module_id: MOD-L00-004_alert_webhook_dispatch_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.data.test_alert_webhook_dispatch
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.alert_webhook_dispatch; zephyr.data.alerter;
#   zephyr.infrastructure.system_telemetry.alerts.ops_alert_feed; stdlib(http.server/threading)
# [CONSUMERS] CI pytest
# [STARTUP] test_only
# [MATURITY] testing
# [INVARIANTS] 本套**不 mock 被验防线自身**（poster=真 urllib、trail/state=真文件、通知板=真 OpsAlertFeed 落盘）；
#   唯一注入面=接收端换成本地回环 http 桩（禁真外发、禁打任何公网地址）；
#   全部输出落 tmp_path（禁写 data/ 业务目录）；每条"通"的断言都读盘/读桩核实，不看函数返回值
#   （规范 §1 第③向：本仓实证 cash_curve 内存有值、落盘 0 点、测试全绿）
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=契约不成立；无自愈
# [TESTS] python -m pytest tests/data/test_alert_webhook_dispatch.py -q
# [TTL] permanent
"""alert_webhook_dispatch 双验证套件（T2：本地 http 桩真收发 + 文件落盘真读，并证明它能红）.

覆盖：
  ①双验证 —— 真接收端（127.0.0.1 http 桩）真收到带正确载荷的请求 + 留痕/状态文件真落盘
  ②能红 —— 关掉接收端 / 接收端返 500 → 通道必须**报失败并留痕**，不得静默成功
  ③fail-closed —— 缺省 enabled=false/端点为空 → blocked 且"通道不可用"投影到通知板
  ④按端点去重 —— A 端成功不得替 B 端吞掉同一条告警（接管时实测的原始缺陷回归钉）
  ⑤升级开关有真读者 —— flags.alerts.auto_escalation 两态行为可测（BRK-052 实现侧）
  ⑥alerter 事件钩子 —— CRITICAL 落盘成功即触发外发；ERROR 不触发；钩子不反噬告警器
"""

from __future__ import annotations

import json
import threading
import types
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

import pytest

from zephyr.data.alert_webhook_dispatch import (
    AlertWebhookConfig,
    AlertWebhookDispatcher,
    AlertWebhookEndpoint,
    AlertWebhookError,
    channel_health,
    dispatch_on_failure_event,
    load_alert_webhook_config,
    read_auto_escalation_flag,
    scan_critical_failures,
    scan_kill_switch,
)
from zephyr.data.alerter import LEVEL_CRITICAL, LEVEL_ERROR, Alerter

# ── 本地回环 http 桩（真 socket + 真 urllib 客户端；禁公网）───────────────


class _AlarmStubHandler(BaseHTTPRequestHandler):
    """记录收到的请求；按 server.mode 返 200 或 500。"""

    def do_POST(self) -> None:  # noqa: N802 — BaseHTTPRequestHandler 命名约定
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length)
        srv = self.server
        srv.received.append({  # type: ignore[attr-defined]
            "path": self.path,
            "body": body.decode("utf-8", "replace"),
            "auth": self.headers.get("Authorization") or "",
            "content_type": self.headers.get("Content-Type") or "",
        })
        code = 200 if getattr(srv, "mode", "ok") == "ok" else 500
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"routed": true}')

    def log_message(self, *args: Any) -> None:
        return  # 静音：测试期禁污染宿主日志


def _start_stub(mode: str = "ok") -> HTTPServer:
    srv = HTTPServer(("127.0.0.1", 0), _AlarmStubHandler)
    srv.received = []  # type: ignore[attr-defined]
    srv.mode = mode  # type: ignore[attr-defined]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def _stub_url(srv: HTTPServer, path: str = "/hook") -> str:
    host, port = srv.server_address[:2]
    return f"http://{host}:{port}{path}"


def _stop_stub(srv: HTTPServer) -> None:
    srv.shutdown()
    srv.server_close()


def _make_cfg(tmp_path: Path, *, urls: tuple[str, ...], enabled: bool = True,
              names: tuple[str, ...] = ("stub",), tag: str = "") -> AlertWebhookConfig:
    runtime = tmp_path / f"runtime{tag}"
    return AlertWebhookConfig(
        enabled=enabled,
        endpoints=tuple(AlertWebhookEndpoint(name=n, url=u) for n, u in zip(names, urls)),
        failures_dir=tmp_path / f"failures{tag}",
        state_path=runtime / "state.json",
        trail_path=runtime / "trail.jsonl",
    )


def _trigger(task_id: str, error: str = "e") -> dict[str, Any]:
    return {"source_kind": "failure_file", "file": "", "task_id": task_id,
            "level": LEVEL_CRITICAL, "error": error, "timestamp": "", "origin": ""}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    """读盘核实（不看函数返回值）。"""
    if not path.exists():
        return []
    return [json.loads(line) for line in
            path.read_text(encoding="utf-8").splitlines() if line.strip()]


@pytest.fixture()
def board(tmp_path: Path) -> types.SimpleNamespace:
    """真 OpsAlertFeed（板目录重定向到 tmp）+ 调用记录。"""
    from zephyr.infrastructure.system_telemetry.alerts.ops_alert_feed import OpsAlertFeed

    board_dir = tmp_path / "ops_notifications"
    feed = OpsAlertFeed(board_dir=board_dir, module_id="test-alert-webhook")
    ns = types.SimpleNamespace(feed=feed, dir=board_dir, path=board_dir / "notifications.jsonl")
    return ns


def _board_records(ns: types.SimpleNamespace) -> list[dict[str, Any]]:
    if not ns.path.exists():
        return []
    return [json.loads(l) for l in
            ns.path.read_text(encoding="utf-8").splitlines() if l.strip()]


# ── ①双验证：桩真收到 + 文件真落盘 ─────────────────────────────────


def test_dual_verification_stub_received_and_files_landed(tmp_path: Path, board) -> None:
    srv = _start_stub("ok")
    try:
        cfg = _make_cfg(tmp_path, urls=(_stub_url(srv),))
        rec = {"task_id": "kline_daily_incremental", "level": LEVEL_CRITICAL,
               "error": "CH 写入超时", "timestamp": "2026-09-18T10:00:00+00:00",
               "source": "akshare"}
        out = dispatch_on_failure_event(rec, file_name="20260918_x.json", config=cfg)
        assert out["action"] == "dispatched", out
        received = srv.received
    finally:
        _stop_stub(srv)

    assert len(received) == 1, "接收端未收到任何请求"
    body = json.loads(received[0]["body"])
    assert body["schema"] == "zephyralpha.alert_webhook.v1"
    assert body["count"] == 1 and body["escalated"] is False
    assert body["alerts"][0]["task_id"] == "kline_daily_incremental"
    assert body["alerts"][0]["level"] == "CRITICAL"
    assert "CH 写入超时" in body["alerts"][0]["error"]
    assert received[0]["content_type"] == "application/json"

    posts = [t for t in _read_jsonl(cfg.trail_path) if t.get("kind") == "post"]
    assert len(posts) == 1 and posts[0]["ok"] is True and posts[0]["status"] == 200
    state = json.loads(cfg.state_path.read_text(encoding="utf-8"))
    assert len(state["delivered_keys"]) == 1
    assert state["delivered_keys"][0].startswith("stub\x1f")
    assert channel_health(config=cfg)["status"] == "available"


def test_real_ops_board_projection_lands_on_disk(tmp_path: Path, board) -> None:
    """blocked/failed 投影到**真** OpsAlertFeed（promotion 页读的块板）——落盘读回核实。"""
    cfg = _make_cfg(tmp_path, urls=(), enabled=False)
    disp = AlertWebhookDispatcher(cfg, board_publisher=board.feed.publish)
    out = disp.dispatch_triggers([_trigger("t_board")])
    assert out["action"] == "blocked"
    entries = _board_records(board)
    assert entries and entries[0]["key"] == "alert-webhook/channel-unavailable"
    assert entries[0]["severity"] == "critical"
    assert "通道不可用" in entries[0]["title"]
    active = board.feed.list_active()
    assert any(a["key"] == "alert-webhook/channel-unavailable" for a in active), \
        "投影必须出现在前端读的活动清单里，否则等于写了没人读"


# ── ②能红：接收端关掉 / 接收端返 500 ──────────────────────────────


def test_can_go_red_receiver_closed_reported_not_silent(tmp_path: Path, board) -> None:
    srv = _start_stub("ok")
    url = _stub_url(srv)
    _stop_stub(srv)  # 端口关死 → 真连接拒绝（仍回环，禁真外发）
    cfg = _make_cfg(tmp_path, urls=(url,))
    out = AlertWebhookDispatcher(cfg, board_publisher=board.feed.publish).dispatch_triggers(
        [_trigger("t_dead")])
    assert out["action"] == "dispatched"
    assert out["sent"] == 0 and out["failed"] == 1
    assert out["endpoints"][0]["ok"] is False
    assert not cfg.state_path.exists(), "未送达不得被记成已送达"
    posts = [t for t in _read_jsonl(cfg.trail_path) if t.get("kind") == "post"]
    assert posts and posts[0]["ok"] is False and posts[0]["status"] == 0
    entries = _board_records(board)
    assert any("投递失败" in e["title"] for e in entries), entries
    assert channel_health(config=cfg)["status"] == "failing"


def test_can_go_red_receiver_500_not_silent_success(tmp_path: Path, board) -> None:
    srv = _start_stub("boom")
    try:
        cfg = _make_cfg(tmp_path, urls=(_stub_url(srv),))
        out = AlertWebhookDispatcher(cfg, board_publisher=board.feed.publish).dispatch_triggers(
            [_trigger("t500")])
        assert out["failed"] == 1 and out["sent"] == 0
        assert out["endpoints"][0]["status"] == 500
        assert not cfg.state_path.exists()
    finally:
        _stop_stub(srv)
    assert any("投递失败" in e["title"] for e in _board_records(board))


def test_undelivered_alert_retried_on_next_event(tmp_path: Path, board) -> None:
    """未送达的告警在下一次事件时必须重试（禁被去重永久吞掉）。"""
    dead = _start_stub("ok")
    dead_url = _stub_url(dead)
    _stop_stub(dead)
    srv = _start_stub("ok")
    try:
        cfg = _make_cfg(tmp_path, urls=(_stub_url(srv),))
        disp = AlertWebhookDispatcher(cfg, board_publisher=board.feed.publish)
        first = disp.dispatch_triggers([_trigger("t_a")])
        assert first["sent"] == 1
        # t_a 已送达 → 去重；但新事件 t_b 必须照常出去
        second = disp.dispatch_triggers([_trigger("t_a"), _trigger("t_b")])
        assert {a["task_id"] for a in json.loads(srv.received[-1]["body"])["alerts"]} == {"t_b"}
        # 打向关掉的端点：不进去重表 → 同一条下轮仍会推
        cfg_dead = _make_cfg(tmp_path, urls=(dead_url,), tag="_dead")
        AlertWebhookDispatcher(cfg_dead, board_publisher=board.feed.publish).dispatch_triggers(
            [_trigger("t_c")])
        assert not cfg_dead.state_path.exists()
        third = disp.dispatch_triggers([_trigger("t_c")])
        assert third["sent"] == 1
    finally:
        _stop_stub(srv)
    assert len(srv.received) == 3, "t_b 与 t_c 各一次（t_a 已送达被去重）"


# ── ③fail-closed 缺省态 ───────────────────────────────────────────


def test_default_fail_closed_blocked_is_landed_and_observable(tmp_path: Path, board) -> None:
    cfg = _make_cfg(tmp_path, urls=(), enabled=False)
    out = AlertWebhookDispatcher(cfg, board_publisher=board.feed.publish).dispatch_triggers(
        [_trigger("t")])
    assert out["action"] == "blocked" and "enabled=false" in out["reason"]
    blocked = [t for t in _read_jsonl(cfg.trail_path) if t.get("kind") == "blocked"]
    assert blocked and blocked[0]["triggers"] == 1, "受阻必须落痕（禁静默丢弃）"
    assert channel_health(config=cfg)["status"] == "blocked"


def test_enabled_but_zero_endpoint_is_blocked(tmp_path: Path) -> None:
    cfg = _make_cfg(tmp_path, urls=(), enabled=True)
    assert cfg.dispatchable is False
    assert "endpoints 为空" in cfg.blocked_reason


def test_missing_config_file_defaults_to_disabled(tmp_path: Path) -> None:
    cfg = load_alert_webhook_config(tmp_path / "not_there.yaml")
    assert cfg.enabled is False and cfg.endpoints == ()


# ── ④按端点去重（接管时实测的原始缺陷回归钉）─────────────────────


def test_per_endpoint_dedup_alive_does_not_swallow_dead(tmp_path: Path, board) -> None:
    srv = _start_stub("ok")
    dead = _start_stub("ok")
    dead_url = _stub_url(dead)
    _stop_stub(dead)
    try:
        cfg = _make_cfg(tmp_path, urls=(_stub_url(srv), dead_url), names=("alive", "dead"))
        disp = AlertWebhookDispatcher(cfg, board_publisher=board.feed.publish)
        trig = [_trigger("t_dup")]
        first = disp.dispatch_triggers(trig)
        assert first["sent"] == 1 and first["failed"] == 1
        second = disp.dispatch_triggers(trig)
        by_name = {r["name"]: r for r in second["endpoints"]}
        assert by_name["alive"].get("skipped") == "dedup", "健康端点不得重复投递"
        assert by_name["dead"].get("delivered") == 1, "故障端点必须重试（共享指纹会把它吞掉）"
        assert len(srv.received) == 1
    finally:
        _stop_stub(srv)


# ── ⑤升级开关必须有真读者（BRK-052 实现侧；flag 翻转本身属 Owner 门位）──


def _write_flags(tmp_path: Path, value: str, name: str = "flags.yaml") -> Path:
    fp = tmp_path / name
    fp.write_text(f"flags:\n  alerts:\n    enabled: true\n    auto_escalation: {value}\n",
                  encoding="utf-8", newline="\n")
    return fp


def test_escalation_flag_reader_two_states(tmp_path: Path) -> None:
    assert read_auto_escalation_flag(_write_flags(tmp_path, "false", "f0.yaml"))["enabled"] is False
    assert read_auto_escalation_flag(_write_flags(tmp_path, "true", "f1.yaml"))["enabled"] is True
    missing = read_auto_escalation_flag(tmp_path / "nope.yaml")
    assert missing["enabled"] is False and missing["observed"] == "missing"


def test_escalation_off_skips_backlog_on_resends_it(tmp_path: Path, board) -> None:
    flags_off = _write_flags(tmp_path, "false", "flags_off.yaml")
    flags_on = _write_flags(tmp_path, "true", "flags_on.yaml")
    srv = _start_stub("ok")
    try:
        cfg = _make_cfg(tmp_path, urls=(_stub_url(srv),))
        trig = [_trigger("t_esc")]
        off = AlertWebhookDispatcher(cfg, board_publisher=board.feed.publish, flags_path=flags_off)
        on = AlertWebhookDispatcher(cfg, board_publisher=board.feed.publish, flags_path=flags_on)
        assert off.dispatch_triggers(trig)["sent"] == 1
        r_off = off.dispatch_triggers(trig)
        assert r_off["endpoints"][0].get("skipped") == "dedup", r_off
        r_on = on.dispatch_triggers(trig)
        assert r_on["escalated"] is True and r_on["sent"] == 1
        body = json.loads(srv.received[-1]["body"])
        assert body["escalated"] is True and body["count"] == 1
    finally:
        _stop_stub(srv)


# ── ⑥alerter 事件钩子与触发源二 ──────────────────────────────────


def test_alerter_hook_fires_on_critical_only(tmp_path: Path, monkeypatch) -> None:
    srv = _start_stub("ok")
    cfg = _make_cfg(tmp_path, urls=(_stub_url(srv),))
    import zephyr.data.alert_webhook_dispatch as m

    monkeypatch.setattr(m, "load_alert_webhook_config", lambda *a, **k: cfg)
    try:
        al = Alerter(failures_dir=tmp_path / "alerter_failures")
        # 冷却窗（_FAILURE_COOLDOWN_SEC=300/同 task_id）会挡同日重发 → 两条用不同 task_id
        assert al.notify("task_b_err", "普通失败", level=LEVEL_ERROR) is True
        assert len(srv.received) == 0, "ERROR 级不得外发（触发源判据）"
        assert al.notify("task_b_crit", "危机级失败", level=LEVEL_CRITICAL) is True
    finally:
        _stop_stub(srv)
    assert len(srv.received) == 1
    assert json.loads(srv.received[0]["body"])["alerts"][0]["task_id"] == "task_b_crit"
    posts = [t for t in _read_jsonl(cfg.trail_path) if t.get("kind") == "post"]
    assert posts and posts[0]["ok"] is True


def test_alerter_notify_survives_broken_dispatch(tmp_path: Path, monkeypatch) -> None:
    """外发面全炸也不许反噬告警器（alerter [ERROR_CONTRACT]=不抛）。"""
    import zephyr.data.alert_webhook_dispatch as m

    def _boom(*a: Any, **k: Any) -> None:
        raise RuntimeError("外发模块不可用")

    monkeypatch.setattr(m, "dispatch_on_failure_event", _boom)
    al = Alerter(failures_dir=tmp_path / "failures")
    assert al.notify("t", "e", level=LEVEL_CRITICAL) is True
    assert list((tmp_path / "failures").glob("*.json"))


def test_kill_switch_probe_failure_counts_as_trigger(monkeypatch) -> None:
    import zephyr.security.access_control.kill_switch as ks

    def _boom() -> None:
        raise RuntimeError("探针不可达")

    monkeypatch.setattr(ks, "get_kill_switch", _boom, raising=False)
    hits = scan_kill_switch()
    assert len(hits) == 1 and hits[0]["level"] == LEVEL_CRITICAL
    assert "探针失败" in hits[0]["error"], "不知道≠没事（fail-closed 出声）"


def test_scan_prunes_by_filename_date(tmp_path: Path) -> None:
    root = tmp_path / "failures"
    root.mkdir()
    (root / "20260101_old_x.json").write_text(
        json.dumps({"task_id": "old", "level": LEVEL_CRITICAL, "error": "e"}), encoding="utf-8")
    (root / "20260918_new_x.json").write_text(
        json.dumps({"task_id": "new", "level": LEVEL_CRITICAL, "error": "e",
                    "timestamp": "2026-09-18T10:00:00+00:00"}), encoding="utf-8")
    hits = scan_critical_failures(root, since_iso="2026-09-18T00:00:00+00:00")
    assert [h["task_id"] for h in hits] == ["new"], "日期前缀剪枝必须生效（事件路径禁全目录 I/O）"


def test_endpoint_url_scheme_rejects_non_http() -> None:
    with pytest.raises(AlertWebhookError):
        AlertWebhookEndpoint(name="evil", url="file:///c:/windows/win.ini")


def test_unknown_config_key_is_hard_error(tmp_path: Path) -> None:
    fp = tmp_path / "cfg.yaml"
    fp.write_text("enabled: true\nendppoints: []\n", encoding="utf-8", newline="\n")
    with pytest.raises(AlertWebhookError):
        load_alert_webhook_config(fp)


# ── ⑦本批接线时实测到的两处自带缺陷的回归钉（详见车道交工报告 §2）──────


def test_relative_sink_paths_are_anchored_not_cwd_relative(tmp_path: Path,
                                                           monkeypatch) -> None:
    """state/trail 必须锚到固定根，**绝不随 cwd 解析**。

    原实现把配置里的相对路径直接 Path() 用 → 去重账本随工作目录分裂：
    换目录跑就"没发过"→ 同一 CRITICAL 重发，或在别的 worktree 造出第二份 trail。
    """
    from zephyr.data.alert_webhook_dispatch import AlertWebhookConfig as _Cfg
    from zephyr.data.alert_webhook_dispatch import AlertWebhookEndpoint as _Ep

    monkeypatch.chdir(tmp_path)  # 故意把 cwd 挪走
    sink = tmp_path / "sinkroot"
    monkeypatch.setenv("ZEPHYR_ALERT_WEBHOOK_DIR", str(sink))
    cfg = _Cfg(enabled=True, endpoints=(_Ep(name="e1", url="http://127.0.0.1:1/h"),))
    disp = AlertWebhookDispatcher(cfg)
    assert disp.cfg.trail_path.is_absolute()
    assert str(disp.cfg.trail_path).startswith(str(sink)), disp.cfg.trail_path
    assert str(disp.cfg.state_path).startswith(str(sink)), disp.cfg.state_path
    # 绝对路径注入（测试/显式配置）不得被改写
    absolute = _Cfg(enabled=True, endpoints=cfg.endpoints,
                    state_path=tmp_path / "abs_state.json",
                    trail_path=tmp_path / "abs_trail.jsonl")
    d2 = AlertWebhookDispatcher(absolute)
    assert d2.cfg.trail_path == tmp_path / "abs_trail.jsonl"


def test_alerter_critical_hook_leaves_production_sinks_untouched(tmp_path: Path) -> None:
    """alerter 的 CRITICAL 钩子**不得**在测试期写真实去重账本/真实通知板。

    这是钩子接线自带副作用的漏写钉：删掉 tests/conftest.py 的
    _isolate_alert_webhook_sinks → 本条必须转红（否则测试会给 Owner 的生产
    promotion 页挂一条假"通道不可用"红条——本仓实证：接线初跑即写了 1 条）。
    本条**不注入配置**，走真实缺省（enabled=false → fail-closed blocked 分支，
    正是会落 trail + 投影板的那条路径），因此它测的是隔离网本身。
    """
    from zephyr.shared.io.paths import REPO_ROOT

    real_trail = Path(REPO_ROOT) / "data" / "runtime" / "alert_webhook_trail.jsonl"
    real_board = Path(REPO_ROOT) / ".runtime" / "ops_notifications" / "notifications.jsonl"
    before = {p: (p.read_bytes() if p.exists() else None) for p in (real_trail, real_board)}

    al = Alerter(failures_dir=tmp_path / "failures")
    assert al.notify("isolation_probe", "探针：CRITICAL 落盘", level=LEVEL_CRITICAL) is True

    for p, blob in before.items():
        now = p.read_bytes() if p.exists() else None
        assert now == blob, f"测试期写穿了生产落点 {p}（隔离 fixture 失效）"
    assert json.loads(list((tmp_path / "failures").glob("*.json"))[0]
                      .read_text(encoding="utf-8"))["level"] == LEVEL_CRITICAL
