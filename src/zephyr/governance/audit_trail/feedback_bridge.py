# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §12
# [MODULE] zephyr.governance.audit_trail.feedback_bridge
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS] audit-orchestrator.feedback_policy(策略引擎消费反馈)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不实现反馈逻辑; 仅桥接FeedbackLoop.analyze_pending()+generate_proposals()+apply_proposal()
# [MODIFY-GUARD] FeedbackLoop API变更时同步此桥接
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 桥接失败返回空结果
# [TESTS] tests/audit-orchestrator/test_feedback_bridge.py
# [A_module] module_id=MOD-GOV_feedback_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from zephyr.shared.io.paths import get_tmp_dir

logger = logging.getLogger(__name__)

__all__ = ["FeedbackBridge"]


class FeedbackBridge:
    def __init__(self, storage_path: Path | None = None) -> None:
        self._loop = None
        self._available = False
        try:
            from zephyr.feedback_loop import FeedbackLoop

            # 5.133.6 修复：mkdtemp 创建系统临时目录从不清理，改为项目托管临时目录；
            # 同时开放 storage_path 参数支持依赖注入（测试可 mock）
            self._loop = FeedbackLoop(storage_path or get_tmp_dir() / "feedback_audit_trail")
            self._available = True
        except ImportError:
            logger.warning("FeedbackLoop not available")
        except Exception as exc:
            logger.warning("FeedbackLoop init failed: %s", exc, exc_info=True)

    def analyze_audit_findings(self, findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not self._available or self._loop is None:
            return []
        try:
            entries = [
                {
                    "id": f.get("issue_id", str(i)),
                    "module": "audit-orchestrator",
                    "context": f.get("detail", f.get("type", "unknown finding")),
                }
                for i, f in enumerate(findings)
            ]
            proposals = self._loop.analyze_pending(entries)
            return [
                {
                    "proposal_id": p.proposal_id,
                    "source": p.source,
                    "pattern": p.pattern,
                    "change": p.suggested_rule_change,
                    "confidence": p.confidence,
                }
                for p in proposals
            ]
        except Exception as exc:
            logger.error("FeedbackBridge.analyze_audit_findings failed: %s", exc, exc_info=True)
            return []

    def generate_rules(self, pending: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not self._available or self._loop is None:
            return []
        try:
            proposals = self._loop.generate_proposals(pending)
            return [
                {
                    "proposal_id": p.proposal_id,
                    "source": p.source,
                    "pattern": p.pattern,
                    "change": p.suggested_rule_change,
                    "confidence": p.confidence,
                    "status": p.status,
                }
                for p in proposals
            ]
        except Exception as exc:
            logger.error("FeedbackBridge.generate_rules failed: %s", exc, exc_info=True)
            return []

    def apply(self, proposal: dict[str, Any]) -> bool:
        if not self._available or self._loop is None:
            return False
        try:
            from zephyr.feedback_loop import EvolutionProposal

            p = EvolutionProposal(
                source=proposal.get("source", "unknown"),
                pattern=proposal.get("pattern", ""),
                suggested_rule_change=proposal.get("change", ""),
                confidence=proposal.get("confidence", 0.5),
            )
            return self._loop.apply_proposal(p)
        except Exception as exc:
            logger.error("FeedbackBridge.apply failed: %s", exc, exc_info=True)
            return False

    def is_available(self) -> bool:
        return self._available