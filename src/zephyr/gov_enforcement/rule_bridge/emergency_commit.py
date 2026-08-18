# [BLUEPRINT] MOD-GOV_EMERGENCY_COMMIT | docs/03_modules/_domain_governance/blueprint.md | §Ruling-100PCT-AI-GOVERNANCE-P2-1
# [MODULE] zephyr.gov_enforcement.rule_bridge.emergency_commit
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (log_emergency_commit); zephyr.shared.io.paths (REPO_ROOT)
# [CONSUMERS] AI 紧急提交场景（GitCommitGateway 锁死/POST-COMMIT-GUARD 反复 reset 时）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 用 git commit-tree plumbing 绕过所有 hook（pre-commit AND post-commit）；临时 index 原子化多文件提交；每次提交持久化到 reconcile_execution_log（action='emergency_commit'）+ .runtime/reconcile_reports/ 审计文件；commit message 含 [GW:{session_id}:emergency] 标记；不获取 _GlobalCommitLock（emergency 模式前提是锁不可用）
# [MODIFY-GUARD] emergency_commit 函数签名；commit-tree 调用序列；[GW:...:emergency] 标记格式
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 文件不存在/空列表→ok=False 不抛异常；git 命令失败→ok=False 含 stderr；DB 日志失败→warn 不阻断
# [TESTS] tests/governance/rule_bridge/test_emergency_commit.py
# [A_module] module_id=MOD-GOV_EMERGENCY_COMMIT | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: 本模块无周期触发
"""

emergency_commit.py — 紧急提交通道（Ruling:100PCT-AI-GOVERNANCE P2-1，2026-07-19）

用 ``git commit-tree`` plumbing 命令绕过所有 git hook（pre-commit AND post-commit），
为 GitCommitGateway 锁死 / POST-COMMIT-GUARD 反复 reset 场景提供合法化逃生通道。

病根（第一性原理）
-----------------
POST-COMMIT-GUARD (#ARCH-050) 对 non-GW commit 执行 ``git reset --soft HEAD~1``。
``--no-verify`` 只跳过 pre-commit，不跳过 post-commit。当 GitCommitGateway 被
stuck 进程阻塞（_GlobalCommitLock 超时）或 session 注册表异常导致 POST-COMMIT-GUARD
反复 reset 时，唯一可靠绕过路径是 ``git commit-tree``（plumbing 命令不触发任何 hook）。

但裸 ``git commit-tree`` 是治理盲区：
  - 无 session_id 标记（审计不可追溯）
  - 无 reconcile_execution_log 记录（AI 无法查询历史）
  - 无 reconciler 触发（post-commit reconciler 链路跳过）
  - 无 SessionRegistry 注册（并发可见性丢失）

治本（P2-1）
-----------
本模块封装 ``git commit-tree`` 为合法化 Python API ``emergency_commit()``：
  1. 添加 ``[GW:{session_id}:emergency]`` 标记到 commit message（审计可追溯）
  2. 持久化到 ``reconcile_execution_log``（action='emergency_commit'）—— AI 可查询
  3. 写审计报告到 ``.runtime/reconcile_reports/emergency_commit_*.json``
  4. 可选触发 post-commit reconciler 链路（默认触发，补齐被绕过的 reconciler）
  5. 临时 index（GIT_INDEX_FILE）原子化多文件提交，不污染主 index

与 GitCommitGateway.commit() 的区别
-----------------------------------
  - GitCommitGateway.commit(): 正常通道，获取 _GlobalCommitLock，跑 pre-commit gate，
    触发 pre-commit/post-commit hook，跑 reconciler
  - emergency_commit(): 紧急通道，不获取锁（前提是锁不可用），跳过所有 gate/hook，
    手动触发 reconciler，全程持久化审计

使用场景
--------
  - GitCommitGateway 被 stuck 进程阻塞（_GlobalCommitLock 超时 60s）
  - POST-COMMIT-GUARD 反复 reset（session 注册表异常，合法 GW commit 被误判）
  - P0 紧急修复需要立即提交（生产故障）

非使用场景（禁止）
-----------------
  - 常规提交（必须走 GitCommitGateway 或 session_worktree_commit）
  - 绕过 gate 检查（gate 失败时必须修复问题，不能用 emergency_commit 逃避）
  - 并发提交（emergency_commit 不获取锁，并发调用会产生 race condition）

用法
----
    from zephyr.gov_enforcement.rule_bridge.emergency_commit import emergency_commit

    result = emergency_commit(
        files=["src/zephyr/some_module/fix.py"],
        message="P0 fix: critical bug in some_module",
        session_id="sess-emergency-001",
        reason="GitCommitGateway 锁死，POST-COMMIT-GUARD 反复 reset",
    )
    if result["ok"]:
        print(f"紧急提交成功: {result['commit_hash']}")
    else:
        print(f"紧急提交失败: {result['error']}")

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 紧急提交请求入参
#   fields: files 文件列表 + message + session_id + reason + scenario + trigger_reconcilers
#   code: emergency_commit(files, message, session_id, ...) L403-411
# - id: I2
#   name: git 仓库 HEAD 与当前分支
#   fields: 当前分支名（detached HEAD 拒绝）+ HEAD SHA（commit-tree 的 parent）
#   code: _get_current_branch L364 / _get_head_sha L376
# - id: I3
#   name: agent 紧急计数桶文件
#   fields: {"count": N, "block_next_start": bool}（按 agent 持久标识分桶，跨 session）
#   code: .runtime/emergency_counts/<bucket_id>.json L111 + L175-182
# 层: 算法
# - id: A1
#   name_zh: ① agent 分桶标识解析
#   name_en: _agent_bucket_id
#   intro: 给 AI 找一个跨 session 不变的持久身份做计数分桶，防每次新 session_id 计数清零
#   desc: ZEPHYR_AGENT_ID 环境变量 > git config --local user.email（先 rev-parse 校验仓库根）> USER/USERNAME > "default" L114-172
#   inputs: I3
#   outputs: bucket_id
# - id: A2
#   name_zh: ② 成本递增门禁
#   name_en: _check_emergency_escalation
#   intro: 紧急提交用得越多门槛越高——3 次起必须写明原因，5 次直接阻断逼你查根因
#   desc: count>=5 硬阻断（须先清计数文件）；count>=3 且 reason 为空拒绝 L223-252
#   inputs: A1 I1
#   outputs: (allowed, error_msg)
#   invariant: 阈值 _EMERGENCY_REASON_THRESHOLD=3 / _EMERGENCY_BLOCK_THRESHOLD=5
# - id: A3
#   name_zh: ③ 文件归一化校验
#   name_en: _normalize_files
#   intro: 把传入文件统一成绝对路径+posix 相对路径，不存在直接 FileNotFoundError
#   desc: 相对路径相对 root 解析 → is_absolute/p.exists 校验 → relative_to(root).as_posix() L384-400
#   inputs: I1
#   outputs: [(abs_path, rel_path)]
# - id: A4
#   name_zh: ④ 无 hook plumbing 提交链
#   name_en: emergency_commit（主流程）
#   intro: 用 git commit-tree 底层命令造 commit，完全不触发 pre/post-commit hook，绕过锁死网关
#   desc: 临时 index（GIT_INDEX_FILE）read-tree HEAD → 逐文件 hash-object -w → update-index --add --cacheinfo → write-tree → commit-tree -p HEAD -F msg → update-ref 更新分支 L544-647；message 自动追加 [GW:{sid}:emergency] + [SCENARIO:*] 标记 L531-533
#   inputs: A2 A3 I2
#   outputs: commit_sha
#   invariant: 不获取 _GlobalCommitLock；不触发任何 git hook；临时 index 不污染主 index
# - id: A5
#   name_zh: ⑤ 审计落地与 reconciler 补齐
#   name_en: log_emergency_commit + _trigger_reconcilers_safely + _increment_emergency_count
#   intro: 提交后补三笔治理账：执行日志、审计报告、reconciler 链路，再递增计数
#   desc: log_emergency_commit 写 reconcile_execution_log(action='emergency_commit') L650-659；trigger_reconcilers 时手动调 gateway._run_post_commit_reconcile L709-749；成功后计数 +1，>=5 置 block_next_start L677-683；审计/计数失败只 warn 不阻断
#   inputs: A4
#   outputs: 审计持久化
# 层: 输出
# - id: O1
#   name_zh: 紧急提交结果
#   name_en: EmergencyCommitResult
#   intro: TypedDict 返回契约——ok 字段是成败唯一入口，含 commit_hash 短 SHA/branch/files_count
#   invariant: 所有失败路径 ok=False 不抛异常
#   downstream: AI 紧急提交场景手工调用（# [CONSUMERS] 头）
# - id: O2
#   name_zh: 紧急提交审计痕迹
#   name_en: reconcile_execution_log + .runtime/reconcile_reports/*.json + GW 标记
#   intro: action='emergency_commit' 的 DB 日志 + JSON 审计报告 + commit message 里的 [GW:{sid}:emergency] 标记
#   downstream: check_start_blocked 被 session_worktree_start 消费 MOD-GOV_SESSION_WORKTREE
# [/ALGO_FLOW]
#
# 边:
# I3 --> A1
# A1 --> A2
# I1 --> A2
# I1 --> A3
# A2 --> A4
# A3 --> A4
# I2 --> A4
# A4 --> A5
# A4 --> O1
# A5 --> O2
"""

