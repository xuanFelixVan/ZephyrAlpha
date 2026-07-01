---
module_id: ARCH-ARC-001
title: "待定架构决策文档"
doc_type: register
status: deprecated
version: 1.0.0
date: 2026-06-27
owner: ZephyrAlpha-Owner
ttl: permanent
---

# 待定架构决策文档

> **文档ID**: ARCH-DECISIONS-PENDING-001
> **创建时间**: 2026-06-19
> **最后更新**: 2026-06-22（T6/T7裁定完成）
> **任务卡**: DM-100244 (K1)
> **状态**: T6✅已裁定（交易链事件延后阶段8/注册表永不实施） | T7✅已裁定（全局/域级配置永不实施） | T17✅已完成 | T18⏸暂缓（转阶段8）
> **来源**: architecture_upgrade_discussion.md §十六 待定决策清单

---

## 决策1: T6 — 事件类型体系设计

### 实施状态（2026-06-22核实）

✅ **已实施（任务治理域）** — 实际实施在 `src/zephyr/shared/event_bus.py`（非文档规划的 `events/event_types.py`），采用选项B（Enum类）而非选项C（注册表+Enum）。

**实际实施内容**：
- `EventType` 枚举：11个任务治理域事件（TASK_CREATED/TASK_LOCKED/TASK_ASSIGNED/TASK_STARTED/TASK_COMPLETED/TASK_FAILED/TASK_ROLLBACK/GATE_PASSED/GATE_FAILED/SCOPE_DRIFT/DEPENDENCY_RESOLVED）
- `DomainEvent` dataclass：event_id/event_type/task_id/payload/timestamp_utc
- `EventBus` 类：单例模式，publish/subscribe
- `EventBusUpgrader`（`src/zephyr/shared/events/event_bus_upgrade.py`）：事件版本化迁移

**与文档方案差异**：
1. 实施的是任务治理域事件（11个），非文档规划的交易链事件（MARKET_DATA→FILL_RECEIVED 8个）
2. 采用 Enum 类（选项B），未实施 DomainEventRegistry 注册表（选项C的扩展部分）
3. 路径在 `shared/event_bus.py`，非文档规划的 `shared/events/event_types.py`

**未实施部分**（文档原规划）：
- 核心交易链事件（MARKET_DATA/KLINE_3S/FACTOR_SIGNAL/STRATEGY_SIGNAL/RISK_APPROVED/ORDER_CREATED/FILL_RECEIVED/POSITION_UPDATED）
- DomainEventRegistry 注册表（域级自定义事件扩展）
- R1-2 AsyncEventBus（异步事件总线）

### 裁定结果（2026-06-22 客观架构师裁定）

**裁定依据**：量化社区实践（gs-quant 12事件/事件驱动回测标准4事件）+ 氛围编程社区实践 + 100% AI开发原则（少一层抽象=少一个幻觉源）+ 项目当前阶段（阶段4完成，阶段8业务层未启动）

| 未实施部分 | 裁定 | 时机 | 核心理由 |
|-----------|------|------|---------|
| 核心交易链事件（8个） | **简化为4-5个，延后阶段8** | 阶段8业务层建设时 | 真实需求但前置依赖未就绪；原方案8事件过度设计，业界标准4事件（Market/Signal/Order/Fill） |
| DomainEventRegistry 注册表 | **❌ 永不实施** | — | 过度设计，违反"少一层抽象=少一个幻觉源"原则；Enum类已满足类型安全需求 |
| R1-2 AsyncEventBus | **延后阶段2** | 阶段2 R1/R2升级时 | 交易链事件前置依赖，按阶段规划推进 |

**裁定理由详述**：

1. **需求必要性**：✅ 真实需求。事件驱动架构（EDA）是量化交易系统标准实践（gs-quant/事件驱动回测引擎），防止 lookahead bias 的唯一结构化方案。数据契约 `trading_contracts/` 已就绪，待业务层启动时接入。

2. **时机合理性**：❌ 现在不做。前置依赖 R1-2 AsyncEventBus（阶段2）未开始；业务层（阶段8）未启动，无实际消费者；当前任务治理域11事件已满足治理阶段需求。

