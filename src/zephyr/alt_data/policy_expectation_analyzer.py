# [BLUEPRINT] MOD-ALT-010 | docs/03_modules/_domain_alt_data/policy_expectation_analyzer/blueprint.md
# [MODULE] zephyr.alt_data.policy_expectation_analyzer
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] 无（分析核心纯内存；statement_source/llm_scorer/review_sink/clock 全注入；源策略语义参照 zephyr.data.policy_registry）
# [CONSUMERS] 运行时装配批（监管表态源绑定 / LLM 打分器绑定 / 预期差信号接人工审核路由与信号漏斗）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 表态三要素非空(statement_id/authority/content)且按statement_id去重幂等; 关键词命中序=词表序、返回按statement_id升序确定性; 事件日历按(event_date,event_id)升序; LLM打分强制[-1,1]闭合校验(越界/NaN/bool/非数值Fail-Closed); ETF快照as_of单调(乱序拒绝，同日同额幂等，同日异额冲突Fail-Closed)，|变动率|≥阈值方记持仓异动; 预期差信号is_inferred恒True(标注推断性质仅作信号输入无下单含义)且必入人工审核队列; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_alt_data/policy_expectation_analyzer/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] PolicyExpectationError(占位 ZA-ALT-UNREGISTERED-POLICY-EXPECTATION)——配置非法(阈值/词表/非callable注入)、statement_source未注入或抓取异常、表态/事件字段非法、未知statement_id、topic空/语料空、llm_scorer未注入/异常/打分越界、ETF快照非法/乱序/冲突、审核销号无匹配时抛
# [TESTS] tests/alt_data/test_policy_expectation_analyzer.py
# [A_module] module_id=MOD-ALT-010 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""



PolicyExpectationAnalyzer — A股政策预期分析器（MOD-ALT-010）。

B5-07096（AUD-DRAFT-001-DIGEST P2 波 P2-W04，CAND-TESTA-026，B5 D-ALT-DATA-16，
canonical 承接 TESTA-013 归并）：监管/交易所**公开表态采集**（注入源）+
**窗口指导关键词库**命中扫描+**政策事件日历**+**LLM 预期倾向打分**（注入
llm，[-1,1] 闭合校验）+**国家队持仓变动识别**（季报公开数据语义：ETF 份额
异动阈值）+**预期差信号输出**（is_inferred 恒 True 标注推断性质，仅作信号
输入，强制入人工审核队列）。

查重分工（蓝图 §0）：policy_registry=数据源采集策略注册（本件仅参照其源语
义，不注册策略）；policy_theme_mapper=政策→主题映射（本件=预期倾向打分与
预期差信号，不做主题映射）；llm_market_interpreter=市场解读 LLM 面（本件
LLM 能力一律注入，不内嵌）；sentiment_engine=情绪聚合（零交集）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: policy_expectation_analyzer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: statement_source 参数
#   fields: 参数 statement_source（无注解）
#   code: policy_expectation_analyzer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: llm_scorer 参数
#   fields: 参数 llm_scorer（无注解）
#   code: policy_expectation_analyzer.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: keyword_library 参数
#   fields: 参数 keyword_library（无注解）
#   code: policy_expectation_analyzer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① PolicyExpectationAnalyzer
#   name_en: PolicyExpectationAnalyzer
#   intro: A股政策预期分析器（表态采集 + 关键词扫描 + 事件日历 + LLM 打分 + 持仓异动 + 审核队列）。
#   desc: A股政策预期分析器（表态采集 + 关键词扫描 + 事件日历 + LLM 打分 + 持仓异动 + 审核队列）。；公共方法（定义序）: collect_statements, statements, scan_window…
#   inputs: clock statement_source llm_scorer keyword_library etf_change_threshol…
#   outputs: 返回值
#   （注：A1 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: PolicyExpectationAnalyzer
#   downstream: 运行时装配批（监管表态源绑定 / LLM 打分器绑定 / 预期差信号接人工审核路由与信号漏斗）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass
from typing import Callable, Final, Iterable

_log = logging.getLogger(__name__)

__all__: Final = [
    "EtfSharesSnapshot",
    "ExpectationSignal",
    "HoldingChange",
    "PolicyEvent",
    "PolicyExpectationAnalyzer",
    "PolicyExpectationError",
    "PolicyStatement",
]


