# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/validate_rules_file_backdoor.py | §
# [MODULE] scripts.governance.meta.validate_rules_file_backdoor
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.meta.__init__
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
"""validate_rules_file_backdoor.py — Rules File Backdoor 检测器

对标 B43（Rules File Backdoor）+ Snyk/Lasso Security 2025 年发现的
AI 规则文件隐形投毒攻击。

检测 AGENTS.md / quickstart.md / thresholds.yaml / blueprint.md / kill_switch_state.yaml /
shadow_mode_state.yaml / error_budget_state.yaml 等关键规则文件中的：
- 零宽连接符 (Zero-Width Joiner: U+200D)
- 零宽非连接符 (Zero-Width Non-Joiner: U+200C)
- 双向文本标记 (Bidirectional markers: U+200E/U+200F/U+202A-U+202E/U+2066-U+2069)
- 零宽空格 (Zero-Width Space: U+200B)
- 字节序标记 (BOM: U+FEFF)
- 软连字符 (Soft Hyphen: U+00AD)
- 从右到左覆盖 (RLM/RLO/LRM/LRO)
- 其他不可见控制字符 (U+0000-U+001F, U+007F-U+009F，白名单字符除外)

这些字符人眼不可见但 AI Agent 会读取并执行隐藏指令。

Usage:
    python scripts/governance/meta/validate_rules_file_backdoor.py
    python scripts/governance/meta/validate_rules_file_backdoor.py --file path/to/file.md
    python scripts/governance/meta/validate_rules_file_backdoor.py --json
    python scripts/governance/meta/validate_rules_file_backdoor.py --warn-only
"""

from __future__ import annotations

__manifest__ = """
args: []
description: >
  Rules File Backdoor 检测器——检测关键规则文件中不可见控制字符（零宽符、双向文本标记等），
  防御 AI 规则文件隐形投毒攻击。
dimensions:
- D1
- D6
priority: P0
timeout_seconds: 30
warn_only: false
"""


import argparse
import json as json_mod
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
from datetime import UTC, datetime
from pathlib import Path

# 治本(2026-06-30): REPO_ROOT 真源来自 _shared.constants, 消除 parents[N] 硬编码
# 原 parents[2] 实为 scripts 目录而非 repo root, 变量名误导且路径计算有 bug
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT as _REPO_ROOT  # noqa: E402
_SCRIPTS_DIR = _REPO_ROOT / "scripts" / "governance"

RULE_FILES: list[Path] = [
    _REPO_ROOT / "AGENTS.md",
    _SCRIPTS_DIR / "quickstart.md",
    _SCRIPTS_DIR / "_shared" / "thresholds.yaml",
    _SCRIPTS_DIR / "meta" / "kill_switch_state.yaml",
    _SCRIPTS_DIR / "meta" / "shadow_mode_state.yaml",
    _SCRIPTS_DIR / "meta" / "error_budget_state.yaml",
    _SCRIPTS_DIR / "quality_standard.md",
    _SCRIPTS_DIR / "script_manifest.yaml",
    _REPO_ROOT / "docs" / "03_modules" / "infrastructure_runtime_integration" / "script-system" / "blueprint.md",
    _REPO_ROOT / "docs" / "03_modules" / "infrastructure_runtime_integration" / "script-system" / "index.md",
]

# Unicode 不可见控制字符危险集
DANGEROUS_INVISIBLE: dict[int, str] = {
    0x200B: "ZERO-WIDTH SPACE",
    0x200C: "ZERO-WIDTH NON-JOINER",
    0x200D: "ZERO-WIDTH JOINER",
    0x200E: "LEFT-TO-RIGHT MARK",
    0x200F: "RIGHT-TO-LEFT MARK",
    0x202A: "LEFT-TO-RIGHT EMBEDDING",
    0x202B: "RIGHT-TO-LEFT EMBEDDING",
    0x202C: "POP DIRECTIONAL FORMATTING",
    0x202D: "LEFT-TO-RIGHT OVERRIDE",
    0x202E: "RIGHT-TO-LEFT OVERRIDE",
    0x2066: "LEFT-TO-RIGHT ISOLATE",
    0x2067: "RIGHT-TO-LEFT ISOLATE",
    0x2068: "FIRST STRONG ISOLATE",
    0x2069: "POP DIRECTIONAL ISOLATE",
    0xFEFF: "BYTE ORDER MARK / ZERO-WIDTH NO-BREAK SPACE",
    0x00AD: "SOFT HYPHEN",
    0x180E: "MONGOLIAN VOWEL SEPARATOR",
    0x2060: "WORD JOINER",
    0x2061: "FUNCTION APPLICATION",
    0x2062: "INVISIBLE TIMES",
    0x2063: "INVISIBLE SEPARATOR",
    0x2064: "INVISIBLE PLUS",
}

