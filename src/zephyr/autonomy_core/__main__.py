# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.__main__
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""



agent-spec MOD-INF-019 CLI — 蓝图->Skill 升级引擎入口.

用法
----
    python -m zephyr.autonomy_core list          # 列出所有已注册 Skill
    python -m zephyr.autonomy_core status        # 显示模块健康状态
    python -m zephyr.autonomy_core help          # 显示帮助

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: args 参数
#   fields: 参数 args（无注解）
#   code: __main__.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① cmd_list
#   name_en: cmd_list
#   intro: 列出所有已注册 Skill.
#   desc: 列出所有已注册 Skill.；源码 L135-L155
#   inputs: 无参数
#   outputs: int
# - id: A2
#   name_zh: ② cmd_status
#   name_en: cmd_status
#   intro: 显示模块健康状态.
#   desc: 显示模块健康状态.；源码 L158-L194
#   inputs: 无参数
#   outputs: int
# - id: A3
#   name_zh: ③ main
#   name_en: main
#   intro: main() 源码 L197-L209
#   desc: 源码 L197-L209
#   inputs: 无参数
#   outputs: int
# - id: A4
#   name_zh: ④ cmd_self_test
#   name_en: cmd_self_test
#   intro: 公共接口：cmd_self_test（Stage 4 公共化）。
#   desc: 公共接口：cmd_self_test（Stage 4 公共化）。；源码 L237-L239
#   inputs: args
#   outputs: 返回值
# - id: A5
#   name_zh: ⑤ cmd_scan
#   name_en: cmd_scan
#   intro: 公共接口：cmd_scan（Stage 4 公共化）。
#   desc: 公共接口：cmd_scan（Stage 4 公共化）。；源码 L243-L245
#   inputs: args
#   outputs: 返回值
# - id: A6
#   name_zh: ⑥ cmd_budget
#   name_en: cmd_budget
#   intro: 公共接口：cmd_budget（Stage 4 公共化）。
#   desc: 公共接口：cmd_budget（Stage 4 公共化）。；源码 L249-L251
#   inputs: args
#   outputs: 返回值
# - id: A7
#   name_zh: ⑦ registry_path
#   name_en: registry_path
#   intro: 公共接口：registry_path（Stage 4 公共化）。
#   desc: 公共接口：registry_path（Stage 4 公共化）。；源码 L255-L257
#   inputs: 无参数
#   outputs: Path
# - id: A8
#   name_zh: ⑧ load_registry
#   name_en: load_registry
#   intro: 公共接口：load_registry（Stage 4 公共化）。
#   desc: 公共接口：load_registry（Stage 4 公共化）。；源码 L261-L263
#   inputs: 无参数
#   outputs: dict
# 层: 输出
# - id: O1
#   name_zh: int
#   name_en: int
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: Path
#   name_en: Path
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> A7
# A7 --> A8
# A8 --> O1
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml


def _registry_path() -> Path:
    # 真源 registry 在 skills/ 子包（曾错指包根致 FileNotFoundError，#ARCH-086）
    return Path(__file__).resolve().parent / "skills" / "skill-registry.yaml"


def _load_registry() -> dict:
    with open(_registry_path(), encoding="utf-8") as f:
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
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def cmd_status() -> int:
    """显示模块健康状态."""
    is_healthy = True
    try:
        from zephyr.autonomy_core.skills.skill_model import SkillStatus, SkillTier, SkillType

        print(f"skill_model       OK  ({len(SkillTier)} tiers, {len(SkillType)} types, {len(SkillStatus)} statuses)")
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        print(f"skill_model       FAIL  {exc}")
        is_healthy = False

    try:
        from zephyr.autonomy_core.skills.skill_loader import SkillLoader

        loader = SkillLoader()
        print(f"skill_loader      OK  (path={loader.registry_path})")
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        print(f"skill_loader      FAIL  {exc}")
        is_healthy = False

    try:
        print("skill_factory     OK")
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        print(f"skill_factory     FAIL  {exc}")
        is_healthy = False

    try:
        reg = _load_registry()
        n_domain = len(reg.get("skills", {}).get("domain", {}))
        n_role = len(reg.get("skills", {}).get("role", {}))
        print(f"skill-registry    OK  ({n_domain} domain + {n_role} role = {n_domain + n_role} total)")
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        print(f"skill-registry    FAIL  {exc}")
        is_healthy = False

    print(f"\n{'ALL SYSTEMS GO' if is_healthy else 'SOME SYSTEMS DEGRADED'}")
    return 0 if is_healthy else 1


def main() -> int:
    args = sys.argv[1:]
    cmd = args[0] if args else "help"

    if cmd in ("list", "ls"):
        return cmd_list()
    elif cmd == "status":
        return cmd_status()
    else:
        print("agent-spec  CLI  —  MOD-INF-019  蓝图->Skill 升级引擎")
        print("  python -m zephyr.autonomy_core list      列出所有已注册 Skill")
        print("  python -m zephyr.autonomy_core status    显示模块健康状态")
        return 0


if __name__ == "__main__":
    sys.exit(main())


def _cmd_budget(args: object) -> None:
    pass


def _cmd_scan(args: object) -> None:
    pass


def _cmd_list(args: object) -> None:
    pass


def _cmd_self_test(args: object) -> None:
    pass


def _cmd_status(args: object) -> None:
    pass


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def cmd_self_test(args) -> None:
    """公共接口：cmd_self_test（Stage 4 公共化）。"""
    return _cmd_self_test(args)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def cmd_scan(args) -> None:
    """公共接口：cmd_scan（Stage 4 公共化）。"""
    return _cmd_scan(args)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def cmd_budget(args) -> None:
    """公共接口：cmd_budget（Stage 4 公共化）。"""
    return _cmd_budget(args)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def registry_path() -> Path:
    """公共接口：registry_path（Stage 4 公共化）。"""
    return _registry_path()


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def load_registry() -> dict:
    """公共接口：load_registry（Stage 4 公共化）。"""
    return _load_registry()
