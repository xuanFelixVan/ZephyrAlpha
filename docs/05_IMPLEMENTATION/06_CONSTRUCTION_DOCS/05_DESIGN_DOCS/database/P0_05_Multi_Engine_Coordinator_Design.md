﻿---
module_id: MULTI_ENGINE_COORDINATOR_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕﻟﮒﺝﮔﭘﮔﮒﺕ?
responsibility:
  - 实施指南、部署文档
  - 文档治理
  - 日志系统
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮒ۳ﮒﺙﮔﮒﮒﮒ۷ﮔﮒ
applicable_scope: ﮒ۳ﮒﺙﮔﻛﭦﮒ۰ﮒﻟﺍ?
compliance_level: ﻛﺕﻛﺕﮔﭦﮔﮔﮒ
parent_document: P0-01_Database_Design_Document.md
implementation_status: ﻟﺟﻟ۰ﻛﺕ?---


# ﮒ۳ﮒﺙﮔﮒﮒﮒ۷ﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰ﺅﺙﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮒﺅﺙ
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨ v5.0 - ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮒﮒ۳ﮒﺙﮔﮒﮒﮒ۷ﻟ؟ﺝﻟ؟۰
> **ﻟ؟ﺝﻟ؟۰ﮔ۷۰ﮒﺙ**: Sagaﮒﮒﺕﮒﺙﻛﭦﮒ۰ﮔ۷۰ﮒﺙ?+ ﻛﭦﻛﭨﭘﻠ۸ﺎﮒ۷ﮔﭘﮔ
> **ﮔﺕﮒﺟﻟﻟﺑ۲**: ﮒ۳ﮒﺙﮔﻛﭦﮒ۰ﮒﻟﺍﻙﮔﺍﮔ؟ﻛﺕﻟﺑﮔ۶ﻛﺟﻠﻙﮔﻠﮔ۱ﮒ۳?

## ﻭ ﮒﮒﮒ۷ﮔ۵ﻟﺟ?

### Sagaﻛﭦﮒ۰ﮔﭘﮔ

```
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   Sagaﮒﻟﺍﮒ?(Saga Coordinator)             ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗ? ﻗ? 1. ﻛﭦﮒ۰ﻝﺙﮔ (Transaction Orchestration)              ﻗ? ﻗ?
ﻗ? ﻗ? 2. ﻝﭘﮔﻝ؟۰ﻝ?(State Management)                       ﻗ? ﻗ?
ﻗ? ﻗ? 3. ﻟ۰۴ﮒﺟﮔﭦﮒﭘ (Compensation Mechanism)                 ﻗ? ﻗ?
ﻗ? ﻗ? 4. ﮔﻠﮔ۱ﮒ۳ (Failure Recovery)                       ﻗ? ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
                            ﻗ?ﻛﭦﻛﭨﭘﻠ۸ﺎﮒ۷
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   Sagaﮔ۶ﻟ۰ﮔ۴ﻠ۹۳                              ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗ? ﻗStep 1    ﻗ?ﻗStep 2    ﻗ?ﻗStep 3    ﻗ?ﻗStep 4    ﻗ?     ﻗ?
ﻗ? ﻗﮒﮒﭨﭦﻟ؟۱ﮒ? ﻗﻗﻗﮒﭨﻝﭨﻟﭖﻠ? ﻗﻗﻗﮔﻛﭦ۳ﮒﺙﮔ? ﻗﻗﻗﮔﺑﮔﺍﮔﻛﭨ? ﻗ?     ﻗ?
ﻗ? ﻗ?         ﻗ?ﻗ?         ﻗ?ﻗ?         ﻗ?ﻗ?         ﻗ?     ﻗ?
ﻗ? ﻗCompensateﻗ?ﻗCompensateﻗ?ﻗCompensateﻗ?ﻗCompensateﻗ?     ﻗ?
ﻗ? ﻗﮒﮔﭘﻟ؟۱ﮒ? ﻗ?ﻗﻟ۶۲ﮒﭨﻟﭖﻠ? ﻗ?ﻗﮒﮔﭘﻟ؟۱ﮒ? ﻗ?ﻗﮒﮔﭨﮔﻛﭨ? ﻗ?     ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
```

