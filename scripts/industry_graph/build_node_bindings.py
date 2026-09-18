# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-DATA-NDBIND | scripts/industry_graph/build_node_bindings.py | 06_transmission_chain_engine.md §8
# [MODULE] scripts.industry_graph.build_node_bindings
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); zephyr.infrastructure.database_service (ClickHouse reader); zephyr.data.table_registry (表名真源); docs/_working/altdata_line/06_transmission_chain_engine.md §8 (DDL 设计真源)
# [CONSUMERS] 传导链游走引擎（读 ig_node_binding 主绑定取数）; 后续绑定放量批（复用策展+校验骨架）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 表名一律经 TableRegistry 解析禁硬编码（TABLE-NAME-REGISTRY）; 每节点恰 1 主绑定（挂价铁律）; 宁缺毋假（模糊映射不挂，node_id+name 双校验不过即拒灌）; 禁 DELETE（表非零拒绝重灌）; PIT valid_from=序列真实数据起点; binding_id=NB-md5(节点|kind|源|键|valid_from)前12 确定性生成; SQL 全部集中于模块级常量（§5.160.2）
# [MODIFY-GUARD] 修改需通过任务卡；新增绑定行须经人工判读并在 07 工作令留痕
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 节点不存在/已退役/改名→该条拒绝入 rejected 并打印; 序列键在 CH 无数据→拒绝; 表已存在且非空→exit 4 拒绝; 主绑定数≠1→exit 3
# [TESTS] .runtime/tmp/igchain_20260918/t6_sample20.json（人工抽检 20/20 记录）；dry-run 报告 t6_dryrun_report.json
# [TTL] task_bound
"""ig_node_binding 建表+灌绑定（T6，REPAIR-WO-001 06 文档 §8 设计）。

设计真源: docs/_working/altdata_line/06_transmission_chain_engine.md §8（ig_node_binding DDL）。
与 §8 设计的差异（最小改动适配，详见 07 工作令 §10）:
  1. ig_node 无 node_type 列 → 绑定表自带 node_type（commodity/industry），写入时按策展规则判定;
  2. 增列 source_system（任务要求：sina 主连码与生意社缩写两套码必须可区分）;
  3. 增列 confidence（任务置信分级 0.9/0.7-0.8；§8 的 fit_quality 留给 WP-3 参数回填，不是决策置信）;
  4. series_kind 增加 'inventory' 值（§8 可观测清单含 库存=仓单，但 kind 枚举漏列）;
  5. series_ref 统一为 {"database","table","key"} 三元组，table 取 TableRegistry 真源注册名
     （§8 的 {database,indicator} 示例语义等价归一；TABLE-NAME-REGISTRY：禁硬编码表名）。

灌数纪律: 宁缺毋假（模糊映射不挂）；写前 count 报数；禁 DELETE；PIT valid_from=序列数据起点（如实）。
用法: python scripts/industry_graph/build_node_bindings.py --dry-run | --execute
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402
from zephyr.infrastructure.database_service import DatabaseService  # noqa: E402
from zephyr.data.table_registry import get_registry  # noqa: E402

RUN_TAG = "st-igchain-20260918/T6"
TODAY = date(2026, 9, 18)

# source_system 标签（区分两套商品码体系与各序列管线）
SS_MACRO = "eia_macro"           # macro_data（EIA）
SS_FUT = "sina_futures_main"     # commodity_futures_main（新浪主连码 cu0 风格）
SS_SPOT = "sci100ppi_spot"       # commodity_spot_price（生意社英文缩写 CU 风格）
SS_WR = "czce_receipt"           # futures_warehouse_receipt（郑商所仓单）
SS_NDRC = "ndrc_fuel"            # ndrc_fuel_price（发改委调价=E8）
SS_ROAD = "cflp_road"            # road_freight_index（物流与采购联合会公路运价）
SS_AGRI = "agri_200idx"          # agri_wholesale_index（农业农村部批发价格200）
SS_HOG = "mysteel_hog_spot"      # hog_spot_index（生猪现货指数）
SS_BOARD = "tdx_880_board"       # kline_sector_intraday（通达信 880 行业板=D6）

# 逻辑表名 → business_data_categories.yaml category_id（表名一律经 TableRegistry 解析，禁硬编码）
TABLE_CATEGORY = {
    "macro_data": "market_macro_data",
    "commodity_futures_main": "market_commodity_futures_main",
    "commodity_spot_price": "market_commodity_spot_price",
    "futures_warehouse_receipt": "market_futures_warehouse_receipt",
    "ndrc_fuel_price": "market_ndrc_fuel_price",
    "road_freight_index": "market_road_freight_index",
    "agri_wholesale_index": "market_agri_wholesale_index",
    "hog_spot_index": "market_hog_spot_index",
    "kline_sector_intraday": "market_sector_kline_intraday",
}
_FULL = {k: get_registry().table(v) for k, v in TABLE_CATEGORY.items()}  # 逻辑名 -> 'db.table'

# ---------------------------------------------------------------------------
# SQL 集中区（§5.160.2：SQL 字面量仅允许出现在模块级常量；CH 驱动不支持参数绑定，
# 动态值经 q() 字面量安全引号 + str.format 组装，表名来自 TableRegistry 真源）
# ---------------------------------------------------------------------------
SQL_TABLE_EXISTS = "SELECT to_regclass('public.{}')"
SQL_ROW_COUNT = "SELECT count(*) FROM {}"
SQL_NODE_LIVE = "SELECT name, valid_to FROM ig_node WHERE node_id=%s"
SQL_BIND_INSERT = (
    "INSERT INTO ig_node_binding "
    "(binding_id, node_id, node_type, series_kind, series_ref, source_system, "
    "primary_flag, quality_tier, fit_quality, confidence, last_verified, valid_from, valid_to, source) "
    "VALUES (%s,%s,%s,%s,%s::jsonb,%s,%s,%s,NULL,%s,%s,%s,NULL,%s)"
)
SQL_STATS = (
    ("node_type", "SELECT node_type, count(*) FROM ig_node_binding GROUP BY 1 ORDER BY 2 DESC"),
    ("source_system", "SELECT source_system, count(*) FROM ig_node_binding GROUP BY 1 ORDER BY 2 DESC"),
    ("series_kind", "SELECT series_kind, count(*) FROM ig_node_binding GROUP BY 1 ORDER BY 2 DESC"),
    ("primary", "SELECT count(*) FROM ig_node_binding WHERE primary_flag"),
)
SQL_CH_COUNT_BY = "SELECT count() FROM {ft} WHERE {col} = {val}"
SQL_CH_RANGE_BY = "SELECT min({dcol}), max({dcol}) FROM {ft} WHERE {col} = {val}"
SQL_CH_RANGE_FULL = "SELECT min({dcol}), max({dcol}) FROM {ft}"

DDL = """
CREATE TABLE IF NOT EXISTS ig_node_binding (
    binding_id    text PRIMARY KEY,
    node_id       text NOT NULL,
    node_type     text NOT NULL,
    series_kind   text NOT NULL,
    series_ref    jsonb NOT NULL,
    source_system text NOT NULL,
    primary_flag  boolean NOT NULL DEFAULT false,
    quality_tier  text NOT NULL DEFAULT 'B',
    fit_quality   numeric,
    confidence    numeric NOT NULL,
    last_verified date,
    valid_from    date NOT NULL,
    valid_to      date,
    source        text NOT NULL,
    ingested_at   timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_node_binding_ref UNIQUE (node_id, series_ref)
);
CREATE INDEX IF NOT EXISTS idx_node_binding_node ON ig_node_binding(node_id);
CREATE INDEX IF NOT EXISTS idx_node_binding_src ON ig_node_binding(source_system);
COMMENT ON TABLE ig_node_binding IS '节点挂价绑定表（06_transmission_chain_engine.md §8 定稿；T6 st-igchain-20260918 建）——每节点≥1条主绑定才可游走（挂价铁律落地点）';
COMMENT ON COLUMN ig_node_binding.series_ref IS '逻辑引用 {"database","table","key"}，图在 PG 序列在 CH，运行层经 DatabaseService 取数，不硬外键';
COMMENT ON COLUMN ig_node_binding.source_system IS '码体系/管线区分：sina_futures_main(新浪主连码 cu0 风格) vs sci100ppi_spot(生意社缩写 CU 风格) 等';
COMMENT ON COLUMN ig_node_binding.confidence IS '绑定决策置信：1:1明确=0.9，语义对应=0.7-0.8，模糊不挂（宁缺毋假）';
COMMENT ON COLUMN ig_node_binding.fit_quality IS 'WP-3 参数回填+衰减制度钩子（本批留空）';
"""


def full_table(logical: str) -> str:
    return _FULL[logical]


def q(v: str) -> str:
    """CH 驱动不支持参数绑定，字面量安全引号。"""
    return "'" + str(v).replace("\\", "\\\\").replace("'", "\\'") + "'"


def ref(table: str, key: str) -> dict:
    db, _, tbl = full_table(table).partition(".")
    return {"database": db, "table": tbl, "key": key}


def _has_data(r) -> bool:
    return bool(r) and r[0][0] is not None


def _check_by_column(col: str, dcol: str):
    def _h(ch, ft, key):
        exists_row = ch.execute(SQL_CH_COUNT_BY.format(ft=ft, col=col, val=q(key)))
        rng = ch.execute(SQL_CH_RANGE_BY.format(ft=ft, col=col, dcol=dcol, val=q(key)))
        return exists_row[0][0] > 0, rng
    return _h


def _check_ndrc(ch, ft, key):
    ok = key in ("gasoline_price", "diesel_price")
    rng = ch.execute(SQL_CH_RANGE_FULL.format(ft=ft, dcol="announce_date"))
    return ok, rng


def _check_hog(ch, ft, key):
    ok = key == "index_value"
    rng = ch.execute(SQL_CH_RANGE_FULL.format(ft=ft, dcol="trade_date"))
    return ok, rng


CHECKERS = {
    "macro_data": _check_by_column("indicator_name", "report_date"),
    "commodity_futures_main": _check_by_column("symbol", "trade_date"),
    "commodity_spot_price": _check_by_column("symbol", "trade_date"),
    "futures_warehouse_receipt": _check_by_column("symbol", "trade_date"),
    "ndrc_fuel_price": _check_ndrc,
    "road_freight_index": _check_by_column("index_code", "trade_date"),
    "agri_wholesale_index": _check_by_column("index_code", "trade_date"),
    "hog_spot_index": _check_hog,
    "kline_sector_intraday": _check_by_column("code", "trade_date"),
}


def check_series(ch, table: str, key: str):
    """序列键存在性校验，返回 (ok, range_row)；表名经 TableRegistry 解析。"""
    handler = CHECKERS.get(table)
    if handler is None:
        return False, None
    ok, r = handler(ch, full_table(table), key)
    return (ok and _has_data(r)), r


# ---------------------------------------------------------------------------
# 策展绑定清单（人工判读定稿；node_id+name 双校验，任一不符即拒绝灌该条）
# conf: 1:1 明确=0.9；语义对应=0.7-0.8；模糊不挂（宁缺毋假）。
# (node_id, node_name, node_type, series_kind, source_system, table, key, primary, conf, note)
# ---------------------------------------------------------------------------
BINDINGS: list[tuple] = [
    # ===== 第一优先：油价五波 6 个【快】绑定（06 §9 MVP 缺口）=====
    # -- N0 原油（图中锚点=油气勘探开采）--
    ("ND-4e516699a4d0", "油气勘探开采", "industry", "price", SS_MACRO, "macro_data", "EIA_BRENT_SPOT", True, 0.8,
     "N0 原油主绑定：图中无纯原油节点，油气勘探开采为其上游锚点；Brent 为中国进口原油定价基准"),
    ("ND-4e516699a4d0", "油气勘探开采", "industry", "price", SS_MACRO, "macro_data", "EIA_WTI_SPOT", False, 0.8,
     "WTI 副序列"),
    ("ND-4e516699a4d0", "油气勘探开采", "industry", "inventory", SS_MACRO, "macro_data", "EIA_CRUDE_INVENTORY", False, 0.8,
     "EIA 原油库存（宏观库存轴）"),
    ("ND-4e516699a4d0", "油气勘探开采", "industry", "index", SS_BOARD, "kline_sector_intraday", "880311", False, 0.7,
     "D6 石油开采板块指数（TDX_INDUSTRY_BOARDS 880311）"),
    # -- N1a 成品油：E8 发改委调价（缺口#1）--
    ("ND-53a732ec94ed", "成品油销售", "industry", "price", SS_NDRC, "ndrc_fuel_price", "gasoline_price", True, 0.9,
     "E8 发改委成品油调价：汽油零售价，1:1 对应成品油价格"),
    ("ND-53a732ec94ed", "成品油销售", "industry", "price", SS_NDRC, "ndrc_fuel_price", "diesel_price", False, 0.9,
     "E8 柴油零售价"),
    ("ND-53a732ec94ed", "成品油销售", "industry", "index", SS_BOARD, "kline_sector_intraday", "880312", False, 0.7,
     "D6 石油加工板块指数"),
    # -- N1b 运价：公路运价指数（缺口#2）--
    ("ND-e6a626f250cc", "公路铁路运输行业聚合", "industry", "index", SS_ROAD, "road_freight_index", "CFLP_ROAD_TOTAL", True, 0.7,
     "中国公路物流运价指数；节点含铁路故为语义对应（覆盖部分）"),
    ("ND-e6a626f250cc", "公路铁路运输行业聚合", "industry", "index", SS_ROAD, "road_freight_index", "CFLP_ROAD_FTL", False, 0.7,
     "公路运价整车指数"),
    ("ND-e6a626f250cc", "公路铁路运输行业聚合", "industry", "index", SS_ROAD, "road_freight_index", "CFLP_ROAD_LTL_HEAVY", False, 0.7,
     "公路运价零担重货指数"),
    ("ND-e6a626f250cc", "公路铁路运输行业聚合", "industry", "index", SS_ROAD, "road_freight_index", "CFLP_ROAD_LTL_LIGHT", False, 0.7,
     "公路运价零担轻货指数"),
    ("ND-e6a626f250cc", "公路铁路运输行业聚合", "industry", "index", SS_BOARD, "kline_sector_intraday", "880459", False, 0.7,
     "D6 运输服务板块指数"),
    # -- N2b 快递：单票收入序列未建（E10 缺口#5 如实挂起），先以仓储物流板块指数为主绑定 --
    ("ND-1e7a1e3fc43f", "快递运输", "industry", "index", SS_BOARD, "kline_sector_intraday", "880464", True, 0.7,
     "D6 仓储物流板块指数，快递运输节点代理主绑定；E10 快递单票收入序列建成后补价绑"),
    # -- N3 家电/塑料制品：板块指数（缺口#4）--
    ("ND-334e9432b851", "家电产业链聚合", "industry", "index", SS_BOARD, "kline_sector_intraday", "880387", True, 0.8,
     "D6 家用电器板块指数"),
    ("ND-c34fcd2d2999", "白色家电行业聚合", "industry", "index", SS_BOARD, "kline_sector_intraday", "880387", True, 0.7,
     "白电子集，与家电板块同指数（覆盖部分 0.7，本节点主绑定）"),
    ("ND-c58fb46ea38c", "塑料制品行业聚合", "industry", "index", SS_BOARD, "kline_sector_intraday", "880338", True, 0.8,
     "D6 塑料板块指数"),
    # -- N4 服装 --
    ("ND-c0093b6fef59", "纺织制造行业聚合", "industry", "index", SS_BOARD, "kline_sector_intraday", "880368", True, 0.8,
     "D6 纺织板块指数"),
    ("ND-cc29535d22c0", "服装家纺行业聚合", "industry", "index", SS_BOARD, "kline_sector_intraday", "880367", True, 0.8,
     "D6 纺织服饰板块指数"),
    ("ND-74620c3c8274", "聚酯涤纶", "commodity", "price", SS_SPOT, "commodity_spot_price", "PF", True, 0.8,
     "涤纶短纤现货（生意社 PF）"),
    ("ND-74620c3c8274", "聚酯涤纶", "commodity", "inventory", SS_WR, "futures_warehouse_receipt", "PF", False, 0.8,
     "短纤仓单（郑商所）"),
    # -- N5 食品：F13 批发价（缺口#3：农产品/菜篮子批发价格200）--
    ("ND-303e23dd22b5", "休闲食品制造", "industry", "index", SS_BOARD, "kline_sector_intraday", "880375", True, 0.7,
     "D6 食品板块指数"),
    ("ND-24574cd134df", "农产品加工行业聚合", "industry", "index", SS_AGRI, "agri_wholesale_index", "AJC200", True, 0.7,
     "农产品批发价格200指数（F13 肉蛋菜批发价现役代理）"),
    ("ND-dc907a73a289", "养殖业行业聚合", "industry", "index", SS_AGRI, "agri_wholesale_index", "CLZ200", True, 0.7,
     "菜篮子产品批发价格200指数"),
    ("ND-da44fc2016bb", "生猪养殖", "industry", "price", SS_HOG, "hog_spot_index", "index_value", True, 0.9,
     "生猪现货指数（11 年日度）"),
    ("ND-da44fc2016bb", "生猪养殖", "industry", "price", SS_FUT, "commodity_futures_main", "lh0", False, 0.9,
     "生猪期货主连（新浪 lh0）"),
    ("ND-da44fc2016bb", "生猪养殖", "industry", "price", SS_SPOT, "commodity_spot_price", "LH", False, 0.9,
     "生猪现货（生意社 LH）"),
    ("ND-e0f5f0e77388", "棉花种植", "industry", "price", SS_SPOT, "commodity_spot_price", "CF", True, 0.8,
     "棉花现货（生意社 CF）"),
    ("ND-e0f5f0e77388", "棉花种植", "industry", "inventory", SS_WR, "futures_warehouse_receipt", "CF", False, 0.9,
     "棉花仓单（郑商所，1:1）"),
    ("ND-0645fa9db53a", "天然气产业链介绍（一）：天然气基础知识", "commodity", "inventory", SS_MACRO, "macro_data", "EIA_NATGAS_INVENTORY", True, 0.7,
     "EIA 天然气库存（图中天然气链锚点；EIA 气价现货序列库内未建，只挂库存）"),
    # ===== 第二优先：放量（商品码两套体系，sina 主连 vs 生意社缩写，source_system 区分）=====
    ("ND-7200af79addc", "PTA", "commodity", "price", SS_SPOT, "commodity_spot_price", "TA", True, 0.9,
     "PTA 现货（生意社 TA），N2 化工品波锚点"),
    ("ND-7200af79addc", "PTA", "commodity", "inventory", SS_WR, "futures_warehouse_receipt", "PTA", False, 0.9,
     "PTA 仓单（郑商所键名 PTA，与生意社 TA 不同键，source_system 区分）"),
    ("ND-83b1a7443df1", "豆粕", "commodity", "price", SS_FUT, "commodity_futures_main", "m0", True, 0.9,
     "豆粕期货主连（m0）"),
    ("ND-83b1a7443df1", "豆粕", "commodity", "price", SS_SPOT, "commodity_spot_price", "M", False, 0.9,
     "豆粕现货（生意社 M）"),
    ("ND-ebc582b1606f", "白糖", "commodity", "price", SS_SPOT, "commodity_spot_price", "SR", True, 0.9,
     "白糖现货（生意社 SR）"),
    ("ND-5431cd451884", "焦煤", "commodity", "price", SS_SPOT, "commodity_spot_price", "JM", True, 0.9,
     "焦煤现货（生意社 JM）"),
    ("ND-ba54c96c9786", "橡胶", "commodity", "price", SS_SPOT, "commodity_spot_price", "RU", True, 0.8,
     "天然橡胶现货（节点语义含合成胶，0.8）"),
    ("ND-732f5aab8bb0", "动力煤", "commodity", "inventory", SS_WR, "futures_warehouse_receipt", "ZC", True, 0.9,
     "动力煤仓单（郑商所 ZC，该品唯一在库序列）"),
    ("ND-2b7ebcaa7573", "白银", "commodity", "price", SS_SPOT, "commodity_spot_price", "AG", True, 0.9,
     "白银现货（生意社 AG）"),
    ("ND-73b5d6358978", "电解铝", "commodity", "price", SS_SPOT, "commodity_spot_price", "AL", True, 0.8,
     "铝现货（生意社 AL=铝锭）"),
    ("ND-73b5d6358978", "电解铝", "commodity", "price", SS_FUT, "commodity_futures_main", "al0", False, 0.8,
     "铝期货主连（al0）"),
    ("ND-fbcb6d1742c9", "锡冶炼", "industry", "price", SS_SPOT, "commodity_spot_price", "SN", True, 0.8,
     "锡现货（冶炼节点价格锚）"),
    ("ND-08582138b227", "锌冶炼", "industry", "price", SS_SPOT, "commodity_spot_price", "ZN", True, 0.8,
     "锌现货"),
    ("ND-74ec961e4968", "纯碱制造", "industry", "price", SS_SPOT, "commodity_spot_price", "SA", True, 0.9,
     "纯碱现货"),
    ("ND-74ec961e4968", "纯碱制造", "industry", "inventory", SS_WR, "futures_warehouse_receipt", "SA", False, 0.9,
     "纯碱仓单"),
    ("ND-ad1de138cd3d", "浮法玻璃", "commodity", "price", SS_SPOT, "commodity_spot_price", "FG", True, 0.8,
     "玻璃现货（期货标的即浮法玻璃）"),
    ("ND-ad1de138cd3d", "浮法玻璃", "commodity", "inventory", SS_WR, "futures_warehouse_receipt", "FG", False, 0.8,
     "玻璃仓单"),
    ("ND-8be0bfe99032", "纸浆制造", "industry", "price", SS_SPOT, "commodity_spot_price", "SP", True, 0.9,
     "纸浆现货"),
    ("ND-14fc1c6194fb", "铁矿开采", "industry", "price", SS_SPOT, "commodity_spot_price", "I", True, 0.8,
     "铁矿石现货"),
    ("ND-5ca6a415f341", "铁矿石采选", "industry", "price", SS_SPOT, "commodity_spot_price", "I", True, 0.8,
     "铁矿石现货（另一链的铁矿节点）"),
    ("ND-cb288399c565", "粮食种植", "industry", "price", SS_SPOT, "commodity_spot_price", "C", True, 0.7,
     "玉米现货（粮食⊃玉米，覆盖部分 0.7）"),
    ("ND-cb288399c565", "粮食种植", "industry", "price", SS_FUT, "commodity_futures_main", "c0", False, 0.7,
     "玉米期货主连（c0）"),
    ("ND-6f305c54b0c7", "油料种植", "industry", "price", SS_SPOT, "commodity_spot_price", "OI", True, 0.7,
     "菜油现货（油料⊃菜籽，覆盖部分 0.7）"),
    ("ND-65dd87544856", "多晶硅料", "commodity", "price", SS_SPOT, "commodity_spot_price", "PL", True, 0.8,
     "多晶硅现货（生意社 PL）"),
    ("ND-65dd87544856", "多晶硅料", "commodity", "inventory", SS_WR, "futures_warehouse_receipt", "PL", False, 0.8,
     "多晶硅仓单"),
    ("ND-165ca02f4b70", "PVC产业链配套与边际装置", "industry", "price", SS_SPOT, "commodity_spot_price", "V", True, 0.7,
     "PVC 现货（研报锚点节点，0.7）"),
    ("ND-4ef90f4acfd0", "甲醇基础及甲醇的产业链介绍", "industry", "price", SS_SPOT, "commodity_spot_price", "MA", True, 0.7,
     "甲醇现货（研报锚点节点）"),
    ("ND-4ef90f4acfd0", "甲醇基础及甲醇的产业链介绍", "industry", "inventory", SS_WR, "futures_warehouse_receipt", "MA", False, 0.7,
     "甲醇仓单"),
    ("ND-0945c8674074", "铜产业链聚合", "industry", "price", SS_SPOT, "commodity_spot_price", "CU", True, 0.7,
     "铜现货（链聚合节点作铜价锚；图中无纯铜商品节点）"),
    ("ND-0945c8674074", "铜产业链聚合", "industry", "price", SS_FUT, "commodity_futures_main", "cu0", False, 0.7,
     "铜期货主连（cu0）"),
]


def binding_id(node_id: str, kind: str, ss: str, key: str, valid_from: date) -> str:
    raw = f"{node_id}|{kind}|{ss}|{key}|{valid_from.isoformat()}"
    return "NB-" + hashlib.md5(raw.encode("utf-8")).hexdigest()[:12]


def verify_binding(cur, ch, spec: tuple):
    """单条绑定双校验（节点存活+序列键），返回 (row|None, ok_item_or_reject)。"""
    node_id, node_name, ntype, kind, ss, table, key, prim, conf, note = spec
    cur.execute(SQL_NODE_LIVE, (node_id,))
    row = cur.fetchone()
    if row is None:
        return None, {"node_id": node_id, "key": key, "reason": "node 不存在"}
    live_name, valid_to = row
    if live_name != node_name or valid_to is not None:
        return None, {"node_id": node_id, "key": key,
                      "reason": f"node 校验失败 name={live_name!r} valid_to={valid_to}"}
    ok, r = check_series(ch, table, key)
    if not ok:
        return None, {"node_id": node_id, "key": f"{table}.{key}", "reason": "序列键在 CH 不存在"}
    valid_from = r[0][0]
    if hasattr(valid_from, "date"):  # datetime -> date 归一
        valid_from = valid_from.date()
    bid = binding_id(node_id, kind, ss, key, valid_from)
    out_row = (bid, node_id, ntype, kind, json.dumps(ref(table, key), ensure_ascii=False),
               ss, prim, "A" if conf >= 0.85 else "B", conf, TODAY, valid_from,
               f"{RUN_TAG}: {note}")
    ok_item = {"binding_id": bid, "node": f"{node_name}({node_id})", "kind": kind,
               "ref": ref(table, key), "ss": ss, "primary": prim, "conf": conf,
               "tier": "A" if conf >= 0.85 else "B", "valid_from": str(valid_from)}
    return out_row, ok_item


def collect_verified(cur, ch) -> tuple[list, list, list]:
    """遍历策展清单做双校验，返回 (verified_rows, ok_items, rejects)。"""
    verified, oks, rejects = [], [], []
    for spec in BINDINGS:
        out_row, item = verify_binding(cur, ch, spec)
        if out_row is None:
            rejects.append(item)
        else:
            verified.append(out_row)
            oks.append(item)
    return verified, oks, rejects


def check_primaries(verified_rows: list) -> dict:
    """挂价铁律：每节点恰 1 主绑定，违规返回 dict。"""
    primaries: dict[str, int] = {}
    for r_ in verified_rows:
        primaries[r_[1]] = primaries.get(r_[1], 0) + (1 if r_[6] else 0)
    return {k: v for k, v in primaries.items() if v != 1}


def print_dry_report(oks: list, report: dict) -> int:
    for b in oks:
        flag = "P" if b["primary"] else " "
        print(f"    {flag} {b['node']} <- {b['ref']['table']}.{b['ref']['key']} "
              f"[{b['ss']}] kind={b['kind']} conf={b['conf']} tier={b['tier']} vf={b['valid_from']}")
    report_path = Path(".runtime/tmp/igchain_20260918/t6_dryrun_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[dry-run] 报告: {report_path}")
    return 0


def insert_all(cur, verified_rows: list, report: dict, exists: bool) -> int:
    """DDL（如需）+灌数+统计；返回进程退出码。"""
    if not exists:
        cur.execute(DDL)
        print("[2] DDL 完成（表+唯一约束+2 索引+注释）")
    else:
        print("[2] 表已存在，跳过 DDL")
    cur.execute(SQL_ROW_COUNT.format("ig_node_binding"))
    before = cur.fetchone()[0]
    print(f"[2] 写前 count={before}（须为 0，非 0 拒绝）")
    if before != 0:
        print("[!] 表非空，拒绝灌入（禁覆盖已有绑定）")
        return 4
    cur.executemany(SQL_BIND_INSERT, verified_rows)
    cur.execute(SQL_ROW_COUNT.format("ig_node_binding"))
    after = cur.fetchone()[0]
    report["rows"] = after
    out = Path(".runtime/tmp/igchain_20260918/t6_report.json")  # 报告先落盘防打印异常丢失
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[3] 写后 count={after}（期望 {len(verified_rows)}）；报告: {out}")
    print_stats(cur)
    return 0


def print_stats(cur) -> None:
    for label, sql in SQL_STATS:
        cur.execute(sql)
        print(f"    {label} 分布:" if label != "primary" else "    主绑定节点数:", cur.fetchall())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--execute", action="store_true")
    args = ap.parse_args()
    if args.dry_run == args.execute:
        print("须且仅须指定 --dry-run 或 --execute 之一")
        return 2

    pg = get_depgraph_pg_connection(superuser=True, read_only=args.dry_run, autocommit=True)
    cur = pg.cursor()  # 元组游标
    ch = DatabaseService().get_clickhouse_conn(role="reader")

    cur.execute(SQL_TABLE_EXISTS.format("ig_node_binding"))
    exists = cur.fetchone()[0] is not None
    print(f"[0] ig_node_binding 存在性: {exists}")
    if exists:
        cur.execute(SQL_ROW_COUNT.format("ig_node_binding"))
        print(f"    现有行数: {cur.fetchone()[0]}（非零则本脚本拒绝灌入，禁覆盖）")

    verified, oks, rejects = collect_verified(cur, ch)
    report = {"created": not exists, "rows": 0, "rejected": rejects, "bindings": oks}
    print(f"[1] 策展 {len(BINDINGS)} 条 → 校验通过 {len(verified)} 条，拒绝 {len(rejects)} 条")
    for rj in rejects:
        print("    REJECT:", rj)

    bad = check_primaries(verified)
    if bad:
        print(f"[!] 主绑定校验失败（每节点须恰 1 主绑定）: {bad}")
        return 3

    if args.dry_run:
        return print_dry_report(oks, report)
    return insert_all(cur, verified, report, exists)


if __name__ == "__main__":
    sys.exit(main())
