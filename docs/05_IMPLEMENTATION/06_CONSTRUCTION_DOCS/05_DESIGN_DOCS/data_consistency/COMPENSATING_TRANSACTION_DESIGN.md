---
module_id: IMPL_DOC_003-02
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕ­ﻟﮒﺝﮔﭘﮔﮒﺕ?
responsibility:
  - 实施指南、部署文档
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮒ؟ﮔﺛﮔ ﮒ
applicable_scope: Sagaﻟ۰۴ﮒﺟﻛﭦﮒ۰ﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰
compliance_level: ﻛﺕﻛﺕﮔﭦﮔﮔ ﮒ
parent_document: ../INDEX.md
implementation_status: ﻟﺟﻟ۰ﻛﺕ?
---
---


# ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> Sagaﮔ۷۰ﮒﺙﻟ۰۴ﮒﺟﻛﭦﮒ۰ﻝﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰ﻛﺕﮒ؟ﻝﺍﻟ۶ﻟ
>
> **ﮔ ﺕﮒﺟﮒﮒ**: ﮒﺗﻝ­ﮔ۶ﻙﮒﺁﻠﻟﺁﮔ۶ﻙﻛﺕﮒ۰ﻟﺁ­ﻛﺗﮒ؟ﮔﺑﮔ?
> **ﻟ؟ﺝﻟ؟۰ﻝ؟ﮔ **: ﻛﺟﻟﺁﮔﺍﮔ؟ﻛﺕﻟﺑﮔ۶ﺅﺙﮔﺁﮔﻟ۹ﮒ۷ﮔ۱ﮒ۳ﺅﺙﮔﮒﺍﮒﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱
> **ﮔﮔﺁﮔﭘﮔ?*: ﻠﮒﭦﻟ۰۴ﮒﺟ + ﻝﭘﮔﮔﭦ + ﻠﻟﺁﮔﭦﮒﭘ + ﻝﮔ۶ﮒﻟ­۵

