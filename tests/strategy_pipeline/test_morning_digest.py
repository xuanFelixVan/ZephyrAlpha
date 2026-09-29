# [BLUEPRINT] MOD-BT-232 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.strategy_pipeline.test_morning_digest
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.strategy_pipeline.morning_digest; zephyr.strategy_pipeline.promotion_advisory
# [CONSUMERS] MOD-BT-232 循环验收（F74 堵点3 晨报承接）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 测试隔离零生产 IO（advisory 目录/摘要落点全 tmp_path 注入）；alerter/渲染失败
#   一律 monkeypatch 假件（禁真通道）；不触碰生产 data/reports 与真实建议目录
# [MODIFY-GUARD] src/zephyr/strategy_pipeline/morning_digest.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-232 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""晨报摘要测试（F74 堵点3）：纯渲染（多事件/空事件/路径指针）/收集已决跳过/落盘刷新/空目录静默跳过/尾挂不反噬。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import zephyr.strategy_pipeline.morning_digest as md  # noqa: E402
from zephyr.strategy_pipeline import promotion_advisory as pa  # noqa: E402


# ---------- 夹具：tmp advisory 树 ----------
def _make_adv(advisory_dir: Path, sid: str, rec: str = "promote", *, decided: bool = False) -> Path:
    adv = {
        "advisory_id": f"ADV-20260928-{sid}",
        "strategy_id": sid,
        "lifecycle_now": "sim",
        "recommendation": rec,
        "generated_at": "2026-09-28T08:00:00+00:00",
    }
    path = advisory_dir / f"ADV-20260928-{sid}.json"
    path.write_text(json.dumps(adv, ensure_ascii=False), encoding="utf-8")
    if decided:
        (advisory_dir / f"ADV-20260928-{sid}.decision.json").write_text("{}", encoding="utf-8")
    return path


@pytest.fixture
def adv_dir(tmp_path):
    d = tmp_path / "advisories"
    d.mkdir()
    return d


# ---------- 纯渲染 ----------
def test_render_multi_events_contains_todo_lines():
    events = [
        {
            "advisory_id": "ADV-20260928-A",
            "strategy_id": "STR-A",
            "lifecycle_now": "sim",
            "recommendation": "promote",
            "generated_at": "2026-09-28T08:00:00+00:00",
            "report_ref": "data/strategy_intake/promotion_advisories/ADV-20260928-A.json",
        },
        {
            "advisory_id": "ADV-20260928-B",
            "strategy_id": "STR-B",
            "lifecycle_now": "sim",
            "recommendation": "demote",
            "generated_at": "2026-09-28T08:00:00+00:00",
            "report_ref": "data/strategy_intake/promotion_advisories/ADV-20260928-B.json",
        },
    ]
    text = md.render_digest(events, date_str="2026-09-28")
    assert text.startswith("# 晨报摘要 · 2026-09-28")
    assert "## 转正建议书待办区" in text
    assert "**STR-A**（sim）结论 **promote**" in text
    assert "建议批准进整装" in text
    assert "**STR-B**（sim）结论 **demote**" in text
    assert "建议降档" in text
    # 每条带报告文件路径指针
    assert "`data/strategy_intake/promotion_advisories/ADV-20260928-A.json`" in text
    assert "`data/strategy_intake/promotion_advisories/ADV-20260928-B.json`" in text
    # 完整报告指针一句
    assert "完整报告见" in text and "promotion-reports" in text and "#promotion" in text


def test_render_empty_events_still_renders():
    text = md.render_digest([], date_str="2026-09-28")
    assert "# 晨报摘要 · 2026-09-28" in text
    assert "无待办" in text
    assert "完整报告见" in text


def test_render_unknown_rec_falls_back_generic_action():
    ev = {
        "advisory_id": "ADV-X",
        "strategy_id": "STR-C",
        "lifecycle_now": "sim",
        "recommendation": "hold",
        "report_ref": "x.json",
    }
    text = md.render_digest([ev], date_str="2026-09-28")
    assert "到前端 #promotion 页查看并拍板" in text


