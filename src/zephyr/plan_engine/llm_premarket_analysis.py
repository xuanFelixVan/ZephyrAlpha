# [BLUEPRINT] MOD-PLAN-007 | 待统筹登记（92号清单 §8.6 / 44号备忘 §9.14 M3-⑨ + §4 表 M3-⑨ 行）
# [MODULE] zephyr.plan_engine.llm_premarket_analysis
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.shared.io.paths(DB_PATH SSoT); zephyr.shared.io.sqlite_factory(get_db_connection); zephyr.shared.io.serialization(dumps canonical); zephyr.data.ch_reader（默认 CH 读取通道，惰性解析）; zephyr.data.table_registry（表名解析）; 注入契约类型仅 TYPE_CHECKING 引用（MOD-SIG-025/057/058/059/060 输出，运行时鸭子类型读字段）
# [CONSUMERS] 阶段三 llm_runtime_gateway（09架构10号件——本模块=其首个真实消费场景，llm_client 由 gateway 注入）; MOD-PLAN-005 scenario_planner（三情景注解栏，对接口径见 docstring——本单不改 scenario_planner）; 回测 PIT 消费（llm_daily_analysis 表，历史回填留阶段三）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] PIT 铁律①全部输入须"T+1 日 08:00 前可见"（asof_cutoff 护栏：数据点时间戳>cutoff 拒绝入包+rejected 留痕，fail-closed）; 铁律②③ model_version/prompt_version 冻结入库（版本漂移=新型 PIT 风险）; 铁律④ input_hash=输入数据包 canonical JSON 的 SHA-256（回测复现校验同源）; LLM 是"分析参考注解层"不是信号真源——输出只进 M3 情景注解，不直接改边界档位（防幻觉直通交易，与"不预测"纪律一致）; 本模块不直连任何 LLM API（llm_client 可调用对象注入；None→status=skipped_not_wired 落库留痕不炸）; 落库幂等 UNIQUE(trade_date, model_version, prompt_version, input_hash) 同键跳过保首条; SQL 参数化+常量（NO-BARE-SQL）; db_path 默认 None 走 DB_PATH SSoT（测试注入临时库）; 容器常量 Final; 输出纯 dataclass JSON 可序列化
# [MODIFY-GUARD] blueprint.md（待统筹登记）
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] trade_date/asof_cutoff 非法→ValueError fail-closed; CH 单族查询/解析异常→该族降级（字段 None+status 留痕）不炸整体; llm_client 调用异常/返回类型非法/输出契约校验失败→status=invalid 落库留痕不炸; llm_client=None→status=skipped_not_wired 落库留痕不炸; DB 写失败 fail-open（db_logged=False+errors 留痕）
# [TESTS] tests/plan_engine/test_llm_premarket_analysis.py
# [A_module] module_id=MOD-PLAN-007 | layer=module | stability=testing | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

LlmPremarketAnalysis — LLM 盘前综合复盘与当日情景分析核心件 (MOD-PLAN-007)

44号备忘 §9.14 M3-⑨ 落码（92号清单 §8.6 工单）。定位铁律：**LLM 是"分析参考
注解层"不是信号真源**——输出只进 M3 情景注解，不直接改边界档位（防幻觉直通
交易，与 90号 §7"不预测"纪律一致：LLM 给的也是边界/情景，不是方向）。

每日运行时点 = 次日 8:00 盘前（44号 v1.2.1 时点修正：昨日 A 股收盘+隔夜美股
已收+A50 夜盘+夜间新闻齐备，且北京 18:00-次日 9:00 全是 DeepSeek 谷时窗口；
产出正好衔接 MOD-PLAN-002 9:00 边界加载与 9:25 竞价验证）。

七族输入（44号 §9.14，全部"T+1 日 8:00 前可见"，~8-15K token）：
    - 指数族：上证/深成/创业板/科创50 昨涨跌幅+振幅+成交额 vs 20 日均量
      （CH kline_index，T-1 日频）。
    - 情绪族：涨跌家数/涨跌停/炸板率/封板率/昨日涨停今表现（CH kline_daily
      ⋈ stk_limit，T-1/T-2）+ M1 综合情绪分+五阶段（MOD-SIG-025 注入，可缺省）。
    - 板块族：领涨/领跌 Top5+主力资金板块净额 Top5（CH kline_sector_880/
      money_flow⋈sector_constituent）+ 5 状态/虹吸态/电风扇速度计
      （MOD-SIG-060 注入，可缺省）。
    - 衍生族：IF/IM 基差率+贴水速率（MOD-SIG-058 注入）+ 期权 PCR+IV Rank
      （MOD-SIG-059 注入）；未注入=缺省 None（"就绪后"消费，不阻塞）。
    - 外盘族：隔夜 SPX/NDX（CH us_index）+ BS-005 状态（注入）；A50 夜盘/
      昨日 ES/NQ 盘中段/日韩早盘=占位 None（数据源缺口 44号 §6，随 M3-①/
      92号 §7.2/M3-④ 落地后回填）。
    - 资金族：两融Δ/主力净流入/大宗折溢价（CH margin_trading/money_flow/
      block_trade，MOD-PLAN-004 同口径）+ 龙虎榜机构游资净买 Top 标的
      （MOD-SIG-057 注入，可缺省）。
    - 日历族：昨日命中 event_type+今日命中预告（CH calendar_event，静态日历
      提前可知属 PIT 豁免族；event_date>trade_date 拒收入 rejected）。

PIT 回填四铁律（44号 §9.14 回测纪律）：
    ① 输入快照="T+1 日 8:00 前可见"——打包器带 asof_cutoff 参数（默认
       trade_date 当日 08:00，Asia/Shanghai 朴素时间）；datetime 精度数据点
       >cutoff 拒入；日频精度数据点日期 ≥ trade_date 拒入（T 日日频 8:00
       尚不可得）；CH 查询 SQL 层同步带 trade_date < cutoff 日约束（双护栏）。
    ② 模型版本冻结：model_version 入库（默认占位 deepseek-v4-flash-0731，
       真跑以 gateway 注入为准）；版本升级=重新回填+新旧对比登记。
    ③ prompt 模板版本冻结：prompt_version 入库（PROMPT_VERSION 常量
       "pm-v1.0.0"；v2 辩论模式有效版本="pm-v1.0.0+debate"——三套 prompt
       与单调用属不同模板集，版本串分离防幂等键碰撞）。
    ④ input_hash=输入数据包（trade_date+asof_cutoff+families）canonical
       JSON 的 SHA-256——回测复现时校验同源（决策可追溯 P4）。

v1/v2 模式（44号 §9.14，config.debate_mode 开关，默认 False=v1 单调用先跑）：
    - v1 单调用：系统 prompt（角色=盘前分析员；输出纪律=只给情景/风险/关键位，
      不给方向指令）+用户 prompt（数据包注入）→ 一次调用出 JSON。
    - v2 多空辩论（借鉴 TradingAgents prompt 编排，不引入框架本体）：同一数据包
      三调用——①多头角色强制找利多（资金面/情绪修复/外盘支撑）②空头角色强制
      找利空（分歧/炸板/贴水/外围风险）③综合席读双方陈词+数据包裁决三情景概率。
      成本×3 ≈ ￥0.1-0.25/天仍可忽略；v1 跑 3 个月质量不足即升 v2。

输出契约（LlmDailyAnalysis，JSON schema 校验）：
    {date, model_version, prompt_version, input_hash,
     scenarios: {gap_up/flat/gap_down 各 {prob, key_levels, action_boundary}},
     risk_points[], watch_sectors[], confidence_note}
    校验规则：缺字段/三情景键不全/prob 越界 [0,1]/概率和偏离 1 超容差（默认
    ±0.02）/date 与交易日不符/LLM 回显的 model_version/prompt_version/input_hash
    与运行值不一致 → 拒收标 invalid（落库留痕 raw_output），不炸。

LLM 客户端接口注入：llm_client 是可调用对象 prompt→text（str 返回）；或返回
    Mapping {text, tokens_in, tokens_out, cost_yuan} 供计量（gateway 形态）。
    **本模块不直连任何 LLM API**——阶段三 09架构10号 llm_runtime_gateway 就绪后
    由其注入（调用登记对账：模型/版本/token/成本/延迟）；llm_client=None →
    status=skipped_not_wired 落库留痕不炸（本阶段常态）。

落库（governance.db 新表 llm_daily_analysis，92号 D2 授权，DDL-as-Code）：
    id/trade_date/model_version/prompt_version/input_hash/output_json/
    status(success/invalid/skipped_not_wired)/error/tokens_in/tokens_out/
    cost_yuan/latency_ms/created_at + UNIQUE(trade_date, model_version,
    prompt_version, input_hash) 幂等（同键重复写=跳过保首条，返已存在行 id）。
    本模块为 llm_daily_analysis schema 唯一真源；新环境/测试库走
    ensure_llm_daily_analysis_table(db_path) 幂等建表。

消费侧对接口径（44号 §9.14 消费侧；本单只注记不改 scenario_planner）：
    MOD-PLAN-005 scenario_planner 三情景输出将来附 LLM 情景作"注解栏"——
    消费方按 (trade_date, model_version, prompt_version) 读 llm_daily_analysis
    当日 status=success 行取 scenarios，与规则生成情景并列展示；**不一致时以
    规则为准，LLM 栏仅作参考**；回测期统计 LLM 情景命中率，>55% 才讨论升级为
    加权输入（升级需 Owner 裁定）。ScenarioPlan 契约零改动。

不做什么：不直连 LLM API / 不改边界档位（注解层）/ 不做方向点预测 /
         不改 scenario_planner 等既有五件 / 不写注册表（登记去向=统筹裁定）。

依据: 44_premarket_intraday_decision_upgrade §4 M3-⑨ + §9.14；92号清单 §8.6
SSoT: depgraph MOD-PLAN-007（待统筹登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: trade_date + CH 七族日频（kline_index/kline_daily/stk_limit/kline_sector_880/sector_meta/money_flow/sector_constituent/us_index/margin_trading/block_trade/calendar_event）+ 注入契约（MOD-SIG-025/057/058/059/060 输出+bs005）+ llm_client（可缺省）
# 特征: 七族数据包 / input_hash(SHA-256 canonical) / asof_cutoff PIT 护栏 / rejected 留痕
# 算法: 打包（PIT 双护栏：SQL 日期约束+ledger 逐点准入）→ prompt 组装（v1 单调用 / v2 多-空-综合三调用编排）→ llm_client 注入调用 → 输出契约 JSON schema 校验（缺字段/概率和容差拒收）→ llm_daily_analysis 幂等落库
# 输出: LlmRunResult（status=success/invalid/skipped_not_wired + LlmDailyAnalysis + 计量留痕）

