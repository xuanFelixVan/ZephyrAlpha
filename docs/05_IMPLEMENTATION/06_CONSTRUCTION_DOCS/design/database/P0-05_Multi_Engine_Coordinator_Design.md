---
module_id: MULTI_ENGINE_COORDINATOR_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕ­ﻟﮒﺝﮔﭘﮔﮒﺕ?
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮒ۳ﮒﺙﮔﮒﮒﮒ۷ﮔ ﮒ
applicable_scope: ﮒ۳ﮒﺙﮔﻛﭦﮒ۰ﮒﻟﺍ?
compliance_level: ﻛﺕﻛﺕﮔﭦﮔﮔ ﮒ
parent_document: P0-01_Database_Design_Document.md
implementation_status: ﻟﺟﻟ۰ﻛﺕ?
---

# ﮒ۳ﮒﺙﮔﮒﮒﮒ۷ﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰ﺅﺙﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔ ﮒﺅﺙ

> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨ v5.0 - ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔ ﮒﮒ۳ﮒﺙﮔﮒﮒﮒ۷ﻟ؟ﺝﻟ؟۰
> **ﻟ؟ﺝﻟ؟۰ﮔ۷۰ﮒﺙ**: Sagaﮒﮒﺕﮒﺙﻛﭦﮒ۰ﮔ۷۰ﮒﺙ?+ ﻛﭦﻛﭨﭘﻠ۸ﺎﮒ۷ﮔﭘﮔ
> **ﮔ ﺕﮒﺟﻟﻟﺑ۲**: ﮒ۳ﮒﺙﮔﻛﭦﮒ۰ﮒﻟﺍﻙﮔﺍﮔ؟ﻛﺕﻟﺑﮔ۶ﻛﺟﻠﻙﮔﻠﮔ۱ﮒ۳?

## ﻭ ﮒﮒﮒ۷ﮔ۵ﻟﺟ?

### Sagaﻛﭦﮒ۰ﮔﭘﮔ

```
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   Sagaﮒﻟﺍﮒ?(Saga Coordinator)             ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗ? ﻗ? 1. ﻛﭦﮒ۰ﻝﺙﮔ (Transaction Orchestration)              ﻗ? ﻗ?
ﻗ? ﻗ? 2. ﻝﭘﮔﻝ؟۰ﻝ?(State Management)                       ﻗ? ﻗ?
ﻗ? ﻗ? 3. ﻟ۰۴ﮒﺟﮔﭦﮒﭘ (Compensation Mechanism)                 ﻗ? ﻗ?
ﻗ? ﻗ? 4. ﮔﻠﮔ۱ﮒ۳ (Failure Recovery)                       ﻗ? ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
                            ﻗ?ﻛﭦﻛﭨﭘﻠ۸ﺎﮒ۷
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   Sagaﮔ۶ﻟ۰ﮔ­۴ﻠ۹۳                              ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗ? ﻗStep 1    ﻗ?ﻗStep 2    ﻗ?ﻗStep 3    ﻗ?ﻗStep 4    ﻗ?     ﻗ?
ﻗ? ﻗﮒﮒﭨﭦﻟ؟۱ﮒ? ﻗﻗﻗﮒﭨﻝﭨﻟﭖﻠ? ﻗﻗﻗﮔﻛﭦ۳ﮒﺙﮔ? ﻗﻗﻗﮔﺑﮔﺍﮔﻛﭨ? ﻗ?     ﻗ?
ﻗ? ﻗ?         ﻗ?ﻗ?         ﻗ?ﻗ?         ﻗ?ﻗ?         ﻗ?     ﻗ?
ﻗ? ﻗCompensateﻗ?ﻗCompensateﻗ?ﻗCompensateﻗ?ﻗCompensateﻗ?     ﻗ?
ﻗ? ﻗﮒﮔﭘﻟ؟۱ﮒ? ﻗ?ﻗﻟ۶۲ﮒﭨﻟﭖﻠ? ﻗ?ﻗﮒﮔﭘﻟ؟۱ﮒ? ﻗ?ﻗﮒﮔﭨﮔﻛﭨ? ﻗ?     ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
```