3. **方案合理性**：⚠️ 原方案选项C过度设计。
   - 选项B（Enum类）已够用：类型安全 + IDE补全 + AI可读
   - 选项C（注册表+Enum）两套机制并存=多一层抽象=多一个幻觉源
   - 业界对标：gs-quant 用单一 Event 基类 + 子类，非注册表模式；事件驱动回测标准4事件，非8事件

4. **100% AI 场景适配**：Enum类优于字符串（类型安全），注册表增加复杂度（违反"一条规则>两条规则"原则）。

<details>
<summary>📋 详细设计（已折叠——实施时未采用，保留作参考）</summary>

### 背景

当前 EventBus 完全同步+内存，handler 异常被 `except: pass` 吞掉。R1 运行时异步化路线图（§4.1）规划了 AsyncEventBus（R1-2），但事件类型枚举体系未定义。

从实时计算数据流设计（§6.5）可见，需要以下事件类型：

```
数据源 → MARKET_DATA → KLINE_3S → FACTOR_SIGNAL → STRATEGY_SIGNAL → RISK_APPROVED → ORDER_CREATED → FILL_RECEIVED
```

**容量要求**（§7.3）：240 events/s，100 AI Session 并发，500 findings/cycle。

### 选项

| 选项 | 描述 | 优点 | 缺点 |
|------|------|------|------|
| A: 字符串枚举 | `EventBus.publish("MARKET_DATA", payload)` | 简单灵活，无需预定义 | 无类型检查，拼写错误运行时才暴露 |
| B: Enum类 | `class EventType(Enum): MARKET_DATA = auto()` | 类型安全，IDE自动补全 | 新增事件需改Enum类，跨模块耦合 |
| C: 注册表+Enum | Enum定义核心事件 + 注册表扩展自定义事件 | 核心类型安全 + 扩展灵活 | 两套机制并存，复杂度高 |

### 利弊分析

- **选项A** 适合快速原型，但 240 events/s + 100 Session 并发下，字符串匹配开销和拼写错误风险不可接受
- **选项B** 是主流做法（如 Python 标准库 `signal.Signals`），但 ZephyrAlpha 有 61 域，每域可能有自定义事件，全部塞入一个 Enum 不可维护
- **选项C** 兼顾安全与扩展，核心交易链事件（MARKET_DATA→FILL_RECEIVED）用 Enum，域级自定义事件用注册表

### 推荐方案

**选项C: 注册表+Enum**

```python
# src/zephyr/shared/events/event_types.py
from enum import Enum, auto

class CoreEventType(Enum):
    """核心交易链事件——类型安全，不可扩展（需改代码）"""
    MARKET_DATA = auto()      # 行情数据到达
    KLINE_3S = auto()         # 3秒K线聚合完成
    FACTOR_SIGNAL = auto()    # 因子信号生成
    STRATEGY_SIGNAL = auto()  # 策略信号生成
    RISK_APPROVED = auto()    # 风控审批通过
    ORDER_CREATED = auto()    # 订单创建
    FILL_RECEIVED = auto()    # 成交回报
    POSITION_UPDATED = auto() # 持仓更新

# 域级事件注册表——运行时注册，灵活扩展
class DomainEventRegistry:
    _events: dict[str, str] = {}

    @classmethod
    def register(cls, domain_id: str, event_name: str):
        key = f"{domain_id}.{event_name}"
        cls._events[key] = key

    @classmethod
    def get(cls, domain_id: str, event_name: str) -> str:
        return cls._events.get(f"{domain_id}.{event_name}", "")
```

**理由**：核心交易链 8 个事件用 Enum 保证类型安全；61 域的自定义事件用注册表灵活扩展。容量 240 events/s 下 Enum 匹配 O(1)，注册表 dict 查找 O(1)。

</details>

---

## 决策2: T7 — 三级配置具体结构

### 实施状态（2026-06-22核实）

⚠️ **部分实施** — 文档规划的"全局+域+蓝图内联"三级结构中，仅蓝图内联配置已实施，config/ 按功能分目录已实施（但非文档规划的按域分目录）。

**已实施部分**：
- ✅ 蓝图内联配置：蓝图 MD 中含 §配置 章节（如 `docs/03_modules/_system_master/blueprint.md`）
- ✅ config/ 按功能分目录：`config/capacity/`、`config/compression/`、`config/infra/`、`config/runtime/` 子目录已存在

