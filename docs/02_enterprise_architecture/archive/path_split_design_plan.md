# 路径拆分设计方案

> **任务编号**: DM-100257
> **生成会话**: session-20260619-257
> **数据来源**: `D:\ZephyrAlpha\data\databases\depgraph.db`（nodes 表 + domains 表，只读查询）
> **适用规则**: RULE-TEN 治理施工流程、RULE-ZERO 文件锁、MTH-006 根源分析
> **状态**: 设计态（未施工）

---

## 1. 概述

### 1.1 问题根源

`depgraph.db` 的 `domains` 表中，3 处 `ssot_path` 被多个 D-XXX 域共享（精确字符串重复），导致域归属判定歧义：任意一条 `file_path` 落在共享路径下时，无法机械判定其归属域。违反 SSoT（Single Source of Truth）原则——一个路径只能有一个权威域。

### 1.2 重复路径清单

| # | 重复 ssot_path | 共享域 | 域声明模块数（domains.current_modules） | DB 实际节点数（nodes 表） |
|---|---|---|---|---|
| 1 | `src/zephyr/data/` | D-DATA_GOV / D-DATA_SEC / D-MKT_DATA | 26 / 17 / 109 | 0 / 3 / 1 |
| 2 | `src/zephyr/integration/` | D-INTEGRATION / D-INTEGRATION-GATEWAY | 314 / 82 | 217 / 82 |
| 3 | `src/zephyr/signal/` | D-SIGNAL / D-SIGNAL_FUNDAMENTAL | 135 / 35 | 2 / 23 |

> **数据偏差说明**: `domains.current_modules` 为域声明值，`nodes` 表为已物化节点。`data/` 路径下声明 152 模块但仅物化 4 节点——多数模块尚未落盘或登记在兄弟包（`data_eng/`、`alt_data/`）。本方案以 `nodes` 表实际分布为迁移依据。

### 1.3 解决策略

每域分配唯一子目录路径，使 `ssot_path` 在 `domains` 表中两两不同。物理迁移已有节点 + 更新 import + 重新生成依赖图。三处独立施工，互不阻塞。

---

## 2. 现状分析

### 2.1 `src/zephyr/data/`（3 域共享）

#### 2.1.1 DB 节点分布（按 domain_id × 子目录交叉表）

| 子目录 / 文件 | D-DATA_GOV | D-DATA_SEC | D-MKT_DATA | 合计 |
|---|---:|---:|---:|---:|
| `persistence/` | 0 | 3 | 0 | 3 |
| `__init__.py`（根） | 0 | 0 | 1 | 1 |
| **合计** | **0** | **3** | **1** | **4** |

- D-DATA_GOV：0 节点（声明 26 模块，未物化到此路径）
- D-DATA_SEC：3 节点（`persistence/__init__.py`、`persistence/sqlite_schema.py`、`persistence/circuit_breaker_types.py`）
- D-MKT_DATA：1 节点（根 `__init__.py`）

#### 2.1.2 实际目录结构

```
D:\ZephyrAlpha\src\zephyr\data\
├── __init__.py
└── persistence\
    ├── __init__.py
    ├── circuit_breaker_types.py
    └── sqlite_schema.py
```

#### 2.1.3 受影响 import

| 搜索模式 | 命中文件数 | 命中语句数 |
|---|---:|---:|
| `from zephyr.data` \| `import zephyr.data` | 25 | 53 |
| `from zephyr.data.persistence` \| `import zephyr.data.persistence` | 1 | 2 |

> ** caveat**: `from zephyr.data` 正则会匹配兄弟包 `zephyr.data_eng` / `zephyr.data_sec`（"data" 为前缀）。25 文件中真正引用 `zephyr.data.*`（共享路径）的仅 `persistence` 子包相关，计 1 文件 2 处。其余命中指向兄弟独立包，不在本方案迁移范围。

---

### 2.2 `src/zephyr/integration/`（2 域共享）

#### 2.2.1 DB 节点分布（按 domain_id × 子目录交叉表）

