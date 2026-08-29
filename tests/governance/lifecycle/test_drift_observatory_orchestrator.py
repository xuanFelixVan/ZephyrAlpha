# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.lifecycle.test_drift_observatory_orchestrator
# [DOMAIN] D_GOVERNANCE
# [A_module] module_id=MOD-TEST-GOV-DRIFTOBS | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Drift Observatory 四层编排器单元测试（61 号 §3.3 纪律 4）。

覆盖:
  - 配置校验：notify 必备 / 权重须四层齐备且和=1 / 响应阈值严格递增且 ∈(0,1) / 空 strategy_id
  - 响应映射：composite 阈值 0.20/0.40/0.60/0.80 全边界 + coverage_breach 直达 RETRAIN（不可稀释）
  - 四层聚合：权重 {1:0.15, 2:0.20, 3:0.25, 4:0.40} 绝对值（缺层计 0 不归一，
    L1 单层 1.0 仅 ALERT——memo 时序纪律"单层告警不触发高级响应"）
  - 载荷路由：L1←features / L2←model_output / L3←realized_pnl / L4←整包观测
  - 下游影响门控：仅作用 L1；gate 否决 → L1 severity 清零；gate 异常 → 保留告警（保守方向）
  - CUSUM→calibration flush 联动：L2 cusum_alarm → L4 flush + BC-ACI 偏置纠正
  - 单层失败降级：层异常/severity 越界 → 该层计 0 + degraded 留痕，其余层照常裁决
  - 空输入：四层全缺 → composite=0.0 → ALERT + degraded（观测面丧失本身即告警）
  - 执行与幂等：五级响应各自端口映射 / 同水位重入零副作用 / 水位只升不降 /
    reset_strategy 人工复位 / 可选端口缺失 skipped_ports 留痕 / 多策略水位独立