**未实施部分**（文档原规划）：
- ❌ 全局配置文件 `config/global.yaml` 不存在
- ❌ 域级配置目录 `config/domains/` 不存在（文档规划的 `config/domains/D-XXX.yaml` 61个域配置文件未创建）

**与文档方案差异**：
1. 文档规划按域分目录（`config/domains/D-XXX.yaml`），实际按功能分目录（capacity/compression/infra/runtime/）
2. 文档规划全局配置 1 文件（`config/global.yaml`），实际未创建
3. 实际结构更接近选项B（按功能分目录），非文档推荐的选项C（混合结构）

### 裁定结果（2026-06-22 客观架构师裁定）

**裁定依据**：配置管理业界实践（AWS AppConfig/K8s ConfigMap/微服务配置中心）+ 氛围编程社区实践（Cursor/Claude Code 单一文本配置）+ 100% AI开发原则（少一层抽象=少一个幻觉源）+ 项目实际约束（单机单环境部署）

| 未实施部分 | 裁定 | 时机 | 核心理由 |
|-----------|------|------|---------|
| `config/global.yaml` 全局配置 | **❌ 永不实施（当前阶段）** | 按需补充 | 单机单环境无全局配置共享需求；按功能分目录已满足；若阶段8出现跨域共享需求再按需补充 |
| `config/domains/` 域级配置 | **❌ 永不实施** | — | 61个域配置文件=过度抽象，违反"少一层抽象=少一个幻觉源"原则；单环境无配置隔离需求 |

**裁定理由详述**：

1. **需求必要性**：⚠️ 弱需求（被高估）。文档规划背景是"1000蓝图不可管理"（§7.2 盲点C），但实际当前 55 域、节点 14383，蓝图未达1000；单机部署无多服务/多租户配置共享需求；单一运行环境（单台PC）无 dev/test/prod 环境隔离需求。

2. **时机合理性**：❌ 现在不做。当前 config/ 43 文件按功能分目录已满足阶段4治理需求，无管理困难；业务层（阶段8）是否出现跨域配置共享需求未知。

3. **方案合理性**：❌ 原方案选项C过度设计。
   - 选项B（按功能分目录）已够用：功能分层清晰，AI可发现
   - 选项C（混合结构）61个域配置文件=过度抽象，违反"一条规则>两条规则"原则
   - 业界对标：AWS AppConfig template+tenant+environment 三层适合多租户/多环境，ZephyrAlpha 单机单环境不适用；K8s ConfigMap 环境变量+YAML 文件，ZephyrAlpha 当前模式已对标；氛围编程社区（Cursor/Claude Code）单一文本配置文件，ZephyrAlpha 当前模式已对标

4. **100% AI 场景适配**：少一层抽象=少一个幻觉源。61个域配置文件增加 AI 理解成本，无实际收益。

<details>
<summary>📋 详细设计（已折叠——部分采用，保留作参考）</summary>

### 背景

当前 `config/` 目录 0.16MB/43 文件，扁平结构。1000 蓝图不可管理（§7.2 盲点C裁定），需三级配置架构。

**已裁定方向**（§7.2）：三级配置 = 全局(config/) + 域(config/domains/) + 蓝图(docs/03_modules/_domain_xxx/)。但具体目录结构和文件命名规则未确定。

### 选项

| 选项 | 描述 | 优点 | 缺点 |
|------|------|------|------|
| A: 按域分目录 | `config/domains/D-INFRA/config.yaml` | 与域结构对齐，易查找 | 域ID变更需重命名目录 |
| B: 按功能分目录 | `config/global/`, `config/domains/`, `config/blueprints/` | 功能分层清晰 | 与域结构不对齐，跨域配置难归类 |
| C: 混合结构 | 全局`config/global.yaml` + 域`config/domains/{domain_id}.yaml` + 蓝图内联 | 最小文件数，SSoT清晰 | 蓝图内联配置与文档混合 |

### 利弊分析

- **选项A** 与 61 域结构对齐，但每域一个目录 = 61 目录，大部分域只有 1-2 个配置文件，目录开销大于内容
- **选项B** 功能分层清晰，但 `config/blueprints/` 与 `docs/03_modules/` 蓝图重复，违反 SSoT
- **选项C** 全局配置 1 文件 + 域配置 61 文件（每域 1 个），蓝图配置内联在蓝图 MD 中。文件数最少，SSoT 最清晰

