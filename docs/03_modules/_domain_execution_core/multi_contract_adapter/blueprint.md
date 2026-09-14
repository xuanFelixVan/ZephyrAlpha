---
module_id: MOD-EX-055
title: "多契约生产适配器蓝图 — CTR-004/005/006 Schema版本演进+消费者注册+变更通知"
doc_type: blueprint
status: Active
version: "0.1.3"
design_maturity: production
ttl: permanent
responsibility_domain: 
---

# MOD-EX-055 | 多契约生产适配器 (Multi-Contract Adapter)

> **域**: D_EX_CORE | **优先级**: P2 | **成熟度**: design→production
> **SSoT**: depgraph MOD-EX-055 | **设计真源**: D-EX-CORE-55 "CTR-004/005/006 Schema+版本演进+消费者注册+变更通知"

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-EX-055`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-EX-055` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-EX-055` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-EX-055 | MOD-EX-055 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## §1 模块定位

多契约生产适配器——D_EX_CORE 域的**契约注册中心**。

管理 CTR-004 (Order) / CTR-005 (Fill) / CTR-006 (PositionSnapshot) 三份
跨域契约的 Schema 元数据、版本演进、消费者注册和变更通知。

**不是**契约本身的定义（契约定义在 `zephyr.shared.contracts.*`），而是契约的
**管理面**：谁生产、谁消费、什么版本、是否冻结、变更时通知谁。

### 与 contracts 的关系

| 层 | 职责 | 真源 |
|----|------|------|
| contracts/ (CTR-004/005/006) | 契约**数据结构**定义 (dataclass + 字段) | cross_layer_contracts.yaml |
| multi_contract_adapter (本模块) | 契约**管理面** (版本/消费者/通知) | depgraph MOD-EX-055 |

## §2 输入输出

### 输入
- 契约注册请求 (contract_id, version, producer, consumers, frozen)
- 消费者注册请求 (contract_id, consumer_domain, callback)
- 版本升级请求 (contract_id, new_version, changelog)

### 输出
- `ContractSchema`: 契约元数据快照 (不可变)
- `ContractRegistry`: 全量契约注册表
- 变更通知: 推送给已注册消费者

## §3 核心规则

1. **契约注册**: 启动时自动注册 CTR-004/005/006 三份契约的元数据
2. **版本追踪**: 每份契约有 schema_version (语义版本)，变更时版本递增
3. **消费者注册**: 消费域通过 `register_consumer()` 订阅契约变更
4. **冻结契约**: 已冻结契约 (frozen=True) 禁止版本升级，需 `--force` 逃生
5. **变更通知**: 契约版本变更时，自动通知所有已注册消费者
6. **不可变快照**: ContractSchema 为 frozen dataclass，变更生成新实例
7. **审计日志**: 所有注册/升级/通知操作记录审计日志

## §4 数据模型

```python
@dataclass(frozen=True)
class ContractSchema:
    contract_id: str          # "CTR-004"
    name: str                 # "Order"
    version: str              # "1.0"
    producer_domain: str      # "D_EX_CORE"
    consumer_domains: tuple[str, ...]  # ("D_PORTFOLIO", "D_EX_SOR")
    frozen: bool              # 是否冻结（禁止升级）
    ssot_path: str            # "cross_layer_contracts.yaml -> CTR-004"
    contract_class_path: str  # "zephyr.shared.contracts.order.Order"
    changelog: tuple[str, ...]  # 版本变更日志

@dataclass(frozen=True)
class MultiContractRegistry:
    contracts: dict[str, ContractSchema]  # contract_id -> schema
    consumer_callbacks: dict[str, list[Callable]]  # contract_id -> callbacks
```

## §5 错误契约

- `ContractAlreadyRegisteredError` (ZA-EX-055-01): 重复注册同一 contract_id
- `ContractNotFoundError` (ZA-EX-055-02): 查询/升级不存在的契约
- `ContractFrozenError` (ZA-EX-055-03): 升级已冻结契约（无 --force）
- `InvalidVersionError` (ZA-EX-055-04): 版本号格式非法或降级

## §6 测试计划

1. 契约注册: 注册 CTR-004/005/006，验证元数据正确
2. 重复注册: 同一 contract_id 二次注册 → ContractAlreadyRegisteredError
3. 消费者注册: 注册消费者 + 验证回调列表
4. 版本升级: 非冻结契约升级 → 版本递增 + 变更日志 + 通知消费者
5. 冻结契约升级: frozen=True 契约升级 → ContractFrozenError
6. 冻结契约强制升级: --force 升级 → 成功 + 审计标记
7. 版本降级: "2.0"→"1.0" → InvalidVersionError
8. 变更通知: 升级后所有已注册回调被调用
9. 查询: 按 contract_id / producer_domain / consumer_domain 查询
10. 审计日志: 所有操作有审计记录

---

## 1. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 1.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 1.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §1（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