| 子目录 / 文件 | D-INTEGRATION | D-INTEGRATION-GATEWAY | 合计 |
|---|---:|---:|---:|
| `shared_08/` | 153 | 0 | 153 |
| `vector_memory/` | 0 | 29 | 29 |
| `shared/` | 23 | 0 | 23 |
| `mcp/` | 0 | 20 | 20 |
| `model_profiler/` | 0 | 11 | 11 |
| `governance/` | 10 | 0 | 10 |
| `layer2_communication/` | 0 | 9 | 9 |
| `local_model/` | 0 | 6 | 6 |
| `layer1_discovery/` | 0 | 4 | 4 |
| `contracts/` | 3 | 0 | 3 |
| `budget_enforcer/` | 2 | 0 | 2 |
| `behavioral_admission/` | 0 | 2 | 2 |
| `layer3_coordination/` | 0 | 1 | 1 |
| 根级 `.py` 文件（19 个） | 19 | 0 | 19 |
| 单 `__init__.py` 子目录（api/core/infrastructure/models/services/_extensions） | 6 | 0 | 6 |
| **合计** | **217** | **82** | **299** |

**根级 19 个 `.py` 文件**（全部归属 D-INTEGRATION）：
`backpressure_types.py`、`circuit_breaker_manager.py`、`backpressure_manager.py`、`cost_tracker.py`、`ct_pipe_routing.py`、`dead_letter_queue.py`、`models.py`、`layer_router.py`、`llm_gateway.py`、`layer_consumer_registry.py`、`pipeline_lock.py`、`pipeline_agent_bridge.py`、`model_router.py`、`pipeline_roadmap.py`、`pipeline_orchestrator.py`、`preemption_manager.py`、`routing_plugins.py`、`__init__.py`、`__init___from_orches.py`、`ports.py`

#### 2.2.2 实际目录结构（关键子目录）

```
D:\ZephyrAlpha\src\zephyr\integration\
├── 19 个根级 .py（见上）
├── _extensions\        ├─ api\                  ├─ behavioral_admission\
├── budget_enforcer\    ├─ contracts\            ├─ core\
├── governance\         ├─ infrastructure\       ├─ layer1_discovery\
├── layer2_communication\ ├─ layer3_coordination\ ├─ local_model\
├── mcp\                ├─ model_profiler\       ├─ models\
├─ services\            ├─ shared\               ├─ shared_08\
└── vector_memory\
```

#### 2.2.3 受影响 import

| 搜索模式 | 命中文件数 | 命中语句数 |
|---|---:|---:|
| `from zephyr.integration` \| `import zephyr.integration` | 459 | 916 |

**Top 消费方**（按命中语句数）：`integration/shared/api_03/api_index.py`(26)、`tests/adversarial/test_task_system_red_team.py`(24)、`scripts/a2a_full_verification.py`(20)、`integration/pipeline_orchestrator.py`(16)、`tests/unit/pipeline/test_pipeline_core.py`(19)、`tests/llm_security/test_cross_module_integration_llm_security.py`(12)。

> **规模警示**: 916 处 import 涉及 459 文件，为本方案最高风险项。MUST 分阶段施工（见 §4）。

---

### 2.3 `src/zephyr/signal/`（2 域共享）

#### 2.3.1 DB 节点分布（按 domain_id × 子目录交叉表）

| 子目录 / 文件 | D-SIGNAL | D-SIGNAL_FUNDAMENTAL | 合计 |
|---|---:|---:|---:|
| `capital/` | 0 | 4 | 4 |
| `gen/` | 0 | 4 | 4 |
| `strategy/` | 0 | 4 | 4 |
| `combiner/` | 0 | 3 | 3 |
| `synth/` | 0 | 2 | 2 |
| `api/` | 0 | 1 | 1 |
| `core/` | 0 | 1 | 1 |
| `infrastructure/` | 0 | 1 | 1 |
| `services/` | 0 | 1 | 1 |
| `models/` | 0 | 1 | 1 |
| `_extensions/` | 0 | 1 | 1 |
| `pipeline.py`（根） | 1 | 0 | 1 |
| `__init__.py`（根） | 1 | 0 | 1 |
| **合计** | **2** | **23** | **25** |

- D-SIGNAL：仅 `pipeline.py` + `__init__.py`（2 节点）
- D-SIGNAL_FUNDAMENTAL：其余全部（23 节点）

