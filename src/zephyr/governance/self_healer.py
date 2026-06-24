# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §3.1 Stage 7
# [MODULE] zephyr.governance.semantic_audit.self_healer
# [DOMAIN] D-GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] FixPrioritizer; AuditOrchestrator (MOD-INF-027)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 修复→自测→回滚闭环; 禁止修改 frozen/immutable_core 文件; 原子写入 tmp+replace
# [MODIFY-GUARD] semantic-auditor/blueprint.md; semantic-auditor/__init__.py __all__
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SelfHealError
# [TESTS] tests/semantic-auditor/test_self_healer.py
# [A_module] module_id=MOD-SEM_self_healer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""[BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic-auditor/blueprint.md

Stage 7 自愈闭环 — 修复→自测→回滚.

=============================================

蓝图 §3.1 组件 #7 · SelfHealer

依赖: LLMBridge (接口注入), Rollback System (MOD-INF-021), AuditTrail (MOD-INF-020)

数据流: 修复文本+目标文档 → Stage 7 自愈闭环 → HealResult

八步工作流:
  Step 1: 安全边界检查 — 解析 [STABILITY]/[AI_AUTONOMY] 头部, frozen/immutable_core 禁止修改
  Step 2: Checkpoint 创建 — 通过 RollbackHandler 或 git stash 保存当前文件状态
  Step 3: 修复内容获取 — LLMBridge 生成或直接传入 fix_suggestion
  Step 4: 原子写入修复 — temp-file + os.replace, 失败自动清理 tmp
  Step 5: 自测验证 — 非空检查 + py_compile 语法验证(.py 文件)
  Step 6: 验证通过 → 返回 HealResult(success=True)
  Step 7: 验证失败 → 执行回滚(RollbackHandler.restore 或 git checkout)
  Step 8: 回滚结果 → 返回 HealResult(success=False, rollback_applied=...)
"""

from __future__ import annotations

import logging
import os
import re
import subprocess
from typing import Any, Protocol, runtime_checkable

from zephyr.governance.semantic_audit.models import HealResult, LLMFixResult

logger = logging.getLogger(__name__)

__all__ = [
    "HealResult",
    "IssueAggregatorProtocol",
    "LLMBridgeProtocol",
    "RollbackHandlerProtocol",
    "SelfHealError",
    "SelfHealer",
]


class SelfHealError(Exception):
    """自愈闭环异常基类."""


# --- Protocol 骨架（升级为 @runtime_checkable 公开接口） ---


@runtime_checkable
class IssueAggregatorProtocol(Protocol):
    """Stage 5 问题聚合器接口 — 蓝图 §3.1 组件 #5."""

    def get_aggregated_issues(self) -> list[dict[str, Any]]: ...


@runtime_checkable
class LLMBridgeProtocol(Protocol):
    """Stage 6 LLM 桥接接口 — 蓝图 §3.1 组件 #6."""

    def generate_fix(self, issue: dict[str, Any]) -> LLMFixResult: ...


@runtime_checkable
class RollbackHandlerProtocol(Protocol):
    """回滚处理器接口 — MOD-INF-021 Rollback System."""

    def checkpoint(self, target_path: str) -> bool: ...
    def restore(self, target_path: str) -> bool: ...


# --- 安全边界常量 ---

_FORBIDDEN_STABILITY = frozenset({"frozen"})
_FORBIDDEN_AUTONOMY = frozenset({"immutable_core"})

_HEADER_RE = re.compile(
    r"^(?:#\s*)?\[(STABILITY|AI_AUTONOMY)\]\s*(.+)$",
    re.MULTILINE,
)


def _parse_header_field(content: str, field: str) -> str | None:
    """解析文件头部 [FIELD] value 标记."""
    for match in _HEADER_RE.finditer(content):
        if match.group(1) == field:
            return match.group(2).strip()
    return None


