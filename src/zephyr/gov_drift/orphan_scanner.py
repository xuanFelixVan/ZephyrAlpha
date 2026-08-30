# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.orphan_scanner
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/gov_drift/_scanners.py ; src/zephyr/gov_drift/brain_integration.py ; tests/audit/test_orphan_scanner.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 孤儿扫描不可跳过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Orphan Resource Scanner — 孤儿资源检测 §6.28。


orphan_script: scripts/下.py文件不在script-manifest.yaml


orphan_data: data/*.db/JSON 无对应代码读写


orphan_doc: docs/下.md 无蓝图引用


orphan_config: yaml/config 无代码读取


对标 blueprint.md §6.28。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root，类型注解 str
#   code: orphan_scanner.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① OrphanResource
#   name_en: OrphanResource
#   intro: class OrphanResource 源码 L113-L133
#   desc: 公共方法（定义序）: to_dict；源码 L113-L133
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② find_orphan_scripts
#   name_en: find_orphan_scripts
#   intro: find_orphan_scripts(project_root) 源码 L136-L177
#   desc: 源码 L136-L177
#   inputs: project_root
#   outputs: list[OrphanResource]
# - id: A3
#   name_zh: ③ find_orphan_data
#   name_en: find_orphan_data
#   intro: find_orphan_data(project_root) 源码 L180-L217
#   desc: 源码 L180-L217
#   inputs: project_root
#   outputs: list[OrphanResource]
# - id: A4
#   name_zh: ④ find_orphan_docs
#   name_en: find_orphan_docs
#   intro: find_orphan_docs(project_root) 源码 L220-L258
#   desc: 源码 L220-L258
#   inputs: project_root
#   outputs: list[OrphanResource]
# - id: A5
#   name_zh: ⑤ scan_orphan_resources
#   name_en: scan_orphan_resources
#   intro: scan_orphan_resources(project_root) 源码 L261-L288
#   desc: 源码 L261-L288
#   inputs: project_root
#   outputs: dict[str, object]
# 层: 输出
# - id: O1
#   name_zh: list[OrphanResource]
#   name_en: list[OrphanResource]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: src/zephyr/gov_drift/_scanners.py ; src/zephyr/gov_drift/brain_integration.py ;…
# - id: O2
#   name_zh: dict[str, object]
#   name_en: dict[str, object]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: src/zephyr/gov_drift/_scanners.py ; src/zephyr/gov_drift/brain_integration.py ;…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

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

        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in orphan_scanner", exc_info=True)

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

        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in orphan_scanner", exc_info=True)

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

        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in orphan_scanner", exc_info=True)

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