---

## 1. Sagaﮒﻟﺍﮒ۷ﮔﺕﮒﺟﻟ؟ﺝﻟ؟?

### 1.1 Sagaﻝﭘﮔﮔﭦ

```python
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal
import asyncio

class SagaStatus(Enum):
    """Sagaﻝﭘﮔ?""
    PENDING = 'pending'           # ﮒﺝﮔ۶ﻟ۰?
    RUNNING = 'running'           # ﮔ۶ﻟ۰ﻛﺕ?
    COMPLETED = 'completed'       # ﮒﺓﺎﮒ؟ﮔ?
    COMPENSATING = 'compensating' # ﻟ۰۴ﮒﺟﻛﺕ?
    COMPENSATED = 'compensated'   # ﮒﺓﺎﻟ۰۴ﮒ?
    FAILED = 'failed'             # ﮒ۳ﺎﻟﺑ۴

class StepStatus(Enum):
"""ﮔ۴ﻠ۹۳ﻝﭘﮔ?""
    PENDING = 'pending'           # ﮒﺝﮔ۶ﻟ۰?
    RUNNING = 'running'           # ﮔ۶ﻟ۰ﻛﺕ?
    COMPLETED = 'completed'       # ﮒﺓﺎﮒ؟ﮔ?
    COMPENSATING = 'compensating' # ﻟ۰۴ﮒﺟﻛﺕ?
    COMPENSATED = 'compensated'   # ﮒﺓﺎﻟ۰۴ﮒ?
    FAILED = 'failed'             # ﮒ۳ﺎﻟﺑ۴

class SagaStep:
"""Sagaﮔ۴ﻠ۹۳"""
    
    def __init__(
        self,
        step_id: str,
        step_name: str,
        execute_func: callable,
        compensate_func: callable,
        timeout: int = 30
    ):
        self.step_id = step_id
        self.step_name = step_name
        self.execute_func = execute_func
        self.compensate_func = compensate_func
        self.timeout = timeout
        self.status = StepStatus.PENDING
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
"""ﮔ۶ﻟ۰ﮔ۴ﻠ۹۳"""
        self.status = StepStatus.RUNNING
        self.started_at = datetime.now()
        
        try:
# ﮔ۶ﻟ۰ﮔ۴ﻠ۹۳ﺅﺙﮒﺕ۵ﻟﭘﮔﭘﮔ۶ﮒﭘ
            result = await asyncio.wait_for(
                self.execute_func(context),
                timeout=self.timeout
            )
            
            self.result = result
            self.status = StepStatus.COMPLETED
            self.completed_at = datetime.now()
            
            return result
        except asyncio.TimeoutError:
            self.status = StepStatus.FAILED
self.error = f"ﮔ۴ﻠ۹۳ﮔ۶ﻟ۰ﻟﭘﮔﭘ: {self.timeout}ﻝ۶?
            raise Exception(self.error)
        except Exception as e:
            self.status = StepStatus.FAILED
            self.error = str(e)
            raise
    
    async def compensate(self, context: Dict[str, Any]) -> bool:
"""ﻟ۰۴ﮒﺟﮔ۴ﻠ۹۳"""
        self.status = StepStatus.COMPENSATING
        
        try:
            # ﮔ۶ﻟ۰ﻟ۰۴ﮒﺟﺅﺙﮒﺕ۵ﻟﭘﮔﭘﮔ۶ﮒﭘ
            success = await asyncio.wait_for(
                self.compensate_func(context, self.result),
                timeout=self.timeout
            )
            
            self.status = StepStatus.COMPENSATED
            return success
        except Exception as e:
            self.status = StepStatus.FAILED
            self.error = f"ﻟ۰۴ﮒﺟﮒ۳ﺎﻟﺑ۴: {str(e)}"
            return False

class Saga:
    """Sagaﻛﭦﮒ۰"""
    
    def __init__(self, saga_id: str, saga_name: str):
        self.saga_id = saga_id
        self.saga_name = saga_name
        self.status = SagaStatus.PENDING
        self.steps: List[SagaStep] = []
        self.context: Dict[str, Any] = {}
        self.current_step_index = 0
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_step(self, step: SagaStep) -> None:
"""ﮔﺓﭨﮒﮔ۴ﻠ۹۳"""
        self.steps.append(step)
    
    async def execute(self) -> bool:
        """ﮔ۶ﻟ۰Saga"""
        self.status = SagaStatus.RUNNING
        self.updated_at = datetime.now()
        
        try:
# ﻠ۰ﭦﮒﭦﮔ۶ﻟ۰ﮔﮔﮔ۴ﻠ۹?
            for i, step in enumerate(self.steps):
                self.current_step_index = i
                
# ﮔ۶ﻟ۰ﮔ۴ﻠ۹۳
                result = await step.execute(self.context)
                
                # ﮔﺑﮔﺍﻛﺕﻛﺕﮔ?
                self.context.update(result)
                self.updated_at = datetime.now()
            
# ﮔﮔﮔ۴ﻠ۹۳ﮔ۶ﻟ۰ﮔﮒ?
            self.status = SagaStatus.COMPLETED
            self.updated_at = datetime.now()
            return True
        
        except Exception as e:
            # ﮔ۶ﻟ۰ﮒ۳ﺎﻟﺑ۴ﺅﺙﮒﺙﮒ۶ﻟ۰۴ﮒ?
            print(f"Sagaﮔ۶ﻟ۰ﮒ۳ﺎﻟﺑ۴: {e}")
            await self.compensate()
            return False
    
    async def compensate(self) -> bool:
        """ﻟ۰۴ﮒﺟSaga"""
        self.status = SagaStatus.COMPENSATING
        self.updated_at = datetime.now()
        
        try:
# ﻠﮒﭦﻟ۰۴ﮒﺟﮒﺓﺎﮒ؟ﮔﻝﮔ۴ﻠ۹۳
            for i in range(self.current_step_index, -1, -1):
                step = self.steps[i]
                
                if step.status == StepStatus.COMPLETED:
# ﻟ۰۴ﮒﺟﮔ۴ﻠ۹۳
                    success = await step.compensate(self.context)
                    
                    if not success:
print(f"ﮔ۴ﻠ۹۳ﻟ۰۴ﮒﺟﮒ۳ﺎﻟﺑ۴: {step.step_name}")
            
            self.status = SagaStatus.COMPENSATED
            self.updated_at = datetime.now()
            return True
        
        except Exception as e:
            print(f"Sagaﻟ۰۴ﮒﺟﮒ۳ﺎﻟﺑ۴: {e}")
            self.status = SagaStatus.FAILED
            self.updated_at = datetime.now()
            return False
```

