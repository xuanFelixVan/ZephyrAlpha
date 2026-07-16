# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/run_script_smoke_test.py | §
# [MODULE] scripts.governance.d1_structure.run_script_smoke_test
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d1_structure.__init__
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
"""
run_script_smoke_test.py — 治理脚本冒烟测试运行器
"""

from __future__ import annotations

__manifest__ = {
    "args": [],
    "description": "治理脚本冒烟测试 [SCRIPT-QUALITY-001 D-H-01 - subprocess + --warn-only 全量运行]",
    "dimensions": ["D1"],
    "priority": "P1",
    "timeout_seconds": 300,
    "warn_only": False,
}

# 对标: SCRIPT-QUALITY-001 D-H-01 (冒烟测试: --warn-only 退出干净)
#       AGENTS.md §6.5 (脚本入库后必须验证)
# 检测内容:
# - 从 script_manifest.yaml 加载全部注册脚本
# - 用 subprocess + --warn-only 逐个运行
# - 报告 exit code 分布 (0=通过 / 1=有发现 / 2=异常)
# - 输出失败和异常脚本清单
# exit codes: 0=pass, 1=findings, 2=error

import py_compile
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
import yaml
from _shared.constants import EXIT_PASS, MANIFEST_PATH, REPO_ROOT, SCRIPTS_DIR
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
_SELF_NAME = "d1_structure/run_script_smoke_test.py"
import argparse


def load_manifest() -> list[dict]:
    """读取 script_manifest.yaml 脚本列表。"""
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
    return manifest.get("scripts", [])


def run_script(script_name: str, timeout: int = 60) -> tuple[int, str, str]:
    """以 --warn-only 子进程执行注册脚本。"""
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        return (-1, "", f"脚本不存在: {script_path}")
    try:
        result = subprocess.run(
            [sys.executable, str(script_path), "--warn-only"],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(REPO_ROOT),
            encoding="utf-8",
            errors="replace",
        )
        return (result.returncode, result.stdout.strip(), result.stderr.strip())
    except subprocess.TimeoutExpired:
        return (-1, "", f"超时（>{timeout}s）")
    except OSError as e:
        return (-2, "", f"OS 错误: {e}")


def check_script_syntax(script_name: str) -> tuple[bool, str]:
    """py_compile 语法检查——治理脚本防损坏的第一道防线"""
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        return (False, f"脚本不存在: {script_path}")
    try:
        py_compile.compile(str(script_path), doraise=True)
        return (True, "")
    except py_compile.PyCompileError as e:
        return (False, str(e))


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="治理脚本冒烟测试 — 用 --warn-only 模式运行全部注册脚本")
    parser.add_argument("--warn-only", action="store_true", help="警告模式：失败不阻塞（exit 0）")
    parser.add_argument("--timeout", type=int, default=60, help="单个脚本超时秒数（默认 60）")
    args = parser.parse_args()
    entries = load_manifest()
    total = len(entries)
    passed = 0
    findings = []
    errors = []
    compile_errors = []
    for entry in entries:
        name = entry["name"]
        if name == _SELF_NAME:
            continue
        ok_syntax, syntax_err = check_script_syntax(name)
        if not ok_syntax:
            compile_errors.append((name, syntax_err[:200]))
            continue
        rc, stdout, stderr = run_script(name, timeout=args.timeout)
        if rc == 0:
            passed += 1
        elif rc == 1:
            findings.append((name, stdout[:120] if stdout else ""))
        else:
            errors.append((name, rc, (stderr or stdout)[:150] if stderr or stdout else "无输出"))
    print(f"\n[SMOKE-TEST] {total} 个注册脚本冒烟测试结果：\n", file=sys.stderr)
    print(f"  ✅ 通过 (exit 0): {passed}/{total}", file=sys.stderr)
    print(f"  ⚠ 有发现 (exit 1): {len(findings)}/{total}", file=sys.stderr)
    print(f"  ❌ 异常 (exit 2/-1): {len(errors)}/{total}", file=sys.stderr)
    print(f"  💀 编译失败 (py_compile): {len(compile_errors)}/{total}", file=sys.stderr)
    if compile_errors:
        print(f"\n--- 编译失败清单 ({len(compile_errors)}) ---", file=sys.stderr)
        for name, err in compile_errors:
            print(f"  [{name}]: {err[:150]}", file=sys.stderr)
    if findings:
        print(f"\n--- 发现清单 ({len(findings)}) ---", file=sys.stderr)
        for name, out in findings:
            print(f"  [{name}]: {out[:150]}", file=sys.stderr)
    if errors:
        print(f"\n--- 异常清单 ({len(errors)}) ---", file=sys.stderr)
        for name, rc, msg in errors:
            print(f"  [{name}] exit={rc}: {msg[:150]}", file=sys.stderr)
    print(file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings or errors or compile_errors else 0)


if __name__ == "__main__":
    main()