class PolicyExpectationError(Exception):
    """政策预期分析输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-ALT-UNREGISTERED-POLICY-EXPECTATION。
    """


@dataclass(frozen=True)
class PolicyStatement:
    """监管/交易所公开表态（采集产物，frozen）。"""

    statement_id: str
    authority: str
    content: str
    published_at: datetime.datetime


@dataclass(frozen=True)
class PolicyEvent:
    """政策事件日历条目（frozen）。"""

    event_id: str
    event_date: datetime.date
    title: str


@dataclass(frozen=True)
class EtfSharesSnapshot:
    """ETF 份额快照（季报公开数据语义，frozen）。"""

    etf_code: str
    shares: float
    as_of: datetime.date


@dataclass(frozen=True)
class HoldingChange:
    """国家队持仓异动（|份额变动率| ≥ 阈值命中事实，frozen）。"""

    etf_code: str
    previous_shares: float
    current_shares: float
    change_ratio: float
    as_of: datetime.date
    flagged_at: datetime.datetime


@dataclass(frozen=True)
class ExpectationSignal:
    """政策预期差信号（推断性质标注，仅作信号输入，frozen）。"""

    topic: str
    expectation_score: float
    keyword_hits: tuple[str, ...]
    is_inferred: bool
    generated_at: datetime.datetime


