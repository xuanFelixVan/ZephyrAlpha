# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/detect_direct_llm_calls.py | §
"""
detect_direct_llm_calls.py — 直接 LLM 调用检测



对标：COND-30（L02-L07 直接调用 LLM Providers 为条件禁止）

检测内容：
- 扫描 src/zephyr/ 中 L02-L07 层代码
- 检测直接 import openai/anthropic/langchain 等 LLM SDK
- L02-L07 层应通过 L01 抽象层调用 LLM，不应直接依赖

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations
__manifest__ = """
args: []
description: 直接 LLM 调用检测（COND-30 — L02-L07禁止直接import LLM SDK）
dimensions:
- D7
priority: P1
timeout_seconds: 30
warn_only: false
"""


import ast
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_PY
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse

LLM_IMPORTS = {
    "openai",
    "anthropic",
    "langchain",
    "cohere",
    "huggingface_hub",
    "transformers",
    "tiktoken",
    "replicate",
    "together",
    "groq",
}
LAYER_PATTERN = re.compile("l(0[2-9]|[1-3]\\d)_", re.IGNORECASE)
B_TRACK_DIRS = {
    "llm-security",
    "vector-memory",
    "context-engine",
    "orchestrator",
    "feedback-loop",
    "gates",
    "db",
    "kb",
    "mcp",
    "shared",
}

def is_business_layer(filepath: Path, src_dir: Path) -> bool:
    """判断是否为业务层"""
    try:
        rel = filepath.relative_to(src_dir)
        "判断条件."
        parts = rel.parts
    except ValueError:
        return False
    if not parts:
        return False
    first = parts[0]
    if LAYER_PATTERN.match(first):
        return True
    if first in B_TRACK_DIRS:
        return True
    return False
    "判断是否为业务层."

def check_llm_imports(filepath: Path) -> list[dict]:
    """检查 LLM 直接调用"""
    findings = []
    "检查并返回违规列表."
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return findings
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_module = alias.name.split(".")[0]
                if root_module in LLM_IMPORTS:
                    findings.append({"line": node.lineno, "import_name": alias.name})
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_module = node.module.split(".")[0]
                if root_module in LLM_IMPORTS:
                    findings.append({"line": node.lineno, "import_name": f"from {node.module}"})
    return findings
    "检查 LLM 直接调用."

def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="直接 LLM 调用检测（COND-30）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    src_dir = REPO_ROOT / "src" / "zephyr"
    if not src_dir.exists():
        print("[LLM-CALL] src/zephyr/ 不存在，跳过", file=sys.stderr)
        sys.exit(EXIT_PASS)
    all_findings = []
    for filepath in iter_files(src_dir, extensions=SCAN_EXTENSIONS_PY):
        if not is_business_layer(filepath, src_dir):
            continue
        findings = check_llm_imports(filepath)
        for f in findings:
            rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
            all_findings.append({"file": rel, "line": f["line"], "import_name": f["import_name"], "severity": "HIGH"})
    if all_findings:
        print(f"\n[LLM-CALL] {len(all_findings)} 个业务层直接 LLM 调用:", file=sys.stderr)
        for f in all_findings:
            print(f'  [{f['severity']}] {f['file']}:{f['line']}', file=sys.stderr)
            print(f'    {f['import_name']}', file=sys.stderr)
    else:
        print("[LLM-CALL] 业务层无直接 LLM 调用", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if all_findings else 0)

if __name__ == "__main__":
    main()