"""

from __future__ import annotations

import datetime
import hashlib
import json
import logging
import math
import re
import time
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Final

from zephyr.shared.io.paths import DB_PATH
from zephyr.shared.io.serialization import dumps as _canonical_dumps
from zephyr.shared.io.sqlite_factory import get_db_connection

if TYPE_CHECKING:  # 注入契约类型仅注解用（运行时鸭子类型读字段，缺数据=该族缺省）
    from zephyr.signal_ashare.futures_basis_monitor import FuturesBasisSnapshot
    from zephyr.signal_ashare.lhb_premium_analyzer import LhbPremiumResult
    from zephyr.signal_ashare.market_sentiment_analyzer import MarketSentimentResult
    from zephyr.signal_ashare.option_sentiment import OptionSentimentResult
    from zephyr.signal_ashare.sector_divergence import SectorDivergenceResult

log = logging.getLogger(__name__)

__all__: Final = [
    "LLM_DAILY_ANALYSIS_DDL",
    "LLM_DAILY_ANALYSIS_TABLE",
    "LlmDailyAnalysis",
    "LlmPremarketConfig",
    "LlmRunResult",
    "LlmScenario",
    "PremarketInjections",
    "PremarketPackage",
    "PremarketPackager",
    "PROMPT_VERSION",
    "DEFAULT_MODEL_VERSION",
    "STATUS_INVALID",
    "STATUS_SKIPPED_NOT_WIRED",
    "STATUS_SUCCESS",
    "build_premarket_package",
    "build_user_prompt",
    "ensure_llm_daily_analysis_table",
    "parse_llm_output",
    "run_llm_analysis",
]

# ── 版本与状态常量（44号 §9.14 铁律②③：模型/prompt 版本冻结入库）──

PROMPT_VERSION: Final = "pm-v1.0.0"  # prompt 模板版本（v1 单调用；v2 辩论有效版本=+debate 后缀）
DEFAULT_MODEL_VERSION: Final = "deepseek-v4-flash-0731"  # 模型版本冻结占位（真跑以 gateway 注入为准）

STATUS_SUCCESS: Final = "success"  # 调用成功且输出契约校验通过
STATUS_INVALID: Final = "invalid"  # 调用异常/输出契约校验失败（拒收不炸，落库留痕）
STATUS_SKIPPED_NOT_WIRED: Final = "skipped_not_wired"  # llm_client=None（阶段三 gateway 接线前常态）

# ── 参数常量（44号 §9.14 默认值，全部可经 LlmPremarketConfig 覆盖）──

DEFAULT_CUTOFF_TIME: Final = "08:00"  # PIT 铁律①：T+1 日 08:00 前可见（Asia/Shanghai）
PROB_SUM_TOLERANCE: Final = 0.02  # 三情景概率和容差（偏离 1 超此值→拒收 invalid）
TOP_N: Final = 5  # 板块领涨/领跌/资金净额榜条数
VOLUME_AVG_WINDOW: Final = 20  # 指数成交额/量能 20 日均值窗（44号 §9.14 指数族口径）
INDEX_LOOKBACK_CALENDAR_DAYS: Final = 40  # 指数历史取数自然日窗（覆盖 20 交易日均值窗）
FUND_HISTORY_LIMIT: Final = 21  # 资金族历史行数（T-1 + 20 日均值参照）
US_INDEX_LIMIT: Final = 400  # us_index 查询行数上限（与 MOD-PLAN-004 同口径）
MAX_LHB_PERF_SYMBOLS: Final = 500  # 昨日涨停今表现 IN 清单上限（防 SQL 膨胀）
MAX_RAW_OUTPUT_CHARS: Final = 8000  # invalid 落库 raw_output 截断上限

# 指数族四指数（裸码+带后缀双写法兼容，kline_index 裸码口径实证 2026-08-22）
INDEX_SET: Final = (
    ("000001", "上证指数", ("000001", "000001.SH")),
    ("399001", "深证成指", ("399001", "399001.SZ")),
    ("399006", "创业板指", ("399006", "399006.SZ")),
    ("000688", "科创50", ("000688", "000688.SH")),
)
_INDEX_SYMBOL_IN: Final = ", ".join(f"'{v}'" for _, _, variants in INDEX_SET for v in variants)

# us_index 表 index_code 取值（tickflow_provider：SPX/DJI/IXIC，ETF 替代真实指数；与 MOD-PLAN-004 同口径）
_US_INDEX_SPX_CODES: Final = frozenset({"SPX", "SPY", "SPY.US"})
_US_INDEX_NDX_CODES: Final = frozenset({"IXIC", "NDX", "QQQ", "QQQ.US"})

_SYMBOL_SAFE_RE: Final = re.compile(r"^[A-Za-z0-9.]+$")  # IN 清单符号消毒（防注入）

# ── SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀，与 ch_reader/overnight_boundary_reviser 同约定）──
# PIT 铁律① SQL 层护栏：全部日频查询严格 trade_date < toDate('{trade_date}')（T 日数据 08:00 不可得）

# 近两个交易日定位（T-1/T-2，kline_daily 最新可得口径）
_SQL_PREV_TRADE_DATES: Final = (
    "SELECT DISTINCT trade_date FROM {table} FINAL "
    "WHERE trade_date < toDate('{trade_date}') ORDER BY trade_date DESC LIMIT 2"
)
# 指数族：四指数日K（open/high/low/close/amount/volume），Python 侧按 symbol 分组算涨幅/振幅/量比
_SQL_INDEX_DAILY: Final = (
    "SELECT symbol, name, trade_date, open, high, low, close, amount, volume "
    "FROM {table} FINAL "
    "WHERE symbol IN ({symbols}) AND trade_date < toDate('{trade_date}') "
    "AND trade_date >= toDate('{win_start}') ORDER BY trade_date DESC"
)
# 情绪族：涨跌家数（market_type/quality_flag 过滤与 sector_report_builder 同口径）
_SQL_BREADTH: Final = (
    "SELECT countIf(toFloat64(pct_change) > 0), countIf(toFloat64(pct_change) < 0), "
    "countIf(toFloat64(pct_change) = 0) FROM {table} FINAL "
    "WHERE trade_date = toDate('{prev_date}') AND market_type = 'A_share' AND quality_flag = 1"
)
# 情绪族：涨跌停/曾涨停（炸板分子）——USING 无别名写法（inject_final 注入 FINAL 后语法仍合法）
_SQL_LIMIT_STATS: Final = (
    "SELECT "
    "countIf(toFloat64(close) >= toFloat64(limit_up) - 0.001), "
    "countIf(toFloat64(high) >= toFloat64(limit_up) - 0.001), "
    "countIf(toFloat64(close) <= toFloat64(limit_down) + 0.001) "
    "FROM {kline_table} INNER JOIN {stk_table} USING (symbol_canonical, trade_date) "
    "WHERE trade_date = toDate('{prev_date}')"
)
# 情绪族：昨日（T-2）收盘封涨停名单（与 scenario_planner _SQL_LIMIT_UP_SYMBOLS 同口径）
_SQL_LIMIT_UP_SYMBOLS: Final = (
    "SELECT symbol_canonical FROM {kline_table} INNER JOIN {stk_table} "
    "USING (symbol_canonical, trade_date) "
    "WHERE trade_date = toDate('{t2}') AND limit_up IS NOT NULL "
    "AND toFloat64(close) >= toFloat64(limit_up) - 0.001"
)
# 情绪族：昨日涨停今（T-1）表现（符号清单来自上查，_SYMBOL_SAFE_RE 消毒+数量封顶）
_SQL_LIMIT_UP_NEXT_PERF: Final = (
    "SELECT symbol_canonical, pct_change FROM {table} FINAL "
    "WHERE trade_date = toDate('{t1}') AND symbol_canonical IN ({symbols})"
)
# 板块族：880 板块日K（T-1/T-2 两日行算涨跌幅）
_SQL_SECTOR_KLINE: Final = (
    "SELECT sector_code, trade_date, close FROM {table} FINAL "
    "WHERE period = '1d' AND trade_date IN (toDate('{t2}'), toDate('{t1}'))"
)
# 板块族：板块代码→名称映射（sector_meta，fail-open 缺省不回填名称）
_SQL_SECTOR_NAMES: Final = (
    "SELECT sector_code, argMax(sector_name, trade_date) FROM {table} FINAL "
    "WHERE sector_name != '' GROUP BY sector_code"
)
# 板块族资金净额腿①：money_flow 当日个股主力净流入（symbol_canonical 口径，与 sector_report_builder 一致）
_SQL_MONEY_FLOW_DAY: Final = (
    "SELECT symbol_canonical, main_net_inflow FROM {table} FINAL WHERE trade_date = toDate('{prev_date}')"
)
# 板块族资金净额腿②：880 成分股映射（valid_from/valid_to 有效期口径，与 sector_report_builder 一致）
_SQL_SECTOR_CONSTITUENTS: Final = (
    "SELECT sector_code, stock_code FROM {table} FINAL "
    "WHERE valid_from <= toDate('{prev_date}') AND (valid_to IS NULL OR valid_to > toDate('{prev_date}'))"
)
# 外盘族：us_index 最新收盘序列（Python 侧按 symbol 分组取最新两条算隔夜涨跌幅；
# 2026-08-22 真跑实证修正：表无 index_code 列，真身=symbol（tracker #247 当前空值缺陷期整族降级））
_SQL_US_INDEX: Final = (
    "SELECT trade_date, symbol, close FROM {table} FINAL "
    "WHERE trade_date < toDate('{trade_date}') ORDER BY trade_date DESC LIMIT {limit}"
)
# 资金族：两融融资净买入（margin_buy-margin_repay，MOD-PLAN-004 同口径）
_SQL_MARGIN: Final = (
    "SELECT trade_date, sum(toFloat64(margin_buy) - toFloat64(margin_repay)) AS net_buy "
    "FROM {table} FINAL WHERE trade_date < toDate('{trade_date}') "
    "GROUP BY trade_date ORDER BY trade_date DESC LIMIT {limit}"
)
# 资金族：主力净流入最新日聚合（全市场净额合计+净入占比均值）
_SQL_MONEY_FLOW_AGG: Final = (
    "SELECT trade_date, sum(toFloat64(main_net_inflow)), avg(toFloat64(main_net_inflow_pct)) "
    "FROM {table} FINAL WHERE trade_date < toDate('{trade_date}') "
    "GROUP BY trade_date ORDER BY trade_date DESC LIMIT 1"
)
# 资金族：大宗交易加权折溢价（LEFT JOIN 取当日收盘；USING 无别名写法，MOD-PLAN-004 同口径）
_SQL_BLOCK_PREMIUM: Final = (
    "SELECT trade_date, "
    "sumIf((toFloat64(price) - toFloat64(close)) / toFloat64(close) * toFloat64(amount), toFloat64(close) > 0) "
    "/ sumIf(toFloat64(amount), toFloat64(close) > 0) AS premium "
    "FROM {bt_table} LEFT JOIN {kline_table} USING (symbol, trade_date) "
    "WHERE trade_date < toDate('{trade_date}') AND toFloat64(amount) > 0 "
    "GROUP BY trade_date ORDER BY trade_date DESC LIMIT 1"
)
# 日历族：昨日命中+今日预告（calendar_event 静态日历，PIT 豁免族——事件日历提前可知）
_SQL_CALENDAR: Final = (
    "SELECT event_date, event_type FROM {table} FINAL "
    "WHERE event_date BETWEEN toDate('{win_start}') AND toDate('{trade_date}')"
)

# ── DDL-as-Code（92号 §8.6/D2 授权；本模块为 llm_daily_analysis schema 唯一真源）──

LLM_DAILY_ANALYSIS_TABLE: Final = "llm_daily_analysis"
LLM_DAILY_ANALYSIS_DDL: Final = """
CREATE TABLE IF NOT EXISTS llm_daily_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_date TEXT NOT NULL,               -- 交易日 YYYY-MM-DD
    model_version TEXT NOT NULL,            -- 模型版本（铁律② 冻结入库）
    prompt_version TEXT NOT NULL,           -- prompt 模板版本（铁律③；v2 辩论=+debate 后缀）
    input_hash TEXT NOT NULL,               -- 输入数据包 canonical JSON SHA-256（铁律④）
    output_json TEXT NOT NULL,              -- LLM 输出（canonical JSON；skipped=空串；invalid=raw 留痕）
    status TEXT NOT NULL,                   -- success / invalid / skipped_not_wired
    error TEXT,                             -- 失败原因留痕（可空）
    tokens_in INTEGER,                      -- 输入 token（可空；v2=三调用合计）
    tokens_out INTEGER,                     -- 输出 token（可空；v2=三调用合计）
    cost_yuan REAL,                         -- 成本元（可空；gateway 计量回填）
    latency_ms REAL,                        -- 调用延迟毫秒（v2=三调用合计）
    created_at TEXT NOT NULL,               -- 落库时点 UTC ISO8601
    UNIQUE(trade_date, model_version, prompt_version, input_hash)
)
"""
_DDL_IDX_TRADE_DATE: Final = (
    "CREATE INDEX IF NOT EXISTS idx_llm_daily_analysis_trade_date ON llm_daily_analysis (trade_date)"
)

# 落库 SQL 常量（NO-BARE-SQL 门禁；append-only 仅 INSERT，参数化防注入；同键幂等跳过保首条）
_SQL_INSERT: Final = (
    "INSERT OR IGNORE INTO llm_daily_analysis "
    "(trade_date, model_version, prompt_version, input_hash, output_json, status, "
    "error, tokens_in, tokens_out, cost_yuan, latency_ms, created_at) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
)
_SQL_SELECT_ID_BY_KEY: Final = (
    "SELECT id FROM llm_daily_analysis WHERE trade_date=? AND model_version=? AND prompt_version=? AND input_hash=?"
)

# ── prompt 模板（版本化：PROMPT_VERSION 常量，模板文本改动=版本升级+重跑回填）──

_OUTPUT_SCHEMA_INSTRUCTION: Final = (
    "严格输出 JSON（除此不输出任何文字），schema："
    '{"date":"YYYY-MM-DD","scenarios":{"gap_up":{"prob":0.0,"key_levels":["..."],"action_boundary":"..."},'
    '"flat":{"prob":0.0,"key_levels":["..."],"action_boundary":"..."},'
    '"gap_down":{"prob":0.0,"key_levels":["..."],"action_boundary":"..."}},'
    '"risk_points":["..."],"watch_sectors":["..."],"confidence_note":"..."}'
)

SYSTEM_PROMPT_V1: Final = (
    "你是 A 股盘前分析员。基于给定盘前数据包（仅含截止时点前可见信息，PIT 快照），"
    "输出当日三情景分析。\n"
    "输出纪律（必须遵守）：\n"
    "1. 只输出情景概率、关键位、风险点与关注板块——不给任何方向性交易指令"
    "（不预测涨跌，只画栏杆；action_boundary 为边界语义描述，非买卖指令）。\n"
    f"2. {_OUTPUT_SCHEMA_INSTRUCTION}\n"
    "3. 三情景概率 prob ∈ [0,1] 且三者之和=1（容差 ±0.02）。\n"
    "4. 数据包中为 null 的字段是数据缺口，不得臆造数值，须在 confidence_note 声明。\n"
    "5. date 必须等于数据包交易日。"
)

_SYSTEM_ROLE_BULL: Final = (
    "你是多头角色分析员。基于给定盘前数据包，**强制找利多**：资金面改善/情绪修复/"
    "外盘支撑/板块主线等。只输出一段多头陈词（纯文本，≤400字），不输出 JSON，"
    "不给方向性交易指令。数据包中 null 字段不得臆造。"
)
_SYSTEM_ROLE_BEAR: Final = (
    "你是空头角色分析员。基于给定盘前数据包，**强制找利空**：分歧/炸板/期指贴水/"
    "外围风险/资金流出等。只输出一段空头陈词（纯文本，≤400字），不输出 JSON，"
    "不给方向性交易指令。数据包中 null 字段不得臆造。"
)
_SYSTEM_ROLE_ARBITER: Final = (
    "你是综合席裁决员。读多头与空头双方陈词+原始盘前数据包，裁决当日三情景概率。\n"
    "输出纪律（必须遵守）：\n"
    "1. 只输出情景概率、关键位、风险点与关注板块——不给任何方向性交易指令。\n"
    f"2. {_OUTPUT_SCHEMA_INSTRUCTION}\n"
    "3. 三情景概率 prob ∈ [0,1] 且三者之和=1（容差 ±0.02）。\n"
    "4. null 字段不得臆造；双方陈词只作论据，最终以数据包为准。"
)

_ROLE_TASK_BULL: Final = "输出多头陈词（资金面/情绪修复/外盘支撑，≤400字纯文本）。"
_ROLE_TASK_BEAR: Final = "输出空头陈词（分歧/炸板/贴水/外围风险，≤400字纯文本）。"


# ── 配置契约（44号 §9.14 参数 config 化，默认值取设计真源口径）──


@dataclass(frozen=True)
class LlmPremarketConfig:
    """LLM 盘前分析配置（全参数可调，默认值=44号 §9.14 设计真源口径）。"""

    debate_mode: bool = False  # v2 多空辩论开关（默认 v1 单调用先跑 3 个月验证）
    model_version: str = DEFAULT_MODEL_VERSION  # 模型版本（铁律② 入库；真跑以 gateway 注入为准）
    prompt_version: str = PROMPT_VERSION  # prompt 模板版本（铁律③ 入库）
    cutoff_time: str = DEFAULT_CUTOFF_TIME  # PIT 默认 cutoff 时刻（trade_date 当日 08:00）
    prob_sum_tolerance: float = PROB_SUM_TOLERANCE  # 概率和容差
    top_n: int = TOP_N  # 板块榜条数
    volume_avg_window: int = VOLUME_AVG_WINDOW  # 指数 20 日均量窗
    index_lookback_calendar_days: int = INDEX_LOOKBACK_CALENDAR_DAYS
    fund_history_limit: int = FUND_HISTORY_LIMIT  # 资金族历史行数
    us_index_limit: int = US_INDEX_LIMIT
    max_lhb_perf_symbols: int = MAX_LHB_PERF_SYMBOLS
    max_raw_output_chars: int = MAX_RAW_OUTPUT_CHARS


DEFAULT_CONFIG: Final = LlmPremarketConfig()


# ── 注入契约（七族中"就绪后消费"族的可选注入位，鸭子类型读字段）──


@dataclass(frozen=True)
class PremarketInjections:
    """可注入可缺省的数据契约（None=该源缺省，对应族字段 None+留痕）。

    各字段带各自产出时点（ts/date/timestamp），打包器经 PIT ledger 逐点校验：
    晚于 asof_cutoff 的注入整块拒入 + rejected 留痕（fail-closed）。
    """

    sentiment_result: Any = None  # MOD-SIG-025 MarketSentimentResult（M1 综合情绪分+五阶段）
    sector_divergence: Any = None  # MOD-SIG-060 SectorDivergenceResult（5 状态/虹吸态/电风扇速度计）
    futures_snapshot: Any = None  # MOD-SIG-058 FuturesBasisSnapshot（IF/IM 基差率+贴水速率）
    option_sentiment: Any = None  # MOD-SIG-059 OptionSentimentResult（期权 PCR+IV Rank）
    lhb_result: Any = None  # MOD-SIG-057 LhbPremiumResult（龙虎榜机构游资净买 Top 标的）
    bs005_triggered: bool | None = None  # BS-005 外围冲击状态（None=未知）


# ── 输出契约：数据包 / LLM 分析 / 运行结果（纯 dataclass，JSON 可序列化）──


@dataclass(frozen=True)
class PremarketPackage:
    """盘前数据包（44号 §9.14 七族；input_hash=铁律④ 同源校验锚）。"""

    trade_date: str  # 交易日 YYYY-MM-DD
    asof_cutoff: str  # PIT cutoff（YYYY-MM-DD HH:MM:SS，Asia/Shanghai）
    families: dict[str, Any]  # 七族载荷（index/sentiment/sector/derivatives/overseas/capital/calendar）
    input_hash: str  # canonical JSON({trade_date, asof_cutoff, families}) 的 SHA-256
    rejected: list[dict[str, Any]]  # PIT 拒收留痕（family/field/asof/reason）
    built_at: str  # 打包时点 UTC ISO8601（审计字段，不参与 input_hash）
    trace: dict[str, Any] = field(default_factory=dict)  # 通道状态留痕

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典。"""
        return asdict(self)


