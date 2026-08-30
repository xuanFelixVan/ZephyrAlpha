# [BLUEPRINT] MOD-SIG-130 | docs/03_modules/_domain_signal/strategy_matrix_3d/blueprint.md
# [MODULE] zephyr.signal_ashare.strategy_matrix_3d
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.volume_regime_adaptive（量能/体制轴枚举）; zephyr.regime.style_regime_model（风格2轴枚举）; backtest_runner/clock 全注入
# [CONSUMERS] 运行时装配批（量能×体制×风格三轴策略参数查询 / 参数版本审计）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 三维轴词表闭合(量能3×体制3×风格2=18格); 格值四要素(仓位∈[0,1]/方向long|flat|short/持仓周期≥1/止损k>0有限); commit必填全18格无多无缺; 版本自1递增不可变快照; 查询默认最新版可按版本回溯; 无任何版本查询Fail-Closed; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal/strategy_matrix_3d/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] StrategyMatrixError(占位 ZA-SIG-UNREGISTERED-STRATEGY-MATRIX)——格值非法/格子缺多/轴类型非法/backtest_runner缺失或异常或产出非法/未知版本/未commit查询时抛
# [TESTS] tests/signal_ashare/test_strategy_matrix_3d.py
# [A_module] module_id=MOD-SIG-130 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
StrategyMatrix3D — 量能×体制×风格三维策略矩阵（MOD-SIG-130）。

B10-01467（AUD-DRAFT-001-DIGEST P2 波 P2-W06，CAND-TESTB-048，A1 模块56）：
**3×3×2=18 格策略查找表**（量能 3 × 体制 3 × 风格 2，格值=仓位/选股方向/
持仓周期/止损 k×ATR 四要素 dataclass）+ **逐格回测填参**（注入
backtest_runner，逐格调用产出格值）+ **格子查询接口**（三轴输入→格值）
+ **参数版本管理**（版本自 1 递增、不可变快照、按版本回溯查询）。

查重分工（蓝图 §0）：volume_regime_adaptive（MOD-SIG-129）=量能×体制
二维查找（本件=扩展第三维风格轴并引入版本管理，轴枚举复用不重建）；
style_regime_model（MOD-REGIME-014）=风格态识别（本件仅复用其 SizeAxis
2 轴枚举）；signal_weight_adjuster=信号权重滚动调节（零交集）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: backtest_runner 参数
#   fields: 参数 backtest_runner（无注解）
#   code: strategy_matrix_3d.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: strategy_matrix_3d.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① StrategyMatrix3D
#   name_en: StrategyMatrix3D
#   intro: 量能×体制×风格 18 格策略查找表（版本化，纯内存确定性）。
#   desc: 量能×体制×风格 18 格策略查找表（版本化，纯内存确定性）。；公共方法（定义序）: all_keys, commit, fill_from_backtest, query, version_snapshot, lat…
#   inputs: backtest_runner clock
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: StrategyMatrix3D
#   downstream: 运行时装配批（量能×体制×风格三轴策略参数查询 / 参数版本审计）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass
from typing import Callable, Final, Mapping

from zephyr.regime.style_regime_model import SizeAxis
from zephyr.signal_ashare.volume_regime_adaptive import MarketRegime, VolumeState

_log = logging.getLogger(__name__)

__all__: Final = [
    "DIRECTIONS",
    "GridKey",
    "MatrixCell",
    "MatrixVersion",
    "StrategyMatrix3D",
    "StrategyMatrixError",
]

#: 选股方向词表（闭合）
DIRECTIONS: Final[frozenset[str]] = frozenset({"long", "flat", "short"})

#: 格子键 = (量能态, 市场体制, 风格2轴)
GridKey = tuple[VolumeState, MarketRegime, SizeAxis]


class StrategyMatrixError(Exception):
    """三维策略矩阵输入/配置非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-STRATEGY-MATRIX。
    """


@dataclass(frozen=True)
class MatrixCell:
    """格值四要素：仓位/选股方向/持仓周期/止损 k×ATR（frozen）。"""

    position_pct: float
    direction: str
    hold_days: int
    stop_k: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.position_pct) or not 0.0 <= self.position_pct <= 1.0:
            raise StrategyMatrixError(f"格值仓位越界: {self.position_pct!r}（须 ∈[0,1]）")
        if self.direction not in DIRECTIONS:
            raise StrategyMatrixError(f"格值方向非法: {self.direction!r}（词表闭合 long|flat|short）")
        if not isinstance(self.hold_days, int) or isinstance(self.hold_days, bool) or self.hold_days < 1:
            raise StrategyMatrixError(f"格值持仓周期非法: {self.hold_days!r}（须 ≥1 整数）")
        if not math.isfinite(self.stop_k) or self.stop_k <= 0.0:
            raise StrategyMatrixError(f"格值止损k非法: {self.stop_k!r}（须 >0 有限）")


@dataclass(frozen=True)
class MatrixVersion:
    """参数版本快照（frozen；cells 为 18 格全量映射）。"""

    version: int
    created_at: datetime.datetime
    cells: Mapping[GridKey, MatrixCell]


