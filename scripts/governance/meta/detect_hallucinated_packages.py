# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/detect_hallucinated_packages.py | §
"""
detect_hallucinated_packages.py — 幻觉包（Slopsquatting）防御引擎



对标 B48（Slopsquatting 防御）+ Socket.dev 205K 幻觉包检测 + PyPI JSON API。

扫描新入库 Python 脚本中的所有 import 语句，
对每个第三方包名通过 PyPI JSON API 验证其真实性。
如果包在 PyPI 上不存在 → 视为 AI 幻觉包 → 拒绝入库。

对抗 Slopsquatting——“AI 捏造了不存在的包名，攻击者注册相同包名投毒”。

Usage:
    python scripts/governance/meta/detect_hallucinated_packages.py --file d7_code/validate_new.py
    python scripts/governance/meta/detect_hallucinated_packages.py --check-all
    python scripts/governance/meta/detect_hallucinated_packages.py --json
"""

from __future__ import annotations
__manifest__ = """
args: []
description: ⚠ __manifest__ 缺失——请添加元数据块
dimensions: []
priority: P2
timeout_seconds: 60
warn_only: false
"""


import os
import ast
import json as json_mod
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_DIR = _REPO_ROOT / "scripts" / "governance"
_PYPI_CACHE = _SCRIPTS_DIR / "meta" / "pypi_verified_cache.json"

# 标准库模块白名单（Python 3.11+）
_STDLIB_WHITELIST: set[str] = {
    "abc", "aifc", "argparse", "array", "ast", "asynchat", "asyncio",
    "asyncore", "atexit", "audioop", "base64", "bdb", "binascii", "binhex",
    "bisect", "builtins", "bz2", "calendar", "cgi", "cgitb", "chunk",
    "cmath", "cmd", "code", "codecs", "codeop", "collections", "colorsys",
    "compileall", "concurrent", "configparser", "contextlib", "contextvars",
    "copy", "copyreg", "cProfile", "crypt", "csv", "ctypes", "curses",
    "dataclasses", "datetime", "dbm", "decimal", "difflib", "dis",
    "distutils", "doctest", "email", "encodings", "enum", "errno",
    "faulthandler", "fcntl", "filecmp", "fileinput", "fnmatch", "formatter",
    "fractions", "ftplib", "functools", "gc", "getopt", "getpass",
    "gettext", "glob", "graphlib", "grp", "gzip", "hashlib", "heapq",
    "hmac", "html", "http", "idlelib", "imaplib", "imghdr", "imp",
    "importlib", "inspect", "io", "ipaddress", "itertools", "json",
    "keyword", "lib2to3", "linecache", "locale", "logging", "lzma",
    "mailbox", "mailcap", "marshal", "math", "mimetypes", "mmap",
    "modulefinder", "multiprocessing", "netrc", "nis", "nntplib",
    "numbers", "operator", "optparse", "os", "ossaudiodev", "pathlib",
    "pdb", "pickle", "pickletools", "pipes", "pkgutil", "platform",
    "plistlib", "poplib", "posix", "posixpath", "pprint", "profile",
    "pstats", "pty", "pwd", "py_compile", "pyclbr", "pydoc", "queue",
    "quopri", "random", "re", "readline", "reprlib", "resource",
    "rlcompleter", "runpy", "sched", "secrets", "select", "selectors",
    "shelve", "shlex", "shutil", "signal", "site", "smtpd", "smtplib",
    "sndhdr", "socket", "socketserver", "spwd", "sqlite3", "ssl",
    "stat", "statistics", "string", "stringprep", "struct", "subprocess",
    "sunau", "symtable", "sys", "sysconfig", "syslog", "tabnanny",
    "tarfile", "telnetlib", "tempfile", "termios", "textwrap",
    "threading", "time", "timeit", "tkinter", "token", "tokenize",
    "trace", "traceback", "tracemalloc", "tty", "turtle", "turtledemo",
    "types", "typing", "unicodedata", "unittest", "urllib", "uu",
    "uuid", "venv", "warnings", "wave", "weakref", "webbrowser",
    "winreg", "winsound", "wsgiref", "xdrlib", "xml", "xmlrpc",
    "zipapp", "zipfile", "zipimport", "zlib", "_thread", "__future__",
}

# 已知本地/已安装的包缓存
_KNOWN_LOCAL: set[str] = set()

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


def _load_cache() -> dict:
    """_load_cache implementation."""
    if not _PYPI_CACHE.exists():
        return {"verified": {}, "hallucinated": {}}
    with open(_PYPI_CACHE, encoding="utf-8") as f:
        return json_mod.load(f)