from __future__ import annotations

__all__ = ["emergency_commit", "check_start_blocked"]

import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import TypedDict

from zephyr.governance.audit.reconciliation_registry import log_emergency_commit
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

# commit-tree plumbing 命令超时（秒）
_COMMIT_TREE_TIMEOUT = 60
# hash-object 单文件超时（秒）
_HASH_OBJECT_TIMEOUT = 10

# #ARCH-HEARTBEAT-001 P1-5 成本递增阈值
# N >= 3 需显式 reason（强制说明紧急提交原因）
# N >= 5 阻断下次 session_worktree_start（强制调查根因）
_EMERGENCY_REASON_THRESHOLD: int = 3
_EMERGENCY_BLOCK_THRESHOLD: int = 5
# P1-2 治本（#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）：
# 原按 session_id 分桶，AI 每次新 session_id 导致计数永远停在 1，N>=3/N>=5 永不触发。
# 改为按 agent_id 持久标识分桶（env ZEPHYR_AGENT_ID > git config user.email > "default"）。
# 计数文件路径 .runtime/emergency_counts/<agent_id>.json（与 .runtime/sessions/ 分离）。
_EMERGENCY_COUNTS_DIR: str = ".runtime/emergency_counts"


def _agent_bucket_id(project_root: str | Path) -> str:
    """获取 emergency_commit 计数分桶 ID（#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001 P1-2）。

    100% AI 开发下，AI 每次启动新 session_id，按 session_id 分桶的计数永远停在 1。
    改为按 agent 持久标识分桶，使同一 AI 的多次 emergency_commit 累积计数。

    优先级：
      1. 环境变量 ZEPHYR_AGENT_ID（AI 显式声明）
      2. git config user.email（git 提交者标识）
      3. 环境变量 USER / USERNAME（OS 用户）
      4. "default"（最终 fallback）

    Args:
        project_root: 项目根目录（用于读取 git config）。

    Returns:
        agent_bucket_id 字符串（用于计数文件分桶路径）。
    """
    # 1. 环境变量 ZEPHYR_AGENT_ID
    agent_id = os.environ.get("ZEPHYR_AGENT_ID", "").strip()
    if agent_id:
        return agent_id
    # 2. git config --local user.email（仅当 project_root 是 git 仓库根时读取）
    # 治本（#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001 P1-2）：
    # pytest basetemp 在项目 git 仓库子目录内（.runtime/tmp/pytest/），
    # `git config --local` 会找到父仓库的 local config 并返回 email，
    # 导致 fallback 链断裂。用 `git rev-parse --show-toplevel` 校验
    # project_root 本身是 git 仓库根（而非子目录），只有根才读取 local config。
    try:
        from zephyr.shared.infra.process_pool import run_subprocess_hidden
        toplevel_r = run_subprocess_hidden(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(project_root),
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            timeout=5,
        )
        if toplevel_r.returncode == 0:
            toplevel = Path(toplevel_r.stdout.strip()).resolve()
            if toplevel == Path(project_root).resolve():
                cfg_r = run_subprocess_hidden(
                    ["git", "config", "--local", "user.email"],
                    cwd=str(project_root),
                    capture_output=True, text=True,
                    encoding="utf-8", errors="replace",
                    timeout=5,
                )
                if cfg_r.returncode == 0:
                    email = cfg_r.stdout.strip()
                    if email:
                        return f"email:{email}"
    except Exception:  # noqa: BLE001 — git 失败 fallback 下一个
        pass
    # 3. USER / USERNAME
    user = os.environ.get("USER") or os.environ.get("USERNAME", "")
    if user:
        return f"user:{user}"
    # 4. default
    return "default"


