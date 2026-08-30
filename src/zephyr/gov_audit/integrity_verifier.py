# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.gov_audit.integrity_verifier
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 启动链验证不可跳过;源码hash必须匹配
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Integrity Verifier — v0.8.0 代码完整性验证器: hash校验+diff detection+rollback。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: integrity_verifier.py
# 层: 算法
# - id: A1
#   name_zh: ① IntegrityVerifier
#   name_en: IntegrityVerifier
#   intro: class IntegrityVerifier 源码 L53-L82
#   desc: 公共方法（定义序）: hashes, register_hash, verify, diff_files；源码 L53-L82
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: IntegrityVerifier
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib


class IntegrityVerifier:
    def __init__(self):
        self._hashes: dict[str, str] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def hashes(self) -> dict[str, str]:
        """只读：hashes（Stage 4 公共化）。"""
        return self._hashes

    @hashes.setter
    def hashes(self, value):
        """写入：hashes（Stage 4 公共化）。"""
        self._hashes = value

    def register_hash(self, filepath: str, content: str):
        self._hashes[filepath] = hashlib.sha256(content.encode()).hexdigest()

    def verify(self, filepath: str, content: str) -> bool:
        expected = self._hashes.get(filepath)
        if expected is None:
            return True
        current = hashlib.sha256(content.encode()).hexdigest()
        return current == expected

    def diff_files(self, filepath: str, old_content: str, new_content: str) -> list[str]:
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()
        diffs = [f"+{l}" for l in new_lines if l not in old_lines] + [f"-{l}" for l in old_lines if l not in new_lines]
        return diffs[:50]
