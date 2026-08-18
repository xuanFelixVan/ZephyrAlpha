# [A_test] module_id: MOD-CD-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CD-001 | docs/03_modules/_cross_layer/cd_pipeline/blueprint.md | §test
# [MODULE] tests.ops.test_shadow_canary_deploy
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] scripts.ops.shadow_canary_deploy; zephyr.gov_enforcement.rule_enforcement.can_i_deploy
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_shadow_canary_deploy.py
# [A_module] module_id=MOD-CD-001 | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_shadow_canary_deploy.py — Shadow Canary 部署运行器单元测试

覆盖主流程分支:
  - compare_decisions: 空集/一致/分歧/单侧差异/阈值边界
  - load_decisions: 文件缺失/空/有效jsonl/无效行
  - run_precheck: skip 模式 vacuous-pass
  - run_deploy: 预检失败(exit 2)/promote(exit 0)/rollback(exit 1)/异常(exit 2)
  - make_deployer: windows/container/unknown
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_OPS = _REPO_ROOT / "scripts" / "ops"
if str(_SCRIPTS_OPS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_OPS))

from shadow_canary_deploy import (  # noqa: E402
    EXIT_PRECHECK_FAIL,
    EXIT_PROMOTE,
    EXIT_ROLLBACK,
    ComparisonResult,
    WindowsProcessDeployer,
    _ThresholdHolder,
    compare_decisions,
    load_decisions,
    make_deployer,
    run_deploy,
    run_precheck,
)

from zephyr.gov_enforcement.rule_enforcement.can_i_deploy import CanIDeployResult  # noqa: E402


