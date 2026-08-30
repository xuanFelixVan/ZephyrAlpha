# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.pre_apply_integrity_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/governance/code_dedup/test_pre_apply_integrity_gate.py
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Pre-Apply 完整性门 — SHA256重新验证.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: pre_apply_integrity_gate.py
# 层: 算法
# - id: A1
#   name_zh: ① PreApplyIntegrityGate
#   name_en: PreApplyIntegrityGate
#   intro: 修复前完整性门.
#   desc: 修复前完整性门.；公共方法（定义序）: verify；源码 L52-L64
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: PreApplyIntegrityGate
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import hashlib
from pathlib import Path


class PreApplyIntegrityGate:
    """修复前完整性门."""

    def verify(self, file_path: str | Path, expected_sha256: str) -> tuple[bool, str]:
        """对即将修改的文件做SHA256验证——不匹配->ABORT."""
        path = Path(file_path)
        if not path.exists():
            return False, "FILE_NOT_FOUND"

        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected_sha256:
            return False, f"SHA_MISMATCH: expected={expected_sha256[:16]}... actual={actual[:16]}..."
        return True, "SHA256_OK"
