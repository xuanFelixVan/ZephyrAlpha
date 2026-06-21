---
module_id: GOV-036-ARCH-DISCUSSION
doc_type: architecture_discussion
status: Active
version: 2.6.0
created: '2026-06-12'
last_updated: '2026-06-19'
owner: human
purpose: 记录架构升级深度讨论的完整上下文、决策和待定项
anti_hallucination: 本文件消除所有二元模糊地带，每个概念只有一个定义、一个归属、一个数字
---

# 架构升级深度讨论记录

> **文档责任范围**：本文档是架构升级项目的**导航图**。进来一看就知道——项目在干嘛、走到哪了、关键决策是什么、下一步做什么。
> **包含**：项目背景、架构设计上下文、重大决策（折叠摘要）、进展追踪、方法论（可反复用）。
> **不包含**：依赖与架构全景图能力定位（见 依赖与架构全景图能力定位书.md）、具体问题清单和修复步骤（见 depgraph\_issue\_registry.md）。
> **生命周期**：施工细节记录在独立文档中，施工完成后删除。本文档只保留方法论和决策。

> 本文件是架构升级讨论的唯一记录点。
> 反幻觉原则：每个概念只有一个定义、一个归属、一个数字。不存在"或""待选""两种都可以"。

> **当前执行状态（2026-06-18 更新）**：
>
> - 阶段0 STEP 0a-0c：部分待执行（ide\_health\_service 重建 + 阶段A安全网卡 + 独立修复卡）
> - 阶段1 STEP 1-2：已完成✅（架构裁定 + 数据库设计）
> - 阶段1 STEP 3：CI/CD 未开始
> - 阶段3 Phase H (生成器9个Bug修复 H1-H9): ✅ 已应用，重跑验证通过（2026-06-16）
> - 阶段3 Phase J (Schema偏差修复 J1-J4): ✅ 已应用（2026-06-16）
> - 阶段3 Phase G (G1 设计态加载源修复): ✅ 已完成（DM-3012 扩展 load\_design\_state\_from\_db 加载 edges+arch）
> - 阶段3 Phase G3/G4 (标记解析): ✅ 随 P0-3 生成器升级完成
> - **阶段3 七批次施工计划（§5.4 P0-1到P0-7）：✅ 全部完成（2026-06-18）**
>   - P0-1 Schema 迁移：✅（nodes 41列, edges 23列, arch\_directory\_tree 11列）
>   - P0-2 apply\_depgraph.py 扩展：✅（4个新命令齐全）
>   - P0-3 生成器升级：✅（12步流程，DM-3002\~3004, DM-3011\~3013 修复 9 项不符合项）
>   - P0-4 audit\_domain\_nodes.py 升级：✅（4类检测，DM-3005\~3009 修复 5 项不符合项）
>   - P0-5 dep\_cycles 视图 + 数据修复：✅（视图存在，8行循环依赖数据）
>   - P0-6 Schema v5 迁移：✅（9新表+4表扩展+27只读触发器+16 CHECK触发器）
>   - P0-7 YAML→DB 同步：✅（DM-3010 修复 sync\_all except块）
> - **17项不符合项全部处置完毕**（12项修复 + 5项规格过时），详见 生成器与全景图不符合项清单.md V2.1
> - depgraph.db 数据质量：重复路径 0 / 空路径 0 / 假blueprint\_id 0
> - 节点 8,746（运营态 6,637 + 设计态 2,109）/ 边 8,229 / 域 61 / 表 25（24业务+1系统 \_schema\_version）
> - arch\_constraints 表已扩展 violation\_status/details/detected\_at 字段（DB-02 已修复，DM-3001）
> - **全景图和生成器已完全符合能力定位书 V5.4 规格**

***

## 〇、架构层级（讨论框架）

> 所有讨论内容必须定位在以下层级中。上层决定下层，下层不能反过来影响上层。

```
L0  业务需求（能力定位书）          ← WHAT：系统必须做什么
    ↓ 决定
L1  域架构（39平铺域→模块）         ← WHERE：模块归属哪个域
    ↓ 决定
L2  技术架构（R1-R8）              ← HOW：模块怎么运行/通信/存储
    ↓ 决定
L3  数据架构（DuckDB/SQLite/数据流）← DATA：数据怎么存/怎么流
    ↓ 决定
L4  物理架构（目录/文件/磁盘）      ← DISK：文件放哪个盘哪个路径
    ↓ 生成
L5  depgraph/全景图                ← DOC：以上所有层的表现形式
```

**当前状态**：L1域架构已裁定（39平铺域，§2.1），L2-L5讨论基于L1展开。

**讨论内容层级归属**：

| 内容         |   层级   | 依赖    |
| ---------- | :----: | ----- |
| 能力定位书45能力  |   L0   | 无     |
| 39平铺域定义    | **L1** | L0    |
| D1-D78决策   |  L2-L4 | L1    |
| R1-R8升级方案  |   L2   | L1    |
| 数据架构设计     |   L3   | L1+L2 |
| 6个盲点       |  L3-L4 | L1    |
| depgraph存储 |   L5   | L1-L4 |
| 场外文件提取     |  L1→L5 | L1    |

**结论**：L1域架构是当前最高优先级，必须先定。

***

## 一、需求定义

### 1.1 核心需求来源

需求真源：`D:\临时工作区\能力定位书.md` v1.9.9

**一句话**：99% AI驱动的量化财富复利引擎，代码生成100%/运维99%/交易决策自主执行>90%。

### 1.2 硬边界约束（5条，不可改变）

| 约束        | 核心限制    | 关键参数                                                        |
| --------- | ------- | ----------------------------------------------------------- |
| 约束一：人力    | 单人+AI   | 1人开发+AI；代码100%AI生成                                          |
| 约束二：硬件    | 单台PC    | i7-12700KF/RTX3090 24GB/64GB RAM/D:731GB+E:931GB SSD/30Mbps |
| 约束三：资金与接口 | AUM 50万 | miniQMT Tick=3秒/下单10笔/秒；iFind QPS=20                        |
| 约束四：交易规则  | T+1     | 主板±10%/科创±20%/ST±5%                                         |
| 约束五：运维容灾  | 单机      | 交易时段RTO<5分钟；持仓RPO=0                                         |

> 约束六"AI原生"已降级为架构决策，不是硬边界。

### 1.3 实时计算上限（从硬边界推导）

| 维度     | 硬边界限制           | 推导上限            | 当前需求            |    余量    |
| ------ | --------------- | --------------- | --------------- | :------: |
| Tick频率 | miniQMT 3秒/次    | 1,667 ticks/sec | 1,667 ticks/sec | 0（外部天花板） |
| 下单速率   | miniQMT 10笔/秒   | 10笔/秒           | <1笔/秒           |    10x   |
| CPU    | i7-12700KF 20线程 | 交易核心25-35%      | 因子计算            |   2-3x   |
| 内存     | 64GB DDR4       | \~25GB需求        | 交易+AI+OS        |   2.5x   |
| GPU    | RTX3090 24GB    | \~10GB需求        | LLM+Embedding   |   2.4x   |
| 磁盘     | D+E=391GB剩余     | 低成本扩容           | 1.94TB需求        |  扩容即可解决  |
| 网络     | 30Mbps          | 盘前批量+盘中实时       | 勉强够             |   \~1x   |

**结论：CPU/内存/GPU全部充裕。磁盘低成本扩容即可。miniQMT 3秒Tick是延迟天花板。**

### 1.4 核心概念定义（唯一真源，禁止歧义）

| 概念             | 唯一定义                   |     当前值     | 注册表                     |
| -------------- | ---------------------- | :---------: | ----------------------- |
| 模块(module)     | 蓝图级代码单元，拥有唯一module\_id |    **60**   | module-registry.yaml    |
| 蓝图(blueprint)  | 模块的设计文档，1:1对应模块        |    **60**   | blueprint-registry.yaml |
| 子域功能组件         | 子域内的功能计数（不是模块）         |   **514**   | panorama.yaml           |
| .py文件          | 磁盘上的Python源文件          | **\~1,300** | 文件系统                    |
| 能力(capability) | 能力定位书定义的业务功能           |    **45**   | 能力定位书                   |

> **514不是模块数**。514是子域功能组件计数。模块数=60。扩缩推算基于模块数60。

### 1.5 规模目标（唯一数字，无范围）

| 指标    |    当前   |   实现目标   |    设计上限   |
| ----- | :-----: | :------: | :-------: |
| 模块数   |    60   |   1,500  | **3,000** |
| 蓝图数   |    60   |   1,000  | **2,000** |
| .py文件 | \~1,300 | \~20,000 |  \~40,000 |
| 门禁数   |    73   |    200   |    300    |
| 注册表   |    30   |    50    |     80    |

> 项目总容量无固定上限（总容量=域数×单域上限，见 trae_055 ARCH-CAP-007）。域数可无限拓展（抽屉式扩展，新增域只 INSERT domains 表）。实际约束是硬件资源（64GB 内存可支撑 10万+ 节点）+ AI 可维护性（单域 ≤200，见 ARCH-CAP-002）。1500 是下限（项目完整后预计 1500+ 模块）。
> 架构按实现目标交付，总容量随域数增长自动扩展。

### 1.6 磁盘容量计算

| 数据类型             |    10年存储(DuckDB 7x压缩)    |
| ---------------- | :----------------------: |
| Tick数据(5000股×3秒) |         1,730 GB         |
| K线数据             |           20 GB          |
| 因子数据             |           50 GB          |
| 订单/成交/持仓         |           10 GB          |
| 基本面/另类/审计/系统     |          180 GB          |
| **总计**           | **\~1,990 GB ≈ 1.94 TB** |

**磁盘扩容裁定**：分层SSD+HDD。近3年Tick存SSD(\~720GB)，3-10年Tick存外置HDD(\~1.2TB)。成本\~500元。

### 1.7 业务能力需求（45项）

架构必须支撑全部45项能力。不存在"只支撑P0不支撑P2"的架构。优先级仅影响实现顺序，不影响架构设计。

| 能力数 | 说明                                                                                                                               |
| :-: | -------------------------------------------------------------------------------------------------------------------------------- |
|  13 | 数据接入/交易执行/回测/风控/预案/因子工厂/信号工厂/策略工厂/自治进化/自治运维/因子管线/决策可解释/AI协作                                                                      |
|  27 | 报告归因/资金行为/做T/外部指令/大盘预测/知识图谱/交易运营/通知/数据质量/基建优化/知识进化/质量保障/执行优化/资金曲线/过拟合防护/主力行为/庄家行为/群体博弈/黑天鹅/跨市场/压力测试/拥挤度/执行质量/策略容量/模型工厂/审计合规/成本治理 |
|  5  | 多账户/微信互动/元级迭代/全球扩展/成本治理                                                                                                          |

### 1.8 质量属性优先级

正确性=安全性=合规性 > 延迟 > 可用性 > 可扩展性=可观测性=可维护性

> 推导方法论：硬边界→上限，需求→下限，推导架构。

***

## 二、架构分类体系裁定

### 2.1 唯一分类体系：39域

**裁定：39域是唯一物理分类体系。14层逻辑层(L00-L13)取消作为并行分类，降级为域属性。**

| 裁定项            | 结论                    | 理由                    |
| -------------- | --------------------- | --------------------- |
| 14层 vs 39域     | **39域唯一**             | 两个并行分类=AI每次判断用哪个=幻觉温床 |
| 14层信息保留方式      | 作为域的`logical_layer`属性 | 属性不是分类，不产生二元性         |
| L00-L13层YAML文件 | 废弃，信息合并入panorama域定义   | 避免SSoT分裂              |

> 39域=场外30域+膨胀域拆分(D-SIGNAL→4域, D-DATA→4域, D-SIMULATION→4域)。详见§17.6。

```yaml
# 唯一分类方式：按域找模块
D-FACTOR:
  logical_layer: L02        # 属性，不是分类
  ssot_path: src/zephyr/factor/
  parent_domain: data
  current_modules: 12
  max_modules: 80
```

> AI找模块只有一条路：按域找。层信息只在需要理解数据流向时才看。

### 2.2 命名标准化裁定

**全项目统一下划线(snake\_case)。一条规则，零例外，AI零歧义。**

| 对象                   | 命名规则              | 变更                  |
| -------------------- | ----------------- | ------------------- |
| Python源文件            | **snake\_case**   | 不变(PEP 8)           |
| src/zephyr/ 目录       | **snake\_case**   | 不变                  |
| docs/03\_modules/ 前缀 | **`_domain_xxx`** | 从`_domain-xxx`改为下划线 |
| 文档文件                 | **snake\_case**   | 从kebab-case改为下划线    |
| config/ 文件           | **snake\_case**   | 统一                  |
| 所有目录名                | **snake\_case**   | 统一                  |

> 理由：100% AI开发项目，一条规则>两条规则。AI不需要判断"这个文件用哪个规则"。
> GOV-DOC-003 trae\_028.yaml 需同步更新此裁定。
> ✅ **2026-06-19 已落地**：trae\_028.yaml 已升级为命名规则唯一真源(gov\_doc\_003\_naming\_ssot)，汇总trae\_010/022/030/042命名规则，统一全项目snake\_case，消除12个命名规则矛盾点(C-1\~C-12)。域ID保持大写D-XXX\_YYY(标识符不是文件名)。

### 2.3 21个未映射目录裁定

**21个未映射目录是`src/zephyr/`下有代码但无子域定义的物理目录，不是场外文件。**

| 旧目录                | 迁入域                   | 目标路径                                   |
| ------------------ | --------------------- | -------------------------------------- |
| execution/         | D-EX-CORE             | src/zephyr/ex\_core/（合并）               |
| factor/            | D-FACTOR              | src/zephyr/factor/（保留，补域定义）            |
| signal/            | D-SIGNAL              | src/zephyr/signal/（保留，补域定义）            |
| signal\_ashare/    | D-SIGNAL              | src/zephyr/signal/ashare/              |
| signal\_quality/   | D-SIGNAL              | src/zephyr/signal/quality/             |
| risk/              | D-RISK                | src/zephyr/risk/（保留，补域定义）              |
| portfolio/         | D-PF-CORE             | src/zephyr/pf\_core/（合并）               |
| pf\_alloc/         | D-PF-ALLOC            | src/zephyr/pf\_alloc/（保留，补域定义）         |
| pf\_core/          | D-PF-CORE             | src/zephyr/pf\_core/（保留，补域定义）          |
| reporting/         | D-REPORTING           | src/zephyr/reporting/（保留，补域定义）         |
| research/          | D-RESEARCH            | src/zephyr/research/（保留，补域定义）          |
| simulation/        | D-SIMULATION          | src/zephyr/simulation/（保留，补域定义）        |
| ml\_train/         | D-ML-TRAIN            | src/zephyr/ml\_train/（保留，补域定义）         |
| cross\_asset/      | D-CROSS-ASSET         | src/zephyr/cross\_asset/（保留，补域定义）      |
| frontend/          | D-FRONTEND            | src/zephyr/frontend/（保留，补域定义）          |
| compliance/        | D-COMPLIANCE          | src/zephyr/compliance/（保留，补域定义）        |
| autonomy\_perm/    | D-AUTONOMY-PERM       | src/zephyr/autonomy\_perm/（保留，补域定义）    |
| semantic\_auditor/ | D-GOV-SEMANTIC\_AUDIT | src/zephyr/governance/semantic\_audit/ |
| integration/       | D-INTEGRATION         | src/zephyr/integration/（保留，补域定义）       |
| trading/           | D-EX-CORE             | src/zephyr/ex\_core/trading/           |
| ex\_core/          | D-EX-CORE             | src/zephyr/ex\_core/（保留，补域定义）          |

