# [BLUEPRINT] MOD-GOV_HEALTH_SMOKE | docs/03_modules/_domain_governance/blueprint.md | §ARCH-GIT-CALL-BUDGET P3.2
# [MODULE] scripts.governance.git_health_smoke
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib (subprocess, time, json, sys, os, pathlib)
# [CONSUMERS] AI session 启动流程；session_worktree_start 可选调用
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 永不抛异常——所有检查返回 dict；失败项标记 status=warn/fail 不阻断
# [MODIFY-GUARD] smoke test 独立脚本，无被引用方
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 返回 dict（不抛异常）；subprocess 超时/失败标记 fail
# [TESTS] tests/governance/test_git_health_smoke.py
# [A_module] module_id=MOD-GOV_HEALTH_SMOKE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""git_health_smoke.py — Git 健康度 smoke test（ARCH-GIT-CALL-BUDGET P3.2）

AI session 启动时运行的核心工具健康度检查。

检测项：1.git 版本(2.48.x 崩溃版本→warn，2.50.1+推荐) 2.fscache/fsmonitor(仓库级 MUST false)
3.git status 计时(>30s fail/>10s warn) 4.git alias(5 个危险命令拦截活跃)

版本语义（2026-07-19 架构裁定，第一性原理 + Web 调研）：
- 2.48.x：warn——MSYS2/Cygwin FAST_CWD 指针计算失效（msys2-runtime#86），
  fscache/fsmonitor 是 fork+pipe-back-to-parent 代码路径上的崩溃放大器。
- 2.49.0+：pass（FAST_CWD 已修复）——但 2.49.x/2.50.0 存在 SSH hang regression。
- 2.50.1+：pass（推荐版本）——FAST_CWD 修复 + SSH hang 修复。
"""

from __future__ import annotations

__manifest__ = """
args: []
description: git_health_smoke.py — Git 健康度 smoke test（ARCH-GIT-CALL-BUDGET P3.2）
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import json
import os
import re
import subprocess
import sys
import time
from typing import Optional

_STATUS_PRIORITY = {"pass": 0, "warn": 1, "fail": 2}
# git 2.48.x：MSYS2/Cygwin FAST_CWD 指针计算失效（msys2-runtime#86），崩溃放大器
# 是 fscache/fsmonitor 的 fork+pipe-back-to-parent 代码路径。铁律3 已锁定两者为 false。
_CRASH_VERSION_PREFIX = "2.48."
# 2.49.0+：FAST_CWD 已修复（msys2-runtime#86），但仍存在 SSH hang regression
_FAST_CWD_FIXED_PREFIX = "2.49."
# 2.50.1+：FAST_CWD 修复 + SSH hang regression 修复（推荐版本）
_RECOMMENDED_VERSION = (2, 50, 1)
_STATUS_WARN_SECONDS = 10.0
_STATUS_FAIL_SECONDS = 30.0


def _parse_git_version(version_str: str) -> tuple[int, int, int] | None:
    """从 'git version 2.50.1.windows.1' 解析出 (major, minor, patch)。

    fail-open：解析失败返回 None（调用方降级为字符串前缀匹配）。
    """
    # 提取第一个 x.y.z 数字序列
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", version_str)
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def run_git(args, cwd, timeout=60.0):
    """_run_git implementation."""
    try:
        r = subprocess.run(  # noqa: bare-subprocess  冒烟诊断脚本直接调 git（人工一次性触发，窗口闪现无影响）
            ["git"] + args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout
        )
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", f"timeout after {timeout}s"
    except Exception as e:
        return -2, "", str(e)


def _run_git(args, cwd, timeout=60.0):
    """向后兼容 thin wrapper（Stage 4 公共化）。"""
    return run_git(args, cwd, timeout)


def _check_git_version(repo_root):
    """_check_git_version implementation."""
    rc, stdout, stderr = _run_git(["--version"], repo_root, timeout=10)
    if rc != 0:
        return {"check": "git_version", "status": "fail", "detail": f"git --version failed: {stderr}"}
    version = stdout.replace("git version", "").strip()
    parsed = _parse_git_version(version)

    # 1. 2.48.x — FAST_CWD 崩溃版本（warn）
    if version.startswith(_CRASH_VERSION_PREFIX):
        detail = (
            f"git version {version} — 已知崩溃版本（MSYS2/Cygwin FAST_CWD 指针计算失效，"
            f"msys2-runtime#86）。铁律3 已锁定 core.fscache=false + core.fsmonitor=false "
            f"切断崩溃放大路径。建议升级到 git {_RECOMMENDED_VERSION[0]}."
            f"{_RECOMMENDED_VERSION[1]}.{_RECOMMENDED_VERSION[2]}+（FAST_CWD 修复 + "
            f"SSH hang regression 修复）。"
        )
        return {
            "check": "git_version",
            "status": "warn",
            "detail": detail,
            "version": version,
            "recommended": ".".join(map(str, _RECOMMENDED_VERSION)),
        }

    # 2. 2.49.0+ 但低于 2.50.1 — FAST_CWD 已修复但存在 SSH hang regression（pass + 提示）
    if parsed is not None and parsed >= (2, 49, 0) and parsed < _RECOMMENDED_VERSION:
        detail = (
            f"git version {version} — FAST_CWD 已修复（2.49.0+，msys2-runtime#86）。"
            f"但仍存在 SSH hang regression（2.49.x/2.50.0），建议升级到 "
            f"git {_RECOMMENDED_VERSION[0]}.{_RECOMMENDED_VERSION[1]}."
            f"{_RECOMMENDED_VERSION[2]}+（同时修复 SSH hang）。"
        )
        return {
            "check": "git_version",
            "status": "pass",
            "detail": detail,
            "version": version,
            "recommended": ".".join(map(str, _RECOMMENDED_VERSION)),
        }

    # 3. 2.50.1+ — 推荐版本（pass）
    if parsed is not None and parsed >= _RECOMMENDED_VERSION:
        detail = f"git version {version} — 推荐版本（FAST_CWD 修复 + SSH hang regression 修复）。"
        return {
            "check": "git_version",
            "status": "pass",
            "detail": detail,
            "version": version,
            "recommended": ".".join(map(str, _RECOMMENDED_VERSION)),
        }

    # 4. 低于 2.48 或解析失败 — fail-open pass + 提示
    detail = (
        f"git version {version} — 未识别版本（低于 2.48 或解析失败）。"
        f"建议升级到 git {_RECOMMENDED_VERSION[0]}.{_RECOMMENDED_VERSION[1]}."
        f"{_RECOMMENDED_VERSION[2]}+ 以确保 FAST_CWD 与 SSH hang 均已修复。"
    )
    return {
        "check": "git_version",
        "status": "pass",
        "detail": detail,
        "version": version,
        "recommended": ".".join(map(str, _RECOMMENDED_VERSION)),
    }


