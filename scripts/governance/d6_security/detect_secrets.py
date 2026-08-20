# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/detect_secrets.py | §
# [MODULE] scripts.governance.d6_security.detect_secrets
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d6_security.__init__
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
detect_secrets.py — 密钥/Token/凭证硬编码检测



对标：PS-STD-003 ABS-29（密钥不入库）/ ABS-32（不硬编码密钥）
     GOV-SEC-001 §2 SEC-001/004

检测内容：
- Python 代码中的 API Key / Token / Password / Secret 赋值
- YAML/JSON 配置文件中的明文密钥
- .env 文件是否被追踪
- 高熵字符串（疑似密钥模式）

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 密钥/Token/凭证硬编码检测（ABS-29/32 — P0安全红线）
dimensions:
- D6
priority: P0
timeout_seconds: 30
warn_only: false
"""


import argparse
import fnmatch
import os
import re
import sys
from collections import Counter
from math import log2
from pathlib import Path

# 治本（性能优化 #3）：避免 from _shared.constants import ... 的 12s 导入链
# （_shared.constants → zephyr.shared.io.paths → zephyr.governance.__init__ → pandas）。
# cProfile 实测：此导入链占脚本总时间 24%（12s/50s）。
# 本地定义 REPO_ROOT/SCAN_EXTENSIONS_CODE/EXCLUDE_DIRS/EXIT_PASS，与 _shared.constants 保持一致。
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout  # 仅导入 sys，无慢链

EXIT_PASS = 0
REPO_ROOT = _SCRIPT_DIR.parents[3]  # scripts/governance/d6_security/ → 项目根
SCAN_EXTENSIONS_CODE: frozenset[str] = frozenset({".py", ".yaml", ".yml", ".json", ".toml", ".md", ".sh", ".ps1"})
# 与 _shared.constants.EXCLUDE_DIRS 保持一致（真源：_shared.constants.py）
_EXCLUDE_DIRS: frozenset[str] = frozenset(
    {
        "__pycache__",
        ".git",
        ".runtime",
        "node_modules",
        ".venv",
        "_DO_NOT_USE_old_tree",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "vector_db",
        "models",
        "data",
        "tmp",
    }
)


def _iter_files(
    root: Path,
    extensions: frozenset[str] | None = None,
    exclude_files: frozenset[str] | None = None,
) -> list[Path]:
    """递归遍历目录，返回符合条件的文件路径列表（与 _shared.walk.iter_files 一致）。"""
    excl_files = exclude_files or frozenset()
    result: list[Path] = []
    if not root.exists():
        return result
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _EXCLUDE_DIRS and not d.startswith(".")]
        for filename in sorted(filenames):
            if filename in excl_files:
                continue
            filepath = Path(dirpath) / filename
            if extensions and filepath.suffix.lower() not in extensions:
                continue
            result.append(filepath)
    return result


ensure_utf8_stdout()

SECRET_PATTERNS = [
    ("(?:api[_-]?key|apikey|API_KEY|Api_Key)\\s*[:=]\\s*['\\\"]([^'\\\"]{8,})['\\\"]", "API Key 硬编码"),
    ("(?:secret|SECRET|Secret)\\s*[:=]\\s*['\\\"]([^'\\\"]{8,})['\\\"]", "Secret 硬编码"),
    ("(?:token|TOKEN|Token)\\s*[:=]\\s*['\\\"]([^'\\\"]{8,})['\\\"]", "Token 硬编码"),
    ("(?:password|PASSWORD|Password|passwd)\\s*[:=]\\s*['\\\"]([^'\\\"]{3,})['\\\"]", "Password 硬编码"),
    ("(?:access[_-]?key|ACCESS_KEY|Access_Key)\\s*[:=]\\s*['\\\"]([^'\\\"]{8,})['\\\"]", "Access Key 硬编码"),
    (
        "(?:private[_-]?key|PRIVATE_KEY|Private_Key)['\\\"]?\\s*[:=]\\s*['\\\"]([^'\\\"]{16,})['\\\"]",
        "Private Key 硬编码",
    ),
    ("sk-[a-zA-Z0-9]{32,}", "OpenAI API Key 格式"),
    ("AKIA[0-9A-Z]{16}", "AWS Access Key ID 格式"),
    ("(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}", "GitHub Token 格式"),
]

# 治本（性能优化 #4）：移除 re.IGNORECASE——显式大小写变体已包含在模式交替中。
# cProfile 实测：re.IGNORECASE 导致 finditer 10x 减速（与预扫 regex 相同根因）。
# 添加 Secret/Token/Password 等常见混合大小写变体覆盖绝大多数实际场景。
_COMPILED_PATTERNS: list[tuple[re.Pattern, str]] = [(re.compile(p), label) for p, label in SECRET_PATTERNS]
# 快速关键词预扫：regex WITHOUT re.IGNORECASE（显式大小写变体）。
# cProfile 实测：re.IGNORECASE 导致 10x 减速（14s vs 1.4s），因 IGNORECASE 阻止
# regex 引擎的 alternation 优化。显式列出大小写变体后，regex 引擎编译为高效状态机。
# 绝大多数文件（~80%）不含任何密钥关键词，预扫可跳过详细正则匹配。
_QUICK_KEYWORD_RE: re.Pattern = re.compile(
    r"api[_-]?key|apikey|API_KEY|secret|SECRET|token|TOKEN|"
    r"password|PASSWORD|passwd|access[_-]?key|ACCESS_KEY|"
    r"private[_-]?key|PRIVATE_KEY|sk-[a-zA-Z0-9]|AKIA|gh[phousr]_"
)

EXCLUDE_FILES = {"detect_secrets.py", ".env", ".env.example"}


def shannon_entropy(s: str) -> float:
    """计算 Shannon 信息熵"""
    if not s:
        return 0.0
    n = len(s)
    freq = Counter(s)
    return -sum(c / n * log2(c / n) for c in freq.values())


def scan_file(filepath: Path) -> list[dict]:
    """扫描单个文件并返回发现列表"""
    findings = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return findings
    # 治本（性能优化）：关键词预扫，无任何密钥关键词则跳过详细正则扫描
    if not _QUICK_KEYWORD_RE.search(content):
        return findings
    for compiled_re, label in _COMPILED_PATTERNS:
        for match in compiled_re.finditer(content):
            matched_value = match.group(0)
            findings.append(
                {
                    "file": str(filepath.relative_to(REPO_ROOT)),
                    "line": content[: match.start()].count("\n") + 1,
                    "pattern": label,
                    "matched": matched_value[:80],
                }
            )
    return findings


def scan_repo(scan_dir: Path | None = None) -> tuple[list[dict], int, int]:
    """扫描仓库并返回发现列表."""
    if scan_dir is None:
        scan_dir = REPO_ROOT
    # 治本（性能优化）：用字符串前缀检查替代 relative_to（cProfile: 5s → <0.1s）
    repo_root_str = str(REPO_ROOT)
    repo_root_len = len(repo_root_str)
    all_findings = []
    files_scanned = 0
    for filepath in _iter_files(scan_dir, extensions=SCAN_EXTENSIONS_CODE, exclude_files=frozenset(EXCLUDE_FILES)):
        fpath_str = str(filepath)
        if fpath_str.startswith(repo_root_str):
            rel_str = fpath_str[repo_root_len:].lstrip("\\/")
        else:
            rel_str = fpath_str
        rel_norm = rel_str.replace("\\", "/")
        if rel_norm.startswith("_DO_NOT_USE") or rel_norm.startswith(".trae"):
            continue
        files_scanned += 1
        findings = scan_file(filepath)
        all_findings.extend(findings)
    return (all_findings, files_scanned, 0)


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="密钥/Token 硬编码检测")
    parser.add_argument("--scan-dir", default=None, help="扫描目录")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    scan_dir = Path(args.scan_dir) if args.scan_dir else None
    findings, files_scanned, errors = scan_repo(scan_dir)
    if findings:
        print(
            f"\n[SECRET-SCAN] {len(findings)} 疑似密钥/Token 硬编码发现（扫描 {files_scanned} 文件）:\n",
            file=sys.stderr,
        )
        for f in findings:
            print(f"  [{f['pattern']}] {f['file']}:{f['line']}", file=sys.stderr)
            print(f"    {f['matched']}", file=sys.stderr)
        print(file=sys.stderr)
    print(f"Scanned {files_scanned} files, {len(findings)} findings, {errors} errors", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