### 推荐方案

**选项C: 混合结构**

```
config/
├── global.yaml                    # 全局配置（数据库路径、日志级别、API密钥等）
├── domains/
│   ├── D-INFRA.yaml               # 基础设施域配置
│   ├── D-GOVERNANCE.yaml          # 治理域配置
│   ├── D-SECURITY.yaml            # 安全域配置
│   └── ... (61个域配置文件)
└── README.md                      # 配置使用说明
```

**蓝图级配置**：内联在 `docs/03_modules/_domain_xxx/{module}/blueprint.md` 的 §配置 章节，不单独建文件。

**加载优先级**：全局 → 域 → 蓝图（后者覆盖前者同名键）。

**理由**：
1. 全局 1 文件 + 域 61 文件 = 62 文件，比当前 43 文件仅多 19 文件，可控
2. 每域 1 配置文件，域ID 变更只需重命名 1 文件
3. 蓝图配置内联避免 SSoT 断裂
4. 加载优先级明确，覆盖语义清晰

</details>

---

## 决策3: T17 — 模块级 [DOMAIN] 字段声明

### 实施状态（2026-06-22核实）

✅ **已完成（STEP 1-4）** — 采用选项B（可选声明），生成器支持 `[DOMAIN]` 字段覆盖路径派生，22 个跨域文件已标注。

**已完成工作**：
- STEP 1 ✅ 生成器 `_extract_domain_override()` + `derive_domain_id(filepath=)` 覆盖逻辑
- STEP 2 ✅ 头部体系从十字段扩展为十一字段（[DOMAIN] 可选）
- STEP 3 ✅ 22 个明确跨域文件已添加 [DOMAIN] 字段（保守映射，治理核心保留 D-GOVERNANCE）
- STEP 4 ✅ 验证 22/22 文件 [DOMAIN] 读取正确 + 无 [DOMAIN] 文件走路径派生

**未完成部分**（未来工作，不阻塞当前阶段）：
- STEP 5 ⏸ 阶段5物理搬家后清理（搬家后重新评估跨域文件标注）

<details>
<summary>📋 详细设计（已折叠——已采用，保留作参考）</summary>

### 背景

当前模块的 `domain_id` 由生成器通过路径派生（`UNREGISTERED_SRC_MAP` + `DOMAIN_NAME_TO_LAYER`）。路径派生的问题：模块放在错误目录时，domain_id 会被错误推导，无法纠正。

**实际案例**：`src/zephyr/governance/` 下有 422 个平铺文件，其中约 100-150 个实际属于其他域（如 trading、data、security），但因路径在 governance/ 下被错误标记为 D-GOVERNANCE。

### 选项

| 选项 | 描述 | 优点 | 缺点 |
|------|------|------|------|
| A: 强制声明 | 每个模块文件头必须含 `[DOMAIN] D-XXX`，无则报错 | 100% 准确，无歧义 | 6452 个 production 模块需逐一添加，工作量大 |
| B: 可选声明 | 文件头有 `[DOMAIN]` 则覆盖路径派生，无则用路径派生 | 渐进式，仅错放模块需添加 | 大部分模块仍靠路径派生，错放问题部分解决 |
| C: 注册表覆盖 | 在 depgraph.db 的 `domain_overrides` 表中记录 path→domain_id 覆盖映射 | 不改源码，集中管理 | 覆盖表与源码分离，漂移风险 |

### 利弊分析

- **选项A** 最严格，但 6452 个模块逐一添加 `[DOMAIN]` 字段不现实，且大部分模块路径正确无需覆盖
- **选项B** 渐进式，仅约 100-150 个错放模块需添加 `[DOMAIN]` 字段，工作量可控。但需修改生成器支持读取 `[DOMAIN]` 字段
- **选项C** 不改源码，但 depgraph.db 中的覆盖表与源码分离，AI session 可能不知道覆盖表存在，导致漂移

### 推荐方案

**选项B: 可选声明**

**文件头格式**（复用现有十字段头部）：

