# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/check_no_tests_unit.py | §
# [MODULE] scripts.governance.d7_code.check_no_tests_unit
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d7_code.__init__
# [CONSUMERS] .pre-commit-config.yaml hook gate-no-tests-unit
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 纯 stdlib；检测 staged .py/.md/.yaml/.yml 文件中 tests/unit/ 旧路径；含豁免清单；exit 0=pass / 1=findings / 2=error
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 永不抛异常——git 失败/I/O 异常降级为 exit 2 + stderr 提示
# [TESTS] tests/governance/test_check_no_tests_unit.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""check_no_tests_unit.py — 禁止 tests/unit/ 旧路径重引入检测（local 替代 pygrep）

裁定 #ARCH-PRECOMMIT-OFFLINE-001 Phase 3 治本：
原 .pre-commit-config.yaml 的 gate-no-tests-unit hook 使用 language: pygrep，
pygrep 是 pre-commit 内置语言，需要 pre-commit 工具运行——破坏离线可运行原则。

本脚本用纯 stdlib 等价替代，检测 staged 文件中 tests/unit/ 旧路径引用。

权威依据：AGENTS.md §7 tests/ 目录组织规范——tests/unit/ 已扁平化为 tests/
真源声明：ARCH-029 漂移种子清理——6 轮 87 文件修复后，添加自动化 guard 防止重引入

exit codes: 0=pass, 1=findings(发现 tests/unit/ 引用), 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: >
  检测 staged .py/.md/.yaml/.yml 文件中 tests/unit/ 旧路径引用。
  纯 stdlib 替代 language: pygrep（裁定 #ARCH-PRECOMMIT-OFFLINE-001）。
dimensions:
- D7
priority: P1
timeout_seconds: 10
warn_only: false
"""

import re
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS  # noqa: E402

# tests/unit/ 旧路径检测正则
_TESTS_UNIT_RE = re.compile(r"tests/unit/")

# 扫描的文件扩展名（对标原 .pre-commit-config.yaml files 字段）
_SCANNABLE_EXTS: frozenset[str] = frozenset({".py", ".md", ".yaml", ".yml"})

# 豁免清单（对标原 .pre-commit-config.yaml exclude 字段）
# 这些路径含 tests/unit/ 字符串是合法的（历史归档/规则文档说明）
_EXEMPT_PATH_PATTERNS = [
    re.compile(r"^_archive/"),
    re.compile(r"^scripts/_archive/"),
    re.compile(r"^scripts/.*/_archive/"),
    re.compile(r"^session_logs/"),
    re.compile(r"^data/"),
    re.compile(r"^reports/"),
    re.compile(r"^docs/01_policies_and_standards/rules/trae_0(28|34)_"),
    re.compile(r"^\.pre-commit-config\.yaml$"),
    re.compile(r"^AGENTS\.md$"),
]


def _get_staged_files_for_path_scan() -> list[str]:
    """获取 staged 文件列表（新增/修改/重命名后）。"""
    try:
        r = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        print(f"[ERR] git diff 失败: {type(e).__name__}: {e}", file=sys.stderr)
        return []
    if r.returncode != 0:
        print(f"[ERR] git diff rc={r.returncode}: {r.stderr}", file=sys.stderr)
        return []
    return [f for f in r.stdout.strip().split("\n") if f]


def _is_exempt(rel: str) -> bool:
    """判断文件是否在豁免清单中（POSIX 路径归一化）。"""
    normalized = rel.replace("\\", "/")
    for pattern in _EXEMPT_PATH_PATTERNS:
        if pattern.search(normalized):
            return True
    return False


def _is_scannable(rel: str) -> bool:
    """判断文件是否在扫描范围内（按扩展名过滤）。"""
    return Path(rel).suffix.lower() in _SCANNABLE_EXTS


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    files = _get_staged_files_for_path_scan()
    if not files:
        return EXIT_PASS

    findings: list[str] = []
    for rel in files:
        if _is_exempt(rel):
            continue
        if not _is_scannable(rel):
            continue
        path = Path(rel)
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            print(f"[WARN] 跳过不可读文件 {rel}: {type(e).__name__}: {e}", file=sys.stderr)
            continue
        matches = _TESTS_UNIT_RE.findall(content)
        if matches:
            findings.append(f"  {rel}: 发现 {len(matches)} 处 tests/unit/ 旧路径引用")

    if findings:
        print("[ERR] 发现 tests/unit/ 旧路径引用（ARCH-029 防漂移）:")
        for f in findings:
            print(f)
        print("")
        print("修复：tests/unit/ 已扁平化为 tests/（AGENTS.md §7），")
        print("     将 tests/unit/xxx 改为 tests/xxx，然后 git add <file> 重新提交。")
        return EXIT_FINDINGS

    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
