# [BLUEPRINT] MOD-AUTO-E1G-001 | docs/_working/fullflow_mining/01_strategy_factory/08_f20_lane_g_stomach_intake.md | §接线
# [PROVISIONAL] 暂编号：docs/03_modules 解冻后按注册表重编（挂单 H-01）
# [MODULE] tests.zephyr.data.test_lane_g_intake_sweep_wiring
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] src.zephyr.data.scheduler (_run_special_schedule); scripts.backtest.lane_g_stomach_intake
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 零网络零 LLM 零真告警通道零生产路径写入（inbox/台账全落 tmp_path；
#   假 chat+假 alerter 注入=唯一喂料面；总闸文件只断言不存在，不创建）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=AssertionError（pytest 收集）
# [TESTS] 本文件
# [A_module] module_id=MOD-AUTO-E1G-001 | layer=test | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""车道G 兜底扫描接线单测（F20 断链①收口，2026-09-27 st-chief4x-gut-20260927）。

断言三件事（任务书口径）：
1. 增量触发被调：lane_g_intake_sweep 槽 → _run_special_schedule 分派 → run_intake_sweep
   （既有入口，禁复制）被调且注入调度器 alerter；
2. 游标推进：seen log（url_md5）记账后重复扫描零重消化（增量语义，禁全量重跑）；
3. 失败降级告警：单条目失败→WARN 不抛；整体异常→ERROR 且槽位返回 False 不反噬调度器。
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

