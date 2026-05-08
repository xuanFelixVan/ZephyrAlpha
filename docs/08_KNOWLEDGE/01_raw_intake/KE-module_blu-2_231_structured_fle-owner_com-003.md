---
module_id: KE-module_blu-2_231_structured_fle-owner_com-003
title: 2.231 Structured FLE-Owner Communication Protocol - fle_owner_comm_protocol.py (
category: module_blueprint
---

# 2.231 Structured FLE-Owner Communication Protocol - fle_owner_comm_protocol.py (

2.231 Structured FLE-Owner Communication Protocol - fle_owner_comm_protocol.py (🆕 v0.21.0 - 盲点280 — FLE到Owner的结构化通信协议)

**致命问题**：FLE通过Feishu/SMS/Email/VS Code通知Owner——但这些通知是非结构化的自然语言文本。Owner收到一条通知后需要"parse"文本→理解severity→找上下文→决定action。这在高频triage场景下效率极低。需要结构化的、机器+人类双可读的通信协议——每条通知有标准的urgency level、expected_owner_response_time、triaging_steps、fallback_if_no_response。
**对标**：PagerDuty Incident Priority + OpsGenie Alert Protocol + ITSM Incident Classification + NL2JSON Structured AI Notifications

```python
@dataclass
class FLEOwnerNotification:
    notification_id: str
    urgency: str           # "CRITICAL_P1"|"HIGH_P2"|"MEDIUM_P3"|"LOW_P4"|"INFO_P5"
    expected_response_time: str  # "IMMEDIATE(<5min)"|"URGENT(<30min)"|"TODAY(<8h)"|"WEEKLY"
    fle_decision_summary: str    # ≤50字→Owner 3秒理解
    fle_confidence: float        # 0-1→FLE对此决定的自信度
    owner_actions_required: list[str]  # ["APPROVE","REVIEW","ACK_ONLY","NO_ACTION"]
    fallback_if_no_response: str  # "FLE_WILL_AUTO_EXECUTE"|"FLE_WILL_ESCALATE"|"FLE_WILL_DEFER"
    triaging_checklist: list[str]  # Owner快速验证的3步checklist
    escalation_contact: str | None
    ttl_seconds: int             # 过期时间→fallback action自动触发

class FLEOwnerCommProtocol:
    URGENCY_MAP: dict[str, tuple[str, int]] = {
        "SEVERITY_CRITICAL+P95+CONFIDENCE>0.9": ("CRITICAL_P1", 300),
        "SEVERITY_HIGH+CONFIDENCE>0.7": ("HIGH_P2", 1800),
        "SEVERITY_MEDIUM+CONFIDENCE>0.5": ("MEDIUM_P3", 28800),
        "SEVERITY_LOW": ("LOW_P4", 604800),
    }

    async def compose_structured_notification(self,
                                                decision: FLEDecision) -> FLEOwnerNotification:
        urgency_tuple = self._classify_urgency(decision)
        notif = FLEOwnerNotification(
            notification_id=str(uuid.uuid4()),
            urgency=urgency_tuple[0],
            expected_response_time=self._format_response_time(urgency_tuple[1]),
            fle_decision_summary=self._generate_50char_summary(decision),
            fle_confidence=decision.confidence,
            owner_actions_required=self._required_actions(decision, urgency_tuple[0]),
            fallback_if_no_response=self._fallback_strategy(decision, urgency_tuple),
            triaging_checklist=self._generate_triage_checklist(decision),
            escalation_contact=self.owner_absence_mode.current_absence.escalation_contact
                if self.owner_absence_mode.current_absence else None,
            ttl_seconds=self._compute_ttl(decision, urgency_tuple[1]))
        # TTL timer: 若Owner未在ttl内响应→执行fallback
        asyncio.create_task(self._arm_ttl_fallback(notif))
        return notif

    async def _arm_ttl_fallback(self, notif: FLEOwnerNotification):
        await asyncio.sleep(notif.ttl_seconds)
        acked = await self._check_if_acked(notif.notification_id)
        if not acked:
            if notif.fallback_if_no_response == "FLE_WILL_AUTO_EXECUTE":
                self.FLE.log_info("OWNER_NO_RESPONSE_AUTO_EXECUTING",
           
