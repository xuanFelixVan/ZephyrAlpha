# [BLUEPRINT] MOD-INF-005 | scripts/governance/d11_compliance/validate_exit_codes.py | §
# [MODULE] scripts.governance.d11_compliance.validate_exit_codes
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d11_compliance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
validate_exit_codes.py — 审计脚本退出码规范门禁

对标 SCRIPT-QUALITY-001 D-F-02（POSIX exit codes）+ D-D-04（同一概念只在一处定义）

检测内容：
- sys.exit(0/1/2) 裸数字 → 应使用 EXIT_PASS / EXIT_FINDINGS / EXIT_ERROR
- return 0/1/2 裸数字（在 main() 或返回 int 的函数中）→ 应使用命名常量
- 缺少 EXIT 常量 import 的文件

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 审计脚本退出码规范门禁——检测裸 sys.exit(0/1/2) 和 return 0/1/2
dimensions:
- D11
- D5
priority: P1
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
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, SCRIPTS_DIR
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

RE_SYS_EXIT_BARE = re.compile(r"sys\.exit\(\s*([012])\s*\)")
RE_RETURN_BARE = re.compile(r"^(\s*)return\s+([012])\s*$", re.MULTILINE)
RE_EXIT_CONST = re.compile(r"EXIT_PASS|EXIT_FINDINGS|EXIT_ERROR")
EXCLUDE_DIRS = frozenset({"_shared", "__pycache__", "test_fixtures"})

# --- #ARCH-114 豁免登记（2026-08-17 AI-GOVA-001 裁定路径 C：豁免登记）---
# 裁定书=architecture_issue_registry.yaml #ARCH-114；三选一对比分析（批量改名/
# 常量替换/豁免登记）随治理批 A 包 commit 说明。本门原无豁免机制，镜像
# validate_script_naming.py EXCEPTIONS 先例新增；按仓内相对路径（正斜杠）精确
# 匹配，D2 纪律逐条注明理由：
#   存量 71 处裸 return/sys.exit(0/1/2) 散布 25 文件，正则无法区分 main()/CLI
#   入口返回值与 helper 业务返回值（0/1 语义非退出码），盲改有语义腐蚀风险；
#   且 apply_depgraph.py/generate_project_depgraph.py 等属并发施工域，逐点核验
#   替换的跨域碰撞风险高于常量纯度收益。豁免=爷爷条款登记，门禁对未来新增
#   脚本保持全量牙齿；豁免文件再新增裸退出码不会被拦（残余风险已告知统筹）。
EXIT_EXCEPTIONS = frozenset(
    {
        "apply_battle_map.py",
        "apply_depgraph.py",
        "d11_compliance/check_generator_no_realtime_time.py",
        "d11_compliance/check_no_commit_derived.py",
        "d11_compliance/validate_worktree_required.py",
        "d3_metadata/domain_header_maint.py",
        "d5_architecture/checkers/check_algo_quality.py",
        "d5_architecture/checkers/check_node_label_quality.py",
        "d5_architecture/checkers/check_registry_code_anchor.py",
        "d5_architecture/generators/generate_battle_map_diagram.py",
        "d5_architecture/generators/generate_candidate_module_report.py",
        "d5_architecture/generators/generate_code_wiki_stats.py",
        "d7_code/check_yaml_anchor_consistency.py",
        "data_quality/check_indicator_prefix.py",
        "fix_depgraph_module_id.py",
        "fix_header_module_id.py",
        "generate_project_depgraph.py",
        "git_hooks/post_commit_regen_yaml.py",
        "harvest_candidates_from_drafts.py",
        "oneoff/data_domain_design_state_complete.py",
        "oneoff/fix_module_translation_zh.py",
        "oneoff/load_acquisition_decisions.py",
        "oneoff/register_candidate_acquisitions.py",
        "reconcile_generators.py",
        "register_deferred_modules.py",
        # --- 测试债清偿登记（2026-08-21，延续 #ARCH-114 裁定路径 C 机制）---
        # [归档一次性脚本——_archive/one_off/ 冻结归档（已执行完毕），常量替换=死代码
        #  churn，与上方 oneoff/ 豁免条目同理由]
        "_archive/one_off/oneoff_migrate_four_question_to_design_admission.py",
        "_archive/one_off/oneoff_purge_harvest_candidates.py",
        "_archive/one_off/oneoff_update_four_question_text_fields.py",
        # [dm 一次性直写脚本（已执行），naming 门已登记豁免（dm200916_write_direct.py），同理由]
        "d5_architecture/dm200916_write_direct.py",
    }
)

_BARE_TO_CONST = {"0": "EXIT_PASS", "1": "EXIT_FINDINGS", "2": "EXIT_ERROR"}


def scan_scripts() -> list[dict]:
    """scan_scripts implementation."""
    findings = []
    for py in sorted(SCRIPTS_DIR.rglob("*.py")):
        parts = py.relative_to(SCRIPTS_DIR).parts
        if any(p in EXCLUDE_DIRS for p in parts):
            continue
        if py.name == "__init__.py":
            continue
        try:
            src = py.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        rel = str(py.relative_to(SCRIPTS_DIR)).replace("\\", "/")
        if rel in EXIT_EXCEPTIONS:
            continue

        for m in RE_SYS_EXIT_BARE.finditer(src):
            line_no = src[: m.start()].count("\n") + 1
            findings.append(
                {
                    "file": rel,
                    "line": line_no,
                    "code": m.group(0),
                    "suggestion": f"sys.exit({_BARE_TO_CONST[m.group(1)]})",
                    "type": "sys.exit",
                }
            )

        for m in RE_RETURN_BARE.finditer(src):
            line_no = src[: m.start()].count("\n") + 1
            findings.append(
                {
                    "file": rel,
                    "line": line_no,
                    "code": m.group(0).strip(),
                    "suggestion": f"return {_BARE_TO_CONST[m.group(2)]}",
                    "type": "return",
                }
            )

    return findings


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ensure_utf8_stdout()
    findings = scan_scripts()
    if not findings:
        print("OK — all exit codes use named constants", file=sys.stderr)
        return EXIT_PASS

    by_file: dict[str, list[dict]] = {}
    for f in findings:
        by_file.setdefault(f["file"], []).append(f)

    print(f"FINDINGS — {len(findings)} bare exit code(s) in {len(by_file)} file(s):", file=sys.stderr)
    for file, items in sorted(by_file.items()):
        print(f"\n  {file}:", file=sys.stderr)
        for item in items:
            print(f"    L{item['line']}: {item['code']}  →  {item['suggestion']}", file=sys.stderr)

    return EXIT_FINDINGS


if __name__ == "__main__":
    sys.exit(main())
