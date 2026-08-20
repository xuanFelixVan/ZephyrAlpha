# [A_test] module_id: MOD-GOV_secret_registry_consistency_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_secret_registry_consistency_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_secret_registry_consistency_gate.py — SECRET-REGISTRY-CONSISTENCY 门禁单测

权威依据：secret_registry_consistency_gate.py（make_secret_registry_consistency_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestKeyExtraction: _extract_env_example_keys / _extract_registry_dotenv_keys
- TestGatewayIntegration: mock gateway 流程
  - staged 不含目标文件 → 放行
  - KEY 一致 → 放行
  - .env.example 有但 registry 无 → 阻断
  - registry 有但 .env.example 无 → 阻断
  - 双向不一致 → 阻断（两条违规）
  - git diff 失败 → fail-open
  - git diff 异常 → fail-open
  - .env.example 不存在 → fail-open
  - config/.env.{service} 的 KEY 不比较（只比 env_file=.env）

测试隔离：MagicMock 模拟 gateway.run_git + tmp_path 真实文件，不读/不写真实仓库。
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.secret_registry_consistency_gate import (  # noqa: E402
    _extract_env_example_keys,
    _extract_registry_dotenv_keys,
    make_secret_registry_consistency_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(
    staged_files=None,
    project_root=None,
    diff_fails=False,
    diff_raises=False,
):
    """构造 mock gateway：--name-only 返回 staged 文件列表；rev-parse --show-toplevel
    返回 project_root。文件内容由 tmp_path 真实文件提供。"""
    gw = MagicMock()
    gw.project_root = project_root or str(_PROJECT_ROOT)

    if diff_raises:

        def _raise(*a, **k):
            raise RuntimeError("git not found")

        gw.run_git = _raise
        return gw

    def _run_git(cmd):
        if diff_fails and "--name-only" in cmd:
            return _MockResult(1, "")
        if "--name-only" in cmd:
            return _MockResult(0, "\n".join(staged_files or []))
        if "rev-parse" in cmd:
            return _MockResult(0, str(gw.project_root))
        return _MockResult(0, "")

    gw.run_git = _run_git
    return gw


# ---------------------------------------------------------------------------
# 测试组 1: GateSpec 字段
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    """验证 factory 返回的 GateSpec 字段正确。"""

    def test_is_gate_spec(self):
        spec = make_secret_registry_consistency_gate()
        assert isinstance(spec, GateSpec)

    def test_gate_id(self):
        spec = make_secret_registry_consistency_gate()
        assert spec.gate_id == "SECRET-REGISTRY-CONSISTENCY"

    def test_priority_is_127(self):
        """priority=127——80-126 段已满，127 是 MCP-VERSION-FIELD(126) 之后首个空位。"""
        spec = make_secret_registry_consistency_gate()
        assert spec.priority == 127


# ---------------------------------------------------------------------------
# 测试组 2: KEY 提取函数
# ---------------------------------------------------------------------------
class TestKeyExtraction:
    """验证 .env.example 和 secret_registry.yaml 的 KEY 提取逻辑。"""

    def test_extract_env_example_keys(self):
        content = (
            "# 注释行\n"
            "TUSHARE_TOKEN=\n"
            "DEEPSEEK_API_KEY=\n"
            "\n"
            "  # 缩进注释\n"
            "ZEPHYR_AUDIT_HMAC_SECRET=\n"
            "lowercase_key=should_not_match\n"
        )
        keys = _extract_env_example_keys(content)
        assert keys == {"TUSHARE_TOKEN", "DEEPSEEK_API_KEY", "ZEPHYR_AUDIT_HMAC_SECRET"}

    def test_extract_env_example_empty(self):
        assert _extract_env_example_keys("") == set()
        assert _extract_env_example_keys("# only comments\n") == set()

    def test_extract_registry_dotenv_keys(self):
        content = (
            "secrets:\n"
            "  - key: TUSHARE_TOKEN\n"
            "    env_file: .env\n"
            "  - key: POSTGRES_PASSWORD\n"
            "    env_file: config/.env.postgres\n"
            "  - key: DEEPSEEK_API_KEY\n"
            "    env_file: .env\n"
        )
        keys = _extract_registry_dotenv_keys(content)
        # 只提取 env_file=.env 的 KEY
        assert keys == {"TUSHARE_TOKEN", "DEEPSEEK_API_KEY"}

    def test_extract_registry_no_env_file(self):
        """key 没有 env_file 字段时不提取。"""
        content = "secrets:\n  - key: ORPHAN_KEY\n  - key: GOOD_KEY\n    env_file: .env\n"
        keys = _extract_registry_dotenv_keys(content)
        assert keys == {"GOOD_KEY"}


# ---------------------------------------------------------------------------
# 测试组 3: Gateway 集成
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    """mock gateway 流程测试。"""

    def test_staged_no_target_files_pass(self, tmp_path):
        """staged 不含 .env.example 或 secret_registry.yaml → 放行。"""
        gw = _make_gateway(staged_files=["src/main.py"], project_root=str(tmp_path))
        spec = make_secret_registry_consistency_gate()
        passed, detail = spec.check(gw, [])
        assert passed is True
        assert detail == ""

    def test_keys_consistent_pass(self, tmp_path):
        """.env.example 和 registry KEY 一致 → 放行。"""
        env_example = tmp_path / ".env.example"
        env_example.write_text("TUSHARE_TOKEN=\nDEEPSEEK_API_KEY=\n", encoding="utf-8")
        registry = tmp_path / "config" / "secret_registry.yaml"
        registry.parent.mkdir(parents=True, exist_ok=True)
        registry.write_text(
            "secrets:\n  - key: TUSHARE_TOKEN\n    env_file: .env\n  - key: DEEPSEEK_API_KEY\n    env_file: .env\n",
            encoding="utf-8",
        )
        gw = _make_gateway(staged_files=[".env.example"], project_root=str(tmp_path))
        spec = make_secret_registry_consistency_gate()
        passed, detail = spec.check(gw, [])
        assert passed is True

    def test_only_in_example_blocks(self, tmp_path):
        """.env.example 有但 registry 未登记 → 阻断。"""
        env_example = tmp_path / ".env.example"
        env_example.write_text("TUSHARE_TOKEN=\nNEW_SECRET=\n", encoding="utf-8")
        registry = tmp_path / "config" / "secret_registry.yaml"
        registry.parent.mkdir(parents=True, exist_ok=True)
        registry.write_text(
            "secrets:\n  - key: TUSHARE_TOKEN\n    env_file: .env\n",
            encoding="utf-8",
        )
        gw = _make_gateway(staged_files=[".env.example"], project_root=str(tmp_path))
        spec = make_secret_registry_consistency_gate()
        passed, detail = spec.check(gw, [])
        assert passed is False
        assert "NEW_SECRET" in detail

    def test_only_in_registry_blocks(self, tmp_path):
        """registry 有但 .env.example 未文档化 → 阻断。"""
        env_example = tmp_path / ".env.example"
        env_example.write_text("TUSHARE_TOKEN=\n", encoding="utf-8")
        registry = tmp_path / "config" / "secret_registry.yaml"
        registry.parent.mkdir(parents=True, exist_ok=True)
        registry.write_text(
            "secrets:\n  - key: TUSHARE_TOKEN\n    env_file: .env\n  - key: HIDDEN_KEY\n    env_file: .env\n",
            encoding="utf-8",
        )
        gw = _make_gateway(
            staged_files=["config/secret_registry.yaml"],
            project_root=str(tmp_path),
        )
        spec = make_secret_registry_consistency_gate()
        passed, detail = spec.check(gw, [])
        assert passed is False
        assert "HIDDEN_KEY" in detail

    def test_bidirectional_mismatch_blocks(self, tmp_path):
        """双向不一致 → 阻断（两条违规都报告）。"""
        env_example = tmp_path / ".env.example"
        env_example.write_text("KEY_A=\nKEY_B=\n", encoding="utf-8")
        registry = tmp_path / "config" / "secret_registry.yaml"
        registry.parent.mkdir(parents=True, exist_ok=True)
        registry.write_text(
            "secrets:\n  - key: KEY_B\n    env_file: .env\n  - key: KEY_C\n    env_file: .env\n",
            encoding="utf-8",
        )
        gw = _make_gateway(
            staged_files=[".env.example", "config/secret_registry.yaml"],
            project_root=str(tmp_path),
        )
        spec = make_secret_registry_consistency_gate()
        passed, detail = spec.check(gw, [])
        assert passed is False
        assert "KEY_A" in detail  # only in example
        assert "KEY_C" in detail  # only in registry

    def test_service_env_keys_not_compared(self, tmp_path):
        """config/.env.{service} 的 KEY 不在 .env.example 中，不比较。"""
        env_example = tmp_path / ".env.example"
        env_example.write_text("TUSHARE_TOKEN=\n", encoding="utf-8")
        registry = tmp_path / "config" / "secret_registry.yaml"
        registry.parent.mkdir(parents=True, exist_ok=True)
        registry.write_text(
            "secrets:\n"
            "  - key: TUSHARE_TOKEN\n"
            "    env_file: .env\n"
            "  - key: POSTGRES_PASSWORD\n"
            "    env_file: config/.env.postgres\n"
            "  - key: CLICKHOUSE_HOST\n"
            "    env_file: config/.env.clickhouse\n",
            encoding="utf-8",
        )
        gw = _make_gateway(staged_files=[".env.example"], project_root=str(tmp_path))
        spec = make_secret_registry_consistency_gate()
        passed, detail = spec.check(gw, [])
        assert passed is True

    def test_git_diff_fails_fail_open(self, tmp_path):
        """git diff 失败 → fail-open。"""
        gw = _make_gateway(diff_fails=True, project_root=str(tmp_path))
        spec = make_secret_registry_consistency_gate()
        passed, detail = spec.check(gw, [])
        assert passed is True
        assert detail == ""

    def test_git_diff_raises_fail_open(self, tmp_path):
        """git diff 异常 → fail-open。"""
        gw = _make_gateway(diff_raises=True, project_root=str(tmp_path))
        spec = make_secret_registry_consistency_gate()
        passed, detail = spec.check(gw, [])
        assert passed is True
        assert detail == ""

    def test_env_example_missing_fail_open(self, tmp_path):
        """.env.example 不存在 → fail-open。"""
        registry = tmp_path / "config" / "secret_registry.yaml"
        registry.parent.mkdir(parents=True, exist_ok=True)
        registry.write_text(
            "secrets:\n  - key: TUSHARE_TOKEN\n    env_file: .env\n",
            encoding="utf-8",
        )
        gw = _make_gateway(staged_files=[".env.example"], project_root=str(tmp_path))
        spec = make_secret_registry_consistency_gate()
        passed, detail = spec.check(gw, [])
        assert passed is True  # fail-open

    def test_registry_missing_fail_open(self, tmp_path):
        """secret_registry.yaml 不存在 → fail-open。"""
        env_example = tmp_path / ".env.example"
        env_example.write_text("TUSHARE_TOKEN=\n", encoding="utf-8")
        gw = _make_gateway(
            staged_files=["config/secret_registry.yaml"],
            project_root=str(tmp_path),
        )
        spec = make_secret_registry_consistency_gate()
        passed, detail = spec.check(gw, [])
        assert passed is True  # fail-open
