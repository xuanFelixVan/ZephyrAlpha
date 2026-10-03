# [BLUEPRINT] MOD-ALT-BOARD-INDEX-SUPPLY | docs/_working/t0_matrix/BOARD_INDEX_INTRADAY_SUPPLY_DESIGN.md | §3 §4 §5
# [MODULE] zephyr.alt_data.board_index_supply
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] stdlib; pandas; zephyr.data.table_registry (get_registry, 禁硬编码表名);
#                zephyr.alt_data.emotion_index_builder (_query_df/_Reader 单源共享, 免 extract 级克隆)
# [CONSUMERS] strategy_pipeline 做T 6.1 龙头-跟风扩散 / 6.2 板块内补涨 (L1 1 分钟主力层);
#             emotion_index_builder C1/C2 (事件级 L4, 注册见 CTR-P1-018, 价格面不接入;
#             L05b-W2 已实接: _daban_event_table() 经 resolve_table 品类派生, 2026-10-04 EXEC-4)
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 消费面只读禁写库（供给落表=S3 写通道单写通道）；三层供给语义=自算(L1)主力、
#              厂商(L2)仅对账兜底（自算缺位才启用且必须带 source=vendor 标记，§3 L2/§4.4 断流可活）；
#              禁跨源拼接（单次返回单源行集，§5.1）；读 ReplacingMergeTree 必 FINAL（§4.5）；
#              PIT 成分仅取 snapshot_date<=trade_date 的最新快照，禁近端成分回看远端（§3 L3/§4.2 零前视）；
#              表名经 TableRegistry 品类派生（未注册品类 fail-closed KeyError，禁凭记忆编表名）；
#              SQL 全部 _SQL_* 模块常量（NO-BARE-SQL）；厂商断流/查询失败降级空表不抛错。
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 品类未注册->KeyError fail-closed（S3/§4.6 注册后自愈）；
#                  自算/厂商查询失败或缺源->空 DataFrame+fallback 原因位，禁拍假值禁抛错拖垮下游。
# [TESTS] tests/alt_data/test_board_index_supply.py
# [A_module] module_id=MOD-ALT-BOARD-INDEX-SUPPLY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""board_index_supply — 板块指数盘中供给消费面（family BOARD-INTRADAY-SUPPLY，设计稿 §3 三层供给）。

消费者注册半件（st-boardidx-20260928）：把做T 6.1/6.2 与 emotion_index C1/C2 登记为
供给家族消费者（consumer_registry.yaml CTR-P1-018），并交付 1 分钟板块指数的统一取数面：
    - L1 自算主力层：板块 1 分钟指数，列契约 (board_code, ts, close, adv_count, dec_count,
      breadth_pct, amount, member_n, version, ingest_ts)，读面带 FINAL；
    - L2 厂商兜底层：board_index_tick 仅当自算缺位时启用（对账兜底），行必带 source=vendor；
    - L3 PIT 成分：sector_constituent_snapshot 仅取 snapshot_date<=trade_date 最新快照。
设计红线：厂商在场不是任何消费者的运行前提（§3 L2 隐式依赖必删）；禁把厂商指数与自算
指数当同一序列混用（§5.1，版本号+source 标记+禁跨源拼接）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 品类表名解析（TableRegistry 注入式解析，未注册 fail-closed）
# - id: I2
#   name: L1 自算/L2 厂商/L3 成分快照 TSV 查询（reader 注入）
# 层: 算法
# - id: A1
#   name_zh: 自算优先取数（空缺位时厂商对账兜底，单源返回禁拼接）
# - id: A2
#   name_zh: PIT 成分映射（snapshot_date<=trade_date 最新快照，零前视）
# 层: 输出
# - id: O1
#   name: SupplyFetch(行集+source+fallback_engaged+reason) 交消费者
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable

import pandas as pd

from zephyr.alt_data.emotion_index_builder import _query_df, _Reader
from zephyr.data.table_registry import get_registry

