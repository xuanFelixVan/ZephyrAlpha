---
module_id: IMPL_DOC_003-01
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席蓝图架构师
standard_type: 专业量化机构实施标准
applicable_scope: Saga模式流程图与状态机
compliance_level: 专业机构标准
parent_document: ../INDEX.md
implementation_status: 进行中
---

# Saga模式实现流程图

> 多引擎数据一致性Saga模式的完整状态机与流程图
>
> **核心状态**: 6个主状态，12个状态转换
> **流程图类型**: Mermaid状态图 + 序列图 + 活动图
> **设计目标**: 清晰展示Saga模式完整生命周期

**版本**: v1.0
**更新**: 2026-04-02
**Layer**: Layer 4 (执行层)
**优先级**: P1 - 架构理解核心

---

## 1. 整体状态机图

### 1.1 Mermaid状态图

```mermaid
stateDiagram-v2
    [*] --> Pending : 创建事务
    
    state Prechecking {
        [*] --> CheckingResources : 检查资源
        CheckingResources --> CheckingConstraints : 资源充足
        CheckingConstraints --> PrecheckPassed : 约束满足
        CheckingResources --> PrecheckFailed : 资源不足
        CheckingConstraints --> PrecheckFailed : 约束违反
    }
    
    Pending --> Prechecking : 开始预检查
    Prechecking --> Executing : 预检查通过
    Prechecking --> Failed : 预检查失败
    
    state Executing {
        [*] --> ExecutingParticipant1 : 执行参与方1
        ExecutingParticipant1 --> ExecutingParticipant2 : 参与方1成功
        ExecutingParticipant2 --> ExecutingParticipantN : 参与方2成功
        ExecutingParticipantN --> AllExecuted : 所有参与方成功
        ExecutingParticipant1 --> Compensating : 参与方1失败
        ExecutingParticipant2 --> Compensating : 参与方2失败
        ExecutingParticipantN --> Compensating : 参与方N失败
    }
    
    Executing --> Completing : 所有参与方执行成功
    Executing --> Compensating : 任何参与方失败
    
    state Compensating {
        [*] --> CompensatingParticipantN : 补偿参与方N
        CompensatingParticipantN --> CompensatingParticipantN1 : 补偿成功
        CompensatingParticipantN1 --> CompensatingParticipant1 : 补偿成功
        CompensatingParticipant1 --> AllCompensated : 所有补偿成功
        CompensatingParticipantN --> CompensationFailed : 补偿失败
        CompensatingParticipantN1 --> CompensationFailed : 补偿失败
        CompensatingParticipant1 --> CompensationFailed : 补偿失败
    }
    
    Completing --> Completed : 确认完成
    Compensating --> Failed : 补偿完成
    Compensating --> CompensationFailed : 补偿失败
    
    Completed --> [*] : 事务结束
    Failed --> [*] : 事务结束
    CompensationFailed --> [*] : 事务结束（需人工干预）
```

### 1.2 状态说明表

| 状态 | 描述 | 进入条件 | 退出条件 |
|------|------|----------|----------|
| **Pending** | 事务已创建，等待执行 | 协调器创建新事务 | 开始预检查 |
| **Prechecking** | 预检查阶段，验证资源与约束 | 从Pending状态开始预检查 | 预检查通过或失败 |
| **Executing** | 执行阶段，顺序执行各参与方 | 预检查通过 | 所有参与方成功或任何失败 |
| **Completing** | 完成阶段，确认事务完成 | 所有参与方执行成功 | 确认完成或确认失败 |
| **Compensating** | 补偿阶段，回滚已执行操作 | 任何参与方执行失败 | 所有补偿完成或补偿失败 |
| **Completed** | 事务成功完成 | 完成阶段确认成功 | 事务结束 |
| **Failed** | 事务失败（预检查失败或补偿完成） | 预检查失败或补偿完成 | 事务结束 |
| **CompensationFailed** | 补偿失败（需人工干预） | 补偿操作失败 | 事务结束（需人工干预） |

