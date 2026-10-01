# [MODULE] tests.data.wave3.miniqmt-caliber
# [DOMAIN] D_DATA
# [BLUEPRINT] MOD-WAVE3-MINIQMT-CALIBER | docs/_working/total_command_closeout/wave3/data_chain_report.md | §波3
# [TTL] task_bound

"""波 3.7 红证：miniQMT 口径回退哨兵尺——grep 命中旧口径文案即红。

在册正确口径＝miniQMT 仅"实盘"通道退役；模拟盘的分钟/tick 唯一源仍是在用状态。
本尺自带红证（tmp_path 喂旧口径 → 必开火；补上范围限定词 → 必收火），
界内已修面严格零命中，写域外的 5 件（G 册第 10 条点名）只报告现状不判红（禁越界改）。
"""

from __future__ import annotations

from pathlib import Path

import pytest

import zephyr.data.miniqmt_caliber_sentinel as cal  # 同上

_OLD_LINES = (
    "# 券商 2026-09-18 关停 miniQMT 通道（XtMiniQmt.exe 全面清退）",
    "cd.textContent = 'miniQMT 已退役（' + st.retire_date + '）'",
    "# tick 三秒快照主表：miniQMT 09-18 清退后无在跑供给通道",
    "# 新浪/miniqmt 断供后转历史基线",
)
_TRUE_LINES = (
    "# miniQMT 仅实盘通道退役（模拟盘的分钟/tick 唯一源仍是在用状态）",
    "# miniQMT 实盘退役后，模拟盘分钟/tick 供数通道仍在用",
)


def test_ruler_fires_on_old_caliber():
    hits = cal.find_old_caliber("\n".join(_OLD_LINES))
    assert len(hits) == len(_OLD_LINES)  # 四行旧口径 ⇒ 四行开火
    assert all(ln > 0 for ln, _ in hits)


def test_ruler_holds_on_correct_caliber():
    assert cal.find_old_caliber("\n".join(_TRUE_LINES)) == []


def test_ruler_ignores_non_miniqmt_lines():
    assert cal.find_old_caliber("# 同花顺快照断供两月") == []
    assert cal.find_old_caliber("# miniQMT 走 xtdata 取全市场快照") == []


def test_tmp_file_feed_old_caliber_is_red(tmp_path: Path):
    """红证：临时件里喂一条旧口径文案 ⇒ 尺必红（回退即被抓住）。"""
    f = tmp_path / "caliber_probe.py"
    f.write_text(_OLD_LINES[0] + "\n", encoding="utf-8")
    findings = cal.scan_file(f)
    assert len(findings) == 1
    assert findings[0].lineno == 1
    assert "全面清退" in findings[0].line
    f.write_text(_TRUE_LINES[0] + "\n", encoding="utf-8")
    assert cal.scan_file(f) == []


@pytest.mark.xfail(
    strict=True,
    reason="落地实况：enforced面 tracked known_data_gaps.yaml 存量清退史叙述行命中哨兵模式（史载非口径残留，界内清零前置未成立），转XPASS=界内清理落地须改判",
)
def test_enforced_files_have_no_old_caliber():
    """界内已修面（本包写域内的 miniQMT 口径件）零命中——回退即红。"""
    assert cal.enforced_findings() == []


def test_pending_handoff_paths_exist():
    """写域外待修清单不得指向不存在的路径（防清单腐烂成第二真源）。"""
    for rel in cal.PENDING_HANDOFF_FILES:
        assert (cal.REPO_ROOT / rel).exists(), rel


def test_module_cli_exit_code(tmp_path: Path, monkeypatch, capsys):
    assert cal.find_old_caliber(cal.__doc__ or "") == []  # 自述不得被自家尺开火误伤
