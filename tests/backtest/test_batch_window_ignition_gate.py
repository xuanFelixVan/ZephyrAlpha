# [BLUEPRINT] MOD-BT-226 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_batch_window_ignition_gate
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; zephyr.backtest.core.batch_window_preflight; scripts.backtest.compute_window_gate
# [CONSUMERS] 波12 点火闸红证（R-5：没红过的规则不算规则）——阻断/转绿/缺卡/不可读四态 + 伪造批文
#   与改空间两态防伪 + 执行器接线自证（防"装饰性守卫无调用方"）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 全用例零 IO 零网络零写生产盘（通道全注入替身，文件面全落 tmp_path）；
#   禁写 n_trial_ledger；禁读 config/search_space_prereg.yaml 真件（用 tmp 副本）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-227 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""波 12 统一跑批窗口点火闸红证（MOD-BT-226 判据面 + FAC-E0 接线面）。

覆盖四类必红（任务书 R-5 明列）：
  1. 任一触发条件未绿 → 拒，且点名是哪条；
  2. 最后一条翻绿 → 放行（证明闸不是恒红摆设）；
  3. 五条全绿但批准卡缺失/未批 → 仍拒（Owner 门位不可由 AI 侧凑齐）；
  4. 条件不可读 → UNKNOWN 且仍拒（禁"读不到=干净"，本仓反复被烧的形态）。
