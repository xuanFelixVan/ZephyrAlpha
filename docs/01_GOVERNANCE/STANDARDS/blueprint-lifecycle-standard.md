---
module_id: GOV_BLUEPRINT_LIFECYCLE_STANDARD
version: '1.0.0'
status: Active
created_date: '2026-04-16'
last_updated: '2026-04-16'
owner: Project Owner
layer: cross_layer
priority: P0
standard_type: governance
---

# 蓝图生命周期标准 (Blueprint Lifecycle Standard)

> **对标参考**：Two Sigma Model Inventory、TOGAF Architecture Repository、量化机构 Strategy Lifecycle Management 实践。
> **适用范围**：所有存放在 `docs/01_FRAMEWORK/`（过渡期）及未来 `docs/03_BLUEPRINTS/` 中的蓝图文件。

---

## 一、蓝图唯一标识规范

每个蓝图必须有全局唯一的 `module_id`，格式：`L{XX}_{DOMAIN}_{MODULE}`

```yaml
module_id: L00_DATA_AKSHARE_ADAPTER   # Layer 00，数据域，AKShare 适配器
module_id: L04_ML_FEATURE_ENGINEERING # Layer 04，ML 域，特征工程
module_id: CL_SHARED_BASE_ERROR       # Cross-Layer，共享，基础错误处理
```

---

## 二、生命周期状态机

### 2.1 状态定义

| 状态 | 含义 | 允许的操作 |
|------|------|-----------|
| `Draft` | 编写中，可自由修改 | 直接修改，无需 CR |
| `Review` | 提交同行评审，待批准 | 评审意见可修改 |
| `Active` | 经批准冻结，为 Baselined 版本 | **变更需走 CR 流程**（见 2.3）|
| `Superseded` | 已被新版本取代，保留追溯链 | 只读，不可修改 |
| `Deprecated` | 计划退役，已设定退役日期 | 只读；退役时执行 Section 4 |
| `Retired` | 已归档，完成价值提取 | 只读，不可删除 |

### 2.2 状态流转图

```
Draft → Review → Active → Superseded → Retired
                 Active → Deprecated → Retired
```

**约束**：
- `Draft` 和 `Review` 状态的蓝图不计入 Blueprint Registry
- `Active` 转 `Superseded`：必须创建新蓝图并在新蓝图中添加 `supersedes: [旧 module_id]`
- `Active` 转 `Deprecated`：必须填写 `deprecated_date` 和 `deprecated_reason`
- `Retired` 状态为终态，不可回滚

### 2.3 Active 蓝图变更控制（Change Request）

**Minor Change（不需要 CR）**：
- 修正拼写错误、格式调整
- 更新 `last_updated` 日期
- 添加澄清性注释（不改变设计决策）
- 操作：直接修改，`version` 末位数字递增（1.0.0 → 1.0.1）

**Major Change（需要 CR 流程）**：
- 改变接口签名、数据模型、核心算法
- 改变依赖关系
- 改变 layer 归属
- 操作：**创建新蓝图文件**（新版本号），在新文件中标注 `supersedes: [旧 module_id]`；旧文件 status 改为 `Superseded`

---

## 三、Frontmatter 强制字段

**所有 `status: Active` 的蓝图必须包含以下字段**：

```yaml
---
module_id: 'L{XX}_{DOMAIN}_{MODULE}'     # 必须，全局唯一
version: '1.0.0'                          # 必须，语义版本号
status: Active                            # 必须：Draft/Review/Active/Superseded/Deprecated/Retired
created_date: '2026-04-16'               # 必须
last_updated: '2026-04-16'               # 必须，每次修改后更新
owner: Project Owner                      # 必须
layer: layer_00                           # 必须，按实际架构层标注（layer_00 ~ layer_11 或 cross_layer）
priority: P0                              # 必须，Active 蓝图必须有：P0/P1/P2
---
```

**退役专用字段（status: Deprecated 或 Retired 时必须添加）**：

```yaml
deprecated_date: '2026-04-16'
deprecated_reason: "被 v2.0 取代（see: new-module-v2-blueprint.md）"
superseded_by: 'L00_DATA_AKSHARE_ADAPTER_V2'
value_extracted_to:
  - "ADR-042: 为何选择 LSTM 而非 Transformer"
  - "FACTOR-023: 动量衰减因子构建方法"
  - "LESSON-008: 调度器不应耦合特定数据源"
```

---

## 四、退役流程（Knowledge Harvesting Checklist）

当蓝图从 `Active` 转为 `Deprecated` 时，**必须执行以下 Checklist**：