_ROOT = Path(__file__).resolve().parents[3]
for _p in (str(_ROOT), str(_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts.backtest import lane_g_stomach_intake as lane_g  # noqa: E402
from src.zephyr.data.scheduler import _run_special_schedule  # noqa: E402

SAMPLE_INBOX = """# 情报收件箱 2026-09-27T00:00:00Z

## 1. Momentum in statistical arbitrage

- 链接: https://arxiv.org/abs/2609.99901  |  日期: Sat, 26 Sep 2026 00:00:0  |  命中词: `momentum`
- 摘要: 统计套利中的动量效应研究。

## 2. Overfitting in backtest selection

- 链接: https://arxiv.org/abs/2609.99902  |  日期: Sat, 26 Sep 2026 00:00:0  |  命中词: `overfitting`
- 摘要: 回测选择中的过拟合风险。
"""


class FakeChat:
    """假 LLM（零网络零 LSG 实调，与 tests/backtest 同款注入位）。"""

    def __init__(self, replies: dict[str, str] | None = None, default: str = "[]"):
        self.replies = replies or {}
        self.default = default
        self.prompts: list[str] = []

    def ask(self, prompt, *, system="", temperature=None, max_tokens=None):
        self.prompts.append(prompt)
        for kw, rep in self.replies.items():
            if kw in prompt:
                return rep
        return self.default


class FakeAlerter:
    """假告警通道：只记录不外发（notify 返回 True=已投递，同 Alerter 语义）。"""

    def __init__(self):
        self.notified: list[dict] = []

    def notify(self, task_id, error, level="WARN", source=None, **kw):
        self.notified.append({"task_id": task_id, "error": error, "level": level, "source": source})
        return True


def _idea(text: str) -> str:
    import json

    return json.dumps(
        [{"hypothesis_zh": text, "mechanism_hint": "机制", "horizon": "5日", "universe": "沪深300"}],
        ensure_ascii=False,
    )


@pytest.fixture()
def sandbox(tmp_path, monkeypatch):
    """假 inbox + 假台账全落 tmp_path（零生产路径写入）。"""
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "intel-20260927.md").write_text(SAMPLE_INBOX, encoding="utf-8")
    monkeypatch.setattr(lane_g, "_INBOX_DIR", inbox)
    monkeypatch.setattr(lane_g, "_INTAKE_CSV", tmp_path / "lane_g_candidates.csv")
    monkeypatch.setattr(lane_g, "_SEEN_CSV", tmp_path / "lane_g_seen_urls.csv")
    return tmp_path


def _fake_scheduler(alerter):
    return SimpleNamespace(_alerter=alerter)


# ── 1. 槽位分派：增量触发被调 ──


def test_slot_dispatches_to_sweep_entry(monkeypatch):
    """槽名 lane_g_intake_sweep → run_intake_sweep 被调且收到调度器 alerter。"""
    calls: list[dict] = []

    def fake_sweep(alerter=None, chat=None):
        calls.append({"alerter": alerter})
        return {"ok": True}

    monkeypatch.setattr(lane_g, "run_intake_sweep", fake_sweep)
    alerter = FakeAlerter()
    out = _run_special_schedule(_fake_scheduler(alerter), "lane_g_intake_sweep")
    assert out == {"lane_g_intake_sweep": True}
    assert len(calls) == 1 and calls[0]["alerter"] is alerter


def test_slot_unknown_name_passes_through():
    """非本槽名返回 None（交回常规 DAG 流程，不劫持他槽）。"""
    assert _run_special_schedule(_fake_scheduler(FakeAlerter()), "not_my_slot") is None


def test_slot_top_level_exception_degrades_to_error_alert(monkeypatch):
    """run_intake_sweep 炸→槽位降级 ERROR 告警并返回 False，不反噬调度器。"""

    def boom(alerter=None, chat=None):
        raise RuntimeError("inbox 台账 IO 损坏")

    monkeypatch.setattr(lane_g, "run_intake_sweep", boom)
    alerter = FakeAlerter()
    out = _run_special_schedule(_fake_scheduler(alerter), "lane_g_intake_sweep")
    assert out == {"lane_g_intake_sweep": False}
    assert alerter.notified and alerter.notified[0]["level"] == "ERROR"
    assert alerter.notified[0]["source"] == "lane_g_intake_sweep"


def test_kill_flag_file_absent():
    """总闸文件现态=不存在（生产开关默认开；测试只读不断言创建）。"""
    assert not (_ROOT / "data" / "runtime" / "lane_g_intake_sweep.disabled").exists()


# ── 2. 游标推进：增量语义 ──


def test_sweep_processes_unseen_and_advances_cursor(sandbox):
    """首扫消化未见条目并写 seen log（游标推进）；二扫零重消化（禁全量重跑）。"""
    chat1 = FakeChat({"Momentum in statistical": _idea("统计套利动量假说")})
    r1 = lane_g.run_intake_sweep(alerter=FakeAlerter(), chat=chat1)
    assert r1["ok"] is True
    assert r1["processed_entries"] == 2 and r1["generated"] == 1
    seen = pd.read_csv(lane_g._SEEN_CSV, encoding="utf-8-sig")
    assert len(seen) == 2  # 游标=seen log，两 url 全记账（含空数组诚实消化）

    chat2 = FakeChat(default="[]")
    r2 = lane_g.run_intake_sweep(alerter=FakeAlerter(), chat=chat2)
    assert r2["processed_entries"] == 0
    assert len(chat2.prompts) == 0  # 已消化 url 零 LLM 调用（增量，非全量重跑）


# ── 3. 失败降级告警 ──


def test_sweep_per_entry_failure_alerts_warn_not_raises(sandbox):
    """单条目 LLM 失败→WARN 告警；失败条目不入 seen（下一班自愈重试）。"""

    class Boom:
        def ask(self, prompt, **kw):
            if "Momentum in statistical" in prompt:
                raise RuntimeError("LSG 不可达")
            return "[]"

    alerter = FakeAlerter()
    r = lane_g.run_intake_sweep(alerter=alerter, chat=Boom())
    assert r["ok"] is True  # 扫描本体完成（降级语义=告警不反噬）
    assert r["failed_urls"] == ["https://arxiv.org/abs/2609.99901"]
    warn = [n for n in alerter.notified if n["level"] == "WARN"]
    assert len(warn) == 1 and warn[0]["source"] == "lane_g_intake_sweep"
    assert "1 条" in warn[0]["error"]
    seen = pd.read_csv(lane_g._SEEN_CSV, encoding="utf-8-sig")
    assert len(seen) == 1  # 失败条目不标 seen→游标只推进成功者（自愈位保留）


def test_sweep_top_level_failure_alerts_error_and_ok_false(sandbox, monkeypatch):
    """整体异常（如台账 IO 炸）→ERROR 告警、ok=False、异常不外抛。"""

    def boom(**kw):
        raise OSError("seen log 读写损坏")

    monkeypatch.setattr(lane_g, "run_intake", boom)
    alerter = FakeAlerter()
    r = lane_g.run_intake_sweep(alerter=alerter)
    assert r["ok"] is False and "OSError" in r["error"]
    assert alerter.notified and alerter.notified[0]["level"] == "ERROR"


def test_sweep_empty_inbox_no_alert(sandbox):
    """空 inbox 扫描=零告警零写盘（no-op 班）。"""
    for f in lane_g._INBOX_DIR.glob("intel-*.md"):
        f.unlink()
    alerter = FakeAlerter()
    r = lane_g.run_intake_sweep(alerter=alerter, chat=FakeChat())
    assert r["ok"] is True and r["processed_entries"] == 0
    assert alerter.notified == []
    assert not lane_g._INTAKE_CSV.exists() and not lane_g._SEEN_CSV.exists()