```python
# [BLUEPRINT] MOD-INF-005 | src/zephyr/governance/kill_switch.py | §3
# [MODULE] zephyr.governance.kill_switch
# [DOMAIN] D-RESILIENCE    # ← 新增字段，覆盖路径派生的 D-GOVERNANCE
# [INVARIANTS] ...
# [MODIFY-GUARD] ...
```

**生成器修改**（`generate_project_depgraph.py`）：

```python
# 读取文件头 [DOMAIN] 字段，覆盖路径派生
def _extract_domain_override(file_path: Path) -> str | None:
    """从文件头提取 [DOMAIN] 字段，返回 domain_id 或 None"""
    try:
        with open(file_path, encoding="utf-8") as f:
            for _ in range(20):  # 只读前20行
                line = f.readline()
                if line.startswith("# [DOMAIN]"):
                    return line.split("]", 1)[1].strip()
    except (OSError, UnicodeDecodeError):
        pass
    return None

# 在 domain_derivation 中：
override = _extract_domain_override(py_file)
if override:
    domain_id = override  # 覆盖路径派生
```

**实施计划**：
1. 修改生成器支持 `[DOMAIN]` 字段（约 20 行代码）
2. 为 100-150 个错放模块添加 `[DOMAIN]` 字段（可批量处理）
3. 重新生成 depgraph 验证 domain_id 正确性

**理由**：
1. 渐进式，不破坏现有 6452 个模块
2. 仅错放模块需添加字段，工作量可控
3. 字段在源码中，AI session 可见，无漂移风险
4. 与现有十一字段头部体系一致

</details>

---

## 决策4: T18 — 依赖图数据真源裁定（设计态YAML化）

### 背景

当前架构存在两类数据的真源边界模糊问题：

| 数据类型 | 当前真源 | 派生物 | 裁定依据 |
|---------|---------|--------|---------|
| 规则内容（trae_028等17类规则yaml） | YAML文件 ✓ | depgraph.db规则表（只读缓存） | D56裁定、§18.8.1 |
| 依赖图数据（nodes/edges/domains） | depgraph.db | project-entity-depgraph.yaml（派生快照） | §3.3/§3.4/§18.3 |

**问题**：depgraph.db混合了设计态和运营态数据，导致：
1. 设计态决策（域划分、路径映射、跨模块依赖声明）无法git审计
2. 7977个设计态节点存在二进制db中，git无法diff/merge/blame
3. AI不能直接Read（157MB OOM风险），需extract_depgraph.py中间层
4. 设计态修改需apply_depgraph.py，有学习曲线，且无冲突可见性

### 第一性原理分析

**核心问题**：在100% AI开发的项目中，依赖图数据的真源应该满足什么特性？

**七项特性评估**：

| # | 特性 | YAML | SQLite DB | 胜者 |
|---|------|:---:|:---:|:---:|
| 1 | AI可读性（直接Read理解语义） | ✅ 文本，AI原生 | ❌ 二进制，需extract中间层 | YAML |
| 2 | Git可审计（diff/merge/blame追溯） | ✅ 原生支持 | ❌ 二进制无法diff | YAML |
| 3 | 人类可审查（Owner能看懂改了什么） | ✅ 文本可读 | ❌ 需SQL查询 | YAML |
| 4 | 无生成步骤（真源不依赖生成器） | ✅ 直接编辑 | ⚠️ 需apply_depgraph.py | YAML |
| 5 | 冲突可检测（多AI并发修改） | ✅ git merge conflict | ⚠️ SQLite锁，冲突不可见 | YAML |
| 6 | 查询性能（关系JOIN/过滤） | ❌ 全量加载或流式解析 | ✅ SQL索引，毫秒级 | DB |
| 7 | 大规模数据（14392节点/8047边） | ⚠️ 37万行，加载慢 | ✅ 索引查询快 | DB |

**结论**：YAML胜4项（1-5，AI可读+git可审计+人类可审查+无生成步骤+冲突可检测），DB胜2项（6-7，查询性能+大规模数据）。

### 关键区分：设计态 vs 运营态

依赖图数据应按生命周期分层，真源不同：

| 数据子类 | 定义 | 第一性原理应有的真源 | 理由 |
|---------|------|-------------------|------|
| **设计态** | 人工/AI决策的"应该是什么样"（域划分、路径映射、跨模块依赖声明） | **YAML** | 决策类数据，需git审计+AI可读+人类可审查 |
| **运营态** | 代码扫描的"实际是什么样"（文件节点、import边） | **代码本身**（db为派生索引） | 可重建，扫描产物，非决策 |