# ============================================================================
# compare_decisions 测试
# ============================================================================
class TestCompareDecisions:
    """compare_decisions 输出比对逻辑——按 (symbol, timestamp) 对齐。"""

    def setup_method(self) -> None:
        _ThresholdHolder.threshold = 0.05

    def test_both_empty(self) -> None:
        """双方皆空 -> divergence 0.0（vacuous promote）。"""
        r = compare_decisions([], [])
        assert r.divergence_rate == 0.0
        assert r.aligned == 0
        assert r.mismatches == 0
        assert r.promote is True

    def test_identical(self) -> None:
        """完全一致 -> divergence 0.0。"""
        d = [{"symbol": "000001", "timestamp": "t1", "side": "BUY", "quantity": 100, "price": 10.0}]
        r = compare_decisions(d, d)
        assert r.divergence_rate == 0.0
        assert r.aligned == 1
        assert r.mismatches == 0
        assert r.promote is True

    def test_mismatch_side(self) -> None:
        """side 不同 -> mismatch, divergence 1.0。"""
        prod = [{"symbol": "000001", "timestamp": "t1", "side": "BUY", "quantity": 100, "price": 10.0}]
        shadow = [{"symbol": "000001", "timestamp": "t1", "side": "SELL", "quantity": 100, "price": 10.0}]
        r = compare_decisions(prod, shadow)
        assert r.divergence_rate == 1.0
        assert r.mismatches == 1
        assert r.promote is False

    def test_mismatch_quantity(self) -> None:
        """quantity 差异超 epsilon -> mismatch。"""
        prod = [{"symbol": "000001", "timestamp": "t1", "side": "BUY", "quantity": 100, "price": 10.0}]
        shadow = [{"symbol": "000001", "timestamp": "t1", "side": "BUY", "quantity": 200, "price": 10.0}]
        r = compare_decisions(prod, shadow)
        assert r.divergence_rate == 1.0
        assert r.mismatches == 1

    def test_mismatch_price(self) -> None:
        """price 差异超 epsilon -> mismatch。"""
        prod = [{"symbol": "000001", "timestamp": "t1", "side": "BUY", "quantity": 100, "price": 10.0}]
        shadow = [{"symbol": "000001", "timestamp": "t1", "side": "BUY", "quantity": 100, "price": 11.0}]
        r = compare_decisions(prod, shadow)
        assert r.divergence_rate == 1.0
        assert r.mismatches == 1

    def test_new_only(self) -> None:
        """shadow 有、prod 无 -> new_only, divergence 1.0（fail-safe）。"""
        shadow = [{"symbol": "000001", "timestamp": "t1", "side": "BUY", "quantity": 100, "price": 10.0}]
        r = compare_decisions([], shadow)
        assert r.divergence_rate == 1.0
        assert r.new_only == 1
        assert r.aligned == 0
        assert r.promote is False

    def test_prod_only(self) -> None:
        """prod 有、shadow 无 -> prod_only, divergence 1.0（fail-safe）。"""
        prod = [{"symbol": "000001", "timestamp": "t1", "side": "BUY", "quantity": 100, "price": 10.0}]
        r = compare_decisions(prod, [])
        assert r.divergence_rate == 1.0
        assert r.prod_only == 1
        assert r.aligned == 0
        assert r.promote is False

    def test_below_threshold(self) -> None:
        """1/10 分歧, 阈值 0.05 -> divergence 0.1 >= 0.05 -> rollback。"""
        _ThresholdHolder.threshold = 0.05
        prod = [{"symbol": f"S{i}", "timestamp": f"t{i}", "side": "BUY", "quantity": 100, "price": 10.0} for i in range(10)]
        shadow = [{"symbol": f"S{i}", "timestamp": f"t{i}", "side": "BUY", "quantity": 100, "price": 10.0} for i in range(10)]
        shadow[0]["side"] = "SELL"  # 1 mismatch
        r = compare_decisions(prod, shadow)
        assert r.divergence_rate == pytest.approx(0.1)
        assert r.promote is False

    def test_at_threshold_boundary(self) -> None:
        """1/20 分歧 = 0.05, 0.05 < 0.05 is False -> rollback（边界 fail-safe）。"""
        _ThresholdHolder.threshold = 0.05
        prod = [{"symbol": f"S{i}", "timestamp": f"t{i}", "side": "BUY", "quantity": 100, "price": 10.0} for i in range(20)]
        shadow = [{"symbol": f"S{i}", "timestamp": f"t{i}", "side": "BUY", "quantity": 100, "price": 10.0} for i in range(20)]
        shadow[0]["side"] = "SELL"  # 1/20 = 0.05
        r = compare_decisions(prod, shadow)
        assert r.divergence_rate == pytest.approx(0.05)
        assert r.promote is False  # 0.05 < 0.05 is False

    def test_just_below_threshold(self) -> None:
        """1/21 分歧 ~0.0476 < 0.05 -> promote。"""
        _ThresholdHolder.threshold = 0.05
        prod = [{"symbol": f"S{i}", "timestamp": f"t{i}", "side": "BUY", "quantity": 100, "price": 10.0} for i in range(21)]
        shadow = [{"symbol": f"S{i}", "timestamp": f"t{i}", "side": "BUY", "quantity": 100, "price": 10.0} for i in range(21)]
        shadow[0]["side"] = "SELL"  # 1/21 ≈ 0.0476
        r = compare_decisions(prod, shadow)
        assert r.divergence_rate < 0.05
        assert r.promote is True


# ============================================================================
# load_decisions 测试
# ============================================================================
class TestLoadDecisions:
    """load_decisions jsonl 读取——文件缺失/空/有效/无效行。"""

    def test_missing_file(self, tmp_path: Path) -> None:
        """文件不存在 -> 空列表。"""
        assert load_decisions(tmp_path / "nonexistent.jsonl") == []

    def test_empty_file(self, tmp_path: Path) -> None:
        """空文件 -> 空列表。"""
        f = tmp_path / "empty.jsonl"
        f.write_text("")
        assert load_decisions(f) == []

    def test_valid_jsonl(self, tmp_path: Path) -> None:
        """有效 jsonl -> 解析所有行。"""
        f = tmp_path / "decisions.jsonl"
        f.write_text(
            json.dumps({"symbol": "000001", "side": "BUY"}) + "\n"
            + json.dumps({"symbol": "000002", "side": "SELL"}) + "\n"
        )
        result = load_decisions(f)
        assert len(result) == 2
        assert result[0]["symbol"] == "000001"

    def test_invalid_json_line_skipped(self, tmp_path: Path) -> None:
        """无效 JSON 行 -> 跳过，返回已解析部分。"""
        f = tmp_path / "mixed.jsonl"
        f.write_text(
            json.dumps({"symbol": "000001"}) + "\n"
            + "NOT JSON\n"
            + json.dumps({"symbol": "000002"}) + "\n"
        )
        result = load_decisions(f)
        assert len(result) == 2  # 无效行跳过