"""

from __future__ import annotations

import pytest

from zephyr.governance.lifecycle_governance.drift_observatory_orchestrator import (
    DEFAULT_LAYER_WEIGHTS,
    DriftLayer,
    DriftLayers,
    DriftObservation,
    DriftObservatoryError,
    DriftObservatoryOrchestrator,
    DriftResponse,
    DriftResponsePorts,
    LayerResult,
    map_response,
)


class _StubLayer:
    """四层通用 stub：固定 severity 出参；boom 注入异常模拟单层失败；flush 计数。"""

    def __init__(
        self,
        layer: DriftLayer,
        severity: float = 0.0,
        *,
        cusum_alarm: bool = False,
        residual_bias: float | None = None,
        coverage_breach: bool = False,
        boom: Exception | None = None,
    ) -> None:
        self._layer = layer
        self._severity = severity
        self._cusum_alarm = cusum_alarm
        self._residual_bias = residual_bias
        self._coverage_breach = coverage_breach
        self._boom = boom
        self.calls: list[object] = []
        self.flush_calls = 0

    def check(self, payload: object) -> LayerResult:
        if self._boom is not None:
            raise self._boom
        self.calls.append(payload)
        return LayerResult(
            layer=self._layer,
            severity=self._severity,
            cusum_alarm=self._cusum_alarm,
            residual_bias=self._residual_bias,
            coverage_breach=self._coverage_breach,
        )

    def flush_calibration_set(self) -> None:
        self.flush_calls += 1


def _ports(*, with_actions: bool = True, with_bias: bool = True):
    """构造 stub 执行端口；calls 列表记录全部执行动作（顺序/计数断言用）。"""
    calls: list[tuple] = []
    ports = DriftResponsePorts(
        notify=lambda sid, verdict: calls.append(("notify", sid, verdict.response)),
        scale_position=(lambda sid, r: calls.append(("scale", sid, r))) if with_actions else None,
        disable_new_entries=(lambda sid: calls.append(("disable_new", sid))) if with_actions else None,
        disable_strategy=(lambda sid: calls.append(("disable_strategy", sid))) if with_actions else None,
        trigger_retraining=(lambda sid: calls.append(("retrain", sid))) if with_actions else None,
        bias_corrector=(lambda b: calls.append(("bias", b))) if with_bias else None,
    )
    return ports, calls


def _orchestrator(*, l1=None, l2=None, l3=None, l4=None, gate=None, ports=None):
    return DriftObservatoryOrchestrator(
        layers=DriftLayers(input_monitor=l1, prediction_monitor=l2, outcome_monitor=l3, conformal_layer=l4),
        ports=ports or _ports()[0],
        downstream_impact_gate=gate,
    )


def _obs(sid: str = "s1") -> DriftObservation:
    return DriftObservation(
        strategy_id=sid,
        features={"f1": [1.0, 2.0]},
        model_output=[0.5, 0.6],
        realized_pnl=[0.01, -0.02],
    )


# ---------------------------------------------------------------------------
# 配置校验
# ---------------------------------------------------------------------------


class TestConfigValidation:
    def test_notify_port_required(self):
        ports, _ = _ports()
        object.__setattr__(ports, "notify", None)  # frozen dataclass 注入非法态
        with pytest.raises(DriftObservatoryError):
            _orchestrator(ports=ports)

    def test_weights_must_cover_exactly_four_layers(self):
        bad = {DriftLayer.INPUT: 0.5, DriftLayer.PREDICTION: 0.5}
        with pytest.raises(DriftObservatoryError):
            DriftObservatoryOrchestrator(layers=DriftLayers(), ports=_ports()[0], weights=bad)

    def test_weights_sum_must_be_one(self):
        bad = {DriftLayer.INPUT: 0.5, DriftLayer.PREDICTION: 0.2, DriftLayer.OUTCOME: 0.25, DriftLayer.CONFORMAL: 0.4}
        with pytest.raises(DriftObservatoryError):
            DriftObservatoryOrchestrator(layers=DriftLayers(), ports=_ports()[0], weights=bad)

    def test_weights_must_be_positive(self):
        bad = {DriftLayer.INPUT: 0.0, DriftLayer.PREDICTION: 0.2, DriftLayer.OUTCOME: 0.25, DriftLayer.CONFORMAL: 0.55}
        with pytest.raises(DriftObservatoryError):
            DriftObservatoryOrchestrator(layers=DriftLayers(), ports=_ports()[0], weights=bad)

    def test_thresholds_strictly_increasing(self):
        with pytest.raises(DriftObservatoryError):
            DriftObservatoryOrchestrator(
                layers=DriftLayers(), ports=_ports()[0], response_thresholds=(0.2, 0.4, 0.4, 0.8)
            )

    def test_thresholds_in_unit_interval(self):
        with pytest.raises(DriftObservatoryError):
            DriftObservatoryOrchestrator(
                layers=DriftLayers(), ports=_ports()[0], response_thresholds=(0.0, 0.4, 0.6, 0.8)
            )

    def test_empty_strategy_id_rejected(self):
        with pytest.raises(DriftObservatoryError):
            _orchestrator().observe(_obs(sid="  "))

    def test_default_weights_match_memo(self):
        """61 号施工要点①：Layer 4 权重最高 0.40（可证覆盖 > 经验阈值）。"""
        assert DEFAULT_LAYER_WEIGHTS == {
            DriftLayer.INPUT: 0.15,
            DriftLayer.PREDICTION: 0.20,
            DriftLayer.OUTCOME: 0.25,
            DriftLayer.CONFORMAL: 0.40,
        }


# ---------------------------------------------------------------------------
# 响应映射（纯函数，阈值全边界）
# ---------------------------------------------------------------------------


class TestResponseMapping:
    @pytest.mark.parametrize(
        "composite,expected",
        [
            (0.0, DriftResponse.ALERT),
            (0.19, DriftResponse.ALERT),
            (0.20, DriftResponse.REDUCE_SIZE),  # 边界含
            (0.39, DriftResponse.REDUCE_SIZE),
            (0.40, DriftResponse.STOP_NEW_ENTRIES),
            (0.59, DriftResponse.STOP_NEW_ENTRIES),
            (0.60, DriftResponse.QUARANTINE),
            (0.79, DriftResponse.QUARANTINE),
            (0.80, DriftResponse.RETRAIN),
            (0.95, DriftResponse.RETRAIN),
        ],
    )
    def test_threshold_boundaries(self, composite, expected):
        assert map_response(composite, coverage_breach=False) is expected

    def test_coverage_breach_bypasses_composite(self):
        """施工要点⑤：Layer 4 可证覆盖破 → 直达 RETRAIN，不被其他层稀释。"""
        assert map_response(0.0, coverage_breach=True) is DriftResponse.RETRAIN
        assert map_response(0.1, coverage_breach=True) is DriftResponse.RETRAIN


# ---------------------------------------------------------------------------
# 四层聚合（权重绝对值 + 载荷路由）
# ---------------------------------------------------------------------------


class TestFourLayerAggregation:
    def test_all_calm_alert_and_notify_only(self):
        ports, calls = _ports()
        orch = _orchestrator(
            l1=_StubLayer(DriftLayer.INPUT),
            l2=_StubLayer(DriftLayer.PREDICTION),
            l3=_StubLayer(DriftLayer.OUTCOME),
            l4=_StubLayer(DriftLayer.CONFORMAL),
            ports=ports,
        )
        verdict = orch.observe(_obs())
        assert verdict.response is DriftResponse.ALERT
        assert verdict.composite == pytest.approx(0.0)
        assert len(verdict.layer_results) == 4
        assert verdict.degraded is False
        assert calls == [("notify", "s1", DriftResponse.ALERT)]  # 仅通知，无执行端口

    @pytest.mark.parametrize(
        "hot_layer,composite,response",
        [
            (DriftLayer.INPUT, 0.15, DriftResponse.ALERT),  # L1 单层最高 0.15 → 仅通知（时序纪律）
            (DriftLayer.PREDICTION, 0.20, DriftResponse.REDUCE_SIZE),
            (DriftLayer.OUTCOME, 0.25, DriftResponse.REDUCE_SIZE),
            (DriftLayer.CONFORMAL, 0.40, DriftResponse.STOP_NEW_ENTRIES),  # L4 单层最多中级
        ],
    )
    def test_single_layer_full_severity_never_reaches_retrain(self, hot_layer, composite, response):
        """memo 核心纪律：单一层告警不触发高级响应，须多层确认（绝对权重不归一）。"""
        layers = {k: _StubLayer(k, severity=1.0 if k is hot_layer else 0.0) for k in DEFAULT_LAYER_WEIGHTS}
        verdict = _orchestrator(
            l1=layers[DriftLayer.INPUT],
            l2=layers[DriftLayer.PREDICTION],
            l3=layers[DriftLayer.OUTCOME],
            l4=layers[DriftLayer.CONFORMAL],
        ).observe(_obs())
        assert verdict.composite == pytest.approx(composite)
        assert verdict.response is response

    def test_all_layers_full_retrain(self):
        verdict = _orchestrator(
            l1=_StubLayer(DriftLayer.INPUT, 1.0),
            l2=_StubLayer(DriftLayer.PREDICTION, 1.0),
            l3=_StubLayer(DriftLayer.OUTCOME, 1.0),
            l4=_StubLayer(DriftLayer.CONFORMAL, 1.0),
        ).observe(_obs())
        assert verdict.composite == pytest.approx(1.0)
        assert verdict.response is DriftResponse.RETRAIN

    def test_payloads_routed_to_layers(self):
        l1, l2, l3, l4 = (
            _StubLayer(DriftLayer.INPUT),
            _StubLayer(DriftLayer.PREDICTION),
            _StubLayer(DriftLayer.OUTCOME),
            _StubLayer(DriftLayer.CONFORMAL),
        )
        obs = _obs()
        _orchestrator(l1=l1, l2=l2, l3=l3, l4=l4).observe(obs)
        assert l1.calls == [obs.features]  # L1 ← 特征
        assert l2.calls == [obs.model_output]  # L2 ← 模型输出
        assert l3.calls == [obs.realized_pnl]  # L3 ← 延迟结果
        assert l4.calls == [obs]  # L4 ← 整包观测（覆盖检验需输入+输出+真值）


# ---------------------------------------------------------------------------
# 下游影响门控（仅 Layer 1）
# ---------------------------------------------------------------------------


class TestDownstreamImpactGate:
    def test_benign_l1_zeroed_by_gate(self):
        """良性漂移（regime 可解释且无性能退化）→ L1 降级 severity=0，防告警疲劳。"""
        gate_calls: list[LayerResult] = []
        gate = lambda r: gate_calls.append(r) or False
        verdict = _orchestrator(l1=_StubLayer(DriftLayer.INPUT, 1.0), gate=gate).observe(_obs())
        assert verdict.composite == pytest.approx(0.0)
        assert verdict.response is DriftResponse.ALERT
        assert len(gate_calls) == 1 and gate_calls[0].layer is DriftLayer.INPUT

    def test_gate_pass_keeps_severity(self):
        verdict = _orchestrator(l1=_StubLayer(DriftLayer.INPUT, 1.0), gate=lambda r: True).observe(_obs())
        assert verdict.composite == pytest.approx(0.15)

    def test_gate_not_applied_to_other_layers(self):
        """施工要点②：门控仅作用 L1——L2-4 已直接关联模型行为。"""
        verdict = _orchestrator(l2=_StubLayer(DriftLayer.PREDICTION, 1.0), gate=lambda r: False).observe(_obs())
        assert verdict.composite == pytest.approx(0.20)

    def test_gate_absent_no_filtering(self):
        verdict = _orchestrator(l1=_StubLayer(DriftLayer.INPUT, 1.0), gate=None).observe(_obs())
        assert verdict.composite == pytest.approx(0.15)

    def test_gate_exception_keeps_alarm(self):
        """门控自身故障 → 保留告警（保守方向：漏过滤优于漏告警）。"""

        def _boom(_r):
            raise RuntimeError("regime detector down")

        verdict = _orchestrator(l1=_StubLayer(DriftLayer.INPUT, 1.0), gate=_boom).observe(_obs())
        assert verdict.composite == pytest.approx(0.15)


# ---------------------------------------------------------------------------
# CUSUM → calibration flush 联动（L2 告警触发 L4 校准集冲刷 + BC-ACI 纠偏）
# ---------------------------------------------------------------------------


class TestCusumConformalLinkage:
    def test_cusum_alarm_triggers_flush_and_bias_correction(self):
        l4 = _StubLayer(DriftLayer.CONFORMAL)
        ports, calls = _ports()
        _orchestrator(
            l2=_StubLayer(DriftLayer.PREDICTION, cusum_alarm=True, residual_bias=0.3),
            l4=l4,
            ports=ports,
        ).observe(_obs())
        assert l4.flush_calls == 1
        assert ("bias", 0.3) in calls

    def test_no_alarm_no_flush(self):
        l4 = _StubLayer(DriftLayer.CONFORMAL)
        ports, calls = _ports()
        _orchestrator(l2=_StubLayer(DriftLayer.PREDICTION), l4=l4, ports=ports).observe(_obs())
        assert l4.flush_calls == 0
        assert not [c for c in calls if c[0] == "bias"]

    def test_alarm_without_conformal_layer_no_crash(self):
        ports, calls = _ports()
        verdict = _orchestrator(
            l2=_StubLayer(DriftLayer.PREDICTION, cusum_alarm=True, residual_bias=0.1),
            ports=ports,
        ).observe(_obs())
        assert verdict.response is DriftResponse.ALERT  # 无 L4 不应崩溃
        assert ("bias", 0.1) in calls  # BC-ACI 与 flush 独立（纠偏不依赖覆盖层）

    def test_alarm_without_bias_skips_corrector(self):
        l4 = _StubLayer(DriftLayer.CONFORMAL)
        ports, calls = _ports()
        _orchestrator(
            l2=_StubLayer(DriftLayer.PREDICTION, cusum_alarm=True, residual_bias=None),
            l4=l4,
            ports=ports,
        ).observe(_obs())
        assert l4.flush_calls == 1
        assert not [c for c in calls if c[0] == "bias"]


# ---------------------------------------------------------------------------
# 单层失败降级 + 空输入
# ---------------------------------------------------------------------------


class TestDegradation:
    def test_single_layer_failure_degrades_gracefully(self):
        """单层异常 → 该层计 0 分 + degraded 留痕，其余在位层照常聚合裁决。"""
        verdict = _orchestrator(
            l2=_StubLayer(DriftLayer.PREDICTION, boom=RuntimeError("CUSUM 栈溢出")),
            l4=_StubLayer(DriftLayer.CONFORMAL, 1.0),
        ).observe(_obs())
        assert verdict.degraded is True
        assert DriftLayer.PREDICTION in verdict.failed_layers  # 异常层
        assert DriftLayer.CONFORMAL not in verdict.failed_layers  # 健康层不留痕
        assert verdict.composite == pytest.approx(0.40)  # L4 单层权重
        assert verdict.response is DriftResponse.STOP_NEW_ENTRIES

    def test_empty_input_all_layers_absent(self):
        """空输入（四层全缺）→ composite=0.0 → ALERT + degraded：观测面丧失本身即告警。"""
        ports, calls = _ports()
        verdict = _orchestrator(ports=ports).observe(_obs())
        assert verdict.degraded is True
        assert set(verdict.failed_layers) == set(DEFAULT_LAYER_WEIGHTS)
        assert verdict.composite == 0.0
        assert verdict.response is DriftResponse.ALERT
        assert calls == [("notify", "s1", DriftResponse.ALERT)]

    def test_invalid_severity_treated_as_layer_failure(self):
        """层输出越界（severity>1 / NaN）按层失败降级处理，不污染 composite。"""
        verdict = _orchestrator(
            l1=_StubLayer(DriftLayer.INPUT, 1.5),
            l3=_StubLayer(DriftLayer.OUTCOME, 1.0),
        ).observe(_obs())
        assert verdict.degraded is True
        assert DriftLayer.INPUT in verdict.failed_layers
        assert verdict.composite == pytest.approx(0.25)

    def test_conformal_failure_cannot_trigger_retrain(self):
        """L4 失败时 coverage_breach 视为 False——数学保证层缺席不得臆断其告警。"""
        verdict = _orchestrator(l4=_StubLayer(DriftLayer.CONFORMAL, boom=ValueError("bad"))).observe(_obs())
        assert verdict.coverage_breach is False
        assert verdict.response is DriftResponse.ALERT
        assert verdict.degraded is True


# ---------------------------------------------------------------------------
# 执行端口映射 + 幂等重入 + 水位只升不降
# ---------------------------------------------------------------------------


class TestExecutionAndIdempotency:
    @pytest.mark.parametrize(
        "severities,response,port_name,action",
        [
            ({DriftLayer.OUTCOME: 1.0}, DriftResponse.REDUCE_SIZE, "scale_position", ("scale", "s1", 0.5)),
            ({DriftLayer.CONFORMAL: 1.0}, DriftResponse.STOP_NEW_ENTRIES, "disable_new_entries", ("disable_new", "s1")),
            (
                {DriftLayer.OUTCOME: 1.0, DriftLayer.CONFORMAL: 1.0},
                DriftResponse.QUARANTINE,
                "disable_strategy",
                ("disable_strategy", "s1"),
            ),
            (
                {DriftLayer.PREDICTION: 1.0, DriftLayer.OUTCOME: 1.0, DriftLayer.CONFORMAL: 1.0},
                DriftResponse.RETRAIN,
                "trigger_retraining",
                ("retrain", "s1"),
            ),
        ],
    )
    def test_escalation_fires_mapped_port(self, severities, response, port_name, action):
        ports, calls = _ports()
        stubs = {k: _StubLayer(k, severities.get(k, 0.0)) for k in DEFAULT_LAYER_WEIGHTS}
        verdict = _orchestrator(
            l1=stubs[DriftLayer.INPUT],
            l2=stubs[DriftLayer.PREDICTION],
            l3=stubs[DriftLayer.OUTCOME],
            l4=stubs[DriftLayer.CONFORMAL],
            ports=ports,
        ).observe(_obs())
        assert verdict.response is response
        assert verdict.actions_fired == (port_name,)
        assert action in calls
        assert calls[-1][0] == "notify"  # 动作先于通知（通知携带终态）

    def test_idempotent_reentry_same_verdict_zero_side_effects(self):
        """幂等重入：同水位重复裁决 → 执行端口只发一次，重放零副作用。"""
        ports, calls = _ports()
        orch = _orchestrator(l4=_StubLayer(DriftLayer.CONFORMAL, 1.0), ports=ports)
        v1 = orch.observe(_obs())
        v2 = orch.observe(_obs())
        assert v1.actions_fired == ("disable_new_entries",)
        assert v2.idempotent_replay is True
        assert v2.actions_fired == ()
        assert [c for c in calls if c[0] == "disable_new"] == [("disable_new", "s1")]  # 仅一次
        assert [c for c in calls if c[0] == "notify"] == [
            ("notify", "s1", DriftResponse.STOP_NEW_ENTRIES),
            ("notify", "s1", DriftResponse.STOP_NEW_ENTRIES),
        ]  # 通知每次照发

    def test_watermark_ratchets_up_only(self):
        """升级有序触发；降级不自动（对齐 rollback_state_machine 单向保守纪律）。"""
        l3, l4 = _StubLayer(DriftLayer.OUTCOME, 1.0), _StubLayer(DriftLayer.CONFORMAL, 0.0)
        ports, calls = _ports()
        orch = _orchestrator(l3=l3, l4=l4, ports=ports)
        v1 = orch.observe(_obs())  # 0.25 → REDUCE_SIZE
        assert v1.applied_response is DriftResponse.REDUCE_SIZE
        l4._severity = 1.0  # 升级为 0.65 → QUARANTINE
        v2 = orch.observe(_obs())
        assert v2.applied_response is DriftResponse.QUARANTINE
        assert [c[0] for c in calls if c[0] != "notify"] == ["scale", "disable_strategy"]
        l3._severity = 0.0
        l4._severity = 0.0  # 观测归零 → 响应回落 ALERT，但水位不自动降
        v3 = orch.observe(_obs())
        assert v3.response is DriftResponse.ALERT
        assert v3.applied_response is DriftResponse.QUARANTINE
        assert [c[0] for c in calls if c[0] != "notify"] == ["scale", "disable_strategy"]  # 无新动作

    def test_reset_strategy_allows_refire(self):
        """人工复位（重训练完成/人工复核后）→ 同输入可再次触发执行。"""
        ports, calls = _ports()
        orch = _orchestrator(l4=_StubLayer(DriftLayer.CONFORMAL, 1.0), ports=ports)
        orch.observe(_obs())
        orch.reset_strategy("s1")
        v = orch.observe(_obs())
        assert v.actions_fired == ("disable_new_entries",)
        assert [c for c in calls if c[0] == "disable_new"] == [("disable_new", "s1"), ("disable_new", "s1")]

    def test_missing_optional_port_skipped_with_trace(self):
        ports, calls = _ports(with_actions=False)
        verdict = _orchestrator(l4=_StubLayer(DriftLayer.CONFORMAL, 1.0), ports=ports).observe(_obs())
        assert verdict.response is DriftResponse.STOP_NEW_ENTRIES
        assert verdict.actions_fired == ()
        assert "disable_new_entries" in verdict.skipped_ports
        assert calls == [("notify", "s1", DriftResponse.STOP_NEW_ENTRIES)]

    def test_watermarks_independent_per_strategy(self):
        ports, _ = _ports()
        orch = _orchestrator(l4=_StubLayer(DriftLayer.CONFORMAL, 1.0), ports=ports)
        orch.observe(_obs("s1"))
        v = orch.observe(_obs("s2"))
        assert v.actions_fired == ("disable_new_entries",)  # s2 独立水位，不受 s1 影响
        assert orch.applied_response("s1") is DriftResponse.STOP_NEW_ENTRIES
        assert orch.applied_response("s2") is DriftResponse.STOP_NEW_ENTRIES
        assert orch.applied_response("s3") is DriftResponse.ALERT  # 未见策略默认 ALERT
