# [A_test] module_id: MOD-TEST_normalize_blueprint_autogen_anchors | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/syncers/normalize_blueprint_autogen_anchors.py | §
# [MODULE] tests.blueprint.test_normalize_blueprint_autogen_anchors
# [INVARIANTS] §0.1 SSoT 失效 AGENTS.md §编号行归一为稳定锚且幂等；AUTOGEN 区外/非 SSoT 语义的 §N 历史引用零误伤；存量蓝图树 AUTOGEN 区无残留失效 SSoT 引用
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/blueprint/test_normalize_blueprint_autogen_anchors.py -q
# [TTL] permanent
"""#移交① 蓝图 AUTOGEN 锚点归一器治本钉（2026-09-16，lane J）。

病根：L0 宪法 2026-09-12 替换后 AGENTS.md §编号失效，40 份既有蓝图 §0.1 AUTOGEN 标记区
残留同款手写行「架构归属SSoT：见 AGENTS.md §7「代码规范」」。本测试钉扎归一器的
正确性（锚定替换/幂等/零误伤）与存量树终态（无残留、门禁通过）。
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

from zephyr.shared.io.paths import REPO_ROOT

SYNCER_PATH = (
    REPO_ROOT
    / "scripts"
    / "governance"
    / "d5_architecture"
    / "syncers"
    / "normalize_blueprint_autogen_anchors.py"
)

STALE_AGENTS_NUMBERED_REF = re.compile(r"AGENTS\.md\s*§\s*\d")

STALE_SSoT_NO_SPACE = "> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）"
STALE_SSoT_WITH_SPACE = "> **架构归属 SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）"

_SECTION = "\n".join(
    [
        "## §0 代码对齐验证",
        "",
        "### §0.1 代码文件清单",
        "",
        "<!-- AUTOGEN: source=depgraph.nodes, generator=extract_depgraph.py, reconciler=blueprint_frontmatter_reconciler.py -->",
        "> **⚠️ 自动化提示**：文件清单真源在 depgraph.nodes 表。",
        "",
        "{ssot}",
        "> **代码头部规范**：`[BLUEPRINT]/[MODULE]` ...",
        "",
        "| # | 文件名 | 职责 | 存在性 |",
        "|---|--------|------|:-----:|",
        "| 1 | foo.py | 主控 | 已实现 |",
        "",
        "### §0.2 对齐验证矩阵",
    ]
)


def _load_normalizer():
    spec = importlib.util.spec_from_file_location("_nbaa_under_test", SYNCER_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def nbaa():
    return _load_normalizer()


class TestNormalizeSsoTLine:
    @pytest.mark.parametrize("stale", [STALE_SSoT_NO_SPACE, STALE_SSoT_WITH_SPACE])
    def test_stale_line_converges_to_stable_anchor(self, nbaa, stale):
        content = _SECTION.format(ssot=stale)
        new_content, changed = nbaa.normalize_content(content)
        assert changed is True
        assert nbaa.SSOT_CANONICAL in new_content
        assert not STALE_AGENTS_NUMBERED_REF.search(new_content), "归一后仍残留失效 §编号引用"
        # 稳定锚在位（不写死 §编号）
        assert "RULE-DEPGRAPH" in new_content and "RULE-SSOT" in new_content

    def test_idempotent_second_pass_no_change(self, nbaa):
        content = _SECTION.format(ssot=STALE_SSoT_NO_SPACE)
        once, changed1 = nbaa.normalize_content(content)
        assert changed1 is True
        twice, changed2 = nbaa.normalize_content(once)
        assert changed2 is False
        assert twice == once

    def test_surrounding_lines_preserved(self, nbaa):
        content = _SECTION.format(ssot=STALE_SSoT_NO_SPACE)
        new_content, _ = nbaa.normalize_content(content)
        assert "| 1 | foo.py | 主控 | 已实现 |" in new_content, "手写表格行被误删"
        assert "### §0.2 对齐验证矩阵" in new_content, "后续章节被吞"
        assert content.count("\n") == new_content.count("\n"), "行数变化（应仅行内替换）"


class TestZeroFalsePositive:
    def test_prose_history_ref_untouched(self, nbaa):
        """历史决策记录里的合法 §N 散文引用（非 SSoT 归属行）不得被归一、不得被门禁标记。"""
        prose = (
            "## §18 决策记录\n\n"
            "- \"AGENTS.md §6.1 data/models/ 目录生命周期\"\n"
            "- 见 AGENTS.md §11.2 实现记录\n"
        )
        new_content, changed = nbaa.normalize_content(prose)
        assert changed is False
        assert nbaa.find_stale_autogen_refs(prose) == [], "散文式历史 §N 引用被误判为病灶"

    def test_non_ssot_line_in_autogen_region_not_flagged(self, nbaa):
        block = (
            "### §0.1 代码文件清单\n\n"
            "<!-- AUTOGEN: generator=extract_depgraph.py -->\n"
            "| `gate.py` | §0.1 | 见 AGENTS.md §11.1.1 |\n"
        )
        # 表格行内 §11.1.1 属门禁/历史描述，非 SSoT 归属语义 → 不归一、不阻断
        _, changed = nbaa.normalize_content(block)
        assert changed is False
        assert nbaa.find_stale_autogen_refs(block) == []


class TestGateDetectionScope:
    def test_stale_ssot_in_autogen_region_detected(self, nbaa):
        content = _SECTION.format(ssot=STALE_SSoT_NO_SPACE)
        hits = nbaa.find_stale_autogen_refs(content)
        assert len(hits) == 1
        lineno, text = hits[0]
        assert "架构归属" in text and "§7" in text

    def test_stale_ssot_outside_autogen_region_not_flagged(self, nbaa):
        # 同一行若脱离 AUTOGEN 标记区（其前最近标题后无 AUTOGEN 标记）→ 不判为回潮
        orphan = (
            "## §99 附录\n\n"
            + STALE_SSoT_NO_SPACE
            + "\n"
        )
        assert nbaa.find_stale_autogen_refs(orphan) == []


class TestLiveTreeConverged:
    """存量终态钉：交付不变量——docs/03_modules 全部蓝图 AUTOGEN 区无残留失效 SSoT 引用。"""

    def test_repo_blueprints_have_no_stale_ssot_refs(self, nbaa):
        offenders = []
        for bp in nbaa._iter_blueprints(REPO_ROOT):
            try:
                content = bp.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            hits = nbaa.find_stale_autogen_refs(content)
            # 归一器幂等：若仍可归一说明残留
            _, changed = nbaa.normalize_content(content)
            if hits or changed:
                offenders.append((str(bp.relative_to(REPO_ROOT)), hits))
        assert offenders == [], f"存量蓝图仍存可归一/可检测失效引用: {offenders[:5]}"

    def test_construction_template_has_no_stale_agents_numbered_ref(self):
        tpl = REPO_ROOT / "docs" / "01_policies_and_standards" / "templates" / "blueprint_construction_template.md"
        text = tpl.read_text(encoding="utf-8")
        assert not STALE_AGENTS_NUMBERED_REF.search(text), "施工模板仍含失效 AGENTS.md §编号引用"


class TestApplyIdempotentOnTemp:
    def test_apply_then_recheck_clean(self, nbaa, tmp_path, monkeypatch):
        mod = tmp_path / "some_module"
        mod.mkdir()
        bp = mod / "blueprint.md"
        bp.write_text(_SECTION.format(ssot=STALE_SSoT_NO_SPACE), encoding="utf-8", newline="\n")

        changed1, residual1 = nbaa._process_blueprint(bp, apply=True)
        assert changed1 is True
        assert residual1 == []
        after = bp.read_text(encoding="utf-8")
        assert nbaa.SSOT_CANONICAL in after

        changed2, residual2 = nbaa._process_blueprint(bp, apply=True)
        assert changed2 is False, "第二遍仍报变更——落盘幂等破坏"
        assert bp.read_text(encoding="utf-8") == after
        assert residual2 == []
