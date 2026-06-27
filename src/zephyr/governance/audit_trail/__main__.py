# [BLUEPRINT] MOD-INF-027 | docs/03_modules/_cross_layer/audit_orchestrator/blueprint.md | §4
# [MODULE] zephyr.governance.audit_trail.__main__
# [DOMAIN] D-GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_trail.cli
# [CONSUMERS] End users; CI/CD
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] python -m zephyr.governance.audit_trail is the ONLY CLI entry
# [MODIFY-GUARD] Changes MUST delegate to cli.main()
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SystemExit from cli.main()
# [TESTS] None
# [A_module] module_id=MOD-GOV___main__ | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from zephyr.governance.audit_trail.cli import main

if __name__ == "__main__":
    main()