---

## 2. 正常执行序列图

### 2.1 Mermaid序列图（成功场景）

```mermaid
sequenceDiagram
    participant C as 协调器
    participant P1 as 参与方1 (vn.py)
    participant P2 as 参与方2 (RQAlpha)
    participant P3 as 参与方3 (Backtrader)
    participant DB as PostgreSQL
    participant Redis as Redis Streams

    Note over C: 1. 事务启动
    C->>DB: 创建事务记录 (tx_id=tx_001)
    DB-->>C: 返回事务ID
    
    Note over C: 2. 预检查阶段
    C->>P1: 预检查请求 (资源、约束)
    P1-->>C: 预检查通过
    C->>P2: 预检查请求
    P2-->>C: 预检查通过
    C->>P3: 预检查请求
    P3-->>C: 预检查通过
    
    Note over C: 3. 执行阶段
    C->>Redis: 发布事务开始事件
    Redis-->>C: 确认
    
    C->>P1: 执行本地事务 (命令1)
    P1->>DB: 记录本地事务开始
    P1-->>C: 执行成功
    C->>Redis: 发布参与方1执行事件
    
    C->>P2: 执行本地事务 (命令2)
    P2->>DB: 记录本地事务开始
    P2-->>C: 执行成功
    C->>Redis: 发布参与方2执行事件
    
    C->>P3: 执行本地事务 (命令3)
    P3->>DB: 记录本地事务开始
    P3-->>C: 执行成功
    C->>Redis: 发布参与方3执行事件
    
    Note over C: 4. 完成阶段
    C->>DB: 更新事务状态为completing
    C->>Redis: 发布所有参与方成功事件
    C->>DB: 更新事务状态为completed
    C->>Redis: 发布事务完成事件
    
    Note over C: 5. 完成通知
    Redis-->>P1: 事务完成通知
    Redis-->>P2: 事务完成通知
    Redis-->>P3: 事务完成通知
```

### 2.2 序列步骤说明

| 步骤 | 参与者 | 动作 | 数据 | 结果 |
|------|--------|------|------|------|
| **1.1** | 协调器 → PostgreSQL | 创建事务记录 | tx_id, transaction_type, initiator | 事务ID |
| **1.2** | PostgreSQL → 协调器 | 返回事务ID | tx_id | 事务创建成功 |
| **2.1** | 协调器 → 参与方1 | 预检查请求 | tx_id, 检查项 | 预检查结果 |
| **2.2** | 参与方1 → 协调器 | 预检查响应 | 通过/失败, 原因 | 资源验证 |
| **3.1** | 协调器 → Redis | 发布事务开始事件 | event_type, tx_id, 参与方列表 | 事件发布成功 |
| **3.2** | 协调器 → 参与方1 | 执行本地事务 | tx_id, 命令类型, 命令数据 | 执行结果 |
| **3.3** | 参与方1 → PostgreSQL | 记录本地事务 | tx_id, 参与方ID, 命令数据 | 持久化成功 |
| **3.4** | 参与方1 → 协调器 | 执行成功响应 | tx_id, 结果数据 | 本地事务完成 |
| **4.1** | 协调器 → PostgreSQL | 更新事务状态 | tx_id, status=completing | 状态更新 |
| **4.2** | 协调器 → Redis | 发布成功事件 | event_type, tx_id, 参与方列表 | 事件发布 |
| **4.3** | 协调器 → PostgreSQL | 最终状态更新 | tx_id, status=completed | 事务完成 |
| **5.1** | Redis → 所有参与方 | 事务完成通知 | event_type, tx_id | 参与方清理本地状态 |

---

## 3. 补偿执行序列图

### 3.1 Mermaid序列图（失败场景）