### Step 1：影响分析
- [ ] 运行 `python scripts/governance/scan_blueprint_dependencies.py --module-id {MODULE_ID}` 找出所有引用此蓝图的文件
- [ ] 通知所有依赖方（其他蓝图、施工图）更新引用
- [ ] 确认无残留的强依赖后，方可执行 Step 2

### Step 2：价值提取（强制，不可跳过）

| 价值类型 | 目标文件 | 提取内容举例 |
|---------|---------|------------|
| 设计决策 | `docs/02_ARCHITECTURE/TECH_DECISION_RECORDS.md` | 为何选择方案 A 而非 B |
| 可复用模式 | `docs/08_KNOWLEDGE/BEST_PRACTICES/` | 通用架构模式、API 设计模式 |
| 失败教训 | `docs/01_GOVERNANCE/REGISTERS/lessons-learned-register.md` | 失败的设计、技术债、回测陷阱 |
| 术语/概念 | `docs/08_KNOWLEDGE/` 术语表 | 新定义的领域术语 |
| 可复用因子 | `docs/08_KNOWLEDGE/FACTOR_LIBRARY/` | 算法公式、因子构建方法 |
| 可复用策略 | `docs/08_KNOWLEDGE/STRATEGY_LIBRARY/` | 策略结构、信号组合方法 |

**提取质量要求**：
- 每条提取的知识条目必须包含 `extracted_from: {module_id}` 反向链接
- 不能只是复制蓝图内容——必须是经提炼的、可独立使用的知识条目

### Step 3：更新蓝图 Frontmatter

```yaml
status: Retired
retired_date: '2026-04-16'
retired_reason: "Superseded by v2.0"
value_extracted_to:
  - "ADR-XXX: ..."
  - "PATTERN-XXX: ..."
```

### Step 4：归档操作
- [ ] 将蓝图文件移至 `docs/06_ARCHIVE/blueprints/`
- [ ] 文件名末尾加 `-archived` 后缀（如 `xxx-blueprint-archived.md`）
- [ ] 在 `docs/01_FRAMEWORK/INDEX.md` 中移除该文件链接
- [ ] 在 Blueprint Registry 中更新状态

### Step 5：提交记录
Commit message 格式：
```
governance(blueprints): retire {module_id}

salvaged: ADR-XXX, PATTERN-XXX, LESSON-XXX
retired_reason: {reason}
```

---

## 五、Blueprint Registry 维护规则

**Blueprint Registry**（`docs/02_ARCHITECTURE/BLUEPRINT_DOMAIN_INVENTORY.yaml`）是机器可读的蓝图中央注册表，由脚本自动维护。

每个活跃蓝图在注册表中应有一条记录：

```yaml
- module_id: L00_DATA_AKSHARE_ADAPTER
  title: "AKShare A 股日线 OHLCV 适配器"
  path: docs/01_FRAMEWORK/akshare-adapter-blueprint.md
  status: Active
  layer: layer_00
  priority: P0
  tags: [data, akshare, ohlcv, adapter]
  depends_on: []
  required_by: [L02_ALPHA_FACTOR_ENGINE]
  created_date: '2026-04-01'
  last_updated: '2026-04-16'
  owner: Project Owner
```

**自动化**：运行 `python scripts/governance/generate_blueprint_registry.py` 从所有蓝图 frontmatter 自动生成/更新注册表。

---

## 六、Pre-commit 自动校验

以下检查在 `git commit` 时自动执行：

1. **Frontmatter 完整性**：Active 蓝图必须有 `module_id`、`version`、`status`、`layer`、`priority` 字段
2. **状态合法性**：`status` 值必须在 {Draft, Review, Active, Superseded, Deprecated, Retired} 中
3. **退役完整性**：`status: Retired` 的蓝图必须有 `value_extracted_to` 字段
4. **Layer 一致性**：`layer` 值必须与文件所在目录（或 module_id 前缀）一致

---

## 七、优先级分级（P0/P1/P2）详细标准

| 级别 | 标准 | 示例 |
|------|------|------|
| P0 | 属于主交易链路核心，没有它系统无法运行 | 数据采集、风控、订单管理 |
| P1 | 增强类功能，专业机构标配，当前 Phase 计划实现 | 因子评估、绩效归因、回测框架 |
| P2 | 机构级合规、前沿探索、规模化才有价值 | 强化学习、MiFID II 报告、暗池接入 |

---

## 变更历史

| 版本 | 日期 | 变更描述 | 变更人 |
|------|------|---------|--------|
| 1.0.0 | 2026-04-16 | 初始创建，对标专业量化机构 Model Lifecycle 实践 | AI |