def _emergency_count_path(project_root: str | Path, bucket_id: str) -> Path:
    """返回 emergency_count.json 文件路径（按 agent bucket_id 分桶）。

    Args:
        project_root: 项目根目录。
        bucket_id: agent bucket ID（由 _agent_bucket_id 返回，非 session_id）。
    """
    return Path(project_root) / _EMERGENCY_COUNTS_DIR / f"{bucket_id}.json"


def _read_emergency_count(project_root: str | Path, bucket_id: str) -> dict:
    """读取 agent bucket 的 emergency 计数（返回 {"count": N, "block_next_start": bool}）。

    文件不存在时返回 {"count": 0, "block_next_start": False}（默认值）。

    Args:
        project_root: 项目根目录。
        bucket_id: agent bucket ID（由 _agent_bucket_id 返回）。
    """
    path = _emergency_count_path(project_root, bucket_id)
    if not path.exists():
        return {"count": 0, "block_next_start": False}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"count": 0, "block_next_start": False}


def _write_emergency_count(
    project_root: str | Path, bucket_id: str, data: dict,
) -> None:
    """写入 emergency 计数（原子写入：tmp + os.replace）。

    Args:
        project_root: 项目根目录。
        bucket_id: agent bucket ID（由 _agent_bucket_id 返回）。
        data: 计数数据 dict。
    """
    path = _emergency_count_path(project_root, bucket_id)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        os.replace(str(tmp), str(path))
    except OSError as e:
        logger.warning("emergency count write failed (non-blocking): %s", e)


