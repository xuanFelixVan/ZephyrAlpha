# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_gitops
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

"""
MOD-INF-019: Agent Spec — Skill GitOps
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

Skill GitOps CI/CD 引擎
========================
Skill 版本管理与自动化发布:
  1. VersionBump: 自动语义化版本号升级
  2. BranchManagement: feature/fix/chore 分支命名
  3. PRTemplate: 自动填充 PR 描述
  4. ReleasesNotes: 生成变更日志
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class SkillGitOps:
    """Skill GitOps 操作引擎"""

    BRANCH_PREFIXES = {
        "feature": "feat",
        "fix": "fix",
        "chore": "chore",
        "breaking": "breaking",
        "deprecate": "deprecate",
    }

    @classmethod
    def generate_branch_name(cls, skill_id: str, change_type: str, description: str) -> str:
        prefix = cls.BRANCH_PREFIXES.get(change_type, "chore")
        slug = description.lower().strip().replace(" ", "-")[:40]
        slug = "".join(c for c in slug if c.isalnum() or c == "-").strip("-")

        skill_abbr = "".join(w[0].upper() for w in skill_id.replace("-", " ").split() if w)[:4]

        return f"{prefix}/{skill_abbr.lower()}-{slug}"

    @classmethod
    def generate_pr_description(cls, skill_id: str, changes: dict[str, Any]) -> str:
        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
        kind = changes.get("kind", "update")
        summary = changes.get("summary", f"Update to {skill_id}")

        lines = [
            f"## Skill Update: `{skill_id}`",
            "",
            f"**Type**: {kind}",
            f"**Date**: {now}",
            "",
            "### Summary",
            summary,
            "",
        ]

        breaking = changes.get("breaking_changes", [])
        if breaking:
            lines.extend(["### Breaking Changes", ""])
            for bc in breaking:
                lines.append(f"- {bc}")
            lines.append("")

        added = changes.get("added", [])
        if added:
            lines.extend(["### Added", ""])
            for a in added:
                lines.append(f"- {a}")
            lines.append("")

        fixed = changes.get("fixed", [])
        if fixed:
            lines.extend(["### Fixed", ""])
            for f_item in fixed:
                lines.append(f"- {f_item}")
            lines.append("")

        lines.extend(
            [
                "### Pre-merge Checklist",
                "- [ ] SkillsBench benchmark passes (score >= 70)",
                "- [ ] SelfEvolutionFidelityGate passes (fidelity >= 80)",
                "- [ ] Token budget compliance verified",
                "- [ ] Registry updated",
            ]
        )

        return "\n".join(lines)

    @classmethod
    def generate_release_notes(cls, version: str, skills_changed: list[dict[str, Any]]) -> str:
        now = datetime.now(UTC).strftime("%Y-%m-%d")
        lines = [
            f"# Agent Spec Release {version}",
            f"**Date**: {now}",
            "",
            "## Skills Changed",
            "",
        ]

        for sc in skills_changed:
            sid = sc.get("skill_id", "?")
            kind = sc.get("kind", "update")
            summary = sc.get("summary", "")
            lines.append(f"- **{sid}** ({kind}): {summary}")

        return "\n".join(lines)

    @classmethod
    def version_bump(cls, current_version: str, change_type: str) -> str:
        parts = current_version.lstrip("v").split(".")

        try:
            major, minor, patch = (
                int(parts[0]),
                int(parts[1]) if len(parts) > 1 else 0,
                int(parts[2]) if len(parts) > 2 else 0,
            )
        except (ValueError, IndexError):
            major, minor, patch = 0, 0, 0

        if change_type == "breaking":
            major += 1
            minor = 0
            patch = 0
        elif change_type == "feature":
            minor += 1
            patch = 0
        elif change_type == "fix":
            patch += 1
        elif change_type == "deprecate":
            minor += 1
            patch = 0
        else:
            patch += 1

        return f"{major}.{minor}.{patch}"

    @classmethod
    def init_skill_repo(cls, skill_id: str, version: str = "0.1.0") -> dict[str, Any]:
        branch = cls.generate_branch_name(skill_id, "feature", "initial-skill-setup")
        pr_desc = cls.generate_pr_description(
            skill_id,
            {
                "kind": "feature",
                "summary": f"Initial skill setup for {skill_id}",
                "added": [f"Skill {skill_id} registered"],
            },
        )
        notes = cls.generate_release_notes(
            version,
            [
                {
                    "skill_id": skill_id,
                    "kind": "feature",
                    "summary": f"Initial skill: {skill_id}",
                }
            ],
        )

        return {
            "skill_id": skill_id,
            "branch": branch,
            "pr_description": pr_desc,
            "release_notes": notes,
            "version": version,
        }
