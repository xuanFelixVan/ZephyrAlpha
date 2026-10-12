# [A_test] module_id=MOD-GOV_ENQUEUE_CLAIM_RENEWAL_TEST | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.gov.governance.test_enqueue_claim_renewal
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; sys; types; pathlib; inspect; scripts.commit_queue
# [CONSUMERS] pytest 自动发现；通宵令"claim TTL/租约错配修法"红绿自证
# [STARTUP] python -m pytest tests/gov/governance/test_enqueue_claim_renewal.py
# [MATURITY] testing
# [INVARIANTS] 零真锁：lock_files 一律以 sys.modules 替身注入，绝不碰主区 .ailocks；
#              四臂各管一条口径（ttl 旋钮/参数透传/fail-open/住在入袋口的结构锁）
# [MODIFY-GUARD] 把续租从 enqueue_item 挪回任一单通道（CLI/requeue/改道重新不续）即红
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] tests/gov/governance/test_enqueue_claim_renewal.py
# [TTL] permanent
"""test_enqueue_claim_renewal.py — 入袋口 claim 续租覆盖自证（队列完整性簇第二件）。

病根实测：续租此前只在交互正门一条通道（git_commit.py:1004-1014），`commit_queue.py enqueue`
直投／`requeue` 复投／网关改道三条全不续（全仓 renew_claim 消费者实测仅一处）；队列深时
一袋等数小时（今夜实测 12.8 分钟/袋），30min 缺省 claim 早过期，held_files 面 90s 心跳一断
即被静默重建＝归因漂移。修法＝把续租升到**入袋合流口** enqueue_item，四条通道共享一份语义。
"""

from __future__ import annotations

import inspect
import sys
import types
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import commit_queue as cq  # noqa: E402


def _fake_lock_files(record: dict, *, raise_exc: bool = False) -> types.SimpleNamespace:
    def _renew_claim(sid, files, ttl_s=None):
        if raise_exc:
            raise RuntimeError("锁目录不可达")
        record["sid"] = sid
        record["files"] = list(files)
        record["ttl"] = ttl_s
        return list(files)

    return types.SimpleNamespace(renew_claim=_renew_claim)


def test_ttl_knob_and_defaults_are_shared_with_front_door(monkeypatch) -> None:
    """旋钮口径与交互正门一致（ZEPHYR_ENQUEUE_CLAIM_TTL_S，缺省 7200s）——不新造第二把旋钮。"""
    rec: dict = {}
    monkeypatch.setitem(sys.modules, "lock_files", _fake_lock_files(rec))
    monkeypatch.delenv("ZEPHYR_ENQUEUE_CLAIM_TTL_S", raising=False)
    out = cq._renew_claims_inflight("st-lane-a", ["a.py", "b.py"])
    assert rec["ttl"] == 7200.0 and rec["sid"] == "st-lane-a" and rec["files"] == ["a.py", "b.py"]
    assert out == {"renewed": 2, "requested": 2, "ttl_s": 7200.0}

    monkeypatch.setenv("ZEPHYR_ENQUEUE_CLAIM_TTL_S", "3600")
    cq._renew_claims_inflight("st-lane-a", ["a.py"])
    assert rec["ttl"] == 3600.0, "回退旗失效＝一键回退是假的"


def test_renewal_failure_never_blocks_enqueue(monkeypatch) -> None:
    """fail-open 臂：锁面异常一律折进返回值，不向上抛（入袋=快照即完成，落地侧仍会重 claim）。"""
    monkeypatch.setitem(sys.modules, "lock_files", _fake_lock_files({}, raise_exc=True))
    out = cq._renew_claims_inflight("st-lane-b", ["x.py"])
    assert out["renewed"] == 0 and out["requested"] == 1 and out["error"] == "RuntimeError"


def test_missing_session_or_files_skips_without_touching_locks(monkeypatch) -> None:
    """不误伤臂：无 sid 或空件集 ⇒ 根本不碰 lock 面（宁不动现状，也不给无关会话挂租约）。"""
    rec: dict = {}
    monkeypatch.setitem(sys.modules, "lock_files", _fake_lock_files(rec))
    assert cq._renew_claims_inflight("", ["a.py"])["skipped"] == "no_session_or_files"
    assert cq._renew_claims_inflight("st-lane-c", [])["skipped"] == "no_session_or_files"
    assert "sid" not in rec, "跳过臂仍调了 renew＝判据没生效"


def test_renewal_lives_at_the_enqueue_choke_point() -> None:
    """结构锁：续租必须住在入袋合流口，且 CLI/requeue 确实经该口（挪回单通道即红）。"""
    body = inspect.getsource(cq.enqueue_item)
    assert "_renew_claims_inflight(session_id" in body, "入袋口没续租＝三条不续通道复活"
    assert "ZEPHYR_ENQUEUE_CLAIM_TTL_S" in inspect.getsource(cq._renew_claims_inflight)


def test_requeue_path_flows_through_the_same_choke_point() -> None:
    """requeue 覆盖臂：复投必须复用入袋口（否则复投袋仍是零续租的长等袋）。"""
    src = Path(cq.__file__).read_text(encoding="utf-8", errors="replace")
    i = src.index("def requeue_dead_item(")
    j = src.index("\ndef ", i + 10)
    assert "enqueue_item(" in src[i:j], "requeue 绕过入袋口＝本件覆盖声明落空"


@pytest.mark.parametrize("sid,files", [("", ["a.py"]), ("st-x", []), ("st-x", ["a.py", "b.py"])])
def test_verdict_shapes_are_stable(monkeypatch, sid: str, files: list[str]) -> None:
    """出口计数键恒在（降级态不得与"没触发"同形——在册假绿教训）。"""
    rec: dict = {}
    monkeypatch.setitem(sys.modules, "lock_files", _fake_lock_files(rec))
    out = cq._renew_claims_inflight(sid, files)
    assert {"renewed", "requested"} <= set(out), out
    assert out["requested"] == len(files)