---

## 2. ﻟ؟۱ﮒSagaﻟ؟ﺝﻟ؟۰

### 2.1 ﻟ؟۱ﮒSagaﮔ۴ﻠ۹۳

```python
class OrderSaga:
    """ﻟ؟۱ﮒSaga"""
    
    def __init__(
        self,
        order_service,
        account_service,
        position_service,
        engine_manager
    ):
        self.order_service = order_service
        self.account_service = account_service
        self.position_service = position_service
        self.engine_manager = engine_manager
    
    async def create_order_saga(self, order_data: Dict[str, Any]) -> Saga:
        """ﮒﮒﭨﭦﻟ؟۱ﮒSaga"""
        saga = Saga(
            saga_id=f"SAGA_ORDER_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            saga_name="ﻟ؟۱ﮒﮔ۶ﻟ۰Saga"
        )
        
        # Step 1: ﮒﮒﭨﭦﻟ؟۱ﮒ
        step1 = SagaStep(
            step_id="create_order",
            step_name="ﮒﮒﭨﭦﻟ؟۱ﮒ",
            execute_func=self._create_order,
            compensate_func=self._cancel_order,
            timeout=10
        )
        
        # Step 2: ﮒﭨﻝﭨﻟﭖﻠ/ﮔﻛﭨ
        step2 = SagaStep(
            step_id="freeze_resource",
            step_name="ﮒﭨﻝﭨﻟﭖﮔﭦ",
            execute_func=self._freeze_resource,
            compensate_func=self._unfreeze_resource,
            timeout=10
        )
        
        # Step 3: ﮔﻛﭦ۳ﮒﺍﮒﺙﮔ?
        step3 = SagaStep(
            step_id="submit_to_engine",
            step_name="ﮔﻛﭦ۳ﮒﺙﮔ",
            execute_func=self._submit_to_engine,
            compensate_func=self._cancel_from_engine,
            timeout=30
        )
        
        # Step 4: ﮔﺑﮔﺍﮔﻛﭨ
        step4 = SagaStep(
            step_id="update_position",
            step_name="ﮔﺑﮔﺍﮔﻛﭨ",
            execute_func=self._update_position,
            compensate_func=self._rollback_position,
            timeout=10
        )
        
# ﮔﺓﭨﮒﮔ۴ﻠ۹۳
        saga.add_step(step1)
        saga.add_step(step2)
        saga.add_step(step3)
        saga.add_step(step4)
        
        # ﮒﮒ۶ﮒﻛﺕﻛﺕﮔ
        saga.context = {
            'order_data': order_data
        }
        
        return saga
    
    async def _create_order(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """ﮒﮒﭨﭦﻟ؟۱ﮒ"""
        order_data = context['order_data']
        
        # ﮒﮒﭨﭦﻟ؟۱ﮒ
        order = await self.order_service.create_order(order_data)
        
        return {
            'order_id': order['id'],
            'order_code': order['order_code'],
            'order': order
        }
    
    async def _cancel_order(self, context: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """ﮒﮔﭘﻟ؟۱ﮒ"""
        order_id = result['order_id']
        
        # ﮒﮔﭘﻟ؟۱ﮒ
        success = await self.order_service.cancel_order(order_id, reason="Sagaﻟ۰۴ﮒﺟ")
        
        return success
    
    async def _freeze_resource(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """ﮒﭨﻝﭨﻟﭖﮔﭦ"""
        order = context['order']
        
        if order['direction'] == 'buy':
            # ﻛﺗﺍﮒ۴ﺅﺙﮒﭨﻝﭨﻟﭖﻠ?
            frozen_amount = order['order_price'] * order['order_quantity']
            success = await self.account_service.freeze_cash(
                order['account_id'],
                frozen_amount
            )
            
            return {
                'frozen_amount': frozen_amount,
                'frozen_type': 'cash'
            }
        else:
            # ﮒﮒﭦﺅﺙﮒﭨﻝﭨﮔﻛﭨ?
            success = await self.position_service.freeze_position(
                order['account_id'],
                order['stock_code'],
                order['order_quantity']
            )
            
            return {
                'frozen_quantity': order['order_quantity'],
                'frozen_type': 'position'
            }
    
    async def _unfreeze_resource(self, context: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """ﻟ۶۲ﮒﭨﻟﭖﮔﭦ"""
        order = context['order']
        
        if result['frozen_type'] == 'cash':
            # ﻟ۶۲ﮒﭨﻟﭖﻠ
            success = await self.account_service.unfreeze_cash(
                order['account_id'],
                result['frozen_amount']
            )
        else:
            # ﻟ۶۲ﮒﭨﮔﻛﭨ
            success = await self.position_service.unfreeze_position(
                order['account_id'],
                order['stock_code'],
                result['frozen_quantity']
            )
        
        return success
    
    async def _submit_to_engine(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """ﮔﻛﭦ۳ﮒﺍﮒﺙﮔ?""
        order = context['order']
        
        # ﻟﺓﮒﮒﺙﮔ
        engine = self.engine_manager.get_engine(order['engine_id'])
        
        if not engine:
raise Exception(f"ﮒﺙﮔﻛﺕﮒﮒ? {order['engine_id']}")
        
        # ﮔﻛﭦ۳ﻟ؟۱ﮒﮒﺍﮒﺙﮔ?
        result = await engine.create_order(
            account_id=order['account_id'],
            stock_code=order['stock_code'],
            exchange=order['exchange'],
            direction=order['direction'],
            order_type=order['order_type'],
            price=Decimal(str(order['order_price'])),
            quantity=order['order_quantity']
        )
        
        if not result['success']:
            raise Exception(f"ﮒﺙﮔﮔﻛﭦ۳ﮒ۳ﺎﻟﺑ۴: {result.get('error')}")
        
        return {
            'broker_order_id': result['order_id'],
            'engine_result': result
        }
    
    async def _cancel_from_engine(self, context: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """ﻛﭨﮒﺙﮔﮒﮔﭘﻟ؟۱ﮒ?""
        order = context['order']
        broker_order_id = result['broker_order_id']
        
        # ﻟﺓﮒﮒﺙﮔ
        engine = self.engine_manager.get_engine(order['engine_id'])
        
        if not engine:
            return False
        
        # ﮒﮔﭘﻟ؟۱ﮒ
        success = await engine.cancel_order(broker_order_id)
        
        return success
    
    async def _update_position(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """ﮔﺑﮔﺍﮔﻛﭨ"""
        order = context['order']
        
        # ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒﮔﻛﭦ۳ﮔﮒﭖ
        order_status = await self.order_service.query_order(order['id'])
        
        if order_status['status'] != 'filled':
            raise Exception("ﻟ؟۱ﮒﮔ۹ﮔﻛﭦ?)
        
        # ﮔﺑﮔﺍﮔﻛﭨ
        if order['direction'] == 'buy':
# ﻛﺗﺍﮒ۴ﺅﺙﮒ۱ﮒﮔﻛﭨ?
            position = await self.position_service.increase_position(
                account_id=order['account_id'],
                stock_code=order['stock_code'],
                quantity=order_status['filled_quantity'],
                price=Decimal(str(order_status['filled_price'])),
                trade_id=order_status.get('trade_id')
            )
        else:
            # ﮒﮒﭦﺅﺙﮒﮒﺍﮔﻛﭨ?
            position = await self.position_service.decrease_position(
                account_id=order['account_id'],
                stock_code=order['stock_code'],
                quantity=order_status['filled_quantity'],
                price=Decimal(str(order_status['filled_price'])),
                trade_id=order_status.get('trade_id')
            )
        
        return {
            'position': position
        }
    
    async def _rollback_position(self, context: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """ﮒﮔﭨﮔﻛﭨ"""
        order = context['order']
        position = result['position']
        
        # ﮒﮔﭨﮔﻛﭨ
        if order['direction'] == 'buy':
            # ﻛﺗﺍﮒ۴ﮒﮔﭨﺅﺙﮒﮒﺍﮔﻛﭨ?
            success = await self.position_service.decrease_position(
                account_id=order['account_id'],
                stock_code=order['stock_code'],
                quantity=position['quantity'],
                price=position['avg_cost']
            )
        else:
# ﮒﮒﭦﮒﮔﭨﺅﺙﮒ۱ﮒﮔﻛﭨ?
            success = await self.position_service.increase_position(
                account_id=order['account_id'],
                stock_code=order['stock_code'],
                quantity=position['quantity'],
                price=position['avg_cost']
            )
        
        return success
```