```mermaid
sequenceDiagram
    participant C as 协调器
    participant P1 as 参与方1 (vn.py)
    participant P2 as 参与方2 (RQAlpha)
    participant P3 as 参与方3 (Backtrader)
    participant DB as PostgreSQL
    participant Redis as Redis Streams

    Note over C: 1. 正常执行开始
    C->>DB: 创建事务记录 (tx_id=tx_002)
    DB-->>C: 返回事务ID
    
    C->>P1: 预检查请求
    P1-->>C: 预检查通过
    C->>P2: 预检查请求
    P2-->>C: 预检查通过
    C->>P3: 预检查请求
    P3-->>C: 预检查通过
    
    C->>Redis: 发布事务开始事件
    
    Note over C: 2. 执行阶段（参与方1成功）
    C->>P1: 执行本地事务 (命令1)
    P1->>DB: 记录本地事务开始
    P1-->>C: 执行成功
    C->>Redis: 发布参与方1执行事件
    
    Note over C: 3. 执行阶段（参与方2失败）
    C->>P2: 执行本地事务 (命令2)
    P2->>DB: 记录本地事务开始
    P2-->>C: 执行失败 (错误: 持仓不足)
    
    Note over C: 4. 失败检测与补偿触发
    C->>DB: 更新事务状态为compensating
    C->>Redis: 发布事务失败事件
    
    Note over C: 5. 补偿阶段（逆序补偿）
    C->>P1: 补偿事务请求 (tx_id=tx_002)
    P1->>DB: 读取本地事务记录
    P1->>DB: 执行补偿操作
    P1-->>C: 补偿成功
    C->>Redis: 发布参与方1补偿事件
    
    Note over C: 6. 补偿完成
    C->>DB: 更新事务状态为failed
    C->>Redis: 发布补偿完成事件
    
    Note over C: 7. 失败通知
    Redis-->>P2: 事务失败通知 (需人工检查)
    Redis-->>P3: 事务失败通知 (未执行)
```

### 3.2 补偿序列步骤说明

| 步骤 | 参与者 | 动作 | 数据 | 结果 |
|------|--------|------|------|------|
| **1.1-1.3** | 协调器 → 各参与方 | 预检查 | tx_id, 检查项 | 全部通过 |
| **2.1** | 协调器 → 参与方1 | 执行本地事务 | tx_id, 命令1 | 执行成功 |
| **2.2** | 参与方1 → PostgreSQL | 记录本地事务 | tx_id, 参与方1, 命令1 | 持久化成功 |
| **3.1** | 协调器 → 参与方2 | 执行本地事务 | tx_id, 命令2 | 执行失败（持仓不足） |
| **3.2** | 参与方2 → 协调器 | 失败响应 | tx_id, 错误信息 | 触发补偿 |
| **4.1** | 协调器 → PostgreSQL | 更新状态为compensating | tx_id, status=compensating | 状态更新 |
| **4.2** | 协调器 → Redis | 发布失败事件 | event_type=failed, tx_id, 错误原因 | 事件发布 |
| **5.1** | 协调器 → 参与方1 | 补偿事务请求 | tx_id, 补偿命令 | 读取本地记录 |
| **5.2** | 参与方1 → PostgreSQL | 读取本地事务记录 | tx_id, 参与方1 | 获取原命令 |
| **5.3** | 参与方1 → PostgreSQL | 执行补偿操作 | tx_id, 反向操作 | 补偿成功 |
| **5.4** | 参与方1 → 协调器 | 补偿成功响应 | tx_id, 补偿结果 | 补偿完成 |
| **6.1** | 协调器 → PostgreSQL | 更新状态为failed | tx_id, status=failed | 最终状态 |
| **7.1** | Redis → 各参与方 | 失败通知 | event_type=failed, tx_id | 清理状态 |

---

## 4. 活动图（业务流程）

### 4.1 Mermaid活动图

