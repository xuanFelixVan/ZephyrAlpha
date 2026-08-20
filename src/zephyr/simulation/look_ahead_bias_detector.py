# [BLUEPRINT] MOD-SIM-022 | docs/03_modules/_domain_simulation/look_ahead_bias_detector/blueprint.md
# [MODULE] zephyr.simulation.look_ahead_bias_detector
# [DOMAIN] D_SIMULATION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.simulation.strategy_simulator; zephyr.simulation.result_analyzer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] DetectorConfig/BiasIssue/DetectionResult frozen不可变; issues按严重度降序; is_clean==(total_issues==0); 截断重算采样点+tolerance; 依赖pandas
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SimulationError(ZA-SIM-0022)
# [TESTS] tests/simulation/test_look_ahead_bias_detector.py
# [A_module] module_id=MOD-SIM-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_SIMULATION — Look-Ahead Bias Detector (未来函数风险检测器)

检测回测中的 look-ahead bias(前瞻偏差), 确保所有判断仅基于当时已知数据。
扫描特征矩阵(列名/尾部NaN/标签泄露/时间戳单调性) + 截断重算验证特征函数,
产出偏差清单 + 严重度评估 + 审计摘要。

属 A 类基础设施(确定性数据扫描), 纯基础层不涉及策略。

设计真源: depgraph MOD-SIM-022
蓝图: docs/03_modules/_domain_simulation/look_ahead_bias_detector/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 特征矩阵 df（pandas DataFrame）
#   fields: 特征列(数值) + 标签列label_column + 时间戳列timestamp_column
#   code: scan(df, feature_columns, label_column, timestamp_column) L191
# - id: I2
#   name: 特征函数与完整数据
#   fields: func(接受list返回可索引序列) + data完整输入数据
#   code: validate_function(func, data) L393
# - id: I3
#   name: 检测器配置 DetectorConfig
#   fields: 前瞻列名模式(_fwd/_forward/_future/_lead/_next) + 目标列名模式(_target/_label/_y) + 截断采样点10 + 容差1e-9
#   code: DetectorConfig L77
# 层: 算法
# - id: A1
#   name_zh: ① 特征矩阵扫描
#   name_en: LookAheadBiasDetector.scan
#   intro: 对特征DataFrame做4项静态扫描揪出疑似未来数据
#   desc: ①列名子串匹配前瞻/目标模式(MEDIUM/HIGH) ②标签列混入特征列=标签泄露(CRITICAL) ③尾部连续NaN且前部干净=疑似shift(-K)前瞻窗口(HIGH) ④时间戳非严格单调/重复(MEDIUM)
#   inputs: I1 I3
#   outputs: BiasIssue清单
# - id: A2
#   name_zh: ② 截断重算验证（金标准）
#   name_en: validate_function
#   intro: 用截断数据重算特征函数，与全样本值不一致即证明用了未来数据
#   desc: 自动均匀采样测试点 → 逐点截断data[:idx+1]重算 → |全样本值-截断值|>容差1e-9即报TRUNCATION_MISMATCH(CRITICAL)，一处不一致即停
#   inputs: I2 I3
#   outputs: BiasIssue清单
# - id: A3
#   name_zh: ③ 检测结果汇总
#   name_en: _build_result
#   intro: 偏差清单按严重度降序排序并统计出不可变结果
#   desc: 按CRITICAL>HIGH>MEDIUM>LOW排序 → 统计total/critical/max_severity → is_clean=(总数==0)
#   inputs: A1 A2
#   outputs: DetectionResult
#   invariant: issues按严重度降序；is_clean==(total_issues==0)
# - id: A4
#   name_zh: ④ 审计摘要生成
#   name_en: audit_summary
#   intro: 把检测结果格式化成PASS/FAIL结论+逐条偏差证据的文本
#   desc: 结论行+统计行+按严重度降序的偏差清单(类型/列/描述/证据)
#   inputs: A3
#   outputs: 审计摘要字符串
# 层: 输出
# - id: O1
#   name_zh: 前瞻偏差检测结果 DetectionResult
#   name_en: DetectionResult
#   intro: 含排序后偏差清单/是否干净/CRITICAL计数/最高严重度的不可变结果
#   invariant: frozen不可变；is_clean==(total_issues==0)
#   downstream: zephyr.simulation.strategy_simulator; zephyr.simulation.result_analyzer（[CONSUMERS]）
# - id: O2
#   name_zh: 审计摘要文本
#   name_en: audit summary str
#   intro: 人类可读的检测审计报告（结论+统计+证据清单）
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I3 --> A1
# I2 --> A2
# I3 --> A2
# A1 --> A3
# A2 --> A3
# A3 --> O1
# A3 --> A4
# A4 --> O2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable

