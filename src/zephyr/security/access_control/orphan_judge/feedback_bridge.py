# [BLUEPRINT] MOD-INF-029 | docs/03_modules/_cross_layer/orphan_judge/blueprint.md | §7.1
# [MODULE] zephyr.security.access_control.orphan_judge.feedback_bridge
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS] orphan-judge.judge.OrphanJudge(误判反馈)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 不实现反馈逻辑; 仅桥接FeedbackLoop.analyze_pending()+generate_proposals()
# [MODIFY-GUARD] FeedbackLoop API变更时同步此桥接
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 桥接失败返回空proposals
# [TESTS] tests/orphan-judge/test_feedback_bridge.py
# [A_module] module_id=MOD-SEC_feedback_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
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
            self._loop = FeedbackLoop(storage_path or get_tmp_dir() / "feedback_orphan_judge")
            self._available = True
        except ImportError:
            logger.warning("FeedbackLoop not available")
        except Exception as exc:
            logger.warning("FeedbackLoop init failed: %s", exc, exc_info=True)

    def report_misjudgment(self, file_path: str, actual: str, predicted: str) -> list[dict[str, Any]]:
        if not self._available or self._loop is None:
            return []
        try:
            entry = [
                {
                    "id": file_path.replace("/", "_"),
                    "module": "orphan-judge",
                    "context": f"Misjudgment: {file_path} predicted={predicted} actual={actual}",
                }
            ]
            proposals = self._loop.analyze_pending(entry)
            return [
                {
                    "source": p.source,
                    "pattern": p.pattern,
                    "change": p.suggested_rule_change,
                    "confidence": p.confidence,
                }
                for p in proposals
            ]
        except Exception as exc:
            logger.error("FeedbackBridge.report_misjudgment failed: %s", exc, exc_info=True)
            return []

    def is_available(self) -> bool:
        return self._available