def _is_modification_allowed(target_path: str) -> tuple[bool, str]:
    """Step 1: 安全边界检查 — 解析文件头部, 判断是否允许修改."""
    if not os.path.isfile(target_path):
        return True, ""
    try:
        with open(target_path, encoding="utf-8") as f:
            head = f.read(4096)
    except OSError as exc:
        return False, f"无法读取文件头部: {exc}"
    stability = _parse_header_field(head, "STABILITY")
    if stability and stability in _FORBIDDEN_STABILITY:
        return False, f"[STABILITY]={stability} 禁止修改"
    autonomy = _parse_header_field(head, "AI_AUTONOMY")
    if autonomy and autonomy in _FORBIDDEN_AUTONOMY:
        return False, f"[AI_AUTONOMY]={autonomy} 禁止修改"
    return True, ""


class SelfHealer:
    """Stage 7 自愈闭环 — 修复→自测→回滚.

    八步工作流:
      Step 1: 安全边界检查
      Step 2: Checkpoint 创建
      Step 3: 修复内容获取
      Step 4: 原子写入修复
      Step 5: 自测验证
      Step 6: 验证通过 → success
      Step 7: 验证失败 → 回滚
      Step 8: 回滚结果 → 最终判定
    """

    def __init__(
        self,
        issue_aggregator: IssueAggregatorProtocol | None = None,
        llm_bridge: LLMBridgeProtocol | None = None,
        rollback_handler: RollbackHandlerProtocol | None = None,
    ) -> None:
        self._aggregator = issue_aggregator
        self._llm_bridge = llm_bridge
        self._rollback_handler = rollback_handler

    def heal(
        self,
        target_path: str,
        issue_description: str,
        fix_suggestion: str = "",
    ) -> HealResult:
        """执行单文件自愈闭环.

        Args:
            target_path: 目标文件路径
            issue_description: 问题描述
            fix_suggestion: 修复建议文本（可选，为空时通过 LLMBridge 获取）

        Returns:
            HealResult: 自愈结果
        """
        # Step 1: 安全边界检查
        allowed, deny_reason = _is_modification_allowed(target_path)
        if not allowed:
            logger.warning("自愈被安全边界拒绝: %s — %s", target_path, deny_reason)
            return HealResult(
                success=False,
                reason=f"安全边界拒绝: {deny_reason}",
                rollback_applied=False,
            )

        # Step 2: Checkpoint 创建
        if self._rollback_handler is not None:
            cp_ok = self._rollback_handler.checkpoint(target_path)
            if not cp_ok:
                return HealResult(
                    success=False,
                    reason="checkpoint 创建失败, 中止修复",
                    rollback_applied=False,
                )

        # Step 3: 修复内容获取
        fix_content = fix_suggestion
        if not fix_content and self._llm_bridge is not None:
            llm_result = self._llm_bridge.generate_fix({"target_path": target_path, "issue": issue_description})
            if llm_result.success and llm_result.fix_text:
                fix_content = llm_result.fix_text
            else:
                logger.warning("LLM Bridge 生成修复失败: %s", llm_result.error)
        if not fix_content:
            return HealResult(
                success=False,
                reason="无修复内容可用",
                rollback_applied=False,
            )

        # Step 4: 原子写入修复
        apply_ok = self._apply_fix(target_path, fix_content)
        if not apply_ok:
            return HealResult(
                success=False,
                reason="修复写入失败",
                rollback_applied=False,
            )

        # Step 5: 自测验证
        verify_ok = self._verify_fix(target_path)

        # Step 6: 验证通过
        if verify_ok:
            logger.info("自愈成功: %s", target_path)
            return HealResult(success=True, reason="修复并验证通过", rollback_applied=False)

        # Step 7: 验证失败 → 回滚
        logger.warning("自愈验证失败, 执行回滚: %s", target_path)
        rollback_ok = self._rollback(target_path)

        # Step 8: 回滚结果
        if rollback_ok:
            return HealResult(
                success=False,
                reason="修复后验证失败, 已回滚",
                rollback_applied=True,
            )
        return HealResult(
            success=False,
            reason="修复后验证失败且回滚失败, 需人工介入",
            rollback_applied=False,
        )

    def heal_with_llm_result(
        self,
        llm_fix: LLMFixResult,
        target_file: str,
    ) -> HealResult:
        """使用 LLMFixResult 执行自愈闭环 — 蓝图 §3.2 数据流 #7.

        Args:
            llm_fix: Stage 6 LLM Bridge 产出的修复结果
            target_file: 目标文件路径

        Returns:
            HealResult: 自愈结果
        """
        if not llm_fix.success or not llm_fix.fix_text:
            return HealResult(
                success=False,
                reason=f"LLM 修复文本不可用: {llm_fix.error}",
                rollback_applied=False,
            )
        return self.heal(target_file, issue_description="", fix_suggestion=llm_fix.fix_text)

    def batch_heal(self, issues: list[dict[str, Any]]) -> list[HealResult]:
        """批量自愈 — 逐文件执行闭环.

        Args:
            issues: 每个元素需包含 target_path, 可选 issue_description/fix_suggestion

        Returns:
            list[HealResult]: 每个文件的自愈结果
        """
        results: list[HealResult] = []
        for issue in issues:
            target_path = issue.get("target_path", "")
            issue_description = issue.get("issue_description", issue.get("issue", ""))
            fix_suggestion = issue.get("fix_suggestion", issue.get("fix", ""))
            if not target_path:
                results.append(HealResult(success=False, reason="缺少 target_path", rollback_applied=False))
                continue
            result = self.heal(target_path, issue_description, fix_suggestion)
            results.append(result)
        return results

    def _apply_fix(self, target_path: str, fix_content: str) -> bool:
        """Step 4: 原子写入修复 — temp-file + os.replace."""
        tmp_path = f"{target_path}.{os.getpid()}.tmp"
        try:
            os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(fix_content)
            os.replace(tmp_path, target_path)
            logger.debug("原子写入完成: %s", target_path)
            return True
        except PermissionError:
            logger.error("写入权限不足: %s", target_path)
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except OSError:
                pass
            return False
        except OSError as exc:
            logger.error("写入失败: %s — %s", target_path, exc)
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except OSError:
                pass
            return False

    def _verify_fix(self, target_path: str) -> bool:
        """Step 5: 自测验证 — 非空检查 + py_compile 语法验证."""
        if not os.path.isfile(target_path):
            return False
        try:
            with open(target_path, encoding="utf-8") as f:
                content = f.read()
            if not content.strip():
                logger.warning("验证失败: 文件为空 — %s", target_path)
                return False
        except OSError as exc:
            logger.warning("验证失败: 无法读取 — %s — %s", target_path, exc)
            return False
        if target_path.endswith(".py"):
            try:
                result = subprocess.run(
                    [
                        "python",
                        "-c",
                        f"import py_compile; py_compile.compile(r'{target_path}', doraise=True)",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode != 0:
                    logger.warning("语法验证失败: %s — %s", target_path, result.stderr.strip())
                    return False
            except subprocess.TimeoutExpired:
                logger.warning("语法验证超时: %s", target_path)
                return False
            except OSError as exc:
                logger.warning("语法验证异常: %s — %s", target_path, exc)
                return False
        logger.debug("验证通过: %s", target_path)
        return True

    def _rollback(self, target_path: str) -> bool:
        """Step 7: 回滚 — RollbackHandler.restore 或 git checkout."""
        if self._rollback_handler is not None:
            return self._rollback_handler.restore(target_path)
        try:
            result = subprocess.run(
                ["git", "checkout", "--", target_path],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                logger.info("git checkout 回滚成功: %s", target_path)
                return True
            logger.warning("git checkout 回滚失败: %s — %s", target_path, result.stderr.strip())
            return False
        except subprocess.TimeoutExpired:
            logger.error("git checkout 回滚超时: %s", target_path)
            return False
        except OSError as exc:
            logger.error("git checkout 回滚异常: %s — %s", target_path, exc)
            return False
