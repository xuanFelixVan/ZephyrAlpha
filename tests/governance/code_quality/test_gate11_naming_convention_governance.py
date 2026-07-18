# [A_test] module_id: SRC-TST-1890 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-509 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.governance.test_gate11_naming_convention
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
GATE-11 命名规范门禁单测
========================

权威依据：`docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml` v2.0.1 §五

测试组：
- TestN01Uppercase：N-01 文件名大写检测 + 白名单
- TestN02VersionSuffix：N-02 版本号后缀检测 + 技术栈豁免
- TestN03DateSuffix：N-03 日期后缀检测 + LATEST 豁免
- TestN04AdrNestedNumber：N-04 ADR 嵌套编号检测
- TestN05AdrMissingSuffix：N-05 ADR 缺 kebab 尾缀检测
- TestN06ModuleIdScope：N-06 module_id scope 前缀检测
- TestN07AdrIdFilenameMismatch：N-07 module_id 与文件名编号一致性
- TestPathExemption：PATH_EXEMPT_PREFIXES 路径豁免
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts" / "governance" / "d3_metadata"))

from check_naming_convention import (  # noqa: E402
    FILENAME_UPPERCASE_WHITELIST,
    TECH_VERSION_TOKENS,
    check_file,
)


def _rules(violations: list) -> set[str]:
    return {v.rule for v in violations}


class TestN01Uppercase:
    def test_lowercase_passes(self) -> None:
        assert check_file("docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml") == []

    def test_uppercase_detected(self, tmp_path: Path) -> None:
        fake = tmp_path / "Bad-File.md"
        fake.write_text("---\n---\n", encoding="utf-8")
        vs = check_file("Bad-File.md", fake)
        assert "N-01" in _rules(vs)

    def test_readme_whitelisted(self) -> None:
        assert "N-01" not in _rules(check_file("docs/README.md"))

    def test_agents_md_whitelisted(self) -> None:
        assert "N-01" not in _rules(check_file("AGENTS.md"))

    def test_all_whitelist_entries_passthrough(self) -> None:
        for name in FILENAME_UPPERCASE_WHITELIST:
            assert "N-01" not in _rules(check_file(f"docs/{name}")), name


class TestN02VersionSuffix:
    def test_v1_suffix_detected(self) -> None:
        vs = check_file("docs/memo-v1-draft.md")
        assert "N-02" in _rules(vs)

    def test_round_suffix_detected(self) -> None:
        assert "N-02" in _rules(check_file("docs/design-round2.md"))

    def test_iteration_suffix_detected(self) -> None:
        assert "N-02" in _rules(check_file("docs/plan-iteration3.md"))

    def test_pydantic_v2_whitelisted(self) -> None:
        vs = check_file("docs/01_policies_and_standards/governance/architecture/pydantic-v2-usage-guide.md")
        assert "N-02" not in _rules(vs)

    def test_python_v3_whitelisted(self) -> None:
        assert "N-02" not in _rules(check_file("docs/guides/python-v3-migration.md"))

    def test_all_tech_tokens_are_lowercase(self) -> None:
        for tok in TECH_VERSION_TOKENS:
            assert tok == tok.lower(), tok


class TestN03DateSuffix:
    def test_date_suffix_detected(self) -> None:
        assert "N-03" in _rules(check_file("docs/audit-20260421.md"))

    def test_latest_whitelisted(self) -> None:
        assert "N-03" not in _rules(check_file("docs/scan-LATEST.json"))

    def test_iso_date_with_dashes_passes(self) -> None:
        assert "N-03" not in _rules(check_file("docs/audit-2026-04-21.md"))


class TestN04KbgNestedNumber:
    def test_nested_kbg_detected(self) -> None:
        assert "N-04" in _rules(check_file("docs/08_knowledge/kbg-011-013.md"))

    def test_flat_kbg_passes(self) -> None:
        vs = check_file("docs/08_knowledge/kbg-0038-file-as-task-paradigm.md")
        assert "N-04" not in _rules(vs)


class TestN05KbgMissingSuffix:
    def test_missing_suffix_detected(self) -> None:
        assert "N-05" in _rules(check_file("docs/08_knowledge/kbg-0042.md"))

    def test_template_exempt(self) -> None:
        assert "N-05" not in _rules(check_file("docs/08_knowledge/_template.md"))

    def test_with_suffix_passes(self) -> None:
        vs = check_file("docs/08_knowledge/kbg-0042-some-decision.md")
        assert "N-05" not in _rules(vs)


class TestN06ModuleIdScope:
    def test_ea_prefix_detected(self, tmp_path: Path) -> None:
        fake = tmp_path / "doc.md"
        fake.write_text("---\nmodule_id: EA-ARCH-OVERVIEW-001\n---\n", encoding="utf-8")
        assert "N-06" in _rules(check_file("doc.md", fake))

    def test_prod_prefix_detected(self, tmp_path: Path) -> None:
        fake = tmp_path / "doc.md"
        fake.write_text("---\nmodule_id: PROD-FOO-001\n---\n", encoding="utf-8")
        assert "N-06" in _rules(check_file("doc.md", fake))

    def test_view_prefix_legal(self, tmp_path: Path) -> None:
        fake = tmp_path / "doc.md"
        fake.write_text("---\nmodule_id: VIEW-00-OVERVIEW\n---\n", encoding="utf-8")
        assert "N-06" not in _rules(check_file("doc.md", fake))

    def test_kbg_prefix_legal(self, tmp_path: Path) -> None:
        fake = tmp_path / "kbg-0001-something.md"
        fake.write_text("---\nmodule_id: KBG-0001\n---\n", encoding="utf-8")
        assert "N-06" not in _rules(check_file("kbg-0001-something.md", fake))


class TestN07KbgIdFilenameMismatch:
    def test_mismatch_detected(self, tmp_path: Path) -> None:
        fake = tmp_path / "kbg-0005-something.md"
        fake.write_text("---\nmodule_id: KBG-0007\n---\n", encoding="utf-8")
        assert "N-07" in _rules(check_file("kbg-0005-something.md", fake))

    def test_consistent_passes(self, tmp_path: Path) -> None:
        fake = tmp_path / "kbg-0005-something.md"
        fake.write_text("---\nmodule_id: KBG-0005\n---\n", encoding="utf-8")
        assert "N-07" not in _rules(check_file("kbg-0005-something.md", fake))


class TestPathExemption:
    def test_archive_dir_exempt(self) -> None:
        assert check_file("archive/old-2026-04-24/Legacy-Uppercase.md") == []

    def test_reorg_snapshot_exempt(self) -> None:
        assert check_file("_reorg_snapshots/snapshot-stage-A-post/Bad.md") == []

    def test_cache_dir_exempt(self) -> None:
        assert check_file(".ruff_cache/CACHEDIR.TAG") == []

    def test_session_logs_exempt(self) -> None:
        assert check_file("docs/19_development_workspace/session_logs/session-20260422-001.md") == []


class TestIntegration:
    def test_multiple_violations_in_one_file(self, tmp_path: Path) -> None:
        fake = tmp_path / "Bad-Name-v1.md"
        fake.write_text("---\nmodule_id: EA-FOO\n---\n", encoding="utf-8")
        rules = _rules(check_file("Bad-Name-v1.md", fake))
        assert {"N-01", "N-02", "N-06"}.issubset(rules)

    def test_clean_file_zero_violations(self, tmp_path: Path) -> None:
        fake = tmp_path / "kbg-0050-example-decision.md"
        fake.write_text("---\nmodule_id: KBG-0050\n---\n", encoding="utf-8")
        assert check_file("kbg-0050-example-decision.md", fake) == []
