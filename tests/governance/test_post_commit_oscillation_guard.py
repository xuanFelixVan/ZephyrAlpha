# [A_test] module_id: MOD-GOV_post_commit_oscillation_guard | layer=test | stability=volatile | safety=L | ai_modifiable
# [BLUEPRINT] MOD-D5_ARCH_TOOLS | docs/02_enterprise_architecture/04_architecture_principles_decisions/panorama/generator_auto_trigger_pilot.md | §防振荡强化
# [MODULE] tests.governance.test_post_commit_oscillation_guard
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [INVARIANTS] 测试不污染真实 .runtime/locks（mock _LOCK_FILE 到 tmp_path）
# [ERROR_CONTRACT] 测试失败 = 防振荡机制缺失/回归
# [MATURITY] evolving
# [A_module] module_id=MOD-D5_ARCH_TOOLS | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_post_commit_oscillation_guard.py — post_commit_regen_yaml.py 防振荡强化机制测试。

本测试验证两个待实施的强化机制（TDD Red phase → Green phase）：

  #1 并发去重（lockfile）：连续多次 commit 只 spawn 1 次 reconcile_stale。
     病根：当前 main() 无 lockfile/PID 检查，连续多次 commit（批量提交/AI 连续提交）
           会 spawn 多个 reconcile_stale，导致产物写冲突/资源争用。
     治本：加 lockfile（.runtime/locks/reconcile_stale.pid，TTL 60s），存在且未过期则跳过 spawn。

  #3 产物循环阻断：commit 命中生成器 yaml 产物时不触发。
     病根：当前 _matches_generator_input 只检查 input_sources，不检查 output_globs。
           若未来误将生成器 yaml 产物（如 policies.yaml）配置为另一生成器输入源，
           会形成 yaml→产物→yaml 循环，导致死循环。
     治本：新增 _generator_yaml_outputs() 收集 yaml 产物，
           _matches_generator_input 命中产物时返回 False（跳过触发）。

当前状态：Red phase（测试应 FAIL，证明强化机制缺失）
实施强化后：Green phase（测试应 PASS）