@dataclass(frozen=True)
class LlmScenario:
    """单情景（gap_up/flat/gap_down 之一）。"""

    prob: float  # 情景概率 ∈[0,1]
    key_levels: list[str]  # 关键位（字符串清单）
    action_boundary: str  # 操作边界描述（边界语义，非买卖指令）


@dataclass(frozen=True)
class LlmDailyAnalysis:
    """LLM 盘前分析输出契约（44号 §9.14；model/prompt/input_hash 以运行侧权威值为准）。"""

    date: str  # 交易日 YYYY-MM-DD（须等于 trade_date）
    model_version: str  # 模型版本（铁律②）
    prompt_version: str  # prompt 模板版本（铁律③）
    input_hash: str  # 输入数据包哈希（铁律④）
    scenarios: dict[str, LlmScenario]  # gap_up/flat/gap_down 三情景
    risk_points: list[str]  # 风险点清单
    watch_sectors: list[str]  # 关注板块清单
    confidence_note: str  # 置信与数据缺口声明

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典。"""
        return asdict(self)


@dataclass(frozen=True)
class LlmRunResult:
    """run_llm_analysis 运行结果（含落库留痕；不炸语义的载体）。"""

    trade_date: str
    status: str  # success / invalid / skipped_not_wired
    analysis: LlmDailyAnalysis | None  # 校验通过的输出契约（invalid/skipped=None）
    input_hash: str
    model_version: str
    prompt_version: str  # 有效版本（debate_mode 时带 +debate 后缀）
    debate_mode: bool
    tokens_in: int | None
    tokens_out: int | None
    cost_yuan: float | None
    latency_ms: float | None
    row_id: int  # 落库行 id（-1=未落库）
    db_logged: bool  # 落库是否成功（同键幂等跳过也算成功，返已存在行 id）
    errors: list[str]
    package: PremarketPackage

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典。"""
        return asdict(self)


# ── 基础工具 ──


def _parse_tsv(tsv: str, ncols: int) -> list[list[str]]:
    """把 ch_reader.query 返回的 TSV 字符串解析成行列表（ncols 不足跳过该行）。"""
    if not tsv or not tsv.strip():
        return []
    rows: list[list[str]] = []
    for line in tsv.strip().split("\n"):
        vals = line.rstrip("\r").split("\t")
        if len(vals) >= ncols:
            rows.append(vals)
    return rows