#### 2.3.2 实际目录结构

```
D:\ZephyrAlpha\src\zephyr\signal\
├── __init__.py          ├─ pipeline.py
├── _extensions\         ├─ api\          ├─ capital\
├── combiner\            ├─ core\         ├─ gen\
├── infrastructure\      ├─ models\       ├─ services\
├── strategy\            ├─ synth\
```

#### 2.3.3 受影响 import

| 搜索模式 | 命中文件数 | 命中语句数 |
|---|---:|---:|
| `from zephyr.signal` \| `import zephyr.signal` | 23 | 36 |

---

## 3. 拆分方案

### 3.1 `src/zephyr/data/` → 三域分立

#### 3.1.1 域路径分配

| 域 | 新 ssot_path | 新物理根 |
|---|---|---|
| D-DATA_GOV | `src/zephyr/data/governance/` | `D:\ZephyrAlpha\src\zephyr\data\governance\` |
| D-DATA_SEC | `src/zephyr/data/security/` | `D:\ZephyrAlpha\src\zephyr\data\security\` |
| D-MKT_DATA | `src/zephyr/data/market/` | `D:\ZephyrAlpha\src\zephyr\data\market\` |

#### 3.1.2 文件迁移清单

| 源（相对 src/zephyr/） | 目标 | 归属域 | 节点数 |
|---|---|---|---:|
| `data/persistence/` | `data/security/persistence/` | D-DATA_SEC | 3 |
| `data/__init__.py` | `data/market/__init__.py`（迁出） | D-MKT_DATA | 1 |
| —（新建） | `data/governance/__init__.py` | D-DATA_GOV | 0（占位） |
| —（新建） | `data/__init__.py`（facade，re-export 三子包） | 共享包标记 | — |

#### 3.1.3 依赖图推演结果

| 检查项 | 结论 |
|---|---|
| 是否产生新循环依赖 | 否。`persistence/` 整体下移一层，内部 import 不变；跨域无下游消费者（仅 1 文件 2 处 import 命中） |
| 跨包违规增减 | 不变（向下移动，依赖方向不变） |
| 目标包蓝图 | D-DATA_GOV/D-DATA_SEC/D-MKT_DATA 均为 operational 域，MUST 在 `docs/03_modules/_domain_data/` 下确认对应蓝图存在 |

#### 3.1.4 import 影响清单

| 原 import | 新 import | 影响文件 |
|---|---|---|
| `from zephyr.data.persistence import X` | `from zephyr.data.security.persistence import X` | `D:\ZephyrAlpha\data\unregistered_modules_registry.md`（1 文件 2 处） |

> 其余 24 文件 51 处命中为兄弟包（`data_eng`/`alt_data`/`data_sec` 独立包），不在迁移范围。

---

### 3.2 `src/zephyr/integration/` → core / gateway 分立

#### 3.2.1 域路径分配

| 域 | 新 ssot_path | 新物理根 |
|---|---|---|
| D-INTEGRATION | `src/zephyr/integration/core/` | `D:\ZephyrAlpha\src\zephyr\integration\core\` |
| D-INTEGRATION-GATEWAY | `src/zephyr/integration/gateway/` | `D:\ZephyrAlpha\src\zephyr\integration\gateway\` |

#### 3.2.2 文件迁移清单

**D-INTEGRATION → `core/`**（217 节点）：

| 源（相对 src/zephyr/integration/） | 目标 | 节点数 |
|---|---|---:|
| `shared_08/` | `core/shared_08/` | 153 |
| `shared/` | `core/shared/` | 23 |
| `governance/` | `core/governance/` | 10 |
| `contracts/` | `core/contracts/` | 3 |
| `budget_enforcer/` | `core/budget_enforcer/` | 2 |
| `api/`、`core/`（已存在）、`infrastructure/`、`models/`、`services/`、`_extensions/` | `core/<同名>/`（已存在 `core/` 内容并入） | 6 |
| 19 个根级 `.py`（见 §2.2.1） | `core/<同名>.py` | 19 |

**D-INTEGRATION-GATEWAY → `gateway/`**（82 节点）：

| 源（相对 src/zephyr/integration/） | 目标 | 节点数 |
|---|---|---:|
| `vector_memory/` | `gateway/vector_memory/` | 29 |
| `mcp/` | `gateway/mcp/` | 20 |
| `model_profiler/` | `gateway/model_profiler/` | 11 |
| `layer2_communication/` | `gateway/layer2_communication/` | 9 |
| `local_model/` | `gateway/local_model/` | 6 |
| `layer1_discovery/` | `gateway/layer1_discovery/` | 4 |
| `behavioral_admission/` | `gateway/behavioral_admission/` | 2 |
| `layer3_coordination/` | `gateway/layer3_coordination/` | 1 |

**根级处理**：`integration/__init__.py` 改为 facade，re-export `core` 与 `gateway` 公共接口；`__init___from_orches.py` 迁入 `core/`。

#### 3.2.3 依赖图推演结果

| 检查项 | 结论 |
|---|---|
| 是否产生新循环依赖 | 否（前提）。迁移仅加一层路径前缀，跨域 import 方向不变。**前置 MUST**：施工前跑 `python scripts/governance/diagnose_depgraph.py` 确认 D-INTEGRATION ↔ D-INTEGRATION-GATEWAY 当前无双向 import 循环；若存在，属既有问题，MUST 先解环再迁移 |
| 跨包违规增减 | 不增。`core/` 与 `gateway/` 同属 `integration/` 父包，向下依赖方向不变 |
| `core/` 与 `gateway/` 互相 import | 允许 `gateway → core`（网关依赖基础契约）；禁止 `core → gateway`（基础层不依赖网关层）。施工后 MUST 用 depgraph 验证无 `core → gateway` 反向边 |
| 目标包蓝图 | D-INTEGRATION / D-INTEGRATION-GATEWAY 均为 operational，MUST 确认 `docs/03_modules/` 下蓝图 §4 文件清单同步更新 |

#### 3.2.4 import 影响清单

**变换规则**（机械替换）：

| 原 import 前缀 | 新 import 前缀 | 归属判定 |
|---|---|---|
| `from zephyr.integration.shared_08` | `from zephyr.integration.core.shared_08` | D-INTEGRATION |
| `from zephyr.integration.shared` | `from zephyr.integration.core.shared` | D-INTEGRATION |
| `from zephyr.integration.governance` | `from zephyr.integration.core.governance` | D-INTEGRATION |
| `from zephyr.integration.contracts` | `from zephyr.integration.core.contracts` | D-INTEGRATION |
| `from zephyr.integration.budget_enforcer` | `from zephyr.integration.core.budget_enforcer` | D-INTEGRATION |
| `from zephyr.integration.<根级模块名>` | `from zephyr.integration.core.<根级模块名>` | D-INTEGRATION（19 个根模块） |
| `from zephyr.integration.vector_memory` | `from zephyr.integration.gateway.vector_memory` | D-INTEGRATION-GATEWAY |
| `from zephyr.integration.mcp` | `from zephyr.integration.gateway.mcp` | D-INTEGRATION-GATEWAY |
| `from zephyr.integration.model_profiler` | `from zephyr.integration.gateway.model_profiler` | D-INTEGRATION-GATEWAY |
| `from zephyr.integration.layer2_communication` | `from zephyr.integration.gateway.layer2_communication` | D-INTEGRATION-GATEWAY |
| `from zephyr.integration.local_model` | `from zephyr.integration.gateway.local_model` | D-INTEGRATION-GATEWAY |
| `from zephyr.integration.layer1_discovery` | `from zephyr.integration.gateway.layer1_discovery` | D-INTEGRATION-GATEWAY |
| `from zephyr.integration.behavioral_admission` | `from zephyr.integration.gateway.behavioral_admission` | D-INTEGRATION-GATEWAY |
| `from zephyr.integration.layer3_coordination` | `from zephyr.integration.gateway.layer3_coordination` | D-INTEGRATION-GATEWAY |

**影响规模**：459 文件 / 916 处语句。MUST 用脚本批量替换 + 人工复核 diff。Top 消费方见 §2.2.3。

> **注意**：`from zephyr.integration.core` 与 `from zephyr.integration.gateway` 在迁移后为新前缀；迁移过程中 `integration/__init__.py` facade 可临时 re-export 旧路径以保持兼容，验证通过后移除 facade。

---

### 3.3 `src/zephyr/signal/` → technical / fundamental 分立

#### 3.3.1 域路径分配

| 域 | 新 ssot_path | 新物理根 |
|---|---|---|
| D-SIGNAL | `src/zephyr/signal/technical/` | `D:\ZephyrAlpha\src\zephyr\signal\technical\` |
| D-SIGNAL_FUNDAMENTAL | `src/zephyr/signal/fundamental/` | `D:\ZephyrAlpha\src\zephyr\signal\fundamental\` |

#### 3.3.2 文件迁移清单

**D-SIGNAL → `technical/`**（2 节点）：

| 源（相对 src/zephyr/signal/） | 目标 | 节点数 |
|---|---|---:|
| `pipeline.py` | `technical/pipeline.py` | 1 |
| `__init__.py` | `technical/__init__.py`（迁出） | 1 |

**D-SIGNAL_FUNDAMENTAL → `fundamental/`**（23 节点）：

| 源（相对 src/zephyr/signal/） | 目标 | 节点数 |
|---|---|---:|
| `capital/` | `fundamental/capital/` | 4 |
| `gen/` | `fundamental/gen/` | 4 |
| `strategy/` | `fundamental/strategy/` | 4 |
| `combiner/` | `fundamental/combiner/` | 3 |
| `synth/` | `fundamental/synth/` | 2 |
| `api/`、`core/`、`infrastructure/`、`services/`、`models/`、`_extensions/` | `fundamental/<同名>/` | 6 |

**根级处理**：新建 `signal/__init__.py` facade，re-export `technical` 与 `fundamental` 公共接口。

#### 3.3.3 依赖图推演结果

| 检查项 | 结论 |
|---|---|
| 是否产生新循环依赖 | 否。`technical/pipeline.py` 可能 import `fundamental/synth` 等（聚合调用），方向 `technical → fundamental` 单向；反向无 |
| 跨包违规增减 | 不增。同属 `signal/` 父包 |
| 目标包蓝图 | D-SIGNAL / D-SIGNAL_FUNDAMENTAL 均为 operational，MUST 确认蓝图 §4 同步 |

#### 3.3.4 import 影响清单

**变换规则**：

| 原 import 前缀 | 新 import 前缀 | 归属判定 |
|---|---|---|
| `from zephyr.signal.pipeline` | `from zephyr.signal.technical.pipeline` | D-SIGNAL |
| `from zephyr.signal.capital` | `from zephyr.signal.fundamental.capital` | D-SIGNAL_FUNDAMENTAL |
| `from zephyr.signal.gen` | `from zephyr.signal.fundamental.gen` | D-SIGNAL_FUNDAMENTAL |
| `from zephyr.signal.strategy` | `from zephyr.signal.fundamental.strategy` | D-SIGNAL_FUNDAMENTAL |
| `from zephyr.signal.combiner` | `from zephyr.signal.fundamental.combiner` | D-SIGNAL_FUNDAMENTAL |
| `from zephyr.signal.synth` | `from zephyr.signal.fundamental.synth` | D-SIGNAL_FUNDAMENTAL |
| `from zephyr.signal.api` / `.core` / `.infrastructure` / `.services` / `.models` / `._extensions` | `from zephyr.signal.fundamental.<同名>` | D-SIGNAL_FUNDAMENTAL |

**影响规模**：23 文件 / 36 处语句。

---

## 4. 执行顺序（RULE-TEN 治理施工流程）

### 4.1 总体顺序

按因果链从简到难、从低风险到高风险：

| 阶段 | 目标路径 | 风险 | 理由 |
|---|---|---|---|
| P1 | `signal/` | 低 | 36 处 import，2 域节点分布清晰（2 vs 23），无跨域循环风险 |
| P2 | `data/` | 低 | 仅 4 节点，1 文件 2 处 import；D-DATA_GOV 空目录占位 |
| P3 | `integration/` | 高 | 916 处 import / 459 文件，MUST 分子阶段 |

### 4.2 每阶段五步流程（RULE-TEN §15.1）

每个阶段（P1/P2/P3）独立执行以下五步：

```
STEP 1  依赖图推演
        python D:\ZephyrAlpha\scripts\governance\diagnose_depgraph.py
        → 确认目标两域间无双向 import 循环
        → 模拟迁移后依赖链（手工对照 §3.x.3 推演表）