对标：tests/governance/test_reconcile_generators.py::TestPostCommitRegenYaml
（前者验证现有行为，本文件验证待实施的强化机制）
"""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_POST_COMMIT_SCRIPT = _REPO_ROOT / "scripts" / "governance" / "git_hooks" / "post_commit_regen_yaml.py"


@pytest.fixture(scope="module")
def pcr():
    """动态加载 post_commit_regen_yaml.py（对标 test_reconcile_generators.py 的 pcr fixture）。

    真实执行模块级代码（含 import 语句）——若 import 缺失会立即抛 ImportError/NameError。
    """
    spec = importlib.util.spec_from_file_location("post_commit_regen_yaml_oscillation_test", _POST_COMMIT_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ============================================================================
# #1 并发去重：连续多次 commit 只 spawn 1 次（lockfile 去重）
# ============================================================================


class TestConcurrentSpawnDedup:
    """验证连续 commit 场景的 spawn 去重。

    Red phase（当前）：无 lockfile，连续 commit spawn N 次 → 测试 FAIL。
    Green phase（强化后）：lockfile TTL 去重，只 spawn 1 次 → 测试 PASS。
    """

    def test_consecutive_commits_should_dedup_to_single_spawn(self, pcr, monkeypatch, tmp_path):
        """连续 3 次 commit 同一 yaml 输入源 → 应只 spawn 1 次（lockfile 去重）。

        模拟场景：AI 批量提交或连续提交多个 yaml 文件，每次 commit 都命中生成器输入源。
        当前行为：spawn 3 次（无去重）→ 测试 FAIL（Red phase）。
        期望行为：spawn 1 次（第 1 次创建 lockfile，后续跳过）→ 测试 PASS（Green phase）。
        """
        monkeypatch.delenv("ZEPHYR_SKIP_REGENERATE", raising=False)
        # 强化后会有 _LOCK_FILE 变量，mock 到 tmp_path 隔离测试（不污染真实 .runtime/locks）
        if hasattr(pcr, "_LOCK_FILE"):
            monkeypatch.setattr(pcr, "_LOCK_FILE", tmp_path / "reconcile_stale.pid")
        # mock commit 了生成器 yaml 输入源（触发 _matches_generator_input）
        monkeypatch.setattr(
            pcr,
            "_committed_yaml_files",
            lambda: ["docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml"],
        )
        # 拦截 Popen 计数（不启动真实子进程）
        spawn_count = {"n": 0}

        def _fake_popen(*args, **kwargs):
            spawn_count["n"] += 1
            m = MagicMock()
            m.pid = 99999 + spawn_count["n"]
            return m

        monkeypatch.setattr(subprocess, "Popen", _fake_popen)

        # 模拟连续 3 次 commit（批量提交场景）
        for _ in range(3):
            pcr.main()

        # 期望：只 spawn 1 次（lockfile 去重）
        assert spawn_count["n"] == 1, (
            f"连续 3 次 commit 应只 spawn 1 次（lockfile 去重），实际 spawn {spawn_count['n']} 次。"
            f"Red phase：当前无去重机制；实施 #1 强化（lockfile TTL）后应 PASS。"
        )


# ============================================================================
# #3 产物循环阻断：commit 命中生成器 yaml 产物时不触发
# ============================================================================


class TestGeneratorOutputCycleBlock:
    """验证产物循环阻断机制。

    Red phase（当前）：_generator_yaml_outputs 函数不存在 + _matches_generator_input
                     不检查 outputs → 测试 FAIL。
    Green phase（强化后）：新增 _generator_yaml_outputs + 产物阻断逻辑 → 测试 PASS。
    """

    def test_generator_yaml_outputs_function_exists(self, pcr):
        """_generator_yaml_outputs() 函数存在且收集所有生成器 yaml 产物。

        当前行为：函数不存在 → AttributeError → 测试 FAIL（Red phase）。
        期望行为：返回包含 policies.yaml 的集合 → 测试 PASS（Green phase）。

        policies 生成器的 output_globs 含 src/zephyr/data/config/policies.yaml，
        是注册表中唯一的 yaml 产物，是 #3 防循环的核心检测点。
        """
        outputs = pcr._generator_yaml_outputs()
        assert isinstance(outputs, set), f"应返回 set，实际 {type(outputs)}"
        assert "src/zephyr/data/config/policies.yaml" in outputs, (
            "policies 生成器的 yaml 产物 src/zephyr/data/config/policies.yaml 应被收集。"
            "这是注册表中唯一的 yaml 产物，是 #3 防循环的核心检测点。"
        )

    def test_commit_generator_output_yaml_skipped(self, pcr, monkeypatch):
        """commit 命中生成器 yaml 产物 → 不触发 spawn（即使误配为输入源）。

        场景：policies 生成器输出 src/zephyr/data/config/policies.yaml，
              假设未来误将其配为另一生成器输入源（模拟配置错误）。
        当前行为：_matches_generator_input 不检查 outputs，命中 inputs 即触发 → spawn 1 次 → FAIL。
        期望行为：命中 outputs 跳过触发 → spawn 0 次 → PASS。

        防循环原理：若 policies.yaml 既是产物又是输入，commit policies.yaml 会触发重生成，
        重生成又产生 policies.yaml diff，下次 commit 又触发 → 死循环。
        产物阻断：commit 命中产物时跳过，打断循环。
        """
        monkeypatch.delenv("ZEPHYR_SKIP_REGENERATE", raising=False)
        # 模拟误配置：policies.yaml 被配为输入源（未来可能的人为配置错误）
        monkeypatch.setattr(
            pcr,
            "_generator_yaml_inputs",
            lambda: {"src/zephyr/data/config/policies.yaml"},
        )
        # commit 了 policies.yaml（生成器产物）
        monkeypatch.setattr(
            pcr,
            "_committed_yaml_files",
            lambda: ["src/zephyr/data/config/policies.yaml"],
        )
        # 拦截 Popen 计数
        spawn_count = {"n": 0}

        def _fake_popen(*args, **kwargs):
            spawn_count["n"] += 1
            return MagicMock()

        monkeypatch.setattr(subprocess, "Popen", _fake_popen)

        pcr.main()

        # 期望：不 spawn（命中生成器产物，应跳过触发）
        assert spawn_count["n"] == 0, (
            f"commit 生成器 yaml 产物不应触发 spawn（防产物→触发→产物循环），"
            f"实际 spawn {spawn_count['n']} 次。"
            f"Red phase：当前 _matches_generator_input 不检查 outputs；"
            f"实施 #3 强化（产物阻断）后应 PASS。"
        )
