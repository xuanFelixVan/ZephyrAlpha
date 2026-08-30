# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.northbound_hold_fetcher
# [DOMAIN] D_DATA
# [DEPENDENCIES] tushare SDK (pro.hk_hold); zephyr.data.provider_base; zephyr.data.table_registry
# [CONSUMERS] zephyr.data.implementations.tushare_provider（capability=northbound_hold_snapshot 路由委托）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 仅北向（exchange in SH/SZ，剔除 HK 南向）; PIT 守卫=季度末+20 自然日才采集（官方季度后第 5 个沪深股通交易日发布，留足缓冲）; 全量覆盖写入（ReplacingMergeTree ORDER BY (ts_code, trade_date) 幂等去重）; 单季度按 SH/SZ 拆 2 次调用（规避 hk_hold 单次 4200 行上限，memo §9 分页风险构造性消除）; 上游撞码组 code 自洽判别救回真主行、判别失效整组剔除（宁缺毋错兜底，2026-08-15 实证 243 组恰好 1 行自洽率 100% 全救回）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单季度拉取异常->yield FetchResult(error=str) 并继续下一季度（季度级任务下季度重跑即可）; 已发布季度双侧 0 行->yield FetchResult(error=...) 触发任务失败告警（上游异常 fail-closed）
# [TESTS] tests/zephyr/data/test_northbound_hold_fetcher.py
# [A_module] module_id=MOD-DAT-northbound_hold_ingest | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
北向资金季度持仓快照 fetcher（设计备忘 19 号，task-19-northbound-snapshot）。

背景：港交所 2024-08-19 停止公布北向资金日频数据（known_data_gaps.yaml
hk_connect_flow_source_discontinued），季度持仓快照成为断档后的替代数据源。
tushare pro.hk_hold(trade_date=季度末) 实测可返回完整北向持股快照（memo §3.2）。

设计刻意保持最小（memo §5.1）：单接口、单表、全量覆盖写入——每次运行重新拉取
GENESIS_QUARTER_END 起全部已发布季度（截至 2026Q2 共 8 个季度，~16 次 API 调用、
约 3 万行），无增量/无分页状态机/无重试编排；季度级任务失败下季度重跑即可。

PIT 语义：官方在每季度后第 5 个沪深股通交易日公布上季度末持仓，本模块以
"季度末 + PIT_PUBLISH_LAG_DAYS 自然日 <= 今日"判定季度已发布，未发布季度不采集
（hk_hold 对未发布季度北向返回 0 行， buffer 双保险）。

分页风险（memo §9）：hk_hold 单次返回上限 4200 行，2026Q2 官方公布北向持股 3958 只
逼近上限。本模块按 exchange 分 SH/SZ 两次调用（单侧当前 <2100 行），上限余量翻倍，
构造性消除分页需求。

上游数据质量（2026-08-15 联调实证）：tushare hk_hold 20260630 响应存在 243 组
ts_code 撞码（多只证券被赋予雷同假 code 并映射到合法 ts_code，如 50ETF 撞
603000.SH=人民网；中航成飛 302132 撞 300132.SZ=青松股份），单证券查询同样撞码，
无 API 修复路径。处理：_resolve_code_collisions 按 code 自洽规则判别——组内恰好
1 行自洽（int(code)+offset==ts_code 数字部，SH+510000/SZ+223000）则保留真主行
剔除入侵行（243 组实证全救回）；判别失效（0/>1 行自洽）则整组剔除（宁缺毋错
兜底）+ warn 日志；上游修复后每日全量重拉自愈。已登记 known_data_gaps.yaml
（tushare_hk_hold_2026q2_code_collision）。

落表：c1_market.northbound_hold_snapshot（表名真源 business_data_categories.yaml
category_id=market_northbound_hold_snapshot，经 TableRegistry 派生，禁硬编码）。

