# [TTL] permanent
"""TRAE-079 熔断他伤豁免测试（A-13，st-chiefc-20261009）。

病情：热册 overlap 5/24h 熔断（#ARCH-264 O2）不区分自伤/他伤——热册"外来整档蒸发战"
（A-12 病灶）期间，受害会话被迫带 allow_overlap 重试，配额被同一根因烧光。实证：
st-libfront-20261009 七连投死链（dead/ q-0001~0007）；st-chiefc-20261009 C-4/C-5
（dead/ q-0120/0121，died_at 14:06/14:10）死于同一熔断——会话是受害者不是滥用者。

修法（净零：改既有计数逻辑，零新门）：usage 记账时按白名单事件
（``_EVICTION_EXCUSE_EVENTS``）判定写 ``eviction_excused`` 标记；计数时跳过 excused
记录；旧格式无字段记录按白名单现场判定（零迁移）。

能红双构：
- 红证 A：5 条纯自伤（无豁免标记、白名单外）→ blocked=True。
- 红证 B：同 5 条带 eviction_excused=True → blocked=False。
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))  # noqa: E402

from zephyr.gov_enforcement.rule_bridge import git_commit_gateway as gcg  # noqa: E402

_CAP_REGISTRY = (
    "D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"
)
_AGENTS = "D:/ZephyrAlpha/AGENTS.md"
_SID = "sess-a13-test"


def _rec(ts: datetime, hot_files: list[str], **extra: object) -> dict[str, object]:
    """构造一条 usage 记录（网关落盘格式）。"""
    rec: dict[str, object] = {
        "ts": ts.isoformat(),
        "session": _SID,
        "files": 1,
        "hot_files": hot_files,
    }
    rec.update(extra)
    return rec


def _write_usage(tmp_path: Path, records: list[dict[str, object]]) -> Path:
    audit_dir = tmp_path / ".runtime" / "gate_audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    usage = audit_dir / "allow_overlap_usage.jsonl"
    with usage.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return usage


def _recent_ts(minutes_ago: int) -> datetime:
    """近窗时间戳（滚动 24h 内；白名单事件窗已收口于 2026-10-09T14:00+08:00）。"""
    return datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)


# ── 红证 A：纯自伤照常熔断 ────────────────────────────────────────────────────
def test_red_a_pure_self_harm_still_blocks(tmp_path: Path) -> None:
    """5 条无豁免标记的热文件 usage（白名单外）→ blocked=True。"""
    ts = _recent_ts(60)
    _write_usage(tmp_path, [_rec(ts, [_AGENTS]) for _ in range(5)])
    blocked, reason = gcg._check_hot_overlap_escalation(tmp_path, _SID)
    assert blocked is True, "纯自伤（无外来事件佐证）必须照常计数熔断"
    assert _SID in reason and "allow_overlap" in reason


# ── 红证 B：他伤豁免不入计数 ──────────────────────────────────────────────────
def test_red_b_eviction_excused_not_counted(tmp_path: Path) -> None:
    """同 5 条但带 eviction_excused=True → blocked=False（配额不被他伤烧光）。"""
    ts = _recent_ts(60)
    _write_usage(tmp_path, [_rec(ts, [_CAP_REGISTRY], eviction_excused=True) for _ in range(5)])
    blocked, reason = gcg._check_hot_overlap_escalation(tmp_path, _SID)
    assert blocked is False, f"他伤（台账佐证）必须豁免不计: {reason}"


def test_mixed_excused_subtracts_from_count(tmp_path: Path) -> None:
    """4 条自伤 + 1 条他伤 → 计数 4 <5 不熔断（excused 真实抵扣而非全量忽略）。"""
    ts = _recent_ts(60)
    records = [_rec(ts, [_AGENTS]) for _ in range(4)]
    records.append(_rec(ts, [_CAP_REGISTRY], eviction_excused=True))
    _write_usage(tmp_path, records)
    blocked, _ = gcg._check_hot_overlap_escalation(tmp_path, _SID)
    assert blocked is False


def test_explicit_false_counts_as_self_harm(tmp_path: Path) -> None:
    """eviction_excused 显式 False（记账时白名单外判定）→ 照常计数。"""
    ts = _recent_ts(60)
    _write_usage(tmp_path, [_rec(ts, [_AGENTS], eviction_excused=False) for _ in range(5)])
    blocked, _ = gcg._check_hot_overlap_escalation(tmp_path, _SID)
    assert blocked is True


# ── 白名单判定助手（判据：同一热册 + 时间窗吻合）────────────────────────────
def test_judge_in_window_cap_registry_is_excused() -> None:
    """事件窗内 + 命中 capability 热册 → 他伤豁免（台账/佐证 commit 时间窗）。"""
    # 2026-10-08T22:30Z = 06:30+08:00——allow_overlap_usage.jsonl 实录受害记录时刻
    ts = datetime.fromisoformat("2026-10-08T22:30:00+00:00")
    assert gcg._judge_eviction_excuse(ts, [_CAP_REGISTRY]) is True


def test_judge_in_window_other_hot_file_not_excused() -> None:
    """事件窗内但热册不匹配（AGENTS.md）→ 不豁免（防白名单无限扩大）。"""
    ts = datetime.fromisoformat("2026-10-08T22:30:00+00:00")
    assert gcg._judge_eviction_excuse(ts, [_AGENTS]) is False


def test_judge_out_of_window_not_excused() -> None:
    """窗口收口后（含未来）同热册 → 不豁免（窗口收口不自动续期）。"""
    ts = datetime.fromisoformat("2026-10-09T07:00:00+00:00")  # 15:00+08:00 > 窗口收口
    assert gcg._judge_eviction_excuse(ts, [_CAP_REGISTRY]) is False


def test_judge_naive_ts_fails_closed_to_counted() -> None:
    """naive 时间戳（无时区）判定失败 → False（保守计数，不豁免）。"""
    assert gcg._judge_eviction_excuse(datetime(2026, 10, 9, 6, 30), [_CAP_REGISTRY]) is False


# ── 记账侧：eviction_excused 标记随记录落盘 ─────────────────────────────────
def test_log_usage_writes_eviction_excused_marker(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """记账时判定写入标记字段（白名单事件窗已收口 → 现值 False，字段必须在）。"""
    monkeypatch.setattr("zephyr.shared.io.file_utils.is_hot_file", lambda path, root: True)
    gcg._log_allow_overlap_usage(tmp_path, _SID, [_CAP_REGISTRY])
    usage = tmp_path / ".runtime" / "gate_audit" / "allow_overlap_usage.jsonl"
    rec = json.loads(usage.read_text(encoding="utf-8").splitlines()[0])
    assert "eviction_excused" in rec, "记账记录必须携带他伤豁免标记字段"
    assert isinstance(rec["eviction_excused"], bool)
    assert rec["eviction_excused"] is False, "事件窗收口后记账 → 纯自伤（False）"
    assert rec["hot_files"] == [_CAP_REGISTRY]


def test_legacy_record_without_field_judged_on_the_fly(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """旧格式无字段记录按白名单现场判定：窗内热册命中 → 豁免（零迁移治愈已烧配额）。"""
    # 加宽滚动窗使历史 ts 稳定落入计数窗（否则随真实时间推移记录会因超 24h 被跳过，
    # 测试退化）——本测试只关心"无字段 → 现场白名单判定"这条路径。
    monkeypatch.setattr(gcg, "_HOT_OVERLAP_WINDOW_SECONDS", 30 * 86400)
    legacy = {
        "timestamp": 1791498600,  # 2026-10-09 06:30+08:00 前后（事件窗内）
        "session_id": _SID,  # 旧格式键名（另一计量写入方）
        "files_count": 1,
    }
    audit_dir = tmp_path / ".runtime" / "gate_audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    (audit_dir / "allow_overlap_usage.jsonl").write_text(
        json.dumps({"ts": "2026-10-09T06:30:00+00:00", "session": _SID, "hot_files": [_CAP_REGISTRY]})
        + "\n"
        + json.dumps(legacy)
        + "\n",
        encoding="utf-8",
    )
    blocked, _ = gcg._check_hot_overlap_escalation(tmp_path, _SID)
    assert blocked is False, "旧格式他伤记录应被白名单现场判定豁免"