另加两处防伪（本仓假绿主形态）：卡上自称 APPROVED 但批文锚在裁定册查无 → 拒；
批后偷改预注册（摘要不一致）→ 拒。以及执行器接线自证（防装饰性守卫）。
"""

from __future__ import annotations

import sys
import textwrap
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "backtest"))

from compute_window_gate import (  # noqa: E402
    REASON_ALLOW_IGNITION_ARMED,
    REASON_ALLOW_OFFHOURS,
    REASON_DENY_IGNITION_NOT_ARMED,
    REASON_DENY_IGNITION_PREFLIGHT_FAILED,
    check_gate,
    check_ignition,
)

from zephyr.backtest.core import batch_window_preflight as bwp  # noqa: E402

_TZ = ZoneInfo("Asia/Shanghai")
_NOW = datetime(2026, 9, 27, 3, 0, tzinfo=_TZ)  # 休市日/盘外——日历窗必放行，隔离出点火面

_RULING_ID = "R-TEST-1"  # 测试用假锚（非 裁定#NNN 形态，避免未登记引用门连坐）


def _reading(cid: str, status: str = bwp.STATUS_GREEN, **kw: str) -> bwp.ConditionReading:
    return bwp.ConditionReading(
        condition_id=cid,
        title_zh=cid,
        status=status,
        cmd="echo test",
        channel="fake",
        as_of=_NOW.isoformat(),
        evidence=kw.get("evidence", ""),
        unknown_reason=kw.get("unknown_reason", ""),
        knowable_when=kw.get("knowable_when", ""),
    )


def _card(
    status: str = "APPROVED",
    *,
    ref_registered: bool = True,
    prereg_ok: bool = True,
    universe: bool = True,
    exists: bool = True,
) -> bwp.ApprovalReading:
    reasons: list[str] = []
    if not exists:
        reasons.append("批准卡不存在")
    if status != "APPROVED":
        reasons.append(f"status={status}")
    return bwp.ApprovalReading(
        exists=exists,
        status=status if exists else "MISSING",
        cmd="cat card",
        channel="fake",
        as_of=_NOW.isoformat(),
        approval_ref=_RULING_ID if ref_registered else "R-NOPE-9",
        approval_ref_registered=ref_registered,
        prereg_sha_matches=prereg_ok,
        universe_sha_present=universe,
        reasons=tuple(reasons),
    )


def _all_green() -> dict[str, bwp.ConditionReader]:
    return {c: (lambda ctx, c=c: _reading(c)) for c in bwp.W12_CONDITION_IDS}


def _ctx(tmp_path: Path) -> bwp.PreflightContext:
    return bwp.PreflightContext(now=_NOW, repo_root=tmp_path)


def _verdict(monkeypatch, readers, approval):
    """跑判决并把批准卡读数换成注入值（条件读数走 readers）。"""
    monkeypatch.setattr(bwp, "read_approval_card", lambda ctx: approval)
    return bwp.run_preflight(_ctx(Path(".")), readers=readers)


# --------------------------------------------------------------------------- 必红四态


def test_blocked_condition_set_refuses_and_names_the_blocker(monkeypatch):
    """红证①：任一条件 RED → 拒，且点名是哪条挡。"""
    readers = _all_green()
    readers[bwp.C4_COST_CALIBER] = lambda ctx: _reading(bwp.C4_COST_CALIBER, bwp.STATUS_BLOCKED)
    v = _verdict(monkeypatch, readers, _card())

    assert v.allowed is False
    assert v.blocking == (bwp.C4_COST_CALIBER,)
    detail = bwp.blocking_detail(v)
    assert bwp.C4_COST_CALIBER in detail and bwp.C2_SECTOR_UNIVERSE not in detail


def test_flipping_last_condition_green_yields_proceed(monkeypatch):
    """红证②：最后一条翻绿即放行——证明闸不是恒红摆设（条件性执法，不是装饰）。"""
    four = {c: (lambda ctx, c=c: _reading(c)) for c in bwp.W12_CONDITION_IDS[:-1]}
    four[bwp.C5_T2_PROMOTION_POOL] = lambda ctx: _reading(bwp.C5_T2_PROMOTION_POOL, bwp.STATUS_RED)
    assert bwp.run_preflight(_ctx(Path(".")), readers=four, approval=_card()).allowed is False

    v = _verdict(monkeypatch, _all_green(), _card())
    assert v.allowed is True and v.blocking == ()


def test_missing_approval_card_refuses_even_when_all_five_green(monkeypatch):
    """红证③：五条全绿但批准卡缺失 → 仍拒（唯一合法停点=WAITING_APPROVAL 等 Owner）。"""
    v = _verdict(monkeypatch, _all_green(), _card(exists=False))

    assert v.allowed is False
    assert v.blocking == ("approval_card",)
    assert "批准卡" in bwp.blocking_detail(v)


def test_waiting_approval_status_refuses(monkeypatch):
    """红证③补：呈卡后未批（WAITING_APPROVAL）同样拒。"""
    v = _verdict(monkeypatch, _all_green(), _card(status="WAITING_APPROVAL"))
    assert v.allowed is False and v.blocking == ("approval_card",)


def test_unreadable_condition_is_unknown_and_still_refuses(monkeypatch):
    """红证④：读数通道抛错 → UNKNOWN（非绿）且计入阻断，禁静默归零。"""
    readers = _all_green()
    readers[bwp.C2_SECTOR_UNIVERSE] = lambda ctx: _reading(
        bwp.C2_SECTOR_UNIVERSE, bwp.STATUS_UNKNOWN, unknown_reason="CH 通道不可达"
    )
    v = _verdict(monkeypatch, readers, _card())

    assert v.allowed is False
    assert v.blocking == (bwp.C2_SECTOR_UNIVERSE,)
    assert v.condition(bwp.C2_SECTOR_UNIVERSE).status == bwp.STATUS_UNKNOWN


def test_real_reader_channel_failure_degrades_to_unknown_not_green(tmp_path):
    """红证④续：走**真实读数器**注入会抛错的通道 → UNKNOWN + knowable_when 非空。"""
    ctx = bwp.PreflightContext(
        now=_NOW,
        repo_root=tmp_path,
        ch_execute=_raising,
        governance_rows=_raising,
        git_probe=_raising_git,
        main_root=tmp_path,
    )
    ctx2 = _with_fake_ruling(tmp_path, ctx)
    reading = bwp.read_sector_universe(ctx2)

    assert reading.status == bwp.STATUS_UNKNOWN
    assert reading.unknown_reason and reading.knowable_when
    assert reading.status != bwp.STATUS_GREEN  # 读不到绝不当成绿


def test_missing_governance_handle_yields_unknown(tmp_path):
    """governance 通道未注入（车道常态）→ c1a 落 UNKNOWN 而非"零卡=没活要干"。"""
    ctx = bwp.PreflightContext(now=_NOW, repo_root=tmp_path, git_probe=lambda argv, globs=(): [])
    assert bwp._wave_card_status(ctx).status == bwp.STATUS_UNKNOWN


# --------------------------------------------------------------------------- 防伪两态


def test_forged_approval_reference_does_not_count(tmp_path):
    """卡上自称 APPROVED、批文锚在裁定册查无 → 拒（散文自证绿不算批）。"""
    root = _seed_tree(tmp_path, card_status="APPROVED", card_ref="R-FABRICATED-9")
    v = bwp.run_preflight(_ctx(root), readers=_all_green())

    assert v.allowed is False
    assert "approval_card" in v.blocking
    assert any("裁定册查无" in r for r in v.approval.reasons)


def test_prereg_changed_after_approval_invalidates_card(tmp_path):
    """批后偷改预注册（摘要不一致）→ 卡作废并拒（对齐 17 号文 prereg hash 触发线）。"""
    root = _seed_tree(tmp_path, card_status="APPROVED", card_ref=_RULING_ID, card_prereg_sha="0" * 64)
    v = bwp.run_preflight(_ctx(root), readers=_all_green())

    assert v.allowed is False
    assert any("预注册" in r or "prereg" in r for r in v.approval.reasons)


def test_universe_declaration_sha_required(tmp_path):
    """宇宙声明未摘要（烧错宇宙不可归责）→ 拒。"""
    root = _seed_tree(tmp_path, card_status="APPROVED", card_ref=_RULING_ID, card_universe="")
    assert any("universe" in r for r in bwp.read_approval_card(_ctx(root)).reasons)


def test_prose_claim_of_owner_approval_is_not_a_ruling(tmp_path):
    """散文里写"Owner 已批准成本门口径"不转绿——只认裁定册成对关键词命中条目。"""
    root = tmp_path
    (root / "docs").mkdir(parents=True, exist_ok=True)
    note = root / "docs" / "claimed_approval.md"
    note.write_text("Owner已批准：成本门抽查口径按幸存者分层抽（此为工棚散文，非正式通道）\n", encoding="utf-8")
    _write_rulings(root, [])  # 裁定册零条目 → 读数器拒判已裁（异常降级，不落绿）
    ctx = bwp.PreflightContext(now=_NOW, repo_root=root)
    reading = bwp.read_cost_gate_caliber(ctx)

    assert reading.status in {bwp.STATUS_BLOCKED, bwp.STATUS_UNKNOWN}
    assert reading.status != bwp.STATUS_GREEN


def test_registered_owner_ruling_turns_c4_green(tmp_path):
    """同一条批文登记进裁定册（正式通道）→ c4 转绿：门位经登记生效，非经口头。"""
    _write_rulings(
        root=tmp_path,
        entries=[
            {
                "ruling_id": _RULING_ID,
                "date": "2026-09-27",
                "status": "decided",
                "category": "架构",
                "title": "⚑-2 成本门抽查口径追认（B∧C 案）",
                "summary": "抽查口径改为从通过成本门的幸存者里分层抽，五档与阈值一字不动。",
            }
        ],
    )
    ctx = bwp.PreflightContext(now=_NOW, repo_root=tmp_path)

    assert bwp.read_cost_gate_caliber(ctx).status == bwp.STATUS_GREEN


def test_same_name_old_ruling_does_not_fake_green(tmp_path):
    """同名无关旧裁定（做T 成本门，早于立案日）不得造绿——成对关键词+日期双限的靶。"""
    _write_rulings(
        root=tmp_path,
        entries=[
            {
                "ruling_id": "R-OLD-0",
                "date": "2026-08-01",
                "status": "active",
                "category": "架构",
                "title": "做T 终裁包（成本门绝对金额制）",
                "summary": "成本门废固定比例改绝对金额制，抽查幸存者口径无关。",
            }
        ],
    )
    ctx = bwp.PreflightContext(now=_NOW, repo_root=tmp_path)

    assert bwp.read_cost_gate_caliber(ctx).status == bwp.STATUS_BLOCKED


# --------------------------------------------------------------------------- 目标值与命名法


def test_undeclared_target_yields_unknown_never_guessed(tmp_path):
    """共振矩阵单格目标耗时未声明 → UNKNOWN（本模块零自定阈值，绝不代拍）。"""
    _write_prereg(tmp_path, {"per_point_seconds_measured": 35.33})
    ctx = bwp.PreflightContext(now=_NOW, repo_root=tmp_path)
    reading = bwp.read_gpu_l2(ctx)

    assert reading.status == bwp.STATUS_UNKNOWN
    assert "他轨" in reading.evidence  # 明写：grid T0 读数不可替代


def test_declared_target_and_measurement_decides(tmp_path):
    """目标+实测都声明后 → 真判（达标绿/不达标红，各测一次）。"""
    _write_prereg(tmp_path, {"resonance_per_cell_seconds_target": 5.0, "resonance_per_cell_seconds_measured": 4.2})
    ok = bwp.read_gpu_l2(bwp.PreflightContext(now=_NOW, repo_root=tmp_path))
    assert ok.status == bwp.STATUS_GREEN

    _write_prereg(tmp_path, {"resonance_per_cell_seconds_target": 5.0, "resonance_per_cell_seconds_measured": 9.9})
    bad = bwp.read_gpu_l2(bwp.PreflightContext(now=_NOW, repo_root=tmp_path))
    assert bad.status == bwp.STATUS_RED


def test_wave12_purpose_naming_is_the_gate_trigger():
    """purpose 命名法即闸门识别法：前缀命中才加点火前置，普通 purpose 判据零改动。"""
    assert all(p.startswith("wave12_") for p in bwp.W12_WINDOW_PURPOSES)
    assert check_gate("f06_grid_batch", "local", _NOW)["allowed"] is True


# --------------------------------------------------------------------------- 接线自证


def test_gate_blocks_ignition_purpose_even_offhours(monkeypatch, tmp_path):
    """休市日盘外（日历窗本放行）仍被点火闸拒——证明接线在执法不在装饰。"""
    root = _seed_tree(tmp_path, card_status="WAITING_APPROVAL")
    monkeypatch.setattr(bwp, "build_context", lambda now=None, repo_root=None: _ctx(root))
    monkeypatch.setattr(bwp, "DEFAULT_READERS", _all_green())

    decision = check_gate("wave12_t2_final", "local_gpu", _NOW)

    assert decision["allowed"] is False
    assert decision["reason_code"] == REASON_DENY_IGNITION_NOT_ARMED
    assert list(decision["blocking"]) == ["approval_card"]


def test_gate_allows_ignition_purpose_when_armed(monkeypatch, tmp_path):
    """全绿+批文在册 → 日历窗放行（盘外），reason 落 heavy_ok 且标 ignition armed。"""
    root = _seed_tree(tmp_path, card_status="APPROVED", card_ref=_RULING_ID)
    monkeypatch.setattr(bwp, "build_context", lambda now=None, repo_root=None: _ctx(root))
    monkeypatch.setattr(bwp, "DEFAULT_READERS", _all_green())
    monkeypatch.setattr("compute_window_gate.fetch_is_trading_day", lambda d: False)

    decision = check_gate("wave12_t2_final", "local_gpu", _NOW)

    assert decision["allowed"] is True
    assert decision["reason_code"] == REASON_ALLOW_OFFHOURS
    assert decision["ignition"] == REASON_ALLOW_IGNITION_ARMED


def test_preflight_crash_refuses(monkeypatch):
    """预检器自身崩（依赖缺失/通道炸）→ 拒，不当成"没有这道闸"。"""

    def _boom(now=None, repo_root=None):
        raise RuntimeError("预检支撑件不可用")

    monkeypatch.setattr(bwp, "build_context", _boom)
    decision = check_ignition("wave12_resonance_first", _NOW)

    assert decision["allowed"] is False
    assert decision["reason_code"] == REASON_DENY_IGNITION_PREFLIGHT_FAILED


def test_executor_routes_stage_t2_to_ignition_purpose(monkeypatch, tmp_path):
    """执行器接线自证：stage=t2 必须走点火 purpose，且 t0/t1/空 stage 保持原 purpose。"""
    import factory_grid_executor as fge

    seen: list[str] = []
    monkeypatch.setattr(
        "compute_window_gate.check_gate", lambda purpose, cls, now: seen.append(purpose) or {"allowed": True}
    )
    for stage in ("t2", "t1", ""):
        fge._ask_compute_window_gate(stage)

    assert seen == ["wave12_t2_final", "f06_grid_batch", "f06_grid_batch"]


def test_executor_refusal_carries_blocker_names(monkeypatch):
    """执行器拒绝时把阻断清单打到退出消息（"到底哪条挡着"必须一眼可见）。"""
    import factory_grid_executor as fge

    def _deny(purpose, cls, now):
        return {
            "allowed": False,
            "reason_code": REASON_DENY_IGNITION_NOT_ARMED,
            "blocking": [bwp.C4_COST_CALIBER],
            "detail": "等 Owner 拍板",
        }

    monkeypatch.setattr("compute_window_gate.check_gate", _deny)
    with pytest.raises(SystemExit) as exc:
        fge._ask_compute_window_gate("t2")

    assert bwp.C4_COST_CALIBER in str(exc.value)
    msg = str(exc.value)
    assert "docs/" not in msg and "\\" not in msg  # 不含内部路径（MSG-EXPOSURE）


# --------------------------------------------------------------------------- 夹具（全落 tmp，零触生产盘）


def _raising(sql: str):
    raise RuntimeError("通道故障（模拟 CH/governance 不可达）")


def _raising_git(argv, globs=()):
    raise RuntimeError("git 树面不可达")


def _with_fake_ruling(tmp_path: Path, ctx: bwp.PreflightContext) -> bwp.PreflightContext:
    _write_rulings(tmp_path, [])
    return bwp.PreflightContext(
        now=ctx.now,
        repo_root=tmp_path,
        ch_execute=_raising,
        governance_rows=_raising,
        git_probe=_raising_git,
        main_root=tmp_path,
    )


def _write_rulings(root: Path, entries: list[dict]) -> None:
    import yaml

    p = root / bwp.RULING_REGISTRY_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        yaml.safe_dump({"entries": entries}, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n"
    )


def _write_prereg(root: Path, caps: dict) -> None:
    import yaml

    p = root / bwp.PREREG_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        yaml.safe_dump({"budget_caps": caps}, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n"
    )


def _seed_tree(
    root: Path,
    *,
    card_status: str,
    card_ref: str = _RULING_ID,
    card_prereg_sha: str | None = None,
    card_universe: str | None = "u" * 64,
    rulings: list[dict] | None = None,
) -> Path:
    """在 tmp 里铺出"裁定册 + 预注册 + 批准卡"三件套（批准卡摘要与预注册实算一致）。"""
    from zephyr.backtest.core.batch_window_preflight import sha256_file

    _write_rulings(
        root,
        rulings
        if rulings is not None
        else [
            {
                "ruling_id": _RULING_ID,
                "date": "2026-09-27",
                "status": "decided",
                "category": "架构",
                "title": "波12 窗口点火批准（Owner 裁）",
                "summary": "一窗一卡，批一次管全窗。",
            }
        ],
    )
    _write_prereg(root, {"grid_points_cap": 25000})
    body = textwrap.dedent(f"""\
        status: {card_status}
        approval_ref: {card_ref if card_ref else "null"}
        universe_declaration_sha256: {card_universe if card_universe else "null"}
        prereg_sha256: {card_prereg_sha if card_prereg_sha else sha256_file(root / bwp.PREREG_REL)}
    """)
    card = root / bwp.APPROVAL_CARD_REL
    card.parent.mkdir(parents=True, exist_ok=True)
    card.write_text(body, encoding="utf-8", newline="\n")
    return root
