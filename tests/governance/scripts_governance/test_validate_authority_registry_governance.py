# [A_test] module_id: MOD-GOV_validate_authority_registry_governance | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-511 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.governance.test_validate_authority_registry
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
import textwrap
from pathlib import Path
from unittest.mock import patch

from scripts.governance.d5_architecture.validators.validate_authority_registry import (
    AuthorityEntry,
    parse_registry_tables,
    run_validation,
    validate_authority_values,
    validate_duplicate_modules,
    validate_immutable_core_coverage,
    validate_required_fields,
    validate_section_coverage,
)


class TestAuthorityEntry:
    def test_valid_authority_immutable_core(self):
        e = AuthorityEntry(module="L00", authority="Immutable Core", rationale="核心数据")
        assert e.is_valid_authority()

    def test_valid_authority_human_gated(self):
        e = AuthorityEntry(module="L08", authority="Human-Gated", rationale="人机界面")
        assert e.is_valid_authority()

    def test_valid_authority_ai_modifiable(self):
        e = AuthorityEntry(module="L09", authority="AI-Modifiable", rationale="研究辅助")
        assert e.is_valid_authority()

    def test_invalid_authority(self):
        e = AuthorityEntry(module="X00", authority="Unknown", rationale="")
        assert not e.is_valid_authority()

    def test_empty_authority(self):
        e = AuthorityEntry(module="X00", authority="", rationale="")
        assert not e.is_valid_authority()


class TestValidateAuthorityValues:
    def test_all_valid(self):
        entries = [
            AuthorityEntry(module="A", authority="Immutable Core", rationale="r"),
            AuthorityEntry(module="B", authority="Human-Gated", rationale="r"),
            AuthorityEntry(module="C", authority="AI-Modifiable", rationale="r"),
        ]
        assert validate_authority_values(entries) == []

    def test_missing_authority(self):
        entries = [AuthorityEntry(module="A", authority="", rationale="r", section="2.1")]
        errors = validate_authority_values(entries)
        assert len(errors) == 1
        assert "缺少权限标注" in errors[0]

    def test_invalid_authority_value(self):
        entries = [AuthorityEntry(module="A", authority="Super-Admin", rationale="r", section="2.1")]
        errors = validate_authority_values(entries)
        assert len(errors) == 1
        assert "无效权限值" in errors[0]


class TestValidateDuplicateModules:
    def test_no_duplicates(self):
        entries = [
            AuthorityEntry(module="L00", authority="Immutable Core", rationale="r", section="2.1"),
            AuthorityEntry(module="L01", authority="AI-Modifiable", rationale="r", section="2.1"),
        ]
        assert validate_duplicate_modules(entries) == []

    def test_duplicate_found(self):
        entries = [
            AuthorityEntry(module="L00", authority="Immutable Core", rationale="r", section="2.1"),
            AuthorityEntry(module="L00", authority="Human-Gated", rationale="r", section="2.2"),
        ]
        errors = validate_duplicate_modules(entries)
        assert len(errors) == 1
        assert "重复模块" in errors[0]

    def test_case_insensitive_duplicate(self):
        entries = [
            AuthorityEntry(module="L00", authority="Immutable Core", rationale="r", section="2.1"),
            AuthorityEntry(module="l00", authority="Human-Gated", rationale="r", section="2.2"),
        ]
        errors = validate_duplicate_modules(entries)
        assert len(errors) == 1


class TestValidateSectionCoverage:
    def test_all_sections_present(self):
        entries = [
            AuthorityEntry(module="A", authority="Immutable Core", rationale="r", section="2.1"),
            AuthorityEntry(module="B", authority="Human-Gated", rationale="r", section="2.2"),
            AuthorityEntry(module="C", authority="AI-Modifiable", rationale="r", section="2.3"),
        ]
        assert validate_section_coverage(entries) == []

    def test_missing_section(self):
        entries = [
            AuthorityEntry(module="A", authority="Immutable Core", rationale="r", section="2.1"),
        ]
        errors = validate_section_coverage(entries)
        assert len(errors) == 1
        assert "2.2" in errors[0]