def _save_cache(data: dict) -> None:
    """_save_cache implementation."""
    _PYPI_CACHE.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = f"{_PYPI_CACHE}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, encoding="utf-8") as f:
            json_mod.dump(data, f, ensure_ascii=False, indent=2)
    
    
        os.replace(tmp_path, _PYPI_CACHE)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
def _extract_imports(file_path: Path) -> list[str]:
    """_extract_imports implementation."""
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return []

    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module.split(".")[0])
    return imports


def _is_real_package(pkg_name: str, cache: dict) -> bool:
    """_is_real_package implementation."""
    if pkg_name in _STDLIB_WHITELIST:
        return True
    if pkg_name in cache.get("verified", {}):
        return True
    if pkg_name in cache.get("hallucinated", {}):
        return False

    try:
        import urllib.request
        url = f"https://pypi.org/pypi/{pkg_name}/json"
        req = urllib.request.Request(url, headers={"User-Agent": "ZephyrAlpha/slopsquatting-defender"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                cache.setdefault("verified", {})[pkg_name] = True
                return True
    except Exception:
        pass

    try:
        import importlib
        importlib.import_module(pkg_name)
        cache.setdefault("verified", {})[pkg_name] = True
        return True
    except ImportError:
        pass

    cache.setdefault("hallucinated", {})[pkg_name] = True
    return False


def check_file(file_path: str | Path) -> dict:
    """Check compliance and report findings."""
    fp = _REPO_ROOT / file_path if not str(file_path).startswith(str(_REPO_ROOT)) else Path(file_path)
    if not fp.exists():
        return {"error": f"File not found: {fp}"}

    cache = _load_cache()
    imports = _extract_imports(fp)
    hallucinated: list[dict] = []

    for pkg in set(imports):
        if pkg.startswith("_"):
            continue
        if not _is_real_package(pkg, cache):
            hallucinated.append({
                "package": pkg,
                "severity": "CRITICAL",
                "detail": f"包 '{pkg}' 在 PyPI 上不存在——可能是 AI 幻觉包（Slopsquatting 候选）",
            })

    _save_cache(cache)

    return {
        "file": str(fp.relative_to(_REPO_ROOT)),
        "total_imports": len(set(imports)),
        "third_party": len(set(imports) - _STDLIB_WHITELIST),
        "hallucinated": hallucinated,
        "hallucinated_count": len(hallucinated),
        "clean": len(hallucinated) == 0,
    }


def check_all() -> dict:
    """Check compliance and report findings."""
    all_results: list[dict] = []
    for py_file in _SCRIPTS_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        result = check_file(py_file)
        if not result.get("clean", True):
            all_results.append(result)

    return {
        "total_scripts_scanned": sum(1 for _ in _SCRIPTS_DIR.rglob("*.py") if "__pycache__" not in str(_)),
        "scripts_with_hallucinations": len(all_results),
        "findings": all_results,
        "clean": len(all_results) == 0,
    }


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    if "--check-all" in sys.argv:
        result = check_all()
        if result["clean"]:
            print(f"[SLOPSQUATTING] ✅ 全部 {result['total_scripts_scanned']} 个脚本 import 验证通过", file=sys.stderr)
        else:
            print(f"[SLOPSQUATTING] 🔴 {result['scripts_with_hallucinations']} 个脚本含幻觉包", file=sys.stderr)
            for f in result["findings"]:
                for h in f["hallucinated"]:
                    print(f"  [{h['severity']}] {f['file']}: {h['package']} — {h['detail']}", file=sys.stderr)
        sys.exit(0 if result["clean"] else 2)
    elif "--file" in sys.argv:
        idx = sys.argv.index("--file")
        file_path = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
        result = check_file(file_path)
        if "--json" in sys.argv:
            print(json_mod.dumps(result, ensure_ascii=False, indent=2))
        else:
            if result.get("clean", True):
                print(f"[SLOPSQUATTING] ✅ {result['file']}: 全部 {result['total_imports']} 个 import 为真实包", file=sys.stderr)
            else:
                print(f"[SLOPSQUATTING] 🔴 {result['file']}: {result['hallucinated_count']} 个幻觉包", file=sys.stderr)
        sys.exit(0 if result.get("clean", True) else 2)
    else:
        print("Usage: python detect_hallucinated_packages.py --file <path> | --check-all", file=sys.stderr)


if __name__ == "__main__":
    main()
