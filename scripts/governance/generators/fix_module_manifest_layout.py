# [BLUEPRINT] MOD-INF-005 | scripts/governance/generators/fix_module_manifest_layout.py | §
# [MODULE] scripts.governance.generators.fix_module_manifest_layout
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.generators.__init__
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
# [TTL] permanent
r"""
fix_module_manifest_layout.py — 校正治理脚本模块 docstring 与 ``__manifest__`` 的顺序

处理问题：
  - ``__manifest__`` 误入模块 docstring，与外层三引号冲突；
  - ``__manifest__`` 出现在 ``from __future__`` 之前（违反 PEP 236）。

正确顺序：闭合模块 docstring → ``from __future__ import annotations`` → ``__manifest__`` → 其余代码。
支持 ``#!/usr/bin/env`` shebang。

用法::
    python scripts/governance/generators/fix_module_manifest_layout.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
from _shared.constants import EXIT_PASS
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

__manifest__ = {
    "args": [],
    "description": "修复治理脚本模块 docstring 与 __manifest__ / from __future__ 顺序",
    "dimensions": ["D1"],
    "priority": "P2",
    "timeout_seconds": 120,
    "warn_only": False,
}

import os
import re
import sys
from pathlib import Path

_MANIFEST_START = re.compile(r"^__manifest__\s*=\s*(\"\"\"|\'\'\')\s*$")
_CODE_HEAD = re.compile(r"^(from __future__|import |from [\w.]+\s+import )")


def _consume_manifest_block(lines: list[str], idx: int) -> tuple[str, str, int] | None:
    """自 ``idx`` 起消费 ``__manifest__ = ...`` 整块，返回 delim、YAML 字符串、块之后行号。"""
    if idx >= len(lines):
        return None
    mk = _MANIFEST_START.match(lines[idx])
    if not mk:
        return None
    delim = mk.group(1)
    end = idx + 1
    while end < len(lines):
        if lines[end].strip() == delim:
            yaml_inner = "".join(lines[idx + 1 : end])
            return delim, yaml_inner, end + 1
        end += 1
    return None


def _is_external_manifest(lines: list[str], manifest_idx: int, manifest_inner_close_idx: int) -> bool:
    """True when the module docstring already ended before ``__manifest__`` (excluding YAML delim lines)."""
    j = manifest_idx - 1
    while j >= 0 and lines[j].strip() == "":
        j -= 1
    while j >= 0 and lines[j].strip() in {'"""', "'''"}:
        if j == manifest_inner_close_idx:
            j -= 1
            while j >= 0 and lines[j].strip() == "":
                j -= 1
            continue
        return True
    return False


def _find_outer_doc_close_after_yaml(lines: list[str], after_yaml_close: int) -> int | None:
    """First standalone triple-quote line at/after ``after_yaml_close`` (closes module doc)."""
    for k in range(after_yaml_close, len(lines)):
        if lines[k].strip() in {'"""', "'''"}:
            return k
    return None


def _find_code_anchor(lines: list[str], start: int) -> int | None:
    """跳过空行、注释、误重复 manifest 块，定位首条 future 或 import。"""
    i = start
    while i < len(lines):
        s = lines[i].strip()
        if s == "" or s.startswith("#"):
            i += 1
            continue
        mk = _consume_manifest_block(lines, i)
        if mk is not None:
            _d, _y, nxt = mk
            i = nxt
            continue
        if _CODE_HEAD.match(lines[i]):
            return i
        return None
    return None


def _extract_future_lines(code_lines: list[str]) -> tuple[list[str], list[str]]:
    """拆出头部连续的 ``from __future__`` 行，其余为 ``body``。"""
    fl: list[str] = []
    k = 0
    while k < len(code_lines) and code_lines[k].strip().startswith("from __future__"):
        fl.append(code_lines[k])
        k += 1
    return fl, code_lines[k:]


def fix_content(text: str) -> tuple[str, bool]:
    """Return (new_text, changed); body may start with optional shebang then ASCII-opening module docstring."""
    lines = text.splitlines(keepends=True)
    shebang = ""
    if lines and lines[0].startswith("#!"):
        shebang = lines[0]
        lines = lines[1:]
    fi = next((i for i, l in enumerate(lines) if l.strip().startswith("from __future__")), None)
    mi = next((i for i, l in enumerate(lines) if _MANIFEST_START.match(l)), None)
    if fi is not None and mi is not None and fi < mi:
        return text, False

    if not lines or not lines[0].startswith('"""'):
        return text, False

    manifest_idx = next((i for i, ln in enumerate(lines) if _MANIFEST_START.match(ln)), None)
    if manifest_idx is None:
        return text, False

    mk = _consume_manifest_block(lines, manifest_idx)
    if mk is None:
        return text, False
    delim, yaml_inner, past_manifest = mk
    inner_close_idx = past_manifest - 1

    external_manifest = _is_external_manifest(lines, manifest_idx, inner_close_idx)

    if external_manifest:
        j = manifest_idx - 1
        while j >= 0 and lines[j].strip() == "":
            j -= 1
        if j < 0 or lines[j].strip() not in {'"""', "'''"}:
            return text, False
        doc_close_idx = j
        doc_body = "".join(lines[1:doc_close_idx]).rstrip("\r\n").rstrip("\n") + "\n"
        anchor = _find_code_anchor(lines, past_manifest)
        if anchor is None:
            return text, False
    else:
        outer_close = _find_outer_doc_close_after_yaml(lines, past_manifest)
        if outer_close is None:
            return text, False
        line0_rest = lines[0][3:] if lines[0].startswith('"""') else lines[0]
        pre = [line0_rest] + lines[1:manifest_idx]
        post = lines[past_manifest:outer_close]
        doc_body = "".join(pre).rstrip("\r\n").rstrip("\n") + "\n\n" + "".join(post).rstrip("\r\n").rstrip("\n") + "\n"
        anchor = _find_code_anchor(lines, outer_close + 1)
        if anchor is None:
            anchor = len(lines)

    tail = lines[anchor:]
    future_lines, body = _extract_future_lines(tail)
    if not future_lines:
        future_lines = ["from __future__ import annotations\n"]

    manifest_block = f"__manifest__ = {delim}\n" + yaml_inner + f"{delim}\n"

    docstring_out = '"""' + doc_body + '"""\n\n'
    futures_out = "".join(future_lines).rstrip("\n") + "\n\n"
    body_out = "".join(body)

    body_assembled = docstring_out + futures_out + manifest_block + "\n" + body_out
    out = shebang + body_assembled if shebang else body_assembled

    return out, out != text


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    generators_dir = Path(__file__).resolve().parent
    gov = generators_dir.parent
    self_name = Path(__file__).name
    changed_n = 0
    for path in sorted(gov.rglob("*.py")):
        if path.name == self_name:
            continue
        if str(path.relative_to(gov)).startswith("_shared"):
            continue
        raw = path.read_text(encoding="utf-8")
        clean = raw.removeprefix("\ufeff")
        new_body, changed = fix_content(clean)
        if changed:
            atomic_write_safe(path, new_body)
            changed_n += 1
    print(f"[fix_module_manifest_layout] 已更新 {changed_n} 个文件")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
