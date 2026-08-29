# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.alerts.alert_precision_tracker
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.io.paths; zephyr.shared.utils.time_utils
# [CONSUMERS] zephyr.infrastructure.capacity_assurance.modules.__init__ ; zephyr.feedback_loop.auto_evolution
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 记录 append-only 落盘且启动回放可恢复计数; 默认纯内存行为与历史版本一致（既有消费方零破坏）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/shared/alerts/test_alert_precision_tracker.py
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""AlertPrecisionTracker — 告警精度/假阳性计数器（16号文 §4.3 P1-3② 落盘扩展）。

假阳性/告警精度记录从纯内存扩为 append-only 落盘（``.runtime/`` 下 JSONL，
生产落点 ``DEFAULT_PERSIST_PATH``），启动时回放恢复计数。

兼容性契约（既有消费方零破坏）：
- ``AlertPrecisionTracker()`` 无参构造 = 纯内存计数，行为与历史版本完全一致；
- 公开接口签名不变：``record_true_positive`` / ``record_false_positive`` /
  ``record_false_negative`` / ``compute`` / ``metrics``；
- 传入 ``persist_path`` 才启用落盘：每次记录 append 一条 ``{"ts","kind"}``
  JSONL（只增不改），初始化时回放已有记录恢复计数。
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_iso

# 假阳性/告警精度记录生产落点（16号文 §4.3 P1-3②：.runtime/ 下 append-only JSONL）
DEFAULT_PERSIST_PATH: Final[Path] = (
    REPO_ROOT / ".runtime" / "shared" / "alerts" / "alert_precision.jsonl"
)

_KIND_TRUE_POSITIVE: Final[str] = "true_positive"
_KIND_FALSE_POSITIVE: Final[str] = "false_positive"
_KIND_FALSE_NEGATIVE: Final[str] = "false_negative"


@dataclass
class PrecisionMetrics:
    total_alerts: int
    true_positives: int
    false_positives: int
    precision: float
    recall: float


class AlertPrecisionTracker:
    """告警精度/假阳性计数器（可选 append-only 落盘 + 启动回放恢复）。"""

    def __init__(self, persist_path: str | Path | None = None) -> None:
        self._persist_path: Path | None = (
            Path(persist_path) if persist_path is not None else None
        )
        self._true_positives: int = 0
        self._false_positives: int = 0
        self._false_negatives: int = 0
        if self._persist_path is not None:
            self._replay()

    @property
    def persist_path(self) -> Path | None:
        """落盘路径（None = 纯内存模式）。"""
        return self._persist_path

    def record_true_positive(self) -> None:
        self._persist(_KIND_TRUE_POSITIVE)
        self._true_positives += 1

    def record_false_positive(self) -> None:
        self._persist(_KIND_FALSE_POSITIVE)
        self._false_positives += 1

    def record_false_negative(self) -> None:
        self._persist(_KIND_FALSE_NEGATIVE)
        self._false_negatives += 1

    def compute(self) -> PrecisionMetrics:
        total = self._true_positives + self._false_positives
        precision = self._true_positives / total if total > 0 else 0.0
        actual_positives = self._true_positives + self._false_negatives
        recall = self._true_positives / actual_positives if actual_positives > 0 else 0.0
        return PrecisionMetrics(total, self._true_positives, self._false_positives, precision, recall)

    def metrics(self) -> PrecisionMetrics:
        return self.compute()

    # ── append-only 落盘（P1-3②）────────────────────────────────────

    def _persist(self, kind: str) -> None:
        if self._persist_path is None:
            return
        self._persist_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._persist_path, "a", encoding="utf-8") as fh:
            fh.write(
                json.dumps({"ts": now_iso(), "kind": kind}, ensure_ascii=False, separators=(",", ":"))
                + "\n"
            )

    def _replay(self) -> None:
        """启动回放：从 append-only JSONL 恢复计数（单写者假设，不做并发合并）。"""
        assert self._persist_path is not None
        if not self._persist_path.exists():
            return
        with open(self._persist_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                kind = json.loads(line).get("kind")
                if kind == _KIND_TRUE_POSITIVE:
                    self._true_positives += 1
                elif kind == _KIND_FALSE_POSITIVE:
                    self._false_positives += 1
                elif kind == _KIND_FALSE_NEGATIVE:
                    self._false_negatives += 1
