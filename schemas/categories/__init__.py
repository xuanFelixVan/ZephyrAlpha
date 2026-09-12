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
     其余杂项参考数据          -> 根（根目录为封顶型，T_soft=120 资格依据本约定）
  3. 本目录为 ClickHouse DDL-as-Code SSoT（每文件恰一个 *_DDL 常量）；
     PostgreSQL 侧 ig_* 表 DDL 走 scripts/industry_graph/apply_industry_graph_ddl.py
     聚合模式，与本目录无关。

对账链：verify_schema_truth.py / lint_symbol_convention.py 按 rglob 递归枚举本目录。
"""
