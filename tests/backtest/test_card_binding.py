# [BLUEPRINT] MOD-BT-248 | docs/03_modules/_domain_backtest/blueprint.md
# [TESTS] tests/backtest/test_card_binding.py
# [TTL] permanent
# 测试隔离：卡件/绑定册/分数册全在 tmp_path；信号面用 monkeypatch 合成（零 CH、零生产路径写）。
"""绑定层红蓝双向：分类拒绑口径/绑定册引句自闸/CH 让路钟闸/位置协议解析。

判别力声明（在册教训：判通过的脚本须先证明能红）——本文件里 CH 让路闸、
prose_quote 校验、缺 data_binding 拒绑三处都写了"应当拒"的正例，任何一条被写成恒过都会红。
"""

from __future__ import annotations

import copy
import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from scripts.backtest.fexam import card_binding as cb


def _crash_then_climb_nav():
    """平顶 20 日 → 10 日跌到 0.65（进 KILL）→ 60 日单调爬回 1.05（回补比例一路走高）。"""
    seg = [1.0] * 20 + list(np.linspace(1.0, 0.65, 10)) + list(np.linspace(0.66, 1.05, 60))
    return pd.Series(seg, index=pd.bdate_range("2023-01-02", periods=len(seg)), dtype="float64")


def _ctx_card(ladder=None, extra_tables=None):
    """判官上下文要的卡面：07b 的 `data_binding.level_to_cap_map` 最小形（阶梯表可改坏以验红线）。

    `ladder=None` ＝不给 recovery_ladder（非复位档用得上：缺表也必须照样过）。
    `extra_tables` 用来添"带阶梯的行"（开臂走在册阶梯、关臂按声明复位即回满），
    卡面没声明过的三元组一律算在册外拍数——这正是被拦的那一面。
    """
    maps = {
        "five_state_native": {"NORMAL": 1.0, "WARN": 0.8, "DANGER": 0.5, "CRISIS": 0.3, "KILL": 0.0},
        "binary_full_clear": {"NORMAL": 1.0, "WARN": 1.0, "DANGER": 1.0, "CRISIS": 1.0, "KILL": 0.0},
    }
    if ladder is not None:
        maps["recovery_ladder"] = ladder
    for k, v in (extra_tables or {}).items():
        maps[k] = v
    return {"card_id": "TDM-X-R1-01/comparison/probe", "data_binding": {"level_to_cap_map": maps}}


def _reset_ctx_pair(rung=None):
    """07b 形配对（两臂都点复位档）：册格＋底座的最小完整夹具，rung 可改坏以验红线。"""
    five = {"NORMAL": 1.0, "WARN": 0.8, "DANGER": 0.5, "CRISIS": 0.3, "KILL": 0.0}
    ladder = {"step_0": 0.25, "step_1": 0.5, "step_2": 0.75} if rung is None else rung
    rungs = {f"RECOVERY@{i}": ladder[f"step_{i}"] for i in range(3)}
    arms = {
        "op_open": "arm_level_cap_multiply",
        "op_base": "arm_level_cap_multiply",
        "reset_trigger_recovered_pct": 0.5,
        "params_open": {"levels": "series:levels_with_reset", "level_map": {**five, **rungs}},
        "params_base": {"levels": "series:levels_no_hysteresis_with_reset", "level_map": {**five, **rungs}},
    }
    idx = pd.bdate_range("2024-01-02", periods=10)
    entry = {"card_id": "TDM-X-R1-01/comparison/probe", "arms": arms, "arms_variant_applied": "mid_A"}
    mod = cb._arm_protocol_module()
    pool = {
        "levels_with_reset": pd.Series(["NORMAL"] * 10, index=idx),
        "levels_no_hysteresis_with_reset": pd.Series(["RECOVERY@0"] * 10, index=idx),
    }
    base = mod.ArmBase(
        exposure=pd.Series(1.0, index=idx),
        daily_return=pd.Series(0.001, index=idx).round(6),
        series=pool,
        face_id="exit_sim_baseline_nav",
    )
    return entry, base


def test_arm_context_declares_tier_flags_and_bracket_for_judge():
    """接线钉：档位属性/复位括号值必须**申报**进上下文（判官禁按档名猜，四跑要能事后分辨）。"""
    idx, five, entry = _ctx_entry()
    entry["arms"]["reset_trigger_recovered_pct"] = 0.75
    ctx = cb.arm_context_for_judge(_ctx_card(), entry, _ctx_base(idx, five))
    assert ctx["tier_flags"] == {
        "open": {"hysteresis": True, "reset": False},
        "base": {"hysteresis": False, "reset": False},
    }
    assert ctx["base_is_no_hysteresis"] is True and ctx["open_is_no_hysteresis"] is False
    assert ctx["reset_trigger_recovered_pct"] == 0.75
    assert ctx["recovery_ladder"] == {"open": {}, "base": {}}  # 非复位档：阶梯面无事可做


def test_arm_context_off_pair_base_arm_may_declare_full_reentry():
    """形状约束只管开臂：关臂的"复位即一次买回"（三档 1.0）是卡面声明的角色，必须放行。
    卡面没声明过的三元组（0.9 那种）照红——放行的是"卡面说过"，不是"看起来宽松"。"""
    entry, base = _reset_ctx_pair()
    card = _ctx_card(
        ladder={"step_0": 0.25, "step_1": 0.5, "step_2": 0.75},
        extra_tables={
            "binary_full_clear_with_ladder": {
                "NORMAL": 1.0,
                "WARN": 1.0,
                "DANGER": 1.0,
                "CRISIS": 1.0,
                "KILL": 0.0,
                "RECOVERY@0": 1.0,
                "RECOVERY@1": 1.0,
                "RECOVERY@2": 1.0,
            }
        },
    )
    e = copy.deepcopy(entry)
    for lbl in cb._RECOVERY_RUNG_LABELS:
        e["arms"]["params_base"]["level_map"][lbl] = 1.0
    ctx = cb.arm_context_for_judge(card, e, base)
    assert ctx["recovery_ladder"]["base"]["rung_caps"] == [1.0, 1.0, 1.0]
    assert ctx["recovery_ladder"]["base"]["declined_from"] == "binary_full_clear_with_ladder"
    assert ctx["recovery_ladder"]["open"]["strictly_increasing"] is True
    e2 = copy.deepcopy(e)
    e2["arms"]["params_base"]["level_map"]["RECOVERY@0"] = 0.9
    with pytest.raises(RuntimeError, match="recovery_rung_cap_off_card_face:base"):
        cb.arm_context_for_judge(card, e2, base)


def test_arm_context_same_level_series_three_faces():
    """同一条级别序列的三面分开钉（off 配对是合法面，不是漏网面）。

    卡面声明"臂间差异只允许出现在级别→cap 乘子表"，07/07b 的 off 配对就是**同一序列×两张不同表**；
    上一版把这一面也一并拦了（＝把自己批过的配对拦死，2026-10-13 实测才暴露），按实质拆三面：
    ①同序列＋同乘子表＝两臂逐字全等⇒红；②同序列＋不同表但那是**无迟滞**档＝迟滞对照跑两臂同形⇒红；
    ③同序列＋不同表且是迟滞档（off 配对）＝合法，上下文照出。"""
    idx, five, entry = _ctx_entry()
    entry["arms"]["params_base"]["levels"] = "series:levels_hysteresis"
    with pytest.raises(ValueError, match="arms_identical_source_and_map"):
        cb.arm_context_for_judge(_ctx_card(), entry, _ctx_base(idx, five))

    idx, five, e2 = _ctx_entry()
    e2["arms"]["params_base"]["level_map"] = {**five, "WARN": 1.0}  # 表不同，但两臂都读无迟滞档
    e2["arms"]["params_open"]["levels"] = "series:levels_no_hysteresis"
    e2["arms"]["params_base"]["levels"] = "series:levels_no_hysteresis"
    with pytest.raises(ValueError, match="arm_levels_same_source"):
        cb.arm_context_for_judge(_ctx_card(), e2, _ctx_base(idx, five))

    idx, five, e3 = _ctx_entry()
    e3["arms"]["params_base"]["levels"] = "series:levels_hysteresis"
    e3["arms"]["params_base"]["level_map"] = {**five, "WARN": 1.0}
    ctx = cb.arm_context_for_judge(_ctx_card(), e3, _ctx_base(idx, five))
    assert ctx is not None and ctx["base_is_no_hysteresis"] is False
    assert ctx["level_source"] == {"open": "levels_hysteresis", "base": "levels_hysteresis"}


def test_arm_context_validates_recovery_ladder_against_card_face():
    """正证＋四面红线（07b implementation_gap ②＝文字柱 reset_not_full_reentry 的机判面）。

    阶梯 cap 逐字取自卡面 recovery_ladder，本层只查"册格表==卡面表"与卡面自报的形状
    （严格递增、首档<1.0）；查不过即抛不出分——复位即回满会让本卡退化成只判回撤一条腿。
    """
    entry, base = _reset_ctx_pair()
    card = _ctx_card(ladder={"step_0": 0.25, "step_1": 0.5, "step_2": 0.75})
    ctx = cb.arm_context_for_judge(card, entry, base)
    assert ctx["recovery_ladder"]["open"] == {
        "rung_caps": [0.25, 0.5, 0.75],
        "strictly_increasing": True,
        "first_rung_below_full": True,
    }
    # 基臂与开臂同表时也放行，但凭据面写的是"从哪张卡面表落下"，不是"递增通过"
    assert ctx["recovery_ladder"]["base"]["rung_caps"] == [0.25, 0.5, 0.75]
    assert ctx["recovery_ladder"]["base"]["declined_from"].startswith("recovery_ladder")
    with pytest.raises(RuntimeError, match="recovery_ladder_face_missing"):
        cb.arm_context_for_judge(_ctx_card(), entry, base)  # 卡面没冻结阶梯表＝不开考
    e2 = copy.deepcopy(entry)
    e2["arms"]["params_base"]["level_map"].pop("RECOVERY@2")
    with pytest.raises(RuntimeError, match="recovery_rung_cap_unfrozen"):
        cb.arm_context_for_judge(card, e2, base)  # 跑到位次再替卡面拍值的形态
    e3 = copy.deepcopy(entry)
    e3["arms"]["params_open"]["level_map"]["RECOVERY@0"] = 0.5
    with pytest.raises(RuntimeError, match="recovery_rung_cap_off_card_face"):
        cb.arm_context_for_judge(card, e3, base)  # 册格与卡面不同源
    bad_card = _ctx_card(ladder={"step_0": 1.0, "step_1": 1.0, "step_2": 1.0})
    e4 = copy.deepcopy(entry)
    for side in ("open", "base"):
        e4["arms"][f"params_{side}"]["level_map"].update({"RECOVERY@0": 1.0, "RECOVERY@1": 1.0, "RECOVERY@2": 1.0})
    with pytest.raises(RuntimeError, match="reset_not_full_reentry_violated"):
        cb.arm_context_for_judge(bad_card, e4, base)  # 开臂复位即回满＝与关臂同形