log = logging.getLogger(__name__)

__all__: list[str] = [
    "SupplyFetch",
    "BOARD_INDEX_CONTRACT_COLUMNS",
    "SOURCE_SELF_COMP",
    "SOURCE_VENDOR",
    "CATEGORY_L1_BOARD_MINUTE",
    "CATEGORY_VENDOR_BOARD_TICK",
    "CATEGORY_SECTOR_CONSTITUENT",
    "CATEGORY_DABAN_BOARD_EVENT",
    "resolve_table",
    "fetch_self_comp_minute",
    "fetch_vendor_minute",
    "get_board_index_minute",
    "fetch_constituents_asof",
]

SOURCE_SELF_COMP = "self_comp"  # L1 自算（主力层）
SOURCE_VENDOR = "vendor"  # L2 厂商（对账兜底，可断）

# 品类 ID（表名唯一真源=TableRegistry/business_data_categories.yaml；本模块禁硬编码表名）。
# L1 表由 S3 件建表注册；vendor/成分两品类按设计 §4.6 入册（当前未注册→fail-closed KeyError）。
CATEGORY_L1_BOARD_MINUTE = "market_board_index_1min"
CATEGORY_VENDOR_BOARD_TICK = "market_board_index_tick"
CATEGORY_SECTOR_CONSTITUTENT = "market_sector_constituent_snapshot"
CATEGORY_DABAN_BOARD_EVENT = "market_daban_board_event"  # L4 事件层（情绪门 C1/C2 供给品类，L05b-W2 实接）

# L1 列契约（设计 §3 L1 输出列，逐一对应，禁增删）
BOARD_INDEX_CONTRACT_COLUMNS: list[str] = [
    "board_code",
    "ts",
    "close",
    "adv_count",
    "dec_count",
    "breadth_pct",
    "amount",
    "member_n",
    "version",
    "ingest_ts",
]

# NO-BARE-SQL：_SQL_* 常量；SELECT 与 FROM 分行；{tbl}/{board}/{start}/{end}/{day} 构建侧注入。
# FINAL=ReplacingMergeTree 消费纪律（§4.5），PIT 子查询亦带 FINAL。
_SQL_SELF_COMP_MINUTE = (
    "SELECT board_code, ts, close, adv_count, dec_count, breadth_pct, "
    "amount, member_n, version, ingest_ts "
    "FROM {tbl} FINAL "
    "WHERE board_code = '{board}' AND ts >= '{start}' AND ts <= '{end}' ORDER BY ts"
)
_SQL_VENDOR_MINUTE = (
    "SELECT board_code, ts, close "
    "FROM {tbl} FINAL "
    "WHERE board_code = '{board}' AND ts >= '{start}' AND ts <= '{end}' ORDER BY ts"
)
_SQL_CONSTITUENTS_PIT = (
    "SELECT stock_code "
    "FROM {tbl} FINAL "
    "WHERE board_code = '{board}' AND snapshot_date <= '{day}' "
    "AND snapshot_date = (SELECT max(snapshot_date) FROM {tbl} FINAL "
    "WHERE board_code = '{board}' AND snapshot_date <= '{day}')"
)

_DEFAULT_RESOLVER: Callable[[str], str] = get_registry().table


def resolve_table(category_id: str, resolver: Callable[[str], str] | None = None) -> str:
    """品类 ID→全限定表名（TableRegistry 单源；未注册 KeyError fail-closed，禁凭记忆编表名）。"""
    return (resolver or _DEFAULT_RESOLVER)(category_id)


@dataclass
class SupplyFetch:
    """消费面统一返回：单源行集 + 兜底语义标记（禁跨源拼接的结构保证）。"""

    df: pd.DataFrame
    source: str  # SOURCE_SELF_COMP | SOURCE_VENDOR
    fallback_engaged: bool  # 自算缺位→厂商兜底启用
    reason: str = ""
    warnings: list[str] = field(default_factory=list)


