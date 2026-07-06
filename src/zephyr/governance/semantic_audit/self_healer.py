# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §3.1 Stage 7
# [MODULE] zephyr.governance.semantic_audit.self_healer
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] FixPrioritizer; AuditOrchestrator (MOD-INF-027)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 修复→自测→回滚闭环; 禁止修改 frozen/immutable_core 文件; 原子写入 tmp+replace
# [MODIFY-GUARD] semantic-auditor/blueprint.md; semantic-auditor/__init__.py __all__
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SelfHealError
# [TESTS] tests/semantic-auditor/
# [A_module] module_id=MOD-GOV_self_healer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic-auditor/blueprint.md

Stage 7 自愈闭环 — 修复→自测→回滚.

=============================================

蓝图 §3.1 组件 #7 · SelfHealer

依赖: LLMBridge (接口注入), Rollback System (MOD-INF-021), AuditTrail (MOD-INF-020)

数据流: 修复文本+目标文档 → Stage 7 自愈闭环 → HealResult

"""

from __future__ import annotations

import logging
import os
import re
import subprocess
from typing import Any, Protocol

from pydantic import BaseModel

logger = logging.getLogger(__name__)


__all__ = [
    "HealResult",
    "SelfHealError",
    "SelfHealer",
]


class SelfHealError(Exception):
    """自愈闭环异常基类."""
    error_code = "ZA-GV-0034"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class HealResult(BaseModel):
    success: bool
    reason: str = ""
    rollback_applied: bool = False


class _IssueAggregatorProtocol(Protocol):
    def get_aggregated_issues(self) -> list[dict[str, Any]]: ...


class _LLMBridgeProtocol(Protocol):
    def generate_fix(self, issue: dict[str, Any]) -> str: ...


class _RollbackHandlerProtocol(Protocol):
    def checkpoint(self, target_path: str) -> bool: ...
    def restore(self, target_path: str) -> bool: ...


_FORBIDDEN_STABILITY = frozenset({"frozen"})
_FORBIDDEN_AUTONOMY = frozenset({"immutable_core"})

_HEADER_RE = re.compile(
    r"^\[(STABILITY|AI_AUTONOMY)\]\s*(.+)$",
    re.MULTILINE,
)


def _parse_header_field(content: str, field: str) -> str | None:
    for match in _HEADER_RE.finditer(content):
        if match.group(1) == field:
            return match.group(2).strip()
    return None


def _is_modification_allowed(target_path: str) -> tuple[bool, str]:
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

    接收 IssueAggregator 的聚合问题和 LLMBridge 的修复建议,
    执行修复(原子写入), 自测验证(import测试), 失败则回滚(git checkout).
    """

    def __init__(
        self,
        issue_aggregator: _IssueAggregatorProtocol | None = None,
        llm_bridge: _LLMBridgeProtocol | None = None,
        rollback_handler: _RollbackHandlerProtocol | None = None,
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
        allowed, deny_reason = _is_modification_allowed(target_path)
        if not allowed:
            logger.warning("自愈被安全边界拒绝: %s — %s", target_path, deny_reason)
            return HealResult(
                success=False,
                reason=f"安全边界拒绝: {deny_reason}",
                rollback_applied=False,
            )
        if self._rollback_handler is not None:
            cp_ok = self._rollback_handler.checkpoint(target_path)
            if not cp_ok:
                return HealResult(
                    success=False,
                    reason="checkpoint 创建失败, 中止修复",
                    rollback_applied=False,
                )
        fix_content = fix_suggestion
        if not fix_content and self._llm_bridge is not None:
            fix_content = self._llm_bridge.generate_fix({"target_path": target_path, "issue": issue_description})
        if not fix_content:
            return HealResult(
                success=False,
                reason="无修复内容可用",
                rollback_applied=False,
            )
        apply_ok = self._apply_fix(target_path, fix_content)
        if not apply_ok:
            return HealResult(
                success=False,
                reason="修复写入失败",
                rollback_applied=False,
            )
        verify_ok = self._verify_fix(target_path)
        if verify_ok:
            logger.info("自愈成功: %s", target_path)
            return HealResult(success=True, reason="修复并验证通过", rollback_applied=False)
        logger.warning("自愈验证失败, 执行回滚: %s", target_path)
        rollback_ok = self._rollback(target_path)
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

    def _apply_fix(self, target_path: str, fix_content: str) -> bool:
        try:
            os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)
            tmp_path = f"{target_path}.{os.getpid()}.tmp"
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
                if "tmp_path" in locals() and os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except OSError:
                pass
            return False

    def _verify_fix(self, target_path: str) -> bool:
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
                # 修复命令注入：原 f-string 插值 target_path 到 python -c 命令字符串，
                # 路径含特殊字符可执行任意命令。改用 -m py_compile + 参数列表传递。
                result = subprocess.run(
                    ["python", "-m", "py_compile", target_path],
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

    def batch_heal(self, issues: list[dict[str, Any]]) -> list[HealResult]:
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