def test_arms_path_target_is_base_daily_return_not_index(tmp_path, monkeypatch):
    """⚑零 CH 预演暴露的 r 位覆盖 bug（钉"双臂跑的 target 必须是底座日收益"）。

    `run_one` 里 `tgt = index_next_day_return()` 那行早于双臂接线（10-10 落），双臂分支算出的
    底座日收益被它**无条件覆盖**成 CSI300 指数面 ⇒ 判官量的是"敞口×指数次日收益"（择时面），
    而卡面声明的是"三臂共用同一基线净值路径"（风控面）。`require_target_identity` 验完就丢，
    正是它要防的那颗雷。
    钉法两道：①把 `index_next_day_return` 换成"一调用就抛"的哨兵——实现若回退成无条件覆盖，
    测试先炸在哨兵上（静默换面最坏）；②间谍接住 `run_card` 收到的 target，逐值等于底座日收益。
    """
    mod = cb._arm_protocol_module()
    idx = pd.bdate_range("2024-01-02", periods=24)
    base_ret = pd.Series([0.004, -0.003] * 12, index=idx)
    fake = mod.ArmBase(
        exposure=pd.Series(1.0, index=idx),
        daily_return=base_ret,
        series={
            "levels_hysteresis": pd.Series(["NORMAL"] * 12 + ["CRISIS"] * 12, index=idx),
            "levels_no_hysteresis": pd.Series(["WARN"] * 24, index=idx),
        },
        face_id="exit_sim_baseline_nav",
    )
    fake.level_creds = {"probe": True}
    monkeypatch.setitem(cb.ARM_BASE_SOURCES, "exit_sim_baseline", lambda card, entry: fake)

    def _sentinel():
        raise AssertionError("双臂跑不许取外部指数面（r 位须＝底座日收益）")

    monkeypatch.setattr(cb, "index_next_day_return", _sentinel)
    captured: dict = {}

    def _spy(card_path, **kw):
        captured.update(kw)
        return {"verdict": "pass", "metrics": {}, "card_id": "spy"}

    import fexam.calibration_exam as ce

    monkeypatch.setattr(ce, "run_card", _spy)

    five = {"NORMAL": 1.0, "WARN": 0.8, "DANGER": 0.5, "CRISIS": 0.3, "KILL": 0.0}
    cid = "TDM-X-R1-01/comparison/probe_r_face"
    card = {
        "card_id": cid,
        "status": "preregistered",
        "signal_kind": "series",
        "family": "comparison",
        "data_binding": {
            "signal_table": "c1_market.kline_daily_hfq",
            "arm_protocol": "三臂输入同一基线净值序列与同一成交口径",
            "signal_column": "基线臂日净值（simulate(stop_enabled=True) 产出）",
        },
        "pillars": {"paired_arm_protocol": "三臂共用同一底层组合净值路径"},
    }
    f = tmp_path / "card.yaml"
    f.write_text(yaml.safe_dump(card, allow_unicode=True, sort_keys=False), encoding="utf-8")
    entry = {
        "card_id": cid,
        "status": "approved",
        "op": "arms",
        "arm_base_source": "exit_sim_baseline",
        "arms": {
            "e_face_quote": "三臂输入同一基线净值序列与同一成交口径",
            "r_face_quote": "基线臂日净值（simulate(stop_enabled=True) 产出）",
            "op_open": "arm_level_cap_multiply",
            "op_base": "arm_level_cap_multiply",
            "quote_open": "三臂输入同一基线净值序列与同一成交口径",
            "quote_base": "三臂输入同一基线净值序列与同一成交口径",
            "params_open": {"levels": "series:levels_hysteresis", "level_map": five},
            "params_base": {"levels": "series:levels_no_hysteresis", "level_map": five},
        },
    }
    res = cb.run_one(f, {cid}, tmp_path / "scores.yaml", "probe", False, {cid: entry}, False)
    assert res.get("verdict") == "pass", res
    tgt = captured["target"]
    assert float(tgt.iloc[0]) == 0.004 and len(tgt) == len(base_ret), tgt.head()
    assert captured["signal"] is not None and captured["signal_b"] is not None
    assert captured["arm_context"]["base_is_no_hysteresis"] is True, captured["arm_context"]


def test_ladder_caps_must_be_numeric_not_silently_coerced():
    """红队四形态：None/布尔/带引号的数字/缺键，全部要**具名**红。

    来历：2026-10-13 红蓝对抗实测里 `float(None)` 抛的是 TypeError——那会把"卡面没给档位数值"
    洗成"调用面写错了"（同族错在 pack 参数上已修过一次，这里是同一课的第二遍，所以钉成测试）。
    带引号的 "0.25" 也不许静默 coerce：阶梯 cap 是卡面冻结数值，写成文字就是没冻结。
    """
    entry, base = _reset_ctx_pair()
    card = _ctx_card(ladder={"step_0": 0.25, "step_1": 0.5, "step_2": 0.75})
    cases = {
        "recovery_rung_cap_not_numeric": {"RECOVERY@1": None},
        "recovery_rung_cap_not_numeric_bool": {"RECOVERY@0": True},
        "recovery_rung_cap_not_numeric_str": {"RECOVERY@2": "0.75"},
        "recovery_rung_cap_unfrozen": {"RECOVERY@2": "__drop__"},
    }
    for expect, mutate in cases.items():
        e = copy.deepcopy(entry)
        for lbl, val in mutate.items():
            if val == "__drop__":
                e["arms"]["params_open"]["level_map"].pop(lbl)
            else:
                e["arms"]["params_open"]["level_map"][lbl] = val
        code = expect.split("_bool")[0].split("_str")[0]
        with pytest.raises(RuntimeError, match=code):
            cb.arm_context_for_judge(card, e, base)


def test_level_tier_registry_is_single_source_for_names_and_flags():
    """档位册自证：四档齐、属性逐档申报、名字面由册派生（禁 tuple 与 dict 两处各写一遍）。"""
    assert sorted(cb.DRAWDOWN_LEVEL_TIERS) == sorted(cb.DRAWDOWN_LEVEL_SERIES_NAMES)
    assert cb.DRAWDOWN_LEVEL_TIERS["levels_no_hysteresis_with_reset"] == {"hysteresis": False, "reset": True}
    assert cb.DRAWDOWN_LEVEL_TIERS["levels_with_reset"]["reset"] is True
    assert cb.DRAWDOWN_LEVEL_TIERS["levels_hysteresis"] == {"hysteresis": True, "reset": False}
    assert cb._RECOVERY_RUNG_LABELS == ("RECOVERY@0", "RECOVERY@1", "RECOVERY@2")
    assert cb._RECOVERY_RUNG_CARD_KEYS == ("step_0", "step_1", "step_2")


def test_load_binding_book_variant_vocabularies_are_per_card(tmp_path):
    """⚑2026-10-13 实测误杀的正证：一册多卡、变体词表**按卡冻结**时必须能各自选档。

    旧语义拿"每一张双臂格都得含这一档"当判据 ⇒ 07（off/mid）与 07b（off_A/off_B/mid_A/mid_B）
    共用一本册后，跑 07b 的 off_A 会被 07 那格弹死，而修 07 的 off 跑又会被 07b 那格弹死——
    四跑与 07 重读全都开不出来。新语义两条都没放松：档名在全册并集里找不到＝打字错必红；
    找得到而某卡词表不含它＝该卡不参与本跑（跳过，绝不降级成单臂）。
    """
    body = {
        "entries": [
            {
                "card_id": "CID_07",
                "status": "approved",
                "arms_variants": {
                    "off": {"op_open": "arm_identity", "op_base": "arm_identity"},
                    "mid": {"op_open": "arm_identity", "op_base": "arm_identity"},
                },
            },
            {
                "card_id": "CID_07B",
                "status": "approved",
                "arms_variants": {
                    "off_A": {"op_open": "arm_identity", "op_base": "arm_identity"},
                    "mid_B": {"op_open": "arm_identity", "op_base": "arm_identity"},
                },
            },
        ]
    }
    f = tmp_path / "book.yaml"
    f.write_text(yaml.safe_dump(body, allow_unicode=True), encoding="utf-8")
    assert sorted(cb.load_binding_book(f, arms_variant="off_A")) == ["CID_07B"]
    assert sorted(cb.load_binding_book(f, arms_variant="off")) == ["CID_07"]
    with pytest.raises(ValueError, match="arms_variant_typo"):
        cb.load_binding_book(f, arms_variant="off_C")
    with pytest.raises(ValueError, match="arms_variant_required"):  # 禁默认第一档这条一字未松
        cb.load_binding_book(f)


