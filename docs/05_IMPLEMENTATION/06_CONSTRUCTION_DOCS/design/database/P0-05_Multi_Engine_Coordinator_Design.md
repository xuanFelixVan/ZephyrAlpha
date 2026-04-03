---
module_id: MULTI_ENGINE_COORDINATOR_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席蓝图架构师
standard_type: 专业量化机构多引擎协同器标准
applicable_scope: 多引擎事务协调
compliance_level: 专业机构标准
parent_document: P0-01_Database_Design_Document.md
implementation_status: 进行中
---

# 多引擎协同器详细设计（专业量化机构标准）

> 清风量化系统 v5.0 - 专业量化机构标准多引擎协同器设计
> **设计模式**: Saga分布式事务模式 + 事件驱动架构
> **核心职责**: 多引擎事务协调、数据一致性保障、故障恢复

## 📋 协同器概述

### Saga事务架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Saga协调器 (Saga Coordinator)             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. 事务编排 (Transaction Orchestration)              │  │
│  │  2. 状态管理 (State Management)                       │  │
│  │  3. 补偿机制 (Compensation Mechanism)                 │  │
│  │  4. 故障恢复 (Failure Recovery)                       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓ 事件驱动
┌─────────────────────────────────────────────────────────────┐
│                    Saga执行步骤                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │Step 1    │ │Step 2    │ │Step 3    │ │Step 4    │      │
│  │创建订单  │→│冻结资金  │→│提交引擎  │→│更新持仓  │      │
│  │          │ │          │ │          │ │          │      │
│  │Compensate│ │Compensate│ │Compensate│ │Compensate│      │
│  │取消订单  │ │解冻资金  │ │取消订单  │ │回滚持仓  │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Saga协调器核心设计

### 1.1 Saga状态机

```python
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal
import asyncio

class SagaStatus(Enum):
    """Saga状态"""
    PENDING = 'pending'           # 待执行
    RUNNING = 'running'           # 执行中
    COMPLETED = 'completed'       # 已完成
    COMPENSATING = 'compensating' # 补偿中
    COMPENSATED = 'compensated'   # 已补偿
    FAILED = 'failed'             # 失败

class StepStatus(Enum):
    """步骤状态"""
    PENDING = 'pending'           # 待执行
    RUNNING = 'running'           # 执行中
    COMPLETED = 'completed'       # 已完成
    COMPENSATING = 'compensating' # 补偿中
    COMPENSATED = 'compensated'   # 已补偿
    FAILED = 'failed'             # 失败

class SagaStep:
    """Saga步骤"""
    
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
        """执行步骤"""
        self.status = StepStatus.RUNNING
        self.started_at = datetime.now()
        
        try:
            # 执行步骤，带超时控制
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
            self.error = f"步骤执行超时: {self.timeout}秒"
            raise Exception(self.error)
        except Exception as e:
            self.status = StepStatus.FAILED
            self.error = str(e)
            raise
    
    async def compensate(self, context: Dict[str, Any]) -> bool:
        """补偿步骤"""
        self.status = StepStatus.COMPENSATING
        
        try:
            # 执行补偿，带超时控制
            success = await asyncio.wait_for(
                self.compensate_func(context, self.result),
                timeout=self.timeout
            )
            
            self.status = StepStatus.COMPENSATED
            return success
        except Exception as e:
            self.status = StepStatus.FAILED
            self.error = f"补偿失败: {str(e)}"
            return False

class Saga:
    """Saga事务"""
    
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
        """添加步骤"""
        self.steps.append(step)
    
    async def execute(self) -> bool:
        """执行Saga"""
        self.status = SagaStatus.RUNNING
        self.updated_at = datetime.now()
        
        try:
            # 顺序执行所有步骤
            for i, step in enumerate(self.steps):
                self.current_step_index = i
                
                # 执行步骤
                result = await step.execute(self.context)
                
                # 更新上下文
                self.context.update(result)
                self.updated_at = datetime.now()
            
            # 所有步骤执行成功
            self.status = SagaStatus.COMPLETED
            self.updated_at = datetime.now()
            return True
        
        except Exception as e:
            # 执行失败，开始补偿
            print(f"Saga执行失败: {e}")
            await self.compensate()
            return False
    
    async def compensate(self) -> bool:
        """补偿Saga"""
        self.status = SagaStatus.COMPENSATING
        self.updated_at = datetime.now()
        
        try:
            # 逆序补偿已完成的步骤
            for i in range(self.current_step_index, -1, -1):
                step = self.steps[i]
                
                if step.status == StepStatus.COMPLETED:
                    # 补偿步骤
                    success = await step.compensate(self.context)
                    
                    if not success:
                        print(f"步骤补偿失败: {step.step_name}")
            
            self.status = SagaStatus.COMPENSATED
            self.updated_at = datetime.now()
            return True
        
        except Exception as e:
            print(f"Saga补偿失败: {e}")
            self.status = SagaStatus.FAILED
            self.updated_at = datetime.now()
            return False
```

