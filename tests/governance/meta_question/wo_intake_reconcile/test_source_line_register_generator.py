# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/chain_piling_campaign/infra_mining/10_intake_gate_design.md | §3 要素1 命中真源（W4 机器可读册）
# [MODULE] tests.governance.meta_question.wo_intake_reconcile.test_source_line_register_generator
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts/governance/meta_question/wo_intake_reconcile/generate_source_line_register.py（importlib 文件装载，仓内 scripts 不可 import 先例同 tests/scripts）
# [CONSUMERS] WO-001① 验收判据（生成器+册+自校验三件套）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 零生产路径写入：全部经 --source/--output 指 tmp_path（宪法 §9.6 测试隔离）
# [MODIFY-GUARD] none
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败=测试红
# [TESTS] 本件即测试
# [TTL] permanent
"""W4 源线谱机器可读册生成器自校验红蓝测试（WO-001①）。

红腿不是装饰：删线/改档位/伪造 md 自陈条数/盘上漂移四类必红，才是"计数经生成器不由人写"
与"静态清单禁手工维护"两条铁律的机械牙齿。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
_SPEC = importlib.util.spec_from_file_location(
    "generate_source_line_register",
    REPO_ROOT / "scripts" / "governance" / "meta_question" / "wo_intake_reconcile" / "generate_source_line_register.py",
)
gen = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
sys.modules[_SPEC.name] = gen  # dataclass 装配需模块在 sys.modules（tests/scripts 先例同因）
_SPEC.loader.exec_module(gen)

MD = gen.SOURCE_MD.read_text(encoding="utf-8")


def _doc() -> dict:
    return gen.build_document(MD, generated_at="2026-09-24T00:00:00+00:00")


# ---------------------------------------------------------------------------
# 蓝腿：真源 md 全过 + 册面事实
# ---------------------------------------------------------------------------


def test_real_md_self_check_is_clean() -> None:
    assert gen.self_check(MD, _doc()) == []


def test_counts_come_from_md_not_literals() -> None:
    doc = _doc()
    rows = gen.parse_summary_table(MD)
    assert doc["counts"]["lines"] == len(rows) == len(doc["lines"])
    for tier in ("A", "B", "C"):
        claimed = int(next(iter(m.group(2) for m in gen._TIER_CLAIM_RE.finditer(MD) if m.group(1) == tier)))
        assert doc["counts"][f"tier_{tier}"] == claimed


def test_every_line_keeps_verbatim_u_fields() -> None:
    sections = gen.parse_detail_sections(MD)
    for entry in _doc()["lines"]:
        source_fields = sections[entry["line_id"]]["fields"]
        assert entry["u_fields"]["U1"] == source_fields["U1"]
        assert entry["detail_name"] == sections[entry["line_id"]]["name"]


def test_a_tier_carries_ds_anchors_and_b_tier_carries_channels() -> None:
    doc = _doc()
    assert all(e["ds_anchors"] for e in doc["lines"] if e["tier"] == "A")
    assert all("渠道" in e["u_fields"] for e in doc["lines"] if e["tier"] == "B")


def test_c_tier_marked_not_expansion_eligible() -> None:
    doc = _doc()
    assert [e["expansion_eligible"] for e in doc["lines"] if e["tier"] == "C"] == [False] * 3


# ---------------------------------------------------------------------------
# 红腿：四类漂移必判红
# ---------------------------------------------------------------------------


def test_red_deleted_line_breaks_count_and_pairing() -> None:
    mutated = MD.replace("### SL-A16｜投入产出线（A）", "### SL-A99｜投入产出线（A）", 1)
    findings = gen.self_check(mutated, gen.build_document(mutated, generated_at="x"))
    assert any("SL-A16" in f for f in findings), findings


def test_red_tier_change_breaks_pairing() -> None:
    mutated = MD.replace("| SL-A01 | 日线/分钟行情 | A |", "| SL-A01 | 日线/分钟行情 | B |", 1)
    doc = gen.build_document(mutated, generated_at="x")
    findings = gen.self_check(mutated, doc)
    assert any("档位" in f for f in findings), findings
    assert any("实解析" in f for f in findings), findings


def test_red_forged_claimed_count_breaks_check() -> None:
    mutated = MD.replace("## §1 三档总表（29 条", "## §1 三档总表（31 条", 1)
    findings = gen.self_check(mutated, gen.build_document(mutated, generated_at="x"))
    assert any("自陈" in f for f in findings), findings


def test_red_missing_u_field_breaks_check() -> None:
    mutated = MD.replace("- U6｜IC/分层回测+样本外复考；证伪=领先性样本外消失即退役。", "", 1)
    findings = gen.self_check(mutated, gen.build_document(mutated, generated_at="x"))
    assert any("SL-A01" in f and "U6" in f for f in findings), findings


def test_red_section5_layer_not_in_u5() -> None:
    mutated = MD.replace(
        "| 1 | SL-A01 日线/分钟行情 | A | L3/L4/L5 |", "| 1 | SL-A01 日线/分钟行情 | A | L3/L4/L6 |", 1
    )
    findings = gen.self_check(mutated, gen.build_document(mutated, generated_at="x"))
    assert any("挂接层" in f for f in findings), findings


# ---------------------------------------------------------------------------
# CLI：零生产写入 + 漂移检测
# ---------------------------------------------------------------------------


def test_cli_check_mode_passes_on_landed_register(tmp_path: Path) -> None:
    out = tmp_path / "register.yaml"
    assert gen.main(["--output", str(out)]) == gen.EXIT_OK
    assert out.exists()
    assert yaml.safe_load(out.read_text(encoding="utf-8"))["counts"]["lines"] == len(gen.parse_summary_table(MD))


def test_cli_check_detects_disk_drift(tmp_path: Path) -> None:
    out = tmp_path / "register.yaml"
    assert gen.main(["--output", str(out)]) == gen.EXIT_OK
    doc = yaml.safe_load(out.read_text(encoding="utf-8"))
    doc["lines"] = [e for e in doc["lines"] if e["line_id"] != "SL-A01"]
    doc["counts"]["lines"] = len(doc["lines"])
    out.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    assert gen.main(["--check", "--output", str(out)]) == gen.EXIT_DRIFT


def test_cli_missing_source_fails_closed(tmp_path: Path) -> None:
    assert gen.main(["--source", str(tmp_path / "nope.md"), "--output", str(tmp_path / "o.yaml")]) == gen.EXIT_ERROR
