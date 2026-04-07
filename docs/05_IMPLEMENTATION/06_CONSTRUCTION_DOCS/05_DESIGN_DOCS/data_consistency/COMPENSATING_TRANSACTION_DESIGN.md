---
module_id: COMPENSATING_TRANSACTION_DESIGN
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
---

﻿---
module_id: IMPL_DOC_003-02
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕﻟﮒﺝﮔﭘﮔﮒﺕ?
responsibility:
  - 实施指南、部署文档
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮒ؟ﮔﺛﮔﮒ
applicable_scope: Sagaﻟ۰۴ﮒﺟﻛﭦﮒ۰ﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰
compliance_level: ﻛﺕﻛﺕﮔﭦﮔﮔﮒ
parent_document: ../INDEX.md
implementation_status: ﻟﺟﻟ۰ﻛﺕ?
---
---


# ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> Sagaﮔ۷۰ﮒﺙﻟ۰۴ﮒﺟﻛﭦﮒ۰ﻝﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰ﻛﺕﮒ؟ﻝﺍﻟ۶ﻟ
>
> **ﮔﺕﮒﺟﮒﮒ**: ﮒﺗﻝﮔ۶ﻙﮒﺁﻠﻟﺁﮔ۶ﻙﻛﺕﮒ۰ﻟﺁﻛﺗﮒ؟ﮔﺑﮔ?
> **ﻟ؟ﺝﻟ؟۰ﻝ؟ﮔ**: ﻛﺟﻟﺁﮔﺍﮔ؟ﻛﺕﻟﺑﮔ۶ﺅﺙﮔﺁﮔﻟ۹ﮒ۷ﮔ۱ﮒ۳ﺅﺙﮔﮒﺍﮒﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱
> **ﮔﮔﺁﮔﭘﮔ?*: ﻠﮒﭦﻟ۰۴ﮒﺟ + ﻝﭘﮔﮔﭦ + ﻠﻟﺁﮔﭦﮒﭘ + ﻝﮔ۶ﮒﻟ۵

