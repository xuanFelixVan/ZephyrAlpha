# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.alerts.threshold_loader
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.io.paths; zephyr.shared.foundation.errors; docs/01_policies_and_standards/_registry/catalogs/alert_threshold_registry.yaml (SSoT，fail-closed 加载)
# [CONSUMERS] MOD-RK-011(drawdown_tracker); MOD-INF-035(health_monitor); MOD-BT-001(decision_gate); post_live_verification; MOD-RK-06(alert_generator); alert_escalation; MOD-RK-20(daily_auditor); MOD-RPT-008(risk_report_engine); MOD-RK-19(operational_risk_monitor)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 阈值唯一真源=alert_threshold_registry.yaml；缺文件/缺条目/类型畸形一律 fail-closed raise，禁止静默回退码内硬编码
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AlertThresholdConfigError(ZA-SH-0052)
# [TESTS] tests/governance/test_alert_threshold_consistency.py（红队 fail-closed 用例内嵌）
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""告警阈值注册表共享加载器（tracker #87 存量统读改造，55 号 §3.3 决策落地）。

唯一职责：从 alert_threshold_registry.yaml（REG-ATH-001）fail-closed 加载阈值，
供 9 个存量模块替代码内硬编码常量（加载范式对齐
strategy_deviation_monitor._load_deviation_thresholds 生产先例）。

fail-closed 四类失败一律 raise AlertThresholdConfigError（禁止第二真源兜底）：
  ① 注册表文件不存在  ② YAML 畸形  ③ 缺条目/缺 value 字段  ④ 类型畸形（cast 失败）

字符串规约值（PLV "±1%" 等）经 cast="str" 保持字符串语义加载，不强行数值化。
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Final, Literal, Mapping

import yaml

from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.io.paths import REPO_ROOT

__all__: Final = [
    "ALERT_THRESHOLD_REGISTRY_PATH",
    "AlertThresholdConfigError",
    "load_alert_thresholds",
]


class AlertThresholdConfigError(ZephyrBaseError):
    """告警阈值注册表缺失/畸形（fail-closed：禁止码内第二真源兜底）。"""

    error_code = "ZA-SH-0052"


#: 告警阈值注册表相对路径（真源唯一：55 号 §3.3 决策）
ALERT_THRESHOLD_REGISTRY_PATH: Final[Path] = (
    REPO_ROOT
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "alert_threshold_registry.yaml"
)


def _cast_value(raw: Any, cast: Literal["float", "int", "str"], tid: str) -> Any:
    """按声明类型转换阈值原始值（类型畸形 → AlertThresholdConfigError）。

    - float: int/float/数值字符串 → float（对齐 strategy_deviation_monitor 范式；
      拒 bool——YAML `value: true` 笔误须 fail-closed，禁止静默 1.0）
    - int:   仅接受 YAML 整数（拒 bool/浮点/字符串，防 300.5→300 静默截断）
    - str:   仅接受 YAML 字符串（PLV 字符串规约语义，不数值化）
    """
    if cast == "float":
        if isinstance(raw, bool):
            raise AlertThresholdConfigError(
                "阈值条目 value 非数值",
                details={"threshold_id": tid, "value": repr(raw)},
            )
        try:
            f = float(raw)
        except (TypeError, ValueError) as exc:
            raise AlertThresholdConfigError(
                "阈值条目 value 非数值",
                details={"threshold_id": tid, "value": repr(raw)},
            ) from exc
        # NaN/Inf 拒绝（AI-R1 复审加固）：NaN 使阈值比较恒 False → 告警链静默
        # 失效（比 bool→1.0 更隐蔽）；YAML `.nan`/`.inf` 与数值字符串 "inf"
        # （含 "1e400" 溢出）统一 fail-closed
        if not math.isfinite(f):
            raise AlertThresholdConfigError(
                "阈值条目 value 非有限数值（NaN/Inf）",
                details={"threshold_id": tid, "value": repr(raw)},
            )
        return f
    if cast == "int":
        if isinstance(raw, bool) or not isinstance(raw, int):
            raise AlertThresholdConfigError(
                "阈值条目 value 非整数",
                details={"threshold_id": tid, "value": repr(raw)},
            )
        return raw
    # cast == "str"
    if not isinstance(raw, str):
        raise AlertThresholdConfigError(
            "阈值条目 value 非字符串",
            details={"threshold_id": tid, "value": repr(raw)},
        )
    return raw


def load_alert_thresholds(
    mapping: Mapping[str, str],
    *,
    registry_path: Path | None = None,
    cast: Literal["float", "int", "str"] = "float",
) -> dict[str, Any]:
    """从告警阈值注册表加载阈值（fail-closed：缺文件/缺条目/类型畸形直接报错）。

    Args:
        mapping: {threshold_id: 输出键} 映射，如 {"THD-DRAWDOWN-001": "warning_threshold"}
        registry_path: 注册表路径（默认 ALERT_THRESHOLD_REGISTRY_PATH；测试注入用）
        cast: 值类型——"float"（默认）/"int"/"str"（字符串规约保持字符串语义）

    Returns:
        {输出键: 转换后阈值}

    Raises:
        AlertThresholdConfigError: 注册表不存在/YAML 畸形/缺条目/缺 value/类型畸形
    """
    path = registry_path or ALERT_THRESHOLD_REGISTRY_PATH
    if not path.exists():
        raise AlertThresholdConfigError(
            "告警阈值注册表不存在", details={"path": str(path)}
        )
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise AlertThresholdConfigError(
            "告警阈值注册表 YAML 畸形",
            details={"path": str(path), "error": str(exc)},
        ) from exc
    entries = {e["threshold_id"]: e for e in (data or {}).get("thresholds", [])}
    out: dict[str, Any] = {}
    for tid, key in mapping.items():
        entry = entries.get(tid)
        if entry is None:
            raise AlertThresholdConfigError(
                "注册表缺条目", details={"threshold_id": tid, "path": str(path)}
            )
        if "value" not in entry:
            raise AlertThresholdConfigError(
                "注册表条目缺 value 字段",
                details={"threshold_id": tid, "path": str(path)},
            )
        out[key] = _cast_value(entry["value"], cast, tid)
    return out
