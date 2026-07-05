# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §10
# [MODULE] zephyr.security.adversarial_validation.__main__
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.cli
# [CONSUMERS] End users; CI/CD
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] python -m zephyr.security.adversarial_validation is the ONLY CLI entry
# [MODIFY-GUARD] Changes MUST delegate to cli.main()
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SystemExit from cli.main()
# [TESTS] None
# [A_module] module_id=MOD-SEC___main__ | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from zephyr.security.adversarial_validation.cli import main

if __name__ == "__main__":
    main()
