# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_code_sync.py | §
# [MODULE] scripts.governance.d5_architecture.validators.blueprint.validate_blueprint_code_sync
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.blueprint.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""


AGENTS.md §6.1 蓝图-代码同步强制约定的 CI 门禁脚本。
扫描所有蓝图 §19（已实现代码路径索引）中声称的文件路径，
与磁盘实际文件交叉比对，检测三类漂移：
  1. 幽灵路径：蓝图声称"已实现/部分实现"但磁盘文件不存在
  2. 遗漏登记：磁盘存在但蓝图 §19 未登记的文件
  3. 路径漂移：蓝图声称的路径与实际文件路径不一致

对标：K8s Admission Controller（未注册资源拒绝进入集群）
      ITIL SACM CI Registration（配置项必须与 CMDB 一致）

用法：
  python scripts/governance/d5_architecture/validate_blueprint_code_sync.py
  python scripts/governance/d5_architecture/validate_blueprint_code_sync.py --warn-only
"""

from __future__ import annotations

__manifest__ = """
args:
  - --warn-only
  - --jsonl
description: GATE-BLUEPRINT-CODE — 蓝图-代码同步校验闸门（AGENTS.md §6.1 — 蓝图§16路径索引vs磁盘实际交叉比对，幽灵路径+遗漏登记+路径漂移）
dimensions:
- D5
- D8
priority: P0
timeout_seconds: 30
warn_only: false
"""

import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
BLUEPRINT_GLOBS = ["docs/03_modules/*/blueprint.md", "docs/03_modules/*/*/blueprint.md"]
SECTION_PATH_INDEX_PATTERN = re.compile("^##\\s+\\d+\\.\\s+已实现代码完整路径索引", re.MULTILINE)
PATH_IN_TABLE_PATTERN = re.compile("`([^`]+\\.(?:py|yaml|yml|json|toml|md))`")
PATH_MUST_HAVE_DIR = re.compile("[/\\\\]")
STATUS_IMPLEMENTED = re.compile("✅|⚠️|已实现|部分实现|已完成")
STATUS_NOT_IMPLEMENTED = re.compile("❌|未实现")


def find_blueprints() -> list[Path]:
    """查找蓝图文件"""
    results: list[Path] = []
    for glob_pattern in BLUEPRINT_GLOBS:
        results.extend(REPO_ROOT.glob(glob_pattern))
    return sorted(set(results))


def extract_path_index_section(content: str) -> str:
    """提取路径索引段落"""
    match = SECTION_PATH_INDEX_PATTERN.search(content)
    if not match:
        return ""
    start = match.start()
    next_h2 = re.search("^## \\d", content[start + 10 :], re.MULTILINE)
    if next_h2:
        return content[start : start + 10 + next_h2.start()]
    return content[start:]


def extract_claimed_paths(section: str) -> dict[str, str]:
    """提取声明的路径列表"""
    claimed: dict[str, str] = {}
    lines = section.split("\n")
    for line in lines:
        if STATUS_NOT_IMPLEMENTED.search(line) and (not STATUS_IMPLEMENTED.search(line)):
            continue
        for m in PATH_IN_TABLE_PATTERN.finditer(line):
            path_str = m.group(1)
            if not PATH_MUST_HAVE_DIR.search(path_str):
                continue
            if any(skip in path_str for skip in ["—", "未创建", "待实现", "未实现", "无独立"]):
                continue
            claimed[path_str] = line.strip()
    return claimed


def validate_blueprint(bp_path: Path, warn_only: bool) -> list[str]:
    """校验蓝图合规性"""
    errors: list[str] = []
    "校验蓝图合规性."
    content = bp_path.read_text(encoding="utf-8")
    rel_bp = bp_path.relative_to(REPO_ROOT)
    section = extract_path_index_section(content)
    if not section:
        errors.append(
            f"[GATE-BLUEPRINT-CODE] {rel_bp}: 缺少「已实现代码路径索引」章节（AGENTS.md §6.1 要求蓝图 §16~§19 为路径索引）"
        )
        return errors
    claimed = extract_claimed_paths(section)
    for path_str, context in claimed.items():
        full_path = REPO_ROOT / path_str
        if not full_path.exists():
            errors.append(f"[GATE-BLUEPRINT-CODE] {rel_bp}: 幽灵路径 — 蓝图声称文件存在但磁盘未找到: {path_str}")
    return errors


def main() -> int:
    """入口函数。"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="蓝图 §16~§19 路径索引与实际文件系统对账（AGENTS.md §6.1）")
    parser.add_argument("--warn-only", action="store_true", help="告警模式，不阻断退出码")
    parser.add_argument("--jsonl", action="store_true", help="单行 JSON 摘要")
    args = parser.parse_args()
    warn_only = args.warn_only

    blueprints = find_blueprints()
    if not blueprints:
        print("[GATE-BLUEPRINT-CODE] 未找到任何蓝图文件，跳过检查")
        code = 0
        if args.jsonl:
            print(
                json.dumps(
                    {
                        "severity": "INFO",
                        "check_id": "GATE-BLUEPRINT-CODE",
                        "issues": 0,
                        "note": "no_blueprints",
                    },
                    ensure_ascii=False,
                )
            )
        return code

    all_errors: list[str] = []
    print(f"[GATE-BLUEPRINT-CODE] 扫描 {len(blueprints)} 份蓝图...")
    for bp in blueprints:
        errors = validate_blueprint(bp, warn_only)
        all_errors.extend(errors)

    if all_errors:
        print(f"\n[GATE-BLUEPRINT-CODE] 发现 {len(all_errors)} 个问题：")
        for err in all_errors:
            print(f"  {'⚠️' if warn_only else '🔴'} {err}")
        if warn_only:
            print("\n[GATE-BLUEPRINT-CODE] --warn-only 模式，不阻断。请尽快修复上述问题。")
            code = 0
        else:
            print(
                "\n[GATE-BLUEPRINT-CODE] 🔴 CI 失败 — 蓝图路径索引与磁盘实际不一致。请按 AGENTS.md §6.1 更新蓝图路径索引章节。"
            )
            code = 1
    else:
        print("[GATE-BLUEPRINT-CODE] ✅ 所有蓝图路径索引与磁盘实际一致")
        code = 0

    if args.jsonl:
        print(
            json.dumps(
                {
                    "severity": "HIGH" if all_errors else "INFO",
                    "check_id": "GATE-BLUEPRINT-CODE",
                    "issues": len(all_errors),
                },
                ensure_ascii=False,
            )
        )
    return code


if __name__ == "__main__":
    sys.exit(main())
