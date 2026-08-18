# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.snapshot_drift_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged 修改 data/runtime_violation_snapshot/latest.json 时校验结构完整性 + generated_at 新鲜度（≤24h）+ commit_sha 与 HEAD 一致；任一校验失败则阻断 commit；JSON 解析失败 fail-closed（阻断）；HEAD SHA 获取失败 fail-open（不阻断）；本 gate 自身文件修改豁免
# [MODIFY-GUARD] gate_id="SNAPSHOT-DRIFT"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——IO/JSON/git 异常降级为 fail-open（passed=True，logger.warning），结构校验失败 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_snapshot_drift_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m20-snapshot-drift  M20豁免: 本文件是SNAPSHOT-DRIFT检测器自身,源码引用snapshot路径用于校验,非实际drift
"""snapshot_drift_gate.py — 运行时违规快照漂移阻断门禁（SNAPSHOT-DRIFT，#ARCH-GOV-CONVERGENCE-META Phase 3.6 补齐 rc1 enforceability）

病根（裁定#221，原 ai_first_governance_principles.md §二，文档已删 2026-07-30，git 历史可查）
------------------------------------------------
rc1_static_snapshot: 静态快照未动态更新
M20 metric warn-only 检测 drift，无 commit gate 硬阻断静态快照漂移。
本 gate 在 GitCommitGateway pre-commit 阶段（in-process，``--no-verify`` 绕不过）注册，
强制快照文件提交时通过结构 + 新鲜度 + SHA 一致性校验。

治本方案
--------
当 staged files 含 ``data/runtime_violation_snapshot/latest.json`` 时：
  1. 解析 JSON 结构（fail-closed：解析失败即阻断）
  2. 校验必需字段：generated_at / commit_sha / violations
  3. 校验 generated_at 新鲜度（≤24h，否则视为漂移）
  4. 校验 commit_sha 与当前 HEAD 一致（snapshot 应基于最新 HEAD 生成）

设计权衡
--------
1. **只在快照被提交时触发**：不阻断其他文件提交，避免影响常规工作流。
2. **fail-closed on JSON error**：快照文件提交时若 JSON 异常，说明文件被破坏，应阻断。
3. **fail-open on git error**：HEAD SHA 获取失败属环境异常，不阻断。
4. **priority=40**：在 FILE-PLACEMENT-TTL(33) 之后、DATA-TASK-COMPLETENESS(41) 之前。

Usage::

    from zephyr.gov_enforcement.commit_gates.snapshot_drift_gate import make_snapshot_drift_gate

    registry.register(make_snapshot_drift_gate())
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta, timezone

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_snapshot_drift_gate"]

# 快照文件相对路径（相对仓库根）
_SNAPSHOT_REL_PATH = "data/runtime_violation_snapshot/latest.json"

# 快照必需字段
_REQUIRED_FIELDS = ("generated_at", "commit_sha", "violations")

# generated_at 最大允许新鲜度（小时）
_MAX_FRESHNESS_HOURS = 24


def _is_snapshot_in_staged(gateway) -> tuple[bool, str]:
    """检查快照文件是否在 staged 列表中。

    Returns:
        (in_staged, worktree_root) — in_staged=True 时 worktree_root 为有效路径。
        git 命令异常时返回 (False, "") 并记录 warning。
    """
    try:
        diff_result = gateway.run_git(
            ["git", "diff", "--cached", "--name-only"]
        )
        if diff_result.returncode != 0:
            logger.warning(
                "SNAPSHOT-DRIFT gate fail-open: git diff 失败(rc=%d)。",
                diff_result.returncode,
            )
            return False, ""
        staged_files = diff_result.stdout.strip().splitlines()
    except Exception as e:  # noqa: BLE001 — broad exception catch for fail-open
        logger.warning(
            "SNAPSHOT-DRIFT gate fail-open: git diff 异常(%s: %s)。",
            type(e).__name__, e, exc_info=True,
        )
        return False, ""

    normalized = [f.replace("\\", "/") for f in staged_files]
    if _SNAPSHOT_REL_PATH not in normalized:
        return False, ""

    try:
        toplevel = gateway.run_git(["git", "rev-parse", "--show-toplevel"])
        wt_root = toplevel.stdout.strip() if toplevel.returncode == 0 else str(gateway.project_root)
    except Exception:  # noqa: BLE001 — broad exception catch for fail-open
        wt_root = str(gateway.project_root)

    return True, wt_root


def _validate_snapshot_structure(data: object) -> list[str]:
    """校验快照 JSON 结构，返回错误列表（空列表=通过）。"""
    errors: list[str] = []
    if not isinstance(data, dict):
        errors.append("snapshot root is not a JSON object")
        return errors
    for field in _REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"missing required field: {field}")
    return errors


def _validate_generated_at_freshness(gen_at: object) -> str:
    """校验 generated_at 新鲜度，返回错误消息（空字符串=通过）。"""
    if not isinstance(gen_at, str):
        return f"generated_at is not a string: {type(gen_at).__name__}"
    try:
        # 兼容 ISO 8601 + 时区后缀（含 Z）
        normalized = gen_at.replace("Z", "+00:00")
        ts = datetime.fromisoformat(normalized)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        age = datetime.now(timezone.utc) - ts
        if age > timedelta(hours=_MAX_FRESHNESS_HOURS):
            hours_old = age.total_seconds() / 3600
            return (
                f"generated_at is stale ({hours_old:.1f}h old, "
                f"max {_MAX_FRESHNESS_HOURS}h) — snapshot drift"
            )
        if age < timedelta(seconds=-60):
            return "generated_at is in the future (clock skew or tampering)"
    except ValueError as e:
        return f"generated_at invalid ISO timestamp: {e}"
    return ""


def _get_head_sha(gateway) -> str | None:
    """获取当前 HEAD SHA；失败返回 None（fail-open 信号）。"""
    try:
        result = gateway.run_git(["git", "rev-parse", "HEAD"])
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:  # noqa: BLE001 — broad exception catch for fail-open
        logger.warning(
            "SNAPSHOT-DRIFT gate fail-open: HEAD SHA 获取异常(%s: %s)。",
            type(e).__name__, e, exc_info=True,
        )
    return None


def _validate_commit_sha(snapshot_sha: object, head_sha: str | None) -> str:
    """校验 commit_sha 一致性，返回错误消息（空字符串=通过）。

    head_sha 为 None 时跳过校验（fail-open on git error）。
    """
    if head_sha is None:
        return ""  # fail-open
    if not isinstance(snapshot_sha, str):
        return f"commit_sha is not a string: {type(snapshot_sha).__name__}"
    # snapshot.commit_sha 可能是 12-char short SHA 或 40-char full SHA
    if snapshot_sha != head_sha and not head_sha.startswith(snapshot_sha):
        return (
            f"commit_sha drift: snapshot={snapshot_sha} vs HEAD={head_sha[:12]}... "
            f"(snapshot was generated against a different commit)"
        )
    return ""


def make_snapshot_drift_gate() -> GateSpec:
    """构造运行时违规快照漂移阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="SNAPSHOT-DRIFT", priority=63)。
        priority=63——避开 33-42 区间（FILE-PLACEMENT-TTL/CH-*/RENAME-DEPGRAPH-SYNC/DATA-TASK/ENCODING），
        在 RECONCILER-HEALTH(64) 之前、RULE-EXECUTION-PAIRING(65) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 检查快照文件是否 staged
        in_staged, wt_root = _is_snapshot_in_staged(gateway)
        if not in_staged:
            return True, ""

        # 2. 读取快照文件内容
        abs_path = os.path.join(wt_root, _SNAPSHOT_REL_PATH.replace("/", os.sep))
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            return False, (
                f"snapshot file 读取失败({type(e).__name__}: {e}) — "
                f"无法验证 drift"
            )

        # 3. 解析 JSON（fail-closed：解析失败即阻断）
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            return False, (
                f"snapshot JSON 解析失败(line {e.lineno} col {e.colno}): {e.msg} — "
                f"快照文件结构破坏"
            )

        # 4. 校验必需字段
        errors = _validate_snapshot_structure(data)
        if errors:
            return False, (
                f"snapshot 结构校验失败: {'; '.join(errors)}"
            )

        # 5. 校验 generated_at 新鲜度
        gen_err = _validate_generated_at_freshness(data.get("generated_at"))
        if gen_err:
            return False, f"snapshot generated_at 漂移: {gen_err}"

        # 6. 校验 commit_sha 一致性
        head_sha = _get_head_sha(gateway)
        sha_err = _validate_commit_sha(data.get("commit_sha"), head_sha)
        if sha_err:
            return False, f"snapshot commit_sha 漂移: {sha_err}"

        return True, ""

    return GateSpec(gate_id="SNAPSHOT-DRIFT", check=_check, priority=63)
