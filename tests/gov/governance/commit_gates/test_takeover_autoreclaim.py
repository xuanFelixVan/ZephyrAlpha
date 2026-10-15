# [TTL] permanent
"""st-perfz2-20261015 P0-2：TAKEOVER-PENDING 自动回收 + 立案活性闸（自指死锁治本）判别测试。

钉住六件不可回退的事：
- 证据链完整（PID dead+idle 超阈值+旁证全空）+ 现判 dead → 门自动 release+resolve 并放行，
  台账 open 条目迁 resolved/、审计落 takeover_autoreclaim.jsonl。
- flag OFF（flags.takeover_autoreclaim.enabled=false）→ 照旧阻断（回滚面）。
- 证据链不全（pid_alive None / idle 未超阈值 / 立案旁证在场）→ 照旧阻断，绝不回收。
- liveness_verdict 现判非 dead（会话复活）→ 不回收，照旧阻断（C11 自挡降级另行处理）。
- release_files 异常 → 照旧阻断，条目仍 open。
- 立案侧（P0-2b）：registry_alive_blocks_case 对 alive 会话闸住（--scan 与判死钩子共闸），
  dead/degraded/闸不可达一律放行立案；钩子路径 alive 跳过、dead 照写。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.governance import session_takeover_ledger as ledger  # noqa: E402
from zephyr.gov_enforcement.commit_gates import takeover_pending_gate as tpg  # noqa: E402

_WATCHED = "src/zephyr/dead_leftover.py"

_EVIDENCE_OK = {
    "pid": 4321,
    "pid_alive": False,
    "last_activity_age_seconds": 90000.0,
    "threshold_seconds": 7200,
    "reason": "pid 4321 dead；last_activity idle 90000.0s > 7200s",
}


def _entry(sid: str, evidence: dict, held: list[str] | None = None) -> dict:
    return {
        "ts": "2026-10-15T00:00:00+00:00",
        "ts_epoch": 0.0,
        "sid": sid,
        "death_evidence": evidence,
        "resources": {
            "held_files": held if held is not None else [_WATCHED],
            "worktrees": [],
            "staging": {"dir": ".runtime/sessions/x/staging", "file_count": 0, "files": []},
            "bags": [],
            "heartbeat_files": [],
        },
        "impacted_modules": [],
        "prescription": [],
        "status": "open",
        "refresh_count": 0,
    }


class _Gateway:
    """最小 gateway 垫片：project_root + release_files 录制器（可注入异常）。"""

    def __init__(self, root: Path, release_error: Exception | None = None):
        self.project_root = root
        self.released: list[tuple[str, list[str]]] = []
        self.release_error = release_error

    def release_files(self, session_id: str, files: list[str]) -> None:
        if self.release_error is not None:
            raise self.release_error
        self.released.append((session_id, list(files)))


def _write_ledger(root: Path, entries: list[dict]) -> None:
    p = root / ".runtime" / "takeover_ledger.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in entries), encoding="utf-8")


def _open_rows(root: Path) -> list[dict]:
    p = root / ".runtime" / "takeover_ledger.jsonl"
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


@pytest.fixture()
def lane_root(tmp_path, monkeypatch):
    """台账模块 import 钉到真仓 scripts（门内 _import_ledger_module 直连）。"""
    monkeypatch.setattr(tpg, "_import_ledger_module", lambda root: ledger)
    return tmp_path


def _run_gate(root: Path, monkeypatch, verdict=("dead", "PID-DEAD")):
    gw = _Gateway(root)
    files = [str(root / _WATCHED)]
    monkeypatch.setattr(tpg, "_self_block_verdict", lambda sid: verdict)
    gate = tpg.make_takeover_pending_gate()
    ok, detail = gate.check(gw, files, session_id="st-other-1")
    return gw, ok, detail


def test_autoreclaim_releases_and_resolves(lane_root, monkeypatch):
    root = lane_root
    _write_ledger(root, [_entry("st-dead-1", _EVIDENCE_OK)])
    gw, ok, detail = _run_gate(root, monkeypatch)
    assert ok is True, f"证据链完整的死条目应自动回收放行: {detail}"
    assert gw.released and gw.released[0][0] == "st-dead-1", "必须 release 死 sid 的 claim"
    assert _open_rows(root) == [], "open 条目必须迁出台账"
    resolved_dir = root / ".runtime" / "takeover" / "resolved"
    assert list(resolved_dir.glob("st-dead-1-*.json")), "resolved/ 必须有终态文件"
    audit = root / ".runtime" / "session_registry_audit" / "takeover_autoreclaim.jsonl"
    rows = [json.loads(x) for x in audit.read_text(encoding="utf-8").splitlines() if x.strip()]
    assert rows and rows[-1]["event"] == "takeover_autoreclaim" and rows[-1]["sid"] == "st-dead-1"
    assert rows[-1]["released_claims"] == 1


def test_autoreclaim_off_blocks(lane_root, monkeypatch):
    root = lane_root
    (root / "config").mkdir(parents=True, exist_ok=True)
    (root / "config" / "flags.yaml").write_text(
        "flags:\n  takeover_autoreclaim:\n    enabled: false\n", encoding="utf-8"
    )
    _write_ledger(root, [_entry("st-dead-2", _EVIDENCE_OK)])
    gw, ok, detail = _run_gate(root, monkeypatch)
    assert ok is False, "flag OFF 必须照旧阻断（回滚面）"
    assert gw.released == []
    assert len(_open_rows(root)) == 1


def test_incomplete_chain_blocks(lane_root, monkeypatch):
    root = lane_root
    cases = [
        ("pid_alive_none", {**_EVIDENCE_OK, "pid_alive": None}),
        ("idle_below_threshold", {**_EVIDENCE_OK, "last_activity_age_seconds": 100.0}),
        ("alive_side_present", {**_EVIDENCE_OK, "alive_side_evidence": {"any_alive_side": True}}),
        ("no_pid", {k: v for k, v in _EVIDENCE_OK.items() if k != "pid"}),
    ]
    for name, ev in cases:
        _write_ledger(root, [_entry(f"st-dead-{name}", ev)])
        gw, ok, detail = _run_gate(root, monkeypatch)
        assert ok is False, f"{name} 证据链不全必须照旧阻断"
        assert gw.released == [], f"{name} 不得 release"
        assert len(_open_rows(root)) == 1, f"{name} 条目必须仍 open"
        (root / ".runtime" / "takeover_ledger.jsonl").unlink()


def test_verdict_not_dead_blocks(lane_root, monkeypatch):
    root = lane_root
    _write_ledger(root, [_entry("st-revived", _EVIDENCE_OK)])
    gw, ok, detail = _run_gate(root, monkeypatch, verdict=("alive", "REGISTRY-FRESH"))
    assert ok is False, "现判 alive（会话复活）绝不自动回收"
    assert gw.released == []
    assert len(_open_rows(root)) == 1


def test_release_failure_blocks_entry_still_open(lane_root, monkeypatch):
    root = lane_root
    _write_ledger(root, [_entry("st-dead-3", _EVIDENCE_OK)])
    gw = _Gateway(root, release_error=RuntimeError("boom"))
    files = [str(root / _WATCHED)]
    monkeypatch.setattr(tpg, "_self_block_verdict", lambda sid: ("dead", "PID-DEAD"))
    gate = tpg.make_takeover_pending_gate()
    ok, detail = gate.check(gw, files, session_id="st-other-1")
    assert ok is False, "release 失败=放弃回收照旧阻断"
    assert len(_open_rows(root)) == 1, "条目必须仍 open"


# ── P0-2b：立案活性闸 ──


def test_registry_alive_blocks_case(monkeypatch):
    import zephyr.security.access_control.session_concurrency as sc

    class _V:
        def __init__(self, state, signal):
            self.state = state
            self.authoritative_signal = signal

    monkeypatch.setattr(sc, "liveness_verdict", lambda sid, now=None: _V("alive", "REGISTRY-FRESH"))
    skip, note = ledger.registry_alive_blocks_case(Path("."), "st-any")
    assert skip is True and "alive" in note

    monkeypatch.setattr(sc, "liveness_verdict", lambda sid, now=None: _V("dead", "PID-DEAD"))
    skip, _ = ledger.registry_alive_blocks_case(Path("."), "st-any")
    assert skip is False, "dead 必须照常立案"

    monkeypatch.setattr(sc, "liveness_verdict", lambda sid, now=None: (_ for _ in ()).throw(RuntimeError("x")))
    skip, note = ledger.registry_alive_blocks_case(Path("."), "st-any")
    assert skip is False and "不可达" in note, "闸不可达=保守照原判据立案"


def test_hook_skips_alive_sessions(monkeypatch, tmp_path):
    """判死钩子：registry-alive 会话不立 open 条目（写侧零调用）；dead 照写。

    数据过硬证据闸（idle>DEATH_IDLE_SECONDS）后直落立案活性闸——闸前形态不在本测面
    （soft-expire 跳过属既有 R2-F1 判据，test_takeover_pid_false_positive 在册覆盖）。
    """
    import zephyr.security.access_control.session_concurrency as sc

    written: list[str] = []
    monkeypatch.setattr(ledger, "write_takeover_entry", lambda root, sid, **kw: written.append(sid) or {})
    monkeypatch.setattr(ledger, "collect_resources", lambda root, sid, entry, now=None: {})
    monkeypatch.setattr(
        sc,
        "collect_alive_side_evidence",
        lambda sid, now, root=None, **kw: {"any_alive_side": False, "witnesses": [], "signals": {}},
    )
    monkeypatch.setattr(
        ledger,
        "registry_alive_blocks_case",
        lambda root, sid, now=None: (sid == "st-alive", f"registry-alive sid={sid}"),
    )

    now = 1_000_000.0
    data = {
        "st-alive": {"last_activity": now - ledger.DEATH_IDLE_SECONDS - 1, "pid": 0},
        "st-dead": {"last_activity": now - ledger.DEATH_IDLE_SECONDS - 1, "pid": 0},
    }
    sc._salvage_takeover_ledger(tmp_path, data, ["st-alive", "st-dead"], now=now)
    assert written == ["st-dead"], "alive 会话不立案；dead 照常立案"