def test_named_series_tiers_and_bracket_injection_are_fail_closed():
    """红证组（07b ③＝参数由册逐跑给，禁硬编也禁"没用上就算了"）：五种错配各红一次。"""
    two = {
        "arms": {
            "params_open": {"levels": "series:levels_hysteresis"},
            "params_base": {"levels": "series:levels_no_hysteresis"},
        }
    }
    assert cb._named_series_tiers(two) == ["levels_hysteresis", "levels_no_hysteresis"]
    assert cb._reset_entry_param(two, cb._named_series_tiers(two)) is None
    reset = {
        "arms": {
            "params_open": {"levels": "series:levels_with_reset"},
            "params_base": {"levels": "series:levels_with_reset"},
        }
    }
    with pytest.raises(RuntimeError, match="reset_bracket_not_injected"):
        cb._reset_entry_param(reset, cb._named_series_tiers(reset))  # 括号没冻结
    stray = {"arms": {**two["arms"], "reset_trigger_recovered_pct": 0.75}}
    with pytest.raises(RuntimeError, match="reset_bracket_unused"):
        cb._reset_entry_param(stray, cb._named_series_tiers(stray))  # 两跑之间动了别的参数
    ghost = {
        "arms": {
            "params_open": {"levels": "series:levels_with_reset_v2"},
            "params_base": {"levels": "series:levels_hysteresis"},
        }
    }
    with pytest.raises(RuntimeError, match="series_tier_unknown"):
        cb._named_series_tiers(ghost)  # 册格先点名、代码后补＝红
    with pytest.raises(RuntimeError, match="arms_levels_not_named_by_book"):
        cb._named_series_tiers({"arms": {"params_open": {}, "params_base": {}}})  # 禁替册格选档


def test_non_reset_tier_face_unchanged_by_reset_wiring():
    """⚑07 读数面不漂钉：无复位档的标签序列必须与"直接在册件上裸跑 evaluate"逐日相等。
    本袋给判官多喂了 recovered_pct、给 config 加了档位分支——这两处一旦动了 07 的读数即红。"""
    from zephyr.risk.core.drawdown_state_machine import DrawdownStateMachine, DrawdownStateMachineConfig

    nav = _crash_then_climb_nav()
    s = pd.Series(nav).astype("float64").sort_index()
    dd = (s / s.cummax()) - 1.0
    cfgs = {
        "levels_hysteresis": DrawdownStateMachineConfig(),
        "levels_no_hysteresis": DrawdownStateMachineConfig(
            hysteresis_ratio=1.0 - 1e-9,
            sustained_warn=1,
            sustained_danger=1,
            sustained_crisis=1,
            min_hold_warn=1,
            min_hold_danger=1,
            min_hold_crisis=1,
        ),
    }
    for name, cfg in cfgs.items():
        sm = DrawdownStateMachine(None, cfg)
        ref = []
        for ts, d in dd.items():
            sm.evaluate(trade_date=ts.date(), drawdown_pct=float(d))
            ref.append(sm.current.value)
        assert list(cb.replay_drawdown_levels(nav, arm_cfg=name)[0]) == ref, name


def test_pack_mixed_reset_and_non_reset_tiers():
    """零 CH 预演暴露的本袋自错：混合 pack（一臂复位＋一臂不复位）曾被"逐档原样递参数"弹死。

    现在钉四件：①混合 pack 出两条等长序列；②非复位那条**没有** RECOVERY 档名（参数没漏给它）；
    ③复位那条凭据带括号值且真放行过；④"整 pack 没有复位档却给参数"仍然是红（没为修 bug 放宽判据）。
    """
    nav = _crash_then_climb_nav()
    series, creds = cb.drawdown_level_series_pack(
        nav, tier_names=["levels_hysteresis", "levels_with_reset"], reset_recovered_pct=0.5
    )
    assert sorted(series) == ["levels_hysteresis", "levels_with_reset"]
    assert len(series["levels_hysteresis"]) == len(series["levels_with_reset"]) == len(nav)
    assert not [x for x in series["levels_hysteresis"].unique() if str(x).startswith("RECOVERY")]
    assert creds["levels_hysteresis"]["vocab"] == list(cb._DRAWDOWN_STATE_VOCAB)
    assert creds["levels_with_reset"]["reset_trigger_recovered_pct"] == 0.5
    assert creds["levels_with_reset"]["resets_granted"] >= 1
    with pytest.raises(RuntimeError, match="reset_param_on_non_reset_tier"):
        cb.drawdown_level_series_pack(nav, tier_names=["levels_hysteresis"], reset_recovered_pct=0.5)
    with pytest.raises(RuntimeError, match="reset_tier_entry_param_missing"):
        cb.drawdown_level_series_pack(nav, tier_names=["levels_hysteresis", "levels_with_reset"])


def test_peak_trough_pairs_match_in_register_tracker():
    """对拍钉：本件的峰/谷更新与在册 `DrawdownTracker` 逐日等值（"镜像"不是自述）。"""
    from datetime import timezone

    from zephyr.risk.core.drawdown_tracker import DrawdownTracker

    nav = _crash_then_climb_nav()
    tr = DrawdownTracker(initial_net_value=float(nav.iloc[0]))
    got = []
    for ts, v in nav.items():
        snap = tr.update(float(v), now=ts.to_pydatetime().replace(tzinfo=timezone.utc))
        got.append((round(snap.peak, 10), round(snap.trough, 10)))
    mine = [(round(p, 10), round(t, 10)) for p, t in cb._peak_trough_pairs(nav)]
    assert mine == got


def test_real_book_carries_07_and_07b_variant_vocabularies():
    """在册真册的同形契约：07 两档＋07b 四档逐跑可装配，档位名/括号值/阶梯表全部过判官上下文。

    读的是**生产路径的在册字节**（只读，零写入），钉的是"册格与码面同形"这条不能靠记忆守的账：
    任何一档装配不出上下文、或括号值漂出 {0.50, 0.75}，本测试即红。
    """
    book_path = Path(__file__).resolve().parents[2] / "docs/_working/mineloop_campaign/02_binding_book.yaml"
    assert book_path.exists(), "绑定册不在册？同形契约无从可核"
    cid_07 = "TDM-X-R1-01/comparison/07_熔断五级梯度减仓对照_五态仓位锚定版"
    cid_07b = "TDM-X-R1-01/comparison/07b_熔断五级梯度减仓对照_复位阶梯锚定版"
    card_07b = yaml.safe_load(
        (
            Path(__file__).resolve().parents[2] / "docs/03_modules/_domain_backtest/exam_cards/exit_flow/X1/"
            "TDM-X-R1-01__comparison__07b_reset_ladder_anchor.yaml"
        ).read_text(encoding="utf-8")
    )
    idx = pd.bdate_range("2024-01-02", periods=8)
    pool = {
        n: pd.Series(["NORMAL", "KILL", "RECOVERY@0", "RECOVERY@1"] * 2, index=idx) for n in cb.DRAWDOWN_LEVEL_TIERS
    }
    mod = cb._arm_protocol_module()
    base = mod.ArmBase(
        exposure=pd.Series(1.0, index=idx),
        daily_return=pd.Series(0.001, index=idx).round(6),
        series=pool,
        face_id="exit_sim_baseline_nav",
    )
    for v, want_cards in (
        ("off", {cid_07}),
        ("mid", {cid_07}),
        ("off_A", {cid_07b}),
        ("off_B", {cid_07b}),
        ("mid_A", {cid_07b}),
        ("mid_B", {cid_07b}),
    ):
        got = cb.load_binding_book(book_path, arms_variant=v)
        assert {k for k in (cid_07, cid_07b) if k in got} == want_cards, (v, sorted(got))
        if v not in ("off", "mid"):
            e = got[cid_07b]
            assert e["arms"]["reset_trigger_recovered_pct"] == (0.5 if v.endswith("_A") else 0.75), v
            ctx = cb.arm_context_for_judge(card_07b, e, base)
            assert ctx is not None and ctx["arms_variant"] == v
            assert ctx["base_is_no_hysteresis"] is v.startswith("mid"), (v, ctx["tier_flags"])
            assert ctx["recovery_ladder"]["open"]["rung_caps"] == [0.25, 0.5, 0.75], v
            # 落地面判官的认腿表达式逐字重放（它写的是 `base_arm_cfg == "levels_no_hysteresis"`）：
            # 复位档若把册名直接交出去，这条等式对 mid 跑恒假 ⇒ 柱一/柱二两跑互推＝零判。
            assert (ctx["base_arm_cfg"] == "levels_no_hysteresis") is v.startswith("mid"), (v, ctx["base_arm_cfg"])
            assert ctx["base_arm_cfg_tier"].endswith("_with_reset") or v in ("off", "mid"), ctx["base_arm_cfg_tier"]
            assert ctx["level_source"]["base"] == ctx["base_arm_cfg_tier"], "真实册名必须另面保留，族名不得顶掉它"


def test_recovered_pct_is_the_in_register_formula_and_saturates_below_one():
    """直调证明＋一条实测结构发现（须随卡披露，不是本件缺陷）。

    在册公式在 dd>=0 时返回 0.0，而 recovered==1.0 要求 nav 恰等于 peak ⇔ dd==0 ⇒
    回升途中 recovered 严格 <1，故阶梯第 2 档→NORMAL 的门槛（recovery_step_recovered[2]=1.0-1e-6）
    在**任何**日频回放面上都不可达：深回撤后的臂会长期停在 RECOVERY@2（cap 0.75），
    要回 NORMAL 只有"回撤加深退级"一条路。读 07b 的敞口面时必须按这条读，禁当成复位失效。
    """
    from zephyr.ex_core.risk_layer_orchestrator import RiskLayerOrchestrator as R

    nav = _crash_then_climb_nav()
    pairs = cb._peak_trough_pairs(nav)
    vals = cb._recovered_pct_values(nav, pairs)
    for i, (v, (p, t)) in enumerate(zip(nav.tolist(), pairs, strict=True)):
        dd = (v - p) / p if p > 0 else 0.0
        assert vals[i] == float(R._recovered_pct(dd, v, p, t)), i
    assert max(vals) < 1.0, "本路径竟触到 1.0＝上面那条结构结论要重查"