---

## 3. Sagaﮒﻟﺍﮒ۷ﮔﮒ?

### 3.1 ﮒﻟﺍﮒ۷ﮒ؟ﻝ?

```python
from typing import Dict, Any, Optional
import uuid
import json

class SagaCoordinator:
    """Sagaﮒﻟﺍﮒ?""
    
    def __init__(self, saga_repository):
        self.saga_repository = saga_repository
        self.active_sagas: Dict[str, Saga] = {}
    
    async def start_saga(self, saga: Saga) -> str:
        """ﮒﺁﮒ۷Saga"""
# ﻛﺟﮒSaga
        await self.saga_repository.save_saga(saga)
        
# ﮔﺓﭨﮒﮒﺍﮔﺑﭨﻟﺓﮒﻟ۰?
        self.active_sagas[saga.saga_id] = saga
        
# ﮒﺙﮔ۴ﮔ۶ﻟ۰Saga
        asyncio.create_task(self._execute_saga(saga))
        
        return saga.saga_id
    
    async def _execute_saga(self, saga: Saga) -> None:
        """ﮔ۶ﻟ۰Saga"""
        try:
            # ﮔ۶ﻟ۰Saga
            success = await saga.execute()
            
            # ﮔﺑﮔﺍSagaﻝﭘﮔ?
            await self.saga_repository.update_saga_status(
                saga.saga_id,
                saga.status,
                saga.context
            )
            
            # ﻛﭨﮔﺑﭨﻟﺓﮒﻟ۰۷ﻝ۶ﭨﻠ?
            if saga.saga_id in self.active_sagas:
                del self.active_sagas[saga.saga_id]
        
        except Exception as e:
            print(f"Sagaﮔ۶ﻟ۰ﮒﺙﮒﺕﺕ: {e}")
            
            # ﮔﺑﮔﺍSagaﻝﭘﮔﻛﺕﭦﮒ۳ﺎﻟﺑ۴
            await self.saga_repository.update_saga_status(
                saga.saga_id,
                SagaStatus.FAILED,
                saga.context
            )
            
            # ﻛﭨﮔﺑﭨﻟﺓﮒﻟ۰۷ﻝ۶ﭨﻠ?
            if saga.saga_id in self.active_sagas:
                del self.active_sagas[saga.saga_id]
    
    async def get_saga_status(self, saga_id: str) -> Optional[Dict[str, Any]]:
        """ﻟﺓﮒSagaﻝﭘﮔ?""
        # ﮒﮔ۴ﮔﺑﭨﻟﺓﮒﻟ۰۷
        if saga_id in self.active_sagas:
            saga = self.active_sagas[saga_id]
            return {
                'saga_id': saga.saga_id,
                'saga_name': saga.saga_name,
                'status': saga.status.value,
                'current_step': saga.current_step_index,
                'total_steps': len(saga.steps),
                'created_at': saga.created_at.isoformat(),
                'updated_at': saga.updated_at.isoformat()
            }
        
        # ﮔ۴ﮔﺍﮔ؟ﮒﭦ
        saga = await self.saga_repository.find_saga(saga_id)
        
        if not saga:
            return None
        
        return {
            'saga_id': saga['saga_id'],
            'saga_name': saga['saga_name'],
            'status': saga['status'],
            'created_at': saga['created_at'],
            'updated_at': saga['updated_at']
        }
    
    async def compensate_saga(self, saga_id: str) -> bool:
        """ﮔﮒ۷ﻟ۰۴ﮒﺟSaga"""
        saga = await self.saga_repository.find_saga(saga_id)
        
        if not saga:
            return False
        
        # ﻠﮒﭨﭦSagaﮒﺁﺗﻟﺎ۰
        saga_obj = Saga(saga['saga_id'], saga['saga_name'])
        saga_obj.status = SagaStatus(saga['status'])
        saga_obj.context = json.loads(saga['context'])
        
        # ﮔ۶ﻟ۰ﻟ۰۴ﮒﺟ
        success = await saga_obj.compensate()
        
        # ﮔﺑﮔﺍﻝﭘﮔ?
        await self.saga_repository.update_saga_status(
            saga_id,
            saga_obj.status,
            saga_obj.context
        )
        
        return success
```

