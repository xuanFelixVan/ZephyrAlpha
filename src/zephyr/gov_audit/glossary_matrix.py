# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain-governance/audit-trail/blueprint.md
# [MODULE] zephyr.gov_audit.glossary_matrix
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不可变审计记录;密码学完整性;只追加
# [MODIFY-GUARD] docs/03_modules/_domain-governance/audit-trail/blueprint.md;src/zephyr/audit-trail/__init__.py
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] IntegrityError;WriteError
# [TESTS] tests/test_audit_trail/
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: term 参数
#   fields: 参数 term，类型注解 str
#   code: glossary_matrix.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① lookup
#   name_en: lookup
#   intro: lookup(term) 源码 L100-L101
#   desc: 源码 L100-L101
#   inputs: term
#   outputs: GlossaryEntry | None
# - id: A2
#   name_zh: ② list_terms
#   name_en: list_terms
#   intro: list_terms() 源码 L104-L105
#   desc: 源码 L104-L105
#   inputs: 无参数
#   outputs: list[str]
#   （注：A2 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: GlossaryEntry | None
#   name_en: GlossaryEntry | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# - id: O2
#   name_zh: list[str]
#   name_en: list[str]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

from pydantic import BaseModel


class GlossaryEntry(BaseModel):
    term: str
    definition: str
    domain: str
    acronym: str = ""


GLOSSARY: dict[str, GlossaryEntry] = {
    "Alpha": GlossaryEntry(term="Alpha", definition="超额收益——策略相对基准的超额回报", domain="量化", acronym="α"),
    "Backtest": GlossaryEntry(term="Backtest", definition="回测——用历史数据模拟策略表现", domain="量化"),
    "C-Track": GlossaryEntry(term="C-Track", definition="Build Track——14层施工流水线", domain="架构"),
    "B-Track": GlossaryEntry(term="B-Track", definition="Business Track——12大业务系统", domain="架构"),
    "DMA": GlossaryEntry(term="DMA", definition="直接市场接入——Direct Market Access", domain="交易"),
    "FIX": GlossaryEntry(term="FIX", definition="金融信息交换协议——Financial Information eXchange", domain="交易"),
    "HFT": GlossaryEntry(term="HFT", definition="高频交易——High Frequency Trading", domain="交易"),
    "IOC": GlossaryEntry(term="IOC", definition="立即成交或取消——Immediate Or Cancel", domain="交易"),
    "LP": GlossaryEntry(term="LP", definition="流动性提供者——Liquidity Provider", domain="交易"),
    "MDD": GlossaryEntry(term="MDD", definition="最大回撤——Maximum Drawdown", domain="风控"),
    "MTF": GlossaryEntry(term="MTF", definition="多边交易设施——Multilateral Trading Facility", domain="交易"),
    "NDD": GlossaryEntry(term="NDD", definition="无交易员平台——No Dealing Desk", domain="交易"),
    "Paper": GlossaryEntry(term="Paper", definition="模拟交易——Paper Trading", domain="交易"),
    "PnL": GlossaryEntry(term="PnL", definition="盈亏——Profit and Loss", domain="风控"),
    "Sharpe": GlossaryEntry(term="Sharpe", definition="夏普比率——风险调整后收益", domain="量化"),
    "SLI": GlossaryEntry(term="SLI", definition="服务等级指标——Service Level Indicator", domain="运维"),
    "SLO": GlossaryEntry(term="SLO", definition="服务等级目标——Service Level Objective", domain="运维"),
    "ETF": GlossaryEntry(term="ETF", definition="交易所交易基金——Exchange Traded Fund", domain="交易"),
    "Vol": GlossaryEntry(term="Vol", definition="波动率——Volatility", domain="风控"),
    "DCA": GlossaryEntry(term="DCA", definition="定投——Dollar Cost Averaging", domain="策略"),
    "ECN": GlossaryEntry(term="ECN", definition="电子通信网络——Electronic Communication Network", domain="交易"),
    "Benchmark": GlossaryEntry(term="Benchmark", definition="业绩基准——如S&P500/沪深300", domain="量化"),
}


def lookup(term: str) -> GlossaryEntry | None:
    return GLOSSARY.get(term)


def list_terms() -> list[str]:
    return sorted(GLOSSARY.keys())


GLOSSARY_COUNT: int = len(GLOSSARY)