***

## 三、各位置容量与效率审查

### 3.1 抽屉架构（src/zephyr/ 域路径）

**结论：当前 max=1,780，不能支撑3,000模块。需扩容。**

| 问题                         | 现状                     | 改造方向                     |
| -------------------------- | ---------------------- | ------------------------ |
| 逻辑容量不足                     | 39域 max=1,780          | 扩容现有域max\_modules到3,000+ |
| 21个物理目录无子域映射               | 见§2.3裁定                | 迁移到已有子域路径                |
| data域4子域ssot\_path指向不存在的目录 | `src/zephyr/data/` 不存在 | 创建目录                     |
| 命名不一致                      | 连字符/下划线混用              | 统一下划线（§2.2裁定）            |

**子域扩容裁定**：扩容现有域max\_modules，不新增子域。39域足够覆盖所有功能，只需调大max值。

### 3.2 数据库层

**结论：9个SQLite合并为1个governance.db，新建depgraph.db，DuckDB用于业务数据。**

| 裁定项          | 结论                                                             |
| ------------ | -------------------------------------------------------------- |
| SQLite合并     | **9个SQLite→1个governance.db**(D51) + **新建depgraph.db**(依赖图+全景图) |
| DuckDB       | **1个**：market.duckdb(业务数据：Tick/K线/因子/订单/持仓/风控)                 |
| 合约模型         | dataclass → Pydantic BaseModel                                 |
| DuckDB迁移框架   | 参照sqlite\_schema.py建版本化迁移                                      |
| OLAPEngine去重 | 保留data/persistence版，删除infra/runtime\_integration版              |

### 3.3 depgraph（依赖全景图）

**结论：YAML→SQLite，增量计算替代O(N²)。**

| 裁定项   | 结论                                            |
| ----- | --------------------------------------------- |
| 存储引擎  | **SQLite**（depgraph.db）。治理元数据不是时序数据，SQLite更合适 |
| 与全景图  | **同库**（depgraph.db）。都是治理元数据，查询模式相同            |
| 投影算法  | 增量计算+按需查询，废弃O(N²)全量投影                         |
| 生成物格式 | **MD格式**依赖关系图（人类+AI可读），不生成YAML                |
| 设计态   | 数据库是唯一真源，无YAML手动编辑                            |

### 3.4 架构全景图

**结论：拆分为汇总+按域索引，数据库为真源，生成MD格式依赖关系图。**

| 裁定项   | 结论                        |
| ----- | ------------------------- |
| 存储    | depgraph.db中的域表+子域表+容量表   |
| 冷启动   | 只读汇总元数据(<100KB)           |
| 按需加载  | SQL查询指定域的详情               |
| 生成物格式 | **MD格式**（人类+AI可读），不生成YAML |
| YAML  | 废弃，数据库是唯一真源               |

### 3.5 数据目录（data/）

**裁定结构**：

```
data/
  governance/        # governance.db（治理元数据+任务+成本）
  depgraph/          # depgraph.db（依赖图+全景图+设计态）
  market/            # market.duckdb（业务时序数据）
  warehouse/         # 冷归档（Parquet）
  models/            # 嵌入模型（从根目录models/迁入）
  security_baselines/ # 安全基线（加TTL自动清理）
  backups/           # 备份
```

### 3.6 测试目录（tests/）

**裁定**：按域分组 `tests/_domain_xxx/`，与 src/zephyr/ 域路径对齐。

### 3.7 门禁系统

**裁定**：增量门禁——只扫描变更文件影响的门禁，非全量。

### 3.8 CI/CD

**裁定**：GitHub Actions + pre-commit hooks，P0优先级，可与阶段B并行启动。

***

## 四、8层架构升级方案

### 4.1 R1 运行时（同步→async）

**现状**：核心调度链100%同步。Conductor.plan\_cycle()→AutoPilot.run\_cycle()→claim\_next()→dispatch()全链路def，无async。PipelineOrchestrator M1-M11串行for循环+time.sleep()重试。EventBus publish()内同步调用所有handler，异常被except:pass吞掉。已有59个文件含async def，但全部在边缘模块（MCP Server/漂移扫描/GPU共识/安全网关），未接入核心调度链。

**策略**：渐进式async化，不是重写。

| Phase | 内容                      | 依赖   | 风险        |
| ----- | ----------------------- | ---- | --------- |
| R1-1  | AsyncRuntime事件循环引导      | 无    | 低         |
| R1-2  | AsyncEventBus           | R1-1 | 中（双版本并存期） |
| R1-3  | PipelineOrchestrator并行化 | R1-2 | 中（竞态）     |
| R1-4  | Conductor async化        | R1-2 | 低         |

**R1风险与回滚**：

| 风险                           |  概率 |  影响 | 缓解                                  |
| ---------------------------- | :-: | :-: | ----------------------------------- |
| asyncio事件循环与threading.Lock死锁 |  中  |  高  | R1-1用run\_in\_executor桥接，不混用        |
| EventBus双版本并存导致事件丢失          |  低  |  高  | R1-2 SyncEventBus内部桥接到AsyncEventBus |
| PipelineOrchestrator并行化引入竞态  |  中  |  中  | 模块内部已有幂等性检查，外部加asyncio.Lock         |

**回滚**：每个Phase独立git分支，回滚=git revert。SyncEventBus保留到R1-4完成后才移除。

### 4.2 R2 持久化（零业务数据→DuckDB时序存储）

**现状**：SQLite 14张表全为治理元数据，零业务数据。DuckDB OLAPEngine已实现但仅读SQLite治理表。10+ dataclass合约模型（行情/订单/成交/持仓/风控）全部纯内存，无数据库表。duckdb/structlog/pyarrow未在pyproject.toml声明。

**策略**：DuckDB为核心，SQLite保留治理，不引入新数据库。

| Phase | 内容            | 依赖   | 风险                  |
| ----- | ------------- | ---- | ------------------- |
| R2-1  | 依赖补全+DuckDB服务 | 无    | 低                   |
| R2-2  | 业务Schema DDL  | R2-1 | 中（Schema设计影响全局）     |
| R2-3  | 写入管道(tick+K线) | R2-2 | 中（吞吐>2000ticks/sec） |
| R2-4  | Repository层   | R2-3 | 低                   |

**关键决策**：DuckDB为唯一业务数据库，不引入TimescaleDB/InfluxDB。

**R2风险与回滚**：

| 风险           |  概率 |  影响 | 缓解                   |
| ------------ | :-: | :-: | -------------------- |
| DuckDB单文件锁竞争 |  低  |  高  | WAL模式+单写入线程+批量APPEND |
| 3秒K线聚合延迟     |  中  |  中  | 异步聚合+内存缓存最近N根K线      |
| 数据文件膨胀       |  中  |  低  | Parquet冷归档+定期VACUUM  |

**回滚**：DDL版本化，回滚=删DuckDB文件+降级到纯内存。

### 4.3 R3 数据流（同步EventBus→async+行情管道）

**现状**：EventBus完全同步+内存，handler异常被吞。EventBusBackpressure有三级背压但deque无自动消费循环。realtime\_streaming.py三份相同副本仅4个常量。market\_data\_pipeline.py三份相同副本全是存根。零网络代码。

**策略**：基于R1 AsyncEventBus构建，不引入Kafka/Redis。

| Phase | 内容              | 依赖        | 风险       |
| ----- | --------------- | --------- | -------- |
| R3-1  | AsyncEventBus完善 | R1-2      | 低        |
| R3-2  | 行情摄入管道          | R2-3+R3-1 | 高（外部数据源） |
| R3-3  | K线聚合引擎          | R3-2      | 中        |
| R3-4  | 因子计算管道          | R3-3      | 中        |

**不引入Kafka/Redis的理由**：单进程架构→asyncio.Queue零序列化开销；5000股×3秒≈1667 ticks/sec→asyncio.Queue轻松支撑；Kafka/Redis需独立服务→与"本地优先"冲突；跨进程需求→ZeroMQ（R4-3可选）。

### 4.4 R4 通信（Protocol空壳→async实现）

**现状**：A2A五协议接口定义完整（Protocol+Pydantic+状态机），但传输层空壳。GovernanceAdapter是唯一实现（安全校验）。StreamingManager只做字符串切片。MessageRouter同步分发。

**策略**：先完善进程内async channel，跨进程用ZeroMQ可选。

| Phase | 内容           | 依赖   | 风险              |
| ----- | ------------ | ---- | --------------- |
| R4-1  | AsyncChannel | R1-2 | 低               |
| R4-2  | A2A传输实现      | R4-1 | 中               |
| R4-3  | ZeroMQ传输层    | R4-2 | 低（未来按需启用，接口已预留） |

### 4.5 R5 管线（AI任务管线→数据流管线，新建）

**现状**：PipelineOrchestrator是AI任务管线（M1-M11 LLM调用链），不是数据流管线。需要新建数据流管线框架，与M1-M11正交。

| Phase | 内容             | 依赖   | 风险 |
| ----- | -------------- | ---- | -- |
| R5-1  | DataPipeline框架 | R3   | 中  |
| R5-2  | 交易数据流管线        | R5-1 | 高  |
| R5-3  | 管线编排           | R5-2 | 中  |

### 4.6 R6 Agent（静态路由→交易Agent）

**现状**：6角色静态路由×10域能力矩阵，AgentOrchestrator是工具调用链编排（非任务编排）。Agent状态纯内存，无持久化。4个AgentOrchestrator副本。

| Phase | 内容          | 依赖   | 风险 |
| ----- | ----------- | ---- | -- |
| R6-1  | 交易Agent角色   | R4   | 中  |
| R6-2  | Agent状态持久化  | R6-1 | 低  |
| R6-3  | Agent生命周期管理 | R6-2 | 低  |

### 4.7 R7 安全（增量扩展，最成熟层）

**现状**：最成熟的层。LSG九层纵深防御完整，async scan\_input/output/agent\_action已实现。RBAC/ABAC/PermissionGuard均有实现。

| Phase | 内容    | 依赖 | 风险 |
| ----- | ----- | -- | -- |
| R7-1  | 交易安全层 | R6 | 低  |
| R7-2  | 数据安全  | R2 | 低  |

### 4.8 R8 基础设施（单容器→多服务）

**现状**：单容器Docker，docker-compose 4服务（zephyr-core+Prometheus+Grafana+Node Exporter）。无多进程编排。

| Phase | 内容                | 依赖     | 风险 |
| ----- | ----------------- | ------ | -- |
| R8-1  | 多服务docker-compose | R1+R2  | 中  |
| R8-2  | 进程管理              | R8-1   | 低  |
| R8-3  | CI/CD             | 无（可先行） | 低  |

***

## 五、升级工作流程

### 5.1 执行阶段（唯一编号）

```
阶段0：安全网+修bug
  STEP 0a: ide_health_service 重建（RULE-GUARDIAN 守护进程，写操作安全前提）
  STEP 0b: 阶段A安全网卡执行（DM-100000 备份 / DM-100001 路径修复 / DM-100002 验收门禁）
  STEP 0c: 独立修复卡执行（DM-408 旧类名 / DM-386 数据格式 / DM-90971 测试表头 / DM-418/419 命名规范 / SRC-100022 depgraph覆盖bug）
  （以上 STEP 0a-0c 状态：部分待执行，非全部已完成）

阶段1：确定整体架构 + 数据库设计 + CI/CD先行
  STEP 1: 确定整体架构（已完成✅：35域→39域裁定+命名标准化+14层降级）
  STEP 2: 设计数据库（已完成✅：3库DDL+迁移框架+数据迁移+v3对齐）
  STEP 3: CI/CD先行（未开始）

阶段2：R1/R2升级 + 数据库实施（未开始）

阶段3：depgraph/全景图迁移到数据库（深化施工已完成✅，数据治理待执行：YAML退役，depgraph.db是依赖图+全景图SSoT；规则内容SSoT为YAML文件，见D56）
  Phase H: 生成器9Bug修复（已完成✅ 2026-06-16）
  Phase J: Schema 4偏差修复（已完成✅ 2026-06-16）
  Phase G: 生成器G1修复（已完成✅ 2026-06-18）— 设计态加载源从YAML改为DB查询
           DM-3012 扩展 load_design_state_from_db 加载 edges+arch_directory_tree 设计态数据
  Phase G3/G4: [STABILITY]/[AI_AUTONOMY]标记解析（已完成✅ 随 P0-3 生成器升级完成）
  Phase A-I-E-C-B-F-K: 数据治理/质量/安全/性能/清理（待执行，10张卡可立即执行）
           注意：B1/B2 必须在 G3/G4 完成后执行（G3/G4 已完成，B1/B2 可执行）

阶段4：搬家对齐（一次性，对齐到阶段1确定的目标架构）+ 全量清洁
阶段5：R3/R4升级
阶段6：R5/R6升级 + depgraph设计态补全
阶段7：R7/R8 + 全量功能测试 + 规则文件格式升级
阶段7b：治理收敛期（治理瘦身 + ROI量化 + 运行时补强）—— 依赖阶段4搬家对齐+阶段7全量功能测试完成
阶段8：业务层建设（A股3秒数据/高速回测/实时决策）
```

> **执行顺序约束**：
>
> - 阶段0 STEP 0a（ide\_health\_service）是所有写操作的安全前提
> - 阶段3 Phase G 必须在 Phase A 之前（设计态数据保护）—— ✅ Phase G 已完成，Phase A 可执行
> - 阶段3 Phase G3/G4 必须在 Phase B1/B2 之前（标记解析是分级前提）—— ✅ G3/G4 已完成，B1/B2 可执行
> - 阶段3 Phase A-I-E-C-B-F-K 中，B1/B2 依赖 G3/G4 完成 —— ✅ 依赖已满足
> - **阶段3深化施工**：depgraph.db 七批次施工计划（P0-1到P0-7）见 §5.4，✅ 全部完成（2026-06-18）。Phase H/J/G/G3/G4 均已完成，P0-6/P0-7 已完成

### 5.2 阶段1详细步骤

> 阶段1 STEP 1-2 已完成✅，STEP 3 未开始。

**STEP 1 子项**（均已完成）：

- 39域扩容max\_modules到3,000+
- 21个未映射目录裁定归属（§2.3）
- 命名标准化（§2.2）
- 14层降级为域属性（§2.1）

**STEP 2 子项**（均已完成）：

- governance.db: 合并9个SQLite的治理数据
- depgraph.db: 依赖图+全景图+设计态
- market.duckdb: 业务时序数据Schema

**STEP 3 子项**（未开始，可与STEP 1-2并行）：

- GitHub Actions: lint + test + gate
- pre-commit hooks

