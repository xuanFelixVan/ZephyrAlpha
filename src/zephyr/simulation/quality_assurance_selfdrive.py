# [BLUEPRINT] MOD-AUDITTEST-001 | docs/03_modules/_domain_simulation/quality_assurance_selfdrive/blueprint.md
# [MODULE] zephyr.simulation.quality_assurance_selfdrive
# [DOMAIN] D_AUDITTEST
# [DEPENDENCIES] 无（纯内存/DI；clock/random_source/bias_detector/skeleton_writer/alert_sink 全注入）
# [CONSUMERS] 运行时装配批（契约变更钩子 / look_ahead 自诊断接线 / 回归基线比对 / 数据准确率抽检）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 契约骨架确定性生成(字段按名排序,含TODO标记,仅经注入writer不落盘); 检测器异常包装Fail-Closed; 退化=(baseline-current)/|baseline|>阈值方告警; 抽检样本由注入随机源确定性抽取; 告警不阻断; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_simulation/quality_assurance_selfdrive/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] QualitySelfdriveError(占位 ZA-AUDITTEST-UNREGISTERED-QA-SELFDRIVE)——非法契约schema/writer缺失/检测器缺失或异常/基线非法/抽检参数非法/随机源越界时抛
# [TESTS] tests/simulation/test_quality_assurance_selfdrive.py
# [A_module] module_id=MOD-AUDITTEST-001 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
QualityAssuranceSelfdrive — 质量保障自驱动器（MOD-AUDITTEST-001）。

B1-00346（AUD-DRAFT-001-DIGEST P2 波 P2-W16，CAND-AUDITTES-001，C2 C-025）：
质量保障**自驱动**四件套——①契约变更触发**测试骨架自生成**（解析契约
schema 字段 → pytest 骨架文本，产物仅经注入 writer，不直写 tracked 文件，
骨架含 TODO 标记）②look_ahead 偏差**自诊断接线**（注入检测器回调，检测器
异常包装为 Fail-Closed 专用 Error）③**性能回归基线比对**（当前指标 vs 基线，
退化幅度 > 阈值告警）④**数据准确率抽检**（注入随机源抽样 + 注入校验器比对，
不达标告警）。

查重分工（蓝图 §0）：look_ahead_bias_detector=偏差检测实现（本件仅做接线与
异常包装，不重复实现检测算法）；result_analyzer=回测结果分析（零交集）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: quality_assurance_selfdrive.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: random_source 参数
#   fields: 参数 random_source（无注解）
#   code: quality_assurance_selfdrive.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: bias_detector 参数
#   fields: 参数 bias_detector（无注解）
#   code: quality_assurance_selfdrive.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: skeleton_writer 参数
#   fields: 参数 skeleton_writer（无注解）
#   code: quality_assurance_selfdrive.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① QualityAssuranceSelfdrive
#   name_en: QualityAssuranceSelfdrive
#   intro: 质量保障自驱动四件套（骨架生成 + 偏差接线 + 回归比对 + 准确率抽检）。
#   desc: 质量保障自驱动四件套（骨架生成 + 偏差接线 + 回归比对 + 准确率抽检）。；公共方法（定义序）: generate_test_skeleton, diagnose_bias, compare_performance…
#   inputs: clock random_source bias_detector skeleton_writer alert_sink
#   outputs: 返回值
#   （注：A1 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: QualityAssuranceSelfdrive
#   downstream: 运行时装配批（契约变更钩子 / look_ahead 自诊断接线 / 回归基线比对 / 数据准确率抽检）
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
from dataclasses import dataclass
from typing import Any, Callable, Final, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "AccuracyReport",
    "BiasDiagnosis",
    "QualityAlert",
    "QualityAssuranceSelfdrive",
    "QualitySelfdriveError",
    "RegressionReport",
    "TestSkeleton",
]

#: 骨架文本中的待办标记（人工补齐断言语义）
_TODO_MARK: Final = "TODO"


class QualitySelfdriveError(Exception):
    """质量自驱动输入/接线非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-AUDITTEST-UNREGISTERED-QA-SELFDRIVE。
    """


@dataclass(frozen=True)
class QualityAlert:
    """质量告警载荷（偏差检出/回归退化/准确率不达标）。"""

    kind: str
    subject: str
    detail: str
    raised_at: datetime.datetime


