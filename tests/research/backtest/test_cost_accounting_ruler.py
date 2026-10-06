# [MODULE] tests.backtest.test_cost_accounting_ruler
# [DOMAIN] D_BACKTEST
# [TESTS] scripts/backtest/cost_accounting_ruler.py 的红证固化语义
# [TTL] permanent
#   （抽取器：模块常量/类字段/__init__ 默认；bps 单位归一；已知差异锁值；基线外漂移检出。
#     仓库级检查只读零写入；合成件一律 tmp_path，禁写生产路径。）
"""成本口径对账尺测试（C345 前置工程件，2026-09-30）。

覆盖：
  1. 三形态 Decimal 抽取（模块 Assign / 类 AnnAssign / __init__ kw 默认）
  2. 裸数值抽取（考尺冻结常量面）+ bps→小数归一
  3. R1 同值语义与漂移检出（合成 module，tmp_path）
  4. R4 已知差异锁值：动 2.5/10.0 = FAIL（防静默暗改）
  5. 仓库级 run_ruler 只读全绿（红证固化基线，2026-09-30）
"""

from __future__ import annotations

import ast
import textwrap

import pytest

import scripts.backtest.cost_accounting_ruler as ruler
from scripts.backtest.cost_accounting_ruler import (
    EXAM_COMMISSION_BP_BASELINE,
    EXAM_STAMP_BP_BASELINE,
    _extract_class_default,
    _extract_decimal_assigns,
    _extract_init_kwdefault,
    _extract_numeric_assigns,
    _normalize_site,
    _read_exam_constants,
    r4_known_diffs_stable,
    run_ruler,
)

# ---- 1. 抽取器三形态 ----


def test_extract_module_assign_decimal():
    tree = ast.parse(
        textwrap.dedent("""
        COMMISSION_RATE: Final[Decimal] = Decimal("0.0000854")
        OTHER = 3
    """)
    )
    assert _extract_decimal_assigns(tree)["COMMISSION_RATE"] == "0.0000854"
    assert "OTHER" not in _extract_decimal_assigns(tree)


def test_extract_class_field_decimal():
    tree = ast.parse(
        textwrap.dedent("""
        class FeeConfig:
            commission_rate: Decimal = Decimal("0.0000854")
            stamp_duty_rate: Decimal = Decimal("0.0005")
    """)
    )
    assert _extract_class_default(tree, "FeeConfig", "commission_rate") == "0.0000854"
    assert _extract_class_default(tree, "FeeConfig", "stamp_duty_rate") == "0.0005"
    assert _extract_class_default(tree, "FeeConfig", "missing") is None


def test_extract_init_kwdefault_decimal():
    tree = ast.parse(
        textwrap.dedent("""
        class Broker:
            def __init__(
                self,
                initial_cash: Decimal = Decimal("1000000"),
                commission_rate: Decimal = Decimal("0.0000854"),
            ):
                self._cash = initial_cash
    """)
    )
    assert _extract_init_kwdefault(tree, "commission_rate") == "0.0000854"
    assert _extract_init_kwdefault(tree, "initial_cash") == "1000000"
    assert _extract_init_kwdefault(tree, "absent") is None


# ---- 2. 裸数值 + 单位归一 ----


def test_extract_numeric_assigns_exam_constants():
    tree = ast.parse("COMMISSION_BP = 2.5\nSTAMP_BP = 10.0\nSLIPPAGE_BP = 5\nFLAG = True\n")
    got = _extract_numeric_assigns(tree)
    assert got == {"COMMISSION_BP": 2.5, "STAMP_BP": 10.0, "SLIPPAGE_BP": 5.0}  # bool 非数值


def test_normalize_units_decimal_vs_bps():
    assert _normalize_site({"unit": "decimal"}, "0.0000854") == "0.0000854"
    assert _normalize_site({"unit": "bps"}, "0.854") == "0.0000854"
    assert _normalize_site({"unit": "bps"}, "5") == "0.0005"
    assert _normalize_site({"unit": "decimal"}, None) is None


def test_read_exam_constants_real_file():
    c = _read_exam_constants()
    assert c["commission_bp"] == EXAM_COMMISSION_BP_BASELINE
    assert c["stamp_bp"] == EXAM_STAMP_BP_BASELINE
    assert c["slippage_bp"] == 5.0


# ---- 3. R1 漂移检出（合成 module，tmp_path）----


def test_r1_detects_commission_drift(tmp_path, monkeypatch):
    """五处之一费率漂移=FAIL（对账尺核心红证语义）。"""
    good = textwrap.dedent("""
        from decimal import Decimal
        COMMISSION_RATE: Final[Decimal] = Decimal("0.0000854")
    """)
    bad = good.replace("0.0000854", "0.00025")
    f = tmp_path / "matching_logic.py"
    f.write_text(bad, encoding="utf-8")
    monkeypatch.setattr(ruler, "_read_module", lambda rel: ast.parse(f.read_text(encoding="utf-8")))
    rep = ruler.r1_commission_five_sites()
    assert rep["pass"] is False


def test_r1_all_same_value_passes(tmp_path, monkeypatch):
    """合成件含全部三形态（模块常量/类字段/__init__ 默认）⇒ 五处 site 均可取值且同值。"""
    good = textwrap.dedent("""
        from decimal import Decimal
        COMMISSION_RATE: Final[Decimal] = Decimal("0.0000854")

        class FeeSchedule:
            commission_rate_bps: Decimal = Decimal("0.854")

        class FeeConfig:
            commission_rate: Decimal = Decimal("0.0000854")

        class T0CostConfig:
            commission_rate: Decimal = Decimal("0.0000854")

        class Broker:
            def __init__(self, commission_rate: Decimal = Decimal("0.0000854")):
                self._c = commission_rate
    """)
    f = tmp_path / "all_sites.py"
    f.write_text(good, encoding="utf-8")
    monkeypatch.setattr(ruler, "_read_module", lambda rel: ast.parse(f.read_text(encoding="utf-8")))
    rep = ruler.r1_commission_five_sites()
    assert rep["pass"] is True, rep["measured"]


# ---- 4. R4 已知差异锁值 ----


def test_r4_locks_known_diffs(monkeypatch):
    """考尺 2.5bp/10bp=在册红证；数值被静默改动=FAIL。"""
    assert r4_known_diffs_stable()["pass"] is True

    def broken_constants():
        return {"commission_bp": 0.854, "stamp_bp": 10.0, "slippage_bp": 5.0}

    monkeypatch.setattr(ruler, "_read_exam_constants", broken_constants)
    rep = r4_known_diffs_stable()
    assert rep["pass"] is False
    assert rep["drift"]["commission_bp"]["expected"] == EXAM_COMMISSION_BP_BASELINE


# ---- 5. 仓库级只读全量对账 ----


def test_run_ruler_repo_baseline_all_green():
    """2026-09-30 红证固化基线：C345 四件在册=已知，基线外漂移=0 ⇒ ALL_PASS。

    只读（AST 解析+冻结册 YAML 读取），零写入。数值改动未经裁定登记时本测必红——
    这是对账尺存在的意义（C345 数值整改=⚑-2 生效后另波，届时改本基线+裁定登记）。
    """
    report = run_ruler()
    assert report["all_pass"] is True, [c["id"] for c in report["checks"] if not c["pass"]]
    assert len(report["checks"]) == 6
    assert report["checks"][0]["id"] == "R1-commission-five-sites"