**ﻝﮔ؛**: v1.0
**ﮔﺑﮔﺍ**: 2026-04-02
**Layer**: Layer 4 (ﮔ۶ﻟ۰ﮒﺎ?
**ﻛﺙﮒﻝﭦ?*: P1 - ﮔﺍﮔ؟ﻛﺕﻟﺑﮔ۶ﮔﺕﮒﺟﻛﺟﻠ?

---

## 1. ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮔ۵ﻟﺟﺍ

### 1.1 ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮒ؟ﻛﺗ

**ﻟ۰۴ﮒﺟﻛﭦﮒ۰**ﺅﺙCompensation TransactionﺅﺙﮔﺁSagaﮔ۷۰ﮒﺙﻛﺕﻝﮔﺕﮒﺟﮔﭦﮒﭘﺅﺙﻝ۷ﻛﭦﮔ۳ﻠﮒﺓﺎﮔﮒﮔ۶ﻟ۰ﻝﮔ؛ﮒﺍﻛﭦﮒ۰ﺅﺙﻛﺟﻟﺁﮒ۷ﮒﮒﺕﮒﺙﻛﭦﮒ۰ﮒ۳ﺎﻟﺑ۴ﮔﭘﮔﺍﮔ؟ﻝﻛﺕﻟﺑﮔ۶ﻙ?

```python
class CompensationTransaction:
    """ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮒ؟ﻛﺗ"""
    
    def __init__(self, original_tx_id: str, participant_id: str):
        self.original_tx_id = original_tx_id  # ﮒﻛﭦﮒ۰ID
        self.participant_id = participant_id   # ﮒﻛﺕﮔﺗID
        self.compensation_type: str            # ﻟ۰۴ﮒﺟﻝﺎﭨﮒ
        self.compensation_data: Dict           # ﻟ۰۴ﮒﺟﮔﺍﮔ؟
        self.status: str = "pending"           # ﻝﭘﮔ? pending, executing, completed, failed
        self.retry_count: int = 0              # ﻠﻟﺁﮔ؛۰ﮔﺍ
        self.max_retries: int = 3              # ﮔﮒ۳۶ﻠﻟﺁﮔ؛۰ﮔ?
```

### 1.2 ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﻟ؟ﺝﻟ؟۰ﮒﮒ

| ﮒﮒ | ﮔﻟﺟﺍ | ﮒ؟ﻝﺍﻟ۵ﮔﺎ |
|------|------|----------|
| **ﮒﺗﻝﮔ?* | ﮒﻛﺕﻟ۰۴ﮒﺟﮔﻛﺛﮔ۶ﻟ۰ﮒ۳ﮔ؛۰ﻝﻝﭨﮔﻝﺕﮒ?| ﻟ۰۴ﮒﺟﮒﮔ۲ﮔ۴ﻝﭘﮔﺅﺙﻠﺟﮒﻠﮒ۳ﻟ۰۴ﮒﺟ |
| **ﮒﺁﻠﻟﺁﮔ?* | ﻟ۰۴ﮒﺟﮒ۳ﺎﻟﺑ۴ﮒﮒﺁﮒ؟ﮒ۷ﻠﻟﺁ | ﮔﮒ۳۶ﻠﻟﺁﮔ؛۰ﮔﺍﻠﮒﭘﺅﺙﮔﮔﺍﻠﻠﺟﻝﻝ?|
| **ﻛﺕﮒ۰ﻟﺁﻛﺗﮒ؟ﮔﺑﮔ?* | ﻟ۰۴ﮒﺟﮔﻛﺛﮒ؟ﮒ۷ﮔ۳ﻠﮒﮔﻛﺛﻝﻛﺕﮒ۰ﮔﮔ | ﮒﮒﮔﻛﺛﻠﭨﻟﺝﮔ۲ﻝ۰؟ﺅﺙﮔﮒﺁﻛﺛﻝ?|
| **ﮒﮒﮔ?* | ﻟ۰۴ﮒﺟﮔﻛﺛﮔ؛ﻟﭦ،ﮔﺁﮒﮒﻝ | ﮒﻛﺕ۹ﮒﻛﺕﮔﺗﻟ۰۴ﮒﺟﻟ۵ﻛﺗﮔﮒﻟ۵ﻛﺗﮒ۳ﺎﻟﺑ?|
| **ﮒﺁﻟ۶ﮔﭖﮔ?* | ﻟ۰۴ﮒﺟﻟﺟﻝ۷ﮒ؟ﮒ۷ﮒﺁﻝﮔ?| ﻟﺁ۵ﻝﭨﮔ۴ﮒﺟﻟ؟ﺍﮒﺛﺅﺙﻝﭘﮔﻟﺓﻟﺕ۹ﺅﺙﮔﮔﻝﮔ۶ |

### 1.3 ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮒﻝﺎﭨ

| ﻝﺎﭨﮒ | ﮒﮔﻛﺛ?| ﻟ۰۴ﮒﺟﮔﻛﺛ | ﮒ۳ﮔﮒﭦ?| ﻠ۲ﻠ۸ |
|------|--------|----------|--------|------|
| **ﻝ؟ﮒﮒﮒ?* | ﻟﭖﻠﮒ۱ﮒ | ﻟﭖﻠﮒﮒﺍ | ﻛﺛ?| ﻛﺛ?|
| **ﮒ۳ﮔﮒﮒ** | ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨ | ﮒﮒﮔﻛﭨﻟﺛ؛ﻝ۶ﭨ | ﻛﺕ?| ﻛﺕ?|
| **ﻝﭘﮔﮔ۱ﮒ۳?* | ﻟ؟۱ﮒﻝﭘﮔﮔﺑﮔ?| ﻝﭘﮔﮒﮔﭨ?| ﻛﺕ?| ﻛﺕ?|
| **ﮔﻟ۰۴ﮒ?* | ﮒ۹ﻟﺁﭨﮔﻛﺛ | ﮔﻠﻟ۰۴ﮒﺟ | ﻛﺛ?| ﮔ?|

---

## 2. ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮔﭘﮔﻟ؟ﺝﻟ؟۰

### 2.1 ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮔ۶ﻟ۰ﮔﭖﻝ۷

```
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                  ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮔ۶ﻟ۰ﮔﭖﻝ۷                            ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ? 1. ﻟ۰۴ﮒﺟﻟ۶۵ﮒ                                                ﻗ?
ﻗ?    ﻗﻗﻗ ﮒﻛﭦﮒ۰ﮒ۳ﺎﻟﺑ?ﻗ?ﮒﻟﺍﮒ۷ﮔ۲ﮔﭖ?ﻗ?ﻝ۰؟ﮒ؟ﻠﻟ۰۴ﮒﺟﮒﻛﺕﮔﺗﮒﻟ۰?         ﻗ?
ﻗ?                                                            ﻗ?
ﻗ? 2. ﻠﮒﭦﻟ۰۴ﮒﺟﻟﺍﮒﭦ۵                                            ﻗ?
ﻗ?    ﻗﻗﻗ ﮔﮔ۶ﻟ۰ﻠ۰ﭦﮒﭦﻠﮒﭦﮔﮒ ﻗ?ﮒﮒﭨﭦﻟ۰۴ﮒﺟﻟ؟۰ﮒ ﻗ?ﮒﮒ۷ﻟ۰۴ﮒﺟﻟ؟۰ﮒ        ﻗ?
ﻗ?                                                            ﻗ?
ﻗ? 3. ﻟ۰۴ﮒﺟﮔ۶ﻟ۰ﮒﺝ۹ﻝﺁ                                            ﻗ?
ﻗ?    ﻗﻗﻗ ﻟﺓﮒﻛﺕﻛﺕﻛﺕ۹ﮒﻛﺕﮔﺗﻟ۰۴ﮒﺟﻛﭨﭨﮒ۰                            ﻗ?
ﻗ?    ﻗﻗﻗ ﮔ۶ﻟ۰ﻟ۰۴ﮒﺟﮔﻛﺛﺅﺙﮒﺗﻝﮔ۲ﮔ۴ﺅﺙ                            ﻗ?
ﻗ?    ﻗﻗﻗ ﻟ؟ﺍﮒﺛﻟ۰۴ﮒﺟﻝﭨﮔ                                        ﻗ?
ﻗ?    ﻗﻗﻗ ﮒ۳ﮔﮔﺁﮒ۵ﻝﭨ۶ﻝﭨﻟ۰۴ﮒﺟ                                    ﻗ?
ﻗ?                                                            ﻗ?
ﻗ? 4. ﻟ۰۴ﮒﺟﮒ؟ﮔﮒ۳ﻝ                                            ﻗ?
ﻗ?    ﻗﻗﻗ ﮔﮔﻟ۰۴ﮒﺟﮔﮒ?ﻗ?ﮔﻟ؟ﺍﮒﻛﭦﮒ۰ﻛﺕﭦfailed                   ﻗ?
ﻗ?    ﻗﻗﻗ ﻠ۷ﮒﻟ۰۴ﮒﺟﮒ۳ﺎﻟﺑ۴ ﻗ?ﻠﻟﺁﮔﭦﮒﭘ                             ﻗ?
ﻗ?    ﻗﻗﻗ ﻠﻟﺁﮒﻛﭨﮒ۳ﺎﻟﺑ۴ ﻗ?ﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱ﮔﭖﻝ۷                         ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
```

### 2.2 ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﻝﭨﻛﭨﭘﻟ؟ﺝﻟ؟۰

#### 2.2.1 ﻟ۰۴ﮒﺟﮒﻟﺍﮒ?(CompensationCoordinator)
```python
class CompensationCoordinator:
    """ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮒﻟﺍﮒ?""
    
    def __init__(self, storage_client, event_bus):
        self.storage = storage_client  # PostgreSQLﮒ؟۱ﮔﺓﻝ،?
        self.event_bus = event_bus     # Redis Streamsﮒ؟۱ﮔﺓﻝ،?
        self.retry_strategy = ExponentialBackoffRetryStrategy()
        
    async def trigger_compensation(self, tx_id: str, failed_participant_id: str) -> CompensationResult:
        """ﻟ۶۵ﮒﻟ۰۴ﮒﺟﻛﭦﮒ۰"""
        # 1. ﻟﺓﮒﮒﺓﺎﮔ۶ﻟ۰ﻝﮒﻛﺕﮔﺗﮒﻟ۰۷ﺅﺙﻠﮒﭦﺅﺙ?
        executed_participants = await self._get_executed_participants(tx_id)
        participants_to_compensate = self._reverse_participants(
            executed_participants, failed_participant_id
        )
        
        # 2. ﮒﮒﭨﭦﻟ۰۴ﮒﺟﻟ؟۰ﮒ
        compensation_plan = CompensationPlan(
            tx_id=tx_id,
            participants=participants_to_compensate,
            status="pending"
        )
        await self._store_compensation_plan(compensation_plan)
        
        # 3. ﮔ۶ﻟ۰ﻟ۰۴ﮒﺟ
        result = await self._execute_compensation_plan(compensation_plan)
        
        # 4. ﮔﺑﮔﺍﮒﻛﭦﮒ۰ﻝﭘﮔ?
        if result.success:
            await self._mark_transaction_failed(tx_id, "compensated")
        else:
            await self._mark_transaction_failed(tx_id, "compensation_failed")
            
        return result
        
    def _reverse_participants(self, executed_participants: List[str], failed_at: str) -> List[str]:
        """ﻝ۰؟ﮒ؟ﻠﻟ۵ﻟ۰۴ﮒﺟﻝﮒﻛﺕﮔﺗﮒﻟ۰۷ﺅﺙﻠﮒﭦﺅﺙ?""
# ﮔﺝﮒﺍﮒ۳ﺎﻟﺑ۴ﮒﻛﺕﮔﺗﮒ۷ﮒﻟ۰۷ﻛﺕﻝﻛﺛﻝﺛ؟
        try:
            fail_index = executed_participants.index(failed_at)
        except ValueError:
# ﮒ۳ﺎﻟﺑ۴ﮒﻛﺕﮔﺗﻛﺕﮒ۷ﮒﻟ۰۷ﻛﺕﺅﺙﻠ۱ﮔ۲ﮔ۴ﮒ۳ﺎﻟﺑ۴ﻝﺅﺙ?
            return []
            
        # ﮒﮒ۳ﺎﻟﺑ۴ﮒﻛﺕﮔﺗﻛﺗﮒﻝﮔﮔﮒﻛﺕﮔﺗﺅﺙﮒﮔ؛ﮒ۳ﺎﻟﺑ۴ﮒﻛﺕﮔﺗﺅﺙ?
        to_compensate = executed_participants[:fail_index + 1]
        
        # ﻠﮒﭦﮔﮒﺅﺙﮒﮔ۶ﻟ۰ﻝﮒﻟ۰۴ﮒﺟﺅﺙ?
        return list(reversed(to_compensate))
```

#### 2.2.2 ﻟ۰۴ﮒﺟﮔ۶ﻟ۰ﮒ?(CompensationExecutor)
```python
class CompensationExecutor:
    """ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮔ۶ﻟ۰ﮒ?""
    
    def __init__(self, participant_clients: Dict[str, SagaParticipantClient]):
        self.clients = participant_clients
        self.compensation_log = CompensationLog()
        
    async def execute_compensation(
        self, tx_id: str, participant_id: str
    ) -> CompensationExecutionResult:
        """ﮔ۶ﻟ۰ﮒﻛﺕ۹ﮒﻛﺕﮔﺗﻝﻟ۰۴ﮒﺟ"""
# 1. ﮔ۲ﮔ۴ﮔﺁﮒ۵ﮒﺓﺎﻟ۰۴ﮒﺟﺅﺙﮒﺗﻝﮔ۶ﺅﺙ
        if await self._is_already_compensated(tx_id, participant_id):
            return CompensationExecutionResult.skipped(
                tx_id, participant_id, "ﮒﺓﺎﻟ۰۴ﮒ?
            )
            
        # 2. ﻟﺓﮒﮒﻛﭦﮒ۰ﻟ؟ﺍﮒﺛ?
        original_tx = await self._get_original_transaction(tx_id, participant_id)
        if not original_tx:
            return CompensationExecutionResult.failed(
tx_id, participant_id, "ﮒﻛﭦﮒ۰ﻟ؟ﺍﮒﺛﻛﺕﮒﮒ۷"
            )
            
        # 3. ﮔ۶ﻟ۰ﻟ۰۴ﮒﺟﮔﻛﺛ
        try:
            client = self.clients.get(participant_id)
            if not client:
                return CompensationExecutionResult.failed(
tx_id, participant_id, "ﮒﻛﺕﮔﺗﮒ؟۱ﮔﺓﻝ،ﺁﻛﺕﮒﮒ?
                )
                
            # ﻟﺍﻝ۷ﮒﻛﺕﮔﺗﻟ۰۴ﮒﺟﮔ۴ﮒ?
            result = await client.compensate_transaction(
                tx_id, original_tx.command_type, original_tx.command_data
            )
            
            # 4. ﻟ؟ﺍﮒﺛﻟ۰۴ﮒﺟﻝﭨﮔ
            await self._log_compensation_result(
                tx_id, participant_id, result, original_tx
            )
            
            return result
            
        except Exception as e:
            # ﻟ؟ﺍﮒﺛﻟ۰۴ﮒﺟﮒﺙﮒﺕﺕ
            await self._log_compensation_exception(
                tx_id, participant_id, str(e), original_tx
            )
            return CompensationExecutionResult.failed(
                tx_id, participant_id, f"ﻟ۰۴ﮒﺟﮔ۶ﻟ۰ﮒﺙﮒﺕﺕ: {str(e)}"
            )
```

#### 2.2.3 ﻟ۰۴ﮒﺟﻠﻟﺁﻝ؟۰ﻝﮒ?(CompensationRetryManager)
```python
class CompensationRetryManager:
    """ﻟ۰۴ﮒﺟﻠﻟﺁﻝ؟۰ﻝﮒ?""
    
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
        """ﻟﺍﮒﭦ۵ﻠﻟﺁ"""
        # ﮔ۲ﮔ۴ﮔﺁﮒ۵ﻟﭘﻟﺟﮔﮒ۳۶ﻠﻟﺁﮔ؛۰ﮔ?
        retry_count = await self._get_retry_count(tx_id, participant_id)
        if retry_count >= self.max_retries:
            return None
            
# ﻠﮔ۸ﻠﻟﺁﻝﻝ۴
        strategy = self.retry_strategies.get(
            error_type, self.retry_strategies["temporary_failure"]
        )
        
        # ﻟ؟۰ﻝ؟ﻛﺕﮔ؛۰ﻠﻟﺁﮔﭘﻠﺑ
        next_retry_time = strategy.next_retry_time(retry_count)
        
        # ﮒﮒﭨﭦﻠﻟﺁﻟ؟۰ﮒ
        schedule = RetrySchedule(
            tx_id=tx_id,
            participant_id=participant_id,
            retry_count=retry_count + 1,
            next_retry_time=next_retry_time,
            error_type=error_type,
            last_error=last_error
        )
        
# ﮒﮒ۷ﻠﻟﺁﻟ؟۰ﮒ
        await self._store_retry_schedule(schedule)
        
        return schedule
        
    async def execute_retry(self, schedule: RetrySchedule) -> RetryResult:
        """ﮔ۶ﻟ۰ﻠﻟﺁ"""
# ﻝﮒﺝﮒﺍﻠﻟﺁﮔﭘﻠ?
        await self._wait_until(schedule.next_retry_time)
        
        # ﮔ۶ﻟ۰ﻟ۰۴ﮒﺟﻠﻟﺁ
        executor = CompensationExecutor(self.participant_clients)
        result = await executor.execute_compensation(
            schedule.tx_id, schedule.participant_id
        )
        
        # ﮔﺑﮔﺍﻠﻟﺁﻝﭨﮔ
        await self._update_retry_result(schedule, result)
        
        return RetryResult.from_execution_result(result, schedule.retry_count)
```

---

## 3. ﻟ۰۴ﮒﺟﻠﭨﻟﺝﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰

### 3.1 ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﻟ۰۴ﮒﺟ

#### 3.1.1 ﮒﮔﻛﺛﺅﺙﮔﻛﭨﻟﺛ؛ﻝ۶ﭨ
```python
class PositionTransferCommand:
    """ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﮒﺛﻛﭨ۳"""
    
    def __init__(self, source_engine: str, target_engine: str, 
                 symbol: str, quantity: int):
        self.source_engine = source_engine
        self.target_engine = target_engine
        self.symbol = symbol
        self.quantity = quantity
        self.transfer_type = "position_transfer"
        
    async def execute(self) -> TransferResult:
        """ﮔ۶ﻟ۰ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨ"""
        # 1. ﻛﭨﮔﭦﮒﺙﮔﮔ۲ﮒﮔﻛﭨ
        source_result = await self._debit_from_source()
        if not source_result.success:
            return TransferResult.failed(f"ﮔﭦﮒﺙﮔﮔ۲ﮒﮒ۳ﺎﻟﺑ? {source_result.error}")
            
# 2. ﮒﻝ؟ﮔﮒﺙﮔﮒ۱ﮒﮔﻛﭨ?
        target_result = await self._credit_to_target()
        if not target_result.success:
            # ﻠﻟ۵ﻟ۰۴ﮒﺟﮔﭦﮒﺙﮔ
            await self._compensate_source()
return TransferResult.failed(f"ﻝ؟ﮔﮒﺙﮔﮒ۱ﮒﮒ۳ﺎﻟﺑ۴: {target_result.error}")
            
        return TransferResult.success(
            f"ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﮔﮒ: {self.quantity} {self.symbol}"
        )
```

#### 3.1.2 ﻟ۰۴ﮒﺟﮔﻛﺛﺅﺙﮒﮒﮔﻛﭨﻟﺛ؛ﻝ۶?
```python
class PositionTransferCompensation:
    """ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﻟ۰۴ﮒﺟ"""
    
    def __init__(self, original_command: PositionTransferCommand):
        self.original = original_command
        
    async def compensate(self) -> CompensationResult:
        """ﮔ۶ﻟ۰ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﻟ۰۴ﮒﺟﺅﺙﮒﮒﮔﻛﺛﺅﺙ"""
# ﮔ۲ﮔ۴ﮒﺛﮒﻝﭘﮔﺅﺙﮒﺗﻝﮔ۶ﺅﺙ
        current_state = await self._check_current_state()
        if current_state.already_compensated:
            return CompensationResult.skipped("ﮒﺓﺎﻟ۰۴ﮒ?)
            
        try:
# 1. ﻛﭨﻝ؟ﮔﮒﺙﮔﮔ۲ﮒﮔﻛﭨﺅﺙﮒﮒﺅﺙ?
            target_debit = await self._debit_from_target()
            if not target_debit.success:
return CompensationResult.failed(f"ﻝ؟ﮔﮒﺙﮔﮔ۲ﮒﮒ۳ﺎﻟﺑ۴: {target_debit.error}")
                
# 2. ﮒﮔﭦﮒﺙﮔﮒ۱ﮒﮔﻛﭨﺅﺙﮒﮒﺅﺙ
            source_credit = await self._credit_to_source()
            if not source_credit.success:
                # ﻠ۷ﮒﻟ۰۴ﮒﺟﮒ۳ﺎﻟﺑ۴ﺅﺙﻠﻟ۵ﻟ؟ﺍﮒﺛﻝﭘﮔ?
                await self._log_partial_compensation()
return CompensationResult.failed(f"ﮔﭦﮒﺙﮔﮒ۱ﮒﮒ۳ﺎﻟﺑ? {source_credit.error}")
                
# 3. ﮔﻟ؟ﺍﻟ۰۴ﮒﺟﮒ؟ﮔ
            await self._mark_compensation_complete()
            
            return CompensationResult.success(
                f"ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﻟ۰۴ﮒﺟﮔﮒ: {self.original.quantity} {self.original.symbol}"
            )
            
        except Exception as e:
            await self._log_compensation_exception(str(e))
            return CompensationResult.failed(f"ﻟ۰۴ﮒﺟﮔ۶ﻟ۰ﮒﺙﮒﺕﺕ: {str(e)}")
```

#### 3.1.3 ﻝﭘﮔﮔ۲ﮔ۴ﻛﺕﮒﺗﻝﮔ?
```python
async def _check_current_state(self) -> CompensationState:
"""ﮔ۲ﮔ۴ﮒﺛﮒﻟ۰۴ﮒﺟﻝﭘﮔﺅﺙﮒﺗﻝﮔ۶ﻛﺟﻠﺅﺙ"""
    # ﮔ۲ﮔ۴ﮔﺁﮒ۵ﮒﺓﺎﻟ؟ﺍﮒﺛﻟ۰۴ﮒﺟﮔﮒ
    compensation_record = await self._get_compensation_record()
    if compensation_record and compensation_record.status == "completed":
        return CompensationState(already_compensated=True)
        
# ﮔ۲ﮔ۴ﻝ؟ﮔﮒﺙﮔﮒﺛﮒﮔﻛﭨ?
    target_position = await self._get_target_position()
    source_position = await self._get_source_position()
    
# ﮒ۳ﮔﮔﺁﮒ۵ﻠﻟ۵ﻟ۰۴ﮒﺟﺅﺙﻛﺕﮒ۰ﻠﭨﻟﺝﮔ۲ﮔ۴ﺅﺙ
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
"""ﮒ۳ﮔﮔﺁﮒ۵ﻠﻟ۵ﻟ۰۴ﮒﺟﺅﺙﻛﺕﮒ۰ﻠﭨﻟﺝﺅﺙ?""
# ﮒ۵ﮔﻝ؟ﮔﮒﺙﮔﮔﻛﭨﻟﭘﺏﮒ۳ﮔ۲ﮒﺅﺙﻛﺕﮔﭦﮒﺙﮔﮔﻝ۸ﭦﻠﺑﮒ۱ﮒﺅﺙﮒﻠﻟ۵ﻟ۰۴ﮒ?
    target_has_enough = target_pos.available >= self.original.quantity
    source_has_space = source_pos.available + self.original.quantity <= source_pos.max_capacity
    
    return target_has_enough and source_has_space
```

### 3.2 ﻟﭖﻠﻟﺍﮔﺑﻟ۰۴ﮒﺟ

#### 3.2.1 ﮒﮔﻛﺛﺅﺙﻟﭖﻠﻟﺍﮔﺑ
```python
class CapitalAdjustmentCommand:
    """ﻟﭖﻠﻟﺍﮔﺑﮒﺛﻛﭨ۳"""
    
    def __init__(self, engine_id: str, adjustment_type: str, amount: float):
        self.engine_id = engine_id
        self.adjustment_type = adjustment_type  # "increase" ﮔ?"decrease"
        self.amount = amount
        
    async def execute(self) -> AdjustmentResult:
        """ﮔ۶ﻟ۰ﻟﭖﻠﻟﺍﮔﺑ"""
        if self.adjustment_type == "increase":
            return await self._increase_capital()
        elif self.adjustment_type == "decrease":
            return await self._decrease_capital()
        else:
            return AdjustmentResult.failed(f"ﮔ۹ﻝ۴ﻟﺍﮔﺑﻝﺎﭨﮒ: {self.adjustment_type}")
```

#### 3.2.2 ﻟ۰۴ﮒﺟﮔﻛﺛﺅﺙﮒﮒﻟﭖﻠﻟﺍﮔ?
```python
class CapitalAdjustmentCompensation:
    """ﻟﭖﻠﻟﺍﮔﺑﻟ۰۴ﮒﺟ"""
    
    def __init__(self, original_command: CapitalAdjustmentCommand):
        self.original = original_command
        
    async def compensate(self) -> CompensationResult:
        """ﮔ۶ﻟ۰ﻟﭖﻠﻟﺍﮔﺑﻟ۰۴ﮒﺟ"""
        # ﻝ۰؟ﮒ؟ﮒﮒﮔﻛﺛﻝﺎﭨﮒ
        reverse_type = "decrease" if self.original.adjustment_type == "increase" else "increase"
        
        # ﮒﮒﭨﭦﮒﮒﮒﺛﻛﭨ۳
        reverse_command = CapitalAdjustmentCommand(
            engine_id=self.original.engine_id,
            adjustment_type=reverse_type,
            amount=self.original.amount
        )
        
        # ﮔ۶ﻟ۰ﮒﮒﮔﻛﺛ
        try:
            result = await reverse_command.execute()
            if result.success:
                await self._log_compensation_success()
                return CompensationResult.success(
                    f"ﻟﭖﻠﻟﺍﮔﺑﻟ۰۴ﮒﺟﮔﮒ: {self.original.amount}"
                )
            else:
                return CompensationResult.failed(
                    f"ﻟﭖﻠﻟﺍﮔﺑﻟ۰۴ﮒﺟﮒ۳ﺎﻟﺑ۴: {result.error}"
                )
                
        except Exception as e:
            return CompensationResult.failed(f"ﻟ۰۴ﮒﺟﮔ۶ﻟ۰ﮒﺙﮒﺕﺕ: {str(e)}")
```

### 3.3 ﻟ؟۱ﮒﻝﭘﮔﮒﮔ۴ﻟ۰۴ﮒ?

#### 3.3.1 ﮒﮔﻛﺛﺅﺙﻟ؟۱ﮒﻝﭘﮔﮒﮔ?
```python
class OrderSyncCommand:
"""ﻟ؟۱ﮒﻝﭘﮔﮒﮔ۴ﮒﺛﻛﭨ?""
    
    def __init__(self, engine_id: str, order_id: str, new_status: str):
        self.engine_id = engine_id
        self.order_id = order_id
        self.new_status = new_status  # "filled", "cancelled", "rejected"
        
    async def execute(self) -> SyncResult:
"""ﮔ۶ﻟ۰ﻟ؟۱ﮒﻝﭘﮔﮒﮔ?""
# ﻟ؟۱ﮒﻝﭘﮔﮒﮔ۴ﮔﺁﮒ۹ﻟﺁﭨﮔﻛﺛﺅﺙﮔﻠﻟ۰۴ﮒﺟ
# ﻛﺛﻠﻟ۵ﻟ؟ﺍﮒﺛﮒﮔ۴ﮒﮒﺎﺅﺙﻝ۷ﻛﭦﻛﺕﻟﺑﮔ۶ﮔ۲ﮔ?
        return await self._update_order_status()
```

#### 3.3.2 ﻟ۰۴ﮒﺟﮔﻛﺛﺅﺙﮔﻠﻟ۰۴ﮒﺟﺅﺙﮒ۹ﻟﺁﭨﮔﻛﺛﺅﺙ
```python
class OrderSyncCompensation:
"""ﻟ؟۱ﮒﻝﭘﮔﮒﮔ۴ﻟ۰۴ﮒﺟﺅﺙﮔﻠﮒ؟ﻠﻟ۰۴ﮒﺟﺅﺙ?""
    
    def __init__(self, original_command: OrderSyncCommand):
        self.original = original_command
        
    async def compensate(self) -> CompensationResult:
"""ﻟ؟۱ﮒﮒﮔ۴ﮔﻠﻟ۰۴ﮒﺟﺅﺙﮒ۹ﻟ؟ﺍﮒﺛﻟ۰۴ﮒﺟﮒ؟ﮔ"""
# ﻟ؟۱ﮒﻝﭘﮔﮒﮔ۴ﮔﺁﮒ۹ﻟﺁﭨﮔﻛﺛﺅﺙﮔﺎ۰ﮔﮒﺁﻛﺛﻝ۷
# ﮒ۹ﻠﮔﻟ؟ﺍﻟ۰۴ﮒﺟﮒ؟ﮔﺅﺙﮔﻠﮒ؟ﻠﮔ۶ﻟ۰ﮒﮒﮔﻛﺛ
        await self._log_no_compensation_needed()
        
        return CompensationResult.skipped(
"ﻟ؟۱ﮒﻝﭘﮔﮒﮔ۴ﻛﺕﭦﮒ۹ﻟﺁﭨﮔﻛﺛﺅﺙﮔﻠﻟ۰۴ﮒﺟ"
        )
```

---

## 4. ﮒﺗﻝﮔ۶ﻟ؟ﺝﻟ؟?

### 4.1 ﮒﺗﻝﮔ۶ﻛﺟﻠﮔﭦﮒ?

#### 4.1.1 ﻟ۰۴ﮒﺟﻝﭘﮔﮔ۲ﮔ?
```python
class IdempotencyChecker:
"""ﮒﺗﻝﮔ۶ﮔ۲ﮔ۴ﮒ۷"""
    
    def __init__(self, storage_client):
        self.storage = storage_client
        
    async def check_compensation_idempotency(
        self, tx_id: str, participant_id: str
    ) -> IdempotencyCheckResult:
"""ﮔ۲ﮔ۴ﻟ۰۴ﮒﺟﮔﻛﺛﻝﮒﺗﻝﮔ?""
# 1. ﮔ۲ﮔ۴ﻟ۰۴ﮒﺟﻟ؟ﺍﮒﺛﮔﺁﮒ۵ﮒﮒ?
        compensation_record = await self._get_compensation_record(tx_id, participant_id)
        
        if compensation_record:
# ﻟ؟ﺍﮒﺛﮒﮒ۷ﺅﺙﮔ۲ﮔ۴ﻝﭘﮔ?
            if compensation_record.status == "completed":
                return IdempotencyCheckResult.already_compensated(
                    compensation_record.completed_at
                )
            elif compensation_record.status == "executing":
                return IdempotencyCheckResult.currently_executing(
                    compensation_record.started_at
                )
            elif compensation_record.status == "failed":
                # ﮒ۳ﺎﻟﺑ۴ﻝﭘﮔﮒﺁﻛﭨ۴ﻠﻟﺁ?
                return IdempotencyCheckResult.can_retry(
                    compensation_record.failed_at,
                    compensation_record.error_message
                )
                
        # 2. ﮔ۲ﮔ۴ﻛﺕﮒ۰ﻝﭘﮔ?
        business_state = await self._check_business_state(tx_id, participant_id)
        
# 3. ﮒ۳ﮔﮔﺁﮒ۵ﻠﻟ۵ﻟ۰۴ﮒ?
        needs_compensation = await self._determine_if_compensation_needed(
            business_state
        )
        
        return IdempotencyCheckResult(
            needs_compensation=needs_compensation,
            business_state=business_state,
            can_proceed=True
        )
```

#### 4.1.2 ﻛﺕﮒ۰ﻝﭘﮔﮔ۲ﮔ?
```python
async def _check_business_state(self, tx_id: str, participant_id: str) -> BusinessState:
    """ﮔ۲ﮔ۴ﻛﺕﮒ۰ﻝﭘﮔ?""
    # ﻟﺓﮒﮒﻛﭦﮒ۰ﻟ؟ﺍﮒﺛ?
    original_tx = await self._get_original_transaction(tx_id, participant_id)
    if not original_tx:
return BusinessState.error("ﮒﻛﭦﮒ۰ﻟ؟ﺍﮒﺛﻛﺕﮒﮒ۷")
        
# ﮔﺗﮔ؟ﮒﺛﻛﭨ۳ﻝﺎﭨﮒﮔ۲ﮔ۴ﻛﺕﮒﻝﻛﺕﮒ۰ﻝﭘﮔ?
    if original_tx.command_type == "position_transfer":
        return await self._check_position_transfer_state(original_tx)
    elif original_tx.command_type == "capital_adjustment":
        return await self._check_capital_adjustment_state(original_tx)
    elif original_tx.command_type == "order_sync":
        return await self._check_order_sync_state(original_tx)
    else:
        return BusinessState.error(f"ﮔ۹ﻝ۴ﮒﺛﻛﭨ۳ﻝﺎﭨﮒ: {original_tx.command_type}")
        
async def _check_position_transfer_state(self, original_tx) -> BusinessState:
    """ﮔ۲ﮔ۴ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﻝﻛﺕﮒ۰ﻝﭘﮔ?""
# ﻟﺓﮒﮔﭦﮒﺙﮔﮒﻝ؟ﮔﮒﺙﮔﻝﮒﺛﮒﮔﻛﭨ?
    source_position = await self._get_position(
        original_tx.source_engine, original_tx.symbol
    )
    target_position = await self._get_position(
        original_tx.target_engine, original_tx.symbol
    )
    
# ﮒ۳ﮔﮒﮔﻛﺛﮔﺁﮒ۵ﮒﺓﺎﻝﮔ
# ﮒ۵ﮔﻝ؟ﮔﮒﺙﮔﮔﻛﭨﮒ۱ﮒﺅﺙﮔﭦﮒﺙﮔﮔﻛﭨﮒﮒﺍﺅﺙﮒﮒﮔﻛﺛﮒﺓﺎﻝﮔ
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

#### 4.1.3 ﮒﺗﻝﮔ۶ﻛﭨ۳ﻝ?
```python
class IdempotencyTokenManager:
"""ﮒﺗﻝﮔ۶ﻛﭨ۳ﻝﻝ؟۰ﻝﮒ۷"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        
    async def generate_token(self, tx_id: str, participant_id: str) -> str:
"""ﻝﮔﮒﺗﻝﮔ۶ﻛﭨ۳ﻝ?""
# ﻛﭨ۳ﻝﮔﺙﮒﺙ: tx_id:participant_id:timestamp:random
        timestamp = int(time.time() * 1000)
        random_str = secrets.token_hex(4)
        token = f"{tx_id}:{participant_id}:{timestamp}:{random_str}"
        
# ﮒﮒ۷ﻛﭨ۳ﻝﺅﺙﻟ؟ﺝﻝﺛ؟ﻟﺟﮔﮔﭘﻠﺑﺅﺙ24ﮒﺍﮔﭘﺅﺙ?
        await self.redis.setex(
            f"idempotency:{token}",
            86400,  # 24ﮒﺍﮔﭘ
            "generated"
        )
        
        return token
        
    async def check_and_consume_token(self, token: str) -> bool:
        """ﮔ۲ﮔ۴ﮒﺗﭘﮔﭘﻟﺑﺗﻛﭨ۳ﻝ"""
# ﮔ۲ﮔ۴ﻛﭨ۳ﻝﮔﺁﮒ۵ﮒﮒ۷ﻛﺕﮔ۹ﻛﺛﺟﻝ?
        key = f"idempotency:{token}"
        exists = await self.redis.exists(key)
        if not exists:
            return False
            
# ﻛﺛﺟﻝ۷ﮒﮒﮔﻛﺛﮔﻟ؟ﺍﻛﭨ۳ﻝﻛﺕﭦﮒﺓﺎﻛﺛﺟﻝ۷
        # ﻛﺛﺟﻝ۷SETNXﻝ۰؟ﻛﺟﮒ۹ﮔﻝ؛؛ﻛﺕﻛﺕ۹ﮔﭘﻟﺑﺗﮔﮒ?
        used = await self.redis.setnx(f"{key}:used", "1")
        if not used:
            return False  # ﮒﺓﺎﻟ۱،ﮒﭘﻛﭨﻟﺁﺓﮔﺎﮔﭘﻟﺑﺗ
            
        # ﻟ؟ﺝﻝﺛ؟ﻛﺛﺟﻝ۷ﮔﭘﻠﺑ
        await self.redis.expire(f"{key}:used", 86400)
        
        return True
```

### 4.2 ﻟ۰۴ﮒﺟﮔﻛﺛﮒﺗﻝﮔ۶ﮒ؟ﻝ?

#### 4.2.1 ﻟ۰۴ﮒﺟﮔﻛﺛﮒﻟ۲ﮒ?
```python
class IdempotentCompensationWrapper:
"""ﮒﺗﻝﮔ۶ﻟ۰۴ﮒﺟﮔﻛﺛﮒﻟ۲ﮒ۷"""
    
    def __init__(self, compensation_operation, idempotency_checker):
        self.operation = compensation_operation
        self.checker = idempotency_checker
        
    async def execute(self, tx_id: str, participant_id: str) -> CompensationResult:
"""ﮔ۶ﻟ۰ﮒﺗﻝﮔ۶ﻟ۰۴ﮒﺟﮔﻛﺛ?""
# 1. ﮒﺗﻝﮔ۶ﮔ۲ﮔ?
        check_result = await self.checker.check_compensation_idempotency(
            tx_id, participant_id
        )
        
        if not check_result.can_proceed:
            if check_result.already_compensated:
                return CompensationResult.skipped("ﮒﺓﺎﻟ۰۴ﮒ?)
            elif check_result.currently_executing:
return CompensationResult.skipped("ﮔ۲ﮒ۷ﮔ۶ﻟ۰ﻛﺕ?)
            else:
return CompensationResult.failed(f"ﮒﺗﻝﮔ۶ﮔ۲ﮔ۴ﮒ۳ﺎﻟﺑ? {check_result.reason}")
                
        # 2. ﻟ؟ﺍﮒﺛﻟ۰۴ﮒﺟﮒﺙﮒ۶?
        await self._log_compensation_start(tx_id, participant_id)
        
        try:
            # 3. ﮔ۶ﻟ۰ﻟ۰۴ﮒﺟﮔﻛﺛ
            result = await self.operation.compensate()
            
            # 4. ﻟ؟ﺍﮒﺛﻟ۰۴ﮒﺟﻝﭨﮔ
            if result.success:
                await self._log_compensation_success(tx_id, participant_id, result)
            else:
                await self._log_compensation_failure(tx_id, participant_id, result)
                
            return result
            
        except Exception as e:
            # 5. ﻟ؟ﺍﮒﺛﮒﺙﮒﺕﺕ
            await self._log_compensation_exception(tx_id, participant_id, str(e))
            return CompensationResult.failed(f"ﻟ۰۴ﮒﺟﮔ۶ﻟ۰ﮒﺙﮒﺕﺕ: {str(e)}")
```

#### 4.2.2 ﻟ۰۴ﮒﺟﮔﻛﺛﻝﭘﮔﮔﭦ
```python
class CompensationStateMachine:
"""ﻟ۰۴ﮒﺟﮔﻛﺛﻝﭘﮔﮔﭦﺅﺙﻛﺟﻠﮒﺗﻝﮔ۶ﺅﺙ"""
    
    def __init__(self, storage_client):
        self.storage = storage_client
        
    async def transition_state(
        self, tx_id: str, participant_id: str, 
        from_state: str, to_state: str
    ) -> bool:
"""ﻝﭘﮔﻟﺛ؛ﮔ۱ﺅﺙﮒﮒﮔﻛﺛﺅﺙ?""
# ﻛﺛﺟﻝ۷ﮔﺍﮔ؟ﮒﭦﻛﭦﮒ۰ﻛﺟﻟﺁﻝﭘﮔﻟﺛ؛ﮔ۱ﻝﮒﮒﮔ?
        async with self.storage.transaction():
            # ﮔ۲ﮔ۴ﮒﺛﮒﻝﭘﮔ?
            current_state = await self._get_current_state(tx_id, participant_id)
            
            if current_state != from_state:
                # ﻝﭘﮔﻛﺕﻝ؛۵ﮒﻠ۱ﮔﺅﺙﻟﺛ؛ﮔ۱ﮒ۳ﺎﻟﺑ?
                return False
                
            # ﮔ۶ﻟ۰ﻝﭘﮔﻟﺛ؛ﮔ?
            await self._update_state(tx_id, participant_id, to_state)
            
            # ﻟ؟ﺍﮒﺛﻝﭘﮔﻟﺛ؛ﮔ۱ﮒﮒ?
            await self._log_state_transition(
                tx_id, participant_id, from_state, to_state
            )
            
            return True
            
    async def get_allowed_transitions(self, current_state: str) -> List[str]:
        """ﻟﺓﮒﮒﻟ؟ﺕﻝﻝﭘﮔﻟﺛ؛ﮔ?""
        transitions = {
            "pending": ["executing", "skipped"],
            "executing": ["completed", "failed", "retrying"],
            "retrying": ["completed", "failed"],
            "completed": [],  # ﻝﭨﮔﺅﺙﻛﺕﮒﻟ؟ﺕﻟﺛ؛ﮔ?
            "failed": ["retrying"],  # ﮒ۳ﺎﻟﺑ۴ﮒﺁﻛﭨ۴ﻠﻟﺁ
            "skipped": []  # ﻝﭨﮔﺅﺙﻛﺕﮒﻟ؟ﺕﻟﺛ؛ﮔ?
        }
        
        return transitions.get(current_state, [])
```

---

## 5. ﻠﻟﺁﮔﭦﮒﭘﻟ؟ﺝﻟ؟۰

### 5.1 ﻠﻟﺁﻝﻝ۴

#### 5.1.1 ﮔﮔﺍﻠﻠﺟﻠﻟﺁﻝﻝ?
```python
class ExponentialBackoffRetryStrategy:
"""ﮔﮔﺍﻠﻠﺟﻠﻟﺁﻝﻝ?""
    
    def __init__(self, initial_delay: float = 1.0, multiplier: float = 2.0,
                 max_delay: float = 60.0, jitter: bool = True):
        self.initial_delay = initial_delay
        self.multiplier = multiplier
        self.max_delay = max_delay
        self.jitter = jitter
        
    def get_delay(self, retry_count: int) -> float:
        """ﻟ؟۰ﻝ؟ﻠﻟﺁﮒﭨﭘﻟﺟ"""
        if retry_count <= 0:
            return 0.0
            
        # ﮔﮔﺍﻟ؟۰ﻝ؟
        delay = self.initial_delay * (self.multiplier ** (retry_count - 1))
        
        # ﻠﮒﭘﮔﮒ۳۶ﮒﭨﭘﻟﺟ?
        delay = min(delay, self.max_delay)
        
# ﮔﺓﭨﮒﮔﮒ۷ﺅﺙﻠﺟﮒﮒ۳ﻛﺕ۹ﮒ؟۱ﮔﺓﻝ،ﺁﮒﮔﭘﻠﻟﺁﺅﺙ?
        if self.jitter:
            jitter_amount = delay * 0.1  # 10%ﮔﮒ۷
            delay += random.uniform(-jitter_amount, jitter_amount)
            delay = max(0.0, delay)  # ﻝ۰؟ﻛﺟﻠﻟﺑ
            
        return delay
```

#### 5.1.2 ﮒﭦﮒ؟ﮒﭨﭘﻟﺟﻠﻟﺁﻝﻝ۴
```python
class FixedDelayRetryStrategy:
"""ﮒﭦﮒ؟ﮒﭨﭘﻟﺟﻠﻟﺁﻝﻝ۴"""
    
    def __init__(self, delay: float = 5.0):
        self.delay = delay
        
    def get_delay(self, retry_count: int) -> float:
        """ﻟ؟۰ﻝ؟ﻠﻟﺁﮒﭨﭘﻟﺟ"""
        return self.delay  # ﮒﭦﮒ؟ﮒﭨﭘﻟﺟ
```

#### 5.1.3 ﻟ۹ﻠﮒﭦﻠﻟﺁﻝﻝ۴
```python
class AdaptiveRetryStrategy:
"""ﻟ۹ﻠﮒﭦﻠﻟﺁﻝﻝ۴"""
    
    def __init__(self):
        self.error_patterns = {}
        self.success_rates = {}
        
    def get_delay(self, retry_count: int, error_type: str) -> float:
"""ﮔﺗﮔ؟ﻠﻟﺁﺁﻝﺎﭨﮒﮒﮒﮒﺎﮔﮒﻝﻟ؟۰ﻝ؟ﮒﭨﭘﻟﺟ"""
        # ﻟﺓﮒﻟﺁ۴ﻝﺎﭨﻠﻟﺁﺁﻝﮒﮒﺎﮔﮒﻝ
        success_rate = self.success_rates.get(error_type, 0.5)
        
# ﮔﺗﮔ؟ﮔﮒﻝﻟﺍﮔﺑﮒﭨﭘﻟﺟ?
if success_rate < 0.3:  # ﮔﮒﻝﻛﺛﺅﺙﮒ۱ﮒﮒﭨﭘﻟﺟ?
            base_delay = 10.0
elif success_rate < 0.7:  # ﮔﮒﻝﻛﺕﻝ?
            base_delay = 5.0
        else:  # ﮔﮒﻝﻠ،ﺅﺙﮒﮒﺍﮒﭨﭘﻟﺟ?
            base_delay = 2.0
            
        # ﻟﻟﻠﻟﺁﮔ؛۰ﮔﺍ
        delay = base_delay * (1.5 ** (retry_count - 1))
        
        return min(delay, 60.0)  # ﮔﮒ۳?0ﻝ۶?
```

### 5.2 ﻠﻟﺁﻝ؟۰ﻝﮒ?

#### 5.2.1 ﻠﻟﺁﻟﺍﮒﭦ۵ﮒ?
```python
class RetryScheduler:
    """ﻠﻟﺁﻟﺍﮒﭦ۵ﮒ?""
    
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
        """ﻟﺍﮒﭦ۵ﻠﻟﺁﻛﭨﭨﮒ۰"""
        # ﻟﺓﮒﮒﺛﮒﻠﻟﺁﮔ؛۰ﮔﺍ
        retry_count = await self._get_retry_count(tx_id, participant_id)
        
        # ﮔ۲ﮔ۴ﮔﺁﮒ۵ﻟﭘﻟﺟﮔﮒ۳۶ﻠﻟﺁﮔ؛۰ﮔ?
        if retry_count >= self._get_max_retries(error_type):
            return None
            
# ﻠﮔ۸ﻠﻟﺁﻝﻝ۴
        strategy = self.strategies.get(error_type, self.strategies["temporary_failure"])
        
        # ﻟ؟۰ﻝ؟ﻛﺕﮔ؛۰ﻠﻟﺁﮔﭘﻠﺑ
        delay = strategy.get_delay(retry_count)
        next_retry_time = datetime.now() + timedelta(seconds=delay)
        
        # ﮒﮒﭨﭦﻠﻟﺁﻛﭨﭨﮒ۰
        task = RetryTask(
            tx_id=tx_id,
            participant_id=participant_id,
            retry_count=retry_count + 1,
            scheduled_time=next_retry_time,
            error_type=error_type,
            last_error=last_error
        )
        
# ﮒﮒ۷ﻠﻟﺁﻛﭨﭨﮒ۰
        await self._store_retry_task(task)
        
        return task
```

#### 5.2.2 ﻠﻟﺁﮔ۶ﻟ۰ﮒ?
```python
class RetryExecutor:
    """ﻠﻟﺁﮔ۶ﻟ۰ﮒ?""
    
    def __init__(self, compensation_executor: CompensationExecutor):
        self.executor = compensation_executor
        self.retry_log = RetryLog()
        
    async def execute_retry(self, task: RetryTask) -> RetryResult:
        """ﮔ۶ﻟ۰ﻠﻟﺁ"""
# ﻝﮒﺝﮒﺍﻟ؟۰ﮒﮔﭘﻠ?
        await self._wait_until(task.scheduled_time)
        
        # ﻟ؟ﺍﮒﺛﻠﻟﺁﮒﺙﮒ۶?
        await self.retry_log.log_retry_start(task)
        
        try:
            # ﮔ۶ﻟ۰ﻟ۰۴ﮒﺟﮔﻛﺛ
            result = await self.executor.execute_compensation(
                task.tx_id, task.participant_id
            )
            
            # ﻟ؟ﺍﮒﺛﻠﻟﺁﻝﭨﮔ
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
            # ﻟ؟ﺍﮒﺛﻠﻟﺁﮒﺙﮒﺕﺕ
            await self.retry_log.log_retry_exception(task, str(e))
            return RetryResult.failed(
                task.tx_id, task.participant_id,
                task.retry_count, f"ﻠﻟﺁﮔ۶ﻟ۰ﮒﺙﮒﺕﺕ: {str(e)}"
            )
```

### 5.3 ﻠﻟﺁﻝﮔ۶ﻛﺕﮒﻟ?

#### 5.3.1 ﻠﻟﺁﻝﮔ۶ﮔﮔ
```python
class RetryMetricsCollector:
"""ﻠﻟﺁﻝﮔ۶ﮔﮔﮔﭘﻠﮒ?""
    
    def __init__(self, prometheus_client):
        self.prometheus = prometheus_client
        
# ﮒ؟ﻛﺗﻝﮔ۶ﮔﮔ
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
        """ﻟ؟ﺍﮒﺛﻠﻟﺁﮒﺍﻟﺁ"""
        # ﻟ؟ﺍﮒﺛﮔﭨﻠﻟﺁﮔ؛۰ﮔ?
        self.retry_total.labels(
            tx_type=tx_type,
            participant=participant,
            error_type=error_type
        ).inc()
        
# ﻟ؟ﺍﮒﺛﻠﻟﺁﮔﻝﭨﮔﭘﻠﺑ
        self.retry_duration.labels(
            tx_type=tx_type,
            participant=participant
        ).observe(duration)
        
        # ﻟ؟ﺍﮒﺛﮔﮒﻠﻟﺁ
        if success:
            self.retry_success.labels(
                tx_type=tx_type,
                participant=participant
            ).inc()
```

#### 5.3.2 ﻠﻟﺁﮒﻟ۵ﻟ۶ﮒ
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
    description: "ﻟ۰۴ﮒﺟﻠﻟﺁﻝﻟﺟﻠ،ﻛﺕﮔﮒﻝﻛﺛ"
    summary: "ﻟ۰۴ﮒﺟﻠﻟﺁﮒﺙﮒﺕﺕ"
    
  - name: CompensationRetryMaxAttempts
    condition: |
      saga_compensation_retries_total - 
      saga_compensation_retry_success_total > 3
    severity: critical
    description: "ﻟ۰۴ﮒﺟﻠﻟﺁﻟﺝﺝﮒﺍﮔﮒ۳۶ﮒﺍﻟﺁﮔ؛۰ﮔ?
    summary: "ﻟ۰۴ﮒﺟﻠﻟﺁﮒ۳ﺎﻟﺑ۴ﻠﻟ۵ﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱?
    
  - name: LongRetryDuration
    condition: |
      histogram_quantile(0.95, 
        rate(saga_compensation_retry_duration_seconds_bucket[5m])
      ) > 10
    severity: warning
description: "95%ﻝﻟ۰۴ﮒﺟﻠﻟﺁﮔﻝﭨﮔﭘﻠﺑﻟﭘﻟﺟ?0ﻝ۶?
    summary: "ﻟ۰۴ﮒﺟﻠﻟﺁﮔ۶ﻟﺛﻛﺕﻠ"
```

---

## 6. ﻠﻟﺁﺁﮒ۳ﻝﻛﺕﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱?

### 6.1 ﻟ۰۴ﮒﺟﮒ۳ﺎﻟﺑ۴ﮒﻝﺎﭨ

| ﮒ۳ﺎﻟﺑ۴ﻝﺎﭨﮒ | ﮒﮒ | ﻟ۹ﮒ۷ﮔ۱ﮒ۳ﮒﺁﻟﺛﮔ?| ﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱ﻠﮔﺎ?|
|----------|------|----------------|--------------|
| **ﻛﺕﺑﮔﭘﮔ۶ﮒ۳ﺎﻟﺑ?* | ﻝﺛﻝﭨﮔﮒ۷ﻙﻟﭖﮔﭦﮔﮔﭘﻛﺕﮒﺁﻝ۷ | ﻠ،ﺅﺙﮒﺁﻠﻟﺁﺅﺙ | ﻛﺛ?|
| **ﻛﺕﮒ۰ﻠﭨﻟﺝﮒ۳ﺎﻟﺑ۴** | ﻛﺕﮒ۰ﻟ۶ﮒﮒﺎﻝ۹ﻙﮔﺍﮔ؟ﻛﺕﻛﺕﻟ?| ﻛﺕﺅﺙﻠﮔ۲ﮔ۴ﺅﺙ | ﻛﺕ?|
| **ﻝﺏﭨﻝﭨﻠﻟﺁﺁ** | ﮔﺍﮔ؟ﮒﭦﮔﻠﻙﮔﮒ۰ﮒ؟ﮔ?| ﻛﺛﺅﺙﻠﻛﺟ؟ﮒ۳ﺅﺙ?| ﻠ،?|
| **ﮔﺍﮔ؟ﮔﮒ** | ﮔﺍﮔ؟ﻛﺕ۱ﮒ۳ﺎﻙﮔﮒ?| ﮔﻛﺛ | ﻠ،ﺅﺙﻠﮔﺍﮔ؟ﻛﺟ؟ﮒ۳ﺅﺙ?|

### 6.2 ﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱ﮔﭖﻝ۷

#### 6.2.1 ﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱ﻟ۶۵ﮒﮒ?
```python
class ManualInterventionTrigger:
    """ﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱ﻟ۶۵ﮒﮒ?""
    
    def __init__(self, alert_client, ticket_system_client):
        self.alert = alert_client
        self.ticket = ticket_system_client
        
    async def trigger_intervention(
        self, tx_id: str, reason: str, details: Dict
    ) -> InterventionTicket:
        """ﻟ۶۵ﮒﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱"""
# 1. ﮔ۲ﮔ۴ﮔﺁﮒ۵ﮒﺓﺎﮒﮒ۷ﮒﺗﺎﻠ۱ﮒﺓ۴ﮒ
        existing_ticket = await self._get_existing_ticket(tx_id)
        if existing_ticket:
            return existing_ticket
            
        # 2. ﮒﮒﭨﭦﮒﺗﺎﻠ۱ﮒﺓ۴ﮒ
        ticket = InterventionTicket(
            tx_id=tx_id,
            reason=reason,
            details=details,
            status="open",
            priority=self._determine_priority(reason),
            created_at=datetime.now()
        )
        
# 3. ﻛﺟﮒﮒﺓ۴ﮒ
        await self._save_ticket(ticket)
        
# 4. ﮒﻠﮒﻟ?
        await self.alert.send_alert(
            f"ﻠﻟ۵ﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱? {reason}",
            f"ﻛﭦﮒ۰ {tx_id} ﻠﻟ۵ﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱ﻙﻟﺁ۵ﮔ? {json.dumps(details)}",
            severity="critical"
        )
        
        return ticket
```

#### 6.2.2 ﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱ﮒﺓ۴ﮒﺓ
```python
class ManualInterventionTool:
    """ﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱ﮒﺓ۴ﮒﺓ"""
    
    def __init__(self, storage_client, engine_clients):
        self.storage = storage_client
        self.engines = engine_clients
        
    async def diagnose_issue(self, tx_id: str) -> DiagnosisReport:
"""ﻟﺁﮔﻠ؟ﻠ۱"""
        # 1. ﻟﺓﮒﻛﭦﮒ۰ﻟﺁ۵ﮔ
        tx_details = await self._get_transaction_details(tx_id)
        
        # 2. ﻟﺓﮒﻟ۰۴ﮒﺟﻝﭘﮔ?
        compensation_state = await self._get_compensation_state(tx_id)
        
        # 3. ﮔ۲ﮔ۴ﮒﮒﺙﮔﻝﭘﮔ?
        engine_states = {}
        for participant in tx_details.participants:
            engine_state = await self._check_engine_state(participant.engine_id)
            engine_states[participant.engine_id] = engine_state
            
# 4. ﻝﮔﻟﺁﮔﮔ۴ﮒ
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
        """ﻛﺟ؟ﮒ۳ﻠ؟ﻠ۱"""
# ﮔﺗﮔ؟actionﮔ۶ﻟ۰ﻛﺕﮒﻝﻛﺟ؟ﮒ۳ﮔﻛﺛ?
        if action == "force_complete_compensation":
            return await self._force_complete_compensation(tx_id, parameters)
        elif action == "rollback_manually":
            return await self._manual_rollback(tx_id, parameters)
        elif action == "mark_as_resolved":
            return await self._mark_as_resolved(tx_id, parameters)
        elif action == "reset_transaction":
            return await self._reset_transaction(tx_id, parameters)
        else:
            return FixResult.failed(f"ﮔ۹ﻝ۴ﮔﻛﺛ: {action}")
```

---

## 7. ﻝﮔ۶ﻛﺕﮒﺁﻟ۶ﮔﭖﮔ?

### 7.1 ﻝﮔ۶ﮔﮔ

#### 7.1.1 ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮔﮔ
```python
COMPENSATION_METRICS = {
    # ﻟ؟۰ﮔﺍﮒ?
    "compensation_triggered_total": "ﻟ۰۴ﮒﺟﻟ۶۵ﮒﮔﭨﮔ؛۰ﮔ?,
    "compensation_success_total": "ﻟ۰۴ﮒﺟﮔﮒﮔﭨﮔ؛۰ﮔ?,
    "compensation_failed_total": "ﻟ۰۴ﮒﺟﮒ۳ﺎﻟﺑ۴ﮔﭨﮔ؛۰ﮔ?,
    "compensation_retry_total": "ﻟ۰۴ﮒﺟﻠﻟﺁﮔﭨﮔ؛۰ﮔ?,
    
    # ﻝﺑﮔﺗﮒ?
    "compensation_duration_seconds": "ﻟ۰۴ﮒﺟﮔ۶ﻟ۰ﮔﭘﻠﺑﮒﮒﺕ",
    "compensation_retry_delay_seconds": "ﻟ۰۴ﮒﺟﻠﻟﺁﮒﭨﭘﻟﺟﮒﮒﺕ",
    
    # ﻛﭨ۹ﻟ۰۷ﻝ?
    "compensation_success_rate": "ﻟ۰۴ﮒﺟﮔﮒﻝ?,
    "compensation_retry_rate": "ﻟ۰۴ﮒﺟﻠﻟﺁﻝ?,
    "compensation_pending_count": "ﮒﺝﮒ۳ﻝﻟ۰۴ﮒﺟﮔﺍﻠ?,
"compensation_in_progress_count": "ﻟﺟﻟ۰ﻛﺕﻟ۰۴ﮒﺟﮔﺍﻠ?,
}
```

#### 7.1.2 ﻛﺕﮒ۰ﮔﮔ
```python
BUSINESS_METRICS = {
    # ﮔﻛﭨﻝﺕﮒﺏ
    "position_transfer_compensation_total": "ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﻟ۰۴ﮒﺟﮔ؛۰ﮔﺍ",
    "position_transfer_compensation_success_rate": "ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﻟ۰۴ﮒﺟﮔﮒﻝ?,
    
    # ﻟﭖﻠﻝﺕﮒﺏ
    "capital_adjustment_compensation_total": "ﻟﭖﻠﻟﺍﮔﺑﻟ۰۴ﮒﺟﮔ؛۰ﮔﺍ",
    "capital_adjustment_compensation_success_rate": "ﻟﭖﻠﻟﺍﮔﺑﻟ۰۴ﮒﺟﮔﮒﻝ?,
    
    # ﮒﺙﮔﻝﺕﮒﺏ
    "engine_compensation_total": "ﮒﮒﺙﮔﻟ۰۴ﮒﺟﮔ؛۰ﮔ?,
    "engine_compensation_success_rate": "ﮒﮒﺙﮔﻟ۰۴ﮒﺟﮔﮒﻝ",
}
```

### 7.2 ﮔ۴ﮒﺟﻟ؟ﺍﮒﺛ

#### 7.2.1 ﻝﭨﮔﮒﮔ۴ﮒﺟ?
```python
class CompensationLogger:
    """ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮔ۴ﮒﺟﻟ؟ﺍﮒﺛﮒ?""
    
    def __init__(self):
        self.logger = logging.getLogger("compensation")
        
    async def log_compensation_start(
        self, tx_id: str, participant_id: str, 
        compensation_type: str
    ):
        """ﻟ؟ﺍﮒﺛﻟ۰۴ﮒﺟﮒﺙﮒ۶?""
        self.logger.info(
            "ﻟ۰۴ﮒﺟﮒﺙﮒ۶?,
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
        """ﻟ؟ﺍﮒﺛﻟ۰۴ﮒﺟﻝﭨﮔ"""
        log_data = {
            "tx_id": tx_id,
            "participant_id": participant_id,
            "success": result.success,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat(),
            "log_type": "compensation_result"
        }
        
        if result.success:
            self.logger.info("ﻟ۰۴ﮒﺟﮔﮒ", extra=log_data)
        else:
            log_data["error"] = result.error_message
            self.logger.error("ﻟ۰۴ﮒﺟﮒ۳ﺎﻟﺑ۴", extra=log_data)
```

#### 7.2.2 ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ
```python
class CompensationAuditLogger:
    """ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ"""
    
    def __init__(self, storage_client):
        self.storage = storage_client
        
    async def log_audit_event(
        self, event_type: str, tx_id: str, 
        participant_id: str, user: str, details: Dict
    ):
        """ﻟ؟ﺍﮒﺛﮒ؟۰ﻟ؟۰ﻛﭦﻛﭨﭘ"""
        audit_record = CompensationAuditRecord(
            event_type=event_type,
            tx_id=tx_id,
            participant_id=participant_id,
            user=user,
            details=details,
            timestamp=datetime.now()
        )
        
# ﮒﮒ۷ﮒﺍﮒ؟۰ﻟ؟۰ﻛﺕﻝ۷ﻟ۰۷
        await self.storage.insert_audit_record(audit_record)
```

---

## 8. ﮔﭖﻟﺁﮔﺗﮔ۰

### 8.1 ﮒﮒﮔﭖﻟﺁ

#### 8.1.1 ﮒﺗﻝﮔ۶ﮔﭖﻟﺁ?
```python
class TestIdempotency:
"""ﮒﺗﻝﮔ۶ﮔﭖﻟﺁ?""
    
    async def test_compensation_idempotency(self):
"""ﮔﭖﻟﺁﻟ۰۴ﮒﺟﮔﻛﺛﻝﮒﺗﻝﮔ?""
        # ﻝ؛؛ﻛﺕﮔ؛۰ﮔ۶ﻟ۰ﻟ۰۴ﮒ?
        result1 = await compensation_executor.execute_compensation(tx_id, participant_id)
        assert result1.success
        
        # ﻝ؛؛ﻛﭦﮔ؛۰ﮔ۶ﻟ۰ﻝﺕﮒﻟ۰۴ﮒﺟﺅﺙﮒﭦﻟﺁ۴ﻟ۱،ﻟﺓﺏﻟﺟﺅﺙ
        result2 = await compensation_executor.execute_compensation(tx_id, participant_id)
        assert result2.skipped
        assert "ﮒﺓﺎﻟ۰۴ﮒ? in result2.message
        
    async def test_partial_compensation_idempotency(self):
"""ﮔﭖﻟﺁﻠ۷ﮒﻟ۰۴ﮒﺟﮒﭦﮔﺁﻝﮒﺗﻝﮔ?""
        # ﮔ۷۰ﮔﻠ۷ﮒﻟ۰۴ﮒﺟﮔﮒﮒﭦﮔﺁ
        await self._setup_partial_compensation_state()
        
# ﮔ۶ﻟ۰ﻟ۰۴ﮒﺟﺅﺙﮒﭦﻟﺁ۴ﻝﭨ۶ﻝﭨﮒ؟ﮔﮒ۸ﻛﺛﻠ۷ﮒﺅﺙ
        result = await compensation_executor.execute_compensation(tx_id, participant_id)
        assert result.success
```

#### 8.1.2 ﻠﻟﺁﮔﭖﻟﺁ
```python
class TestRetryMechanism:
    """ﻠﻟﺁﮔﭦﮒﭘﮔﭖﻟﺁ"""
    
    async def test_exponential_backoff(self):
        """ﮔﭖﻟﺁﮔﮔﺍﻠﻠﺟﻠﻟﺁ?""
        strategy = ExponentialBackoffRetryStrategy()
        
        delays = [strategy.get_delay(i) for i in range(1, 5)]
        # ﻠ۹ﻟﺁﮒﭨﭘﻟﺟﻝ؛۵ﮒﮔﮔﺍﮒ۱ﻠﺟ
        assert delays[0] == 1.0
        assert delays[1] == 2.0
        assert delays[2] == 4.0
        assert delays[3] == 8.0
        
    async def test_max_retry_limit(self):
        """ﮔﭖﻟﺁﮔﮒ۳۶ﻠﻟﺁﮔ؛۰ﮔﺍﻠﮒ?""
# ﮔ۷۰ﮔﻟﺟﻝﭨﮒ۳ﺎﻟﺑ۴
        for i in range(3):
            result = await compensation_executor.execute_compensation(tx_id, participant_id)
            assert result.failed
            
        # ﻝ؛؛ﮒﮔ؛۰ﮒﭦﻟﺁ۴ﻛﺕﮒﻠﻟﺁ?
        result = await compensation_executor.execute_compensation(tx_id, participant_id)
        assert result.failed
        assert "ﻟﭘﻟﺟﮔﮒ۳۶ﻠﻟﺁﮔ؛۰ﮔ? in result.error_message
```

### 8.2 ﻠﮔﮔﭖﻟﺁ

#### 8.2.1 ﻝ،ﺁﮒﺍﻝ،ﺁﻟ۰۴ﮒﺟﮔﭖﻟﺁ?
```python
class TestEndToEndCompensation:
    """ﻝ،ﺁﮒﺍﻝ،ﺁﻟ۰۴ﮒﺟﮔﭖﻟﺁ?""
    
    async def test_position_transfer_compensation(self):
        """ﮔﭖﻟﺁﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﻟ۰۴ﮒﺟﻝ،ﺁﮒﺍﻝ،?""
        # 1. ﮔ۶ﻟ۰ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨ
        transfer_result = await position_transfer.execute()
        assert transfer_result.success
        
# 2. ﮔ۷۰ﮔﮒﻝﭨﮔﻛﺛﮒ۳ﺎﻟﺑ۴ﺅﺙﻟ۶۵ﮒﻟ۰۴ﮒ?
        await self._simulate_subsequent_failure()
        
        # 3. ﻠ۹ﻟﺁﻟ۰۴ﮒﺟﮔ۶ﻟ۰
        compensation_result = await compensation_coordinator.trigger_compensation()
        assert compensation_result.success
        
        # 4. ﻠ۹ﻟﺁﮔﺍﮔ؟ﻛﺕﻟﺑﮔ?
        source_position = await self._get_source_position()
        target_position = await self._get_target_position()
        
        # ﻟ۰۴ﮒﺟﮒﮒﭦﮔ۱ﮒ۳ﮒﺍﻟﺛ؛ﻝ۶ﭨﮒﻝﭘﮔ?
        assert source_position.available == original_source_position
        assert target_position.available == original_target_position
        
    async def test_capital_adjustment_compensation(self):
        """ﮔﭖﻟﺁﻟﭖﻠﻟﺍﮔﺑﻟ۰۴ﮒﺟﻝ،ﺁﮒﺍﻝ،?""
        # ﻝﺎﭨﻛﺙﺙﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﮔﭖﻟﺁ...
        pass
```

#### 8.2.2 ﮔﻠﮔﺏ۷ﮒ۴ﮔﭖﻟﺁ
```python
class TestFaultInjection:
    """ﮔﻠﮔﺏ۷ﮒ۴ﮔﭖﻟﺁ"""
    
    async def test_network_partition_during_compensation(self):
        """ﮔﭖﻟﺁﻟ۰۴ﮒﺟﮔﻠﺑﻝﺛﻝﭨﮒﮒﭦ"""
        # 1. ﮒﺙﮒ۶ﻟ۰۴ﮒ?
        compensation_task = asyncio.create_task(
            compensation_executor.execute_compensation(tx_id, participant_id)
        )
        
        # 2. ﮔﺏ۷ﮒ۴ﻝﺛﻝﭨﮔﻠ
        await self._inject_network_partition()
        
# 3. ﻠ۹ﻟﺁﻟ۰۴ﮒﺟﮔ۲ﻝ۰؟ﮒ۳ﻝﻝﺛﻝﭨﮔﻠ
        try:
            result = await asyncio.wait_for(compensation_task, timeout=5.0)
            # ﮒﭦﻟﺁ۴ﻟﭘﮔﭘﮔﻟﺟﮒﻠﮒﺛﻝﻠﻟﺁ?
        except asyncio.TimeoutError:
            pass  # ﻠ۱ﮔﻟ۰ﻛﺕﭦ
            
        # 4. ﮔ۱ﮒ۳ﻝﺛﻝﭨ
        await self._restore_network()
        
        # 5. ﻠ۹ﻟﺁﻟ۰۴ﮒﺟﮒﺁﻛﭨ۴ﮔ۱ﮒ۳
        result = await compensation_executor.execute_compensation(tx_id, participant_id)
        assert result.success or result.skipped
        
    async def test_database_failure_during_compensation(self):
        """ﮔﭖﻟﺁﻟ۰۴ﮒﺟﮔﻠﺑﮔﺍﮔ؟ﮒﭦﮔﻠ?""
        # ﻝﺎﭨﻛﺙﺙﻝﺛﻝﭨﮒﮒﭦﮔﭖﻟﺁ...
        pass
```

### 8.3 ﮔ۶ﻟﺛﮔﭖﻟﺁ

#### 8.3.1 ﻟ۰۴ﮒﺟﮔ۶ﻟﺛﮒﭦﮒﮔﭖﻟﺁ
```python
class TestCompensationPerformance:
    """ﻟ۰۴ﮒﺟﮔ۶ﻟﺛﮔﭖﻟﺁ"""
    
    async def test_compensation_latency(self):
        """ﮔﭖﻟﺁﻟ۰۴ﮒﺟﮒﭨﭘﻟﺟ"""
        latencies = []
        
        for i in range(100):
            start_time = time.time()
            result = await compensation_executor.execute_compensation(
                f"tx_test_{i}", "participant_1"
            )
            end_time = time.time()
            
            assert result.success
            latencies.append(end_time - start_time)
            
        # ﻟ؟۰ﻝ؟ﻝﭨﻟ؟۰ﻛﺟ۰ﮔﺁ
        avg_latency = sum(latencies) / len(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        
        # ﮔ۶ﻟﺛﻟ۵ﮔﺎ: ﮒﺗﺏﮒﮒﭨﭘﻟﺟ < 100ms, P95ﮒﭨﭘﻟﺟ < 200ms
        assert avg_latency < 0.1, f"ﮒﺗﺏﮒﮒﭨﭘﻟﺟﻟﺟﻠ،: {avg_latency}"
        assert p95_latency < 0.2, f"P95ﮒﭨﭘﻟﺟﻟﺟﻠ،: {p95_latency}"
        
    async def test_concurrent_compensation(self):
        """ﮔﭖﻟﺁﮒﺗﭘﮒﻟ۰۴ﮒﺟ"""
        # ﮒﮒﭨﭦﮒ۳ﻛﺕ۹ﮒﺗﭘﮒﻟ۰۴ﮒﺟﻛﭨﭨﮒ۰
        tasks = []
        for i in range(50):
            task = compensation_executor.execute_compensation(
                f"tx_concurrent_{i}", f"participant_{i % 5}"
            )
            tasks.append(task)
            
        # ﮒﺗﭘﮒﮔ۶ﻟ۰
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # ﻠ۹ﻟﺁﮔﮔﻟ۰۴ﮒﺟﮔﮒ?
        success_count = sum(1 for r in results if isinstance(r, CompensationResult) and r.success)
        assert success_count >= 45, f"ﮒﺗﭘﮒﻟ۰۴ﮒﺟﮔﮒﻝﻟﺟﻛﺛ? {success_count}/50"
```

---

## 9. ﮒ؟ﮔﺛﻛﺕﻠ۷ﻝﺛ?

### 9.1 ﻛﺝﻟﭖﻝﭨﻛﭨﭘ

| ﻝﭨﻛﭨﭘ | ﻝﮔ؛ﻟ۵ﮔﺎ | ﻠﻝﺛ؟ﻟ۵ﮔﺎ | ﻠ۷ﻝﺛﺎﮔﺗﮒﺙ |
|------|----------|----------|----------|
| **PostgreSQL** | 12+ | ﻠﻟ۵JSONBﮔﺁﮔﺅﺙﻟ؟ﺝﻝﺛ؟ﮒﻝﻟﺟﮔ۴ﮔﺎ | ﻝ؛ﻝ،ﻠ۷ﻝﺛﺎﮔﻛﭦﮔﮒ۰ |
| **Redis** | 6.0+ | ﮒﺁﻝ۷Streamsﮒﻟﺛﺅﺙﻠﻝﺛ؟ﮔﻛﺗﮒ | ﻝ؛ﻝ،ﻠ۷ﻝﺛﺎﮔﻛﭦﮔﮒ۰ |
| **Python** | 3.9+ | ﮒ؟ﻟ۲asyncpg, redis-pyﻝﻛﺝﻟﭖ?| ﮒﭦﻝ۷ﮔﮒ۰ﮒ?|
| **ﻝﮔ۶ﻝﺏﭨﻝﭨ** | Prometheus 2.0+ | ﻠﻝﺛ؟ﮔﮒﮒﮒﻟ۵ﻟ۶ﮒ?| ﻝ؛ﻝ،ﻠ۷ﻝﺛﺎ |

### 9.2 ﻠﻝﺛ؟ﻝ۳ﭦﻛﺝ

#### 9.2.1 ﻟ۰۴ﮒﺟﻠﻝﺛ؟
```yaml
# compensation_config.yaml
compensation:
  # ﻠﻟﺁﻠﻝﺛ؟
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
        
  # ﻟﭘﮔﭘﻠﻝﺛ؟
  timeouts:
    compensation_execution: 30  # ﻝ۶?
    participant_response: 10    # ﻝ۶?
    
  # ﻝﮔ۶ﻠﻝﺛ؟
  monitoring:
    metrics_enabled: true
    detailed_logging: true
    alert_thresholds:
      success_rate: 0.95
      avg_duration: 0.5  # ﻝ۶?
      
  # ﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱ﻠﻝﺛ؟
  manual_intervention:
    auto_trigger: true
    alert_channels:
      - email
      - slack
    escalation_rules:
      - after_retries_exhausted: true
      - after_duration_exceeded: 300  # 5ﮒﻠ
```

#### 9.2.2 ﮔﺍﮔ؟ﮒﭦﻠﻝﺛ?
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
    
  # ﻟ۰۷ﻠﻝﺛ?
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

### 9.3 ﻠ۷ﻝﺛﺎﮔﭘﮔ

```
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﻠ۷ﻝﺛﺎﮔﭘﮔ                            ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗ? ﻗ?               ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮔﮒ۰ﻠﻝﺝ۳                          ﻗ? ﻗ?
ﻗ? ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?          ﻗ? ﻗ?
ﻗ? ﻗ? ﻗ? ﻟﻝﺗ1   ﻗ? ﻗ? ﻟﻝﺗ2   ﻗ? ﻗ? ﻟﻝﺗ3   ﻗ?          ﻗ? ﻗ?
ﻗ? ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?          ﻗ? ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗ?                          ﻗ?                                 ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗ? ﻗ?               ﮔﺍﮔ؟ﮒﭦﻛﺕﻝﺙﮒﮒﺎ?                          ﻗ? ﻗ?
ﻗ? ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                 ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?         ﻗ? ﻗ?
ﻗ? ﻗ? ﻗPostgreSQLﻗ?                 ﻗ? Redis   ﻗ?         ﻗ? ﻗ?
ﻗ? ﻗ? ﻗ? ﻠﻝﺝ۳    ﻗ?                 ﻗ? ﻠﻝﺝ۳    ﻗ?         ﻗ? ﻗ?
ﻗ? ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                 ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?         ﻗ? ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗ?                          ﻗ?                                 ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗ? ﻗ?               ﻝﮔ۶ﻛﺕﮒﻟ۵ﮒﺎ                             ﻗ? ﻗ?
ﻗ? ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?          ﻗ? ﻗ?
ﻗ? ﻗ? ﻗPrometheusﻗ? ﻗ?Grafana  ﻗ? ﻗ?Alert    ﻗ?          ﻗ? ﻗ?
ﻗ? ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?          ﻗ? ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
```

---

## 10. ﻝﭨﺑﮔ۳ﻛﺕﻟﺟﻝﭨ?

### 10.1 ﮔ۴ﮒﺕﺕﻝﭨﺑﮔ۳

#### 10.1.1 ﮒ۴ﮒﭦﺓﮔ۲ﮔ?
```python
class CompensationHealthChecker:
    """ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮒ۴ﮒﭦﺓﮔ۲ﮔ?""
    
    async def check_health(self) -> HealthStatus:
        """ﮔ۲ﮔ۴ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﻝﺏﭨﻝﭨﮒ۴ﮒﭦﺓﻝﭘﮔ?""
        checks = []
        
        # ﮔ۲ﮔ۴ﮔﺍﮔ؟ﮒﭦﻟﺟﮔ۴
        db_ok = await self._check_database_connection()
        checks.append(HealthCheck("database", db_ok))
        
        # ﮔ۲ﮔ۴Redisﻟﺟﮔ۴
        redis_ok = await self._check_redis_connection()
        checks.append(HealthCheck("redis", redis_ok))
        
        # ﮔ۲ﮔ۴ﮒﺝﮒ۳ﻝﻟ۰۴ﮒﺟ
        pending_count = await self._get_pending_compensations()
        checks.append(HealthCheck(
            "pending_compensations", 
            pending_count < 100,
            details={"count": pending_count}
        ))
        
        # ﮔ۲ﮔ۴ﻟ۰۴ﮒﺟﮔﮒﻝ
        success_rate = await self._get_success_rate()
        checks.append(HealthCheck(
            "success_rate",
            success_rate > 0.95,
            details={"rate": success_rate}
        ))
        
        # ﮔﭨﻛﺛﮒ۴ﮒﭦﺓﻝﭘﮔ?
        all_healthy = all(c.healthy for c in checks)
        return HealthStatus(
            healthy=all_healthy,
            checks=checks,
            timestamp=datetime.now()
        )
```

#### 10.1.2 ﮔﺍﮔ؟ﮔﺕﻝ
```python
class CompensationDataCleaner:
    """ﻟ۰۴ﮒﺟﮔﺍﮔ؟ﮔﺕﻝ"""
    
    async def cleanup_old_data(self, retention_days: int = 30):
        """ﮔﺕﻝﮔ۶ﮔﺍﮔ?""
        # ﮔﺕﻝﮔ۶ﻝﻟ۰۴ﮒﺟﻟ؟ﺍﮒﺛ
        await self._cleanup_old_compensations(retention_days)
        
        # ﮔﺕﻝﮔ۶ﻝﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ
        await self._cleanup_old_audit_logs(retention_days)
        
        # ﮔﺕﻝﮔ۶ﻝﻝﮔ۶ﮔﺍﮔ؟
        await self._cleanup_old_metrics(retention_days)
        
    async def archive_data(self, archive_date: str):
        """ﮒﺛﮔ۰۲ﮔﺍﮔ؟"""
# ﮒﺍﮔﮒ؟ﮔ۴ﮔﮒﻝﮔﺍﮔ؟ﮒﺛﮔ۰۲ﮒﺍﮒﺓﮒﮒ?
        await self._archive_compensations(archive_date)
        await self._archive_logs(archive_date)
```

### 10.2 ﮔﻠﮒ۳ﻝ

#### 10.2.1 ﮒﺕﺕﻟ۶ﮔﻠﮒ۳ﻝ
| ﮔﻠﻝﺍﻟﺎ۰ | ﮒﺁﻟﺛﮒﮒ | ﮔﮔ۴ﮔ۴ﻠ۹۳ | ﻟ۶۲ﮒﺏﮔﺗﮔ۰ |
|----------|----------|----------|----------|
| ﻟ۰۴ﮒﺟﮔﮒﻝﻛﺕﻠ?| ﻝﺛﻝﭨﻠ؟ﻠ۱ﻙﮒﺙﮔﮔﻠ?| 1. ﮔ۲ﮔ۴ﻝﺛﻝﭨﻟﺟﮔ?br>2. ﮔ۲ﮔ۴ﮒﺙﮔﻝﭘﮔ?br>3. ﮔ۴ﻝﻠﻟﺁﺁﮔ۴ﮒﺟ | 1. ﻛﺟ؟ﮒ۳ﻝﺛﻝﭨ<br>2. ﻠﮒﺁﮒﺙﮔ<br>3. ﻟﺍﮔﺑﻠﻟﺁﻝﻝ۴ |
| ﻟ۰۴ﮒﺟﮒﭨﭘﻟﺟﮒ۱ﮒ | ﮔﺍﮔ؟ﮒﭦﮔ۶ﻟﺛﻠ؟ﻠ۱ﻙﻟﭖﮔﭦﻛﺕﻟﭘ?| 1. ﮔ۲ﮔ۴ﮔﺍﮔ؟ﮒﭦﮔ۶ﻟﺛ<br>2. ﮔ۲ﮔ۴ﻝﺏﭨﻝﭨﻟﭖﮔﭦ?br>3. ﮒﮔﮔ۱ﮔ۴ﻟﺁ?| 1. ﻛﺙﮒﮔﺍﮔ؟ﮒﭦ?br>2. ﮔ۸ﮒ؟ﺗﻟﭖﮔﭦ<br>3. ﻛﺙﮒﮔ۴ﻟﺁ۱ |

#### 10.2.2 ﻝﺝﻠﺝﮔ۱ﮒ۳
```python
class CompensationDisasterRecovery:
    """ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﻝﺝﻠﺝﮔ۱ﮒ۳"""
    
    async def recover_from_failure(self, failure_type: str) -> RecoveryResult:
"""ﻛﭨﮔﻠﻛﺕﮔ۱ﮒ۳"""
        if failure_type == "database_outage":
            return await self._recover_from_database_outage()
        elif failure_type == "redis_outage":
            return await self._recover_from_redis_outage()
        elif failure_type == "data_corruption":
            return await self._recover_from_data_corruption()
        else:
            return RecoveryResult.failed(f"ﮔ۹ﻝ۴ﮔﻠﻝﺎﭨﮒ: {failure_type}")
            
    async def _recover_from_database_outage(self) -> RecoveryResult:
        """ﻛﭨﮔﺍﮔ؟ﮒﭦﮔﻠﮔ۱ﮒ۳"""
# 1. ﻝﮒﺝﮔﺍﮔ؟ﮒﭦﮔ۱ﮒ۳?
        await self._wait_for_database_recovery()
        
        # 2. ﮔ۲ﮔ۴ﮔﺍﮔ؟ﻛﺕﻟﺑﮔ?
        inconsistencies = await self._check_data_consistency()
        
        # 3. ﻛﺟ؟ﮒ۳ﻛﺕﻛﺕﻟﺑﮔﺍﮔ?
        if inconsistencies:
            await self._repair_inconsistencies(inconsistencies)
            
        # 4. ﻠﮔﺍﮒﺁﮒ۷ﻟ۰۴ﮒﺟﮒ۳ﻝ
        await self._restart_compensation_processing()
        
        return RecoveryResult.success("ﮔﺍﮔ؟ﮒﭦﮔﻠﮔ۱ﮒ۳ﮒ؟ﮔ?)
```

---

## ﻠﮒﺛﺅﺙﻝﺕﮒﺏﮔﮔ۰۲ﻝﺑ۱ﮒﺙ?

1. ﮒ۳ﮒﺙﮔﮔﺍﮔ؟ﻛﺕﻟﺑﮔ۶ﻟ؟ﺝﻟ؟۰ﮔﺗﮔ۰?md - ﻛﺕﭨﻟ؟ﺝﻟ؟۰ﮔﮔ۰?
2. Sagaﮔ۷۰ﮒﺙﮒ؟ﻝﺍﮔﭖﻝ۷ﮒ?md - ﮔﭖﻝ۷ﮒﺝﮔﮔ۰?
3.  - ﮒﺙﮔﻠﻠﮒ۷ﻟ؟ﺝﻟ؟?
4. [STORAGE_TIER.md](05_IMPLEMENTATION/04_INFRASTRUCTURE/STORAGE_TIER.md) - ﮒﮒ۷ﮒﺎﻟ؟ﺝﻟ؟?

---

**ﮔﮔ۰۲ﻝﮔ؛ﮒﮒﺎ**:
- v1.0.0 (2026-04-02): ﮒﮒ۶ﻝﮔ؛ﺅﺙﮒ؟ﮔﺑﻟ۰۴ﮒﺟﻛﭦﮒ۰ﻟ؟ﺝﻟ؟?

**ﮒ؟۰ﮔﺕﻟ؟ﺍﮒﺛ**:
- ﮔﭘﮔﮒ؟۰ﮔﺕ: ﻠ۵ﮒﺕﻟﮒﺝﮔﭘﮔﮒﺕ?
- ﮔﮔﺁﮒ؟۰ﮔ? ﮒﺝﮒ؟۰ﮔ?
- ﮒ؟ﮒ۷ﮒ؟۰ﮔﺕ: ﮒﺝﮒ؟۰ﮔ?

**ﮒﻟ۶ﮔ۶ﮔ۲ﮔ?*:
- ﻗ?ﮒﺗﻝﮔ۶ﻟ؟ﺝﻟ؟۰ﮒ؟ﮔ?
- ﻗ?ﻠﻟﺁﮔﭦﮒﭘﮒ؟ﮒ
- ﻗ?ﻠﻟﺁﺁﮒ۳ﻝﮒ۷ﻠ۱
- ﻗ?ﻝﮔ۶ﮒﺁﻟ۶ﮔﭖﮔ۶ﮒﮒ?
- ﻗ?ﮔﭖﻟﺁﮔﺗﮔ۰ﮒ؟ﮒ۳
- ﻗ?ﻝ؛۵ﮒﻛﺕﻛﺕﮔﭦﮔﮔﮒ (ﻠ۱ﻟ؟۰ﮒﻟ۶ﻝﻗ۴95%)