# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_loader
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] frozen
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

import re
from pathlib import Path
from typing import Any

import yaml

_BASE_DIR = Path(__file__).resolve().parent
_REGISTRY_PATH = _BASE_DIR / "skill-registry.yaml"


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+|[^\w\s]", text)


def _count_tokens(text: str) -> int:
    return len(_tokenize(text))


class SkillLoader:
    def __init__(self, registry_path: Path | None = None):
        self.registry_path = registry_path or _REGISTRY_PATH
        self._l0_cache: dict[str, Any] | None = None

    def _load_registry(self) -> dict[str, Any]:
        with open(self.registry_path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _resolve_skill_path(self, skill_id: str) -> Path:
        if not skill_id or skill_id.strip() != skill_id:
            raise KeyError(f"Invalid skill_id: '{skill_id}'")
        if ".." in skill_id.split("/") or ".." in skill_id.split("\\"):
            raise ValueError(f"Path traversal detected in skill_id: '{skill_id}'")
        registry = self._load_registry()
        skills = registry.get("skills", {})
        for category in ("domain", "role"):
            for sid, data in skills.get(category, {}).items():
                if sid == skill_id:
                    resolved = (_BASE_DIR / "skills" / category / data.get("path", "")).resolve()
                    allowed = _BASE_DIR.resolve()
                    if allowed not in resolved.parents and resolved != allowed:
                        raise ValueError(f"Resolved path outside allowed directory: {resolved}")
                    return resolved
        raise KeyError(f"Skill {skill_id} not found in registry")

    def _parse_yaml_frontmatter(self, content: str) -> dict[str, Any]:
        match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if match:
            return yaml.safe_load(match.group(1)) or {}
        return {}

    def _extract_body(self, content: str) -> str:
        match = re.match(r"^---\s*\n.*?\n---\s*\n(.*)", content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return content.strip()

    def _load_l1_frontmatter(self, skill_id: str) -> dict[str, Any]:
        path = self._resolve_skill_path(skill_id)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        fm = self._parse_yaml_frontmatter(content)
        return {
            "skill_id": fm.get("skill_id"),
            "name": fm.get("name"),
            "description": fm.get("description"),
            "allowed_tools": fm.get("allowed_tools", []),
            "model_hint": fm.get("model_hint"),
            "freshness_score": fm.get("freshness_score", 100.0),
            "last_validated": fm.get("last_validated"),
        }

    def _load_l2_body(self, skill_id: str) -> str:
        path = self._resolve_skill_path(skill_id)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        body = self._extract_body(content)
        if _count_tokens(body) > 500:
            body = self._compress_to_critical_rules(body)
        return body

    def _compress_to_critical_rules(self, body: str) -> str:
        lines = body.split("\n")
        critical_sections: list[str] = []
        in_critical = False
        for line in lines:
            if re.match(r"^#{1,3}\s*(CRITICAL|CRITICAL:|关键|MUST|必做)", line, re.IGNORECASE):
                in_critical = True
                critical_sections.append(line)
            elif re.match(r"^#{1,3}\s", line):
                in_critical = False
            elif in_critical:
                critical_sections.append(line)
        if not critical_sections:
            header_match = re.search(r"^(#{1,3}\s+.+)$", body, re.MULTILINE)
            if header_match:
                first_section = body[body.find(header_match.group(1)) :]
                lines = first_section.split("\n")
                critical_sections = lines[:20]
            else:
                critical_sections = lines[:20]
        return "\n".join(critical_sections)

    def _list_l3_references(self, skill_id: str) -> list[dict[str, str]]:
        registry = self._load_registry()
        skills = registry.get("skills", {})
        for category in ("domain", "role"):
            for sid, data in skills.get(category, {}).items():
                if sid == skill_id:
                    return data.get("references", [])
        return []

    def _resolve_reference_path(self, skill_id: str, ref_name: str) -> Path:
        refs = self._list_l3_references(skill_id)
        for ref in refs:
            if ref.get("name") == ref_name:
                return _BASE_DIR / "references" / ref.get("path", ref_name)
        return _BASE_DIR / "references" / ref_name

    def load_l0(self) -> dict[str, Any]:
        if self._l0_cache is not None:
            return self._l0_cache
        agents_md = _BASE_DIR / "skills" / "factory" / "AGENT.md"
        if agents_md.exists():
            self._l0_cache = {
                "constitution_path": str(agents_md),
                "content": agents_md.read_text(encoding="utf-8"),
            }
        else:
            self._l0_cache = {"constitution_path": str(agents_md), "content": ""}
        return self._l0_cache

    def load_l3_reference(self, skill_id: str, ref_name: str) -> str:
        ref_path = self._resolve_reference_path(skill_id, ref_name)
        if ref_path.exists():
            return ref_path.read_text(encoding="utf-8")
        raise FileNotFoundError(f"L3 reference {ref_name} not found for {skill_id}")

    def progressive_load(self, skill_id: str) -> dict[str, Any]:
        l1 = self._load_l1_frontmatter(skill_id)
        l2 = self._load_l2_body(skill_id)
        result = {"l1": l1, "l2": l2}
        result["l3_available"] = self._list_l3_references(skill_id)
        result["token_count_l2"] = _count_tokens(l2)
        return result

    def progressive_load_full(self, skill_id: str) -> dict[str, Any]:
        result = self.progressive_load(skill_id)
        l3_contents = {}
        for ref in result.get("l3_available", []):
            ref_name = ref.get("name", ref.get("path", ""))
            if ref_name:
                try:
                    l3_contents[ref_name] = self.load_l3_reference(skill_id, ref_name)
                except FileNotFoundError:
                    l3_contents[ref_name] = None
        result["l3_contents"] = l3_contents
        return result

    def check_token_budget(self, domain_skill_id: str, role_skill_id: str) -> dict[str, Any]:
        domain_body = self._load_l2_body(domain_skill_id)
        role_body = self._load_l2_body(role_skill_id)
        domain_tokens = _count_tokens(domain_body)
        role_tokens = _count_tokens(role_body)
        total = domain_tokens + role_tokens
        return {
            "domain_tokens": domain_tokens,
            "role_tokens": role_tokens,
            "total_tokens": total,
            "within_budget": total <= 800,
            "budget_limit": 800,
        }


_STABILITY_FROZEN = True
_FROZEN_PUBLIC_API = frozenset({"SkillLoader"})


def __getattr__(name: str):
    if name in _FROZEN_PUBLIC_API:
        import logging

        logging.getLogger("zephyr.stability_guard").warning(
            "STABILITY VIOLATION: Public API attribute '%s' removed from frozen module zephyr.autonomy_core.skills.skill_loader",
            name,
        )
    raise AttributeError(f"module 'zephyr.autonomy_core.skills.skill_loader' has no attribute {name!r}")