```mermaid
flowchart TD
    Start([开始]) --> CreateTransaction[创建Saga事务]
    CreateTransaction --> Precheck{预检查}
    
    Precheck -->|通过| Execute[执行本地事务]
    Precheck -->|失败| Fail1[事务失败]
    
    Execute --> CheckResult{检查执行结果}
    
    CheckResult -->|成功| MoreParticipants{更多参与方?}
    CheckResult -->|失败| TriggerCompensation[触发补偿]
    
    MoreParticipants -->|是| Execute
    MoreParticipants -->|否| Confirm[确认事务完成]
    
    Confirm --> Complete[事务完成]
    
    TriggerCompensation --> ReverseOrder[逆序补偿]
    ReverseOrder --> Compensate[执行补偿]
    Compensate --> CheckCompensation{补偿成功?}
    
    CheckCompensation -->|是| MoreToCompensate{更多需补偿?}
    CheckCompensation -->|否| ManualIntervention[人工干预]
    
    MoreToCompensate -->|是| Compensate
    MoreToCompensate -->|否| Fail2[补偿完成，事务失败]
    
    Fail1 --> End([结束])
    Complete --> End
    Fail2 --> End
    ManualIntervention --> End
```

### 4.2 活动节点说明

| 节点 | 类型 | 描述 | 输入 | 输出 |
|------|------|------|------|------|
| **CreateTransaction** | 操作 | 创建Saga事务记录 | 事务请求 | 事务ID |
| **Precheck** | 决策 | 预检查所有参与方 | 事务ID | 通过/失败 |
| **Execute** | 操作 | 执行参与方本地事务 | 命令数据 | 执行结果 |
| **CheckResult** | 决策 | 检查执行结果 | 执行结果 | 成功/失败 |
| **MoreParticipants** | 决策 | 检查是否还有参与方 | 参与方列表 | 是/否 |
| **Confirm** | 操作 | 确认事务完成 | 所有成功结果 | 确认结果 |
| **TriggerCompensation** | 操作 | 触发补偿机制 | 失败参与方ID | 补偿计划 |
| **ReverseOrder** | 操作 | 确定逆序补偿顺序 | 已执行参与方列表 | 补偿顺序 |
| **Compensate** | 操作 | 执行补偿事务 | 补偿命令 | 补偿结果 |
| **CheckCompensation** | 决策 | 检查补偿结果 | 补偿结果 | 成功/失败 |
| **MoreToCompensate** | 决策 | 检查是否还有需补偿 | 补偿列表 | 是/否 |
| **ManualIntervention** | 操作 | 人工干预处理 | 补偿失败信息 | 人工处理结果 |

---

## 5. 数据流图

### 5.1 Mermaid数据流图

```mermaid
graph TD
    subgraph "引擎层"
        E1[vn.py引擎]
        E2[RQAlpha引擎]
        E3[Backtrader引擎]
        E4[QMT引擎]
        E5[backtesting.py引擎]
    end
    
    subgraph "适配器层"
        A1[vn.py适配器]
        A2[RQAlpha适配器]
        A3[Backtrader适配器]
        A4[QMT适配器]
        A5[backtesting.py适配器]
    end
    
    subgraph "Saga层"
        P1[Saga参与方1]
        P2[Saga参与方2]
        P3[Saga参与方3]
        P4[Saga参与方4]
        P5[Saga参与方5]
        C[Saga协调器]
    end
    
    subgraph "存储层"
        DB[PostgreSQL]
        Redis[Redis Streams]
    end
    
    subgraph "监控层"
        Monitor[监控系统]
        Alert[告警系统]
    end
    
    E1 --> A1
    E2 --> A2
    E3 --> A3
    E4 --> A4
    E5 --> A5
    
    A1 --> P1
    A2 --> P2
    A3 --> P3
    A4 --> P4
    A5 --> P5
    
    P1 --> C
    P2 --> C
    P3 --> C
    P4 --> C
    P5 --> C
    
    C --> DB
    C --> Redis
    
    Redis --> P1
    Redis --> P2
    Redis --> P3
    Redis --> P4
    Redis --> P5
    
    DB --> Monitor
    Redis --> Monitor
    Monitor --> Alert
    
    style C fill:#e1f5e1
    style DB fill:#f0f8ff
    style Redis fill:#fff0f5
    style Monitor fill:#fffacd
```

