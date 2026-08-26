# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.sector_code_bridge
# [DOMAIN] D_DATA
# [DEPENDENCIES] 无三方/无网络/无库；消费方契约对齐 zephyr.signal_ashare.counter_trend_board（fund_flow 注入位，类型上仅结构化 dict 不 import）；输入行对齐 zephyr.data.implementations.sector_fund_flow_collector.SectorFundFlowEntry（鸭子类型读取 sector_type/sector_name/net_amount）
# [CONSUMERS] （GAP-F-16 逆势榜资金卡注入位：build_counter_trend_board(fund_flow=...)，段内差分+重钥经 zephyr.signal_ashare.counter_trend_board run 层自动加载；tasks.yaml 采集排期待 8803/8804 分钟K线接线）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 纯函数不触网不触库（CSV 中间层除外）；映射 SSoT=模块内常量（90 行 THS 881xxx 行业 ↔ 132 条 TDX 8803/8804 行业指数主数据）；90/90 全映射零缺失；多 881 同目标净额 SUM（行业互不相交故可加）；concept 行/空净额/未知名跳过留痕不炸；段内差分=段末累计−段前累计（段前无快照按开盘 0 起算，差分可为负不伪造）；输出 dict[880code, float] 直插消费方 fund_flow 注入位；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-16 行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CSV 读取 880 目标不在 TDX 主数据→ValueError（fail-closed）；映射行重复 881 码→import 期不校验、消费期后写覆盖先写（不发生，单测锁唯一性）
# [TESTS] tests/zephyr/data/test_sector_code_bridge.py
# [A_module] module_id=MOD-DAT-sector_code_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-DAT-sector_code_bridge — 881xxx→880xxx 板块代码桥接适配器（GAP-F-16）。

两代码体系口径（2026-08-24 实证）：
- **881xxx（资金流采集侧）**：同花顺行业指数代码。c1_market.sector_meta 90 码
  （akshare stock_board_industry_name_ths 采集，sector_type=同花顺行业）；
  sector_fund_flow_collector 的 THS 资金流快照行业名与之 90/90 对齐零缺失
  （2026-08-24 活体校验：stock_fund_flow_industry(即时) 90 名 ∩ sector_meta 90 名
  双向零缺失——D3 实证重建，原 D3FUND_report 落盘丢失）。
- **880xxx（项目板块主数据侧）**：通达信板块指数代码。名源真源=TDX 客户端
  tdxzs.cfg（604 条：8800 统计 2 + 8802 地区 32 + **8803/8804 行业 132** +
  8805-8809 概念风格 428），行业板带 T 码（通达信行业分类码，层级可比）。
  CH 侧 880 名称全为代码回显/空（sector_constituent/kline_sector_880 实证），
  故 132 条行业主数据随模块内置（SSoT=本模块常量）。

关键排雷（2026-08-24 T 码分布实证）：sector_constituent/kline_sector_intraday
的 128 个 881xxx 码与 sector_meta 的 881xxx 是**不同命名空间**（同号不同义：
meta 881157=证券，SC 881157 成分 T 码分布=服饰）——本桥不接 SC/KI 的 881 码，
唯一 881 真源=sector_meta（THS 体系）。

映射方法（策展+留痕）：90 个 THS 一级行业 → 132 条 TDX 行业指数，按名称对应
（exact 18）/语义对应（semantic 54）/上卷聚合（aggregate 18，TDX 无同级板块时
归最近聚合族，如 光伏/风电/电池/电机→电气设备 T0706）。THS 细分而 TDX 聚合处
多 881 同目标——重钥时净额 **SUM**（THS 行业互不相交，可加）；TDX 细分而
THS 聚合处取主映射（如 种植业与林业→种植业），未配腿在 note 列留痕。

消费方契约（逆势榜资金卡）：build_counter_trend_board(fund_flow: Mapping[str,
float] | None)——fund_flow 键=板块代码、值=段内净流入；None→卡2 降级；全负→
卡2"段内无正净流入板块"降级（消费方自身口径，本适配器不伪造）。sector_names_880()
供 CounterTrendConfig.sector_names 回显中文名。

CSV 中间层（仿 D3 采集器先例）：dump_mapping_csv 落盘映射表（运行时产物不入
git），load_mapping 读回（880 目标不在 TDX 主数据→ValueError fail-closed）。