---

## 4. Sagaﮔﻛﺗﮒﻟ؟ﺝﻟ؟?

### 4.1 Sagaﻟ۰۷ﻝﭨﮔ?

```sql
-- Sagaﻛﭦﮒ۰ﻟ۰?
CREATE TABLE saga_transactions (
    id BIGSERIAL PRIMARY KEY,
    saga_id VARCHAR(100) NOT NULL UNIQUE,
    saga_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    context JSONB NOT NULL DEFAULT '{}',
    current_step INT NOT NULL DEFAULT 0,
    total_steps INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    error_message TEXT
);

-- Sagaﮔ۴ﻠ۹۳ﻟ۰?
CREATE TABLE saga_steps (
    id BIGSERIAL PRIMARY KEY,
    saga_id VARCHAR(100) NOT NULL,
    step_id VARCHAR(100) NOT NULL,
    step_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    result JSONB DEFAULT '{}',
    error TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (saga_id) REFERENCES saga_transactions(saga_id)
);

-- ﻝﺑ۱ﮒﺙ
CREATE INDEX idx_saga_transactions_status ON saga_transactions(status);
CREATE INDEX idx_saga_transactions_created_at ON saga_transactions(created_at);
CREATE INDEX idx_saga_steps_saga_id ON saga_steps(saga_id);
CREATE INDEX idx_saga_steps_status ON saga_steps(status);
```

