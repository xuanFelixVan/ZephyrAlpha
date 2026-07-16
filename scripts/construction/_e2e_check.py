# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
# [MODULE] scripts.construction._e2e_check
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.construction.check_statuses
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
import importlib
import re
import sys
from pathlib import Path

import yaml

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

ROOT = REPO_ROOT  # alias 真源
sys.path.insert(0, str(ROOT / "src"))

with open(ROOT / "docs/03_modules/blueprint_registry.yaml", encoding="utf-8") as f:
    reg = yaml.safe_load(f)

results = []

for bp in reg.get("blueprints", []):
    mid = bp.get("module_id", "")
    if bp.get("belongs_to"):
        continue

    cp = bp.get("construction_progress", "")
    layer = bp.get("layer", "")
    fp = bp.get("file_path", "")

    entry = {
        "module_id": mid,
        "progress": cp,
        "layer": layer,
        "code_path": "",
        "code_exists": False,
        "import_ok": False,
        "import_error": "",
        "key_classes": [],
        "missing_classes": [],
    }

    with open(ROOT / "docs" / fp, encoding="utf-8") as f:
        text = f.read()
    fm_match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    fm = yaml.safe_load(fm_match.group(1)) if fm_match else {}

    adp = fm.get("actual_disk_path", "")
    if not adp:
        adp = str(bp.get("file_path", "")).replace("03_modules/", "").replace("/blueprint.md", "")
        adp = "docs/03_modules/" + adp.rsplit("/", 1)[0] if "/" in bp.get("file_path", "") else ""

    code_paths = []
    if adp and adp.startswith("src/"):
        code_paths = [p.strip() for p in adp.split("+")]

    if not code_paths:
        code_path_str = ""
        for line in text.split("\n"):
            if "src/zephyr/" in line and "path" in line.lower():
                m = re.search(r"(src/zephyr/[a-z0-9_/]+)", line)
                if m:
                    code_path_str = m.group(1)
                    break

    if not code_paths and code_path_str:
        code_paths = [code_path_str]

    entry["code_path"] = " + ".join(code_paths) if code_paths else "N/A"

    for cp_item in code_paths:
        disk = ROOT / cp_item.strip()
        if disk.exists():
            entry["code_exists"] = True
            break

    if entry["code_exists"] and code_paths:
        primary = code_paths[0].strip().replace("src/", "").replace("/", ".").rstrip(".")
        try:
            mod = importlib.import_module(primary)
            entry["import_ok"] = True

            exports = []
            if hasattr(mod, "__all__"):
                exports = mod.__all__
            else:
                exports = [n for n in dir(mod) if not n.startswith("_") and n[0].isupper()]

            entry["key_classes"] = exports[:10]

            key_names = []
            for line in text.split("\n"):
                m = re.match(r"^\s*-\s*(?:class|interface):\s*(\w+)", line)
                if m:
                    key_names.append(m.group(1))

            for kn in key_names[:5]:
                if not hasattr(mod, kn):
                    entry["missing_classes"].append(kn)

        except Exception as e:
            entry["import_error"] = str(e)[:120]

    results.append(entry)

print(f"Total blueprints: {len(results)}")
print(f"Code exists: {sum(1 for r in results if r['code_exists'])}")
print(f"Import OK: {sum(1 for r in results if r['import_ok'])}")
print(f"Import FAIL: {sum(1 for r in results if r['code_exists'] and not r['import_ok'])}")
print(f"No code (design_only/N/A): {sum(1 for r in results if not r['code_exists'])}")
print()

for r in results:
    status = ""
    if not r["code_exists"]:
        status = "NO_CODE"
    elif r["import_ok"]:
        missing = ", missing: " + str(r["missing_classes"]) if r["missing_classes"] else ""
        status = "OK" + missing
    else:
        status = "FAIL: " + r["import_error"][:80]

    print(f"  {r['module_id']:20s} | {r['progress']:20s} | {status}")
