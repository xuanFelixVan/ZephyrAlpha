# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.infrastructure.auto_diagnostics
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
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
# [A_module] module_id=MOD-INF_auto_diagnostics | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RI-12 AutoDiagnostics — 自动诊断引擎
====================================
职责：对系统异常进行自动诊断——检测模式、推断根因、输出诊断报告。
使用方式：
    engine = AutoDiagnostics(config_path="config/diagnostics.yaml")
    report = engine.diagnose(anomaly_event)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "AutoDiagnostics",
    "DiagnosisReport",
    "DiagnosisSeverity",
    "DiagnosisStatus",
]


class DiagnosisSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class DiagnosisStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    UNKNOWN = "unknown"


@dataclass
class DiagnosisReport:
    """单次诊断报告"""

    report_id: str
    severity: DiagnosisSeverity = DiagnosisSeverity.INFO
    status: DiagnosisStatus = DiagnosisStatus.UNKNOWN
    component: str = ""
    symptoms: list[str] = field(default_factory=list)
    root_cause: str = ""
    evidence: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    confidence: float = 0.0
    inversion_verified: bool = False
    diagnosed_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "severity": self.severity.value,
            "status": self.status.value,
            "component": self.component,
            "symptoms": self.symptoms,
            "root_cause": self.root_cause,
            "evidence": self.evidence,
            "recommendations": self.recommendations,
            "confidence": self.confidence,
            "inversion_verified": self.inversion_verified,
            "diagnosed_at": self.diagnosed_at,
            "metadata": self.metadata,
        }


@dataclass
class DiagnosisRule:
    """诊断规则定义"""

    rule_id: str
    pattern: str
    severity: DiagnosisSeverity = DiagnosisSeverity.MEDIUM
    status: DiagnosisStatus = DiagnosisStatus.DEGRADED
    root_cause_template: str = ""
    recommendations: list[str] = field(default_factory=list)


class AutoDiagnostics:
    """自动诊断引擎

    基于规则模式的异常诊断，支持：
    - 多维度症状匹配
    - 置信度评估
    - 根因推断
    - 修复建议生成
    """

    def __init__(self, config_path: str | None = None):
        self._rules: list[DiagnosisRule] = []
        self._diagnosis_count: int = 0
        if config_path:
            self._load_rules(config_path)
        else:
            self._load_default_rules()

    def _load_default_rules(self) -> None:
        self._rules = [
            DiagnosisRule(
                rule_id="DR-001",
                pattern="timeout|慢|卡住",
                severity=DiagnosisSeverity.HIGH,
                status=DiagnosisStatus.FAILING,
                root_cause_template="可能的耗时操作未设timeout或资源争用",
                recommendations=["增加超时限制", "添加异步超时机制", "检查资源使用率"],
            ),
            DiagnosisRule(
                rule_id="DR-002",
                pattern="import.*failed|ModuleNotFoundError|ImportError",
                severity=DiagnosisSeverity.CRITICAL,
                status=DiagnosisStatus.FAILING,
                root_cause_template="模块导入路径异常或依赖缺失",
                recommendations=["检查sys.path", "验证包结构", "安装缺失依赖"],
            ),
            DiagnosisRule(
                rule_id="DR-003",
                pattern="PermissionError|拒绝访问|AccessDenied",
                severity=DiagnosisSeverity.HIGH,
                status=DiagnosisStatus.FAILING,
                root_cause_template="文件权限不足或进程无访问权",
                recommendations=["检查文件/目录权限", "以管理员身份运行", "检查文件是否被其他进程占用"],
            ),
            DiagnosisRule(
                rule_id="DR-004",
                pattern="encoding|乱码|UnicodeDecodeError",
                severity=DiagnosisSeverity.MEDIUM,
                status=DiagnosisStatus.DEGRADED,
                root_cause_template="编码声明缺失或与实际文件编码不符",
                recommendations=["显式声明encoding='utf-8'", "检查文件实际编码"],
            ),
            DiagnosisRule(
                rule_id="DR-005",
                pattern="orphan|未注册|无人调用|孤儿",
                severity=DiagnosisSeverity.MEDIUM,
                status=DiagnosisStatus.DEGRADED,
                root_cause_template="文件未在注册表中登记或调用链断裂",
                recommendations=["注册到manifest/registry", "建立调用入口", "更新__init__.py"],
            ),
        ]

    def _load_rules(self, config_path: str) -> None:
        try:
            import yaml

            with open(config_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            for r in data.get("rules", []):
                self._rules.append(DiagnosisRule(**r))
        except Exception as e:
            logger.warning("Failed to load rules from %s: %s", config_path, e)
            self._load_default_rules()

    def diagnose(
        self,
        event: dict[str, Any] | str,
        component: str = "",
    ) -> DiagnosisReport:
        self._diagnosis_count += 1
        msg = event if isinstance(event, str) else str(event)

        matched_rules: list[tuple[DiagnosisRule, float]] = []

        for rule in self._rules:
            import re

            confidence = 0.0
            for keyword in rule.pattern.split("|"):
                if re.search(keyword, msg, re.IGNORECASE):
                    confidence += 1.0 / len(rule.pattern.split("|"))
            if confidence > 0:
                matched_rules.append((rule, min(confidence, 1.0)))

        if not matched_rules:
            return DiagnosisReport(
                report_id=f"DR-{self._diagnosis_count:04d}",
                severity=DiagnosisSeverity.INFO,
                status=DiagnosisStatus.UNKNOWN,
                component=component,
                symptoms=["未能匹配到已知诊断模式"],
                root_cause="未知",
                confidence=0.0,
            )

        matched_rules.sort(key=lambda x: x[1], reverse=True)
        best_rule, best_confidence = matched_rules[0]

        return DiagnosisReport(
            report_id=f"DR-{self._diagnosis_count:04d}",
            severity=best_rule.severity,
            status=best_rule.status,
            component=component,
            symptoms=[msg[:200]],
            root_cause=best_rule.root_cause_template,
            recommendations=best_rule.recommendations,
            confidence=round(best_confidence, 3),
        )


if __name__ == "__main__":
    engine = AutoDiagnostics()
    report = engine.diagnose("导入失败 ModuleNotFoundError: No module named 'zephyr.xxx'", "gate_engine")
    print(report.to_dict())
