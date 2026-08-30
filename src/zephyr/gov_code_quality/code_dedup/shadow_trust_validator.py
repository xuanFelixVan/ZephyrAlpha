# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.shadow_trust_validator
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/delegation/test_shadow_trust_validator.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
影子信任验证器 — ImportError 防护回路.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: shadow_trust_validator.py
# 层: 算法
# - id: A1
#   name_zh: ① ShadowTrustValidator
#   name_en: ShadowTrustValidator
#   intro: 影子清单信任链验证.
#   desc: 影子清单信任链验证.；公共方法（定义序）: validate_imports；源码 L51-L78
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ShadowTrustValidator
#   downstream: tests/governance/delegation/test_shadow_trust_validator.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from pathlib import Path


class ShadowTrustValidator:
    """影子清单信任链验证."""

    def validate_imports(self, manifest_functions: list[str], codebase_root: str | Path) -> dict:
        """验证影子清单中的导入在codebase中确实存在."""
        root = Path(codebase_root)
        missing = []
        verified = 0

        for fname in manifest_functions:
            found = False
            for py_file in root.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding="utf-8")
                    if fname in content:
                        found = True
                        verified += 1
                        break
                except (OSError, UnicodeDecodeError):
                    pass
            if not found:
                missing.append(fname)

        return {
            "verified": verified,
            "missing": len(missing),
            "missing_functions": missing[:10],
        }
