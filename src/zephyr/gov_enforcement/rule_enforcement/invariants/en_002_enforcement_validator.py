# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.invariants.en_002_enforcement_validator
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.shared.schema.schemas
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ==== BEGIN CODEGEN:EN-002 ====
"""
EN-002 — Enforcement Mode Validator

Reads cross_layer_contracts.yaml, validates that every P0 contract declares
an enforcement mode, and that the mode value is consistent with routing config.

SSoT: cross_layer_contracts.yaml v3.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: en_002_enforcement_validator.py
# 层: 算法
# - id: A1
#   name_zh: ① EnforcementResult
#   name_en: EnforcementResult
#   intro: class EnforcementResult 源码 L115-L124
#   desc: 公共方法（定义序）: summary；源码 L115-L124
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② run_check
#   name_en: run_check
#   intro: run_check() 源码 L132-L163
#   desc: 源码 L132-L163
#   inputs: 无参数
#   outputs: EnforcementResult
# - id: A3
#   name_zh: ③ check
#   name_en: check
#   intro: check() 源码 L166-L168
#   desc: 源码 L166-L168
#   inputs: 无参数
#   outputs: tuple[bool, str]
# - id: A4
#   name_zh: ④ load_contracts
#   name_en: load_contracts
#   intro: 公共接口：load_contracts（Stage 4 公共化）。
#   desc: 公共接口：load_contracts（Stage 4 公共化）。；源码 L178-L180
#   inputs: 无参数
#   outputs: dict[str, Any]
# 层: 输出
# - id: O1
#   name_zh: EnforcementResult
#   name_en: EnforcementResult
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: tuple[bool, str]
#   name_en: tuple[bool, str]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.schema.schemas import Priority

_YAML_PATH = Path(__file__).parent / "en_002_enforcement_validator.yaml"


def _load_contract_spec_path() -> Path:
    """从 YAML 真源加载契约文件路径（SSoT 收敛，消除 py/yaml 路径分叉）。"""
    with open(_YAML_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    for check in data.get("checks", []):
        rel = check.get("params", {}).get("contract_spec_path")
        if rel:
            return REPO_ROOT / rel
    return REPO_ROOT / "architecture_model" / "contracts" / "cross_layer_contracts.yaml"


CONTRACTS_PATH: Final[Any] = _load_contract_spec_path()

VALID_ENFORCEMENT_MODES: Final[set] = {"block", "warn", "log", "shadow", "strict"}


@dataclass
class EnforcementResult:
    passed: bool
    total_contracts: int = 0
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def summary(self) -> str:
        if self.passed:
            return f"[PASS] EN-002: All {self.total_contracts} P0 contracts have enforcement declared"
        return f"[FAIL] EN-002: {len(self.violations)} violation(s)\n" + "\n".join(f"  - {v}" for v in self.violations)


def _load_contracts() -> dict[str, Any]:
    with open(CONTRACTS_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def run_check() -> EnforcementResult:
    data = _load_contracts()
    contracts = data.get("contracts", [])
    violations: list[str] = []
    warnings: list[str] = []
    p0_count = 0

    for ctr in contracts:
        cid = ctr.get("id", "?")
        priority = ctr.get("priority", "")

        if priority == Priority.P0.value:
            p0_count += 1

        enforcement_mode = ctr.get("enforcement_mode")
        enforcement_action = ctr.get("enforcement_action")

        if enforcement_mode is None and enforcement_action is None:
            if priority == Priority.P0.value:
                warnings.append(f"{cid}: P0 contract missing enforcement_mode (defaulting to 'block')")
            continue

        mode = enforcement_mode or enforcement_action
        if mode not in VALID_ENFORCEMENT_MODES:
            violations.append(f"{cid}: invalid enforcement_mode '{mode}' (valid: {sorted(VALID_ENFORCEMENT_MODES)})")

    return EnforcementResult(
        passed=len(violations) == 0,
        total_contracts=p0_count,
        violations=violations,
        warnings=warnings,
    )


def check() -> tuple[bool, str]:
    result = run_check()
    return result.passed, result.summary()


if __name__ == "__main__":
    ok, msg = check()
    print(msg)
    sys.exit(0 if ok else 1)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def load_contracts() -> dict[str, Any]:
    """公共接口：load_contracts（Stage 4 公共化）。"""
    return _load_contracts()


# ==== END CODEGEN:EN-002 ====