接线待办（Owner 窗口）：8803/8804 行业指数分钟K线当前未入
kline_sector_intraday（该表现存 8800/8802/8805-8809 + 异构 881 共 593 码），
资金卡全链路（卡1/3/4 行业腿覆盖）需 8803/8804 采集接线后排期。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: SectorFundFlowEntry 行集（sector_fund_flow_collector 产出，THS 行业名+净额）
# - id: I2
#   name: 映射表（SSoT=SECTOR_881_TO_880 90 行 / CSV 读回）
# 层: 算法
# - id: A1
#   name_zh: 重钥（纯函数）
#   desc: industry 行按 name→881→880 重钥，同目标 SUM；concept/空净额/未知名跳过留痕
# - id: A2
#   name_zh: CSV 中间层
#   desc: dump_mapping_csv 落盘 / load_mapping 读回（880 目标引用完整性 fail-closed）
# 层: 输出
# - id: O1
#   name_zh: RekeyResult{fund_flow: dict[880code, float], 留痕四件} / 132 条 880 中文名表
#   intro: fund_flow 直插 build_counter_trend_board fund_flow 注入位
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I2 --> A2
# A1 --> O1
# A2 --> O1
"""

from __future__ import annotations

import csv
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final, Iterable, Mapping

logger = logging.getLogger(__name__)

__all__: Final = [
    "MAPPING_CSV_COLUMNS",
    "SECTOR_881_TO_880",
    "TDX_INDUSTRY_BOARDS",
    "RekeyResult",
    "SectorCodeBridge",
    "SectorCodeBridgeRow",
    "TdxIndustryBoard",
    "default_mapping",
    "dump_mapping_csv",
    "fund_flow_for_card",
    "fund_flow_for_segment",
    "load_mapping",
    "rekey_sector_fund_flow",
    "rekey_segment_fund_flow",
    "sector_names_880",
    "segment_net_inflow",
]

#: 映射 CSV 列序（name_880/t_code 由 TDX 主数据派生落盘，读回时校验引用完整性）
MAPPING_CSV_COLUMNS: Final = (
    "code_881",
    "name_881",
    "code_880",
    "name_880",
    "t_code",
    "match_kind",
    "note",
)


@dataclass(frozen=True, slots=True)
class TdxIndustryBoard:
    """TDX 8803/8804 行业指数主数据行（名源=tdxzs.cfg，T 码=通达信行业分类码）。"""

    code: str  # 880xxx（8803/8804 族）
    name: str  # TDX 板块名
    t_code: str  # 通达信行业分类码（T 开头层级码）


@dataclass(frozen=True, slots=True)
class SectorCodeBridgeRow:
    """881→880 映射行（一个 THS 一级行业 → 一个 TDX 行业指数主映射）。"""

    code_881: str  # THS 行业指数码（sector_meta 真源）
    name_881: str  # THS 行业名（采集器产出行 sector_name 对齐键）
    code_880: str  # TDX 行业指数码（8803/8804 族，重钥目标）
    match_kind: str  # exact/semantic/aggregate
    note: str = ""  # 未配腿/低置信留痕


@dataclass(frozen=True, slots=True)
class RekeyResult:
    """重钥结果（fund_flow 直插逆势榜 fund_flow 注入位；留痕四件供观测）。"""

    fund_flow: dict[str, float] = field(default_factory=dict)  # {880code: 净流入}
    mapped_codes: tuple[str, ...] = ()  # 实际命中重钥的 881 码（升序去重）
    unmapped_sectors: tuple[str, ...] = ()  # 未知名（不在映射 90 名内）
    null_value_sectors: tuple[str, ...] = ()  # 净额 None 跳过
    skipped_concept_rows: int = 0  # concept 行跳过计数


# ---------------------------------------------------------------------------
# TDX 8803/8804 行业指数主数据（132 条；2026-08-24 提取自 TDX 客户端 tdxzs.cfg）
# ---------------------------------------------------------------------------

TDX_INDUSTRY_BOARDS: Final[tuple[TdxIndustryBoard, ...]] = tuple(
    TdxIndustryBoard(code=c, name=n, t_code=t)
    for c, n, t in (
        ("880301", "煤炭", "T0101"),
        ("880302", "煤炭开采", "T010101"),
        ("880303", "焦炭加工", "T010102"),
        ("880305", "电力", "T0102"),
        ("880306", "水力发电", "T010201"),
        ("880307", "火力发电", "T010202"),
        ("880308", "新型电力", "T010203"),
        ("880310", "石油", "T0103"),
        ("880311", "石油开采", "T010301"),
        ("880312", "石油加工", "T010302"),
        ("880313", "石油贸易", "T010303"),
        ("880318", "钢铁", "T0201"),
        ("880319", "普钢", "T020101"),
        ("880320", "特种钢", "T020102"),
        ("880321", "钢加工", "T020103"),
        ("880324", "有色", "T0202"),
        ("880325", "铜", "T020201"),
        ("880326", "铝", "T020202"),
        ("880327", "铅锌", "T020203"),
        ("880328", "黄金", "T020204"),
        ("880329", "小金属", "T020205"),
        ("880330", "化纤", "T0203"),
        ("880335", "化工", "T0204"),
        ("880336", "化工原料", "T020401"),
        ("880337", "农药化肥", "T020402"),
        ("880338", "塑料", "T020404"),
        ("880339", "橡胶", "T020405"),
        ("880340", "染料涂料", "T020406"),
        ("880344", "建材", "T0206"),
        ("880345", "陶瓷", "T020601"),
        ("880346", "水泥", "T020602"),
        ("880347", "玻璃", "T020603"),
        ("880348", "其他建材", "T020604"),
        ("880350", "造纸", "T0207"),
        ("880351", "矿物制品", "T0208"),
        ("880355", "日用化工", "T0301"),
        ("880360", "农林牧渔", "T0302"),
        ("880361", "种植业", "T030201"),
        ("880362", "渔业", "T030202"),
        ("880363", "林业", "T030203"),
        ("880364", "饲料", "T030204"),
        ("880366", "农业综合", "T030206"),
        ("880367", "纺织服饰", "T0303"),
        ("880368", "纺织", "T030301"),
        ("880369", "服饰", "T030302"),
        ("880372", "食品饮料", "T0304"),
        ("880373", "乳制品", "T030401"),
        ("880374", "软饮料", "T030402"),
        ("880375", "食品", "T030403"),
        ("880380", "酿酒", "T0305"),
        ("880381", "白酒", "T030501"),
        ("880382", "啤酒", "T030502"),
        ("880383", "红黄酒", "T030503"),
        ("880387", "家用电器", "T0401"),
        ("880390", "汽车类", "T0402"),
        ("880391", "汽车整车", "T040201"),
        ("880392", "汽车配件", "T040202"),
        ("880393", "汽车服务", "T040203"),
        ("880394", "摩托车", "T040204"),
        ("880398", "医疗保健", "T0403"),
        ("880399", "家居用品", "T0404"),
        ("880400", "医药", "T0405"),
        ("880401", "化学制药", "T040501"),
        ("880402", "生物制药", "T040502"),
        ("880403", "中成药", "T040503"),
        ("880406", "商业连锁", "T0501"),
        ("880407", "百货", "T050101"),
        ("880408", "超市连锁", "T050102"),
        ("880409", "电器连锁", "T050103"),
        ("880410", "医药商业", "T050104"),
        ("880411", "其他商业", "T050105"),
        ("880412", "商品城", "T050106"),
        ("880413", "批发业", "T050107"),
        ("880414", "商贸代理", "T0502"),
        ("880418", "传媒娱乐", "T0601"),
        ("880419", "出版业", "T060101"),
        ("880420", "影视音像", "T060102"),
        ("880421", "广告包装", "T0602"),
        ("880422", "文教休闲", "T0603"),
        ("880423", "酒店餐饮", "T0604"),
        ("880424", "旅游", "T0605"),
        ("880425", "旅游服务", "T060501"),
        ("880426", "旅游景点", "T060502"),
        ("880430", "航空", "T0701"),
        ("880431", "船舶", "T0702"),
        ("880432", "运输设备", "T0703"),
        ("880437", "通用机械", "T0704"),
        ("880438", "机床制造", "T070401"),
        ("880439", "机械基件", "T070402"),
        ("880440", "工业机械", "T0705"),
        ("880441", "化工机械", "T070501"),
        ("880442", "轻工机械", "T070502"),
        ("880443", "纺织机械", "T070504"),
        ("880444", "农用机械", "T070505"),
        ("880445", "专用机械", "T070506"),
        ("880446", "电气设备", "T0706"),
        ("880447", "工程机械", "T0707"),
        ("880448", "电器仪表", "T0708"),
        ("880452", "电信运营", "T0801"),
        ("880453", "公共交通", "T0802"),
        ("880454", "水务", "T0803"),
        ("880455", "供气供热", "T0804"),
        ("880456", "环境保护", "T0805"),
        ("880459", "运输服务", "T0901"),
        ("880460", "铁路", "T090101"),
        ("880461", "水运", "T090102"),
        ("880462", "空运", "T090103"),
        ("880463", "公路", "T090104"),
        ("880464", "仓储物流", "T0902"),
        ("880465", "交通设施", "T0903"),
        ("880466", "路桥", "T090301"),
        ("880467", "机场", "T090302"),
        ("880468", "港口", "T090303"),
        ("880471", "银行", "T1001"),
        ("880472", "证券", "T1002"),
        ("880473", "保险", "T1003"),
        ("880474", "多元金融", "T1004"),
        ("880476", "建筑", "T1101"),
        ("880477", "建筑工程", "T110101"),
        ("880478", "装修装饰", "T110102"),
        ("880482", "房地产", "T1102"),
        ("880483", "全国地产", "T110201"),
        ("880484", "区域地产", "T110202"),
        ("880485", "园区开发", "T110203"),
        ("880486", "房产服务", "T110204"),
        ("880489", "IT设备", "T1201"),
        ("880490", "通信设备", "T1202"),
        ("880491", "半导体", "T1203"),
        ("880492", "元器件", "T1204"),
        ("880493", "软件服务", "T1205"),
        ("880494", "互联网", "T1206"),
        ("880497", "综合类", "T1301"),
    )
)

_BOARD_INDEX: Final[dict[str, TdxIndustryBoard]] = {b.code: b for b in TDX_INDUSTRY_BOARDS}

# ---------------------------------------------------------------------------
# 881→880 映射 SSoT（90 行；881 码/名=sector_meta 2026-08-24 真源，90/90 实证）
# match_kind: exact=名称对应 18 / semantic=语义对应 54 / aggregate=上卷聚合 18
# ---------------------------------------------------------------------------

SECTOR_881_TO_880: Final[tuple[SectorCodeBridgeRow, ...]] = tuple(
    SectorCodeBridgeRow(code_881=c1, name_881=n1, code_880=c8, match_kind=k, note=note)
    for c1, n1, c8, k, note in (
        ("881101", "种植业与林业", "880361", "semantic", "TDX 种植业/林业分列，主映射种植业（成分权重主导），林业腿 880363 未配"),
        ("881102", "养殖业", "880360", "aggregate", "TDX 无畜牧单列板块，上卷农林牧渔聚合（水产腿 T030202 含于该聚合）"),
        ("881103", "农产品加工", "880375", "aggregate", "粮油糖料加工就近食品（与 881134 同目标 SUM）；饲料腿 T030204 未单列"),
        ("881105", "煤炭开采加工", "880301", "aggregate", "THS 含焦炭洗选，对齐 TDX T0101 全族聚合（880302 仅开采缺焦炭腿）"),
        ("881107", "油气开采及服务", "880311", "semantic", "石油开采（油服腿随开采口径 T010301）"),
        ("881108", "化学原料", "880336", "semantic", "化工原料 T020401（与 881172 同目标 SUM）"),
        ("881109", "化学制品", "880335", "aggregate", "TDX 化学制品粒度粗，上卷 T0204 化工聚合"),
        ("881112", "钢铁", "880318", "exact", ""),
        ("881114", "金属新材料", "880324", "aggregate", "TDX 无新材料板块，上卷 T0202 有色聚合（与 881168 同目标 SUM）"),
        ("881115", "建筑材料", "880344", "semantic", "建材 T0206 聚合（水泥/玻璃/陶瓷/其他建材）"),
        ("881116", "建筑装饰", "880476", "aggregate", "THS 含房建/基建/专业工程，对齐 T1101 建筑聚合"),
        ("881117", "通用设备", "880437", "semantic", "通用机械 T0704"),
        ("881118", "专用设备", "880445", "semantic", "专用机械 T070506"),
        ("881121", "半导体", "880491", "exact", ""),
        ("881122", "光学光电子", "880492", "aggregate", "面板归 TDX T1204 元器件（SUM 组）"),
        ("881123", "其他电子", "880492", "aggregate", "元器件 SUM 组"),
        ("881124", "消费电子", "880492", "aggregate", "立讯/歌尔等 TDX 归元器件 T1204（SUM 组）"),
        ("881125", "汽车整车", "880391", "exact", ""),
        ("881126", "汽车零部件", "880392", "semantic", "汽车配件 T040202"),
        ("881128", "汽车服务及其他", "880393", "exact", ""),
        ("881129", "通信设备", "880490", "exact", ""),
        ("881130", "计算机设备", "880489", "semantic", "IT设备 T1201"),
        ("881131", "白色家电", "880387", "aggregate", "家电全族聚合（SUM 组）"),
        ("881132", "黑色家电", "880387", "aggregate", "家电 SUM 组"),
        ("881133", "饮料制造", "880374", "semantic", "软饮料 T030402（乳制品腿 T030401 未单列）"),
        ("881134", "食品加工制造", "880375", "semantic", "食品 T030403（与 881103 同目标 SUM）"),
        ("881135", "纺织制造", "880368", "semantic", "纺织 T030301"),
        ("881136", "服装家纺", "880369", "semantic", "服饰 T030302（家纺腿随服饰口径）"),
        ("881137", "造纸", "880350", "exact", ""),
        ("881138", "包装印刷", "880421", "semantic", "广告包装 T0602"),
        ("881139", "家居用品", "880399", "exact", ""),
        ("881140", "化学制药", "880401", "exact", ""),
        ("881141", "中药", "880403", "semantic", "中成药 T040503"),
        ("881142", "生物制品", "880402", "semantic", "生物制药 T040502"),
        ("881143", "医药商业", "880410", "exact", ""),
        ("881144", "医疗器械", "880398", "semantic", "医疗保健 T0403（与 881175 同目标 SUM）"),
        ("881145", "电力", "880305", "exact", ""),
        ("881146", "燃气", "880455", "semantic", "供气供热 T0804"),
        ("881148", "港口航运", "880461", "semantic", "航运权重主导归水运 T090102（港口腿 880468 未配）"),
        ("881149", "公路铁路运输", "880460", "semantic", "铁路权重略主导 T090101（公路腿 880463 未配）"),
        ("881151", "机场航运", "880462", "semantic", "航空机场归空运 T090103（机场腿 880467 未配）"),
        ("881152", "物流", "880464", "semantic", "仓储物流 T0902"),
        ("881153", "房地产", "880482", "exact", ""),
        ("881155", "银行", "880471", "exact", ""),
        ("881156", "保险", "880473", "exact", ""),
        ("881157", "证券", "880472", "exact", ""),
        ("881158", "零售", "880406", "semantic", "商业连锁 T0501 聚合"),
        ("881159", "贸易", "880413", "semantic", "批发业 T050107"),
        ("881160", "旅游及酒店", "880424", "semantic", "旅游 T0605 聚合（酒店腿 880423 未配）"),
        ("881162", "通信服务", "880452", "semantic", "电信运营 T0801（增值服务腿随运营口径）"),
        ("881164", "文化传媒", "880418", "semantic", "传媒娱乐 T0601 聚合"),
        ("881165", "综合", "880497", "semantic", "综合类 T1301（与 881179 同目标 SUM）"),
        ("881166", "军工装备", "880430", "aggregate", "TDX 无军工行业板，主机厂权重归航空 T0701（船舶腿 880431 未配）"),
        ("881167", "非金属材料", "880351", "semantic", "矿物制品 T0208"),
        ("881168", "工业金属", "880324", "semantic", "有色 T0202 聚合（与 881114 同目标 SUM）"),
        ("881169", "贵金属", "880328", "semantic", "黄金 T020204（白银腿随黄金口径）"),
        ("881170", "小金属", "880329", "exact", ""),
        ("881171", "自动化设备", "880440", "aggregate", "工业机械 T0705（电气设备腿 T0706 未单列）"),
        ("881172", "电子化学品", "880336", "aggregate", "半导体材料归化工原料 T020401（与 881108 同目标 SUM）"),
        ("881173", "小家电", "880387", "aggregate", "家电 SUM 组"),
        ("881174", "厨卫电器", "880387", "aggregate", "家电 SUM 组"),
        ("881175", "医疗服务", "880398", "semantic", "医疗保健 T0403（CXO/眼科/口腔随医疗口径，与 881144 SUM）"),
        ("881177", "互联网电商", "880494", "semantic", "互联网 T1206（与 881275 同目标 SUM）"),
        ("881178", "教育", "880422", "semantic", "文教休闲 T0603"),
        ("881179", "其他社会服务", "880497", "aggregate", "TDX 无专业服务板，归综合类（与 881165 SUM，低置信留痕）"),
        ("881180", "石油加工贸易", "880312", "semantic", "石油加工 T010302（贸易腿 880313 未配）"),
        ("881181", "环境治理", "880456", "semantic", "环境保护 T0805（与 881284 同目标 SUM）"),
        ("881182", "美容护理", "880355", "semantic", "日用化工 T0301（医美腿 T0403 未单列）"),
        ("881263", "农化制品", "880337", "semantic", "农药化肥 T020402"),
        ("881264", "化学纤维", "880330", "semantic", "化纤 T0203"),
        ("881265", "塑料制品", "880338", "semantic", "塑料 T020404"),
        ("881266", "橡胶制品", "880339", "semantic", "橡胶 T020405"),
        ("881267", "能源金属", "880329", "semantic", "锂钴镍归小金属 T020205（与 881170 同目标 SUM）"),
        ("881268", "工程机械", "880447", "exact", ""),
        ("881269", "轨交设备", "880432", "semantic", "运输设备 T0703"),
        ("881270", "元件", "880492", "semantic", "元器件 T1204（SUM 组）"),
        ("881271", "IT服务", "880493", "semantic", "软件服务 T1205（与 881272 同目标 SUM）"),
        ("881272", "软件开发", "880493", "semantic", "软件服务 T1205（SUM 组）"),
        ("881273", "白酒", "880381", "exact", ""),
        ("881274", "影视院线", "880420", "semantic", "影视音像 T060102"),
        ("881275", "游戏", "880494", "aggregate", "游戏股 TDX 多归互联网 T1206（与 881177 SUM，低置信留痕）"),
        ("881276", "军工电子", "880492", "aggregate", "元器件 T1204（SUM 组，半导体腿 T1203 未单列）"),
        ("881277", "电机", "880446", "semantic", "电气设备 T0706（SUM 组）"),
        ("881278", "电网设备", "880446", "semantic", "电气设备 T0706（SUM 组）"),
        ("881279", "光伏设备", "880446", "aggregate", "电气设备 T0706（SUM 组；跨归属个股随 TDX 单分类口径）"),
        ("881280", "风电设备", "880446", "semantic", "电气设备 T0706（SUM 组）"),
        ("881281", "电池", "880446", "semantic", "电气设备 T0706（SUM 组）"),
        ("881282", "其他电源设备", "880446", "semantic", "电气设备 T0706（SUM 组）"),
        ("881283", "多元金融", "880474", "exact", ""),
        ("881284", "环保设备", "880456", "aggregate", "环境保护 T0805（与 881181 同目标 SUM；装备腿 T0705 未单列）"),
    )
)


def default_mapping() -> tuple[SectorCodeBridgeRow, ...]:
    """映射 SSoT（90 行，模块内常量直出）。"""
    return SECTOR_881_TO_880


def load_mapping(path: str | Path) -> tuple[SectorCodeBridgeRow, ...]:
    """CSV 中间层读回（880 目标/name_880/t_code 引用完整性校验，fail-closed）。

    Raises:
        ValueError: 880 目标不在 TDX 主数据，或 name_880/t_code 与主数据不一致。
    """
    rows: list[SectorCodeBridgeRow] = []
    with Path(path).open("r", encoding="utf-8", newline="") as f:
        for rec in csv.DictReader(f):
            code_880 = str(rec["code_880"]).strip()
            board = _BOARD_INDEX.get(code_880)
            if board is None:
                raise ValueError(f"映射 CSV 880 目标不在 TDX 主数据: {code_880!r}")
            if str(rec["name_880"]).strip() != board.name or str(rec["t_code"]).strip() != board.t_code:
                raise ValueError(f"映射 CSV 880 目标与主数据不一致: {code_880!r}")
            rows.append(
                SectorCodeBridgeRow(
                    code_881=str(rec["code_881"]).strip(),
                    name_881=str(rec["name_881"]).strip(),
                    code_880=code_880,
                    match_kind=str(rec["match_kind"]).strip(),
                    note=str(rec.get("note") or "").strip(),
                )
            )
    return tuple(rows)


def dump_mapping_csv(path: str | Path, mapping: Iterable[SectorCodeBridgeRow] | None = None) -> str:
    """映射表 CSV 中间层落盘（运行时产物不入 git；父目录自动创建，覆盖写）。"""
    rows = list(mapping) if mapping is not None else list(SECTOR_881_TO_880)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(MAPPING_CSV_COLUMNS))
        writer.writeheader()
        for r in rows:
            board = _BOARD_INDEX[r.code_880]
            writer.writerow(
                {
                    "code_881": r.code_881,
                    "name_881": r.name_881,
                    "code_880": r.code_880,
                    "name_880": board.name,
                    "t_code": board.t_code,
                    "match_kind": r.match_kind,
                    "note": r.note,
                }
            )
    return str(p)


def rekey_sector_fund_flow(
    entries: Iterable[Any],
    mapping: Iterable[SectorCodeBridgeRow] | None = None,
) -> RekeyResult:
    """重钥（纯函数）：881 侧采集产出 → 880 侧消费形态 {880code: 净流入}。

    口径：仅 industry 行参与（concept 行跳过计数）；name→881→880 主映射；
    多 881 同目标净额 SUM（THS 行业互不相交故可加）；净额 None/未知名跳过留痕。
    entries 鸭子类型读取 sector_type/sector_name/net_amount（对齐 SectorFundFlowEntry）。
    """
    rows = list(mapping) if mapping is not None else SECTOR_881_TO_880
    by_name = {r.name_881: r for r in rows}
    fund_flow: dict[str, float] = {}
    mapped: set[str] = set()
    unmapped: list[str] = []
    null_named: list[str] = []
    skipped_concept = 0
    for e in entries:
        if str(getattr(e, "sector_type", "")) != "industry":
            skipped_concept += 1
            continue
        name = str(getattr(e, "sector_name", "") or "").strip()
        row = by_name.get(name)
        if row is None:
            unmapped.append(name)
            continue
        net = getattr(e, "net_amount", None)
        if net is None:
            null_named.append(name)
            continue
        fund_flow[row.code_880] = fund_flow.get(row.code_880, 0.0) + float(net)
        mapped.add(row.code_881)
    return RekeyResult(
        fund_flow=fund_flow,
        mapped_codes=tuple(sorted(mapped)),
        unmapped_sectors=tuple(unmapped),
        null_value_sectors=tuple(null_named),
        skipped_concept_rows=skipped_concept,
    )


def fund_flow_for_card(
    entries: Iterable[Any],
    mapping: Iterable[SectorCodeBridgeRow] | None = None,
) -> dict[str, float]:
    """逆势榜资金卡注入形态（=rekey(...).fund_flow，直插 build_counter_trend_board）。"""
    return rekey_sector_fund_flow(entries, mapping).fund_flow


# ---------------------------------------------------------------------------
# 段内差分（GAP-F-16 注入适配器核：当日累计快照 → 段内净流入 → 880 重钥）
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _SegmentFlowEntry:
    """段差分产物行（鸭子类型对齐 SectorFundFlowEntry 三字段，供 rekey 复用）。"""

    sector_name: str
    net_amount: float  # 段内净流入（亿元，差分结果）
    sector_type: str = "industry"


def segment_net_inflow(
    rows: Iterable[tuple[str, Any, Any]],
    start_ts: str,
    end_ts: str,
) -> dict[str, float]:
    """段内净流入差分（纯函数）：{THS 板块名: 段末累计 − 段前累计}（亿元）。

    口径（对齐 D3FUND 报告 §1 差分裁定）：
    - 净额=当日累计（THS 原始口径），快照时刻按分钟截断对齐（str(ts)[:16]，
      与 kline_sector_intraday 分钟粒度一致；起界分钟快照归段前侧、止界分钟
      快照归段末侧，轮询粒度 ±1 分钟口径留痕）；
    - 段前累计=最后一条 ≤start_ts 的快照（无 → 0.0，开盘累计起点为零）；
    - 段末累计=最后一条 (start_ts, end_ts] 内快照（段内无新快照 → 该板块
      不出现在输出：段内无观测如实缺席，不伪造 0 净流入）；
    - 净额 None 行跳过；差分可为负（消费方自筛正流入，本函数不伪造）。

    Args:
        rows: 快照行 (sector_name, timestamp, net_amount) 迭代（CH 查询行鸭子类型）。
        start_ts/end_ts: 段界分钟 'YYYY-MM-DD HH:MM'（逆势榜 down_start/end_ts）。
    """
    start_m = str(start_ts)[:16]
    end_m = str(end_ts)[:16]
    cum_start: dict[str, tuple[str, float]] = {}
    cum_end: dict[str, tuple[str, float]] = {}
    for name, ts, net in rows:
        if net is None:
            continue
        minute = str(ts)[:16]
        key = str(name)
        val = float(net)
        if minute <= start_m:
            prev = cum_start.get(key)
            if prev is None or minute >= prev[0]:
                cum_start[key] = (minute, val)
        if start_m < minute <= end_m:
            prev = cum_end.get(key)
            if prev is None or minute >= prev[0]:
                cum_end[key] = (minute, val)
    return {k: v[1] - cum_start.get(k, ("", 0.0))[1] for k, v in cum_end.items()}


def rekey_segment_fund_flow(
    rows: Iterable[tuple[str, Any, Any]],
    start_ts: str,
    end_ts: str,
    mapping: Iterable[SectorCodeBridgeRow] | None = None,
) -> RekeyResult:
    """段差分+重钥一条龙（纯函数）：快照行 → {880code: 段内净流入}（含留痕四件）。"""
    diff = segment_net_inflow(rows, start_ts, end_ts)
    entries = [_SegmentFlowEntry(sector_name=n, net_amount=v) for n, v in diff.items()]
    return rekey_sector_fund_flow(entries, mapping)


def fund_flow_for_segment(
    rows: Iterable[tuple[str, Any, Any]],
    start_ts: str,
    end_ts: str,
    mapping: Iterable[SectorCodeBridgeRow] | None = None,
) -> dict[str, float]:
    """逆势榜资金卡段内注入形态（=rekey_segment_fund_flow(...).fund_flow）。"""
    return rekey_segment_fund_flow(rows, start_ts, end_ts, mapping).fund_flow


def sector_names_880(mapping: Iterable[SectorCodeBridgeRow] | None = None) -> dict[str, str]:
    """880 中文名表（CounterTrendConfig.sector_names 回显用；全 132 条主数据）。"""
    _ = mapping  # 预留：按映射子集过滤（当前全量回显，消费方 names.get 缺省安全）
    return {b.code: b.name for b in TDX_INDUSTRY_BOARDS}


class SectorCodeBridge:
    """881xxx→880xxx 桥接适配器（映射可注入/CSV 可换，默认 SSoT 90 行）。"""

    def __init__(self, mapping: Iterable[SectorCodeBridgeRow] | None = None) -> None:
        self._mapping: tuple[SectorCodeBridgeRow, ...] = (
            tuple(mapping) if mapping is not None else SECTOR_881_TO_880
        )

    @classmethod
    def from_csv(cls, path: str | Path) -> SectorCodeBridge:
        """CSV 中间层装配（load_mapping 引用完整性 fail-closed）。"""
        return cls(load_mapping(path))

    @property
    def mapping(self) -> tuple[SectorCodeBridgeRow, ...]:
        return self._mapping

    def rekey(self, entries: Iterable[Any]) -> RekeyResult:
        """采集产出 → RekeyResult（fund_flow + 留痕四件）。"""
        return rekey_sector_fund_flow(entries, self._mapping)

    def fund_flow(self, entries: Iterable[Any]) -> dict[str, float]:
        """逆势榜资金卡注入形态 {880code: 净流入}。"""
        return self.rekey(entries).fund_flow

    def sector_names(self) -> dict[str, str]:
        """880 中文名表（全 132 条）。"""
        return sector_names_880(self._mapping)

    def dump_csv(self, path: str | Path) -> str:
        """当前映射落 CSV 中间层。"""
        return dump_mapping_csv(path, self._mapping)
