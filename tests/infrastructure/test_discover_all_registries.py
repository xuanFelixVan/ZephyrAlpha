# [A_test] module_id: MOD-GOV_discover_all_registries | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain_infrastructure_operations/asset_inventory/blueprint.md | §
# [MODULE] tests.infrastructure.test_discover_all_registries
# [INVARIANTS] discover_all_registries() 读 ROOR（SSoT）返回全量 REG-* registry；AGENTS.md 不含硬编码计数
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ROOR 缺失/tiers 缺失 → 返回空 list（不抛）
# [TESTS] tests/infrastructure/test_discover_all_registries.py
# [TTL] task_bound
"""#ARCH-REGISTRY-DISCOVERY-SSOT-001 治本测试。

验证：discover_all_registries() 读 ROOR（注册表发现真源）而非 master_index（catalogs 派生缓存），
返回全部 REG-* registry（含 master_index 无法覆盖的 postgresql/code_inline/directory 格式），
且 AGENTS.md RULE-REGISTRY 不再硬编码 stale 计数。
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from zephyr.infrastructure.asset_inventory.registry_adapter import discover_all_registries
from zephyr.shared.io.paths import REPO_ROOT

_ROOR = REPO_ROOT / "docs" / "registry_of_registries.yaml"
_AGENTS = REPO_ROOT / "AGENTS.md"
_MASTER_INDEX = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "registry_master_index.yaml"
)


def _roor_registry_count() -> int:
    data = yaml.safe_load(_ROOR.read_text(encoding="utf-8"))
    return sum(len(t.get("registries", [])) for t in data.get("tiers", []))


class TestDiscoverAllRegistriesReadsROOR:
    """discover_all_registries() 必须读 ROOR（SSoT），返回全量 REG-* registry。"""

    def test_returns_all_roor_entries(self):
        regs = discover_all_registries()
        assert len(regs) == _roor_registry_count()

    def test_entries_are_reg_ids_not_catalogs_module_ids(self):
        """ROOR 用 REG-* 编号；master_index 用 CFG/PS-REG/GOV（catalogs 文件 module_id）。
        若误读 master_index，多数 registry_id 会以 CFG-/GOV- 开头。"""
        regs = discover_all_registries()
        ids = [r.get("registry_id", "") for r in regs]
        # ROOR 全部为 REG-* 编号（含 REG-MOD-*/REG-STD-* 等变体）
        assert all(rid.startswith("REG-") for rid in ids), (
            f"非 REG-* 编号泄露: {[r for r in ids if not r.startswith('REG-')]}"
        )

    def test_includes_non_catalogs_formats(self):
        """ROOR 覆盖 master_index 无法自动提取的格式（postgresql/code_inline/directory）。
        master_index 32/32 physical_path 全在 catalogs/，不可能含这三类。"""
        regs = discover_all_registries()
        formats = {r.get("format", "") for r in regs}
        # postgresql（depgraph/panorama）、code_inline（fixer_map）、directory（capability_cards）
        assert any("postgresql" in f for f in formats), "缺失 postgresql 格式 registry（master_index 无法覆盖）"
        assert any("code_inline" in f for f in formats), "缺失 code_inline 格式 registry"
        assert any("directory" in f for f in formats), "缺失 directory 格式 registry"

    def test_flattens_tiers_and_preserves_metadata(self):
        """flatten tiers → 单一 list，保留 tier_level/tier_name + ROOR rich metadata。"""
        regs = discover_all_registries()
        # 至少一个条目带 owner/ssot_for 等 rich metadata（master_index 无此字段）
        rich = [r for r in regs if "owner" in r or "ssot_for" in r or "ssot_for".replace("_", "_") in r]
        assert rich, "ROOR rich metadata 未透传"
        # tier 元信息注入
        assert all("tier_level" in r for r in regs)

    def test_roor_missing_returns_empty(self, monkeypatch, tmp_path):
        """ROOR 不存在时返回空 list，不抛异常（ERROR_CONTRACT）。"""
        import zephyr.infrastructure.asset_inventory.registry_adapter as mod

        monkeypatch.setattr(mod, "_ROOR_REL", "nonexistent/roor.yaml")
        assert discover_all_registries() == []


class TestAgentsMdNoHardcodedCount:
    """AGENTS.md RULE-REGISTRY 不应硬编码 stale 计数（曾硬编码"31"，实际 ROOR=52/master_index=32）。"""

    def test_no_stale_31_hardcode_in_rule_registry(self):
        text = _AGENTS.read_text(encoding="utf-8")
        # RULE-REGISTRY 段落（## RULE-REGISTRY 到下一个 ## 之间）
        m = re.search(r"## RULE-REGISTRY.*?(?=\n## )", text, re.DOTALL)
        assert m, "未找到 RULE-REGISTRY 段落"
        section = m.group(0)
        # 禁止"31 个 registry"这类硬编码计数
        assert not re.search(r"31\s*个\s*registry", section), "RULE-REGISTRY 仍含 stale 硬编码 31"
        # 必须指向 ROOR 作为发现真源
        assert "registry_of_registries.yaml" in section, "RULE-REGISTRY 未指向 ROOR 发现真源"

    def test_rule_registry_clarifies_master_index_is_cache(self):
        """RULE-REGISTRY 必须说明 master_index 是 catalogs 派生缓存（非 registry-of-registries）。"""
        text = _AGENTS.read_text(encoding="utf-8")
        m = re.search(r"## RULE-REGISTRY.*?(?=\n## )", text, re.DOTALL)
        section = m.group(0)
        assert "catalogs" in section and "缓存" in section, "未声明 master_index 为 catalogs 派生缓存"

    def test_no_stale_ruling_count_hardcode(self):
        """RULE-RULING 不应硬编码裁定条目计数（曾硬编码"54"，实际 ruling_registry=56）。
        同类病根：AGENTS.md 硬编码 registry 计数，registry 增长后漂移。"""
        text = _AGENTS.read_text(encoding="utf-8")
        m = re.search(r"## RULE-RULING.*?(?=\n## )", text, re.DOTALL)
        assert m, "未找到 RULE-RULING 段落"
        section = m.group(0)
        # 禁止"\d+ 个裁定条目"这类硬编码计数
        assert not re.search(r"\d+\s*个\s*裁定条目", section), "RULE-RULING 仍含硬编码裁定计数"
        # 必须声明"勿写死"并指向 entries 真源
        assert "勿在文档/AI 记忆中写死" in section or "勿写死" in section, "RULE-RULING 未声明计数勿写死"


class TestSsotAlignment:
    """真源对齐：ROOR（SSoT）条目数 ≥ master_index（派生缓存），且 master_index 全在 catalogs/。"""

    def test_roor_superset_of_catalogs_scope(self):
        regs = discover_all_registries()
        mi = yaml.safe_load(_MASTER_INDEX.read_text(encoding="utf-8"))
        # ROOR 是项目级 SSoT（含非 catalogs 注册表），必然 ≥ master_index 的 catalogs 子集
        assert len(regs) >= len(mi.get("registries", []))
        # master_index 必须全在 catalogs/（证明它是 catalogs 派生缓存，非项目级 SSoT）
        mi_paths = [r.get("physical_path", "") for r in mi.get("registries", [])]
        assert all("_registry/catalogs/" in p for p in mi_paths), "master_index 含非 catalogs 路径（角色漂移）"
