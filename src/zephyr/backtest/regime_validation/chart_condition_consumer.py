# [BLUEPRINT] MOD-BT-COND-PACKAGE | docs/03_modules/_domain_backtest/blueprint.md
# create-guard-not-dup: 本件=chart_condition_package（MOD-BT-COND-PACKAGE）唯一 src 下游接线适配层（纯委托零第二实现，判据口径全数委托包内真源）；命中词"图形条件轴消费适配器"系本件 MTR 登记译名与 QMT 桥/决策图适配器/比较器在册描述的词碰撞，非其第二实现。
# [MODULE] zephyr.backtest.regime_validation.chart_condition_consumer
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pandas; zephyr.backtest.regime_validation.chart_condition_package
# [CONSUMERS] tests/backtest/test_chart_condition_consumer.py; scripts/backtest/condition_attribution.py（save_axis_pack 落盘后 load_pack 同构文件契约零改动归因——工件面真消费，本件集成测试红证）; [DEFERRED-1LINE] scripts/backtest/factory_grid_executor.py:559（evaluate_recipe 的 daily_net_returns 产出处——chief 后继单行补丁：run_batch 侧 chart_condition_consumer.stratify_key_join(net_returns, provider, family=...) 挂图形条件轴分层键，本道禁改他会话在册热文件故缓一行）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 纯适配零第二实现：全部判据行为委托 chart_condition_package（轴口径/30日地板/fail-closed 单一真源，禁复制判据禁调参）；图形信号=考试条件轴禁作独立交易信号（波 10 硬约束）；零 CH 连接零下单零生产写（本件禁 import DatabaseService/ch_reader，事件读数由调用方注入 DataFrame）；无统计=None 不是 0（地板不达 cell_id=None 下沉 conditional-free 原样透传禁补 0）；禁跨族混算（一胞一族：stratify_key_join 多族 provider 未指定 family 即抛）；stable axis_id="chart_condition"（考试链注册名冻结）
# [MODIFY-GUARD] tests/backtest/test_chart_condition_consumer.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError/KeyError/RuntimeError 全部由被委托的 chart_condition_package 原样上抛（适配层禁吞禁包装）；join 零重叠日抛 RuntimeError（与判读端 condition_attribution 同口径）；多族未定族抛 ValueError
# [TESTS] tests/backtest/test_chart_condition_consumer.py
# [TTL] permanent
"""图形条件轴消费适配器（st-zcloseout 接线袋：把已在库的 chart_condition_package 接出第一个 src 下游真消费）。

缺口定性（census 2026-09-28）：图形条件包 MOD-BT-COND-PACKAGE 第三轴已建但零下游消费
（git grep 仅 self+test）。本件是唯一缺口"接线"件，不是第二实现件：

1. `ChartConditionAxisProvider` 把 ChartConditionPack 包成**稳定的条件轴供给面**
   （axis_frame/cells/eligible_cells/provenance 四方法，axis_id 冻结 "chart_condition"），
   供给面列契约与判读端消费面逐列对齐（date/cell_id/cell_eligible）；
2. `provider_from_events`：调用方注入事件 DataFrame（读数通道 DI，CH 由上游负责）
   → 委托 build_chart_daily_state + build_chart_condition_pack 出三轴包；
3. `provider_from_pack_dir`：离线回读（load_pack 同构文件契约）——闭卷窗内
   一次性装配、多次消费的判读路径；
4. `save_axis_pack`：委托 save_pack 落盘（同构文件名）⇒ `condition_attribution.py`
   判读端零改动即可归因本轴（真消费红证=tests/backtest/test_chart_condition_consumer.py
   ::TestArtifactConsumerRoundtrip）；
5. `stratify_key_join`：把逐日收益/信号面板按 date join 上 cell_id/cell_eligible
   条件分层键（T1 条件维分层键的供给函数；工厂侧接线点见 [CONSUMERS] DEFERRED-1LINE）。

本件无独立算法图（纯委托适配层零自持判据，算法真源=chart_condition_package，
图随真源件，禁在此复制第二份流程图；GATE-ALGO-FLOW 硬门禁要求 src/zephyr 模块
带标记，故按 P2-1 口径挂 external 锚，机器块待册线 externalize 出仓补齐）。
# [ALGO_FLOW] external: docs/03_modules/_domain_backtest/algo_flow/chart_condition_consumer.yaml
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final, Iterable

import pandas as pd

from zephyr.backtest.regime_validation import chart_condition_package as ccp

#: 考试链条件轴注册名（冻结；改名=破坏消费面契约）
AXIS_ID: Final = "chart_condition"

#: axis_frame 稳定列契约（判读端 join 面逐列对齐；扩列不删列）
_AXIS_COLUMNS: Final = ("date", "family", "chart_state", "grey_band", "state", "cell_id", "cell_eligible")


@dataclass(frozen=True)
class ChartConditionAxisProvider:
    """三轴图形条件轴供给面（稳定接口：四读数方法 + 冻结 axis_id）。

    纯只读视图——持有 ChartConditionPack，禁改写；全部判据语义在包内（本类零判据）。
    """

    pack: ccp.ChartConditionPack

    @property
    def axis_id(self) -> str:
        return AXIS_ID

    def axis_frame(self) -> pd.DataFrame:
        """逐日条件轴长表 [date, family, chart_state, grey_band, state, cell_id, cell_eligible]。

        chart_none 日不入轴（当日该族无事件=无信息，包内口径原样透传）。
        """
        frame = self.pack.frame.copy()
        missing = [c for c in _AXIS_COLUMNS if c not in frame.columns]
        if missing:
            raise KeyError(f"条件包日框缺稳定列 {missing}（期望 {_AXIS_COLUMNS}）")
        return frame[list(_AXIS_COLUMNS)]

    def cells(self) -> pd.DataFrame:
        """胞级台账（cell_id/family/chart_state/grey_band/state/days/eligible）。"""
        return self.pack.cells.copy()

    def eligible_cells(self) -> list[str]:
        """达标胞 id 列表（30 日地板原样透传，禁凑 n）。"""
        return self.pack.eligible_cells()

    def provenance(self) -> dict:
        """产源台账（closed_book_window/轴族/地板口径）。"""
        return dict(self.pack.provenance)


def provider_from_events(
    events: pd.DataFrame,
    base_pack: ccp.ConditionPack,
    *,
    floor_days: int | None = None,
    keep_families: Iterable[str] | None = None,
) -> ChartConditionAxisProvider:
    """事件明细（调用方注入，DI 读通道）+ 两轴基准包 → 图形条件轴供给面。

    floor_days=None=不覆盖，委托包内默认（condition_package._CELL_FLOOR_DAYS 单一真源）。
    """
    chart_daily = ccp.build_chart_daily_state(events)
    kwargs: dict = {"keep_families": keep_families}
    if floor_days is not None:
        kwargs["floor_days"] = floor_days
    pack = ccp.build_chart_condition_pack(chart_daily, base_pack, **kwargs)
    return ChartConditionAxisProvider(pack=pack)


def provider_from_pack_dir(out_dir: str | Path) -> ChartConditionAxisProvider:
    """离线回读（load_pack 同构文件契约）——判读端零 CH 消费路径。"""
    return ChartConditionAxisProvider(pack=ccp.load_pack(out_dir))


def save_axis_pack(provider: ChartConditionAxisProvider, out_dir: str | Path) -> Path:
    """落盘（委托 condition_package.save_pack，同构文件名 ⇒ 判读端零改动归因）。"""
    return ccp.save_pack(provider.pack, out_dir)


def stratify_key_join(
    daily: pd.DataFrame,
    provider: ChartConditionAxisProvider,
    *,
    family: str | None = None,
) -> pd.DataFrame:
    """逐日面板 × 条件轴 → 挂上 cell_id/cell_eligible 分层键（inner join，禁补行）。

    daily：DatetimeIndex 或 date 列的逐日面板（net_returns/信号面板皆可）。
    family：一胞一族论域——provider 含多族时 MUST 显式指定（禁跨族混算，
    包内 [INVARIANTS] 原样执行）；单族 provider 可省。
    零重叠日抛 RuntimeError（与判读端同口径：窗口不一致≠无数据）。
    """
    axis = provider.axis_frame()
    families = set(axis["family"].unique())
    if len(families) > 1 and family is None:
        raise ValueError(f"多族条件轴（{sorted(families)}）禁跨族混算——显式传 family（一胞一族，包内铁规）")
    if family is not None:
        axis = axis[axis["family"] == family]
        if axis.empty:
            raise RuntimeError(f"族 {family!r} 在条件轴内零行——禁跨族拼轴")
    axis_dates = pd.to_datetime(axis["date"])
    if axis_dates.duplicated().any():
        raise RuntimeError("条件轴 date 重复——单族论域下应逐日唯一（数据越界即停）")

    frame = daily.copy()
    if isinstance(frame.index, pd.DatetimeIndex):
        frame = frame.reset_index().rename(columns={"index": "date"})
    if "date" not in frame.columns:
        raise KeyError("daily 面板缺 date 列或 DatetimeIndex（判读端同口径）")
    frame["date"] = pd.to_datetime(frame["date"])
    keys = axis[["date", "cell_id", "cell_eligible"]].copy()
    keys["date"] = axis_dates
    joined = frame.merge(keys, on="date", how="inner")
    if joined.empty:
        raise RuntimeError("逐日面板与条件轴零重叠日——窗口口径不一致，禁组装")
    return joined
