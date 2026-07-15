# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.signal_fundamental.pipeline
# [DOMAIN] D_SIGLEGACY
# [DEPENDENCIES] zephyr.governance.__init__; zephyr.signal_fundamental.synth.signal_synthesizer; zephyr.trading.trading_contracts.market.factor_signal; zephyr.trading.trading_contracts.market.synthesized_signal
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_pipeline | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""AlphaSignalPipeline D_FACTOR->D_SIGNAL跨层集成管道
============================================
Domain   : _domain_signal (SIGNAL-DOMAIN-001)
Contracts: AS-CT-001~005
Layers   : D_FACTOR (AlphaFactor) -> D_SIGNAL (SignalGeneration)
Status   : Phase B — 骨架管道已就绪，底层C轨模块 blocked_by_infrastructure

管线阶段
--------
Stage 1: FactorDiscovery    — 发现已注册因子
Stage 2: FactorCompute      — 并行计算因子信号
Stage 3: SignalSynthesis    — 多因子加权聚合
Stage 4: SignalValidation   — 信号降级/置信度/regime校验
Stage 5: CapitalAllocation  — 信号->资金分配

AS-CT 契约覆盖
---------------
AS-CT-001: FactorSignal 生命周期管理
AS-CT-002: 因子计算幂等性保证
AS-CT-003: 信号合成加权策略契约
AS-CT-004: 信号降级->告警路由
AS-CT-005: 跨层审计追踪
"""

from __future__ import annotations

import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# 5.76.1 修复：删除同名 PipelineError 副本，统一使用 shared/foundation/errors.py 的 SSoT 定义
from zephyr.shared.foundation.errors import PipelineError
from zephyr.shared.utils.time_utils import now_utc

_MAX_WORKERS = 8

__all__ = [
    "AlphaSignalPipeline",
    "PipelineError",
    "PipelineResult",
    "PipelineStage",
]

try:
    from zephyr.factor.factor_base import FactorBase
    from zephyr.signal_fundamental.synth.signal_synthesizer import SignalSynthesizerBase
    from zephyr.trading.trading_contracts.market.factor_signal import FactorSignal
    from zephyr.trading.trading_contracts.market.synthesized_signal import SynthesizedSignal

    _CONTRACTS_AVAILABLE = True
except ImportError:
    _CONTRACTS_AVAILABLE = False


class PipelineStage(Enum):
    FACTOR_DISCOVERY = "factor_discovery"
    FACTOR_COMPUTE = "factor_compute"
    SIGNAL_SYNTHESIS = "signal_synthesis"
    SIGNAL_VALIDATION = "signal_validation"
    CAPITAL_ALLOCATION = "capital_allocation"


@dataclass
class PipelineResult:
    pipeline_id: str
    status: str
    stage: PipelineStage
    factors_computed: int = 0
    factors_failed: int = 0
    signal_count: int = 0
    confidence: float = 0.0
    degraded: bool = False
    errors: list[dict[str, Any]] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: now_utc().isoformat())
    completed_at: str | None = None
    idempotency_key: str = field(default_factory=lambda: str(uuid.uuid4()))


class AlphaSignalPipeline:
    """D_FACTOR->D_SIGNAL Alpha-Signal 跨层集成管道。

    将 D_FACTOR 因子层的原始因子信号通过 D_SIGNAL 信号合成引擎
    转化为统一的合成交易信号，并执行信号质量校验和降级路由。
    """

    _FACTOR_NAME_BLACKLIST = frozenset(
        {
            "malicious",
            "poison",
            "exploit",
            "trojan",
            "backdoor",
            "hack",
        }
    )
    _SUSPICIOUS_FACTORS: set[str] = set()
    _CONFIDENCE_CAP = 1.0
    _EXTREME_WEIGHT_THRESHOLD = 2.0

    def __init__(self) -> None:
        self._factors: list[type] = []
        self._synthesizers: list[type] = []
        self._degraded_reasons: list[str] = []
        self._builtins_guard_enabled: bool = True

    @staticmethod
    def _snapshot_builtins() -> frozenset[str]:
        try:
            import builtins

            return frozenset(builtins.__dict__.keys())
        except Exception:
            return frozenset()

    @staticmethod
    def _check_builtins_integrity(snapshot: frozenset[str]) -> list[str]:
        violations: list[str] = []
        try:
            import builtins

            current = set(builtins.__dict__.keys())
            added = current - snapshot
            if added:
                violations.append(f"builtins keys added: {sorted(added)}")
        except Exception as e:
            violations.append(f"builtins guard error: {e}")
        return violations

    def register_factor(self, factor_cls: type) -> None:
        if not _CONTRACTS_AVAILABLE:
            return
        name_lower = factor_cls.__name__.lower()
        for banned in self._FACTOR_NAME_BLACKLIST:
            if banned in name_lower:
                self._SUSPICIOUS_FACTORS.add(factor_cls.__name__)
                self._degraded_reasons.append(
                    f"Rejected suspicious factor: {factor_cls.__name__} (matches blacklist '{banned}')"
                )
                return
        self._factors.append(factor_cls)

    def register_synthesizer(self, synthesizer_cls: type) -> None:
        if not _CONTRACTS_AVAILABLE:
            return
        name_lower = synthesizer_cls.__name__.lower()
        for banned in self._FACTOR_NAME_BLACKLIST:
            if banned in name_lower:
                self._degraded_reasons.append(f"Rejected suspicious synthesizer: {synthesizer_cls.__name__}")
                return
        self._synthesizers.append(synthesizer_cls)

    def run(
        self,
        idempotency_key: str | None = None,
    ) -> PipelineResult:
        key = idempotency_key or str(uuid.uuid4())
        result = PipelineResult(
            pipeline_id=str(uuid.uuid4())[:8],
            status="running",
            stage=PipelineStage.FACTOR_DISCOVERY,
            idempotency_key=key,
        )

        # Preflight: 契约检查 + 因子发现
        early_return = self._run_preflight(result)
        if early_return is not None:
            return early_return

        # Factor compute: 并行计算因子信号
        result.stage = PipelineStage.FACTOR_COMPUTE
        factor_signals = self._compute_factors(result, key)
        if not factor_signals:
            result.status = "no_signals"
            return result

        # Signal synthesis: 多因子加权聚合
        result.stage = PipelineStage.SIGNAL_SYNTHESIS
        synthesized = self._run_synthesis(factor_signals, key)
        synthesized = self._flatten_signals(synthesized)

        # Signal validation: 极端信号检测 + 置信度计算
        extreme_signal_detected = self._detect_extreme_signals(synthesized)
        self._finalize_confidence_and_degradation(result, synthesized, extreme_signal_detected)
        self._record_degraded_errors(result)

        # Capital allocation: 最终阶段
        result.stage = PipelineStage.CAPITAL_ALLOCATION
        result.status = "completed_with_errors" if result.errors else "completed"
        result.completed_at = now_utc().isoformat()
        return result

    # ===== run() 各阶段辅助方法 =====

    def _run_preflight(self, result: PipelineResult) -> PipelineResult | None:
        """Preflight: 检查契约可用性和因子注册状态。返回 None=通过，PipelineResult=提前返回。"""
        if not _CONTRACTS_AVAILABLE:
            result.errors.append(
                {
                    "stage": "preflight",
                    "message": "D_FACTOR/D_SIGNAL contracts unavailable — running in degraded mode",
                }
            )
            result.degraded = True

        if not self._factors:
            # FactorBase 因子 compute(data) 需数据参数，与本管道 compute()->list 协议不兼容；
            # 不自动发现 FactorBase 因子（避免 TypeError），因子须通过 register_factor() 显式注册。
            # 原代码 getattr(FB,"discover_factors") 调用不存在的方法名，已修正为 FactorRegistry 查询。
            try:
                from zephyr.factor.factor_base import FactorRegistry

                _ = FactorRegistry.list_all()  # 确认 registry 可达，供未来协议适配扩展
            except Exception:
                pass
            self._factors = []

        if not self._factors:
            result.status = "no_factors"
            result.errors.append(
                {
                    "stage": PipelineStage.FACTOR_DISCOVERY.value,
                    "message": "No factors discovered or registered",
                }
            )
            return result
        return None

    def _compute_factors(self, result: PipelineResult, key: str) -> list:
        """并行计算所有因子，返回因子信号列表。"""
        factor_signals: list = []
        builtins_snapshot = self._snapshot_builtins() if self._builtins_guard_enabled else frozenset()

        with ThreadPoolExecutor(max_workers=min(_MAX_WORKERS, len(self._factors))) as executor:
            futures = {
                executor.submit(self._compute_single, factor_cls, key): factor_cls for factor_cls in self._factors
            }
            for future in as_completed(futures):
                self._collect_factor_result(future, futures, factor_signals, builtins_snapshot, result)
        return factor_signals

    def _collect_factor_result(
        self,
        future: Any,
        futures: dict,
        factor_signals: list,
        builtins_snapshot: frozenset,
        result: PipelineResult,
    ) -> None:
        """收集单个因子计算结果。"""
        try:
            signals = future.result()
            if self._builtins_guard_enabled:
                violations = self._check_builtins_integrity(builtins_snapshot)
                if violations:
                    result.factors_failed += 1
                    result.errors.append(
                        {
                            "stage": PipelineStage.FACTOR_COMPUTE.value,
                            "factor": futures[future].__name__,
                            "error": f"BUILTINS TAMPERED: {violations}",
                        }
                    )
                    return
            if signals:
                factor_signals.extend(signals if isinstance(signals, list) else [signals])
                result.factors_computed += 1
        except Exception as e:
            result.factors_failed += 1
            result.errors.append(
                {
                    "stage": PipelineStage.FACTOR_COMPUTE.value,
                    "factor": futures[future].__name__,
                    "error": str(e),
                }
            )

    @staticmethod
    def _flatten_signals(synthesized: list) -> list:
        """展平信号列表（处理嵌套列表）。"""
        flat_signals: list = []
        for item in synthesized:
            if isinstance(item, list):
                flat_signals.extend(item)
            else:
                flat_signals.append(item)
        return flat_signals

    def _detect_extreme_signals(self, synthesized: list) -> bool:
        """检测极端信号值和置信度，返回是否检测到极端信号。"""
        extreme_signal_detected = False
        for s in synthesized:
            sv = getattr(s, "signal_value", 0.0)
            if abs(sv) > 1000.0:
                extreme_signal_detected = True
                self._degraded_reasons.append(f"Extreme signal_value={sv:.1f} detected from synthesizer")
            meta_conf = getattr(s, "confidence", 0.0)
            if meta_conf > self._EXTREME_WEIGHT_THRESHOLD:
                self._degraded_reasons.append(f"Extreme confidence={meta_conf:.4f} > {self._EXTREME_WEIGHT_THRESHOLD}")
        return extreme_signal_detected

    def _finalize_confidence_and_degradation(
        self,
        result: PipelineResult,
        synthesized: list,
        extreme_signal_detected: bool,
    ) -> None:
        """计算置信度并确定降级状态。"""
        result.signal_count = len(synthesized)
        raw_confidence = self._aggregate_confidence(synthesized)

        if extreme_signal_detected:
            raw_confidence = self._EXTREME_WEIGHT_THRESHOLD + 1.0

        result.confidence = min(raw_confidence, self._CONFIDENCE_CAP)
        result.degraded = (
            result.confidence < 0.5
            or raw_confidence > self._EXTREME_WEIGHT_THRESHOLD
            or extreme_signal_detected
            or bool(self._degraded_reasons)
        )

        if raw_confidence > self._EXTREME_WEIGHT_THRESHOLD:
            self._degraded_reasons.append(
                f"Extreme weight detected: raw_confidence={raw_confidence:.4f} > {self._EXTREME_WEIGHT_THRESHOLD}"
            )

    def _record_degraded_errors(self, result: PipelineResult) -> None:
        """记录降级原因到错误列表。"""
        if not result.degraded:
            return
        for reason in self._degraded_reasons:
            result.errors.append(
                {
                    "stage": PipelineStage.SIGNAL_VALIDATION.value,
                    "message": reason,
                    "confidence": result.confidence,
                }
            )
        if result.confidence < 0.5 and not self._degraded_reasons:
            result.errors.append(
                {
                    "stage": PipelineStage.SIGNAL_VALIDATION.value,
                    "message": f"Signal degraded: confidence={result.confidence:.3f} < 0.5",
                    "confidence": result.confidence,
                }
            )

    def _compute_single(self, factor_cls: type, idempotency_key: str) -> list | None:
        instance = factor_cls()
        if hasattr(instance, "compute"):
            return instance.compute()
        if hasattr(instance, "compute_with_key"):
            return instance.compute_with_key(idempotency_key)
        return None

    def _run_synthesis(self, factor_signals: list, idempotency_key: str) -> list:
        if not self._synthesizers:
            try:
                from zephyr.signal_fundamental.synth.signal_synthesizer import SignalSynthesizerBase as SSB

                synthesizers = getattr(SSB, "_registry", {})
                self._synthesizers = list(synthesizers.values())
            except Exception:
                self._synthesizers = []

        if not self._synthesizers:
            raw_confidences = []
            for sig in factor_signals:
                if hasattr(sig, "confidence"):
                    raw_confidences.append(sig.confidence)
                elif isinstance(sig, dict) and "confidence" in sig:
                    raw_confidences.append(sig["confidence"])
            avg_confidence = sum(raw_confidences) / len(raw_confidences) if raw_confidences else 0.5
            return [
                {
                    "synthesized": True,
                    "signal_count": len(factor_signals),
                    "key": idempotency_key,
                    "confidence": avg_confidence,
                }
            ]

        results = []
        for synth_cls in self._synthesizers:
            synth = synth_cls()
            if hasattr(synth, "synthesize"):
                result = synth.synthesize(factor_signals, symbol="", as_of_timestamp=None)
                results.append(result)
        return results

    @staticmethod
    def _aggregate_confidence(synthesized: list) -> float:
        if not synthesized:
            return 0.0
        confidences = []
        for sig in synthesized:
            if hasattr(sig, "confidence"):
                confidences.append(sig.confidence)
            elif isinstance(sig, dict) and "confidence" in sig:
                confidences.append(sig["confidence"])
        if not confidences:
            return 0.5
        return sum(confidences) / len(confidences)


if __name__ == "__main__":
    import json as _json

    pipe = AlphaSignalPipeline()
    result = pipe.run()
    print(
        _json.dumps(
            {
                "status": result.status,
                "factors_computed": result.factors_computed,
                "signal_count": result.signal_count,
                "confidence": result.confidence,
                "degraded": result.degraded,
                "errors": result.errors,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