**当前架构根本问题**：depgraph.db混合了设计态和运营态，导致设计态决策无法git审计。

### 业界对标

| 系统 | 决策类数据真源 | 运行时/扫描数据 | 模式 |
|------|--------------|---------------|------|
| Bazel/Google | BUILD文件（文本） | 内存索引（派生） | 文本真源+DB派生 |
| Kubernetes | YAML manifest | etcd运行时状态 | 文本真源+DB派生 |
| Terraform | .tf文件 | state文件（派生） | 文本真源+DB派生 |
| dbt | .sql/.yaml | target/编译产物 | 文本真源+DB派生 |
| GitHub Actions | .github/workflows/*.yaml | 运行时日志 | 文本真源+DB派生 |

**业界共识**：决策类数据用文本文件做真源，DB做派生缓存/查询加速层。

### 氛围编程社区实践

| 工具 | 规则/配置真源 | 特点 |
|------|-------------|------|
| Cursor | .mdc/.cursorrules（文本） | AI原生可读 |
| Claude Code | CLAUDE.md（文本） | AI原生可读 |
| Cline | .clinerules（文本） | AI原生可读 |
| Windsurf | .windsurfrules（文本） | AI原生可读 |

**氛围编程社区共识**：AI直接消费的配置/规则用文本文件，不用DB。

### 推荐方案

**选项B: 分层真源（设计态YAML化 + 运营态保持DB）**

```
┌─────────────────────────────────────────────────────────────┐
│  决策类数据（规则 + 设计态依赖图）                            │
│  真源：YAML文件（git可审计，AI可读，人类可审查）              │
│  - 规则内容：docs/01_policies_and_standards/rules/*.yaml     │
│  - 设计态依赖：data/asset_index/design_state/*.yaml（新增）  │
│  同步：YAML → depgraph.db 单向（sync脚本）                   │
│  DB角色：只读缓存（查询加速）                                 │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│  扫描类数据（运营态依赖图）                                   │
│  真源：代码本身（src/zephyr/**/*.py）                        │
│  生成器：generate_project_depgraph.py（扫描代码→写DB）        │
│  DB角色：运营态索引（可重建，非真源）                         │
│  生命周期：每次代码变更后重新生成                             │
└─────────────────────────────────────────────────────────────┘
```

### 实施路径

| 阶段 | 工作 | 优先级 | 理由 |
|------|------|:---:|------|
| 当前 | 维持现状（db是依赖图真源） | - | 阶段5物理搬家优先，避免重构风险 |
| 阶段5后 | 评估设计态数据YAML化 | 中 | 将7977个设计态节点导出为YAML，git可审计 |
| 长期 | 统一真源架构 | 低 | 决策类→YAML，扫描类→DB，sync层连接 |

### 理由

1. **符合第一性原理**：决策类数据（设计态）需git审计+AI可读+人类可审查，YAML满足前4项特性
2. **符合业界共识**：Bazel/K8s/Terraform/dbt均采用"文本真源+DB派生"模式
3. **符合氛围编程实践**：AI直接消费的配置用文本文件
4. **与D56裁定一致**：规则内容已YAML化为真源，设计态数据应遵循同样原则
5. **渐进式**：不破坏现有运营态数据，仅设计态数据YAML化
6. **可审计**：设计态决策变更可通过git diff追溯，解决当前无法审计问题

### 风险与缓解

| 风险 | 缓解措施 |
|------|---------|
| YAML大规模数据加载慢 | 分文件存储（按域拆分）+ 增量加载 |
| 查询性能下降 | DB作为查询加速层保留，YAML→DB单向同步 |
| 重构成本 | 阶段5后评估，不阻塞当前物理搬家 |
| 设计态与运营态边界模糊 | 通过design_maturity字段区分，YAML仅存design_maturity='design'的节点 |

### Owner讨论结论（2026-06-21）

**裁定：T18暂缓，转为未来"生产环节"**

**讨论要点**：

1. **全景图的核心价值已达成共识**：depgraph.db是完整的项目蓝图，所有模块依赖、数据流向、边界约束都在里面更新和对齐。有了全景图后，AI几乎不会产生幻觉和漂移——全局依赖关系可查、模块边界清晰、数据流向明确。

2. **T18的本质是"生产环节"而非"治理环节"**：
   - T18描述的YAML化实际上是"按域生产蓝图"的过程
   - 应该等业务域一个一个设计好、蓝图做好、代码做好后再生产
   - 不是现在做的治理工作，而是阶段8业务层建设时的生产工作

3. **未来生产流程**：
   ```
   业务域设计 → 域内依赖全景图设计 → 模块蓝图制作 → 代码实现
                                                        ↓
                                               按域导出蓝图（YAML或MD）
   ```

4. **蓝图格式倾向YAML**：Owner倾向于YAML格式，理由：
   - AI解析YAML无歧义（结构化字段）
   - 与现有规则体系一致（trae_XXX.yaml）
   - 程序可直接消费（yaml.load）
   - 字段明确性优于MD

5. **当前优先级**：先做阶段3数据治理（Phase A-I-E-C-B-F-K），T18推迟到阶段8业务层建设时按域生产。

**状态更新**：
- T18从"待Owner审批"改为"暂缓，转为阶段8生产环节"
- T18_implementation_plan.md保留作为未来生产环节的参考方案
- T18_design_state_yaml_assessment.md已删除（数据过时，边数预估230 vs 实际15295，差66倍）
- 实际数据已记录在T18_implementation_plan.md §0中

**未来重启条件**：
- 阶段8业务层建设启动
- 业务域设计完成，开始按域生产蓝图
- 届时重新评估蓝图格式（YAML vs MD）和拆分策略

---

## 总结

| 决策 | 推荐方案 | 实际实施 | 裁定状态 | 优先级 |
|------|---------|---------|---------|:---:|
| T6 事件类型体系 | 选项C: 注册表+Enum | 选项B: Enum类（任务治理域11事件） | ✅ 已裁定：交易链事件延后阶段8（简化为4-5个）/ 注册表永不实施 / AsyncEventBus延后阶段2 | 中 |
| T7 三级配置结构 | 选项C: 混合结构 | 选项B: 按功能分目录 + 蓝图内联 | ✅ 已裁定：全局配置永不实施（当前）/ 域级配置永不实施 | 高 |
| T17 模块DOMAIN字段 | 选项B: 可选声明 | 选项B: 可选声明 | ✅ STEP 1-4已完成（STEP 5待阶段5后） | 中 |
| T18 依赖图真源裁定 | 选项B: 分层真源（设计态YAML化） | — | ⏸ 暂缓（转阶段8生产环节） | 低（暂缓） |

**裁定说明**（2026-06-22 客观架构师裁定）：
- T6 ✅ 已裁定：任务治理域事件已实施（选项B Enum类）。未实施部分裁定——交易链事件为真实需求但延后到阶段8业务层建设时实施（简化为4-5个业界标准事件，非原方案8个）；DomainEventRegistry 注册表永不实施（过度设计，违反"少一层抽象=少一个幻觉源"原则）；R1-2 AsyncEventBus 延后到阶段2 R1/R2升级时实施
- T7 ✅ 已裁定：蓝图内联配置✅ + config/按功能分目录✅ 已满足当前需求。未实施部分裁定——`config/global.yaml` 全局配置永不实施（当前阶段，单机单环境无需求）；`config/domains/` 域级配置永不实施（61个域配置文件=过度抽象，违反AI开发原则）。若阶段8业务层出现跨域配置共享需求再按需补充
- T17 ✅ 已完成核心实施（生成器支持[DOMAIN]字段+22个跨域文件已标注），STEP 5 是阶段5物理搬家后的清理工作
- T18 ⏸ 已有 Owner 讨论结论（2026-06-21），暂缓转为阶段8生产环节

**裁定依据**：量化社区实践（gs-quant 12事件/事件驱动回测标准4事件）+ 配置管理业界实践（AWS AppConfig/K8s ConfigMap）+ 氛围编程社区实践（Cursor/Claude Code 单一文本配置）+ 100% AI开发原则（一条规则>两条规则 / 少一层抽象=少一个幻觉源 / AI可读性优先）+ 项目实际约束（单机单环境部署 / 阶段4完成 / 业务层未启动）
