# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_sector_code_bridge
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.implementations.sector_code_bridge; zephyr.data.implementations.sector_fund_flow_collector; zephyr.signal_ashare.counter_trend_board
# [CONSUMERS] none
# [STARTUP] pytest
# [INVARIANTS] 不触网不触库；映射表 90/90 断言基于模块内 SSoT 常量；消费方契约经 build_counter_trend_board 真调验证
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=881→880 桥接映射/重钥/消费形态契约缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-DAT-sector_code_bridge_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""sector_code_bridge 881xxx→880xxx 桥接适配器 单元测试（GAP-F-16，不触网不触库）。

覆盖：映射覆盖率（90/90 零缺失，锚定 sector_meta 实证 90 名）、880 目标引用完整性
（TDX 行业指数主数据 132 条内）、重钥语义（SUM 聚合/概念行跳过/空净额跳过/未映射留痕）、
消费方形态契约（build_counter_trend_board fund_flow 注入）、CSV 中间层 roundtrip。
"""

from __future__ import annotations

import json
import re

import pytest

from src.zephyr.data.implementations.sector_code_bridge import (
    MAPPING_CSV_COLUMNS,
    SECTOR_881_TO_880,
    TDX_INDUSTRY_BOARDS,
    RekeyResult,
    SectorCodeBridge,
    SectorCodeBridgeRow,
    default_mapping,
    dump_mapping_csv,
    fund_flow_for_card,
    load_mapping,
    rekey_sector_fund_flow,
    sector_names_880,
)
from src.zephyr.data.implementations.sector_fund_flow_collector import SectorFundFlowEntry
from src.zephyr.signal_ashare.counter_trend_board import (
    CounterTrendConfig,
    build_counter_trend_board,
)

# ---------------------------------------------------------------------------
# 实证锚（2026-08-24 活体校验）：c1_market.sector_meta 90 个 881xxx↔THS 名，
# 与 akshare stock_fund_flow_industry(即时) 90 行业名 90/90 对齐零缺失。
# ---------------------------------------------------------------------------
THS_INDUSTRY_90: frozenset[tuple[str, str]] = frozenset(
    {
        ("881101", "种植业与林业"),
        ("881102", "养殖业"),
        ("881103", "农产品加工"),
        ("881105", "煤炭开采加工"),
        ("881107", "油气开采及服务"),
        ("881108", "化学原料"),
        ("881109", "化学制品"),
        ("881112", "钢铁"),
        ("881114", "金属新材料"),
        ("881115", "建筑材料"),
        ("881116", "建筑装饰"),
        ("881117", "通用设备"),
        ("881118", "专用设备"),
        ("881121", "半导体"),
        ("881122", "光学光电子"),
        ("881123", "其他电子"),
        ("881124", "消费电子"),
        ("881125", "汽车整车"),
        ("881126", "汽车零部件"),
        ("881128", "汽车服务及其他"),
        ("881129", "通信设备"),
        ("881130", "计算机设备"),
        ("881131", "白色家电"),
        ("881132", "黑色家电"),
        ("881133", "饮料制造"),
        ("881134", "食品加工制造"),
        ("881135", "纺织制造"),
        ("881136", "服装家纺"),
        ("881137", "造纸"),
        ("881138", "包装印刷"),
        ("881139", "家居用品"),
        ("881140", "化学制药"),
        ("881141", "中药"),
        ("881142", "生物制品"),
        ("881143", "医药商业"),
        ("881144", "医疗器械"),
        ("881145", "电力"),
        ("881146", "燃气"),
        ("881148", "港口航运"),
        ("881149", "公路铁路运输"),
        ("881151", "机场航运"),
        ("881152", "物流"),
        ("881153", "房地产"),
        ("881155", "银行"),
        ("881156", "保险"),
        ("881157", "证券"),
        ("881158", "零售"),
        ("881159", "贸易"),
        ("881160", "旅游及酒店"),
        ("881162", "通信服务"),
        ("881164", "文化传媒"),
        ("881165", "综合"),
        ("881166", "军工装备"),
        ("881167", "非金属材料"),
        ("881168", "工业金属"),
        ("881169", "贵金属"),
        ("881170", "小金属"),
        ("881171", "自动化设备"),
        ("881172", "电子化学品"),
        ("881173", "小家电"),
        ("881174", "厨卫电器"),
        ("881175", "医疗服务"),
        ("881177", "互联网电商"),
        ("881178", "教育"),
        ("881179", "其他社会服务"),
        ("881180", "石油加工贸易"),
        ("881181", "环境治理"),
        ("881182", "美容护理"),
        ("881263", "农化制品"),
        ("881264", "化学纤维"),
        ("881265", "塑料制品"),
        ("881266", "橡胶制品"),
        ("881267", "能源金属"),
        ("881268", "工程机械"),
        ("881269", "轨交设备"),
        ("881270", "元件"),
        ("881271", "IT服务"),
        ("881272", "软件开发"),
        ("881273", "白酒"),
        ("881274", "影视院线"),
        ("881275", "游戏"),
        ("881276", "军工电子"),
        ("881277", "电机"),
        ("881278", "电网设备"),
        ("881279", "光伏设备"),
        ("881280", "风电设备"),
        ("881281", "电池"),
        ("881282", "其他电源设备"),
        ("881283", "多元金融"),
        ("881284", "环保设备"),
    }
)

_CODE_881_RE = re.compile(r"^881\d{3}$")
_CODE_880_RE = re.compile(r"^880[34]\d{2}$")


def _entry(name: str, net: float | None, sector_type: str = "industry") -> SectorFundFlowEntry:
    """合成采集器产出行（最小字段，重钥只读 sector_type/sector_name/net_amount）。"""
    return SectorFundFlowEntry(
        trade_date="2026-08-24",
        timestamp="2026-08-24 10:30:00",
        sector_type=sector_type,
        sector_name=name,
        sector_index=None,
        pct_change=None,
        inflow_amount=None,
        outflow_amount=None,
        net_amount=net,
        company_count=None,
        lead_stock="",
        lead_pct_change=None,
    )


# ---------- 映射覆盖率（90/90 零缺失） ----------


class TestMappingCoverage:
    def test_exactly_90_rows_covering_ths_industry_universe(self):
        rows = default_mapping()
        assert len(rows) == 90
        pairs = {(r.code_881, r.name_881) for r in rows}
        assert pairs == THS_INDUSTRY_90  # 90/90 全映射零缺失（实证锚）

    def test_code_881_format_and_uniqueness(self):
        codes = [r.code_881 for r in SECTOR_881_TO_880]
        assert len(set(codes)) == 90
        assert all(_CODE_881_RE.match(c) for c in codes)

    def test_code_880_referential_integrity(self):
        """每个 880 目标必须存在于 TDX 行业指数主数据（132 条）且名称/T 码一致。"""
        boards = {b.code: b for b in TDX_INDUSTRY_BOARDS}
        assert len(boards) == 132
        for r in SECTOR_881_TO_880:
            assert _CODE_880_RE.match(r.code_880), r
            assert r.code_880 in boards, f"{r.code_881} {r.name_881} 目标 {r.code_880} 不在 TDX 主数据"
            assert boards[r.code_880].t_code.startswith("T"), r.code_880

    def test_known_anchor_mappings(self):
        """锚点抽查（exact 语义对应）。"""
        idx = {r.code_881: r.code_880 for r in SECTOR_881_TO_880}
        assert idx["881169"] == "880328"  # 贵金属 → 黄金
        assert idx["881155"] == "880471"  # 银行 → 银行
        assert idx["881121"] == "880491"  # 半导体 → 半导体
        assert idx["881145"] == "880305"  # 电力 → 电力
        assert idx["881157"] == "880472"  # 证券 → 证券

    def test_aggregate_sum_groups(self):
        """多 881 同目标聚合组留痕（SUM 语义依赖此分组）。"""
        by880: dict[str, set[str]] = {}
        for r in SECTOR_881_TO_880:
            by880.setdefault(r.code_880, set()).add(r.code_881)
        assert by880["880446"] == {"881277", "881278", "881279", "881280", "881281", "881282"}  # 电气设备族
        assert by880["880387"] == {"881131", "881132", "881173", "881174"}  # 家用电器族
        assert by880["880492"] == {"881122", "881123", "881124", "881270", "881276"}  # 元器件族

    def test_match_kind_vocabulary(self):
        assert {r.match_kind for r in SECTOR_881_TO_880} <= {"exact", "semantic", "aggregate"}

    def test_mapping_rows_json_serializable(self):
        from dataclasses import asdict

        json.dumps([asdict(r) for r in SECTOR_881_TO_880], ensure_ascii=False)
        assert isinstance(SECTOR_881_TO_880[0], SectorCodeBridgeRow)


# ---------- 重钥语义 ----------


class TestRekeySemantics:
    def test_single_industry_rekeyed_to_880(self):
        res = rekey_sector_fund_flow([_entry("贵金属", 2.73)])
        assert res.fund_flow == {"880328": pytest.approx(2.73)}
        assert res.unmapped_sectors == ()

    def test_sum_aggregation_same_880_target(self):
        """电网设备+光伏设备+电池 → 同目标 880446 电气设备，净额 SUM。"""
        res = rekey_sector_fund_flow(
            [
                _entry("电网设备", 1.0),
                _entry("光伏设备", 2.0),
                _entry("电池", -0.5),
            ]
        )
        assert res.fund_flow == {"880446": pytest.approx(2.5)}

    def test_concept_rows_skipped_with_trace(self):
        res = rekey_sector_fund_flow([_entry("转基因", 1.32, sector_type="concept")])
        assert res.fund_flow == {}
        assert res.skipped_concept_rows == 1

    def test_null_net_amount_skipped_with_trace(self):
        res = rekey_sector_fund_flow([_entry("贵金属", None)])
        assert res.fund_flow == {}
        assert res.null_value_sectors == ("贵金属",)

    def test_unknown_sector_name_unmapped_not_crash(self):
        res = rekey_sector_fund_flow([_entry("不存在的板块", 1.0)])
        assert res.fund_flow == {}
        assert res.unmapped_sectors == ("不存在的板块",)

    def test_mixed_rows_full_flow(self):
        res = rekey_sector_fund_flow(
            [
                _entry("银行", 10.0),
                _entry("证券", -3.0),
                _entry("保险", None),
                _entry("转基因", 1.0, sector_type="concept"),
                _entry("幽灵板块", 9.9),
            ]
        )
        assert res.fund_flow["880471"] == pytest.approx(10.0)
        assert res.fund_flow["880472"] == pytest.approx(-3.0)
        assert set(res.fund_flow) == {"880471", "880472"}
        assert res.null_value_sectors == ("保险",)
        assert res.unmapped_sectors == ("幽灵板块",)
        assert res.skipped_concept_rows == 1
        assert sorted(res.mapped_codes) == ["881155", "881157"]

    def test_empty_input(self):
        res = rekey_sector_fund_flow([])
        assert res.fund_flow == {}
        assert isinstance(res, RekeyResult)

    def test_output_keys_values_contract(self):
        res = rekey_sector_fund_flow([_entry(n, 1.0) for _, n in sorted(THS_INDUSTRY_90)][:20])
        assert all(_CODE_880_RE.match(k) for k in res.fund_flow)
        assert all(isinstance(v, float) for v in res.fund_flow.values())
        json.dumps(res.fund_flow, ensure_ascii=False)

    def test_bridge_class_and_facade_equivalence(self):
        entries = [_entry("银行", 1.0), _entry("白酒", 2.0)]
        bridge = SectorCodeBridge()
        assert bridge.fund_flow(entries) == fund_flow_for_card(entries)
        assert bridge.fund_flow(entries) == rekey_sector_fund_flow(entries).fund_flow


# ---------- 消费方形态契约（counter_trend_board fund_flow 注入位） ----------


def _synthetic_board_inputs():
    """合成指数主下跌段 + 板块分钟（纯函数核输入）。"""
    index_series = [
        ("2026-08-24 09:31", 100.0),
        ("2026-08-24 09:32", 101.0),  # 峰
        ("2026-08-24 09:33", 99.0),
        ("2026-08-24 09:34", 98.0),
        ("2026-08-24 09:35", 97.0),  # 谷
        ("2026-08-24 09:36", 98.5),
    ]
    sector_series = {
        "880328": [(ts, 50.0) for ts, _ in index_series],
        "880471": [(ts, 80.0) for ts, _ in index_series],
    }
    return index_series, sector_series


class TestConsumerContract:
    def test_fund_flow_plugs_into_counter_trend_card2(self):
        index_series, sector_series = _synthetic_board_inputs()
        entries = [_entry("贵金属", 2.73), _entry("银行", 10.0), _entry("白酒", -1.0)]
        fund_flow = fund_flow_for_card(entries)
        cfg = CounterTrendConfig(sector_names=sector_names_880())
        board = build_counter_trend_board(index_series, sector_series, fund_flow, cfg)
        card2 = next(c for c in board.cards if c.card == "fund_inflow")
        assert not board.degraded
        assert not card2.degraded
        got = {i.sector_code: i.metric_value for i in card2.items}
        assert got["880471"] == pytest.approx(10.0)
        assert got["880328"] == pytest.approx(2.73)
        assert "880381" not in got  # 负净流入不入卡2（消费方口径）
        names = {i.sector_code: i.sector_name for i in card2.items}
        assert names["880471"] == "银行"
        assert names["880328"] == "黄金"

    def test_all_nonpositive_flow_card2_degraded_clean(self):
        """全部净流出 → 卡2 按消费方自身口径降级（适配器不伪造假流入）。"""
        index_series, sector_series = _synthetic_board_inputs()
        fund_flow = fund_flow_for_card([_entry("银行", -1.0)])
        board = build_counter_trend_board(index_series, sector_series, fund_flow, CounterTrendConfig())
        card2 = next(c for c in board.cards if c.card == "fund_inflow")
        assert card2.degraded
        assert "无正净流入" in card2.note

    def test_none_flow_still_degrades_card2(self):
        """适配器未接线时消费方原降级路径不受影响（回归守卫）。"""
        index_series, sector_series = _synthetic_board_inputs()
        board = build_counter_trend_board(index_series, sector_series, None, CounterTrendConfig())
        card2 = next(c for c in board.cards if c.card == "fund_inflow")
        assert card2.degraded

    def test_sector_names_cover_all_mapping_targets(self):
        names = sector_names_880()
        for r in SECTOR_881_TO_880:
            assert names[r.code_880], r


# ---------- CSV 中间层 ----------


class TestCsvIntermediateLayer:
    def test_dump_and_load_roundtrip(self, tmp_path):
        out = dump_mapping_csv(tmp_path / "bridge.csv")
        assert out.endswith("bridge.csv")
        loaded = load_mapping(tmp_path / "bridge.csv")
        assert loaded == default_mapping()

    def test_csv_header_columns(self, tmp_path):
        dump_mapping_csv(tmp_path / "bridge.csv")
        header = (tmp_path / "bridge.csv").read_text(encoding="utf-8").splitlines()[0]
        assert header.split(",") == list(MAPPING_CSV_COLUMNS)

    def test_loaded_mapping_rekey_identical(self, tmp_path):
        dump_mapping_csv(tmp_path / "bridge.csv")
        bridge = SectorCodeBridge.from_csv(tmp_path / "bridge.csv")
        entries = [_entry("电网设备", 1.0), _entry("电池", 2.0)]
        assert bridge.fund_flow(entries) == {"880446": pytest.approx(3.0)}

    def test_dump_creates_parent_dirs(self, tmp_path):
        out = dump_mapping_csv(tmp_path / "nested" / "dir" / "bridge.csv")
        assert out.endswith("bridge.csv")
