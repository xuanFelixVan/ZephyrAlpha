# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain-governance/audit-trail/blueprint.md
# [MODULE] zephyr.gov_audit.supply_chain_security
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不可变审计记录;密码学完整性;只追加
# [MODIFY-GUARD] docs/03_modules/_domain-governance/audit-trail/blueprint.md;src/zephyr/audit-trail/__init__.py
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] IntegrityError;WriteError
# [TESTS] tests/test_audit_trail/
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: lock_file_path 参数
#   fields: 参数 lock_file_path，类型注解 str
#   code: supply_chain_security.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: last_update 参数
#   fields: 参数 last_update，类型注解 str
#   code: supply_chain_security.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: months_threshold 参数
#   fields: 参数 months_threshold，类型注解 int
#   code: supply_chain_security.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: project_name 参数
#   fields: 参数 project_name，类型注解 str
#   code: supply_chain_security.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① scan_dependencies
#   name_en: scan_dependencies
#   intro: scan_dependencies(lock_file_path) 源码 L111-L116
#   desc: 源码 L111-L116
#   inputs: lock_file_path
#   outputs: SupplyChainReport
# - id: A2
#   name_zh: ② check_vendor_lockin
#   name_en: check_vendor_lockin
#   intro: check_vendor_lockin(last_update, months_threshold) 源码 L119-…
#   desc: 源码 L119-L129
#   inputs: last_update months_threshold
#   outputs: VendorRisk
# - id: A3
#   name_zh: ③ generate_spdx
#   name_en: generate_spdx
#   intro: generate_spdx(project_name, packages) 源码 L132-L143
#   desc: 源码 L132-L143
#   inputs: project_name packages
#   outputs: dict[str, object]
#   （注：A3 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: SupplyChainReport
#   name_en: SupplyChainReport
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# - id: O2
#   name_zh: VendorRisk
#   name_en: VendorRisk
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class VendorRisk(str, Enum):
    OK = "OK"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class SupplyChainReport(BaseModel):
    scanned_at: str = ""
    total_deps: int = 0
    vulnerabilities: list[dict[str, object]] = Field(default_factory=list)
    blocked: bool = False
    last_vendor_update: str | None = None
    vendor_risk: VendorRisk = VendorRisk.OK


def scan_dependencies(lock_file_path: str = "requirements.lock") -> SupplyChainReport:
    report = SupplyChainReport(
        scanned_at=datetime.now(UTC).isoformat(),
    )
    report.total_deps = 0
    return report


def check_vendor_lockin(last_update: str, months_threshold: int = 12) -> VendorRisk:
    try:
        last_dt = datetime.fromisoformat(last_update.replace("Z", "+00:00"))
        age = datetime.now(UTC) - last_dt
        if age > timedelta(days=months_threshold * 30):
            return VendorRisk.CRITICAL
        if age > timedelta(days=(months_threshold - 3) * 30):
            return VendorRisk.WARNING
        return VendorRisk.OK
    except (ValueError, TypeError):
        return VendorRisk.WARNING


def generate_spdx(project_name: str, packages: list[dict[str, str]]) -> dict[str, object]:
    return {
        "SPDXVersion": "SPDX-2.3",
        "DataLicense": "CC0-1.0",
        "SPDXID": f"SPDXRef-{project_name}",
        "name": project_name,
        "packages": packages,
        "creationInfo": {
            "created": datetime.now(UTC).isoformat(),
            "creators": ["Tool: ZephyrAlpha supply_chain_security.py"],
        },
    }