from zephyr.shared.foundation.errors import ZephyrBaseError

if TYPE_CHECKING:
    import pandas as pd

_logger = logging.getLogger(__name__)


class SimulationError(ZephyrBaseError):
    """仿真检测异常——输入非法。"""

    error_code = "ZA-SIM-0022"


class BiasType(str, Enum):
    """前瞻偏差类型。"""

    FORWARD_COLUMN_NAME = "forward_column_name"  # 前瞻列名
    LABEL_LEAKAGE = "label_leakage"  # 标签泄露
    FUTURE_SHIFT = "future_shift"  # 尾部NaN(前瞻窗口)
    TRUNCATION_MISMATCH = "truncation_mismatch"  # 截断重算不一致
    NON_MONOTONIC_TIMESTAMP = "non_monotonic_timestamp"  # 时间戳非单调


class BiasSeverity(str, Enum):
    """偏差严重度(降序: CRITICAL > HIGH > MEDIUM > LOW)。"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


_SEVERITY_ORDER: dict[BiasSeverity, int] = {
    BiasSeverity.CRITICAL: 4,
    BiasSeverity.HIGH: 3,
    BiasSeverity.MEDIUM: 2,
    BiasSeverity.LOW: 1,
}


@dataclass(frozen=True)
class DetectorConfig:
    """检测器配置——不可变。

    Attributes:
        forward_name_patterns: 前瞻列名匹配模式(子串匹配)。
        target_name_patterns: 目标/标签列名匹配模式。
        truncation_test_points: 截断重算采样点数(控制 O(n²) 成本)。
        truncation_tolerance: 截断重算浮点相等容差。
    """

    forward_name_patterns: tuple[str, ...] = (
        "_fwd",
        "_forward",
        "_future",
        "_lead",
        "_next",
    )
    target_name_patterns: tuple[str, ...] = ("_target", "_label", "_y")
    truncation_test_points: int = 10
    truncation_tolerance: float = 1e-9


@dataclass(frozen=True)
class BiasIssue:
    """单条偏差记录——不可变。

    Attributes:
        bias_type: 偏差类型。
        severity: 严重度。
        column: 涉及列名(无具体列时为 None)。
        description: 人类可读描述。
        evidence: 具体证据(数值/位置等)。
    """

    bias_type: BiasType
    severity: BiasSeverity
    column: str | None
    description: str
    evidence: str


@dataclass(frozen=True)
class DetectionResult:
    """检测结果——不可变。

    Attributes:
        issues: 偏差清单(按严重度降序)。
        is_clean: 是否无偏差(== total_issues==0)。
        total_issues: 偏差总数。
        critical_count: CRITICAL 级偏差数。
        max_severity: 最高严重度(空清单为 None)。
    """

    issues: list[BiasIssue] = field(default_factory=list)
    is_clean: bool = True
    total_issues: int = 0
    critical_count: int = 0
    max_severity: BiasSeverity | None = None


def _build_result(issues: list[BiasIssue]) -> DetectionResult:
    """从偏差清单构建不可变结果(排序 + 统计)。"""
    ordered = sorted(issues, key=lambda x: _SEVERITY_ORDER[x.severity], reverse=True)
    critical = sum(1 for i in ordered if i.severity == BiasSeverity.CRITICAL)
    max_sev = ordered[0].severity if ordered else None
    return DetectionResult(
        issues=ordered,
        is_clean=(len(ordered) == 0),
        total_issues=len(ordered),
        critical_count=critical,
        max_severity=max_sev,
    )


class LookAheadBiasDetector:
    """未来函数风险检测器——回测 look-ahead bias 扫描与验证。

    两类检测:
      1. scan(): 扫描特征 DataFrame(列名/尾部NaN/标签泄露/时间戳)
      2. validate_function(): 截断重算验证特征函数(金标准)

    Usage:
        detector = LookAheadBiasDetector()

        # 扫描特征矩阵
        result = detector.scan(df, feature_columns=["ma5","rsi"], label_column="ret_fwd")
        if not result.is_clean:
            for issue in result.issues:
                print(issue.severity, issue.bias_type, issue.description)

        # 验证特征函数(截断重算)
        result = detector.validate_function(
            func=lambda d: [sum(d[:i+1])/(i+1) for i in range(len(d))],
            data=returns,
        )

        # 审计摘要
        print(detector.audit_summary(result))
    """

    def __init__(self, config: DetectorConfig | None = None) -> None:
        self._config = config if config is not None else DetectorConfig()

    @property
    def config(self) -> DetectorConfig:
        """配置(只读)。"""
        return self._config

    # ------------------------------------------------------------------
    # scan: 特征矩阵扫描
    # ------------------------------------------------------------------
    def scan(
        self,
        df: pd.DataFrame,
        feature_columns: list[str] | None = None,
        label_column: str | None = None,
        timestamp_column: str | None = None,
    ) -> DetectionResult:
        """扫描特征 DataFrame 检测前瞻偏差。

        Args:
            df: 特征 DataFrame(pandas)。
            feature_columns: 特征列名, None=全部数值列。
            label_column: 标签/目标列名。
            timestamp_column: 时间戳列名(用于单调性检查)。

        Returns:
            DetectionResult

        Raises:
            SimulationError: df 为空 / 列不存在。
        """
        try:
            import pandas as pd
        except ImportError as e:  # pragma: no cover - pandas 是项目核心依赖
            raise SimulationError("pandas 未安装") from e

        if df is None or len(df) == 0:
            raise SimulationError("df 不能为空")

        if feature_columns is None:
            feature_columns = [
                c
                for c in df.columns
                if c != label_column and c != timestamp_column and pd.api.types.is_numeric_dtype(df[c])
            ]

        # 列存在性校验
        all_cols = set(feature_columns)
        if label_column:
            all_cols.add(label_column)
        if timestamp_column:
            all_cols.add(timestamp_column)
        missing = [c for c in all_cols if c not in df.columns]
        if missing:
            raise SimulationError(
                f"列不存在: {missing}",
                details={"missing": missing},
            )

        issues: list[BiasIssue] = []

        # 1. 列名扫描
        issues.extend(self._scan_column_names(feature_columns, label_column))

        # 2. 标签泄露
        if label_column and label_column in feature_columns:
            issues.append(
                BiasIssue(
                    bias_type=BiasType.LABEL_LEAKAGE,
                    severity=BiasSeverity.CRITICAL,
                    column=label_column,
                    description=f"标签列 '{label_column}' 同时出现在特征列中",
                    evidence=f"feature_columns 含 '{label_column}'",
                )
            )

        # 3. 尾部 NaN 检测
        for col in feature_columns:
            issue = self._detect_trailing_nan(df, col)
            if issue is not None:
                issues.append(issue)

        # 4. 时间戳单调性
        if timestamp_column:
            issue = self._check_timestamp_monotonic(df, timestamp_column)
            if issue is not None:
                issues.append(issue)

        result = _build_result(issues)
        _logger.debug(
            "Look-ahead扫描: clean=%s issues=%d critical=%d",
            result.is_clean,
            result.total_issues,
            result.critical_count,
        )
        return result

    def _scan_column_names(self, feature_columns: list[str], label_column: str | None) -> list[BiasIssue]:
        """按列名模式扫描前瞻特征。"""
        issues: list[BiasIssue] = []
        lowered_targets = tuple(p.lower() for p in self._config.target_name_patterns)
        lowered_forwards = tuple(p.lower() for p in self._config.forward_name_patterns)
        for col in feature_columns:
            cl = col.lower()
            for pat in lowered_targets:
                if pat in cl:
                    issues.append(
                        BiasIssue(
                            bias_type=BiasType.FORWARD_COLUMN_NAME,
                            severity=BiasSeverity.HIGH,
                            column=col,
                            description=(f"特征列 '{col}' 名称匹配目标模式 '{pat}'——疑似标签/目标泄露"),
                            evidence=f"name='{col}' matches '{pat}'",
                        )
                    )
                    break
            else:
                for pat in lowered_forwards:
                    if pat in cl:
                        issues.append(
                            BiasIssue(
                                bias_type=BiasType.FORWARD_COLUMN_NAME,
                                severity=BiasSeverity.MEDIUM,
                                column=col,
                                description=(f"特征列 '{col}' 名称匹配前瞻模式 '{pat}'——疑似使用未来数据"),
                                evidence=f"name='{col}' matches '{pat}'",
                            )
                        )
                        break
        return issues

    def _detect_trailing_nan(self, df: pd.DataFrame, col: str) -> BiasIssue | None:
        """检测尾部 NaN 模式(前瞻窗口信号)。

        NaN 全部集中在序列末尾(前部干净) → shift(-K) 类前瞻窗口。
        前部含 NaN 的列不触发(常规缺失值)。
        """
        s = df[col]
        nan_mask = s.isna()
        if not nan_mask.any():
            return None
        last_valid = s.last_valid_index()
        if last_valid is None:
            # 全 NaN, 非前瞻信号
            return None
        last_valid_pos = s.index.get_loc(last_valid)
        nan_positions = [i for i, v in enumerate(nan_mask) if v]
        # 所有 NaN 必须在 last_valid 之后(尾部), 且前部完全干净
        trailing = all(p > last_valid_pos for p in nan_positions)
        if not trailing or len(nan_positions) == 0:
            return None
        k = len(nan_positions)
        return BiasIssue(
            bias_type=BiasType.FUTURE_SHIFT,
            severity=BiasSeverity.HIGH,
            column=col,
            description=(f"特征列 '{col}' 末尾 {k} 行连续 NaN(前部干净)——疑似 shift(-{{k}}) 前瞻窗口").format(k=k),
            evidence=f"trailing_nan_count={k}, last_valid_pos={last_valid_pos}",
        )

    def _check_timestamp_monotonic(self, df: pd.DataFrame, timestamp_column: str) -> BiasIssue | None:
        """检查时间戳单调递增(含重复检测)。"""
        ts = df[timestamp_column]
        n = len(ts)
        if n < 2:
            return None
        non_monotonic = 0
        duplicates = 0
        vals = list(ts)
        for i in range(1, n):
            if vals[i] < vals[i - 1]:
                non_monotonic += 1
            elif vals[i] == vals[i - 1]:
                duplicates += 1
        if non_monotonic == 0 and duplicates == 0:
            return None
        parts: list[str] = []
        if non_monotonic:
            parts.append(f"{non_monotonic}处递减")
        if duplicates:
            parts.append(f"{duplicates}处重复")
        return BiasIssue(
            bias_type=BiasType.NON_MONOTONIC_TIMESTAMP,
            severity=BiasSeverity.MEDIUM,
            column=timestamp_column,
            description=(f"时间戳列 '{timestamp_column}' 非严格单调递增: " + ", ".join(parts)),
            evidence=f"non_monotonic={non_monotonic}, duplicates={duplicates}",
        )

    # ------------------------------------------------------------------
    # validate_function: 截断重算验证(金标准)
    # ------------------------------------------------------------------
    def validate_function(
        self,
        func: Callable[[list], Any],
        data: list,
        test_indices: list[int] | None = None,
    ) -> DetectionResult:
        """截断重算验证特征函数是否有前瞻偏差。

        金标准: 若 func 在截断数据上重算的早期值与全样本值不一致,
        则 func 使用了未来数据(前瞻偏差)。

        Args:
            func: 特征函数, 接受 list 返回可索引序列(list/Series)。
            data: 完整输入数据。
            test_indices: 自定义测试点, None=自动采样。

        Returns:
            DetectionResult(CRITICAL=检测到前瞻偏差)

        Raises:
            SimulationError: data 为空 / func 返回长度不匹配。
        """
        if not data:
            raise SimulationError("data 不能为空")

        full_result = list(func(data))
        n = len(data)

        if test_indices is None:
            test_indices = self._sample_indices(n)

        issues: list[BiasIssue] = []
        tol = self._config.truncation_tolerance

        for idx in test_indices:
            if idx <= 0 or idx >= n:
                continue
            if idx >= len(full_result):
                continue
            truncated = data[: idx + 1]
            trunc_result = list(func(truncated))
            if idx >= len(trunc_result):
                continue
            full_val = full_result[idx]
            trunc_val = trunc_result[idx]
            if full_val is None or trunc_val is None:
                continue
            # NaN 检查
            try:
                if full_val != full_val or trunc_val != trunc_val:  # noqa: PLR0124
                    continue
            except TypeError:
                pass
            diff = abs(float(full_val) - float(trunc_val))
            if diff > tol:
                issues.append(
                    BiasIssue(
                        bias_type=BiasType.TRUNCATION_MISMATCH,
                        severity=BiasSeverity.CRITICAL,
                        column=None,
                        description=(f"截断重算不一致: 位置 {idx} 全样本值={full_val} 截断值={trunc_val}"),
                        evidence=(
                            f"diff={diff:.2e} > tolerance={tol} (full[{idx}]={full_val}, trunc[{idx}]={trunc_val})"
                        ),
                    )
                )
                break  # 一处不一致足以证明前瞻偏差

        result = _build_result(issues)
        _logger.debug(
            "截断重算验证: clean=%s test_points=%d",
            result.is_clean,
            len(test_indices),
        )
        return result

    def _sample_indices(self, n: int) -> list[int]:
        """采样测试点(均匀分布在 [1, n-1])。"""
        k = self._config.truncation_test_points
        if n <= 2:
            return [1] if n > 1 else []
        if n - 1 <= k:
            return list(range(1, n))
        return [int(round(i * (n - 1) / (k + 1))) for i in range(1, k + 1)]

    # ------------------------------------------------------------------
    # audit_summary: 审计摘要
    # ------------------------------------------------------------------
    def audit_summary(self, result: DetectionResult) -> str:
        """生成审计摘要文本。

        Args:
            result: 检测结果。

        Returns:
            审计摘要字符串(含统计 + 逐条偏差清单)。
        """
        lines: list[str] = []
        lines.append("=== Look-Ahead Bias 检测审计 ===")
        verdict = "PASS(无前瞻偏差)" if result.is_clean else "FAIL(检出前瞻偏差)"
        lines.append(f"结论: {verdict}")
        lines.append(
            f"偏差总数: {result.total_issues} | CRITICAL: {result.critical_count} "
            f"| 最高严重度: {result.max_severity.value if result.max_severity else 'N/A'}"
        )
        if result.issues:
            lines.append("")
            lines.append("偏差清单(按严重度降序):")
            for i, issue in enumerate(result.issues, 1):
                col = f" col={issue.column}" if issue.column else ""
                lines.append(f"  {i}. [{issue.severity.value}] {issue.bias_type.value}{col}")
                lines.append(f"     {issue.description}")
                lines.append(f"     证据: {issue.evidence}")
        return "\n".join(lines)


__all__ = [
    "BiasIssue",
    "BiasSeverity",
    "BiasType",
    "DetectorConfig",
    "DetectionResult",
    "LookAheadBiasDetector",
    "SimulationError",
]
