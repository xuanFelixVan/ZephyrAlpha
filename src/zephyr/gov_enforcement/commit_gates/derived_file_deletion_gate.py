# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.derived_file_deletion_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged 删除受保护派生文件时阻断 commit；allow_derived_deletion=True 时放行（逃生通道）；git diff 不可达 fail-open（不阻断 commit，治标不卡死工作流）；受保护清单为 frozenset，扩展经本模块 _PROTECTED_DERIVED_FILES 追加（P1.5 将迁移至 YAML 真源）
# [MODIFY-GUARD] gate_id="DERIVED-FILE-DELETION-PROTECTION"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed（passed=False）
# [TESTS] tests/governance/commit_gates/test_derived_file_deletion_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-BP-REGISTRY-DELETION-001] P1 治本——GATE-21 守护洞封堵（in-process gate，gateway --no-verify 绕不过）
"""derived_file_deletion_gate.py — 派生文件删除保护门禁（DERIVED-FILE-DELETION-PROTECTION）

治本目标（#ARCH-BP-REGISTRY-DELETION-001 P1）
--------------------------------------------
blueprint_registry.yaml 三次被暂存删除（303fb9c9b2 KB 清理误删 → 8ae1da59f0 回滚 →
本次第三次暂存删除已拦截），每次都导致 20+ 消费方（GAP-2 / SYS-C00 / SYS-C02 等）
静默降级。AGENTS.md 声称"漂移由 GATE-21 守护"，但 GATE-21 是 pre-commit hook
（.pre-commit-config.yaml gate-21-manifest-drift），GitCommitGateway 用 --no-verify
系统性绕过全部 pre-commit hook——GATE-21 对 AI commit 形同虚设（详见
architecture_issue_registry.yaml L3552-3554 失效原因②）。

本 gate 是 **in-process gate**（注册到 CommitGateRegistry，commit() 内 check_all 调度），
gateway 无法绕过。补强 GATE-21（pre-commit，可被 --no-verify 绕过）与
pre_delete_safety_check.py（独立脚本，未接入 commit 流程）双重盲区。

病根（第一性原理）
-----------------
派生文件（blueprint_registry.yaml / path_ownership_map.yaml 等）由 sync 脚本从真源
（blueprint.md frontmatter）自动生成，删除派生文件不影响真源，但会让 20+ 消费方
读不到数据 → 静默返回空集 → 检测失效（GAP-2 把"无合法 blueprint_id"判为合规）。
"删除派生文件"是高破坏低可见操作，必须在 commit 时硬阻断。

检测逻辑
---------
- allow_derived_deletion=True → 放行（逃生通道，调用方负责审计）
- git diff --cached --diff-filter=D 取 staged 删除文件清单
- 与 _PROTECTED_DERIVED_FILES 交集非空 → BLOCK
- git diff 失败/异常 → fail-open（不阻断，治标不卡死工作流）

逃生通道设计
-------------
--allow-derived-deletion CLI 旗标（git_commit.py）→ commit(allow_derived_deletion=True)
→ check_all 透传 → 本 gate 放行。适用于派生文件退库（P3）等合法删除场景。
与 --allow-overlap（搭便车逃生）对称：显式声明 + 留审计痕迹。

受保护清单（P1 硬编码起步）
----------------------------
当前仅含已知删除受害者（blueprint_registry.yaml 3x + path_ownership_map.yaml）。
P1.5 将迁移至 YAML 真源（如 derived_file_protection_list.yaml），从
capability_canonical_file_registry.yaml 的 is_derived 字段派生，避免硬编码漂移。
当前硬编码是 P1 止血的合理代价——清单短、变更频率低、误报风险可控。

Usage::

    from zephyr.gov_enforcement.commit_gates.derived_file_deletion_gate import (
        make_derived_file_deletion_gate,
    )

    registry.register(make_derived_file_deletion_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid,
    #                                  allow_derived_deletion=False, ...)
"""