---

## 2. 订单Saga设计

### 2.1 订单Saga步骤

```python
class OrderSaga:
    """订单Saga"""
    
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
        """创建订单Saga"""
        saga = Saga(
            saga_id=f"SAGA_ORDER_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            saga_name="订单执行Saga"
        )
        
        # Step 1: 创建订单
        step1 = SagaStep(
            step_id="create_order",
            step_name="创建订单",
            execute_func=self._create_order,
            compensate_func=self._cancel_order,
            timeout=10
        )
        
        # Step 2: 冻结资金/持仓
        step2 = SagaStep(
            step_id="freeze_resource",
            step_name="冻结资源",
            execute_func=self._freeze_resource,
            compensate_func=self._unfreeze_resource,
            timeout=10
        )
        
        # Step 3: 提交到引擎
        step3 = SagaStep(
            step_id="submit_to_engine",
            step_name="提交引擎",
            execute_func=self._submit_to_engine,
            compensate_func=self._cancel_from_engine,
            timeout=30
        )
        
        # Step 4: 更新持仓
        step4 = SagaStep(
            step_id="update_position",
            step_name="更新持仓",
            execute_func=self._update_position,
            compensate_func=self._rollback_position,
            timeout=10
        )
        
        # 添加步骤
        saga.add_step(step1)
        saga.add_step(step2)
        saga.add_step(step3)
        saga.add_step(step4)
        
        # 初始化上下文
        saga.context = {
            'order_data': order_data
        }
        
        return saga
    
    async def _create_order(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """创建订单"""
        order_data = context['order_data']
        
        # 创建订单
        order = await self.order_service.create_order(order_data)
        
        return {
            'order_id': order['id'],
            'order_code': order['order_code'],
            'order': order
        }
    
    async def _cancel_order(self, context: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """取消订单"""
        order_id = result['order_id']
        
        # 取消订单
        success = await self.order_service.cancel_order(order_id, reason="Saga补偿")
        
        return success
    
    async def _freeze_resource(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """冻结资源"""
        order = context['order']
        
        if order['direction'] == 'buy':
            # 买入：冻结资金
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
            # 卖出：冻结持仓
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
        """解冻资源"""
        order = context['order']
        
        if result['frozen_type'] == 'cash':
            # 解冻资金
            success = await self.account_service.unfreeze_cash(
                order['account_id'],
                result['frozen_amount']
            )
        else:
            # 解冻持仓
            success = await self.position_service.unfreeze_position(
                order['account_id'],
                order['stock_code'],
                result['frozen_quantity']
            )
        
        return success
    
    async def _submit_to_engine(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """提交到引擎"""
        order = context['order']
        
        # 获取引擎
        engine = self.engine_manager.get_engine(order['engine_id'])
        
        if not engine:
            raise Exception(f"引擎不存在: {order['engine_id']}")
        
        # 提交订单到引擎
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
            raise Exception(f"引擎提交失败: {result.get('error')}")
        
        return {
            'broker_order_id': result['order_id'],
            'engine_result': result
        }
    
    async def _cancel_from_engine(self, context: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """从引擎取消订单"""
        order = context['order']
        broker_order_id = result['broker_order_id']
        
        # 获取引擎
        engine = self.engine_manager.get_engine(order['engine_id'])
        
        if not engine:
            return False
        
        # 取消订单
        success = await engine.cancel_order(broker_order_id)
        
        return success
    
    async def _update_position(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """更新持仓"""
        order = context['order']
        
        # 查询订单成交情况
        order_status = await self.order_service.query_order(order['id'])
        
        if order_status['status'] != 'filled':
            raise Exception("订单未成交")
        
        # 更新持仓
        if order['direction'] == 'buy':
            # 买入：增加持仓
            position = await self.position_service.increase_position(
                account_id=order['account_id'],
                stock_code=order['stock_code'],
                quantity=order_status['filled_quantity'],
                price=Decimal(str(order_status['filled_price'])),
                trade_id=order_status.get('trade_id')
            )
        else:
            # 卖出：减少持仓
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
        """回滚持仓"""
        order = context['order']
        position = result['position']
        
        # 回滚持仓
        if order['direction'] == 'buy':
            # 买入回滚：减少持仓
            success = await self.position_service.decrease_position(
                account_id=order['account_id'],
                stock_code=order['stock_code'],
                quantity=position['quantity'],
                price=position['avg_cost']
            )
        else:
            # 卖出回滚：增加持仓
            success = await self.position_service.increase_position(
                account_id=order['account_id'],
                stock_code=order['stock_code'],
                quantity=position['quantity'],
                price=position['avg_cost']
            )
        
        return success
```