def _check_emergency_escalation(
    project_root: str | Path, bucket_id: str, reason: str,
) -> tuple[bool, str]:
    """检查 emergency_commit 成本递增门禁（#ARCH-HEARTBEAT-001 P1-5 + P1-2 治本）。

    - N >= 3 且 reason 为空 → 拒绝（强制说明原因）
    - N >= 5 → 拒绝（已超阈值，必须先解决根因）

    Args:
        project_root: 项目根目录。
        bucket_id: agent bucket ID（由 _agent_bucket_id 返回，跨 session 持久）。
        reason: 调用方提供的紧急提交原因。

    Returns:
        (allowed, error_msg) — allowed=True 时 error_msg 为空。
    """
    data = _read_emergency_count(project_root, bucket_id)
    count = data.get("count", 0)
    if count >= _EMERGENCY_BLOCK_THRESHOLD:
        return False, (
            f"emergency_commit 已达 {count} 次（阈值 {_EMERGENCY_BLOCK_THRESHOLD}），"
            f"阻断本次提交。必须先调查根因（GitCommitGateway 锁死/POST-COMMIT-GUARD 反复 reset），"
            f"解决后清理 .runtime/emergency_counts/{bucket_id}.json 重置计数。"
        )
    if count >= _EMERGENCY_REASON_THRESHOLD and not reason.strip():
        return False, (
            f"emergency_commit 已达 {count} 次（阈值 {_EMERGENCY_REASON_THRESHOLD}），"
            f"必须提供非空 reason 参数说明紧急提交原因。"
        )
    return True, ""


def _increment_emergency_count(
    project_root: str | Path, bucket_id: str,
) -> int:
    """emergency_commit 成功后递增计数（#ARCH-HEARTBEAT-001 P1-5 + P1-2 治本）。

    N+1 >= 5 时设置 block_next_start=True（阻断下次 session_worktree_start）。

    Args:
        project_root: 项目根目录。
        bucket_id: agent bucket ID（由 _agent_bucket_id 返回）。

    Returns:
        递增后的新计数。
    """
    data = _read_emergency_count(project_root, bucket_id)
    new_count = data.get("count", 0) + 1
    block_next = new_count >= _EMERGENCY_BLOCK_THRESHOLD
    _write_emergency_count(project_root, bucket_id, {
        "count": new_count,
        "block_next_start": block_next,
        "bucket_id": bucket_id,
    })
    if block_next:
        logger.warning(
            "emergency_commit count reached %d (block threshold %d) — "
            "next session_worktree_start will be blocked (bucket=%s)",
            new_count, _EMERGENCY_BLOCK_THRESHOLD, bucket_id,
        )
    return new_count