---

## 1. Sagaﮒﻟﺍﮒ۷ﮔ ﺕﮒﺟﻟ؟ﺝﻟ؟?

### 1.1 Sagaﻝﭘﮔﮔﭦ

```python
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal
import asyncio

class SagaStatus(Enum):
    """Sagaﻝﭘﮔ?""
    PENDING = 'pending'           # ﮒﺝﮔ۶ﻟ۰?
    RUNNING = 'running'           # ﮔ۶ﻟ۰ﻛﺕ?
    COMPLETED = 'completed'       # ﮒﺓﺎﮒ؟ﮔ?
    COMPENSATING = 'compensating' # ﻟ۰۴ﮒﺟﻛﺕ?
    COMPENSATED = 'compensated'   # ﮒﺓﺎﻟ۰۴ﮒ?
    FAILED = 'failed'             # ﮒ۳ﺎﻟﺑ۴

class StepStatus(Enum):
    """ﮔ­۴ﻠ۹۳ﻝﭘﮔ?""
    PENDING = 'pending'           # ﮒﺝﮔ۶ﻟ۰?
    RUNNING = 'running'           # ﮔ۶ﻟ۰ﻛﺕ?
    COMPLETED = 'completed'       # ﮒﺓﺎﮒ؟ﮔ?
    COMPENSATING = 'compensating' # ﻟ۰۴ﮒﺟﻛﺕ?
    COMPENSATED = 'compensated'   # ﮒﺓﺎﻟ۰۴ﮒ?
    FAILED = 'failed'             # ﮒ۳ﺎﻟﺑ۴

class SagaStep:
    """Sagaﮔ­۴ﻠ۹۳"""
    
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
        """ﮔ۶ﻟ۰ﮔ­۴ﻠ۹۳"""
        self.status = StepStatus.RUNNING
        self.started_at = datetime.now()
        
        try:
            # ﮔ۶ﻟ۰ﮔ­۴ﻠ۹۳ﺅﺙﮒﺕ۵ﻟﭘﮔﭘﮔ۶ﮒﭘ
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
            self.error = f"ﮔ­۴ﻠ۹۳ﮔ۶ﻟ۰ﻟﭘﮔﭘ: {self.timeout}ﻝ۶?
            raise Exception(self.error)
        except Exception as e:
            self.status = StepStatus.FAILED
            self.error = str(e)
            raise
    
    async def compensate(self, context: Dict[str, Any]) -> bool:
        """ﻟ۰۴ﮒﺟﮔ­۴ﻠ۹۳"""
        self.status = StepStatus.COMPENSATING
        
        try:
            # ﮔ۶ﻟ۰ﻟ۰۴ﮒﺟﺅﺙﮒﺕ۵ﻟﭘﮔﭘﮔ۶ﮒﭘ
            success = await asyncio.wait_for(
                self.compensate_func(context, self.result),
                timeout=self.timeout
            )
            
            self.status = StepStatus.COMPENSATED
            return success
        except Exception as e:
            self.status = StepStatus.FAILED
            self.error = f"ﻟ۰۴ﮒﺟﮒ۳ﺎﻟﺑ۴: {str(e)}"
            return False

class Saga:
    """Sagaﻛﭦﮒ۰"""
    
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
        """ﮔﺓﭨﮒ ﮔ­۴ﻠ۹۳"""
        self.steps.append(step)
    
    async def execute(self) -> bool:
        """ﮔ۶ﻟ۰Saga"""
        self.status = SagaStatus.RUNNING
        self.updated_at = datetime.now()
        
        try:
            # ﻠ۰ﭦﮒﭦﮔ۶ﻟ۰ﮔﮔﮔ­۴ﻠ۹?
            for i, step in enumerate(self.steps):
                self.current_step_index = i
                
                # ﮔ۶ﻟ۰ﮔ­۴ﻠ۹۳
                result = await step.execute(self.context)
                
                # ﮔﺑﮔﺍﻛﺕﻛﺕﮔ?
                self.context.update(result)
                self.updated_at = datetime.now()
            
            # ﮔﮔﮔ­۴ﻠ۹۳ﮔ۶ﻟ۰ﮔﮒ?
            self.status = SagaStatus.COMPLETED
            self.updated_at = datetime.now()
            return True
        
        except Exception as e:
            # ﮔ۶ﻟ۰ﮒ۳ﺎﻟﺑ۴ﺅﺙﮒﺙﮒ۶ﻟ۰۴ﮒ?
            print(f"Sagaﮔ۶ﻟ۰ﮒ۳ﺎﻟﺑ۴: {e}")
            await self.compensate()
            return False
    
    async def compensate(self) -> bool:
        """ﻟ۰۴ﮒﺟSaga"""
        self.status = SagaStatus.COMPENSATING
        self.updated_at = datetime.now()
        
        try:
            # ﻠﮒﭦﻟ۰۴ﮒﺟﮒﺓﺎﮒ؟ﮔﻝﮔ­۴ﻠ۹۳
            for i in range(self.current_step_index, -1, -1):
                step = self.steps[i]
                
                if step.status == StepStatus.COMPLETED:
                    # ﻟ۰۴ﮒﺟﮔ­۴ﻠ۹۳
                    success = await step.compensate(self.context)
                    
                    if not success:
                        print(f"ﮔ­۴ﻠ۹۳ﻟ۰۴ﮒﺟﮒ۳ﺎﻟﺑ۴: {step.step_name}")
            
            self.status = SagaStatus.COMPENSATED
            self.updated_at = datetime.now()
            return True
        
        except Exception as e:
            print(f"Sagaﻟ۰۴ﮒﺟﮒ۳ﺎﻟﺑ۴: {e}")
            self.status = SagaStatus.FAILED
            self.updated_at = datetime.now()
            return False
```