def test_replay_bracket_b_resets_fewer_times_than_a():
    """括号敏感性方向钉：入口更严（0.75）⇒ 复位次数不得比 0.50 多，且驻留形状要能差别。
    两档跑出一模一样的数＝括号参数根本没进回放面（那 07b 的四跑就是同一跑跑四遍）。"""
    nav = _crash_then_climb_nav()
    _, a = cb.replay_drawdown_levels(nav, arm_cfg="levels_with_reset", reset_recovered_pct=0.50)
    _, b = cb.replay_drawdown_levels(nav, arm_cfg="levels_with_reset", reset_recovered_pct=0.75)
    assert b["resets_granted"] < a["resets_granted"], (a["resets_granted"], b["resets_granted"])
    assert (a["reset_trigger_recovered_pct"], b["reset_trigger_recovered_pct"]) == (0.5, 0.75)
    assert a["state_days"] != b["state_days"], "两档级别序列逐日全等＝入口参数没改变任何读数"


def test_replay_config_rejects_bracket_param_mismatch():
    """四态错配各红一次：无复位档收到参数／复位档缺参数／入口值越界／档名未登。"""
    nav = _crash_then_climb_nav().head(40)
    with pytest.raises(RuntimeError, match="reset_param_on_non_reset_tier"):
        cb.replay_drawdown_levels(nav, arm_cfg="levels_hysteresis", reset_recovered_pct=0.5)
    with pytest.raises(RuntimeError, match="reset_tier_entry_param_missing"):
        cb.replay_drawdown_levels(nav, arm_cfg="levels_with_reset")
    with pytest.raises(RuntimeError, match="out_of_range"):
        cb.replay_drawdown_levels(nav, arm_cfg="levels_with_reset", reset_recovered_pct=1.5)
    with pytest.raises(RuntimeError, match="arm_cfg_unknown"):
        cb.replay_drawdown_levels(nav, arm_cfg="levels_reset")  # 差一个字也不算档名


def test_replay_non_reset_tiers_never_emit_recovery_labels():
    """07 的两档在词表上仍只有五态：出现 RECOVERY 即红（禁因为加了复位档就顺手放宽旧档）。"""
    nav = _crash_then_climb_nav()
    for name in ("levels_hysteresis", "levels_no_hysteresis"):
        lv, creds = cb.replay_drawdown_levels(nav, arm_cfg=name)
        assert not [x for x in lv.unique() if str(x).startswith("RECOVERY")], (name, sorted(lv.unique()))
        assert creds["vocab"] == list(cb._DRAWDOWN_STATE_VOCAB)


def test_replay_refusals_come_from_in_register_guards():
    """守卫面判别力：括号 A（0.50 入口）在这条路径上会撞在册冷却守卫，拒因须是在册件原文。
    本函数零守卫代码——查的就是"被拒不放行、不重试、不改参数，只计数"。"""
    nav = _crash_then_climb_nav()
    _, creds = cb.replay_drawdown_levels(nav, arm_cfg="levels_with_reset", reset_recovered_pct=0.50)
    assert creds["resets_refused"] >= 1, creds
    joined = " ".join(r["reason"] for r in creds["refusals_first8"])
    assert "RefuseResetError" in joined and "冷却期" in joined, joined[:220]
    assert all({"date", "reason"} <= set(r) for r in creds["refusals_first8"])


def test_replay_reset_tier_uses_in_register_reset_and_ladder():
    """正证：复位档真的经在册件出口离开 KILL，并按在册 RECOVERY 阶梯给出带步号的档名。
    若复位动作是适配器自己写的分支（卡面禁的形态），这里不会看到在册守卫与毕业留痕。"""
    nav = _crash_then_climb_nav()
    plain, plain_creds = cb.replay_drawdown_levels(nav, arm_cfg="levels_hysteresis")
    reset, creds = cb.replay_drawdown_levels(nav, arm_cfg="levels_with_reset", reset_recovered_pct=0.50)
    assert int(plain.eq("KILL").sum()) == plain_creds["state_days"]["KILL"] > int(reset.eq("KILL").sum()), (
        "复位档没把 KILL 驻留日数降下来＝复位路径根本没跑，读数会与 07 同形"
    )
    assert creds["resets_granted"] >= 1 and creds["tier_flags"] == {"hysteresis": True, "reset": True}
    rungs = creds["recovery_rung_days"]
    assert rungs and sum(rungs.values()) >= creds["resets_granted"]
    assert set(rungs) <= set(cb._RECOVERY_RUNG_LABELS), rungs
    assert creds["graduation_face"] == "absent" and creds["graduation_face_skips"] >= 1
    assert creds["ladder_promotions"] >= 1, "进了阶梯却没晋升＝min_hold/冻结面没被走到"


def _card(**kw) -> dict:
    base = {
        "schema_version": "1.0",
        "card_id": "TDM-E-TEST/calibration/02_x",
        "node_id": "TDM-E-TEST",
        "family": "calibration",
        "status": "preregistered",
        "signal_kind": "series",
        "window": {
            "in_sample": ["2020-01-01", "2023-12-31"],
            "oos": ["2024-01-01", "2025-06-30"],
            "regimes": {"bull": "2020-01-01..2021-12-31"},
        },
        "oos_window_ref": ["2024-01-01", "2025-06-30"],
        "buckets": {"type": "quantile_decile", "on": "当日信号值", "min_obs_per_bucket": 60},
        "pillars": {"ic_floor": "IC>=0.02"},
        "pillars_numeric": {
            "mono_spearman_min": 0.6,
            "ic_mean_min": 0.02,
            "ic_ir_min": 0.3,
            "regime_same_sign": True,
            "oos_same_sign": True,
        },
        "target": {"primary": "next_day_index_return（CSI300 次日收益）"},
        "hypothesis": "测试假设",
    }
    base.update(kw)
    return base


def _binding(**kw) -> dict:
    base = {
        "signal_table": "c1_market.kline_index",
        "signal_column": "close",
        "signal_derivation": "收盘水平（示例）",
        "target_source": "next_day_index_return",
        "data_window_evidence": "实测在案",
    }
    base.update(kw)
    return base


def test_missing_data_binding_is_class_U():
    r = cb.classify_card(_card())
    assert r["cls"] == "U" and r["reason"] == "no_data_binding_section"


def test_target_face_not_index_next_day_is_class_C():
    c = _card(data_binding=_binding(target_source="daily_net_returns → NAV → window_metrics"))
    assert cb.classify_card(c)["cls"] == "C"


def test_multi_day_horizon_refused_not_silently_examined():
    c = _card(data_binding=_binding(), target={"primary": "next_20day_sector_return"})
    r = cb.classify_card(c)
    assert r["cls"] == "C" and "horizon" in r["reason"]


def test_panel_deferred_and_unregistered_table_refused():
    p = _card(signal_kind="panel", data_binding=_binding())
    assert cb.classify_card(p)["cls"] == "B"
    t = _card(data_binding=_binding(signal_table="c1_market.technical_indicator"))
    r = cb.classify_card(t)
    assert r["cls"] == "A?" and "table_not_in_recipe_book" in r["reason"]


def test_local_csv_only_binds_on_exact_signal_column(tmp_path, monkeypatch):
    """回归用例：曾把 margin_flow 卡按全文关键词误牵到连板分布序列＝误绑出分形态。"""
    fake = tmp_path / "series"
    fake.mkdir()
    (fake / "streak_distribution.csv").write_text("trade_date,value\n2024-01-02,3\n", encoding="utf-8")
    (fake / "max_streak_height.csv").write_text("trade_date,value\n2024-01-02,3\n", encoding="utf-8")
    monkeypatch.setattr(cb, "SERIES_DIR", fake)
    good = _card(
        data_binding=_binding(
            signal_table="c1_market.limit_up_pool",
            signal_column="max_streak_height",
            signal_derivation="连板最高高度日度序列",
        )
    )
    bad = _card(
        card_id="TDM-E-TEST/calibration/07_margin",
        data_binding=_binding(
            signal_table="c1_market.margin_trading",
            signal_column="margin_balance",
            signal_derivation="余额变化与连板无关，仅文内出现 streak 字样",
        ),
    )
    assert cb.classify_card(good)["cls"] == "D"
    assert cb.classify_card(bad)["cls"] != "D"


def test_binding_book_refuses_prose_quote_absent_from_card():
    """反自造绿：绑定册引句不在卡面原文里即拒绑（算子不得替卡面说话）。"""
    c = _card(data_binding=_binding(signal_derivation="收盘水平（示例）"))
    entry = {"op": "downside_deviation_250_pctile", "prose_quote": "下行半偏差 = sqrt(244", "args": {}}
    with pytest.raises(ValueError, match="prose_quote_not_found_on_card"):
        cb.run_binding_book(c, entry)


def test_binding_book_refuses_unknown_op():
    c = _card(data_binding=_binding())
    with pytest.raises(ValueError, match="op_not_in_ops_book"):
        cb.run_binding_book(c, {"op": "made_up_op", "prose_quote": "收盘水平", "args": {}})


@pytest.mark.parametrize(
    ("stamp", "expect_refused"),
    [
        (dt.datetime(2026, 10, 10, 21, 0), True),
        (dt.datetime(2026, 10, 10, 22, 29), True),
        (dt.datetime(2026, 10, 10, 22, 30), False),
        (dt.datetime(2026, 10, 10, 23, 59), False),
        (dt.datetime(2026, 10, 11, 1, 0), True),
        (dt.datetime(2026, 10, 11, 3, 59), True),
        (dt.datetime(2026, 10, 11, 4, 0), False),
    ],
)
def test_ch_yield_window_clock_gate(stamp, expect_refused):
    got = cb._in_ch_yield_window(stamp)
    assert (got is not None) is expect_refused