---

## 3. Saga协调器服务

### 3.1 协调器实现

```python
from typing import Dict, Any, Optional
import uuid
import json

class SagaCoordinator:
    """Saga协调器"""
    
    def __init__(self, saga_repository):
        self.saga_repository = saga_repository
        self.active_sagas: Dict[str, Saga] = {}
    
    async def start_saga(self, saga: Saga) -> str:
        """启动Saga"""
        # 保存Saga
        await self.saga_repository.save_saga(saga)
        
        # 添加到活跃列表
        self.active_sagas[saga.saga_id] = saga
        
        # 异步执行Saga
        asyncio.create_task(self._execute_saga(saga))
        
        return saga.saga_id
    
    async def _execute_saga(self, saga: Saga) -> None:
        """执行Saga"""
        try:
            # 执行Saga
            success = await saga.execute()
            
            # 更新Saga状态
            await self.saga_repository.update_saga_status(
                saga.saga_id,
                saga.status,
                saga.context
            )
            
            # 从活跃列表移除
            if saga.saga_id in self.active_sagas:
                del self.active_sagas[saga.saga_id]
        
        except Exception as e:
            print(f"Saga执行异常: {e}")
            
            # 更新Saga状态为失败
            await self.saga_repository.update_saga_status(
                saga.saga_id,
                SagaStatus.FAILED,
                saga.context
            )
            
            # 从活跃列表移除
            if saga.saga_id in self.active_sagas:
                del self.active_sagas[saga.saga_id]
    
    async def get_saga_status(self, saga_id: str) -> Optional[Dict[str, Any]]:
        """获取Saga状态"""
        # 先查活跃列表
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
        
        # 查数据库
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
        """手动补偿Saga"""
        saga = await self.saga_repository.find_saga(saga_id)
        
        if not saga:
            return False
        
        # 重建Saga对象
        saga_obj = Saga(saga['saga_id'], saga['saga_name'])
        saga_obj.status = SagaStatus(saga['status'])
        saga_obj.context = json.loads(saga['context'])
        
        # 执行补偿
        success = await saga_obj.compensate()
        
        # 更新状态
        await self.saga_repository.update_saga_status(
            saga_id,
            saga_obj.status,
            saga_obj.context
        )
        
        return success
```

