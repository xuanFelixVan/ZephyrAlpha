# [BLUEPRINT] MOD-BT-039 | tests/backtest/test_c4_pit_red_injection.py
# [MODULE] tests.backtest.test_c4_pit_red_injection
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] tests.backtest.test_c4_pit_universal_gate; scripts.backtest.factor_strategy_template
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 红证双向（裁定#325 变性纪律，max_remediation_plan §2-批B 验收）：
#   红侧=把已修破口手工注回（宇宙=旧 valid_to IS NULL 快照口径；权重=拔掉 ≤T-1 平移），
#   PIT 闸/探针不变式必须立刻翻红——闸有牙，不是装饰；
#   蓝侧=修复口径（SCD-2 窗口并集 + shift(1)）同一不变式绿。
#   本件=闸的自检（test-the-test），防 PIT 闸退化成无鉴别力的假绿。
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败->测试失败
# [TESTS] self
# [TTL] permanent
"""批B 红证注入测试（IBT 整改 §2-批B：修后红证=注入前视必红）。

双向纪律（裁定#325 禁"全绿"表述）：
- 红侧：宇宙轴注入旧快照口径 → 双世界 ≤X 宇宙即分歧（PIT 闸判红）；
  权重轴注入同 bar stamping → 探针不变式翻红。
- 蓝侧：修复口径（SCD-2 窗口并集 / ≤T-1 平移）同一不变式绿。
- 引擎层：SQL 常量被注回快照口径 → 考卷路径炸响（fail-closed，禁静默绿）。
不触 CH（全部夹具 mock），不触网。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd
import pytest

_REPO = Path(__file__).resolve().parents[2]

# 复用 PIT 闸夹具（单一真源：双世界构造不复制第二份）
_gate_spec = importlib.util.spec_from_file_location(
    "_c4_pit_gate", Path(__file__).resolve().parent / "test_c4_pit_universal_gate.py"
)
_gate = importlib.util.module_from_spec(_gate_spec)
_gate_spec.loader.exec_module(_gate)

sys.path.insert(0, str(_REPO / "scripts" / "backtest"))

import factor_strategy_template as fst  # noqa: E402 — 依赖区在头之后

_EXIT_MEMBER = _gate._EXIT_MEMBER


# ── 宇宙轴：注入旧快照口径 → 双世界必分歧（红）；修复口径必一致（绿） ─────────


def test_universe_snapshot_injection_leaks_post_x_info():
    """注入=旧快照口径（valid_to IS NULL，S14-1 病根）：≤X 窗宇宙即区分双世界。

    世界 A 的 _EXIT_MEMBER 在 X 后调出（valid_to 非 NULL）→ 快照口径把它剔出
    ≤X 窗宇宙=「用 X 后的信息改写 X 前的决策面」=闸必须判红的注入形态；
    修复口径（SCD-2 窗口并集）双世界一致=绿。双向红证。
    """
    rows_a = _gate._constituent_rows("A")
    rows_b = _gate._constituent_rows("B")
    snap_a = {s for s, _vf, vt in rows_a if vt is None}
    snap_b = {s for s, _vf, vt in rows_b if vt is None}
    # 注入鉴别力：快照口径必须真的区分双世界（否则本红证空转）
    assert snap_a != snap_b, "注入丧失鉴别力：快照口径未区分双世界（夹具失效）"
    assert _EXIT_MEMBER not in snap_a and _EXIT_MEMBER in snap_b
    # 蓝侧：修复口径（窗口并集）双世界 ≤X 宇宙逐位一致
    win_a = {s for s, _vt in _gate._scd2_window_filter(rows_a, "2024-01-01", "2024-03-31")}
    win_b = {s for s, _vt in _gate._scd2_window_filter(rows_b, "2024-01-01", "2024-03-31")}
    assert win_a == win_b, "修复口径在无注入基线下竟不一致=范式退化"
    assert _EXIT_MEMBER in win_a  # 窗内曾是成份即入池（幸存者回池语义钉）


def test_engine_snapshot_sql_injection_fail_closed():
    """引擎层注入：SQL 常量被注回快照口径 → 考卷路径必须炸响，禁止静默绿。

    夹具 fake 对纯快照 SQL 返回 1 元组行，引擎 load_index_constituents 解包
    即 raise——注入形态无法无声通过考卷（fail-closed 语义钉）。
    """
    eng = _gate._load_c4_engine()
    polluted_sql = (
        "SELECT symbol_canonical, valid_to FROM c1_market.index_constituent FINAL "
        "WHERE index_code = '{index_code}' AND valid_to IS NULL"
    )
    orig = eng.SQL_INDEX_CONS_WINDOW
    eng.SQL_INDEX_CONS_WINDOW = polluted_sql
    try:
        with pytest.raises(Exception, match="unpack|values|Exception"):
            _gate._universe_c4_window("B", "2024-01-01", "2024-03-31")
    finally:
        eng.SQL_INDEX_CONS_WINDOW = orig
    # 还原后必须自愈回绿（注入不残留）
    assert _gate._universe_c4_window("A", "2024-01-01", "2024-03-31") == (
        _gate._universe_c4_window("B", "2024-01-01", "2024-03-31")
    )


# ── 权重轴：注入同 bar stamping → 探针不变式必翻红（红）；修复版绿 ───────────

_DATES = pd.bdate_range("2023-03-01", periods=10)
_X = _DATES[5]
_SYMS = ["s1", "s2", "s3", "s4"]


def _feats(x_day_flip: bool) -> pd.DataFrame:
    """与 B1 探针同构夹具：常设排名 s1>s2>s3>s4；X 日 flip 变体改 s4 居首。"""
    rows = []
    for d in _DATES:
        for i, s in enumerate(_SYMS):
            f = (4 - i) * 1.0
            if x_day_flip and d == _X:
                f = 10.0 if s == "s4" else 4 - i
            rows.append((d, s, 10.0, f))
    return pd.DataFrame(rows, columns=["date", "s", "close", "factor"])


def _samebar_assemble(feats: pd.DataFrame, top_n: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """注入变体：忠实复刻 edd503ef 之前的同 bar 形态（无 ≤T-1 平移）。"""
    closes = feats.pivot(index="date", columns="s", values="close").sort_index()
    weights = pd.DataFrame(index=closes.index, columns=closes.columns, dtype=float)
    for d, grp in feats.groupby("date"):
        day = grp.dropna(subset=["factor"]).nlargest(top_n, "factor")["s"]
        if day.empty:
            continue
        weights.loc[d, day] = 1.0 / len(day)
    return weights.fillna(0.0), closes


def _probe_invariant(assemble) -> None:
    """B1 探针不变式：X 日 factor 翻转不得改写 ≤X 权重（不变式红=同 bar 实锤）。"""
    w_a, _ = assemble(_feats(False), top_n=2)
    w_b, _ = assemble(_feats(True), top_n=2)
    assert float(w_a.loc[_X].sum()) > 0 and float(w_b.loc[_X].sum()) > 0, "探针空转"
    assert w_a.loc[:_X].equals(w_b.loc[:_X]), "同 bar 前视：X 日权重被 X 日 factor 改写"


def test_samebar_assemble_injection_probe_invariant_fires_red():
    """注入=拔掉 ≤T-1 平移 → 探针不变式必须翻红；修复版同不变式绿。"""
    with pytest.raises(AssertionError, match="同 bar"):
        _probe_invariant(_samebar_assemble)
    _probe_invariant(fst.assemble_weights)  # 蓝侧：现状修复版绿


# ── 防退化：红证套件成员在位（删探针=藏红，本件拦） ──────────────────────────


def test_red_evidence_suite_membership_pin():
    """S14 建立的探针/闸套件必须整体在位——缺件=防线被拆（本件红）。"""
    tests_dir = Path(__file__).resolve().parent
    required = {
        "test_c4_pit_universal_gate.py": [
            "def test_c4_engine_universe_pit_gate",
            "def test_template_family_weights_pit_axis",
            "def test_affected_list_zero_drift",
        ],
        "test_b1_fact_assemble_samebar_probe.py": [
            "def test_assemble_weights_at_x_must_not_use_day_x_factor",
        ],
        "test_b1_gftd_samebar_probe.py": [
            "def test_gftd_signal_at_x_must_not_use_day_x_bar",
        ],
        "test_b1_cgo_pit_probe.py": [],
    }
    for fname, funcs in required.items():
        text = (tests_dir / fname).read_text(encoding="utf-8")
        for fn in funcs:
            assert fn in text, f"红证套件缺件：{fname}::{fn}"
