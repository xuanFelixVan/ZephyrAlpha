# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_factory
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

import os
import re
from collections.abc import Generator
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
from typing import Any

import yaml

_BASE_DIR = Path(__file__).resolve().parent
_SKILLS_DIR = _BASE_DIR / "skills"
_FACTORY_DIR = _SKILLS_DIR / "factory"
_REGISTRY_PATH = _BASE_DIR / "skill-registry.yaml"
_AGENTS_MD_PATH = _BASE_DIR / "AGENTS.md"


class SkillFactory:
    def __init__(self):
        self.template_path = _FACTORY_DIR / "skill-template.md"

    def _load_template(self) -> str:
        with open(self.template_path, encoding="utf-8") as f:
            return f.read()

    def _read_blueprint(self, blueprint_path: str) -> str:
        path = Path(blueprint_path)
        if not path.is_absolute():
            candidate = REPO_ROOT / path
            if candidate.exists():
                path = candidate
            else:
                legacy = _BASE_DIR.parent.parent / path
                if legacy.exists():
                    path = legacy
        return path.read_text(encoding="utf-8")

    def _extract_module_info(self, module_name: str, blueprint_content: str) -> dict[str, str]:
        core_ops = self._find_section(blueprint_content, ["核心操作", "Core Operations", "操作"])
        constraints = self._find_section(blueprint_content, ["约束", "Constraints", "限制"])
        errors = self._find_section(blueprint_content, ["常见错误", "Common Errors", "错误模式", "Error Patterns"])
        return {
            "module_name": module_name,
            "core_operations": core_ops or "待填写",
            "unique_constraints": constraints or "待填写",
            "common_errors": errors or "待填写",
        }

    def _find_section(self, content: str, keywords: list[str]) -> str:
        for kw in keywords:
            pattern = rf"^#{{1,3}}\s+.*{re.escape(kw)}.*$"
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                start = match.start()
                next_section = re.search(r"^#{1,3}\s+", content[match.end() :], re.MULTILINE)
                end = match.end() + next_section.start() if next_section else len(content)
                return content[start:end].strip()
        return ""

    def _render_template(self, template: str, info: dict[str, str]) -> str:
        result = template
        result = result.replace("{{MODULE_NAME}}", info["module_name"])
        result = result.replace("{{CORE_OPERATIONS}}", info["core_operations"])
        result = result.replace("{{UNIQUE_CONSTRAINTS}}", info["unique_constraints"])
        result = result.replace("{{COMMON_ERRORS}}", info["common_errors"])
        return result

    def _sanitize_dir_name(self, module_name: str) -> str:
        return re.sub(r"[^a-z0-9_-]", "-", module_name.lower().replace(" ", "-"))

    def _write_skill_file(self, module_name: str, content: str) -> Path:
        dir_name = self._sanitize_dir_name(module_name)
        skill_dir = _SKILLS_DIR / "domain" / dir_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(content, encoding="utf-8")
        (skill_dir / "references").mkdir(exist_ok=True)
        (skill_dir / "scripts").mkdir(exist_ok=True)
        agents_md = skill_dir / "agent.md"
        agents_md.write_text(f"# {module_name} Domain Skill\n\nCreated by SkillFactory.\n", encoding="utf-8")
        return skill_md

    def _generate_skill_id(self, module_name: str) -> str:
        abbr = "".join(w[0].upper() for w in module_name.split("-") if w)[:3]
        existing = self._count_domain_skills()
        num = str(existing + 1).zfill(3)
        return f"SKILL-DOM-{abbr:0<3}-{num}"

    def _count_domain_skills(self) -> int:
        registry = self._load_registry()
        return len(registry.get("skills", {}).get("domain", {}))

    def _load_registry(self) -> dict[str, Any]:
        with open(_REGISTRY_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _save_registry(self, registry: dict[str, Any]):
        tmp_path = f"{_REGISTRY_PATH}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                yaml.dump(registry, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            os.replace(tmp_path, _REGISTRY_PATH)
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    def _update_registry(self, module_name: str, skill_id: str, path: str):
        registry = self._load_registry()
        dir_name = self._sanitize_dir_name(module_name)
        registry.setdefault("skills", {}).setdefault("domain", {})
        registry["skills"]["domain"][skill_id] = {
            "name": module_name,
            "description": f"Domain skill for {module_name}",
            "skill_type": "domain",
            "tier": "L1",
            "path": f"{dir_name}/SKILL.md",
            "references": [],
        }
        registry["metadata"]["total_skills"] = registry["metadata"].get("total_skills", 0) + 1
        self._save_registry(registry)

    def _update_trigger_table(self, module_name: str):
        content = _AGENTS_MD_PATH.read_text(encoding="utf-8") if _AGENTS_MD_PATH.exists() else ""
        keyword = module_name.lower().replace("-", "|")
        new_entry = f"| {module_name} | {module_name} | implementer |\n"
        if new_entry.strip() not in content:
            insert_pos = content.rfind("|")
            if insert_pos > 0:
                line_end = content.find("\n", insert_pos)
                content = content[: line_end + 1] + new_entry + content[line_end + 1 :]
                _AGENTS_MD_PATH.write_text(content, encoding="utf-8")

    def generate_domain_skill(self, module_name: str, blueprint_path: str) -> Path:
        blueprint_content = self._read_blueprint(blueprint_path)
        info = self._extract_module_info(module_name, blueprint_content)
        template = self._load_template()
        skill_content = self._render_template(template, info)
        skill_path = self._write_skill_file(module_name, skill_content)
        skill_id = self._generate_skill_id(module_name)
        self._update_registry(module_name, skill_id, str(skill_path.relative_to(_SKILLS_DIR)))
        return skill_path

    def bootstrap_sequence(self, module_name: str, blueprint_path: str) -> Generator[tuple[str, str], None, None]:
        yield ("create_blueprint", f"Blueprint verified: {blueprint_path}")
        skill_path = self.generate_domain_skill(module_name, blueprint_path)
        yield ("factory_generate", f"Skill generated: {skill_path}")
        yield ("human_review", "Awaiting human review of generated SKILL.md")
        yield ("register", "Skill registered in skill-registry.yaml")
