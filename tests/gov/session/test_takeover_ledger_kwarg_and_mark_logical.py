# [TTL] permanent
# [MODULE] tests.gov.session.test_takeover_ledger_kwarg_and_mark_logical
# [STARTUP] pytest collection only（零生产路径写：全部落 tmp_path fixture）
# [CONSUMERS] 无运行时消费者；本班裁定包"候件+1"＋⑤保活正门评估的验收件
"""接管台账形参错位修复 ＋ mark_logical 授标核验（st-maint2-20261011，2026-10-11）。

两件同族（都是"会话死亡显化/保活"这条地基上的静默面）：

1. `session_concurrency` 判死循环里调 `write_takeover_entry(..., extra_death_evidence=…)`，
   而被调方形参叫 `death_evidence`（`session_takeover_ledger.py:987-995`）⇒ **每次判死都
   TypeError**，又被 `except Exception` 只记 warning 吞掉 ⇒ "会话死亡显化台账"从未写成
   （后果不是少一个字段，是整条接管条目缺失）。第 1、2 例＝AST 级形参一致性检查＋功能落盘；
   第 3 例＝对 dev 原始字节（内容寻址）跑同一把尺，证明缺陷原样存在（红来自字节非推测）。
2. `mark_logical(sid, logical=True)` 原先**不做** `_verify_chief_form`（核验只写在
   `register():1124`），而 `logical=True` 的实际作用＝豁免 register 的 1860s 重注册频率
   护栏（它不进 `_is_session_alive`）⇒ 等于一条绕开 W-29 的自授权口。第 4-8 例＝
   授标须过核验／撤标永远放行／既有条目已带标不误伤／未在册返回 False 语义不变。
"""

from __future__ import annotations

import ast
import importlib.util
import inspect
import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

from zephyr.security.access_control.session_concurrency import SessionRegistry  # noqa: E402

BASELINE_SHA = "cfbebbf8dd49f8b8ae935d186f4fbe7f8cfc6c66"
CALLER_REL = "src/zephyr/security/access_control/session_concurrency.py"
CALLEE_REL = "scripts/governance/session_takeover_ledger.py"