### 5.3 20路AI分配

| 阶段  |  AI路数 | 负责               |
| --- | :---: | ---------------- |
| 阶段1 |  2-3  | 架构确定+数据库设计+CI/CD |
| 阶段2 |   4   | R1/R2/数据库实施      |
| 阶段3 |  1-2  | depgraph/全景图迁移   |
| 阶段4 | 10-15 | 搬家对齐+清洁（按域并行）    |
| 阶段5 |   3   | R3/R4            |
| 阶段6 |   4   | R5/R6            |
| 阶段7 |  4-6  | R7/R8/测试         |
| 阶段8 |   4   | 业务层              |

### 5.4 depgraph.db 七批次施工计划（V4.1扩展，详见能力定位书§22）—— ✅ 全部完成（2026-06-18）

> **核心原则**：施工必须按因果链从根到叶执行，不能按数量从大到小。规则表是"约束"，nodes/edges是"被约束的对象"，必须先有被约束的对象，约束才有意义。
> **当前状态**：七批次全部完成。17项不符合项全部处置完毕（12项修复+5项规格过时），全景图和生成器已完全符合能力定位书V5.4规格。

|    批次    | 施工内容                                                                                                                                                                                   | 前置条件                                         | 验收命令（详见能力定位书§23）                                                         |   状态  |
| :------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- | ------------------------------------------------------------------------ | :---: |
| **P0-1** | Schema 迁移：node\_id 改 INTEGER PK + edges 字段重命名(from\_node/to\_node→from\_node\_id/to\_node\_id) + edges 新增 dep\_maturity + arch\_directory\_tree 删 state 新增 node\_id 外键 + nodes 新增 5 字段 | 无                                            | 确认 nodes 36 列 + edges 20 列 + arch\_directory\_tree 11 列(无state有node\_id) | ✅ 已完成 |
| **P0-2** | apply\_depgraph.py 扩展：新增 --add-design-node / --add-design-edge / --transition-build-status / --remove-design-node                                                                      | P0-1 完成                                      | `apply_depgraph.py --help` 确认 4 命令                                       | ✅ 已完成 |
| **P0-3** | 生成器升级：12 步流程 + 异常处理 + 执行报告 + 循环检测 + blueprint\_id 校验                                                                                                                                   | P0-1 完成                                      | `generate_project_depgraph.py --dry-run`                                 | ✅ 已完成 |
| **P0-4** | audit\_domain\_nodes.py 升级：4 类检测 + 写入 arch\_constraints                                                                                                                                | P0-3 完成                                      | `audit_domain_nodes.py --check`                                          | ✅ 已完成 |
| **P0-5** | dep\_cycles 视图创建 + 数据修复（I7/I8）                                                                                                                                                         | P0-1 完成                                      | 确认 dep\_cycles 视图存在 + arch\_directory\_tree 无空 domain\_id                | ✅ 已完成 |
| **P0-6** | Schema v5 迁移：新建 9 表 + 扩展 4 表 + CHECK 约束 + 只读触发器                                                                                                                                        | **P0-3 完成**（规则表要和 nodes 表 JOIN，nodes 必须先有数据） | `migrate_schema_v5.py` + 确认 gates 表存在 + 18 个只读触发器                        | ✅ 已完成 |
| **P0-7** | YAML→DB 同步：14 项规则/契约/门禁/词汇表从 YAML 同步到 depgraph.db                                                                                                                                      | **P0-6 完成**（需要新表已建好）                         | `sync_yaml_to_depgraph.py` + 确认各表数据非零                                    | ✅ 已完成 |

**因果链**：

```
第一阶段：核心架构（必须先完成）
  P0-1（Schema 迁移）← 根因：所有脚本依赖 schema
    ↓
  P0-2（apply_depgraph.py）← 依赖 P0-1 的新字段
  P0-3（生成器升级）← 依赖 P0-1 的新字段，扫描代码填充 nodes/edges
    ↓
  P0-4（audit_domain_nodes.py）← 依赖 P0-3 的生成器输出
  P0-5（dep_cycles + 数据修复）← 依赖 P0-1 的 schema

第二阶段：规则统一合并（核心架构完成后才能做）
  P0-6（Schema v5 迁移）← 依赖 P0-1 schema + P0-3 生成器
    ↓
  P0-7（YAML→DB 同步）← 依赖 P0-6 的新表 + P0-3 的 nodes 数据
```

**禁止**：在 P0-3 生成器升级完成前，提前做 P0-6/P0-7。否则规则表同步进来，但 nodes 表是空的，所有 SQL JOIN 都返回空结果，规则约束形同虚设。

**与§5.1阶段的关系**：P0-1到P0-7属于§5.1阶段3（depgraph/全景图迁移到数据库）的深化施工计划。Phase H/J已完成的生成器Bug修复是P0-3的前置工作。Phase G（G1设计态加载源修复）属于P0-3的组成部分。**七批次已于2026-06-18全部完成。**

**回滚方案**：施工前 `cp data/databases/depgraph.db data/databases/depgraph.db.backup.V4.1`；失败回滚 `cp data/databases/depgraph.db.backup.V4.1 data/databases/depgraph.db` + `git checkout` 相关脚本。

***

## 六、数据架构设计

### 6.1 数据流全景

```
数据源（akshare/miniQMT/iFind）
  ↓ WebSocket/TCP
MarketDataIngestor（解码+校验+标准化）
  ↓ AsyncEventBus: MARKET_DATA
KlineAggregator（3秒窗口聚合）
  ↓ AsyncEventBus: KLINE_3S
FactorEngine（增量因子计算）
  ↓ AsyncEventBus: FACTOR_SIGNAL
StrategyEngine（策略评估+信号评分）
  ↓ AsyncEventBus: STRATEGY_SIGNAL
RiskEngine（风控检查+限额验证）
  ↓ AsyncEventBus: RISK_APPROVED
OrderGenerator（订单生成）
  ↓ AsyncEventBus: ORDER_CREATED
ExecutionEngine（订单执行+成交回报）
  ↓ AsyncEventBus: FILL_RECEIVED
PositionManager（持仓更新+盈亏计算）
```

### 6.2 数据库架构（3个数据库，职责清晰）

| 数据库           | 引擎     | 职责                          | 位置               |
| ------------- | ------ | --------------------------- | ---------------- |
| governance.db | SQLite | 治理元数据+任务+成本+审计              | data/governance/ |
| depgraph.db   | SQLite | 依赖图+全景图+设计态                 | data/depgraph/   |
| market.duckdb | DuckDB | 业务时序数据(Tick/K线/因子/订单/持仓/风控) | data/market/     |

### 6.3 market.duckdb 核心表设计约束

| 表               | 分区策略       | 写入模式     | 保留策略            |
| --------------- | ---------- | -------- | --------------- |
| tick\_data      | symbol + 月 | APPEND批量 | 近3年SSD/3-10年HDD |
| orders          | 无分区        | APPEND   | 7年              |
| fills           | 无分区        | APPEND   | 7年              |
| positions       | 无分区        | UPSERT   | 当前+历史快照         |
| risk\_snapshots | 无分区        | APPEND   | 3年              |

K线(kline\_3s/1m/5m/1d)从tick\_data聚合为视图，不建物理表。

### 6.4 数据分层（对应能力定位书约束十一）

| 层      | 时间范围    | 用途   | 存储位置            |
| ------ | ------- | ---- | --------------- |
| Layer0 | 1990-至今 | 压力测试 | Parquet冷归档(HDD) |
| Layer1 | 2005-至今 | 体制检测 | DuckDB(SSD)     |
| Layer2 | 2015-至今 | 8态预测 | DuckDB(SSD)     |
| Layer3 | 2020-至今 | 因子训练 | DuckDB(SSD)     |
| Layer4 | 近252天   | 在线训练 | DuckDB+内存缓存     |

### 6.5 回测引擎设计约束

- 数据源：DuckDB SQL查询（列式扫描+分区裁剪）
- 执行模型：模拟撮合（限价精确/市价下一根开盘价）
- 目标：5年日线<30秒，3秒级<5分钟
- 数据源选择：akshare（免费A股数据）+ miniQMT（盘中实时）+ iFind（基本面）

### 6.6 实时计算设计约束

- 事件驱动：AsyncEventBus
- 增量计算：只处理新数据
- 延迟预算：
  - 行情摄入→K线聚合：<100ms
  - K线→因子计算：<200ms
  - 因子→信号生成：<100ms
  - 信号→风控检查：<50ms
  - 风控→订单生成：<50ms
  - 总计：<500ms（远低于3秒K线周期）

***

## 七、depgraph/全景图存储改造

### 7.1 改造方案（已裁定，七批次深化施工已全部完成✅ 2026-06-18）

**结论：YAML→SQLite，增量计算替代O(N²)。基础迁移+七批次深化施工（P0-1到P0-7）全部完成。depgraph.db 是依赖图+全景图唯一真源（SSoT）。**

> 裁定内容见 §3.3。表设计约束见 §十八 DDL。七批次施工计划见 §5.4（全部已完成）。验收标准见能力定位书§23。
> 17项不符合项全部处置完毕（12项修复+5项规格过时），详见 生成器与全景图不符合项清单.md V2.1。

***

## 八、代码去重与物理路径归一化

### 8.1 重复文件裁定

| 文件                        | 副本数 | 保留位置              | 其余处理          |
| ------------------------- | :-: | ----------------- | ------------- |
| realtime\_streaming.py    |  3  | data/             | 删除，改re-export |
| market\_data\_pipeline.py |  3  | data/             | 删除，改re-export |
| event\_bus.py             |  2  | shared/           | 删除，改re-export |
| olap\_engine.py           |  2  | data/persistence/ | 删除，改re-export |
| agent\_orchestrator.py    |  4  | orchestration/    | 删除，改re-export |

> 命名标准化见 §2.2，21个未映射目录见 §2.3。

***

## 九、AI冷启动效率

**3000模块时冷启动方案**：

```
STEP 0: 读汇总元数据(<100KB) — 域列表+容量+健康状态
STEP 1: 按需加载域详情 — 只读当前任务涉及的域
STEP 2: depgraph按需查询 — SQL查询子图，非全量读取
STEP 3: 规则文件渐进加载 — 只加载相关规则子集
```

***

## 十、饱和式设计原则

**按硬件上限设计架构容量，实现时按需渐进。地基按50层打，先盖10层。**

| 类别      | 维度            | 设计上限/策略         |
| ------- | ------------- | --------------- |
| 必须饱和式设计 | 数据库Schema     | 3,000模块容量       |
| 必须饱和式设计 | depgraph存储    | SQLite+增量查询     |
| 必须饱和式设计 | 抽屉架构路径        | 39域max=3,000+   |
| 必须饱和式设计 | 配置分层          | 三级(全局/域/蓝图)     |
| 必须饱和式设计 | 事件类型体系        | 可扩展枚举           |
| 必须饱和式设计 | 分类体系          | 39域唯一           |
| 可渐进实现   | async runtime | sync\_bridge桥接  |
| 可渐进实现   | Agent角色       | 按P0能力逐步添加       |
| 可渐进实现   | 监控告警          | 先关键指标后全面覆盖      |
| 可渐进实现   | CI/CD         | 先lint后test后gate |

***

## 十一、6个架构级盲点

### 盲点A：models/ 目录——4.5GB

| 问题              | 裁定                                     |
| --------------- | -------------------------------------- |
| 无模型版本管理         | 建立models/registry.yaml，记录版本+路径+GPU显存需求 |
| 无按需加载机制         | 实现ModelManager，按需加载+LRU淘汰              |
| 未纳入Git LFS      | .gitignore排除大文件，首次运行自动下载               |
| 迁移到data/models/ | 与数据目录统一管理                              |

### 盲点B：data/ 目录——527K文件

| 问题                             | 裁定                    |
| ------------------------------ | --------------------- |
| security\_baselines/ 140+个JSON | 加TTL=30天自动清理，保留最新5个快照 |
| .runtime/ 146个报告               | 加TTL=7天自动清理           |
| 无热/温/冷分层                       | 按§3.5数据目录重构           |

### 盲点C：config/——18个扁平YAML

| 问题         | 裁定                                                                          |
| ---------- | --------------------------------------------------------------------------- |
| 1000蓝图不可管理 | 三级配置：全局(config/) + 域(config/domains/) + 蓝图(docs/03\_modules/\_domain\_xxx/) |

### 盲点D：infra/——监控空壳

| 问题         | 裁定                                  |
| ---------- | ----------------------------------- |
| 无告警规则      | 从capacity\_slo.yaml自动生成Prometheus规则 |
| 无dashboard | 按域生成Grafana dashboard模板             |

### 盲点E：日志/审计分散4处

| 问题                                                          | 裁定                                          |
| ----------------------------------------------------------- | ------------------------------------------- |
| logs/ + data/audit\_logs/ + .runtime/reports/ + \_journals/ | 统一到data/governance/audit\_logs/，其余改为符号链接或废弃 |

### 盲点F：根目录30+临时文件

| 问题              | 裁定               |
| --------------- | ---------------- |
| 22个\_temp\*.py等 | 全部清理，违反RULE-FIVE |

***

## 十二、老架构文档评估

**裁定：架构哲学保留，数据层刷新，14层降级为域属性。**

| 文件                          | 处置                           |
| --------------------------- | ---------------------------- |
| overview\.md                | 更新模块计数+域映射+删除14层独立分类         |
| architecture\_principles.md | 保留，小幅更新数字                    |
| data\_architecture.md       | 更新路径+实现状态                    |
| runtime\_planes.md          | 更新映射矩阵+模块数+14层→域属性           |
| technology\_architecture.md | 更新容量模型                       |
| layers/schema.yaml          | 废弃L00-L13独立层定义，信息合并入panorama |
| L00-L13层YAML                | 废弃，logical\_layer信息合并入域定义    |

***

## 十三、AI自进化架构

**架构级问题，不是工程细节。**

| 组件                                 | 层级  | 状态                        |
| ---------------------------------- | --- | ------------------------- |
| Feedback Loop Engine (MOD-INF-010) | 架构级 | 有蓝图+代码                    |
| Agent Spec (MOD-INF-019)           | 架构级 | 有蓝图+代码                    |
| SelfEvolutionFidelityGate          | 工程级 | 已实现(EchoTrap)             |
| AutoEvolution                      | 工程级 | 已实现(自动触发)                 |
| Agent架构图(三层指挥链)                    | 架构级 | `D:\临时工作区\架构图\Agent架构.md` |

**容量要求**：100 AI Session并发/500 findings/cycle/240 events/s。这决定了async runtime和EventBus的容量设计上限。

***

## 十四、顶层目录完整审计