# ============================================================================
# run_precheck 测试
# ============================================================================
class TestRunPrecheck:
    """run_precheck 预检模式——skip vacuous-pass。"""

    def test_skip_mode_vacuous_pass(self) -> None:
        """skip 模式 -> 全部 vacuous-pass, allowed=True。"""
        result = run_precheck("skip")
        assert result.allowed is True
        assert len(result.blockers) == 0


# ============================================================================
# make_deployer 测试
# ============================================================================
class TestMakeDeployer:
    """make_deployer 工厂——windows/container/unknown。"""

    def test_windows(self, tmp_path: Path) -> None:
        """windows adapter -> WindowsProcessDeployer 实例。"""
        d = make_deployer("windows", ["python", "-c", "pass"], tmp_path / "out.jsonl", 1)
        assert isinstance(d, WindowsProcessDeployer)

    def test_container_raises_not_implemented(self, tmp_path: Path) -> None:
        """container adapter -> NotImplementedError（post-activation stub）。"""
        with pytest.raises(NotImplementedError):
            make_deployer("container", ["python", "-c", "pass"], tmp_path / "out.jsonl", 1)

    def test_unknown_raises_value_error(self, tmp_path: Path) -> None:
        """未知 adapter -> ValueError。"""
        with pytest.raises(ValueError):
            make_deployer("unknown", ["python", "-c", "pass"], tmp_path / "out.jsonl", 1)