def test_norm_handles_positional_protocol_and_null_empty_strings():
    df = pd.DataFrame({"c1": ["2024-01-02", "2024-01-03", "2024-01-03"], "c2": ["1.5", "", "2.5"]})
    s = cb._norm(df, 0, 1)
    assert list(s.index) == [pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-03")]
    assert float(s.iloc[0]) == 1.5 and float(s.iloc[1]) == 2.5  # 同日均值取末版，空串归 NaN 后被 drop


def test_rolling_pctile_warmup_is_nan_and_range_valid():
    s = pd.Series(range(30), index=pd.bdate_range("2024-01-01", periods=30), dtype=float)
    out = cb._rolling_pctile(s, 20)
    assert out.iloc[:19].isna().all()
    assert out.dropna().between(0.0, 1.0).all()


def test_run_one_skips_cards_not_in_approve_list(tmp_path):
    card = _card(data_binding=_binding())
    p = tmp_path / "c.yaml"
    p.write_text(yaml.safe_dump(card, allow_unicode=True), encoding="utf-8")
    r = cb.run_one(p, {"other"}, tmp_path / "scores.yaml", "t", True)
    assert r["skipped"] == "not_in_approve_list"


def test_limit_up_panel_sql_carries_card_frozen_face():
    """SQL 底座必须逐字承载卡 05/06 冻结式（自创口径=替卡面拍数，禁）：
    比值分母=lag(close)、缺前一交易日取哨兵永不判、limit_pct 缺失（无涨跌幅限制）永不判、
    is_lu_{t-1} 由 lag(lu) 给出、溢价截面=avgIf(ret_close, lu_prev=1)、容差走 {tol} 占位。"""
    s = cb.SQL_LIMIT_UP_PANEL
    assert "FINAL" in s
    assert "ifNull(limit_pct, 9.9)" in s
    assert "lagInFrame(k.c, 1, 0)" in s
    assert "if(lag_c > 0" in s
    assert "lagInFrame(lu, 1, 0)" in s
    assert "avgIf(ret_close, lu_prev = 1)" in s
    assert "{tol}" in s


def _panel() -> pd.DataFrame:
    idx = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"])
    return pd.DataFrame(
        {
            "n_lu": [0, 40, 50, 30],
            "n_lu_prev": [0, 0, 40, 25],
            "n_promo": [0, 0, 12, 10],
            "prem_close": [float("nan"), float("nan"), 0.02, 0.03],
            "prem_open": [float("nan"), float("nan"), 0.01, 0.015],
            "n_rows": [100, 200, 300, 400],
        },
        index=idx,
    )


def test_promotion_rate_den_is_prev_board_not_universe():
    """判别力正例：分母=昨板家数 40 ⇒ 12/40=0.30；若误取当日在市家数 300 ⇒ 0.04（涨停占比形）。"""
    rate, ev = cb.promotion_rate_from_panel(_panel(), 20)
    assert rate.loc[pd.Timestamp("2024-01-04")] == pytest.approx(12 / 40)
    assert rate.loc[pd.Timestamp("2024-01-04")] != pytest.approx(12 / 300)
    assert ev["days_below_set_floor"] == 2


def test_set_floor_drops_small_cross_section_and_counts_missing():
    """卡面「|S_{t-1}|<20 的日置 NaN」＋「停牌股不入截面均值并计缺失数」两面都要出数：
    2024-01-05 在架 25 < 在册昨板 50 ⇒ 缺失 25 票·日；分母 <20 的两日必须被剔掉。"""
    ser, ev = cb._apply_set_floor(_panel(), "prem_close", 20)
    assert [str(x.date()) for x in ser.index] == ["2024-01-04", "2024-01-05"]
    assert ev["suspended_missing_symbol_days"] == 25
    assert ev["days_below_set_floor"] == 2
    assert ev["rows_kept"] == 2


@pytest.mark.parametrize(
    ("op", "card_file"),
    [
        (
            "limit_up_premium_close_mean",
            "entry_flow/L1/TDM-E-L1-S3__calibration__05_limit_up_premium_derived.yaml",
        ),
        (
            "promotion_rate_from_limit_panel",
            "entry_flow/L1/TDM-E-L1-S3__calibration__06_promotion_rate_derived.yaml",
        ),
    ],
)
def test_ops_default_quote_is_verbatim_on_the_real_card(op, card_file):
    """反假绿：算子缺省引句必须是真卡 data_binding 原文子串（改引句/改卡面即红）。"""
    path = cb.CARDS_DIR / card_file
    card = yaml.safe_load(path.read_text(encoding="utf-8"))
    q = cb.OPS[op]["quote_key"]
    assert q.replace(" ", "") in cb._card_text(card).replace(" ", "")


def _vocab_cards(tmp_path):
    d = tmp_path / "cards"
    d.mkdir()
    (d / "a.yaml").write_text(
        yaml.safe_dump(
            {
                "card_id": "T-A",
                "family": "calibration",
                "status": "preregistered",
                "signal_kind": "series",
                "pillars_numeric": {"mono_spearman_min": 0.6, "car_t_stat_min": 2.0},
                "pillars": {"lag_profile": "x"},
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    (d / "b.yaml").write_text(
        yaml.safe_dump(
            {
                "card_id": "T-B",
                "family": "comparison",
                "status": "preregistered",
                "signal_kind": "panel",
                "pillars_numeric": {"sharpe_delta_min": 0.1, "mono_spearman_min": 0.6},
            }
        ),
        encoding="utf-8",
    )
    (d / "c.yaml").write_text(
        yaml.safe_dump({"card_id": "T-C", "family": "calibration", "status": "empty"}), encoding="utf-8"
    )
    (d / "e.yaml").write_text(
        yaml.safe_dump(
            {
                "card_id": "T-E",
                "family": "comparison",
                "status": "preregistered",
                "signal_kind": "panel",
                "pillars_numeric": {"sharpe_delta_min": 0.1, "tail_ratio_min": 0.3},
            }
        ),
        encoding="utf-8",
    )
    (d / "not_a_card.md").write_text("x", encoding="utf-8")
    return d


def test_vocab_census_is_machine_generated_and_zero_write(tmp_path):
    """普查件四钉：①按 pillars_route 分侧取词表（a 卡走校准判官→car_t_stat_min 列外）；
    ②裁定①并集词表后，混形卡（b 卡：NAV 柱＋校准柱）走双臂判官且校准柱已在词表内＝不再列越表
    ——这条断言就是"另一侧门柱从此有判官接手"的可执行证明；
    ③两侧都不认的越表柱（e 卡 tail_ratio_min）在双臂判官下仍须点名，证明并集没把闸放宽；
    ④无机判面卡单独计数不编造＋discipline 三面零（阈值/卡件/CH 全 0，普查只列键名不改值）。"""
    out = cb.build_vocab_census(_vocab_cards(tmp_path))
    assert out["card_total"] == 4
    assert out["cards_without_numeric_face"] == 1
    by_id = {r["card_id"]: r for r in out["rows"]}
    assert by_id["T-A"]["keys_outside_route_vocab"] == ["car_t_stat_min"]
    assert by_id["T-A"]["route"] == "series"
    assert by_id["T-A"]["prose_pillar_keys"] == ["lag_profile"]
    assert "T-B" not in by_id
    assert by_id["T-E"]["route"] == "dual_arm"
    assert by_id["T-E"]["keys_outside_route_vocab"] == ["tail_ratio_min"]
    assert out["unique_keys_outside_vocab"] == 2
    assert out["discipline"]["threshold_values_written"] == 0
    assert out["discipline"]["cards_modified"] == 0
    assert out["discipline"]["ch_queries"] == 0


def test_vocab_census_vocab_sources_read_from_core_constants():
    """词表两侧必须直读执行核常量（复制定义=普查与判决漂移，改一处即红）。"""
    from fexam.calibration_exam import _CALIBRATION_JUDGED_KEYS, _UNION_PILLAR_KEYS

    out = cb.build_vocab_census(cb.CARDS_DIR)
    assert set(out["vocab_sources"]["series"]) == set(_CALIBRATION_JUDGED_KEYS)
    assert set(out["vocab_sources"]["dual_arm"]) == set(_UNION_PILLAR_KEYS)


def _fake_csv(monkeypatch, vals, start="2020-01-01"):
    idx = pd.bdate_range(start, periods=len(vals))
    ser = pd.Series(vals, index=idx)
    monkeypatch.setattr(cb, "_load_csv_series", lambda name: ser)
    return ser


def test_event_flag_excludes_warmup_and_is_binary(monkeypatch):
    """滚动分位底座：暖机段（min_periods 未满）必须无读数，不得用前期值冒充事件日；输出只允许 {0,1}。"""
    ser = _fake_csv(monkeypatch, list(range(400)))
    card = {"data_binding": {"signal_column": "x_event_flag"}}
    flag, ev = cb.op_event_flag_rolling_pctile(card, {"base_csv": "x.csv", "pctile_window": 60, "pct_threshold": 0.9})
    assert ev["warmup_dropped_days"] == 59
    assert set(flag.unique()) <= {0.0, 1.0}
    assert ev["n_event_days"] == int((flag > 0).sum()) and ev["n_event_days"] > 0
    assert ev["pit_statement"].startswith("事件判定只用 t 及以前")


def test_event_flag_is_pit_invariant_to_future_values(monkeypatch):
    """判别力正例（反未来函数）：改动 t 之后的基序列取值，t 及之前的事件标记必须一字不变。
    若实现用了全样本分位（用未来定过去门槛），本支必红。"""
    vals = [float(v % 37) for v in range(300)]
    ser = _fake_csv(monkeypatch, vals)
    card = {"data_binding": {"signal_column": "x_event_flag"}}
    args = {"base_csv": "x.csv", "pctile_window": 50, "pct_threshold": 0.8}
    f1, _ = cb.op_event_flag_rolling_pctile(card, args)
    cut = ser.index[180]
    bumped = ser.copy()
    bumped.loc[bumped.index >= cut] = 999.0
    monkeypatch.setattr(cb, "_load_csv_series", lambda name: bumped)
    f2, _ = cb.op_event_flag_rolling_pctile(card, args)
    common = f1.index.intersection(f2.index)
    before = common[common <= cut]
    assert (f1.loc[before] == f2.loc[before]).all(), "未来值改动了过去的事件标记＝全样本分位（事后挪门柱形态）"


def test_event_flag_base_selection_fail_closed():
    """底座二选一硬闸：base_op 与 base_csv 同时给或同时不给 ⇒ 直接拒（禁第三条取数路静默生效）；
    base_op 不在算子册 ⇒ 点名拒（防绑到不存在的算子上冒充分数）。"""
    card = {"data_binding": {"signal_column": "x"}}
    for args in (
        {"pctile_window": 50, "pct_threshold": 0.9},
        {"base_csv": "a.csv", "base_op": "daily_agg_series", "pctile_window": 50, "pct_threshold": 0.9},
    ):
        with pytest.raises(ValueError):
            cb.op_event_flag_rolling_pctile(card, args)
    with pytest.raises(ValueError) as ei:
        cb.op_event_flag_rolling_pctile(card, {"base_op": "no_such_op", "pctile_window": 50, "pct_threshold": 0.9})
    assert "base_op_not_in_ops_book" in str(ei.value)


# ── WO-A1 双臂通道（绑定侧；量纲错必红由真源件 arm_protocol_binding 把关）────
def _arm_card() -> dict:
    return {
        "card_id": "TDM-E-TEST/comparison/09_x",
        "family": "comparison",
        "status": "preregistered",
        "signal_kind": "series",
        "buckets": {"type": "arm_matrix", "on": "关臂=满仓 vs 开臂=三级仓位映射（A 100%/B 60%/C 0%）"},
        "pillars_numeric": {"maxdd_improvement_min": 5.0, "sharpe_delta_min": -0.1, "oos_same_sign": True},
        "data_binding": {
            "signal_derivation": "基线臂日净值序列",
            "target_source": "风控层改写后的净值路径，减仓=按级别比例，现金停放 0 收益",
            "arm_protocol": "三臂输入同一基线净值序列与同一成交口径；级别→仓位映射（A 100%/B 60%/C 0%）冻结于本卡",
        },
    }


def _arm_entry() -> dict:
    idx = pd.date_range("2024-01-02", periods=8, freq="D")
    return {
        "card_id": "TDM-E-TEST/comparison/09_x",
        "op": "arms",
        "arm_base_source": "wired_for_test",
        "arms": {
            "op_open": "arm_level_cap_multiply",
            "op_base": "arm_identity",
            "quote_open": "级别→仓位映射（A 100%/B 60%/C 0%）冻结于本卡",
            "e_face_quote": "级别→仓位映射（A 100%/B 60%/C 0%）冻结于本卡",
            "r_face_quote": "风控层改写后的净值路径，减仓=按级别比例，现金停放 0 收益",
            "params_open": {
                "level_map": {"A": 1.0, "B": 0.6, "C": 0.0},
                "levels": pd.Series(["A", "B", "C", "A", "B", "C", "A", "B"], index=idx),
            },
        },
    }


def _test_base_exposure():
    idx = pd.date_range("2024-01-02", periods=8, freq="D")
    return pd.Series(1.0, index=idx, name="exposure")


def _test_target_returns():
    idx = pd.date_range("2024-01-02", periods=8, freq="D")
    return pd.Series([0.01, -0.02, 0.005, -0.001, 0.02, -0.015, 0.004, -0.006], index=idx, name="r")


def test_arms_from_binding_book_returns_three_faces_and_merges_provenance(monkeypatch):
    """绿正证：册格 arms 面 → 开臂/基臂/日收益三面齐备，凭据并上绑定册字段（零 CH）。"""
    import scripts.backtest.fexam.arm_protocol_binding as apb

    monkeypatch.setattr(apb, "ARM_OPS", dict(apb.ARM_OPS))
    open_arm, base_arm, tgt, ev = cb.arms_from_binding_book(
        _arm_card(), _arm_entry(), base=_test_base_exposure(), target=_test_target_returns()
    )
    assert [round(float(x), 2) for x in open_arm[:3]] == [1.0, 0.6, 0.0]
    assert float(base_arm.iloc[0]) == 1.0
    assert len(tgt) == 8 and float(tgt.min()) < 0  # r 位确实是含负日的收益面
    assert ev["arm_op_open"] == "arm_level_cap_multiply" and ev["arm_op_base"] == "arm_identity"
    assert ev["face_contract"]["r_face_quote"].startswith("风控层改写后的净值路径")


def test_arms_from_binding_book_refuses_return_like_base():
    """红证（假分雷在绑定层仍必红）：把"池组合收益回放"当底座喂进来 ⇒ 拒装配不出分。"""
    import pytest as _pytest

    import scripts.backtest.fexam.arm_protocol_binding as apb

    with _pytest.raises(apb.ArmFaceMismatch, match="not_exposure_face"):
        cb.arms_from_binding_book(_arm_card(), _arm_entry(), base=_test_target_returns(), target=_test_target_returns())


def test_arms_from_binding_book_requires_arms_face():
    """红证：册格没写 arms 面却走双臂入口 ⇒ 直拒（禁按单臂路径冒充双臂出分）。"""
    import pytest as _pytest

    with _pytest.raises(ValueError, match="arms_face_missing"):
        cb.arms_from_binding_book(
            _arm_card(), {"card_id": "x", "op": "arms"}, base=_test_base_exposure(), target=_test_target_returns()
        )


def test_run_one_dual_arm_without_wired_source_errors_instead_of_scoring(tmp_path, monkeypatch):
    """红证：底座来源未接线 ⇒ run_one 如实报错且**不碰 CH**（零取数也不出假分）。"""
    calls = {"n": 0}

    def _boom(*a, **k):
        calls["n"] += 1
        raise AssertionError("底座来源未接线时不得触 CH 取数")

    monkeypatch.setattr(cb, "index_next_day_return", _boom)
    card = _arm_card()
    p = tmp_path / "c.yaml"
    p.write_text(yaml.safe_dump(card, allow_unicode=True), encoding="utf-8")
    r = cb.run_one(
        p,
        {card["card_id"]},
        tmp_path / "scores.yaml",
        "t",
        False,
        book={card["card_id"]: _arm_entry()},
    )
    assert calls["n"] == 0, "未接线就取数＝拿别处底座冒充分母"
    assert str(r.get("error", "")).startswith("arm_base_source_unwired"), r
    assert not (tmp_path / "scores.yaml").exists(), "拒绑路径不得留下分数行"


def test_arm_base_sources_book_only_holds_signed_sources(tmp_path):
    """在册纪律演进袋（原桩"空册是有意"由 0081 明文指定本批重写，两句纪律一条不松）：

    ①册内只准**在册已签认**的来源（统筹批复乙案批 06 卡＋甲链签认；装置返回面另由救援袋落地）；
    ②未列名一律 fail-closed——run_one 走 arm_base_source_unwired 如实报错，
      禁静默降级成单臂、禁在绑定层现编近似序列冒充分母（与 ArmBaseMissing/ArmFaceMismatch 同哲学）。
    有人往这里塞"临时用指数日收益兜底"之类的未签认来源，本用例先红。
    """
    assert set(cb.ARM_BASE_SOURCES) == {"exit_sim_baseline"}, sorted(cb.ARM_BASE_SOURCES)
    src = cb.ARM_BASE_SOURCES["exit_sim_baseline"]
    assert callable(src), type(src).__name__
    # ②的活体判据：未列名来源必须落到拒绑出口，而不是回落到别处取数
    calls = {"n": 0}

    def _boom(*a, **k):
        calls["n"] += 1
        raise AssertionError("未签认来源不得触 CH 取数")

    orig = cb.index_next_day_return
    cb.index_next_day_return = _boom
    try:
        card = _arm_card()
        entry = _arm_entry()
        entry["arm_base_source"] = "bogus_unsigned_source"
        p = tmp_path / "c.yaml"
        p.write_text(yaml.safe_dump(card, allow_unicode=True), encoding="utf-8")
        r = cb.run_one(p, {card["card_id"]}, tmp_path / "scores.yaml", "t", False, book={card["card_id"]: entry})
        assert str(r.get("error", "")).startswith("arm_base_source_unwired"), r
        assert calls["n"] == 0
        assert not (tmp_path / "scores.yaml").exists()
    finally:
        cb.index_next_day_return = orig


def test_wrong_base_identity_is_red_before_sizing_gate(tmp_path):
    """红证"喂错底座必红"（统筹点名的那颗）：底座自报 face_id 与卡面 r 引句所讲的面不符 ⇒ 必抛。

    这条专门防"闸真拦住、测试却认不出"的同名不同类坑：这里**直接用真源件的异常类**，
    从 card_binding 的装配入口打进去，验的是同一条链（两路导入名归一后同一个类对象）。
    """
    from scripts.backtest.fexam.arm_protocol_binding import ArmBase, ArmFaceMismatch

    idx = pd.date_range("2024-01-02", periods=8, freq="D")
    exposure = pd.Series(0.5, index=idx)
    daily_return = pd.Series([0.01, -0.02, 0.015, 0.0, -0.01, 0.02, -0.005, 0.01], index=idx)
    # 身份冒充：形状与量帽都是合格的日收益面，只有 face_id 说漏嘴（喂的是指数收益不是基线组合）
    wrong = ArmBase(exposure=exposure, daily_return=daily_return, series={}, face_id="index_csi300_next_day")
    card = _arm_card()
    entry = _arm_entry()
    with pytest.raises(ArmFaceMismatch, match="target_face_mismatch"):
        cb.arms_from_binding_book(card, entry, base=wrong, target=daily_return)


# ──────────────────────────────────────────────────────────────────────────────
# 级别序列回放适配器（MOD-RK-049 在册件的日频腿）——三颗红证＋四颗正证
# 全部走合成净值，零 CH 零写生产路径（根宪法 §9 条目 6）
# ──────────────────────────────────────────────────────────────────────────────


def _nav(returns: list[float]) -> pd.Series:
    """日收益序列 → 基线日净值（首日 1.0，其后累乘；峰值即 cummax，与卡面口径同形）。"""
    idx = pd.bdate_range("2024-01-02", periods=len(returns) + 1)
    vals: list[float] = []
    v = 1.0
    for r in returns:
        v *= 1.0 + r
        vals.append(v)
    return pd.Series([1.0] + vals, index=idx)


def test_replay_levels_hysteresis_is_slower_than_no_hysteresis():
    """正证：两档确实在**降级时序**上分道——否则 maxdd_improvement_vs_no_hysteresis 门柱吃的是常数 0 差＝假考。"""
    nav = _nav([-0.03, -0.0306, 0.0625] + [0.0] * 12)  # 探到 -6% 进 WARN，次日即完全修复
    lv_h, cr_h = cb.replay_drawdown_levels(nav, arm_cfg="levels_hysteresis")
    lv_n, cr_n = cb.replay_drawdown_levels(nav, arm_cfg="levels_no_hysteresis")
    assert "WARN" in set(lv_h) and "WARN" in set(lv_n), (lv_h.tolist(), lv_n.tolist())
    last_non_normal_h = len(lv_h) - 1 - int((lv_h[::-1] != "NORMAL").to_numpy().argmax())
    last_non_normal_n = len(lv_n) - 1 - int((lv_n[::-1] != "NORMAL").to_numpy().argmax())
    assert last_non_normal_h > last_non_normal_n, (
        f"迟滞档应在册 min_hold 下更晚回满（h={last_non_normal_h} n={last_non_normal_n}）＝"
        "两档同形意味着迟滞带根本没被回放"
    )
    assert cr_h["arm_cfg"] == "levels_hysteresis" and cr_n["arm_cfg"] == "levels_no_hysteresis"
    assert cr_h["state_days"] != cr_n["state_days"], "两档驻留日数全等＝无迟滞档没生效"


def test_replay_levels_deescalates_one_step_per_day_only():
    """正证＋披露锚：无迟滞档仍**不可跳级**（CRISIS→DANGER→WARN→NORMAL 一日一级）。

    这条同时证明两件事：①级别真由在册件产生（手按 5/10/15/25 逐日查表会得到"即日回满"，
    与本断言相反）；②07 卡面 approximations_disclosed 里"逐级降级不可跳级"是可测事实不是免责话术。
    """
    nav = _nav([-0.06, -0.06, -0.06, 0.2039] + [0.0] * 10)  # 最深 -16.9% 进 CRISIS，次日基本修复
    lv, cr = cb.replay_drawdown_levels(nav, arm_cfg="levels_no_hysteresis")
    assert cr["first_kill_date"] is None
    assert lv.iloc[3:7].tolist() == ["CRISIS", "DANGER", "WARN", "NORMAL"], lv.tolist()
    # 第 4 日回撤已小于最轻档触发线（5%）却仍停在 DANGER＝"解除即回满"做不到，只能逐级
    dd4 = float((nav / nav.cummax() - 1.0).iloc[4])
    assert abs(dd4) < 0.05, dd4
    assert str(lv.iloc[4]) == "DANGER", lv.tolist()


def test_replay_levels_kill_is_sticky_and_quantified():
    """红证①（L4 不可解除近似）：净值完全修复后 KILL 仍驻留，且凭据把驻留日数量化出来。

    在册件 KILL 的唯一出口是 request_manual_reset（三项人工确认），回测面不可能触发；
    若将来有人给状态机加了自动复位，本用例的红面（末段仍 KILL）会当场翻红＝披露被钉住。
    """
    nav = _nav([-0.10, -0.10, -0.10, -0.05, 0.30] + [0.0] * 10)  # 最深约 -31% 破 kill_dd，后修复到 -10%
    lv, cr = cb.replay_drawdown_levels(nav, arm_cfg="levels_hysteresis")
    assert cr["first_kill_date"] is not None
    assert str(lv.iloc[-1]) == "KILL", lv.tail(5).tolist()
    assert cr["kill_stuck_days"] > 0, "回撤已回到 25% 阈值内却记 0 驻留日＝近似没被量化"


def test_replay_levels_rejects_empty_and_nan_and_nonpositive_nav():
    """红证②：三类脏净值必须红，禁把"缺失/无数据"伪装成最轻档（NORMAL 全程）。"""
    with pytest.raises(RuntimeError, match="empty_nav"):
        cb.replay_drawdown_levels(pd.Series([], dtype="float64"))
    dirty = pd.Series([1.0, float("nan"), 0.9], index=pd.bdate_range("2024-01-02", periods=3))
    with pytest.raises(RuntimeError, match="has_nan"):
        cb.replay_drawdown_levels(dirty)
    neg = pd.Series([1.0, 0.0, -0.5], index=pd.bdate_range("2024-01-02", periods=3))
    with pytest.raises(RuntimeError, match="nonpositive"):
        cb.replay_drawdown_levels(neg)


def test_replay_levels_rejects_unknown_arm_cfg_and_out_of_vocab_state():
    """红证③：档名白名单＋五态词表外出现即红（禁在适配器里静默扩档给数，含 RECOVERY）。"""
    nav = _nav([-0.03])
    with pytest.raises(RuntimeError, match="arm_cfg_unknown"):
        cb.replay_drawdown_levels(nav, arm_cfg="levels_bogus")
    seen: list[str] = []

    seen: list[str] = []
    import zephyr.risk.core.drawdown_state_machine as dsm

    orig = dsm.DrawdownStateMachine  # 先取原件再换面，否则 spy 自己套自己无限递归

    class _SpyingMachine:
        """把在册件的 current 换成词表外的 RECOVERY，验适配器必红（判定逻辑仍在在册件里）。"""

        def __init__(self, *a, **k) -> None:
            self._real = orig(*a, **k)

        def evaluate(self, **kw):
            return self._real.evaluate(**kw)

        @property
        def current(self):
            from zephyr.risk.core.drawdown_state_machine import DrawdownState

            seen.append("probed")
            return DrawdownState.RECOVERY

        @property
        def position_cap(self):
            return self._real.position_cap

        @property
        def recovery_step(self):
            return self._real.recovery_step

    dsm.DrawdownStateMachine = _SpyingMachine
    try:
        with pytest.raises(RuntimeError, match="state_out_of_vocab"):
            cb.replay_drawdown_levels(nav, arm_cfg="levels_hysteresis")
    finally:
        dsm.DrawdownStateMachine = orig
    assert seen, "间谍机未被调用＝断言测的是空气"


def test_drawdown_level_series_pack_names_match_book_contract():
    """正证：pack 交付的 series 键名＝册格 "series:<档名>" 点名的那几个（册与码面同形）。

    档位册是档名唯一真源，`DRAWDOWN_LEVEL_SERIES_NAMES` 由它派生；pack **无默认全集**——
    默认全产会让复位档悄悄进 07 的每一跑，两卡的读数面从此不可比。
    """
    nav = _nav([-0.04, -0.04])
    two = ["levels_hysteresis", "levels_no_hysteresis"]
    series, creds = cb.drawdown_level_series_pack(nav, tier_names=two)
    assert sorted(series) == two and sorted(creds) == two
    for name, s in series.items():
        assert len(s) == len(nav), name
        assert set(s.unique()) <= set(cb._DRAWDOWN_STATE_VOCAB), (name, s.unique().tolist())
        assert s.index.equals(pd.DatetimeIndex(nav.index).sort_values()), name
    with pytest.raises(TypeError):
        cb.drawdown_level_series_pack(nav)  # 不点名档位＝调用面缺件，禁"默认给你全部"
    with pytest.raises(RuntimeError, match="drawdown_level_arm_cfg_unknown"):
        cb.drawdown_level_series_pack(nav, tier_names=["levels_bogus"])
    with pytest.raises(RuntimeError, match="reset_tier_entry_param_missing"):
        cb.drawdown_level_series_pack(nav, tier_names=["levels_with_reset"])


# ---------- 2026-10-13 挖矿二班：多日标的前向面申报（统筹立项批；只开目标面这一环） ----------
def _agg_card(h: int = 10, **kw) -> dict:
    """聚合 8 卡的卡面形制：r 位=面板等权 h 日前向（_proxy 非指数），表未入配方册。"""
    c = _card(
        target={"primary": f"mkt_fwd{h}_panel_ew_return（面板等权 {h} 日前向收益均值，_proxy 披露非指数）"},
        data_binding=_binding(
            signal_table="c1_market.kline_daily_hfq",
            signal_column="close",
            target_source=f"mkt_fwd{h}=nanmean(y_fwd{h}, axis=1)",
        ),
    )
    c.update(kw)
    return c


def test_forward_face_absent_still_refused_by_index_gate():
    """正对照（缺省语义零改）：不申报的聚合卡照旧死在 target_face_not_index_next_day——
    既有 178 张 preregistered 卡与 5 类拒绑 reason 的分布不受本补丁影响。"""
    r = cb.classify_card(_agg_card(10))
    assert r["cls"] == "C" and r["reason"] == "target_face_not_index_next_day"


def test_declared_forward_face_opens_target_gate_only():
    """申报且自洽 ⇒ 目标面放行，但**数据面照拦**（表未入配方册）——证明本补丁没顺手放宽别的闸。"""
    c = _agg_card(10, target_forward_face="precomputed", target_horizon_days=10)
    r = cb.classify_card(c)
    assert r["cls"] == "A?" and r["reason"].startswith("table_not_in_recipe_book"), r


def test_declared_forward_face_half_or_inconsistent_refused():
    """红证：半申报（只给 horizon）与两处不同值都必须照拦，reason 点名缺陷形态。"""
    half = _agg_card(10, target_horizon_days=10)
    r_half = cb.classify_card(half)
    assert r_half["cls"] == "C" and r_half["reason"].startswith("declared_forward_face_bad_marker"), r_half
    mism = _agg_card(10, target_forward_face="precomputed", target_horizon_days=5)
    r_mis = cb.classify_card(mism)
    assert r_mis["cls"] == "C" and r_mis["reason"] == "declared_forward_face_horizon_mismatch:5vs10", r_mis


def test_other_multi_day_wording_still_horizon_blocked():
    """不弱化：申报面只摘掉自己声明的 mkt_fwd<h> 记号，卡面另有多日措辞（next_5d）仍判 executor_horizon_mismatch。"""
    c = _agg_card(10, target_forward_face="precomputed", target_horizon_days=10)
    c["target"]["primary"] += "；另看 next_5d 表现"
    r = cb.classify_card(c)
    assert r["cls"] == "C" and r["reason"].startswith("executor_horizon_mismatch"), r


def test_load_binding_book_arms_variant_is_fail_closed(tmp_path):
    """配对选择器三红：缺档名/未知档名/两键并存，都必须当场红，禁默认取第一档。

    统筹裁定甲③要求"跑与跑之间禁动其他参数"，这道选择器是它的机械面：
    默认第一档＝静默换命题，与"未接线不出分"同一哲学。
    """
    body = {
        "entries": [
            {
                "card_id": "TDM-E-TEST/comparison/99_variant",
                "status": "approved",
                "arms_variants": {
                    "off": {"op_open": "arm_identity", "op_base": "arm_identity"},
                    "mid": {"op_open": "arm_identity", "op_base": "arm_identity"},
                },
            },
            {
                "card_id": "TDM-E-TEST/comparison/97_plain",
                "status": "approved",
                "arms": {"op_open": "arm_identity", "op_base": "arm_identity"},
            },
        ]
    }
    f = tmp_path / "book.yaml"
    f.write_text(yaml.safe_dump(body, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ValueError, match="arms_variant_required"):
        cb.load_binding_book(f)
    with pytest.raises(ValueError, match="arms_variant_typo"):
        cb.load_binding_book(f, arms_variant="bogus")
    assert (
        cb.load_binding_book(f, arms_variant="mid")["TDM-E-TEST/comparison/99_variant"]["arms_variant_applied"] == "mid"
    )
    # 无 arms_variants 的普通格不受选择器影响（单臂与既有双臂通道行为零变更）
    plain = cb.load_binding_book(f, arms_variant="mid")["TDM-E-TEST/comparison/97_plain"]
    assert plain["arms"]["op_open"] == "arm_identity" and "arms_variant_applied" not in plain


def test_arms_variant_ambiguation_is_red(tmp_path):
    """两键并存（arms 与 arms_variants 同格）＝哪一跑在跑说不清，必红。"""
    body = {
        "entries": [
            {
                "card_id": "X/99",
                "status": "approved",
                "arms": {"op_open": "arm_identity", "op_base": "arm_identity"},
                "arms_variants": {"off": {"op_open": "arm_identity", "op_base": "arm_identity"}},
            }
        ]
    }
    f = tmp_path / "book.yaml"
    f.write_text(yaml.safe_dump(body, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ValueError, match="arms_pairing_ambiguous"):
        cb.load_binding_book(f, arms_variant="off")


def test_arm_protocol_class_identity_is_single_parser():
    """不变量：装配函数与底座来源用的 ArmBase 必须来自**同一个模块对象**。

    同一模块被两个包名各导一次＝同一个类成为两个对象，`isinstance(base, ArmBase)` 判不出
    底座 ⇒ 敞口乘子会拿 ArmBase 去乘（21:5x 合成装配预证实测到 TypeError: ArmBase * float）。
    本支把"两处共用一个解析器"钉成断言，谁再各走各的路径即红。
    """
    mod = cb._arm_protocol_module()
    assert cb._arm_pair_builder().__module__ == mod.__name__
    assert mod.ArmBase.__module__ == mod.__name__


# ──────────────────────────────────────────────────────────────────────────────
# 裁定③（统筹 2026-10-12）：三柱读数的注入上下文由绑定层组装（判官零自取底座）
# ──────────────────────────────────────────────────────────────────────────────


def _ctx_entry(**over):
    idx = pd.bdate_range("2024-01-02", periods=10)
    five = {"NORMAL": 1.0, "WARN": 0.8, "DANGER": 0.5, "CRISIS": 0.3, "KILL": 0.0}
    arms = {
        "op_open": "arm_level_cap_multiply",
        "op_base": "arm_level_cap_multiply",
        "params_open": {"levels": "series:levels_hysteresis", "level_map": five},
        "params_base": {"levels": "series:levels_no_hysteresis", "level_map": five},
    }
    arms.update(over.pop("arms", {}))
    e = {"card_id": "TDM-X-R1-01/comparison/probe", "arms": arms, "arms_variant_applied": "mid"}
    e.update(over)
    return idx, five, e


def _ctx_base(idx, five, drop=None):
    mod = cb._arm_protocol_module()
    series = {
        "levels_hysteresis": pd.Series(["NORMAL"] * 10, index=idx),
        "levels_no_hysteresis": pd.Series(["WARN"] * 10, index=idx),
    }
    if drop:
        series.pop(drop)
    base = mod.ArmBase(
        exposure=pd.Series(1.0, index=idx),
        daily_return=pd.Series(0.001, index=idx).round(6),
        series=series,
        face_id="exit_sim_baseline_nav",
    )
    base.level_creds = {"probe": True}
    return base


def test_arm_context_resolves_named_series_from_base():
    """正证：册格按名点两档级别序列 ⇒ 上下文齐（序列/映射/档名/基臂档/变体/凭据）。"""
    idx, five, entry = _ctx_entry()
    ctx = cb.arm_context_for_judge(_ctx_card(), entry, _ctx_base(idx, five))
    assert ctx is not None
    assert ctx["base_arm_cfg"] == "levels_no_hysteresis" and ctx["arms_variant"] == "mid"
    assert list(ctx["levels"]["open"].unique()) == ["NORMAL"] and len(ctx["levels"]["open"]) == 10
    assert ctx["cap_map"]["open"] == five and ctx["creds"] == {"probe": True}


def test_arm_context_is_none_when_base_has_no_named_series():
    """红证（空转形态）：底座没交命名序列（旧裸 Series 形状）⇒ 返回 None，
    由判官侧显式记败——绝不允许退化成"用敞口序列冒充级别序列"。"""
    idx, five, entry = _ctx_entry()
    base = _ctx_base(idx, five, drop="levels_no_hysteresis")
    assert cb.arm_context_for_judge(_ctx_card(), entry, base) is None
    bare = pd.Series(1.0, index=idx)
    assert cb.arm_context_for_judge(_ctx_card(), entry, bare) is None


def test_arm_context_refuses_unnamed_level_source():
    """红证（第二真源形态）：册格把 levels 写成裸序列或别的字面量（非 "series:<名>"）⇒ None。
    判官不许从"来路不明的序列"上读数——档位来源必须可追到在册回放件。"""
    idx, five, entry = _ctx_entry()
    entry["arms"]["params_open"]["levels"] = pd.Series(["NORMAL"] * 10, index=idx)
    assert cb.arm_context_for_judge(_ctx_card(), entry, _ctx_base(idx, five)) is None
    idx2, five2, entry2 = _ctx_entry()
    entry2["arms"]["params_base"].pop("level_map")
    assert cb.arm_context_for_judge(_ctx_card(), entry2, _ctx_base(idx2, five2)) is None


# ---------- 2026-10-13 挖矿二班：聚合 8 卡走 class D 本地序列路（物化件 agg8-v1） ----------
def test_agg8_declared_names_are_registered_hints():
    """正证：8 卡申报的 derived_series/target_series 全部命中 _CSV_HINTS 精确键（禁靠子串误绑）。

    走查面＝模块自带 CARDS_DIR（有界）。禁写成 `_P(".").rglob("docs/**")`：那会从仓库根
    下穿 .runtime（队列 blobs 2.7 万＋dead 面）与全部嵌套 worktree——主区实测 45s 不返、
    车道秒过，同一件两副耗时面孔，卡住的正是本班落地面复跑（2026-10-13 21:4x 实测）。
    """
    import yaml

    cards = sorted(cb.CARDS_DIR.rglob("*__calibration__4*_agg_*.yaml"))
    assert len(cards) == 8, len(cards)
    for c in cards:
        b = yaml.safe_load(c.read_text(encoding="utf-8"))["data_binding"]
        assert b["derived_series"] in cb._CSV_HINTS, (c.name, b.get("derived_series"))
        assert b["target_series"] in cb._CSV_HINTS, (c.name, b.get("target_series"))


def test_class_d_requires_the_file_and_names_it_when_absent(tmp_path, monkeypatch):
    """红证＋绿证：文件不在 ⇒ cls U 且 reason 点名缺哪枚 CSV；放入后 ⇒ cls D 绑到该文件。"""
    import pandas as _pd

    monkeypatch.setattr(cb, "SERIES_DIR", tmp_path)
    card = _agg_card(10, target_forward_face="precomputed", target_horizon_days=10)
    card["data_binding"] = dict(card["data_binding"], derived_series="lu_count")
    r_absent = cb.classify_card(card)
    assert r_absent["cls"] == "U" and r_absent["reason"] == "series_csv_absent:lu_count.csv", r_absent
    _pd.DataFrame({"value": [1.0, 2.0]}, index=_pd.to_datetime(["2024-01-01", "2024-01-02"])).rename_axis(
        "trade_date"
    ).to_csv(tmp_path / "lu_count.csv")
    r_present = cb.classify_card(card)
    assert r_present["cls"] == "D" and r_present["recipe"] == "local_series_csv", r_present


def test_load_named_series_empty_name_is_none_not_crash():
    """申报位空缺 ⇒ 返回 None 交调用方 fail-closed（禁把空名当有效序列名去拼路径）。"""
    assert cb.load_named_series("") is None
    assert cb.load_named_series(None) is None