def _check_fscache_fsmonitor(repo_root):
    """_check_fscache_fsmonitor implementation."""
    issues = []
    rc_f, val_f, _ = _run_git(["config", "--local", "core.fscache"], repo_root)
    rc_m, val_m, _ = _run_git(["config", "--local", "core.fsmonitor"], repo_root)
    if rc_f == 0 and val_f.lower() == "true":
        issues.append("core.fscache=true(仓库级)—违反 GIT-BUDGET-INV-004")
    if rc_m == 0 and val_m.lower() == "true":
        issues.append("core.fsmonitor=true(仓库级)—违反 GIT-BUDGET-INV-004")
    if issues:
        return {"check": "fscache_fsmonitor", "status": "fail", "detail": "; ".join(issues)}
    return {
        "check": "fscache_fsmonitor",
        "status": "pass",
        "detail": f"core.fscache={val_f or '(unset)'} / core.fsmonitor={val_m or '(unset)'}(仓库级)",
    }


def _check_status_timing(repo_root):
    """_check_status_timing implementation."""
    start = time.monotonic()
    rc, stdout, stderr = _run_git(["status", "--short"], repo_root, timeout=120)
    elapsed = time.monotonic() - start
    if rc != 0:
        return {
            "check": "status_timing",
            "status": "fail",
            "detail": f"git status failed({rc}): {stderr}",
            "elapsed_s": round(elapsed, 2),
        }
    if elapsed > _STATUS_FAIL_SECONDS:
        status = "fail"
        detail = f"git status 耗时 {elapsed:.1f}s > {_STATUS_FAIL_SECONDS}s — index 缓存可能损坏"
    elif elapsed > _STATUS_WARN_SECONDS:
        status = "warn"
        detail = f"git status 耗时 {elapsed:.1f}s > {_STATUS_WARN_SECONDS}s — index 缓存需刷新"
    else:
        status = "pass"
        detail = f"git status 耗时 {elapsed:.2f}s(正常)"
    return {"check": "status_timing", "status": status, "detail": detail, "elapsed_s": round(elapsed, 2)}


def _check_git_aliases(repo_root):
    """_check_git_aliases implementation."""
    expected = {"reset", "checkout", "stash", "revert", "restore"}
    rc, stdout, stderr = _run_git(["config", "--local", "--get-regexp", "^alias\\."], repo_root)
    if rc != 0 and rc != 1:
        return {"check": "git_aliases", "status": "warn", "detail": f"git config failed: {stderr}"}
    found = set()
    for line in stdout.split("\n"):
        if line.startswith("alias."):
            found.add(line.split(".")[1].split(" ")[0])
    missing = expected - found
    if missing:
        return {"check": "git_aliases", "status": "warn", "detail": f"缺失 alias: {missing}"}
    return {"check": "git_aliases", "status": "pass", "detail": "5 个危险命令 alias 均已注册"}


def run_git_health_smoke(repo_root=None):
    """run_git_health_smoke implementation."""
    root = str(repo_root) if repo_root else os.getcwd()
    if not os.path.isdir(os.path.join(root, ".git")) and not os.path.isfile(os.path.join(root, ".git")):
        return {"status": "fail", "checks": [], "timestamp": time.time(), "summary": f"不是 git 仓库: {root}"}
    checks = [
        _check_git_version(root),
        _check_fscache_fsmonitor(root),
        _check_status_timing(root),
        _check_git_aliases(root),
    ]
    overall = "pass"
    for c in checks:
        if _STATUS_PRIORITY.get(c["status"], 0) > _STATUS_PRIORITY.get(overall, 0):
            overall = c["status"]
    summary = ", ".join(f"{c['check']}={c['status']}" for c in checks)
    return {
        "status": overall,
        "checks": checks,
        "timestamp": time.time(),
        "summary": f"git_health_smoke: {overall} ({summary})",
    }


def main():
    """Entry point: parse args, run logic, return exit code."""
    repo_root = sys.argv[1] if len(sys.argv) > 1 else None
    result = run_git_health_smoke(repo_root)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] != "fail" else 1


if __name__ == "__main__":
    sys.exit(main())
