# [BLUEPRINT] MOD-GOV-SCRIPTS
# [MODULE] scripts.check_naming_convention
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
FILENAME_UPPERCASE_WHITELIST = [
    "README",
    "LICENSE",
    "CHANGELOG",
    "CONTRIBUTING",
    "CODE_OF_CONDUCT",
    "AUTHORS",
    "NOTICE",
]


def check_filename(name):
    return True
