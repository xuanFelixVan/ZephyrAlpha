# [BLUEPRINT] SH-GOV-004 | docs/03_modules/_domain_governance/blueprint.md | §ARCH-TOOL-HEALTH-V1
# [MODULE] scripts.governance.session_startup_health_check
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib (importlib, subprocess, json, sys, os, time, pathlib); 无 zephyr 内部依赖（smoke test 必须独立可运行）
# [CONSUMERS] AI session 启动流程（AGENTS.md 规则）；session_worktree_start 可选调用
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 永不抛异常——所有检查返回 dict 结构；失败项标记 status=warn/fail；AI 见 fail 必须 escalate 不可静默 workaround
# [MODIFY-GUARD] smoke test 是独立脚本，无被引用方
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 返回 dict（不抛异常）；subprocess 超时/失败标记 fail；总结果 status = max(各检查项 status)
# [TESTS] tests/governance/test_session_startup_health_check.py
# [TTL] permanent
"""session_startup_health_check.py — AI session 启动健康度自检（ARCH-TOOL-HEALTH-V1 Phase 6）

AI session 启动时运行的核心工具健康度检查。对应裁定 #ARCH-TOOL-HEALTH-V1 Phase 6
+ 项目记忆"AI session 启动 smoke test"。

病根（第一性原理）
------------------
commit deb695006f 误删 get_depgraph_pg_connection import 导致 NameError 静默累积，
5 层防线（pre-commit hook、GitCommitGateway、测试等）全失效。

根因：无"启动健康度自检"机制——AI session 启动时不检测核心工具是否可用。
AI 遇到核心工具报错默认 silently workaround 是 100% AI 开发场景的最大风险。

治本
----
本脚本在 AI session 启动时检测核心治理工具（apply_depgraph 等 L1/L2/L3 铁律
执行工具）的 import + CLI + 关键符号可用性。失败时返回 fail 状态，
AI 必须 escalate（上报）而非静默绕过。

检测项
------
1. **核心工具 import**：apply_depgraph / apply_decisiongraph / apply_dataflowgraph /
   sync_yaml_to_depgraph 能否被 importlib 加载（检测 Phase 1 类 NameError）
2. **关键符号存在**：get_depgraph_pg_connection / EXIT_* 常量 / 核心函数
3. **CLI 可运行**：--list-ops / --list-readonly-tables 返回 rc=0
4. **Gateway 模块 import**：GitCommitGateway / session_worktree / reconciliation_registry

设计原则
--------
1. **独立可运行**：不依赖 zephyr 包（避免 import 链故障导致 smoke test 本身不可用）
2. **非阻断**：返回 dict 结构，调用方决定如何处理（escalate / warn / ignore）
3. **CLI + import 双模式**：可 `python session_startup_health_check.py` 直接运行，
   也可 import 调用
4. **JSON 输出**：CLI 模式输出 JSON，便于 AI 解析
5. **快速（<30s）**：subprocess 超时 30s/项，总计 <60s

Usage::

    # CLI 模式（session 启动时）
    python scripts/governance/session_startup_health_check.py

    # import 模式
    from scripts.governance.session_startup_health_check import run_startup_health_check
    result = run_startup_health_check(repo_root="/path/to/repo")
    if result["status"] == "fail":
        # MUST escalate, don't silently workaround
        ...

Exit codes:
    0 = all pass (status=pass)
    1 = at least one fail (status=fail)
    2 = at least one warn but no fail (status=warn)
"""
from __future__ import annotations

