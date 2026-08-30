# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.behavioral_trust_checker
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/delegation/test_behavioral_trust_checker.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
行为信任检查器 — 行为漂移DIVERGED检测.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: behavioral_trust_checker.py
# 层: 算法
# - id: A1
#   name_zh: ① BehavioralTrustChecker
#   name_en: BehavioralTrustChecker
#   intro: 行为正确性检查.
#   desc: 行为正确性检查.；公共方法（定义序）: signatures, register, verify；源码 L62-L107
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: BehavioralTrustChecker
#   downstream: tests/governance/delegation/test_behavioral_trust_checker.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class TrustCheck:
    function_name: str = ""
    behavior_signature: str = ""
    current_hash: str = ""
    original_hash: str = ""
    trusted: bool = False
    status: str = "TRUSTED"


class BehavioralTrustChecker:
    """行为正确性检查."""

    def __init__(self) -> None:
        self._signatures: dict[str, str] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def signatures(self) -> dict[str, str]:
        """只读：signatures（Stage 4 公共化）。"""
        return self._signatures

    @signatures.setter
    def signatures(self, value):
        """写入：signatures（Stage 4 公共化）。"""
        self._signatures = value

    def register(self, function_name: str, behavior_signature: str) -> None:
        self._signatures[function_name] = behavior_signature

    def verify(self, function_name: str, current_behavior: str) -> TrustCheck:
        original = self._signatures.get(function_name)
        if original is None:
            return TrustCheck(
                function_name=function_name,
                current_hash=current_behavior,
                trusted=True,
                status="UNTRACKED",
            )
        if current_behavior == original:
            return TrustCheck(
                function_name=function_name,
                behavior_signature=original,
                current_hash=current_behavior,
                original_hash=original,
                trusted=True,
                status="TRUSTED",
            )
        return TrustCheck(
            function_name=function_name,
            behavior_signature=original,
            current_hash=current_behavior,
            original_hash=original,
            trusted=False,
            status="DIVERGED",
        )
