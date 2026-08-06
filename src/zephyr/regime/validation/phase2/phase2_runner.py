# [BLUEPRINT] MOD-REGIME-VAL-002-RUN | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/discussion_003_phase2_model_quality_validation.md §4
# [MODULE] zephyr.regime.validation.phase2.phase2_runner
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas; zephyr.regime.core.regime_detector; zephyr.regime.regime_feature_builder
# [CONSUMERS] scripts.tests.run_phase2_validation; BM-BT-05
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] runner只读 builder/detector, 不改其状态; walk-forward 复刻 C1 真实模式(PIT shift+季度refit+trailing窗口); A1用全历史fit, B4用walk-forward逐日detect收集_last_transitions
# [MODIFY-GUARD] discussion_003_phase2_model_quality_validation.md §4
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] Phase2RunnerError(ZA-REGIME-0022)
# [TESTS] tests/regime/phase2/test_phase2_runner.py
# [TTL] permanent
# [ARCH-REF] #discussion_003 §4 #discussion_002 §6
"""Phase 2 模型质量验证编排器（discussion_003 §4）.

复用 C1 真实模式管线（取数+特征+walk-forward refit），但自行执行 detect 以收集
A1/B4 所需中间产物（_last_transitions / Viterbi 状态序列）。

编排:
  A1 - 样本充足性（全历史 fit + Viterbi 解码 + 计数）
  B4 - 转换触发准确性（walk-forward 逐日 detect 收集 _last_transitions + 事件匹配）
  第二批 A2/B1 待补

依据: discussion_003 §4
Version: 0.1.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

try:
    from sklearn.preprocessing import RobustScaler
except ImportError:  # pragma: no cover
    RobustScaler = None  # type: ignore[assignment,misc]

try:
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # pragma: no cover
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

from zephyr.regime.validation.phase2.a1_sample_sufficiency import (
    A1Overall,
    A1Report,
    A1SampleSufficiency,
)
from zephyr.regime.validation.phase2.a2_hmm_overfitting import (
    A2HmmOverfitting,
    A2Report,
    A2Verdict,
)
from zephyr.regime.validation.phase2.b1_probability_calibration import (
    B1ProbabilityCalibration,
    B1Report,
    B1Verdict,
)
from zephyr.regime.validation.phase2.b4_transition_accuracy import (
    B4Report,
    B4TransitionAccuracy,
    B4Verdict,
)

_logger = logging.getLogger(__name__)


class Phase2RunnerError(ZephyrBaseError):
    """ZA-REGIME-0022: Phase 2 runner 错误（builder 未配置 overlay / 特征缺失）。"""

    error_code = "ZA-REGIME-0022"


@dataclass(frozen=True)
class Phase2Report:
    """Phase 2 综合报告。"""

    a1: A1Report
    b4: B4Report
    overall_pass: bool  # A1 PASS/REVIEW 且 B4 PASS
    summary: str
    a2: A2Report | None = None  # 第二批（None=未运行）
    b1: B1Report | None = None  # 第二批（None=未运行）
    run_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "a1": self.a1.to_dict(),
            "b4": self.b4.to_dict(),
            "a2": self.a2.to_dict() if self.a2 is not None else None,
            "b1": self.b1.to_dict() if self.b1 is not None else None,
            "overall_pass": self.overall_pass,
            "summary": self.summary,
            "run_at": self.run_at.isoformat(),
        }


class Phase2Runner:
    """Phase 2 编排器：串 A1 → B4 → A2 → B1 → 综合报告.

    Usage（real 模式，复用 C1 真实模式 builder 配置）:
        builder = RegimeFeatureBuilder(
            backtest_start="2015-01-01", backtest_end="2026-06-30",
            data_load_start="2010-01-01",
            enable_full_risk=True,   # Phase 2a
            enable_overlay=True,    # Phase 2b（B4 必需）
        )
        runner = Phase2Runner()
        report = runner.run(builder, train_years=5, detect_window=60)

    Note:
        - A1 用全历史特征（2010-2026）fit 一个全新 HMM 做 Viterbi 解码
        - B4 复刻 walk-forward 季度 refit + 逐日 detect，收集 _last_transitions
        - A2 用全历史特征做 IS/OOS 交叉解码一致率（第二批）
        - B1 用 walk-forward detect 收集的 (confidence, dominant_regime) + 后续收益（第二批）
        - builder 必须 enable_overlay=True（否则 _last_transitions 恒空，B4 无意义）
    """

    def __init__(self, hmm_params: dict[str, Any] | None = None) -> None:
        self.hmm_params = hmm_params

    def run(
        self,
        builder: Any,
        train_years: int = 5,
        detect_window: int = 60,
        refit_freq: str = "QE",
        events_path: str | Any | None = None,
        run_second_batch: bool = True,
        is_oos_split: str = "2018-12-31",
        b1_forward_days: int = 20,
    ) -> Phase2Report:
        """运行 Phase 2 验证（A1 + B4 [+ A2 + B1]）。

        Args:
            builder: RegimeFeatureBuilder 实例（需 enable_overlay=True）。
            train_years: walk-forward 训练窗口年数。
            detect_window: detect 时 trailing 特征窗口。
            refit_freq: 重拟合频率（"QE"=季末）。
            events_path: 历史事件库 YAML 路径（None 用默认）。
            run_second_batch: 是否运行第二批 A2+B1（默认 True）。
            is_oos_split: A2 的 IS/OOS 分割日期（IS ≤ 此日 < OOS，默认 "2018-12-31"）。
            b1_forward_days: B1 后续收益天数（默认 20 交易日）。

        Returns:
            Phase2Report。
        """
        if not getattr(builder, "enable_overlay", False):
            raise Phase2RunnerError(
                "builder.enable_overlay=False，B4 无 _last_transitions 可收集；"
                "Phase 2 需 enable_overlay=True"
            )

        features = builder.build_features()
        feature_names = _get_feature_names(builder)
        _logger.info(
            "Phase2 runner: features=%d 行 × %d 特征 [%s, %s]",
            len(features), len(feature_names),
            features.index.min(), features.index.max(),
        )

        # ── A1: 全历史 fit + Viterbi ──
        _logger.info("Phase2 A1: 全历史 fit + Viterbi 解码...")
        X_full = features[feature_names].to_numpy(dtype=float)
        a1_validator = A1SampleSufficiency(hmm_params=self.hmm_params)
        a1_report = a1_validator.validate(X_full, standardize=True)
        _logger.info("A1: %s", a1_report.summary)

        # ── B4: walk-forward 逐日 detect 收集 _last_transitions + detect_records ──
        _logger.info("Phase2 B4: walk-forward 逐日 detect 收集 _last_transitions...")
        daily_transitions, trading_dates, detect_records = self._collect_daily_transitions(
            builder, features, feature_names, train_years, detect_window, refit_freq,
        )
        _logger.info(
            "B4: 收集 %d 日 transitions，%d 日有触发记录，%d 条 detect_records",
            len(daily_transitions),
            sum(1 for v in daily_transitions.values() if v),
            len(detect_records),
        )

        b4_validator = B4TransitionAccuracy()
        b4_report = b4_validator.validate(daily_transitions, events=events_path,
                                          trading_dates=trading_dates)
        _logger.info("B4: %s", b4_report.summary)

        # ── 第二批：A2 + B1 ──
        a2_report: A2Report | None = None
        b1_report: B1Report | None = None
        if run_second_batch:
            # A2: IS/OOS 交叉解码一致率
            a2_report = self._run_a2(features, feature_names, is_oos_split)
            # B1: 概率校准度（detect_records + 后续收益）
            b1_report = self._run_b1(builder, detect_records, b1_forward_days)

        # ── 综合 ──
        a1_ok = a1_report.overall in (A1Overall.PASS, A1Overall.REVIEW)
        b4_ok = b4_report.verdict is B4Verdict.PASS
        overall_pass = a1_ok and b4_ok and not a1_report.degraded
        parts = [
            f"A1={a1_report.overall.value}",
            f"B4={b4_report.verdict.value} ({b4_report.hit_count}/{b4_report.total_evaluated})",
        ]
        if a2_report is not None:
            parts.append(f"A2={a2_report.verdict.value} (OOS/IS={a2_report.ratio:.3f})")
            a2_ok = a2_report.verdict in (A2Verdict.PASS, A2Verdict.REVIEW) and not a2_report.degraded
            overall_pass = overall_pass and a2_ok
        if b1_report is not None:
            parts.append(f"B1={b1_report.verdict.value} (err={b1_report.calibration_error:.1%})")
            b1_ok = b1_report.verdict in (B1Verdict.PASS, B1Verdict.REVIEW) and not b1_report.degraded
            overall_pass = overall_pass and b1_ok
        summary = f"Phase 2: {', '.join(parts)} → {'PASS' if overall_pass else '需复核'}"
        _logger.info("Phase 2 完成: %s", summary)
        return Phase2Report(
            a1=a1_report,
            b4=b4_report,
            overall_pass=overall_pass,
            summary=summary,
            a2=a2_report,
            b1=b1_report,
        )

    def _run_a2(
        self,
        features: pd.DataFrame,
        feature_names: list[str],
        is_oos_split: str,
    ) -> A2Report | None:
        """运行 A2 过拟合验证（IS/OOS 交叉解码一致率）。

        Args:
            features: 全历史特征 DataFrame。
            feature_names: 特征列名。
            is_oos_split: IS/OOS 分割日期字符串（IS ≤ 此日 < OOS）。

        Returns:
            A2Report，失败返回 None。
        """
        _logger.info("Phase2 A2: IS/OOS 交叉解码一致率...")
        try:
            split_ts = pd.Timestamp(is_oos_split)
            # 取 ≤ split_ts 的最后位置作为 IS 末尾（IS = X[:is_end_idx]）
            is_mask = features.index <= split_ts
            if not is_mask.any():
                _logger.warning("A2: IS 段为空（split=%s 超出特征范围），跳过", is_oos_split)
                return None
            is_end_idx = int(is_mask.sum())
            X_full = features[feature_names].to_numpy(dtype=float)
            a2_validator = A2HmmOverfitting(hmm_params=self.hmm_params)
            a2_report = a2_validator.validate(X_full, is_end_idx=is_end_idx, standardize=True)
            _logger.info("A2: %s", a2_report.summary)
            return a2_report
        except Exception as exc:
            _logger.warning("A2 验证异常，跳过: %s", exc)
            return None

    def _run_b1(
        self,
        builder: Any,
        detect_records: list[dict[str, Any]],
        forward_days: int,
    ) -> B1Report | None:
        """运行 B1 概率校准度验证（后续收益实现代理标签）。

        Args:
            builder: RegimeFeatureBuilder 实例（取 index close 算 forward return）。
            detect_records: walk-forward 收集的 [{timestamp, confidence, dominant_regime}]。
            forward_days: 后续收益天数。

        Returns:
            B1Report，失败返回 None。
        """
        _logger.info("Phase2 B1: 概率校准度（后续收益实现代理标签）...")
        if not detect_records:
            _logger.warning("B1: detect_records 为空，跳过")
            return None
        try:
            close = self._get_index_close(builder)
            if close is None or close.empty:
                _logger.warning("B1: 无法获取 index close，跳过")
                return None
            b1_validator = B1ProbabilityCalibration()
            b1_report = b1_validator.validate(detect_records, close, forward_days=forward_days)
            _logger.info("B1: %s", b1_report.summary)
            return b1_report
        except Exception as exc:
            _logger.warning("B1 验证异常，跳过: %s", exc)
            return None

    @staticmethod
    def _get_index_close(builder: Any) -> pd.Series | None:
        """从 builder 获取 market_proxy 的 close 序列（B1 forward return 用）。"""
        try:
            kline = builder.get_index_kline()
            if kline is None or kline.empty:
                return None
            proxy = builder.market_proxy
            # 兼容 MultiIndex (symbol, date) 和单层 date index
            if isinstance(kline.index, pd.MultiIndex):
                try:
                    proxy_df = kline.xs(proxy, level="symbol")
                except KeyError:
                    return None
            else:
                proxy_df = kline[kline.index.get_level_values("symbol") == proxy] if "symbol" in kline.index.names else kline
            close = proxy_df["close"].astype(float).sort_index()
            close = close[~close.index.duplicated(keep="last")]
            return close
        except Exception as exc:
            _logger.warning("获取 index close 失败: %s", exc)
            return None

    # ── 内部：walk-forward detect 收集 _last_transitions ─────────────

    def _collect_daily_transitions(
        self,
        builder: Any,
        features: pd.DataFrame,
        feature_names: list[str],
        train_years: int,
        detect_window: int,
        refit_freq: str,
    ) -> tuple[dict[pd.Timestamp, list[Any]], list[pd.Timestamp], list[dict[str, Any]]]:
        """复刻 build_shrinkage_schedule 的 walk-forward detect 循环，但收集 _last_transitions.

        与 build_shrinkage_schedule 严格对齐：
          - PIT shift(1)
          - 季度 refit + RobustScaler（每季 fit on train）
          - trailing detect_window 窗口
          - overlay_signals / risk_inputs 构造器复用 builder 的 _risk_ctor / _overlay_ctor

        Returns:
            (daily_transitions, trading_dates, detect_records)
            daily_transitions: {date: list[TransitionTriggered]}
            trading_dates: 排序的交易日列表
            detect_records: [{timestamp, confidence, dominant_regime}] 供 B1 用
        """
        from zephyr.regime.core.regime_detector import RegimeDetector

        features_shifted = features.shift(1)  # PIT

        # 触发 builder 惰性构造 risk/overlay 构造器（与 build_shrinkage_schedule 一致）
        self._ensure_constructors(builder)

        # 季度边界
        quarter_ends = _quarter_end_dates(
            pd.Timestamp(builder.data_load_start) + pd.DateOffset(years=train_years),
            pd.Timestamp(builder.backtest_end),
            freq=refit_freq,
        )
        if not quarter_ends:
            raise Phase2RunnerError(
                f"walk-forward 无可用季度边界（data_load_start={builder.data_load_start}, "
                f"train_years={train_years}, backtest_end={builder.backtest_end}）"
            )

        detector = RegimeDetector(shrinkage_enabled=True, hmm_params=self.hmm_params)
        daily_transitions: dict[pd.Timestamp, list[Any]] = {}
        all_trading_dates: list[pd.Timestamp] = []
        detect_records: list[dict[str, Any]] = []  # B1 用

        for i, q in enumerate(quarter_ends):
            train_start = (q - pd.DateOffset(years=train_years)).strftime("%Y-%m-%d")
            train_end = q.strftime("%Y-%m-%d")
            scaler = None
            try:
                train_matrix = builder.build_train_matrix(train_start, train_end)
                X_train = train_matrix["X"]
                if getattr(builder, "standardize_features", False) and RobustScaler is not None:
                    scaler = RobustScaler().fit(X_train)
                    X_train = scaler.transform(X_train)
                detector.fit({"X": X_train, "lengths": train_matrix.get("lengths")})
                _logger.info("Phase2 walk-forward fit Q%d [%s, %s] OK", i + 1, train_start, train_end)
            except Exception as exc:
                _logger.warning(
                    "Phase2 walk-forward fit Q%d [%s, %s] 失败，本季降级: %s",
                    i + 1, train_start, train_end, exc,
                )

            next_q = (
                quarter_ends[i + 1]
                if i + 1 < len(quarter_ends)
                else pd.Timestamp(builder.backtest_end)
            )
            detect_start = max(q + pd.Timedelta(days=1), pd.Timestamp(builder.backtest_start))
            detect_end = min(next_q, pd.Timestamp(builder.backtest_end))
            if detect_start > detect_end:
                continue

            period = features_shifted.loc[detect_start:detect_end]
            for dt, _row in period.iterrows():
                window = features_shifted.loc[:dt].iloc[-detect_window:]
                if len(window) < 10 or window.dropna().empty:
                    daily_transitions[dt] = []
                    all_trading_dates.append(dt)
                    continue

                risk_inputs, overlay_signals = self._build_signals(builder, dt, window)
                X = window[feature_names].to_numpy(dtype=float)
                X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
                if scaler is not None:
                    X = scaler.transform(X)
                try:
                    probs, _shrinkage = detector.detect(
                        {"X": X},
                        overlay_signals=overlay_signals,
                        risk_signal_inputs=risk_inputs,
                    )
                    # 核心：读取 detect 后的 _last_transitions（B4 用）
                    daily_transitions[dt] = list(detector._last_transitions)  # noqa: SLF001
                    # B1 用：confidence + dominant_regime
                    detect_records.append({
                        "timestamp": dt,
                        "confidence": float(getattr(probs, "confidence", 0.0)),
                        "dominant_regime": str(getattr(probs, "dominant_regime", "")),
                    })
                except Exception as exc:
                    _logger.warning("Phase2 detect 异常 (date=%s): %s", dt, exc)
                    daily_transitions[dt] = []
                all_trading_dates.append(dt)

        return daily_transitions, sorted(set(all_trading_dates)), detect_records

    @staticmethod
    def _ensure_constructors(builder: Any) -> None:
        """触发 builder 惰性构造 risk/overlay 构造器（复刻 build_shrinkage_schedule 逻辑）."""
        if getattr(builder, "enable_full_risk", False) and builder._risk_ctor is None:  # noqa: SLF001
            from zephyr.regime.risk_signal_builder import RiskSignalConstructor
            builder._risk_ctor = RiskSignalConstructor(  # noqa: SLF001
                backtest_start=builder.backtest_start,
                backtest_end=builder.backtest_end,
                data_load_start=builder.data_load_start,
                feature_builder=builder,
                market_proxy=builder.market_proxy,
            )
            _logger.info("Phase2: 启用 RiskSignalConstructor")
        if getattr(builder, "enable_overlay", False) and builder._overlay_ctor is None:  # noqa: SLF001
            try:
                from zephyr.regime.overlay_signals_builder import OverlaySignalsConstructor
                builder._overlay_ctor = OverlaySignalsConstructor(  # noqa: SLF001
                    backtest_start=builder.backtest_start,
                    backtest_end=builder.backtest_end,
                    data_load_start=builder.data_load_start,
                    feature_builder=builder,
                    risk_constructor=builder._risk_ctor,  # noqa: SLF001
                    market_proxy=builder.market_proxy,
                )
                _logger.info("Phase2: 启用 OverlaySignalsConstructor")
            except Exception as exc:
                _logger.warning("Phase2: OverlaySignalsConstructor 不可用，降级 overlay={}: %s", exc)
                builder._overlay_ctor = None  # noqa: SLF001

    @staticmethod
    def _build_signals(
        builder: Any,
        dt: pd.Timestamp,
        window: pd.DataFrame,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """构造 detect 所需的 risk_inputs + overlay_signals（复刻 build_shrinkage_schedule）."""
        risk_ctor = getattr(builder, "_risk_ctor", None)  # noqa: SLF001
        if risk_ctor is not None:
            risk_inputs = risk_ctor.build_for_date(dt)
        else:
            last_row = window.iloc[-1]
            risk_inputs = builder._build_feature_risk(  # noqa: SLF001
                vol_pct=_safe_float(last_row.get("realized_vol_pct")),
                slope=_safe_float(last_row.get("kalman_slope")),
                vol_anom=_safe_float(last_row.get("volume_anomaly")),
            )
        overlay_ctor = getattr(builder, "_overlay_ctor", None)  # noqa: SLF001
        overlay_signals = (
            overlay_ctor.build_for_date(dt) if overlay_ctor is not None else {}
        )
        return risk_inputs, overlay_signals


# ── 模块级工具函数 ────────────────────────────────────────────────────


def _get_feature_names(builder: Any) -> list[str]:
    """从 builder 获取 FEATURE_NAMES（兼容 builder.feature_names / 模块常量）."""
    names = getattr(builder, "feature_names", None)
    if names is not None:
        return list(names)
    # fallback: 从 builder 所在模块导入
    from zephyr.regime.regime_feature_builder import FEATURE_NAMES
    return list(FEATURE_NAMES)


def _quarter_end_dates(
    start: pd.Timestamp, end: pd.Timestamp, freq: str = "QE",
) -> list[pd.Timestamp]:
    """生成 [start, end] 内的季度末日列表（复刻 builder._quarter_end_dates）."""
    return list(pd.date_range(start=start, end=end, freq=freq))


def _safe_float(v: Any) -> float:
    """NaN/None 安全转 float."""
    if v is None:
        return 0.0
    try:
        f = float(v)
        return 0.0 if f != f else f
    except (TypeError, ValueError):
        return 0.0


__all__ = ["Phase2Report", "Phase2Runner", "Phase2RunnerError"]