from __future__ import annotations

import logging
import os

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_derived_file_deletion_gate"]

# 受保护派生文件清单（相对 project_root，正斜杠）。
# P1 硬编码起步——已知删除受害者。P1.5 迁移至 YAML 真源（见模块 docstring）。
# 扩展方式：追加相对路径到此 frozenset。每条均应有对应消费者审计（删除会导致静默降级）。
_PROTECTED_DERIVED_FILES: frozenset[str] = frozenset(
    {
        # 三次删除事故对象（303fb9c9b2/1f172f3224/8ae1da59f0 + 本次第三次），
        # 20+ 消费方（GAP-2/SYS-C00/SYS-C02）读不到 → 静默返回空集 → 检测失效。
        "docs/03_modules/blueprint_registry.yaml",
        # 5710 path claims，path_ownership_reconciler 自动重生成；删除致路径冲突检测失效。
        "docs/03_modules/path_ownership_map.yaml",
    }
)


def _normalize_rel(path: str) -> str:
    """归一化为正斜杠相对路径，与 _PROTECTED_DERIVED_FILES 比对。

    git diff --name-only 输出正斜杠相对路径（POSIX 风格），但 Windows 环境下
    调用方可能传入反斜杠。统一 replace + strip 防漏。
    """
    return path.strip().replace("\\", "/")


def _collect_staged_deletions(gateway) -> set[str] | None:
    """获取 staged 区被删除的文件清单（相对路径，正斜杠）。

    Returns:
        删除文件相对路径集合；git diff 失败/异常返回 None（fail-open）。
    """
    try:
        result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=D"])
        if result.returncode != 0:
            logger.warning(
                "DERIVED-FILE-DELETION-PROTECTION gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                result.returncode,
            )
            return None
        deleted = {_normalize_rel(line) for line in result.stdout.strip().splitlines() if line.strip()}
        return deleted
    except Exception as e:  # noqa: BLE001 — fail-open 不阻断
        logger.warning(
            "DERIVED-FILE-DELETION-PROTECTION gate fail-open: git diff 异常(%s: %s)，检测器失效。",
            type(e).__name__,
            e,
            exc_info=True,
        )
        return None


def make_derived_file_deletion_gate() -> GateSpec:
    """构造派生文件删除保护门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="DERIVED-FILE-DELETION-PROTECTION", priority=46)。
        priority=46——在 FOREIGN-CHANGE-DETECTION(45) 之后、HELD-OVERLAP(50) 之前：
        先检外来变更（搭便车根因），再检派生文件删除（破坏性根因），最后检
        session 持有重叠。三者同属"commit 安全性"层级，46 无冲突。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 逃生通道：显式声明放行（P3 派生文件退库等合法删除场景）
        allow_derived_deletion = kwargs.get("allow_derived_deletion", False)
        if allow_derived_deletion:
            return True, ""

        deleted = _collect_staged_deletions(gateway)
        if deleted is None:
            # fail-open：git diff 不可达，不阻断 commit（治标不卡死工作流）
            return True, ""

        blocked = deleted & _PROTECTED_DERIVED_FILES
        if blocked:
            blocked_sorted = sorted(blocked)
            return False, (
                f"目标派生文件被暂存删除（DERIVED_FILE_DELETION_VIOLATION）: "
                f"{blocked_sorted}. 派生文件真源=物理 blueprint.md frontmatter，"
                f"删除派生文件会导致 20+ 消费方（GAP-2/SYS-C00/SYS-C02）静默降级"
                f"（检测返回空集=误判合规）。如确需删除（如派生文件退库 P3），"
                f"用 commit(allow_derived_deletion=True) 或 CLI --allow-derived-deletion "
                f"逃生通道。或运行 sync_registry_from_blueprints.py --write 恢复派生文件。"
            )
        return True, ""

    return GateSpec(gate_id="DERIVED-FILE-DELETION-PROTECTION", check=_check, priority=46)
