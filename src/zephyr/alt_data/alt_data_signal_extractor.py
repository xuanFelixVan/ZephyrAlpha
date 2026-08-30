# [BLUEPRINT] MOD-ALT-013 | docs/03_modules/_domain_alt_data/alt_data_signal_extractor/blueprint.md
# [MODULE] zephyr.alt_data.alt_data_signal_extractor
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] 无（协议核心纯内存；ic计算器/回归器/CTR-002产出校验器/时钟全注入，复用 ctr002_producer_validator 语义不 import）
# [CONSUMERS] 运行时装配批（另类数据因子统一输出网关接信号族 / 校验器接 shared/contracts/ctr002_producer_validator）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 协议核心纯内存无IO；特征注册表 feature_id 唯一；IC 恒经注入计算器且须∈[-1,1]（越界即计算器违约 Fail-Closed）；衰减权重=0.5**(age/half_life) 恒∈(0,1]；正交化强制注入回归器取残差（未注入 Fail-Closed 不旁路）；emit 唯一出口且恒过注入校验器（拒绝即 Fail-Closed 不出伪信号）；输出 values 按键确定性排序；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_alt_data/alt_data_signal_extractor/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AltSignalExtractorError(占位 ZA-ALT-UNREGISTERED-SIGNAL-EXTRACTOR)——ic计算器未注入/特征空白或重复/半衰期非正/样本长度不齐/样本不足/IC越界/负age/回归器未注入/代理变量空或长度不齐/残差长度违约/校验器未注入或拒绝时抛
# [TESTS] tests/alt_data/test_alt_data_signal_extractor.py
# [A_module] module_id=MOD-ALT-013 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
AltDataSignalExtractor — 另类数据信号提取网关（MOD-ALT-013）。

B5-07085（AUD-DRAFT-001-DIGEST P2 波 P2-W04，CAND-TESTA-023，B5
D-ALT-DATA-05）：另类数据信号**唯一输出网关**——特征工程（**特征注册表**）
+ **IC 测试**（注入 ic 计算器，∈[-1,1] 闭合校验）+ **衰减分析**
（0.5**(age/half_life) 半衰期权重）+ **正交化**（对行业/市值代理变量回归
取残差，注入回归器，未注入 Fail-Closed）+ 统一 **CTR-002 FactorSignal
兼容输出**（注入产出校验器，拒绝即 Fail-Closed 不出伪信号）。
alphalens/Barra 思想单机版。

查重分工（蓝图 §0）：shared/contracts/ctr002_producer_validator=CTR-002
产出契约校验实现（本件经注入委托，不 import 不重建）；alphalens=全量
分层回测框架（本件仅 IC/衰减/正交三判定面）；本件不做因子计算本身
（原始特征在采集族），仅做注册、检验与统一出口。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: ic_calculator 参数
#   fields: 参数 ic_calculator（无注解）
#   code: alt_data_signal_extractor.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: ic_threshold 参数
#   fields: 参数 ic_threshold（无注解）
#   code: alt_data_signal_extractor.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: regressor 参数
#   fields: 参数 regressor（无注解）
#   code: alt_data_signal_extractor.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: validator 参数
#   fields: 参数 validator（无注解）
#   code: alt_data_signal_extractor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AltDataSignalExtractor
#   name_en: AltDataSignalExtractor
#   intro: 另类数据信号提取网关（注册表 + IC + 衰减 + 正交化 + CTR-002 出口）。
#   desc: 另类数据信号提取网关（注册表 + IC + 衰减 + 正交化 + CTR-002 出口）。；公共方法（定义序）: register_feature, features, test_ic, decay_weight, a…
#   inputs: ic_calculator ic_threshold regressor validator clock
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: AltDataSignalExtractor
#   downstream: 运行时装配批（另类数据因子统一输出网关接信号族 / 校验器接 shared/contracts/ctr002_producer_validator）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "AltDataSignalExtractor",
    "AltSignalExtractorError",
    "FeatureDefinition",
    "ICTestResult",
]

#: IC 计算器签名：(factor_values, forward_returns) -> ic ∈ [-1, 1]
IcCalculator = Callable[[Sequence[float], Sequence[float]], float]

#: 回归器签名：(target, proxies) -> residuals（与 target 等长）
Regressor = Callable[[Sequence[float], Mapping[str, Sequence[float]]], Sequence[float]]

#: CTR-002 产出校验器签名：signal -> True 放行 / False 拒绝
SignalValidator = Callable[[Mapping[str, object]], bool]


