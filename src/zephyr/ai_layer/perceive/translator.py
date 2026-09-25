# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_perceive
# [MODULE] zephyr.ai_layer.perceive.translator
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
# [DEPENDENCIES] zephyr.ai_layer.perceive.search_orders (SearchOrderJournal/SearchOrder);
#                zephyr.ai_layer.perceive.source_registry (SourceRegistry, 可选注入);
#                zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] 内监五通道事件源（E6 衰减认证器/E9 归因/月度偏离/堵点本/feedback_loop Detector 族
#             ——接线=调用方把探测器信号包成 DetectorSignal 注入 translate，本件零定时器零轮询）;
#             tests/ai_layer/perceive/test_translator.py（合成信号注入）
# [STARTUP] event_driven
# [MATURITY] new
# [INVARIANTS] 翻译器只开单不执行（执行=L2 起的收集链，DESIGN §2.2 接线纪律②）;
#              同矿脉冷却期 30 天防重复开单（§2.2 合并节流：E6 认证线与顾问线同 vein 共享冷却）;
#              全部任务单共享每日预算（§2.3 budget+§2.1② 总量闸 40/日），内监开单优先级高于节拍
#              （beat/manual 不得动用内监保留底 DETECTOR_RESERVE_FLOOR）;
#              内监零定时器——全部挂既有事件源（§2.2 接线纪律①），本件无任何自轮询;
#              trigger=l7_prior/手动路径不在本件射程（l7_prior 挂起=施工项 9，解锁待 L7 定稿）;
#              禁 datetime.now()/time.time()，一律 now_utc（可注入）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L1_perceive/DESIGN.md §2.2（接线图）+§2.3（schema）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未知通道→SearchOrderError（fail-closed，拼错通道绝不静默吞信号）;
#                  冷却期内同矿脉→返回 skipped_cooldown（不开单，留痕原因，非异常）;
#                  共享预算不足→返回 refused_budget（不开单，留痕原因，非异常）;
#                  keyword 派生缺方向键→只落通道基础关键词组（不失败——信号贫信息也要留开单痕）
# [TESTS] tests/ai_layer/perceive/test_translator.py（五通道各注入合成信号→正确开单且 vein/关键词
#         正确/decay_cause 四向枚举映射/E6 认证线+顾问线合并节流（同矿脉冷却期生效）/
#         共享预算扣减正确+beat 不得动用内监保留底/预算耗尽拒单留痕/未知通道拒）
"""translator — L1 内监接线件：探测器信号 → 定向搜索任务单（施工项 6）。

设计真源：``docs/_working/ai_layer_vision/L1_perceive/DESIGN.md`` §2.2（内部信号接线图）+
§2.3（任务单 schema）。五通道全部是**已建件**的信号，本件是纯翻译层：把标准化后的
``DetectorSignal`` 翻译成矿脉定向的任务单并登记进 ``SearchOrderJournal``——

======================  ==================================  ==========================
通道（channel）          信号源（在档路径见 DESIGN §2.2）      矿脉（vein_id/family）
======================  ==================================  ==========================
strategy_decay          E6 认证器+顾问线（合并节流）          VEIN-FAC-E6 / E6
e9_attribution          E9 实盘归因（MOD-PF-007）            VEIN-FAC-E9 / E9
monthly_deviation       sim_deviation 月度偏离（MOD-BT-092）  VEIN-FAC-E7 / E7
commit_block            堵点本（commit_block_events.jsonl）   VEIN-GOV-COMMIT-GATES / governance
feedback_loop           feedback_loop Detector 族             VEIN-FB-DETECTORS / feedback_loop
======================  ==================================  ==========================

commit_block/feedback_loop 两通道的矿脉派生自治理骨架与 AI 层骨架（DESIGN §2.5"真源三件"
之治理骨架），非 strategy_production_map 节点——vein_family 相应取 governance/feedback_loop。
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Final

from zephyr.ai_layer.perceive.search_orders import (
    SearchOrder,
    SearchOrderDraft,
    SearchOrderError,
    SearchOrderJournal,
)
from zephyr.ai_layer.perceive.source_registry import SourceRegistry
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

__all__: Final = [
    "CHANNEL_VEINS",
    "COOLDOWN_DAYS",
    "DETECTOR_PRIORITY",
    "DETECTOR_RESERVE_FLOOR",
    "BEAT_PRIORITY",
    "DEFAULT_DAILY_BUDGET",
    "DEFAULT_STATE_DIR",
    "DetectorSignal",
    "TranslateOutcome",
    "BudgetLedger",
    "PerceiveTranslator",
]

DEFAULT_STATE_DIR: Final = REPO_ROOT / ".runtime" / "ai_layer" / "perceive" / "search_orders"
COOLDOWN_DAYS: Final = 30                 # §2.2：同矿脉冷却期 30 天防重复开单
DEFAULT_DAILY_BUDGET: Final = 40          # §2.1② 总量闸：全注册表每日进漏斗候选 ≤40
DETECTOR_RESERVE_FLOOR: Final = 8         # 内监保留底：beat/manual 不得动用（20% 总量闸）
DETECTOR_PRIORITY: Final = 1.5            # 内监开单优先级高于节拍（beat=1.0）
BEAT_PRIORITY: Final = 1.0

#: 五通道 → 矿脉定向表（vein_id, vein_family, 基础关键词组）。值域见本模块 docstring 表。
CHANNEL_VEINS: Final[dict[str, tuple[str, str, tuple[str, ...]]]] = {
    "strategy_decay": (
        "VEIN-FAC-E6", "E6",
        ("策略衰减 定向搜索", "strategy decay monitoring"),
    ),
    "e9_attribution": (
        "VEIN-FAC-E9", "E9",
        ("实盘归因 改进机制", "performance attribution improvement"),
    ),
    "monthly_deviation": (
        "VEIN-FAC-E7", "E7",
        ("模拟盘偏离 修正机制", "sim live deviation reconciliation"),
    ),
    "commit_block": (
        "VEIN-GOV-COMMIT-GATES", "governance",
        ("同类堵点 业界解法", "workflow bottleneck industry practice"),
    ),
    "feedback_loop": (
        "VEIN-FB-DETECTORS", "feedback_loop",
        ("告警治理 SLO 实践", "alert governance SLO practice"),
    ),
}

#: E6 decay_cause 四向枚举 → 关键词组（DESIGN §2.2 原文映射；tech 为 map FAC-E6 枚举第 5 值，
#: DESIGN 未给方向，按"执行/工程基础设施"外扩展并在此留痕）。
DECAY_DIRECTION_KEYWORDS: Final[dict[str, tuple[str, ...]]] = {
    "crowding": ("同类因子拥挤度监控", "factor crowding monitoring"),
    "regime": ("regime 切换检测", "regime switching detection"),
    "overfitting": ("泛化护栏 PBO DSR 后继", "deflated Sharpe PBO generalization guard"),
    "tech": ("交易执行工程 基础设施", "trading execution infrastructure"),
    "depletion": ("该机制族替代品", "alpha mechanism family replacement"),
}

#: 月度偏离 breach 指标 → 关键词组（DESIGN §2.2：成交价偏差→执行/滑点；一致率低→更稳变体；
#: 漏单率高→数据/触发行新做法。键=sim_deviation_report 的指标名）。
DEVIATION_DIRECTION_KEYWORDS: Final[dict[str, tuple[str, ...]]] = {
    "gap_rel": ("执行 滑点建模新方法", "execution slippage modeling"),
    "signal_agree": ("该策略机制更稳变体", "robust strategy mechanism variant"),
    "missed_rate": ("数据 触发行 新做法", "data trigger signal coverage practice"),
}

#: feedback_loop Detector 族 kind → 关键词组（DESIGN §2.2：flapping/轨迹异常/heisenbug 三向）。
FEEDBACK_DIRECTION_KEYWORDS: Final[dict[str, tuple[str, ...]]] = {
    "flapping": ("告警治理 SLO 实践", "alert governance SLO practice"),
    "trajectory": ("agent 安全 评测新方法", "agent safety evaluation"),
    "heisenbug": ("测试隔离 确定性实践", "test isolation determinism practice"),
}


@dataclass(frozen=True)
class DetectorSignal:
    """内监信号的标准化信封（调用方把探测器输出包成此对象注入 translate）。

    attributes 按通道携带方向键：strategy_decay→decay_cause（crowding/regime/overfitting/
    tech/depletion）；monthly_deviation→breach_kind（gap_rel/signal_agree/missed_rate）；
    e9_attribution→style_family（风格/因子族名）；commit_block→gate_id；
    feedback_loop→detector_kind（flapping/trajectory/heisenbug/…）。
    """

    channel: str
    signal_name: str
    trigger_ref: str
    occurred_at: datetime
    attributes: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class TranslateOutcome:
    """translate 的三态结果（opened / skipped_cooldown / refused_budget），留痕不抛异常。"""

    action: str
    reason: str
    vein_id: str
    order: SearchOrder | None = None


class BudgetExhaustedError(Exception):
    """共享预算不足（内部信号；translate 捕获后转为 refused_budget 留痕）。"""


class BudgetLedger:
    """共享每日预算台账（§2.3 budget 池；按日落盘 budget_YYYYMMDD.json，幂等原子写）。"""

    def __init__(
        self,
        state_dir: Path | str | None = None,
        *,
        daily_cap: int = DEFAULT_DAILY_BUDGET,
        detector_floor: int = DETECTOR_RESERVE_FLOOR,
    ) -> None:
        self.state_dir: Final = Path(state_dir) if state_dir else DEFAULT_STATE_DIR
        self.daily_cap: Final = int(daily_cap)
        self.detector_floor: Final = int(detector_floor)

    def _ledger_path(self, day_key: str) -> Path:
        return self.state_dir / f"budget_{day_key}.json"

    def _load(self, day_key: str) -> dict[str, Any]:
        path = self._ledger_path(day_key)
        if not path.exists():
            return {"date": day_key, "reserved": 0, "by_order": {}}
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            return {
                "date": str(raw.get("date") or day_key),
                "reserved": int(raw.get("reserved") or 0),
                "by_order": dict(raw.get("by_order") or {}),
            }
        except (json.JSONDecodeError, TypeError, ValueError):
            log.warning("预算台账坏文件按空处理: %s", path)
            return {"date": day_key, "reserved": 0, "by_order": {}}

    def _save(self, day_key: str, ledger: dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        path = self._ledger_path(day_key)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(ledger, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(path)

    def reserved(self, *, now: datetime | None = None) -> int:
        day_key = (now or now_utc()).strftime("%Y%m%d")
        return int(self._load(day_key)["reserved"])

    def remaining(self, *, now: datetime | None = None) -> int:
        return self.daily_cap - self.reserved(now=now)

    def reserve(
        self,
        order_id: str,
        amount: int,
        *,
        detector: bool,
        now: datetime | None = None,
    ) -> None:
        """按单扣减共享预算；越界抛 BudgetExhaustedError（beat/manual 受内监保留底约束）。"""
        if amount <= 0:
            return
        moment = now or now_utc()
        day_key = moment.strftime("%Y%m%d")
        ledger = self._load(day_key)
        ceiling = self.daily_cap if detector else self.daily_cap - self.detector_floor
        if ledger["reserved"] + amount > ceiling:
            raise BudgetExhaustedError(
                f"daily_budget_exhausted: reserved={ledger['reserved']} ask={amount} "
                f"ceiling={ceiling}（detector={detector}）"
            )
        ledger["reserved"] = int(ledger["reserved"]) + amount
        ledger["by_order"][order_id] = int(amount)
        self._save(day_key, ledger)


class PerceiveTranslator:
    """内监翻译器：DetectorSignal → 定向搜索任务单（开单/冷却/共享预算三闸）。"""

    def __init__(
        self,
        journal: SearchOrderJournal,
        *,
        ledger: BudgetLedger | None = None,
        registry: SourceRegistry | None = None,
        now_fn: Any = None,
        detector_priority: float = DETECTOR_PRIORITY,
    ) -> None:
        self.journal: Final = journal
        self.ledger: Final = ledger or BudgetLedger(journal.state_dir)
        self.registry: Final = registry
        self._now_fn: Final = now_fn or now_utc
        self.detector_priority: Final = float(detector_priority)

    # ── 主入口 ────────────────────────────────────────────────────────────

    def translate(self, signal: DetectorSignal, *, now: datetime | None = None) -> TranslateOutcome:
        """信号 → 任务单。三态：opened / skipped_cooldown / refused_budget（留痕不抛）。"""
        target = CHANNEL_VEINS.get(signal.channel)
        if target is None:
            raise SearchOrderError(
                f"未知内监通道: {signal.channel}（白名单={sorted(CHANNEL_VEINS)}）"
            )
        vein_id, vein_family, base_keywords = target
        moment = now or self._now_fn()
        cooled = self._cooldown_hit(vein_id, moment)
        if cooled is not None:
            return TranslateOutcome(
                action="skipped_cooldown",
                reason=f"vein={vein_id} 冷却期内已有任务单 {cooled}（{COOLDOWN_DAYS} 天）",
                vein_id=vein_id,
            )
        keywords = self._derive_keywords(signal, base_keywords)
        expected_cards = 6  # = budget.max_searches 默认（§2.3）；亦是共享预算扣减额
        if self.ledger.remaining(now=moment) < expected_cards:
            return TranslateOutcome(
                action="refused_budget",
                reason=(
                    f"daily_budget_exhausted: remaining={self.ledger.remaining(now=moment)} "
                    f"ask={expected_cards} cap={self.ledger.daily_cap}"
                ),
                vein_id=vein_id,
            )
        order = self.journal.open_draft(
            SearchOrderDraft(
                vein_id=vein_id,
                vein_family=vein_family,
                trigger="detector",
                trigger_ref=signal.trigger_ref,
                keyword_groups=keywords,
                source_scope=self._resolve_source_scope(signal),
                priority=self.detector_priority,
                expected_cards=expected_cards,
                now=moment,
            )
        )
        # 先查余量再落单（check-then-act，单线程 journal 语义与 intake_events 同构），
        # 此处 reserve 不再越界——万一越界属编程错误，让它抛而不是吞。
        self.ledger.reserve(order.order_id, expected_cards, detector=True, now=moment)
        return TranslateOutcome(action="opened", reason="ok", vein_id=vein_id, order=order)

    # ── 内部步骤 ──────────────────────────────────────────────────────────

    def _cooldown_hit(self, vein_id: str, moment: datetime) -> str | None:
        """同矿脉冷却期检查：冷却窗口内任一状态任务单存在即命中，返回挡道单号。"""
        window_start = moment - timedelta(days=COOLDOWN_DAYS)
        for order in self.journal.list_orders():
            if order.vein_id != vein_id or not order.created_at:
                continue
            created = datetime.fromisoformat(order.created_at)
            if created >= window_start:
                return order.order_id
        return None

    def _derive_keywords(self, signal: DetectorSignal, base: tuple[str, ...]) -> list[str]:
        """通道基础词组 + 方向键词组（双语成对；缺方向键只落基础词组，不失败）。"""
        keywords: list[str] = list(base)
        attrs = signal.attributes or {}
        mapping: dict[str, tuple[str, ...]] = {}
        if signal.channel == "strategy_decay":
            mapping = DECAY_DIRECTION_KEYWORDS
            key = attrs.get("decay_cause", "")
        elif signal.channel == "monthly_deviation":
            mapping = DEVIATION_DIRECTION_KEYWORDS
            key = attrs.get("breach_kind", "")
        elif signal.channel == "feedback_loop":
            mapping = FEEDBACK_DIRECTION_KEYWORDS
            key = attrs.get("detector_kind", "")
        elif signal.channel == "e9_attribution":
            family = attrs.get("style_family", "")
            if family:
                keywords.extend((f"{family} 因子族改进机制", f"{family} factor family improvement"))
            return keywords
        else:  # commit_block：gate_id 直接作定向词
            gate_id = attrs.get("gate_id", "")
            if gate_id:
                keywords.extend((f"{gate_id} 同类问题 业界解法", f"{gate_id} industry practice"))
            return keywords
        if key and key in mapping:
            keywords.extend(mapping[key])
        elif key:
            keywords.append(key)
        return keywords

    def _resolve_source_scope(self, signal: DetectorSignal) -> tuple[str, ...]:
        """空=全注册表按轨轮询（§2.3）；显式 scope 逐 slug 对注册表校验（未知 slug 拒单）。"""
        raw = (signal.attributes or {}).get("source_scope", "")
        scope = tuple(s.strip() for s in raw.split(",") if s.strip())
        if scope and self.registry is not None:
            known = self.registry.by_slug()
            unknown = [s for s in scope if s not in known]
            if unknown:
                raise SearchOrderError(f"source_scope 含未知 slug: {unknown}")
        return scope
