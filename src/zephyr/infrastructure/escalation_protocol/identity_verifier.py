"""Identity Verifier — D-022-12 Agent身份验证器: session_id+role+capability三元组验证。"""
from __future__ import annotations

class IdentityVerifier:
    def verify(self, agent_id:str, session_id:str, claimed_role:str, required_capability:str)->tuple[bool,str]:
        if not session_id or len(session_id)<5:
            return False,"Invalid session_id"
        allowed_roles={"orchestrator":["dispatch_task","invoke_gate"],
                        "script_engine":["report_finding","scan_code"],
                        "knowledge_agent":["query_knowledge","write_knowledge"],
                        "human_owner":["override","emergency_stop","approve"]}
        capabilities=allowed_roles.get(claimed_role,[])
        if required_capability not in capabilities:
            return False,f"Role {claimed_role} lacks capability {required_capability}"
        return True,"OK"

    def validate_session(self, session_id:str)->bool:
        return bool(session_id and len(session_id)>=5)
