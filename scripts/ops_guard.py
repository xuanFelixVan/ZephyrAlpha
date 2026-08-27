#!/usr/bin/env python3
# [BLUEPRINT] MOD-GOV-042 | scripts/ops_guard.py | §
# [MODULE] scripts.ops_guard
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] (无外部依赖——纯 stdlib)
# [CONSUMERS] AI session 执行文件删除前调用；红队测试直接调用分析引擎；session_worktree abort 流程接入审计
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 分析+审计为纯函数无副作用；exec 模式先审计后执行；BLOCKED 时 exit 1 不执行
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=allowed; exit 1=blocked; exit 2=internal error
# [TESTS] tests/governance/test_ops_guard_red_team.py
# [A_script] module_id=MOD-GOV-042 | layer=script | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Ops Guard — 全原语删除拦截（S1，2026-08-14 wipe 事故治本）

根因：git_guard 只拦 git 子命令——Remove-Item / del / os.remove / shutil.rmtree
等删除原语零拦截（R1 能力层失守）。2026-08-14 三 worktree tracked 文件被物理
清空，唯一吻合的执行者是临时构造的"worktree 清理"命令（PowerShell/Python
物理删除）。

防护策略：
  1. 命令分析引擎 analyze_delete_command()——识别 PowerShell/CMD/Python/git
     四类删除原语，判定目标路径是否命中保护区
  2. 保护区：.worktrees/*、仓库根、src/、docs/、tests/
  3. 白名单：.runtime/tmp、__pycache__、显式单文件（非递归）
  4. 强制审计：所有删除命令先落审计 jsonl（命令行+cwd+session_id+目标清单
     hash）后执行

使用方式：
    # CLI 检查（不执行）
    python scripts/ops_guard.py check "Remove-Item -Recurse -Force .worktrees\\AI-X"

    # CLI 执行（先审计后执行）
    python scripts/ops_guard.py exec "Remove-Item .runtime\\tmp\\cache"

    # Python API（替换裸 shutil.rmtree/os.remove）
    from scripts.ops_guard import guard_rmtree, guard_remove
    guard_rmtree(".runtime/tmp/cache")   # 白名单内放行+审计
    guard_rmtree(".worktrees/AI-X")      # BLOCKED→raise DeleteBlockedError

退出码：
    0 = 放行（已审计）
    1 = 阻断（命中保护区）
    2 = 内部错误
"""

from __future__ import annotations

import contextlib
import contextvars
import hashlib
import json
import os
import re
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

__all__ = [
    "DeleteBlockedError",
    "DeleteVerdict",
    "analyze_delete_command",
    "audit_delete",
    "guard_move",
    "guard_remove",
    "guard_rmtree",
    "guard_recycle",
    "prune_recycle_bin",
    "set_reconciler_context",
    "reset_reconciler_context",
    "get_reconciler_context",
    "install_inprocess_enforcement",
    "install_inprocess_enforcement_audit_only",
    "inprocess_enforcement_installed",
    "main",
]

# ============================================================================
# 常量
# ============================================================================

# 保护区前缀（相对仓库根，正斜杠分隔）
PROTECTED_PREFIXES: tuple[str, ...] = (
    ".worktrees",
    "src",
    "docs",
    "tests",
    # #ARCH-264 O4②（2026-08-26）：drift watchdog 告警快照=事故取证存证，
    # 2026-08-25/26 两起带外裸删（drift_* 选择性清除、零审计）实证需保护区。
    # 授权通道唯一化：watchdog retention 清扫经 safe_rmtree 授权通道（留痕），
    # 人工处置走 ZEPHYR_FORCE_DELETE=1。
    ".runtime/quarantine",
)

# 白名单前缀（这些路径下的删除放行）
ALLOWED_PREFIXES: tuple[str, ...] = (
    ".runtime/tmp",
    ".runtime/cache",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".aidrafts",
    # gitignore 的运行时缓存目录（src/zephyr/autonomy_core/skills/_skill_cache/）——
    # 虽物理位于 src/ 保护区内，本质是运行时产物（与 __pycache__ 同型），
    # skill_cache_provider 正常缓存清理不应被拦（批5a，观测期 350 条 would_block
    # 误报族②：测试/运行时删缓存 json 撞保护区）。
    "_skill_cache",
)

# 会话 ID 环境变量（与 git_guard.py 对齐）
SESSION_ID_ENV = "ZEPHYR_SESSION_ID"

# 授权环境变量（与 git_guard.py 对齐——gateway/强制场景）
GATEWAY_ENV = "ZEPHYR_COMMIT_GATEWAY"
FORCE_ENV = "ZEPHYR_FORCE_DELETE"

#: 观测模式环境变量（CAND-GOVSEC-001 ② 推广配套）：=1 时 in-process 补丁只审计不阻断。
#: 供 pytest conftest 等「先补仪表化盲区、暂不硬拦」的入口进程使用——判定应拦的
#: 目标落 inprocess_would_block 审计 + would_block 计数，实际放行。审计覆盖率=100%
#: 语义不变（每次删除判定必落审计），仅阻断面软化；遥测证明零误伤后可翻硬拦。
AUDIT_ONLY_ENV = "ZEPHYR_OPS_GUARD_AUDIT_ONLY"


class DeleteBlockedError(RuntimeError):
    """删除操作命中保护区被阻断。"""


@dataclass
class DeleteVerdict:
    """删除命令分析结果。"""

    allowed: bool
    reason: str
    primitive: str  # powershell_recurse / cmd_recurse / python_rmtree / python_remove / git_clean / unknown
    targets: list[str] = field(default_factory=list)
    is_recursive: bool = False
    is_protected_zone: bool = False


# ============================================================================
# 工具函数
# ============================================================================


def _get_session_id() -> str:
    """获取当前 session_id。"""
    return os.environ.get(SESSION_ID_ENV, "ops-guard-unknown")


_PROJECT_ROOT_CACHE: Path | None = None


def _get_project_root() -> Path:
    """获取 git 仓库根目录（run_subprocess_hidden 统一入口，trae_067 合规）。

    进程内缓存（in-process 补丁的逐文件判定路径不可承受 subprocess 开销）。
    """
    global _PROJECT_ROOT_CACHE
    if _PROJECT_ROOT_CACHE is not None:
        return _PROJECT_ROOT_CACHE
    try:
        from zephyr.shared.infra.process_pool import run_subprocess_hidden

        result = run_subprocess_hidden(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        _PROJECT_ROOT_CACHE = Path(result.stdout.strip())
    except Exception:
        _PROJECT_ROOT_CACHE = Path.cwd()
    return _PROJECT_ROOT_CACHE


def _normalize_path(p: str) -> str:
    """归一化路径为正斜杠小写相对路径（用于保护区/白名单匹配）。"""
    # 去除引号
    p = p.strip().strip("'\"")
    # 统一正斜杠
    p = p.replace("\\", "/")
    # 折叠重复斜杠（D:\\X\\Y → D:/X/Y 后不会出现 //，但防御双反斜杠输入）
    p = re.sub(r"/{2,}", "/", p)
    # 去除尾部斜杠
    p = p.rstrip("/")
    return p


def _is_under_prefix(path: str, prefix: str) -> bool:
    """检查 path 是否在 prefix 下（或等于 prefix）。"""
    path = _normalize_path(path).lower()
    prefix = _normalize_path(prefix).lower()
    if not prefix:
        return False
    return path == prefix or path.startswith(prefix + "/")


def _is_whitelisted(path: str) -> bool:
    """白名单判定：段级包含匹配。

    白名单条目（.runtime/tmp、__pycache__ 等）是"任意位置的缓存/临时目录"
    语义——worktree 内的 .runtime/tmp 与主仓的 .runtime/tmp 同等合法。
    匹配规则：等于 / 前缀命中 / 中段包含（/prefix/）/ 尾段命中（/prefix）。
    """
    path = _normalize_path(path).lower()
    for wp in ALLOWED_PREFIXES:
        wp_norm = _normalize_path(wp).lower()
        if path == wp_norm or path.startswith(wp_norm + "/") or f"/{wp_norm}/" in path or path.endswith(f"/{wp_norm}"):
            return True
    return False


def _resolve_to_repo_rel(target: str, cwd: str | Path | None = None) -> str:
    """将目标路径解析为相对仓库根的正斜杠路径。

    支持：
    - 相对路径（相对于 cwd 或仓库根）
    - 绝对路径（D:\\ZephyrAlpha\\src → src）
    - worktree 内路径（D:\\ZephyrAlpha\\.worktrees\\AI-X\\src → .worktrees/AI-X/src）
    - 主仓绝对路径（D:\\ZephyrAlpha\\.worktrees → .worktrees）——即使 cwd 在
      某个 worktree 内（git rev-parse 返回 worktree 根），也剥离主仓根判定
    - 尾部通配符（src\\* → src）
    """
    target = _normalize_path(target)
    if not target:
        return target

    # 去尾部通配符（del /s src\* → src）
    target = re.sub(r"/\*(\.\*)?$", "", target)

    root = _get_project_root()
    root_norm = _normalize_path(str(root)).lower()
    # 主仓根：worktree 进程内 git rev-parse 返回 worktree 根，
    # 剥离 .worktrees/<session> 或 .aidrafts/<session> 回主仓
    main_norm = root_norm
    for marker in ("/.worktrees/", "/.aidrafts/"):
        if marker in main_norm:
            main_norm = main_norm[: main_norm.index(marker)]
            break

    target_lower = target.lower()

    # 绝对路径：优先剥离主仓根（覆盖 D:\ZephyrAlpha\.worktrees 等场景）
    if target_lower.startswith(main_norm + "/"):
        return target[len(main_norm) + 1 :]
    # 主仓根本身
    if target_lower == main_norm:
        return "."
    # worktree 根（cwd 所在 worktree）
    if root_norm != main_norm:
        if target_lower.startswith(root_norm + "/"):
            wt_rel = target[len(root_norm) + 1 :]
            session_part = root_norm[len(main_norm) + 1 :]  # .worktrees/<sid>
            return f"{session_part}/{wt_rel}"
        if target_lower == root_norm:
            session_part = root_norm[len(main_norm) + 1 :]
            return session_part
    # 含 .worktrees/ 段的其他绝对路径（主仓其他 worktree）
    if "/.worktrees/" in target_lower:
        idx = target_lower.index("/.worktrees/")
        return target[idx + 1 :]

    # 相对路径：先相对 cwd（默认进程 cwd）拼绝对路径、折叠 . / ..，再重走仓内
    # 剥离逻辑；落仓外则返回归一化绝对路径（保护区/白名单前缀均不命中 → 按非
    # 保护区放行）。批5a 修复：旧实现把相对路径直接当 repo-rel——cwd 在仓外
    # （如 pytest tmp 目录）时删 ./tests/conftest.py 被误判命中仓内保护区，
    # 观测期 402 条 would_block 中 360 条即此误报族；翻硬拦前必修。
    curdir_prefix = os.curdir + "/"
    if target.startswith(curdir_prefix):
        target = target[len(curdir_prefix) :]
    base = Path(cwd) if cwd is not None else Path.cwd()
    abs_path = _normalize_path(os.path.normpath(str(base / target)))
    abs_lower = abs_path.lower()
    if abs_lower.startswith(main_norm + "/"):
        return abs_path[len(main_norm) + 1 :]
    if abs_lower == main_norm:
        return "."
    if root_norm != main_norm:
        if abs_lower.startswith(root_norm + "/"):
            wt_rel = abs_path[len(root_norm) + 1 :]
            session_part = root_norm[len(main_norm) + 1 :]
            return f"{session_part}/{wt_rel}"
        if abs_lower == root_norm:
            return root_norm[len(main_norm) + 1 :]
    # 仓外绝对路径（tmp/其他盘符等）——不命中任何仓内前缀
    return abs_path


def _targets_hash(targets: list[str]) -> str:
    """目标清单的 SHA256 hash（审计用）。"""
    content = "\n".join(sorted(targets))
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


# ============================================================================
# 审计
# ============================================================================


def audit_delete(
    action: str,
    command: str,
    verdict: DeleteVerdict,
    cwd: str | None = None,
) -> None:
    """删除操作审计落盘（非阻断，jsonl 追加 + 分级落盘 + 大小轮转）。

    审计文件: .runtime/gate_audit/ops_guard_delete.jsonl

    批5c 分级落盘（2026-08-26，3.7GB/42h 洪峰治本）：
    - in-process 补丁的非敏感区 allow → 只计数（allow_skipped）不落盘
      （信噪比第一性：异常取证不依赖 tmp/白名单区的 allow 明细，
      333 万条/42h 洪峰 99.99% 是 gateway 临时文件清理）；
    - 敏感区 allow + 全部 block/would_block/guard_* 显式 API 动作 → 全量落盘
      （8-23 型 src 误删事件取证面完整保留——删保护区文件每次必留痕）；
    - 落盘经 audit_jsonl_writer（50MB 大小轮转，旧段移位保留不物理删除）。
    """
    if action == "inprocess_allow" and verdict.allowed and not verdict.is_protected_zone:
        _AUDIT_STATS["allow_skipped"] += 1
        return

    audit_dir = _get_project_root() / ".runtime" / "gate_audit"

    record = {
        "timestamp": time.time(),
        "session_id": _get_session_id(),
        "action": action,
        "command": command,
        "cwd": cwd or str(Path.cwd()),
        "verdict": "ALLOWED" if verdict.allowed else "BLOCKED",
        "reason": verdict.reason,
        "primitive": verdict.primitive,
        "is_recursive": verdict.is_recursive,
        "is_protected_zone": verdict.is_protected_zone,
        "targets": verdict.targets[:20],  # 截断防日志膨胀
        "targets_hash": _targets_hash(verdict.targets),
        "pid": os.getpid(),
    }
    try:
        from zephyr.shared.io.audit_jsonl_writer import append_audit_jsonl

        if not append_audit_jsonl(audit_dir, "ops_guard_delete.jsonl", record):
            _AUDIT_STATS["audit_failed"] += 1  # T2③ 覆盖率指标：落盘失败=覆盖率缺口
    except Exception:  # noqa: BLE001 — 审计不阻断（含写入助手不可导入降级）
        _AUDIT_STATS["audit_failed"] += 1


# ============================================================================
# 命令分析引擎
# ============================================================================


# Remove-Item 已知开关（token 级精确匹配，防误吃路径内连字符段如 AI-BGT-001）
_PS_SWITCH_NO_VALUE = {
    "recurse",
    "force",
    "confirm",
    "whatif",
    "usetransaction",
    "verbose",
    "debug",
    "passthru",
}
_PS_SWITCH_WITH_VALUE = {
    "path",
    "literalpath",
    "include",
    "exclude",
    "filter",
    "credential",
    "erroraction",
    "warningaction",
    "informationaction",
    "errorvariable",
    "warningvariable",
    "informationvariable",
    "outvariable",
    "outbuffer",
    "pipelinevariable",
    "stream",
}


def _extract_ps_targets(cmd: str) -> tuple[list[str], bool]:
    """提取 PowerShell Remove-Item 命令的目标和递归标志。

    token 级解析：逐 token 判定是否为已知开关，未知 `-` 前缀段（如路径内
    AI-BGT-001 的 -BGT）不视为开关——根治连字符路径被开关正则误吃的缺陷。
    """
    is_recursive = bool(re.search(r"-Recurse\b", cmd, re.IGNORECASE))
    # 去掉动词/别名（Remove-Item / ri / rm）
    cleaned = re.sub(r"^(Remove-Item|ri|rm)\s+", "", cmd.strip(), flags=re.IGNORECASE)
    targets: list[str] = []
    tokens = cleaned.split()
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.startswith("-"):
            name = tok[1:].split(":", 1)[0].lower()
            if name in _PS_SWITCH_NO_VALUE:
                i += 1
                continue
            if name in _PS_SWITCH_WITH_VALUE:
                if ":" in tok:
                    # -Path:value 形式
                    value = tok.split(":", 1)[1].strip("'\"")
                    if name in ("path", "literalpath") and value:
                        targets.append(value)
                    i += 1
                    continue
                # -Path value 形式（值是下一个 token）
                if name in ("path", "literalpath") and i + 1 < len(tokens):
                    targets.append(tokens[i + 1].strip("'\""))
                i += 2
                continue
            # 未知 `-` 前缀 token：视为目标（路径可能含连字符段）
        targets.append(tok.strip("'\""))
        i += 1
    return [t for t in targets if t], is_recursive


def _extract_cmd_targets(cmd: str) -> tuple[list[str], bool]:
    """提取 CMD del/rd/rmdir 命令的目标和递归标志。"""
    is_recursive = bool(re.search(r"/[sS]\b", cmd))
    targets: list[str] = []
    # del /s /q <target> 或 rd /s /q <target> 或 rmdir /s /q <target>
    cleaned = re.sub(r"^(del|rd|rmdir|erase)\s+", "", cmd, flags=re.IGNORECASE)
    cleaned = re.sub(r"/[a-zA-Z]+\s*", "", cleaned)  # 去开关
    cleaned = cleaned.strip().strip('"')
    if cleaned:
        targets.append(cleaned)
    return targets, is_recursive


def _extract_python_targets(cmd: str) -> tuple[list[str], bool]:
    """提取 Python shutil.rmtree/os.remove 调用目标。"""
    targets: list[str] = []
    # shutil.rmtree("path") 或 shutil.rmtree('path')
    rmtree_matches = re.findall(r"(?:shutil\.)?rmtree\s*\(\s*['\"]([^'\"]+)['\"]", cmd)
    targets.extend(rmtree_matches)
    # os.remove("path")
    remove_matches = re.findall(r"(?:os\.)?remove\s*\(\s*['\"]([^'\"]+)['\"]", cmd)
    targets.extend(remove_matches)
    is_recursive = bool(rmtree_matches)
    # 批量模式无字面量目标时，从 Path('...')/os.listdir('...')/glob 提取作用目录
    if not targets:
        scope_matches = re.findall(
            r"(?:Path|os\.listdir|glob\.glob|rglob|glob)\s*\(\s*['\"]([^'\"]+)['\"]",
            cmd,
        )
        targets.extend(scope_matches)
    return targets, is_recursive


def _is_batch_os_remove(cmd: str) -> bool:
    """检测 os.remove 批量模式（循环中调用）。"""
    has_loop = bool(re.search(r"(for\s+\w+\s+in|while\s+)", cmd))
    has_remove = bool(re.search(r"os\.remove|os\.unlink", cmd))
    return has_loop and has_remove


def _detect_primitive(cmd: str) -> tuple[str, list[str], bool]:
    """识别命令的删除原语类型，返回 (primitive, targets, is_recursive)。"""
    # PowerShell Remove-Item / ri / rm 别名
    if re.search(r"Remove-Item", cmd, re.IGNORECASE) or re.match(r"^(ri|rm)\s+", cmd, re.IGNORECASE):
        targets, is_recursive = _extract_ps_targets(cmd)
        return "powershell_recurse", targets, is_recursive
    # CMD del/rd/rmdir/erase
    if re.match(r"^(del|rd|rmdir|erase)\s+", cmd, re.IGNORECASE):
        targets, is_recursive = _extract_cmd_targets(cmd)
        return "cmd_recurse", targets, is_recursive
    # Python shutil.rmtree / os.remove / os.unlink
    if re.search(r"(?:shutil\.)?rmtree|(?:os\.)?remove|(?:os\.)?unlink", cmd):
        if _is_batch_os_remove(cmd):
            targets, _ = _extract_python_targets(cmd)
            return "python_remove_batch", targets, True
        rmtree_t, rmtree_r = _extract_python_targets(cmd)
        if rmtree_r:
            return "python_rmtree", rmtree_t, True
        return "python_remove", rmtree_t, False
    # git clean
    if re.match(r"^git\s+clean\b", cmd):
        return "git_clean", ["."], True
    return "unknown", [], False


def _judge_protected(targets: list[str], is_recursive: bool, cwd: str | Path | None) -> tuple[bool, list[str]]:
    """判定目标是否命中保护区，返回 (is_protected, resolved_targets)。"""
    resolved: list[str] = []
    for t in targets:
        rel = _resolve_to_repo_rel(t, cwd)
        resolved.append(rel)
        if _is_whitelisted(rel):
            continue
        if not is_recursive:
            continue
        if rel in (".", ""):
            return True, resolved
        if any(_is_under_prefix(rel, pp) for pp in PROTECTED_PREFIXES):
            return True, resolved
    return False, resolved


def _is_authorized() -> bool:
    """授权环境变量检查（gateway/强制删除场景）。"""
    return os.environ.get(GATEWAY_ENV) == "1" or os.environ.get(FORCE_ENV) == "1"


def _is_docs_untracked(path_str: str, cwd: str | Path | None = None) -> bool:
    """T3②（#ARCH-RECONCILER-AUTO-DELETE-GOV-001）：目标为 docs/ 下 git 未跟踪文件判定。

    清风草稿丢失实证：docs/ 下 untracked 文件"三重无保护"（不在 git、归档器可动、
    物理删除无审计）——此类文件的删除/移动 MUST 人工确认（guard 规则）。

    Returns:
        True=目标在 docs/ 下且 git 未跟踪（git ls-files --error-unmatch 非零）。
        判定异常降级 False（不阻断主流——git 不可达时按 tracked 对待，松约束）。
    """
    rel = _resolve_to_repo_rel(path_str, cwd)
    if not _is_under_prefix(rel, "docs"):
        return False
    try:
        from zephyr.shared.infra.process_pool import run_subprocess_hidden

        result = run_subprocess_hidden(
            ["git", "ls-files", "--error-unmatch", "--", rel],
            cwd=str(_get_project_root()),
            capture_output=True,
            text=True,
        )
        return result.returncode != 0
    except Exception:  # noqa: BLE001 — git 不可达降级 tracked（松约束不阻断）
        return False


def _enforce_docs_untracked(path_str: str, cwd: str | Path | None = None) -> None:
    """docs/ 下 untracked 文件删除/移动的人工确认闸门（T3②）。

    命中且未人工确认（ZEPHYR_FORCE_DELETE=1）→ 审计 + raise。

    ⚠️ 授权判定只认 FORCE_ENV，不认 GATEWAY_ENV：gateway 标记经
    os.environ.copy() 被 reconcile worker 继承（reconcile_runner L708），
    若认 GATEWAY_ENV 则全部 reconciler 天然"已授权"、本闸门形同虚设。
    人工确认 = 人显式设 ZEPHYR_FORCE_DELETE=1，或人直接操作（不经代理）。
    """
    if os.environ.get(FORCE_ENV) == "1":
        return
    if not _is_docs_untracked(path_str, cwd):
        return
    rel = _resolve_to_repo_rel(path_str, cwd)
    verdict = DeleteVerdict(
        allowed=False,
        reason=(
            f"docs/ 下 untracked 文件删除/移动需人工确认（T3② 清风草稿丢失治本）: {rel}——"
            f"三重无保护文件（不在 git/归档器可动/删除无追溯），自动化代理禁动"
        ),
        primitive="docs_untracked",
        targets=[rel],
        is_protected_zone=True,
    )
    audit_delete("docs_untracked_block", f"docs-untracked('{rel}')", verdict, cwd=str(cwd) if cwd else None)
    raise DeleteBlockedError(
        f"[OPS-GUARD] docs/ untracked 文件删除被阻断——{rel}\n"
        f"  解决方案: 人工确认后设 {FORCE_ENV}=1 重试，或由人工直接操作（不经代理）"
    )


def analyze_delete_command(cmd: str, cwd: str | Path | None = None) -> DeleteVerdict:
    """分析命令是否为危险删除操作，判定是否放行。

    识别四类删除原语：
    1. PowerShell: Remove-Item [-Recurse]
    2. CMD: del /s, rd /s, rmdir /s
    3. Python: shutil.rmtree(), os.remove() 批量模式
    4. Git: git clean

    Args:
        cmd: 命令字符串
        cwd: 命令执行的工作目录（用于相对路径解析）

    Returns:
        DeleteVerdict: allowed/reason/primitive/targets/is_recursive/is_protected_zone
    """
    cmd_stripped = cmd.strip()
    if not cmd_stripped:
        return DeleteVerdict(allowed=True, reason="空命令", primitive="unknown")

    primitive, targets, is_recursive = _detect_primitive(cmd_stripped)
    if primitive == "unknown":
        return DeleteVerdict(allowed=True, reason="非删除命令", primitive="unknown")

    is_protected, resolved_targets = _judge_protected(targets, is_recursive, cwd)
    authorized = _is_authorized()

    if is_protected and not authorized:
        return DeleteVerdict(
            allowed=False,
            reason=f"递归删除命中保护区: {resolved_targets}",
            primitive=primitive,
            targets=resolved_targets,
            is_recursive=is_recursive,
            is_protected_zone=True,
        )

    # T3②：docs/ 下 untracked 文件（含非递归单文件——_judge_protected 对非递归
    # 直接放行，此处补齐盲区）删除/移动需人工确认（FORCE_ENV，gateway 标记不算）。
    if os.environ.get(FORCE_ENV) != "1":
        untracked_hits = [t for t in resolved_targets if _is_docs_untracked(t, cwd)]
        if untracked_hits:
            return DeleteVerdict(
                allowed=False,
                reason=(
                    f"docs/ 下 untracked 文件删除需人工确认（T3② 清风治本）: {untracked_hits}——"
                    f"人工确认后设 {FORCE_ENV}=1 重试"
                ),
                primitive=primitive,
                targets=resolved_targets,
                is_recursive=is_recursive,
                is_protected_zone=True,
            )

    reason = (
        "白名单路径"
        if any(_is_whitelisted(rt) for rt in resolved_targets)
        else ("授权放行" if authorized else "非保护区")
    )
    if is_protected and authorized:
        reason = "授权放行（命中保护区但有授权标记）"

    return DeleteVerdict(
        allowed=True,
        reason=reason,
        primitive=primitive,
        targets=resolved_targets,
        is_recursive=is_recursive,
        is_protected_zone=is_protected,
    )


# ============================================================================
# Python API（替换裸 shutil.rmtree / os.remove）
# ============================================================================


def guard_rmtree(path: str | Path, *, cwd: str | Path | None = None) -> None:
    """白名单+审计保护的 shutil.rmtree 替代。

    目标在保护区内且未授权 → raise DeleteBlockedError。
    白名单内或未命中保护区 → 落审计后执行实际删除。
    reconciler 上下文内：先校验 file_ops 声明（未声明 delete → 阻断），
    保护区内递归删除即使已声明也硬拦（双保险）。
    """
    import shutil

    path_str = str(path)
    _enforce_docs_untracked(path_str, cwd)  # T3②：声明制/保护区判定均不豁免
    ctx = _RECONCILER_CTX.get()
    if ctx is not None:
        rel = _resolve_to_repo_rel(path_str, cwd)
        _enforce_file_ops("delete", [rel], cwd=cwd)
    cmd_repr = f"shutil.rmtree('{path_str}')"
    verdict = analyze_delete_command(cmd_repr, cwd)
    audit_delete("guard_rmtree", cmd_repr, verdict, cwd=str(cwd) if cwd else None)

    if not verdict.allowed:
        raise DeleteBlockedError(
            f"[OPS-GUARD] rmtree 被阻断——{verdict.reason}\n"
            f"  目标: {path_str}\n"
            f"  解决方案: 设置 {FORCE_ENV}=1 授权，或移入白名单路径"
        )

    # 2026-08-27 三起误删治本：pytest 上下文保护区浅层永不真删（授权放行也不得执行）
    _enforce_pytest_never_delete_protected("rmtree", _resolve_to_repo_rel(path_str, cwd), path_str)
    shutil.rmtree(path_str, ignore_errors=True)


def guard_remove(path: str | Path, *, cwd: str | Path | None = None) -> None:
    """审计保护的 os.remove 替代（单文件删除不拦递归，但落审计）。

    reconciler 上下文内：校验 file_ops 声明（未声明 delete → 阻断）；
    已声明 → 直通执行+审计（声明即授权，is_protected_zone 标记照记）。
    """
    path_str = str(path)
    ctx = _RECONCILER_CTX.get()
    if ctx is not None:
        rel = _resolve_to_repo_rel(path_str, cwd)
        _enforce_file_ops("delete", [rel], cwd=cwd)
        _enforce_docs_untracked(path_str, cwd)  # T3②：声明制不豁免 untracked 人工确认
        verdict = DeleteVerdict(
            allowed=True,
            reason=f"reconciler {ctx[0]} 已声明 delete（声明制直通）",
            primitive="python_remove",
            targets=[rel],
            is_recursive=False,
            is_protected_zone=any(_is_under_prefix(rel, pp) for pp in PROTECTED_PREFIXES),
        )
        audit_delete("guard_remove", f"os.remove('{path_str}')", verdict, cwd=str(cwd) if cwd else None)
        try:
            os.remove(path_str)
        except FileNotFoundError:
            pass
        return

    _enforce_docs_untracked(path_str, cwd)  # T3②
    cmd_repr = f"os.remove('{path_str}')"
    verdict = analyze_delete_command(cmd_repr, cwd)
    audit_delete("guard_remove", cmd_repr, verdict, cwd=str(cwd) if cwd else None)

    if not verdict.allowed:
        raise DeleteBlockedError(f"[OPS-GUARD] remove 被阻断——{verdict.reason}\n  目标: {path_str}")
    # 2026-08-27 三起误删治本：pytest 上下文保护区浅层递归永不真删（授权放行也不得执行）
    _enforce_pytest_never_delete_protected("remove", _resolve_to_repo_rel(path_str, cwd), path_str, recursive=False)
    try:
        os.remove(path_str)
    except FileNotFoundError:
        pass


# ============================================================================
# 统一回收站（#ARCH-RECONCILER-AUTO-DELETE-GOV-001 T1 治本）
# 治理代理的一切删除/归档 = move 进回收站，30 天保留期，物理删除违规
# ============================================================================

#: 回收站根目录（相对仓库根；.runtime/ 已 gitignore 不入库）
RECYCLE_BIN = ".runtime/recycle_bin"

#: 回收站保留期（秒）——30 天 >>> 事故发现周期
RECYCLE_TTL_SECONDS = 30 * 24 * 3600

#: 回收站容量封顶（字节）——超容时按 ts 批次最旧优先清理（T1③ 裁定：
#: 保留期+容量双上限，防失控归档撑爆磁盘）。
RECYCLE_MAX_BYTES = 512 * 1024 * 1024


def guard_move(src: str | Path, dst: str | Path, *, cwd: str | Path | None = None) -> None:
    """审计保护的 shutil.move 替代。

    源在保护区内且未授权 → raise DeleteBlockedError（move 出保护区 = 删除变体）。
    白名单内或未命中保护区 → 落审计后执行。
    reconciler 上下文内：校验 file_ops 声明（未声明 move → 阻断）；
    已声明 → 直通执行+审计（声明即授权）。
    """
    import shutil

    src_str = str(src)
    dst_str = str(dst)
    _enforce_docs_untracked(src_str, cwd)  # T3②：move 出 docs/ = 删除变体，untracked 需人工确认
    cmd_repr = f"shutil.move('{src_str}', '{dst_str}')"
    ctx = _RECONCILER_CTX.get()
    if ctx is not None:
        rel = _resolve_to_repo_rel(src_str, cwd)
        _enforce_file_ops("move", [rel], cwd=cwd)
        verdict = DeleteVerdict(
            allowed=True,
            reason=f"reconciler {ctx[0]} 已声明 move（声明制直通）",
            primitive="shutil_move",
            targets=[rel],
            is_recursive=False,
            is_protected_zone=any(_is_under_prefix(rel, pp) for pp in PROTECTED_PREFIXES),
        )
        audit_delete("guard_move", cmd_repr, verdict, cwd=str(cwd) if cwd else None)
        Path(dst_str).parent.mkdir(parents=True, exist_ok=True)
        shutil.move(src_str, dst_str)
        return

    # 上下文外：move 出保护区 = 删除变体（补齐原语识别——analyze 不识别 move，
    # 此处直接按源路径判定：递归未知按文件级，保护区内源未授权即拦）。
    rel_src = _resolve_to_repo_rel(src_str, cwd)
    if (
        any(_is_under_prefix(rel_src, pp) for pp in PROTECTED_PREFIXES)
        and not _is_whitelisted(rel_src)
        and not _is_authorized()
    ):
        verdict = DeleteVerdict(
            allowed=False,
            reason=f"move 源命中保护区（move 出保护区=删除变体）: {rel_src}",
            primitive="shutil_move",
            targets=[rel_src],
            is_recursive=Path(src_str).is_dir(),
            is_protected_zone=True,
        )
        audit_delete("guard_move", cmd_repr, verdict, cwd=str(cwd) if cwd else None)
        raise DeleteBlockedError(f"[OPS-GUARD] move 被阻断——{verdict.reason}\n  源: {src_str}\n  目标: {dst_str}")

    verdict = DeleteVerdict(
        allowed=True,
        reason="非保护区 move" if not _is_whitelisted(rel_src) else "白名单路径",
        primitive="shutil_move",
        targets=[rel_src],
        is_recursive=Path(src_str).is_dir(),
    )
    audit_delete("guard_move", cmd_repr, verdict, cwd=str(cwd) if cwd else None)
    Path(dst_str).parent.mkdir(parents=True, exist_ok=True)
    shutil.move(src_str, dst_str)


def guard_recycle(
    path: str | Path,
    *,
    cwd: str | Path | None = None,
    reason: str = "",
    repo_root: str | Path | None = None,
) -> str:
    """统一回收站入口：任何治理代理的"删除"一律 move 进回收站（永不物理删除）。

    回收站结构：.runtime/recycle_bin/<epoch_ts>/<原仓库相对路径>（保留目录层级防重名）。
    保护区文件也允许进回收站——回收站语义本身即保护（30 天可恢复）；
    审计记录 reason 供事后追溯。返回回收站内目标路径（相对仓库根）。

    #ARCH-RECONCILER-AUTO-DELETE-GOV-001 第一性原理：自动化代理判定准确率恒<100%，
    故永不持有不可逆操作能力——guard_recycle 是治理代理唯一合法的"删除"出口。

    reconciler 上下文内：recycle 视同 move（文件离开原位），校验 file_ops 声明。
    """
    import shutil

    # T3②：untracked docs 文件进回收站 = 从 docs/ 消失（清风案正是"被移走找不到"），
    # 回收站 30 天可恢复不豁免人工确认——文件原位消失即构成用户损失。
    _enforce_docs_untracked(str(path), cwd)

    ctx = _RECONCILER_CTX.get()
    if ctx is not None:
        _enforce_file_ops("move", [_resolve_to_repo_rel(str(path), cwd)], cwd=cwd)

    src = Path(str(path))
    root = Path(str(repo_root)) if repo_root else Path(str(cwd)) if cwd else Path.cwd()
    try:
        rel = src.resolve().relative_to(root.resolve())
    except (ValueError, OSError):
        rel = Path(src.name)  # 仓库外路径降级为裸文件名
    ts = int(time.time())
    dst = root / RECYCLE_BIN / str(ts) / rel
    cmd_repr = f"guard_recycle('{src}', reason='{reason}')"

    verdict = DeleteVerdict(
        allowed=True,
        reason=f"回收站收纳（保留 30 天可恢复）: {reason or '未注明'}",
        primitive="recycle_bin",
        targets=[str(rel)],
        is_recursive=src.is_dir(),
        is_protected_zone=False,
    )
    audit_delete("guard_recycle", cmd_repr, verdict, cwd=str(cwd) if cwd else None)

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    return str(dst.relative_to(root))


def prune_recycle_bin(
    *,
    repo_root: str | Path,
    ttl_seconds: int = RECYCLE_TTL_SECONDS,
    max_bytes: int = RECYCLE_MAX_BYTES,
) -> int:
    """回收站清理（唯一合法的物理删除点，仅作用于回收站内部）。

    双上限（T1③）：①TTL 到期清理（30 天）；②容量封顶——超 max_bytes 时
    按 ts 批次最旧优先整批清理直至达标。返回清理的批次数。
    由 doc_lifecycle reconciler 每次运行顺带调用（零新增调度）。
    """
    import shutil

    bin_root = Path(str(repo_root)) / RECYCLE_BIN
    if not bin_root.is_dir():
        return 0
    now = int(time.time())
    pruned = 0

    def _purge_batch(ts_dir: Path, reason: str) -> None:
        for child in ts_dir.iterdir():
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
            else:
                child.unlink(missing_ok=True)
        try:
            ts_dir.rmdir()
        except OSError:
            pass
        audit_delete(
            "recycle_prune",
            f"prune_recycle_bin('{ts_dir.name}')",
            DeleteVerdict(allowed=True, reason=reason, primitive="recycle_prune", targets=[ts_dir.name]),
            cwd=str(repo_root),
        )

    # ① TTL 到期清理
    for ts_dir in list(bin_root.iterdir()):
        if not ts_dir.is_dir() or not ts_dir.name.isdigit():
            continue
        if now - int(ts_dir.name) <= ttl_seconds:
            continue
        _purge_batch(ts_dir, f"回收站 {ttl_seconds // 86400} 天到期清理")
        pruned += 1

    # ② 容量封顶（最旧批次优先；ts 目录名=epoch 可直接排序）
    remaining = sorted(
        (d for d in bin_root.iterdir() if d.is_dir() and d.name.isdigit()),
        key=lambda d: int(d.name),
    )
    total = 0
    for d in remaining:
        for dirpath, _dirs, files in os.walk(d):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(dirpath, f))
                except OSError:
                    pass
    for d in remaining:
        if total <= max_bytes:
            break
        batch_size = 0
        for dirpath, _dirs, files in os.walk(d):
            for f in files:
                try:
                    batch_size += os.path.getsize(os.path.join(dirpath, f))
                except OSError:
                    pass
        _purge_batch(d, f"回收站容量封顶（{max_bytes}B）最旧批次优先清理")
        total -= batch_size
        pruned += 1

    return pruned


# ============================================================================
# reconciler file_ops 声明制运行时强制 + in-process 删除原语补丁
# （#ARCH-RECONCILER-AUTO-DELETE-GOV-001 T1①②，2026-08-14 裁定）
#
# 第一性原理：自动化代理判定准确率恒<100% → 删除/移动能力必须显式声明、
# 全量审计、可逆（回收站）。两层机制：
#   1. reconciler 上下文（contextvar）：reconcile_for 执行每个 reconciler 前
#      注入其 ReconcilerSpec.file_ops 声明；guard_* API 入口校验——未声明
#      delete/move 而执行对应操作 → 审计 + DeleteBlockedError（reconcile_for
#      映射 critical_warn）。
#   2. in-process 补丁（install_inprocess_enforcement）：patch os.remove/
#      os.unlink/os.rmdir/os.rename/shutil.rmtree/shutil.move，reconcile worker
#      进程入口安装——库层生效与进程无关，worker 内裸 stdlib 删除同样被拦
#      （保护区硬拦）+ 落审计（T2③ 审计覆盖率=100% 的采集层）。
# ============================================================================

#: 当前执行的 reconciler 上下文：(gate_id, file_ops frozenset)；None=非 reconciler 执行期
_RECONCILER_CTX: contextvars.ContextVar[tuple[str, frozenset] | None] = contextvars.ContextVar(
    "ops_guard_reconciler_ctx", default=None
)

#: rmtree/move 整体判定后的批量子操作直通 flag（防内部逐文件重复判定刷屏审计）
_BULK_APPROVED: contextvars.ContextVar[bool] = contextvars.ContextVar("ops_guard_bulk_approved", default=False)


@contextlib.contextmanager
def bulk_delete_approved():
    """已授权删除直通（补丁判定短路）——批5b 翻硬拦配套。

    供 safe_rmtree 等自带硬断言的授权通道使用：硬断言通过即授权完成，执行期
    补丁不再重复判定——防授权通道（如 .worktrees/.aidrafts 合法清理）被自家
    补丁拦截。与 _wrapped_shutil_rmtree 的批内直通同一 ContextVar，语义一致。
    """
    token = _BULK_APPROVED.set(True)
    try:
        yield
    finally:
        _BULK_APPROVED.reset(token)


def set_reconciler_context(gate_id: str, file_ops: object) -> contextvars.Token:
    """注入 reconciler 上下文（reconcile_for 执行前调用）。返回 reset 用 token。"""
    return _RECONCILER_CTX.set((gate_id, frozenset(file_ops)))


def reset_reconciler_context(token: contextvars.Token) -> None:
    """复位 reconciler 上下文（reconcile_for 执行后 finally 调用，防泄漏到下一 reconciler）。"""
    _RECONCILER_CTX.reset(token)


def get_reconciler_context() -> tuple[str, frozenset] | None:
    """读取当前 reconciler 上下文（None=非 reconciler 执行期）。"""
    return _RECONCILER_CTX.get()


def _enforce_file_ops(op: str, targets: list[str], cwd: str | Path | None = None) -> None:
    """file_ops 声明强校验：reconciler 上下文内未声明 delete/move 而执行对应操作
    → 审计落盘 + raise DeleteBlockedError（由 reconcile_for 映射 critical_warn）。

    仓外豁免（批5b 配套）：targets 经 _resolve_to_repo_rel 解析后仍为绝对路径的
    = 仓外目标（系统 Temp 的 subprocess housekeeping 清理等）——声明制约束的是
    仓内业务目标的删除能力，仓外 housekeeping 天然豁免，否则每次 commit 的
    reconciler 链产生 file_ops_block 噪音洪峰（2026-08-26 gateway 实证）。
    """
    ctx = _RECONCILER_CTX.get()
    if ctx is None:
        return
    gate_id, declared = ctx
    if op in ("delete", "move") and op not in declared:
        in_repo_targets = [t for t in targets if not _is_absolute_normalized(t)]
        if not in_repo_targets:
            return  # 仓外 housekeeping 豁免（见 docstring）
        _AUDIT_STATS["block"] += 1
        verdict = DeleteVerdict(
            allowed=False,
            reason=(
                f"reconciler {gate_id} file_ops={sorted(declared)} 未声明 '{op}'——"
                "注册时显式声明制（I-GOV-2/T1①），未声明即无此能力"
            ),
            primitive=f"file_ops_{op}",
            targets=list(in_repo_targets),
        )
        audit_delete(
            "file_ops_block", f"{op}({';'.join(in_repo_targets)[:200]})", verdict, cwd=str(cwd) if cwd else None
        )
        raise DeleteBlockedError(
            f"[OPS-GUARD] file_ops 未声明阻断——reconciler {gate_id} 未声明 '{op}' 能力。\n"
            f"  目标: {in_repo_targets[:3]}\n"
            f"  解决方案: 在该 reconciler 的 ReconcilerSpec.file_ops 中显式声明 '{op}'"
            "（声明即承担全量审计+回收站可逆义务）"
        )


def _is_absolute_normalized(p: str) -> bool:
    """归一化（正斜杠）路径是否为绝对路径——POSIX /... 或 Windows d:/...。

    _resolve_to_repo_rel 批5a 语义：仓内目标一律剥离为 repo-rel，返回绝对路径
    的 ⟺ 仓外目标（_enforce_file_ops 仓外豁免判定的唯一依据）。
    """
    return p.startswith("/") or (len(p) > 2 and p[1] == ":" and p[2] == "/")


# ---- in-process 补丁 ----

_ORIG_PRIMITIVES: dict[str, object] = {}
_INSTALLED = False
_INSTALL_LOCK = threading.Lock()

#: 删除判定/审计运行统计（T2③ 审计覆盖率指标化真源）：
#: judge_calls=补丁判定调用总数；allow/block=判定结果；audit_failed=审计落盘失败数；
#: would_block=观测模式（AUDIT_ONLY_ENV=1）下「应拦但放行」计数。
#: 覆盖率 = 已落审计的删除动作 / 实际删除动作 ——每次判定必先审计后执行，
#: audit_failed>0 即覆盖率<100%（RECONCILER-HEALTH 消费报警）。
_AUDIT_STATS: dict[str, int] = {
    "judge_calls": 0,
    "allow": 0,
    "block": 0,
    "audit_failed": 0,
    "would_block": 0,
    "allow_skipped": 0,  # 批5c 分级落盘：非敏感区 allow 只计数不落盘
}


def get_audit_stats() -> dict[str, int]:
    """读取删除判定/审计统计（RECONCILER-HEALTH 覆盖率指标消费）。"""
    return dict(_AUDIT_STATS)


def _audit_only_mode() -> bool:
    """观测模式开关（CAND-GOVSEC-001 ②）：=1 时补丁只审计不阻断。"""
    return os.environ.get(AUDIT_ONLY_ENV) == "1"


def _in_pytest_context() -> bool:
    """pytest 测试上下文检测（PYTEST_CURRENT_TEST 由 pytest 运行期置位）。"""
    return os.environ.get("PYTEST_CURRENT_TEST") is not None


def _enforce_pytest_never_delete_protected(op: str, rel: str, path_str: str, *, recursive: bool = True) -> None:
    """pytest 上下文保护区浅层递归永不真删不变量（2026-08-27 三起误删治本）。

    病灶实证（ops_guard_delete.jsonl 三起 ALLOWED 记录）：pytest 进程继承
    ZEPHYR_COMMIT_GATEWAY / ZEPHYR_FORCE_DELETE 授权变量时，红队测试以真路径
    调用 guard_rmtree('src/zephyr') → 判定"授权放行" → 真删 src/zephyr 整包
    （03:27/08:24/12:27 三起，3513~3537 文件/起，全部经 git restore 恢复）。

    裁定（Owner 2026-08-27 裁定五）：pytest 进程定位=观测哨，但"观测"绝不含真删
    保护区浅层——测试上下文命中「保护区前缀本身或其直接子级」（如 src/zephyr、
    .worktrees/AI-X）的**递归**删除只能是测试缺陷或攻击，无条件硬拦：
    - 不受授权变量影响（_is_authorized 不参与判定）；
    - 不受观测模式软化（不走 _raise_or_observe，直接 raise）；
    - 仅递归删除（rmtree/move 目录，事故型）触发；单文件 remove 走常规分级规则
      （graded audit/untracked/授权门），不受影响；
    - 深层路径（≥前缀深度+2，如 tests/governance/tmp_x 测试自建fixture）不受影响；
    - 白名单（.runtime/tmp 等）不受影响。
    """
    if not recursive:
        return
    if not _in_pytest_context():
        return
    if not rel or _is_whitelisted(rel):
        return
    rel_parts = [p for p in rel.split("/") if p]
    for prefix in PROTECTED_PREFIXES:
        prefix_parts = prefix.split("/")
        if rel_parts[: len(prefix_parts)] != prefix_parts:
            continue
        if len(rel_parts) <= len(prefix_parts) + 1:
            verdict = DeleteVerdict(
                allowed=False,
                reason=f"pytest 上下文保护区浅层永不真删（2026-08-27 三起误删治本）: {rel}",
                primitive=f"inprocess_{op}",
                targets=[rel],
                is_recursive=True,
                is_protected_zone=True,
            )
            _AUDIT_STATS["block"] += 1
            audit_delete("inprocess_block", f"{op}('{path_str}')", verdict)
            raise DeleteBlockedError(
                f"[OPS-GUARD] pytest 上下文禁止真删保护区浅层——{rel}\n"
                f"  测试应使用 tmp_path/假目标；以真实护路径调用属测试缺陷（今日三起误删同型）"
            )
        return



def _raise_or_observe(verdict: DeleteVerdict, cmd_repr: str, message: str) -> bool:
    """阻断统一出口（观测模式软化）。

    硬拦模式（默认）：block 计数 + inprocess_block 审计 + raise DeleteBlockedError。
    观测模式：would_block 计数 + inprocess_would_block 审计 + 返回 True——
    调用方 MUST 立即 return 放行（不再落 allow 审计，防同一删除双记）。
    硬拦模式不返回（raise 不可达）。
    """
    if _audit_only_mode():
        _AUDIT_STATS["would_block"] += 1
        audit_delete("inprocess_would_block", cmd_repr, verdict)
        return True
    _AUDIT_STATS["block"] += 1
    audit_delete("inprocess_block", cmd_repr, verdict)
    raise DeleteBlockedError(message)


def _enforce_docs_untracked_inprocess(op: str, path_str: str, *, recursive: bool) -> bool:
    """T3② docs/ untracked 闸门（in-process 补丁路径包装，观测模式软化）。

    硬拦模式：委托 _enforce_docs_untracked（自落 docs_untracked_block 审计+raise）。
    观测模式：命中则落 inprocess_would_block 审计 + would_block 计数，返回 True
    （调用方 MUST 立即 return 放行）。
    未命中：返回 False（继续主流判定）。
    """
    if not _audit_only_mode():
        try:
            _enforce_docs_untracked(path_str)
        except DeleteBlockedError:
            _AUDIT_STATS["block"] += 1
            raise
        return False
    if not _is_docs_untracked(path_str):
        return False
    rel = _resolve_to_repo_rel(path_str)
    verdict = DeleteVerdict(
        allowed=False,
        reason=f"docs/ untracked 人工确认闸门（观测模式记录，硬拦模式阻断）: {rel}",
        primitive=f"inprocess_{op}",
        targets=[rel],
        is_recursive=recursive,
        is_protected_zone=True,
    )
    _AUDIT_STATS["would_block"] += 1
    audit_delete("inprocess_would_block", f"{op}('{path_str}')", verdict)
    return True


def _inprocess_judge(op: str, path: object, *, recursive: bool) -> None:
    """补丁统一判定：raise DeleteBlockedError 阻断；否则落审计后由 wrapper 执行。

    判定矩阵：
    - 批量直通 flag → 直接放行（rmtree/move 整体判定已过）
    - reconciler 上下文内 → file_ops 声明校验；已声明且递归+保护区仍硬拦（双保险）
    - 上下文外（worker/进程内裸调用）→ 保护区内目标（含单文件）未授权即拦；
      白名单/其他区域放行+审计
    """
    if _BULK_APPROVED.get():
        return
    _AUDIT_STATS["judge_calls"] += 1
    path_str = os.fspath(path) if not isinstance(path, str) else path
    # 2026-08-27 三起误删治本：pytest 上下文保护区浅层递归永不真删（最先判定，先于一切授权）
    _enforce_pytest_never_delete_protected(op, _resolve_to_repo_rel(path_str), path_str, recursive=recursive)
    ctx = _RECONCILER_CTX.get()
    if ctx is not None:
        rel = _resolve_to_repo_rel(path_str)
        _enforce_file_ops(op, [rel])
        if _enforce_docs_untracked_inprocess(op, path_str, recursive=recursive):
            return  # 观测模式：would_block 已落审计，放行
        if (
            recursive
            and not _is_whitelisted(rel)
            and any(_is_under_prefix(rel, pp) for pp in PROTECTED_PREFIXES)
            and not _is_authorized()
        ):
            verdict = DeleteVerdict(
                allowed=False,
                reason=f"reconciler {ctx[0]} 已声明 {op} 但保护区内递归删除硬拦（双保险）: {rel}",
                primitive=f"inprocess_{op}",
                targets=[rel],
                is_recursive=True,
                is_protected_zone=True,
            )
            if _raise_or_observe(verdict, f"{op}('{path_str}')", f"[OPS-GUARD] {verdict.reason}"):
                return  # 观测模式：would_block 已落审计，放行
        _AUDIT_STATS["allow"] += 1
        audit_delete(
            "inprocess_allow",
            f"{op}('{path_str}')",
            DeleteVerdict(
                allowed=True,
                reason=f"reconciler {ctx[0]} 已声明 {op}",
                primitive=f"inprocess_{op}",
                targets=[rel],
                is_recursive=recursive,
                is_protected_zone=any(_is_under_prefix(rel, pp) for pp in PROTECTED_PREFIXES),
            ),
        )
        return
    # 上下文外：裸 stdlib 调用（worker 进程任意代码路径）
    rel = _resolve_to_repo_rel(path_str)
    if _is_whitelisted(rel):
        _AUDIT_STATS["allow"] += 1
        audit_delete(
            "inprocess_allow",
            f"{op}('{path_str}')",
            DeleteVerdict(
                allowed=True, reason="白名单路径", primitive=f"inprocess_{op}", targets=[rel], is_recursive=recursive
            ),
        )
        return
    if _enforce_docs_untracked_inprocess(op, path_str, recursive=recursive):
        return  # 观测模式：would_block 已落审计，放行
    if any(_is_under_prefix(rel, pp) for pp in PROTECTED_PREFIXES) and not _is_authorized():
        verdict = DeleteVerdict(
            allowed=False,
            reason=f"in-process 裸删除命中保护区: {rel}",
            primitive=f"inprocess_{op}",
            targets=[rel],
            is_recursive=recursive,
            is_protected_zone=True,
        )
        if _raise_or_observe(
            verdict,
            f"{op}('{path_str}')",
            f"[OPS-GUARD] in-process 删除被阻断——{verdict.reason}\n"
            f"  解决方案: 治理代理改用 guard_* API 并在 ReconcilerSpec.file_ops 显式声明",
        ):
            return  # 观测模式：would_block 已落审计，放行
    _AUDIT_STATS["allow"] += 1
    audit_delete(
        "inprocess_allow",
        f"{op}('{path_str}')",
        DeleteVerdict(
            allowed=True,
            # 授权通过的保护区目标须如实标注——否则批5c 分级落盘把"授权删 src"
            # 当非敏感区跳过（8-23 型事件取证面缺口，test_graded_audit_sensitive 钉）
            reason=(
                "授权通过（FORCE/GATEWAY）"
                if any(_is_under_prefix(rel, pp) for pp in PROTECTED_PREFIXES)
                else "非保护区"
            ),
            primitive=f"inprocess_{op}",
            targets=[rel],
            is_recursive=recursive,
            is_protected_zone=any(_is_under_prefix(rel, pp) for pp in PROTECTED_PREFIXES),
        ),
    )


def _wrapped_remove(path: object, *a: object, **kw: object) -> object:
    _inprocess_judge("delete", path, recursive=False)
    return _ORIG_PRIMITIVES["os.remove"](path, *a, **kw)


def _wrapped_unlink(path: object, *a: object, **kw: object) -> object:
    _inprocess_judge("delete", path, recursive=False)
    return _ORIG_PRIMITIVES["os.unlink"](path, *a, **kw)


def _wrapped_rmdir(path: object, *a: object, **kw: object) -> object:
    _inprocess_judge("delete", path, recursive=False)
    return _ORIG_PRIMITIVES["os.rmdir"](path, *a, **kw)


def _wrapped_rename(src: object, dst: object, *a: object, **kw: object) -> object:
    _inprocess_judge("move", src, recursive=False)
    return _ORIG_PRIMITIVES["os.rename"](src, dst, *a, **kw)


def _wrapped_shutil_rmtree(path: object, *a: object, **kw: object) -> object:
    _inprocess_judge("delete", path, recursive=True)
    token = _BULK_APPROVED.set(True)
    try:
        return _ORIG_PRIMITIVES["shutil.rmtree"](path, *a, **kw)
    finally:
        _BULK_APPROVED.reset(token)


def _wrapped_shutil_move(src: object, dst: object, *a: object, **kw: object) -> object:
    _inprocess_judge("move", src, recursive=False)
    token = _BULK_APPROVED.set(True)
    try:
        return _ORIG_PRIMITIVES["shutil.move"](src, dst, *a, **kw)
    finally:
        _BULK_APPROVED.reset(token)


def install_inprocess_enforcement() -> bool:
    """幂等安装 in-process 删除原语补丁（reconcile worker 进程入口调用）。

    patch os.remove/os.unlink/os.rmdir/os.rename + shutil.rmtree/shutil.move
    （pathlib.Path.unlink/rmdir 内部走 os.unlink/os.rmdir，一并覆盖）。
    返回 True=本次新装，False=已装（幂等）。
    """
    global _INSTALLED
    with _INSTALL_LOCK:
        if _INSTALLED:
            return False
        import shutil as _shutil_mod

        _ORIG_PRIMITIVES["os.remove"] = os.remove
        _ORIG_PRIMITIVES["os.unlink"] = os.unlink
        _ORIG_PRIMITIVES["os.rmdir"] = os.rmdir
        _ORIG_PRIMITIVES["os.rename"] = os.rename
        _ORIG_PRIMITIVES["shutil.rmtree"] = _shutil_mod.rmtree
        _ORIG_PRIMITIVES["shutil.move"] = _shutil_mod.move

        os.remove = _wrapped_remove  # type: ignore[assignment]
        os.unlink = _wrapped_unlink  # type: ignore[assignment]
        os.rmdir = _wrapped_rmdir  # type: ignore[assignment]
        os.rename = _wrapped_rename  # type: ignore[assignment]
        _shutil_mod.rmtree = _wrapped_shutil_rmtree  # type: ignore[assignment]
        _shutil_mod.move = _wrapped_shutil_move  # type: ignore[assignment]
        _INSTALLED = True
        return True


def install_inprocess_enforcement_audit_only() -> bool:
    """CAND-GOVSEC-001 ② 推广入口专用：audit-only 模式装 in-process 删除护栏。

    推广期一律观测模式（ZEPHYR_OPS_GUARD_AUDIT_ONLY=1，setdefault 不覆盖宿主
    显式 =0 的硬拦配置）——先补仪表化盲区不硬拦，遥测证明零误伤后可翻硬拦。
    装配面：git_commit / session_worktree CLI / commit_queue drain / pytest
    conftest / session_worktree_sweep 库入口（reconcile_worker 仍走硬拦版
    install_inprocess_enforcement）。永不抛异常（观测补强不阻断宿主主链路）。

    Returns:
        bool: True=本次新装，False=已装（幂等）或安装失败降级。
    """
    os.environ.setdefault(AUDIT_ONLY_ENV, "1")
    try:
        return install_inprocess_enforcement()
    except Exception:  # noqa: BLE001 — 观测补强永不阻断宿主主链路
        return False


def inprocess_enforcement_installed() -> bool:
    """补丁是否已安装（测试/自检用）。"""
    return _INSTALLED


def uninstall_inprocess_enforcement() -> bool:
    """卸载 in-process 补丁，恢复原语（测试进程污染防护，治理批③ 2026-08-15）。

    生产 worker 进程从不调用（补丁随进程退出消亡）；仅供测试场景：
    同进程调用 run_worker（如 selfheal integration 测试）后补丁残留，
    会拦截同进程后续测试自身的清理删除（字母序在 audit 后的 rule_bridge
    等目录 fixture 清理命中保护区误拦实证）。测试 fixture 收尾调用本函数。
    返回 True=本次卸载，False=未安装（幂等）。
    """
    global _INSTALLED
    with _INSTALL_LOCK:
        if not _INSTALLED:
            return False
        import shutil as _shutil_mod

        for name, orig in _ORIG_PRIMITIVES.items():
            if name.startswith("shutil."):
                setattr(_shutil_mod, name.split(".", 1)[1], orig)
            else:
                setattr(os, name.split(".", 1)[1], orig)
        _ORIG_PRIMITIVES.clear()
        _INSTALLED = False
        return True


# ============================================================================
# CLI
# ============================================================================


def _cmd_check(args: list[str]) -> int:
    """检查命令是否安全（不执行）。"""
    if not args:
        print("[OPS-GUARD] 错误: 未指定要检查的命令", file=sys.stderr)
        return 2
    cmd = " ".join(args)
    verdict = analyze_delete_command(cmd)
    audit_delete("check", cmd, verdict)

    if not verdict.allowed:
        print("", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print("[OPS-GUARD] 命令被阻断——递归删除命中保护区（wipe 事故防护）", file=sys.stderr)
        print(f"  命令: {cmd}", file=sys.stderr)
        print(f"  原语: {verdict.primitive}", file=sys.stderr)
        print(f"  目标: {verdict.targets}", file=sys.stderr)
        print(f"  原因: {verdict.reason}", file=sys.stderr)
        print("", file=sys.stderr)
        print("  解决方案:", file=sys.stderr)
        print(f"    1. 确认安全后强制执行: {FORCE_ENV}=1 python scripts/ops_guard.py exec ...", file=sys.stderr)
        print("    2. 将目标移入白名单路径（.runtime/tmp 等）", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        return 1

    print(f"[OPS-GUARD] 放行: {verdict.reason}")
    return 0


def _cmd_exec(args: list[str]) -> int:
    """先审计后执行命令。"""
    if not args:
        print("[OPS-GUARD] 错误: 未指定要执行的命令", file=sys.stderr)
        return 2
    cmd = " ".join(args)
    verdict = analyze_delete_command(cmd)
    audit_delete("exec", cmd, verdict)

    if not verdict.allowed:
        print("", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print("[OPS-GUARD] 命令被阻断——递归删除命中保护区（wipe 事故防护）", file=sys.stderr)
        print(f"  命令: {cmd}", file=sys.stderr)
        print(f"  原语: {verdict.primitive}", file=sys.stderr)
        print(f"  目标: {verdict.targets}", file=sys.stderr)
        print(f"  原因: {verdict.reason}", file=sys.stderr)
        print("", file=sys.stderr)
        print("  解决方案:", file=sys.stderr)
        print(f"    1. 确认安全后强制执行: {FORCE_ENV}=1 python scripts/ops_guard.py exec ...", file=sys.stderr)
        print("    2. 将目标移入白名单路径（.runtime/tmp 等）", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        return 1

    # 放行：执行命令（run_subprocess_hidden 统一入口，trae_067 合规）
    print(f"[OPS-GUARD] 放行（{verdict.reason}），执行: {cmd}")
    from zephyr.shared.infra.process_pool import run_subprocess_hidden

    result = run_subprocess_hidden(cmd, shell=True)
    return result.returncode


def main() -> int:
    """CLI 入口。"""
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2

    subcommand = sys.argv[1]
    args = sys.argv[2:]

    if subcommand == "check":
        return _cmd_check(args)
    elif subcommand == "exec":
        return _cmd_exec(args)
    else:
        print(f"[OPS-GUARD] 未知子命令: {subcommand}", file=sys.stderr)
        print("用法: python scripts/ops_guard.py check|exec <command...>", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
