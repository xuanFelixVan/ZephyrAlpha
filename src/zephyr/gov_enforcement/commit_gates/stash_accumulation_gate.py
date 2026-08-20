# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §ARCH-STASH-ACCUMULATION-001
# [MODULE] zephyr.gov_enforcement.commit_gates.stash_accumulation_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.gate_auto_registrar.auto_register_gates
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 阈值检测——git stash list 计数 > 40 block（阻断 commit），> 20 warn（passed=True + detail）；fail-open（git 失败不阻断）；全局状态检测（不依赖 staged files）；每次 commit 都执行（与 stash 累积风险正相关）
# [MODIFY-GUARD] gate_id="STASH-ACCUMULATION"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]; _WARN_THRESHOLD=20 / _BLOCK_THRESHOLD=40
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git stash list 失败降级为 fail-open（passed=True）
# [TESTS]
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""stash_accumulation_gate.py — stash 堆积阈值检测门禁（STASH-ACCUMULATION）

对应裁定 #ARCH-STASH-ACCUMULATION-001（2026-07-21）Phase 4 治本。

病根（第一性原理）
-----------------
100% AI 开发场景下，多 session 并发 + WORKSPACE-CLEAN-CHECK merge 阻断 +
session_worktree_commit 漏列文件检测 = stash 累积。原 reconciler
（make_stash_lifecycle_reconciler）只在 post-commit 清理过期 stash，但：

1. **无前置阻断**：stash 累积到 34 个时才被人工发现，reconciler 只清理过期
   的，无法阻止"活跃 stash 持续累积"的趋势
2. **AI 无感知**：AI 不知道 stash 数量，每次 merge 前继续 stash，导致累积
3. **stash 累积后果**：git 对象存储膨胀 + AI 判断混淆（看到 stash list 以为
   有未提交工作）+ stash pop 误恢复其他 session WIP 覆盖当前工作

治本方案（本 gate，阈值阻断）
------------------------------
1. **> 20 warn**：passed=True + detail 含计数 + 建议（运行 reconciler 清理
   或手动 drop），不阻断 commit 但提醒 AI stash 已堆积
2. **> 40 block**：passed=False 阻断 commit，强制 AI 先清理 stash 再 commit
3. **fail-open**：git stash list 失败不阻断（passed=True），避免 git 临时
   故障卡死所有 commit
4. **每次 commit 都执行**：stash 累积与 AI 活跃正相关，每次 commit 是检测
   的合适时机（git stash list 成本 <0.1s）

设计权衡
--------
1. **block 阈值 40**：实测 34 个 stash 已导致 AI 判断混淆，40 是"必须干预"
   的红线。低于 40 时 warn 让 AI 有机会自愈（运行 reconciler）
2. **warn 阈值 20**：低于 20 是正常范围（活跃 session 各 1-2 个 stash），
   20+ 提醒 AI 注意
3. **priority=118**：在 ISSUE-RESOLVED-INTEGRITY=117 之后，作为基础设施级
   stash 治理 gate（原 113/114/115 均被占用，后到者让位至 118）
4. **不检测 staged files**：本 gate 检测全局 stash 状态，与 staged files
   无关——即使空 commit 也检测（防 stash 累积）

Usage::

    from zephyr.gov_enforcement.commit_gates.stash_accumulation_gate import make_stash_accumulation_gate

    registry.register(make_stash_accumulation_gate())
"""

from __future__ import annotations

import logging

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_stash_accumulation_gate"]

# 阈值（第一性原理：实测 34 个 stash 已致 AI 判断混淆）
_WARN_THRESHOLD = 20  # > 20 提醒（passed=True + detail）
_BLOCK_THRESHOLD = 40  # > 40 阻断（passed=False）


def _count_stash_entries(gateway: object) -> int | None:
    """执行 git stash list 并返回 stash 条目数。

    Args:
        gateway: GitCommitGateway 实例（提供 _run_git + project_root）。

    Returns:
        stash 条目数（int）；git 失败时返回 None（调用方 fail-open）。
    """
    try:
        result = gateway.run_git(["git", "stash", "list"])
        if result.returncode != 0:
            logger.warning(
                "STASH-ACCUMULATION: git stash list failed (rc=%d): %s",
                result.returncode,
                (result.stderr or "").strip()[:200],
            )
            return None
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        return len(lines)
    except Exception as e:  # noqa: BLE001 — fail-open: git 故障不阻断 commit
        logger.warning(
            "STASH-ACCUMULATION: git stash list exception (fail-open): %s",
            e,
            exc_info=True,
        )
        return None


def make_stash_accumulation_gate() -> GateSpec:
    """构造 stash 堆积阈值检测 GateSpec。

    Returns:
        GateSpec(gate_id="STASH-ACCUMULATION", priority=118).
        - stash count > 40: (False, detail) 阻断 commit
        - stash count > 20: (True, detail) warn 不阻断
        - stash count <= 20: (True, "") 通过
        - git 失败: (True, "") fail-open 通过
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        count = _count_stash_entries(gateway)
        if count is None:
            # fail-open: git 故障不阻断 commit
            return True, ""
        if count > _BLOCK_THRESHOLD:
            return False, (
                f"stash 堆积阻断（count={count} > {_BLOCK_THRESHOLD}）："
                f"当前 stash 数量过多，请先清理再 commit。"
                f"建议：1) 运行 ZEPHYR_STASH_LIFECYCLE_AGGRESSIVE=1 触发 reconciler "
                f"清理所有非 user-manual- stash；2) 手动 git stash list 查看 + "
                f"git stash drop stash@{{N}} 清理不需要的 stash；"
                f"3) 确认无活跃 session 需要 pop 后再 commit。"
            )
        if count > _WARN_THRESHOLD:
            return True, (
                f"stash 堆积提醒（count={count} > {_WARN_THRESHOLD}）："
                f"stash 数量偏多，建议清理。"
                f"可运行 ZEPHYR_STASH_LIFECYCLE_AGGRESSIVE=1 触发 reconciler 清理。"
            )
        return True, ""

    return GateSpec(
        gate_id="STASH-ACCUMULATION",
        check=_check,
        priority=118,  # ISSUE-RESOLVED-INTEGRITY=117 之后（原 113/114/115 均被占用，后到者让位）
    )


if __name__ == "__main__":
    # 入口文件标记——让 ORPHAN-MODULE gate 豁免（本 gate 通过 gate_auto_registrar 动态注册）
    _spec = make_stash_accumulation_gate()
    print(f"gate_id={_spec.gate_id}, priority={_spec.priority}")
