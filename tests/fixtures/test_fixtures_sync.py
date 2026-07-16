# [A_test] module_id: SRC-TST-2299 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] tests.fixtures.test_fixtures_sync
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_fixtures_sync.py — fixtures mock 与真源规则同步校验。

校验内容：
1. 每个 g_trae_XXX_mock.yaml 引用的 applicable_rules 中的规则编号，
   在 docs/01_policies_and_standards/rules/ 下存在对应的 trae_XXX_*.yaml 真源文件。
2. mock 文件名编号（g_trae_003_mock → 003）与真源规则编号（trae_003_*.yaml → 003）一致。

真源：docs/01_policies_and_standards/rules/trae_XXX_*.yaml
派生：tests/fixtures/g_trae_XXX_mock.yaml
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from zephyr.shared.io.paths import REPO_ROOT

FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
RULES_DIR = REPO_ROOT / "docs" / "01_policies_and_standards" / "rules"

_MOCK_PATTERN = re.compile(r"^g_trae_(\d+)_mock\.yaml$")
_RULE_PATTERN = re.compile(r"^trae_(\d+)_.*\.yaml$")


def _collect_mock_files() -> list[Path]:
    """收集所有 g_trae_XXX_mock.yaml 文件。"""
    if not FIXTURES_DIR.exists():
        return []
    return sorted(FIXTURES_DIR.glob("g_trae_*_mock.yaml"))


def _collect_rule_numbers() -> set[str]:
    """收集真源规则编号集合（trae_XXX_*.yaml 中的 XXX）。"""
    if not RULES_DIR.exists():
        return set()
    numbers: set[str] = set()
    for f in RULES_DIR.glob("trae_*_*.yaml"):
        m = _RULE_PATTERN.match(f.name)
        if m:
            numbers.add(m.group(1))
    return numbers


def _extract_rule_refs(mock_path: Path) -> list[str]:
    """从 mock 文件的 applicable_rules 字段提取规则编号（如 TRAE-003 → 003）。"""
    with open(mock_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    refs: list[str] = []
    for ref in data.get("applicable_rules", []) or []:
        # ref 形如 "TRAE-003"，提取数字部分
        m = re.search(r"TRAE-(\d+)", str(ref))
        if m:
            refs.append(m.group(1))
    return refs


class TestFixturesSync:
    """fixtures mock 与真源规则同步校验。"""

    def test_fixtures_dir_exists(self):
        """PASS: fixtures 目录存在。"""
        assert FIXTURES_DIR.exists(), f"fixtures 目录不存在: {FIXTURES_DIR}"

    def test_rules_dir_exists(self):
        """PASS: 真源规则目录存在。"""
        assert RULES_DIR.exists(), f"真源规则目录不存在: {RULES_DIR}"

    def test_mock_files_non_empty(self):
        """PASS: 至少有 1 个 mock 文件（防止 glob 失败误判通过）。"""
        mocks = _collect_mock_files()
        assert len(mocks) > 0, "未找到 g_trae_*_mock.yaml 文件，glob 可能失效"

    def test_mock_filename_matches_rule_number(self):
        """PASS: mock 文件名编号与内部引用规则编号一致（防止编号漂移）。"""
        mocks = _collect_mock_files()
        for mock_path in mocks:
            m = _MOCK_PATTERN.match(mock_path.name)
            assert m, f"mock 文件名不合规: {mock_path.name}"
            file_num = m.group(1)
            rule_refs = _extract_rule_refs(mock_path)
            # mock 文件至少应引用自身编号的规则（g_trae_003_mock 应引用 TRAE-003）
            assert file_num in rule_refs, (
                f"mock 文件 {mock_path.name} 编号 {file_num} 不在 applicable_rules {rule_refs} 中"
            )

    def test_mock_referenced_rules_exist_in_source(self):
        """PASS: mock 引用的所有规则编号在真源 docs/01_policies_and_standards/rules/ 下存在。"""
        mocks = _collect_mock_files()
        rule_numbers = _collect_rule_numbers()
        missing: list[tuple[str, str]] = []
        for mock_path in mocks:
            rule_refs = _extract_rule_refs(mock_path)
            for ref_num in rule_refs:
                if ref_num not in rule_numbers:
                    missing.append((mock_path.name, f"TRAE-{ref_num}"))
        if missing:
            details = "; ".join(f"{m}→{r}" for m, r in missing[:10])
            assert False, f"{len(missing)} 个 mock 引用的规则在真源不存在: {details}"

    def test_no_orphan_mock_files(self):
        """PASS: 每个 mock 文件编号都有对应的真源规则文件（防止 mock 残留）。"""
        mocks = _collect_mock_files()
        rule_numbers = _collect_rule_numbers()
        orphans: list[str] = []
        for mock_path in mocks:
            m = _MOCK_PATTERN.match(mock_path.name)
            if m:
                file_num = m.group(1)
                if file_num not in rule_numbers:
                    orphans.append(mock_path.name)
        if orphans:
            assert False, f"{len(orphans)} 个 orphan mock（真源规则已删除但 mock 残留）: {orphans[:10]}"
