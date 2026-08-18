# [A_test] module_id: MOD-GOV_import_smoke_agent_spec | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-450 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.agent_spec.test_import_smoke
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""agent-spec MOD-INF-019 import 冒烟测试 — 验证核心模块可被导入."""

import sys
from pathlib import Path

import pytest

from zephyr.shared.io.paths import REPO_ROOT

_PROJECT_ROOT = REPO_ROOT
_SRC_DIR = _PROJECT_ROOT / "src"


def _ensure_path() -> None:
    """确保 src/ 在 sys.path 中."""
    src_str = str(_SRC_DIR)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)


class TestAgentSpecImportSmoke:
    """验证 agent-spec 核心模块可以被成功导入."""

    def test_import_agent_spec_init(self) -> None:
        """测试导入 zephyr.governance.agent_spec 包自身."""
        _ensure_path()
        import zephyr.autonomy_core

        assert hasattr(zephyr.governance.agent_spec, "__all__")

    def test_import_skill_model(self) -> None:
        """测试导入 SkillModel / SkillTier / SkillType."""
        _ensure_path()
        from zephyr.autonomy_core.skills.skill_model import (
            SkillStatus,
            SkillTier,
            SkillType,
        )

        assert SkillTier is not None
        assert SkillType is not None
        assert SkillStatus is not None

    def test_import_skill_loader(self) -> None:
        """测试导入 SkillLoader."""
        _ensure_path()
        from zephyr.autonomy_core.skills.skill_loader import SkillLoader

        assert SkillLoader is not None

    def test_import_skill_factory(self) -> None:
        """测试导入 SkillFactory — 蓝图→Skill 升级引擎核心."""
        _ensure_path()
        from zephyr.autonomy_core.skills.skill_factory import SkillFactory

        assert SkillFactory is not None

    def test_import_skill_router(self) -> None:
        _ensure_path()
        from zephyr.autonomy_core.skills.skill_router import SkillRouter

        assert SkillRouter is not None

    def test_import_skill_constructor(self) -> None:
        """测试导入 SkillConstructor — 蓝图→Skill 构建器."""
        _ensure_path()
        from zephyr.autonomy_core.skills.skill_constructor import SkillConstructor

        assert SkillConstructor is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
