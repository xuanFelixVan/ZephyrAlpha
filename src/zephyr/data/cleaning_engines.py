# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.cleaning_engines
# [DOMAIN] D_DATA
# [DEPENDENCIES] stdlib; zephyr.data.cleaning_rule_engine(惰性); zephyr.data_eng.cleaning_anomaly_engine(惰性); zephyr.data_eng.expectation_governance(惰性); zephyr.data_eng.data_anomaly_alerter(惰性)
# [CONSUMERS] F04 C1 解锁后的接线方（现仅测试/诊断面；生产接线=Owner 门）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 纯派发门面零判据值（判据值真源各引擎自带，宪法 RULE-SSOT）;engines_status 接线实况为静态声明须与 grep 复扫一致（虚标=事故）;三 data_eng 引擎本门面不构成生产接线（C1 解锁前调用方仅测试/诊断）;ai_adjudicate 只留接口位一律抛 OwnerGate（花钱点禁自作主张）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AiAdjudicationPendingOwnerGateError（C6 AI 判净接口位）；派发函数异常原样透传各引擎（不吞不改判）
# [TESTS] tests/zephyr/data/test_cleaning_engines.py
# [A_module] module_id=MOD-L00-004-R1 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# create-guard-not-dup: 清洗校验四引擎统一门面（F04 案卷 C1/C2/C6，状态台账+派发），非任何单一引擎的第二实现
# [TTL] permanent

