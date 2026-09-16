# [A_test] test_id=T10-20260917 | module=scripts/lock_files.py+scripts/git_commit.py | gate=pytest
# [BLUEPRINT] MOD-INF-005 | scripts/lock_files.py | §7.28+裁定#252+交接纪律三查
# [TESTS] self
# [TTL] permanent
"""T10 治本回归钉（2026-09-17）：

1. lock_files.acquire 对 TTL 过期不敏感的治本钉：
   - 过期 claim + 会话静默超窗（last_activity>30min）→ RECLAIMED 可夺 + 审计留痕；
   - 过期 claim + 会话仍活跃 → DENIED 且如实告知三查结论（禁一条 DENIED 走天下）。
2. git_commit.py --release-only 不落盘的治本钉（伪造释放不落盘场景）：
   - .ailocks 仍持有 → RELEASE-VERIFY FAILED exit=6（禁假成功）；
   - 两处登记处均已无持有 → RELEASED (verified) exit=0。
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
import types
from pathlib import Path
from types import SimpleNamespace

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = _REPO / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import lock_files  # noqa: E402


def _load_git_commit():
    spec = importlib.util.spec_from_file_location("git_commit_under_test", SCRIPTS_DIR / "git_commit.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ─────────────── lock_files.acquire：过期 claim 回收（T10②）───────────────

@pytest.fixture
def isolated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(lock_files, "LOCK_ROOT", tmp_path / ".ailocks")
    monkeypatch.setattr(lock_files, "REGISTRY_PATH", tmp_path / ".ailocks" / "registry.json")
    return tmp_path


def _seed_expired_claim(tmp_path: Path, rel: str, owner_id: str, session_id: str) -> None:
    """伪造一条他会话的过期 claim（owner.json 带 session_id，expires_at 已过）。"""
    lock_dir = lock_files._lock_dir(rel)
    lock_dir.mkdir(parents=True, exist_ok=True)
    now = time.time()
    (lock_dir / "owner.json").write_text(
        json.dumps(
            {
                "owner_id": owner_id,
                "pid": 999999,
                "timestamp": now - 7200,
                "ttl_s": 1800.0,
                "expires_at": now - 3600,
                "task": "old-shift",
                "session_id": session_id,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _fake_registry(monkeypatch: pytest.MonkeyPatch, last_activity: float) -> None:
    """伪造 SessionRegistry：会话判活=True、last_activity 可控（heartbeat 不刷 last_activity）。"""
    import zephyr.security.access_control.session_concurrency as sc

    info = SimpleNamespace(last_activity=last_activity)

    class _FakeRegistry:
        def __init__(self, *_a, **_k) -> None:
            pass

        def get_session(self, _sid: str):
            return info

    monkeypatch.setattr(sc, "SessionRegistry", _FakeRegistry)
    monkeypatch.setattr(sc, "_is_session_alive", lambda info, now: True)


def test_expired_claim_with_idle_session_reclaimed(isolated, tmp_path, monkeypatch):
    """过期 + 静默超窗 → acquire 成功回收（RECLAIMED 行 + jsonl 审计）。"""
    _fake_registry(monkeypatch, last_activity=time.time() - 7200)
    _seed_expired_claim(tmp_path, "docs/hot_registry.yaml", "st-old", "st-old")
    rc = lock_files.cmd_acquire("docs/hot_registry.yaml", "st-new")
    assert rc == 0
    audit = isolated / ".ailocks" / "reclaim_audit.jsonl"
    assert audit.exists()
    row = json.loads(audit.read_text(encoding="utf-8").strip().splitlines()[-1])
    assert row["file"] == "docs/hot_registry.yaml"
    assert row["prev_owner"] == "st-old"
    assert row["reason"] == "expired+idle"


def test_expired_claim_with_active_session_still_denied_but_truthful(isolated, tmp_path, monkeypatch, capsys):
    """过期 + 会话活跃 → 仍 DENIED（禁抢，它随时会重 claim）但如实告知三查结论。"""
    _fake_registry(monkeypatch, last_activity=time.time() - 60)
    _seed_expired_claim(tmp_path, "docs/hot_registry.yaml", "st-old", "st-old")
    rc = lock_files.cmd_acquire("docs/hot_registry.yaml", "st-new")
    assert rc == 1
    out = capsys.readouterr().out
    assert "DENIED" in out
    assert "claim 已过期" in out
    assert "过期+静默才可回收" in out


# ─────────────── git_commit --release-only：回读校验（T10①）───────────────

def _make_gw(tmp_path: Path, session_id: str, held: list[str], ailocks_owned: list[str]):
    """伪造 gateway：SessionRegistry held_files 可控；.ailocks registry.json 落 tmp。"""
    locks_dir = tmp_path / ".ailocks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    (locks_dir / "registry.json").write_text(
        json.dumps(
            {
                "version": 1,
                "locks": {
                    rel: {"owner_id": session_id, "task": "", "timestamp": time.time(), "ttl_s": 1800.0}
                    for rel in ailocks_owned
                },
                "updated_at": time.time(),
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    gw = types.SimpleNamespace(
        project_root=str(tmp_path),
        release_files=lambda sid, files: None,  # 伪造"释放不落盘"：调用后注册表现值由构造决定
        registry=types.SimpleNamespace(get_session=lambda sid: SimpleNamespace(held_files=list(held))),
    )
    return gw


def test_release_verify_fails_when_ailocks_still_holds(tmp_path, monkeypatch):
    """伪造释放不落盘：.ailocks 仍持有 → exit=6 + FAILED 明细（禁假成功）。"""
    monkeypatch.setattr(lock_files, "LOCK_ROOT", tmp_path / ".ailocks")
    monkeypatch.setattr(lock_files, "REGISTRY_PATH", tmp_path / ".ailocks" / "registry.json")
    gc = _load_git_commit()
    gw = _make_gw(tmp_path, "st-me", held=[], ailocks_owned=["docs/x.yaml"])
    rc, lines = gc._release_and_verify(gw, "st-me", ["docs/x.yaml"])
    assert rc == 6
    assert any("docs/x.yaml" in ln and "ailocks=True" in ln for ln in lines)


def test_release_verify_passes_when_both_registries_clean(tmp_path, monkeypatch):
    """两处登记处均无持有 → exit=0。"""
    monkeypatch.setattr(lock_files, "LOCK_ROOT", tmp_path / ".ailocks")
    monkeypatch.setattr(lock_files, "REGISTRY_PATH", tmp_path / ".ailocks" / "registry.json")
    gc = _load_git_commit()
    gw = _make_gw(tmp_path, "st-me", held=[], ailocks_owned=[])
    rc, _lines = gc._release_and_verify(gw, "st-me", ["docs/x.yaml", "docs/y.yaml"])
    assert rc == 0


def test_release_verify_fails_when_session_registry_still_holds(tmp_path, monkeypatch):
    """SessionRegistry 侧释放不落盘同样被抓（held_files 仍有）。"""
    monkeypatch.setattr(lock_files, "LOCK_ROOT", tmp_path / ".ailocks")
    monkeypatch.setattr(lock_files, "REGISTRY_PATH", tmp_path / ".ailocks" / "registry.json")
    gc = _load_git_commit()
    gw = _make_gw(tmp_path, "st-me", held=["docs/y.yaml"], ailocks_owned=[])
    rc, lines = gc._release_and_verify(gw, "st-me", ["docs/y.yaml"])
    assert rc == 6
    assert any("session_registry=True" in ln for ln in lines)
