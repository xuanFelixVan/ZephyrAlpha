# [TTL] permanent
# [MODULE] tests.governance.redblue_wave73.test_v8_hot_registry_whole_overwrite
# [DOMAIN] D_GOV_CODE_QUALITY
"""wave7.3 V8 热册整覆：绕 safe_write_text 的陈旧整册覆写 → 双面防线拦。

面1（文件级 CAS）：safe_write_text expected_base 与磁盘不符 → StaleWriteRefused
拒写不落盘——"读→改→写"窗口被外来变更插队时整册覆写被拒。
面2（git 级）：HOT-FILE-BASE-FRESHNESS 门——claim 后 HEAD 推进且目标热册在
claim_head..HEAD 区间被上游改动 → STALE_BASE_VIOLATION 阻断（陈旧快照覆写事故治本）。
两面互补覆盖（面2 治"全程磁盘未变但 HEAD 已推进"的盲区）。
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from zephyr.shared.io.file_utils import StaleWriteRefused, content_sha256, safe_write_text


def _gate():
    import zephyr.gov_enforcement.commit_gates.hot_file_base_freshness_gate as hfg

    return hfg


def test_stale_base_whole_overwrite_refused(tmp_path):
    target = tmp_path / "some_registry.yaml"
    target.write_text("total: 1\nitems: []\n", encoding="utf-8")
    stale_base = "0" * 64  # 攻击者持陈旧 base（磁盘已被他人推进）
    with pytest.raises(StaleWriteRefused):
        safe_write_text(target, "total: 0\nitems: []\n", expected_base_sha256=stale_base)
    assert target.read_text(encoding="utf-8") == "total: 1\nitems: []\n", "拒写后磁盘被污染"


def test_fresh_base_overwrite_allowed(tmp_path):
    target = tmp_path / "some_registry.yaml"
    target.write_text("total: 1\nitems: []\n", encoding="utf-8", newline="\n")
    fresh = content_sha256(target.read_text(encoding="utf-8"))
    safe_write_text(target, "total: 2\nitems: [a]\n", expected_base_sha256=fresh)
    assert "total: 2" in target.read_text(encoding="utf-8")


def test_stale_claim_head_hot_file_commit_blocks(monkeypatch):
    """面2：claim 后上游已推进热册 → STALE_BASE_VIOLATION 阻断（陈旧整册覆写=在案事故形态）。"""
    import zephyr.gov_enforcement.commit_gates.hot_file_base_freshness_gate as hfg

    rel = "docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml"
    gw = MagicMock()
    gw.project_root = "D:/fake_root"
    gw.claim_heads = {"st-attacker": "aaaaaaaaaaaa"}
    calls = {"diff": 0}

    def _run(cmd: list[str]):
        res = MagicMock()
        if cmd[:2] == ["git", "rev-parse"]:
            res.returncode, res.stdout = 0, "bbbbbbbbbbbb\n"
        elif cmd[:2] == ["git", "diff"]:
            calls["diff"] += 1
            res.returncode, res.stdout = 0, rel + "\n"  # 上游确实动过该热册
        else:
            res.returncode, res.stdout = 1, ""
        return res

    gw.run_git = _run
    monkeypatch.setattr(_gate(), "is_hot_file", lambda path, root: True)
    passed, detail = (
        _gate()
        .make_hot_file_base_freshness_gate()
        .check(
            gw,
            [f"D:/fake_root/{rel}"],
            session_id="st-attacker",
        )
    )
    assert passed is False, "陈旧 claim 基线整册覆写未阻断——热册 CAS 被绕过得手"
    assert "STALE_BASE_VIOLATION" in detail
    assert calls["diff"] == 1


def test_fresh_claim_head_hot_file_commit_passes(monkeypatch):
    rel = "docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml"
    gw = MagicMock()
    gw.project_root = "D:/fake_root"
    gw.claim_heads = {"st-fresh": "bbbbbbbbbbbb"}  # == 当前 HEAD（无上游推进）

    def _run(cmd: list[str]):
        res = MagicMock()
        if cmd[:2] == ["git", "rev-parse"]:
            res.returncode, res.stdout = 0, "bbbbbbbbbbbb\n"
        else:
            res.returncode, res.stdout = 1, ""
        return res

    gw.run_git = _run
    monkeypatch.setattr(_gate(), "is_hot_file", lambda path, root: True)
    passed, _ = (
        _gate()
        .make_hot_file_base_freshness_gate()
        .check(
            gw,
            [f"D:/fake_root/{rel}"],
            session_id="st-fresh",
        )
    )
    assert passed is True