def _safe_float(v: Any) -> float | None:
    """安全转 float；失败/NaN/Inf 返回 None（区别于 0.0，供降级判定）。"""
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def _safe_int(v: Any) -> int | None:
    """安全转 int；失败返回 None。"""
    if v is None or isinstance(v, bool):
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _parse_date(v: Any) -> datetime.date | None:
    """日期归一（date/datetime/'YYYY-MM-DD'；非法返回 None）。"""
    if isinstance(v, datetime.datetime):
        return v.date()
    if isinstance(v, datetime.date):
        return v
    try:
        return datetime.date.fromisoformat(str(v).strip()[:10])
    except ValueError:
        return None


def _parse_ts(v: Any) -> datetime.datetime | None:
    """时点归一（datetime/'YYYY-MM-DD HH:MM[:SS]'/ISO/日频；非法返回 None）。

    项目约定：朴素 datetime = Asia/Shanghai（与 futures_basis_monitor._normalize_ts
    同约定）；tz-aware 入参去 tzinfo 按 Asia/Shanghai 口径对待。
    """
    if v is None:
        return None
    if isinstance(v, datetime.datetime):
        return v.replace(tzinfo=None)
    if isinstance(v, datetime.date):
        return datetime.datetime(v.year, v.month, v.day)
    s = str(v).strip().replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(s[:19], fmt)
        except ValueError:
            continue
    return None


def _canon_symbol(sym: str) -> str:
    """symbol 规范化（去交易所后缀，000001.SH→000001）。"""
    return (sym or "").strip().split(".")[0]


# ── PIT 护栏（铁律①：任何数据点时间戳 > cutoff 拒绝入包，fail-closed 并留痕）──


class _PitLedger:
    """PIT 准入台账：逐数据点校验 asof ≤ cutoff；拒收记 rejected 留痕。

    双规则：
        - datetime 精度：ts ≤ cutoff 准入（cutoff 默认 trade_date 08:00）。
        - 日频精度：date < trade_date 准入（T 日日频数据 08:00 尚不可得）。
        - None 时间戳：静态/无时点数据放行（日历族另走 event_date ≤ trade_date 上限校验）。
    """

    def __init__(self, trade_date: datetime.date, cutoff: datetime.datetime) -> None:
        self._trade_date = trade_date
        self._cutoff = cutoff
        self.rejected: list[dict[str, Any]] = []

    def admit_ts(self, family: str, field_name: str, ts: datetime.datetime | None) -> bool:
        """datetime 精度准入校验。"""
        if ts is None:
            return True
        if ts <= self._cutoff:
            return True
        self.rejected.append(
            {
                "family": family,
                "field": field_name,
                "asof": ts.isoformat(sep=" "),
                "reason": f"ts > cutoff({self._cutoff.isoformat(sep=' ')})",
            }
        )
        return False

    def admit_date(self, family: str, field_name: str, d: datetime.date | None) -> bool:
        """日频精度准入校验（date ≥ trade_date 拒入）。"""
        if d is None:
            return True
        if d < self._trade_date:
            return True
        self.rejected.append(
            {
                "family": family,
                "field": field_name,
                "asof": d.isoformat(),
                "reason": f"date >= trade_date({self._trade_date.isoformat()})",
            }
        )
        return False

    def reject(self, family: str, field_name: str, asof: str, reason: str) -> None:
        """显式拒收留痕（日历族 event_date 越界等自定义规则用）。"""
        self.rejected.append({"family": family, "field": field_name, "asof": asof, "reason": reason})


def _normalize_cutoff(
    trade_date: datetime.date,
    asof_cutoff: str | datetime.datetime | None,
    cutoff_time: str,
) -> datetime.datetime:
    """cutoff 归一：None=trade_date 当日 cutoff_time；非法输入 ValueError（fail-closed）。"""
    if asof_cutoff is None:
        try:
            hh, mm = cutoff_time.split(":")[:2]
            return datetime.datetime(trade_date.year, trade_date.month, trade_date.day, int(hh), int(mm))
        except (ValueError, AttributeError) as exc:
            raise ValueError(f"cutoff_time 非法（须 HH:MM）: {cutoff_time!r}") from exc
    ts = _parse_ts(asof_cutoff)
    if ts is None:
        raise ValueError(f"asof_cutoff 非法（须 YYYY-MM-DD[ HH:MM[:SS]] 或 datetime）: {asof_cutoff!r}")
    return ts


def _input_hash(trade_date: str, asof_cutoff: str, families: dict[str, Any]) -> str:
    """铁律④：输入数据包 canonical JSON 的 SHA-256（回测复现同源校验锚）。"""
    payload = {"trade_date": trade_date, "asof_cutoff": asof_cutoff, "families": families}
    canonical = _canonical_dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ── 数据打包器（44号 §9.14 七族输入，全 PIT 护栏）──


