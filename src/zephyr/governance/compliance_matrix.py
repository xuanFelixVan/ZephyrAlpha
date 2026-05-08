from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    EXEMPT = "exempt"
    NON_COMPLIANT = "non_compliant"


class ComplianceItem(BaseModel):
    reg_id: str
    regulation: str
    status: ComplianceStatus
    control: str
    evidence_path: str = ""
    last_audit: Optional[str] = None


COMPLIANCE_MATRIX: list[ComplianceItem] = [
    ComplianceItem(
        reg_id="KYC",
        regulation="KYC — 客户身份识别",
        status=ComplianceStatus.EXEMPT,
        control="个人实盘交易 — 已通过经纪商履行 KYC",
        evidence_path="broker/kyc_confirmation/",
        last_audit=None,
    ),
    ComplianceItem(
        reg_id="AML",
        regulation="AML — 反洗钱",
        status=ComplianceStatus.EXEMPT,
        control="个人实盘交易 — 已通过经纪商履行 AML",
        evidence_path="broker/aml_policy/",
        last_audit=None,
    ),
    ComplianceItem(
        reg_id="MIFID_II",
        regulation="MiFID II — 金融工具市场指令",
        status=ComplianceStatus.EXEMPT,
        control="个人交易豁免 — 不构成系统化内部撮合",
        evidence_path="compliance/mifid_exemption/",
        last_audit=None,
    ),
    ComplianceItem(
        reg_id="GDPR",
        regulation="GDPR — 通用数据保护条例",
        status=ComplianceStatus.COMPLIANT,
        control="data_minimization + L3_Confidential 分级 + 仅本地存储",
        evidence_path="governance/data_classification.py",
        last_audit="2026-05-01",
    ),
    ComplianceItem(
        reg_id="SOX",
        regulation="SOX — 萨班斯法案",
        status=ComplianceStatus.EXEMPT,
        control="N/A personal — 保留5年审计轨迹 + immutable_runtime_assertions",
        evidence_path="journals/audit_trail/",
        last_audit=None,
    ),
]


def get_by_reg_id(reg_id: str) -> Optional[ComplianceItem]:
    for item in COMPLIANCE_MATRIX:
        if item.reg_id == reg_id:
            return item
    return None


def non_compliant_items() -> list[ComplianceItem]:
    return [i for i in COMPLIANCE_MATRIX if i.status == ComplianceStatus.NON_COMPLIANT]


def compliant_items() -> list[ComplianceItem]:
    return [i for i in COMPLIANCE_MATRIX if i.status == ComplianceStatus.COMPLIANT]