### 5.2 数据流说明

| 数据流 | 方向 | 数据类型 | 频率 | 大小 |
|--------|------|----------|------|------|
| **引擎→适配器** | 单向 | 引擎原生数据 | 实时 | 1KB-1MB |
| **适配器→参与方** | 双向 | 统一数据模型 | 事务触发 | 1KB-10KB |
| **参与方→协调器** | 双向 | 命令/响应 | 事务步骤 | 1KB-5KB |
| **协调器→PostgreSQL** | 双向 | 事务状态 | 状态变更 | 1KB-2KB |
| **协调器→Redis** | 单向 | 事件消息 | 事件触发 | 1KB-5KB |
| **Redis→参与方** | 单向 | 事件通知 | 事件发布 | 1KB-2KB |
| **存储→监控** | 单向 | 监控指标 | 定期轮询 | 1KB-10KB |

---

## 6. 关键决策点流程图

### 6.1 Mermaid决策流程图

```mermaid
flowchart TD
    Start([事务开始]) --> D1{预检查通过?}
    
    D1 -->|是| D2{参与方1执行成功?}
    D1 -->|否| Fail1[事务失败]
    
    D2 -->|是| D3{参与方2执行成功?}
    D2 -->|否| Comp1[补偿参与方1]
    
    D3 -->|是| D4{参与方N执行成功?}
    D3 -->|否| Comp2[补偿参与方2<br>补偿参与方1]
    
    D4 -->|是| Success[事务成功]
    D4 -->|否| CompN[补偿参与方N<br>...<br>补偿参与方1]
    
    Comp1 --> Fail2[事务失败]
    Comp2 --> Fail3[事务失败]
    CompN --> FailN[事务失败]
    
    Success --> End1([结束成功])
    Fail1 --> End2([结束失败])
    Fail2 --> End2
    Fail3 --> End2
    FailN --> End2
```

### 6.2 决策点说明

| 决策点 | 条件 | 是路径 | 否路径 | 备注 |
|--------|------|--------|--------|------|
| **D1** | 所有参与方预检查通过 | 进入执行阶段 | 事务立即失败 | 避免无效事务执行 |
| **D2** | 参与方1本地事务执行成功 | 继续参与方2 | 补偿参与方1 | 第一个参与方失败只需补偿自己 |
| **D3** | 参与方2本地事务执行成功 | 继续参与方3 | 补偿参与方2→参与方1 | 逆序补偿已执行的参与方 |
| **D4** | 参与方N本地事务执行成功 | 事务成功 | 补偿参与方N→...→参与方1 | 最后一个参与方失败需补偿所有 |

---

## 7. 错误处理流程图

### 7.1 Mermaid错误处理图

```mermaid
flowchart TD
    Start([错误发生]) --> Detect[错误检测]
    
    Detect --> Classify{错误分类}
    
    Classify -->|预检查错误| PrecheckError[预检查错误处理]
    Classify -->|执行错误| ExecutionError[执行错误处理]
    Classify -->|补偿错误| CompensationError[补偿错误处理]
    Classify -->|系统错误| SystemError[系统错误处理]
    
    PrecheckError --> Log1[记录错误日志]
    Log1 --> Notify1[通知调用方]
    Notify1 --> Clean1[清理临时资源]
    Clean1 --> End1([处理完成])
    
    ExecutionError --> Trigger[触发补偿]
    Trigger --> ExecuteComp[执行补偿]
    ExecuteComp --> Log2[记录补偿日志]
    Log2 --> Notify2[通知相关方]
    Notify2 --> End2([处理完成])
    
    CompensationError --> Retry{重试次数<3?}
    Retry -->|是| Wait[等待重试]
    Wait --> ExecuteComp
    Retry -->|否| Escalate[升级处理]
    Escalate --> Manual[人工干预]
    Manual --> End3([处理完成])
    
    SystemError --> Recover{可自动恢复?}
    Recover -->|是| AutoRecover[自动恢复]
    AutoRecover --> End4([处理完成])
    Recover -->|否| Alert[发送告警]
    Alert --> Admin[管理员处理]
    Admin --> End5([处理完成])
```

