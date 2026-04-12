---

module_id: P0_06_ACCOUNT_MANAGEMENT_001

version: 1.0.0

status: Active

created_date: 2026-04-07

last_updated: 2026-04-07

owner: 首席文档架构师

responsibility:

  - 账户生命周期管理

  - 资金管理

  - 账户快照

layer: layer_05

---



# 账户管理详细设计



## 核心定位



负责账户全生命周期管理，包括账户创建、资金划转、账户冻结、账户关闭等功能，支持模拟账户和实盘账户的统一管理。



> **职责边界**:

> - ✅ 本文档负责：账户创建、资金划转、账户冻结、账户关闭、账户快照

> - ❌ 本文档不负责：订单管理、交易执行、风险控制



## 设计目标



### 主要目标



1. **账户统一管理**: 支持模拟账户和实盘账户的统一管理

2. **资金安全保障**: 确保资金划转的安全性和准确性

3. **账户状态追踪**: 实时记录账户状态变化

4. **账户快照机制**: 定期生成账户快照用于审计和对账



### 质量目标



- 资金划转准确率: 100%

- 账户状态一致性: 100%

- 快照生成及时性: T+0



## 核心功能



### 账户管理特有功能



1. **账户创建服务**: 支持模拟账户和实盘账户创建

2. **资金划转服务**: 入金、出金、内部转账

3. **账户冻结服务**: 风控触发冻结、手动冻结

4. **账户快照服务**: 日终快照、实时快照

5. **账户查询服务**: 余额查询、流水查询、状态查询



### 领域模型



```python

class Account:

    """账户实体"""

    account_id: str          # 账户ID

    account_type: AccountType  # 账户类型(模拟/实盘)

    status: AccountStatus    # 账户状态

    balance: Decimal         # 账户余额

    available: Decimal       # 可用资金

    frozen: Decimal          # 冻结资金

    created_at: datetime     # 创建时间

    updated_at: datetime     # 更新时间



class AccountSnapshot:

    """账户快照实体"""

    snapshot_id: str         # 快照ID

    account_id: str          # 账户ID

    balance: Decimal         # 快照余额

    positions: List[Position] # 持仓列表

    snapshot_time: datetime  # 快照时间

```



## 接口设计



### 账户应用服务接口



```python

class AccountApplicationService:

    """账户应用服务"""

    

    def create_account(self, request: CreateAccountRequest) -> Account:

        """创建账户"""

        pass

    

    def deposit(self, account_id: str, amount: Decimal) -> Transaction:

        """入金"""

        pass

    

    def withdraw(self, account_id: str, amount: Decimal) -> Transaction:

        """出金"""

        pass

    

    def freeze_account(self, account_id: str, reason: str) -> None:

        """冻结账户"""

        pass

    

    def create_snapshot(self, account_id: str) -> AccountSnapshot:

        """创建账户快照"""

        pass

```



## 数据库设计



### 账户表 (accounts)



| 字段 | 类型 | 说明 |

|------|------|------|

| account_id | VARCHAR(32) | 账户ID (主键) |

| account_type | VARCHAR(20) | 账户类型 |

| status | VARCHAR(20) | 账户状态 |

| balance | DECIMAL(20,4) | 账户余额 |

| available | DECIMAL(20,4) | 可用资金 |

| frozen | DECIMAL(20,4) | 冻结资金 |

| created_at | TIMESTAMP | 创建时间 |

| updated_at | TIMESTAMP | 更新时间 |



### 账户快照表 (account_snapshots)



| 字段 | 类型 | 说明 |

|------|------|------|

| snapshot_id | VARCHAR(32) | 快照ID (主键) |

| account_id | VARCHAR(32) | 账户ID |

| balance | DECIMAL(20,4) | 快照余额 |

| snapshot_time | TIMESTAMP | 快照时间 |



---



**最后更新**: 2026-04-07

