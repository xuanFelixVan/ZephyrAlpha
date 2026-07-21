# [A_test] module_id: MOD-GOV_conftest | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.conftest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
pytest fixtures for agent-rbac tests.

Fixture 清单:
  - test_agent: AgentIdentity 工厂
  - permission_config: RbacConfig 加载器
  - rbac_roles_path: 测试用 rbac_roles.yaml 路径
"""

from pathlib import Path

import pytest
import yaml

TEST_SESSION_ID = "session-test-20260507-001"


@pytest.fixture
def rbac_roles_path(tmp_path: Path) -> Path:
    """生成测试用 rbac_roles.yaml"""
    config = {
        "version": "0.14.0",
        "agents": {
            "session-test-20260507-001": {
                "maturity": "infant",
                "permissions": ["read:docs", "read:src", "write:tests", "execute:scripts"],
                "auto_guard_eligible": True,
                "owner_approved": False,
            },
            "session-test-20260507-admin": {
                "maturity": "mature",
                "permissions": [
                    "read:docs",
                    "read:src",
                    "write:src",
                    "write:tests",
                    "execute:scripts",
                    "manage:rbac",
                    "manage:kill_switch",
                ],
                "auto_guard_eligible": False,
                "owner_approved": True,
            },
        },
    }
    config_path = tmp_path / "rbac_roles.yaml"
    config_path.write_text(yaml.dump(config), encoding="utf-8")
    return config_path


@pytest.fixture
def test_agent() -> dict:
    """返回测试 Agent 的基础身份数据"""
    return {
        "session_id": TEST_SESSION_ID,
        "ide": "trae",
        "model": "deepseek",
        "maturity": "infant",
        "task_context": "unit-tests for agent-rbac module",
    }


@pytest.fixture
def admin_agent() -> dict:
    """返回管理员 Agent 的身份数据"""
    return {
        "session_id": "session-test-20260507-admin",
        "ide": "trae",
        "model": "deepseek",
        "maturity": "mature",
        "task_context": "administrative operations",
    }


@pytest.fixture
def permission_config(rbac_roles_path: Path) -> dict:
    """从 YAML 加载权限配置"""
    config = yaml.safe_load(rbac_roles_path.read_text(encoding="utf-8"))
    return config