class PremarketPackager:
    """盘前数据打包器（MOD-PLAN-007 核心件①）。

    数据经 ch_client 注入（测试 mock/离线）；未注入时走项目默认 CH 通道
    （zephyr.data.ch_reader.query，惰性解析）。单族异常=该族降级不炸整体。
    """

    def __init__(
        self,
        ch_client: Callable[[str], str] | None = None,
        config: LlmPremarketConfig | None = None,
        *,
        asof_cutoff: str | datetime.datetime | None = None,
        injected: PremarketInjections | None = None,
    ) -> None:
        self._config = config or DEFAULT_CONFIG
        self._ch = ch_client  # None → 查询时走 ch_reader.query（惰性解析，离线可导入）
        self._asof_cutoff = asof_cutoff
        self._injected = injected or PremarketInjections()

    # ── 基础设施 ──────────────────────────────────────────────────────────

    @staticmethod
    def _table(category_id: str, fallback: str) -> str:
        """按 category_id 解析全限定表名；注册表不可用降级 fallback（fail-open）。"""
        try:
            from zephyr.data.table_registry import get_registry

            return get_registry().table(category_id)
        except Exception as exc:  # noqa: BLE001 — fail-open：表名解析失败不阻塞主流程
            log.warning("表名解析失败 %s，降级 %s: %s", category_id, fallback, exc)
            return fallback

    def _query(self, sql: str, channel: str, trace: dict[str, Any]) -> str:
        """执行 CH 查询；异常→通道降级空串+留痕（fail-open 不炸整体）。"""
        try:
            if self._ch is not None:
                return self._ch(sql)
            from zephyr.data import ch_reader

            return ch_reader.query(sql)
        except Exception as exc:  # noqa: BLE001 — fail-open：单通道异常不炸整体
            log.warning("通道 %s 查询异常，降级跳过: %s", channel, exc)
            trace["channels"][channel] = f"error:{exc}"
            return ""

    # ── 交易日定位 ────────────────────────────────────────────────────────

    def _prev_trade_dates(self, trade_date: str, ledger: _PitLedger, trace: dict[str, Any]) -> list[str]:
        """近两个交易日 [T-1, T-2]（kline_daily 最新可得口径，逐日行 PIT 准入）。"""
        table = self._table("market_kline_daily", "c1_market.kline_daily")
        tsv = self._query(
            _SQL_PREV_TRADE_DATES.format(table=table, trade_date=trade_date),
            "prev_trade_dates",
            trace,
        )
        dates: list[str] = []
        for (dt,) in _parse_tsv(tsv, 1):
            d = _parse_date(dt)
            if d is None:
                continue
            if ledger.admit_date("calendar_ref", "prev_trade_date", d):
                dates.append(d.isoformat())
        trace["channels"]["prev_trade_dates"] = f"ok:{len(dates)}" if dates else "skipped:no_data"
        return dates

    # ── 指数族（上证/深成/创业板/科创50 昨涨跌幅+振幅+成交额 vs 20 日均量）──

    def _build_index_family(
        self, trade_date: str, d0: datetime.date, ledger: _PitLedger, trace: dict[str, Any]
    ) -> dict[str, Any]:
        cfg = self._config
        win_start = (d0 - datetime.timedelta(days=cfg.index_lookback_calendar_days)).isoformat()
        table = self._table("market_index_kline", "c1_market.kline_index")
        tsv = self._query(
            _SQL_INDEX_DAILY.format(table=table, symbols=_INDEX_SYMBOL_IN, trade_date=trade_date, win_start=win_start),
            "index_kline",
            trace,
        )
        per: dict[str, list[dict[str, Any]]] = {}
        names: dict[str, str] = {}
        for sym, name, dt, _o, h, low, c, amt, vol in _parse_tsv(tsv, 9):
            d = _parse_date(dt)
            canon = _canon_symbol(sym)
            if d is None or not canon:
                continue
            if not ledger.admit_date("index", canon, d):  # PIT 护栏：≥trade_date 的行拒入
                continue
            close, high, low_f = _safe_float(c), _safe_float(h), _safe_float(low)
            if close is None or close <= 0:
                continue
            names.setdefault(canon, (name or "").strip())
            per.setdefault(canon, []).append(
                {
                    "date": d.isoformat(),
                    "close": close,
                    "high": high,
                    "low": low_f,
                    "amount": _safe_float(amt),
                    "volume": _safe_float(vol),
                }
            )

        items: list[dict[str, Any]] = []
        for canon, display, _variants in INDEX_SET:
            rows = sorted(per.get(canon, []), key=lambda r: r["date"], reverse=True)
            if len(rows) < 2:
                items.append(
                    {
                        "symbol": canon,
                        "name": display,
                        "date": rows[0]["date"] if rows else None,
                        "close": rows[0]["close"] if rows else None,
                        "pct_change": None,
                        "amplitude": None,
                        "turnover": None,
                        "turnover_avg_20d": None,
                        "turnover_vs_20d": None,
                        "note": "历史不足两日（degraded）",
                    }
                )
                continue
            t1, t2 = rows[0], rows[1]
            pct = (t1["close"] - t2["close"]) / t2["close"] if t2["close"] > 0 else None
            amplitude = (
                (t1["high"] - t1["low"]) / t2["close"]
                if t1["high"] is not None and t1["low"] is not None and t2["close"] > 0
                else None
            )
            # 成交额 vs 20 日均量：amount 优先（>0 有效），缺失退化 volume 腿（sina 源 amount 缺省 0）
            basis = "amount" if (t1["amount"] or 0) > 0 else "volume"
            cur = t1[basis]
            hist = [r[basis] for r in rows[1 : 1 + cfg.volume_avg_window] if (r[basis] or 0) > 0]
            avg = sum(hist) / len(hist) if hist else None
            ratio = (cur / avg) if cur is not None and avg else None
            items.append(
                {
                    "symbol": canon,
                    "name": names.get(canon) or display,
                    "date": t1["date"],
                    "close": t1["close"],
                    "pct_change": pct,
                    "amplitude": amplitude,
                    "turnover": cur,
                    "turnover_avg_20d": avg,
                    "turnover_vs_20d": ratio,
                    "note": f"turnover_basis={basis}",
                }
            )
        n_ok = sum(1 for it in items if it["pct_change"] is not None)
        trace["channels"]["index_kline"] = f"ok:{n_ok}/{len(INDEX_SET)}" if n_ok else "skipped:no_data"
        return {
            "asof": max((it["date"] for it in items if it["date"]), default=None),
            "items": items,
            "status": "ok" if n_ok == len(INDEX_SET) else ("degraded:partial" if n_ok else "degraded:no_data"),
        }

    # ── 情绪族（涨跌家数/涨跌停/炸板率/封板率/昨日涨停今表现 + M1 分注入）──

    def _build_sentiment_family(
        self, prev_dates: list[str], ledger: _PitLedger, trace: dict[str, Any]
    ) -> dict[str, Any]:
        family: dict[str, Any] = {
            "asof": prev_dates[0] if prev_dates else None,
            "advance_count": None,
            "decline_count": None,
            "flat_count": None,
            "limit_up_count": None,
            "limit_down_count": None,
            "attempted_up_count": None,
            "break_rate": None,  # 炸板率 = (曾涨停-封住)/曾涨停
            "seal_rate": None,  # 封板率 = 封住/曾涨停
            "yesterday_limit_up_perf": None,  # 昨日（T-2）涨停今（T-1）表现
            "m1_overall_score": None,  # M1 综合情绪分（MOD-SIG-025 注入）
            "m1_phase": None,  # M1 五阶段（注入）
            "status": "ok",
        }
        notes: list[str] = []

        # M1 综合情绪分+五阶段（注入，与 CH 链路无关先处理；PIT：timestamp ≤ cutoff 才准入）
        m1 = self._injected.sentiment_result
        if m1 is not None:
            ts = _parse_ts(getattr(m1, "timestamp", None))
            if ledger.admit_ts("sentiment", "m1_result", ts):
                family["m1_overall_score"] = _safe_float(getattr(m1, "overall_score", None))
                family["m1_phase"] = getattr(m1, "sentiment_phase", None)
            else:
                notes.append("M1 情绪分注入超 cutoff 拒入（PIT）")
                family["status"] = "degraded:pit_rejected"

        if not prev_dates:
            family["status"] = "degraded:no_prev_date" if family["status"] == "ok" else family["status"]
            if notes:
                family["notes"] = notes
            return family
        t1 = prev_dates[0]
        kline = self._table("market_kline_daily", "c1_market.kline_daily")
        stk = self._table("market_stk_limit", "c1_market.stk_limit")

        # 涨跌家数
        rows = _parse_tsv(self._query(_SQL_BREADTH.format(table=kline, prev_date=t1), "breadth", trace), 3)
        if rows:
            family["advance_count"] = _safe_int(rows[0][0])
            family["decline_count"] = _safe_int(rows[0][1])
            family["flat_count"] = _safe_int(rows[0][2])
        else:
            notes.append("涨跌家数缺失")

        # 涨跌停/炸板率/封板率
        rows = _parse_tsv(
            self._query(
                _SQL_LIMIT_STATS.format(kline_table=kline, stk_table=stk, prev_date=t1),
                "limit_stats",
                trace,
            ),
            3,
        )
        if rows:
            sealed_up = _safe_int(rows[0][0])
            attempted = _safe_int(rows[0][1])
            family["limit_up_count"] = sealed_up
            family["attempted_up_count"] = attempted
            family["limit_down_count"] = _safe_int(rows[0][2])
            if attempted:
                family["seal_rate"] = round((sealed_up or 0) / attempted, 4)
                family["break_rate"] = round(max(0, attempted - (sealed_up or 0)) / attempted, 4)
        else:
            notes.append("涨跌停统计缺失")

        # 昨日涨停今表现（T-2 封板名单 → T-1 涨跌幅均值）
        if len(prev_dates) >= 2:
            t2 = prev_dates[1]
            sym_rows = _parse_tsv(
                self._query(
                    _SQL_LIMIT_UP_SYMBOLS.format(kline_table=kline, stk_table=stk, t2=t2),
                    "limit_up_symbols",
                    trace,
                ),
                1,
            )
            symbols = [r[0].strip() for r in sym_rows if _SYMBOL_SAFE_RE.match(r[0].strip())]
            symbols = symbols[: self._config.max_lhb_perf_symbols]
            if symbols:
                perf_rows = _parse_tsv(
                    self._query(
                        _SQL_LIMIT_UP_NEXT_PERF.format(
                            table=kline, t1=t1, symbols=", ".join(f"'{s}'" for s in symbols)
                        ),
                        "limit_up_next_perf",
                        trace,
                    ),
                    2,
                )
                gains = [v for _, p in perf_rows if (v := _safe_float(p)) is not None]
                if gains:
                    family["yesterday_limit_up_perf"] = {
                        "date_t2": t2,
                        "count": len(gains),
                        "avg_pct_change": round(sum(gains) / len(gains), 4),
                    }
                else:
                    notes.append("昨日涨停今表现无有效涨幅")
            else:
                notes.append("昨日无涨停名单")

        if notes:
            family["notes"] = notes
            if family["status"] == "ok" and family["advance_count"] is None:
                family["status"] = "degraded:partial"
        return family

    # ── 板块族（领涨领跌 Top5 + 主力资金板块净额 Top5 + 5 状态/虹吸/电风扇注入）──

    def _build_sector_family(self, prev_dates: list[str], ledger: _PitLedger, trace: dict[str, Any]) -> dict[str, Any]:
        cfg = self._config
        family: dict[str, Any] = {
            "asof": prev_dates[0] if prev_dates else None,
            "top_gainers": None,
            "top_losers": None,
            "sector_money_flow_top": None,  # 主力资金板块净额 Top5（亿元）
            "rotation_state": None,  # 5 状态（MOD-SIG-060 注入）
            "siphon_z": None,
            "siphon_flag": None,
            "rotation_velocity": None,  # 电风扇速度计
            "velocity_percentile": None,
            "fan_market_flag": None,
            "top_risk_flag": None,
            "status": "ok",
        }
        notes: list[str] = []
        names = self._sector_names(trace)

        if len(prev_dates) >= 2:
            t1, t2 = prev_dates[0], prev_dates[1]
            table = self._table("market_sector_kline_880", "c1_market.kline_sector_880")
            rows = _parse_tsv(
                self._query(_SQL_SECTOR_KLINE.format(table=table, t1=t1, t2=t2), "sector_kline", trace),
                3,
            )
            closes: dict[str, dict[str, float]] = {}
            for code, dt, close_s in rows:
                d = _parse_date(dt)
                close = _safe_float(close_s)
                if d is None or close is None or close <= 0:
                    continue
                if not ledger.admit_date("sector", (code or "").strip(), d):
                    continue
                closes.setdefault((code or "").strip(), {})[d.isoformat()] = close
            changes: list[tuple[str, float]] = []
            for code, by_date in closes.items():
                c1, c2 = by_date.get(t1), by_date.get(t2)
                if c1 is not None and c2 is not None and c2 > 0:
                    changes.append((code, (c1 - c2) / c2))
            if changes:
                changes.sort(key=lambda x: x[1], reverse=True)
                family["top_gainers"] = [
                    {"sector_code": c, "name": names.get(c), "pct_change": round(p, 4)} for c, p in changes[: cfg.top_n]
                ]
                family["top_losers"] = [
                    {"sector_code": c, "name": names.get(c), "pct_change": round(p, 4)}
                    for c, p in changes[-cfg.top_n :][::-1]
                ]
            else:
                notes.append("板块涨跌幅缺失（K线不足两日）")

            # 主力资金板块净额 Top5（money_flow ⋈ sector_constituent，Python 侧聚合）
            mf_rows = _parse_tsv(
                self._query(
                    _SQL_MONEY_FLOW_DAY.format(
                        table=self._table("market_money_flow", "c1_market.money_flow"), prev_date=t1
                    ),
                    "money_flow_day",
                    trace,
                ),
                2,
            )
            flow_map = {
                (s or "").strip(): v for s, mf in mf_rows if (v := _safe_float(mf)) is not None and (s or "").strip()
            }
            cs_rows = _parse_tsv(
                self._query(
                    _SQL_SECTOR_CONSTITUENTS.format(
                        table=self._table("market_sector_constituent_880", "c1_market.sector_constituent"),
                        prev_date=t1,
                    ),
                    "sector_constituents",
                    trace,
                ),
                2,
            )
            members: dict[str, list[str]] = {}
            for code, stock in cs_rows:
                code, stock = (code or "").strip(), (stock or "").strip()
                if code and stock:
                    members.setdefault(code, []).append(stock)
            sector_net = {code: sum(flow_map[s] for s in stocks if s in flow_map) for code, stocks in members.items()}
            sector_net = {
                c: v for c, v in sector_net.items() if members.get(c) and any(s in flow_map for s in members[c])
            }
            if sector_net:
                top = sorted(sector_net.items(), key=lambda x: x[1], reverse=True)[: cfg.top_n]
                # money_flow 万元口径（sector_report_builder 实证 yi_unit=1e4）→ 亿元
                family["sector_money_flow_top"] = [
                    {"sector_code": c, "name": names.get(c), "net_inflow_yi": round(v / 1e4, 4)} for c, v in top
                ]
            else:
                notes.append("主力资金板块净额缺失")
        else:
            family["status"] = "degraded:no_prev_date"

        # 5 状态/虹吸态/电风扇速度计（MOD-SIG-060 注入，PIT：date < trade_date）
        div = self._injected.sector_divergence
        if div is not None:
            d = _parse_date(getattr(div, "date", None))
            if ledger.admit_date("sector", "sector_divergence", d):
                family["rotation_state"] = getattr(div, "rotation_state", None)
                family["siphon_z"] = _safe_float(getattr(div, "siphon_z", None))
                family["siphon_flag"] = getattr(div, "siphon_flag", None)
                family["rotation_velocity"] = _safe_float(getattr(div, "rotation_velocity", None))
                family["velocity_percentile"] = _safe_float(getattr(div, "velocity_percentile", None))
                family["fan_market_flag"] = getattr(div, "fan_market_flag", None)
                family["top_risk_flag"] = getattr(div, "top_risk_flag", None)
            else:
                notes.append("板块分歧度注入日期越界拒入（PIT）")
                family["status"] = "degraded:pit_rejected"

        if notes:
            family["notes"] = notes
            if family["status"] == "ok" and family["top_gainers"] is None:
                family["status"] = "degraded:partial"
        return family

    def _sector_names(self, trace: dict[str, Any]) -> dict[str, str]:
        """板块代码→名称映射（sector_meta，fail-open 缺省空表）。"""
        table = self._table("market_sector_meta", "c1_market.sector_meta")
        rows = _parse_tsv(self._query(_SQL_SECTOR_NAMES.format(table=table), "sector_meta", trace), 2)
        return {(c or "").strip(): (n or "").strip() for c, n in rows if (c or "").strip()}

    # ── 衍生族（MOD-SIG-058/059 注入，可缺省；PIT 逐源校验）──

    def _build_derivatives_family(self, ledger: _PitLedger) -> dict[str, Any]:
        family: dict[str, Any] = {
            "if_basis_rate": None,
            "if_basis_vel_30m": None,
            "im_basis_rate": None,
            "im_basis_vel_30m": None,
            "futures_delivery_week": None,
            "option_pcr": None,
            "option_pcr_percentile": None,
            "option_iv_rank": None,
            "option_iv_jump": None,
            "option_skew_norm": None,
            "status": "not_injected",
        }
        notes: list[str] = []
        snap = self._injected.futures_snapshot
        if snap is not None:
            ts = _parse_ts(getattr(snap, "ts", None))
            if ledger.admit_ts("derivatives", "futures_snapshot", ts):
                per_symbol = getattr(snap, "per_symbol", None) or {}
                for product, prefix in (("IF", "if"), ("IM", "im")):
                    sym = per_symbol.get(product)
                    if sym is None:
                        continue
                    family[f"{prefix}_basis_rate"] = _safe_float(getattr(sym, "basis_rate", None))
                    family[f"{prefix}_basis_vel_30m"] = _safe_float(getattr(sym, "basis_vel_30m", None))
                family["futures_delivery_week"] = getattr(snap, "delivery_week", None)
                family["status"] = "ok"
            else:
                notes.append("期指基差注入超 cutoff 拒入（PIT）")
                family["status"] = "degraded:pit_rejected"
        opt = self._injected.option_sentiment
        if opt is not None:
            d = _parse_date(getattr(opt, "date", None))
            if ledger.admit_date("derivatives", "option_sentiment", d):
                family["option_pcr"] = _safe_float(getattr(opt, "pcr", None))
                family["option_pcr_percentile"] = _safe_float(getattr(opt, "pcr_percentile", None))
                family["option_iv_rank"] = _safe_float(getattr(opt, "iv_rank", None))
                family["option_iv_jump"] = getattr(opt, "iv_jump_flag", None)
                family["option_skew_norm"] = _safe_float(getattr(opt, "skew_norm", None))
                if family["status"] == "not_injected":
                    family["status"] = "ok"
            else:
                notes.append("期权情绪注入日期越界拒入（PIT）")
                family["status"] = "degraded:pit_rejected"
        if notes:
            family["notes"] = notes
        return family

    # ── 外盘族（隔夜 SPX/NDX + BS-005；A50/ES-NQ/日韩=数据源缺口占位）──

    def _build_overseas_family(self, trade_date: str, ledger: _PitLedger, trace: dict[str, Any]) -> dict[str, Any]:
        cfg = self._config
        table = self._table("market_us_index", "c1_market.us_index")
        tsv = self._query(
            _SQL_US_INDEX.format(table=table, trade_date=trade_date, limit=cfg.us_index_limit),
            "us_index",
            trace,
        )
        series: dict[str, list[tuple[str, float]]] = {}
        for dt, code, close_s in _parse_tsv(tsv, 3):
            d = _parse_date(dt)
            code = (code or "").strip()
            close = _safe_float(close_s)
            if d is None or not code or close is None or close <= 0:
                continue  # 实证缺陷：symbol 空值行剔除（tracker #247，与 MOD-PLAN-004 同口径）
            if not ledger.admit_date("overseas", code, d):  # PIT 护栏
                continue
            series.setdefault(code, []).append((d.isoformat(), close))
        for code in series:
            series[code] = sorted(series[code], key=lambda x: x[0], reverse=True)[:2]

        def _ret(codes: frozenset[str]) -> dict[str, Any] | None:
            for c in series:
                if c in codes and len(series[c]) >= 2 and series[c][1][1] > 0:
                    (d1, c1), (d0, c0) = series[c][0], series[c][1]
                    return {"index_code": c, "date": d1, "pct_change": (c1 - c0) / c0}
            return None

        family = {
            "asof": max((s[0][0] for s in series.values() if s), default=None),
            "spx": _ret(_US_INDEX_SPX_CODES),
            "ndx": _ret(_US_INDEX_NDX_CODES),
            "a50_night": None,  # 数据源缺口（44号 §6，随 M3-① akshare 接口评估落地）
            "es_nq_intraday": None,  # 昨日 ES/NQ 盘中段（采集待 92号 §7.2 落地）
            "japan_korea_early": None,  # 日韩早盘 8 点参考（M3-④ Phase 3）
            "bs005_triggered": self._injected.bs005_triggered,  # BS-005 外围冲击状态（注入）
            "status": "ok" if series else "degraded:no_data",
        }
        return family

    # ── 资金族（两融Δ/主力净流入/大宗折溢价 + 龙虎榜注入）──

    def _build_capital_family(self, trade_date: str, ledger: _PitLedger, trace: dict[str, Any]) -> dict[str, Any]:
        cfg = self._config
        family: dict[str, Any] = {
            "asof": None,
            "margin": None,  # {date, net_buy, delta_vs_prev, avg_20d}
            "main_force": None,  # {date, net_inflow, net_inflow_pct_avg}
            "block_trade": None,  # {date, premium_rate}
            "lhb": None,  # MOD-SIG-057 注入：机构/游资净买 Top 标的
            "status": "ok",
        }
        notes: list[str] = []

        # 两融Δ（融资净买入 T-1 + 对 T-2 增量 + 20 日均值）
        table = self._table("market_margin_trading", "c1_market.margin_trading")
        rows = _parse_tsv(
            self._query(
                _SQL_MARGIN.format(table=table, trade_date=trade_date, limit=cfg.fund_history_limit),
                "margin_trading",
                trace,
            ),
            2,
        )
        nets: list[tuple[str, float]] = []
        for dt, s in rows:
            d = _parse_date(dt)
            v = _safe_float(s)
            if d is None or v is None:
                continue
            if ledger.admit_date("capital", "margin_trading", d):
                nets.append((d.isoformat(), v))
        if nets:
            latest_date, latest = nets[0]
            delta = (latest - nets[1][1]) if len(nets) >= 2 else None
            hist = [v for _, v in nets[1:]]
            family["margin"] = {
                "date": latest_date,
                "net_buy": latest,
                "delta_vs_prev": delta,
                "avg_20d": (sum(hist) / len(hist)) if hist else None,
            }
            family["asof"] = latest_date
        else:
            notes.append("两融数据缺失")

        # 主力净流入（全市场最新日聚合）
        rows = _parse_tsv(
            self._query(
                _SQL_MONEY_FLOW_AGG.format(
                    table=self._table("market_money_flow", "c1_market.money_flow"),
                    trade_date=trade_date,
                ),
                "money_flow_agg",
                trace,
            ),
            3,
        )
        if rows:
            d = _parse_date(rows[0][0])
            if d is not None and ledger.admit_date("capital", "money_flow", d):
                family["main_force"] = {
                    "date": d.isoformat(),
                    "net_inflow": _safe_float(rows[0][1]),
                    "net_inflow_pct_avg": _safe_float(rows[0][2]),
                }
                family["asof"] = family["asof"] or d.isoformat()
        else:
            notes.append("主力资金流缺失")

        # 大宗交易折溢价（MOD-PLAN-004 同口径）
        rows = _parse_tsv(
            self._query(
                _SQL_BLOCK_PREMIUM.format(
                    bt_table=self._table("market_block_trade", "c1_market.block_trade"),
                    kline_table=self._table("market_kline_daily", "c1_market.kline_daily"),
                    trade_date=trade_date,
                ),
                "block_trade",
                trace,
            ),
            2,
        )
        if rows:
            d = _parse_date(rows[0][0])
            if d is not None and ledger.admit_date("capital", "block_trade", d):
                family["block_trade"] = {"date": d.isoformat(), "premium_rate": _safe_float(rows[0][1])}
        else:
            notes.append("大宗交易数据缺失")

        # 龙虎榜机构游资净买 Top 标的（MOD-SIG-057 注入，PIT：date < trade_date）
        lhb = self._injected.lhb_result
        if lhb is not None:
            d = _parse_date(getattr(lhb, "date", None))
            if ledger.admit_date("capital", "lhb_result", d):
                family["lhb"] = {
                    "date": d.isoformat() if d else None,
                    "high_open_candidates": list(getattr(lhb, "high_open_candidates", None) or []),
                    "low_open_risks": list(getattr(lhb, "low_open_risks", None) or []),
                    "fanhe_watchlist": list(getattr(lhb, "fanhe_watchlist", None) or []),
                }
            else:
                notes.append("龙虎榜注入日期越界拒入（PIT）")
                family["status"] = "degraded:pit_rejected"

        if notes:
            family["notes"] = notes
            if family["margin"] is None and family["main_force"] is None and family["block_trade"] is None:
                family["status"] = "degraded:no_data" if family["status"] == "ok" else family["status"]
        return family

    # ── 日历族（昨日命中+今日预告；静态日历 PIT 豁免，event_date ≤ trade_date 上限）──

    def _build_calendar_family(
        self, trade_date: str, prev_dates: list[str], ledger: _PitLedger, trace: dict[str, Any]
    ) -> dict[str, Any]:
        d0 = datetime.date.fromisoformat(trade_date)
        # 窗口：昨日命中需 T-1 日（prev_dates 缺省时退化仅今日预告）
        win_start = prev_dates[0] if prev_dates else trade_date
        table = self._table("market_calendar_event", "c1_market.calendar_event")
        rows = _parse_tsv(
            self._query(
                _SQL_CALENDAR.format(table=table, win_start=win_start, trade_date=trade_date),
                "calendar_event",
                trace,
            ),
            2,
        )
        yesterday: list[dict[str, str]] = []
        today: list[dict[str, str]] = []
        t1 = prev_dates[0] if prev_dates else None
        for dt, etype in rows:
            d = _parse_date(dt)
            etype = (etype or "").strip()
            if d is None or not etype:
                continue
            if d > d0:  # 日历族上限：预告不超今日（>trade_date 拒入留痕）
                ledger.reject("calendar", etype, d.isoformat(), "event_date > trade_date")
                continue
            entry = {"event_date": d.isoformat(), "event_type": etype}
            if t1 is not None and d.isoformat() == t1:
                yesterday.append(entry)
            elif d.isoformat() == trade_date:
                today.append(entry)
        return {
            "yesterday_hits": yesterday,
            "today_preview": today,
            "status": "ok" if rows else "degraded:no_data",  # 空表静默跳过（44号 §9.12 fail-open）
        }

    # ── 主合成 ────────────────────────────────────────────────────────────

    def build(self, trade_date: str | datetime.date) -> PremarketPackage:
        """打包七族盘前数据（PIT 铁律① 全护栏；单族异常降级不炸整体）。

        Args:
            trade_date: 交易日（ISO 字符串或 date；非法抛 ValueError——ERROR_CONTRACT）。

        Returns:
            PremarketPackage：七族载荷 + input_hash（铁律④）+ rejected 留痕。
        """
        if isinstance(trade_date, str):
            d0 = datetime.date.fromisoformat(trade_date)  # 非法日期抛 ValueError
        elif isinstance(trade_date, datetime.date):
            d0 = trade_date
        else:
            raise ValueError(f"trade_date 非法（须 YYYY-MM-DD 字符串或 date）: {trade_date!r}")
        iso = d0.isoformat()
        cutoff = _normalize_cutoff(d0, self._asof_cutoff, self._config.cutoff_time)
        ledger = _PitLedger(d0, cutoff)
        trace: dict[str, Any] = {"channels": {}}

        prev_dates = self._prev_trade_dates(iso, ledger, trace)

        builders = (
            ("index", lambda: self._build_index_family(iso, d0, ledger, trace)),
            ("sentiment", lambda: self._build_sentiment_family(prev_dates, ledger, trace)),
            ("sector", lambda: self._build_sector_family(prev_dates, ledger, trace)),
            ("derivatives", lambda: self._build_derivatives_family(ledger)),
            ("overseas", lambda: self._build_overseas_family(iso, ledger, trace)),
            ("capital", lambda: self._build_capital_family(iso, ledger, trace)),
            ("calendar", lambda: self._build_calendar_family(iso, prev_dates, ledger, trace)),
        )
        families: dict[str, Any] = {}
        for name, fn in builders:
            try:
                families[name] = fn()
            except Exception as exc:  # noqa: BLE001 — fail-open：单族异常不炸整体
                log.warning("族 %s 打包异常，降级: %s", name, exc)
                trace["channels"][name] = f"error:{exc}"
                families[name] = {"status": f"error:{exc}"}

        cutoff_s = cutoff.isoformat(sep=" ")
        return PremarketPackage(
            trade_date=iso,
            asof_cutoff=cutoff_s,
            families=families,
            input_hash=_input_hash(iso, cutoff_s, families),
            rejected=ledger.rejected,
            built_at=datetime.datetime.now(datetime.UTC).isoformat(),
            trace=trace,
        )