---

## 2. ﻟ؟۱ﮒSagaﻟ؟ﺝﻟ؟۰

### 2.1 ﻟ؟۱ﮒSagaﮔ­۴ﻠ۹۳

```python
class OrderSaga:
    """ﻟ؟۱ﮒSaga"""
    
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
        """ﮒﮒﭨﭦﻟ؟۱ﮒSaga"""
        saga = Saga(
            saga_id=f"SAGA_ORDER_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            saga_name="ﻟ؟۱ﮒﮔ۶ﻟ۰Saga"
        )
        
        # Step 1: ﮒﮒﭨﭦﻟ؟۱ﮒ
        step1 = SagaStep(
            step_id="create_order",
            step_name="ﮒﮒﭨﭦﻟ؟۱ﮒ",
            execute_func=self._create_order,
            compensate_func=self._cancel_order,
            timeout=10
        )
        
        # Step 2: ﮒﭨﻝﭨﻟﭖﻠ/ﮔﻛﭨ
        step2 = SagaStep(
            step_id="freeze_resource",
            step_name="ﮒﭨﻝﭨﻟﭖﮔﭦ",
            execute_func=self._freeze_resource,
            compensate_func=self._unfreeze_resource,
            timeout=10
        )
        
        # Step 3: ﮔﻛﭦ۳ﮒﺍﮒﺙﮔ?
        step3 = SagaStep(
            step_id="submit_to_engine",
            step_name="ﮔﻛﭦ۳ﮒﺙﮔ",
            execute_func=self._submit_to_engine,
            compensate_func=self._cancel_from_engine,
            timeout=30
        )
        
        # Step 4: ﮔﺑﮔﺍﮔﻛﭨ
        step4 = SagaStep(
            step_id="update_position",
            step_name="ﮔﺑﮔﺍﮔﻛﭨ",
            execute_func=self._update_position,
            compensate_func=self._rollback_position,
            timeout=10
        )
        
        # ﮔﺓﭨﮒ ﮔ­۴ﻠ۹۳
        saga.add_step(step1)
        saga.add_step(step2)
        saga.add_step(step3)
        saga.add_step(step4)
        
        # ﮒﮒ۶ﮒﻛﺕﻛﺕﮔ
        saga.context = {
            'order_data': order_data
        }
        
        return saga
    
    async def _create_order(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """ﮒﮒﭨﭦﻟ؟۱ﮒ"""
        order_data = context['order_data']
        
        # ﮒﮒﭨﭦﻟ؟۱ﮒ
        order = await self.order_service.create_order(order_data)
        
        return {
            'order_id': order['id'],
            'order_code': order['order_code'],
            'order': order
        }
    
    async def _cancel_order(self, context: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """ﮒﮔﭘﻟ؟۱ﮒ"""
        order_id = result['order_id']
        
        # ﮒﮔﭘﻟ؟۱ﮒ
        success = await self.order_service.cancel_order(order_id, reason="Sagaﻟ۰۴ﮒﺟ")
        
        return success
    
    async def _freeze_resource(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """ﮒﭨﻝﭨﻟﭖﮔﭦ"""
        order = context['order']
        
        if order['direction'] == 'buy':
            # ﻛﺗﺍﮒ۴ﺅﺙﮒﭨﻝﭨﻟﭖﻠ?
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
            # ﮒﮒﭦﺅﺙﮒﭨﻝﭨﮔﻛﭨ?
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
        """ﻟ۶۲ﮒﭨﻟﭖﮔﭦ"""
        order = context['order']
        
        if result['frozen_type'] == 'cash':
            # ﻟ۶۲ﮒﭨﻟﭖﻠ
            success = await self.account_service.unfreeze_cash(
                order['account_id'],
                result['frozen_amount']
            )
        else:
            # ﻟ۶۲ﮒﭨﮔﻛﭨ
            success = await self.position_service.unfreeze_position(
                order['account_id'],
                order['stock_code'],
                result['frozen_quantity']
            )
        
        return success
    
    async def _submit_to_engine(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """ﮔﻛﭦ۳ﮒﺍﮒﺙﮔ?""
        order = context['order']
        
        # ﻟﺓﮒﮒﺙﮔ
        engine = self.engine_manager.get_engine(order['engine_id'])
        
        if not engine:
            raise Exception(f"ﮒﺙﮔﻛﺕﮒ­ﮒ? {order['engine_id']}")
        
        # ﮔﻛﭦ۳ﻟ؟۱ﮒﮒﺍﮒﺙﮔ?
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
            raise Exception(f"ﮒﺙﮔﮔﻛﭦ۳ﮒ۳ﺎﻟﺑ۴: {result.get('error')}")
        
        return {
            'broker_order_id': result['order_id'],
            'engine_result': result
        }
    
    async def _cancel_from_engine(self, context: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """ﻛﭨﮒﺙﮔﮒﮔﭘﻟ؟۱ﮒ?""
        order = context['order']
        broker_order_id = result['broker_order_id']
        
        # ﻟﺓﮒﮒﺙﮔ
        engine = self.engine_manager.get_engine(order['engine_id'])
        
        if not engine:
            return False
        
        # ﮒﮔﭘﻟ؟۱ﮒ
        success = await engine.cancel_order(broker_order_id)
        
        return success
    
    async def _update_position(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """ﮔﺑﮔﺍﮔﻛﭨ"""
        order = context['order']
        
        # ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒﮔﻛﭦ۳ﮔﮒﭖ
        order_status = await self.order_service.query_order(order['id'])
        
        if order_status['status'] != 'filled':
            raise Exception("ﻟ؟۱ﮒﮔ۹ﮔﻛﭦ?)
        
        # ﮔﺑﮔﺍﮔﻛﭨ
        if order['direction'] == 'buy':
            # ﻛﺗﺍﮒ۴ﺅﺙﮒ۱ﮒ ﮔﻛﭨ?
            position = await self.position_service.increase_position(
                account_id=order['account_id'],
                stock_code=order['stock_code'],
                quantity=order_status['filled_quantity'],
                price=Decimal(str(order_status['filled_price'])),
                trade_id=order_status.get('trade_id')
            )
        else:
            # ﮒﮒﭦﺅﺙﮒﮒﺍﮔﻛﭨ?
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
        """ﮒﮔﭨﮔﻛﭨ"""
        order = context['order']
        position = result['position']
        
        # ﮒﮔﭨﮔﻛﭨ
        if order['direction'] == 'buy':
            # ﻛﺗﺍﮒ۴ﮒﮔﭨﺅﺙﮒﮒﺍﮔﻛﭨ?
            success = await self.position_service.decrease_position(
                account_id=order['account_id'],
                stock_code=order['stock_code'],
                quantity=position['quantity'],
                price=position['avg_cost']
            )
        else:
            # ﮒﮒﭦﮒﮔﭨﺅﺙﮒ۱ﮒ ﮔﻛﭨ?
            success = await self.position_service.increase_position(
                account_id=order['account_id'],
                stock_code=order['stock_code'],
                quantity=position['quantity'],
                price=position['avg_cost']
            )
        
        return success
```