STEP 2  蓝图归属
        Grep docs/03_modules/ 确认 D-XXX 域蓝图存在
        → 更新蓝图 §4 文件清单（新增子目录路径）
STEP 3  导入路径映射
        Grep 全项目受影响 import（见 §3.x.4）
        → 生成 sed/脚本替换清单（绝对路径列表）
STEP 4  执行操作
        4a. 获取文件锁（RULE-ZERO，逐文件 acquire）
        4b. 物理迁移（git mv 保留 history）
        4c. 批量替换 import（脚本 + 人工 diff 复核）
        4d. 更新 domains 表 ssot_path（SQL UPDATE，事务包裹）
        4e. 释放文件锁
STEP 5  验证（任一失败 → 回滚）
        python D:\ZephyrAlpha\scripts\governance\generate_project_depgraph.py --output-yaml D:\ZephyrAlpha\data\asset_index\project_entity_depgraph.yaml
        python D:\ZephyrAlpha\scripts\governance\diagnose_depgraph.py
        python D:\ZephyrAlpha\scripts\governance\generate_project_path_tree.py --write
        python D:\ZephyrAlpha\scripts\governance\audit_registration.py
        python -m pytest tests/ --collect-only -q
        python -c "import zephyr.signal; import zephyr.data; import zephyr.integration; print('OK')"