def build_premarket_package(
    trade_date: str | datetime.date,
    ch_client: Callable[[str], str] | None = None,
    config: LlmPremarketConfig | None = None,
    *,
    asof_cutoff: str | datetime.datetime | None = None,
    injected: PremarketInjections | None = None,
) -> PremarketPackage:
    """盘前数据打包主入口（MOD-PLAN-007 核心件①）。

    Args:
        trade_date: 交易日（ISO 字符串或 date）。
        ch_client: CH 查询客户端（sql→TSV），可注入（测试 mock/离线）；
            None 时走项目默认 CH 通道（zephyr.data.ch_reader.query）。
        config: 参数配置（None=44号 §9.14 设计真源默认值）。
        asof_cutoff: PIT cutoff（None=trade_date 当日 08:00，Asia/Shanghai）——
            铁律①：任何数据点时间戳 > cutoff 拒绝入包（fail-closed+rejected 留痕）。
        injected: 可注入可缺省契约（MOD-SIG-025/057/058/059/060 输出+BS-005 状态）。

    Returns:
        PremarketPackage（input_hash=canonical JSON SHA-256，铁律④）。
    """
    return PremarketPackager(ch_client=ch_client, config=config, asof_cutoff=asof_cutoff, injected=injected).build(
        trade_date
    )