| 目录                  |      大小 |  文件数 | 容量风险 | 裁定                              |
| ------------------- | ------: | ---: | :--: | ------------------------------- |
| data/               |  31.4GB | 527K |  🔴  | 重构为§3.5结构+TTL清理                 |
| models/             |   4.5GB |   90 |  🔴  | 迁入data/models/+版本管理             |
| docs/               |    74MB | 5.2K |  🟡  | 老架构文档按§12处置                     |
| tests/              |    69MB | 4.5K |  🟡  | 按域分组                            |
| src/                |    40MB | 6.7K |  🟡  | 21目录迁移按§2.3                     |
| scripts/            |    11MB | 2.0K |  🟢  | 保留                              |
| config/             |  0.16MB |   43 |  🔴  | 三级配置架构                          |
| infra/              |       0 |    4 |  🔴  | 从capacity\_slo生成告警规则            |
| logs/               |   1.4MB |    4 |  🟡  | 统一到data/governance/audit\_logs/ |
| \_journals/         |  0.65MB |   32 |  🟡  | 统一到data/governance/             |
| .runtime/           |  0.08MB |  146 |  🟡  | 加TTL=7天清理                       |
| .audit\_cache/      |   3.6MB |    5 |  🟡  | 增量更新策略                          |
| specs/              |  0.09MB |    4 |  🟡  | 与蓝图关联                           |
| architecture-model/ |  0.07MB |   19 |  🟡  | 废弃，信息合并入panorama                |
| frontend/           |  0.02MB |    8 |  🟡  | 数据聚合策略                          |
| .github/            |  0.01MB |    4 |  🟡  | CI增量触发                          |
| .zephyr/            |  0.04MB |    7 |  🟢  | 保留                              |
| .zephyr\_secure/    |       0 |    1 |  🟢  | 保留                              |
| reports/            |  0.06MB |    1 |  🟢  | 合并到data/                        |
| 根目录临时文件             | \~130KB |  30+ |  🟡  | 全部清理                            |

***

## 十五、已裁定决策清单

