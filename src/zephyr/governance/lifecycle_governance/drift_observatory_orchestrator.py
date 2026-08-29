# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.lifecycle_governance.drift_observatory_orchestrator
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.foundation.errors（仅错误基类；四层检测器与执行端口全部依赖注入，本模块不 import 生产执行体）
# [CONSUMERS] 调用方（盘后批量漂移巡检编排；首批策略上线后由 64 号 §6.4 调度基座装配，执行端口接 order_manager/position_sizer 适配器）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] composite=Σw·s 绝对权重（缺层计 0 不归一）保"多层确认"语义——L1 单层满格仅 ALERT，L4 单层满格至多 STOP_NEW_ENTRIES;coverage_breach 直达 RETRAIN 不被其他层稀释;执行水位只升不降（无自动降级，恢复须人工 reset_strategy，对齐 rollback_state_machine 单向保守纪律）;幂等重入=同水位重复裁决零执行副作用
# [MODIFY-GUARD] 61_lifecycle_multi_ai.md §3.3 纪律 4
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftObservatoryError(ZA-GV-0052);执行端口异常原样上抛（本次水位不推进，重试安全）
# [TESTS] tests/governance/lifecycle/test_drift_observatory_orchestrator.py
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: DriftObservation(strategy_id + features/model_output/realized_pnl 三载荷)
# I2: DriftLayers 四层检测端口（input/prediction/outcome/conformal，皆可缺省降级）+ downstream_impact_gate（仅 L1）
# F1: 四层并行检测（单层异常/越界 → 该层计 0 + degraded 留痕，不扩散）
# F2: L1 下游影响门控（良性漂移清零 severity，防告警疲劳；gate 异常保留告警=保守方向）
# F3: CUSUM→calibration flush 联动（L2 cusum_alarm → L4 flush_calibration_set + BC-ACI bias_corrector）
# F4: composite=Σw·s 加权聚合 → map_response 五级响应（0.20/0.40/0.60/0.80 + coverage_breach 直达）
# F5: 水位棘轮执行（只升不降；升级才触发执行端口；同/低水位幂等零副作用；notify 每次照发）
# O1: DriftVerdict(response/composite/applied_response/actions_fired/failed_layers/degraded/idempotent_replay)
# [/ALGO_FLOW]
"""D_GOVERNANCE — Drift Observatory 四层联动编排器（61 号 §3.3 纪律 4，编排层）。

四层递进（memo 实际分层名）：Layer 1 输入监控（PSI/KS/MMD/Wasserstein 特征漂移，
预警"输入变了"）→ Layer 2 预测监控（prediction drift + CUSUM 残差漂移，确认
"模型行为变了"）→ Layer 3 延迟结果监控（ADWIN 概念漂移 + 标签漂移，验证
"预测质量变了"）→ Layer 4 可证覆盖层（Conformal 实际覆盖 < 名义 1-α，可证
"覆盖保证破了"）。四层检测器全部以端口注入（DriftLayers），本模块只做编排：
探测聚合 → 门控归因 → 响应裁决 → 分级执行/观察，不实现任何检测算法。

memo 施工要点落地映射：
  ① 权重 Layer 4 最高（0.40，可证覆盖非启发式 > 经验阈值）→ DEFAULT_LAYER_WEIGHTS。
  ② 下游影响门控仅作用 Layer 1（特征漂移多为良性），Layer 2-4 已直接关联模型行为不门控。
  ③ CUSUM→calibration flush 复用 L2 残差 CUSUM 告警触发 L4 校准集冲刷 + BC-ACI 纠偏。
  ④ 分级响应阈值 0.20/0.40/0.60/0.80 对应五级响应阶梯（不直接跳重训练）。
  ⑤ Layer 4 coverage_breach 直达 RETRAIN 绕过 composite——数学保证层告警不可被稀释。

memo 留白裁定（编排层补全，不越入检测内核）：
  - 缺层语义：memo 伪代码假设四层全在位。本编排层采用**绝对权重不归一**——缺层/失败层
    计 0 分而非按在位层重归一，保住"单层告警不触发高级响应，须多层确认"的时序纪律
    （归一会让 L4 单层直达 RETRAIN，违背纪律）。缺层降级以 degraded/failed_layers 留痕。
  - 幂等与恢复：memo 伪代码每次全量执行动作。本编排层加执行水位棘轮（只升不降），
    同水位/回落重入零执行副作用（幂等）；降级恢复不自动（对齐同包
    rollback_state_machine 单向保守纪律），人工复核后 reset_strategy 复位。

依据: 61_lifecycle_multi_ai §3.3 纪律 4（四层 Drift Observatory 联动编排伪代码 + 施工要点①-⑤）
Version: 0.1.0
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Final, Protocol

from zephyr.shared.foundation.errors import ZephyrBaseError

logger = logging.getLogger(__name__)

#: 分级响应阈值（61 号施工要点④：0.20/0.40/0.60/0.80 → 五级响应阶梯）
DEFAULT_RESPONSE_THRESHOLDS: Final[tuple[float, float, float, float]] = (0.20, 0.40, 0.60, 0.80)
#: REDUCE_SIZE 减仓比例（61 号 §3.3：减仓至 50%）
REDUCE_SIZE_SCALE: Final[float] = 0.5
#: 权重和容差
_WEIGHT_SUM_TOL: Final[float] = 1e-6


class DriftObservatoryError(ZephyrBaseError):
    """Drift Observatory 编排配置/输入非法（notify 缺失 / 权重畸形 / 阈值乱序 / 空 strategy_id）。"""

    error_code = "ZA-GV-0052"


class DriftLayer(str, Enum):
    """四层 Drift Observatory 分层（61 号 §3.3 三层检测架构 + Layer 4 可证覆盖层）。"""

    INPUT = "input"  # Layer 1 输入监控：特征漂移（PSI/KS/MMD/Wasserstein），最快预警
    PREDICTION = "prediction"  # Layer 2 预测监控：预测漂移 + CUSUM 残差漂移
    OUTCOME = "outcome"  # Layer 3 延迟结果监控：ADWIN 概念漂移 + 标签漂移（需延迟 ground truth）
    CONFORMAL = "conformal"  # Layer 4 可证覆盖层：Conformal 覆盖保证（数学保证非启发式）


#: 四层权重（61 号施工要点①：Layer 4 可证覆盖权重最高 0.40，数学保证 > 经验阈值）
DEFAULT_LAYER_WEIGHTS: Final[dict[DriftLayer, float]] = {
    DriftLayer.INPUT: 0.15,
    DriftLayer.PREDICTION: 0.20,
    DriftLayer.OUTCOME: 0.25,
    DriftLayer.CONFORMAL: 0.40,
}


class DriftResponse(str, Enum):
    """分级响应阶梯（61 号 §3.3：不直接跳重训练，按严重程度分级）。"""

    ALERT = "ALERT"  # ① 仅通知，策略正常运行
    REDUCE_SIZE = "REDUCE_SIZE"  # ② 减仓至 50%
    STOP_NEW_ENTRIES = "STOP_NEW_ENTRIES"  # ③ 停止新建仓，仅平存量
    QUARANTINE = "QUARANTINE"  # ④ 隔离暂停待诊断
    RETRAIN = "RETRAIN"  # ⑤ 触发重训练


#: 响应严重度序（枚举序=严重度序，水位棘轮比较用）
_RESPONSE_RANK: Final[dict[DriftResponse, int]] = {
    DriftResponse.ALERT: 0,
    DriftResponse.REDUCE_SIZE: 1,
    DriftResponse.STOP_NEW_ENTRIES: 2,
    DriftResponse.QUARANTINE: 3,
    DriftResponse.RETRAIN: 4,
}


@dataclass(frozen=True)
class LayerResult:
    """单层检测结果（各层检测器出参契约；severity ∈ [0,1]）。

    Attributes:
        layer: 产出层标识（编排层按端口位置取权重，本字段供归因留痕）。
        severity: 层内告警严重度 0.0-1.0。
        cusum_alarm: Layer 2 残差 CUSUM 告警（触发 L4 calibration flush 联动）。
        residual_bias: Layer 2 残差偏置估计（BC-ACI 纠偏输入；None=无偏置估计）。
        coverage_breach: Layer 4 可证覆盖破（实际覆盖 < 名义 1-α；直达 RETRAIN）。
        detail: 人类可读说明（告警留痕）。
    """

    layer: DriftLayer
    severity: float
    cusum_alarm: bool = False
    residual_bias: float | None = None
    coverage_breach: bool = False
    detail: str = ""


@dataclass(frozen=True)
class DriftObservation:
    """单策略单观测窗口输入（参数对象，NO-LONG-PARAM-LIST 合规）。

    features/model_output/realized_pnl 为不透明载荷（类型由各层检测器契约自定），
    编排层只做路由不解读：L1←features，L2←model_output，L3←realized_pnl，L4←整包。
    """

    strategy_id: str
    features: object = None
    model_output: object = None
    realized_pnl: object = None


class LayerDetector(Protocol):
    """Layer 1-3 检测器端口协议（check 返回 LayerResult；输入载荷按层路由）。"""

    def check(self, payload: object) -> LayerResult:
        """对路由载荷执行漂移检测，返回层结果。"""
        ...


class ConformalLayerDetector(Protocol):
    """Layer 4 可证覆盖层端口协议（check + calibration flush 联动）。"""

    def check(self, observation: DriftObservation) -> LayerResult:
        """覆盖检验：实际覆盖 < 名义 (1-α) → coverage_breach=True。"""
        ...

    def flush_calibration_set(self) -> None:
        """丢弃陈旧校准集，post-drift 重建（calibration flush，minimax 最优）。"""
        ...


@dataclass(frozen=True)
class DriftLayers:
    """四层检测端口（全部可缺省——缺省层按失败降级计 0 分并留痕，空输入=四层全缺）。"""

    input_monitor: LayerDetector | None = None
    prediction_monitor: LayerDetector | None = None
    outcome_monitor: LayerDetector | None = None
    conformal_layer: ConformalLayerDetector | None = None


@dataclass(frozen=True)
class DriftResponsePorts:
    """响应执行端口（依赖注入；notify 必备，执行端口 None=跳过并留痕）。

    必备：
        notify: (strategy_id, DriftVerdict) -> None——每轮照发（含 ALERT），告警通道由调用方装配。
    可选：
        scale_position: (strategy_id, ratio)——REDUCE_SIZE 减仓（61 号：至 50%）。
        disable_new_entries: (strategy_id)——STOP_NEW_ENTRIES 停新建仓。
        disable_strategy: (strategy_id)——QUARANTINE 隔离暂停。
        trigger_retraining: (strategy_id)——RETRAIN 触发重训练（61 号第 8 条三触发之性能触发）。
        bias_corrector: (residual_bias)——BC-ACI 在线纠正残余偏置（CUSUM 联动）。
    """

    notify: Callable[[str, "DriftVerdict"], None]
    scale_position: Callable[[str, float], None] | None = None
    disable_new_entries: Callable[[str], None] | None = None
    disable_strategy: Callable[[str], None] | None = None
    trigger_retraining: Callable[[str], None] | None = None
    bias_corrector: Callable[[float], None] | None = None


@dataclass(frozen=True)
class DriftVerdict:
    """编排裁决产物（每轮 observe 返回一份；告警/审计留痕载体）。

    response: 本轮计算响应（按当前观测）。applied_response: 执行水位（只升不降）。
    二者分离承载"降级不自动"——观测回落时 response 下行但 applied_response 不降。
    idempotent_replay: 本轮未产生新执行副作用（同水位重入/观测回落）。
    """

    strategy_id: str
    response: DriftResponse
    composite: float
    applied_response: DriftResponse
    layer_results: tuple[LayerResult, ...] = ()
    actions_fired: tuple[str, ...] = ()
    skipped_ports: tuple[str, ...] = ()
    failed_layers: tuple[DriftLayer, ...] = ()
    degraded: bool = False
    coverage_breach: bool = False
    idempotent_replay: bool = False


def map_response(
    composite: float,
    coverage_breach: bool,
    thresholds: tuple[float, float, float, float] = DEFAULT_RESPONSE_THRESHOLDS,
) -> DriftResponse:
    """composite → 五级响应映射（61 号施工要点④⑤；纯函数）。

    coverage_breach 直达 RETRAIN 绕过 composite 阈值——数学保证层告警不可被
    其他层"稀释"。阈值含边界（>=）。
    """
    if coverage_breach or composite >= thresholds[3]:
        return DriftResponse.RETRAIN
    if composite >= thresholds[2]:
        return DriftResponse.QUARANTINE
    if composite >= thresholds[1]:
        return DriftResponse.STOP_NEW_ENTRIES
    if composite >= thresholds[0]:
        return DriftResponse.REDUCE_SIZE
    return DriftResponse.ALERT


class DriftObservatoryOrchestrator:
    """四层 Drift Observatory 联动编排器（61 号 §3.3 纪律 4）。

    用法：调用方装配四层检测器（DriftLayers，可为 None 降级）与执行端口
    （DriftResponsePorts），每个观测窗口（盘后批量巡检）对每个上线策略调
    observe(DriftObservation(...))；执行水位按策略独立棘轮，人工复核后
    reset_strategy 复位（重训练完成/诊断闭环）。
    """

    def __init__(
        self,
        layers: DriftLayers,
        ports: DriftResponsePorts,
        downstream_impact_gate: Callable[[LayerResult], bool] | None = None,
        *,
        weights: dict[DriftLayer, float] | None = None,
        response_thresholds: tuple[float, float, float, float] = DEFAULT_RESPONSE_THRESHOLDS,
    ) -> None:
        if ports.notify is None:
            raise DriftObservatoryError("notify 为必备端口（告警不可静默）")
        self._layers = layers
        self._ports = ports
        self._gate = downstream_impact_gate
        self._weights = self._validate_weights(weights if weights is not None else DEFAULT_LAYER_WEIGHTS)
        self._thresholds = self._validate_thresholds(response_thresholds)
        self._applied: dict[str, DriftResponse] = {}  # 执行水位棘轮（每策略）

    @staticmethod
    def _validate_weights(weights: dict[DriftLayer, float]) -> dict[DriftLayer, float]:
        """权重校验：四层齐备 + 各 ∈(0,1] + 和=1（fail-closed 防静默误配）。"""
        if set(weights) != set(DriftLayer):
            raise DriftObservatoryError(
                f"权重须覆盖且仅覆盖四层: {sorted(k.value for k in weights)}",
                details={"expected": sorted(k.value for k in DriftLayer)},
            )
        if any(not 0.0 < w <= 1.0 for w in weights.values()):
            raise DriftObservatoryError(f"层权重须 ∈ (0,1]: {weights}")
        if abs(sum(weights.values()) - 1.0) > _WEIGHT_SUM_TOL:
            raise DriftObservatoryError(f"层权重和须 = 1.0: {sum(weights.values())}")
        return dict(weights)

    @staticmethod
    def _validate_thresholds(thresholds: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
        """响应阈值校验：四档严格递增且 ∈(0,1)（fail-closed 防阶梯倒置）。"""
        if len(thresholds) != 4:
            raise DriftObservatoryError(f"响应阈值须四档: {thresholds}")
        if any(not 0.0 < t < 1.0 for t in thresholds):
            raise DriftObservatoryError(f"响应阈值须 ∈ (0,1): {thresholds}")
        if any(b <= a for a, b in zip(thresholds, thresholds[1:])):
            raise DriftObservatoryError(f"响应阈值须严格递增: {thresholds}")
        return tuple(float(t) for t in thresholds)

    def applied_response(self, strategy_id: str) -> DriftResponse:
        """当前执行水位（未见策略默认 ALERT）。"""
        return self._applied.get(strategy_id, DriftResponse.ALERT)

    def reset_strategy(self, strategy_id: str) -> None:
        """人工复位执行水位（重训练完成/人工复核后；降级恢复不自动，须显式调用）。"""
        self._applied.pop(strategy_id, None)

    def observe(self, observation: DriftObservation) -> DriftVerdict:
        """单策略单窗口四层编排：检测 → 门控 → 联动 → 聚合裁决 → 棘轮执行。

        Raises:
            DriftObservatoryError: strategy_id 空。
            执行端口异常原样上抛（本次水位不推进，重试安全）。
        """
        strategy_id = observation.strategy_id
        if not strategy_id or not strategy_id.strip():
            raise DriftObservatoryError("strategy_id 不能为空")

        # F1: 四层并行检测（单层失败降级：计 0 分 + 留痕，不扩散）
        failed: list[DriftLayer] = []
        l1 = self._run_layer(self._layers.input_monitor, DriftLayer.INPUT, observation.features, failed)
        l2 = self._run_layer(self._layers.prediction_monitor, DriftLayer.PREDICTION, observation.model_output, failed)
        l3 = self._run_layer(self._layers.outcome_monitor, DriftLayer.OUTCOME, observation.realized_pnl, failed)
        l4 = self._run_layer(self._layers.conformal_layer, DriftLayer.CONFORMAL, observation, failed)

        # F2: 下游影响门控（仅 L1；良性漂移降级 severity=0 防告警疲劳）
        if l1 is not None and l1.severity > 0.0 and self._gate is not None:
            l1 = self._apply_impact_gate(l1)

        # F3: CUSUM→calibration flush 联动（L2 告警触发 L4 冲刷 + BC-ACI 纠偏）
        if l2 is not None and l2.cusum_alarm:
            self._cascade_cusum_flush(l2)

        # F4: 加权聚合 + 五级响应裁决（绝对权重：缺层计 0 不归一）
        present = tuple(r for r in (l1, l2, l3, l4) if r is not None)
        composite = sum(self._weights[r.layer] * r.severity for r in present)
        coverage_breach = bool(l4.coverage_breach) if l4 is not None else False
        response = map_response(composite, coverage_breach, self._thresholds)

        # F5: 水位棘轮执行（只升不降；同/低水位幂等零副作用）
        actions, skipped, idempotent = self._apply_response(strategy_id, response)

        verdict = DriftVerdict(
            strategy_id=strategy_id,
            response=response,
            composite=composite,
            applied_response=self._applied[strategy_id],
            layer_results=present,
            actions_fired=actions,
            skipped_ports=skipped,
            failed_layers=tuple(failed),
            degraded=bool(failed),
            coverage_breach=coverage_breach,
            idempotent_replay=idempotent,
        )
        if response is not DriftResponse.ALERT or verdict.degraded:
            logger.warning(
                "漂移裁决 %s: response=%s composite=%.3f applied=%s degraded=%s failed=%s",
                strategy_id,
                response.value,
                composite,
                verdict.applied_response.value,
                verdict.degraded,
                [k.value for k in failed],
            )
        self._ports.notify(strategy_id, verdict)  # 通知每轮照发（含 ALERT）
        return verdict

    # ── 内部步骤（每步一个 helper）──

    def _run_layer(
        self,
        detector: LayerDetector | ConformalLayerDetector | None,
        layer: DriftLayer,
        payload: object,
        failed: list[DriftLayer],
    ) -> LayerResult | None:
        """单层检测执行：缺省/异常/severity 越界一律降级（计 0 分 + failed 留痕）。"""
        if detector is None:
            failed.append(layer)
            return None
        try:
            result = detector.check(payload)  # type: ignore[arg-type]
        except Exception as exc:  # noqa: BLE001 — 单层失败降级语义要求全捕获：检测器故障不扩散到编排层
            logger.error("漂移层 %s 检测异常（降级计 0 分）: %s", layer.value, exc, exc_info=True)
            failed.append(layer)
            return None
        severity = result.severity
        if not isinstance(severity, (int, float)) or math.isnan(severity) or not 0.0 <= severity <= 1.0:
            logger.error("漂移层 %s severity 越界（%r，降级计 0 分）", layer.value, severity)
            failed.append(layer)
            return None
        return result

    def _apply_impact_gate(self, l1: LayerResult) -> LayerResult:
        """L1 下游影响门控：gate 否决 → severity 清零；gate 异常 → 保留告警（保守方向）。"""
        try:
            material = bool(self._gate(l1))
        except Exception as exc:  # noqa: BLE001 — 门控故障保留告警：漏过滤（告警疲劳）优于漏告警
            logger.error("L1 下游影响门控异常（保留告警）: %s", exc, exc_info=True)
            return l1
        if material:
            return l1
        logger.info("L1 良性漂移降级（regime 可解释且无性能退化）: %s", l1.detail)
        return LayerResult(layer=l1.layer, severity=0.0, detail=f"良性漂移降级: {l1.detail}")

    def _cascade_cusum_flush(self, l2: LayerResult) -> None:
        """CUSUM→calibration flush 联动（61 号：同一 CUSUM 既检残差漂移又触发 CP 校准集冲刷）。"""
        conformal = self._layers.conformal_layer
        if conformal is not None:
            try:
                conformal.flush_calibration_set()
            except Exception as exc:  # noqa: BLE001 — 冲刷失败不阻断本轮裁决（下轮重试）
                logger.error("calibration flush 异常（本轮裁决继续）: %s", exc, exc_info=True)
        if l2.residual_bias is not None and self._ports.bias_corrector is not None:
            self._ports.bias_corrector(l2.residual_bias)  # BC-ACI 纠偏（宽度+中心双重保护）

    def _apply_response(self, strategy_id: str, response: DriftResponse) -> tuple[tuple[str, ...], tuple[str, ...], bool]:
        """水位棘轮执行：升级才触发执行端口；同/低水位幂等零副作用（返回 idempotent=True）。"""
        applied = self._applied.get(strategy_id)
        if applied is not None and _RESPONSE_RANK[response] <= _RESPONSE_RANK[applied]:
            return (), (), True
        actions: list[str] = []
        skipped: list[str] = []
        # (端口名, 端口, 调用参数)——响应到执行端口的唯一映射
        port_name, port, args = {
            DriftResponse.REDUCE_SIZE: ("scale_position", self._ports.scale_position, (strategy_id, REDUCE_SIZE_SCALE)),
            DriftResponse.STOP_NEW_ENTRIES: ("disable_new_entries", self._ports.disable_new_entries, (strategy_id,)),
            DriftResponse.QUARANTINE: ("disable_strategy", self._ports.disable_strategy, (strategy_id,)),
            DriftResponse.RETRAIN: ("trigger_retraining", self._ports.trigger_retraining, (strategy_id,)),
        }.get(response, ("", None, ()))
        if port is not None:
            port(*args)  # 端口异常原样上抛：水位不推进，重试安全
            actions.append(port_name)
        elif port_name:
            skipped.append(port_name)
            logger.warning("响应 %s 执行端口 %s 未装配（跳过留痕）", response.value, port_name)
        self._applied[strategy_id] = response
        return tuple(actions), tuple(skipped), False


__all__ = [
    "DEFAULT_LAYER_WEIGHTS",
    "DEFAULT_RESPONSE_THRESHOLDS",
    "REDUCE_SIZE_SCALE",
    "ConformalLayerDetector",
    "DriftLayer",
    "DriftLayers",
    "DriftObservation",
    "DriftObservatoryError",
    "DriftObservatoryOrchestrator",
    "DriftResponse",
    "DriftResponsePorts",
    "DriftVerdict",
    "LayerDetector",
    "LayerResult",
    "map_response",
]