class AltSignalExtractorError(Exception):
    """信号提取协议输入/配置非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-ALT-UNREGISTERED-SIGNAL-EXTRACTOR。
    """


@dataclass(frozen=True)
class FeatureDefinition:
    """特征注册表条目（frozen）。"""

    feature_id: str
    description: str
    half_life_days: float


@dataclass(frozen=True)
class ICTestResult:
    """IC 测试报告（frozen）。"""

    feature_id: str
    ic: float
    passed: bool
    sample_size: int


class AltDataSignalExtractor:
    """另类数据信号提取网关（注册表 + IC + 衰减 + 正交化 + CTR-002 出口）。"""

    def __init__(
        self,
        *,
        ic_calculator: IcCalculator | None,
        ic_threshold: float = 0.03,
        regressor: Regressor | None = None,
        validator: SignalValidator | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if ic_calculator is None:
            raise AltSignalExtractorError("ic_calculator 未注入（IC 测试强制注入，禁止旁路）")
        if not 0.0 <= ic_threshold <= 1.0:
            raise AltSignalExtractorError(f"ic_threshold 越界: {ic_threshold!r}（须∈[0,1]）")
        self._ic_calculator = ic_calculator
        self._ic_threshold = ic_threshold
        self._regressor = regressor
        self._validator = validator
        self._clock = clock or datetime.datetime.now
        self._features: dict[str, FeatureDefinition] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _feature_of(self, feature_id: str) -> FeatureDefinition:
        feat = self._features.get(feature_id)
        if feat is None:
            raise AltSignalExtractorError(f"未知特征: {feature_id!r}（未注册）")
        return feat

    @staticmethod
    def _as_floats(values: Sequence[float], name: str) -> tuple[float, ...]:
        try:
            return tuple(float(v) for v in values)
        except (TypeError, ValueError) as exc:
            raise AltSignalExtractorError(f"{name} 含非数值: {exc}") from exc

    # ── 特征注册表 ──────────────────────────────────────────────────────────

    def register_feature(
        self,
        feature_id: str,
        *,
        description: str = "",
        half_life_days: float,
    ) -> FeatureDefinition:
        """注册特征（feature_id 唯一；half_life_days 须为正）。"""
        if not feature_id or not feature_id.strip():
            raise AltSignalExtractorError("feature_id 空白")
        if feature_id in self._features:
            raise AltSignalExtractorError(f"feature_id 重复: {feature_id!r}")
        if half_life_days <= 0:
            raise AltSignalExtractorError(f"half_life_days 非正: {half_life_days!r}")
        feat = FeatureDefinition(feature_id=feature_id, description=description, half_life_days=float(half_life_days))
        self._features[feature_id] = feat
        return feat

    def features(self) -> tuple[FeatureDefinition, ...]:
        """注册表视图（按 feature_id 确定性排序）。"""
        return tuple(self._features[k] for k in sorted(self._features))

    # ── IC 测试（注入计算器） ───────────────────────────────────────────────

    def test_ic(
        self,
        feature_id: str,
        factor_values: Sequence[float],
        forward_returns: Sequence[float],
    ) -> ICTestResult:
        """IC 测试：等长样本 ≥2 → 注入计算器 → |ic|≥threshold 为通过。"""
        self._feature_of(feature_id)
        fv = self._as_floats(factor_values, "factor_values")
        fr = self._as_floats(forward_returns, "forward_returns")
        if len(fv) != len(fr):
            raise AltSignalExtractorError(f"样本长度不齐: factor={len(fv)} vs returns={len(fr)}")
        if len(fv) < 2:
            raise AltSignalExtractorError(f"样本不足: {len(fv)}（须≥2）")
        try:
            ic = float(self._ic_calculator(fv, fr))
        except AltSignalExtractorError:
            raise
        except Exception as exc:  # noqa: BLE001 — 计算器违约 Fail-Closed
            raise AltSignalExtractorError(f"ic_calculator 执行异常: {exc}") from exc
        if not -1.0 <= ic <= 1.0:
            raise AltSignalExtractorError(f"IC 越界: {ic!r}（计算器违约，须∈[-1,1]）")
        return ICTestResult(
            feature_id=feature_id,
            ic=ic,
            passed=abs(ic) >= self._ic_threshold,
            sample_size=len(fv),
        )

    # ── 衰减分析 ──────────────────────────────────────────────────────────

    def decay_weight(self, feature_id: str, age_days: float) -> float:
        """单点衰减权重：0.5**(age/half_life)，恒∈(0,1]。"""
        feat = self._feature_of(feature_id)
        if age_days < 0:
            raise AltSignalExtractorError(f"age_days 为负: {age_days!r}")
        return 0.5 ** (age_days / feat.half_life_days)

    def analyze_decay(self, feature_id: str, ages_days: Sequence[float]) -> tuple[float, ...]:
        """批量衰减分析（与输入同序）。"""
        self._feature_of(feature_id)
        ages = self._as_floats(ages_days, "ages_days")
        return tuple(self.decay_weight(feature_id, age) for age in ages)

    # ── 正交化（行业/市值代理回归取残差，注入回归器） ──────────────────────

    def orthogonalize(
        self,
        feature_id: str,
        factor_values: Sequence[float],
        proxies: Mapping[str, Sequence[float]],
    ) -> tuple[float, ...]:
        """正交化：对行业/市值代理变量回归取残差（未注入回归器 Fail-Closed）。"""
        self._feature_of(feature_id)
        if self._regressor is None:
            raise AltSignalExtractorError("regressor 未注入（正交化强制注入回归器，禁止旁路）")
        fv = self._as_floats(factor_values, "factor_values")
        if not proxies:
            raise AltSignalExtractorError("proxies 为空（正交化须至少一个代理变量）")
        clean_proxies: dict[str, tuple[float, ...]] = {}
        for name, series in sorted(proxies.items()):
            if not name or not str(name).strip():
                raise AltSignalExtractorError("代理变量名空白")
            vals = self._as_floats(series, f"proxies[{name!r}]")
            if len(vals) != len(fv):
                raise AltSignalExtractorError(f"代理变量 {name!r} 长度不齐: {len(vals)} vs factor={len(fv)}")
            clean_proxies[name] = vals
        try:
            residuals = tuple(float(r) for r in self._regressor(fv, clean_proxies))
        except AltSignalExtractorError:
            raise
        except Exception as exc:  # noqa: BLE001 — 回归器违约 Fail-Closed
            raise AltSignalExtractorError(f"regressor 执行异常: {exc}") from exc
        if len(residuals) != len(fv):
            raise AltSignalExtractorError(f"残差长度违约: {len(residuals)} vs factor={len(fv)}")
        return residuals

    # ── 统一 CTR-002 兼容输出（注入校验器） ─────────────────────────────────

    def emit_signal(
        self,
        feature_id: str,
        values: Mapping[str, float],
        *,
        as_of: datetime.datetime,
        ic: float | None = None,
    ) -> dict[str, object]:
        """唯一信号出口：CTR-002 FactorSignal 兼容载荷，过注入校验器方可出网。"""
        self._feature_of(feature_id)
        if self._validator is None:
            raise AltSignalExtractorError("validator 未注入（CTR-002 出口强制校验，禁止旁路）")
        if not values:
            raise AltSignalExtractorError("values 为空（无截面取值不可发信号）")
        if as_of > self._clock():
            raise AltSignalExtractorError(f"as_of 晚于当前时钟（未来信号）: {as_of!r}")
        if ic is not None and not -1.0 <= ic <= 1.0:
            raise AltSignalExtractorError(f"ic 越界: {ic!r}（须∈[-1,1]）")
        clean_values: dict[str, float] = {}
        for symbol, val in sorted(values.items()):
            if not symbol or not str(symbol).strip():
                raise AltSignalExtractorError("标的代码空白")
            try:
                clean_values[str(symbol)] = float(val)
            except (TypeError, ValueError) as exc:
                raise AltSignalExtractorError(f"标的 {symbol!r} 取值非数值: {exc}") from exc
        signal: dict[str, object] = {
            "contract": "CTR-002",
            "factor_id": feature_id,
            "source_domain": "alt_data",
            "values": clean_values,
            "as_of": as_of.isoformat(),
            "ic": ic,
            "advisory": True,
        }
        try:
            ok = bool(self._validator(signal))
        except Exception as exc:  # noqa: BLE001 — 校验器违约 Fail-Closed
            raise AltSignalExtractorError(f"validator 执行异常: {exc}") from exc
        if not ok:
            raise AltSignalExtractorError(f"CTR-002 校验拒绝: feature {feature_id!r}（Fail-Closed 不出伪信号）")
        _log.info("另类数据信号出网: %s（%d 标的）", feature_id, len(clean_values))
        return signal
