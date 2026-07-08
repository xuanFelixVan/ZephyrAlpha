from typing import Final

# [BLUEPRINT] SRC-020 | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.governance.behavioral_admission.ai_code_standards
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_ai_code_standards | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

CODE_CONVENTIONS: Final[dict[str, str]] = {
    "file_org": "按YAML约定abord",
    "scaffold": "python setup+page=模板自动生成",
    "header": "Python: shebang+path",
    "comments": "no justification/no redundant->code self-document->majors only",
    "imports": "future->stdlib->3rd->local+isort",
    "type_hints": "全部public函数must",
}

AI_FORBIDDEN: Final[list[str]] = [
    "禁止生成注释in demo/example",
    "测试必须Fail(TDD mode)->pass=bad",
]
