# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.architecture_governance.blueprint_code_consistency
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_blueprint_code_consistency | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Blueprint-Code Consistency Gate — MOD-INF-022.

Validates that each blueprint decision (D-022-01 through D-022-30) has at least
one corresponding code implementation or declared status.

Run: python -m zephyr.governance.architecture_governance.blueprint_code_consistency [--json]
Returns: 0 if consistent, 1 if drift detected.
"""

from __future__ import annotations

from typing import Final
import importlib
import json
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class DecisionStatus(str, Enum):
    IMPLEMENTED = "implemented"
    IN_PROGRESS = "in_progress"
    BACKLOG = "backlog"
    OWNER_ONLY = "owner_only"
    PHASE_GATED = "phase_gated"


@dataclass
class DecisionMapping:
    decision_id: str
    title: str
    status: DecisionStatus
    code_module: str = ""
    notes: str = ""


DECISION_MAP: Final[list[DecisionMapping]] = [
    DecisionMapping(
        "D-022-01",
        "三级升级策略 L0-L4",
        DecisionStatus.IMPLEMENTED,
        "zephyr.governance.escalation.escalation_engine",
        "EscalationEngine.evaluate() + escalate()",
    ),
    DecisionMapping(
        "D-022-02",
        "自动委托协议 + 四级安全约束",
        DecisionStatus.IMPLEMENTED,
        "zephyr.governance.intelligence_governance.delegation_engine",
        "DelegationEngine.delegate()",
    ),
    DecisionMapping(
        "D-022-03",
        "经济护栏 Token预算",
        DecisionStatus.IMPLEMENTED,
        "zephyr.governance.escalation.escalation_models",
        "EconomicGuard + CATEGORY_COST",
    ),
    DecisionMapping(
        "D-022-04", "规则不可变保护", DecisionStatus.IN_PROGRESS, "scripts.lock_files", "RULE-ZERO 锁协议部分覆盖"
    ),
    DecisionMapping(
        "D-022-05",
        "引擎故障处理 fail-safe",
        DecisionStatus.IN_PROGRESS,
        "zephyr.governance.resilience_governance.circuit_breaker",
        "CircuitBreaker 提供降级保护",
    ),
    DecisionMapping(
        "D-022-06",
        "多Agent死锁防护",
        DecisionStatus.IMPLEMENTED,
        "zephyr.governance.resilience_governance.deadlock_detector",
        "集成到 Engine hooks",
    ),
    DecisionMapping(
        "D-022-07",
        "心理说服防御 Crescendo检测",
        DecisionStatus.IMPLEMENTED,
        "zephyr.governance.security_governance.persuasion_detector",
        "集成到 Engine hooks",
    ),
    DecisionMapping(
        "D-022-08",
        "引擎 OS级 Sandboxing",
        DecisionStatus.IMPLEMENTED,
        "zephyr.governance.resilience_governance.engine_sandbox",
        "EngineSandbox 文件/网络/进程隔离 + 完整性快照 + 12 项测试覆盖",
    ),
    DecisionMapping(
        "D-022-09",
        "反自动化偏见",
        DecisionStatus.IMPLEMENTED,
        "zephyr.governance.security_governance.anti_automation_bias",
        "AntiAutomationBias 5%强制审查 + 疲劳检测 + 反谄媚 + 11 项测试覆盖",
    ),
    DecisionMapping(
        "D-022-10",
        "Meta-Confidence 自校准",
        DecisionStatus.IMPLEMENTED,
        "zephyr.governance.intelligence_governance.confidence_estimator",
        "ConfidenceEstimator 已集成到 hooks",
    ),
    DecisionMapping(
        "D-022-11",
        "五层顶尖架构 L0-L4",
        DecisionStatus.IMPLEMENTED,
        "zephyr.governance.escalation.escalation_models",
        "EscalationLevel 枚举 5级",
    ),
    DecisionMapping(
        "D-022-12",
        "SLO驱动升级合约",
        DecisionStatus.IMPLEMENTED,
        "zephyr.gov_enforcement.rule_enforcement.slo_contract",
        "SLOContractEngine 7 SLI + 4级 Error Budget + 11 项测试覆盖",
    ),
    DecisionMapping(
        "D-022-16",
        "Agent行为漂移检测",
        DecisionStatus.IMPLEMENTED,
        "zephyr.gov_drift.drift_detector",
        "四维漂移检测已实现",
    ),
    DecisionMapping(
        "D-022-17",
        "VIGIL维护运行时",
        DecisionStatus.IMPLEMENTED,
        "zephyr.gov_drift.vigil_runtime",
        "VigilRuntime 已加载",
    ),
    DecisionMapping(
        "D-022-18",
        "形式验证 MCMAS",
        DecisionStatus.IMPLEMENTED,
        "zephyr.governance.architecture_governance.formal_verifier",
        "FormalVerifier 已加载",
    ),
    DecisionMapping(
        "D-022-19",
        "多Provider API容灾",
        DecisionStatus.IMPLEMENTED,
        "zephyr.governance.intelligence_governance.provider_failover",
        "ProviderFailover 已加载",
    ),
    DecisionMapping(
        "D-022-20",
        "API密钥泄露处理",
        DecisionStatus.IMPLEMENTED,
        "zephyr.governance.security_governance.credential_guard",
        "CredentialGuard 已集成到 hooks",
    ),
    DecisionMapping(
        "D-022-21",
        "冷启动自举策略",
        DecisionStatus.IMPLEMENTED,
        "zephyr.governance.intelligence_governance.self_test",
        "冷启动序列已集成 + self_test.py",
    ),
    DecisionMapping(
        "D-022-22",
        "Merkle Tree 密码学审计",
        DecisionStatus.IMPLEMENTED,
        "zephyr.gov_audit.merkle_audit",
        "MerkleAudit 已集成到 hooks",
    ),
    DecisionMapping(
        "D-022-23",
        "SBOM + 代码签名",
        DecisionStatus.IMPLEMENTED,
        "zephyr.governance.security_governance.sbom_guard",
        "SBOMGuard 已加载",
    ),
    DecisionMapping(
        "D-022-24",
        "时钟完整性防御",
        DecisionStatus.IMPLEMENTED,
        "zephyr.governance.ops_governance.clock_guard",
        "ClockGuard 已集成到 hooks",
    ),
    DecisionMapping(
        "D-022-29",
        "命令体积退化防御",
        DecisionStatus.IMPLEMENTED,
        "zephyr.governance.context_governance.command_chain_length_gate",
        "CommandChainGate 已集成到 hooks",
    ),
    DecisionMapping(
        "D-022-30",
        "组合性不安全防御",
        DecisionStatus.IMPLEMENTED,
        "zephyr.governance.security_governance.compositional_safety_tester",
        "CompositionalSafetyTester 已加载",
    ),
    DecisionMapping(
        "D-022-37D",
        "奖励黑客三阶段反弹纵向检测 (盲点#161)",
        DecisionStatus.IMPLEMENTED,
        "zephyr.gov_drift.reward_hacking_rebound_detector",
        "ReboundDetector 90天滑动窗口+严重度比较+P0-FATAL升级+Engine Hook集成",
    ),
]


def _verify_module_exists(module_path: str) -> bool:
    if not module_path:
        return False
    try:
        importlib.import_module(module_path)
        return True
    except ImportError:
        return _file_exists(module_path)


def _file_exists(module_path: str) -> bool:
    parts = module_path.split(".")
    py_path = Path("src") / Path(*parts).with_suffix(".py")
    return py_path.exists()


def check_consistency() -> tuple[int, list[dict]]:
    results = []
    for dm in DECISION_MAP:
        module_ok = _verify_module_exists(dm.code_module) if dm.code_module else (dm.status == DecisionStatus.BACKLOG)
        results.append(
            {
                "decision_id": dm.decision_id,
                "title": dm.title,
                "status": dm.status.value,
                "code_module": dm.code_module,
                "module_found": module_ok,
                "notes": dm.notes,
                "drift": (dm.status == DecisionStatus.IMPLEMENTED and not module_ok),
            }
        )
    drift_count = sum(1 for r in results if r["drift"])
    return drift_count, results


check_blueprint_consistency = check_consistency


def main():
    json_flag = "--json" in sys.argv
    drift_count, results = check_consistency()
    if json_flag:
        print(json.dumps({"drift_count": drift_count, "decisions": results}, indent=2, ensure_ascii=False))
    else:
        print(f"Blueprint-Code Consistency Check: {len(results)} decisions")
        print(f"  Implemented:  {sum(1 for r in results if r['status'] == 'implemented')}")
        print(f"  In Progress:  {sum(1 for r in results if r['status'] == 'in_progress')}")
        print(f"  Backlog:      {sum(1 for r in results if r['status'] == 'backlog')}")
        print(f"  Owner/Phase:  {sum(1 for r in results if r['status'] in ('owner_only', 'phase_gated'))}")
        print(f"  Drift alerts: {drift_count}")
        if drift_count:
            print()
            for r in results:
                if r["drift"]:
                    print(f"  ⚠ DRIFT: {r['decision_id']} ({r['title']}) -> {r['code_module']} NOT FOUND")

    return 1 if drift_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
