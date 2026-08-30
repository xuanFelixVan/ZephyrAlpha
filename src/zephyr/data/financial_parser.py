# [BLUEPRINT] MOD-DAT-FIN-PARSER | docs/03_modules/_domain_data/financial_parser/blueprint.md
# [MODULE] zephyr.data.financial_parser
# [DOMAIN] D_DATA
# [DEPENDENCIES] 无（判定核心纯内存；pdf_extractor/xbrl_parser/llm_fallback 全注入）
# [CONSUMERS] 运行时装配批（巨潮 PDF 下载执行 / pdfplumber·Arelle 真实绑定 / qwen3:8b 本地调用 / c3 财务表写入接线）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 解析路径阶梯 XBRL(0.95)>表格(0.80)>LLM兜底(0.60)；三路皆无 Fail-Closed；未映射指标留痕不静默丢弃；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_data/financial_parser/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空symbol/未知report_type/空period/无可用解析路径→ValueError；单值不可解析→跳过入unmapped_keys
# [TESTS] tests/zephyr/data/test_financial_parser.py
# [A_module] module_id=MOD-DAT-FIN-PARSER | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""



FinancialParser — 财报结构化解析器（MOD-DAT-FIN-PARSER）

B13-04263（AUD-DRAFT-001-DIGEST P1 波 W-P1-09，D-DATA-80，§17.1）：
年报/季报/快报/更正公告 PDF 与 XBRL → 结构化指标——XBRL(Arelle) 解析 /
pdfplumber 表格抽取双路径 + 指标标准化映射 c3 财务表口径；本地 qwen3:8b
兜底非标准格式；解析置信度入 quality_flag。

查重裁定：announcement_provider（10603035，P1W08）为巨潮/交易所**公告
采集**（元数据落 fund_news_data）；本模块为**财报内容结构化解析**
（PDF/XBRL→指标），消费其公告元数据定位财报附件，不复制采集链。
B1-00619 dig 已裁定重复并入本模块；B13-04280（Filing NLP，公告文本 NLP）
复用本模块 PDF 解析产物，互补不重复。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: pdf_extractor 参数
#   fields: 参数 pdf_extractor（无注解）
#   code: financial_parser.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: xbrl_parser 参数
#   fields: 参数 xbrl_parser（无注解）
#   code: financial_parser.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: llm_fallback 参数
#   fields: 参数 llm_fallback（无注解）
#   code: financial_parser.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① FinancialParser
#   name_en: FinancialParser
#   intro: 财报解析管道（判定核心纯内存，解析器全注入式）。
#   desc: 财报解析管道（判定核心纯内存，解析器全注入式）。；公共方法（定义序）: parse_report；源码 L141-L266
#   inputs: pdf_extractor xbrl_parser llm_fallback
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: FinancialParser
#   downstream: 运行时装配批（巨潮 PDF 下载执行 / pdfplumber·Arelle 真实绑定 / qwen3:8b 本地调用 / c3 财务表写入接线）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Callable, Final, Optional

log = logging.getLogger(__name__)

__all__: Final = [
    "FinancialParser",
    "METRIC_MAP",
    "ParsedFinancials",
    "ReportRef",
]

REPORT_TYPES: Final = ("annual", "quarterly", "express", "correction")

#: 指标标准化映射：中文表头/XBRL 标签 → 规范指标键（c3 财务表口径）
METRIC_MAP: Final[dict[str, str]] = {
    "营业收入": "revenue",
    "营业总收入": "revenue",
    "净利润": "net_profit",
    "归母净利润": "net_profit",
    "归属于母公司股东的净利润": "net_profit",
    "归属于上市公司股东的净利润": "net_profit",
    "总资产": "total_assets",
    "资产总计": "total_assets",
    "总负债": "total_liabilities",
    "负债合计": "total_liabilities",
    "经营活动产生的现金流量净额": "operating_cashflow",
    "经营现金流净额": "operating_cashflow",
    "基本每股收益": "eps",
    "每股收益": "eps",
}

_CONFIDENCE_BY_PARSER: Final = {"xbrl": 0.95, "table": 0.80, "llm": 0.60}

_UNIT_MULTIPLIER: Final = (("亿元", 1e8), ("万元", 1e4), ("元", 1.0))

_NUM_RE: Final = re.compile(r"^-?\d[\d,]*\.?\d*$")


@dataclass(frozen=True)
class ReportRef:
    """财报引用：解析输入。"""

    symbol: str
    report_type: str
    period: str
    pdf_path: str | None = None
    raw_tables: list | None = None
    xbrl_facts: dict | None = None
    text: str | None = None