# ============================================================================
# run_deploy 测试（mock 外部依赖）
# ============================================================================
class TestRunDeploy:
    """run_deploy 主流程——预检失败/promote/rollback/异常。"""

    @staticmethod
    def _make_prod_log(tmp_path: Path, decisions: list[dict]) -> str:
        """创建临时生产决策 jsonl 文件，返回路径。"""
        f = tmp_path / "prod_decisions.jsonl"
        lines = [json.dumps(d) for d in decisions]
        f.write_text("\n".join(lines) + ("\n" if lines else ""))
        return str(f)

    @patch("shadow_canary_deploy._write_report")
    @patch("shadow_canary_deploy.ShadowCanary")
    @patch("shadow_canary_deploy.CanaryRolloutManager")
    @patch("shadow_canary_deploy.make_deployer")
    @patch("shadow_canary_deploy.run_precheck")
    def test_precheck_fail_exit2(
        self, mock_precheck, mock_factory, mock_mgr, mock_shadow, mock_report, tmp_path: Path
    ) -> None:
        """预检失败 -> exit 2，不进入 shadow。"""
        mock_precheck.return_value = CanIDeployResult(
            allowed=False, checks={"health": False}, blockers=["health check failed"]
        )
        exit_code = run_deploy(
            baseline_ref="HEAD", duration=1, divergence_threshold=0.05,
            adapter="windows", shadow_cmd="python -c 'simulation pass'",
            production_log=self._make_prod_log(tmp_path, []),
            precheck_mode="full",
        )
        assert exit_code == EXIT_PRECHECK_FAIL
        mock_factory.assert_not_called()  # 预检失败不进入 shadow

    @patch("shadow_canary_deploy._write_report")
    @patch("shadow_canary_deploy.ShadowCanary")
    @patch("shadow_canary_deploy.CanaryRolloutManager")
    @patch("shadow_canary_deploy.make_deployer")
    @patch("shadow_canary_deploy.run_precheck")
    def test_promote_exit0(
        self, mock_precheck, mock_factory, mock_mgr, mock_shadow, mock_report, tmp_path: Path
    ) -> None:
        """预检通过 + 分歧 < 阈值 -> exit 0 (promote)。"""
        mock_precheck.return_value = CanIDeployResult(allowed=True, checks={}, blockers=[])
        decision = {"symbol": "000001", "timestamp": "t1", "side": "BUY", "quantity": 100, "price": 10.0}
        mock_deployer = MagicMock()
        mock_deployer.read_output.return_value = [decision]
        mock_factory.return_value = mock_deployer

        exit_code = run_deploy(
            baseline_ref="HEAD", duration=1, divergence_threshold=0.05,
            adapter="windows", shadow_cmd="python -c 'simulation pass'",
            production_log=self._make_prod_log(tmp_path, [decision]),
            precheck_mode="skip",
        )
        assert exit_code == EXIT_PROMOTE

    @patch("shadow_canary_deploy._write_report")
    @patch("shadow_canary_deploy.ShadowCanary")
    @patch("shadow_canary_deploy.CanaryRolloutManager")
    @patch("shadow_canary_deploy.make_deployer")
    @patch("shadow_canary_deploy.run_precheck")
    def test_rollback_exit1(
        self, mock_precheck, mock_factory, mock_mgr, mock_shadow, mock_report, tmp_path: Path
    ) -> None:
        """预检通过 + 分歧 >= 阈值 -> exit 1 (rollback)。"""
        mock_precheck.return_value = CanIDeployResult(allowed=True, checks={}, blockers=[])
        prod = {"symbol": "000001", "timestamp": "t1", "side": "BUY", "quantity": 100, "price": 10.0}
        shadow = {"symbol": "000001", "timestamp": "t1", "side": "SELL", "quantity": 100, "price": 10.0}
        mock_deployer = MagicMock()
        mock_deployer.read_output.return_value = [shadow]
        mock_factory.return_value = mock_deployer

        exit_code = run_deploy(
            baseline_ref="HEAD", duration=1, divergence_threshold=0.05,
            adapter="windows", shadow_cmd="python -c 'simulation pass'",
            production_log=self._make_prod_log(tmp_path, [prod]),
            precheck_mode="skip",
        )
        assert exit_code == EXIT_ROLLBACK

    @patch("shadow_canary_deploy._write_report")
    @patch("shadow_canary_deploy.ShadowCanary")
    @patch("shadow_canary_deploy.CanaryRolloutManager")
    @patch("shadow_canary_deploy.make_deployer")
    @patch("shadow_canary_deploy.run_precheck")
    def test_exception_exit2(
        self, mock_precheck, mock_factory, mock_mgr, mock_shadow, mock_report, tmp_path: Path
    ) -> None:
        """运行异常 -> exit 2 (fail-closed)。"""
        mock_precheck.return_value = CanIDeployResult(allowed=True, checks={}, blockers=[])
        mock_factory.side_effect = RuntimeError("deployer construction failed")

        exit_code = run_deploy(
            baseline_ref="HEAD", duration=1, divergence_threshold=0.05,
            adapter="windows", shadow_cmd="python -c 'simulation pass'",
            production_log=self._make_prod_log(tmp_path, []),
            precheck_mode="skip",
        )
        assert exit_code == EXIT_PRECHECK_FAIL  # fail-closed

    @patch("shadow_canary_deploy._write_report")
    @patch("shadow_canary_deploy.ShadowCanary")
    @patch("shadow_canary_deploy.CanaryRolloutManager")
    @patch("shadow_canary_deploy.make_deployer")
    @patch("shadow_canary_deploy.run_precheck")
    def test_both_empty_promote_exit0(
        self, mock_precheck, mock_factory, mock_mgr, mock_shadow, mock_report, tmp_path: Path
    ) -> None:
        """预检通过 + 双方皆空 -> divergence 0.0 -> exit 0 (vacuous promote)。"""
        mock_precheck.return_value = CanIDeployResult(allowed=True, checks={}, blockers=[])
        mock_deployer = MagicMock()
        mock_deployer.read_output.return_value = []  # shadow 空
        mock_factory.return_value = mock_deployer

        exit_code = run_deploy(
            baseline_ref="HEAD", duration=1, divergence_threshold=0.05,
            adapter="windows", shadow_cmd="python -c 'simulation pass'",
            production_log=self._make_prod_log(tmp_path, []),  # prod 空
            precheck_mode="skip",
        )
        assert exit_code == EXIT_PROMOTE  # vacuous promote
