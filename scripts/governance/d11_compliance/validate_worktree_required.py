# [BLUEPRINT] MOD-INF-005 | scripts/governance/d11_compliance/validate_worktree_required.py | §gate-worktree-required
# [MODULE] scripts.governance.d11_compliance.validate_worktree_required
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d11_compliance.__init__
# [CONSUMERS] .pre-commit-config.yaml (GATE-WORKTREE-REQUIRED hook)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] worktree 内 commit 放行；主工作区 commit warn（exit 0）+ 计数；单 session 累计 >= 阈值升级阻断（exit 1）；合并提交放行；reconciler auto-commit 放行
# [MODIFY-GUARD] _THRESHOLD 阈值；计数文件路径
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=放行/warn; exit 1=阈值超限阻断; exit 2=脚本错误
# [TESTS] tests/scripts/test_validate_worktree_required.py
# [A_module] module_id=MOD-INF-005 | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""validate_worktree_required.py — GATE-WORKTREE-REQUIRED 门禁（L3.1）

#ARCH-GIT-SELF-HARM-GUARD L3.1（2026-08-04）

将 AGENTS.md RULE-WORKTREE 从"君子协定"升级为"软门禁"。

治本动机
--------
100% AI 开发场景下，多 session 共享主工作区 git index，并发 reset/commit 导致
工作区修改被覆盖（reflog 19 次 reset --hard）。session_worktree 物理隔离是治本
方向（独立 worktree + 独立 index），但 AGENTS.md RULE-WORKTREE 只是文档君子协定，
AI 可忽略。

本 hook 将君子协定升级为渐进式软门禁:
  1. worktree 内 commit → 放行（鼓励行为）
  2. 主工作区 commit → warn（exit 0，不阻断）+ 计数到 worktree_skip.jsonl
  3. 单 session 累计 >= 5 次 → 升级为阻断（exit 1）

为什么不直接硬阻断？
  - reconciler auto-commit 等合法场景需主工作区 commit（AGENTS.md 豁免条款）
  - 首次 warn 教育而非惩罚，渐进收紧避免误伤
  - 阈值机制容忍偶发主工作区 commit，但阻止系统性忽略 worktree

已知局限（L3.2 方向性）
  - GitCommitGateway 用 --no-verify 绕过所有 pre-commit hooks，本 hook 无法
    拦截 gateway 路径的主工作区 commit。完整覆盖需 L3.2 在 check_protected_paths
    或 gateway 内部增加 worktree 上下文检查。

对标: validate_commit_gateway.py（gate-commit-gw 拦截裸 commit）
区别: 本脚本检测 worktree 使用率（软门禁），非 commit 路径（硬门禁）

exit codes: 0=放行/warn, 1=阈值超限阻断, 2=脚本错误
"""

from __future__ import annotations

__manifest__ = """
args: []
description: GATE-WORKTREE-REQUIRED门禁——主工作区commit warn+计数，累计>=5次升级阻断
dimensions:
- D11
priority: P2
timeout_seconds: 5
warn_only: true
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

# sys.path 必须在 from _shared 导入之前设置
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS  # noqa: E402

# 单 session 主工作区 commit 容忍阈值（超过则升级为阻断）
_THRESHOLD = 5  # noqa: gate-vocab  gate-vocab豁免: worktree 跳过容忍阈值（脚本专用非系统阈值）

# 计数日志路径（相对 project_root）
_SKIP_LOG_REL = Path(".runtime") / "gate_audit" / "worktree_skip.jsonl"

# session_id env（与 git_guard.py SESSION_ID_ENV 对齐）
_SESSION_ID_ENV = "ZEPHYR_SESSION_ID"

# reconciler auto-commit 标记（主工作区合法 commit 场景）
_RECONCILER_ENV = "ZEPHYR_RECONCILER_AUTO_COMMIT"


def _get_project_root() -> Path:
    """获取 git 仓库根目录。"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except Exception:  # noqa: BLE001 — fail-open
        pass
    return Path.cwd()


def _is_merge_commit() -> bool:
    """检测当前是否为合并提交（.git/MERGE_HEAD 存在）。"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return False
        git_dir = Path(result.stdout.strip())
        return (git_dir / "MERGE_HEAD").exists()
    except Exception:  # noqa: BLE001 — fail-open
        return False