class PolicyExpectationAnalyzer:
    """A股政策预期分析器（表态采集 + 关键词扫描 + 事件日历 + LLM 打分 + 持仓异动 + 审核队列）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        statement_source: Callable[[], list[PolicyStatement]] | None = None,
        llm_scorer: Callable[[str], float] | None = None,
        keyword_library: Iterable[str] = (),
        etf_change_threshold: float = 0.10,
        review_sink: Callable[[ExpectationSignal], None] | None = None,
    ) -> None:
        for name, fn in (
            ("clock", clock),
            ("statement_source", statement_source),
            ("llm_scorer", llm_scorer),
            ("review_sink", review_sink),
        ):
            if fn is not None and not callable(fn):
                raise PolicyExpectationError(f"{name} 非 callable")
        if isinstance(etf_change_threshold, bool) or not isinstance(etf_change_threshold, (int, float)):
            raise PolicyExpectationError(f"etf_change_threshold 类型非法: {etf_change_threshold!r}")
        threshold = float(etf_change_threshold)
        if not math.isfinite(threshold) or threshold <= 0.0:
            raise PolicyExpectationError(f"etf_change_threshold 须为正有限值: {etf_change_threshold!r}")
        keywords: list[str] = []
        for kw in keyword_library:
            if not isinstance(kw, str) or not kw:
                raise PolicyExpectationError(f"关键词非法: {kw!r}（须非空 str）")
            if kw not in keywords:
                keywords.append(kw)
        self._clock = clock or datetime.datetime.now
        self._source = statement_source
        self._llm = llm_scorer
        self._review_sink = review_sink
        self._keywords = tuple(keywords)
        self._threshold = threshold
        self._statements: dict[str, PolicyStatement] = {}
        self._events: dict[str, PolicyEvent] = {}
        self._etf: dict[str, EtfSharesSnapshot] = {}
        self._holding_changes: list[HoldingChange] = []
        self._signals: list[ExpectationSignal] = []
        self._review_queue: list[ExpectationSignal] = []

    # ── 表态采集 ──────────────────────────────────────────────────────────

    def collect_statements(self) -> int:
        """采集公开表态：注入源抓取 → 校验 → 按 statement_id 去重落库。"""
        if self._source is None:
            raise PolicyExpectationError("statement_source 未注入（采集源全注入，禁止旁路）")
        try:
            batch = self._source()
        except Exception as exc:
            raise PolicyExpectationError(f"statement_source 抓取异常: {exc}") from exc
        if not isinstance(batch, (list, tuple)):
            raise PolicyExpectationError(f"statement_source 返回类型非法: {type(batch)!r}")
        new_count = 0
        for item in batch:
            if not isinstance(item, PolicyStatement):
                raise PolicyExpectationError(f"表态条目类型非法: {type(item)!r}（须 PolicyStatement）")
            self._validate_statement(item)
            if item.statement_id in self._statements:
                continue  # 幂等去重
            self._statements[item.statement_id] = item
            new_count += 1
        return new_count

    @staticmethod
    def _validate_statement(item: PolicyStatement) -> None:
        for field_name in ("statement_id", "authority", "content"):
            value = getattr(item, field_name)
            if not isinstance(value, str) or not value:
                raise PolicyExpectationError(f"{field_name} 为空")
        if not isinstance(item.published_at, datetime.datetime):
            raise PolicyExpectationError(f"published_at 类型非法: {item.published_at!r}")

    def statements(self) -> tuple[PolicyStatement, ...]:
        """已采集表态（(published_at, statement_id) 升序，确定性）。"""
        return tuple(sorted(self._statements.values(), key=lambda s: (s.published_at, s.statement_id)))

    # ── 窗口指导关键词扫描 ────────────────────────────────────────────────

    def _keyword_hits(self, text: str) -> tuple[str, ...]:
        return tuple(kw for kw in self._keywords if kw in text)

    def scan_window_guidance(self, statement_ids: Iterable[str] | None = None) -> dict[str, tuple[str, ...]]:
        """窗口指导关键词命中扫描（命中序=词表序；返回按 statement_id 升序，仅含命中者）。"""
        if statement_ids is None:
            targets = sorted(self._statements)
        else:
            targets = []
            for sid in statement_ids:
                if sid not in self._statements:
                    raise PolicyExpectationError(f"未知 statement_id: {sid!r}")
                targets.append(sid)
            targets = sorted(set(targets))
        hits: dict[str, tuple[str, ...]] = {}
        for sid in targets:
            matched = self._keyword_hits(self._statements[sid].content)
            if matched:
                hits[sid] = matched
        return hits

    # ── 政策事件日历 ──────────────────────────────────────────────────────

    def add_event(self, event: PolicyEvent) -> None:
        """登记政策事件日历条目。"""
        if not isinstance(event, PolicyEvent):
            raise PolicyExpectationError(f"event 类型非法: {type(event)!r}")
        if not isinstance(event.event_id, str) or not event.event_id:
            raise PolicyExpectationError("event_id 为空")
        if not isinstance(event.title, str) or not event.title:
            raise PolicyExpectationError("title 为空")
        if not isinstance(event.event_date, datetime.date):
            raise PolicyExpectationError(f"event_date 类型非法: {event.event_date!r}")
        if event.event_id in self._events:
            raise PolicyExpectationError(f"event_id 重复: {event.event_id!r}")
        self._events[event.event_id] = event

    def calendar(self, from_date: datetime.date | None = None) -> tuple[PolicyEvent, ...]:
        """事件日历（(event_date, event_id) 升序；from_date 起滤，确定性）。"""
        if from_date is not None and not isinstance(from_date, datetime.date):
            raise PolicyExpectationError(f"from_date 类型非法: {from_date!r}")
        out = [e for e in self._events.values() if from_date is None or e.event_date >= from_date]
        out.sort(key=lambda e: (e.event_date, e.event_id))
        return tuple(out)

    # ── LLM 预期倾向打分 + 预期差信号 ─────────────────────────────────────

    def score_expectation(self, topic: str, text: str | None = None) -> ExpectationSignal:
        """LLM 预期倾向打分：[-1,1] 闭合校验 → 预期差信号入人工审核队列。

        text=None 时按 topic 子串聚合已采集表态语料（(published_at, id) 序）。
        信号 is_inferred 恒 True：标注推断性质，仅作信号输入，无下单含义。
        """
        if not isinstance(topic, str) or not topic:
            raise PolicyExpectationError("topic 为空")
        if text is not None and (not isinstance(text, str) or not text):
            raise PolicyExpectationError("text 为空")
        if self._llm is None:
            raise PolicyExpectationError("llm_scorer 未注入（LLM 能力不内嵌，禁止伪打分）")
        corpus = text if text is not None else self._topic_corpus(topic)
        try:
            raw = self._llm(corpus)
        except Exception as exc:
            raise PolicyExpectationError(f"llm_scorer 打分异常: {exc}") from exc
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise PolicyExpectationError(f"llm_scorer 返回类型非法: {raw!r}")
        score = float(raw)
        if not math.isfinite(score) or score < -1.0 or score > 1.0:
            raise PolicyExpectationError(f"llm_scorer 打分越界 [-1,1] 闭合校验失败: {raw!r}")
        signal = ExpectationSignal(
            topic=topic,
            expectation_score=score,
            keyword_hits=self._keyword_hits(corpus),
            is_inferred=True,
            generated_at=self._clock(),
        )
        self._signals.append(signal)
        self._review_queue.append(signal)
        _log.info("预期差信号: %s score=%.3f（推断性质，入人工审核队列）", topic, score)
        if self._review_sink is not None:
            try:
                self._review_sink(signal)
            except Exception:  # noqa: BLE001 — 审核回调不阻断（蓝图 §1）
                _log.exception("review_sink 回调失败")
        return signal

    def _topic_corpus(self, topic: str) -> str:
        matched = [s for s in self.statements() if topic in s.content]
        if not matched:
            raise PolicyExpectationError(f"topic {topic!r} 无相关表态语料（禁止空语料打分）")
        return "\n".join(s.content for s in matched)

    # ── 国家队持仓变动识别 ────────────────────────────────────────────────

    def register_etf_snapshot(self, snapshot: EtfSharesSnapshot) -> HoldingChange | None:
        """登记 ETF 份额快照：|份额变动率| ≥ 阈值 → 国家队持仓异动。

        as_of 单调：乱序拒绝；同日同额幂等（None）；同日异额冲突 Fail-Closed。
        """
        if not isinstance(snapshot, EtfSharesSnapshot):
            raise PolicyExpectationError(f"snapshot 类型非法: {type(snapshot)!r}")
        if not isinstance(snapshot.etf_code, str) or not snapshot.etf_code:
            raise PolicyExpectationError("etf_code 为空")
        if isinstance(snapshot.shares, bool) or not isinstance(snapshot.shares, (int, float)):
            raise PolicyExpectationError(f"shares 类型非法: {snapshot.shares!r}")
        shares = float(snapshot.shares)
        if not math.isfinite(shares) or shares <= 0.0:
            raise PolicyExpectationError(f"shares 须为正有限值: {snapshot.shares!r}")
        if not isinstance(snapshot.as_of, datetime.date):
            raise PolicyExpectationError(f"as_of 类型非法: {snapshot.as_of!r}")
        previous = self._etf.get(snapshot.etf_code)
        if previous is not None:
            if snapshot.as_of < previous.as_of:
                raise PolicyExpectationError(
                    f"快照乱序拒绝: {snapshot.etf_code!r} as_of {snapshot.as_of} 早于已存 {previous.as_of}"
                )
            if snapshot.as_of == previous.as_of:
                if shares == previous.shares:
                    return None  # 幂等
                raise PolicyExpectationError(f"同日期快照份额冲突: {snapshot.etf_code!r} as_of {snapshot.as_of}")
        change: HoldingChange | None = None
        if previous is not None:
            ratio = (shares - previous.shares) / previous.shares
            if abs(ratio) >= self._threshold:
                change = HoldingChange(
                    etf_code=snapshot.etf_code,
                    previous_shares=previous.shares,
                    current_shares=shares,
                    change_ratio=ratio,
                    as_of=snapshot.as_of,
                    flagged_at=self._clock(),
                )
                self._holding_changes.append(change)
                _log.info("国家队持仓异动: %s 变动率 %.3f", snapshot.etf_code, ratio)
        self._etf[snapshot.etf_code] = EtfSharesSnapshot(
            etf_code=snapshot.etf_code,
            shares=shares,
            as_of=snapshot.as_of,
        )
        return change

    # ── 查询与人工审核队列 ────────────────────────────────────────────────

    def holding_changes(self) -> tuple[HoldingChange, ...]:
        """持仓异动流（检出序，确定性）。"""
        return tuple(self._holding_changes)

    def signals(self) -> tuple[ExpectationSignal, ...]:
        """全部预期差信号（生成序，确定性）。"""
        return tuple(self._signals)

    def pending_review(self) -> tuple[ExpectationSignal, ...]:
        """人工审核队列（入队序，确定性）。"""
        return tuple(self._review_queue)

    def mark_reviewed(self, topic: str, generated_at: datetime.datetime) -> None:
        """人工审核销号：按 (topic, generated_at) 精确匹配（无匹配 → Fail-Closed）。"""
        for index, signal in enumerate(self._review_queue):
            if signal.topic == topic and signal.generated_at == generated_at:
                del self._review_queue[index]
                return
        raise PolicyExpectationError(f"审核队列无匹配信号: topic={topic!r} generated_at={generated_at!r}")
