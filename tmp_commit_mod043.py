# -*- coding: utf-8 -*-
"""临时脚本：统一灾备备份module_id为MOD-INF-043并提交"""
import sys
from pathlib import Path

root = Path(r"d:\ZephyrAlpha")

def replace_in_file(relpath, old, new):
    p = root / relpath
    content = p.read_text(encoding="utf-8")
    if old not in content:
        print(f"  WARN: pattern not found in {relpath}")
        return False
    content = content.replace(old, new)
    p.write_text(content, encoding="utf-8")
    return True

# 1. 6个脚本文件: MOD-INF-027 -> MOD-INF-043
script_files = [
    "scripts/backup/backup_config.yaml",
    "scripts/backup/backup_reconciler.py",
    "scripts/backup/backup.ps1",
    "scripts/backup/backup_manual.ps1",
    "scripts/backup/restore.ps1",
    "scripts/backup/README.md",
]
for f in script_files:
    replace_in_file(f, "MOD-INF-027", "MOD-INF-043")
    print(f"  OK: {f}")

# 2. blueprint.md: frontmatter MOD-INF-040->043, body MOD-INF-027->043
bp = "docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md"
replace_in_file(bp, "module_id: MOD-INF-040", "module_id: MOD-INF-043")
replace_in_file(bp, "MOD-INF-027", "MOD-INF-043")
print(f"  OK: {bp}")

# 3. blueprint_registry.yaml: block replacement
br = "docs/03_modules/blueprint_registry.yaml"
old_block = """- module_id: MOD-INF-040
  name: disaster_recovery_backup
  title: \u707e\u5907\u5907\u4efd\u7cfb\u7edf\u84dd\u56fe \u2014 \u4e8b\u4ef6\u89e6\u53d1\u2192DB dump\u2192Restic\u53bb\u91cd\u5907\u4efd\u2192\u4fdd\u7559\u6e05\u7406\u2192\u6821\u9a8c\u2192\u62a5\u544a
  summary: \u707e\u5907\u5907\u4efd\u7cfb\u7edf\u2014\u2014\u4e8b\u4ef6\u89e6\u53d1\u7684Restic\u53bb\u91cd\u5907\u4efd\u6d41\u6c34\u7ebf\uff0cpost-commit reconciler\u81ea\u52a8\u9a71\u52a8\uff08\u91cd\u8981\u6587\u4ef6\u53d8\u66f4+8\u5c0f\u65f6\u95f4\u9694\u4fdd\u62a4\uff0c\u65e5\u57471-2\u6b21\uff09\uff0c\u8986\u76d6\u4ee3\u7801+\u914d\u7f6e+\u6570\u636e\u5e93+\u4e0d\u53ef\u66ff\u4ee3\u6570\u636e\uff0c\u76ee\u6807\u76d8F:(SanDisk
    2TB)\uff0c\u9075\u5faa3-2-1\u539f\u5219\u4e0e\u6570\u636e\u6700\u5c0f\u5316\u539f\u5219
  layer: L0_infrastructure
  functional_domain: operations
  blueprint_status: Active
  blueprint_level: module
  priority: P1
  version: 1.1.0
  generation: 1
  last_updated: '2026-07-09'
  file_path: 03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md
  construction_progress: not_started"""
new_block = """- module_id: MOD-INF-043
  name: disaster_recovery_backup
  title: \u707e\u5907\u5907\u4efd\u7cfb\u7edf\u84dd\u56fe \u2014 \u4e8b\u4ef6\u89e6\u53d1\u2192DB dump\u2192Restic\u53bb\u91cd\u5907\u4efd\u2192\u4fdd\u7559\u6e05\u7406\u2192\u6821\u9a8c\u2192\u62a5\u544a
  summary: \u707e\u5907\u5907\u4efd\u7cfb\u7edf\u2014\u2014\u4e8b\u4ef6\u89e6\u53d1\u7684Restic\u53bb\u91cd\u5907\u4efd\u6d41\u6c34\u7ebf\uff0cpost-commit reconciler\u81ea\u52a8\u9a71\u52a8\uff08\u91cd\u8981\u6587\u4ef6\u53d8\u66f4+8\u5c0f\u65f6\u95f4\u9694\u4fdd\u62a4\uff0c\u65e5\u57471-2\u6b21\uff09\uff0c\u8986\u76d6\u4ee3\u7801+\u914d\u7f6e+\u6570\u636e\u5e93+\u4e0d\u53ef\u66ff\u4ee3\u6570\u636e\uff0c\u76ee\u6807\u76d8F:(SanDisk
    2TB)\uff0c\u9075\u5faa3-2-1\u539f\u5219\u4e0e\u6570\u636e\u6700\u5c0f\u5316\u539f\u5219
  layer: L0_infrastructure
  functional_domain: operations
  blueprint_status: Active
  blueprint_level: module
  priority: P1
  version: 1.1.0
  generation: 1
  last_updated: '2026-07-17'
  file_path: 03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md
  construction_progress: completed"""
replace_in_file(br, old_block, new_block)
print(f"  OK: {br}")

# 4. capability_canonical_file_registry.yaml
cf = "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"
replace_in_file(cf, "MOD-INF-027 \u707e\u5907\u5907\u4efd\u7cfb\u7edf", "MOD-INF-043 \u707e\u5907\u5907\u4efd\u7cfb\u7edf")
replace_in_file(cf, "session-sess-backup-mod-inf-027", "session-sess-backup-mod-inf-043")
print(f"  OK: {cf}")

# 5. Delete residual file
residual = root / "scripts" / "backup" / "\u4e00\u952e\u5907\u4efd.ps1"
if residual.exists():
    residual.unlink()
    print("  OK: deleted residual file")
else:
    print("  SKIP: residual file already absent")

# 6. Session worktree commit
sys.path.insert(0, str(root / "src"))
from zephyr.gov_enforcement.rule_bridge.session_worktree import (
    session_worktree_start, generate_session_id,
    session_worktree_commit, session_worktree_merge,
)

sid = generate_session_id()
start_r = session_worktree_start(sid)
print(f"  start: {start_r.get('session_id', sid)}")

commit_files = [
    "scripts/backup/backup_config.yaml",
    "scripts/backup/backup_reconciler.py",
    "scripts/backup/backup.ps1",
    "scripts/backup/backup_manual.ps1",
    "scripts/backup/restore.ps1",
    "scripts/backup/README.md",
    "docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md",
    "docs/03_modules/blueprint_registry.yaml",
    "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml",
]
commit_msg = "fix(infra): MOD-INF-043\u2014\u2014\u7edf\u4e00\u707e\u5907\u5907\u4efdmodule_id(027/040\u2192043)+construction_progress=completed+\u5220\u9664\u6b8b\u7559\u4e00\u952e\u5907\u4efd.ps1"
r = session_worktree_commit(sid, commit_files, commit_msg, allow_overlap=True, allow_promote=True)
print("commit:", r)

if r.get("status") == "OK" and r.get("commit_hash"):
    m = session_worktree_merge(sid)
    print("merge:", m)
else:
    # Clean up worktree even if commit failed
    try:
        m = session_worktree_merge(sid)
        print("merge (cleanup):", m)
    except Exception as e:
        print(f"merge error: {e}")
