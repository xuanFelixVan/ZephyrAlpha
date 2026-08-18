# [A_test] module_id: MOD-GOV-zephyr_env_direct_access_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_COMMIT_GATES | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] tests.governance.commit_gates.test_zephyr_env_direct_access_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_COMMIT_GATES | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_zephyr_env_direct_access_gate.py — ZEPHYR_ENV 直访硬阻断门禁单测（ZEPHYR-ENV-DIRECT-ACCESS）

权威依据：zephyr_env_direct_access_gate.py（make_zephyr_env_direct_access_gate）
5.34 环境隔离防复发

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestEnvSubscriptBlocked: os.environ["ZEPHYR_ENV"] → hard-block
- TestEnvGetBlocked: os.environ.get("ZEPHYR_ENV") → hard-block
- TestConfigLayerPasses: config 层目录豁免
- TestCleanFilePasses: 干净文件通过
- TestNoqaExemption: # noqa: e34-env  测试gate豁免检测
- TestTestExempt: tests/ 下文件豁免
- TestNonSrcZephyrPasses: 非 src/zephyr/ 文件豁免
- TestAddedLinesOnly: 存量违规非 added → 通过
- TestFailOpenGitDiff: git diff 失败 → 通过
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from tests.governance.commit_gates.gate_test_helpers import make_mock_gateway  # noqa: E402
from zephyr.gov_enforcement.commit_gates.zephyr_env_direct_access_gate import (  # noqa: E402
    make_zephyr_env_direct_access_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402

# ============================================================================
# TestGateSpecFields
# ============================================================================


class TestGateSpecFields:
    def test_gate_id(self):
        gate = make_zephyr_env_direct_access_gate()
        assert gate.gate_id == "ZEPHYR-ENV-DIRECT-ACCESS"

    def test_priority(self):
        gate = make_zephyr_env_direct_access_gate()
        assert gate.priority == 125

    def test_is_gatespec(self):
        gate = make_zephyr_env_direct_access_gate()
        assert isinstance(gate, GateSpec)


# ============================================================================
# TestEnvSubscriptBlocked (hard-block 命中)
# ============================================================================


class TestEnvSubscriptBlocked:
    def test_double_quote_subscript_blocked(self):
        """os.environ["ZEPHYR_ENV"] → hard-block"""
        src_file = "src/zephyr/trading/foo.py"
        gw = make_mock_gateway(
            [src_file], {src_file: ['    env = os.environ["ZEPHYR_ENV"]']}
        )
        gate = make_zephyr_env_direct_access_gate()
        passed, detail = gate.check(gw, [])
        assert not passed
        assert "ZEPHYR-ENV-DIRECT-ACCESS" in detail

    def test_single_quote_subscript_blocked(self):
        """os.environ['ZEPHYR_ENV'] → hard-block"""
        src_file = "src/zephyr/trading/foo.py"
        gw = make_mock_gateway(
            [src_file], {src_file: ["    env = os.environ['ZEPHYR_ENV']"]}
        )
        gate = make_zephyr_env_direct_access_gate()
        passed, _ = gate.check(gw, [])
        assert not passed


# ============================================================================
# TestEnvGetBlocked
# ============================================================================


class TestEnvGetBlocked:
    def test_env_get_double_quote_blocked(self):
        """os.environ.get("ZEPHYR_ENV") → hard-block"""
        src_file = "src/zephyr/trading/foo.py"
        gw = make_mock_gateway(
            [src_file], {src_file: ['    env = os.environ.get("ZEPHYR_ENV")']}
        )
        gate = make_zephyr_env_direct_access_gate()
        passed, detail = gate.check(gw, [])
        assert not passed
        assert "ZEPHYR-ENV-DIRECT-ACCESS" in detail

    def test_env_get_single_quote_blocked(self):
        """os.environ.get('ZEPHYR_ENV') → hard-block"""
        src_file = "src/zephyr/trading/foo.py"
        gw = make_mock_gateway(
            [src_file], {src_file: ["    env = os.environ.get('ZEPHYR_ENV')"]}
        )
        gate = make_zephyr_env_direct_access_gate()
        passed, _ = gate.check(gw, [])
        assert not passed


# ============================================================================
# TestConfigLayerPasses (config 层目录豁免)
# ============================================================================


class TestConfigLayerPasses:
    def test_config_layer_subscript_passes(self):
        """src/zephyr/shared/foundation/config/ 下的 os.environ["ZEPHYR_ENV"] → 豁免"""
        config_file = "src/zephyr/shared/foundation/config/settings.py"
        gw = make_mock_gateway(
            [config_file], {config_file: ['    env = os.environ["ZEPHYR_ENV"]']}
        )
        gate = make_zephyr_env_direct_access_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""

    def test_config_layer_get_passes(self):
        """src/zephyr/shared/foundation/config/ 下的 os.environ.get → 豁免"""
        config_file = "src/zephyr/shared/foundation/config/loader.py"
        gw = make_mock_gateway(
            [config_file], {config_file: ['    env = os.environ.get("ZEPHYR_ENV", "dev")']}
        )
        gate = make_zephyr_env_direct_access_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestCleanFilePasses
# ============================================================================


class TestCleanFilePasses:
    def test_clean_src_zephyr_passes(self):
        """src/zephyr/ 中无 ZEPHYR_ENV 直访 → 通过"""
        src_file = "src/zephyr/trading/clean.py"
        gw = make_mock_gateway(
            [src_file], {src_file: ["    x = 1 + 2"]}
        )
        gate = make_zephyr_env_direct_access_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""

    def test_other_env_var_passes(self):
        """os.environ["OTHER_VAR"]（非 ZEPHYR_ENV）→ 通过"""
        src_file = "src/zephyr/trading/foo.py"
        gw = make_mock_gateway(
            [src_file], {src_file: ['    path = os.environ["PATH"]']}
        )
        gate = make_zephyr_env_direct_access_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestNoqaExemption
# ============================================================================


class TestNoqaExemption:
    def test_noqa_exempts(self):
        """os.environ["ZEPHYR_ENV"] + noqa:e34-env → 豁免"""
        src_file = "src/zephyr/trading/foo.py"
        gw = make_mock_gateway(
            [src_file],
            {src_file: ['    env = os.environ["ZEPHYR_ENV"]  # noqa: e34-env  合法场景测试用']},
        )
        gate = make_zephyr_env_direct_access_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestTestExempt
# ============================================================================


class TestTestExempt:
    def test_tests_dir_exempt(self):
        """tests/ 下文件中的 os.environ["ZEPHYR_ENV"] → 豁免"""
        test_file = "tests/governance/foo.py"
        gw = make_mock_gateway(
            [test_file], {test_file: ['    env = os.environ["ZEPHYR_ENV"]']}
        )
        gate = make_zephyr_env_direct_access_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestNonSrcZephyrPasses
# ============================================================================


class TestNonSrcZephyrPasses:
    def test_non_src_zephyr_passes(self):
        """非 src/zephyr/ 文件中的 os.environ["ZEPHYR_ENV"] → 豁免"""
        ext_file = "scripts/ops/foo.py"
        gw = make_mock_gateway(
            [ext_file], {ext_file: ['    env = os.environ["ZEPHYR_ENV"]']}
        )
        gate = make_zephyr_env_direct_access_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestAddedLinesOnly (存量违规非 added → 通过)
# ============================================================================


class TestAddedLinesOnly:
    def test_existing_violation_not_added_passes(self):
        """存量 os.environ["ZEPHYR_ENV"]（非 added 行）→ 通过（由 M30 监控）"""
        src_file = "src/zephyr/trading/legacy.py"
        full_content = (
            "# header comment\n"
            "\n"
            'env = os.environ["ZEPHYR_ENV"]  # 存量违规，非 added 行\n'
            "\n"
            "def new_func():\n"
            "    pass\n"
        )
        gw = make_mock_gateway(
            [src_file],
            {src_file: ["# header comment", "def new_func():", "    pass"]},
            file_contents={src_file: full_content},
        )
        gate = make_zephyr_env_direct_access_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestFailOpenGitDiff
# ============================================================================


class TestFailOpenGitDiff:
    def test_git_diff_fail_open(self):
        """git diff --name-only returncode != 0 → fail-open（通过）"""
        gw = make_mock_gateway([], {}, diff_fail=True)
        gate = make_zephyr_env_direct_access_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""
