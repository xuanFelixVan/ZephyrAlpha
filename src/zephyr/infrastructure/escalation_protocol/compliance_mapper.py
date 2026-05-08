"""Compliance Mapper — D-022-13 合规映射器: 操作→法规(SOX/GDPR/MiFID)映射+审计迹。"""
from __future__ import annotations

COMPLIANCE_MAP={
    "modify_financial_data":{"sox":True,"gdpr":False,"mifid":True},
    "access_personal_data":{"sox":False,"gdpr":True,"mifid":False},
    "execute_trade":{"sox":True,"gdpr":False,"mifid":True},
    "delete_audit_log":{"sox":True,"gdpr":False,"mifid":True},
}

class ComplianceMapper:
    def check(self,operation:str)->dict:
        return COMPLIANCE_MAP.get(operation,{"sox":False,"gdpr":False,"mifid":False})

    def requires_escalation(self,operation:str)->bool:
        check=self.check(operation)
        return any(check.values())