def _is_session_worktree() -> bool:
    """检测当前 cwd 是否在 session worktree 内（.aidrafts/sess-* 路径）。

    对标 validate_commit_gateway.py:_is_session_worktree_commit 的检测逻辑。
    """
    cwd = Path(os.getcwd()).resolve()
    parts = cwd.parts
    for i, part in enumerate(parts):
        if part == ".aidrafts" and i + 1 < len(parts) and parts[i + 1].startswith("sess-"):
            return True
    return False


def _is_reconciler_auto_commit() -> bool:
    """检测是否为 reconciler auto-commit（合法的主工作区 commit 场景）。

    reconciler 自动提交（如 manifest 重生成、blueprint 同步）在主工作区执行，
    属 AGENTS.md 豁免条款。设 ZEPHYR_RECONCILER_AUTO_COMMIT=1 标记放行。
    """
    return os.environ.get(_RECONCILER_ENV) == "1"


def _get_session_id() -> str:
    """获取当前 session_id（用于 per-session 计数）。"""
    return os.environ.get(_SESSION_ID_ENV, "unknown")


def _read_skip_count(project_root: Path, session_id: str) -> int:
    """读取指定 session 的累计 skip 次数。"""
    skip_log = project_root / _SKIP_LOG_REL
    if not skip_log.exists():
        return 0
    count = 0
    try:
        with skip_log.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if rec.get("session_id") == session_id:
                    count += 1
    except OSError:  # noqa: BLE001 — fail-open
        pass
    return count


def _write_skip_record(project_root: Path, session_id: str) -> None:
    """追加一条 skip 记录到计数日志。"""
    skip_log = project_root / _SKIP_LOG_REL
    try:
        skip_log.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": int(time.time()),
            "session_id": session_id,
            "cwd": str(Path(os.getcwd()).resolve()),
        }
        with skip_log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:  # noqa: BLE001 — 计数失败不阻断 commit
        print("[GATE-WORKTREE-REQUIRED] 计数日志写入失败（非阻断）", file=sys.stderr)


def main() -> int:
    """Entry point: 检测 worktree 使用率，渐进式软门禁。"""
    # 合并提交放行
    if _is_merge_commit():
        return EXIT_PASS

    # worktree 内 commit 放行（鼓励行为）
    if _is_session_worktree():
        return EXIT_PASS

    # reconciler auto-commit 放行（合法主工作区场景）
    if _is_reconciler_auto_commit():
        return EXIT_PASS

    project_root = _get_project_root()
    session_id = _get_session_id()

    # 循环审计 R1 治本（2026-08-19）：unknown 桶永不升级阻断——
    # ZEPHYR_SESSION_ID 缺失的来源=git merge 触发的 hooks（merge commit 无 session env）
    # 与手动 pre-commit run（审计/基线跑批），两者都不是"系统性忽略 worktree"的
    # 可归因行为；unknown 桶计数只增不减会永久毒化（merge 批打爆阈值后所有手动
    # 全量跑恒 BLOCKED，2026-08-19 基线实证）。可识别 session 的渐进升级语义不变。
    if session_id == "unknown":
        print(
            "GATE-WORKTREE-REQUIRED: WARN — 主工作区操作（无 session 归因，merge hook/手动跑批场景），不升级阻断",
            file=sys.stderr,
        )
        return EXIT_PASS

    count = _read_skip_count(project_root, session_id)

    # 阈值超限 → 升级为阻断
    if count >= _THRESHOLD:
        print(
            f"GATE-WORKTREE-REQUIRED: BLOCKED — 主工作区 commit 累计 {count} 次"
            f"（阈值 {_THRESHOLD}），session={session_id}\n"
            "  根因: 多 AI session 共享主工作区 git index，并发 reset/commit 导致修改被覆盖\n"
            "  治本: 使用 session_worktree 物理隔离\n"
            "  正确方式:\n"
            "    from zephyr.gov_enforcement.rule_bridge.session_worktree import "
            "session_worktree_start\n"
            "    session_worktree_start(session_id, files=[...])\n"
            f"  如确需主工作区 commit（reconciler 等）: 设 {_RECONCILER_ENV}=1",
            file=sys.stderr,
        )
        return EXIT_FINDINGS

    # 未超阈值 → warn（exit 0，不阻断）+ 计数
    _write_skip_record(project_root, session_id)
    print(
        f"GATE-WORKTREE-REQUIRED: WARN — 主工作区 commit（非 worktree 隔离），"
        f"session={session_id}, 累计 {count + 1}/{_THRESHOLD}\n"
        "  建议: 使用 session_worktree 物理隔离避免并发冲突\n"
        f"  累计达 {_THRESHOLD} 次后将升级为硬阻断",
        file=sys.stderr,
    )
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