# ── prompt 组装（版本化模板；v1 单调用 / v2 多-空-综合三调用编排）──


def build_user_prompt(
    package: PremarketPackage,
    *,
    role_instruction: str | None = None,
    debate_transcripts: dict[str, str] | None = None,
) -> str:
    """用户 prompt：数据包注入（canonical JSON）+ 可选角色任务/多空陈词。

    Args:
        package: 盘前数据包（families 以 canonical JSON 注入，PIT 时点声明随附）。
        role_instruction: v2 辩论角色任务（多头/空头）；None=v1 综合调用。
        debate_transcripts: 综合席输入 {"bull": 多头陈词, "bear": 空头陈词}。
    """
    parts = [
        f"【盘前数据包】交易日 {package.trade_date}，数据截至 {package.asof_cutoff}"
        "（PIT 快照：仅含该时点前可见信息；null=数据缺口，不得臆造）：",
        _canonical_dumps(package.families, ensure_ascii=False, sort_keys=True, indent=2),
    ]
    if role_instruction:
        parts.append(f"【角色任务】{role_instruction}")
    if debate_transcripts:
        parts.append(f"【多头陈词】\n{debate_transcripts.get('bull', '')}")
        parts.append(f"【空头陈词】\n{debate_transcripts.get('bear', '')}")
    return "\n".join(parts)


# ── LLM 调用（llm_client 注入；本模块不直连任何 LLM API）──


@dataclass(frozen=True)
class _LlmReply:
    """单次调用归一结果（text + 可选计量 + 实际服务模型）。"""

    text: str
    tokens_in: int | None
    tokens_out: int | None
    cost_yuan: float | None
    latency_ms: float
    model: str | None = None  # 实际服务模型（gateway 降级链真实通道模型，铁律②真值）


def _invoke_llm(
    role: str,
    llm_client: Callable[[str], Any],
    prompt: str,
    errors: list[str],
) -> _LlmReply | None:
    """调用注入的 llm_client（prompt→text 或 Mapping 计量形态）；异常/类型非法→None+errors 留痕。

    llm_client 契约（阶段三 gateway 注入形态）：
        - str 返回：纯文本（计量字段 None）。
        - Mapping 返回：{"text": str, "tokens_in"?: int, "tokens_out"?: int, "cost_yuan"?: float}。
    """
    t0 = time.perf_counter()
    try:
        raw = llm_client(prompt)
    except Exception as exc:  # noqa: BLE001 — 不炸：标 invalid 落库留痕
        errors.append(f"llm_call_failed:{role}: {exc!r}")
        return None
    latency = (time.perf_counter() - t0) * 1000.0
    if isinstance(raw, str):
        return _LlmReply(text=raw, tokens_in=None, tokens_out=None, cost_yuan=None, latency_ms=latency)
    if isinstance(raw, Mapping):
        return _LlmReply(
            text=str(raw.get("text", "")),
            tokens_in=_safe_int(raw.get("tokens_in")),
            tokens_out=_safe_int(raw.get("tokens_out")),
            cost_yuan=_safe_float(raw.get("cost_yuan")),
            latency_ms=latency,
            model=(str(raw["model"]) if raw.get("model") else None),
        )
    errors.append(f"llm_reply_type_illegal:{role}: {type(raw).__name__}")
    return None


# ── 输出契约校验（JSON schema：缺字段/概率和容差 → 拒收标 invalid 不炸）──

_SCENARIO_KEYS: Final = ("gap_up", "flat", "gap_down")
_REQUIRED_TOP_KEYS: Final = ("date", "scenarios", "risk_points", "watch_sectors", "confidence_note")


def _extract_json(text: str) -> dict[str, Any]:
    """从 LLM 文本提取首个 JSON 对象（容忍 ```json 围栏/前后杂文）。"""
    t = (text or "").strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    try:
        obj = json.loads(t)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        obj = None
        for i, ch in enumerate(t):
            if ch != "{":
                continue
            try:
                obj, _ = decoder.raw_decode(t[i:])
                break
            except json.JSONDecodeError:
                continue
        if obj is None:
            raise ValueError("输出中未找到 JSON 对象") from None
    if not isinstance(obj, dict):
        raise ValueError(f"输出 JSON 非对象: {type(obj).__name__}")
    return obj


def _coerce_str_list(v: Any, field_name: str, errors: list[str]) -> list[str]:
    """list 字段校验（元素强转 str）；非 list → errors 留痕并返回空清单。"""
    if not isinstance(v, list):
        errors.append(f"{field_name} 须为 list: {type(v).__name__}")
        return []
    return [str(x) for x in v]


def parse_llm_output(
    text: str,
    *,
    trade_date: str,
    input_hash: str,
    model_version: str,
    prompt_version: str,
    prob_sum_tolerance: float = PROB_SUM_TOLERANCE,
) -> tuple[LlmDailyAnalysis | None, list[str]]:
    """LLM 输出 → 输出契约（JSON schema 校验；拒收不炸，返回 (None, errors)）。

    校验规则（44号 §9.14 输出契约）：
        - 顶层缺字段（date/scenarios/risk_points/watch_sectors/confidence_note）→ 拒收。
        - scenarios 须恰含 gap_up/flat/gap_down 三键，各含 prob/key_levels/action_boundary。
        - prob ∈ [0,1] 且三者和偏离 1 超 prob_sum_tolerance → 拒收。
        - date 须等于 trade_date。
        - LLM 回显的 model_version/prompt_version/input_hash（如有）须与运行值一致；
          最终契约字段恒取运行侧权威值（铁律②③④，不信 LLM 回显）。
    """
    errors: list[str] = []
    try:
        obj = _extract_json(text)
    except ValueError as exc:
        return None, [f"json_extract_failed: {exc}"]

    for key in _REQUIRED_TOP_KEYS:
        if key not in obj:
            errors.append(f"缺字段: {key}")
    if errors:
        return None, errors

    if str(obj.get("date", "")).strip() != trade_date:
        errors.append(f"date 与交易日不符: {obj.get('date')!r} != {trade_date}")

    scenarios_obj = obj.get("scenarios")
    scenarios: dict[str, LlmScenario] = {}
    prob_sum = 0.0
    if not isinstance(scenarios_obj, dict):
        errors.append("scenarios 须为对象")
    else:
        extra = set(scenarios_obj) - set(_SCENARIO_KEYS)
        if extra:
            errors.append(f"scenarios 含未知情景键: {sorted(extra)}")
        for key in _SCENARIO_KEYS:
            entry = scenarios_obj.get(key)
            if not isinstance(entry, dict):
                errors.append(f"scenarios.{key} 缺失或非法")
                continue
            prob = entry.get("prob")
            if isinstance(prob, bool) or not isinstance(prob, (int, float)) or not math.isfinite(prob):
                errors.append(f"scenarios.{key}.prob 非法: {prob!r}")
                continue
            if not 0.0 <= float(prob) <= 1.0:
                errors.append(f"scenarios.{key}.prob 越界 [0,1]: {prob}")
                continue
            key_levels = _coerce_str_list(entry.get("key_levels"), f"scenarios.{key}.key_levels", errors)
            action_boundary = entry.get("action_boundary")
            if not isinstance(action_boundary, str):
                errors.append(f"scenarios.{key}.action_boundary 须为 str")
                action_boundary = str(action_boundary)
            scenarios[key] = LlmScenario(
                prob=round(float(prob), 4), key_levels=key_levels, action_boundary=action_boundary
            )
            prob_sum += float(prob)
    if len(scenarios) == len(_SCENARIO_KEYS) and abs(prob_sum - 1.0) > prob_sum_tolerance:
        errors.append(f"三情景概率和 {prob_sum:.4f} 偏离 1 超容差 ±{prob_sum_tolerance}")

    risk_points = _coerce_str_list(obj.get("risk_points"), "risk_points", errors)
    watch_sectors = _coerce_str_list(obj.get("watch_sectors"), "watch_sectors", errors)
    confidence_note = obj.get("confidence_note")
    if not isinstance(confidence_note, str):
        errors.append("confidence_note 须为 str")
        confidence_note = str(confidence_note)

    # 回显一致性（LLM 若回显铁律字段，须与运行值一致；不回显不扣分）
    for echoed, expected, label in (
        (obj.get("model_version"), model_version, "model_version"),
        (obj.get("prompt_version"), prompt_version, "prompt_version"),
        (obj.get("input_hash"), input_hash, "input_hash"),
    ):
        if echoed is not None and str(echoed) != expected:
            errors.append(f"回显 {label} 与运行值不一致: {echoed!r} != {expected!r}")

    if errors:
        return None, errors
    return (
        LlmDailyAnalysis(
            date=trade_date,
            model_version=model_version,
            prompt_version=prompt_version,
            input_hash=input_hash,
            scenarios=scenarios,
            risk_points=risk_points,
            watch_sectors=watch_sectors,
            confidence_note=confidence_note,
        ),
        [],
    )