"""

Cleaning Engines Facade — 清洗校验四引擎统一入口 (MOD-L00-004-R1 / F04 夜战批)

背景（F04 案卷 C1/C2/C6）: 清洗四引擎（DSL 规则引擎/清洗异常引擎/期望治理/
数据异常告警器）API 各异、接线实况分裂——DSL 引擎已经 R-M1-06 读侧托管接线
（cleaning_rules_hosting），其余三件零生产调用方挂 Owner 门。本门面提供：

    1. engines_status(): 四引擎静态台账（接线实况声明，与 grep 复扫对账）；
    2. 四个派发函数（run_dsl_rules/detect_frame_anomalies/validate_expectations/
       evaluate_anomaly_signals）：统一签名习惯，惰性 import 防循环/重依赖；
    3. ai_adjudicate(): C6 AI 判净站**接口位**——花钱点=OWNER-GATE，本件只留
       挂钩点（调用即抛 AiAdjudicationPendingOwnerGateError），不解锁不实现。

红线: 本门面不改变任何引擎行为、不构成生产接线（C1 解锁前调用方=测试/诊断）；
判据值一律在各引擎/配置真源，门面零判据（宪法 RULE-SSOT）。

SSoT: depgraph MOD-L00-004-R1
Version: 0.1.0

# [ALGO_FLOW] external: docs/03_modules/_domain_data/algo_flow/cleaning_rule_engine.yaml
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:
    from zephyr.data_eng.cleaning_anomaly_engine import AnomalyFinding
    from zephyr.data_eng.expectation_governance import Expectation, ValidationReport

import pandas as pd

__all__: Final = [
    "EngineDescriptor",
    "AiAdjudicationPendingOwnerGateError",
    "engines_status",
    "run_dsl_rules",
    "detect_frame_anomalies",
    "validate_expectations",
    "evaluate_anomaly_signals",
    "ai_adjudicate",
]


class AiAdjudicationPendingOwnerGateError(Exception):
    """C6 AI 判净站未解锁（花钱点=Owner 门，接口位调用即抛）。"""


@dataclass(frozen=True)
class EngineDescriptor:
    """单引擎静态台账条目（接线实况声明，grep 可复扫对账）。"""

    key: str
    module: str
    display_name: str
    wired: bool
    consumer: str
    entry: str  # 本门面派发函数名


_ENGINES: Final = (
    EngineDescriptor(
        key="dsl_rule_engine",
        module="zephyr.data.cleaning_rule_engine",
        display_name="清洗规则DSL引擎",
        wired=True,
        consumer="zephyr.data.cleaning_rules_hosting（R-M1-06 读侧托管）",
        entry="run_dsl_rules",
    ),
    EngineDescriptor(
        key="cleaning_anomaly_engine",
        module="zephyr.data_eng.cleaning_anomaly_engine",
        display_name="清洗异常引擎",
        wired=False,
        consumer="built-not-wired（F04 C1 挂 Owner 门）",
        entry="detect_frame_anomalies",
    ),
    EngineDescriptor(
        key="expectation_governance",
        module="zephyr.data_eng.expectation_governance",
        display_name="期望治理门控",
        wired=False,
        consumer="built-not-wired（F04 C1 挂 Owner 门）",
        entry="validate_expectations",
    ),
    EngineDescriptor(
        key="data_anomaly_alerter",
        module="zephyr.data_eng.data_anomaly_alerter",
        display_name="数据异常告警器",
        wired=False,
        consumer="built-not-wired（F04 C1 挂 Owner 门）",
        entry="evaluate_anomaly_signals",
    ),
)


def engines_status() -> tuple[EngineDescriptor, ...]:
    """四引擎静态台账（只读；接线实况如有变化须先 grep 复扫再改声明）。"""
    return _ENGINES


# ---------------------------------------------------------------------------
# 派发函数（惰性 import：防循环依赖+重依赖按需加载）
# ---------------------------------------------------------------------------


def run_dsl_rules(
    rows: Sequence[dict[str, Any]],
    rule_specs: Sequence[dict[str, Any]],
    table: str = "",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """引擎1 派发：DSL 规则判定（规则 spec 结构见 cleaning_rule_engine.parse_rules）。

    Returns:
        (clean_rows, stats)——stats = {table, total, flagged, intercepted,
        by_rule, pending_approvals}（对齐 apply_quality_gate 形态）。
    """
    from zephyr.data.cleaning_rule_engine import CleaningRuleEngine, parse_rules, run_quality_gate

    engine = CleaningRuleEngine(parse_rules(list(rule_specs)))
    return run_quality_gate(engine, table, list(rows))


def detect_frame_anomalies(df: pd.DataFrame, symbol: str = "") -> list[AnomalyFinding]:
    """引擎2 派发：OHLCV 帧五类异常检出（价格跳变/复权断点/重复bar/量能/缺失）。"""
    from zephyr.data_eng.cleaning_anomaly_engine import CleaningAnomalyEngine

    return CleaningAnomalyEngine().detect(df, symbol=symbol)


def validate_expectations(
    df: pd.DataFrame,
    expectations: Sequence[Expectation],
    suite_name: str = "",
    archive_path: str | None = None,
) -> ValidationReport:
    """引擎3 派发：期望套件验证（三档门控 block/degrade/warn）。

    expectations 来源：ExpectationGovernance.load_suite(yaml) 或 suite_from_ctr001()。
    """
    from zephyr.data_eng.expectation_governance import ExpectationGovernance

    gov = ExpectationGovernance(archive_path=archive_path)
    return gov.validate(df, list(expectations), suite_name=suite_name)


def evaluate_anomaly_signals(
    signals: Sequence[Any],
    now_utc: datetime | None = None,
    source: str = "data_eng",
    alert_sink: Callable[..., bool] | None = None,
) -> tuple[list[Any], list[Any]]:
    """引擎4 派发：异常信号分级+抑制+路由（返回 (alerts, quality_gate_events)）。

    信号构造见 data_anomaly_alerter.detect_price_jumps / detect_missing_rate 等。
    """
    from zephyr.data_eng.data_anomaly_alerter import DataAnomalyAlerter

    alerter = DataAnomalyAlerter(alert_sink=alert_sink) if alert_sink else DataAnomalyAlerter()
    return alerter.evaluate(list(signals), now_utc=now_utc, source=source)


def ai_adjudicate(
    findings: Sequence[dict[str, Any]],
    *,
    requested_by: str = "",
) -> dict[str, Any]:
    """C6 AI 判净站接口位（花钱点=OWNER-GATE，只留挂钩不解锁）。

    F04 案卷 C6：AI 判净考尺挂起，解锁条件=C1 接线 Owner 门同批。在 Owner
    裁定解锁并落地计费通道之前，任何调用一律 fail-closed 抛错——禁自作主张
    花钱。解锁后本函数应路由 LSG 网关（zephyr.security.llm_defense），签名不变。
    """
    raise AiAdjudicationPendingOwnerGateError(
        "C6 AI 判净站=OWNER-GATE（花钱点）：F04 案卷解锁条件=C1 接线同批解锁；"
        f"当前调用 requested_by={requested_by!r} findings={len(findings)} 条——"
        "接口位已就位，等待 Owner 解锁裁定"
    )


if __name__ == "__main__":  # ORPHAN-MODULE 入口豁免形态：facade 自检 CLI（只读台账，零副作用）
    for d in engines_status():
        print(f"{d.key}	{d.display_name}	wired={d.wired}	consumer={d.consumer}")