# ASCII 控制字符白名单（换行/制表符是正常的）
CONTROL_WHITELIST: set[int] = {0x0A, 0x0D, 0x09}


def _scan_file(file_path: Path) -> list[dict]:
    """_scan_file implementation."""
    findings: list[dict] = []
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        findings.append(
            {
                "file": str(file_path.relative_to(_REPO_ROOT)),
                "severity": "CRITICAL",
                "line": 0,
                "column": 0,
                "char_code": "U+????",
                "char_name": "UNREADABLE",
                "detail": "文件无法以 UTF-8 读取——可能被损坏或编码错误",
            }
        )
        return findings

    for idx, ch in enumerate(content):
        cp = ord(ch)
        if cp in DANGEROUS_INVISIBLE:
            line = content[:idx].count("\n") + 1
            col = idx - (content[:idx].rfind("\n") + 1) + 1 if "\n" in content[:idx] else idx + 1
            findings.append(
                {
                    "file": str(file_path.relative_to(_REPO_ROOT)),
                    "severity": "CRITICAL",
                    "line": line,
                    "column": col,
                    "char_code": f"U+{cp:04X}",
                    "char_name": DANGEROUS_INVISIBLE[cp],
                    "detail": f"发现不可见控制字符 {DANGEROUS_INVISIBLE[cp]} (U+{cp:04X})——可能为 Rules File Backdoor 投毒",
                }
            )
        elif cp < 0x20 and cp not in CONTROL_WHITELIST:
            line = content[:idx].count("\n") + 1
            col = idx - (content[:idx].rfind("\n") + 1) + 1 if "\n" in content[:idx] else idx + 1
            findings.append(
                {
                    "file": str(file_path.relative_to(_REPO_ROOT)),
                    "severity": "HIGH",
                    "line": line,
                    "column": col,
                    "char_code": f"U+{cp:04X}",
                    "char_name": f"ASCII CONTROL {cp}",
                    "detail": f"ASCII 控制字符 U+{cp:04X} 不应出现在文本文件规则中",
                }
            )

    return findings


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Rules File Backdoor 检测器")
    parser.add_argument("--file", "-f", type=str, help="指定单个文件扫描")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--warn-only", action="store_true", help="警告模式，不阻断")
    args = parser.parse_args()

    if args.file:
        files = [Path(args.file) if args.file.startswith(str(_REPO_ROOT)) else _REPO_ROOT / args.file]
    else:
        files = RULE_FILES

    all_findings: list[dict] = []
    for fp in files:
        if fp.exists():
            all_findings.extend(_scan_file(fp))

    summary = {
        "timestamp": datetime.now(UTC).isoformat(),
        "files_scanned": len([fp for fp in files if fp.exists()]),
        "findings": all_findings,
        "total": len(all_findings),
        "clean": len(all_findings) == 0,
    }

    if args.json:
        print(json_mod.dumps(summary, ensure_ascii=False, indent=2))
    else:
        if all_findings:
            print(f"\n[RULES-BACKDOOR] 🔴 危险！发现 {len(all_findings)} 个可疑不可见字符", file=sys.stderr)
            for f in all_findings:
                print(f"  [{f['severity']}] {f['file']}:L{f['line']}:{f['column']} — {f['char_name']}", file=sys.stderr)
        else:
            print(f"[RULES-BACKDOOR] ✅ 全部 {len(files)} 个规则文件通过检查——无不可见字符投毒", file=sys.stderr)

    should_block = not args.warn_only and not summary["clean"]
    sys.exit(2 if should_block else 0)


if __name__ == "__main__":
    main()