---

## 4. Saga持久化设计

### 4.1 Saga表结构

```sql
-- Saga事务表
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

-- Saga步骤表
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

-- 索引
CREATE INDEX idx_saga_transactions_status ON saga_transactions(status);
CREATE INDEX idx_saga_transactions_created_at ON saga_transactions(created_at);
CREATE INDEX idx_saga_steps_saga_id ON saga_steps(saga_id);
CREATE INDEX idx_saga_steps_status ON saga_steps(status);
```

---

## 5. 故障恢复机制

### 5.1 故障检测

```python
class SagaRecoveryService:
    """Saga故障恢复服务"""
    
    def __init__(self, saga_coordinator: SagaCoordinator, saga_repository):
        self.coordinator = saga_coordinator
        self.repository = saga_repository
    
    async def detect_failed_sagas(self) -> List[Dict[str, Any]]:
        """检测失败的Saga"""
        # 查询超时的Saga
        timeout_sagas = await self.repository.find_timeout_sagas(timeout_minutes=30)
        
        # 查询异常状态的Saga
        failed_sagas = await self.repository.find_sagas_by_status(SagaStatus.FAILED)
        
        return timeout_sagas + failed_sagas
    
    async def recover_saga(self, saga_id: str) -> bool:
        """恢复Saga"""
        saga = await self.repository.find_saga(saga_id)
        
        if not saga:
            return False
        
        # 根据状态决定恢复策略
        if saga['status'] == SagaStatus.RUNNING.value:
            # 执行中的Saga：重新执行
            return await self._retry_saga(saga)
        elif saga['status'] == SagaStatus.COMPENSATING.value:
            # 补偿中的Saga：继续补偿
            return await self._continue_compensate(saga)
        elif saga['status'] == SagaStatus.FAILED.value:
            # 失败的Saga：手动处理
            return await self._manual_recovery(saga)
        
        return False
    
    async def _retry_saga(self, saga: Dict[str, Any]) -> bool:
        """重试Saga"""
        # TODO: 实现重试逻辑
        return False
    
    async def _continue_compensate(self, saga: Dict[str, Any]) -> bool:
        """继续补偿"""
        # TODO: 实现继续补偿逻辑
        return False
    
    async def _manual_recovery(self, saga: Dict[str, Any]) -> bool:
        """手动恢复"""
        # TODO: 实现手动恢复逻辑
        return False
```

---

## 6. 性能与监控

### 6.1 性能指标

| 指标 | 目标值 | 备注 |
|------|--------|------|
| **Saga执行时间** | < 5秒 | 包含所有步骤 |
| **补偿时间** | < 10秒 | 包含所有补偿步骤 |
| **并发Saga数** | 100 | 同时执行的Saga数量 |
| **成功率** | ≥ 99% | Saga成功完成率 |

### 6.2 监控指标

```python
class SagaMonitor:
    """Saga监控"""
    
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
        """记录Saga完成"""
        self.metrics['total_sagas'] += 1
        
        if saga.status == SagaStatus.COMPLETED:
            self.metrics['successful_sagas'] += 1
        elif saga.status == SagaStatus.COMPENSATED:
            self.metrics['compensated_sagas'] += 1
        else:
            self.metrics['failed_sagas'] += 1
        
        # 更新平均执行时间
        self.metrics['avg_execution_time'] = (
            (self.metrics['avg_execution_time'] * (self.metrics['total_sagas'] - 1) + execution_time)
            / self.metrics['total_sagas']
        )
    
    async def get_metrics(self) -> Dict[str, Any]:
        """获取监控指标"""
        return {
            **self.metrics,
            'success_rate': (
                self.metrics['successful_sagas'] / self.metrics['total_sagas']
                if self.metrics['total_sagas'] > 0 else 0
            )
        }
```

---

**版本**: 1.0.0 | **更新日期**: 2026-04-02 | **状态**: ✅ 已完成  
**下一步**: P0-6 账户管理详细设计