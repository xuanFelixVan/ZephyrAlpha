# [BLUEPRINT] MOD-DATA_ENG | (pending)
# [MODULE] zephyr.data_eng.expectation_governance
# [DOMAIN] D_DATA_ENG
# [DEPENDENCIES] pandas; PyYAML; zephyr.shared.contracts.market_data(CTR-001字段联动)
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 三档裁定block>degrade>warn>ok; 报告JSONL追加存档可追溯; 未知期望类型fail-closed抛ValueError
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 套件YAML缺expectations键->ValueError; 未知type->ValueError; 存档IO失败仅log不阻断验证
# [TESTS] tests/zephyr/data/test_expectation_governance.py
# [TTL] permanent
"""
ZephyrAlpha — D_DATA_ENG 期望治理门控（CAND-DATENG-002 / B1-00607）。

min_build_spec（AUD-DRAFT-001-DIGEST P0）：
  - 期望套件 YAML：schema / 非空 / 值域 / 分布 / 时效
  - 验证器接入质量门控：阻断(BLOCK) / 降级(DEGRADE) / 告警(WARN) 三档
  - 验证报告存档可追溯（JSONL 追加）
  - 与 CTR-001 NormalizedMarketData 契约字段联动（suite_from_ctr001）
  - 轻量自研，不引 Great Expectations 重依赖

套件 YAML 格式::

    suite: market_data_daily
    expectations:
      - type: schema          # 列存在性
        column: close
        severity: block       # block|degrade|warn（默认 warn）
      - type: not_null
        column: close
      - type: range
        column: close
        params: {min: 0, max: 100000}
      - type: distribution
        column: volume
        params: {mean_min: 0, mean_max: 1e12, std_max: 1e12}
      - type: freshness
        column: timestamp
        params: {max_age_hours: 48}

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: archive_path 参数
#   fields: 参数 archive_path（无注解）
#   code: expectation_governance.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: now_fn 参数
#   fields: 参数 now_fn（无注解）
#   code: expectation_governance.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ExpectationGovernance
#   name_en: ExpectationGovernance
#   intro: 期望套件验证器 + 三档质量门控。
#   desc: 期望套件验证器 + 三档质量门控。；公共方法（定义序）: load_suite, suite_from_ctr001, validate；源码 L142-L325
#   inputs: archive_path now_fn
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: ExpectationGovernance
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import dataclasses
import datetime
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable

import pandas as pd
import yaml

logger = logging.getLogger(__name__)

__all__ = [
    "Expectation",
    "ExpectationGovernance",
    "ExpectationResult",
    "GateVerdict",
    "ValidationReport",
]


class GateVerdict(str, Enum):
    """质量门控三档+放行裁定。"""

    OK = "ok"
    WARN = "warn"
    DEGRADE = "degrade"
    BLOCK = "block"


@dataclass(frozen=True)
class Expectation:
    """单条期望。"""

    type: str
    column: str
    params: dict = field(default_factory=dict)
    severity: str = "warn"


@dataclass(frozen=True)
class ExpectationResult:
    """单条期望验证结果。"""

    expectation: Expectation
    passed: bool
    detail: str


@dataclass(frozen=True)
class ValidationReport:
    """套件验证报告（可存档追溯）。"""

    suite_name: str
    verdict: GateVerdict
    results: list[ExpectationResult]
    validated_at: str
    row_count: int


class ExpectationGovernance:
    """期望套件验证器 + 三档质量门控。"""

    def __init__(
        self,
        archive_path: str | Path | None = None,
        now_fn: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        """
        Args:
            archive_path: 验证报告 JSONL 存档路径（None=不存档）
            now_fn: 时钟注入（时效期望/报告时间戳用），默认本地当前时间
        """
        self._archive_path = Path(archive_path) if archive_path else None
        self._now_fn = now_fn or datetime.datetime.now

    # ------------------------------------------------------------------
    # 套件加载
    # ------------------------------------------------------------------

    @staticmethod
    def load_suite(path: str | Path) -> list[Expectation]:
        """加载期望套件 YAML。缺 expectations 键 fail-closed 抛 ValueError。"""
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        if not isinstance(raw, dict) or "expectations" not in raw:
            raise ValueError(f"期望套件缺少 expectations 键: {path}")
        exps: list[Expectation] = []
        for i, item in enumerate(raw["expectations"] or []):
            if not isinstance(item, dict) or "type" not in item or "column" not in item:
                raise ValueError(f"期望条目 #{i} 缺 type/column: {item!r}")
            exps.append(
                Expectation(
                    type=str(item["type"]),
                    column=str(item["column"]),
                    params=dict(item.get("params") or {}),
                    severity=str(item.get("severity", "warn")),
                )
            )
        return exps

    @staticmethod
    def suite_from_ctr001() -> list[Expectation]:
        """从 CTR-001 NormalizedMarketData 契约生成 schema 期望（block 级）。

        契约必填字段（无默认值）= 数据契约承重墙，缺失即阻断。
        """
        from zephyr.shared.contracts.market_data import NormalizedMarketData

        required = [
            f.name
            for f in dataclasses.fields(NormalizedMarketData)
            if f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING
        ]
        return [Expectation(type="schema", column=name, severity="block") for name in required]

    # ------------------------------------------------------------------
    # 验证
    # ------------------------------------------------------------------

    def validate(
        self,
        df: pd.DataFrame,
        expectations: list[Expectation],
        suite_name: str = "",
    ) -> ValidationReport:
        """执行套件验证并聚合成三档门控裁定。"""
        results = [self._check(df, e) for e in expectations]
        verdict = GateVerdict.OK
        for r in results:
            if r.passed:
                continue
            sev = r.expectation.severity
            if sev == "block":
                verdict = GateVerdict.BLOCK
                break
            if sev == "degrade" and verdict in (GateVerdict.OK, GateVerdict.WARN):
                verdict = GateVerdict.DEGRADE
            elif sev == "warn" and verdict == GateVerdict.OK:
                verdict = GateVerdict.WARN
        report = ValidationReport(
            suite_name=suite_name,
            verdict=verdict,
            results=results,
            validated_at=self._now_fn().isoformat(),
            row_count=len(df) if df is not None else 0,
        )
        self._archive(report)
        return report

    def _check(self, df: pd.DataFrame, exp: Expectation) -> ExpectationResult:
        handler = getattr(self, f"_exp_{exp.type}", None)
        if handler is None:
            raise ValueError(f"未知期望类型: {exp.type}")
        passed, detail = handler(df, exp)
        return ExpectationResult(expectation=exp, passed=passed, detail=detail)

    # ------------------------------------------------------------------
    # 期望类型实现
    # ------------------------------------------------------------------

    def _exp_schema(self, df: pd.DataFrame, exp: Expectation) -> tuple[bool, str]:
        ok = exp.column in df.columns
        return ok, f"列 {exp.column} {'存在' if ok else '缺失'}"

    def _exp_not_null(self, df: pd.DataFrame, exp: Expectation) -> tuple[bool, str]:
        if exp.column not in df.columns:
            return False, f"列 {exp.column} 缺失"
        n_null = int(df[exp.column].isna().sum())
        return n_null == 0, f"列 {exp.column} 空值 {n_null} 行"

    def _exp_range(self, df: pd.DataFrame, exp: Expectation) -> tuple[bool, str]:
        if exp.column not in df.columns:
            return False, f"列 {exp.column} 缺失"
        series = pd.to_numeric(df[exp.column], errors="coerce").dropna()
        lo = exp.params.get("min")
        hi = exp.params.get("max")
        bad = 0
        if lo is not None:
            bad += int((series < lo).sum())
        if hi is not None:
            bad += int((series > hi).sum())
        return bad == 0, f"列 {exp.column} 值域 [{lo},{hi}] 越界 {bad} 行"

    def _exp_distribution(self, df: pd.DataFrame, exp: Expectation) -> tuple[bool, str]:
        if exp.column not in df.columns:
            return False, f"列 {exp.column} 缺失"
        series = pd.to_numeric(df[exp.column], errors="coerce").dropna()
        if series.empty:
            return False, f"列 {exp.column} 无有效数值"
        mean_v = float(series.mean())
        std_v = float(series.std()) if len(series) > 1 else 0.0
        ok = True
        parts = []
        if "mean_min" in exp.params:
            ok = ok and mean_v >= exp.params["mean_min"]
        if "mean_max" in exp.params:
            ok = ok and mean_v <= exp.params["mean_max"]
        if "std_max" in exp.params:
            ok = ok and std_v <= exp.params["std_max"]
        parts.append(f"mean={mean_v:.4g} std={std_v:.4g}")
        return ok, f"列 {exp.column} 分布 {'达标' if ok else '越限'}（{'; '.join(parts)}）"

    def _exp_freshness(self, df: pd.DataFrame, exp: Expectation) -> tuple[bool, str]:
        if exp.column not in df.columns:
            return False, f"列 {exp.column} 缺失"
        max_ts = pd.to_datetime(df[exp.column], errors="coerce").max()
        if pd.isna(max_ts):
            return False, f"列 {exp.column} 无有效时间戳"
        max_age_hours = float(exp.params.get("max_age_hours", 48))
        now = self._now_fn().replace(tzinfo=None)
        latest = max_ts.to_pydatetime().replace(tzinfo=None)
        age_hours = (now - latest).total_seconds() / 3600.0
        ok = age_hours <= max_age_hours
        return ok, f"列 {exp.column} 最新 {max_ts}，龄期 {age_hours:.1f}h / 上限 {max_age_hours:.0f}h"

    # ------------------------------------------------------------------
    # 存档
    # ------------------------------------------------------------------

    def _archive(self, report: ValidationReport) -> None:
        if self._archive_path is None:
            return
        try:
            self._archive_path.parent.mkdir(parents=True, exist_ok=True)
            rec = {
                "suite_name": report.suite_name,
                "verdict": report.verdict.value,
                "validated_at": report.validated_at,
                "row_count": report.row_count,
                "results": [
                    {
                        "type": r.expectation.type,
                        "column": r.expectation.column,
                        "severity": r.expectation.severity,
                        "passed": r.passed,
                        "detail": r.detail,
                    }
                    for r in report.results
                ],
            }
            with self._archive_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except OSError:  # 存档失败不阻断验证主流程
            logger.exception("验证报告存档失败: %s", self._archive_path)
