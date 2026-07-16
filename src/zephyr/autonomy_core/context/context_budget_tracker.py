# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.context_budget_tracker
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.shared.infra.observer; zephyr.autonomy_core.__init__; zephyr.shared.events.event_schemas; zephyr.shared.infra.cache
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-CONTEXT_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""ContextBudgetTracker: token budget management with 3-level thresholds.

Tracks token usage per session and emits Observer events when
thresholds are crossed. Uses tiktoken for accurate counting.

Task: T-1-24 | experimental | GLM-5.1
Depends: T-1-04 (Sonnet), T-1-14 (Composer), observer.py

T-V2-006 扩展（experimental）
--------------------------
新增 DocCompressor 注入接口：
- register_doc_compressor(compressor)  — M1 build() 时注入单例
- L2_THROTTLE 事件触发时，事件 payload 追加 compression_suggested=True
- get_doc_compressor()                 — M3 触发器调用入口
"""

from __future__ import annotations

from typing import Final
import logging

logger = logging.getLogger(__name__)

import time
from enum import Enum, unique
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
from threading import RLock
from typing import TYPE_CHECKING, Any

from zephyr.infrastructure.capacity_assurance.token_budget import DEFAULT_CONTEXT_TOKEN_BUDGET
from zephyr.shared.infra.observer import EventType, Observer

if TYPE_CHECKING:
    from zephyr.shared.io.doc_compressor import DocCompressor


@unique
class ContextBudgetLevel(str, Enum):
    L1_WARNING = "budget_l1_warning"
    L2_THROTTLE = "budget_l2_throttle"
    L3_HARD_STOP = "budget_l3_hard_stop"


BudgetLevel = ContextBudgetLevel


DEFAULT_THRESHOLDS: Final[set] = {
    ContextBudgetLevel.L1_WARNING: 0.80,
    ContextBudgetLevel.L2_THROTTLE: 0.90,
    ContextBudgetLevel.L3_HARD_STOP: 0.95,
}


_CONTEXT_RULES_PATH = REPO_ROOT / "config" / "context_rules.yaml"
_context_rules_cache: dict | None = None


def _load_context_rules_yaml() -> dict:
    """从 config/context_rules.yaml 加载上下文管理规则（CT-001 契约兑现）。

    首次调用时加载并缓存；后续调用返回缓存。YAML 不存在时返回空字典，
    ContextBudgetTracker 回退到 DEFAULT_THRESHOLDS。
    """
    global _context_rules_cache
    if _context_rules_cache is not None:
        return _context_rules_cache
    try:
        import yaml as _yaml

        if _CONTEXT_RULES_PATH.exists():
            with _CONTEXT_RULES_PATH.open(encoding="utf-8") as fh:
                data = _yaml.safe_load(fh) or {}
            _context_rules_cache = data
            return data
    except Exception as e:
        logger.warning("suppressed error in context_budget_tracker", exc_info=True)
    _context_rules_cache = {}
    return _context_rules_cache


def get_thresholds_from_yaml() -> dict[ContextBudgetLevel, float] | None:
    """从 context_rules.yaml CTX-001 规则提取阈值。

    Returns
    -------
    dict[ContextBudgetLevel, float] | None
        YAML 中定义的阈值；YAML 不存在或规则缺失时返回 None。
    """
    data = _load_context_rules_yaml()
    for rule in data.get("rules", []):
        if rule.get("id") == "CTX-001" and rule.get("name") == "token_budget_tiers":
            params = rule.get("parameters", {})
            return {
                ContextBudgetLevel.L1_WARNING: params.get("l1_warning_ratio", 0.80),
                ContextBudgetLevel.L2_THROTTLE: params.get("l2_compress_ratio", 0.90),
                ContextBudgetLevel.L3_HARD_STOP: params.get("l3_hard_cutoff_ratio", 0.95),
            }
    return None


class ContextBudgetTracker:
    """Per-session token budget tracker with threshold events.

    Usage::

        bus = Observer()
        tracker = ContextBudgetTracker(bus)  # 默认会话上限 DEFAULT_CONTEXT_TOKEN_BUDGET（8000）
        tracker.count_tokens("some text", session_id="s1")
        tracker.evaluate_budget("s1")

    T-V2-006 DocCompressor 集成（experimental）
    ----------------------------------------
    M1 build() 结束时调用 register_doc_compressor(compressor)，
    之后 evaluate_budget() 在 L2_THROTTLE 触发时在事件 payload 中追加
    compression_suggested=True，供 M3 触发器调度 DocCompressor。
    """

    def __init__(
        self,
        observer: Observer,
        session_limit: int = DEFAULT_CONTEXT_TOKEN_BUDGET,
        thresholds: dict[ContextBudgetLevel, float] | None = None,
    ) -> None:
        self._observer = observer
        self._session_limit = session_limit
        self._thresholds = thresholds or get_thresholds_from_yaml() or DEFAULT_THRESHOLDS
        self._lock = RLock()
        self._sessions: dict[str, dict[str, Any]] = {}
        self._doc_compressor: Any | None = None  # DocCompressor（TYPE_CHECKING 避免循环导入）

    def _get_session(self, session_id: str) -> dict[str, Any]:
        self._cleanup_expired_sessions()
        if session_id not in self._sessions:
            self._sessions[session_id] = {
                "token_count": 0,
                "limit": self._session_limit,
                "triggered_levels": set(),
                "created_at": time.time(),
            }
        return self._sessions[session_id]

    def _cleanup_expired_sessions(self, max_age_seconds: float = 86400.0) -> int:
        now = time.time()
        expired = [sid for sid, s in self._sessions.items() if now - s.get("created_at", 0) > max_age_seconds]
        for sid in expired:
            del self._sessions[sid]
        return len(expired)

    def count_tokens(self, text: str, session_id: str = "default") -> int:
        try:
            import tiktoken

            enc = tiktoken.encoding_for_model("cl100k_base")
            count = len(enc.encode(text))
        except (ImportError, Exception):
            count = len(text) // 4

        with self._lock:
            session = self._get_session(session_id)
            session["token_count"] += count
        return count

    def evaluate_budget(self, session_id: str = "default") -> ContextBudgetLevel:
        with self._lock:
            session = self._get_session(session_id)
            usage = session["token_count"]
            limit = session["limit"]
            ratio = usage / limit if limit > 0 else 0.0

            triggered = ContextBudgetLevel.L1_WARNING
            for level in [
                ContextBudgetLevel.L3_HARD_STOP,
                ContextBudgetLevel.L2_THROTTLE,
                ContextBudgetLevel.L1_WARNING,
            ]:
                threshold = self._thresholds.get(level, 0.0)
                if ratio >= threshold:
                    triggered = level
                    if level not in session["triggered_levels"]:
                        session["triggered_levels"].add(level)
                        payload: dict[str, Any] = {
                            "budget_level": level.value,
                            "session_id": session_id,
                            "usage": usage,
                            "limit": limit,
                            "ratio": round(ratio, 3),
                        }
                        # T-V2-006: L2_THROTTLE 时追加压缩建议标志
                        if level is ContextBudgetLevel.L2_THROTTLE:
                            payload["compression_suggested"] = True
                            payload["doc_compressor_available"] = self._doc_compressor is not None
                        self._observer.emit(EventType.METRIC_EVENT, payload)
                    break

        return triggered

    def get_usage(self, session_id: str = "default") -> dict[str, Any]:
        with self._lock:
            session = self._get_session(session_id)
            usage = session["token_count"]
            limit = session["limit"]
            return {
                "session_id": session_id,
                "token_count": usage,
                "limit": limit,
                "ratio": round(usage / limit, 3) if limit > 0 else 0.0,
                "triggered_levels": [l.value for l in session["triggered_levels"]],
            }

    def reset_session(self, session_id: str = "default") -> None:
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]

    def set_session_limit(self, session_id: str, limit: int) -> None:
        with self._lock:
            session = self._get_session(session_id)
            session["limit"] = limit

    # ------------------------------------------------------------------
    # T-V2-006 DocCompressor 注入接口（experimental 新增）
    # ------------------------------------------------------------------

    def register_doc_compressor(self, compressor: DocCompressor) -> None:
        """注册 DocCompressor 单例（由 M1 build() 调用）。

        注册后，L2_THROTTLE 触发时事件 payload 中
        doc_compressor_available = True，供 M3 触发器查询。

        参数
        ----
        compressor
            DocCompressor 实例；通常由 M1 build() 末尾注入：
                tracker.register_doc_compressor(DocCompressor.instance())
        """
        with self._lock:
            self._doc_compressor = compressor

    def get_doc_compressor(self) -> object | None:
        """返回已注册的 DocCompressor 实例（M3 触发器调用入口）。

        未注册时返回 None（M3 负责处理 None 情况，不抛出异常）。
        """
        with self._lock:
            return self._doc_compressor

    def compress_session_context(
        self,
        text: str,
        session_id: str = "default",
    ) -> str | None:
        """调用已注册的 DocCompressor 压缩文本（便捷方法）。

        未注册 DocCompressor 时返回 None（调用方负责降级处理）。

        参数
        ----
        text
            待压缩的上下文文本。
        session_id
            会话标识（传递给 DocCompressor.compress）。

        返回
        ----
        str | None
            压缩后文本；DocCompressor 未注册时为 None。
        """
        with self._lock:
            compressor = self._doc_compressor
        if compressor is None:
            return None
        return compressor.compress(text, session_id=session_id)


_default_tracker: ContextBudgetTracker | None = None


def handle_compression_needed(payload: dict[str, Any], **context: Any) -> str | None:
    """Module-level entry point for TriggerRouter dispatch.

    Resolves the singleton ContextBudgetTracker and delegates to
    compress_session_context. Returns None when no tracker or
    compressor is registered.
    """
    global _default_tracker
    if _default_tracker is None:
        return None
    text = payload.get("text", "")
    session_id = payload.get("session_id", "default")
    return _default_tracker.compress_session_context(text, session_id=session_id)


def set_default_tracker(tracker: ContextBudgetTracker) -> None:
    """Register the default tracker for trigger dispatch."""
    global _default_tracker
    _default_tracker = tracker
