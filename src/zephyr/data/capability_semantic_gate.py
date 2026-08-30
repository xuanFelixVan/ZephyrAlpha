# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.capability_semantic_gate
# [DOMAIN] D_DATA
# [DEPENDENCIES] stdlib ast/dataclasses（语义注册表以代码数据结构承载——docs/ 注册表 YAML 由 17 号 §5.3 施工项 2 另行落地，本模块为其可执行核心）
# [CONSUMERS] commit gate（capability_validator AST gate 装配批，17 号 §5.4 施工项 3）; 调用方（capability-API 语义校验）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 未登记 capability 不校验（过度工程防线，17 号 §5.8）; 只对跨市场/跨品种易混淆 capability 强制登记; 提取 API ⊆ allowed_apis 白名单才放行; 解析失败 fail-open
# [MODIFY-GUARD] 17_special_trading_days_data_assets.md §5.3/§5.4/§5.8
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无（违规以字符串列表返回，空=通过）
# [TESTS] tests/zephyr/data/test_capability_semantic_gate.py
# [A_module] module_id=MOD-GOV-capability_semantic_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: provider .py 文件内容 + CapabilitySemanticEntry 注册表（默认 3 条：hk_trade_calendar/trade_calendar/industry_class）
# F1: _import_aliases（import ... as 别名映射）+ _extract_called_apis（_fetch_<cap> 方法体内 alias.attr 调用提取；exchange_calendars.get_calendar("XHKG") 特化为 exchange_calendars.XHKG）
# F2: check_capability_api_whitelist_content（已登记 capability 的提取 API ⊆ allowed_apis；通配符前缀 THS_*/ifind.*；违例提示登记或换 API）
# O1: 违规描述列表（空=通过）
# [/ALGO_FLOW]
"""



capability 语义注册表 + API 白名单 AST gate（17 号 §5.3 施工项 2 + §5.4 施工项 3 合并收缩 MVP）。

病根（17 号 §5.1）：provider 声明的 capability 名携带市场/品种语义（hk_/industry_），
但底层调用的 API 返回数据语义不符（#ARCH-DATA-001：hk_trade_calendar 用
``ak.tool_trade_date_hist_sina`` A股日历冒充；#ARCH-CH-INDUSTRY-CLASS-MIGRATE：
industry_class 用 mootdx 板块成分冒充申万行业分级）——全项目无机制校验对齐。

收缩口径（AI-NIGHT-001 包 Q1）：语义注册表以**代码数据结构**承载
（``DEFAULT_SEMANTIC_REGISTRY``，初始 3 条与 17 号 §5.8 定稿一致）——
docs/ 注册表 YAML 落地归 17 号 §5.3 后续治理批；本模块承载 validator 核心规则：
AST 提取 ``_fetch_<cap>`` 方法体外部 API 符号，校验 ⊆ 白名单；
**未登记 capability 不校验**（过度工程防线保留，§5.8）。

依据: 17_special_trading_days_data_assets §5.3/§5.4/§5.8（#ARCH-DATA-002 施工项 2+3）
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: content 参数
#   fields: 参数 content，类型注解 str
#   code: capability_semantic_gate.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: registry 参数
#   fields: 参数 registry，类型注解 tuple[CapabilitySemanticEntry, ...]
#   code: capability_semantic_gate.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: file_path 参数
#   fields: 参数 file_path，类型注解 Path
#   code: capability_semantic_gate.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① check_capability_api_whitelist_content
#   name_en: check_capability_api_whitelist_content
#   intro: 校验 provider 文件内容的 capability-API 语义一致性（17 号 §5.8 项 3）。
#   desc: 校验 provider 文件内容的 capability-API 语义一致性（17 号 §5.8 项 3）。 对已登记 capability：AST 提取 ``_fetch_<c…；源码 L228-L253
#   inputs: content registry
#   outputs: list[str]
# - id: A2
#   name_zh: ② check_capability_api_whitelist
#   name_en: check_capability_api_whitelist
#   intro: 校验 provider 文件的 capability-API 语义一致性（文件读取后委托 content 版）。
#   desc: 校验 provider 文件的 capability-API 语义一致性（文件读取后委托 content 版）。；源码 L256-L265
#   inputs: file_path registry
#   outputs: list[str]
#   （注：A2 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: list[str]
#   name_en: list[str]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: commit gate（capability_validator AST gate 装配批，17 号 §5.4 施工项 3）; 调用方（capability-…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import ast
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

log = logging.getLogger(__name__)

__all__: Final = [
    "CapabilitySemanticEntry",
    "DEFAULT_SEMANTIC_REGISTRY",
    "check_capability_api_whitelist",
    "check_capability_api_whitelist_content",
]


@dataclass(frozen=True)
class CapabilitySemanticEntry:
    """语义锚 + API 白名单（17 号 §5.3 capability_semantic_registry 条目）。"""

    capability_id: str
    market: str  # a_share / hk / us / futures / macro / cross
    variety: str  # stock / etf / index / calendar / classification / ...
    allowed_apis: frozenset[str]  # 精确符号（akshare.tool_trade_date_hist_sina）或前缀通配（THS_*）
    rationale: str = ""


#: 初始登记 3 条（17 号 §5.8 定稿：只对跨市场/跨品种易混淆 capability 强制登记；
#: API 符号按规范模块名书写——akshare./baostock.（非 ak./bs. 别名），提取侧已归一化）
DEFAULT_SEMANTIC_REGISTRY: Final[tuple[CapabilitySemanticEntry, ...]] = (
    CapabilitySemanticEntry(
        capability_id="hk_trade_calendar",
        market="hk",
        variety="calendar",
        allowed_apis=frozenset({"exchange_calendars.XHKG"}),
        rationale="港股日历与A股日历在圣诞/复活节/佛诞差异显著，易错配",
    ),
    CapabilitySemanticEntry(
        capability_id="trade_calendar",
        market="a_share",
        variety="calendar",
        allowed_apis=frozenset(
            {
                "exchange_calendars.XSHG",
                "akshare.tool_trade_date_hist_sina",
                "baostock.query_trade_dates",
            }
        ),
        rationale="A股交易日历主备三源",
    ),
    CapabilitySemanticEntry(
        capability_id="industry_class",
        market="a_share",
        variety="classification",
        allowed_apis=frozenset({"THS_*", "ifind.*"}),
        rationale="mootdx client.block 不在此列 → 拒（防 INDUSTRY-CLASS 重演）",
    ),
)

#: 外部数据源模块集合（17 号 §5.4：ak/bs/xt/THS/exchange_calendars + 常见源；
#: stdlib/pandas 工具调用不在此列，不提取不校验）
_DATA_SOURCE_MODULES: Final[frozenset[str]] = frozenset(
    {
        "akshare",
        "baostock",
        "xtquant",
        "xtdata",
        "exchange_calendars",
        "tushare",
        "yfinance",
        "efinance",
        "mootdx",
        "iFinDPy",
        "THS_iFinD",
        "ifind",
    }
)


def _import_aliases(tree: ast.Module) -> dict[str, str]:
    """import 别名映射（import exchange_calendars as xcals → {xcals: exchange_calendars}）。"""
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                aliases[a.asname or a.name.split(".")[0]] = a.name
    return aliases


def _extract_called_apis(tree: ast.Module, method_name: str, aliases: dict[str, str]) -> set[str]:
    """提取 ``_fetch_<cap>`` 方法体内调用的外部数据源 API 符号集（规范模块名）。

    形态：``<alias>.<attr>(...)`` → ``<module>.<attr>``（alias 归一化为 import 的
    规范模块名，与注册表书写口径一致）；仅提取 ``_DATA_SOURCE_MODULES`` 内模块
    （stdlib/pandas 工具调用不提取）；``exchange_calendars.get_calendar("XHKG")``
    特化为 ``exchange_calendars.XHKG``（日历语义锚在参数而非函数名）。
    """
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for child in node.body:
            if not (isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == method_name):
                continue
            apis: set[str] = set()
            for call in ast.walk(child):
                if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)):
                    continue
                base, attr = call.func.value, call.func.attr
                if not (isinstance(base, ast.Name) and base.id in aliases):
                    continue
                module = aliases[base.id]
                if module.split(".")[0] not in _DATA_SOURCE_MODULES:
                    continue
                if (
                    module == "exchange_calendars"
                    and attr == "get_calendar"
                    and call.args
                    and isinstance(call.args[0], ast.Constant)
                    and isinstance(call.args[0].value, str)
                ):
                    apis.add(f"exchange_calendars.{call.args[0].value}")
                else:
                    apis.add(f"{module}.{attr}")
            return apis
    return set()


def _api_allowed(api: str, whitelist: frozenset[str]) -> bool:
    """白名单匹配：精确命中或 ``*`` 前缀通配（THS_* / ifind.*）。"""
    for w in whitelist:
        if w.endswith("*"):
            if api.startswith(w[:-1]):
                return True
        elif api == w:
            return True
    return False


def check_capability_api_whitelist_content(
    content: str,
    registry: tuple[CapabilitySemanticEntry, ...] = DEFAULT_SEMANTIC_REGISTRY,
) -> list[str]:
    """校验 provider 文件内容的 capability-API 语义一致性（17 号 §5.8 项 3）。

    对已登记 capability：AST 提取 ``_fetch_<cap>`` 方法体外部 API 符号，校验 ⊆
    allowed_apis 白名单；未登记 capability 不校验（过度工程防线）。
    语法错误 fail-open 返回空。
    """
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []
    aliases = _import_aliases(tree)
    violations: list[str] = []
    for entry in registry:
        apis = _extract_called_apis(tree, f"_fetch_{entry.capability_id}", aliases)
        for api in sorted(apis):
            if not _api_allowed(api, entry.allowed_apis):
                violations.append(
                    f"capability '{entry.capability_id}'（{entry.market}/{entry.variety}）"
                    f"调用白名单外 API: {api}（17 号施工项 3：请登记或换 API；"
                    f"白名单 {sorted(entry.allowed_apis)}）"
                )
    return violations


def check_capability_api_whitelist(
    file_path: Path,
    registry: tuple[CapabilitySemanticEntry, ...] = DEFAULT_SEMANTIC_REGISTRY,
) -> list[str]:
    """校验 provider 文件的 capability-API 语义一致性（文件读取后委托 content 版）。"""
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    return check_capability_api_whitelist_content(content, registry)
