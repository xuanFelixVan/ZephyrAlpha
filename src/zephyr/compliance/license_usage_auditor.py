# [BLUEPRINT] MOD-CMP-008 | docs/03_modules/_domain_compliance/license_usage_auditor/blueprint.md
# [MODULE] zephyr.compliance.license_usage_auditor
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] stdlib + pyyaml + zephyr.compliance.compliance_log
# [CONSUMERS] 62 号 REG-DATAFLOW-001 治理流程（定期复核+新增消费模块触发，43 号 §5.3）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 缺 compliance 段的源默认仅 backtest 用途（最保守假设）; 授权过期=Fail-Closed 立即切断; 违规处置分级 L1/L2/L3 不降级
# [MODIFY-GUARD] 43_compliance_discipline.md §5（BM-BUY-09）
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] LicenseAuditError(ZA-CMP-0003)
# [TESTS] tests/compliance/test_license_usage_auditor.py
# [TTL] permanent

"""
数据源授权条款合规审计（43_compliance_discipline §5，BM-BUY-09 信息合规）。

管数据源使用条款合规——确保行情/另类数据来源与使用符合供应商授权条款。
本篇按 panorama 定义落地为**数据源授权合规**；内幕隔离墙/通信监控不建设
（个人自有资金单人决策，§5.2 裁定）。

合规段结构（§5.3，作为 62 号 data_asset_registry compliance 字段展开真源）：
  vendor / license_type(personal|professional|redistribution|trial) /
  permitted_use(backtest|live_trading|display|ml_training) / redistribution /
  derived_data_policy / expiry / terms_ref / registered_at / review_cycle_days

违规分级处置（§5.3 表格）：
  L1 超范围使用 → 切断该用途数据流 + Warning + 限期整改
  L2 授权过期   → 立即切断数据流（Fail-Closed）+ 告警
  L3 再分发违规 → 人工处置 + 条款复核 + 功能下线评估（联动 §6 门禁）

降级（§5.3）：登记表缺失某源 compliance 段 → 该源默认仅 backtest 用途，
直至补登。存量 legacy 形态（compliance 为自由文本字符串）视同缺失段处理。

Version: 1.0.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: registry_path 参数
#   fields: 参数 registry_path（无注解）
#   code: license_usage_auditor.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: logger 参数
#   fields: 参数 logger（无注解）
#   code: license_usage_auditor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① LicenseUsageAuditor
#   name_en: LicenseUsageAuditor
#   intro: 授权使用审计器。
#   desc: 授权使用审计器。 Args: registry_path: data_asset_registry.yaml 路径（默认主仓真源）。 logger: 合规日志。；公共方法（定义序）: load_source, audi…
#   inputs: registry_path logger
#   outputs: 返回值
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: LicenseUsageAuditor
#   downstream: 62 号 REG-DATAFLOW-001 治理流程（定期复核+新增消费模块触发，43 号 §5.3）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

from zephyr.compliance.compliance_log import ComplianceLogger
from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.io.paths import REPO_ROOT

DEFAULT_REGISTRY_PATH: Path = (
    REPO_ROOT  # git 版本化配置锚定当前检出（区别于治理观测库锚主仓）
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "data_asset_registry.yaml"
)

#: 合法用途词表（§5.3 permitted_use 枚举）
VALID_USES: frozenset[str] = frozenset({"backtest", "live_trading", "display", "ml_training", "redistribution"})

#: 缺 compliance 段时的最保守默认用途（§5.3 降级裁定）
CONSERVATIVE_DEFAULT_USES: frozenset[str] = frozenset({"backtest"})


class LicenseAuditError(ZephyrBaseError):
    """授权审计错误。"""

    error_code = "ZA-CMP-0003"


class ViolationLevel(enum.Enum):
    """违规级别（§5.3 处置表）。"""

    L1_SCOPE = "L1_SCOPE"  # 超范围使用
    L2_EXPIRED = "L2_EXPIRED"  # 授权过期
    L3_REDISTRIBUTION = "L3_REDISTRIBUTION"  # 再分发违规


@dataclass(frozen=True)
class LicenseAuditFinding:
    """一条违规发现。"""

    level: ViolationLevel
    detail: str
    action: str  # 处置动作（§5.3 表格）


@dataclass(frozen=True)
class LicenseAuditReport:
    """单源审计报告（不可变）。"""

    source_id: str
    compliant: bool
    findings: tuple[LicenseAuditFinding, ...]
    effective_permitted_use: frozenset[str]  # 实际生效的允许用途（含保守降级）
    audited_at: datetime
    detail: str = ""


@dataclass(frozen=True)
class SourceLicense:
    """解析后的授权条款（compliance 段缺失时 fields 为空、uses 走保守默认）。"""

    source_id: str
    has_compliance_section: bool
    permitted_use: frozenset[str]
    redistribution_allowed: bool
    expiry: date | None
    raw: dict = field(default_factory=dict)


class LicenseUsageAuditor:
    """授权使用审计器。

    Args:
        registry_path: data_asset_registry.yaml 路径（默认主仓真源）。
        logger: 合规日志。
    """

    def __init__(
        self,
        registry_path: Path | None = None,
        logger: ComplianceLogger | None = None,
    ) -> None:
        self._registry_path = registry_path or DEFAULT_REGISTRY_PATH
        self._logger = logger or ComplianceLogger()

    def load_source(self, source_id: str) -> SourceLicense:
        """读取某源的授权条款；未登记/缺段走保守默认。"""
        sources = self._load_sources()
        entry = sources.get(source_id)
        if entry is None:
            raise LicenseAuditError(
                f"数据源未登记: {source_id}",
                details={"source_id": source_id, "registry": str(self._registry_path)},
            )
        return self._parse(source_id, entry)

    def audit(
        self,
        source_id: str,
        actual_uses: set[str],
        *,
        today: date | None = None,
    ) -> LicenseAuditReport:
        """核对实际使用方式是否 ∈ permitted_use，输出审计报告并落 compliance_log。

        Args:
            source_id: 数据源 ID（SRC-XXX-NNN）。
            actual_uses: 实际用途集合（模块消费方式，由 depgraph path 反查供给）。
            today: 日期注入（测试用）。
        """
        today = today or date.today()
        lic = self.load_source(source_id)
        findings: list[LicenseAuditFinding] = []

        # L2 授权过期（Fail-Closed，最优先）
        if lic.expiry is not None and lic.expiry < today:
            findings.append(
                LicenseAuditFinding(
                    ViolationLevel.L2_EXPIRED,
                    f"授权到期日 {lic.expiry.isoformat()} 已过（{today.isoformat()}）仍消费",
                    "立即切断数据流（Fail-Closed）+ 告警",
                )
            )
        # L3 再分发违规
        if "redistribution" in actual_uses and not lic.redistribution_allowed:
            findings.append(
                LicenseAuditFinding(
                    ViolationLevel.L3_REDISTRIBUTION,
                    "存在再分发/对外发布用途但条款不允许",
                    "人工处置 + 条款复核 + 功能下线评估（联动 §6 门禁）",
                )
            )
        # L1 超范围使用
        for use in sorted(actual_uses - VALID_USES):
            findings.append(
                LicenseAuditFinding(
                    ViolationLevel.L1_SCOPE,
                    f"未知用途 '{use}'（不在合法用途词表）",
                    "切断该用途数据流 + Warning + 限期整改",
                )
            )
        for use in sorted((actual_uses - {"redistribution"}) & VALID_USES):
            if use not in lic.permitted_use:
                findings.append(
                    LicenseAuditFinding(
                        ViolationLevel.L1_SCOPE,
                        f"用途 '{use}' 超出授权范围 {sorted(lic.permitted_use)}"
                        + ("" if lic.has_compliance_section else "（缺 compliance 段，保守默认）"),
                        "切断该用途数据流 + Warning + 限期整改（升级授权或下线用途）",
                    )
                )

        report = LicenseAuditReport(
            source_id=source_id,
            compliant=not findings,
            findings=tuple(findings),
            effective_permitted_use=lic.permitted_use,
            audited_at=datetime.now(timezone.utc),
            detail="" if lic.has_compliance_section else "缺 compliance 段，按仅 backtest 保守假设",
        )
        self._logger.log(
            "LICENSE_AUDIT",
            "license_usage_auditor",
            {
                "source_id": source_id,
                "compliant": report.compliant,
                "findings": [{"level": f.level.value, "detail": f.detail, "action": f.action} for f in findings],
                "actual_uses": sorted(actual_uses),
                "effective_permitted_use": sorted(lic.permitted_use),
            },
        )
        return report

    def review_due(self, source_id: str, *, today: date | None = None) -> bool:
        """是否到复核期（registered_at + review_cycle_days ≤ today）。

        compliance 段缺失 → True（需补登复核）。
        """
        today = today or date.today()
        lic = self.load_source(source_id)
        if not lic.has_compliance_section:
            return True
        registered = lic.raw.get("registered_at")
        cycle = int(lic.raw.get("review_cycle_days") or 90)
        if registered is None:
            return True
        reg_date = registered if isinstance(registered, date) else date.fromisoformat(str(registered))
        return (today - reg_date).days >= cycle

    def _load_sources(self) -> dict[str, dict]:
        if not self._registry_path.exists():
            raise LicenseAuditError(f"登记表不可读（Fail-Closed）: {self._registry_path}")
        data = yaml.safe_load(self._registry_path.read_text(encoding="utf-8"))
        return {s["source_id"]: s for s in data.get("sources", [])}

    @staticmethod
    def _parse(source_id: str, entry: dict) -> SourceLicense:
        comp = entry.get("compliance")
        if not isinstance(comp, dict):
            # legacy 自由文本 / 缺段 → 保守默认（§5.3 降级）
            return SourceLicense(
                source_id=source_id,
                has_compliance_section=False,
                permitted_use=CONSERVATIVE_DEFAULT_USES,
                redistribution_allowed=False,
                expiry=None,
                raw={},
            )
        expiry_raw = comp.get("expiry")
        expiry: date | None = None
        if expiry_raw:
            expiry = expiry_raw if isinstance(expiry_raw, date) else date.fromisoformat(str(expiry_raw))
        uses = comp.get("permitted_use") or []
        return SourceLicense(
            source_id=source_id,
            has_compliance_section=True,
            permitted_use=frozenset(str(u) for u in uses),
            redistribution_allowed=bool(comp.get("redistribution", False)),
            expiry=expiry,
            raw=dict(comp),
        )