__manifest__ = """
args: []
description: session_startup_health_check.py — AI session 启动健康度自检（ARCH-TOOL-HEALTH-V1
  Phase 6）
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import importlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Exit codes (convention: 0=pass, 1=findings, 2=error)
EXIT_PASS = 0
EXIT_FINDINGS = 1
EXIT_ERROR = 2

# 检查项状态优先级：fail > warn > pass
_STATUS_PRIORITY = {"pass": 0, "warn": 1, "fail": 2}

# 核心工具定义：相对路径 + CLI 只读命令 + 关键符号（import 后检测）
_CORE_TOOLS = [
    {
        "name": "apply_depgraph",
        "rel_path": "scripts/governance/apply_depgraph.py",
        "cli_args": ["--list-ops"],
        "cli_output_contains": "cmd_batch",
        "required_symbols": ["get_depgraph_pg_connection", "EXIT_PASS", "EXIT_ERROR",
                             "add_design_node", "add_design_edge", "transition_build_status"],
    },
    {
        "name": "apply_decisiongraph",
        "rel_path": "scripts/governance/apply_decisiongraph.py",
        "cli_args": ["--list-ops"],
        "cli_output_contains": None,  # 宽松检测：只看 rc=0
        "required_symbols": [],  # 决策图工具符号各异，只检测 import 成功
    },
    {
        "name": "apply_dataflowgraph",
        "rel_path": "scripts/governance/apply_dataflowgraph.py",
        "cli_args": ["--list-ops"],
        "cli_output_contains": None,
        "required_symbols": [],
    },
    {
        "name": "sync_yaml_to_depgraph",
        "rel_path": "scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py",
        "cli_args": ["--list-readonly-tables"],
        "cli_output_contains": None,
        "required_symbols": [],
    },
]

# Gateway 模块定义：Python 模块路径 + 必须存在的属性
_GATEWAY_MODULES = [
    {
        "module": "zephyr.gov_enforcement.rule_bridge.git_commit_gateway",
        "required_attrs": ["GitCommitGateway"],
    },
    {
        "module": "zephyr.gov_enforcement.rule_bridge.session_worktree",
        "required_attrs": ["session_worktree_start", "session_worktree_commit",
                           "session_worktree_merge", "session_worktree_abort",
                           # P2-2 (2026-07-19): claim_files_for_edit 新增
                           "claim_files_for_edit"],
    },
    {
        "module": "zephyr.governance.audit.reconciliation_registry",
        "required_attrs": ["ReconcilerSpec", "ReconcileResult", "ReconciliationRegistry"],
    },
    # P2-4 (2026-07-19): 新增 P2-1/P2-3 工具覆盖
    {
        "module": "zephyr.gov_enforcement.rule_bridge.emergency_commit",
        "required_attrs": ["emergency_commit", "EmergencyCommitResult"],
    },
    {
        "module": "zephyr.governance.audit.reconcile_runner",
        "required_attrs": ["launch_reconcile_async", "query_reconcile_status",
                           "write_status_file", "read_status_file"],
    },
    {
        "module": "zephyr.governance.audit.reconcile_worker",
        "required_attrs": ["main", "_load_payload"],
    },
]
GATEWAY_MODULES = _GATEWAY_MODULES  # public alias (R5 reverse hierarchy)


def _load_script_module(script_path: Path, module_name: str):
    """用 importlib 动态加载脚本文件（不依赖 __init__.py）。

    返回 (module, error)。成功时 error=None，失败时 module=None + error=异常信息。
    """
    try:
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        if spec is None or spec.loader is None:
            return None, f"spec_from_file_location returned None for {script_path}"
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod, None
    except Exception as e:  # noqa: BLE001 — smoke test 必须捕获所有异常
        return None, f"{type(e).__name__}: {e}"


def check_core_tool_import(tool: dict, repo_root: Path) -> dict:
    """检查核心工具能否被 importlib 加载（检测 Phase 1 类 NameError）。"""
    script_path = repo_root / tool["rel_path"]
    if not script_path.exists():
        return {
            "check": f"{tool['name']}_import",
            "status": "fail",
            "detail": f"文件不存在: {tool['rel_path']}",
        }
    mod, err = _load_script_module(script_path, f"_smoke_{tool['name']}")
    if err:
        return {
            "check": f"{tool['name']}_import",
            "status": "fail",
            "detail": f"import 失败（疑似 Phase 1 类 NameError/import 缺失）: {err}",
        }
    # 检测关键符号
    missing = [s for s in tool["required_symbols"] if not hasattr(mod, s)]
    if missing:
        return {
            "check": f"{tool['name']}_import",
            "status": "fail",
            "detail": f"import 成功但缺少关键符号: {missing}",
        }
    return {
        "check": f"{tool['name']}_import",
        "status": "pass",
        "detail": f"import 成功，{len(tool['required_symbols'])} 个关键符号均存在",
    }


def _check_core_tool_import(tool: dict, repo_root: Path) -> dict:
    """向后兼容包装：委托给 check_core_tool_import。"""
    return check_core_tool_import(tool, repo_root)


def check_core_tool_cli(tool: dict, repo_root: Path) -> dict:
    """检查核心工具 CLI 能否运行（--list-ops / --list-readonly-tables 返回 rc=0）。"""
    script_path = repo_root / tool["rel_path"]
    if not script_path.exists():
        return {
            "check": f"{tool['name']}_cli",
            "status": "fail",
            "detail": f"文件不存在: {tool['rel_path']}",
        }
    try:
        env = os.environ.copy()
        # 核心 tools 需要 PYTHONPATH=src 和 scripts/governance（_shared 导入）
        src_path = str(repo_root / "src")
        gov_path = str(repo_root / "scripts" / "governance")
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{src_path};{gov_path};{existing}" if existing else f"{src_path};{gov_path}"
        result = subprocess.run(
            [sys.executable, str(script_path)] + tool["cli_args"],
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            timeout=30, cwd=str(repo_root), env=env,
        )
    except subprocess.TimeoutExpired:
        return {
            "check": f"{tool['name']}_cli",
            "status": "fail",
            "detail": f"CLI 超时（>{30}s）: {' '.join(tool['cli_args'])}",
        }
    except Exception as e:  # noqa: BLE001 — smoke test 必须捕获所有异常
        return {
            "check": f"{tool['name']}_cli",
            "status": "fail",
            "detail": f"CLI 执行异常: {type(e).__name__}: {e}",
        }
    if result.returncode != 0:
        return {
            "check": f"{tool['name']}_cli",
            "status": "fail",
            "detail": f"CLI rc={result.returncode}: {result.stderr[:200]}",
        }
    # 可选：检测输出包含特定字符串
    expected = tool.get("cli_output_contains")
    if expected and expected not in result.stdout:
        return {
            "check": f"{tool['name']}_cli",
            "status": "warn",
            "detail": f"CLI rc=0 但输出缺少 '{expected}'（输出格式可能已变更）",
        }
    return {
        "check": f"{tool['name']}_cli",
        "status": "pass",
        "detail": f"CLI rc=0 ({' '.join(tool['cli_args'])})",
    }


def _check_core_tool_cli(tool: dict, repo_root: Path) -> dict:
    """向后兼容包装：委托给 check_core_tool_cli。"""
    return check_core_tool_cli(tool, repo_root)


def check_gateway_module(mod_spec: dict, repo_root: Path) -> dict:
    """检查 gateway 模块能否 import + 关键属性存在。"""
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))  # noqa: import-integrity  src_path 依赖函数参数 repo_root，静态不可解析
    try:
        mod = importlib.import_module(mod_spec["module"])
    except Exception as e:  # noqa: BLE001 — smoke test 必须捕获所有异常
        return {
            "check": f"gateway_{mod_spec['module'].split('.')[-1]}",
            "status": "fail",
            "detail": f"import 失败: {type(e).__name__}: {e}",
        }
    missing = [a for a in mod_spec["required_attrs"] if not hasattr(mod, a)]
    if missing:
        return {
            "check": f"gateway_{mod_spec['module'].split('.')[-1]}",
            "status": "fail",
            "detail": f"import 成功但缺少关键属性: {missing}",
        }
    return {
        "check": f"gateway_{mod_spec['module'].split('.')[-1]}",
        "status": "pass",
        "detail": f"import 成功，{len(mod_spec['required_attrs'])} 个关键属性均存在",
    }


def _check_gateway_module(mod_spec: dict, repo_root: Path) -> dict:
    """向后兼容包装：委托给 check_gateway_module。"""
    return check_gateway_module(mod_spec, repo_root)


def check_git_health_smoke(repo_root: Path) -> dict:
    """可选：委托 git_health_smoke.py 做 git 层面检查。

    若 git_health_smoke.py 不可用则跳过（warn）——不阻断核心工具检查。
    """
    smoke_script = repo_root / "scripts" / "governance" / "git_health_smoke.py"
    if not smoke_script.exists():
        return {
            "check": "git_health_smoke",
            "status": "warn",
            "detail": "git_health_smoke.py 不存在，跳过 git 层面检查",
        }
    try:
        result = subprocess.run(
            [sys.executable, str(smoke_script), str(repo_root)],
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            timeout=60, cwd=str(repo_root),
        )
    except subprocess.TimeoutExpired:
        return {"check": "git_health_smoke", "status": "warn", "detail": "git_health_smoke 超时（>60s）"}
    except Exception as e:  # noqa: BLE001
        return {"check": "git_health_smoke", "status": "warn", "detail": f"git_health_smoke 异常: {e}"}
    if result.returncode != 0:
        return {
            "check": "git_health_smoke",
            "status": "warn",
            "detail": "git_health_smoke 返回 fail（见 git_health_smoke.py 输出）",
        }
    return {
        "check": "git_health_smoke",
        "status": "pass",
        "detail": "git_health_smoke 全通过（git version/fscache/status/aliases）",
    }


def _check_git_health_smoke(repo_root: Path) -> dict:
    """向后兼容包装：委托给 check_git_health_smoke。"""
    return check_git_health_smoke(repo_root)


def run_startup_health_check(
    repo_root: str | Path | None = None,
    include_git: bool = True,
    session_id: str = "",
) -> dict:
    """运行 AI session 启动健康度自检。

    Args:
        repo_root: 仓库根目录。None = 当前工作目录。
        include_git: 是否包含 git_health_smoke 检查（默认 True）。
        session_id: 可选——AI session ID，用于失败时持久化到 reconcile_execution_log
            （action='critical_warn'，gate_id='STARTUP-HEALTH-CHECK'）。AI 可后续查询
            历史 session 的健康度失败记录。P2-4 (2026-07-19) 新增。

    Returns:
        dict 结构：
        {
            "status": "pass" | "warn" | "fail",  # 总状态 = max(各检查项)
            "checks": [...],                      # 各检查项结果
            "timestamp": float,                   # Unix 时间戳
            "summary": str,                       # 人类可读摘要
            "escalation_required": bool,          # True = AI 必须 escalate
        }
    """
    root = Path(repo_root) if repo_root else Path.cwd()
    if not (root / ".git").exists() and not (root / ".git").is_file():
        return {
            "status": "fail",
            "checks": [],
            "timestamp": time.time(),
            "summary": f"不是 git 仓库: {root}",
            "escalation_required": True,
        }

    # 确保 src/ 在 sys.path 上——核心工具（apply_depgraph 等）import zephyr.*，
    # 独立运行时（非 pytest）需要此设置才能正确检测 import 失败（Phase 1 类 NameError）
    src_path = root / "src"
    if src_path.is_dir() and str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))  # noqa: import-integrity  src_path 依赖函数参数 repo_root，静态不可解析

    checks: list[dict] = []

    # 1. 核心工具 import 检查
    for tool in _CORE_TOOLS:
        checks.append(check_core_tool_import(tool, root))

    # 2. 核心工具 CLI 检查
    for tool in _CORE_TOOLS:
        checks.append(check_core_tool_cli(tool, root))

    # 3. Gateway 模块 import 检查
    for mod_spec in GATEWAY_MODULES:
        checks.append(check_gateway_module(mod_spec, root))

    # 4. 可选：git 层面检查
    if include_git:
        checks.append(check_git_health_smoke(root))

    # 总状态 = 最高优先级的检查项状态
    overall = "pass"
    for c in checks:
        if _STATUS_PRIORITY.get(c["status"], 0) > _STATUS_PRIORITY.get(overall, 0):
            overall = c["status"]

    summary_parts = [f"{c['check']}={c['status']}" for c in checks]
    # 失败项摘要（前 5 个）
    failed = [c for c in checks if c["status"] == "fail"]
    escalation = overall == "fail"
    fail_summary = ""
    if failed:
        fail_details = "; ".join(f"{c['check']}: {c['detail'][:80]}" for c in failed[:5])
        fail_summary = f" | FAIL项: {fail_details}"

    # P2-4 (2026-07-19): 失败持久化到 reconcile_execution_log
    # 病根：原实现只返回 dict，AI 可静默忽略失败。治本：session_id 提供时，
    # 调用 log_gate_failure 持久化（action='critical_warn'），下次 commit/merge
    # 时 _print_critical_warn_banner 强制 AI 看到历史失败。
    # 设计原则：脚本无 zephyr 内部依赖——try/except import 失败时降级为 logger.warning。
    persisted_to_db = False
    if overall == "fail" and session_id:
        try:
            # 确保 src/ 在 sys.path（_check_gateway_module 已设过，但保险）
            src_path = root / "src"
            if src_path.is_dir() and str(src_path) not in sys.path:
                sys.path.insert(0, str(src_path))  # noqa: import-integrity  src_path 依赖函数参数 repo_root，静态不可解析
            from zephyr.governance.audit.reconciliation_registry import log_gate_failure
            detail = fail_summary or f"session_startup_health_check failed: {len(failed)}/{len(checks)} 项 fail"
            log_gate_failure(
                project_root=root,
                gate_id="STARTUP-HEALTH-CHECK",
                detail=detail,
                session_id=session_id,
                trigger_source="session_startup",
            )
            persisted_to_db = True
        except Exception as persist_err:  # noqa: BLE001 — 持久化失败不阻断主流程
            # 降级：仅 stderr 警告，主结果仍返回（AI 见 escalation_required 仍需 escalate）
            print(
                f"[session_startup_health_check] WARN: 持久化失败到 DB 失败: {persist_err}",
                file=sys.stderr,
            )

    return {
        "status": overall,
        "checks": checks,
        "timestamp": time.time(),
        "summary": f"session_startup_health_check: {overall} ({len(checks)} 项){fail_summary}",
        "escalation_required": escalation,
        "failed_count": len(failed),
        "total_count": len(checks),
        "session_id": session_id,
        "persisted_to_db": persisted_to_db,
    }


def main() -> int:
    """CLI 入口：运行健康度自检并输出 JSON。

    Exit codes:
        0 = all pass
        1 = at least one fail (AI MUST escalate)
        2 = at least one warn but no fail

    CLI args:
        [repo_root]              仓库根目录（可选，默认 cwd）
        --no-git                 跳过 git_health_smoke 检查
        --session-id <SID>       AI session ID（失败时持久化到 DB，P2-4）
    """
    args = sys.argv[1:]
    repo_root = None
    include_git = True
    session_id = ""
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--no-git":
            include_git = False
        elif a == "--session-id":
            if i + 1 < len(args):
                session_id = args[i + 1]
                i += 1
        elif not a.startswith("--"):
            repo_root = a
        i += 1
    result = run_startup_health_check(
        repo_root, include_git=include_git, session_id=session_id,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["status"] == "fail":
        # 关键：AI 见此输出 MUST escalate，不可静默 workaround
        print(
            "\n!! ESCALATION REQUIRED !!\n"
            "核心工具健康度自检失败。AI 不可静默 workaround，必须：\n"
            "1. 上报失败项给用户\n"
            "2. 排查根因（疑似 import 缺失/NameError/CLI 配置错误）\n"
            "3. 修复后再继续施工\n"
            "见裁定 #ARCH-TOOL-HEALTH-V1 Phase 6",
            file=sys.stderr,
        )
        return EXIT_FINDINGS
    if result["status"] == "warn":
        return EXIT_ERROR
    return EXIT_PASS
if __name__ == "__main__":
    sys.exit(main())