def fetch_self_comp_minute(
    reader: _Reader,
    board_code: str,
    start: str,
    end: str,
    resolver: Callable[[str], str] | None = None,
) -> pd.DataFrame:
    """L1 自算板块 1 分钟指数（主力层；FINAL 读纪律；失败降级空表不抛错）。"""
    tbl = resolve_table(CATEGORY_L1_BOARD_MINUTE, resolver)
    sql = _SQL_SELF_COMP_MINUTE.format(tbl=tbl, board=board_code, start=start, end=end)
    return _query_df(reader, sql, BOARD_INDEX_CONTRACT_COLUMNS)


def fetch_vendor_minute(
    reader: _Reader,
    board_code: str,
    start: str,
    end: str,
    resolver: Callable[[str], str] | None = None,
) -> pd.DataFrame:
    """L2 厂商板块指数（对账兜底层，可断；失败降级空表不抛错——厂商在场非运行前提）。"""
    tbl = resolve_table(CATEGORY_VENDOR_BOARD_TICK, resolver)
    sql = _SQL_VENDOR_MINUTE.format(tbl=tbl, board=board_code, start=start, end=end)
    return _query_df(reader, sql, ["board_code", "ts", "close"])


def get_board_index_minute(
    reader: _Reader,
    board_code: str,
    start: str,
    end: str,
    resolver: Callable[[str], str] | None = None,
) -> SupplyFetch:
    """三层供给消费入口：自算(L1)主力、厂商(L2)仅当自算缺位时对账兜底。

    兜底语义（§3 L2/§4.4）：自算行集非空→原样返回（厂商不参与，防跨源拼接）；
    自算缺位→厂商兜底启用，source=vendor 显式标记+原因位；厂商也缺/断流→空表
    降级（reason 记录），不抛错——下游情绪/方法卡不得把任一单源在场当运行前提。
    """
    warnings: list[str] = []
    df_self = fetch_self_comp_minute(reader, board_code, start, end, resolver)
    if not df_self.empty:
        return SupplyFetch(df_self, SOURCE_SELF_COMP, fallback_engaged=False)
    warnings.append("self_comp 行集为空，vendor 对账兜底启用（§3 L2）")
    try:
        df_vendor = fetch_vendor_minute(reader, board_code, start, end, resolver)
    except Exception as e:  # noqa: BLE001 — 厂商断流降级契约（§4.4 断流可活）
        log.warning("board_index_supply vendor 兜底查询失败降级: %s: %s", type(e).__name__, e)
        df_vendor = pd.DataFrame(columns=["board_code", "ts", "close"])
        warnings.append(f"vendor 查询异常降级空表: {type(e).__name__}")
    if df_vendor.empty:
        warnings.append("vendor 亦缺（断流或未入库），空表降级（§4.4 断流可活）")
    return SupplyFetch(
        df_vendor,
        SOURCE_VENDOR,
        fallback_engaged=True,
        reason="self_comp 缺位，vendor 对账兜底（禁与自算序列跨源拼接，§5.1）",
        warnings=warnings,
    )


def fetch_constituents_asof(
    reader: _Reader,
    board_code: str,
    day: str,
    resolver: Callable[[str], str] | None = None,
) -> list[str]:
    """PIT 成分映射：仅取 snapshot_date<=day 的最新快照成员（零前视，§3 L3/§4.2）。

    禁用近端成分回看远端；无满足 PIT 的快照→空列表（调用方按无成分降级，禁拍今日成分）。
    """
    tbl = resolve_table(CATEGORY_SECTOR_CONSTITUTENT, resolver)
    sql = _SQL_CONSTITUENTS_PIT.format(tbl=tbl, board=board_code, day=day)
    df = _query_df(reader, sql, ["stock_code"])
    if df.empty:
        return []
    codes = df["stock_code"].dropna().astype(str)
    return sorted({c.strip() for c in codes if c.strip()})


