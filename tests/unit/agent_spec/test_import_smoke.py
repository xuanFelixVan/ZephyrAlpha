"""agent-spec MOD-INF-019 import 冒烟测试 — 验证核心模块可被导入."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_SRC_DIR = _PROJECT_ROOT / "src"


def _ensure_path() -> None:
    """确保 src/ 在 sys.path 中."""
    src_str = str(_SRC_DIR)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)


class TestAgentSpecImportSmoke:
    """验证 agent_spec 核心模块可以被成功导入."""

    def test_import_agent_spec_init(self) -> None:
        """测试导入 zephyr.agent_spec 包自身."""
        _ensure_path()
        import zephyr.agent_spec  # noqa: F401
        assert hasattr(zephyr.agent_spec, "__all__")

    def test_import_skill_model(self) -> None:
        """测试导入 SkillModel / SkillTier / SkillType."""
        _ensure_path()
        from zephyr.agent_spec.skill_model import (
            SkillModel,
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
        from zephyr.agent_spec.skill_loader import SkillLoader
        assert SkillLoader is not None

    def test_import_skill_factory(self) -> None:
        """测试导入 SkillFactory — 蓝图→Skill 升级引擎核心."""
        _ensure_path()
        from zephyr.agent_spec.skill_factory import SkillFactory
        assert SkillFactory is not None

    def test_import_trigger_router(self) -> None:
        """测试导入 TriggerRouter."""
        _ensure_path()
        from zephyr.agent_spec.trigger_router import TriggerRouter
        assert TriggerRouter is not None

    def test_import_skill_constructor(self) -> None:
        """测试导入 SkillConstructor — 蓝图→Skill 构建器."""
        _ensure_path()
        from zephyr.agent_spec.skill_constructor import SkillConstructor
        assert SkillConstructor is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
