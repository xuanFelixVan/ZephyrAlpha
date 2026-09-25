# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_heritage
# [MODULE] tests.ai_layer.heritage.test_heritage_digest
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.ai_layer.gen_heritage_human_digest（importlib 装载）
# [CONSUMERS] pytest tests/ai_layer/heritage/test_heritage_digest.py
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] build_digest_text 纯函数面（冻结态可见/plain_zh 空拒出）；写盘与前言链走 tmp_path 注入，
#              禁写生产 digests 目录
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L7_heredity/DESIGN.md §2.7
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] plain_zh 空→ValueError 断言；断言失败即红
# [TESTS] tests/ai_layer/heritage/test_heritage_digest.py
# [TTL] permanent
"""test_heritage_digest - 坑集月报生成器验收（DESIGN 施工项 8）。"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]


def _load_gen():
    spec = importlib.util.spec_from_file_location(
        "gen_heritage_digest_under_test", REPO / "scripts" / "ai_layer" / "gen_heritage_human_digest.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


DEFECT_ROW = {
    "entry_id": "HT-20260923-001",
    "plain_zh": "工单收尾路径参数写错导致改动落错目录，登记签名与配方防再犯",
    "source_ref": "WO-20260917-001",
    "pattern_norm": "pathspec_semantic_mixup",
    "recipe": "改关键字传参+补 smoke",
    "occurrence_count": 2,
    "last_seen": "2026-09-23T00:00:00+00:00",
}
KPI_ROW = {
    "month": "2026-09",
    "entries_new": 3,
    "hits_recorded": 7,
    "demoted": 1,
    "l7_prior_share": None,
    "coverage_pct": 62.5,
    "prior_frozen": False,
}


def test_digest_text_contains_freeze_and_sections() -> None:
    gen = _load_gen()
    text = gen.build_digest_text("2026-09", [DEFECT_ROW], [KPI_ROW], 62.5, None, None, False, "healthy")
    assert "# 传承段坑集月报（2026-09）" in text
    assert "## 冻结状态" in text and "正常" in text, "prior 冻结状态可见"
    assert "## 坑集（active 缺陷模式）" in text and DEFECT_ROW["plain_zh"] in text
    assert "coverage_now: 62.5" in text, "前言覆盖率链（供下月连续下降判据）"
    assert "| 2026-09 | 3 | 7 | 1 |" in text


def test_digest_text_frozen_state_visible() -> None:
    gen = _load_gen()
    text = gen.build_digest_text("2026-09", [], [], 55.0, None, None, True, "coverage=55.0<60.0")
    assert "已冻结 1.0" in text and "coverage=55.0<60.0" in text
    assert "快照面为空属正常态" in text, "空坑集=正常态非异常"


def test_digest_rejects_empty_plain_zh() -> None:
    gen = _load_gen()
    bad = dict(DEFECT_ROW, plain_zh="")
    with pytest.raises(ValueError, match="plain_zh_empty"):
        gen.build_digest_text("2026-09", [bad], [KPI_ROW], 62.5, None, None, False, "healthy")


def test_prev_coverage_chain_from_digests(tmp_path: Path) -> None:
    gen = _load_gen()
    (tmp_path / "2026-08.md").write_text("---\ncoverage_now: 61.5\n---\nbody", encoding="utf-8")
    (tmp_path / "2026-07.md").write_text("---\ncoverage_now: 63.0\n---\nbody", encoding="utf-8")
    prev1, prev2 = gen.read_prev_coverages(tmp_path, "2026-09")
    assert (prev1, prev2) == (61.5, 63.0)
    missing = gen.read_prev_coverages(tmp_path, "2025-01")
    assert missing == (None, None), "缺文件=None 正常态（首月无趋势）"


def test_year_boundary_month_math(tmp_path: Path) -> None:
    gen = _load_gen()
    (tmp_path / "2025-12.md").write_text("coverage_now: 70.0", encoding="utf-8")
    prev1, _ = gen.read_prev_coverages(tmp_path, "2026-01")
    assert prev1 == 70.0
