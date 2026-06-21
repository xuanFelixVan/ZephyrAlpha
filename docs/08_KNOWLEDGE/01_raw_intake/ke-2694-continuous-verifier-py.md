---
module_id: KE-2597---------000
status: active
title: continuous_verifier.py — 新增文件（横切面D组件）
category: module_blueprint
---

# continuous_verifier.py — 新增文件（横切面D组件）

continuous_verifier.py — 新增文件（横切面D组件）
class ContinuousVerifier:
    """
    连续验证器——横切面D，每步重验证Agent身份+权限一致性。
    
    执行节奏：
    - L0→L3 一次性大检查（不变）
    - 横切面D 每步连续性检查（新增）
    - L4 Micro-Verified 每子步骤微验证（新增）
    """
    
    async def verify_step(
        self,
        agent: AgentIdentity,
        action: Action,
        intent_binding: IntentBindingContext,
        session_token: SessionToken,
    ) -> StepVerificationResult:
        """
        每步验证——验证四项一致性：
        1. SessionToken 是否仍然有效（未过期/未被吊销）
        2. Agent Identity 是否与 SessionToken 一致（未被替换）
        3. 当前操作是否在 Intent 信封内
        4. 委托链是否未超深度（MAX_DELEGATION_DEPTH）
        """
        checks = {
            "token_valid": await self._verify_token(session_token),
            "identity_match": await self._verify_identity(agent, session_token),
            "intent_envelope": await self._check_intent_envelope(action, intent_binding),
            "delegation_chain": agent.delegation_depth <= self.MAX_DELEGATION_DEPTH,
        }
        
        all_passed = all(checks.values())
        return StepVerificationResult(
            passed=all_passed,
            checks=checks,
            requires_reauthentication=not checks["token_valid"],
            requires_intent_reconfirmation=not checks["intent_envelope"],
        )
```

---