| #   | 决策项                                   | 裁定结论                                                                                                                   | 理由                                                                         |
| --- | ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| D1  | 模块容量目标                                | **无固定上限**（总容量=域数×单域上限，见 trae_055 ARCH-CAP-007）                                                                                                        | 抽屉式扩展，域数无限拓展                                                                      |
| D2  | 子域扩容方式                                | **扩现有max\_modules**                                                                                                    | 39域足够（D44-D46裁定膨胀域拆分），不新增子域                                                |
| D3  | DuckDB文件位置                            | **data/market/**                                                                                                       | 统一数据目录                                                                     |
| D4  | depgraph存储                            | **SQLite**                                                                                                             | 治理元数据不是时序数据                                                                |
| D5  | 全景图与depgraph                          | **同库(depgraph.db)**                                                                                                    | 查询模式相同                                                                     |
| D6  | 合约模型迁移                                | **dataclass→Pydantic**                                                                                                 | 序列化+校验                                                                     |
| D7  | 21个未映射目录                              | **迁移到已有子域路径**                                                                                                          | 不新建子域迁就旧目录                                                                 |
| D8  | 命名标准化                                 | **全项目统一下划线(snake\_case)**                                                                                              | 100%AI开发：一条规则>两条规则                                                         |
| D9  | 9个SQLite合并                            | **9个SQLite→1个governance.db(D51)+新建depgraph.db**                                                                        | 职责清晰                                                                       |
| D10 | CI/CD先行                               | **是**                                                                                                                  | 可与阶段B并行                                                                    |
| D11 | 跨进程通信                                 | **asyncio.Queue当前实现，接口预留ZeroMQ**                                                                                       | 接口抽象确保未来可切换                                                                |
| D12 | 数据目录重构                                | **§3.5结构**                                                                                                             | 统一管理                                                                       |
| D13 | 约束六                                   | **降级为架构决策**                                                                                                            | 不是硬边界                                                                      |
| D14 | models/存储                             | **迁入data/models/+版本管理**                                                                                                | 统一数据目录                                                                     |
| D15 | data/分层存储                             | **热/温/冷+TTL**                                                                                                          | 527K文件NTFS性能                                                               |
| D16 | config/分层                             | **三级(全局/域/蓝图)**                                                                                                        | 1000蓝图配置管理                                                                 |
| D17 | 可观测性                                  | **Prometheus+Grafana**                                                                                                 | 从capacity\_slo生成规则                                                         |
| D18 | 统一日志                                  | **集中到data/governance/audit\_logs/**                                                                                    | 审计合规                                                                       |
| D19 | 14层→39域                               | **14层降级为域属性**                                                                                                          | 消除并行分类=消除幻觉源                                                               |
| D20 | 磁盘扩容                                  | **分层SSD+HDD**                                                                                                          | 成本最低                                                                       |
| D21 | 分类体系                                  | **39域唯一**                                                                                                              | 消除二元性                                                                      |
| D22 | 3000模块上限                              | **业务合理上限，非硬件上限**                                                                                                       | 50万AUM单人+AI不需要更多                                                           |
| D23 | 业务数据库                                 | **DuckDB唯一，不分层多库**                                                                                                     | 回测效率最高(列式+向量化+分区裁剪)                                                        |
| D24 | 全景图/depgraph生成物                       | **MD格式，不生成YAML**                                                                                                       | 人类+AI可读                                                                    |
| D25 | P0/P1/P2优先级                           | **架构层面取消，全部必须支撑**                                                                                                      | 优先级仅影响实现顺序                                                                 |
| D26 | ZeroMQ                                | **现在不做，接口预留**                                                                                                          | A2ACommunicationProtocol确保可切换                                              |
| D27 | 全项目命名                                 | **统一下划线(snake\_case)**                                                                                                 | 一条规则零例外，AI零歧义                                                              |
| D28 | 场外文件提取                                | **先提取定顶层架构，再推进数据库设计**                                                                                                  | 场外文件是depgraph设计态核心数据源                                                      |
| D29 | 场外vs场内域体系                             | **全景图遗漏10个业务顶级域，需补录**                                                                                                  | 不是两套正交体系，是全景图录入不完整                                                         |
| D30 | 时序存储引擎                                | **DuckDB**                                                                                                             | 嵌入式+列式+已有基础，接受单进程限制(D23已裁定)                                                |
| D31 | 消息队列                                  | **asyncio.Queue**                                                                                                      | 单进程零序列化，不引入Kafka/Redis(D11已裁定)                                             |
| D32 | 合约模型                                  | **dataclass→Pydantic BaseModel**                                                                                       | 序列化+校验(D6已裁定)                                                              |
| D33 | 代码去重                                  | **保留规范位置，其余改re-export**                                                                                                | 搬家阶段统一处理(§8.1已裁定)                                                          |
| D34 | CI/CD                                 | **GitHub Actions，可与阶段B并行**                                                                                             | P0优先级(D10已裁定)                                                              |
| D35 | 回测数据源                                 | **akshare+miniQMT+iFind**                                                                                              | 免费+盘中+基本面三源                                                                |
| D36 | 部署架构                                  | **先单进程多线程，后多服务docker-compose**                                                                                         | 渐进式(D12已裁定)                                                                |
| D37 | D-DATA消歧                              | **场外D-DATA→D-MKT-DATA，全景保留D-DATA**                                                                                     | 同ID不同语义，必须消歧                                                               |
| D38 | 域体系修正                                 | **39个平铺域=场外30域+膨胀域拆分(D-SIGNAL/D-DATA/D-SIMULATION各拆4域)，无层级无子域**                                                        | 9父域+35子域是漂移，parent\_domain仅作分组属性                                           |
| D39 | 漂移根因                                  | **全景图把35平铺域错误重组为9+35层级，且遗漏业务域**                                                                                        | 迁移计划§5.7 R7评估已指出但未修复                                                       |
| D40 | 架构层级                                  | **6层：L0需求→L1域→L2技术→L3数据→L4物理→L5文档**                                                                                    | L1未定则L2-L5无法落地                                                             |
| D41 | 域结构                                   | **平铺，不做子域**                                                                                                            | 之前已讨论裁定，不增加层级深度                                                            |
| D42 | 35域来源                                 | **场外30域逐个提取模块，3个膨胀域各拆分为4域→39平铺域**                                                                                      | 不是9父域+35子域，是30+3×3拆分=39平铺域                                                 |
| D43 | 域容量标准                                 | **80-150默认/150-200高度耦合/>200硬上限**（见 trae_055 ARCH-CAP-002）                                                                                | AI上下文可导航极限，200是硬上限                                                         |
| D44 | 39平铺域方案（D45/D46追加拆分后）                 | **27业务域+12平台域，D-SIGNAL/D-DATA/D-SIMULATION各拆4域**                                                                       | 详见§17.6完整39平铺域方案                                                           |
| D45 | D-DATA拆分                              | **D-DATA(71)→D-MKT\_DATA/D-DATA\_ENG/D-DATA\_GOV/D-DATA\_SEC**                                                         | 11子域4层功能边界清晰，必须拆                                                           |
| D46 | D-SIMULATION拆分                        | **D-SIMULATION(71)→D-SIMULATION/D-BACKTEST/D-EXEC\_SIM/D-DIGITAL\_TWIN**                                               | 5功能集群，回测方法论最明显可独立                                                          |
| D47 | 工作流                                   | **数据库先行→depgraph入库→域裁定→搬家**                                                                                            | depgraph 157MB YAML无法高效裁定，入库后SQL毫秒级查询                                      |
| D48 | 平台域重新裁定                               | **平台域模块划分是漂移产物，需逐个重新裁定归属域**                                                                                            | 当前平台域是AI幻觉重组的结果                                                            |
| D49 | 数据库位置                                 | **全部放D盘**                                                                                                              | E盘仅剩55GB无增长空间，D盘335GB充裕                                                    |
| D50 | 数据库架构                                 | **3库：governance.db(SQLite)+depgraph.db(SQLite)+market.duckdb(DuckDB)**                                                 | 治理/依赖/业务三分离                                                                |
| D51 | SQLite合并                              | **9个SQLite→1个governance.db，8个空库删除，42备份保留1份**                                                                           | 去重去碎片                                                                      |
| D52 | depgraph.db DDL                       | **7表：domains/nodes/edges/domain\_dependencies/contracts/domain\_events/invariants**（初始裁定；P0-6后扩展为25表，见§18.3）           | §十八完整DDL                                                                   |
| D53 | market.duckdb DDL                     | **7表+1视图：tick\_data/kline\_3s(视图)/orders/positions/backtest\_results/backtest\_trades/risk\_snapshots/factor\_values** | §十八完整DDL                                                                   |
| D54 | 架构全景图入库                               | **同库(depgraph.db)不同表组，arch\_前缀**                                                                                       | 消费者不同但domain\_id需外键关联                                                      |
| D55 | 数据库路径                                 | **data/databases/，未来1万模块不变**                                                                                           | SQLite单文件可达280TB，路径是逻辑位置                                                   |
| D56 | 规则内容SSoT                              | **结构化YAML文件为唯一真源，1条规则1个YAML文件**                                                                                        | Policy as Code+AI直接Read+无生成步骤=无漂移（原DB-SSoT裁定已推翻）                           |
| D57 | 规则不入独立库                               | **规则入depgraph.db，node\_type='rule'，不建第四个库**                                                                            | 规则是依赖图节点（约束关系=边），135条不值得独立库                                                |
| D58 | 模板入库                                  | **10个模板文件作为node\_type='template'存入depgraph.db nodes表**                                                                 | 模板是结构化元数据，DB查询比文件遍历高效                                                      |
| D59 | nodes/edges DDL对齐模板                   | **对齐dependency\_graph\_template.md字段：nodes 12列→23列，edges 6列→18列**（初始裁定；P0-1后nodes扩展为41列，edges扩展为23列，见§18.3）            | 模板定义20核心字段+16边字段，DDL必须覆盖                                                   |
| D60 | depgraph.db总表数                        | **15业务表（7dep+7arch+1rule）+2系统表（\_schema\_version+sqlite\_sequence）=17表**（初始裁定；P0-6后新建9表扩展为25表，见§18.3），不建第四个库           | nodes/edges扩展+rule\_bindings 1表；rule\_enforcement\_log移入governance.db(D61) |
| D61 | 规则执行日志归属                              | **governance.db**（非depgraph.db）                                                                                        | 执行日志是append-only运营数据，不是依赖图数据                                               |
| D62 | 规则同步方向                                | **YAML→depgraph.db单向索引**                                                                                               | sync\_rule\_registry.py读YAML写DB索引，方向不可逆                                    |
| D63 | rule\_bindings数据源                     | **从YAML triggers字段同步**                                                                                                 | 不需要单独维护，YAML的triggers字段就是绑定定义                                              |
| D68 | task\_cards.db                        | **删除，任务卡保留在governance.db**                                                                                             | D9/D51已裁定2库架构；空库违反RULE-FIVE                                                |
| D69 | 架构层标签归一化                              | **15种→4种标准层(L0/L1/L2/L3)**                                                                                             | 非标标签=架构分层形同虚设                                                              |
| D70 | 域-层映射补全                               | **所有域映射到L0-L3：业务域→L2, 平台域→L1, 横切→L1, 基础设施→L0**                                                                         | 缺失=无法执行层间规则                                                                |
| D71 | 容量数据刷新                                | **从nodes表COUNT(\*)更新current，按D43标准设定max**                                                                              | current>max=容量管控失效                                                         |
| D72 | 稳定性分级目标                               | **frozen≥5%, stable≥20%, evolving≤70%, volatile≤5%**                                                                   | 95.5% evolving=变更管控无差异                                                     |
| D73 | 安全边界目标                                | **immutable\_core≥5%, human\_gated≥15%, ai\_modifiable≤80%**                                                           | 96.4% ai\_modifiable=安全风险高                                                 |
| D74 | 短域名归并                                 | **D-GOV→D-GOVERNANCE, D-INFRA→D-INFRA\_RUNTIME, D-SEC→D-SECURITY, D-OBS→D-OPS, D-INTEL→D-INTELLIGENCE, D-DATA→按子路径拆分** | 消除域ID重复                                                                    |
| D75 | D-TRAE处置                              | **归入D-GOVERNANCE，不作为独立域**                                                                                              | domain\_group已是governance，0个模块节点                                           |
| D76 | max\_modules三档                        | **16域×80 + 19域×60 + 5域×40 = 2620≤3000**                                                                                | 80硬约束+软上限60触发评审                                                            |
| D77 | D-TEST保留为第40域                         | **独立保留，不归入其他域**                                                                                                        | 2104个test类型边界清晰，拆分会破坏测试组织                                                  |
| D78 | D-RESILIENCE/D-ORCHESTRATION/D-DATA删除 | **AI生成器膨胀产物，不属于合法域**                                                                                                   | 0个src/模块，归入D-GOVERNANCE或按子路径拆分                                             |

> **编号说明**：D67 编号预留（历史讨论中跳过，未正式裁定）。D64-D66 见 §20 待办事项。

### V4.1/V4.2 补充裁定（#151-172，详见能力定位书§20.7/§20.8）

> **背景**：扫描 `docs/01_policies_and_standards` 下所有规则文件和模板文件，将规则、契约、门禁、词汇表统一到全景图。YAML是唯一真源，DB规则表是只读缓存。

| #   | 裁定项                            | 裁定结论                                                           | 理由                                        |
| --- | ------------------------------ | -------------------------------------------------------------- | ----------------------------------------- |
| 151 | 唯一真源（V4.3修订）                   | **YAML文件是唯一真源，DB规则表是只读缓存**；6张规则表安装只读触发器                        | 不能改/可重建/无责任/派生物                           |
| 152 | 跨模块依赖注册表（111条）                 | **YAML→edges表** 数据导入                                           | P0                                        |
| 153 | 架构契约VR规则（11条）                  | **YAML→arch\_constraints表** 数据导入                               | P0                                        |
| 154 | 契约映射表（18条层契约）                  | **YAML→contracts表** 数据导入                                       | P0                                        |
| 155 | 门禁注册表（25个）                     | **新建gates表+YAML数据导入**                                          | P1                                        |
| 156 | 功能域注册表（30+域）                   | **YAML→domains+arch\_path\_mappings** 数据导入                     | P1                                        |
| 157 | 词汇表（22个枚举字段）                   | **新建field\_vocabularies表+CHECK约束**                             | P1                                        |
| 158 | 架构规则TRAE-013\~017/036\~038     | **YAML→arch\_constraints表** 数据导入                               | P1                                        |
| 159 | 声明式契约追踪（11条）                   | **contracts表扩展+YAML数据导入**                                      | P2                                        |
| 160 | Frontmatter字段注册表（54字段）         | **YAML→field\_vocabularies表** 数据导入                             | P2                                        |
| 161 | 注册表之注册表（18个）                   | **新建registries+cross\_registry\_rules表+YAML数据导入**              | P2                                        |
| 162 | 目录注册表                          | **YAML→arch\_directory\_tree表** 数据导入                           | P2                                        |
| 163 | 规则路径目录（154文件）                  | **YAML→nodes表（文档节点）** 数据导入                                     | P2                                        |
| 164 | 基础设施+模型能力契约                    | **新建infrastructure\_components+model\_capabilities表+YAML数据导入** | P3                                        |
| 165 | nodes缺失字段 business\_stream     | **合并到nodes表**                                                  | 业务流归属是域级核心字段                              |
| 166 | nodes缺失字段 stream\_role         | **合并到nodes表**                                                  | 业务流角色影响依赖分析                               |
| 167 | nodes缺失字段 runtime\_plane       | **合并到nodes表**                                                  | 运行时平面影响部署决策                               |
| 168 | nodes缺失字段 ddd\_aggregate       | **合并到nodes表**                                                  | DDD聚合根标识影响领域驱动设计分析                        |
| 169 | nodes缺失字段 provided\_interfaces | **合并到nodes表**                                                  | 已有consumed\_interfaces，缺provided导致接口契约不完整 |
| 170 | 缺失表 hard\_boundaries           | **新建表**（8条硬边界）                                                 | 架构核心约束，当前散落在模板中                           |
| 171 | 缺失表 business\_streams          | **新建表**（业务流定义）                                                 | 跨域分析基础                                    |
| 172 | 缺失表 blueprint\_links           | **新建表**（蓝图→文件映射）                                               | 蓝图-代码双向对齐核心                               |

**Schema v5 迁移内容**（P0-6施工）：新建9表 + 扩展4表（contracts+6字段/edges+3字段/domains+1字段/nodes+5字段）+ CHECK约束 + 只读触发器。详见§18.8.7和能力定位书§22.9。

***

## 十六、待定决策清单

| #   | 决策项                                  | 说明                         | 依赖                                  |
| --- | ------------------------------------ | -------------------------- | ----------------------------------- |
| T1  | 各域max\_modules具体数值                   | 需基于干净数据裁定，80硬约束            | 生成器修复✅+数据清理（Phase A-I-E-C-B-F-K待执行） |
| T6  | 事件类型体系设计                             | AsyncEventBus的事件枚举         | 阶段2 R1-2（未开始）                       |
| T7  | 三级配置具体结构                             | config/目录重组方案              | 阶段1 STEP 1✅（待执行重组）                  |
| T8  | 场外文件重新提取到全景图                         | 补录10缺失顶级域+31缺失子域+场外20业务域映射 | §17.4已裁定v2方案                        |
| T9  | 场外文件提取优先级                            | 补录>提取>消缺>重新生成              | §17.4已裁定                            |
| T14 | 422个governance根目录平铺文件重分类             | 约100-150个属于其他域             | 技术债，后续迭代                            |
| T15 | 同类功能文件合并（rollback×12, escalation×6等） | 功能碎片化                      | 技术债，后续迭代                            |
| T16 | 生成器从domains表动态加载域名                   | 替代硬编码，防止域名漂移               | 长期技术债                               |
| T17 | 模块级\[DOMAIN]字段声明                     | 覆盖路径派生，纠正错放模块              | 长期技术债                               |

> T2/T3/T4/T5 已解决（阶段1 STEP 1-2已完成）：T2 market.duckdb DDL见§18.7；T3 governance.db合并见§18.3.1已完成✅；T4 depgraph.db DDL见§18.5；T5 45能力→域映射已由D44-D46裁定。
> T10-T13 已裁定删除：T10过时(D38/D41/D42)、T11已由D44给出、T12已裁定(D45/D46)、T13已裁定(D48)。

***

## 十七、场外文件评估

### 17.1 场外文件清单

| 位置                             | 文件数 | 核心内容                                       | 架构价值             |
| ------------------------------ | :-: | ------------------------------------------ | ---------------- |
| D:\临时工作区\ZephyrAlpha全系统模块清单.md |  1  | \~2,800模块定义(去重后\~2,000-2,500)              | depgraph设计态核心数据源 |
| D:\临时工作区\依赖图\\                 |  33 | 30域定义+30x30依赖矩阵+38契约+22事件+20不变量+场内模块清单.csv | depgraph设计态核心数据源 |
| D:\临时工作区\架构图\\                 |  11 | 9+1架构图+40交叉引用+边界矩阵+详细域设计                   | 顶层架构约束来源         |

### 17.2 场外文件关键数据

| 数据项     |    数量   | 来源                     |
| ------- | :-----: | ---------------------- |
| 域定义     |    30   | 依赖图/00-总览与索引.md (v7.0) |
| 模块定义    | \~2,800 | 全系统模块清单.md             |
| 依赖矩阵    |  30x30  | 依赖图/00-总览与索引.md        |
| 契约      |   38条   | 依赖图/01-跨域交叉点.md        |
| 领域事件    |   22条   | 依赖图/01-跨域交叉点.md        |
| 不变量     |   20条   | 依赖图/00-总览与索引.md        |
| 聚合根     |   10个   | 依赖图/00-总览与索引.md        |
| 值对象     |   12个   | 依赖图/00-总览与索引.md        |
| Saga事务  |    4个   | 依赖图/01-跨域交叉点.md        |
| 架构图交叉引用 |   40条   | 架构图/00-总览.md           |
| 硬边界约束   |   43条   | 依赖图/01-跨域交叉点.md        |
| 因果链     |    4条   | 依赖图/01-跨域交叉点.md        |

### 17.3 域体系裁定结论

**结论**：39个平铺域（场外30域+膨胀域拆分D-SIGNAL/D-DATA/D-SIMULATION各拆4域），无层级无子域。parent\_domain仅作分组属性标签。

**D-DATA消歧**：场外D-DATA(行情数据)→D-MKT-DATA，全景D-DATA保留(平台数据基础设施)。

> 漂移历史见 git log。裁定结果见 §17.6 完整39平铺域方案。

### 17.4 提取方案

**原则**：39个平铺域，无层级无子域。parent\_domain仅作分组属性标签。

```
STEP 1: 重建全景图
  删除9+35层级结构，改为39平铺域
  每个域：domain_id + name + group_tag + ssot_path + modules[]

STEP 2: 从场外文件提取每个域的设计态
  域定义+模块清单+域内依赖+域事件+契约+不变量

STEP 3: 提取跨域元数据
  依赖矩阵+38契约+22事件+20不变量+10聚合根+12值对象+4Saga+4因果链+43硬边界

STEP 4: 域ID消歧
  场外D-DATA→D-MKT-DATA

STEP 5: 重新生成depgraph+全景图(MD格式)
```

### 17.5 域容量标准（见 trae_055 ARCH-CAP-002）

**核心结论**：平铺不做子域是正确的。100% AI开发少一层抽象=少一个幻觉源。

|   production 节点数/域   |    判定    | 理由                 |
| :-------: | :------: | ------------------ |
|    < 80    |    偏小    | 可独立，但考虑合并到相关域    |
| **80-150** |  **默认安全区间**  | AI单次上下文可覆盖全部模块名+职责 |
|   150-200   |    高度耦合放宽    | 需满足高度耦合四标准（见 ARCH-CAP-003）       |
|  **> 200** | **硬上限必须拆分** | AI无法在单次上下文中理解全域    |

**超过200的问题**：依赖关系不可管理/重复造轮子/搜索结果过多/命名冲突/修改影响不可控。

### 17.6 域方案（v4，D44-D46裁定后）

**拆分汇总**：D-SIGNAL(164)→4域，D-DATA(71)→4域，D-SIMULATION(71)→4域。30+3×3=39域。

> 39 域是当前结果非最终结果。域数可无限拓展（见 trae_055 ARCH-CAP-005 抽屉式扩展 / ARCH-CAP-007 项目总容量无固定上限）。新增域只需 INSERT 到 domains 表，不修改生成器代码。

**完整39平铺域**：

| #  | 域ID                   | 域名             |  模块数 |  分组 | 拆分来源                             |
| -- | --------------------- | -------------- | :--: | :-: | -------------------------------- |
| 1  | D-MKT\_DATA           | 行情数据(接入+存储)    | \~16 |  业务 | D-DATA拆                          |
| 2  | D-DATA\_ENG           | 数据工程(增值+融合+知识) | \~19 |  业务 | D-DATA拆                          |
| 3  | D-DATA\_GOV           | 数据治理(质量+血缘+参考) | \~15 |  业务 | D-DATA拆                          |
| 4  | D-DATA\_SEC           | 数据安全与契约        | \~17 |  业务 | D-DATA拆                          |
| 5  | D-FACTOR              | 因子             |   7  |  业务 | —                                |
| 6  | D-SIGNAL              | 信号(技术+通用)      | \~50 |  业务 | D-SIGNAL拆                        |
| 7  | D-SIGNAL\_ASHARE      | A股特色信号         | \~44 |  业务 | D-SIGNAL拆                        |
| 8  | D-SIGNAL\_FUNDAMENTAL | 基本面信号          | \~30 |  业务 | D-SIGNAL拆                        |
| 9  | D-SIGNAL\_QUALITY     | 信号质量           | \~22 |  业务 | D-SIGNAL拆                        |
| 10 | D-PF\_CORE            | 组合核心           |   6  |  业务 | —                                |
| 11 | D-PF\_ALLOC           | 组合分配           |   4  |  业务 | —                                |
| 12 | D-SELL\_DECISION      | 卖出决策           |  18  |  业务 | —                                |
| 13 | D-POSITION            | 仓位管理           |   4  |  业务 | —                                |
| 14 | D-EX\_CORE            | 执行核心           |   4  |  业务 | —                                |
| 15 | D-EX\_SOR             | 执行路由           |   4  |  业务 | —                                |
| 16 | D-REPORTING           | 报告             |   5  |  业务 | —                                |
| 17 | D-RISK                | 风控             |  20  |  业务 | —                                |
| 18 | D-ML\_TRAIN           | 训练             |   5  |  业务 | —                                |
| 19 | D-ML\_SERVE           | 推理             |   6  |  业务 | —                                |
| 20 | D-ALT\_DATA           | 另类数据           |  17  |  业务 | —                                |
| 21 | D-CROSS\_ASSET        | 跨资产            |  21  |  业务 | —                                |
| 22 | D-COMPLIANCE          | 合规             |  18  |  业务 | —                                |
| 23 | D-TRADING             | 交易运营           |   6  |  业务 | —                                |
| 24 | D-SIMULATION          | 仿真核心           |  \~8 |  业务 | D-SIMULATION拆                    |
| 25 | D-BACKTEST            | 回测验证           | \~30 |  业务 | D-SIMULATION拆                    |
| 26 | D-EXEC\_SIM           | 执行仿真           |  \~3 |  业务 | D-SIMULATION拆(偏小，可合并到D-EX\_CORE) |
| 27 | D-DIGITAL\_TWIN       | 数字孪生           |  \~8 |  业务 | D-SIMULATION拆                    |
| 28 | D-GOVERNANCE          | 治理             |  待裁定 |  平台 | 模块需重新裁定(D48)                     |
| 29 | D-SECURITY            | 安全             |  待裁定 |  平台 | 模块需重新裁定(D48)                     |
| 30 | D-AUTONOMY\_CORE      | 自治核心           |  待裁定 |  平台 | 模块需重新裁定(D48)                     |
| 31 | D-AUTONOMY\_PERM      | 自治保护           |  待裁定 |  平台 | 模块需重新裁定(D48)                     |
| 32 | D-INFRA\_RUNTIME      | 运行时基础设施        |  待裁定 |  平台 | 模块需重新裁定(D48)                     |
| 33 | D-INFRA\_OPS          | 运维基础设施         |  待裁定 |  平台 | 模块需重新裁定(D48)                     |
| 34 | D-OPS                 | 运维             |  待裁定 |  平台 | 模块需重新裁定(D48)                     |
| 35 | D-INTEGRATION         | 集成             |  待裁定 |  平台 | 模块需重新裁定(D48)                     |
| 36 | D-KNOWLEDGE           | 知识             |  待裁定 |  平台 | 模块需重新裁定(D48)                     |
| 37 | D-INTELLIGENCE        | 智能             |  待裁定 |  平台 | 模块需重新裁定(D48)                     |
| 38 | D-FRONTEND            | 前端             |  待裁定 |  平台 | 模块需重新裁定(D48)                     |
| 39 | D-SHARED              | 共享             |  待裁定 |  横切 | 模块需重新裁定(D48)                     |

**业务域(27个)模块数已确定，平台域(12个)模块数待depgraph入库后逐个裁定。**

### 17.7 执行工作流（D47裁定）

```
STEP 1: 建数据库
  depgraph.db(SQLite) + governance.db(SQLite合并) + market.duckdb(业务数据)

STEP 2: depgraph YAML → depgraph.db
  157MB YAML → SQLite表(nodes/edges/attributes)
  入库后SQL毫秒级查询，替代YAML全文扫描

STEP 3: 定义39域
  27业务域已确定(§17.6)
  12平台域待逐模块裁定(D48)

STEP 4: 逐模块裁定归属域
  查depgraph.db：模块依赖谁/被谁依赖/职责
  裁定结果写回depgraph.db的domain_id字段
  平台域模块可能重新分配到业务域

STEP 5: 搬家
  按域裁定结果，搬到对应物理路径
```

***

## 十八、数据库架构（D49-D53裁定）

### 18.1 数据库位置

| 盘  | 可用     | 用途                     |
| -- | ------ | ---------------------- |
| D: | 335 GB | 代码+全部数据库（频繁读写）         |
| E: | 55 GB  | 仅冷归档（Parquet/备份），不放数据库 |

### 18.2 三库架构

| 数据库           | 引擎     | 职责          | 预估大小      | 路径                           |
| ------------- | ------ | ----------- | --------- | ---------------------------- |
| governance.db | SQLite | 治理元数据       | \~50MB    | data/databases/governance.db |
| depgraph.db   | SQLite | 依赖全景图+架构全景图 | \~300MB   | data/databases/depgraph.db   |
| market.duckdb | DuckDB | 业务数据        | 10GB→1TB+ | data/databases/market.duckdb |

**路径未来1万模块不变**：SQLite单文件可达280TB，DuckDB无硬限制，路径是逻辑位置不随容量变化。

### 18.3 数据库当前实际状态（2026-06-18 更新）

| 数据库           |   大小   |  表数 | 关键数据                                                                                                                                                                                | Schema版本 | 迁移框架                |
| ------------- | :----: | :-: | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------: | ------------------- |
| governance.db |  11MB  |  26 | 969 tasks(15 DEPGRAPH卡已COMPLETED), 6401 gates, 398 knowledge, 23687 audit\_entries, 386 drift\_events, 99613 fle\_metrics                                                           |    v27   | sqlite\_schema.py   |
| depgraph.db   | 39.2MB |  25 | 8,746 nodes(41列, 运营态6,637+设计态2,109), 8,229 edges(23列), 61 domains, 9,321 arch\_directory\_tree, 27 arch\_constraints(12列含violation\_status), 43触发器(27只读+16CHECK), dep\_cycles视图(8行) |    v5    | depgraph\_schema.py |
| market.duckdb |  0.5MB |  7  | 0行（Schema已建，业务数据待Phase 8）                                                                                                                                                           |     —    | —                   |

**depgraph.db v5 迁移（2026-06-18 完成）**：七批次施工计划（P0-1到P0-7）全部完成。

<details>
<summary>📋 v3.4+v5迁移详情（已完成，点击展开）</summary>

**v3.4 迁移（P0-1，2026-06-17）**：

- node\_id 改 INTEGER PRIMARY KEY
- edges 字段重命名 from\_node/to\_node → from\_node\_id/to\_node\_id（外键）
- edges 新增 dep\_maturity 字段
- arch\_directory\_tree 删 state 字段，新增 node\_id 外键
- nodes 新增 5 字段（can\_build, gate\_reason, hard\_boundary\_ref, consumed\_interfaces 等）
- nodes 表达 41 列，edges 表达 23 列

**v5 迁移（P0-6，2026-06-17）**：

- 新建 9 表：gates, hard\_boundaries, business\_streams, infrastructure\_components, model\_capabilities, cross\_registry\_rules, field\_vocabularies, registries, blueprint\_links
- 扩展 4 表：arch\_constraints 新增 violation\_status/details/detected\_at 字段（DB-02 修复）；contracts +6字段；edges +3字段；domains +1字段；nodes +5字段
- 27 个只读触发器（readonly\_前缀，保护规则表数据）
- 16 个 CHECK 触发器（chk\_前缀，校验 nodes/edges 字段约束）

**不符合项修复（DM-3001\~DM-3013，2026-06-18）**：

- 17 项不符合项全部处置完毕（12 项修复 + 5 项规格过时）
- 详见 生成器与全景图不符合项清单.md V2.1

</details>

**YAML全景图退役（2026-06-13）**：

- project-entity-depgraph.yaml + project-architecture-panorama.yaml 已删除
- 所有消费者脚本已改为从 depgraph.db 读取
- 64个蓝图.md + 3个.yaml + 34个.py 中的旧路径引用全部更新为 data/databases/depgraph.db
- Grep全项目确认零残留
- **depgraph.db 现在是依赖图+全景图的唯一真源（SSoT）**（规则内容SSoT为YAML文件，见D56）

**governance.db 变更**：domains表已删除（DM-100100），domains真源在depgraph.db。

### 18.3.1 SQLite合并计划（已完成✅）

**结论：9个SQLite→1个governance.db，8个空库删除，42备份保留1份。**

<details>
<summary>📋 合并详情（已完成，点击展开）</summary>

| 来源                           |   大小   |  表数 | 处置                                                  |   状态   |
| ---------------------------- | :----: | :-: | --------------------------------------------------- | :----: |
| data/databases/governance.db | 32.4MB |  19 | 主库，保留全部表                                            |  DONE  |
| audit\_index.db              |  8.5MB |  3  | 合并入audit\_entries/audit\_summary/integrity\_records |  DONE  |
| drift\_events.db             |  0.2MB |  1  | 合并入drift\_events                                    |  DONE  |
| drift\_audit.db              | 0.03MB |  3  | 合并入drift\_events/scan\_results/gate\_decisions      |  DONE  |
| data/databases/governance.db | 0.03MB |  1  | 合并入usage\_records                                   |  DONE  |
| auto\_fix.db                 | 0.03MB |  4  | 合并入fix\_records                                     |  DONE  |
| governance\_shards(×16)      |  1.5MB |  7  | 合并入对应表                                              | <br /> |
| 8个空库                         |    0   |  0  | **删除**                                              | <br /> |
| 42个备份                        |  \~5MB |  —  | 保留1份最新，删除其余                                         | <br /> |

</details>

### 18.4 governance.db DDL

```sql
-- 任务系统
CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'READY',
    priority TEXT NOT NULL DEFAULT 'MEDIUM',
    blueprint_id TEXT,
    domain_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    owner TEXT,
    post_sync_standard TEXT,
    acceptance_criteria TEXT,
    deliverables TEXT,
    files_in_scope TEXT,
    applicable_rules TEXT,
    allowed_touch TEXT,
    rollback_instructions TEXT,
    construction_targets TEXT,
    FOREIGN KEY (domain_id) REFERENCES domains(domain_id)
);

CREATE TABLE task_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    from_status TEXT,
    to_status TEXT,
    actor TEXT,
    detail TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
);

CREATE TABLE task_snapshots (
    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    snapshot_data TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
);

CREATE TABLE task_files (
    task_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    change_type TEXT,
    PRIMARY KEY (task_id, file_path),
    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
);

-- 门禁系统
CREATE TABLE gates (
    gate_id TEXT PRIMARY KEY,
    gate_name TEXT NOT NULL,
    gate_type TEXT NOT NULL,
    phase TEXT,
    config TEXT,
    enabled INTEGER NOT NULL DEFAULT 1,
    last_run TEXT,
    last_result TEXT
);

-- 知识系统
CREATE TABLE knowledge (
    ke_id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    content TEXT NOT NULL,
    provenance TEXT,
    tags TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    embedding_id TEXT
);

CREATE TABLE ke_tombstones (
    ke_id TEXT PRIMARY KEY,
    deleted_at TEXT NOT NULL,
    reason TEXT
);

-- 审计系统
CREATE TABLE audit_entries (
    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    category TEXT NOT NULL,
    action TEXT NOT NULL,
    actor TEXT,
    target TEXT,
    detail TEXT,
    session_id TEXT,
    integrity_hash TEXT
);

CREATE TABLE audit_summary (
    summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,
    category TEXT NOT NULL,
    count INTEGER,
    summary_data TEXT
);

CREATE TABLE integrity_records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    checkpoint_time TEXT NOT NULL,
    root_hash TEXT NOT NULL,
    entry_count INTEGER,
    verified INTEGER DEFAULT 0
);

-- 漂移系统
CREATE TABLE drift_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    detector_id TEXT NOT NULL,
    severity TEXT NOT NULL,
    description TEXT,
    baseline_hash TEXT,
    current_hash TEXT,
    resolved INTEGER DEFAULT 0,
    resolution TEXT
);

CREATE TABLE scan_results (
    scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    scanner_type TEXT NOT NULL,
    total_checked INTEGER,
    violations_found INTEGER,
    details TEXT
);

CREATE TABLE gate_decisions (
    decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
    gate_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    decision TEXT NOT NULL,
    detail TEXT,
    FOREIGN KEY (gate_id) REFERENCES gates(gate_id)
);

-- FLE系统
CREATE TABLE fle_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    metric_type TEXT NOT NULL,
    value REAL,
    detail TEXT
);

CREATE TABLE fle_alerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    description TEXT,
    resolved INTEGER DEFAULT 0
);

CREATE TABLE fle_dispatch_log (
    dispatch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    from_domain TEXT,
    to_domain TEXT,
    action TEXT,
    result TEXT
);

CREATE TABLE judgment_records (
    judgment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    case_type TEXT NOT NULL,
    decision TEXT NOT NULL,
    reasoning TEXT,
    actor TEXT
);

-- 基础设施
CREATE TABLE circuit_breaker_state (
    breaker_id TEXT PRIMARY KEY,
    state TEXT NOT NULL DEFAULT 'CLOSED',
    failure_count INTEGER DEFAULT 0,
    last_failure TEXT,
    last_reset TEXT
);

CREATE TABLE slow_queries (
    query_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    query_text TEXT,
    duration_ms INTEGER,
    table_name TEXT
);

CREATE TABLE tx_idempotency (
    tx_id TEXT PRIMARY KEY,
    operation TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    result TEXT
);

CREATE TABLE usage_records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    operation TEXT NOT NULL,
    tokens_used INTEGER,
    cost REAL,
    model TEXT
);

CREATE TABLE fix_records (
    fix_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    fix_type TEXT NOT NULL,
    target TEXT,
    result TEXT,
    budget_consumed REAL
);

CREATE TABLE _schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL,
    description TEXT
);
```

### 18.5 depgraph.db DDL

> **注**：以下为初始版本DDL（2026-06-12）。P0-1（v3.4迁移）+ P0-6（v5迁移）后，实际schema已大幅升级：nodes 41列（node\_id改INTEGER PK）、edges 23列（from\_node/to\_node→from\_node\_id/to\_node\_id + dep\_maturity）、新增9表。当前实际schema见 `PRAGMA table_info()` 或能力定位书§22.4。

```sql
-- 域定义(39平铺域)
CREATE TABLE domains (
    domain_id TEXT PRIMARY KEY,
    domain_name TEXT NOT NULL,
    domain_group TEXT NOT NULL,
    description TEXT,
    ssot_path TEXT,
    current_modules INTEGER DEFAULT 0,
    max_modules INTEGER,
    lifecycle TEXT DEFAULT 'design_only',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- 模块节点
CREATE TABLE nodes (
    node_id TEXT PRIMARY KEY,
    node_type TEXT NOT NULL,
    node_name TEXT NOT NULL,
    domain_id TEXT,
    blueprint_id TEXT,
    stability TEXT,
    safety_level TEXT,
    ai_autonomy TEXT,
    file_path TEXT,
    design_state TEXT,
    runtime_state TEXT,
    last_verified TEXT,
    FOREIGN KEY (domain_id) REFERENCES domains(domain_id)
);

-- 依赖边
CREATE TABLE edges (
    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_node TEXT NOT NULL,
    to_node TEXT NOT NULL,
    edge_type TEXT NOT NULL,
    strength TEXT DEFAULT 'hard',
    cross_domain INTEGER DEFAULT 0,
    verified INTEGER DEFAULT 0,
    FOREIGN KEY (from_node) REFERENCES nodes(node_id),
    FOREIGN KEY (to_node) REFERENCES nodes(node_id)
);

-- 域间依赖
CREATE TABLE domain_dependencies (
    from_domain TEXT NOT NULL,
    to_domain TEXT NOT NULL,
    edge_count INTEGER DEFAULT 0,
    edge_types TEXT,
    constraint_type TEXT,
    PRIMARY KEY (from_domain, to_domain),
    FOREIGN KEY (from_domain) REFERENCES domains(domain_id),
    FOREIGN KEY (to_domain) REFERENCES domains(domain_id)
);

-- 契约
CREATE TABLE contracts (
    contract_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    provider_domain TEXT NOT NULL,
    consumer_domain TEXT NOT NULL,
    contract_type TEXT NOT NULL,
    schema_definition TEXT,
    version TEXT,
    FOREIGN KEY (provider_domain) REFERENCES domains(domain_id),
    FOREIGN KEY (consumer_domain) REFERENCES domains(domain_id)
);

-- 领域事件
CREATE TABLE domain_events (
    event_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    source_domain TEXT NOT NULL,
    target_domains TEXT,
    payload_schema TEXT,
    priority TEXT DEFAULT 'P1',
    FOREIGN KEY (source_domain) REFERENCES domains(domain_id)
);

-- 不变量
CREATE TABLE invariants (
    invariant_id TEXT PRIMARY KEY,
    domain_id TEXT NOT NULL,
    description TEXT NOT NULL,
    constraint_type TEXT NOT NULL,
    enforcement TEXT,
    FOREIGN KEY (domain_id) REFERENCES domains(domain_id)
);

-- 索引
CREATE INDEX idx_nodes_domain ON nodes(domain_id);
CREATE INDEX idx_nodes_type ON nodes(node_type);
CREATE INDEX idx_nodes_blueprint ON nodes(blueprint_id);
CREATE INDEX idx_edges_from ON edges(from_node);
CREATE INDEX idx_edges_to ON edges(to_node);
CREATE INDEX idx_edges_cross_domain ON edges(cross_domain);
CREATE INDEX idx_contracts_provider ON contracts(provider_domain);
CREATE INDEX idx_contracts_consumer ON contracts(consumer_domain);
CREATE INDEX idx_events_source ON domain_events(source_domain);
CREATE INDEX idx_invariants_domain ON invariants(domain_id);
```

### 18.6 架构全景图 DDL（arch\_前缀，同库depgraph.db）

> 消费者：容量规划/路径解析/域裁定/搬家。与dep\_表组共享domains表。
> **注**：以下为初始版本DDL。P0-1后arch\_directory\_tree删state新增node\_id外键；P0-6后arch\_constraints新增violation\_status/details/detected\_at字段（DB-02修复）。当前实际schema见 `PRAGMA table_info()`。

```sql
-- ===== 架构全景图表组（arch_前缀）=====
-- 消费者：容量规划/路径解析/域裁定/搬家
-- 与dep_表组共享domains表（domain_id外键）

-- 域容量规划（扩展domains表的容量信息）
CREATE TABLE arch_domain_capacity (
    domain_id TEXT PRIMARY KEY,
    current_modules INTEGER DEFAULT 0,
    max_modules INTEGER NOT NULL,
    growth_pattern TEXT DEFAULT 'linear',  -- linear/logarithmic/exponential
    target_modules INTEGER,                -- 目标模块数
    feasibility TEXT DEFAULT 'feasible',   -- feasible/at_risk/infeasible
    bottleneck_description TEXT,
    last_capacity_check TEXT,
    FOREIGN KEY (domain_id) REFERENCES domains(domain_id)
);

-- 域路径映射（物理路径→域的映射）
CREATE TABLE arch_path_mappings (
    mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain_id TEXT NOT NULL,
    path_pattern TEXT NOT NULL,            -- 物理路径模式
    path_type TEXT NOT NULL,               -- ssot/design/runtime/test/script
    state TEXT NOT NULL DEFAULT 'design',  -- design/operational
    covers TEXT,                           -- JSON: 覆盖的功能描述列表
    aliases TEXT,                          -- JSON: 别名列表
    FOREIGN KEY (domain_id) REFERENCES domains(domain_id)
);

-- 架构层定义（L0-L5）
CREATE TABLE arch_layers (
    layer_id TEXT PRIMARY KEY,             -- L0/L1/L2/L3/L4/L5
    layer_name TEXT NOT NULL,
    layer_description TEXT,
    decision_type TEXT NOT NULL,           -- WHAT/WHERE/HOW/DATA/DISK/DOC
    parent_layer TEXT,
    FOREIGN KEY (parent_layer) REFERENCES arch_layers(layer_id)
);

-- 域→架构层映射（一个域属于哪个架构层）
CREATE TABLE arch_domain_layers (
    domain_id TEXT NOT NULL,
    layer_id TEXT NOT NULL,
    PRIMARY KEY (domain_id, layer_id),
    FOREIGN KEY (domain_id) REFERENCES domains(domain_id),
    FOREIGN KEY (layer_id) REFERENCES arch_layers(layer_id)
);

-- 架构约束（跨域约束规则）
CREATE TABLE arch_constraints (
    constraint_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    constraint_type TEXT NOT NULL,         -- cross_domain_dependency/path_rule/capacity_rule
    from_domain TEXT,
    to_domain TEXT,
    rule_definition TEXT NOT NULL,         -- JSON: 约束规则定义
    severity TEXT DEFAULT 'hard',          -- hard/soft
    enforcement TEXT DEFAULT 'gate',       -- gate/runtime/compile_time
    description TEXT,
    FOREIGN KEY (from_domain) REFERENCES domains(domain_id),
    FOREIGN KEY (to_domain) REFERENCES domains(domain_id)
);

-- 目录结构（运营态+设计态）
CREATE TABLE arch_directory_tree (
    path TEXT PRIMARY KEY,                 -- 物理路径
    parent_path TEXT,
    path_type TEXT NOT NULL,               -- directory/file
    domain_id TEXT,                        -- 归属域
    state TEXT NOT NULL DEFAULT 'design',  -- design/operational
    blueprint_id TEXT,                     -- 关联蓝图
    stability TEXT,                        -- frozen/stable/evolving/volatile
    ai_autonomy TEXT,                      -- immutable_core/human_gated/ai_modifiable
    last_scanned TEXT,
    FOREIGN KEY (domain_id) REFERENCES domains(domain_id),
    FOREIGN KEY (parent_path) REFERENCES arch_directory_tree(path)
);

-- 容量瓶颈追踪
CREATE TABLE arch_bottlenecks (
    bottleneck_id INTEGER PRIMARY KEY AUTOINCREMENT,
    area TEXT NOT NULL,                    -- depgraph/tests/gate_execution/disk/config
    description TEXT NOT NULL,
    severity TEXT NOT NULL,                -- critical/warning/info
    current_impact TEXT,
    proposed_solution TEXT,
    status TEXT DEFAULT 'open',            -- open/in_progress/resolved
    detected_at TEXT NOT NULL,
    resolved_at TEXT
);

-- 索引
CREATE INDEX idx_arch_capacity_domain ON arch_domain_capacity(domain_id);
CREATE INDEX idx_arch_path_domain ON arch_path_mappings(domain_id);
CREATE INDEX idx_arch_path_type ON arch_path_mappings(path_type);
CREATE INDEX idx_arch_dir_domain ON arch_directory_tree(domain_id);
CREATE INDEX idx_arch_dir_state ON arch_directory_tree(state);
CREATE INDEX idx_arch_dir_parent ON arch_directory_tree(parent_path);
CREATE INDEX idx_arch_constraint_from ON arch_constraints(from_domain);
CREATE INDEX idx_arch_constraint_to ON arch_constraints(to_domain);
CREATE INDEX idx_arch_bottleneck_status ON arch_bottlenecks(status);
```

### 18.7 market.duckdb DDL

```sql
-- 行情Tick数据
CREATE TABLE tick_data (
    symbol VARCHAR NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    price DOUBLE,
    volume BIGINT,
    amount DOUBLE,
    bid1 DOUBLE, ask1 DOUBLE,
    bid_vol1 BIGINT, ask_vol1 BIGINT,
    data_source VARCHAR,
    quality_score SMALLINT
) PARTITION BY (symbol, MONTH(timestamp));

-- K线视图
CREATE VIEW kline_3s AS
SELECT symbol,
    first(price) AS open, max(price) AS high,
    min(price) AS low, last(price) AS close,
    sum(volume) AS volume, sum(amount) AS amount,
    time_bucket('3 seconds', timestamp) AS ts
FROM tick_data GROUP BY symbol, ts;

-- 订单
CREATE TABLE orders (
    order_id VARCHAR PRIMARY KEY,
    symbol VARCHAR NOT NULL,
    side VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    qty DOUBLE NOT NULL,
    price DOUBLE,
    status VARCHAR NOT NULL,
    strategy_id VARCHAR,
    portfolio_id VARCHAR,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    fill_price DOUBLE,
    fill_qty DOUBLE,
    commission DOUBLE,
    slippage DOUBLE
);

-- 持仓
CREATE TABLE positions (
    portfolio_id VARCHAR NOT NULL,
    symbol VARCHAR NOT NULL,
    qty DOUBLE NOT NULL,
    avg_cost DOUBLE,
    current_price DOUBLE,
    unrealized_pnl DOUBLE,
    realized_pnl DOUBLE,
    updated_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (portfolio_id, symbol)
);

-- 回测结果
CREATE TABLE backtest_results (
    backtest_id VARCHAR PRIMARY KEY,
    strategy_id VARCHAR NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DOUBLE NOT NULL,
    final_capital DOUBLE,
    total_return DOUBLE,
    sharpe_ratio DOUBLE,
    max_drawdown DOUBLE,
    win_rate DOUBLE,
    total_trades INTEGER,
    parameters VARCHAR,
    created_at TIMESTAMPTZ NOT NULL
);

-- 回测交易明细
CREATE TABLE backtest_trades (
    trade_id INTEGER PRIMARY KEY,
    backtest_id VARCHAR NOT NULL,
    symbol VARCHAR NOT NULL,
    side VARCHAR NOT NULL,
    entry_time TIMESTAMPTZ NOT NULL,
    exit_time TIMESTAMPTZ,
    entry_price DOUBLE NOT NULL,
    exit_price DOUBLE,
    qty DOUBLE NOT NULL,
    pnl DOUBLE,
    commission DOUBLE,
    FOREIGN KEY (backtest_id) REFERENCES backtest_results(backtest_id)
);

-- 风控快照
CREATE TABLE risk_snapshots (
    snapshot_id INTEGER PRIMARY KEY,
    portfolio_id VARCHAR NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    var_1d DOUBLE,
    var_1d_95 DOUBLE,
    max_drawdown DOUBLE,
    exposure_by_sector VARCHAR,
    margin_usage DOUBLE,
    liquidity_score DOUBLE
);

-- 因子值
CREATE TABLE factor_values (
    factor_id VARCHAR NOT NULL,
    symbol VARCHAR NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    value DOUBLE,
    quality SMALLINT
) PARTITION BY (factor_id, MONTH(timestamp));
```

### 18.8 Phase E：规则+模板入库设计（D56-D60裁定）

#### 18.8.1 SSoT架构（V4.3修订：唯一真源+只读缓存）

结构化YAML文件为规则内容的**唯一真源**（唯一责任，D56裁定）。depgraph.db的规则表为从YAML单向同步的**只读缓存**（派生物，D62裁定）。6张规则表（gates/field\_vocabularies/registries/cross\_registry\_rules/hard\_boundaries/business\_streams）安装只读触发器，禁止任何直接修改，只有sync\_yaml\_to\_depgraph.py能临时禁用触发器写入。

```
YAML文件 ──唯一真源──→ sync_yaml_to_depgraph.py ──→ depgraph.db 规则表（只读缓存）
     ↓                                                    ↓
  AI/人类 Read                                     DB查询（快速定位/SQL JOIN）
     ↓
  Git commit
```

| 维度     | YAML文件（唯一真源）   | depgraph.db 规则表（只读缓存）                |
| ------ | -------------- | ------------------------------------ |
| 角色     | **唯一真源**（唯一责任） | **只读缓存**（派生物，不是真源）                   |
| 能否修改   | ✅ 唯一可修改处       | ❌ 触发器拦截，禁止任何直接修改                     |
| 写入方    | 人工/AI 修改规则时    | 只有 sync\_yaml\_to\_depgraph.py（有通行证） |
| 读取方    | AI 理解规则语义      | AI 查询关系、SQL JOIN                     |
| Git 追踪 | ✅ 可追踪、可 review | ❌ 二进制不可追踪                            |
| 枚举校验   | ❌ 无 CHECK 约束   | ✅ 有 CHECK 约束                         |
| 同步方向   | 源              | 目标（YAML → DB 单向）                     |
| 删除策略   | **保留**（永不删除）   | 可随时从 YAML 重建                         |

#### 18.8.2 规则体系实况

| 维度                        |    数量   |
| ------------------------- | :-----: |
| 规则登记条目（rule\_registry.md） |   135条  |
| ABS（绝对禁止）                 |   52条   |
| COND（条件禁止）                |   52条   |
| CODE（代码强制）                |   10条   |
| TRAE（IDE注入铁律）             |   11条   |
| SCRIPT                    |   13条   |
| MTH（方法论）                  |   13条   |
| 规则文件总数（非index .md）        |   82个   |
| 规则文件总行数                   | 18,594行 |
| 注册表YAML文件                 |   46个   |

**死规则率**：有代码执行器的规则遵守率70%+，纯靠AI"读到并遵守"的遵守率<30%。

#### 18.8.3 规则与模块的关系（四层）

| 关系层     | 含义         | 升级后存储                                                     |
| ------- | ---------- | --------------------------------------------------------- |
| 1. 约束关系 | 规则约束模块的行为  | edges表 dep\_type='constrains'                             |
| 2. 触发关系 | 操作触发规则检查   | rule\_bindings表                                           |
| 3. 执行关系 | 代码执行器强制规则  | YAML enforcement字段 + governance.db rule\_enforcement\_log |
| 4. 发现关系 | AI如何找到适用规则 | RuleLoader查DB索引→Read YAML                                 |

#### 18.8.4 升级后nodes表DDL（对齐dependency\_graph\_template.md）

```sql
CREATE TABLE nodes (
    node_id TEXT PRIMARY KEY,
    node_type TEXT NOT NULL,               -- 21种+rule+template=23种
    path TEXT NOT NULL,
    granularity TEXT NOT NULL DEFAULT 'file',
    domain_id TEXT,
    subdomain_id TEXT,
    blueprint_id TEXT,
    belongs_to TEXT,
    owner TEXT,
    change_policy TEXT DEFAULT 'evolving', -- frozen/stable/evolving/volatile
    impact_level TEXT DEFAULT 'M',         -- H/M/L
    modification_permission TEXT DEFAULT 'ai_modifiable',
    file_header_score INTEGER DEFAULT 0,
    tags TEXT,                             -- JSON数组
    architecture_layer TEXT,
    design_maturity TEXT DEFAULT 'production',
    deployment_lifecycle TEXT DEFAULT 'stable',
    trust_zone TEXT DEFAULT 'trusted_core',
    license TEXT DEFAULT 'Internal',
    drive_direction TEXT DEFAULT 'bottom_up',
    type_specific_data TEXT,               -- JSON: 差异字段
    last_verified TEXT,
    FOREIGN KEY (domain_id) REFERENCES domains(domain_id)
);
CREATE INDEX idx_nodes_domain ON nodes(domain_id);
CREATE INDEX idx_nodes_type ON nodes(node_type);
CREATE INDEX idx_nodes_blueprint ON nodes(blueprint_id);
CREATE INDEX idx_nodes_granularity ON nodes(granularity);
CREATE INDEX idx_nodes_change_policy ON nodes(change_policy);
CREATE INDEX idx_nodes_design_maturity ON nodes(design_maturity);
```

#### 18.8.5 升级后edges表DDL

> **注**：以下为V4.1裁定时的"升级后"DDL。P0-1（v3.4迁移）后，from\_node/to\_node已重命名为from\_node\_id/to\_node\_id（外键），edges表从17列扩展到23列（新增dep\_maturity等3字段）。当前实际schema见 `PRAGMA table_info(edges)`。

```sql
CREATE TABLE edges (
    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_node TEXT NOT NULL,
    to_node TEXT NOT NULL,
    dep_type TEXT NOT NULL,                -- 12种+constrains/triggers=14种
    architecture_direction TEXT DEFAULT 'downstream',
    coupling_strength TEXT DEFAULT 'critical',
    used_symbol TEXT,
    invocation_method TEXT,
    api_contract_refs TEXT,                -- JSON
    event_ref TEXT,
    ddd_integration_pattern TEXT,
    failure_mode TEXT,
    fallback TEXT,
    activation_condition TEXT,
    data_transfer_description TEXT,
    resource_impact TEXT,
    relationship_type TEXT DEFAULT 'one_to_many',
    cross_domain INTEGER DEFAULT 0,
    verified INTEGER DEFAULT 0,
    FOREIGN KEY (from_node) REFERENCES nodes(node_id),
    FOREIGN KEY (to_node) REFERENCES nodes(node_id)
);
CREATE INDEX idx_edges_from ON edges(from_node);
CREATE INDEX idx_edges_to ON edges(to_node);
CREATE INDEX idx_edges_type ON edges(dep_type);
CREATE INDEX idx_edges_direction ON edges(architecture_direction);
CREATE INDEX idx_edges_cross_domain ON edges(cross_domain);
```

#### 18.8.6 规则表组（rule\_前缀）

```sql
-- rule_bindings表留在depgraph.db（关系索引）
-- rule_enforcement_log表移到governance.db（运营数据）

CREATE TABLE rule_bindings (
    binding_id INTEGER PRIMARY KEY AUTOINCREMENT,
    function_name TEXT NOT NULL,
    rule_id TEXT NOT NULL,
    binding_type TEXT NOT NULL,            -- pre_check/post_check/enforcement
    trigger_type TEXT NOT NULL,            -- operation/skill/gate
    trigger_id TEXT,
    FOREIGN KEY (rule_id) REFERENCES nodes(node_id)
);
CREATE INDEX idx_rule_bindings_function ON rule_bindings(function_name);
CREATE INDEX idx_rule_bindings_rule ON rule_bindings(rule_id);
```

#### 18.8.7 depgraph.db升级后总表清单

| 表组     |   表数   | 表名                                                                                                                                            |
| ------ | :----: | --------------------------------------------------------------------------------------------------------------------------------------------- |
| dep\_  |    7   | domains, nodes(升级), edges(升级), domain\_dependencies, contracts, domain\_events, invariants                                                    |
| arch\_ |    7   | arch\_domain\_capacity, arch\_path\_mappings, arch\_layers, arch\_domain\_layers, arch\_constraints, arch\_directory\_tree, arch\_bottlenecks |
| rule\_ |    1   | rule\_bindings                                                                                                                                |
| 系统     |    2   | \_schema\_version, sqlite\_sequence                                                                                                           |
| **合计** | **17** | —                                                                                                                                             |

rule\_enforcement\_log移入governance.db（D61裁定），governance.db从25表→26表

> **P0-6 Schema v5 迁移后更新（2026-06-17 完成）**：新建9表（gates/hard\_boundaries/business\_streams/infrastructure\_components/model\_capabilities/cross\_registry\_rules/field\_vocabularies/registries/blueprint\_links），depgraph.db从17表→25表（24业务+1系统\_schema\_version）。当前实际表清单见§18.3。

> **Schema v5 迁移已完成✅**（V4.1/V4.2裁定，P0-6施工 2026-06-17）：新建9表（gates/field\_vocabularies/registries/cross\_registry\_rules/infrastructure\_components/model\_capabilities/hard\_boundaries/business\_streams/blueprint\_links）+ 扩展4表（contracts+6字段/edges+3字段/domains+1字段/nodes+5字段）+ CHECK约束 + 只读触发器。详见能力定位书§20.7/§20.8/§22.9。当前depgraph.db共25表（24业务+1系统）。

***

## 十九、讨论进度

| 阶段              |    状态    | 说明                                                     |
| --------------- | :------: | ------------------------------------------------------ |
| 阶段0 安全网         |   部分完成   | ide\_health\_service 重建+阶段A安全网卡+独立修复卡待执行               |
| 阶段1 架构+DB       |   已完成✅   | STEP 1-2完成，STEP 3 CI/CD未开始                             |
| 阶段2 R1/R2升级     |    未开始   | async runtime + DuckDB时序存储                             |
| 阶段3 depgraph迁移  | 深化施工已完成✅ | 七批次P0-1\~P0-7完成，17项不符合项处置完毕；Phase A-I-E-C-B-F-K数据治理待执行 |
| 阶段4 搬家对齐        |    未开始   | 依赖阶段3数据治理完成                                            |
| 阶段5-8 R3-R8+业务层 |    未开始   | 依赖阶段4完成                                                |

> 完整讨论时间线见 git log。决策结果已固化在 §15 D1-D78 + #151-172 决策清单和 §16 待定项中。

***

## 二十、后续待办事项（域裁定后执行）

> 以下3项依赖域裁定完成（§17.7 STEP 3-4），任务卡已创建，暂不执行。

| 编号  | 裁定        | 任务卡 | 内容                                            | 前置条件                   | 状态      |
| --- | --------- | --- | --------------------------------------------- | ---------------------- | ------- |
| D64 | DM-100050 | 已创建 | 将 DatabaseService 集成到事件驱动系统（自动启动/自动运行）        | 域裁定完成；平台域模块归属确定        | PENDING |
| D65 | DM-100051 | 已创建 | 将 29 个 YAML 读取脚本迁移到 DepgraphReader            | 域裁定完成；depgraph.db 数据完整 | PENDING |
| D66 | DM-100052 | 已创建 | 配置自动健康检查定时任务（SELECT 1 + WAL 检查 + schema 版本检查） | DM-100050 完成           | PENDING |

**执行时机**：§17.7 STEP 3（域裁定）+ STEP 4（平台域逐模块重新裁定）完成后，按 DM-100050→DM-100051→DM-100052 顺序执行。

***

## 二十一、超容域拆分策略

> 具体超容域清单、拆分方案、域数预估见 `archive/depgraph_issue_registry.md` §七。
> 方法论：先清理后拆分，小域不拆（< 2x max），大域按自然边界拆。按P0→P1→P2→P3优先级执行。

***

## 二十二、架构健康度评估与修复方案（2026-06-15 评估，2026-06-18 更新）

### 22.1 评估结论

**设计是顶级的，执行曾不达标，Phase H+J 已修复生成器根因，七批次施工+17项不符合项修复已全部完成。**

> 修复文件：`scripts/governance/generate_project_depgraph.py`（H1-H9, A1, DM-3002\~3004, DM-3011\~3013）
> Schema修复：`depgraph.db`（J1-J4 ALTER TABLE + P0-1 v3.4迁移 + P0-6 v5迁移）
> 修复详情见 `archive/depgraph_issue_registry.md`（原 `depgraph_fix_plans.md` 已合并）。
> **七批次施工计划（P0-1到P0-7）已全部完成（2026-06-18）**，17项不符合项全部处置完毕（12项修复+5项规格过时）。
> **下一步**：阶段3 Phase A-I-E-C-B-F-K 数据治理（10张卡可立即执行，B1/B2 依赖已满足）。

### 22.2 项目规模速览（2026-06-18 更新）

| 维度                             |                                                    数量 |
| ------------------------------ | ----------------------------------------------------: |
| depgraph.db 节点                 |                              8,746（运营态6,637+设计态2,109） |
| depgraph.db 边                  |                                                 8,229 |
| depgraph.db 域                  |                                                    61 |
| depgraph.db 表                  |                                          25（24业务+1系统） |
| depgraph.db 触发器                |                                      43（27只读+16CHECK） |
| governance.db 任务               |                                                   969 |
| `generate_project_depgraph.py` | 已修复 H1-H9 + A1 + 9项不符合项（DM-3002\~3004, DM-3011\~3013） |
| `audit_domain_nodes.py`        |                             已修复 5项不符合项（DM-3005\~3009） |
| `sync_yaml_to_depgraph.py`     |                                   已修复 1项不符合项（DM-3010） |

***

## 二十三、规则文件对齐方案（2026-06-19）

> **触发**：审查 project_rules.md / onboarding_detail.md / AGENTS.md 三件套时发现大量"死链接"，经核对架构升级进度后判定为**规则文件落后于架构升级进度**，非规则文件本身错误。
> **原则**：只修复"不依赖搬家且 SSoT 已明确"的漂移；结构优化/重复消除推迟到阶段7（§5.1 规则文件格式升级）。

### 23.1 漂移分类与处置原则

| 类别 | 例子 | 处置 |
| ---- | ---- | ---- |
| 已明确废弃 | panorama.yaml（被 depgraph.db 取代，§18.3 2026-06-13 删除） | 删除引用，改指 depgraph.db |
| 部分实现+路径漂移 | agent_spec（MOD-INF-019，partially_implemented，actual_disk_path 用连字符违反 Python 命名） | 重定向到实际数据源 data/capability_cards/，标注待阶段4搬家 |
| 待阶段7统一处理 | 标准文档缺失（code-construction-standards.md 等）、结构重复 | 推迟，不现在动 |

### 23.2 对齐方案（9 项，不依赖搬家）

| # | 修复项 | SSoT 依据 | 影响文件 |
| :-: | ---- | ---- | ---- |
| 1 | panorama.yaml 引用 → depgraph.db | §18.3 废弃 | project_rules.md |
| 2 | unified-asset-index.yaml → unified_asset_index.yaml（下划线） | 实际文件名 data/asset_index/unified_asset_index.yaml | project_rules.md |
| 3 | Python 3.12+ → >=3.11 | pyproject.toml requires-python | project_rules.md, AGENTS.md |
| 4 | TaskRepo import 路径 → zephyr.governance.task_repo | 实际代码 src/zephyr/governance/task_repo.py | project_rules.md, AGENTS.md |
| 5 | onboarding 章节跳号修复（缺第十二章） | 纯结构 | onboarding_detail.md |
| 6 | onboarding §十四"架构对标参考"删除 | 违反自身 §10.4 删掉清单"对标段" | onboarding_detail.md |
| 7 | onboarding §15.5 python -c 多行内联 → 落盘 .py 脚本 | 违反 RULE-SEVENTEEN | onboarding_detail.md |
| 8 | MCP 数 7 → 9 | config/mcp.json description "9 Server" | project_rules.md |
| 9 | agent_spec 引用 → data/capability_cards/skill_*.yaml（22个已落地） | 实际数据存在 | project_rules.md, onboarding_detail.md |

### 23.3 执行顺序

```
STEP 0  建立测试基础设施
        ├─ data/rule_optimization/key_facts.yaml（关键事实清单，SSoT 基准）
        └─ scripts/governance/check_rule_coverage.py（验证脚本，走 scaffold 注册）
STEP 1  逐项执行 23.2 的 9 项修复（每项：加锁→编辑→释放锁→静态测试）
STEP 2  最终全量测试（静态覆盖 + 动态模拟，连续 2 次零问题）
```

**因果链**：先建测试基准 → 再逐项修复 → 每项后立即静态测试 → 失败则回滚重做。

### 23.4 测试方案

| 层 | 方法 | 频率 | 判定 |
| :-: | ---- | ---- | ---- |
| 层1 静态 | check_rule_coverage.py 扫描 .md 检查关键事实覆盖 + 引用文件存在性 | 每次修改后 | exit 0=通过，exit 1=漂移→回滚 |
| 层2 动态 | 子 agent 只读修改后规则文件，回答关键问题 | 每批次后 | 回答错误=漂移→回滚 |

**回滚机制**：修改前备份原文件 → 测试失败 → 回滚 → 分析原因 → 重新修改 → 再测 → 连续 2 次通过才算稳定。

**关键事实清单 SSoT**：以 depgraph.db / pyproject.toml / config/mcp.json / 实际文件系统为准，不以规则文件旧声明为准。

### 23.5 不做的事项（推迟到阶段7）

| # | 推迟项 | 理由 |
| :-: | ---- | ---- |
| 1 | 大规模消除 project_rules ↔ onboarding 重复 | 阶段7规则文件格式升级时统一做 |
| 2 | 重构三层职责边界（L0瘦身/L1聚焦/AGENTS区分） | 搬家后路径稳定再做 |
| 3 | 创建缺失标准文档（code-construction-standards.md 等） | 待阶段7 |
| 4 | YAML frontmatter 大改 | 待阶段7 |
| 5 | 删除 agent_spec 引用 | 模块有蓝图（MOD-INF-019），待阶段4搬家对齐 |

### 23.6 agent_spec 处置详情

**现状**：蓝图 MOD-INF-019 存在（docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md），`construction_progress: partially_implemented`，`actual_disk_path: src/zephyr/agent-spec/`（连字符违反 Python 命名）。实际目录不存在，`python -m zephyr.agent_spec` 失败。

**数据层已落地**：data/capability_cards/ 下 22 个 skill yaml（19 域 skill_dom_* + 3 角色 skill_rol_*）。

**处置**：规则文件中 `python -m zephyr.agent_spec list` 改为引用 `data/capability_cards/skill_*.yaml`，标注"完整 CLI 待阶段4搬家后激活"。AI 能立即找到 skill 数据，不会因命令失败产生幻觉。

***

## 二十四、治理收敛期方案（阶段7b，2026-06-18 架构师裁定）

> **触发**：100% AI 开发项目治理模式评估，对标 ISO 42001 + NIST AI RMF + 氛围编程社区实践
> **性质**：架构师裁定，从"治理扩张期"转向"治理收敛期"
> **详细工作内容**：见独立文档 `docs/02_enterprise_architecture/governance_convergence_plan.md`
> **前置条件**：阶段4（搬家对齐+全量清洁）+ 阶段7（全量功能测试+规则文件格式升级）完成

### 24.1 裁定背景

基于项目文档体系全量调研 + 业界标准对标 + 量化数据采集，得出核心裁定：

**方向正确，密度偏重，运行时有缺口，需从"治理扩张期"转向"治理收敛期"。**

| 维度 | 裁定 | 依据 |
|------|------|------|
| 治理方向 | ✅ 正确 | 与 ISO 42001 + NIST AI RMF 对齐，防幻觉十八条业界领先 |
| 治理强度 | ⚠️ 偏重 | 治理脚本占 scripts/ 81.6%，处于业界"生产系统"档位上限 |
| 治理有效性 | ⚠️ 有缺口 | 142 规则 + 44 门禁未能阻止 100+ 处引用错误 |
| 治理可持续性 | ⚠️ 有风险 | 治理基础设施自身复杂度高，"治理的治理"递归 |

### 24.2 量化对标（项目 vs 业界）

| 指标 | 项目数值 | 业界基准 | 评估 |
|------|---------|---------|------|
| 治理脚本/功能代码（行数比） | 0.15x | 无基准 | — |
| scripts/ 下治理脚本占比 | 81.6%（384/489） | 无基准 | ⚠️ 异常 |
| 文档/功能代码（行数比） | 0.49x | 传统 0.05-0.1x | 5-10 倍 |
| 门禁数 | 44 个 | CI/CD 通常 5-15 个 | 3 倍 |
| 注册表数 | 48 个 | K8s api-resources ~30 | 1.6 倍 |
| 任务状态机 | 10 态 | 业界 3-5 态 | 2-3 倍 |
| 冷启动步骤 | ~20 步 | Cursor 0 步 | ⚠️ 偏重 |
| 防幻觉条律 | 18 条四层 | 业界 5 大做法 | ✅ 覆盖且更细 |

### 24.3 收敛期四阶段（P0-P3）

| 优先级 | 阶段 | 内容 | 前置条件 |
|:---:|------|------|---------|
| P0 | 修复治理基础设施自身故障 | severity_types.py 导入链 + persistence 子包引用批量修复 | 立即（已建卡 OPS-2026061802/1803） |
| P1 | 治理瘦身 | 审计 384 脚本消费者 + 退役零拦截门禁 + 合并重复规则 + 冷启动精简 | 阶段4搬家完成（路径稳定后才能审计消费者） |
| P2 | 建立治理 ROI 量化 | 每条规则/门禁/脚本记录拦截错误次数，零拦截的退役 | 阶段7全量功能测试完成（有测试基线才能量化拦截率） |
| P3 | 防幻觉机制补强 | 运行时导入健康检查 + 实时幻觉检测 + 关键链形式验证 | P0-P1 完成 |

### 24.4 收敛目标

| 指标 | 当前 | 收敛目标 | 业界区间 |
|------|------|---------|---------|
| 治理脚本占 scripts/ 比 | 81.6% | <40% | 无基准 |
| 冷启动步骤 | ~20 步 | ~10 步 | Cursor 0 步 |
| 治理开销时间占比 | 未测量 | 25-35% | 生产系统 20-35% |
| 治理绕过次数 | 未测量 | 0 | — |
| 运行时导入健康检查 | 无 | Session 启动自动验证 | — |

### 24.5 不做的事项

| # | 不做 | 理由 |
|---|------|------|
| 1 | 删除防幻觉十八条 | 业界领先，覆盖所有公认做法 |
| 2 | 降级 `[AI_AUTONOMY]` 三级分级 | 符合业界 L1-L3 企业主流 |
| 3 | 废弃注册表体系 | 可发现性基础设施，符合 NIST Govern |
| 4 | 取消任务卡粒度门禁 | R1-R6 机械判定是正确设计 |

### 24.6 与其他阶段的关系

```
阶段4（搬家对齐+清洁）→ 路径稳定
  ↓
阶段7（全量功能测试+规则文件格式升级）→ 测试基线建立
  ↓
阶段7b（治理收敛期）← 本章节
  ├─ P0: 修复治理基础设施故障（立即，不依赖阶段4/7）
  ├─ P1: 治理瘦身（依赖阶段4，路径稳定后审计消费者）
  ├─ P2: ROI量化（依赖阶段7，有测试基线才能量化拦截率）
  └─ P3: 运行时补强（依赖P0-P1）
  ↓
阶段8（业务层建设）→ 治理收敛后进入业务冲刺
```

> **核心原则**：治理收敛期不是"减少治理"，而是"让治理从纸面完备走向运行时有效"。从"加规则"转向"减规则 + 强运行时"。

