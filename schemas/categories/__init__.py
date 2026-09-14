# [BLUEPRINT] MOD-L04-001 | schemas/categories/__init__.py | §
# [MODULE] schemas.categories
# [DOMAIN] D_DATA
# [TTL] permanent
"""DDL-as-Code 真源目录地图与前缀约定（GOV-DOC-018 T_soft 资格文档）。

布局（2026-09-12 增长簇拆分，方案 E 裁定：文件名一律不动，只动父目录）：

  kline/        market_kline_*（K 线族，32+ 文件，频率×资产类持续裂变）
  fundamental/  fundamental_*（基本面三表及衍生，12+ 文件，对齐 c3_fundamental 库）
  crypto/       crypto_*（币圈，战略扩面域，预铺增长路径）
  intraday/     盘中微结构簇（tick/l2/竞价/大宗/成交回报/资金流/实时快照，10+ 文件）
  meta/         参考元数据（meta_stock_profile_ths）
  market/       market_*（行情与另类数据，92+ 文件，2026-09-14 第二批；不含 kline/ 与 intraday/ 已持有前缀）
  backtest/     backtest_*（回测域，4 文件，2026-09-14 第二批，对齐 D_BACKTEST）
  macro/        macro_*（宏观，2 文件，2026-09-14 第二批）
  （根）        杂项参考数据区——异质本体（指数/板块/融资融券/日历/ST/龙虎榜/
                港美股/可转债/期权期货等），非债，封顶型

命名规则（前缀簇，模块地图）：
  1. 文件名 == category_id + ".py"（硬约定；business_data_categories.yaml 的
     schema_file 字段与 verify_schema_truth 按此反查，禁止改名）
  2. 新表落位规则（线性增长型按增长簇归位）：
     market_kline_*           -> kline/
     fundamental_*            -> fundamental/
     crypto_*                 -> crypto/
     盘中微结构（tick/l2/auction/block/execution/trade_report/money_flow/realtime）
                              -> intraday/
     market_*（非 kline/非盘中微结构） -> market/
     backtest_*               -> backtest/
     macro_*                  -> macro/
     其余杂项参考数据          -> 根（根目录为封顶型，T_soft=120 资格依据本约定）
  3. 本目录为 ClickHouse DDL-as-Code SSoT（每文件恰一个 *_DDL 常量）；
     PostgreSQL 侧 ig_* 表 DDL 走 scripts/industry_graph/apply_industry_graph_ddl.py
     聚合模式，与本目录无关。

对账链：verify_schema_truth.py / lint_symbol_convention.py 按 rglob 递归枚举本目录。
"""

# 【GOV-DOC-018 命名约定（T_soft=120 资格声明，2026-09-14 第二批拆分后更新）】
# 根目录 8 个业务 .py（+1 __init__.py）为封顶型杂项参考数据区，按文件名前缀簇管理命名规则（模块地图如下）。
# 前缀簇（现存）：cross_* (1)、factor_* (1)、meta_* (2)、regime_* (1)、sim_* (3)
# 约定：新增文件必须延续所属簇前缀；新簇须先在本约定登记再落文件；
# market_*/backtest_*/macro_* 一律不入根（2026-09-14 起分属 market/ backtest/ macro/ 子目录）；
# 单簇超过 20 件时应拆子目录（参照 tests/signal_ashare 拆分先例）。
