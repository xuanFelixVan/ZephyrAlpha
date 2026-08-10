# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_dividend_tax_node
# [DOMAIN] D_DATA
# [DEPENDENCIES] c3_fundamental.rights_issue
# [CONSUMERS] apply_market_tables_ddl; 回测/分析 pipeline
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] dividend_tax_node VIEW DDL 唯一真源；VIEW 由 rights_issue 实时派生，无独立存储
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] VIEW定义与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [TTL] permanent
"""dividend_tax_node（红利税节点）DDL-as-Code — VIEW，非 TABLE（category_id: market_dividend_tax_node）。

A 股红利税差别化征收规则（个人投资者）：
    持股 ≤ 1个月（含）：20% 税
    持股 1个月~1年（含）：10% 税
    持股 > 1年：免税（2015年9月8日起）

"红利税节点" = 除息日前1个月/前1年的日期。这些日期前后买入，持股期限跨过税率档位，
引发税动机交易（如：短线持有者赶在 ex_date 前卖出避 20% 税；长线资金在 ex_date-1年前
买入以获免税待遇）。

设计：
    本表为 ClickHouse VIEW（非 TABLE），由 c3_fundamental.rights_issue 实时派生，无独立存储。
    每次 rights_issue 更新后，VIEW 自动反映最新数据（无需单独调度任务）。
    遵循"由现有数据派生，不新建表"原则（用户第二档建议）。

输出列：
    symbol          symbol_canonical 格式（如 601988.SH），可直接 JOIN kline_daily 等行情表
    stock_name      股票名称
    exchange        交易所（SH/SZ/BJ）
    ex_date         除权除息日
    node_type       dividend_tax_1m（1月节点）/ dividend_tax_1y（1年节点）
    node_date       节点日期（ex_date - 1月 / ex_date - 1年）
    dividend_pre_tax 税前派息（元/10股）
    description     节点描述

典型查询：
    -- 某日有哪些股票触达红利税节点
    SELECT * FROM c1_market.dividend_tax_node WHERE node_date = today()

    -- 某股票未来30天的红利税节点
    SELECT * FROM c1_market.dividend_tax_node
    WHERE symbol = '601988.SH' AND node_date BETWEEN today() AND addDays(today(), 30)

    -- JOIN 行情分析税节点日涨跌
    SELECT n.*, k.pct_change FROM c1_market.dividend_tax_node n
    ANY LEFT JOIN c1_market.kline_daily k ON n.symbol = k.symbol AND k.trade_date = n.node_date
    WHERE n.node_date = '2025-06-10'
"""

from __future__ import annotations

# category_id: market_dividend_tax_node
# calc_mode: on_demand（VIEW 实时派生，无需预加载/调度）

DIVIDEND_TAX_NODE_DDL = """
CREATE VIEW IF NOT EXISTS c1_market.dividend_tax_node AS
SELECT
    symbol_canonical AS symbol,
    stock_name,
    exchange,
    toDate(ex_date) AS ex_date,
    'dividend_tax_1m' AS node_type,
    addMonths(toDate(ex_date), -1) AS node_date,
    dividend_pre_tax,
    concat(toString(stock_name), ' 红利税1月节点(除息日前1月,持股>1月税率10%)') AS description
FROM c3_fundamental.rights_issue
WHERE ex_date IS NOT NULL
  AND ex_date > toDate('1970-01-01')
  AND type = '分红'
  AND coalesce(dividend_pre_tax, 0) > 0
UNION ALL
SELECT
    symbol_canonical AS symbol,
    stock_name,
    exchange,
    toDate(ex_date) AS ex_date,
    'dividend_tax_1y' AS node_type,
    addYears(toDate(ex_date), -1) AS node_date,
    dividend_pre_tax,
    concat(toString(stock_name), ' 红利税1年节点(除息日前1年,持股>1年免税)') AS description
FROM c3_fundamental.rights_issue
WHERE ex_date IS NOT NULL
  AND ex_date > toDate('1970-01-01')
  AND type = '分红'
  AND coalesce(dividend_pre_tax, 0) > 0
"""

# 表元数据
TABLE_NAME = "dividend_tax_node"
DATABASE = "c1_market"
CATEGORY_ID = "market_dividend_tax_node"
CALC_MODE = "on_demand"
ENGINE = "VIEW"
PARTITION_KEY = "N/A (VIEW)"
ORDER_BY = "N/A (VIEW)"

# VIEW 无 INSERT_COLUMNS（只读派生）
INSERT_COLUMNS = None