```

### 4.3 P3 `integration/` 子阶段拆分

P3 风险最高，MUST 分两子阶段：

| 子阶段 | 操作 | import 影响 | 验证门槛 |
|---|---|---|---|
| P3a | 迁移 D-INTEGRATION-GATEWAY → `gateway/`（82 节点 / 8 子目录） | ~250 处（按 82/299 占比估算） | 跑完 §4.2 STEP 5 全部验证 |
| P3b | 迁移 D-INTEGRATION → `core/`（217 节点 / 19 根文件 + 11 子目录） | ~660 处 | 跑完 §4.2 STEP 5 全部验证 |

> P3a 完成后，`integration/` 根下仅剩 D-INTEGRATION 内容，ssot_path 冲突已实质消除（D-INTEGRATION-GATEWAY 已有独立 `gateway/` 路径）。P3b 为对称性收尾，可在 P3a 验证稳定后择期执行。

### 4.4 domains 表更新 SQL（每阶段 STEP 4d）

```sql
-- P1: signal
UPDATE domains SET ssot_path='src/zephyr/signal/technical/' WHERE domain_id='D-SIGNAL';
UPDATE domains SET ssot_path='src/zephyr/signal/fundamental/' WHERE domain_id='D-SIGNAL_FUNDAMENTAL';