tushare hk_hold 返回列：code/trade_date/ts_code/name/vol/ratio/exchange。
字段映射（memo §5.1）：ts_code→ts_code, name→name, vol→hold_share,
ratio→hold_ratio, exchange→exchange, trade_date→trade_date；code（6 位原代码）
可从 ts_code 派生，不落列（§5.2 表 schema 无 src_code 列，以表 schema 为准）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: today 参数
#   fields: 参数 today，类型注解 datetime.date
#   code: northbound_hold_fetcher.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: genesis 参数
#   fields: 参数 genesis，类型注解 datetime.date
#   code: northbound_hold_fetcher.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: pit_lag_days 参数
#   fields: 参数 pit_lag_days，类型注解 int
#   code: northbound_hold_fetcher.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: pro 参数
#   fields: 参数 pro（无注解）
#   code: northbound_hold_fetcher.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① published_quarter_ends
#   name_en: published_quarter_ends
#   intro: 枚举 genesis 起全部已发布季度末（PIT 守卫：季度末+lag 自然日 <= today）。
#   desc: 枚举 genesis 起全部已发布季度末（PIT 守卫：季度末+lag 自然日 <= today）。 Args: today: 今日日期（注入便于测试）。 genesis: 回填…；源码 L156-L180
#   inputs: today genesis pit_lag_days
#   outputs: list[datetime.date]
# - id: A2
#   name_zh: ② fetch_northbound_hold_snapshot
#   name_en: fetch_northbound_hold_snapshot
#   intro: 拉取全部已发布季度北向持仓快照（每季度 SH/SZ 两次调用，全量覆盖）。
#   desc: 拉取全部已发布季度北向持仓快照（每季度 SH/SZ 两次调用，全量覆盖）。 Args: pro: tushare pro_api 客户端（由 TushareProvider.co…；源码 L318-L389
#   inputs: pro payload policy call_with_policy logger today
#   outputs: Iterator[FetchResult]
# 层: 输出
# - id: O1
#   name_zh: list[datetime.date]
#   name_en: list[datetime.date]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.data.implementations.tushare_provider（capability=northbound_hold_snapsho…
# - id: O2
#   name_zh: Iterator[FetchResult]
#   name_en: Iterator[FetchResult]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.data.implementations.tushare_provider（capability=northbound_hold_snapsho…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import datetime
import logging
from typing import Callable, Final, Iterator

from ..policy_registry import SourcePolicy
from ..provider_base import FetchPayload, FetchResult
from ..table_registry import get_registry

log = logging.getLogger(__name__)

# 表名从 business_data_categories.yaml 真源派生（裁定 #ARCH-CH-024）
_TBL_NORTHBOUND_HOLD = get_registry().table("market_northbound_hold_snapshot")

# 断档后首个季度快照（memo §5.3 回填起点；2024-08-16 前日频数据在 hk_connect_flow 表，不重复采集）
GENESIS_QUARTER_END = datetime.date(2024, 9, 30)

# PIT 发布滞后缓冲（自然日）：官方季度后第 5 个沪深股通交易日发布，
# 最差情形 Q3 末遇国庆长假第 6 个交易日 ≈ 10-15，20 自然日全覆盖
PIT_PUBLISH_LAG_DAYS = 20

# 北向交易所（HK=南向，本备忘不采集）
_NORTHBOUND_EXCHANGES = ("SH", "SZ")

# 落表列顺序（与 schemas/categories/market_northbound_hold_snapshot.py INSERT_COLUMNS 一致；
# ingested_at 由 CH DEFAULT now() 填充，不在写入列内）
COLUMNS: Final = ["trade_date", "ts_code", "name", "hold_share", "hold_ratio", "exchange", "data_source"]

__all__: Final = [
    "COLUMNS",
    "GENESIS_QUARTER_END",
    "PIT_PUBLISH_LAG_DAYS",
    "published_quarter_ends",
    "fetch_northbound_hold_snapshot",
]


def _quarter_end(year: int, quarter: int) -> datetime.date:
    """季度末日期（Q1=03-31 / Q2=06-30 / Q3=09-30 / Q4=12-31）。"""
    return [
        datetime.date(year, 3, 31),
        datetime.date(year, 6, 30),
        datetime.date(year, 9, 30),
        datetime.date(year, 12, 31),
    ][quarter - 1]


def published_quarter_ends(
    today: datetime.date,
    genesis: datetime.date = GENESIS_QUARTER_END,
    pit_lag_days: int = PIT_PUBLISH_LAG_DAYS,
) -> list[datetime.date]:
    """枚举 genesis 起全部已发布季度末（PIT 守卫：季度末+lag 自然日 <= today）。

    Args:
        today: 今日日期（注入便于测试）。
        genesis: 回填起点季度末。
        pit_lag_days: 发布滞后缓冲（自然日）。

    Returns:
        升序季度末日期列表；无已发布季度时为空列表。
    """
    ends: list[datetime.date] = []
    for year in range(genesis.year, today.year + 1):
        for quarter in (1, 2, 3, 4):
            qe = _quarter_end(year, quarter)
            if qe < genesis:
                continue
            if qe + datetime.timedelta(days=pit_lag_days) > today:
                continue  # 未发布（PIT）
            ends.append(qe)
    return sorted(ends)