# ── 落库（governance.db llm_daily_analysis；DDL-as-Code 唯一真源；幂等）──


def _resolve_db_path(db_path: str | Path | None) -> Path:
    """db_path 解析：None=DB_PATH SSoT（测试注入临时库走显式参数）。"""
    return Path(db_path) if db_path is not None else DB_PATH


def ensure_llm_daily_analysis_table(db_path: str | Path | None = None) -> Path:
    """幂等建表（CREATE TABLE IF NOT EXISTS + trade_date 索引）。

    Args:
        db_path: 库路径；None=DB_PATH SSoT（governance.db，92号 D2 授权）。

    Returns:
        实际建表库路径。
    """
    resolved = _resolve_db_path(db_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db_connection(resolved)
    try:
        conn.execute(LLM_DAILY_ANALYSIS_DDL)
        conn.execute(_DDL_IDX_TRADE_DATE)
    finally:
        conn.close()
    return resolved


def _persist_row(
    db_path: str | Path | None,
    *,
    trade_date: str,
    model_version: str,
    prompt_version: str,
    input_hash: str,
    output_json: str,
    status: str,
    error: str | None,
    tokens_in: int | None,
    tokens_out: int | None,
    cost_yuan: float | None,
    latency_ms: float | None,
    errors: list[str],
) -> tuple[int, bool]:
    """写一行 llm_daily_analysis（INSERT OR IGNORE 幂等：同键跳过保首条，返已存在行 id）。

    Returns:
        (row_id, db_logged)；DB 写失败 fail-open → (-1, False)+errors 留痕。
    """
    try:
        resolved = ensure_llm_daily_analysis_table(db_path)
        conn = get_db_connection(resolved)
        try:
            cur = conn.execute(
                _SQL_INSERT,
                (
                    trade_date,
                    model_version,
                    prompt_version,
                    input_hash,
                    output_json,
                    status,
                    error,
                    tokens_in,
                    tokens_out,
                    cost_yuan,
                    latency_ms,
                    datetime.datetime.now(datetime.UTC).isoformat(),
                ),
            )
            if cur.rowcount == 1:
                return int(cur.lastrowid), True
            row = conn.execute(
                _SQL_SELECT_ID_BY_KEY, (trade_date, model_version, prompt_version, input_hash)
            ).fetchone()
            return (int(row["id"]) if row is not None else -1), True
        finally:
            conn.close()
    except Exception as exc:  # noqa: BLE001 — fail-open：落库失败不炸（留痕）
        log.warning("llm_daily_analysis 落库失败（fail-open）: %s", exc)
        errors.append(f"db_write_failed: {exc!r}")
        return -1, False


# ── 主入口：打包 → 调用编排（v1/v2）→ 契约校验 → 落库 ──


def run_llm_analysis(
    trade_date: str | datetime.date,
    llm_client: Callable[[str], Any] | None = None,
    ch_client: Callable[[str], str] | None = None,
    config: LlmPremarketConfig | None = None,
    *,
    db_path: str | Path | None = None,
    asof_cutoff: str | datetime.datetime | None = None,
    injected: PremarketInjections | None = None,
) -> LlmRunResult:
    """LLM 盘前分析主入口（MOD-PLAN-007；不炸语义：一切异常落库留痕标状态）。

    Args:
        trade_date: 交易日（ISO 字符串或 date；非法抛 ValueError——唯一的 fail-closed 口）。
        llm_client: LLM 调用注入位（prompt→text str，或 Mapping 计量形态）；
            **None → status=skipped_not_wired 落库留痕不炸**（阶段三 gateway 接线前常态；
            本模块不直连任何 LLM API）。
        ch_client: CH 查询客户端（sql→TSV），可注入（测试 mock/离线）。
        config: 参数配置（debate_mode 默认 False=v1 单调用；True=v2 多空辩论三调用）。
        db_path: 库路径；None=DB_PATH SSoT（测试注入临时库）。
        asof_cutoff: PIT cutoff（None=trade_date 当日 08:00）。
        injected: 可注入可缺省契约（MOD-SIG-025/057/058/059/060 输出+BS-005 状态）。

    Returns:
        LlmRunResult：status∈{success, invalid, skipped_not_wired} + 输出契约 +
        计量（tokens/cost/latency，v2=三调用合计）+ 落库留痕（幂等键同键保首条）。
    """
    cfg = config or DEFAULT_CONFIG
    package = build_premarket_package(
        trade_date, ch_client=ch_client, config=cfg, asof_cutoff=asof_cutoff, injected=injected
    )
    # 铁律③：v2 辩论三套 prompt 与 v1 单调用属不同模板集，版本串分离（防幂等键碰撞）
    prompt_version_eff = cfg.prompt_version + ("+debate" if cfg.debate_mode else "")
    errors: list[str] = []

    def _persist(
        status: str,
        output_json: str,
        error: str | None,
        tokens_in: int | None = None,
        tokens_out: int | None = None,
        cost_yuan: float | None = None,
        latency_ms: float | None = None,
        actual_model: str | None = None,
    ) -> tuple[int, bool]:
        return _persist_row(
            db_path,
            trade_date=package.trade_date,
            model_version=actual_model or cfg.model_version,
            prompt_version=prompt_version_eff,
            input_hash=package.input_hash,
            output_json=output_json,
            status=status,
            error=error,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_yuan=cost_yuan,
            latency_ms=latency_ms,
            errors=errors,
        )

    # ── llm_client=None：skipped_not_wired 落库留痕不炸（阶段三接线前常态）──
    if llm_client is None:
        row_id, logged = _persist(STATUS_SKIPPED_NOT_WIRED, "", None)
        return LlmRunResult(
            trade_date=package.trade_date,
            status=STATUS_SKIPPED_NOT_WIRED,
            analysis=None,
            input_hash=package.input_hash,
            model_version=cfg.model_version,
            prompt_version=prompt_version_eff,
            debate_mode=cfg.debate_mode,
            tokens_in=None,
            tokens_out=None,
            cost_yuan=None,
            latency_ms=None,
            row_id=row_id,
            db_logged=logged,
            errors=errors,
            package=package,
        )

    # ── 调用编排：v1 单调用 / v2 多空辩论三调用（44号 §9.14）──
    replies: list[_LlmReply] = []
    debate: dict[str, str] = {}
    final_reply: _LlmReply | None = None
    if not cfg.debate_mode:
        final_reply = _invoke_llm("main", llm_client, SYSTEM_PROMPT_V1 + "\n\n" + build_user_prompt(package), errors)
        if final_reply is not None:
            replies.append(final_reply)
    else:
        bull = _invoke_llm(
            "bull",
            llm_client,
            _SYSTEM_ROLE_BULL + "\n\n" + build_user_prompt(package, role_instruction=_ROLE_TASK_BULL),
            errors,
        )
        bear = _invoke_llm(
            "bear",
            llm_client,
            _SYSTEM_ROLE_BEAR + "\n\n" + build_user_prompt(package, role_instruction=_ROLE_TASK_BEAR),
            errors,
        )
        for r in (bull, bear):
            if r is not None:
                replies.append(r)
        if bull is not None and bear is not None:
            debate = {"bull": bull.text, "bear": bear.text}
            final_reply = _invoke_llm(
                "arbiter",
                llm_client,
                _SYSTEM_ROLE_ARBITER + "\n\n" + build_user_prompt(package, debate_transcripts=debate),
                errors,
            )
            if final_reply is not None:
                replies.append(final_reply)

    tokens_in = sum(r.tokens_in for r in replies if r.tokens_in is not None) or None
    tokens_out = sum(r.tokens_out for r in replies if r.tokens_out is not None) or None
    cost_yuan = sum(r.cost_yuan for r in replies if r.cost_yuan is not None) or None
    latency_ms = sum(r.latency_ms for r in replies) if replies else None

    # ── 铁律②真值：实际服务模型以客户端回报为准（gateway 降级链真实通道），
    #    与 cfg.model_version（预期模型）不一致时留痕——落库 model_version=实际值 ──
    actual_model = next((r.model for r in replies if r.model), None)
    if actual_model and actual_model != cfg.model_version:
        errors.append(f"model_version_divergence: expected={cfg.model_version} actual={actual_model}")
    persist_model = actual_model or cfg.model_version

    # ── 调用失败 → invalid 落库留痕不炸 ──
    if final_reply is None:
        err_s = "; ".join(errors) or "llm_call_failed"
        output_json = _canonical_dumps(
            {"mode": "v2_debate" if cfg.debate_mode else "v1", "debate": debate or None},
            ensure_ascii=False,
            sort_keys=True,
        )
        row_id, logged = _persist(
            STATUS_INVALID, output_json, err_s, tokens_in, tokens_out, cost_yuan, latency_ms, actual_model=persist_model
        )
        return LlmRunResult(
            trade_date=package.trade_date,
            status=STATUS_INVALID,
            analysis=None,
            input_hash=package.input_hash,
            model_version=persist_model,
            prompt_version=prompt_version_eff,
            debate_mode=cfg.debate_mode,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_yuan=cost_yuan,
            latency_ms=latency_ms,
            row_id=row_id,
            db_logged=logged,
            errors=errors,
            package=package,
        )

    # ── 输出契约校验（拒收标 invalid 不炸）──
    analysis, parse_errors = parse_llm_output(
        final_reply.text,
        trade_date=package.trade_date,
        input_hash=package.input_hash,
        model_version=cfg.model_version,
        prompt_version=prompt_version_eff,
        prob_sum_tolerance=cfg.prob_sum_tolerance,
    )
    if analysis is None:
        errors.extend(parse_errors)
        raw = final_reply.text[: cfg.max_raw_output_chars]
        output_json = _canonical_dumps(
            {
                "mode": "v2_debate" if cfg.debate_mode else "v1",
                "raw_output": raw,
                "debate": debate or None,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        row_id, logged = _persist(
            STATUS_INVALID, output_json, "; ".join(parse_errors), tokens_in, tokens_out, cost_yuan, latency_ms,
            actual_model=persist_model,
        )
        return LlmRunResult(
            trade_date=package.trade_date,
            status=STATUS_INVALID,
            analysis=None,
            input_hash=package.input_hash,
            model_version=persist_model,
            prompt_version=prompt_version_eff,
            debate_mode=cfg.debate_mode,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_yuan=cost_yuan,
            latency_ms=latency_ms,
            row_id=row_id,
            db_logged=logged,
            errors=errors,
            package=package,
        )

    output_json = _canonical_dumps(
        {
            "mode": "v2_debate" if cfg.debate_mode else "v1",
            "analysis": analysis.to_dict(),
            "debate": debate or None,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    row_id, logged = _persist(
        STATUS_SUCCESS, output_json, None, tokens_in, tokens_out, cost_yuan, latency_ms, actual_model=persist_model
    )
    return LlmRunResult(
        trade_date=package.trade_date,
        status=STATUS_SUCCESS,
        analysis=analysis,
        input_hash=package.input_hash,
        model_version=persist_model,
        prompt_version=prompt_version_eff,
        debate_mode=cfg.debate_mode,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cost_yuan=cost_yuan,
        latency_ms=latency_ms,
        row_id=row_id,
        db_logged=logged,
        errors=errors,
        package=package,
    )