---

## 3. Sagaﮒﻟﺍﮒ۷ﮔﮒ?

### 3.1 ﮒﻟﺍﮒ۷ﮒ؟ﻝ?

```python
from typing import Dict, Any, Optional
import uuid
import json

class SagaCoordinator:
    """Sagaﮒﻟﺍﮒ?""
    
    def __init__(self, saga_repository):
        self.saga_repository = saga_repository
        self.active_sagas: Dict[str, Saga] = {}
    
    async def start_saga(self, saga: Saga) -> str:
        """ﮒﺁﮒ۷Saga"""
        # ﻛﺟﮒ­Saga
        await self.saga_repository.save_saga(saga)
        
        # ﮔﺓﭨﮒ ﮒﺍﮔﺑﭨﻟﺓﮒﻟ۰?
        self.active_sagas[saga.saga_id] = saga
        
        # ﮒﺙﮔ­۴ﮔ۶ﻟ۰Saga
        asyncio.create_task(self._execute_saga(saga))
        
        return saga.saga_id
    
    async def _execute_saga(self, saga: Saga) -> None:
        """ﮔ۶ﻟ۰Saga"""
        try:
            # ﮔ۶ﻟ۰Saga
            success = await saga.execute()
            
            # ﮔﺑﮔﺍSagaﻝﭘﮔ?
            await self.saga_repository.update_saga_status(
                saga.saga_id,
                saga.status,
                saga.context
            )
            
            # ﻛﭨﮔﺑﭨﻟﺓﮒﻟ۰۷ﻝ۶ﭨﻠ?
            if saga.saga_id in self.active_sagas:
                del self.active_sagas[saga.saga_id]
        
        except Exception as e:
            print(f"Sagaﮔ۶ﻟ۰ﮒﺙﮒﺕﺕ: {e}")
            
            # ﮔﺑﮔﺍSagaﻝﭘﮔﻛﺕﭦﮒ۳ﺎﻟﺑ۴
            await self.saga_repository.update_saga_status(
                saga.saga_id,
                SagaStatus.FAILED,
                saga.context
            )
            
            # ﻛﭨﮔﺑﭨﻟﺓﮒﻟ۰۷ﻝ۶ﭨﻠ?
            if saga.saga_id in self.active_sagas:
                del self.active_sagas[saga.saga_id]
    
    async def get_saga_status(self, saga_id: str) -> Optional[Dict[str, Any]]:
        """ﻟﺓﮒSagaﻝﭘﮔ?""
        # ﮒﮔ۴ﮔﺑﭨﻟﺓﮒﻟ۰۷
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
        
        # ﮔ۴ﮔﺍﮔ؟ﮒﭦ
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
        """ﮔﮒ۷ﻟ۰۴ﮒﺟSaga"""
        saga = await self.saga_repository.find_saga(saga_id)
        
        if not saga:
            return False
        
        # ﻠﮒﭨﭦSagaﮒﺁﺗﻟﺎ۰
        saga_obj = Saga(saga['saga_id'], saga['saga_name'])
        saga_obj.status = SagaStatus(saga['status'])
        saga_obj.context = json.loads(saga['context'])
        
        # ﮔ۶ﻟ۰ﻟ۰۴ﮒﺟ
        success = await saga_obj.compensate()
        
        # ﮔﺑﮔﺍﻝﭘﮔ?
        await self.saga_repository.update_saga_status(
            saga_id,
            saga_obj.status,
            saga_obj.context
        )
        
        return success
```

