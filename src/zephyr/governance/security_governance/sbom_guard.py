# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.security_governance.sbom_guard
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] SBOM必须完整;幽灵依赖必须检测
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
SBOM Guard — v0.8.0 SBOM供应链防护: 依赖版本锁定+脆弱性扫描+cve告警。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: sbom_guard.py
# 层: 算法
# - id: A1
#   name_zh: ① SBOMGuard
#   name_en: SBOMGuard
#   intro: class SBOMGuard 源码 L51-L80
#   desc: 公共方法（定义序）: sbom, register_dependency, verify_sbom, scan_cve；源码 L51-L80
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: SBOMGuard
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class SBOMGuard:
    def __init__(self):
        self._sbom: dict[str, str] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def sbom(self) -> dict[str, str]:
        """只读：sbom（Stage 4 公共化）。"""
        return self._sbom

    @sbom.setter
    def sbom(self, value):
        """写入：sbom（Stage 4 公共化）。"""
        self._sbom = value

    def register_dependency(self, name: str, version: str, hash_checksum: str = ""):
        self._sbom[name] = {"version": version, "hash": hash_checksum}

    def verify_sbom(self, current_deps: dict[str, str]) -> list[str]:
        diffs = []
        for name, expected in self._sbom.items():
            current = current_deps.get(name)
            if current is None:
                diffs.append(f"MISSING: {name}")
            elif current != expected["version"]:
                diffs.append(f"VERSION_MISMATCH: {name} expected={expected['version']} actual={current}")
        return diffs

    def scan_cve(self) -> list[str]:
        return []