**ﻝﮔ؛**: v1.0
**ﮔﺑﮔﺍ**: 2026-04-02
**Layer**: Layer 4 (ﮔ۶ﻟ۰ﮒﺎ?
**ﻛﺙﮒﻝﭦ?*: P1 - ﮔﺍﮔ؟ﻛﺕﻟﺑﮔ۶ﮔ ﺕﮒﺟﻛﺟﻠ?

---

## 1. ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮔ۵ﻟﺟﺍ

### 1.1 ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮒ؟ﻛﺗ

**ﻟ۰۴ﮒﺟﻛﭦﮒ۰**ﺅﺙCompensation TransactionﺅﺙﮔﺁSagaﮔ۷۰ﮒﺙﻛﺕ­ﻝﮔ ﺕﮒﺟﮔﭦﮒﭘﺅﺙﻝ۷ﻛﭦﮔ۳ﻠﮒﺓﺎﮔﮒﮔ۶ﻟ۰ﻝﮔ؛ﮒﺍﻛﭦﮒ۰ﺅﺙﻛﺟﻟﺁﮒ۷ﮒﮒﺕﮒﺙﻛﭦﮒ۰ﮒ۳ﺎﻟﺑ۴ﮔﭘﮔﺍﮔ؟ﻝﻛﺕﻟﺑﮔ۶ﻙ?

```python
class CompensationTransaction:
    """ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮒ؟ﻛﺗ"""
    
    def __init__(self, original_tx_id: str, participant_id: str):
        self.original_tx_id = original_tx_id  # ﮒﻛﭦﮒ۰ID
        self.participant_id = participant_id   # ﮒﻛﺕﮔﺗID
        self.compensation_type: str            # ﻟ۰۴ﮒﺟﻝﺎﭨﮒ
        self.compensation_data: Dict           # ﻟ۰۴ﮒﺟﮔﺍﮔ؟
        self.status: str = "pending"           # ﻝﭘﮔ? pending, executing, completed, failed
        self.retry_count: int = 0              # ﻠﻟﺁﮔ؛۰ﮔﺍ
        self.max_retries: int = 3              # ﮔﮒ۳۶ﻠﻟﺁﮔ؛۰ﮔ?
```

### 1.2 ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﻟ؟ﺝﻟ؟۰ﮒﮒ

| ﮒﮒ | ﮔﻟﺟﺍ | ﮒ؟ﻝﺍﻟ۵ﮔﺎ |
|------|------|----------|
| **ﮒﺗﻝ­ﮔ?* | ﮒﻛﺕﻟ۰۴ﮒﺟﮔﻛﺛﮔ۶ﻟ۰ﮒ۳ﮔ؛۰ﻝﻝﭨﮔﻝﺕﮒ?| ﻟ۰۴ﮒﺟﮒﮔ۲ﮔ۴ﻝﭘﮔﺅﺙﻠﺟﮒﻠﮒ۳ﻟ۰۴ﮒﺟ |
| **ﮒﺁﻠﻟﺁﮔ?* | ﻟ۰۴ﮒﺟﮒ۳ﺎﻟﺑ۴ﮒﮒﺁﮒ؟ﮒ۷ﻠﻟﺁ | ﮔﮒ۳۶ﻠﻟﺁﮔ؛۰ﮔﺍﻠﮒﭘﺅﺙﮔﮔﺍﻠﻠﺟﻝ­ﻝ?|
| **ﻛﺕﮒ۰ﻟﺁ­ﻛﺗﮒ؟ﮔﺑﮔ?* | ﻟ۰۴ﮒﺟﮔﻛﺛﮒ؟ﮒ۷ﮔ۳ﻠﮒﮔﻛﺛﻝﻛﺕﮒ۰ﮔﮔ | ﮒﮒﮔﻛﺛﻠﭨﻟﺝﮔ­۲ﻝ۰؟ﺅﺙﮔ ﮒﺁﻛﺛﻝ?|
| **ﮒﮒ­ﮔ?* | ﻟ۰۴ﮒﺟﮔﻛﺛﮔ؛ﻟﭦ،ﮔﺁﮒﮒ­ﻝ | ﮒﻛﺕ۹ﮒﻛﺕﮔﺗﻟ۰۴ﮒﺟﻟ۵ﻛﺗﮔﮒﻟ۵ﻛﺗﮒ۳ﺎﻟﺑ?|
| **ﮒﺁﻟ۶ﮔﭖﮔ?* | ﻟ۰۴ﮒﺟﻟﺟﻝ۷ﮒ؟ﮒ۷ﮒﺁﻝﮔ?| ﻟﺁ۵ﻝﭨﮔ۴ﮒﺟﻟ؟ﺍﮒﺛﺅﺙﻝﭘﮔﻟﺓﻟﺕ۹ﺅﺙﮔﮔ ﻝﮔ۶ |

### 1.3 ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮒﻝﺎﭨ

| ﻝﺎﭨﮒ | ﮒﮔﻛﺛ?| ﻟ۰۴ﮒﺟﮔﻛﺛ | ﮒ۳ﮔﮒﭦ?| ﻠ۲ﻠ۸ |
|------|--------|----------|--------|------|
| **ﻝ؟ﮒﮒﮒ?* | ﻟﭖﻠﮒ۱ﮒ  | ﻟﭖﻠﮒﮒﺍ | ﻛﺛ?| ﻛﺛ?|
| **ﮒ۳ﮔﮒﮒ** | ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨ | ﮒﮒﮔﻛﭨﻟﺛ؛ﻝ۶ﭨ | ﻛﺕ?| ﻛﺕ?|
| **ﻝﭘﮔﮔ۱ﮒ۳?* | ﻟ؟۱ﮒﻝﭘﮔﮔﺑﮔ?| ﻝﭘﮔﮒﮔﭨ?| ﻛﺕ?| ﻛﺕ?|
| **ﮔ ﻟ۰۴ﮒ?* | ﮒ۹ﻟﺁﭨﮔﻛﺛ | ﮔ ﻠﻟ۰۴ﮒﺟ | ﻛﺛ?| ﮔ?|

---

## 2. ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮔﭘﮔﻟ؟ﺝﻟ؟۰

### 2.1 ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮔ۶ﻟ۰ﮔﭖﻝ۷

```
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                  ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮔ۶ﻟ۰ﮔﭖﻝ۷                            ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ? 1. ﻟ۰۴ﮒﺟﻟ۶۵ﮒ                                                ﻗ?
ﻗ?    ﻗﻗﻗ ﮒﻛﭦﮒ۰ﮒ۳ﺎﻟﺑ?ﻗ?ﮒﻟﺍﮒ۷ﮔ۲ﮔﭖ?ﻗ?ﻝ۰؟ﮒ؟ﻠﻟ۰۴ﮒﺟﮒﻛﺕﮔﺗﮒﻟ۰?         ﻗ?
ﻗ?                                                            ﻗ?
ﻗ? 2. ﻠﮒﭦﻟ۰۴ﮒﺟﻟﺍﮒﭦ۵                                            ﻗ?
ﻗ?    ﻗﻗﻗ ﮔﮔ۶ﻟ۰ﻠ۰ﭦﮒﭦﻠﮒﭦﮔﮒ ﻗ?ﮒﮒﭨﭦﻟ۰۴ﮒﺟﻟ؟۰ﮒ ﻗ?ﮒ­ﮒ۷ﻟ۰۴ﮒﺟﻟ؟۰ﮒ        ﻗ?
ﻗ?                                                            ﻗ?
ﻗ? 3. ﻟ۰۴ﮒﺟﮔ۶ﻟ۰ﮒﺝ۹ﻝﺁ                                            ﻗ?
ﻗ?    ﻗﻗﻗ ﻟﺓﮒﻛﺕﻛﺕﻛﺕ۹ﮒﻛﺕﮔﺗﻟ۰۴ﮒﺟﻛﭨﭨﮒ۰                            ﻗ?
ﻗ?    ﻗﻗﻗ ﮔ۶ﻟ۰ﻟ۰۴ﮒﺟﮔﻛﺛﺅﺙﮒﺗﻝ­ﮔ۲ﮔ۴ﺅﺙ                            ﻗ?
ﻗ?    ﻗﻗﻗ ﻟ؟ﺍﮒﺛﻟ۰۴ﮒﺟﻝﭨﮔ                                        ﻗ?
ﻗ?    ﻗﻗﻗ ﮒ۳ﮔ­ﮔﺁﮒ۵ﻝﭨ۶ﻝﭨ­ﻟ۰۴ﮒﺟ                                    ﻗ?
ﻗ?                                                            ﻗ?
ﻗ? 4. ﻟ۰۴ﮒﺟﮒ؟ﮔﮒ۳ﻝ                                            ﻗ?
ﻗ?    ﻗﻗﻗ ﮔﮔﻟ۰۴ﮒﺟﮔﮒ?ﻗ?ﮔ ﻟ؟ﺍﮒﻛﭦﮒ۰ﻛﺕﭦfailed                   ﻗ?
ﻗ?    ﻗﻗﻗ ﻠ۷ﮒﻟ۰۴ﮒﺟﮒ۳ﺎﻟﺑ۴ ﻗ?ﻠﻟﺁﮔﭦﮒﭘ                             ﻗ?
ﻗ?    ﻗﻗﻗ ﻠﻟﺁﮒﻛﭨﮒ۳ﺎﻟﺑ۴ ﻗ?ﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱ﮔﭖﻝ۷                         ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
```

### 2.2 ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﻝﭨﻛﭨﭘﻟ؟ﺝﻟ؟۰

#### 2.2.1 ﻟ۰۴ﮒﺟﮒﻟﺍﮒ?(CompensationCoordinator)
```python
class CompensationCoordinator:
    """ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮒﻟﺍﮒ?""
    
    def __init__(self, storage_client, event_bus):
        self.storage = storage_client  # PostgreSQLﮒ؟۱ﮔﺓﻝ،?
        self.event_bus = event_bus     # Redis Streamsﮒ؟۱ﮔﺓﻝ،?
        self.retry_strategy = ExponentialBackoffRetryStrategy()
        
    async def trigger_compensation(self, tx_id: str, failed_participant_id: str) -> CompensationResult:
        """ﻟ۶۵ﮒﻟ۰۴ﮒﺟﻛﭦﮒ۰"""
        # 1. ﻟﺓﮒﮒﺓﺎﮔ۶ﻟ۰ﻝﮒﻛﺕﮔﺗﮒﻟ۰۷ﺅﺙﻠﮒﭦﺅﺙ?
        executed_participants = await self._get_executed_participants(tx_id)
        participants_to_compensate = self._reverse_participants(
            executed_participants, failed_participant_id
        )
        
        # 2. ﮒﮒﭨﭦﻟ۰۴ﮒﺟﻟ؟۰ﮒ
        compensation_plan = CompensationPlan(
            tx_id=tx_id,
            participants=participants_to_compensate,
            status="pending"
        )
        await self._store_compensation_plan(compensation_plan)
        
        # 3. ﮔ۶ﻟ۰ﻟ۰۴ﮒﺟ
        result = await self._execute_compensation_plan(compensation_plan)
        
        # 4. ﮔﺑﮔﺍﮒﻛﭦﮒ۰ﻝﭘﮔ?
        if result.success:
            await self._mark_transaction_failed(tx_id, "compensated")
        else:
            await self._mark_transaction_failed(tx_id, "compensation_failed")
            
        return result
        
    def _reverse_participants(self, executed_participants: List[str], failed_at: str) -> List[str]:
        """ﻝ۰؟ﮒ؟ﻠﻟ۵ﻟ۰۴ﮒﺟﻝﮒﻛﺕﮔﺗﮒﻟ۰۷ﺅﺙﻠﮒﭦﺅﺙ?""
        # ﮔﺝﮒﺍﮒ۳ﺎﻟﺑ۴ﮒﻛﺕﮔﺗﮒ۷ﮒﻟ۰۷ﻛﺕ­ﻝﻛﺛﻝﺛ؟
        try:
            fail_index = executed_participants.index(failed_at)
        except ValueError:
            # ﮒ۳ﺎﻟﺑ۴ﮒﻛﺕﮔﺗﻛﺕﮒ۷ﮒﻟ۰۷ﻛﺕ­ﺅﺙﻠ۱ﮔ۲ﮔ۴ﮒ۳ﺎﻟﺑ۴ﻝ­ﺅﺙ?
            return []
            
        # ﮒﮒ۳ﺎﻟﺑ۴ﮒﻛﺕﮔﺗﻛﺗﮒﻝﮔﮔﮒﻛﺕﮔﺗﺅﺙﮒﮔ؛ﮒ۳ﺎﻟﺑ۴ﮒﻛﺕﮔﺗﺅﺙ?
        to_compensate = executed_participants[:fail_index + 1]
        
        # ﻠﮒﭦﮔﮒﺅﺙﮒﮔ۶ﻟ۰ﻝﮒﻟ۰۴ﮒﺟﺅﺙ?
        return list(reversed(to_compensate))
```

#### 2.2.2 ﻟ۰۴ﮒﺟﮔ۶ﻟ۰ﮒ?(CompensationExecutor)
```python
class CompensationExecutor:
    """ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮔ۶ﻟ۰ﮒ?""
    
    def __init__(self, participant_clients: Dict[str, SagaParticipantClient]):
        self.clients = participant_clients
        self.compensation_log = CompensationLog()
        
    async def execute_compensation(
        self, tx_id: str, participant_id: str
    ) -> CompensationExecutionResult:
        """ﮔ۶ﻟ۰ﮒﻛﺕ۹ﮒﻛﺕﮔﺗﻝﻟ۰۴ﮒﺟ"""
        # 1. ﮔ۲ﮔ۴ﮔﺁﮒ۵ﮒﺓﺎﻟ۰۴ﮒﺟﺅﺙﮒﺗﻝ­ﮔ۶ﺅﺙ
        if await self._is_already_compensated(tx_id, participant_id):
            return CompensationExecutionResult.skipped(
                tx_id, participant_id, "ﮒﺓﺎﻟ۰۴ﮒ?
            )
            
        # 2. ﻟﺓﮒﮒﻛﭦﮒ۰ﻟ؟ﺍﮒﺛ?
        original_tx = await self._get_original_transaction(tx_id, participant_id)
        if not original_tx:
            return CompensationExecutionResult.failed(
                tx_id, participant_id, "ﮒﻛﭦﮒ۰ﻟ؟ﺍﮒﺛﻛﺕﮒ­ﮒ۷"
            )
            
        # 3. ﮔ۶ﻟ۰ﻟ۰۴ﮒﺟﮔﻛﺛ
        try:
            client = self.clients.get(participant_id)
            if not client:
                return CompensationExecutionResult.failed(
                    tx_id, participant_id, "ﮒﻛﺕﮔﺗﮒ؟۱ﮔﺓﻝ،ﺁﻛﺕﮒ­ﮒ?
                )
                
            # ﻟﺍﻝ۷ﮒﻛﺕﮔﺗﻟ۰۴ﮒﺟﮔ۴ﮒ?
            result = await client.compensate_transaction(
                tx_id, original_tx.command_type, original_tx.command_data
            )
            
            # 4. ﻟ؟ﺍﮒﺛﻟ۰۴ﮒﺟﻝﭨﮔ
            await self._log_compensation_result(
                tx_id, participant_id, result, original_tx
            )
            
            return result
            
        except Exception as e:
            # ﻟ؟ﺍﮒﺛﻟ۰۴ﮒﺟﮒﺙﮒﺕﺕ
            await self._log_compensation_exception(
                tx_id, participant_id, str(e), original_tx
            )
            return CompensationExecutionResult.failed(
                tx_id, participant_id, f"ﻟ۰۴ﮒﺟﮔ۶ﻟ۰ﮒﺙﮒﺕﺕ: {str(e)}"
            )
```

#### 2.2.3 ﻟ۰۴ﮒﺟﻠﻟﺁﻝ؟۰ﻝﮒ?(CompensationRetryManager)
```python
class CompensationRetryManager:
    """ﻟ۰۴ﮒﺟﻠﻟﺁﻝ؟۰ﻝﮒ?""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.retry_strategies = {
            "network_error": ExponentialBackoffStrategy(initial_delay=1.0, multiplier=2.0),
            "resource_busy": FixedDelayStrategy(delay=5.0),
            "temporary_failure": ExponentialBackoffStrategy(initial_delay=2.0, multiplier=1.5),
        }
        
    async def schedule_retry(
        self, tx_id: str, participant_id: str, error_type: str, last_error: str
    ) -> Optional[RetrySchedule]:
        """ﻟﺍﮒﭦ۵ﻠﻟﺁ"""
        # ﮔ۲ﮔ۴ﮔﺁﮒ۵ﻟﭘﻟﺟﮔﮒ۳۶ﻠﻟﺁﮔ؛۰ﮔ?
        retry_count = await self._get_retry_count(tx_id, participant_id)
        if retry_count >= self.max_retries:
            return None
            
        # ﻠﮔ۸ﻠﻟﺁﻝ­ﻝ۴
        strategy = self.retry_strategies.get(
            error_type, self.retry_strategies["temporary_failure"]
        )
        
        # ﻟ؟۰ﻝ؟ﻛﺕﮔ؛۰ﻠﻟﺁﮔﭘﻠﺑ
        next_retry_time = strategy.next_retry_time(retry_count)
        
        # ﮒﮒﭨﭦﻠﻟﺁﻟ؟۰ﮒ
        schedule = RetrySchedule(
            tx_id=tx_id,
            participant_id=participant_id,
            retry_count=retry_count + 1,
            next_retry_time=next_retry_time,
            error_type=error_type,
            last_error=last_error
        )
        
        # ﮒ­ﮒ۷ﻠﻟﺁﻟ؟۰ﮒ
        await self._store_retry_schedule(schedule)
        
        return schedule
        
    async def execute_retry(self, schedule: RetrySchedule) -> RetryResult:
        """ﮔ۶ﻟ۰ﻠﻟﺁ"""
        # ﻝ­ﮒﺝﮒﺍﻠﻟﺁﮔﭘﻠ?
        await self._wait_until(schedule.next_retry_time)
        
        # ﮔ۶ﻟ۰ﻟ۰۴ﮒﺟﻠﻟﺁ
        executor = CompensationExecutor(self.participant_clients)
        result = await executor.execute_compensation(
            schedule.tx_id, schedule.participant_id
        )
        
        # ﮔﺑﮔﺍﻠﻟﺁﻝﭨﮔ
        await self._update_retry_result(schedule, result)
        
        return RetryResult.from_execution_result(result, schedule.retry_count)
```

---

## 3. ﻟ۰۴ﮒﺟﻠﭨﻟﺝﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰

### 3.1 ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﻟ۰۴ﮒﺟ

#### 3.1.1 ﮒﮔﻛﺛﺅﺙﮔﻛﭨﻟﺛ؛ﻝ۶ﭨ
```python
class PositionTransferCommand:
    """ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﮒﺛﻛﭨ۳"""
    
    def __init__(self, source_engine: str, target_engine: str, 
                 symbol: str, quantity: int):
        self.source_engine = source_engine
        self.target_engine = target_engine
        self.symbol = symbol
        self.quantity = quantity
        self.transfer_type = "position_transfer"
        
    async def execute(self) -> TransferResult:
        """ﮔ۶ﻟ۰ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨ"""
        # 1. ﻛﭨﮔﭦﮒﺙﮔﮔ۲ﮒﮔﻛﭨ
        source_result = await self._debit_from_source()
        if not source_result.success:
            return TransferResult.failed(f"ﮔﭦﮒﺙﮔﮔ۲ﮒﮒ۳ﺎﻟﺑ? {source_result.error}")
            
        # 2. ﮒﻝ؟ﮔ ﮒﺙﮔﮒ۱ﮒ ﮔﻛﭨ?
        target_result = await self._credit_to_target()
        if not target_result.success:
            # ﻠﻟ۵ﻟ۰۴ﮒﺟﮔﭦﮒﺙﮔ
            await self._compensate_source()
            return TransferResult.failed(f"ﻝ؟ﮔ ﮒﺙﮔﮒ۱ﮒ ﮒ۳ﺎﻟﺑ۴: {target_result.error}")
            
        return TransferResult.success(
            f"ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﮔﮒ: {self.quantity} {self.symbol}"
        )
```

#### 3.1.2 ﻟ۰۴ﮒﺟﮔﻛﺛﺅﺙﮒﮒﮔﻛﭨﻟﺛ؛ﻝ۶?
```python
class PositionTransferCompensation:
    """ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﻟ۰۴ﮒﺟ"""
    
    def __init__(self, original_command: PositionTransferCommand):
        self.original = original_command
        
    async def compensate(self) -> CompensationResult:
        """ﮔ۶ﻟ۰ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﻟ۰۴ﮒﺟﺅﺙﮒﮒﮔﻛﺛﺅﺙ"""
        # ﮔ۲ﮔ۴ﮒﺛﮒﻝﭘﮔﺅﺙﮒﺗﻝ­ﮔ۶ﺅﺙ
        current_state = await self._check_current_state()
        if current_state.already_compensated:
            return CompensationResult.skipped("ﮒﺓﺎﻟ۰۴ﮒ?)
            
        try:
            # 1. ﻛﭨﻝ؟ﮔ ﮒﺙﮔﮔ۲ﮒﮔﻛﭨﺅﺙﮒﮒﺅﺙ?
            target_debit = await self._debit_from_target()
            if not target_debit.success:
                return CompensationResult.failed(f"ﻝ؟ﮔ ﮒﺙﮔﮔ۲ﮒﮒ۳ﺎﻟﺑ۴: {target_debit.error}")
                
            # 2. ﮒﮔﭦﮒﺙﮔﮒ۱ﮒ ﮔﻛﭨﺅﺙﮒﮒﺅﺙ
            source_credit = await self._credit_to_source()
            if not source_credit.success:
                # ﻠ۷ﮒﻟ۰۴ﮒﺟﮒ۳ﺎﻟﺑ۴ﺅﺙﻠﻟ۵ﻟ؟ﺍﮒﺛﻝﭘﮔ?
                await self._log_partial_compensation()
                return CompensationResult.failed(f"ﮔﭦﮒﺙﮔﮒ۱ﮒ ﮒ۳ﺎﻟﺑ? {source_credit.error}")
                
            # 3. ﮔ ﻟ؟ﺍﻟ۰۴ﮒﺟﮒ؟ﮔ
            await self._mark_compensation_complete()
            
            return CompensationResult.success(
                f"ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﻟ۰۴ﮒﺟﮔﮒ: {self.original.quantity} {self.original.symbol}"
            )
            
        except Exception as e:
            await self._log_compensation_exception(str(e))
            return CompensationResult.failed(f"ﻟ۰۴ﮒﺟﮔ۶ﻟ۰ﮒﺙﮒﺕﺕ: {str(e)}")
```

#### 3.1.3 ﻝﭘﮔﮔ۲ﮔ۴ﻛﺕﮒﺗﻝ­ﮔ?
```python
async def _check_current_state(self) -> CompensationState:
    """ﮔ۲ﮔ۴ﮒﺛﮒﻟ۰۴ﮒﺟﻝﭘﮔﺅﺙﮒﺗﻝ­ﮔ۶ﻛﺟﻠﺅﺙ"""
    # ﮔ۲ﮔ۴ﮔﺁﮒ۵ﮒﺓﺎﻟ؟ﺍﮒﺛﻟ۰۴ﮒﺟﮔﮒ
    compensation_record = await self._get_compensation_record()
    if compensation_record and compensation_record.status == "completed":
        return CompensationState(already_compensated=True)
        
    # ﮔ۲ﮔ۴ﻝ؟ﮔ ﮒﺙﮔﮒﺛﮒﮔﻛﭨ?
    target_position = await self._get_target_position()
    source_position = await self._get_source_position()
    
    # ﮒ۳ﮔ­ﮔﺁﮒ۵ﻠﻟ۵ﻟ۰۴ﮒﺟﺅﺙﻛﺕﮒ۰ﻠﭨﻟﺝﮔ۲ﮔ۴ﺅﺙ
    needs_compensation = await self._needs_compensation(
        target_position, source_position
    )
    
    return CompensationState(
        already_compensated=False,
        needs_compensation=needs_compensation,
        target_position=target_position,
        source_position=source_position
    )
    
async def _needs_compensation(self, target_pos, source_pos) -> bool:
    """ﮒ۳ﮔ­ﮔﺁﮒ۵ﻠﻟ۵ﻟ۰۴ﮒﺟﺅﺙﻛﺕﮒ۰ﻠﭨﻟﺝﺅﺙ?""
    # ﮒ۵ﮔﻝ؟ﮔ ﮒﺙﮔﮔﻛﭨﻟﭘﺏﮒ۳ﮔ۲ﮒﺅﺙﻛﺕﮔﭦﮒﺙﮔﮔﻝ۸ﭦﻠﺑﮒ۱ﮒ ﺅﺙﮒﻠﻟ۵ﻟ۰۴ﮒ?
    target_has_enough = target_pos.available >= self.original.quantity
    source_has_space = source_pos.available + self.original.quantity <= source_pos.max_capacity
    
    return target_has_enough and source_has_space
```

### 3.2 ﻟﭖﻠﻟﺍﮔﺑﻟ۰۴ﮒﺟ

#### 3.2.1 ﮒﮔﻛﺛﺅﺙﻟﭖﻠﻟﺍﮔﺑ
```python
class CapitalAdjustmentCommand:
    """ﻟﭖﻠﻟﺍﮔﺑﮒﺛﻛﭨ۳"""
    
    def __init__(self, engine_id: str, adjustment_type: str, amount: float):
        self.engine_id = engine_id
        self.adjustment_type = adjustment_type  # "increase" ﮔ?"decrease"
        self.amount = amount
        
    async def execute(self) -> AdjustmentResult:
        """ﮔ۶ﻟ۰ﻟﭖﻠﻟﺍﮔﺑ"""
        if self.adjustment_type == "increase":
            return await self._increase_capital()
        elif self.adjustment_type == "decrease":
            return await self._decrease_capital()
        else:
            return AdjustmentResult.failed(f"ﮔ۹ﻝ۴ﻟﺍﮔﺑﻝﺎﭨﮒ: {self.adjustment_type}")
```

#### 3.2.2 ﻟ۰۴ﮒﺟﮔﻛﺛﺅﺙﮒﮒﻟﭖﻠﻟﺍﮔ?
```python
class CapitalAdjustmentCompensation:
    """ﻟﭖﻠﻟﺍﮔﺑﻟ۰۴ﮒﺟ"""
    
    def __init__(self, original_command: CapitalAdjustmentCommand):
        self.original = original_command
        
    async def compensate(self) -> CompensationResult:
        """ﮔ۶ﻟ۰ﻟﭖﻠﻟﺍﮔﺑﻟ۰۴ﮒﺟ"""
        # ﻝ۰؟ﮒ؟ﮒﮒﮔﻛﺛﻝﺎﭨﮒ
        reverse_type = "decrease" if self.original.adjustment_type == "increase" else "increase"
        
        # ﮒﮒﭨﭦﮒﮒﮒﺛﻛﭨ۳
        reverse_command = CapitalAdjustmentCommand(
            engine_id=self.original.engine_id,
            adjustment_type=reverse_type,
            amount=self.original.amount
        )
        
        # ﮔ۶ﻟ۰ﮒﮒﮔﻛﺛ
        try:
            result = await reverse_command.execute()
            if result.success:
                await self._log_compensation_success()
                return CompensationResult.success(
                    f"ﻟﭖﻠﻟﺍﮔﺑﻟ۰۴ﮒﺟﮔﮒ: {self.original.amount}"
                )
            else:
                return CompensationResult.failed(
                    f"ﻟﭖﻠﻟﺍﮔﺑﻟ۰۴ﮒﺟﮒ۳ﺎﻟﺑ۴: {result.error}"
                )
                
        except Exception as e:
            return CompensationResult.failed(f"ﻟ۰۴ﮒﺟﮔ۶ﻟ۰ﮒﺙﮒﺕﺕ: {str(e)}")
```

### 3.3 ﻟ؟۱ﮒﻝﭘﮔﮒﮔ­۴ﻟ۰۴ﮒ?

#### 3.3.1 ﮒﮔﻛﺛﺅﺙﻟ؟۱ﮒﻝﭘﮔﮒﮔ­?
```python
class OrderSyncCommand:
    """ﻟ؟۱ﮒﻝﭘﮔﮒﮔ­۴ﮒﺛﻛﭨ?""
    
    def __init__(self, engine_id: str, order_id: str, new_status: str):
        self.engine_id = engine_id
        self.order_id = order_id
        self.new_status = new_status  # "filled", "cancelled", "rejected"
        
    async def execute(self) -> SyncResult:
        """ﮔ۶ﻟ۰ﻟ؟۱ﮒﻝﭘﮔﮒﮔ­?""
        # ﻟ؟۱ﮒﻝﭘﮔﮒﮔ­۴ﮔﺁﮒ۹ﻟﺁﭨﮔﻛﺛﺅﺙﮔ ﻠﻟ۰۴ﮒﺟ
        # ﻛﺛﻠﻟ۵ﻟ؟ﺍﮒﺛﮒﮔ­۴ﮒﮒﺎﺅﺙﻝ۷ﻛﭦﻛﺕﻟﺑﮔ۶ﮔ۲ﮔ?
        return await self._update_order_status()
```

#### 3.3.2 ﻟ۰۴ﮒﺟﮔﻛﺛﺅﺙﮔ ﻠﻟ۰۴ﮒﺟﺅﺙﮒ۹ﻟﺁﭨﮔﻛﺛﺅﺙ
```python
class OrderSyncCompensation:
    """ﻟ؟۱ﮒﻝﭘﮔﮒﮔ­۴ﻟ۰۴ﮒﺟﺅﺙﮔ ﻠﮒ؟ﻠﻟ۰۴ﮒﺟﺅﺙ?""
    
    def __init__(self, original_command: OrderSyncCommand):
        self.original = original_command
        
    async def compensate(self) -> CompensationResult:
        """ﻟ؟۱ﮒﮒﮔ­۴ﮔ ﻠﻟ۰۴ﮒﺟﺅﺙﮒ۹ﻟ؟ﺍﮒﺛﻟ۰۴ﮒﺟﮒ؟ﮔ"""
        # ﻟ؟۱ﮒﻝﭘﮔﮒﮔ­۴ﮔﺁﮒ۹ﻟﺁﭨﮔﻛﺛﺅﺙﮔﺎ۰ﮔﮒﺁﻛﺛﻝ۷
        # ﮒ۹ﻠﮔ ﻟ؟ﺍﻟ۰۴ﮒﺟﮒ؟ﮔﺅﺙﮔ ﻠﮒ؟ﻠﮔ۶ﻟ۰ﮒﮒﮔﻛﺛ
        await self._log_no_compensation_needed()
        
        return CompensationResult.skipped(
            "ﻟ؟۱ﮒﻝﭘﮔﮒﮔ­۴ﻛﺕﭦﮒ۹ﻟﺁﭨﮔﻛﺛﺅﺙﮔ ﻠﻟ۰۴ﮒﺟ"
        )
```

---

## 4. ﮒﺗﻝ­ﮔ۶ﻟ؟ﺝﻟ؟?

### 4.1 ﮒﺗﻝ­ﮔ۶ﻛﺟﻠﮔﭦﮒ?

#### 4.1.1 ﻟ۰۴ﮒﺟﻝﭘﮔﮔ۲ﮔ?
```python
class IdempotencyChecker:
    """ﮒﺗﻝ­ﮔ۶ﮔ۲ﮔ۴ﮒ۷"""
    
    def __init__(self, storage_client):
        self.storage = storage_client
        
    async def check_compensation_idempotency(
        self, tx_id: str, participant_id: str
    ) -> IdempotencyCheckResult:
        """ﮔ۲ﮔ۴ﻟ۰۴ﮒﺟﮔﻛﺛﻝﮒﺗﻝ­ﮔ?""
        # 1. ﮔ۲ﮔ۴ﻟ۰۴ﮒﺟﻟ؟ﺍﮒﺛﮔﺁﮒ۵ﮒ­ﮒ?
        compensation_record = await self._get_compensation_record(tx_id, participant_id)
        
        if compensation_record:
            # ﻟ؟ﺍﮒﺛﮒ­ﮒ۷ﺅﺙﮔ۲ﮔ۴ﻝﭘﮔ?
            if compensation_record.status == "completed":
                return IdempotencyCheckResult.already_compensated(
                    compensation_record.completed_at
                )
            elif compensation_record.status == "executing":
                return IdempotencyCheckResult.currently_executing(
                    compensation_record.started_at
                )
            elif compensation_record.status == "failed":
                # ﮒ۳ﺎﻟﺑ۴ﻝﭘﮔﮒﺁﻛﭨ۴ﻠﻟﺁ?
                return IdempotencyCheckResult.can_retry(
                    compensation_record.failed_at,
                    compensation_record.error_message
                )
                
        # 2. ﮔ۲ﮔ۴ﻛﺕﮒ۰ﻝﭘﮔ?
        business_state = await self._check_business_state(tx_id, participant_id)
        
        # 3. ﮒ۳ﮔ­ﮔﺁﮒ۵ﻠﻟ۵ﻟ۰۴ﮒ?
        needs_compensation = await self._determine_if_compensation_needed(
            business_state
        )
        
        return IdempotencyCheckResult(
            needs_compensation=needs_compensation,
            business_state=business_state,
            can_proceed=True
        )
```

#### 4.1.2 ﻛﺕﮒ۰ﻝﭘﮔﮔ۲ﮔ?
```python
async def _check_business_state(self, tx_id: str, participant_id: str) -> BusinessState:
    """ﮔ۲ﮔ۴ﻛﺕﮒ۰ﻝﭘﮔ?""
    # ﻟﺓﮒﮒﻛﭦﮒ۰ﻟ؟ﺍﮒﺛ?
    original_tx = await self._get_original_transaction(tx_id, participant_id)
    if not original_tx:
        return BusinessState.error("ﮒﻛﭦﮒ۰ﻟ؟ﺍﮒﺛﻛﺕﮒ­ﮒ۷")
        
    # ﮔ ﺗﮔ؟ﮒﺛﻛﭨ۳ﻝﺎﭨﮒﮔ۲ﮔ۴ﻛﺕﮒﻝﻛﺕﮒ۰ﻝﭘﮔ?
    if original_tx.command_type == "position_transfer":
        return await self._check_position_transfer_state(original_tx)
    elif original_tx.command_type == "capital_adjustment":
        return await self._check_capital_adjustment_state(original_tx)
    elif original_tx.command_type == "order_sync":
        return await self._check_order_sync_state(original_tx)
    else:
        return BusinessState.error(f"ﮔ۹ﻝ۴ﮒﺛﻛﭨ۳ﻝﺎﭨﮒ: {original_tx.command_type}")
        
async def _check_position_transfer_state(self, original_tx) -> BusinessState:
    """ﮔ۲ﮔ۴ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﻝﻛﺕﮒ۰ﻝﭘﮔ?""
    # ﻟﺓﮒﮔﭦﮒﺙﮔﮒﻝ؟ﮔ ﮒﺙﮔﻝﮒﺛﮒﮔﻛﭨ?
    source_position = await self._get_position(
        original_tx.source_engine, original_tx.symbol
    )
    target_position = await self._get_position(
        original_tx.target_engine, original_tx.symbol
    )
    
    # ﮒ۳ﮔ­ﮒﮔﻛﺛﮔﺁﮒ۵ﮒﺓﺎﻝﮔ
    # ﮒ۵ﮔﻝ؟ﮔ ﮒﺙﮔﮔﻛﭨﮒ۱ﮒ ﺅﺙﮔﭦﮒﺙﮔﮔﻛﭨﮒﮒﺍﺅﺙﮒﮒﮔﻛﺛﮒﺓﺎﻝﮔ
    target_increased = target_position.available >= original_tx.quantity
    source_decreased = source_position.available <= source_position.original - original_tx.quantity
    
    if target_increased and source_decreased:
        return BusinessState.operation_effective()
    elif not target_increased and not source_decreased:
        return BusinessState.operation_not_effective()
    else:
        return BusinessState.partially_effective(
            target_increased=target_increased,
            source_decreased=source_decreased
        )
```

#### 4.1.3 ﮒﺗﻝ­ﮔ۶ﻛﭨ۳ﻝ?
```python
class IdempotencyTokenManager:
    """ﮒﺗﻝ­ﮔ۶ﻛﭨ۳ﻝﻝ؟۰ﻝﮒ۷"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        
    async def generate_token(self, tx_id: str, participant_id: str) -> str:
        """ﻝﮔﮒﺗﻝ­ﮔ۶ﻛﭨ۳ﻝ?""
        # ﻛﭨ۳ﻝﮔ ﺙﮒﺙ: tx_id:participant_id:timestamp:random
        timestamp = int(time.time() * 1000)
        random_str = secrets.token_hex(4)
        token = f"{tx_id}:{participant_id}:{timestamp}:{random_str}"
        
        # ﮒ­ﮒ۷ﻛﭨ۳ﻝﺅﺙﻟ؟ﺝﻝﺛ؟ﻟﺟﮔﮔﭘﻠﺑﺅﺙ24ﮒﺍﮔﭘﺅﺙ?
        await self.redis.setex(
            f"idempotency:{token}",
            86400,  # 24ﮒﺍﮔﭘ
            "generated"
        )
        
        return token
        
    async def check_and_consume_token(self, token: str) -> bool:
        """ﮔ۲ﮔ۴ﮒﺗﭘﮔﭘﻟﺑﺗﻛﭨ۳ﻝ"""
        # ﮔ۲ﮔ۴ﻛﭨ۳ﻝﮔﺁﮒ۵ﮒ­ﮒ۷ﻛﺕﮔ۹ﻛﺛﺟﻝ?
        key = f"idempotency:{token}"
        exists = await self.redis.exists(key)
        if not exists:
            return False
            
        # ﻛﺛﺟﻝ۷ﮒﮒ­ﮔﻛﺛﮔ ﻟ؟ﺍﻛﭨ۳ﻝﻛﺕﭦﮒﺓﺎﻛﺛﺟﻝ۷
        # ﻛﺛﺟﻝ۷SETNXﻝ۰؟ﻛﺟﮒ۹ﮔﻝ؛؛ﻛﺕﻛﺕ۹ﮔﭘﻟﺑﺗﮔﮒ?
        used = await self.redis.setnx(f"{key}:used", "1")
        if not used:
            return False  # ﮒﺓﺎﻟ۱،ﮒﭘﻛﭨﻟﺁﺓﮔﺎﮔﭘﻟﺑﺗ
            
        # ﻟ؟ﺝﻝﺛ؟ﻛﺛﺟﻝ۷ﮔﭘﻠﺑ
        await self.redis.expire(f"{key}:used", 86400)
        
        return True
```

### 4.2 ﻟ۰۴ﮒﺟﮔﻛﺛﮒﺗﻝ­ﮔ۶ﮒ؟ﻝ?

#### 4.2.1 ﻟ۰۴ﮒﺟﮔﻛﺛﮒﻟ۲ﮒ?
```python
class IdempotentCompensationWrapper:
    """ﮒﺗﻝ­ﮔ۶ﻟ۰۴ﮒﺟﮔﻛﺛﮒﻟ۲ﮒ۷"""
    
    def __init__(self, compensation_operation, idempotency_checker):
        self.operation = compensation_operation
        self.checker = idempotency_checker
        
    async def execute(self, tx_id: str, participant_id: str) -> CompensationResult:
        """ﮔ۶ﻟ۰ﮒﺗﻝ­ﮔ۶ﻟ۰۴ﮒﺟﮔﻛﺛ?""
        # 1. ﮒﺗﻝ­ﮔ۶ﮔ۲ﮔ?
        check_result = await self.checker.check_compensation_idempotency(
            tx_id, participant_id
        )
        
        if not check_result.can_proceed:
            if check_result.already_compensated:
                return CompensationResult.skipped("ﮒﺓﺎﻟ۰۴ﮒ?)
            elif check_result.currently_executing:
                return CompensationResult.skipped("ﮔ­۲ﮒ۷ﮔ۶ﻟ۰ﻛﺕ?)
            else:
                return CompensationResult.failed(f"ﮒﺗﻝ­ﮔ۶ﮔ۲ﮔ۴ﮒ۳ﺎﻟﺑ? {check_result.reason}")
                
        # 2. ﻟ؟ﺍﮒﺛﻟ۰۴ﮒﺟﮒﺙﮒ۶?
        await self._log_compensation_start(tx_id, participant_id)
        
        try:
            # 3. ﮔ۶ﻟ۰ﻟ۰۴ﮒﺟﮔﻛﺛ
            result = await self.operation.compensate()
            
            # 4. ﻟ؟ﺍﮒﺛﻟ۰۴ﮒﺟﻝﭨﮔ
            if result.success:
                await self._log_compensation_success(tx_id, participant_id, result)
            else:
                await self._log_compensation_failure(tx_id, participant_id, result)
                
            return result
            
        except Exception as e:
            # 5. ﻟ؟ﺍﮒﺛﮒﺙﮒﺕﺕ
            await self._log_compensation_exception(tx_id, participant_id, str(e))
            return CompensationResult.failed(f"ﻟ۰۴ﮒﺟﮔ۶ﻟ۰ﮒﺙﮒﺕﺕ: {str(e)}")
```

#### 4.2.2 ﻟ۰۴ﮒﺟﮔﻛﺛﻝﭘﮔﮔﭦ
```python
class CompensationStateMachine:
    """ﻟ۰۴ﮒﺟﮔﻛﺛﻝﭘﮔﮔﭦﺅﺙﻛﺟﻠﮒﺗﻝ­ﮔ۶ﺅﺙ"""
    
    def __init__(self, storage_client):
        self.storage = storage_client
        
    async def transition_state(
        self, tx_id: str, participant_id: str, 
        from_state: str, to_state: str
    ) -> bool:
        """ﻝﭘﮔﻟﺛ؛ﮔ۱ﺅﺙﮒﮒ­ﮔﻛﺛﺅﺙ?""
        # ﻛﺛﺟﻝ۷ﮔﺍﮔ؟ﮒﭦﻛﭦﮒ۰ﻛﺟﻟﺁﻝﭘﮔﻟﺛ؛ﮔ۱ﻝﮒﮒ­ﮔ?
        async with self.storage.transaction():
            # ﮔ۲ﮔ۴ﮒﺛﮒﻝﭘﮔ?
            current_state = await self._get_current_state(tx_id, participant_id)
            
            if current_state != from_state:
                # ﻝﭘﮔﻛﺕﻝ؛۵ﮒﻠ۱ﮔﺅﺙﻟﺛ؛ﮔ۱ﮒ۳ﺎﻟﺑ?
                return False
                
            # ﮔ۶ﻟ۰ﻝﭘﮔﻟﺛ؛ﮔ?
            await self._update_state(tx_id, participant_id, to_state)
            
            # ﻟ؟ﺍﮒﺛﻝﭘﮔﻟﺛ؛ﮔ۱ﮒﮒ?
            await self._log_state_transition(
                tx_id, participant_id, from_state, to_state
            )
            
            return True
            
    async def get_allowed_transitions(self, current_state: str) -> List[str]:
        """ﻟﺓﮒﮒﻟ؟ﺕﻝﻝﭘﮔﻟﺛ؛ﮔ?""
        transitions = {
            "pending": ["executing", "skipped"],
            "executing": ["completed", "failed", "retrying"],
            "retrying": ["completed", "failed"],
            "completed": [],  # ﻝﭨﮔﺅﺙﻛﺕﮒﻟ؟ﺕﻟﺛ؛ﮔ?
            "failed": ["retrying"],  # ﮒ۳ﺎﻟﺑ۴ﮒﺁﻛﭨ۴ﻠﻟﺁ
            "skipped": []  # ﻝﭨﮔﺅﺙﻛﺕﮒﻟ؟ﺕﻟﺛ؛ﮔ?
        }
        
        return transitions.get(current_state, [])
```

---

## 5. ﻠﻟﺁﮔﭦﮒﭘﻟ؟ﺝﻟ؟۰

### 5.1 ﻠﻟﺁﻝ­ﻝ۴

#### 5.1.1 ﮔﮔﺍﻠﻠﺟﻠﻟﺁﻝ­ﻝ?
```python
class ExponentialBackoffRetryStrategy:
    """ﮔﮔﺍﻠﻠﺟﻠﻟﺁﻝ­ﻝ?""
    
    def __init__(self, initial_delay: float = 1.0, multiplier: float = 2.0,
                 max_delay: float = 60.0, jitter: bool = True):
        self.initial_delay = initial_delay
        self.multiplier = multiplier
        self.max_delay = max_delay
        self.jitter = jitter
        
    def get_delay(self, retry_count: int) -> float:
        """ﻟ؟۰ﻝ؟ﻠﻟﺁﮒﭨﭘﻟﺟ"""
        if retry_count <= 0:
            return 0.0
            
        # ﮔﮔﺍﻟ؟۰ﻝ؟
        delay = self.initial_delay * (self.multiplier ** (retry_count - 1))
        
        # ﻠﮒﭘﮔﮒ۳۶ﮒﭨﭘﻟﺟ?
        delay = min(delay, self.max_delay)
        
        # ﮔﺓﭨﮒ ﮔﮒ۷ﺅﺙﻠﺟﮒﮒ۳ﻛﺕ۹ﮒ؟۱ﮔﺓﻝ،ﺁﮒﮔﭘﻠﻟﺁﺅﺙ?
        if self.jitter:
            jitter_amount = delay * 0.1  # 10%ﮔﮒ۷
            delay += random.uniform(-jitter_amount, jitter_amount)
            delay = max(0.0, delay)  # ﻝ۰؟ﻛﺟﻠﻟﺑ
            
        return delay
```

#### 5.1.2 ﮒﭦﮒ؟ﮒﭨﭘﻟﺟﻠﻟﺁﻝ­ﻝ۴
```python
class FixedDelayRetryStrategy:
    """ﮒﭦﮒ؟ﮒﭨﭘﻟﺟﻠﻟﺁﻝ­ﻝ۴"""
    
    def __init__(self, delay: float = 5.0):
        self.delay = delay
        
    def get_delay(self, retry_count: int) -> float:
        """ﻟ؟۰ﻝ؟ﻠﻟﺁﮒﭨﭘﻟﺟ"""
        return self.delay  # ﮒﭦﮒ؟ﮒﭨﭘﻟﺟ
```

#### 5.1.3 ﻟ۹ﻠﮒﭦﻠﻟﺁﻝ­ﻝ۴
```python
class AdaptiveRetryStrategy:
    """ﻟ۹ﻠﮒﭦﻠﻟﺁﻝ­ﻝ۴"""
    
    def __init__(self):
        self.error_patterns = {}
        self.success_rates = {}
        
    def get_delay(self, retry_count: int, error_type: str) -> float:
        """ﮔ ﺗﮔ؟ﻠﻟﺁﺁﻝﺎﭨﮒﮒﮒﮒﺎﮔﮒﻝﻟ؟۰ﻝ؟ﮒﭨﭘﻟﺟ"""
        # ﻟﺓﮒﻟﺁ۴ﻝﺎﭨﻠﻟﺁﺁﻝﮒﮒﺎﮔﮒﻝ
        success_rate = self.success_rates.get(error_type, 0.5)
        
        # ﮔ ﺗﮔ؟ﮔﮒﻝﻟﺍﮔﺑﮒﭨﭘﻟﺟ?
        if success_rate < 0.3:  # ﮔﮒﻝﻛﺛﺅﺙﮒ۱ﮒ ﮒﭨﭘﻟﺟ?
            base_delay = 10.0
        elif success_rate < 0.7:  # ﮔﮒﻝﻛﺕ­ﻝ­?
            base_delay = 5.0
        else:  # ﮔﮒﻝﻠ،ﺅﺙﮒﮒﺍﮒﭨﭘﻟﺟ?
            base_delay = 2.0
            
        # ﻟﻟﻠﻟﺁﮔ؛۰ﮔﺍ
        delay = base_delay * (1.5 ** (retry_count - 1))
        
        return min(delay, 60.0)  # ﮔﮒ۳?0ﻝ۶?
```

### 5.2 ﻠﻟﺁﻝ؟۰ﻝﮒ?

#### 5.2.1 ﻠﻟﺁﻟﺍﮒﭦ۵ﮒ?
```python
class RetryScheduler:
    """ﻠﻟﺁﻟﺍﮒﭦ۵ﮒ?""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.strategies = {
            "network_error": ExponentialBackoffRetryStrategy(initial_delay=1.0),
            "timeout": ExponentialBackoffRetryStrategy(initial_delay=2.0),
            "resource_busy": FixedDelayRetryStrategy(delay=10.0),
            "temporary_failure": ExponentialBackoffRetryStrategy(initial_delay=3.0),
        }
        
    async def schedule_retry(
        self, tx_id: str, participant_id: str, 
        error_type: str, last_error: str
    ) -> Optional[RetryTask]:
        """ﻟﺍﮒﭦ۵ﻠﻟﺁﻛﭨﭨﮒ۰"""
        # ﻟﺓﮒﮒﺛﮒﻠﻟﺁﮔ؛۰ﮔﺍ
        retry_count = await self._get_retry_count(tx_id, participant_id)
        
        # ﮔ۲ﮔ۴ﮔﺁﮒ۵ﻟﭘﻟﺟﮔﮒ۳۶ﻠﻟﺁﮔ؛۰ﮔ?
        if retry_count >= self._get_max_retries(error_type):
            return None
            
        # ﻠﮔ۸ﻠﻟﺁﻝ­ﻝ۴
        strategy = self.strategies.get(error_type, self.strategies["temporary_failure"])
        
        # ﻟ؟۰ﻝ؟ﻛﺕﮔ؛۰ﻠﻟﺁﮔﭘﻠﺑ
        delay = strategy.get_delay(retry_count)
        next_retry_time = datetime.now() + timedelta(seconds=delay)
        
        # ﮒﮒﭨﭦﻠﻟﺁﻛﭨﭨﮒ۰
        task = RetryTask(
            tx_id=tx_id,
            participant_id=participant_id,
            retry_count=retry_count + 1,
            scheduled_time=next_retry_time,
            error_type=error_type,
            last_error=last_error
        )
        
        # ﮒ­ﮒ۷ﻠﻟﺁﻛﭨﭨﮒ۰
        await self._store_retry_task(task)
        
        return task
```

#### 5.2.2 ﻠﻟﺁﮔ۶ﻟ۰ﮒ?
```python
class RetryExecutor:
    """ﻠﻟﺁﮔ۶ﻟ۰ﮒ?""
    
    def __init__(self, compensation_executor: CompensationExecutor):
        self.executor = compensation_executor
        self.retry_log = RetryLog()
        
    async def execute_retry(self, task: RetryTask) -> RetryResult:
        """ﮔ۶ﻟ۰ﻠﻟﺁ"""
        # ﻝ­ﮒﺝﮒﺍﻟ؟۰ﮒﮔﭘﻠ?
        await self._wait_until(task.scheduled_time)
        
        # ﻟ؟ﺍﮒﺛﻠﻟﺁﮒﺙﮒ۶?
        await self.retry_log.log_retry_start(task)
        
        try:
            # ﮔ۶ﻟ۰ﻟ۰۴ﮒﺟﮔﻛﺛ
            result = await self.executor.execute_compensation(
                task.tx_id, task.participant_id
            )
            
            # ﻟ؟ﺍﮒﺛﻠﻟﺁﻝﭨﮔ
            if result.success:
                await self.retry_log.log_retry_success(task, result)
                return RetryResult.success(
                    task.tx_id, task.participant_id, task.retry_count
                )
            else:
                await self.retry_log.log_retry_failure(task, result)
                return RetryResult.failed(
                    task.tx_id, task.participant_id, 
                    task.retry_count, result.error_message
                )
                
        except Exception as e:
            # ﻟ؟ﺍﮒﺛﻠﻟﺁﮒﺙﮒﺕﺕ
            await self.retry_log.log_retry_exception(task, str(e))
            return RetryResult.failed(
                task.tx_id, task.participant_id,
                task.retry_count, f"ﻠﻟﺁﮔ۶ﻟ۰ﮒﺙﮒﺕﺕ: {str(e)}"
            )
```

### 5.3 ﻠﻟﺁﻝﮔ۶ﻛﺕﮒﻟ­?

#### 5.3.1 ﻠﻟﺁﻝﮔ۶ﮔﮔ 
```python
class RetryMetricsCollector:
    """ﻠﻟﺁﻝﮔ۶ﮔﮔ ﮔﭘﻠﮒ?""
    
    def __init__(self, prometheus_client):
        self.prometheus = prometheus_client
        
        # ﮒ؟ﻛﺗﻝﮔ۶ﮔﮔ 
        self.retry_total = self.prometheus.Counter(
            "saga_compensation_retries_total",
            "Total number of compensation retries",
            ["tx_type", "participant", "error_type"]
        )
        
        self.retry_success = self.prometheus.Counter(
            "saga_compensation_retry_success_total",
            "Total number of successful compensation retries",
            ["tx_type", "participant"]
        )
        
        self.retry_duration = self.prometheus.Histogram(
            "saga_compensation_retry_duration_seconds",
            "Duration of compensation retries",
            ["tx_type", "participant"],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
        )
        
    async def record_retry_attempt(
        self, tx_type: str, participant: str, 
        error_type: str, duration: float, success: bool
    ):
        """ﻟ؟ﺍﮒﺛﻠﻟﺁﮒﺍﻟﺁ"""
        # ﻟ؟ﺍﮒﺛﮔﭨﻠﻟﺁﮔ؛۰ﮔ?
        self.retry_total.labels(
            tx_type=tx_type,
            participant=participant,
            error_type=error_type
        ).inc()
        
        # ﻟ؟ﺍﮒﺛﻠﻟﺁﮔﻝﭨ­ﮔﭘﻠﺑ
        self.retry_duration.labels(
            tx_type=tx_type,
            participant=participant
        ).observe(duration)
        
        # ﻟ؟ﺍﮒﺛﮔﮒﻠﻟﺁ
        if success:
            self.retry_success.labels(
                tx_type=tx_type,
                participant=participant
            ).inc()
```

#### 5.3.2 ﻠﻟﺁﮒﻟ­۵ﻟ۶ﮒ
```yaml
# retry_alerts.yaml
alerts:
  - name: HighCompensationRetryRate
    condition: |
      rate(saga_compensation_retries_total[5m]) > 10
      and
      rate(saga_compensation_retry_success_total[5m]) / 
      rate(saga_compensation_retries_total[5m]) < 0.5
    severity: warning
    description: "ﻟ۰۴ﮒﺟﻠﻟﺁﻝﻟﺟﻠ،ﻛﺕﮔﮒﻝﻛﺛ"
    summary: "ﻟ۰۴ﮒﺟﻠﻟﺁﮒﺙﮒﺕﺕ"
    
  - name: CompensationRetryMaxAttempts
    condition: |
      saga_compensation_retries_total - 
      saga_compensation_retry_success_total > 3
    severity: critical
    description: "ﻟ۰۴ﮒﺟﻠﻟﺁﻟﺝﺝﮒﺍﮔﮒ۳۶ﮒﺍﻟﺁﮔ؛۰ﮔ?
    summary: "ﻟ۰۴ﮒﺟﻠﻟﺁﮒ۳ﺎﻟﺑ۴ﻠﻟ۵ﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱?
    
  - name: LongRetryDuration
    condition: |
      histogram_quantile(0.95, 
        rate(saga_compensation_retry_duration_seconds_bucket[5m])
      ) > 10
    severity: warning
    description: "95%ﻝﻟ۰۴ﮒﺟﻠﻟﺁﮔﻝﭨ­ﮔﭘﻠﺑﻟﭘﻟﺟ?0ﻝ۶?
    summary: "ﻟ۰۴ﮒﺟﻠﻟﺁﮔ۶ﻟﺛﻛﺕﻠ"
```

---

## 6. ﻠﻟﺁﺁﮒ۳ﻝﻛﺕﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱?

### 6.1 ﻟ۰۴ﮒﺟﮒ۳ﺎﻟﺑ۴ﮒﻝﺎﭨ

| ﮒ۳ﺎﻟﺑ۴ﻝﺎﭨﮒ | ﮒﮒ  | ﻟ۹ﮒ۷ﮔ۱ﮒ۳ﮒﺁﻟﺛﮔ?| ﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱ﻠﮔﺎ?|
|----------|------|----------------|--------------|
| **ﻛﺕﺑﮔﭘﮔ۶ﮒ۳ﺎﻟﺑ?* | ﻝﺛﻝﭨﮔﮒ۷ﻙﻟﭖﮔﭦﮔﮔﭘﻛﺕﮒﺁﻝ۷ | ﻠ،ﺅﺙﮒﺁﻠﻟﺁﺅﺙ | ﻛﺛ?|
| **ﻛﺕﮒ۰ﻠﭨﻟﺝﮒ۳ﺎﻟﺑ۴** | ﻛﺕﮒ۰ﻟ۶ﮒﮒﺎﻝ۹ﻙﮔﺍﮔ؟ﻛﺕﻛﺕﻟ?| ﻛﺕ­ﺅﺙﻠﮔ۲ﮔ۴ﺅﺙ | ﻛﺕ?|
| **ﻝﺏﭨﻝﭨﻠﻟﺁﺁ** | ﮔﺍﮔ؟ﮒﭦﮔﻠﻙﮔﮒ۰ﮒ؟ﮔ?| ﻛﺛﺅﺙﻠﻛﺟ؟ﮒ۳ﺅﺙ?| ﻠ،?|
| **ﮔﺍﮔ؟ﮔﮒ** | ﮔﺍﮔ؟ﻛﺕ۱ﮒ۳ﺎﻙﮔﮒ?| ﮔﻛﺛ | ﻠ،ﺅﺙﻠﮔﺍﮔ؟ﻛﺟ؟ﮒ۳ﺅﺙ?|

### 6.2 ﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱ﮔﭖﻝ۷

#### 6.2.1 ﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱ﻟ۶۵ﮒﮒ?
```python
class ManualInterventionTrigger:
    """ﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱ﻟ۶۵ﮒﮒ?""
    
    def __init__(self, alert_client, ticket_system_client):
        self.alert = alert_client
        self.ticket = ticket_system_client
        
    async def trigger_intervention(
        self, tx_id: str, reason: str, details: Dict
    ) -> InterventionTicket:
        """ﻟ۶۵ﮒﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱"""
        # 1. ﮔ۲ﮔ۴ﮔﺁﮒ۵ﮒﺓﺎﮒ­ﮒ۷ﮒﺗﺎﻠ۱ﮒﺓ۴ﮒ
        existing_ticket = await self._get_existing_ticket(tx_id)
        if existing_ticket:
            return existing_ticket
            
        # 2. ﮒﮒﭨﭦﮒﺗﺎﻠ۱ﮒﺓ۴ﮒ
        ticket = InterventionTicket(
            tx_id=tx_id,
            reason=reason,
            details=details,
            status="open",
            priority=self._determine_priority(reason),
            created_at=datetime.now()
        )
        
        # 3. ﻛﺟﮒ­ﮒﺓ۴ﮒ
        await self._save_ticket(ticket)
        
        # 4. ﮒﻠﮒﻟ­?
        await self.alert.send_alert(
            f"ﻠﻟ۵ﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱? {reason}",
            f"ﻛﭦﮒ۰ {tx_id} ﻠﻟ۵ﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱ﻙﻟﺁ۵ﮔ? {json.dumps(details)}",
            severity="critical"
        )
        
        return ticket
```

#### 6.2.2 ﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱ﮒﺓ۴ﮒﺓ
```python
class ManualInterventionTool:
    """ﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱ﮒﺓ۴ﮒﺓ"""
    
    def __init__(self, storage_client, engine_clients):
        self.storage = storage_client
        self.engines = engine_clients
        
    async def diagnose_issue(self, tx_id: str) -> DiagnosisReport:
        """ﻟﺁﮔ­ﻠ؟ﻠ۱"""
        # 1. ﻟﺓﮒﻛﭦﮒ۰ﻟﺁ۵ﮔ
        tx_details = await self._get_transaction_details(tx_id)
        
        # 2. ﻟﺓﮒﻟ۰۴ﮒﺟﻝﭘﮔ?
        compensation_state = await self._get_compensation_state(tx_id)
        
        # 3. ﮔ۲ﮔ۴ﮒﮒﺙﮔﻝﭘﮔ?
        engine_states = {}
        for participant in tx_details.participants:
            engine_state = await self._check_engine_state(participant.engine_id)
            engine_states[participant.engine_id] = engine_state
            
        # 4. ﻝﮔﻟﺁﮔ­ﮔ۴ﮒ
        report = DiagnosisReport(
            tx_id=tx_id,
            transaction_state=tx_details.status,
            compensation_state=compensation_state,
            engine_states=engine_states,
            issues=self._identify_issues(tx_details, compensation_state, engine_states),
            recommendations=self._generate_recommendations()
        )
        
        return report
        
    async def fix_issue(self, tx_id: str, action: str, parameters: Dict) -> FixResult:
        """ﻛﺟ؟ﮒ۳ﻠ؟ﻠ۱"""
        # ﮔ ﺗﮔ؟actionﮔ۶ﻟ۰ﻛﺕﮒﻝﻛﺟ؟ﮒ۳ﮔﻛﺛ?
        if action == "force_complete_compensation":
            return await self._force_complete_compensation(tx_id, parameters)
        elif action == "rollback_manually":
            return await self._manual_rollback(tx_id, parameters)
        elif action == "mark_as_resolved":
            return await self._mark_as_resolved(tx_id, parameters)
        elif action == "reset_transaction":
            return await self._reset_transaction(tx_id, parameters)
        else:
            return FixResult.failed(f"ﮔ۹ﻝ۴ﮔﻛﺛ: {action}")
```

---

## 7. ﻝﮔ۶ﻛﺕﮒﺁﻟ۶ﮔﭖﮔ?

### 7.1 ﻝﮔ۶ﮔﮔ 

#### 7.1.1 ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮔﮔ 
```python
COMPENSATION_METRICS = {
    # ﻟ؟۰ﮔﺍﮒ?
    "compensation_triggered_total": "ﻟ۰۴ﮒﺟﻟ۶۵ﮒﮔﭨﮔ؛۰ﮔ?,
    "compensation_success_total": "ﻟ۰۴ﮒﺟﮔﮒﮔﭨﮔ؛۰ﮔ?,
    "compensation_failed_total": "ﻟ۰۴ﮒﺟﮒ۳ﺎﻟﺑ۴ﮔﭨﮔ؛۰ﮔ?,
    "compensation_retry_total": "ﻟ۰۴ﮒﺟﻠﻟﺁﮔﭨﮔ؛۰ﮔ?,
    
    # ﻝﺑﮔﺗﮒ?
    "compensation_duration_seconds": "ﻟ۰۴ﮒﺟﮔ۶ﻟ۰ﮔﭘﻠﺑﮒﮒﺕ",
    "compensation_retry_delay_seconds": "ﻟ۰۴ﮒﺟﻠﻟﺁﮒﭨﭘﻟﺟﮒﮒﺕ",
    
    # ﻛﭨ۹ﻟ۰۷ﻝ?
    "compensation_success_rate": "ﻟ۰۴ﮒﺟﮔﮒﻝ?,
    "compensation_retry_rate": "ﻟ۰۴ﮒﺟﻠﻟﺁﻝ?,
    "compensation_pending_count": "ﮒﺝﮒ۳ﻝﻟ۰۴ﮒﺟﮔﺍﻠ?,
    "compensation_in_progress_count": "ﻟﺟﻟ۰ﻛﺕ­ﻟ۰۴ﮒﺟﮔﺍﻠ?,
}
```

#### 7.1.2 ﻛﺕﮒ۰ﮔﮔ 
```python
BUSINESS_METRICS = {
    # ﮔﻛﭨﻝﺕﮒﺏ
    "position_transfer_compensation_total": "ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﻟ۰۴ﮒﺟﮔ؛۰ﮔﺍ",
    "position_transfer_compensation_success_rate": "ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﻟ۰۴ﮒﺟﮔﮒﻝ?,
    
    # ﻟﭖﻠﻝﺕﮒﺏ
    "capital_adjustment_compensation_total": "ﻟﭖﻠﻟﺍﮔﺑﻟ۰۴ﮒﺟﮔ؛۰ﮔﺍ",
    "capital_adjustment_compensation_success_rate": "ﻟﭖﻠﻟﺍﮔﺑﻟ۰۴ﮒﺟﮔﮒﻝ?,
    
    # ﮒﺙﮔﻝﺕﮒﺏ
    "engine_compensation_total": "ﮒﮒﺙﮔﻟ۰۴ﮒﺟﮔ؛۰ﮔ?,
    "engine_compensation_success_rate": "ﮒﮒﺙﮔﻟ۰۴ﮒﺟﮔﮒﻝ",
}
```

### 7.2 ﮔ۴ﮒﺟﻟ؟ﺍﮒﺛ

#### 7.2.1 ﻝﭨﮔﮒﮔ۴ﮒﺟ?
```python
class CompensationLogger:
    """ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮔ۴ﮒﺟﻟ؟ﺍﮒﺛﮒ?""
    
    def __init__(self):
        self.logger = logging.getLogger("compensation")
        
    async def log_compensation_start(
        self, tx_id: str, participant_id: str, 
        compensation_type: str
    ):
        """ﻟ؟ﺍﮒﺛﻟ۰۴ﮒﺟﮒﺙﮒ۶?""
        self.logger.info(
            "ﻟ۰۴ﮒﺟﮒﺙﮒ۶?,
            extra={
                "tx_id": tx_id,
                "participant_id": participant_id,
                "compensation_type": compensation_type,
                "timestamp": datetime.now().isoformat(),
                "log_type": "compensation_start"
            }
        )
        
    async def log_compensation_result(
        self, tx_id: str, participant_id: str,
        result: CompensationResult, duration: float
    ):
        """ﻟ؟ﺍﮒﺛﻟ۰۴ﮒﺟﻝﭨﮔ"""
        log_data = {
            "tx_id": tx_id,
            "participant_id": participant_id,
            "success": result.success,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat(),
            "log_type": "compensation_result"
        }
        
        if result.success:
            self.logger.info("ﻟ۰۴ﮒﺟﮔﮒ", extra=log_data)
        else:
            log_data["error"] = result.error_message
            self.logger.error("ﻟ۰۴ﮒﺟﮒ۳ﺎﻟﺑ۴", extra=log_data)
```

#### 7.2.2 ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ
```python
class CompensationAuditLogger:
    """ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ"""
    
    def __init__(self, storage_client):
        self.storage = storage_client
        
    async def log_audit_event(
        self, event_type: str, tx_id: str, 
        participant_id: str, user: str, details: Dict
    ):
        """ﻟ؟ﺍﮒﺛﮒ؟۰ﻟ؟۰ﻛﭦﻛﭨﭘ"""
        audit_record = CompensationAuditRecord(
            event_type=event_type,
            tx_id=tx_id,
            participant_id=participant_id,
            user=user,
            details=details,
            timestamp=datetime.now()
        )
        
        # ﮒ­ﮒ۷ﮒﺍﮒ؟۰ﻟ؟۰ﻛﺕﻝ۷ﻟ۰۷
        await self.storage.insert_audit_record(audit_record)
```

---

## 8. ﮔﭖﻟﺁﮔﺗﮔ۰

### 8.1 ﮒﮒﮔﭖﻟﺁ

#### 8.1.1 ﮒﺗﻝ­ﮔ۶ﮔﭖﻟﺁ?
```python
class TestIdempotency:
    """ﮒﺗﻝ­ﮔ۶ﮔﭖﻟﺁ?""
    
    async def test_compensation_idempotency(self):
        """ﮔﭖﻟﺁﻟ۰۴ﮒﺟﮔﻛﺛﻝﮒﺗﻝ­ﮔ?""
        # ﻝ؛؛ﻛﺕﮔ؛۰ﮔ۶ﻟ۰ﻟ۰۴ﮒ?
        result1 = await compensation_executor.execute_compensation(tx_id, participant_id)
        assert result1.success
        
        # ﻝ؛؛ﻛﭦﮔ؛۰ﮔ۶ﻟ۰ﻝﺕﮒﻟ۰۴ﮒﺟﺅﺙﮒﭦﻟﺁ۴ﻟ۱،ﻟﺓﺏﻟﺟﺅﺙ
        result2 = await compensation_executor.execute_compensation(tx_id, participant_id)
        assert result2.skipped
        assert "ﮒﺓﺎﻟ۰۴ﮒ? in result2.message
        
    async def test_partial_compensation_idempotency(self):
        """ﮔﭖﻟﺁﻠ۷ﮒﻟ۰۴ﮒﺟﮒﭦﮔﺁﻝﮒﺗﻝ­ﮔ?""
        # ﮔ۷۰ﮔﻠ۷ﮒﻟ۰۴ﮒﺟﮔﮒﮒﭦﮔﺁ
        await self._setup_partial_compensation_state()
        
        # ﮔ۶ﻟ۰ﻟ۰۴ﮒﺟﺅﺙﮒﭦﻟﺁ۴ﻝﭨ۶ﻝﭨ­ﮒ؟ﮔﮒ۸ﻛﺛﻠ۷ﮒﺅﺙ
        result = await compensation_executor.execute_compensation(tx_id, participant_id)
        assert result.success
```

#### 8.1.2 ﻠﻟﺁﮔﭖﻟﺁ
```python
class TestRetryMechanism:
    """ﻠﻟﺁﮔﭦﮒﭘﮔﭖﻟﺁ"""
    
    async def test_exponential_backoff(self):
        """ﮔﭖﻟﺁﮔﮔﺍﻠﻠﺟﻠﻟﺁ?""
        strategy = ExponentialBackoffRetryStrategy()
        
        delays = [strategy.get_delay(i) for i in range(1, 5)]
        # ﻠ۹ﻟﺁﮒﭨﭘﻟﺟﻝ؛۵ﮒﮔﮔﺍﮒ۱ﻠﺟ
        assert delays[0] == 1.0
        assert delays[1] == 2.0
        assert delays[2] == 4.0
        assert delays[3] == 8.0
        
    async def test_max_retry_limit(self):
        """ﮔﭖﻟﺁﮔﮒ۳۶ﻠﻟﺁﮔ؛۰ﮔﺍﻠﮒ?""
        # ﮔ۷۰ﮔﻟﺟﻝﭨ­ﮒ۳ﺎﻟﺑ۴
        for i in range(3):
            result = await compensation_executor.execute_compensation(tx_id, participant_id)
            assert result.failed
            
        # ﻝ؛؛ﮒﮔ؛۰ﮒﭦﻟﺁ۴ﻛﺕﮒﻠﻟﺁ?
        result = await compensation_executor.execute_compensation(tx_id, participant_id)
        assert result.failed
        assert "ﻟﭘﻟﺟﮔﮒ۳۶ﻠﻟﺁﮔ؛۰ﮔ? in result.error_message
```

### 8.2 ﻠﮔﮔﭖﻟﺁ

#### 8.2.1 ﻝ،ﺁﮒﺍﻝ،ﺁﻟ۰۴ﮒﺟﮔﭖﻟﺁ?
```python
class TestEndToEndCompensation:
    """ﻝ،ﺁﮒﺍﻝ،ﺁﻟ۰۴ﮒﺟﮔﭖﻟﺁ?""
    
    async def test_position_transfer_compensation(self):
        """ﮔﭖﻟﺁﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﻟ۰۴ﮒﺟﻝ،ﺁﮒﺍﻝ،?""
        # 1. ﮔ۶ﻟ۰ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨ
        transfer_result = await position_transfer.execute()
        assert transfer_result.success
        
        # 2. ﮔ۷۰ﮔﮒﻝﭨ­ﮔﻛﺛﮒ۳ﺎﻟﺑ۴ﺅﺙﻟ۶۵ﮒﻟ۰۴ﮒ?
        await self._simulate_subsequent_failure()
        
        # 3. ﻠ۹ﻟﺁﻟ۰۴ﮒﺟﮔ۶ﻟ۰
        compensation_result = await compensation_coordinator.trigger_compensation()
        assert compensation_result.success
        
        # 4. ﻠ۹ﻟﺁﮔﺍﮔ؟ﻛﺕﻟﺑﮔ?
        source_position = await self._get_source_position()
        target_position = await self._get_target_position()
        
        # ﻟ۰۴ﮒﺟﮒﮒﭦﮔ۱ﮒ۳ﮒﺍﻟﺛ؛ﻝ۶ﭨﮒﻝﭘﮔ?
        assert source_position.available == original_source_position
        assert target_position.available == original_target_position
        
    async def test_capital_adjustment_compensation(self):
        """ﮔﭖﻟﺁﻟﭖﻠﻟﺍﮔﺑﻟ۰۴ﮒﺟﻝ،ﺁﮒﺍﻝ،?""
        # ﻝﺎﭨﻛﺙﺙﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﮔﭖﻟﺁ...
        pass
```

#### 8.2.2 ﮔﻠﮔﺏ۷ﮒ۴ﮔﭖﻟﺁ
```python
class TestFaultInjection:
    """ﮔﻠﮔﺏ۷ﮒ۴ﮔﭖﻟﺁ"""
    
    async def test_network_partition_during_compensation(self):
        """ﮔﭖﻟﺁﻟ۰۴ﮒﺟﮔﻠﺑﻝﺛﻝﭨﮒﮒﭦ"""
        # 1. ﮒﺙﮒ۶ﻟ۰۴ﮒ?
        compensation_task = asyncio.create_task(
            compensation_executor.execute_compensation(tx_id, participant_id)
        )
        
        # 2. ﮔﺏ۷ﮒ۴ﻝﺛﻝﭨﮔﻠ
        await self._inject_network_partition()
        
        # 3. ﻠ۹ﻟﺁﻟ۰۴ﮒﺟﮔ­۲ﻝ۰؟ﮒ۳ﻝﻝﺛﻝﭨﮔﻠ
        try:
            result = await asyncio.wait_for(compensation_task, timeout=5.0)
            # ﮒﭦﻟﺁ۴ﻟﭘﮔﭘﮔﻟﺟﮒﻠﮒﺛﻝﻠﻟﺁ?
        except asyncio.TimeoutError:
            pass  # ﻠ۱ﮔﻟ۰ﻛﺕﭦ
            
        # 4. ﮔ۱ﮒ۳ﻝﺛﻝﭨ
        await self._restore_network()
        
        # 5. ﻠ۹ﻟﺁﻟ۰۴ﮒﺟﮒﺁﻛﭨ۴ﮔ۱ﮒ۳
        result = await compensation_executor.execute_compensation(tx_id, participant_id)
        assert result.success or result.skipped
        
    async def test_database_failure_during_compensation(self):
        """ﮔﭖﻟﺁﻟ۰۴ﮒﺟﮔﻠﺑﮔﺍﮔ؟ﮒﭦﮔﻠ?""
        # ﻝﺎﭨﻛﺙﺙﻝﺛﻝﭨﮒﮒﭦﮔﭖﻟﺁ...
        pass
```

### 8.3 ﮔ۶ﻟﺛﮔﭖﻟﺁ

#### 8.3.1 ﻟ۰۴ﮒﺟﮔ۶ﻟﺛﮒﭦﮒﮔﭖﻟﺁ
```python
class TestCompensationPerformance:
    """ﻟ۰۴ﮒﺟﮔ۶ﻟﺛﮔﭖﻟﺁ"""
    
    async def test_compensation_latency(self):
        """ﮔﭖﻟﺁﻟ۰۴ﮒﺟﮒﭨﭘﻟﺟ"""
        latencies = []
        
        for i in range(100):
            start_time = time.time()
            result = await compensation_executor.execute_compensation(
                f"tx_test_{i}", "participant_1"
            )
            end_time = time.time()
            
            assert result.success
            latencies.append(end_time - start_time)
            
        # ﻟ؟۰ﻝ؟ﻝﭨﻟ؟۰ﻛﺟ۰ﮔﺁ
        avg_latency = sum(latencies) / len(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        
        # ﮔ۶ﻟﺛﻟ۵ﮔﺎ: ﮒﺗﺏﮒﮒﭨﭘﻟﺟ < 100ms, P95ﮒﭨﭘﻟﺟ < 200ms
        assert avg_latency < 0.1, f"ﮒﺗﺏﮒﮒﭨﭘﻟﺟﻟﺟﻠ،: {avg_latency}"
        assert p95_latency < 0.2, f"P95ﮒﭨﭘﻟﺟﻟﺟﻠ،: {p95_latency}"
        
    async def test_concurrent_compensation(self):
        """ﮔﭖﻟﺁﮒﺗﭘﮒﻟ۰۴ﮒﺟ"""
        # ﮒﮒﭨﭦﮒ۳ﻛﺕ۹ﮒﺗﭘﮒﻟ۰۴ﮒﺟﻛﭨﭨﮒ۰
        tasks = []
        for i in range(50):
            task = compensation_executor.execute_compensation(
                f"tx_concurrent_{i}", f"participant_{i % 5}"
            )
            tasks.append(task)
            
        # ﮒﺗﭘﮒﮔ۶ﻟ۰
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # ﻠ۹ﻟﺁﮔﮔﻟ۰۴ﮒﺟﮔﮒ?
        success_count = sum(1 for r in results if isinstance(r, CompensationResult) and r.success)
        assert success_count >= 45, f"ﮒﺗﭘﮒﻟ۰۴ﮒﺟﮔﮒﻝﻟﺟﻛﺛ? {success_count}/50"
```

---

## 9. ﮒ؟ﮔﺛﻛﺕﻠ۷ﻝﺛ?

### 9.1 ﻛﺝﻟﭖﻝﭨﻛﭨﭘ

| ﻝﭨﻛﭨﭘ | ﻝﮔ؛ﻟ۵ﮔﺎ | ﻠﻝﺛ؟ﻟ۵ﮔﺎ | ﻠ۷ﻝﺛﺎﮔﺗﮒﺙ |
|------|----------|----------|----------|
| **PostgreSQL** | 12+ | ﻠﻟ۵JSONBﮔﺁﮔﺅﺙﻟ؟ﺝﻝﺛ؟ﮒﻝﻟﺟﮔ۴ﮔﺎ  | ﻝ؛ﻝ،ﻠ۷ﻝﺛﺎﮔﻛﭦﮔﮒ۰ |
| **Redis** | 6.0+ | ﮒﺁﻝ۷Streamsﮒﻟﺛﺅﺙﻠﻝﺛ؟ﮔﻛﺗﮒ | ﻝ؛ﻝ،ﻠ۷ﻝﺛﺎﮔﻛﭦﮔﮒ۰ |
| **Python** | 3.9+ | ﮒ؟ﻟ۲asyncpg, redis-pyﻝ­ﻛﺝﻟﭖ?| ﮒﭦﻝ۷ﮔﮒ۰ﮒ?|
| **ﻝﮔ۶ﻝﺏﭨﻝﭨ** | Prometheus 2.0+ | ﻠﻝﺛ؟ﮔﮒﮒﮒﻟ­۵ﻟ۶ﮒ?| ﻝ؛ﻝ،ﻠ۷ﻝﺛﺎ |

### 9.2 ﻠﻝﺛ؟ﻝ۳ﭦﻛﺝ

#### 9.2.1 ﻟ۰۴ﮒﺟﻠﻝﺛ؟
```yaml
# compensation_config.yaml
compensation:
  # ﻠﻟﺁﻠﻝﺛ؟
  retry:
    max_attempts: 3
    strategies:
      network_error:
        type: exponential_backoff
        initial_delay: 1.0
        multiplier: 2.0
        max_delay: 60.0
        
      resource_busy:
        type: fixed_delay
        delay: 10.0
        
  # ﻟﭘﮔﭘﻠﻝﺛ؟
  timeouts:
    compensation_execution: 30  # ﻝ۶?
    participant_response: 10    # ﻝ۶?
    
  # ﻝﮔ۶ﻠﻝﺛ؟
  monitoring:
    metrics_enabled: true
    detailed_logging: true
    alert_thresholds:
      success_rate: 0.95
      avg_duration: 0.5  # ﻝ۶?
      
  # ﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱ﻠﻝﺛ؟
  manual_intervention:
    auto_trigger: true
    alert_channels:
      - email
      - slack
    escalation_rules:
      - after_retries_exhausted: true
      - after_duration_exceeded: 300  # 5ﮒﻠ
```

#### 9.2.2 ﮔﺍﮔ؟ﮒﭦﻠﻝﺛ?
```yaml
# database_config.yaml
postgresql:
  host: localhost
  port: 5432
  database: saga_compensation
  user: saga_user
  password: ${DB_PASSWORD}
  pool:
    min_size: 5
    max_size: 20
    max_queries: 50000
    max_inactive_connection_lifetime: 300.0
    
  # ﻟ۰۷ﻠﻝﺛ?
  tables:
    compensation_transactions:
      partition_by: month
      retention_months: 12
      
    compensation_logs:
      partition_by: day
      retention_days: 30
      
redis:
  host: localhost
  port: 6379
  stream_prefix: "compensation:"
  retention_days: 7
```

### 9.3 ﻠ۷ﻝﺛﺎﮔﭘﮔ

```
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﻠ۷ﻝﺛﺎﮔﭘﮔ                            ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗ? ﻗ?               ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮔﮒ۰ﻠﻝﺝ۳                          ﻗ? ﻗ?
ﻗ? ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?          ﻗ? ﻗ?
ﻗ? ﻗ? ﻗ? ﻟﻝﺗ1   ﻗ? ﻗ? ﻟﻝﺗ2   ﻗ? ﻗ? ﻟﻝﺗ3   ﻗ?          ﻗ? ﻗ?
ﻗ? ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?          ﻗ? ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗ?                          ﻗ?                                 ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗ? ﻗ?               ﮔﺍﮔ؟ﮒﭦﻛﺕﻝﺙﮒ­ﮒﺎ?                          ﻗ? ﻗ?
ﻗ? ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                 ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?         ﻗ? ﻗ?
ﻗ? ﻗ? ﻗPostgreSQLﻗ?                 ﻗ? Redis   ﻗ?         ﻗ? ﻗ?
ﻗ? ﻗ? ﻗ? ﻠﻝﺝ۳    ﻗ?                 ﻗ? ﻠﻝﺝ۳    ﻗ?         ﻗ? ﻗ?
ﻗ? ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                 ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?         ﻗ? ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗ?                          ﻗ?                                 ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗ? ﻗ?               ﻝﮔ۶ﻛﺕﮒﻟ­۵ﮒﺎ                             ﻗ? ﻗ?
ﻗ? ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?          ﻗ? ﻗ?
ﻗ? ﻗ? ﻗPrometheusﻗ? ﻗ?Grafana  ﻗ? ﻗ?Alert    ﻗ?          ﻗ? ﻗ?
ﻗ? ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?          ﻗ? ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
```

---

## 10. ﻝﭨﺑﮔ۳ﻛﺕﻟﺟﻝﭨ?

### 10.1 ﮔ۴ﮒﺕﺕﻝﭨﺑﮔ۳

#### 10.1.1 ﮒ۴ﮒﭦﺓﮔ۲ﮔ?
```python
class CompensationHealthChecker:
    """ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮒ۴ﮒﭦﺓﮔ۲ﮔ?""
    
    async def check_health(self) -> HealthStatus:
        """ﮔ۲ﮔ۴ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﻝﺏﭨﻝﭨﮒ۴ﮒﭦﺓﻝﭘﮔ?""
        checks = []
        
        # ﮔ۲ﮔ۴ﮔﺍﮔ؟ﮒﭦﻟﺟﮔ۴
        db_ok = await self._check_database_connection()
        checks.append(HealthCheck("database", db_ok))
        
        # ﮔ۲ﮔ۴Redisﻟﺟﮔ۴
        redis_ok = await self._check_redis_connection()
        checks.append(HealthCheck("redis", redis_ok))
        
        # ﮔ۲ﮔ۴ﮒﺝﮒ۳ﻝﻟ۰۴ﮒﺟ
        pending_count = await self._get_pending_compensations()
        checks.append(HealthCheck(
            "pending_compensations", 
            pending_count < 100,
            details={"count": pending_count}
        ))
        
        # ﮔ۲ﮔ۴ﻟ۰۴ﮒﺟﮔﮒﻝ
        success_rate = await self._get_success_rate()
        checks.append(HealthCheck(
            "success_rate",
            success_rate > 0.95,
            details={"rate": success_rate}
        ))
        
        # ﮔﭨﻛﺛﮒ۴ﮒﭦﺓﻝﭘﮔ?
        all_healthy = all(c.healthy for c in checks)
        return HealthStatus(
            healthy=all_healthy,
            checks=checks,
            timestamp=datetime.now()
        )
```

#### 10.1.2 ﮔﺍﮔ؟ﮔﺕﻝ
```python
class CompensationDataCleaner:
    """ﻟ۰۴ﮒﺟﮔﺍﮔ؟ﮔﺕﻝ"""
    
    async def cleanup_old_data(self, retention_days: int = 30):
        """ﮔﺕﻝﮔ۶ﮔﺍﮔ?""
        # ﮔﺕﻝﮔ۶ﻝﻟ۰۴ﮒﺟﻟ؟ﺍﮒﺛ
        await self._cleanup_old_compensations(retention_days)
        
        # ﮔﺕﻝﮔ۶ﻝﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ
        await self._cleanup_old_audit_logs(retention_days)
        
        # ﮔﺕﻝﮔ۶ﻝﻝﮔ۶ﮔﺍﮔ؟
        await self._cleanup_old_metrics(retention_days)
        
    async def archive_data(self, archive_date: str):
        """ﮒﺛﮔ۰۲ﮔﺍﮔ؟"""
        # ﮒﺍﮔﮒ؟ﮔ۴ﮔﮒﻝﮔﺍﮔ؟ﮒﺛﮔ۰۲ﮒﺍﮒﺓﮒ­ﮒ?
        await self._archive_compensations(archive_date)
        await self._archive_logs(archive_date)
```

### 10.2 ﮔﻠﮒ۳ﻝ

#### 10.2.1 ﮒﺕﺕﻟ۶ﮔﻠﮒ۳ﻝ
| ﮔﻠﻝﺍﻟﺎ۰ | ﮒﺁﻟﺛﮒﮒ  | ﮔﮔ۴ﮔ­۴ﻠ۹۳ | ﻟ۶۲ﮒﺏﮔﺗﮔ۰ |
|----------|----------|----------|----------|
| ﻟ۰۴ﮒﺟﮔﮒﻝﻛﺕﻠ?| ﻝﺛﻝﭨﻠ؟ﻠ۱ﻙﮒﺙﮔﮔﻠ?| 1. ﮔ۲ﮔ۴ﻝﺛﻝﭨﻟﺟﮔ?br>2. ﮔ۲ﮔ۴ﮒﺙﮔﻝﭘﮔ?br>3. ﮔ۴ﻝﻠﻟﺁﺁﮔ۴ﮒﺟ | 1. ﻛﺟ؟ﮒ۳ﻝﺛﻝﭨ<br>2. ﻠﮒﺁﮒﺙﮔ<br>3. ﻟﺍﮔﺑﻠﻟﺁﻝ­ﻝ۴ |
| ﻟ۰۴ﮒﺟﮒﭨﭘﻟﺟﮒ۱ﮒ  | ﮔﺍﮔ؟ﮒﭦﮔ۶ﻟﺛﻠ؟ﻠ۱ﻙﻟﭖﮔﭦﻛﺕﻟﭘ?| 1. ﮔ۲ﮔ۴ﮔﺍﮔ؟ﮒﭦﮔ۶ﻟﺛ<br>2. ﮔ۲ﮔ۴ﻝﺏﭨﻝﭨﻟﭖﮔﭦ?br>3. ﮒﮔﮔ۱ﮔ۴ﻟﺁ?| 1. ﻛﺙﮒﮔﺍﮔ؟ﮒﭦ?br>2. ﮔ۸ﮒ؟ﺗﻟﭖﮔﭦ<br>3. ﻛﺙﮒﮔ۴ﻟﺁ۱ |
| ﻟ۰۴ﮒﺟﮒ ﻝ۶ﺁ | ﮒ۳ﻝﻟﺛﮒﻛﺕﻟﭘﺏﻙﻠ۱ﻝﺗﮒ۳ﺎﻟﺑ?| 1. ﮔ۲ﮔ۴ﮒ۳ﻝﻝﭦﺟﻝ۷?br>2. ﮒﮔﮒ۳ﺎﻟﺑ۴ﮒﮒ <br>3. ﮔ۴ﻝﻠﮒﻠﺟﮒﭦ۵ | 1. ﮒ۱ﮒ ﮒ۳ﻝﻟﺛﮒ<br>2. ﻛﺟ؟ﮒ۳ﮔ ﺗﮔ؛ﮒﮒ <br>3. ﻛﺕﺑﮔﭘﮒ۱ﮒ ﻟﭖﮔﭦ |

#### 10.2.2 ﻝﺝﻠﺝﮔ۱ﮒ۳
```python
class CompensationDisasterRecovery:
    """ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﻝﺝﻠﺝﮔ۱ﮒ۳"""
    
    async def recover_from_failure(self, failure_type: str) -> RecoveryResult:
        """ﻛﭨﮔﻠﻛﺕ­ﮔ۱ﮒ۳"""
        if failure_type == "database_outage":
            return await self._recover_from_database_outage()
        elif failure_type == "redis_outage":
            return await self._recover_from_redis_outage()
        elif failure_type == "data_corruption":
            return await self._recover_from_data_corruption()
        else:
            return RecoveryResult.failed(f"ﮔ۹ﻝ۴ﮔﻠﻝﺎﭨﮒ: {failure_type}")
            
    async def _recover_from_database_outage(self) -> RecoveryResult:
        """ﻛﭨﮔﺍﮔ؟ﮒﭦﮔﻠﮔ۱ﮒ۳"""
        # 1. ﻝ­ﮒﺝﮔﺍﮔ؟ﮒﭦﮔ۱ﮒ۳?
        await self._wait_for_database_recovery()
        
        # 2. ﮔ۲ﮔ۴ﮔﺍﮔ؟ﻛﺕﻟﺑﮔ?
        inconsistencies = await self._check_data_consistency()
        
        # 3. ﻛﺟ؟ﮒ۳ﻛﺕﻛﺕﻟﺑﮔﺍﮔ?
        if inconsistencies:
            await self._repair_inconsistencies(inconsistencies)
            
        # 4. ﻠﮔﺍﮒﺁﮒ۷ﻟ۰۴ﮒﺟﮒ۳ﻝ
        await self._restart_compensation_processing()
        
        return RecoveryResult.success("ﮔﺍﮔ؟ﮒﭦﮔﻠﮔ۱ﮒ۳ﮒ؟ﮔ?)
```

---

## ﻠﮒﺛﺅﺙﻝﺕﮒﺏﮔﮔ۰۲ﻝﺑ۱ﮒﺙ?

1. [ﮒ۳ﮒﺙﮔﮔﺍﮔ؟ﻛﺕﻟﺑﮔ۶ﻟ؟ﺝﻟ؟۰ﮔﺗﮔ۰?md](ﮒ۳ﮒﺙﮔﮔﺍﮔ؟ﻛﺕﻟﺑﮔ۶ﻟ؟ﺝﻟ؟۰ﮔﺗﮔ۰?md) - ﻛﺕﭨﻟ؟ﺝﻟ؟۰ﮔﮔ۰?
2. [Sagaﮔ۷۰ﮒﺙﮒ؟ﻝﺍﮔﭖﻝ۷ﮒ?md](Sagaﮔ۷۰ﮒﺙﮒ؟ﻝﺍﮔﭖﻝ۷ﮒ?md) - ﮔﭖﻝ۷ﮒﺝﮔﮔ۰?
3.  - ﮒﺙﮔﻠﻠﮒ۷ﻟ؟ﺝﻟ؟?
4. [STORAGE_TIER.md](05_IMPLEMENTATION/04_INFRASTRUCTURE/STORAGE_TIER.md) - ﮒ­ﮒ۷ﮒﺎﻟ؟ﺝﻟ؟?

---

**ﮔﮔ۰۲ﻝﮔ؛ﮒﮒﺎ**:
- v1.0.0 (2026-04-02): ﮒﮒ۶ﻝﮔ؛ﺅﺙﮒ؟ﮔﺑﻟ۰۴ﮒﺟﻛﭦﮒ۰ﻟ؟ﺝﻟ؟?

**ﮒ؟۰ﮔ ﺕﻟ؟ﺍﮒﺛ**:
- ﮔﭘﮔﮒ؟۰ﮔ ﺕ: ﻠ۵ﮒﺕ­ﻟﮒﺝﮔﭘﮔﮒﺕ?
- ﮔﮔﺁﮒ؟۰ﮔ ? ﮒﺝﮒ؟۰ﮔ ?
- ﮒ؟ﮒ۷ﮒ؟۰ﮔ ﺕ: ﮒﺝﮒ؟۰ﮔ ?

**ﮒﻟ۶ﮔ۶ﮔ۲ﮔ?*:
- ﻗ?ﮒﺗﻝ­ﮔ۶ﻟ؟ﺝﻟ؟۰ﮒ؟ﮔ?
- ﻗ?ﻠﻟﺁﮔﭦﮒﭘﮒ؟ﮒ
- ﻗ?ﻠﻟﺁﺁﮒ۳ﻝﮒ۷ﻠ۱
- ﻗ?ﻝﮔ۶ﮒﺁﻟ۶ﮔﭖﮔ۶ﮒﮒ?
- ﻗ?ﮔﭖﻟﺁﮔﺗﮔ۰ﮒ؟ﮒ۳
- ﻗ?ﻝ؛۵ﮒﻛﺕﻛﺕﮔﭦﮔﮔ ﮒ (ﻠ۱ﻟ؟۰ﮒﻟ۶ﻝﻗ۴95%)