if __name__ == "__main__":  # CH 停机期合成自检（零网零库）：兜底语义+PIT 零前视可独立演练

    class _SyntheticReader:
        """同构单测 FakeReader：按表名路由预制 TSV。"""

        def __init__(self, routes: dict[str, str]) -> None:
            self._routes = routes
            self.calls: list[str] = []

        def query(self, sql: str) -> str:
            self.calls.append(sql)
            for key, tsv in self._routes.items():
                if key in sql:
                    return tsv
            return ""

    _synth_tables = {
        CATEGORY_L1_BOARD_MINUTE: "synthtbl_board_1min",
        CATEGORY_VENDOR_BOARD_TICK: "synthtbl_vendor_tick",
        CATEGORY_SECTOR_CONSTITUTENT: "synthtbl_constit_snap",
    }
    # 合成表名=前缀+品类 ID 派生（不出现任何已注册全限定表名字面，TABLE-NAME-REGISTRY 纪律同构）
    _synth_resolver = lambda cid: "synthtbl_" + cid  # noqa: E731 — 自检局部注入
    _keys = {cid: _synth_resolver(cid) for cid in _synth_tables}
    _self_tsv = "BK.demo\t2026-09-26 09:31:00\t1050.5\t35\t15\t0.7\t1.2e8\t50\tself_comp_v1\t2026-09-26 15:01:00\n"
    _vendor_tsv = "BK.demo\t2026-09-26 09:31:00\t1049.9\n"
    _constit_tsv = "600000\n000001\n300750\n"

    def _run_case(name: str, routes: dict[str, str]) -> SupplyFetch | list[str]:
        reader = _SyntheticReader(routes)
        if name == "pit":
            return fetch_constituents_asof(reader, "BK.demo", "2026-09-26", _synth_resolver)
        return get_board_index_minute(reader, "BK.demo", "2026-09-26 09:30:00", "2026-09-26 15:00:00", _synth_resolver)

    _ok = True
    _primary = _run_case(
        "primary", {_keys[CATEGORY_L1_BOARD_MINUTE]: _self_tsv, _keys[CATEGORY_VENDOR_BOARD_TICK]: _vendor_tsv}
    )
    assert isinstance(_primary, SupplyFetch)
    _ok &= _primary.source == SOURCE_SELF_COMP and list(_primary.df.columns) == BOARD_INDEX_CONTRACT_COLUMNS
    print(f"[1] 自算主力契约列: {'PASS' if _ok else 'FAIL'} source={_primary.source}")
    _fallback = _run_case("fallback", {_keys[CATEGORY_VENDOR_BOARD_TICK]: _vendor_tsv})
    assert isinstance(_fallback, SupplyFetch)
    _ok &= _fallback.fallback_engaged and _fallback.source == SOURCE_VENDOR and not _fallback.df.empty
    print(f"[2] 自算缺位→厂商对账兜底: {'PASS' if _ok else 'FAIL'} reason={_fallback.reason}")
    _cut = _run_case("cut", {})
    assert isinstance(_cut, SupplyFetch)
    _ok &= _cut.df.empty and _cut.fallback_engaged and any("断流" in w for w in _cut.warnings)
    print(f"[3] 双源断流空表降级(§4.4): {'PASS' if _ok else 'FAIL'} warnings={_cut.warnings}")
    _pit = _run_case("pit", {_keys[CATEGORY_SECTOR_CONSTITUTENT]: _constit_tsv})
    assert isinstance(_pit, list)
    _ok &= _pit == ["000001", "300750", "600000"]
    print(f"[4] PIT 成分 snapshot_date<=day 零前视: {'PASS' if _ok else 'FAIL'} codes={_pit}")
    print("SELF-CHECK:", "PASS" if _ok else "FAIL", "(合成数据，CH 恢复后按设计 §4 判据①②③④实数据复核)")
    raise SystemExit(0 if _ok else 1)