def check_start_blocked(project_root: str | Path) -> tuple[bool, str]:
    """检查是否有 agent bucket 阻断 session_worktree_start（#ARCH-HEARTBEAT-001 P1-5 + P1-2 治本）。

    扫描 .runtime/emergency_counts/*.json，若任何 bucket 的
    block_next_start=True 则阻断。

    Args:
        project_root: 项目根目录。

    Returns:
        (blocked, reason) — blocked=True 时 reason 含阻断 bucket 信息。
    """
    counts_dir = Path(project_root) / _EMERGENCY_COUNTS_DIR
    if not counts_dir.exists():
        return False, ""
    try:
        for count_file in counts_dir.glob("*.json"):
            if not count_file.is_file():
                continue
            try:
                data = json.loads(count_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            if data.get("block_next_start", False):
                bucket_id = data.get("bucket_id", count_file.stem)
                return True, (
                    f"agent bucket '{bucket_id}' 的 emergency_commit 计数达 "
                    f"{data.get('count', 0)} 次（阈值 {_EMERGENCY_BLOCK_THRESHOLD}），"
                    f"阻断新 session 启动。必须先调查根因（GitCommitGateway 锁死/POST-COMMIT-GUARD 反复 reset），"
                    f"解决后删除 {count_file} 重置计数。"
                )
    except OSError:
        pass
    return False, ""


class EmergencyCommitResult(TypedDict, total=False):
    """emergency_commit 返回契约（对标 session_worktree_commit 的 CommitResult）。

    ``ok`` 是判定成败的唯一入口（项目 memory 硬约束：TypedDict 统一 ok 键）。
    """
    ok: bool
    session_id: str
    status: str  # "OK" | "FAILED"
    commit_hash: str  # 成功时为短 SHA，否则空
    error: str  # 失败原因
    branch: str  # 提交到的分支名
    files_count: int  # 提交的文件数


def run_git(
    cmd: list[str],
    cwd: str,
    env: dict | None = None,
    timeout: int = _COMMIT_TREE_TIMEOUT,
) -> subprocess.CompletedProcess:
    """执行 git 命令（统一 encoding + timeout + CREATE_NO_WINDOW）。"""
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    from zephyr.shared.infra.process_pool import run_subprocess_hidden

    return run_subprocess_hidden(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        env=full_env,
    )

def _run_git(cmd: list[str], cwd: str, env: dict | None = None, timeout: int = _COMMIT_TREE_TIMEOUT) -> subprocess.CompletedProcess:
    """向后兼容 thin wrapper（Stage 4 公共化）。"""
    return run_git(cmd, cwd, env, timeout)


def _get_current_branch(root: str) -> str | None:
    """获取当前分支名（用于 update-ref）。"""
    r = _run_git(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=root)
    if r.returncode != 0:
        return None
    branch = r.stdout.strip()
    # detached HEAD 时返回 "HEAD"，无法 update-ref
    if branch == "HEAD":
        return None
    return branch


def _get_head_sha(root: str) -> str | None:
    """获取当前 HEAD SHA（作为 commit-tree 的 parent）。"""
    r = _run_git(["git", "rev-parse", "HEAD"], cwd=root)
    if r.returncode != 0:
        return None
    return r.stdout.strip()


def _normalize_files(files: list[str], root: Path) -> list[tuple[Path, str]]:
    """归一化文件列表为 [(abs_path, rel_path), ...]。

    - 绝对路径直接用，相对路径相对 root 解析
    - 验证文件存在
    - rel_path 用 forward slash（git index 规范）
    """
    result: list[tuple[Path, str]] = []
    for f in files:
        p = Path(f)
        if not p.is_absolute():
            p = (root / f).resolve()
        if not p.exists():
            raise FileNotFoundError(f"文件不存在: {p}")
        rel = p.relative_to(root).as_posix()
        result.append((p, rel))
    return result


def emergency_commit(
    files: list[str],
    message: str,
    session_id: str,
    project_root: str | Path | None = None,
    reason: str = "",
    trigger_reconcilers: bool = True,
    scenario: str = "production",
) -> EmergencyCommitResult:
    """紧急提交通道：用 git commit-tree 绕过所有 hook。

    适用场景：GitCommitGateway 锁死 / POST-COMMIT-GUARD 反复 reset / P0 紧急修复。
    禁止用于常规提交或绕过 gate 检查。

    治理可见性（治本 vs 裸 commit-tree）：
      1. commit message 添加 [GW:{session_id}:emergency] 标记
      2. commit message 添加 [SCENARIO:{scenario}] 标记（P1-3 治本，dogfood 豁免）
      3. 持久化到 reconcile_execution_log（action='emergency_commit'）
      4. 写审计报告到 .runtime/reconcile_reports/emergency_commit_*.json
      5. 可选触发 post-commit reconciler 链路（默认触发）

    技术实现：
      - 临时 index（GIT_INDEX_FILE=<temp>）原子化多文件提交
      - git read-tree HEAD → git hash-object -w <file> → git update-index --add --cacheinfo
      - git write-tree → git commit-tree <tree> -p HEAD -F <msg> → git update-ref
      - 完全不触发 git hook（plumbing 命令特性）

    Args:
        files: 要提交的文件列表（绝对路径或相对项目根的路径）。
        message: commit message（不含 [GW:] 标记，本函数自动添加）。
        session_id: session 标识（用于审计和 [GW:] 标记）。
        project_root: 项目根目录（默认 REPO_ROOT）。
        reason: 紧急提交原因（写入 reconcile_execution_log，便于事后审计）。
        trigger_reconcilers: 是否触发 post-commit reconciler（默认 True）。
            emergency 提交绕过了 post-commit hook，reconciler 不会自动触发。
            设为 True 时手动调用 reconciler 链路补齐。设为 False 跳过（速度优先）。
        scenario: 场景标签（P1-3 治本，#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）。
            可选值：production（默认，计入滥用监控）/ dogfood / test / governance_fix。
            abuse_monitor 只统计 scenario=production 的 emergency_commit，
            避免治本工作 dogfood 污染 24h 滥用计数。

    Returns:
        EmergencyCommitResult TypedDict，``ok`` 字段是判定成败的唯一入口。
    """
    root = Path(project_root) if project_root else REPO_ROOT
    root = root.resolve()

    # #ARCH-HEARTBEAT-001 P1-5 + P1-2 治本（#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）：
    # 成本递增门禁检查——按 agent_id 分桶（跨 session 持久），而非 session_id
    # N>=3 需显式 reason，N>=5 阻断提交（强制调查根因）
    bucket_id = _agent_bucket_id(root)
    allowed, escalation_error = _check_emergency_escalation(root, bucket_id, reason)
    if not allowed:
        return {
            "ok": False,
            "session_id": session_id,
            "status": "FAILED",
            "commit_hash": "",
            "error": f"emergency cost escalation blocked: {escalation_error}",
            "files_count": len(files),
        }

    # 输入校验
    if not files:
        return {
            "ok": False,
            "session_id": session_id,
            "status": "FAILED",
            "commit_hash": "",
            "error": "empty files list",
            "files_count": 0,
        }
    if not session_id:
        return {
            "ok": False,
            "session_id": "",
            "status": "FAILED",
            "commit_hash": "",
            "error": "session_id required for audit trail",
            "files_count": len(files),
        }

    # 归一化文件路径 + 存在性校验
    try:
        norm_files = _normalize_files(files, root)
    except FileNotFoundError as e:
        return {
            "ok": False,
            "session_id": session_id,
            "status": "FAILED",
            "commit_hash": "",
            "error": str(e),
            "files_count": len(files),
        }

    # 获取当前分支和 HEAD SHA
    branch = _get_current_branch(str(root))
    if not branch:
        return {
            "ok": False,
            "session_id": session_id,
            "status": "FAILED",
            "commit_hash": "",
            "error": "无法获取当前分支（detached HEAD？），emergency_commit 需要 branch ref",
            "files_count": len(norm_files),
        }
    parent_sha = _get_head_sha(str(root))
    if not parent_sha:
        return {
            "ok": False,
            "session_id": session_id,
            "status": "FAILED",
            "commit_hash": "",
            "error": "无法获取 HEAD SHA",
            "files_count": len(norm_files),
        }

    # 临时 index 文件（原子化多文件提交，不污染主 index）
    tmp_index = tempfile.NamedTemporaryFile(
        prefix="emergency_index_", suffix=".tmp", delete=False, dir=str(root / ".git")
    )
    tmp_index.close()
    tmp_index_path = tmp_index.name

    # commit message 临时文件（避免 PowerShell 特殊字符问题，RULE-TWENTY 裁定2）
    # P1-3 治本（#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）：
    # 追加 [SCENARIO:{scenario}] 标记，abuse_monitor 按 scenario 过滤——
    # 只统计 scenario=production 的 emergency_commit，dogfood/test/governance_fix 豁免
    gw_marker = f"[GW:{session_id}:emergency]"
    scenario_marker = f"[SCENARIO:{scenario}]"
    full_message = f"{message}\n\n{gw_marker}\n{scenario_marker}"
    if reason:
        full_message += f"\n\nEmergency reason: {reason}"
    tmp_msg = tempfile.NamedTemporaryFile(
        prefix="emergency_msg_", suffix=".txt", delete=False, mode="w",
        encoding="utf-8", dir=str(root / ".git"),
    )
    tmp_msg.write(full_message)
    tmp_msg.close()
    tmp_msg_path = tmp_msg.name

    try:
        # #ARCH-WORKTREE-BASE-FRESHNESS-001 Phase 2.1: workspace vs HEAD consistency check (warn-only)
        try:
            _warn_files = []
            for _abs, _rel in norm_files:
                _diff_r = _run_git(["git", "diff", "--quiet", "HEAD", "--", _rel], cwd=str(root), timeout=10)
                if _diff_r.returncode == 1:
                    _warn_files.append(_rel)
            if _warn_files:
                logger.warning("emergency_commit: 主工作区文件与 HEAD 不一致: %s", _warn_files)
                try:
                    _ops_log = root / ".runtime" / "worktree_ops_log.jsonl"
                    _ops_log.parent.mkdir(parents=True, exist_ok=True)
                    import json as _j
                    import time as _t
                    with open(_ops_log, "a", encoding="utf-8") as _f:
                        _f.write(_j.dumps({"ts": _t.time(), "session_id": session_id, "stage": "emergency_commit", "event": "workspace_head_diff", "files": _warn_files}, ensure_ascii=False) + "\n")
                except OSError:
                    pass
        except Exception as _bf_err:
            logger.debug("emergency_commit: base consistency check failed (non-blocking): %s", _bf_err)

        # Step 1: 临时 index 读取 HEAD tree
        env_index = {"GIT_INDEX_FILE": tmp_index_path}
        r = _run_git(
            ["git", "read-tree", "HEAD"],
            cwd=str(root), env=env_index, timeout=30,
        )
        if r.returncode != 0:
            return {
                "ok": False, "session_id": session_id, "status": "FAILED",
                "commit_hash": "", "error": f"git read-tree HEAD failed: {r.stderr.strip()}",
                "branch": branch, "files_count": len(norm_files),
            }

        # Step 2: 逐文件 hash-object + update-index
        for abs_path, rel_path in norm_files:
            # hash-object -w：写入 object store，返回 SHA
            r = _run_git(
                ["git", "hash-object", "-w", "--", str(abs_path)],
                cwd=str(root), timeout=_HASH_OBJECT_TIMEOUT,
            )
            if r.returncode != 0:
                return {
                    "ok": False, "session_id": session_id, "status": "FAILED",
                    "commit_hash": "", "error": f"git hash-object failed for {rel_path}: {r.stderr.strip()}",
                    "branch": branch, "files_count": len(norm_files),
                }
            blob_sha = r.stdout.strip()

            # update-index --add --cacheinfo：添加到临时 index
            # --add 必须用于新文件（不在 HEAD tree 中的文件）
            # 100644 = normal file mode
            r = _run_git(
                ["git", "update-index", "--add", "--cacheinfo",
                 f"100644,{blob_sha},{rel_path}"],
                cwd=str(root), env=env_index, timeout=30,
            )
            if r.returncode != 0:
                return {
                    "ok": False, "session_id": session_id, "status": "FAILED",
                    "commit_hash": "", "error": f"git update-index failed for {rel_path}: {r.stderr.strip()}",
                    "branch": branch, "files_count": len(norm_files),
                }

        # Step 3: write-tree（从临时 index 创建 tree object）
        r = _run_git(
            ["git", "write-tree"],
            cwd=str(root), env=env_index, timeout=30,
        )
        if r.returncode != 0:
            return {
                "ok": False, "session_id": session_id, "status": "FAILED",
                "commit_hash": "", "error": f"git write-tree failed: {r.stderr.strip()}",
                "branch": branch, "files_count": len(norm_files),
            }
        tree_sha = r.stdout.strip()

        # Step 4: commit-tree（创建 commit object，不触发任何 hook！）
        r = _run_git(
            ["git", "commit-tree", tree_sha, "-p", parent_sha, "-F", tmp_msg_path],
            cwd=str(root), timeout=_COMMIT_TREE_TIMEOUT,
        )
        if r.returncode != 0:
            return {
                "ok": False, "session_id": session_id, "status": "FAILED",
                "commit_hash": "", "error": f"git commit-tree failed: {r.stderr.strip()}",
                "branch": branch, "files_count": len(norm_files),
            }
        commit_sha = r.stdout.strip()

        # Step 5: update-ref（更新分支指针到新 commit）
        # 这是 plumbing 命令，不触发 hook
        # #ARCH-WORKTREE-BASE-FRESHNESS-001 Phase 2.2: reflog message for audit traceability
        _reflog_msg = f"emergency_commit: {session_id} reason={reason or 'unspecified'}"
        r = _run_git(
            ["git", "update-ref", "-m", _reflog_msg, f"refs/heads/{branch}", commit_sha, parent_sha],
            cwd=str(root), timeout=30,
        )
        if r.returncode != 0:
            return {
                "ok": False, "session_id": session_id, "status": "FAILED",
                "commit_hash": "", "error": f"git update-ref failed: {r.stderr.strip()}",
                "branch": branch, "files_count": len(norm_files),
            }

        # Step 6: 治理可见性——持久化到 reconcile_execution_log + 审计报告
        try:
            log_emergency_commit(
                project_root=root,
                session_id=session_id,
                commit_sha=commit_sha,
                branch=branch,
                files=[rel for _, rel in norm_files],
                reason=reason or "unspecified",
                message=full_message,
            )
        except Exception as e:  # noqa: BLE001 — 审计日志失败不阻断 commit
            logger.warning("emergency_commit: log_emergency_commit failed: %s", e)

        # Step 7: 可选触发 reconciler 链路
        if trigger_reconcilers:
            try:
                _trigger_reconcilers_safely(root, session_id, commit_sha,
                                            [rel for _, rel in norm_files])
            except Exception as e:  # noqa: BLE001 — reconciler 失败不阻断 commit
                logger.warning("emergency_commit: reconciler trigger failed: %s", e)

        # 短 SHA（前 10 位）
        short_sha = commit_sha[:10]
        logger.info(
            "emergency_commit: OK commit=%s branch=%s files=%d session=%s",
            short_sha, branch, len(norm_files), session_id,
        )
        # #ARCH-HEARTBEAT-001 P1-5 + P1-2 治本：成功后递增计数（按 agent bucket）
        # N+1 >= 5 时设置 block_next_start=True（阻断下次 session_worktree_start）
        try:
            new_count = _increment_emergency_count(root, bucket_id)
        except Exception as e:  # noqa: BLE001 — 计数失败不阻断 commit
            logger.warning("emergency_commit: increment count failed: %s", e)
            new_count = -1
        return {
            "ok": True,
            "session_id": session_id,
            "status": "OK",
            "commit_hash": short_sha,
            "branch": branch,
            "files_count": len(norm_files),
            "emergency_count": new_count,
        }

    except subprocess.TimeoutExpired as e:
        return {
            "ok": False, "session_id": session_id, "status": "FAILED",
            "commit_hash": "", "error": f"git command timeout: {e}",
            "branch": branch, "files_count": len(norm_files),
        }
    finally:
        # 清理临时文件
        for tmp in (tmp_index_path, tmp_msg_path):
            try:
                os.unlink(tmp)
            except OSError:
                pass


def _trigger_reconcilers_safely(
    root: Path,
    session_id: str,
    commit_sha: str,
    rel_files: list[str],
) -> None:
    """手动触发 post-commit reconciler 链路（补齐被绕过的 hook）。

    emergency_commit 绕过了 post-commit hook，reconciler 不会自动触发。
    本函数手动调用 reconciler 链路，对标 GitCommitGateway._run_post_commit_reconcile。

    失败不抛异常（reconciler 失败不阻断 emergency commit，已持久化到 DB）。
    """
    # 延迟导入避免循环依赖
    try:
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway
        from zephyr.governance.audit.reconciliation_registry import (
            ReconciliationRegistry,
        )
    except ImportError as e:
        logger.warning("emergency_commit: cannot import reconciler modules: %s", e)
        return

    try:
        gateway = GitCommitGateway(project_root=root)
        # _run_post_commit_reconcile 是内部方法，但 emergency 场景需要补齐
        # 对标 session_worktree.py:1852 的 _run_post_commit_reconcile 调用
        abs_files = [str(root / f) for f in rel_files]
        # 构造一个 minimal CommitResult 供 reconciler 使用
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
            CommitResult,
            CommitStatus,
        )
        result = CommitResult(
            status=CommitStatus.OK,
            message=f"emergency_commit {commit_sha[:10]}",
            commit_hash=commit_sha[:10],
        )
        gateway._run_post_commit_reconcile(abs_files, session_id, result, commit_message="")
        logger.info("emergency_commit: reconciler chain triggered for %s", commit_sha[:10])
    except Exception as e:  # noqa: BLE001 — reconciler 失败不阻断
        logger.warning("emergency_commit: reconciler chain failed: %s", e)