def _load_callee(path: Path):
    spec = importlib.util.spec_from_file_location("takeover_ledger_under_test", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _caller_kwargs_for(path: Path, func_name: str = "write_takeover_entry") -> set[str]:
    """从调用方源码里机提实参关键字（形参改名的漂移只有这种尺能抓到）。"""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            name = getattr(fn, "id", None) or getattr(fn, "attr", None)
            if name == func_name:
                found |= {kw.arg for kw in node.keywords if kw.arg}
    assert found, f"调用方源码里查无 {func_name} 调用（尺失效，不是通过）"
    return found


# ---------------------------------------------------------------------------
# 1-3 接管台账形参错位
# ---------------------------------------------------------------------------


def test_caller_kwargs_are_subset_of_callee_signature() -> None:
    mod = _load_callee(ROOT / CALLEE_REL)
    params = set(inspect.signature(mod.write_takeover_entry).parameters)
    used = _caller_kwargs_for(ROOT / CALLER_REL)
    unknown = used - params
    assert unknown == set(), f"调用方传了被调方没有的形参（会被 broad except 吞成静默降级）：{unknown}"


def test_takeover_entry_actually_written_with_death_evidence(tmp_path: Path) -> None:
    """功能面：按调用方实参形态真写一条，且落盘可见（不能只"不抛"）。"""
    mod = _load_callee(ROOT / CALLEE_REL)
    root = tmp_path / "rt"
    (root / ".runtime").mkdir(parents=True)
    entry = mod.write_takeover_entry(
        root,
        "st-probe-dead-20261011",
        registry_entry={"session_id": "st-probe-dead-20261011"},
        now=time.time(),
        extra_death_evidence={"alive_side_evidence": {"any_alive_side": False, "witnesses": []}},
    )
    assert isinstance(entry, dict) and entry, "write_takeover_entry 应返回写入后的条目"
    ledger = root / ".runtime" / "takeover_ledger.jsonl"
    assert ledger.exists(), f"接管台账未落盘（查 {ledger}）"
    rows = [json.loads(x) for x in ledger.read_text(encoding="utf-8").splitlines() if x.strip()]
    mine = [r for r in rows if r.get("sid") == "st-probe-dead-20261011"]
    assert mine, rows
    # 合并语义（session_takeover_ledger.py:1023-1024 `death_evidence = {**death_evidence, **extra}`）：
    # 三证读数必须真进台账条目的 death_evidence——形参被删（回退弹落地）时这条必红，而不是默默少字段。
    assert (mine[-1].get("death_evidence") or {}).get("alive_side_evidence") == {
        "any_alive_side": False,
        "witnesses": [],
    }, f"三证读数未并入 death_evidence（合并腿失效）：{mine[-1]}"


def test_contract_guard_has_teeth_against_head_subset_rollback(tmp_path: Path) -> None:
    """这把尺必须有牙：拿"主区暂存那份回退弹"的形态（纯删 extra_death_evidence）喂进去要判红。

    现场凭据（本班 2026-10-11 实读主区）：`git diff --cached --numstat` 对 dev 是
    **0 增 / 11 删**，被删的正是该形参＋合并行＋[MODIFY-GUARD]:12 三证立法注。
    无判别力的合同闸等于没闸（在册形态：恒真空集／提到即算）。
    """
    good = _load_callee(ROOT / CALLEE_REL)
    params = set(inspect.signature(good.write_takeover_entry).parameters)
    used = _caller_kwargs_for(ROOT / CALLER_REL)
    assert used - params == set(), "当前 dev 面合同应成立（被调方确实收 extra_death_evidence）"

    stripped = (
        (ROOT / CALLEE_REL).read_text(encoding="utf-8").replace("    extra_death_evidence: dict | None = None,\n", "")
    )
    assert stripped != (ROOT / CALLEE_REL).read_text(encoding="utf-8"), "剥形参夹具失效（什么都没删掉）"
    fake = tmp_path / "stripped_ledger.py"
    fake.write_text(stripped, encoding="utf-8")
    bad = _load_callee(fake)
    bad_params = set(inspect.signature(bad.write_takeover_entry).parameters)
    assert "extra_death_evidence" not in bad_params
    assert used - bad_params == {"extra_death_evidence"}, "尺抓不到回退弹 ⇒ 本件无判别力，须重做"


def test_pristine_baseline_already_had_matching_signature() -> None:
    """基线自证：错位不是本班引入的——dev 基线调用方与被调方本就同名同物。

    （本班一度据"主区盘上那份缺形参"判为形参错位并把调用方改成 death_evidence，
    实为读到回退弹⇒误伤，已撤回；这条就是那次误判的反向钉桩。）
    """
    caller_raw = subprocess.run(
        ["git", "-C", ROOT.as_posix(), "show", f"{BASELINE_SHA}:{CALLER_REL}"],
        capture_output=True,
    ).stdout
    callee_raw = subprocess.run(
        ["git", "-C", ROOT.as_posix(), "show", f"{BASELINE_SHA}:{CALLEE_REL}"],
        capture_output=True,
    ).stdout
    assert caller_raw and callee_raw, "基线 blob 取回失败"
    assert b"extra_death_evidence: dict | None = None" in callee_raw, (
        "基线被调方应已含三证配套形参（维护一班 t3lane 落地件）；查无＝本班对本件的定性需重估"
    )
    probe = ROOT / ".runtime" / "tmp" / "pristine_caller_parity.py"
    probe.parent.mkdir(parents=True, exist_ok=True)
    probe.write_bytes(caller_raw)
    try:
        assert "extra_death_evidence" in _caller_kwargs_for(probe), "基线调用方实参形态被改动过"
    finally:
        probe.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# 4-8 mark_logical 授标核验
# ---------------------------------------------------------------------------


def _registry(tmp_path: Path) -> SessionRegistry:
    return SessionRegistry(project_root=tmp_path)


def _seed(reg: SessionRegistry, sid: str) -> None:
    reg.register(sid, pid=0, held_files=[])


def test_mark_logical_denied_for_non_chief_without_fresh_heartbeat(tmp_path: Path) -> None:
    reg = _registry(tmp_path)
    sid = "st-plain-worker-20261011"
    _seed(reg, sid)
    assert reg.mark_logical(sid, logical=True) is False, "非 chief 形态且心跳不新鲜，授标必须被拒"
    got = reg.get_session(sid)
    assert not bool(getattr(got, "logical", True)), f"被拒后条目不得带上 logical 标：{got}"


def test_mark_logical_allowed_for_chief_form_sid(tmp_path: Path) -> None:
    """正向腿（防我把核验做成"永远拒绝"）：chief 形态词命中即授标。"""
    reg = _registry(tmp_path)
    sid = "st-chief-probe-20261011"
    _seed(reg, sid)
    assert reg.mark_logical(sid, logical=True) is True
    assert bool(getattr(reg.get_session(sid), "logical", None)) is True


def test_mark_logical_allowed_with_fresh_heartbeat(tmp_path: Path) -> None:
    """形态核验证据②（心跳 <120s 真在岗）必须仍通——否则就是把 GPU 班那条正解堵死。"""
    reg = _registry(tmp_path)
    sid = "st-fresh-hb-20261011"
    _seed(reg, sid)
    hb = tmp_path / ".runtime" / "sessions" / sid / "heartbeat.jsonl"
    hb.parent.mkdir(parents=True, exist_ok=True)
    hb.write_text(
        json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "pid": 0, "status": "alive"}) + "\n", encoding="utf-8"
    )
    os_age = time.time() - hb.stat().st_mtime
    assert os_age < 120.0, f"夹具自身心跳已 {os_age:.1f}s，测不了证据②"
    assert reg.mark_logical(sid, logical=True) is True


def test_revoking_logical_flag_is_always_allowed(tmp_path: Path) -> None:
    """收紧不对称：撤标（False）永远放行，哪怕非 chief 形态——只许减特权。"""
    reg = _registry(tmp_path)
    sid = "st-chief-revoke-20261011"
    _seed(reg, sid)
    assert reg.mark_logical(sid, logical=True) is True
    plain = "st-plain-worker-20261011"
    _seed(reg, plain)
    assert reg.mark_logical(plain, logical=False) is True
    assert not bool(getattr(reg.get_session(plain), "logical", None))


def test_mark_logical_on_unregistered_session_still_false(tmp_path: Path) -> None:
    """既有语义零变更：不在册 ⇒ False（不因新核验分支而变成抛异常或授标）。"""
    reg = _registry(tmp_path)
    assert reg.mark_logical("st-never-registered-20261011", logical=True) is False
