# [A_test] module_id: QCURE-OBS-1-test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.test_qcure_offset_report
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest；scripts.governance.qcure_offset_report；scripts.commit_queue（经被测件 importlib 复用，不直接加载）
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_qcure_offset_report.py
# [MATURITY] testing
# [INVARIANTS] 全 tmp 隔离（假死信/假预检账全部落 tmp_path，绝不读写主仓 .runtime 生产账）；
#              时间锚固定（2026-09-25 12:00 +08:00 注入 now），周桶判定与真实时钟解耦
# [MODIFY-GUARD] QCURE-OBS-1 验收回归尺：聚合口径漂移/对消率公式变更/复用分类器被换第二实现，任一即红
# [STABILITY] volatile
# [SAFETY] L
# [TTL] task_bound
"""qcure_offset_report 回归尺：对消聚合与输出结构的 tmp 隔离验证。

覆盖面：三族聚合（env/item/other）×周桶、连字符 gate 名归一匹配（COMMIT-SCOPE→
COMMIT_SCOPE）、对消率公式、趋势箭头、损坏行跳过计数、窗外死信不计、--out 落盘读回、
分类器真源唯一性（无第二分类器）。
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 9, 25, 12, 0, 0, tzinfo=timezone(timedelta(hours=8)))


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def rpt():
    return _load("_qcure_offset_report", "scripts/governance/qcure_offset_report.py")


def _dead(sid: str, dead_at: str, reason: str) -> dict:
    return {"qid": f"q-{sid}", "session_id": sid, "dead_at": dead_at, "dead_reason": reason}


@pytest.fixture()
def accounts(tmp_path: Path):
    """3+2 笔假死信（含窗外 1 笔、损坏 1 笔）+ 假预检账（blocked/passed/坏行混合）。"""
    dead_dir = tmp_path / "dead"
    dead_dir.mkdir()
    cases = [
        ("a1", "2026-09-24T10:00:00+08:00", "网关落盘失败（COMMIT_FAILED）: 门禁 TRANSLATION-COVERAGE 阻断"),  # W1 item
        ("a2", "2026-09-23T10:00:00+08:00", "网关落盘失败（COMMIT_FAILED）: PROTECTED-PATHS 阻断"),  # W1 item
        ("a3", "2026-09-24T11:00:00+08:00", "网关落盘失败（LOCK_TIMEOUT）"),  # W1 env（env 优先于 item 标记）
        ("b1", "2026-09-18T10:00:00+08:00", "PROTECTED-PATHS 阻断"),  # W2 item
        ("b2", "2026-09-17T10:00:00+08:00", "第三十八号实验性失败样例串"),  # W2 other（W2 桶止于 09-18 12:00）
        ("b3", "2026-09-16T10:00:00+08:00", "第三十九号实验性失败样例串"),  # W2 other（造 W2>W1 下降样本）
        ("old", "2026-03-01T10:00:00+08:00", "PROTECTED-PATHS 阻断"),  # 窗外，不计
    ]
    for sid, at, reason in cases:
        item = _dead(sid, at, reason)
        if sid == "a2":
            item["requeued"] = {"new_qid": "q-new", "at": at}  # 复活死信样本
        (dead_dir / f"q-{sid}.json").write_text(json.dumps(item, ensure_ascii=False), encoding="utf-8")
    (dead_dir / "q-broken.json").write_text("{not-json", encoding="utf-8")  # 损坏死信
    pre = tmp_path / "preflight_events.jsonl"
    events = [
        {"timestamp": "2026-09-24T02:00:00+00:00", "event": "blocked", "gates_failed": ["SESSION-REQUIRED"]},  # W1 item
        {
            "timestamp": "2026-09-24T03:00:00+00:00",
            "event": "blocked",
            "gates_failed": ["COMMIT-SCOPE"],
        },  # W1 item（连字符归一）
        {
            "timestamp": "2026-09-18T03:00:00+00:00",
            "event": "blocked",
            "gates_failed": ["TRANSLATION-COVERAGE"],
        },  # W2 other
        {"timestamp": "2026-09-24T04:00:00+00:00", "event": "passed", "gates_failed": []},  # passed 不参与对消
        "这行是坏数据",
        "",
    ]
    pre.write_text(
        "\n".join(e if isinstance(e, str) else json.dumps(e, ensure_ascii=False) for e in events), encoding="utf-8"
    )
    return dead_dir, pre


def test_family_aggregation_and_trend(rpt, accounts):
    dead_dir, pre = accounts
    report = rpt.build_report(2, dead_dir=dead_dir, preflight_path=pre, now=NOW)
    rows = {r["family"]: r for r in report["rows"]}
    # 死信：item=W1 2 + W2 1=3；env=W1 1；other=W2 2
    assert rows["item"]["dead"] == 3 and rows["env"]["dead"] == 1 and rows["other"]["dead"] == 2
    # 预检拦截：item=W1 2（SESSION-REQUIRED + COMMIT-SCOPE 归一）；other=W2 1；env=0
    assert rows["item"]["blocked"] == 2 and rows["env"]["blocked"] == 0 and rows["other"]["blocked"] == 1
    assert report["grand"]["dead"] == 6 and report["grand"]["blocked"] == 3
    # 趋势（箭头=死信环比方向）：item W2=1→W1=2 上升；env W2=0→W1=1 上升；other W2=2→W1=0 下降
    assert rows["item"]["trend"].startswith("↑")
    assert rows["env"]["trend"].startswith("↑")
    assert rows["other"]["trend"] == "↓ 2->0"
    assert report["requeued"] == 1  # 复活死信如实计数


def test_ratio_formula(rpt, accounts):
    dead_dir, pre = accounts
    rows = {r["family"]: r for r in rpt.build_report(2, dead_dir=dead_dir, preflight_path=pre, now=NOW)["rows"]}
    assert rows["item"]["ratio"] == f"{2 / 5 * 100:.1f}%"  # 2/(2+3)
    assert rows["env"]["ratio"] == "0.0%"  # 0/(0+1)
    empty_dir = dead_dir.parent / "empty_dead"  # 不存在的空账路径——缺账诚实零
    empty = rpt.build_report(2, dead_dir=empty_dir, preflight_path=dead_dir.parent / "none.jsonl", now=NOW)
    assert empty["grand"]["ratio"] == "n/a" and empty["grand"]["dead"] == 0


def test_output_structure(rpt, accounts):
    dead_dir, pre = accounts
    text = rpt.render_markdown(rpt.build_report(2, dead_dir=dead_dir, preflight_path=pre, now=NOW))
    for token in (
        "| 死因族 | 死信数 | 预检拦截数 | 对消率 |",
        "env（环境性）",
        "item（物品性）",
        "other（其他）",
        "| 合计 |",
        "## 周粒度明细",
        "W1（09-18~09-25）",
        "高频死因 Top5",
    ):
        assert token in text, f"缺结构要素: {token}"
    assert "TRANSLATION-COVERAGE" in text  # 高频死因 Top5 含真实门禁串（截断前完整命中）


def test_skip_and_out_of_window(rpt, accounts):
    dead_dir, pre = accounts
    report = rpt.build_report(2, dead_dir=dead_dir, preflight_path=pre, now=NOW)
    assert report["skipped"] == {"dead": 1, "preflight": 1}  # 各一笔坏数据，不中断
    assert report["scanned"] == {"dead": 8, "preflight": 5}  # 扫描面含坏行/窗外件
    w2 = report["week_labels"][1][0]
    per_week_env = next(r for r in report["rows"] if r["family"] == "env")["per_week"]
    assert per_week_env[w2] == (0, 0)  # 窗外死信（03-01）绝不进 W2 桶


def test_main_out_and_exit_codes(rpt, accounts, tmp_path, capsys):
    dead_dir, pre = accounts
    out = tmp_path / "report.md"
    assert rpt.main(["--weeks", "2", "--out", str(out)], dead_dir=dead_dir, preflight_path=pre, now=NOW) == 0
    expected = rpt.render_markdown(rpt.build_report(2, dead_dir=dead_dir, preflight_path=pre, now=NOW))
    assert out.read_text(encoding="utf-8") == expected  # 落盘内容=stdout 语义同一渲染
    assert "| 合计 | 6 | 3 |" in expected
    assert rpt.main(["--weeks", "0"], dead_dir=dead_dir, preflight_path=pre, now=NOW) == 1  # 参数错


def test_classifier_is_reused_not_forked(rpt):
    classify = rpt.load_classifier()
    # 与 scripts/commit_queue.py 同源（经 importlib 文件加载），三分类语义一致
    assert classify("网关落盘失败（LOCK_TIMEOUT）") == "env"  # env 标记优先
    assert classify("PROTECTED-PATHS 阻断") == "item"
    assert classify("未知怪串") == "other"
    assert classify("COMMIT_SCOPE") == "item"
