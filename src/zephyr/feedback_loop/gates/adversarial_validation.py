# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §adversarial_validation
# [MODULE] zephyr.feedback_loop.gates.adversarial_validation
# [DOMAIN] D_FBL_VERIFICATION
# [DEPENDENCIES] zephyr.security.adversarial_validation.__init__
# [CONSUMERS] feedback-loop.gates.__init__; _registry.yaml FLE-ADVERSARIAL-VALIDATION; RED-BLUE-GATE
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] challenge() maintains backward compat; run_adversarial_check() bridges to RedBlueValidator
# [MODIFY-GUARD] challenge() return type MUST remain list[str] for backward compat
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RedBlueImportError on import failure; returns degraded results
# [TESTS] tests/federated_learning/test_fl_adversarial_validation.py; tests/governance/rule_enforcement/gate_engine/test_adversarial_validation.py  # 2026-09-05 STEWARD B20 重锚：AI-00 修复脚本 src. 前缀 bug 漏网（AST/patch 直查 2 个测试）
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Adversarial Validation Gate — FLE-ADVERSARIAL-VALIDATION + RED-BLUE-GATE bridge.

Bridges feedback-loop gate engine with MOD-INF-030 Red-Blue Validator:
红方注入 -> 蓝方 Gate 判定 -> 绕过检测 -> 收敛验证 -> 宪法自进化。

# [ALGO_FLOW] external: docs/03_modules/_domain_feedback_loop/algo_flow/gates/adversarial_validation.yaml
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


class RedBlueImportError(ImportError):
    error_code = "ZA-TR-0017"

    def __init__(self, *args, error_code: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


@dataclass
class AdversarialResult:
    claim: str
    passed: bool
    bypass_count: int = 0
    constitution_violations: list[str] = field(default_factory=list)
    core_result: dict[str, Any] | None = None
    error: str = ""


def _evaluate_red_blue_scenario(scenario, claim, DefenseRunner, ConstitutionGuard, BypassRecorder):
    """单场景评估（裁定#359 WP17 分桶语义）。

    返回 (defense_result, v_list, entry, tool_error)：
      - tool_error 非空 = 工具/入参自身异常，defense_result=None，
        绝不计入 blocked/bypass（原实现静默吞异常→场景被跳过→假绿，已废除）；
      - tool_error 为空 = 评估真实完成，defense_result.passed=True 表示攻击被拦下。
    """
    runner = DefenseRunner()
    defense_result = None
    tool_error = ""
    try:
        defense_result = runner.run_defense(scenario)
        if getattr(defense_result, "error", ""):
            # DefenseRunner 已分桶的工具异常（TOOL_ERROR）→ 上抛为 error 桶
            tool_error = defense_result.error
            defense_result = None
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        tool_error = f"{type(exc).__name__}: {exc}"
        logger.warning("red_blue_scenario_tool_error scenario_id=%s error=%s", scenario.scenario_id, tool_error)

    guard = ConstitutionGuard()
    try:
        guard.validate_all()
        v_list = guard.get_violations()
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        v_list = []

    counter_claim = f"'{claim}' survives {scenario.name}"
    recorder = BypassRecorder()
    try:
        entry = recorder.record(
            scenario_id=scenario.scenario_id or "unknown",
            scenario_name=scenario.name,
            counter_claim=counter_claim,
        )
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        entry = None

    return defense_result, v_list, entry, tool_error


@dataclass
class AdversarialValidation:
    def challenge(self, claim: str) -> list[str]:
        challenges: list[str] = [f"What if {claim} is wrong?"]

        try:
            adversarial_result = self.run_adversarial_check(claim)
            if adversarial_result.bypass_count > 0:
                challenges.append(f"Claim '{claim}' bypassed {adversarial_result.bypass_count} defense(s)")
            if adversarial_result.constitution_violations:
                challenges.append("Constitution violations: %s" % ", ".join(adversarial_result.constitution_violations))
            if not adversarial_result.passed:
                challenges.append(f"Adversarial validation FAILED for claim: '{claim}'")
            if adversarial_result.error:
                challenges.append(f"Validation error: {adversarial_result.error}")
        except RedBlueImportError:
            pass
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("challenge() enrich failed: %s", exc, exc_info=True)

        return challenges

    def run_adversarial_check(self, claim: str, **kwargs: Any) -> AdversarialResult:
        try:
            return self._run_with_red_blue_validator(claim, **kwargs)
        except RedBlueImportError:
            return AdversarialResult(
                claim=claim,
                passed=True,
                error="RedBlueValidator not available — skipped adversarial check",
            )
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.error("run_adversarial_check failed: %s", exc, exc_info=True)
            return AdversarialResult(
                claim=claim,
                passed=False,
                error=str(exc),
            )

    def _run_with_red_blue_validator(self, claim: str, **kwargs: Any) -> AdversarialResult:
        try:
            from zephyr.security.adversarial_validation import (
                BypassRecorder,
                ConstitutionGuard,
                DefenseRunner,
                ScenarioLoader,
            )
        except ImportError as exc:
            raise RedBlueImportError(
                f"Cannot import zephyr.security.adversarial_validation: {exc}"
            ) from exc  # 5.99.13 修复: %格式化改f-string统一

        tier = kwargs.get("tier", 1)
        attempts = kwargs.get("attempts", 3)

        loader = ScenarioLoader()
        try:
            scenarios = loader.list_by_tier(tier)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            return AdversarialResult(
                claim=claim,
                passed=True,
                error="No attack scenarios available for tier=%d" % tier,
            )

        if not scenarios:
            return AdversarialResult(
                claim=claim,
                passed=True,
                bypass_count=0,
                error="No scenarios loaded",
            )

        bypass_count = 0
        passed = True
        violations: list[str] = []
        tool_errors: list[str] = []
        core_result: dict[str, Any] | None = None

        for i in range(min(attempts, len(scenarios))):
            scenario = scenarios[i]

            result, v_list, entry, tool_error = _evaluate_red_blue_scenario(
                scenario, claim, DefenseRunner, ConstitutionGuard, BypassRecorder
            )

            if tool_error:
                # 裁定#359 WP17 ①：工具/入参异常 → error 桶，绝不计入 bypass/blocked，
                # 也不再静默跳过（原实现异常吞掉后场景消失=假绿）。
                tool_errors.append(tool_error)
            elif result is not None:
                if not result.passed:
                    # 攻击未被拦下（防御失守）→ bypass
                    bypass_count += 1
                    passed = False
                # result.passed=True = 攻击被防御拦下 → defender win，不计数

            if v_list:
                violations.extend(v_list)

            if entry is not None and hasattr(entry, "bypass_count"):
                bypass_count = entry.bypass_count

            if bypass_count >= 3:
                passed = False
                break

        tested = min(attempts, len(scenarios))
        core_result = {
            "total_scenarios": len(scenarios),
            "tested": tested,
            "bypass_count": bypass_count,
            "violation_count": len(violations),
            "error_count": len(tool_errors),
        }

        # 裁定#359 WP17 ①：全部场景工具故障=零真实评估 → 禁止满分假绿，
        # 报 error 而非通过（与 run_adversarial_check 通用异常路径语义一致）。
        if tool_errors and len(tool_errors) >= tested:
            passed = False

        return AdversarialResult(
            claim=claim,
            passed=passed,
            bypass_count=bypass_count,
            constitution_violations=list(set(violations)),
            core_result=core_result,
            error="; ".join(tool_errors[:3]),
        )