### 7.2 错误处理策略

| 错误类型 | 检测方式 | 处理策略 | 恢复目标 | 监控指标 |
|----------|----------|----------|----------|----------|
| **预检查错误** | 预检查响应 | 立即失败，不执行事务 | 避免无效操作 | 预检查失败率 |
| **执行错误** | 执行响应超时/失败 | 触发补偿事务 | 数据一致性 | 执行失败率 |
| **补偿错误** | 补偿响应超时/失败 | 重试机制（最多3次） | 最终一致性 | 补偿失败率 |
| **系统错误** | 健康检查、异常监控 | 自动恢复或人工干预 | 系统可用性 | 系统可用率 |

---

## 8. 性能优化流程图

### 8.1 Mermaid性能优化图

```mermaid
flowchart TD
    Start([事务请求]) --> BatchCheck{批量处理?}
    
    BatchCheck -->|是| BatchProcess[批量事务处理]
    BatchCheck -->|否| SingleProcess[单事务处理]
    
    BatchProcess --> Split[拆分为子事务]
    Split --> Parallel{可并行?}
    
    Parallel -->|是| ParallelExecute[并行执行子事务]
    Parallel -->|否| SequenceExecute[顺序执行子事务]
    
    ParallelExecute --> Merge[合并结果]
    SequenceExecute --> Merge
    
    Merge --> BatchComplete[批量完成]
    
    SingleProcess --> NormalFlow[正常流程]
    NormalFlow --> SingleComplete[单事务完成]
    
    BatchComplete --> End1([完成])
    SingleComplete --> End2([完成])
    
    subgraph "优化策略"
        direction LR
        O1[批量处理]
        O2[并行执行]
        O3[缓存优化]
        O4[异步IO]
    end
    
    BatchProcess --> O1
    ParallelExecute --> O2
    Merge --> O3
    NormalFlow --> O4
```

### 8.2 优化策略说明

| 优化策略 | 适用场景 | 实现方式 | 预期收益 | 风险 |
|----------|----------|----------|----------|------|
| **批量处理** | 大量小事务 | 事务分组，批量提交 | 吞吐量提升50-80% | 批量失败影响范围大 |
| **并行执行** | 无依赖的子事务 | 多线程/协程并行 | 延迟降低30-60% | 资源竞争，复杂度增加 |
| **缓存优化** | 高频读取数据 | Redis缓存热点数据 | 读取延迟降低90% | 缓存一致性维护 |
| **异步IO** | 网络/磁盘IO | 异步非阻塞调用 | CPU利用率提升 | 异步编程复杂度 |

---

## 附录：流程图使用说明

### 使用场景

1. **架构设计评审**: 使用整体状态机图理解Saga模式完整生命周期
2. **开发实施指导**: 使用序列图明确各组件交互时序
3. **故障排查参考**: 使用错误处理流程图定位问题处理路径
4. **性能优化分析**: 使用性能优化流程图识别优化机会

### 版本管理

- **v1.0.0**: 基础流程图集，涵盖主要场景
- **v1.1.0**: 增加QMT引擎特定流程图
- **v1.2.0**: 增加分布式部署流程图
- **v2.0.0**: 交互式可视化流程图

### 合规检查

- ✅ 状态机完整覆盖所有业务场景
- ✅ 序列图明确展示组件交互
- ✅ 错误处理路径清晰可行
- ✅ 性能优化策略实际有效
- ✅ 符合专业机构文档标准

---

**文档版本历史**:
- v1.0.0 (2026-04-02): 初始版本，完整流程图集

**审核记录**:
- 架构审核: 首席蓝图架构师
- 技术审核: 待审核
- 流程图审核: 待审核

**生成工具**:
- 流程图: Mermaid.js
- 编辑工具: Markdown + 专业图表工具
- 版本控制: Git + 文档管理系统