class StrategyMatrix3D:
    """量能×体制×风格 18 格策略查找表（版本化，纯内存确定性）。"""

    def __init__(
        self,
        *,
        backtest_runner: Callable[[VolumeState, MarketRegime, SizeAxis], MatrixCell | Mapping] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        self._backtest_runner = backtest_runner
        self._clock = clock or datetime.datetime.now
        self._versions: dict[int, MatrixVersion] = {}

    # ── 格子键 ───────────────────────────────────────────────────────────

    @staticmethod
    def all_keys() -> tuple[GridKey, ...]:
        """全 18 格键（枚举定义序，确定性）。"""
        return tuple((v, r, s) for v in VolumeState for r in MarketRegime for s in SizeAxis)

    @staticmethod
    def _check_key(key: object) -> GridKey:
        if (
            not isinstance(key, tuple)
            or len(key) != 3
            or not isinstance(key[0], VolumeState)
            or not isinstance(key[1], MarketRegime)
            or not isinstance(key[2], SizeAxis)
        ):
            raise StrategyMatrixError(f"格子键非法: {key!r}（须 (VolumeState, MarketRegime, SizeAxis)）")
        return key

    # ── 版本管理 ──────────────────────────────────────────────────────────

    def commit(self, cells: Mapping[GridKey, MatrixCell]) -> int:
        """全量 18 格提交新版本：缺格/多格/格值非法 Fail-Closed，不残留半版。"""
        expected = set(self.all_keys())
        for key in cells.keys():
            self._check_key(key)
        given = set(cells.keys())
        missing = expected - given
        extra = given - expected
        if missing:
            raise StrategyMatrixError(f"格子缺失: {sorted(str(k) for k in missing)}")
        if extra:
            raise StrategyMatrixError(f"格子多出（键非法）: {sorted(str(k) for k in extra)}")
        snapshot: dict[GridKey, MatrixCell] = {}
        for key in self.all_keys():
            cell = cells[key]
            if not isinstance(cell, MatrixCell):
                raise StrategyMatrixError(f"格值类型非法: {key!r} -> {type(cell).__name__}")
            snapshot[key] = cell
        version = len(self._versions) + 1
        self._versions[version] = MatrixVersion(version=version, created_at=self._clock(), cells=snapshot)
        _log.info("三维策略矩阵版本提交: v%d（18 格）", version)
        return version

    def fill_from_backtest(self) -> int:
        """逐格回测填参：对 18 格逐格调用注入 backtest_runner → 提交新版本。

        backtest_runner 未注入 / 抛异常 / 产出非法格值 → Fail-Closed 不提交。
        返回值为 Mapping 时按四要素字段名强制转换（多字段忽略，缺字段抛）。
        """
        if self._backtest_runner is None:
            raise StrategyMatrixError("backtest_runner 未注入（逐格回测填参强制注入，禁止旁路）")
        cells: dict[GridKey, MatrixCell] = {}
        for volume_state, regime, style in self.all_keys():
            try:
                raw = self._backtest_runner(volume_state, regime, style)
            except StrategyMatrixError:
                raise
            except Exception as exc:  # noqa: BLE001 — 回测异常 Fail-Closed 包装
                raise StrategyMatrixError(f"backtest_runner 异常: {(volume_state, regime, style)!r}: {exc}") from exc
            cells[(volume_state, regime, style)] = self._coerce_cell(raw, (volume_state, regime, style))
        return self.commit(cells)

    @staticmethod
    def _coerce_cell(raw: MatrixCell | Mapping, key: GridKey) -> MatrixCell:
        if isinstance(raw, MatrixCell):
            return raw
        if isinstance(raw, Mapping):
            try:
                return MatrixCell(
                    position_pct=raw["position_pct"],
                    direction=raw["direction"],
                    hold_days=raw["hold_days"],
                    stop_k=raw["stop_k"],
                )
            except KeyError as exc:
                raise StrategyMatrixError(f"回测格值缺字段: {key!r}: {exc}") from exc
        raise StrategyMatrixError(f"回测格值类型非法: {key!r} -> {type(raw).__name__}")

    # ── 查询 ─────────────────────────────────────────────────────────────

    def query(
        self,
        volume_state: VolumeState,
        regime: MarketRegime,
        style: SizeAxis,
        *,
        version: int | None = None,
    ) -> MatrixCell:
        """三轴 → 格值；version=None 取最新版，指定版本回溯查询。"""
        key = self._check_key((volume_state, regime, style))
        snap = self._resolve_version(version)
        return snap.cells[key]

    def version_snapshot(self, version: int) -> MatrixVersion:
        """指定版本快照（未知版本 Fail-Closed）。"""
        return self._resolve_version(version)

    def latest_version(self) -> int:
        """最新版本号（无版本 Fail-Closed）。"""
        if not self._versions:
            raise StrategyMatrixError("尚无参数版本（须先 commit 或 fill_from_backtest）")
        return max(self._versions)

    def list_versions(self) -> tuple[int, ...]:
        """全版本号升序（确定性）。"""
        return tuple(sorted(self._versions))

    def _resolve_version(self, version: int | None) -> MatrixVersion:
        if not self._versions:
            raise StrategyMatrixError("尚无参数版本（须先 commit 或 fill_from_backtest）")
        v = self.latest_version() if version is None else version
        snap = self._versions.get(v)
        if snap is None:
            raise StrategyMatrixError(f"未知参数版本: {v!r}（现有 {self.list_versions()!r}）")
        return snap
