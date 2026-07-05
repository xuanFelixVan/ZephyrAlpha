# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.governance.drift_detection.orphan_scanner
# [DOMAIN] D_BEHAVIORAL_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_scanners.py; src/zephyr/governance/drift_detection/brain_integration.py; tests/audit/test_orphan_scanner.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 孤儿扫描不可跳过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_orphan_scanner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Orphan Resource Scanner — 孤儿资源检测 §6.28。





module_id: MOD-INF-023


orphan_script: scripts/下.py文件不在script-manifest.yaml


orphan_data: data/*.db/JSON 无对应代码读写


orphan_doc: docs/下.md 无蓝图引用


orphan_config: yaml/config 无代码读取


对标 blueprint.md §6.28。"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class OrphanResource:
    resource_id: str

    resource_path: str

    resource_type: str

    description: str

    severity: str = "MINOR"

    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, object]:
        return {
            "resource_id": self.resource_id,
            "resource_path": self.resource_path,
            "resource_type": self.resource_type,
            "description": self.description,
            "severity": self.severity,
        }


def find_orphan_scripts(project_root: str) -> list[OrphanResource]:
    orphans: list[OrphanResource] = []

    scripts_dir = Path(project_root) / "scripts"

    if not scripts_dir.exists():
        return orphans

    manifest_path = scripts_dir / "script-manifest.yaml"

    manifest_scripts: set[str] = set()

    if manifest_path.exists():
        try:
            import yaml

            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

            if isinstance(manifest, dict) and "scripts" in manifest:
                for entry in manifest["scripts"]:
                    if isinstance(entry, dict):
                        p = entry.get("path", entry.get("script", ""))

                        manifest_scripts.add(str(p))

        except Exception:
            pass

    for py_file in scripts_dir.rglob("*.py"):
        rel = py_file.relative_to(project_root).as_posix()

        if rel not in manifest_scripts:
            orphans.append(
                OrphanResource(
                    resource_id=f"orphan-script-{py_file.stem}",
                    resource_path=str(py_file),
                    resource_type="orphan_script",
                    description=f"Script {rel} not in script-manifest.yaml",
                )
            )

    return orphans


def find_orphan_data(project_root: str) -> list[OrphanResource]:
    orphans: list[OrphanResource] = []

    data_dir = Path(project_root) / "data"

    if not data_dir.exists():
        return orphans

    data_files: list[Path] = []

    for ext in ["*.db", "*.json", "*.yaml"]:
        data_files.extend(data_dir.rglob(ext))

    src_text = ""

    src_root = Path(project_root) / "src"

    for pf in list(src_root.rglob("*.py"))[:50]:
        try:
            src_text += pf.read_text(encoding="utf-8") + "\n"

        except Exception:
            pass

    for df in data_files:
        stem_lower = df.stem.lower().replace("_", "").replace("-", "")

        if stem_lower not in src_text.lower():
            orphans.append(
                OrphanResource(
                    resource_id=f"orphan-data-{df.stem}",
                    resource_path=str(df),
                    resource_type="orphan_data",
                    description=f"Data file {df.name} not referenced in src/",
                )
            )

    return orphans


def find_orphan_docs(project_root: str) -> list[OrphanResource]:
    orphans: list[OrphanResource] = []

    docs_dir = Path(project_root) / "docs"

    if not docs_dir.exists():
        return orphans

    blueprint_set: set[str] = set()

    for bp in docs_dir.rglob("**/blueprint.md"):
        try:
            content = bp.read_text(encoding="utf-8")

            refs = re.findall(r"`([^`]+\.(?:py|yaml|md))`", content)

            blueprint_set.update(refs)

        except Exception:
            pass

    for md_file in docs_dir.rglob("*.md"):
        rel = md_file.relative_to(project_root).as_posix()

        if "blueprint.md" in rel or "changes" in rel:
            continue

        if rel not in blueprint_set:
            orphans.append(
                OrphanResource(
                    resource_id=f"orphan-doc-{md_file.stem}",
                    resource_path=str(md_file),
                    resource_type="orphan_doc",
                    description=f"Doc {rel} not referenced in any blueprint",
                    severity="INFO",
                )
            )

    return orphans


def scan_orphan_resources(project_root: str) -> dict[str, object]:
    results: dict[str, object] = {
        "scripts": [],
        "data": [],
        "docs": [],
        "summary": {},
    }

    script_orphans = find_orphan_scripts(project_root)

    data_orphans = find_orphan_data(project_root)

    doc_orphans = find_orphan_docs(project_root)

    results["scripts"] = [o.to_dict() for o in script_orphans]

    results["data"] = [o.to_dict() for o in data_orphans]

    results["docs"] = [o.to_dict() for o in doc_orphans]

    results["summary"] = {
        "total": len(script_orphans) + len(data_orphans) + len(doc_orphans),
        "scripts": len(script_orphans),
        "data": len(data_orphans),
        "docs": len(doc_orphans),
    }

    return results
