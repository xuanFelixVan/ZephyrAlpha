# [BLUEPRINT] MOD-GOV-SCRIPTS
# [MODULE] scripts.governance._shared.frontmatter
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS] scripts.governance.d5_architecture.validators.validate_ssot; tests.unit.test_drafts_zone_archiver_unit; tests.unit.test_validate_blueprint_overlap_unit; tests.unit.test_validate_ssot_unit; tests.unit.governance.test_drafts_zone_archiver_governance; tests.unit.governance.test_validate_ssot_governance
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
import yaml


def parse_frontmatter(text_or_path):
    if isinstance(text_or_path, str) and len(text_or_path) < 260 and "\n" not in text_or_path:
        try:
            with open(text_or_path, encoding="utf-8") as f:
                text = f.read()
        except OSError:
            text = str(text_or_path)
    else:
        text = str(text_or_path)
    metadata = {}
    body = text
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            try:
                metadata = yaml.safe_load(text[3:end]) or {}
            except Exception:
                metadata = {}
            body = text[end + 3 :].lstrip("\n")
    return metadata, body


def parse_frontmatter_from_file(filepath):
    with open(filepath, encoding="utf-8") as f:
        text = f.read()
    return parse_frontmatter(text)
