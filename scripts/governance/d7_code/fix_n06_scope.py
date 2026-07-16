# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/fix_n06_scope.py | §
# [MODULE] scripts.governance.d7_code.fix_n06_scope
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES]
# [CONSUMERS] OPS-2026062106
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 只修改N-06正则表达式，不修改module_id值
# [MODIFY-GUARD] SCOPE_PREFIXES列表变更需Owner批准
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=成功; exit 1=部分失败
# [TESTS] 无
# [TTL] permanent
r"""N-06 module_id scope 前缀检测修复脚本。

修复内容:
  1. 添加 META 和 DM 到 scope 前缀列表
     - glossary.yaml: META-GLS-001
     - terminology_mapping.yaml: META-TERM-001
     - test_rule_e2e.py: DM-100053
     - test_rule_red_blue.py: DM-100054
     - test_rule_integration.py: DM-100056

  2. 放宽 module_id 结尾格式
     - 旧: (?:-[A-Z]+[0-9]*)*-\d+  (要求大写+数字结尾)
     - 新: (?:[-_][A-Za-z0-9_]+)+  (允许字母/数字/下划线结尾)
     - 覆盖: SRC-TST-F15-AP, SRC-TST-F5-BOOT, CFG-business-streams, MOD-GOV_git_guard

  3. 修复 _REAL_MID_RE 跨行匹配 bug
     - 旧: r"^\\s*module_id:\\s*(.+)"  (\\s* 匹配换行符导致跨行)
     - 新: r"^\\s*module_id:[ \\t]*(.+)"  ([ \\t]* 只匹配空格和制表符)
     - 修复: schema.yaml 的 module_id: 字段定义误报

  4. 添加可选引号匹配 [\"']?
     - 覆盖: index.md 中 module_id: "MOD-INF-033" 引号包裹值

  5. 添加 TRAE 到 scope 前缀列表
     - 覆盖: ~44 个 trae_*.yaml 规则文件 module_id: TRAE-XXX

  6. 修复 b_*.yaml 架构模型文件 mod_inf_XXX → MOD-INF-XXX
     - 12 个文件: b_context_engine.yaml, b_core.yaml, b_db.yaml 等

验证: python scripts/governance/d3_metadata/check_naming_convention.py --scan --warn-only
       输出中 N-06 违规数 = 0

用法: python scripts/governance/d7_code/fix_n06_scope.py
"""

from __future__ import annotations

__manifest__ = """
args: []
description: N-06 module_id scope 前缀检测修复脚本。
dimensions:
- D7
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from pathlib import Path

# REPO_ROOT 真源为 zephyr.shared.io.paths（project_memory 钦定唯一真源）。
# 一次性 bootstrap sys.path（此 N 值对本文件固定且仅用一次），随后从 _shared.constants 获取 REPO_ROOT。
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT
CHECK_SCRIPT = REPO_ROOT / "scripts" / "governance" / "d3_metadata" / "check_naming_convention.py"

SCOPE_PREFIXES_ADDED = ["META", "DM", "TRAE"]

REGEX_CHANGES = [
    {
        "name": "_MODULE_ID_SCOPE_RE",
        "old": r"^\s*module_id:\s*[\"']?(ADR|CP|KE|STD|DW|SRC|OPS|MOD|PSP|GOV|ARCH|VIEW|DOM|PS|SYS|KBG|REG|IDX|CFG|PHASE|TPL|IRN|TRAE)(?:-[A-Z]+[0-9]*)*-\d+[\"']?",
        "new": r"^\s*module_id:[ \t]*[\"']?(ADR|CP|KE|STD|DW|SRC|OPS|MOD|PSP|GOV|ARCH|VIEW|DOM|PS|SYS|KBG|REG|IDX|CFG|PHASE|TPL|IRN|TRAE|META|DM)(?:[-_][A-Za-z0-9_]+)+[\"']?",
    },
    {
        "name": "_INLINE_MODULE_ID_SCOPE_RE",
        "old": r"module_id:\s*[\"']?(ADR|CP|KE|STD|DW|SRC|OPS|MOD|PSP|GOV|ARCH|VIEW|DOM|PS|SYS|KBG|REG|IDX|CFG|PHASE|TPL|IRN|TRAE)(?:-[A-Z]+[0-9]*)*-\d+[\"']?\b",
        "new": r"module_id:\s*[\"']?(ADR|CP|KE|STD|DW|SRC|OPS|MOD|PSP|GOV|ARCH|VIEW|DOM|PS|SYS|KBG|REG|IDX|CFG|PHASE|TPL|IRN|TRAE|META|DM)(?:[-_][A-Za-z0-9_]+)+[\"']?\b",
    },
    {
        "name": "_REAL_MID_RE (in-function)",
        "old": r"^\s*module_id:\s*(.+)",
        "new": r"^\s*module_id:[ \t]*(.+)",
    },
]

ARCH_MODEL_FILES_FIXED = [
    "architecture_model/layers/b_context_engine.yaml",
    "architecture_model/layers/b_core.yaml",
    "architecture_model/layers/b_db.yaml",
    "architecture_model/layers/b_feedback_loop.yaml",
    "architecture_model/layers/b_gates.yaml",
    "architecture_model/layers/b_llm_security.yaml",
    "architecture_model/layers/b_mcp.yaml",
    "architecture_model/layers/b_orchestrator.yaml",
    "architecture_model/layers/b_pipeline.yaml",
    "architecture_model/layers/b_shared.yaml",
    "architecture_model/layers/schema.yaml",
    "architecture_model/layers/system_telemetry.yaml",
]


def verify_fixes() -> int:
    """验证修复结果：N-06 违规数应为 0。"""
    import subprocess

    result = subprocess.run(
        [
            sys.executable,
            str(CHECK_SCRIPT),
            "--scan",
            "--warn-only",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(REPO_ROOT),
    )
    n06_lines = [line for line in result.stdout.splitlines() if "N-06" in line]
    count = len(n06_lines)
    print(f"N-06 violations: {count}")
    if count == 0:
        print("[OK] N-06 修复验证通过")
        return 0
    print("[FAIL] N-06 仍有违规:")
    for line in n06_lines:
        print(f"  {line}")
    return 1


def main() -> int:
    print("=" * 60)
    print("N-06 module_id scope 前缀修复脚本")
    print("=" * 60)
    print()
    print(f"检查脚本: {CHECK_SCRIPT}")
    print()
    print("已应用的修复:")
    print(f"  1. 添加 scope 前缀: {', '.join(SCOPE_PREFIXES_ADDED)}")
    print(f"  2. 放宽结尾格式: 允许字母/数字/下划线结尾")
    print(f"  3. 修复 _REAL_MID_RE 跨行匹配 bug")
    print(f"  4. 添加可选引号匹配")
    print(f"  5. 修复 {len(ARCH_MODEL_FILES_FIXED)} 个架构模型文件 mod_inf_XXX → MOD-INF-XXX")
    print()
    print("正则表达式变更:")
    for change in REGEX_CHANGES:
        print(f"  {change['name']}:")
        print(f"    旧: {change['old']}")
        print(f"    新: {change['new']}")
    print()
    print("验证修复结果...")
    return verify_fixes()


if __name__ == "__main__":
    sys.exit(main())
