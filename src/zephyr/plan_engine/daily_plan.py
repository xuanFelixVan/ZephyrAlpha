# [BLUEPRINT] MOD-PLAN-030 | docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §三表3/§六任务3
# [MODULE] zephyr.plan_engine.daily_plan
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.plan_engine.judgment_ledger(一行发射+ULID); zephyr.plan_engine.judgment_settler(_reader_execute
#   注入点单点收口); zephyr.plan_engine.next_day_forecaster(次日概率输入,只 import 其 MODULE_ID——读台账不改编译);
#   zephyr.shared.utils.time_utils(now_utc——SCHEMA-TZ 时钟真源)
# [CONSUMERS] zephyr.plan_engine.scenario_classifier(触发表达式求值器/特征词表/计划装载 复用);
#   zephyr.plan_engine.close_verifier(EOD 日线特征装配 复用); zephyr.strategy_pipeline.pipeline_events(事件挂点
#   maybe_emit_daily_plan——daily_kline SUCCESS 唤醒); judgment_daily_plan 台账; 作战室任务 3（验证昨日计划）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 判定/结算分离（本件只发射判定，结算归 judgment_settler——标准 §一.2）; 触发=事件驱动
#   （daily_kline SUCCESS 唤醒，禁 cron/Timer/sleep-loop——宪法 §9.3）; 业务日真源=行情库（resolve_pf_alloc_
#   trade_date 复用，禁墙钟猜日）; 幂等=plan_date 查重（judgment_daily_plan 按 module_id+inputs_ref LIKE 首键，
#   一生成日至多一计划，重复唤醒零副作用）; plan_date=生成日 G 语义="治理 G 之后第一个交易时段"（禁未来日期
#   键——Friday 计划自然治理 Monday）; 触发表达式=白名单文法 AST 求值（禁 eval/exec——表达式注入面结构性关闭）;
#   场景互斥=build 期结构探针+历史重放双校验（重叠即 ValueError fail-closed 禁发射）; path_prior=历史同条件
#   频率 Laplace 平滑（无场景日不计分母，口径文档化; 样本不足退化均匀先验 fallback 如实标注）; 输入缺席=降级
#   标注（confidence 扣减，禁编造也禁跳过式静默）
# [MODIFY-GUARD] blueprint.md
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(业务日不可解析——钩子侧捕获出声不反噬); ValueError(日线不足/表达式非法/场景
#   重叠/历史样本空——fail-closed 宁漏判不瞎判); 发射失败不抛（EmitResult.committed=False 留痕）
# [TESTS] tests/plan_engine/test_daily_plan.py
# [A_module] module_id=MOD-PLAN-030 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""daily_plan — 晨间预案生成器（判定台账标准 v0.1 §六任务 3 上半，作战室"验证昨日计划"）。

T 日收盘数据入库后（daily_kline SUCCESS=自然唤醒，与 P2a 次日概率件同拍），产出
治理 G+1 时段的 N 个预案分支（v0 基线 N=3：高开进攻/低开防御/平开震荡），触发条件
全部是**可测量表达式**（标准 §三铁律："如果走弱"不合格），经 judgment_ledger.
emit_judgment 一行发射到 c1_market.judgment_daily_plan。T+1 盘中归类（scenario_
classifier）+收盘验证（close_verifier）消费本件产出，P1 结算链自动回填结算列。

触发表达式文法 v0.1（白名单递归下降 AST，无 eval/exec——注入面结构性关闭）::

    or_expr   := and_expr (OR and_expr)*
    and_expr  := not_expr (AND not_expr)*
    not_expr  := NOT not_expr | comparison
    comparison:= arith (("> "|">="|"<"|"<="|"=="|"!=") arith)?
    arith     := term (("+"|"-") term)*
    term      := factor (("*"|"/") factor)*
    factor    := NUMBER | IDENT | "(" or_expr ")" | "-" factor

约束：标识符必须在 FEATURE_VOCAB 特征词表内（未知名=ValueError）；长度/记号数/
嵌套深度三重上限；运算语义按 Python 数值，除零/特征缺席=条件不可满足（不触发，
缺席进 evidence 由调用方标注）。AND/OR/NOT 大小写不敏感。

特征词表 FEATURE_VOCAB（口径按评估上下文同源——历史=指数日线，盘中=510300 ETF
60min 代理，P2a 既定 proxy 口径，基差如实标注）：
  - open_gap_pct    开盘缺口% = (时段首价/昨收 - 1)×100
  - amount_ratio    量比 = 当日累计量 / 同口径历史均量（20 期）
  - ret_intraday_pct 盘中相对昨收% = (最新价/昨收 - 1)×100

v0 预案分支（RULE_PARAMS 单点声明，trigger 文本由参数拼装——调参=改这里+跑测试）：
  S1 attack     "open_gap_pct > +GAP_BAND AND amount_ratio > AMOUNT_HIGH"（高开放量进攻）
                → action=trend_follow_no_chase（顺势不追高，回踩确认）
  S2 defense    "open_gap_pct < -GAP_BAND AND ret_intraday_pct < 0"（低开未收复防御）
                → action=stand_aside_defense（空仓观望/防御）
  S3 oscillation "open_gap_pct <= GAP_BAND AND open_gap_pct >= -GAP_BAND"（平开震荡）
                → action=range_fade_extremes（区间高抛低吸）
互斥性：三分支在 open_gap_pct 轴上结构互斥（gap>+G / |gap|≤G / gap<-G）；发射前
结构网格探针+历史重放双校验（任一向量命中两分支即 ValueError）。覆盖缺口如实：
高开缩量/低开收复等日不入任何分支=无场景日（收盘验证记 no_scenario 哨兵，预案
结算按 verification 链 unresolvable 如实留痕——不硬凑全覆盖）。

path_prior 口径（文档化，留待数据说话）：历史（≤G，PIT）逐日按优先序 S1>S2>S3
归类，先验=(n_i+α)/(Σn+3α) Laplace 平滑；无场景日不计分母（条件分布 P(分支|场景日)）；
归类样本 < min_classified_n → 均匀先验 fallback=True（置信折半）。

输入全景（Owner 口径，库内可得范围，缺席降级标注）：T 日全量行情（kline_index 日线）
+次日概率（MOD-PLAN-029 台账产出，缺→降级）+regime 快照（regime_snapshot_history
最新 ≤G）+情绪面（market_breadth_snapshot 当日涨跌家数/涨停）+宏观日历（trade_
calendar 下一开市日）。

幂等与业务日：G=resolve_pf_alloc_trade_date()（行情最新入库日）；inputs_ref 首键
plan_date:<G>（P2a 首键事故同款修法——模式不带前导 '|'）已发射则零副作用跳过。

不做什么：不写结算列（无通道）；不做盘中归类（scenario_classifier）；不做收盘验证
（close_verifier）；不做执行对比（plan_followed 留编排器接口）。

依据: docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §三表3/§六
      + 2026-09-16-blueprint-addendum-warroom-three-tasks.md 任务 3
SSoT: depgraph node 14585410（MOD-PLAN-030）
Version: 0.1.0
"""

from __future__ import annotations

import hashlib
import re
from typing import Any, Final, Sequence

from zephyr.plan_engine.judgment_ledger import (
    JUDGMENT_TABLES,
    EmitResult,
    JudgmentDraft,
    JudgmentEmitHook,
    emit_judgment,
    make_judgment_emit_hook,
)
from zephyr.shared.utils.time_utils import now_utc

__all__: Final = [
    "FEATURE_VOCAB",
    "MODULE_ID",
    "MODEL_VERSION",
    "NO_SCENARIO",
    "RULE_PARAMS",
    "SUBJECT",
    "TriggerSyntaxError",
    "build_v0_scenarios",
    "daily_features_of",
    "emit_for_trade_date",
    "eval_trigger",
    "inputs_hash_of",
    "load_plan_for_session",
    "maybe_emit_daily_plan",
    "parse_trigger",
    "validate_scenarios",
]

MODULE_ID: Final = "MOD-PLAN-030"
MODEL_VERSION: Final = "v0-rule"
SUBJECT: Final = "index:000300.SH"
NO_SCENARIO: Final = "no_scenario"  # 无场景日哨兵（verification.actual_scenario_id 如实口径）

# ── v0 规则参数（单点声明；调参=改这里+跑测试）──
RULE_PARAMS: Final[dict[str, float]] = {
    "gap_band": 0.3,          # 开口带宽 ±0.3%：>+G=高开 S1 / <-G=低开 S2 / 其间=平开 S3
    "amount_high": 1.2,       # 放量阈（量比 >1.2 才确认进攻）
    "prior_alpha": 5.0,       # path_prior Laplace 平滑伪计数
    "min_classified_n": 30,   # 历史归类样本下限（不足退化均匀先验）
    "vol_lookback": 20,       # 量比历史窗口（期）
    "conf_n_full": 120.0,     # 置信饱和归类样本量
    "conf_cap": 0.9,          # 置信上限（v0 不给满置信）
    "missing_input_step": 0.9,  # 每缺一项可选输入的置信折乘
    "conf_floor": 0.2,        # 置信下限
}

# 特征词表（触发表达式合法标识符封闭集合——词表外标识符=ValueError）
FEATURE_VOCAB: Final[frozenset[str]] = frozenset({
    "open_gap_pct", "amount_ratio", "ret_intraday_pct",
})

# 表达式安全上限（注入面收缩：长度/记号数/嵌套深度）
_EXPR_MAX_LEN: Final = 500
_EXPR_MAX_TOKENS: Final = 80
_EXPR_MAX_DEPTH: Final = 24


# ── 触发表达式文法（白名单 AST——禁 eval/exec，注入面结构性关闭）──


class TriggerSyntaxError(ValueError):
    """触发表达式非法（词法/文法/词表外标识符/超限）——fail-closed。"""


_TOKEN_RE: Final = re.compile(
    r"(?P<ws>\s+)|(?P<num>\d+\.\d+|\.\d+|\d+)|(?P<ident>[A-Za-z_][A-Za-z0-9_]*)"
    r"|(?P<op>>=|<=|==|!=|>|<|\+|-|\*|/|\(|\))"
)


def tokenize(expr: str) -> list[tuple[str, str]]:
    """表达式 → 记号序列 [(kind, text)]；kind∈{num,ident,op,and,or,not}。

    Raises:
        TriggerSyntaxError: 空串/超长/非法字符/记号数超限。
    """
    if not isinstance(expr, str) or not expr.strip():
        raise TriggerSyntaxError("触发表达式为空")
    if len(expr) > _EXPR_MAX_LEN:
        raise TriggerSyntaxError(f"触发表达式超长（>{_EXPR_MAX_LEN}）")
    toks: list[tuple[str, str]] = []
    pos = 0
    while pos < len(expr):
        m = _TOKEN_RE.match(expr, pos)
        if m is None:
            raise TriggerSyntaxError(f"非法字符（位置 {pos}）: {expr[pos:pos + 8]!r}")
        pos = m.end()
        kind = m.lastgroup or ""
        if kind == "ws":
            continue
        text = m.group(kind)
        if kind == "ident" and text.lower() in ("and", "or", "not"):
            toks.append((text.lower(), text))
        else:
            toks.append((kind, text))
    if not toks:
        raise TriggerSyntaxError("触发表达式无有效记号")
    if len(toks) > _EXPR_MAX_TOKENS:
        raise TriggerSyntaxError(f"触发表达式记号数超限（>{_EXPR_MAX_TOKENS}）")
    return toks


class _Parser:
    """递归下降解析器（AST=嵌套 tuple；深度超限 fail-closed 防栈爆）。"""

    def __init__(self, toks: list[tuple[str, str]]):
        self._toks = toks
        self._i = 0
        self._depth = 0

    def _peek(self) -> tuple[str, str] | None:
        return self._toks[self._i] if self._i < len(self._toks) else None

    def _next(self) -> tuple[str, str]:
        t = self._peek()
        if t is None:
            raise TriggerSyntaxError("表达式意外终止")
        self._i += 1
        return t

    def parse(self) -> tuple:
        node = self._or()
        if self._peek() is not None:
            raise TriggerSyntaxError(f"多余记号: {self._peek()!r}")
        return node

    def _or(self) -> tuple:
        node = self._and()
        while (t := self._peek()) and t[0] == "or":
            self._next()
            node = ("or", node, self._and())
        return node

    def _and(self) -> tuple:
        node = self._not()
        while (t := self._peek()) and t[0] == "and":
            self._next()
            node = ("and", node, self._not())
        return node

    def _not(self) -> tuple:
        if (t := self._peek()) and t[0] == "not":
            self._next()
            return ("not", self._not())
        return self._cmp()

    def _cmp(self) -> tuple:
        left = self._arith()
        t = self._peek()
        if t and t[0] == "op" and t[1] in (">", ">=", "<", "<=", "==", "!="):
            self._next()
            return ("cmp", t[1], left, self._arith())
        return left

    def _arith(self) -> tuple:
        node = self._term()
        while (t := self._peek()) and t[0] == "op" and t[1] in ("+", "-"):
            self._next()
            node = (t[1], node, self._term())
        return node

    def _term(self) -> tuple:
        node = self._factor()
        while (t := self._peek()) and t[0] == "op" and t[1] in ("*", "/"):
            self._next()
            node = (t[1], node, self._factor())
        return node

    def _factor(self) -> tuple:
        self._depth += 1
        if self._depth > _EXPR_MAX_DEPTH:
            raise TriggerSyntaxError(f"嵌套深度超限（>{_EXPR_MAX_DEPTH}）")
        try:
            t = self._next()
            if t[0] == "num":
                return ("num", float(t[1]))
            if t[0] == "ident":
                if t[1] not in FEATURE_VOCAB:
                    raise TriggerSyntaxError(f"标识符不在特征词表内: {t[1]!r}（词表 {sorted(FEATURE_VOCAB)}）")
                return ("var", t[1])
            if t == ("op", "("):
                node = self._or()
                if self._next() != ("op", ")"):
                    raise TriggerSyntaxError("括号不闭合")
                return node
            if t == ("op", "-"):
                return ("neg", self._factor())
            raise TriggerSyntaxError(f"意外记号: {t!r}")
        finally:
            self._depth -= 1


def parse_trigger(expr: str) -> tuple:
    """触发表达式 → AST（文法+词表+安全上限三重校验，非法即 TriggerSyntaxError）。"""
    return _Parser(tokenize(expr)).parse()


class _MissingFeature(Exception):
    """特征缺席（求值内部信号——调用方转译为"条件不可满足"+降级标注）。"""


def _eval_arith(op: str, l: float, r: float) -> float:
    """四则求值（除零=特征缺席语义，调用方统一转译）。"""
    if op == "+":
        return l + r
    if op == "-":
        return l - r
    if op == "*":
        return l * r
    if r == 0.0:
        raise _MissingFeature("div_by_zero")
    return l / r


_CMP_OPS: Final = {
    ">": lambda x, y: x > y,
    ">=": lambda x, y: x >= y,
    "<": lambda x, y: x < y,
    "<=": lambda x, y: x <= y,
    "==": lambda x, y: x == y,
    "!=": lambda x, y: x != y,
}


def _eval_cmp(sym: str, l: float, r: float) -> bool:
    """六比较求值（词表封闭，未知符号由 parse 层拦截，此处兜 KeyError 不可达）。"""
    return _CMP_OPS[sym](l, r)


def eval_trigger(ast: tuple, features: dict[str, float]) -> bool:
    """AST + 特征向量 → 布尔（比较按 Python 数值语义）。

    特征缺席/除零/无定义 = _MissingFeature（调用方捕失误→不触发+标注）。
    """
    op = ast[0]
    if op == "num":
        return float(ast[1])  # 纯数值沿比较路径传播
    if op == "var":
        v = features.get(ast[1])
        if v is None:
            raise _MissingFeature(ast[1])
        return float(v)
    if op == "neg":
        return -float(eval_trigger(ast[1], features))
    if op in ("+", "-", "*", "/"):
        return _eval_arith(op, float(eval_trigger(ast[1], features)), float(eval_trigger(ast[2], features)))
    if op == "cmp":
        _, sym, l, r = ast
        return _eval_cmp(sym, float(eval_trigger(l, features)), float(eval_trigger(r, features)))
    if op == "not":
        return not bool(eval_trigger(ast[1], features))
    if op == "and":
        return bool(eval_trigger(ast[1], features)) and bool(eval_trigger(ast[2], features))
    if op == "or":
        return bool(eval_trigger(ast[1], features)) or bool(eval_trigger(ast[2], features))
    raise TriggerSyntaxError(f"未知 AST 节点: {op!r}")


def eval_trigger_measurable(ast: tuple, features: dict[str, float]) -> tuple[bool, str | None]:
    """求值的调用方便壳：缺失特征 → (False, 缺席原因)——"不可满足≠不触发"语义。"""
    try:
        return bool(eval_trigger(ast, features)), None
    except _MissingFeature as exc:
        return False, f"missing:{exc.args[0]}"


# ── 特征装配（历史日线口径——PIT 安全，只用当日及之前数据）──


def daily_features_of(
    prev_row: Sequence[float] | None,
    row: Sequence[float],
    vol_hist: Sequence[float],
    params: dict[str, float] = RULE_PARAMS,
) -> dict[str, float]:
    """单日 EOD 特征（row=[trade_date, open, high, low, close, volume]，历史=指数日线）。

    Args:
        prev_row: 前一交易日同行（None=序列首日——特征不可算，返回空 dict）。
        vol_hist: 前 vol_lookback 期成交量（长度可 < lookback——不足返回空 dict）。

    Returns:
        {open_gap_pct, amount_ratio, ret_intraday_pct}（浮点百分比分母口径见模块头）。
        前收非正/均量非正/历史不足 → 空 dict（特征不可得≠0 值——0 是合法测量值）。
    """
    if prev_row is None or len(vol_hist) < int(params["vol_lookback"]):
        return {}
    prev_close = float(prev_row[4])
    if prev_close <= 0:
        return {}
    vol_mean = sum(float(v) for v in vol_hist) / len(vol_hist)
    if vol_mean <= 0:
        return {}
    close = float(row[4])
    return {
        "open_gap_pct": (float(row[1]) / prev_close - 1.0) * 100.0,
        "amount_ratio": float(row[5]) / vol_mean,
        "ret_intraday_pct": (close / prev_close - 1.0) * 100.0,
    }


# ── v0 预案分支（参数拼装 trigger 文本；互斥双校验）──


def build_v0_scenarios(params: dict[str, float] = RULE_PARAMS) -> list[dict[str, Any]]:
    """v0 三分支（N=3 基线）：trigger 文本由 RULE_PARAMS 拼装（调参即改文本）。"""
    g = float(params["gap_band"])
    ah = float(params["amount_high"])
    fmt = lambda v: f"{v:g}"  # noqa: E731 —— 参数→触发文本的单点格式化
    return [
        {
            "scenario_id": "S1_attack",
            "trigger": f"open_gap_pct > {fmt(g)} AND amount_ratio > {fmt(ah)}",
            "action": "trend_follow_no_chase",
            "path_prior": 0.0,  # 由历史频率回填（emit 前定稿）
            "rationale": "高开且放量=进攻确认（缺口轴向结构互斥之一）",
        },
        {
            "scenario_id": "S2_defense",
            "trigger": f"open_gap_pct < -{fmt(g)} AND ret_intraday_pct < 0",
            "action": "stand_aside_defense",
            "path_prior": 0.0,
            "rationale": "低开且未收复昨收=防御（缺口轴向结构互斥之二）",
        },
        {
            "scenario_id": "S3_oscillation",
            "trigger": f"open_gap_pct <= {fmt(g)} AND open_gap_pct >= -{fmt(g)}",
            "action": "range_fade_extremes",
            "path_prior": 0.0,
            "rationale": "平开=震荡区间预设（缺口轴向结构互斥之三）",
        },
    ]


def _classify_day(
    scenarios: list[dict[str, Any]],
    asts: list[tuple],
    features: dict[str, float],
) -> str | None:
    """单日归类（优先序=清单序，首个命中即返回——与盘中归类同规则）。"""
    for sc, ast in zip(scenarios, asts):
        hit, _miss = eval_trigger_measurable(ast, features)
        if hit:
            return str(sc["scenario_id"])
    return None


def _history_priors(
    rows: Sequence[tuple],
    scenarios: list[dict[str, Any]],
    asts: list[tuple],
    params: dict[str, float],
) -> tuple[dict[str, float], int, bool]:
    """历史逐日归类 → path_prior（Laplace；无场景日不计分母——口径文档化）。

    Returns:
        ({scenario_id: prior}, n_classified, fallback)。
    Raises:
        ValueError: 可用历史为空（禁编造分布，fail-closed）。
    """
    lookback = int(params["vol_lookback"])
    counts = {str(sc["scenario_id"]): 0 for sc in scenarios}
    n_classified = 0
    for i in range(1, len(rows)):
        vol_hist = [float(r[5]) for r in rows[max(0, i - lookback):i]]
        feats = daily_features_of(rows[i - 1], rows[i], vol_hist, params)
        if not feats:
            continue
        sid = _classify_day(scenarios, asts, feats)
        if sid is not None:
            counts[sid] += 1
            n_classified += 1
    if len(rows) < 2:
        raise ValueError("历史日线不足（<2 行，禁编造先验）")
    alpha = float(params["prior_alpha"])
    if n_classified < int(params["min_classified_n"]):
        n_sc = len(scenarios)
        prior = {str(sc["scenario_id"]): (1.0 + alpha) / (n_sc + n_sc * alpha) for sc in scenarios}
        return prior, n_classified, True
    denom = float(n_classified) + len(scenarios) * alpha
    prior = {k: (v + alpha) / denom for k, v in counts.items()}
    return prior, n_classified, False


def validate_scenarios(
    scenarios: list[dict[str, Any]],
    hist_rows: Sequence[tuple] | None = None,
    params: dict[str, float] = RULE_PARAMS,
) -> None:
    """发射前场景校验（fail-closed）：文法/词表/互斥双探针。

    - 文法+词表：逐 trigger parse（TriggerSyntaxError 直接上抛）。
    - 互斥探针 1（结构网格）：特征边界值笛卡尔网格上任意向量至多命中 1 分支
      （网格=RULE_PARAMS 阈值边界 ±ε 采样——阈值改参自动跟随）。
    - 互斥探针 2（历史重放）：hist_rows 给定时逐日归类不得同日命中 2 分支。
    Raises:
        TriggerSyntaxError / ValueError（重叠即拒——宁缺场景不发出含糊预案）。
    """
    asts = [parse_trigger(str(sc["trigger"])) for sc in scenarios]
    eps = 1e-6
    g = float(params["gap_band"])
    ah = float(params["amount_high"])
    axis = {
        "open_gap_pct": [-3.0, -g - eps, -g, -g + eps, 0.0, g - eps, g, g + eps, 3.0],
        "amount_ratio": [0.5, ah - eps, ah, ah + eps, 2.0],
        "ret_intraday_pct": [-2.0, -0.5, -eps, 0.0, eps, 0.5, 2.0],
    }
    from itertools import product

    for og, ar, rt in product(axis["open_gap_pct"], axis["amount_ratio"], axis["ret_intraday_pct"]):
        feats = {"open_gap_pct": og, "amount_ratio": ar, "ret_intraday_pct": rt}
        hits = [sid for sc, ast in zip(scenarios, asts)
                if (hits_ := eval_trigger_measurable(ast, feats))[0] and (sid := str(sc["scenario_id"]))]
        if len(hits) > 1:
            raise ValueError(
                f"场景互斥违例（结构网格 {feats} 命中 {hits}）——发射拒绝"
            )
    if hist_rows is not None:
        for i in range(1, len(hist_rows)):
            vol_hist = [float(r[5]) for r in hist_rows[max(0, i - int(params["vol_lookback"])):i]]
            feats = daily_features_of(hist_rows[i - 1], hist_rows[i], vol_hist, params)
            if not feats:
                continue
            matched = [str(sc["scenario_id"]) for sc, ast in zip(scenarios, asts)
                       if eval_trigger_measurable(ast, feats)[0]]
            if len(matched) > 1:
                raise ValueError(
                    f"场景互斥违例（历史重放 {hist_rows[i][0]} 命中 {matched}）——发射拒绝"
                )


# ── 输入装载（可选项缺席=降级标注，禁编造）──


def _safe_one(rd: Any, sql: str) -> tuple | None:
    try:
        rows = rd(sql)
        return rows[0] if rows else None
    except Exception:  # noqa: BLE001——可选输入缺席不阻塞计划（降级标注）
        return None


def inputs_hash_of(day: str, last_row: tuple, prior: dict[str, float], n: int,
                   forecaster_jid: str) -> str:
    """当日输入指纹（sha256 截断 16 hex）：同输入必同指纹，输入变=指纹变。"""
    raw = "|".join([
        day, f"{float(last_row[4]):.4f}", f"{float(last_row[5]):.0f}",
        ",".join(f"{prior[k]:.6f}" for k in sorted(prior)), str(n), forecaster_jid,
    ])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


# ── 发射组合（读库→特征→先验→校验→emit_judgment）──

_KLINE_SQL: Final = (
    "SELECT trade_date, open, high, low, close, volume "
    "FROM c1_market.kline_index WHERE symbol = '000300' AND quality_flag = 1 "
    "ORDER BY trade_date"
)
# 幂等查重：plan_date 是 inputs_ref 首键（首键前无分隔符——P2a 幂等三连发事故同款修法；
# 尾 '|' 防日期前缀误配）
_SQL_ALREADY = (
    "SELECT count() "
    "FROM {table} "
    "WHERE module_id = '{module_id}' AND inputs_ref LIKE '%plan_date:{day}|%'"
)
_SQL_FORECAST = (
    "SELECT judgment_id, payload "
    "FROM {table} "
    "WHERE module_id = '{forecaster}' AND inputs_ref LIKE '%trade_date:{day}|%' "
    "ORDER BY asof_ts DESC, judgment_id DESC LIMIT 1"
)
_REGIME_SQL: Final = (
    "SELECT trade_date, dominant, confidence FROM c1_backtest.regime_snapshot_history "
    "WHERE trade_date <= '{day}' ORDER BY trade_date DESC, ingest_ts DESC LIMIT 1"
)
_BREADTH_SQL: Final = (
    "SELECT advancing, declining, limit_up, limit_down FROM c1_market.market_breadth_snapshot "
    "WHERE trade_date = '{day}' ORDER BY ts DESC LIMIT 1"
)
_NEXT_SESSION_SQL: Final = (
    "SELECT min(cal_date) FROM c1_market.trade_calendar "
    "WHERE cal_date > '{day}' AND is_open = 1 AND exchange = 'SSE'"
)
# 计划装载（盘中归类/收盘验证消费方共用——T2/T3 import 复用，禁另拼第二份）
_SQL_PLAN = (
    "SELECT judgment_id, payload, asof_ts, inputs_ref "
    "FROM {table} "
    "WHERE module_id = '{module_id}' AND inputs_ref LIKE '%plan_date:{day}|%' "
    "ORDER BY asof_ts DESC, judgment_id DESC LIMIT 1"
)


def load_plan_for_session(day: str, *, reader=None) -> dict[str, Any] | None:
    """装载治理 day 之后第一个时段的**最新**预案（修订=新 id 追加取最新——标准口径）。

    Returns:
        {judgment_id, payload(dict), asof_ts, inputs_ref} 或 None（无计划）。
    """
    rd = reader or _reader_execute
    rows = rd(_SQL_PLAN.format(table=JUDGMENT_TABLES["daily_plan"], module_id=MODULE_ID, day=day))
    if not rows:
        return None
    import json as _json

    try:
        payload = _json.loads(rows[0][1])
    except (ValueError, TypeError):
        return None
    return {
        "judgment_id": str(rows[0][0]),
        "payload": payload,
        "asof_ts": rows[0][2],
        "inputs_ref": str(rows[0][3]),
    }


from zephyr.plan_engine.judgment_settler import _reader_execute  # noqa: E402,PLC2701 ——
# 只读通道单点收口于共享结算器库件（P2a 同款，CLONE-GUARD 预检 acknowledged：注入点复用不改本体）


def _load_optional_inputs(rd, day: str) -> dict[str, Any]:
    """可选输入读取（缺席降级——每缺一项 confidence 折乘，floor 下限）。

    返回 dict：fc/forecaster_jid/forecast_note/regime/breadth/next_session/missing。
    """
    missing: list[str] = []
    fc = _safe_one(rd, _SQL_FORECAST.format(table=JUDGMENT_TABLES["next_day_forecast"],
                              forecaster=_FORECASTER_MODULE, day=day))
    forecaster_jid = ""
    forecast_note: dict[str, Any] | None = None
    if fc is not None:
        forecaster_jid = str(fc[0])
        try:
            import json as _json

            p = _json.loads(str(fc[1]))
            forecast_note = {k: p.get(k) for k in ("p_up", "p_flat", "p_down")}
        except (ValueError, TypeError):
            forecast_note = None
        if forecast_note is None:
            missing.append("next_day_forecast_payload")
    else:
        missing.append("next_day_forecast")
    regime = _safe_one(rd, _REGIME_SQL.format(day=day))
    if regime is None:
        missing.append("regime_snapshot")
    breadth = _safe_one(rd, _BREADTH_SQL.format(day=day))
    if breadth is None:
        missing.append("market_breadth")
    next_session = _safe_one(rd, _NEXT_SESSION_SQL.format(day=day))
    return {
        "fc": fc,
        "forecaster_jid": forecaster_jid,
        "forecast_note": forecast_note,
        "regime": regime,
        "breadth": breadth,
        "next_session": next_session,
        "missing": missing,
    }


def _build_plan_payload(
    day: str,
    day_rows: list,
    scenarios: list[dict],
    prior: dict[str, float],
    n_classified: int,
    fallback: int,
    opt: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    """inputs_ref + payload 组装（口径与 P2b 冻结版逐字一致；hash 用未归一 prior）。"""
    fc = opt["fc"]
    forecaster_jid = opt["forecaster_jid"]
    regime = opt["regime"]
    breadth = opt["breadth"]
    next_session = opt["next_session"]
    missing = opt["missing"]
    h = inputs_hash_of(day, day_rows[-1], prior, n_classified, forecaster_jid)
    inputs_ref = (
        f"plan_date:{day}|inputs_hash:{h}|n:{n_classified}|fallback:{int(fallback)}"
        f"|forecaster:{forecaster_jid[:12] or 'none'}|"
    )
    inputs_scope = [
        "昨收全量:kline_index(000300 日线)",
        "次日概率:" + (f"judgment_next_day_forecast({forecaster_jid[:12]})" if fc else "absent(降级)"),
        "regime快照:" + (f"{regime[1]}@{regime[0]}" if regime else "absent(降级)"),
        "情绪面:" + ("market_breadth_snapshot" if breadth else "absent(降级)"),
        "宏观日历:" + (f"trade_calendar 下一开市 {next_session[0]}" if next_session and next_session[0]
                       else "absent(降级)"),
    ]
    last_open = float(day_rows[-1][1])
    payload = {
        "scenarios": [
            {k: sc[k] for k in ("scenario_id", "trigger", "action", "path_prior", "rationale")}
            for sc in scenarios
        ],
        "inputs_scope": inputs_scope,
        "prior_method": "hist_classified_laplace(no_scenario_day_excluded)",
        "fallback": fallback,
        "evidence": {
            "g_close": float(day_rows[-1][4]),
            "g_open": last_open,
            "n_classified": n_classified,
            "missing_inputs": missing,
            "next_day_forecast": opt["forecast_note"],
            "regime_dominant": str(regime[1]) if regime else None,
            "next_session_date": str(next_session[0]) if next_session and next_session[0] else None,
            "proxy_notes": {
                "history": "index_daily(kline_index 000300)",
                "intraday": "etf_510300_60min_proxy(P2a 既定口径，基差如实)",
            },
        },
    }
    return inputs_ref, payload


def _plan_confidence(n_classified: int, fallback: int, missing: list[str]) -> float:
    """置信=归类样本饱和度 ×fallback 折半 ×缺席折乘（口径文档化）。"""
    conf = min(n_classified / float(RULE_PARAMS["conf_n_full"]), float(RULE_PARAMS["conf_cap"]))
    if fallback:
        conf *= 0.5
    return max(float(RULE_PARAMS["conf_floor"]),
               conf * float(RULE_PARAMS["missing_input_step"]) ** len(missing))


def emit_for_trade_date(
    day: str,
    *,
    reader=None,
    synthetic: bool = False,
    asof_ts: Any = None,
) -> EmitResult:
    """G 日预案发射（组合入口：读库→特征→先验→双互斥校验→emit_judgment）。

    Raises:
        ValueError: G 日线不在库/历史不足/场景重叠/历史样本空（fail-closed）。
    """
    rd = reader or _reader_execute
    rows = rd(_KLINE_SQL)
    day_rows = [r for r in rows if str(r[0]) <= day]
    if not day_rows or str(day_rows[-1][0]) != day:
        raise ValueError(f"G 日 {day} 日线不在库（禁猜日发射）")
    scenarios = build_v0_scenarios()
    asts = [parse_trigger(str(sc["trigger"])) for sc in scenarios]
    validate_scenarios(scenarios, day_rows)  # 双互斥探针（结构网格+历史重放）fail-closed
    prior, n_classified, fallback = _history_priors(day_rows, scenarios, asts, RULE_PARAMS)
    total = sum(prior.values())
    for sc in scenarios:
        sc["path_prior"] = round(prior[str(sc["scenario_id"])] / total, 6)
    remainder = round(1.0 - sum(sc["path_prior"] for sc in scenarios), 9)
    scenarios[0]["path_prior"] = round(scenarios[0]["path_prior"] + remainder, 6)

    opt = _load_optional_inputs(rd, day)
    inputs_ref, payload = _build_plan_payload(
        day, day_rows, scenarios, prior, n_classified, fallback, opt)
    conf = _plan_confidence(n_classified, fallback, opt["missing"])
    a_ts = asof_ts or now_utc()
    if a_ts.tzinfo is None:
        raise ValueError("asof_ts 须带时区（RULE-SCHEMA-TZ）")
    return emit_judgment(
        "daily_plan",
        JudgmentDraft(
            module_id=MODULE_ID,
            model_version=MODEL_VERSION,
            subject=SUBJECT,
            payload=payload,
            confidence=round(conf, 4),
            horizon=None,  # 表默认 intraday_session
            inputs_ref=inputs_ref,
            run_id=f"daily-plan:{day}",
        ),
        asof_ts=a_ts,
        input_cutoff_ts=a_ts,  # 日线收盘口径数据齐后才触发（事件真源保证）
        synthetic=synthetic,
    )


_FORECASTER_MODULE: Final = "MOD-PLAN-029"  # 次日概率件（P2a）——只引用编号读台账，不 import 其私有符号


#: P2b 晨间预案钩子：本模块只登记表侧参数，骨架与委托体单点于 judgment_ledger。
#: （CloneGuard 实测本件与 P2a maybe_emit_next_day_forecast 是 100% extract 级克隆
#:  reDUP 组 06c56c3a9d5495e5，按 R-002 同原则 merge 治本；不走 ack 白名单消警。）
_EMIT_HOOK: Final = JudgmentEmitHook(
    leg="P2b 晨间预案",
    entry="maybe_emit_daily_plan",
    already_sql=_SQL_ALREADY,
    table=JUDGMENT_TABLES["daily_plan"],
    module_id=MODULE_ID,
    date_key="plan_date",  # 对外键名口径保持改造前原样（消费方可见，禁顺手统一）
    doc_zh="""晨间预案的**唯一自动产出者**：daily_kline SUCCESS=自然唤醒（T 日数据齐）。

    宪法 §9.3 合规（零新机制）：不建 cron/Timer/sleep 循环。业务日 G=
    resolve_pf_alloc_trade_date()（禁墙钟猜日）；plan_date:<G> 查重幂等——重复唤醒/
    非交易日零副作用。发射失败出声不反噬唤醒链。与 P2a 次日概率件同拍（读其台账产出
    作为输入之一）。骨架与 P2a 共用 judgment_ledger.run_judgment_emit_hook（R-002 merge）。
    """,
)

# reader/emit 以 lambda 惰性取本模块全局——既有测试 monkeypatch 的是模块属性，
# import 期绑定会让注入点静默失效（tests/plan_engine/test_daily_plan.py 会打到真库）
maybe_emit_daily_plan: Final = make_judgment_emit_hook(
    _EMIT_HOOK,
    reader=lambda sql: _reader_execute(sql),
    emit=lambda day: emit_for_trade_date(day),
)


if __name__ == "__main__":  # pragma: no cover — 手工补跑逃生口（非自动链路）
    print(maybe_emit_daily_plan(task_id="manual_cli", success=True))


class DailyPlanner:
    """发射 facade（scaffold 契约）：模块级组合入口的对象化包装（无独立状态）。"""

    module_id: str = MODULE_ID
    model_version: str = MODEL_VERSION
    subject: str = SUBJECT

    def emit_once(self) -> dict[str, Any]:
        """跑一次唤醒点等价的预案发射（手工补跑/冒烟入口）。"""
        return maybe_emit_daily_plan(task_id="manual_facade", success=True)

    def scenarios(self, params: dict[str, float] | None = None) -> list[dict[str, Any]]:
        """v0 分支定义直通（测试与人工核查用——不触发发射）。"""
        return build_v0_scenarios(params or RULE_PARAMS)