@dataclass(frozen=True)
class TestSkeleton:
    """契约变更触发的 pytest 测试骨架（frozen）。"""

    contract_name: str
    fields: tuple[str, ...]
    skeleton_text: str
    generated_at: datetime.datetime


@dataclass(frozen=True)
class BiasDiagnosis:
    """look_ahead 偏差自诊断结果（frozen）。"""

    target: str
    issues: tuple[str, ...]
    is_clean: bool
    diagnosed_at: datetime.datetime


@dataclass(frozen=True)
class RegressionReport:
    """性能回归基线比对结果（frozen；degraded 按指标名确定性排序）。"""

    degraded: tuple[str, ...]
    ratios: Mapping[str, float]
    threshold: float
    compared_at: datetime.datetime


@dataclass(frozen=True)
class AccuracyReport:
    """数据准确率抽检结果（frozen）。"""

    sample_size: int
    passed: int
    accuracy: float
    meets_standard: bool
    sampled_at: datetime.datetime


class QualityAssuranceSelfdrive:
    """质量保障自驱动四件套（骨架生成 + 偏差接线 + 回归比对 + 准确率抽检）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        random_source: Callable[[], float] | None = None,
        bias_detector: Callable[[str], Sequence[str]] | None = None,
        skeleton_writer: Callable[[str, str], None] | None = None,
        alert_sink: Callable[[QualityAlert], None] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._rng = random_source
        self._detector = bias_detector
        self._writer = skeleton_writer
        self._alert_sink = alert_sink

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _alert(self, kind: str, subject: str, detail: str) -> None:
        alert = QualityAlert(kind=kind, subject=subject, detail=detail, raised_at=self._clock())
        _log.warning("质量告警[%s]: %s (%s)", kind, subject, detail)
        if self._alert_sink is not None:
            try:
                self._alert_sink(alert)
            except Exception:  # noqa: BLE001 — 告警不阻断（蓝图 §1）
                _log.exception("alert_sink 告警失败")

    def _random(self) -> float:
        if self._rng is None:
            raise QualitySelfdriveError("random_source 未注入（抽检须确定性随机源）")
        value = float(self._rng())
        if not 0.0 <= value < 1.0:
            raise QualitySelfdriveError(f"随机源越界: {value!r} 不在 [0,1)")
        return value

    # ── ① 契约变更触发测试骨架自生成 ─────────────────────────────────────

    def generate_test_skeleton(
        self,
        contract_name: str,
        schema: Mapping[str, str],
    ) -> TestSkeleton:
        """解析契约 schema → pytest 骨架文本，经注入 writer 交付（不落盘）。"""
        if not contract_name or not contract_name.isidentifier():
            raise QualitySelfdriveError(f"非法契约名: {contract_name!r}")
        if not schema:
            raise QualitySelfdriveError("契约 schema 为空（无字段可生成骨架）")
        for field in schema:
            if not field or not field.isidentifier():
                raise QualitySelfdriveError(f"非法契约字段名: {field!r}")
        if self._writer is None:
            # 骨架产物强制经注入 writer：未注入 Fail-Closed，禁止旁路落盘
            raise QualitySelfdriveError("skeleton_writer 未注入（骨架产物禁止直写 tracked 文件）")

        fields = tuple(sorted(schema))
        lines = [
            f'"""契约 {contract_name} 变更触发的测试骨架（自生成，{_TODO_MARK} 待人工补齐）。"""',
            "",
            "import pytest",
            "",
            "",
        ]
        for field in fields:
            lines += [
                f"def test_{contract_name}_has_field_{field}() -> None:",
                f'    """{_TODO_MARK}: 断言契约字段 {field}（类型 {schema[field]}）存在且合法。"""',
                f"    pytest.skip('{_TODO_MARK}: 待人工补齐字段 {field} 断言语义')",
                "",
                "",
            ]
        skeleton_text = "\n".join(lines).rstrip("\n") + "\n"
        self._writer(contract_name, skeleton_text)
        return TestSkeleton(
            contract_name=contract_name,
            fields=fields,
            skeleton_text=skeleton_text,
            generated_at=self._clock(),
        )

    # ── ② look_ahead 偏差自诊断接线 ──────────────────────────────────────

    def diagnose_bias(self, target: str) -> BiasDiagnosis:
        """经注入检测器回调诊断 look_ahead 偏差；检出即告警，异常包装 Fail-Closed。"""
        if not target:
            raise QualitySelfdriveError("诊断目标为空")
        if self._detector is None:
            raise QualitySelfdriveError("bias_detector 未注入（偏差自诊断禁止旁路）")
        try:
            issues = tuple(str(issue) for issue in self._detector(target))
        except QualitySelfdriveError:
            raise
        except Exception as exc:  # noqa: BLE001 — 检测器异常包装 Fail-Closed
            raise QualitySelfdriveError(f"bias_detector 检测异常: {exc!r}") from exc
        is_clean = len(issues) == 0
        if not is_clean:
            self._alert(
                "bias_detected",
                target,
                f"检出 {len(issues)} 项 look_ahead 偏差: {'; '.join(issues)}",
            )
        return BiasDiagnosis(target=target, issues=issues, is_clean=is_clean, diagnosed_at=self._clock())

    # ── ③ 性能回归基线比对 ───────────────────────────────────────────────

    def compare_performance(
        self,
        current: Mapping[str, float],
        baseline: Mapping[str, float],
        *,
        threshold: float,
    ) -> RegressionReport:
        """当前指标 vs 基线：退化幅度 (baseline-current)/|baseline| > 阈值 → 告警。"""
        if threshold < 0:
            raise QualitySelfdriveError(f"非法退化阈值: {threshold!r}（须 ≥ 0）")
        if not baseline:
            raise QualitySelfdriveError("性能基线为空（无指标可比对）")
        ratios: dict[str, float] = {}
        degraded: list[str] = []
        for metric in sorted(baseline):
            base = float(baseline[metric])
            if metric not in current:
                raise QualitySelfdriveError(f"当前指标缺失: {metric!r}（基线要求比对）")
            cur = float(current[metric])
            ratio = (base - cur) / abs(base) if base != 0 else (0.0 if cur == 0.0 else 1.0)
            ratios[metric] = ratio
            if ratio > threshold:
                degraded.append(metric)
        if degraded:
            self._alert(
                "performance_regression",
                ",".join(degraded),
                f"{len(degraded)} 项指标退化超阈值 {threshold}: "
                + "; ".join(f"{m} 退化 {ratios[m]:.4f}" for m in degraded),
            )
        return RegressionReport(
            degraded=tuple(degraded),
            ratios=ratios,
            threshold=threshold,
            compared_at=self._clock(),
        )

    # ── ④ 数据准确率抽检 ─────────────────────────────────────────────────

    def sample_accuracy(
        self,
        records: Sequence[Any],
        sample_size: int,
        validator: Callable[[Any], bool] | None,
        *,
        min_accuracy: float,
    ) -> AccuracyReport:
        """注入随机源抽样 + 注入校验器比对：准确率低于 min_accuracy → 告警。"""
        if not records:
            raise QualitySelfdriveError("抽检记录为空")
        if not isinstance(sample_size, int) or isinstance(sample_size, bool):
            raise QualitySelfdriveError(f"非法抽检样本量: {sample_size!r}")
        if not 1 <= sample_size <= len(records):
            raise QualitySelfdriveError(f"抽检样本量越界: {sample_size}（须在 [1, {len(records)}]）")
        if validator is None:
            raise QualitySelfdriveError("validator 未注入（准确率比对禁止旁路）")
        if not 0.0 <= min_accuracy <= 1.0:
            raise QualitySelfdriveError(f"非法准确率下限: {min_accuracy!r}（须在 [0,1]）")

        n = len(records)
        keyed = sorted((self._random(), idx) for idx in range(n))
        sampled_idx = sorted(idx for _, idx in keyed[:sample_size])
        passed = 0
        for idx in sampled_idx:
            try:
                ok = bool(validator(records[idx]))
            except Exception as exc:  # noqa: BLE001 — 校验器异常包装 Fail-Closed
                raise QualitySelfdriveError(f"validator 校验异常(记录 #{idx}): {exc!r}") from exc
            if ok:
                passed += 1
        accuracy = passed / sample_size
        meets = accuracy >= min_accuracy
        if not meets:
            self._alert(
                "accuracy_below_standard",
                f"{passed}/{sample_size}",
                f"抽检准确率 {accuracy:.4f} 低于下限 {min_accuracy}",
            )
        return AccuracyReport(
            sample_size=sample_size,
            passed=passed,
            accuracy=accuracy,
            meets_standard=meets,
            sampled_at=self._clock(),
        )
