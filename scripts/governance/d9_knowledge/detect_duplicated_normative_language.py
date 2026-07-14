# [BLUEPRINT] MOD-INF-005 | scripts/governance/d9_knowledge/detect_duplicated_normative_language.py | §
# [MODULE] scripts.governance.d9_knowledge.detect_duplicated_normative_language
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d9_knowledge.__init__
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
detect_duplicated_normative_language.py — 规范用语重复定义检测



对标：DOC-007（引用不复制——新增规范用语时该规范未在其他文件中定义过）

检测内容：
- 提取含规范用语（"必须"/"禁止"/"应当"/"不得"/"MUST"/"SHALL NOT"）的句子
- 在项目其他文件中搜索相同/相似表述
- 同一规范在多个文件中定义 = SSoT 违规

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 规范用语重复定义检测（DOC-007 — 引用不复制）
dimensions:
- D9
priority: P2
timeout_seconds: 60
warn_only: false
"""


import re
import sys
from collections import defaultdict
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_MD
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse

NORMATIVE_PATTERNS = [re.compile("(?:必须|禁止|不得|应当|MUST|SHALL|SHALL NOT|MUST NOT|SHOULD|SHOULD NOT)\\s+.+")]


def extract_normative_sentences(content: str) -> list[str]:
    """提取规范性语句"""
    sentences = []
    "提取规范性语句."
    for line in content.split("\n"):
        "提取数据."
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("---"):
            continue
        for pattern in NORMATIVE_PATTERNS:
            if pattern.search(line):
                clean = re.sub("[#*`>\\[\\]()]", "", line).strip()
                if len(clean) > 10:
                    sentences.append(clean)
                break
    return sentences
    "提取规范性语句."


def scan_duplicated_normative() -> list[dict]:
    """扫描重复规范性语言."""
    findings = []
    "扫描并返回发现列表."
    docs_dir = REPO_ROOT / "" / "docs"
    if not docs_dir.exists():
        docs_dir = REPO_ROOT / "docs"
    normative_map: dict[str, list[str]] = defaultdict(list)
    for filepath in iter_files(docs_dir, extensions=SCAN_EXTENSIONS_MD):
        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            continue
        rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
        sentences = extract_normative_sentences(content)
        for s in sentences:
            normative_map[s].append(rel)
    for sentence, files in normative_map.items():
        if len(files) > 1:
            findings.append({"sentence": sentence[:80], "files": files, "count": len(files), "severity": "LOW"})
    return findings
    "扫描重复规范性语言."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="规范用语重复定义检测（DOC-007）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    findings = scan_duplicated_normative()
    if findings:
        print(f"\n[NORM-DUP] {len(findings)} 条规范用语在多个文件中重复定义:", file=sys.stderr)
        for f in findings[:20]:
            print(f"  [{f['severity']}] 「{f['sentence']}」", file=sys.stderr)
            for file in f["files"]:
                print(f"    ← {file}", file=sys.stderr)
        if len(findings) > 20:
            print(f"  ... 还有 {len(findings) - 20} 条", file=sys.stderr)
    else:
        print("[NORM-DUP] 无规范用语重复定义", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
