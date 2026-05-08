"""
MOD-INF-019: Agent Spec — Skill Discovery
Blueprint: docs/03_modules/l01_infrastructure/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0

Skill 发现——从模块蓝图与源码自动发现可生成 Skill 的模块。
v0.3.0: 新增 auto_generate_missing() — B156 自动化 Skill 生成闭环.
"""

from __future__ import annotations

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

from zephyr.agent_spec.skill_factory import SkillFactory
from zephyr.agent_spec.skill_loader import SkillLoader


class DiscoveryGap:
    def __init__(self, module_name: str, blueprint_path: str, reason: str):
        self.module_name = module_name
        self.blueprint_path = blueprint_path
        self.reason = reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "module_name": self.module_name,
            "blueprint_path": self.blueprint_path,
            "reason": self.reason,
        }


class DiscoveryResult:
    def __init__(self):
        self.existing_skills: List[str] = []
        self.gaps: List[DiscoveryGap] = []
        self.generated: List[str] = []
        self.errors: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "existing_skills": self.existing_skills,
            "gaps": [g.to_dict() for g in self.gaps],
            "generated": self.generated,
            "errors": self.errors,
            "total_gaps": len(self.gaps),
            "total_generated": len(self.generated),
        }


class SkillDiscovery:
    """Skill 发现——从模块蓝图自动发现可生成 Skill 的模块."""

    @staticmethod
    def scan_modules(modules_path: str) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        base = Path(modules_path)
        if not base.exists() or not base.is_dir():
            return results

        skills_base = base / "skills"
        if skills_base.exists():
            for category_dir in ("domain", "role"):
                cat_path = skills_base / category_dir
                if not cat_path.exists():
                    continue
                for md_file in sorted(cat_path.glob("*.md")):
                    skill_id = md_file.stem
                    frontmatter = SkillDiscovery._parse_frontmatter(md_file)
                    results.append({
                        "skill_id": (
                            f"SKILL-DOM-{skill_id[:3].upper()}-001"
                            if category_dir == "domain"
                            else f"SKILL-ROL-{skill_id[:3].upper()}-001"
                        ),
                        "name": skill_id,
                        "source": md_file.as_posix(),
                        "category": category_dir,
                        "version": frontmatter.get("version", "0.1.0"),
                        "freshness": frontmatter.get("freshness_score", 0.0),
                        "description": frontmatter.get("description", "")[:100],
                    })

        all_skills = base / "all_skill_modules.py"
        if all_skills.exists():
            try:
                content = all_skills.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                try:
                    content = all_skills.read_text(encoding="gbk")
                except (UnicodeDecodeError, OSError):
                    return results
            for line in content.splitlines():
                line = line.strip()
                if line.startswith('"') and line.endswith('",'):
                    module_name = line.strip('" ,')
                    if module_name not in [r["name"] for r in results]:
                        results.append({
                            "skill_id": f"SKILL-MOD-{module_name[:3].upper()}",
                            "name": module_name,
                            "source": "all_skill_modules.py",
                            "category": "registered",
                            "version": "registered",
                            "freshness": 0.0,
                            "description": f"Registered module: {module_name}",
                        })

        return results

    @staticmethod
    def discover_gaps(docs_path: Optional[str] = None) -> DiscoveryResult:
        result = DiscoveryResult()

        registry = SkillLoader()._load_registry()
        existing_ids = set()
        for cat in ("domain", "role"):
            for sid in registry.get("skills", {}).get(cat, {}):
                existing_ids.add(sid)
        result.existing_skills = sorted(existing_ids)

        docs_base = Path(docs_path) if docs_path else Path("docs/03_modules")
        docs_base = docs_base.resolve()
        if not docs_base.exists():
            result.errors.append(f"Docs path not found: {docs_base}")
            return result

        for bp_file in docs_base.rglob("**/blueprint.md"):
            try:
                content = bp_file.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                try:
                    content = bp_file.read_text(encoding="gbk")
                except (UnicodeDecodeError, OSError):
                    try:
                        content = bp_file.read_text(encoding="latin-1")
                    except (UnicodeDecodeError, OSError):
                        continue
            module_name = SkillDiscovery._extract_module_name(content, bp_file)
            if not module_name:
                continue

            module_id = SkillDiscovery._derive_skill_id(module_name)
            if module_id and module_id not in existing_ids:
                result.gaps.append(DiscoveryGap(
                    module_name=module_name,
                    blueprint_path=str(bp_file),
                    reason=f"No Skill registered for module '{module_name}' — expected skill_id={module_id}",
                ))

        return result

    @staticmethod
    def auto_generate_missing(docs_path: Optional[str] = None,
                              dry_run: bool = True) -> DiscoveryResult:
        gap_result = SkillDiscovery.discover_gaps(docs_path)
        if not gap_result.gaps:
            return gap_result

        factory = SkillFactory()
        for gap in gap_result.gaps:
            try:
                if not dry_run:
                    factory.generate_domain_skill(gap.module_name, gap.blueprint_path)
                gap_result.generated.append(gap.module_name)
            except Exception as exc:
                gap_result.errors.append(f"Failed to generate Skill for {gap.module_name}: {exc}")

        return gap_result

    @staticmethod
    def _extract_module_name(content: str, bp_file: Path) -> str:
        for line in content.split("\n"):
            ls = line.strip()
            if ls.startswith("# ") and "MOD-" in ls:
                parts = ls.lstrip("# ").strip().split()
                for p in parts:
                    if p.startswith("MOD-"):
                        return p
        for line in content.split("\n"):
            ls = line.strip()
            if ls.startswith("# ") and ("蓝图" in ls or "Blueprint" in ls):
                for word in ls.lstrip("# ").strip().split():
                    if word.startswith("MOD-"):
                        return word
                name = ls.lstrip("# ").strip().split(":")[0].strip()
                if len(name) > 2 and len(name) < 60 and "[" not in name:
                    return name

        parent_dir = bp_file.parent.name
        if parent_dir and parent_dir not in ("03_modules", "module", "blueprints", "docs"):
            clean = parent_dir.replace("_", "-").strip()
            if len(clean) > 1 and not any(c in clean for c in ("[", "]", ":", "(", ")")):
                return clean

        for part in bp_file.parts:
            if part.startswith("l") and "_" in part:
                for p in bp_file.parent.parts:
                    if p not in ("docs", "03_modules", "l01_infrastructure", "l02_services",
                                 "blueprints", "module"):
                        clean = p.replace("_", "-").strip()
                        if len(clean) > 1 and not any(c in clean for c in ("[", "]", ":", "(", ")")):
                            return clean
                return parent_dir

        return ""

    @staticmethod
    def _derive_skill_id(module_name: str) -> str:
        if not module_name:
            return ""
        short = module_name.split("-")[-1] if "-" in module_name else module_name
        return f"SKILL-DOM-{short[:3].upper()}-001"

    @staticmethod
    def _parse_frontmatter(md_file: Path) -> Dict[str, Any]:
        content = md_file.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return {}
        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}
        try:
            return yaml.safe_load(parts[1]) or {}
        except yaml.YAMLError:
            return {}


__all__ = ["SkillDiscovery", "DiscoveryResult", "DiscoveryGap"]