---

## 4. Sagaﮔﻛﺗﮒﻟ؟ﺝﻟ؟?

### 4.1 Sagaﻟ۰۷ﻝﭨﮔ?

```sql
-- Sagaﻛﭦﮒ۰ﻟ۰?
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

-- Sagaﮔ­۴ﻠ۹۳ﻟ۰?
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

-- ﻝﺑ۱ﮒﺙ
CREATE INDEX idx_saga_transactions_status ON saga_transactions(status);
CREATE INDEX idx_saga_transactions_created_at ON saga_transactions(created_at);
CREATE INDEX idx_saga_steps_saga_id ON saga_steps(saga_id);
CREATE INDEX idx_saga_steps_status ON saga_steps(status);
```

---

## 5. ﮔﻠﮔ۱ﮒ۳ﮔﭦﮒﭘ

### 5.1 ﮔﻠﮔ۲ﮔﭖ?

```python
class SagaRecoveryService:
    """Sagaﮔﻠﮔ۱ﮒ۳ﮔﮒ۰"""
    
    def __init__(self, saga_coordinator: SagaCoordinator, saga_repository):
        self.coordinator = saga_coordinator
        self.repository = saga_repository
    
    async def detect_failed_sagas(self) -> List[Dict[str, Any]]:
        """ﮔ۲ﮔﭖﮒ۳ﺎﻟﺑ۴ﻝSaga"""
        # ﮔ۴ﻟﺁ۱ﻟﭘﮔﭘﻝSaga
        timeout_sagas = await self.repository.find_timeout_sagas(timeout_minutes=30)
        
        # ﮔ۴ﻟﺁ۱ﮒﺙﮒﺕﺕﻝﭘﮔﻝSaga
        failed_sagas = await self.repository.find_sagas_by_status(SagaStatus.FAILED)
        
        return timeout_sagas + failed_sagas
    
    async def recover_saga(self, saga_id: str) -> bool:
        """ﮔ۱ﮒ۳Saga"""
        saga = await self.repository.find_saga(saga_id)
        
        if not saga:
            return False
        
        # ﮔ ﺗﮔ؟ﻝﭘﮔﮒﺏﮒ؟ﮔ۱ﮒ۳ﻝ­ﻝ?
        if saga['status'] == SagaStatus.RUNNING.value:
            # ﮔ۶ﻟ۰ﻛﺕ­ﻝSagaﺅﺙﻠﮔﺍﮔ۶ﻟ۰?
            return await self._retry_saga(saga)
        elif saga['status'] == SagaStatus.COMPENSATING.value:
            # ﻟ۰۴ﮒﺟﻛﺕ­ﻝSagaﺅﺙﻝﭨ۶ﻝﭨ­ﻟ۰۴ﮒ?
            return await self._continue_compensate(saga)
        elif saga['status'] == SagaStatus.FAILED.value:
            # ﮒ۳ﺎﻟﺑ۴ﻝSagaﺅﺙﮔﮒ۷ﮒ۳ﻝ?
            return await self._manual_recovery(saga)
        
        return False
    
    async def _retry_saga(self, saga: Dict[str, Any]) -> bool:
        """ﻠﻟﺁSaga"""
        # TODO: ﮒ؟ﻝﺍﻠﻟﺁﻠﭨﻟﺝ
        return False
    
    async def _continue_compensate(self, saga: Dict[str, Any]) -> bool:
        """ﻝﭨ۶ﻝﭨ­ﻟ۰۴ﮒﺟ"""
        # TODO: ﮒ؟ﻝﺍﻝﭨ۶ﻝﭨ­ﻟ۰۴ﮒﺟﻠﭨﻟﺝ
        return False
    
    async def _manual_recovery(self, saga: Dict[str, Any]) -> bool:
        """ﮔﮒ۷ﮔ۱ﮒ۳"""
        # TODO: ﮒ؟ﻝﺍﮔﮒ۷ﮔ۱ﮒ۳ﻠﭨﻟﺝ
        return False
```