class TestValidateRequiredFields:
    def test_immutable_core_without_rationale(self):
        entries = [AuthorityEntry(module="L00", authority="Immutable Core", rationale="", section="2.1")]
        errors = validate_required_fields(entries)
        assert any("缺少判定理由" in e for e in errors)

    def test_ai_modifiable_without_rationale_ok(self):
        entries = [AuthorityEntry(module="L09", authority="AI-Modifiable", rationale="", section="2.1")]
        errors = validate_required_fields(entries)
        assert not any("缺少判定理由" in e for e in errors)

    def test_empty_module_name(self):
        entries = [AuthorityEntry(module="  ", authority="Immutable Core", rationale="r", section="2.1")]
        errors = validate_required_fields(entries)
        assert any("模块名为空" in e for e in errors)


class TestValidateImmutableCoreCoverage:
    def test_sufficient_immutable(self):
        entries = [AuthorityEntry(module=f"L0{i}", authority="Immutable Core", rationale="r") for i in range(6)]
        assert validate_immutable_core_coverage(entries) == []

    def test_insufficient_immutable(self):
        entries = [
            AuthorityEntry(module="L00", authority="Immutable Core", rationale="r"),
            AuthorityEntry(module="L01", authority="AI-Modifiable", rationale="r"),
        ]
        errors = validate_immutable_core_coverage(entries)
        assert len(errors) == 1
        assert "Immutable Core 模块数过少" in errors[0]


class TestParseRegistryTables:
    def test_parse_simple_table(self, tmp_path: Path):
        md = tmp_path / "test_registry.md"
        md.write_text(
            textwrap.dedent("""\
            ---
            module_id: PSP-AI-AUTONOMY-AUTHORITY-001
            ---
            # AI 自治权限注册表

            ### 2.1 业务核心层

            | 模块 | 权限 | 判定理由 |
            |------|------|---------|
            | L00 数据接入 | Immutable Core | 核心数据管道 |
            | L08 人机界面 | Human-Gated | 需人工确认 |
            | L09 研究创新 | AI-Modifiable | AI 辅助研究 |
            """),
            encoding="utf-8",
        )
        entries = parse_registry_tables(md)
        assert len(entries) == 3
        assert entries[0].authority == "Immutable Core"
        assert entries[1].authority == "Human-Gated"
        assert entries[2].authority == "AI-Modifiable"

    def test_parse_empty_file(self, tmp_path: Path):
        md = tmp_path / "empty.md"
        md.write_text("", encoding="utf-8")
        entries = parse_registry_tables(md)
        assert entries == []


class TestRunValidation:
    def test_missing_registry_file(self, tmp_path: Path):
        fake_path = tmp_path / "nonexistent.md"
        with patch(
            "scripts.governance.d5_architecture.validators.validate_authority_registry.REGISTRY_PATH",
            fake_path,
        ):
            errors, count = run_validation()
            assert len(errors) == 1
            assert "不存在" in errors[0]
            assert count == 0

    def test_valid_registry(self, tmp_path: Path):
        md = tmp_path / "valid_registry.md"
        md.write_text(
            textwrap.dedent("""\
            ---
            module_id: PSP-AI-AUTONOMY-AUTHORITY-001
            ---
            # AI 自治权限注册表

            ### 2.1 业务核心层

            | 模块 | 权限 | 判定理由 |
            |------|------|---------|
            | L00 数据接入 | Immutable Core | 核心数据管道 |
            | L01 基础设施 | Immutable Core | 基础设施层 |
            | L02 Alpha因子 | Immutable Core | 因子计算核心 |
            | L03 信号生成 | Human-Gated | 信号需人工复核 |
            | L04 风险管理 | Immutable Core | 风控核心 |
            | L08 人机界面 | Human-Gated | 需人工确认 |

            ### 2.2 平台能力层

            | 模块 | 权限 | 判定理由 |
            |------|------|---------|
            | context-engine | AI-Modifiable | 上下文管理 |
            | gates | Immutable Core | 门禁核心 |

            ### 2.3 Vibe Coding 基础设施

            | 模块 | 权限 | 判定理由 |
            |------|------|---------|
            | M1 扩展 | Human-Gated | 上下文扩展 |
            | M2 统一记忆 | Immutable Core | 记忆核心 |
            """),
            encoding="utf-8",
        )
        with patch(
            "scripts.governance.d5_architecture.validators.validate_authority_registry.REGISTRY_PATH",
            md,
        ):
            errors, count = run_validation()
            assert count >= 8
            assert errors == []
