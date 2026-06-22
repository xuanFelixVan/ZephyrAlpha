---
module_id: KE-1837
status: active
title: 2.250 Diagnostic Self-Consistency Verifier - diagnostic_self_consistency.py (🆕 v
category: module_blueprint
---

# 2.250 Diagnostic Self-Consistency Verifier - diagnostic_self_consistency.py (🆕 v

2.250 Diagnostic Self-Consistency Verifier - diagnostic_self_consistency.py (🆕 v0.23.0 - 盲点299 — 同一个异常两次诊断→FLE给出不同答案→诊断不可复现→不可信任)

**致命问题**：LLM的固有属性：非确定性。FLE今天用temperature=0诊断出"CPU_LOAD_DUE_TO_CONNECTION_LEAK"→明天用同样的数据诊断出"CPU_LOAD_DUE_TO_INEFFICIENT_QUERY"。两个诊断都可能合理——但不同。这意味着FLE的诊断没有复现性(reproducibility)。在医学领域，"同一个病人，同一个CT→两个医生的诊断不同"是严重问题。在AIOps中，诊断不可复现→修复不可信→Owner失去了对FLE行为predictability的信念。这不同于decision entropy（多样性监视），这是**同一输入的输出稳定性**。
**对标**：Google AI Test Kitchen Consistency Metrics + FDA Medical Device AI Reproducibility + Google Research Self-Consistency Prompting (Wang et al. 2022) + Pass@k Metrics + Anthropic Model Stability

```python
@dataclass
class ConsistencyTest:
    original_decision_id: str
    replayed_at: datetime
    same_input_checksum: str         # 输入数据的hash→验证输入确实一样
    original_diagnosis: str
    replayed_diagnosis: str
    diagnosis_match: bool
    original_action: str
    replayed_action: str
    action_match: bool
    embedding_similarity: float      # 两个诊断文本embedding的cosine相似度
    semantic_equivalence: bool        # 语义是否等值（cosine>0.92）

class DiagnosticSelfConsistencyVerifier:
    REPLAY_COUNT: int = 3            # 重放次数
    CONSISTENCY_ALERT_THRESHOLD: float = 0.70  # <70%一致→告警
    REPLAY_TEMPERATURE: float = 0.0

    async def verify_diagnostic_consistency(self,
                                              decision_id: str) -> ConsistencyReport:
        original = await self._load_decision(decision_id)
        replays = []
        for _ in range(self.REPLAY_COUNT):
            replayed = await self._replay_diagnosis(
                same_input=original.input_data, temperature=self.REPLAY_TEMPERATURE)
            match = replayed.diagnosis == original.diagnosis
            sim = await self._cosine_similarity(replayed.diagnosis_embedding,
                                                  original.diagnosis_embedding)
            replays.append(ConsistencyTest(
                original_decision_id=decision_id,
                replayed_at=datetime.now(),
                same_input_checksum=hashlib.sha256(original.input_data).hexdigest(),
                original_diagnosis=original.diagnosis,
                replayed_diagnosis=replayed.diagnosis,
                diagnosis_match=match,
                original_action=original.action_type,
                replayed_action=replayed.action_type,
                action_match=replayed.action_type == original.action_type,
                embedding_similarity=sim,
                semantic_equivalence=sim > 0.92))

        consistency = sum(1 for r in replays
                          if r.diagnosis_match or r.semantic_equivalence) / len(replays)
        if consistency < self.CONSISTENCY_ALERT_THRESHOLD:
            self.FLE.notify_owner("DIAGNOSTIC_INCONSISTENCY",
                f"Decision {decision_id} diagnostic consistency={consistency:.0%} "
                f"(<{self.CONSISTENCY_ALERT_THRESHOLD:.0%} threshold). "
                f"Original diagnosis: {original.diagnosis}