-- P2: data
UPDATE domains SET ssot_path='src/zephyr/data/governance/' WHERE domain_id='D-DATA_GOV';
UPDATE domains SET ssot_path='src/zephyr/data/security/' WHERE domain_id='D-DATA_SEC';
UPDATE domains SET ssot_path='src/zephyr/data/market/' WHERE domain_id='D-MKT_DATA';

-- P3: integration
UPDATE domains SET ssot_path='src/zephyr/integration/core/' WHERE domain_id='D-INTEGRATION';
UPDATE domains SET ssot_path='src/zephyr/integration/gateway/' WHERE domain_id='D-INTEGRATION-GATEWAY';
```

> SQL MUST 在事务中执行，配合文件迁移原子提交。本方案为设计态，不执行 SQL。

---

## 5. 风险与回滚

### 5.1 风险矩阵

| 风险 | 等级 | 触发条件 | 缓解措施 |
|---|---|---|---|
| import 替换遗漏 | 高（P3） | 脚本未覆盖动态 import / 字符串拼接路径 | Grep 二次扫描 + `pytest --collect-only` + 关键模块 import 自测 |
| 既有循环依赖暴露 | 中 | D-INTEGRATION ↔ D-INTEGRATION-GATEWAY 已有双向 import | STEP 1 前置 depgraph 诊断；若有，先解环（MTH-006 根因） |
| 蓝图 §4 漂移 | 中 | 物理迁移后蓝图文件清单未同步 | STEP 2 强制更新蓝图 + `check_contract_code_drift.py` |
| `__init__.py` facade 残留 | 低 | 兼容期 facade 未及时移除 | 每阶段验证后移除 facade，Grep 确认无 `from zephyr.X import` 走 facade |
| domains 表与文件不一致 | 中 | SQL 提交但文件迁移失败 | 事务包裹 + 文件迁移先于 SQL 提交 |
| 兄弟包误伤（data） | 低 | `from zephyr.data` 正则误匹配 `data_eng` 等 | 替换脚本 MUST 用完整路径前缀匹配，禁止短前缀 |

### 5.2 回滚方案

每阶段独立回滚，互不影响：

| 阶段 | 回滚操作 |
|---|---|
| 文件迁移 | `git mv` 反向移动（保留 history）；或 `git checkout -- <path>` 恢复 |
| import 替换 | `git checkout -- <受影响文件>` 恢复 |
| domains 表 | `UPDATE domains SET ssot_path='<原值>'` 反向 SQL |
| depgraph | 重新跑 `generate_project_depgraph.py` 覆盖回滚后状态 |
| 路径树 | `generate_project_path_tree.py --write` 重生成 |

**回滚前置检查**（RULE-回滚系统）：

```
python D:\ZephyrAlpha\scripts\rollback.py preflight
→ CLEAN → 执行回滚
→ FAIL → 禁止回滚，先解决阻断项
```

**回滚触发条件**：§4.2 STEP 5 任一验证命令 `exit ≠ 0`，立即回滚当前阶段，禁止进入下一阶段。

### 5.3 完成验收标准

| 验收项 | 判定方式 |
|---|---|
| 3 处 ssot_path 无重复 | `SELECT ssot_path, COUNT(*) FROM domains GROUP BY ssot_path HAVING COUNT(*)>1` 返回空 |
| 每域唯一子目录 | `domains.ssot_path` 两两不同，且物理目录存在 |
| import 全部更新 | Grep `from zephyr.data.persistence`（旧路径）等返回 0 命中 |
| 依赖图无新循环 | `diagnose_depgraph.py` exit 0 |
| 测试收集通过 | `pytest --collect-only -q` exit 0 |
| 关键模块可导入 | `python -c "import zephyr.signal; import zephyr.data; import zephyr.integration"` exit 0 |
| 蓝图同步 | 蓝图 §4 文件清单与物理路径一致（`check_contract_code_drift.py` exit 0） |

---

## 6. 附录

### 6.1 数据采集脚本

- `C:\Users\fanzi\AppData\Local\Temp\临时工作区\query_depgraph_paths.py`（nodes 表结构 + 域分布查询）
- `C:\Users\fanzi\AppData\Local\Temp\临时工作区\query_depgraph_crosstab.py`（子目录 × 域交叉表）

### 6.2 关键数据快照（2026-06-19）

| 路径 | 域 | nodes 表节点数 | domains.current_modules |
|---|---|---:|---:|
| `src/zephyr/data/` | D-DATA_GOV | 0 | 26 |
| `src/zephyr/data/` | D-DATA_SEC | 3 | 17 |
| `src/zephyr/data/` | D-MKT_DATA | 1 | 109 |
| `src/zephyr/integration/` | D-INTEGRATION | 217 | 314 |
| `src/zephyr/integration/` | D-INTEGRATION-GATEWAY | 82 | 82 |
| `src/zephyr/signal/` | D-SIGNAL | 2 | 135 |
| `src/zephyr/signal/` | D-SIGNAL_FUNDAMENTAL | 23 | 35 |

### 6.3 引用规则

| 规则 | 适用章节 |
|---|---|
| RULE-TEN（治理施工流程） | §4 全文 |
| RULE-ZERO（文件锁协议） | §4.2 STEP 4a/4e |
| RULE-ONE（原子写入） | §4.2 STEP 4d SQL 事务 |
| MTH-006（根源分析） | §1.1 问题根源 |
| 防幻觉 #17（跨文件影响检查） | §3.x.4 import 影响清单 |
| 极简产出标准 §10 | 全文表格化 |