---

## 5. ﮔﻠﮔ۱ﮒ۳ﮔﭦﮒﭘ

### 5.1 ﮔﻠﮔ۲ﮔﭖ?

```python
class SagaRecoveryService:
    """Sagaﮔﻠﮔ۱ﮒ۳ﮔﮒ۰"""
    
    def __init__(self, saga_coordinator: SagaCoordinator, saga_repository):
        self.coordinator = saga_coordinator
        self.repository = saga_repository
    
    async def detect_failed_sagas(self) -> List[Dict[str, Any]]:
        """ﮔ۲ﮔﭖﮒ۳ﺎﻟﺑ۴ﻝSaga"""
        # ﮔ۴ﻟﺁ۱ﻟﭘﮔﭘﻝSaga
        timeout_sagas = await self.repository.find_timeout_sagas(timeout_minutes=30)
        
        # ﮔ۴ﻟﺁ۱ﮒﺙﮒﺕﺕﻝﭘﮔﻝSaga
        failed_sagas = await self.repository.find_sagas_by_status(SagaStatus.FAILED)
        
        return timeout_sagas + failed_sagas
    
    async def recover_saga(self, saga_id: str) -> bool:
        """ﮔ۱ﮒ۳Saga"""
        saga = await self.repository.find_saga(saga_id)
        
        if not saga:
            return False
        
# ﮔﺗﮔ؟ﻝﭘﮔﮒﺏﮒ؟ﮔ۱ﮒ۳ﻝﻝ?
        if saga['status'] == SagaStatus.RUNNING.value:
# ﮔ۶ﻟ۰ﻛﺕﻝSagaﺅﺙﻠﮔﺍﮔ۶ﻟ۰?
            return await self._retry_saga(saga)
        elif saga['status'] == SagaStatus.COMPENSATING.value:
# ﻟ۰۴ﮒﺟﻛﺕﻝSagaﺅﺙﻝﭨ۶ﻝﭨﻟ۰۴ﮒ?
            return await self._continue_compensate(saga)
        elif saga['status'] == SagaStatus.FAILED.value:
            # ﮒ۳ﺎﻟﺑ۴ﻝSagaﺅﺙﮔﮒ۷ﮒ۳ﻝ?
            return await self._manual_recovery(saga)
        
        return False
    
    async def _retry_saga(self, saga: Dict[str, Any]) -> bool:
        """ﻠﻟﺁSaga"""
        # TODO: ﮒ؟ﻝﺍﻠﻟﺁﻠﭨﻟﺝ
        return False
    
    async def _continue_compensate(self, saga: Dict[str, Any]) -> bool:
"""ﻝﭨ۶ﻝﭨﻟ۰۴ﮒﺟ"""
# TODO: ﮒ؟ﻝﺍﻝﭨ۶ﻝﭨﻟ۰۴ﮒﺟﻠﭨﻟﺝ
        return False
    
    async def _manual_recovery(self, saga: Dict[str, Any]) -> bool:
        """ﮔﮒ۷ﮔ۱ﮒ۳"""
        # TODO: ﮒ؟ﻝﺍﮔﮒ۷ﮔ۱ﮒ۳ﻠﭨﻟﺝ
        return False
```