# ---------- 收集 ----------
def test_collect_skips_decided_and_bad_packages(adv_dir):
    _make_adv(adv_dir, "STR-A")
    _make_adv(adv_dir, "STR-B", rec="demote")
    _make_adv(adv_dir, "STR-DECIDED", decided=True)
    (adv_dir / "ADV-20260928-STR-BROKEN.json").write_text("{not json", encoding="utf-8")
    events = md.collect_pending_advisories(adv_dir)
    assert [e["strategy_id"] for e in events] == ["STR-A", "STR-B"]
    assert events[0]["report_ref"].endswith("ADV-20260928-STR-A.json")


def test_collect_missing_dir_returns_empty(tmp_path):
    assert md.collect_pending_advisories(tmp_path / "nope") == []


def test_collect_and_refresh_skip_poison_shapes(adv_dir, tmp_path):
    """毒 ADV 包（顶层 list/标量而非 dict）跳过不抛（redblue R4c 回归钉）：

    一个毒包不许打死整份晨报——合法包照收、毒包记 warning 跳过、refresh 仍 ok=True。
    """
    _make_adv(adv_dir, "STR-A")
    (adv_dir / "ADV-20260928-STR-POISON-LIST.json").write_text("[1, 2, 3]", encoding="utf-8")
    (adv_dir / "ADV-20260928-STR-POISON-SCALAR.json").write_text("42", encoding="utf-8")
    events = md.collect_pending_advisories(adv_dir)
    assert [e["strategy_id"] for e in events] == ["STR-A"]
    out = tmp_path / "digest" / "morning_digest.md"
    r = md.refresh_morning_digest(adv_dir, out, date_str="2026-09-28")
    assert r["ok"] is True and r["rc"] == 0 and r["pending"] == 1
    assert "**STR-A**" in out.read_text(encoding="utf-8")


# ---------- 刷新落盘 ----------
def test_refresh_writes_digest(adv_dir, tmp_path):
    _make_adv(adv_dir, "STR-A")
    _make_adv(adv_dir, "STR-B", rec="demote")
    out = tmp_path / "digest" / "morning_digest.md"
    r = md.refresh_morning_digest(adv_dir, out, date_str="2026-09-28")
    assert r["ok"] is True and r["rc"] == 0 and r["pending"] == 2
    text = out.read_text(encoding="utf-8")
    assert "**STR-A**" in text and "**STR-B**" in text and "无待办" not in text


def test_refresh_skips_empty_dir_silently(tmp_path):
    empty = tmp_path / "empty"
    out = tmp_path / "digest" / "morning_digest.md"
    r = md.refresh_morning_digest(empty, out, date_str="2026-09-28")
    assert r.get("skipped") == "advisory_dir_empty_or_missing"
    assert not out.exists()


def test_refresh_failure_never_raises(tmp_path):
    """落盘目标非法（父路径是文件）→ 折进返回 dict，不外抛。"""
    adv = tmp_path / "adv"
    adv.mkdir()
    _make_adv(adv, "STR-A")
    blocker = tmp_path / "blocker"
    blocker.write_text("x", encoding="utf-8")
    r = md.refresh_morning_digest(adv, blocker / "nested" / "digest.md", date_str="2026-09-28")
    assert r["ok"] is False and r["rc"] == -1 and "reason" in r


# ---------- advisory due 尾挂：不反噬 ----------
def _isolate_due(monkeypatch):
    """run_promotion_advisory_due 外围假件：零生产扫描/零真 combo 子进程/零真推送。"""
    monkeypatch.setattr(pa, "build_advisories", lambda: [])
    monkeypatch.setattr(pa, "run_promotion_combo_gate", lambda: {"rc": 0, "skipped": "advisory_dir_empty_or_missing"})


def test_due_tail_digest_happy(monkeypatch):
    _isolate_due(monkeypatch)
    monkeypatch.setattr(md, "refresh_morning_digest", lambda *a, **k: {"ok": True, "rc": 0, "pending": 0})
    out = pa.run_promotion_advisory_due({"id": "e1"})
    assert out["digest_rc"] == 0
    assert out["combo_skipped"] == "advisory_dir_empty_or_missing"


def test_due_tail_digest_failure_no_poison(monkeypatch):
    """晨报刷新抛异常 → advisory due 仍绿（digest_rc=-1，主流程零反噬）。"""
    _isolate_due(monkeypatch)

    def _boom(*a, **k):
        raise RuntimeError("digest exploded")

    monkeypatch.setattr(md, "refresh_morning_digest", _boom)
    out = pa.run_promotion_advisory_due({"id": "e2"})
    assert out["digest_rc"] == -1
    assert out["built"] == 0