@dataclass(frozen=True)
class ParsedFinancials:
    """结构化解析结果。"""

    symbol: str
    period: str
    report_type: str
    metrics: dict
    parser_used: str
    confidence: float
    quality_flag: str
    unmapped_keys: tuple = field(default_factory=tuple)


class FinancialParser:
    """财报解析管道（判定核心纯内存，解析器全注入式）。"""

    def __init__(
        self,
        pdf_extractor: Callable[[str], list] | None = None,
        xbrl_parser: Callable[[str], dict] | None = None,
        llm_fallback: Callable[[str], dict] | None = None,
    ) -> None:
        self._pdf_extractor = pdf_extractor
        self._xbrl_parser = xbrl_parser
        self._llm_fallback = llm_fallback

    # ── 数值清洗 ──

    @staticmethod
    def _clean_number(raw: object) -> float | None:
        """千分位/括号负数/单位倍率（万元/亿元→元）归一；不可解析返回 None。"""
        if isinstance(raw, (int, float)):
            return float(raw)
        if not isinstance(raw, str):
            return None
        text = raw.strip()
        if not text:
            return None
        negative = False
        if text.startswith("(") and text.endswith(")"):
            negative = True
            text = text[1:-1].strip()
        multiplier = 1.0
        for unit, mult in _UNIT_MULTIPLIER:
            if text.endswith(unit):
                multiplier = mult
                text = text[: -len(unit)].strip()
                break
        if text.startswith("-"):
            negative = True
            text = text[1:].strip()
        if not _NUM_RE.match(text):
            return None
        value = float(text.replace(",", "")) * multiplier
        return -value if negative else value

    # ── 指标标准化 ──

    def _standardize(self, facts: dict) -> tuple[dict, list]:
        metrics: dict[str, float] = {}
        unmapped: list[str] = []
        for key, raw in facts.items():
            canonical = METRIC_MAP.get(key)
            if canonical is None:
                unmapped.append(key)
                continue
            value = self._clean_number(raw)
            if value is None:
                unmapped.append(key)
                continue
            metrics[canonical] = value
        return metrics, unmapped

    @staticmethod
    def _tables_to_facts(tables: list) -> dict:
        """pdfplumber 表格（list[list[list[str]]]）→ {指标名: 值} 平铺。"""
        facts: dict[str, str] = {}
        for table in tables or []:
            for row in table or []:
                if not row or len(row) < 2:
                    continue
                head = str(row[0]).strip()
                if not head:
                    continue
                facts.setdefault(head, str(row[-1]).strip())
        return facts

    # ── 主接口 ──

    def parse_report(self, report: ReportRef) -> ParsedFinancials:
        """解析路径阶梯：XBRL(0.95) > 表格(0.80) > LLM 兜底(0.60)。"""
        if not report.symbol:
            raise ValueError("symbol 不能为空")
        if report.report_type not in REPORT_TYPES:
            raise ValueError(f"未知 report_type: {report.report_type!r}（合法: {REPORT_TYPES}）")
        if not report.period:
            raise ValueError("period 不能为空")

        facts: dict | None = None
        parser_used = ""
        if report.xbrl_facts:
            facts = dict(report.xbrl_facts)
            parser_used = "xbrl"
        elif self._xbrl_parser is not None and report.pdf_path:
            parsed = self._xbrl_parser(report.pdf_path)
            if parsed:
                facts = dict(parsed)
                parser_used = "xbrl"
        if facts is None:
            tables = report.raw_tables
            if tables is None and self._pdf_extractor is not None and report.pdf_path:
                tables = self._pdf_extractor(report.pdf_path)
            if tables:
                facts = self._tables_to_facts(tables)
                parser_used = "table"
        if facts is None and self._llm_fallback is not None and report.text:
            facts = dict(self._llm_fallback(report.text))
            parser_used = "llm"
        if facts is None:
            raise ValueError("无可用解析路径（XBRL/表格/LLM 三路皆缺）")

        metrics, unmapped = self._standardize(facts)
        confidence = _CONFIDENCE_BY_PARSER[parser_used]
        if confidence >= 0.90:
            flag = "good"
        elif confidence >= 0.70:
            flag = "degraded"
        else:
            flag = "poor"
        return ParsedFinancials(
            symbol=report.symbol,
            period=report.period,
            report_type=report.report_type,
            metrics=metrics,
            parser_used=parser_used,
            confidence=confidence,
            quality_flag=flag,
            unmapped_keys=tuple(unmapped),
        )
