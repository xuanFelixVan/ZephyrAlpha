# [BLUEPRINT] MOD-GOV-CHIEFLEASE | scripts/governance/chief_lease.py | 裁定#415 唯一在任总包
# [TTL] permanent
# [MODULE] tests.governance.test_chief_lease
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.chief_lease
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] tmp_path 假租约测裁定#415 仲裁语义：vacant claim 成功 / LIVE 被他手持有拒绝并回报 holder / heartbeat 仅 holder 可续且延长生命线 / TTL 过期自动让位先到先得 / release 仅 holder（过期清尸合法）/ --json 机读模式 / 损坏文件自愈（备份 .corrupt-*.bak + 按空位处理）/ 同 sid 幂等重入；全注入冻结时钟零 sleep，零生产路径写入
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-TEST_CHIEF_LEASE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_chief_lease.py — 总指挥租约仲裁器单元测试（裁定#415 机械化）

覆盖（全部 tmp_path 假租约 + 注入冻结时钟，零生产路径写入）：
- claim: 空位成功 / LIVE 他手拒绝（回报 holder sid）/ 同 sid 幂等重入 / TTL 过期先到先得
- heartbeat: holder 续期延长生命线 / 非 holder 拒绝 / 过期后 heartbeat 失败
- release: holder 释放归空 / 非 holder 拒绝 / 空位释放失败
- status: NONE（缺失/过期）与在任快照（age_seconds）
- --json 机读模式与 rc 语义（0 成功 / 1 仲裁失败）
- 损坏文件自愈：备份 + 按空位继续
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "governance"))
import chief_lease as cl  # noqa: E402

T0 = datetime(2026, 9, 28, 12, 0, 0, tzinfo=timezone.utc)


def _lease(tmp_path: Path) -> Path:
    return tmp_path / "chief_lease.json"


def _backup_glob(tmp_path: Path) -> list[Path]:
    return list(tmp_path.glob("chief_lease.json.corrupt-*.bak"))


# ---------------------------------------------------------------------------
# claim
# ---------------------------------------------------------------------------


def test_claim_when_vacant_ok(tmp_path: Path) -> None:
    res = cl.claim("sid-A", path=_lease(tmp_path), now=T0)
    assert res["ok"] is True
    assert res["chief"] == "sid-A"
    assert res["lease"]["ttl_seconds"] == 600
    stored = json.loads(_lease(tmp_path).read_text(encoding="utf-8"))
    assert stored["sid"] == "sid-A"
    assert stored["claimed_at"] == T0.isoformat()


def test_claim_when_live_rejected_with_holder(tmp_path: Path) -> None:
    assert cl.claim("sid-A", path=_lease(tmp_path), now=T0)["ok"] is True
    res = cl.claim("sid-B", path=_lease(tmp_path), now=T0 + timedelta(seconds=100))
    assert res["ok"] is False
    assert res["reason"] == "lease_held"
    assert res["holder"] == "sid-A"
    # 在任者未被篡夺
    assert cl.status(path=_lease(tmp_path), now=T0 + timedelta(seconds=100))["chief"] == "sid-A"


def test_claim_same_sid_idempotent_reentry(tmp_path: Path) -> None:
    assert cl.claim("sid-A", path=_lease(tmp_path), now=T0)["ok"] is True
    res = cl.claim("sid-A", path=_lease(tmp_path), now=T0 + timedelta(seconds=50))
    assert res["ok"] is True
    assert res["reclaimed"] is True


def test_claim_ttl_expiry_auto_vacant_first_claimer_wins(tmp_path: Path) -> None:
    assert cl.claim("sid-A", path=_lease(tmp_path), now=T0)["ok"] is True
    expired_at = T0 + timedelta(seconds=601)
    st = cl.status(path=_lease(tmp_path), now=expired_at)
    assert st["chief"] is None and st["state"] == "expired"
    res = cl.claim("sid-B", path=_lease(tmp_path), now=expired_at)
    assert res["ok"] is True and res["chief"] == "sid-B"


# ---------------------------------------------------------------------------
# heartbeat
# ---------------------------------------------------------------------------


def test_heartbeat_extends_beyond_original_ttl(tmp_path: Path) -> None:
    assert cl.claim("sid-A", path=_lease(tmp_path), now=T0)["ok"] is True
    late = T0 + timedelta(seconds=500)
    res = cl.heartbeat("sid-A", path=_lease(tmp_path), now=late)
    assert res["ok"] is True and res["last_heartbeat"] == late.isoformat()
    # 原 TTL 窗口（T0+600）早已过去，但心跳已把生命线延到 late+600
    still = cl.status(path=_lease(tmp_path), now=T0 + timedelta(seconds=1000))
    assert still["chief"] == "sid-A"
    gone = cl.status(path=_lease(tmp_path), now=late + timedelta(seconds=601))
    assert gone["chief"] is None


def test_heartbeat_by_non_holder_rejected(tmp_path: Path) -> None:
    assert cl.claim("sid-A", path=_lease(tmp_path), now=T0)["ok"] is True
    res = cl.heartbeat("sid-B", path=_lease(tmp_path), now=T0 + timedelta(seconds=10))
    assert res["ok"] is False and res["reason"] == "not_holder" and res["holder"] == "sid-A"


def test_heartbeat_after_expiry_fails(tmp_path: Path) -> None:
    assert cl.claim("sid-A", path=_lease(tmp_path), now=T0)["ok"] is True
    res = cl.heartbeat("sid-A", path=_lease(tmp_path), now=T0 + timedelta(seconds=601))
    assert res["ok"] is False and res["reason"] == "lease_expired"


