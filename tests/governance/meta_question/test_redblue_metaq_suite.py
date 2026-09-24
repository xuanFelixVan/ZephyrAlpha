"""红蓝套件自身的用例——保证四把尺"蓝不误报、红必被抓"可被 pytest 常驻守住。

关键防退化点：豁免位 `ruler:quoting-revoked` 不得成为万能逃生口，
故本文件同时钉住"未标豁免的真伪造必须被抓"与"豁免位使用处必须可枚举"。
"""

from __future__ import annotations

import datetime
import importlib.util
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "scripts" / "governance" / "meta_question" / "redblue_metaq_suite.py"


def _load():
    spec = importlib.util.spec_from_file_location("rb_suite_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


rb = _load()
NOON = datetime.datetime(2026, 9, 24, 16, 30)


def test_r1_catches_live_fabrication_without_marker():
    """编号分支单独钉：假裁定号必须**抓到**，且理由必须是"未登记"而不是搭未来时戳那条腿。"""
    fake = "Owner 裁定" + chr(35) + "9999"  # 组装：字面量会被 REFERENCE-INTEGRITY 门当悬空引用打死整袋
    red = f"threshold: 0.01   # {fake} 变更口径（无时戳）\n"
    findings = rb.ruler_r1_fabricated_authority(red, now=NOON)
    assert any("未见于 ruling_registry" in x for x in findings), f"编号腿失灵：{findings}"


def test_r1_marker_is_only_used_in_adjudication_sections():
    """豁免位使用处必须可枚举且全部落在'记录造假'的审计段里。"""
    used = []
    for p in (REPO / "docs" / "_working" / "meta_question_answers").rglob("*.yaml"):
        txt = p.read_text(encoding="utf-8")
        for ln, line in enumerate(txt.splitlines(), 1):
            if "ruler:quoting-revoked" in line:
                used.append((p.name, ln, line))
    for name, ln, line in used:
        assert "17:35" in line or "终版" in line or "伪造" in line, f"{name}:{ln} 豁免位用在了非引述语境"


def test_r2_rejects_missing_canonical_keys():
    bad = {"conclusion": "c", "evidence": [], "threshold": "t"}
    findings = rb.ruler_r2_conclusion_shape(bad)
    assert any("outcome" in f for f in findings), "缺裁决键必须报"


def test_r2_accepts_full_canonical_blob():
    good = {k: "x" for k in rb.CONCLUSION_CANONICAL_KEYS}
    good.update({"outcome": "pass", "evidence": [], "fail_type": None, "data_window": {}, "three_check": {}})
    assert rb.ruler_r2_conclusion_shape(good) == []


def test_r2_flags_fail_without_fail_type():
    blob = {k: "x" for k in rb.CONCLUSION_CANONICAL_KEYS}
    blob.update({"outcome": "fail", "fail_type": None, "evidence": [], "data_window": {}, "three_check": {}})
    assert any("fail_type" in f for f in rb.ruler_r2_conclusion_shape(blob))


def test_r3_tolerance_is_scale_derived_not_magic():
    tol, scale = rb._decimal_ulp(
        "c1_market.money_flow", ["main_net_inflow", "large_net_inflow", "super_large_net_inflow"]
    )
    assert scale == 2, f"应读到 Decimal(18,2) 的标度，实得 {scale}"
    assert abs(tol - 3 * 10**-scale) < 1e-9, f"容差应为 3ulp，实得 {tol}"


def test_r3_rounding_noise_blue_and_real_break_red():
    tol, _ = rb._decimal_ulp("c1_market.money_flow", ["main_net_inflow", "large_net_inflow", "super_large_net_inflow"])
    assert rb.ruler_r3_caliber_identity([(436.03, 488.27, -52.22)], tol) == []
    assert len(rb.ruler_r3_caliber_identity([(30.0, 20.0, 5.0)], tol)) == 1


def test_r4_detects_dropped_question():
    latest = {f"PQ-{i:04d}": "pass" for i in range(1, 11)}
    assert rb.ruler_r4_tristate_consistency(latest, 10) == []
    latest["PQ-0001"] = ""
    assert rb.ruler_r4_tristate_consistency(latest, 10), "掉桶必须被发现"


def test_every_ruler_self_proves():
    """每把尺都必须自证能红；尺数不硬编码（写死数量=会随加尺而静默漏考）。"""
    results = rb.run_selftests()
    assert len(results) >= 4, f"尺数异常：{len(results)}"
    assert all(ok for _, ok, _ in results), "存在不自证的尺：" + "; ".join(f"{n}:{d}" for n, ok, d in results if not ok)


def test_r5_detects_the_real_repollution_shape():
    """R5 必须能抓住 2026-09-24 实测形态：旧基座在 FINAL 上胜出 + 双写重复键。"""
    okw = [(100, 5210)]
    okc = {"checked": 44240, "mismatch": 0, "worst": 4.3e-05}
    findings = rb.ruler_r5_single_hfq_lineage(
        {"bdpan_hfq": 5210, "recalc_raw_x_adjfactor": 349}, 5265, version_win=okw, continuity=okc
    )
    assert len(findings) == 2, findings
    assert any("重复键" in f for f in findings)
    assert any("非预期口径" in f for f in findings)
    assert rb.ruler_r5_single_hfq_lineage({"recalc_raw_x_adjfactor": 5210}, 0, version_win=okw, continuity=okc) == []


def test_r5_refuses_green_when_probe_is_blind():
    """版本列读不到 / 连续性腿零样本 ⇒ 一律报红。

    这条是防"尺自己瞎了还报绿"：CH 服务端一张表坏掉后所有 system.* 枚举都失败，
    若吞异常继续判，R5 会在看不见版本列与恒等性的情况下给出一个假的通过。
    """
    counts = {"recalc_raw_x_adjfactor": 5210}
    no_ver = rb.ruler_r5_single_hfq_lineage(counts, 0, version_win=None, continuity={"checked": 10, "mismatch": 0})
    assert any("lineage_version" in f for f in no_ver), no_ver
    zero_sample = rb.ruler_r5_single_hfq_lineage(
        counts, 0, version_win=[(100, 5210)], continuity={"checked": 0, "mismatch": 0}
    )
    assert any("零样本" in f for f in zero_sample), zero_sample
    drift = rb.ruler_r5_single_hfq_lineage(
        counts, 0, version_win=[(100, 5210)], continuity={"checked": 1000, "mismatch": 17, "worst": 0.31}
    )
    assert any("非事件日" in f for f in drift), drift


def test_module_header_carries_required_fields():
    txt = SCRIPT.read_text(encoding="utf-8")
    for field in (
        "BLUEPRINT",
        "MODULE",
        "DOMAIN",
        "DEPENDENCIES",
        "CONSUMERS",
        "INVARIANTS",
        "ERROR_CONTRACT",
        "TESTS",
        "TTL",
    ):
        assert f"# [{field}]" in txt, f"缺头部字段 {field}"