# 撞码组真主判别的 code 自洽 offset（2026-08-15 probe 实证）：冲突组内恰好 1 行满足
# int(code)+offset == int(ts_code 数字部)——该行归属该 ts_code（真主，code 与 ts_code
# 自洽）；其余行为入侵行（ETF/他股假码撞入，code+offset 指向他证券）。243 组实证
# 恰好 1 行自洽率 100%（SH 139 + SZ 104）。规则失效（0 或 >1 行自洽）时整组剔除兜底。
_CODE_SELF_CONSISTENCY_OFFSET: Final = {"SH": 510000, "SZ": 223000}


def _is_code_self_consistent(code_val, ts_code: str, exchange: str) -> bool:
    """code 与 ts_code 自洽性判定（撞码组内真主行判别，见 _resolve_code_collisions）。

    解析失败（非数字/未知 exchange）保守返回 False（视为非真主）。
    """
    offset = _CODE_SELF_CONSISTENCY_OFFSET.get(exchange)
    if offset is None:
        return False
    try:
        code_num = int(str(code_val).strip().zfill(6))
        ts_num = int(str(ts_code).split(".")[0])
    except (TypeError, ValueError):
        return False
    return code_num + offset == ts_num


def _resolve_code_collisions(df, quarter_end: datetime.date, exchange: str):
    """判别并剔除上游撞码行（同 ts_code 多行且 name/vol 冲突），宁缺毋错兜底。

    实证（2026-08-15 联调，tmp 探针 6-9）：tushare hk_hold 20260630 响应中 243 组
    ts_code 撞码（多只证券被赋予雷同假 code 并映射到合法 ts_code，如 50ETF 撞
    603000.SH=人民网；中航成飛 302132 撞 300132.SZ=青松股份），按 ts_code 单证券
    查询同样撞码（无 API 修复路径）。组内结构：真主行 code 与 ts_code 自洽
    （_is_code_self_consistent，name 为繁体真名），入侵行 code+offset 指向他证券
    （ETF 或他股假码），243 组恰好 1 行自洽率 100%。

    裁定：组内恰好 1 行自洽 -> 保留真主行剔除入侵行（救回）；0 或 >1 行自洽
    （判别规则失效）-> 整组剔除（宁缺毋错：数据缺失可自愈——下次全量重拉；
    错误归属是静默毒数据）。完全相同的重复行（分页重叠）保留首行。
    已登记 known_data_gaps.yaml（tushare_hk_hold_2026q2_code_collision）。

    Returns:
        (clean_df, salvaged_codes, dropped_codes):
        剔除后的 DataFrame、救回的 ts_code 清单、整组剔除的 ts_code 清单。
    """
    if df is None or df.empty:
        return df, [], []
    dup_mask = df.duplicated("ts_code", keep=False)
    if not dup_mask.any():
        return df, [], []
    dup = df[dup_mask]
    # 冲突组：同 ts_code 下 name 或 vol 不唯一（真正撞码）
    conflict_codes = [code for code, g in dup.groupby("ts_code") if g["name"].nunique() > 1 or g["vol"].nunique() > 1]
    salvaged: list[str] = []
    dropped: list[str] = []
    drop_idx: list = []
    for code in conflict_codes:
        g = dup[dup["ts_code"] == code]
        cons_mask = g.apply(
            lambda r: _is_code_self_consistent(r["code"], r["ts_code"], exchange),
            axis=1,
        )
        if int(cons_mask.sum()) == 1:
            salvaged.append(code)  # 保留真主行，剔除入侵行
            drop_idx.extend(g[~cons_mask].index.tolist())
        else:
            dropped.append(code)  # 判别失效，整组剔除兜底
            drop_idx.extend(g.index.tolist())
    if conflict_codes:
        sample = dup[dup["ts_code"].isin(conflict_codes[:3])][["code", "ts_code", "name", "vol"]].to_dict("records")
        log.warning(
            "北向持仓 %s %s: 上游撞码 %d 组——code 自洽判别救回 %d 组（保留真主行），"
            "判别失效整组剔除 %d 组（宁缺毋错，待上游修复后重拉自愈）: sample=%s",
            quarter_end,
            exchange,
            len(conflict_codes),
            len(salvaged),
            len(dropped),
            sample,
        )
    if drop_idx:
        df = df.drop(index=drop_idx)
    #  benign 完全重复（分页重叠）去重保留首行
    df = df.drop_duplicates(subset=["ts_code"], keep="first")
    return df, salvaged, dropped


