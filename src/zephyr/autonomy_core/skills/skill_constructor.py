# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_constructor
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
# [A_module] module_id=MOD-ORC_skill_constructor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Constructor
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

蓝图->Skill 全自动构造器
=======================
流程:
  1. 读取蓝图 markdown 文件
  2. 解析 frontmatter 获取模块 ID / 版本 / 依赖
  3. 提取核心操作、独特约束、常见错误模式
  4. 生成 SKILL.md 模板填入
  5. 写入 skills/domain/{module_name}/SKILL.md
  6. 更新 skill-registry.yaml
  7. 可选：触发 AGENTS.md 触发表更新
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

_BASE_DIR = Path(__file__).resolve().parent
_SKILLS_DIR = _BASE_DIR / "skills"
_TEMPLATE_DIR = _SKILLS_DIR / "factory"
_REGISTRY_PATH = _BASE_DIR / "skill-registry.yaml"


class SkillConstructor:
    """蓝图->Skill 全自动生成器"""

    KEYWORD_MAP = {
        "database": "database-specialist",
        "migration": "database-specialist",
        "sql": "database-specialist",
        "atm": "database-specialist",
        "mcp": "mcp-specialist",
        "server": "mcp-specialist",
        "tool": "mcp-specialist",
        "context": "context-specialist",
        "ctx": "context-specialist",
        "feedback": "feedback-specialist",
        "loop": "feedback-specialist",
        "gate": "gate-specialist",
        "rule": "gate-specialist",
        "policy": "gate-specialist",
        "rbac": "agent-specialist",
        "permission": "agent-specialist",
        "acl": "agent-specialist",
        "blueprint": "master-blueprint",
        "audit": "drift-detector",
        "compliance": "drift-detector",
        "governance": "drift-detector",
        "drift": "drift-detector",
        "knowledge": "knowledge-specialist",
        "kb": "knowledge-specialist",
        "ke": "knowledge-specialist",
        "rollback": "rollback-specialist",
        "undo": "rollback-specialist",
        "revert": "rollback-specialist",
        "checkpoint": "rollback-specialist",
        "vector": "vector-memory",
        "memory": "vector-memory",
        "vms": "vector-memory",
        "embedding": "vector-memory",
        "a2a": "a2a-protocol",
        "agent-to-agent": "a2a-protocol",
        "多agent": "a2a-protocol",
        "script": "system-telemetry",
        "telemetry": "system-telemetry",
        "observability": "system-telemetry",
        "metrics": "system-telemetry",
        "llm": "lsg-security",
        "security": "lsg-security",
        "injection": "lsg-security",
        "jailbreak": "lsg-security",
        "dedup": "code-dedup-engine",
        "duplicate": "code-dedup-engine",
        "fix": "auto-fix-engine",
        "repair": "auto-fix-engine",
        "自愈": "auto-fix-engine",
        "heal": "auto-fix-engine",
    }

    def __init__(self, base_dir: Path | None = None):
        self._base_dir = base_dir or _BASE_DIR
        self._skills_dir = self._base_dir / "skills"
        self._registry_path = self._base_dir / "skill-registry.yaml"

    def _parse_blueprint(self, blueprint_path: str) -> dict[str, Any]:
        path = Path(blueprint_path)
        if not path.is_absolute():
            path = self._base_dir.parent.parent / path

        content = path.read_text(encoding="utf-8")

        fm: dict[str, Any] = {}
        body = content
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
        if match:
            try:
                fm = yaml.safe_load(match.group(1)) or {}
            except yaml.YAMLError:
                pass
            body = match.group(2)

        return {
            "path": str(path),
            "frontmatter": fm,
            "body": body,
            "content": content,
        }

    def _extract_sections(self, body: str) -> dict[str, str]:
        sections: dict[str, str] = {}
        current_section = "preamble"
        current_lines: list[str] = []

        for line in body.split("\n"):
            header_match = re.match(r"^#{1,3}\s+(.+)$", line)
            if header_match:
                if current_lines:
                    sections[current_section] = "\n".join(current_lines).strip()
                current_section = header_match.group(1).lower().strip()
                current_lines = [line]
            else:
                current_lines.append(line)

        if current_lines:
            sections[current_section] = "\n".join(current_lines).strip()

        return sections

    def _extract_core_operations(self, sections: dict[str, str], body: str) -> str:
        for key in ["核心操作", "core operations", "操作", "operations", "核心职能"]:
            for sk, sv in sections.items():
                if key in sk:
                    return sv.split("\n")[1:][:15] if "\n" in sv else ""

        code_blocks = re.findall(r"^```(?:\w+)?\n(.*?)^```", body, re.MULTILINE | re.DOTALL)
        api_calls = re.findall(r"(?:def|class|async def)\s+(\w+)", body)
        steps = re.findall(r"^\d+[.\)]\s*(.+)$", body, re.MULTILINE)

        parts = []
        if steps:
            parts.append("步骤:\n" + "\n".join(f"- {s}" for s in steps[:10]))
        if api_calls:
            parts.append("API:\n" + "\n".join(f"- {a}()" for a in api_calls[:10]))

        return "\n\n".join(parts) if parts else ""

    def _extract_constraints(self, sections: dict[str, str], body: str) -> str:
        for key in ["约束", "constraints", "限制", "restrictions", "注意事项"]:
            for sk, sv in sections.items():
                if key in sk:
                    return sv.split("\n")[1:][:12] if "\n" in sv else ""

        constraints = re.findall(r"(?:MUST|必须|必须确保|不可|不能|禁止|不允许)\s*(.+?)(?:[。；\n]|$)", body)
        return "\n".join(f"- {c.strip()}" for c in constraints[:12]) if constraints else ""

    def _extract_common_errors(self, sections: dict[str, str]) -> str:
        for key in ["常见错误", "common errors", "错误模式", "error patterns", "陷阱", "pitfalls", "注意事项"]:
            for sk, sv in sections.items():
                if key in sk:
                    return sv.split("\n")[1:][:10] if "\n" in sv else ""

        return ""

    def _infer_skill_name(self, blueprint_data: dict[str, Any]) -> str:
        fm = blueprint_data.get("frontmatter", {})
        module_id = fm.get("module_id", "")

        keyword_lower = ""
        for key in self.KEYWORD_MAP:
            if key in module_id.lower() or key in blueprint_data.get("body", "").lower()[:500]:
                keyword_lower = self.KEYWORD_MAP[key]
                break

        if keyword_lower:
            return keyword_lower

        body_lower = blueprint_data.get("body", "").lower()[:1000]
        for key, name in self.KEYWORD_MAP.items():
            if key in body_lower:
                return name

        return "master-blueprint"

    def _resolve_skill_id(self, skill_name: str) -> str | None:
        if not _REGISTRY_PATH.exists():
            return None

        reg = yaml.safe_load(_REGISTRY_PATH.read_text(encoding="utf-8")) or {}
        for category in ("domain", "role"):
            for sid, data in reg.get("skills", {}).get(category, {}).items():
                if data.get("name") == skill_name:
                    return sid
        return None

    def _generate_skill_content(
        self,
        skill_name: str,
        skill_id: str,
        core_ops: str,
        constraints: str,
        errors: str,
    ) -> str:
        now = datetime.now(UTC).isoformat()

        parts = [
            "---",
            f"skill_id: {skill_id}",
            f"name: {skill_name}",
            f"description: Auto-generated Domain Skill for {skill_name}",
            "allowed_tools:",
            "  - read_file",
            "  - write_file",
            "  - search_replace",
            "  - grep",
            "  - run_command",
            "model_hint: deepseek",
            "freshness_score: 100.0",
            f"last_validated: {now}",
            "version: 0.1.0",
            "---",
            "",
            f"# {skill_name}",
            "",
            "## 核心操作",
            "",
            core_ops or "_待人工补充_",
            "",
        ]

        if constraints:
            parts.extend(
                [
                    "## 独特约束",
                    "",
                    constraints,
                    "",
                ]
            )

        if errors:
            parts.extend(
                [
                    "## 常见错误模式",
                    "",
                    errors,
                    "",
                ]
            )

        parts.append("---")
        parts.append(f"_Auto-generated by SkillConstructor at {now}_")

        return "\n".join(parts)

    def construct(self, blueprint_path: str) -> dict[str, Any]:
        try:
            bp = self._parse_blueprint(blueprint_path)
        except Exception as e:
            return {
                "blueprint": blueprint_path,
                "skill_id": None,
                "status": "parse_failed",
                "error": str(e),
                "files": [],
            }

        sections = self._extract_sections(bp["body"])
        core_ops = self._extract_core_operations(sections, bp["body"])
        constraints = self._extract_constraints(sections, bp["body"])
        errors = self._extract_common_errors(sections)

        skill_name = self._infer_skill_name(bp)
        skill_id = self._resolve_skill_id(skill_name)

        if skill_id is None:
            abbr = "".join(w[0].upper() for w in skill_name.split("-") if w)[:3]
            existing = len(self._load_registry().get("skills", {}).get("domain", {}))
            num = str(existing + 1).zfill(3)
            skill_id = f"SKILL-DOM-{abbr:0<3}-{num}"

        content = self._generate_skill_content(skill_name, skill_id, core_ops, constraints, errors)

        dir_name = skill_name.replace(" ", "-").lower()
        skill_dir = self._skills_dir / "domain" / dir_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "references").mkdir(exist_ok=True)
        (skill_dir / "scripts").mkdir(exist_ok=True)

        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(content, encoding="utf-8")

        self._update_registry(skill_name, skill_id, f"{dir_name}/SKILL.md")

        return {
            "blueprint": blueprint_path,
            "skill_id": skill_id,
            "skill_name": skill_name,
            "status": "constructed",
            "files": [str(skill_md.relative_to(self._base_dir))],
            "core_ops_extracted": bool(core_ops),
            "constraints_extracted": bool(constraints),
            "errors_extracted": bool(errors),
        }

    def validate_construction(self, skill_id: str) -> dict[str, Any]:
        issues: list[str] = []
        try:
            loader = None
            from zephyr.autonomy_core.skills.skill_loader import SkillLoader

            loader = SkillLoader()
            result = loader.progressive_load(skill_id)
            if not result.get("l1", {}).get("skill_id"):
                issues.append("l1_metadata_missing")
            if not result.get("l2"):
                issues.append("l2_body_empty")
            if result.get("token_count_l2", 0) > 500:
                issues.append("l2_over_budget")
        except KeyError:
            issues.append("skill_not_registered")
        except FileNotFoundError:
            issues.append("skill_file_missing")
        except Exception as e:
            issues.append(f"validation_error: {e}")

        return {
            "skill_id": skill_id,
            "valid": len(issues) == 0,
            "issues": issues,
        }

    def _load_registry(self) -> dict[str, Any]:
        if not _REGISTRY_PATH.exists():
            return {}
        return yaml.safe_load(_REGISTRY_PATH.read_text(encoding="utf-8")) or {}

    def _update_registry(self, skill_name: str, skill_id: str, path: str):
        registry = self._load_registry()
        registry.setdefault("skills", {}).setdefault("domain", {})
        if skill_id not in registry["skills"]["domain"]:
            registry["skills"]["domain"][skill_id] = {
                "name": skill_name,
                "description": f"Domain skill for {skill_name}",
                "skill_type": "domain",
                "tier": "L1",
                "path": path,
                "references": [],
            }
            old_total = registry.get("metadata", {}).get("total_skills", 0)
            registry.setdefault("metadata", {})
            registry["metadata"]["total_skills"] = old_total + 1
            tmp = str(_REGISTRY_PATH) + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                yaml.dump(registry, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            Path(tmp).replace(_REGISTRY_PATH)