---

## 6. ﮔ۶ﻟﺛﻛﺕﻝﮔ?

### 6.1 ﮔ۶ﻟﺛﮔﮔ

| ﮔﮔ | ﻝ؟ﮔﮒ?| ﮒ۳ﮔﺏ۷ |
|------|--------|------|
| **Sagaﮔ۶ﻟ۰ﮔﭘﻠﺑ** | < 5ﻝ۶?| ﮒﮒ،ﮔﮔﮔ۴ﻠ۹?|
| **ﻟ۰۴ﮒﺟﮔﭘﻠﺑ** | < 10ﻝ۶?| ﮒﮒ،ﮔﮔﻟ۰۴ﮒﺟﮔ۴ﻠ۹?|
| **ﮒﺗﭘﮒSagaﮔ?* | 100 | ﮒﮔﭘﮔ۶ﻟ۰ﻝSagaﮔﺍﻠ |
| **ﮔﮒﻝ?* | ﻗ?99% | Sagaﮔﮒﮒ؟ﮔﻝ?|

### 6.2 ﻝﮔ۶ﮔﮔ

```python
class SagaMonitor:
    """Sagaﻝﮔ۶"""
    
    def __init__(self):
        self.metrics = {
            'total_sagas': 0,
            'successful_sagas': 0,
            'failed_sagas': 0,
            'compensated_sagas': 0,
            'avg_execution_time': 0,
            'avg_compensation_time': 0
        }
    
    async def record_saga_completion(
        self,
        saga: Saga,
        execution_time: float
    ) -> None:
        """ﻟ؟ﺍﮒﺛSagaﮒ؟ﮔ"""
        self.metrics['total_sagas'] += 1
        
        if saga.status == SagaStatus.COMPLETED:
            self.metrics['successful_sagas'] += 1
        elif saga.status == SagaStatus.COMPENSATED:
            self.metrics['compensated_sagas'] += 1
        else:
            self.metrics['failed_sagas'] += 1
        
        # ﮔﺑﮔﺍﮒﺗﺏﮒﮔ۶ﻟ۰ﮔﭘﻠﺑ
        self.metrics['avg_execution_time'] = (
            (self.metrics['avg_execution_time'] * (self.metrics['total_sagas'] - 1) + execution_time)
            / self.metrics['total_sagas']
        )
    
    async def get_metrics(self) -> Dict[str, Any]:
"""ﻟﺓﮒﻝﮔ۶ﮔﮔ"""
        return {
            **self.metrics,
            'success_rate': (
                self.metrics['successful_sagas'] / self.metrics['total_sagas']
                if self.metrics['total_sagas'] > 0 else 0
            )
        }
```

---

**ﻝﮔ؛**: 1.0.0 | **ﮔﺑﮔﺍﮔ۴ﮔ**: 2026-04-02 | **ﻝﭘﮔ?*: ﻗ?ﮒﺓﺎﮒ؟ﮔ? 
**ﻛﺕﻛﺕﮔ?*: P0-6 ﻟﺑ۵ﮔﺓﻝ؟۰ﻝﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