def _fetch_one_exchange(
    pro,
    policy: SourcePolicy,
    call_with_policy: Callable,
    quarter_end: datetime.date,
    exchange: str,
) -> list[tuple]:
    """拉取单交易所北向持仓快照并映射为落表行。"""
    df = call_with_policy(
        pro.hk_hold,
        policy,
        trade_date=quarter_end.strftime("%Y%m%d"),
        exchange=exchange,
    )
    rows: list[tuple] = []
    if df is None or df.empty:
        return rows
    df, _salvaged, _dropped = _resolve_code_collisions(df, quarter_end, exchange)
    skipped = 0
    for _, r in df.iterrows():
        try:
            hold_share = int(r["vol"])
            hold_ratio = float(r["ratio"])
        except (TypeError, ValueError, KeyError):
            skipped += 1
            continue
        # memo §7 字段质量：hold_share > 0，hold_ratio ∈ [0, 100]
        if hold_share <= 0 or not (0.0 <= hold_ratio <= 100.0):
            skipped += 1
            continue
        rows.append(
            (
                quarter_end,
                str(r["ts_code"]),
                str(r["name"]),
                hold_share,
                hold_ratio,
                str(r.get("exchange", exchange)),
                "tushare",
            )
        )
    if skipped:
        log.warning(
            "北向持仓 %s %s: %d 行质量校验未过被跳过（hold_share<=0 或 ratio 越界/类型异常）",
            quarter_end,
            exchange,
            skipped,
        )
    return rows


def fetch_northbound_hold_snapshot(
    pro,
    payload: FetchPayload,
    policy: SourcePolicy,
    call_with_policy: Callable,
    logger: logging.Logger | None = None,
    today: datetime.date | None = None,
) -> Iterator[FetchResult]:
    """拉取全部已发布季度北向持仓快照（每季度 SH/SZ 两次调用，全量覆盖）。

    Args:
        pro: tushare pro_api 客户端（由 TushareProvider.connect 建立）。
        payload: 下载请求（start/end 不参与季度枚举，本模块按 PIT 自给自足）。
        policy: 源策略（限流/重试由 call_with_policy 应用）。
        call_with_policy: Provider 基类的策略调用器（通常为 self._call_with_policy）。
        logger: 可选日志器（默认模块级 log）。
        today: 可选今日日期注入（测试用；None=datetime.date.today()）。

    Yields:
        每季度一个 FetchResult；单季度异常 yield error 结果并继续下一季度。
    """
    log_ = logger or log
    table = _TBL_NORTHBOUND_HOLD
    today = today or datetime.date.today()
    quarter_ends = published_quarter_ends(today)
    if not quarter_ends:
        yield FetchResult(
            table=table,
            columns=COLUMNS,
            rows=[],
            last_key="",
            elapsed_sec=0.0,
            error=f"无已发布季度（genesis={GENESIS_QUARTER_END}, today={today}）",
        )
        return
    for qe in quarter_ends:
        t0 = datetime.datetime.now(datetime.timezone.utc)
        try:
            rows: list[tuple] = []
            for exchange in _NORTHBOUND_EXCHANGES:
                rows.extend(_fetch_one_exchange(pro, policy, call_with_policy, qe, exchange))
            elapsed = (datetime.datetime.now(datetime.timezone.utc) - t0).total_seconds()
            if not rows:
                # 已发布季度双侧 0 行 = 上游异常（北向每季度持股数千只，0 行非合法情形）
                yield FetchResult(
                    table=table,
                    columns=COLUMNS,
                    rows=[],
                    last_key=qe.isoformat(),
                    elapsed_sec=elapsed,
                    error=f"已发布季度 {qe} SH/SZ 均返回 0 行（上游异常或接口失效）",
                )
                continue
            log_.info("北向持仓快照 %s: %d 行（SH+SZ）", qe, len(rows))
            yield FetchResult(
                table=table,
                columns=COLUMNS,
                rows=rows,
                last_key=qe.isoformat(),
                elapsed_sec=elapsed,
            )
        except Exception as e:  # noqa: BLE001 — 单季度失败不阻断其余季度，下季度重跑自愈
            elapsed = (datetime.datetime.now(datetime.timezone.utc) - t0).total_seconds()
            log_.warning("北向持仓快照 %s 获取失败: %s", qe, e)
            yield FetchResult(
                table=table,
                columns=COLUMNS,
                rows=[],
                last_key=qe.isoformat(),
                elapsed_sec=elapsed,
                error=str(e),
            )
