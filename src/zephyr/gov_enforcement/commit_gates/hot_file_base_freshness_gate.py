# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.hot_file_base_freshness_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); zephyr.shared.io.file_utils (is_hot_file 热文件判定真源)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__（in_process_gate_registry.yaml 自动注册）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] allow_overlap=True 时直接放行（逃生通道，与 FOREIGN-CHANGE-DETECTION 对齐）；无 session_id 放行；session 无 claim_head 锚点放行（reconciler auto-commit 等未走 claim_files 的路径不阻断）；当前 HEAD==claim_head 放行（无上游推进）；HEAD 已推进但目标热文件在 claim_head..HEAD 区间未被改动放行（上游移动与本 commit 无关）；目标热文件在区间内被上游改动则 BLOCK（本 session 编辑基于陈旧 base）；git 异常 fail-open 不阻断
# [MODIFY-GUARD] gate_id="HOT-FILE-BASE-FRESHNESS"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——run_git/路径解析异常降级 fail-open（passed=True，logger.warning）
# [TESTS] tests/governance/commit_gates/test_hot_file_base_freshness_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
hot_file_base_freshness_gate.py — 热文件 base 新鲜度门禁（HOT-FILE-BASE-FRESHNESS）

2026-08-23 陈旧快照覆写事故治本（与 safe_write_text CAS 文件级防线互补的 git 级防线）。

病根（第一性原理）
-----------------
多 session 共享工作区并发期：session A claim 热注册表文件 X（HEAD=abc），
session B 随后 commit 了 X 的修改（HEAD 推进到 def）。session A 的编辑缓冲区
基于 abc 版本，commit 时工作区 diff 以 def 为 base 结算——A 不知道上游已推进，
自己基于陈旧 base 的修改会把 B 的已提交变更静默回退（陈旧快照覆写）。

既有防线只覆盖部分时序：
- FOREIGN-CHANGE-DETECTION(45)：检测 **claim 时刻** 工作区已脏（未提交外来变更），
  不检测 claim 之后其他 session **已 commit** 导致的 HEAD 推进。
- safe_write_text CAS：检测 **文件写入时刻** 磁盘内容与读取 base 不符，
  不覆盖「读→改→commit」全程磁盘字节未变、但 git HEAD 已推进的场景
  （他 session 从同一磁盘内容 commit 了自己的缓冲区）。

本 gate 在 commit 时对比 claim_files 锚定的 HEAD（claim_head）与当前 HEAD：
HEAD 已推进且目标热文件在 ``claim_head..HEAD`` 区间被上游改动 → 阻断，
强制调用方确认工作区已含上游修改后 release+重新 claim（锚点刷新）再提交。

检测逻辑
--------
- allow_overlap=True → PASS（逃生通道，与 FOREIGN-CHANGE-DETECTION 对齐）
- 无 session_id / session 无 claim_head（未走 claim_files）→ PASS
- 当前 HEAD == claim_head（无上游推进）→ PASS
- HEAD 已推进，逐个检查 commit 目标中的热文件
  （``is_hot_file`` 真源：file_utils.DEFAULT_HOT_FILES）：
  ``git diff --name-only claim_head..HEAD -- <file>`` 非空 → 该文件上游已变 → BLOCK
- git 命令异常 → fail-open（环境异常非违规，对标 SNAPSHOT-DRIFT 设计）

设计权衡
--------
1. **只查热文件**：热文件（双注册表等）是陈旧覆写事故的唯一实证灾区，
   全量文件检查会给正常并发开发（不同 session 改不同文件）带来误报。
2. **文件级精确判定**：HEAD 推进但目标热文件未被上游改动 → PASS——
   避免「他 session commit 了无关文件」误伤本 commit。
3. **fail-open on git error**：git 不可用属环境异常，不阻断 commit 工作流。
4. **priority=47**：在 FOREIGN-CHANGE-DETECTION(45)/DERIVED-FILE(46) 之后、
   COMMIT-SCOPE(48) 之前——先在内容层确认 base 新鲜，再做语义层跨域检测。
5. **与 CAS 分层**：CAS 管写盘瞬间，本 gate 管 commit 瞬间；两层独立失效，
   任一层命中都能阻断覆写（纵深防御）。

Usage::

    from zephyr.gov_enforcement.commit_gates.hot_file_base_freshness_gate import (
        make_hot_file_base_freshness_gate,
    )

    registry.register(make_hot_file_base_freshness_gate())

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: hot_file_base_freshness_gate.py
# 层: 算法
# - id: A1
#   name_zh: ① make_hot_file_base_freshness_gate
#   name_en: make_hot_file_base_freshness_gate
#   intro: 构造热文件 base 新鲜度门禁 GateSpec（硬阻断型）。
#   desc: 构造热文件 base 新鲜度门禁 GateSpec（硬阻断型）。 Returns: GateSpec(gate_id="HOT-FILE-BASE-FRESHNESS", pri…；源码 L155-L211
#   inputs: 无参数
#   outputs: GateSpec
# 层: 输出
# - id: O1
#   name_zh: GateSpec
#   name_en: GateSpec
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec
from zephyr.shared.io.file_utils import is_hot_file

