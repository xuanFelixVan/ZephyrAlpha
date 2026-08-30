# [BLUEPRINT] MOD-INF-029 | docs/03_modules/_cross_layer/orphan_judge/blueprint.md | §6.4
# [MODULE] zephyr.security.access_control.orphan_judge.kb_bridge
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.intelligence.model_evaluation.unified_memory_api
# [CONSUMERS] orphan-judge.__main__._cmd_report; report_generator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不实现KB逻辑; 仅桥接UnifiedMemoryAPI.write()+search()
# [MODIFY-GUARD] UnifiedMemoryAPI API变更时同步此桥接
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 桥接失败返回 False
# [TESTS] tests/orphan-judge/test_kb_bridge.py
# [A_module] module_id=MOD-INF-029 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: kb_bridge.py
# 层: 算法
# - id: A1
#   name_zh: ① KbBridge
#   name_en: KbBridge
#   intro: class KbBridge 源码 L55-L100
#   desc: 公共方法（定义序）: write_judgment, search_history, is_available；源码 L55-L100
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: KbBridge
#   downstream: orphan-judge.__main__._cmd_report; report_generator
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["KbBridge"]


class KbBridge:
    def __init__(self) -> None:
        self._api = None
        self._available = False
        try:
            from zephyr.intelligence.model_evaluation.unified_memory_api import build_provenance, get_unified_memory_api

            self._api = get_unified_memory_api()
            self._build_prov = build_provenance
            self._available = True
        except ImportError:
            logger.warning("UnifiedMemoryAPI not available")
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("UnifiedMemoryAPI init failed: %s", exc, exc_info=True)

    def write_judgment(self, file_path: str, verdict: str, reason: str) -> bool:
        if not self._available or self._api is None:
            return False
        try:
            prov = self._build_prov(origin="orphan-judge", audit_chain=["judgment"])
            content = f"orphan_judge判决: {file_path} -> {verdict}: {reason}"
            self._api.write(topic="orphan-judge", content=content, provenance=prov)
            return True
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.error("KbBridge.write_judgment failed: %s", exc, exc_info=True)
            return False

    def search_history(self, query: str, k: int = 10) -> list[dict[str, Any]]:
        if not self._available or self._api is None:
            return []
        try:
            records = self._api.search(query=query, k=k)
            return [
                {
                    "topic": getattr(r, "topic", ""),
                    "content": getattr(r, "content", ""),
                    "chunk_id": getattr(r, "chunk_id", ""),
                }
                for r in records
            ]
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.error("KbBridge.search_history failed: %s", exc, exc_info=True)
            return []

    def is_available(self) -> bool:
        return self._available