---

## 6. ﮔ۶ﻟﺛﻛﺕﻝﮔ?

### 6.1 ﮔ۶ﻟﺛﮔﮔ 

| ﮔﮔ  | ﻝ؟ﮔ ﮒ?| ﮒ۳ﮔﺏ۷ |
|------|--------|------|
| **Sagaﮔ۶ﻟ۰ﮔﭘﻠﺑ** | < 5ﻝ۶?| ﮒﮒ،ﮔﮔﮔ­۴ﻠ۹?|
| **ﻟ۰۴ﮒﺟﮔﭘﻠﺑ** | < 10ﻝ۶?| ﮒﮒ،ﮔﮔﻟ۰۴ﮒﺟﮔ­۴ﻠ۹?|
| **ﮒﺗﭘﮒSagaﮔ?* | 100 | ﮒﮔﭘﮔ۶ﻟ۰ﻝSagaﮔﺍﻠ |
| **ﮔﮒﻝ?* | ﻗ?99% | Sagaﮔﮒﮒ؟ﮔﻝ?|

### 6.2 ﻝﮔ۶ﮔﮔ 

```python
class SagaMonitor:
    """Sagaﻝﮔ۶"""
    
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
        """ﻟ؟ﺍﮒﺛSagaﮒ؟ﮔ"""
        self.metrics['total_sagas'] += 1
        
        if saga.status == SagaStatus.COMPLETED:
            self.metrics['successful_sagas'] += 1
        elif saga.status == SagaStatus.COMPENSATED:
            self.metrics['compensated_sagas'] += 1
        else:
            self.metrics['failed_sagas'] += 1
        
        # ﮔﺑﮔﺍﮒﺗﺏﮒﮔ۶ﻟ۰ﮔﭘﻠﺑ
        self.metrics['avg_execution_time'] = (
            (self.metrics['avg_execution_time'] * (self.metrics['total_sagas'] - 1) + execution_time)
            / self.metrics['total_sagas']
        )
    
    async def get_metrics(self) -> Dict[str, Any]:
        """ﻟﺓﮒﻝﮔ۶ﮔﮔ """
        return {
            **self.metrics,
            'success_rate': (
                self.metrics['successful_sagas'] / self.metrics['total_sagas']
                if self.metrics['total_sagas'] > 0 else 0
            )
        }
```

---

**ﻝﮔ؛**: 1.0.0 | **ﮔﺑﮔﺍﮔ۴ﮔ**: 2026-04-02 | **ﻝﭘﮔ?*: ﻗ?ﮒﺓﺎﮒ؟ﮔ? 
**ﻛﺕﻛﺕﮔ­?*: P0-6 ﻟﺑ۵ﮔﺓﻝ؟۰ﻝﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