def test_heartbeat_without_lease_fails(tmp_path: Path) -> None:
    res = cl.heartbeat("sid-A", path=_lease(tmp_path), now=T0)
    assert res["ok"] is False and res["reason"] == "no_lease"


# ---------------------------------------------------------------------------
# release
# ---------------------------------------------------------------------------


def test_release_by_holder_vacates(tmp_path: Path) -> None:
    assert cl.claim("sid-A", path=_lease(tmp_path), now=T0)["ok"] is True
    res = cl.release("sid-A", path=_lease(tmp_path), now=T0 + timedelta(seconds=10))
    assert res["ok"] is True and res["expired"] is False
    assert not _lease(tmp_path).exists()
    assert cl.status(path=_lease(tmp_path), now=T0 + timedelta(seconds=11))["chief"] is None


def test_release_by_non_holder_rejected(tmp_path: Path) -> None:
    assert cl.claim("sid-A", path=_lease(tmp_path), now=T0)["ok"] is True
    res = cl.release("sid-B", path=_lease(tmp_path), now=T0 + timedelta(seconds=10))
    assert res["ok"] is False and res["reason"] == "not_holder"
    assert cl.status(path=_lease(tmp_path), now=T0 + timedelta(seconds=11))["chief"] == "sid-A"


def test_release_holder_may_clear_expired_lease(tmp_path: Path) -> None:
    assert cl.claim("sid-A", path=_lease(tmp_path), now=T0)["ok"] is True
    res = cl.release("sid-A", path=_lease(tmp_path), now=T0 + timedelta(seconds=601))
    assert res["ok"] is True and res["expired"] is True


def test_release_when_vacant_fails(tmp_path: Path) -> None:
    res = cl.release("sid-A", path=_lease(tmp_path), now=T0)
    assert res["ok"] is False and res["reason"] == "no_lease"


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------


def test_status_snapshot_when_held(tmp_path: Path) -> None:
    assert cl.claim("sid-A", path=_lease(tmp_path), now=T0)["ok"] is True
    st = cl.status(path=_lease(tmp_path), now=T0 + timedelta(seconds=42))
    assert st["chief"] == "sid-A" and st["state"] == "held"
    assert st["age_seconds"] == 42.0


def test_status_vacant_when_missing(tmp_path: Path) -> None:
    st = cl.status(path=_lease(tmp_path), now=T0)
    assert st["ok"] is True and st["chief"] is None and st["state"] == "vacant"


# ---------------------------------------------------------------------------
# 损坏自愈
# ---------------------------------------------------------------------------


def test_corrupt_file_self_heals_with_backup(tmp_path: Path) -> None:
    lease_path = _lease(tmp_path)
    lease_path.write_text("{not-json-at-all", encoding="utf-8")
    res = cl.claim("sid-A", path=lease_path, now=T0)
    assert res["ok"] is True
    backups = _backup_glob(tmp_path)
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == "{not-json-at-all"
    stored = json.loads(lease_path.read_text(encoding="utf-8"))
    assert stored["sid"] == "sid-A"


def test_corrupt_schema_self_heals_too(tmp_path: Path) -> None:
    lease_path = _lease(tmp_path)
    lease_path.write_text('{"unexpected": true}', encoding="utf-8")
    assert cl.claim("sid-A", path=lease_path, now=T0)["ok"] is True
    assert len(_backup_glob(tmp_path)) == 1


# ---------------------------------------------------------------------------
# CLI（含 --json 模式与 rc 语义）
# ---------------------------------------------------------------------------


def _run_cli(capsys, *argv: str) -> tuple[int, str]:
    rc = cl.main(list(argv))
    out = capsys.readouterr().out
    return rc, out


def test_cli_status_vacant_human_and_json(capsys, tmp_path: Path) -> None:
    lp = str(_lease(tmp_path))
    rc, out = _run_cli(capsys, "status", "--path", lp)
    assert rc == 0 and "CHIEF: NONE" in out
    rc, out = _run_cli(capsys, "--json", "status", "--path", lp)
    assert rc == 0 and json.loads(out)["chief"] is None


def test_cli_json_claim_rejected_reports_holder(capsys, tmp_path: Path) -> None:
    lp = str(_lease(tmp_path))
    rc, out = _run_cli(capsys, "--json", "claim", "sid-A", "--path", lp)
    assert rc == 0 and json.loads(out)["chief"] == "sid-A"
    rc, out = _run_cli(capsys, "--json", "claim", "sid-B", "--path", lp)
    payload = json.loads(out)
    assert rc == 1
    assert payload["ok"] is False and payload["holder"] == "sid-A" and payload["reason"] == "lease_held"


def test_cli_human_claim_rejected_prints_holder(capsys, tmp_path: Path) -> None:
    lp = str(_lease(tmp_path))
    _run_cli(capsys, "claim", "sid-A", "--path", lp)
    rc, out = _run_cli(capsys, "claim", "sid-B", "--path", lp)
    assert rc == 1 and "holder=sid-A" in out


def test_cli_ttl_expiry_then_reclaim_via_cli(capsys, tmp_path: Path) -> None:
    lp = str(_lease(tmp_path))
    assert _run_cli(capsys, "--json", "claim", "sid-A", "--path", lp, "--ttl", "1")[0] == 0
    # TTL=1s：冻结钟跳 2s 即过期（全注入时钟，CLI 默认 now=真实钟——此处走库层验证过期让位）
    expired = datetime.now(timezone.utc) + timedelta(seconds=2)
    res = cl.claim("sid-B", path=lp, now=expired)
    assert res["ok"] is True and res["chief"] == "sid-B"
