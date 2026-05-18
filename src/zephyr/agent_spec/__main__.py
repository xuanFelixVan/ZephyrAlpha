# [BLUEPRINT] MOD-INF-019 | 03_modules/l01_infrastructure/agent-spec/blueprint.md | §

# [MODULE] zephyr.agent_spec.__main__

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""agent-spec MOD-INF-019 CLI — 蓝图→Skill 升级引擎入口.

用法
----
    python -m zephyr.agent_spec list          # 列出所有已注册 Skill
    python -m zephyr.agent_spec status        # 显示模块健康状态
    python -m zephyr.agent_spec help          # 显示帮助
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml


def _registry_path() -> Path:
    return Path(__file__).resolve().parent / "skill_registry.yaml"


def _load_registry() -> dict:
    with open(_registry_path(), "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def cmd_list() -> int:
    """列出所有已注册 Skill."""
    try:
        reg = _load_registry()
        skills = reg.get("skills", {})
        total = 0
        for category in ("domain", "role"):
            entries = skills.get(category, {})
            if entries:
                print(f"\n[{category}]")
                for sid, data in entries.items():
                    tier = data.get("tier", "?")
                    name = data.get("name", sid)
                    desc = data.get("description", "")
                    print(f"  {sid}  {name}  [{tier}]  {desc}")
                    total += 1
        print(f"\n--- 共 {total} 个已注册 Skill ---")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def cmd_status() -> int:
    """显示模块健康状态."""
    ok = True
    try:
        from zephyr.agent_spec.skill_model import SkillModel, SkillTier, SkillType, SkillStatus
        print(f"skill_model       OK  ({len(SkillTier)} tiers, {len(SkillType)} types, {len(SkillStatus)} statuses)")
    except Exception as exc:
        print(f"skill_model       FAIL  {exc}")
        ok = False

    try:
        from zephyr.agent_spec.skill_loader import SkillLoader
        loader = SkillLoader()
        print(f"skill_loader      OK  (path={loader.registry_path})")
    except Exception as exc:
        print(f"skill_loader      FAIL  {exc}")
        ok = False

    try:
        from zephyr.agent_spec.skill_factory import SkillFactory
        print("skill_factory     OK")
    except Exception as exc:
        print(f"skill_factory     FAIL  {exc}")
        ok = False

    try:
        reg = _load_registry()
        n_domain = len(reg.get("skills", {}).get("domain", {}))
        n_role = len(reg.get("skills", {}).get("role", {}))
        print(f"skill_registry    OK  ({n_domain} domain + {n_role} role = {n_domain + n_role} total)")
    except Exception as exc:
        print(f"skill_registry    FAIL  {exc}")
        ok = False

    print(f"\n{'ALL SYSTEMS GO' if ok else 'SOME SYSTEMS DEGRADED'}")
    return 0 if ok else 1


def main() -> int:
    args = sys.argv[1:]
    cmd = args[0] if args else "help"

    if cmd in ("list", "ls"):
        return cmd_list()
    elif cmd == "status":
        return cmd_status()
    else:
        print("agent-spec  CLI  —  MOD-INF-019  蓝图→Skill 升级引擎")
        print("  python -m zephyr.agent_spec list      列出所有已注册 Skill")
        print("  python -m zephyr.agent_spec status    显示模块健康状态")
        return 0


if __name__ == "__main__":
    sys.exit(main())