logger = logging.getLogger(__name__)

__all__ = ["make_hot_file_base_freshness_gate"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定，非可变常量，无需Final标注


def _current_head(gateway) -> str:
    """获取当前 HEAD sha；异常/失败返回空串（fail-open 信号）。"""
    try:
        result = gateway.run_git(["git", "rev-parse", "HEAD"])
        if result.returncode == 0:
            return result.stdout.strip()
        logger.warning(
            "HOT-FILE-BASE-FRESHNESS gate fail-open: rev-parse HEAD 失败(rc=%d)。",
            result.returncode,
        )
    except Exception as e:  # noqa: BLE001 — broad exception catch for fail-open
        logger.warning(
            "HOT-FILE-BASE-FRESHNESS gate fail-open: HEAD 获取异常(%s: %s)。",
            type(e).__name__,
            e,
            exc_info=True,
        )
    return ""


def _upstream_touched(gateway, claim_head: str, current_head: str, rel: str) -> bool:
    """判定文件在 claim_head..current_head 区间是否被上游改动；异常返回 False（fail-open）。"""
    try:
        result = gateway.run_git(["git", "diff", "--name-only", f"{claim_head}..{current_head}", "--", rel])
        if result.returncode != 0:
            logger.warning(
                "HOT-FILE-BASE-FRESHNESS gate fail-open: diff %s..%s -- %s 失败(rc=%d)。",
                claim_head[:12],
                current_head[:12],
                rel,
                result.returncode,
            )
            return False
        return bool(result.stdout.strip())
    except Exception as e:  # noqa: BLE001 — broad exception catch for fail-open
        logger.warning(
            "HOT-FILE-BASE-FRESHNESS gate fail-open: diff 异常(%s: %s)。",
            type(e).__name__,
            e,
            exc_info=True,
        )
        return False


def make_hot_file_base_freshness_gate() -> GateSpec:
    """构造热文件 base 新鲜度门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="HOT-FILE-BASE-FRESHNESS", priority=47)。
        priority=47——FOREIGN-CHANGE-DETECTION(45)/DERIVED-FILE(46) 之后、
        COMMIT-SCOPE(48) 之前：先确认 base 新鲜（git 层），再做跨域语义检测。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        if kwargs.get("allow_overlap", False):
            # 逃生通道：显式声明放行（与 FOREIGN-CHANGE-DETECTION 对齐）
            return True, ""

        session_id = kwargs.get("session_id", "")
        if not session_id:
            return True, ""

        # 读取 session 的 claim_head 锚点（异常安全降级为无锚点 → PASS）
        try:
            claim_head = gateway.claim_heads.get(session_id, "")
        except Exception:  # noqa: BLE001 — broad exception catch for fail-open
            claim_head = ""
        if not claim_head:
            # 未走 claim_files（reconciler auto-commit 等）→ 不阻断
            return True, ""

        current_head = _current_head(gateway)
        if not current_head or current_head == claim_head:
            return True, ""  # git 异常 fail-open / 无上游推进

        # HEAD 已推进——仅当 commit 目标热文件在区间内被上游改动才阻断
        repo_root = Path(str(gateway.project_root))
        stale: list[str] = []
        for f in files:
            try:
                abs_f = os.path.abspath(f)
                if not is_hot_file(Path(abs_f), repo_root):
                    continue
                rel = os.path.relpath(abs_f, str(repo_root)).replace("\\", "/")
            except (ValueError, OSError):
                continue
            if _upstream_touched(gateway, claim_head, current_head, rel):
                stale.append(rel)

        if stale:
            return False, (
                f"目标热文件在 claim 后被上游 commit 修改（STALE_BASE_VIOLATION）: "
                f"{sorted(stale)}. claim_head={claim_head[:12]} 已推进到 HEAD={current_head[:12]}，"
                f"本 session 的编辑基于陈旧 base，commit 会覆写上游已提交变更。"
                f"处置：确认工作区文件已包含上游修改（git log -p {claim_head[:12]}..HEAD -- <file> 核对）"
                f"→ release_files 后重新 claim（锚点刷新到新 HEAD）→ 再 commit；"
                f"或确认无误后用 commit(allow_overlap=True) / CLI --allow-overlap 逃生通道。"
            )
        return True, ""

    return GateSpec(gate_id="HOT-FILE-BASE-FRESHNESS", check=_check, priority=47)
