# 数据域（数据库）设计态全面排查与补全审查报告

> **审查日期**: 2026-07-24
> **审查范围**: D_DATA / D_MKT_DATA / D_DATA_ENG / D_DATA_GOV / D_DATA_SEC / D_ALT_DATA
> **审查目的**: 判断数据域是否就绪支撑因子库施工
> **审查方法**: 场外文档（D:\临时工作区）vs 场内 DB（depgraph）逐条对比

---

## 一、场外文档盘点结果（Phase 1）

### 1.1 场外文档清单

| 文档路径 | 内容摘要 |
|---|---|
| D:\临时工作区\依赖图\00-总览与索引.md | 全局索引，域清单+域间依赖矩阵 |
| D:\临时工作区\依赖图\01-跨域交叉点与因果链.md | 跨域依赖+契约矩阵+因果链+受限门禁总表 |
| D:\临时工作区\依赖图\02-D-DATA-数据域.md | D-DATA 核心设计：子模块+依赖图+契约+GATE |
| D:\临时工作区\依赖图\14-D-ALT-DATA-另类数据域.md | 另类数据域：5 骨架+12 P2扩展子模块 |
| D:\临时工作区\依赖图\15-D-DATA-ENG-数据工程域.md | 数据工程域设计 |
| D:\临时工作区\架构图\数据架构.md | 数据架构总设计（367KB，含 FeatureStore/PIT/DataObservability） |

### 1.2 场外文档提取的 6 类条目

#### A. D-DATA 子模块清单（来自 01-跨域交叉点）

| 模块ID | 名称 | 场外状态 | 场内对应 |
|---|---|:---:|---|
| C-001 | 多源数据接入 | ✅ | src/zephyr/data/implementations/（11 个 provider） |
| C-022 | 数据质量自管理 | ✅ | src/zephyr/data/cross_source_validator.py + quality_gate.py |
| D-DATA-02 | NormalizedMarketData生成 | ⛔ | **缺失**（仅契约 dataclass，无生产者） |
| D-DATA-03 | FeatureStore | ✅ | 场内无独立 FeatureStore 模块（pit_query.py 部分覆盖） |
| D-DATA-05 | 数据质量监控 | ✅ | src/zephyr/data/quality_gate.py + integrity_checker.py |
| D-DATA-06 | 数据血缘追踪 | ✅ | 场内无独立 lineage 模块 |
| D-DATA-07 | 数据调度器 | ✅ | src/zephyr/data/scheduler.py |
| D-DATA-08 | 数据压缩与归档 | ✅ | src/zephyr/data/wal_codec/ + wal_writer.py |
| D-DATA-10 | DataQualityScorer | ✅ | src/zephyr/data/quality_gate.py |
| — | PIT一致性保证 | ✅ | src/zephyr/data/pit_query.py |
| — | 双时态建模 | ✅ | 场内未独立实现（pit_query 部分覆盖） |
| — | DataObservability | ✅ | 场内无独立模块 |
| — | FWT检索增强扩散 | ⛔ | 场内无 |

#### B. D-ALT-DATA 子模块清单（来自 14-D-ALT-DATA）

| 模块ID | 名称 | 场外状态 | 场内对应 |
|---|---|:---:|---|
| D-ALT-DATA-01 | AltDataConnector | 骨架 | src/zephyr/alt_data/（仅 __init__.py） |
| D-ALT-DATA-02 | SentimentEngine | 骨架 | 无实现 |
| D-ALT-DATA-03 | FilingNLPEngine | 骨架 | 无实现 |
| D-ALT-DATA-04 | SupplyChainGraphEngine | 骨架 | 无实现 |
| D-ALT-DATA-05 | AltDataSignalExtractor | 骨架 | 无实现 |
| D-ALT-DATA-05~17 | P2扩展（13个） | P2 | 无实现 |

#### C. 跨域契约（来自 01-跨域交叉点）

| 契约ID | 名称 | 生产者 | 消费者 | 场外状态 |
|---|---|---|---|:---:|
| CTR-001 | NormalizedMarketData | D-DATA(L00) | D-FACTOR等 | ⛔ Python文件缺失 |
| CTR-ERR-001 | DataQualityError | D-DATA(L00) | D-FACTOR | 未明确 |
| CTR-TRACE-001 | TraceContext | D-DATA(L00) | *(all) | 未明确 |

#### D. 受限门禁（来自 01-跨域交叉点）

| 门禁ID | 受限原因 | 建设门禁 |
|---|---|---|
| CP-03 | NormalizedMarketData Python文件缺失 | D-DATA-02生成Python实现 |
| CP-08 | 单卡GPU硬件约束 | GPU扩容或MOD-INF-011推理调度策略就绪 |

#### E. 数据架构.md 增量设计

| 模块 | 场内有无 | 增量信息 |
|---|:---:|---|
| FeatureStore (D-DATA-03) | ❌ 独立模块 | 离线PIT+在线Serving+四维索引 |
| PIT Manager | ❌ | DuckDB AS OF JOIN时间旅行查询 |
| DataObservability (D-DATA-23) | ❌ | 新鲜度监控+Schema漂移+SLA |
| Data Lineage (D-DATA-06) | ❌ 独立模块 | OpenLineage标准+列级血缘 |
| Data Mesh (§17) | ❌ | 未来架构方向 |

---

## 二、场内 DB 现状（Phase 2）

### 2.1 节点统计（共 118 个数据相关域节点）

| 域 | production | design | deprecated | 合计 | 实际实现 |
|---|:---:|:---:|:---:|:---:|---|
| **D_DATA（旧轨）** | 83 | 2 | 2 | 87 | ✅ 核心功能已实现 |
| D_MKT_DATA（新轨） | 7 | 0 | 0 | 7 | ❌ 仅 __init__.py 骨架 |
| D_DATA_ENG | 7 | 0 | 0 | 7 | ❌ 仅 __init__.py 骨架 |
| D_DATA_GOV | 7 | 0 | 0 | 7 | ❌ 仅 __init__.py 骨架 |
| D_DATA_SEC | 7 | 0 | 0 | 7 | ❌ 仅 __init__.py 骨架 |
| D_ALT_DATA | 7 | 0 | 0 | 7 | ❌ 仅 __init__.py 骨架 |

### 2.2 D_DATA 已实现的核心模块（83 production 节点）

**数据接入层**：11 个 provider（akshare/baostock/cls/eastmoney_news/ifind/miniqmt/rss/tdx/tickflow/tushare）
**存储层**：ch_writer.py / ch_reader.py / ch_config.py / table_registry.py / buffered_writer.py / wal_writer.py / wal_codec/
**质量管控**：quality_gate.py / integrity_checker.py / cross_source_validator.py / capability_validator.py / error_classifier.py
**PIT 查询**：pit_query.py（production + design 蓝图节点各 1）
**调度**：scheduler.py / task_queue.py / progress_store.py / backfill_checker.py / alerter.py
**处理**：kline_resampler.py / news_dedup.py / trading_calendar.py / sector_*.py
**冗余**：redundant_source/（recovery/heartbeat_monitor/sqlite_fallback/source_switcher/backup_tick_poller）
**Schema**：schemas/categories/ 15 个表结构定义
**DDL 脚本**：scripts/ch/ 5 个（apply_market/fundamental_tables_ddl/apply_rbac/apply_timezone_migration/_data_inventory/_recovery_drill）

### 2.3 边统计（239 条）

- 域内边（D_DATA→D_DATA）：约 170 条，全是实际代码 import 依赖（active）
- 跨域边（D_DATA→其他域）：约 30 条
  - D_DATA → D_SHARED（15条）：metrics/paths/secrets/time_utils/constants
  - D_DATA → D_GOV_ENFORCEMENT（3条）：quality_gate
  - D_DATA → D_INFRA_RUNTIME（1条）：database_service→ch_config
  - D_BACKTEST → D_DATA（2条）：data_handler→ch_reader
  - D_GOVERNANCE → D_DATA（3条）：memory_provider→provider_base/policy_registry
  - D_GOV_CODE_QUALITY → D_DATA（2条）：capability_validator/table_registry
  - D_GOV_SCRIPTS → D_DATA（4条）：data_inventory/check_tick_duplication
- 新轨4域边：仅 1 条（src/zephyr/market_data/__init__.py → src/zephyr/shared/contracts/market_data.py）

### 2.4 契约状态

| 契约ID | 名称 | provider_domain | fulfillment_status | 实际状态 |
|---|---|---|---|---|
| CTR-001 | NormalizedMarketData | D_MKT_DATA | **planned** | ⚠️ 契约 dataclass 已实现并被 10+ 模块消费，但生产者缺失 |
| CTR-ERR-001 | DataQualityError | D_MKT_DATA | **unresolved** | ⚠️ 状态滞后 |
| CTR-TRACE-001 | TraceContext | D_MKT_DATA | **planned** | ⚠️ TraceContext 已实现（src/zephyr/shared/contracts/core/trace_context.py） |

---

## 三、逐条对比审查（Phase 3）

### 3.1 核心裁定原则

1. **场内是真源**：场内 D_DATA 的 83 个 production 节点是实际代码，场外文档描述的是设计/规划
2. **场外文档状态滞后**：场外文档标记 D-DATA 子模块为 ✅，但实际是场内 D_DATA 已实现，不是场外文档驱动实现的
3. **新轨4域是未来重构方向**：D_MKT_DATA/D_DATA_ENG/D_DATA_GOV/D_DATA_SEC 是规划中的域拆分，当前只有空骨架
4. **不阻塞因子库施工**：因子库依赖的 CTR-001 契约类型已实现，回测数据可通过 ch_reader 获取

### 3.2 逐条审查清单

#### A. 子模块审查

| 场外条目 | 场内有？ | 场内更完整？ | 场外更详细？ | 冲突？ | **裁定** |
|---|:---:|:---:|:---:|:---:|---|
| C-001 多源数据接入 | ✅ | ✅（11 provider） | ❌ | ❌ | **跳过**（场内已实现） |
| C-022 数据质量自管理 | ✅ | ✅ | ❌ | ❌ | **跳过** |
| D-DATA-02 NormalizedMarketData生成 | ❌ | ❌ | ✅ | ❌ | **搬入**（登记 design 节点） |
| D-DATA-03 FeatureStore | ❌ 独立模块 | ❌ | ✅ | ❌ | **搬入**（登记 design 节点） |
| D-DATA-05 数据质量监控 | ✅ | ✅ | ❌ | ❌ | **跳过** |
| D-DATA-06 数据血缘追踪 | ❌ 独立模块 | ❌ | ✅ | ❌ | **搬入**（登记 design 节点） |
| D-DATA-07 数据调度器 | ✅ | ✅ | ❌ | ❌ | **跳过** |
| D-DATA-08 数据压缩与归档 | ✅ | ✅ | ❌ | ❌ | **跳过** |
| D-DATA-10 DataQualityScorer | ✅ | ✅ | ❌ | ❌ | **跳过** |
| PIT一致性保证 | ✅ | ✅ | ❌ | ❌ | **跳过** |
| DataObservability | ❌ | ❌ | ✅ | ❌ | **搬入**（登记 design 节点） |
| FWT检索增强扩散 | ❌ | ❌ | ✅ | ❌ | **跳过**（P2级，非因子库依赖） |
| D-ALT-DATA-01~05 | ❌ 骨架 | ❌ | ✅ | ❌ | **跳过**（P2级，非因子库依赖） |

#### B. 契约审查

| 契约ID | 场内状态 | 场外状态 | 冲突？ | **裁定** |
|---|---|---|:---:|---|
| CTR-001 | dataclass 已实现，生产者缺失，DB=planned | ⛔ Python文件缺失 | ✅ | **合并**（更新 fulfillment_status: planned→generated） |
| CTR-ERR-001 | DB=unresolved | 未明确 | ❌ | **搬入**（更新 fulfillment_status: unresolved→generated） |
| CTR-TRACE-001 | TraceContext 已实现，DB=planned | 未明确 | ✅ | **合并**（更新 fulfillment_status: planned→generated） |

#### C. GATE 门禁审查

| 门禁ID | 场内状态 | 场外描述 | **裁定** |
|---|---|---|---|
| CP-03 | D_MKT_DATA 空骨架 | Python文件缺失，门禁=D-DATA-02生成 | **搬入**（gate_reason 注解到 D_MKT_DATA 节点） |
| CP-08 | GPU 硬件约束 | 单卡RTX3090 | **跳过**（与数据域无关，属 ML 域） |

#### D. 依赖关系审查

| 场外依赖 | 场内有？ | **裁定** |
|---|:---:|---|
| D_MKT_DATA → D_SHARED（contracts） | ✅（1条边） | **跳过**（已存在） |
| D_DATA 域内依赖 | ✅（170条） | **跳过**（已存在） |
| D_DATA → D_SHARED | ✅（15条） | **跳过**（已存在） |
| 新轨4域域内依赖 | ❌ | **跳过**（空骨架，无需登记域内边） |

---

## 四、搬入清单（Phase 4）

### 4.1 契约 fulfillment_status 修复（3 条）

| 契约ID | 当前值 | 目标值 | 理由 |
|---|---|---|---|
| CTR-001 | planned | generated | dataclass 已实现于 src/zephyr/shared/contracts/market_data.py，被 10+ 模块消费 |
| CTR-ERR-001 | unresolved | generated | DataQualityError 契约已实现 |
| CTR-TRACE-001 | planned | generated | TraceContext 已实现于 src/zephyr/shared/contracts/core/trace_context.py |

**修改方式**：contracts 表 fulfillment_status 字段不在 sync_yaml_to_depgraph.py 同步范围内（sync 不处理此字段），需直接 UPDATE DB。fulfillment_status 合法值：planned/generated/testing/stable/deprecated。

### 4.2 design 节点登记（4 个，供后续施工参考）

| 节点 path | blueprint_id | subdomain_id | gate_reason | 说明 |
|---|---|---|---|---|
| src/zephyr/market_data/normalized_market_data_producer/ | MOD-MKT_DATA | MKT-CORE | CP-03: 需D-DATA-02生成NormalizedMarketData Python实现 | NormalizedMarketData 生产者 |
| src/zephyr/data/feature_store/ | MOD-L00-004 | DATA-ENG | D-DATA-03: 离线PIT+在线Serving+四维索引 | FeatureStore 独立模块 |
| src/zephyr/data/data_lineage/ | MOD-L00-004 | DATA-GOV | D-DATA-06: OpenLineage标准+列级血缘 | 数据血缘追踪独立模块 |
| src/zephyr/data/data_observability/ | MOD-L00-004 | DATA-GOV | D-DATA-23: 新鲜度监控+Schema漂移+SLA | DataObservability 模块 |

### 4.3 subdomain_id 补全（已有节点）

| 域 | 节点 path 前缀 | subdomain_id |
|---|---|---|
| D_MKT_DATA | src/zephyr/market_data/ | MKT-CORE |
| D_DATA_ENG | src/zephyr/data_eng/ | DATA-ENG |
| D_DATA_GOV | src/zephyr/data_governance/ | DATA-GOV |
| D_DATA_SEC | src/zephyr/data_security/ | DATA-SEC |
| D_ALT_DATA | src/zephyr/alt_data/ | ALT-CORE |
| D_DATA（已实现核心） | src/zephyr/data/ | DATA-CORE |

### 4.4 不搬入的内容（审查后跳过）

- 场内 D_DATA 已实现的 83 个 production 节点（场内是真源）
- 场外文档描述的 D-ALT-DATA 子模块（P2级，非因子库依赖）
- 场外文档描述的 FWT检索增强扩散（P2级）
- 场外文档描述的 Data Mesh（未来架构方向）
- 新轨4域的域内依赖边（空骨架，无实际依赖）

---

## 五、最终判断（Phase 8）

### 5.1 数据域是否就绪可支撑因子库施工？

**结论：✅ 就绪（契约层+回测层），⚠️ 部分缺口（实时生产者层）**

| 因子库需求 | 就绪状态 | 说明 |
|---|:---:|---|
| CTR-001 NormalizedMarketData 类型 | ✅ | dataclass 已实现，因子库可 import 使用 |
| 历史行情数据（回测） | ✅ | ch_reader.py 已 production，可读 ClickHouse |
| 因子库已有消费先例 | ✅ | factor/momentum_factor.py + value_factor.py 已消费 NormalizedMarketData |
| 实时 NormalizedMarketData 实例生产 | ⛔ | D_MKT_DATA 生产者缺失（design 节点已登记） |
| 数据质量管控 | ✅ | quality_gate.py + integrity_checker.py 已 production |
| PIT 查询 | ✅ | pit_query.py 已 production |

### 5.2 缺口是什么？

**唯一阻塞实时施工的缺口**：D-DATA-02 NormalizedMarketData 生产者
- 契约类型已就绪（因子库可基于类型开发）
- 回测数据已就绪（ch_reader 可读历史行情）
- **实时生产者缺失**（需要实现 src/zephyr/market_data/ 下的标准化服务，将 ch_reader 读取的原始行情转换为 NormalizedMarketData 实例）

**非阻塞缺口**（供后续施工参考，已登记 design 节点）：
- FeatureStore（D-DATA-03）：独立特征存储模块
- Data Lineage（D-DATA-06）：独立数据血缘模块
- DataObservability（D-DATA-23）：数据可观测性模块

### 5.3 施工顺序建议

**建议路径：先施工因子库，并行实现 NormalizedMarketData 生产者**

1. **立即施工因子库**（不阻塞）：
   - 因子库基于 CTR-001 NormalizedMarketData 契约类型开发
   - 回测使用 ch_reader.py 读取历史行情，构造 NormalizedMarketData 实例
   - 参考 factor/momentum_factor.py + value_factor.py 已有先例

2. **并行实现 NormalizedMarketData 生产者**（D-DATA-02）：
   - 在 src/zephyr/market_data/ 下实现标准化服务
   - 输入：ch_reader 读取的原始行情数据
   - 输出：NormalizedMarketData 实例（供实时因子计算消费）
   - 完成后 CTR-001 fulfillment_status: generated → stable

3. **后续完善数据域**（非阻塞，按需）：
   - FeatureStore / Data Lineage / DataObservability（已登记 design 节点）
   - D-ALT-DATA 子模块（P2级，按需启动）

### 5.4 治理状态修复

本次排查发现 3 个契约的 fulfillment_status 滞后于代码实现，本次补全会修复：
- CTR-001: planned → generated
- CTR-ERR-001: unresolved → generated
- CTR-TRACE-001: planned → generated

---

## 六、执行清单总结

| 步骤 | 操作 | 工具 |
|---|---|---|
| Step 1 | 补全 6 个数据域节点的 subdomain_id | apply_depgraph.py `_load_depgraph` + `_atomic_write` |
| Step 2 | 登记 4 个 design 节点（含 gate_reason） | apply_depgraph.py `--add-design-node` |
| Step 3 | 修复 3 个契约的 fulfillment_status | 直接 UPDATE contracts 表（sync 不处理此字段） |
| Step 4 | 四图对齐验证 | sync_panorama_module.py + align_panoramas.py |
| Step 5 | GitCommitGateway 提交 | python scripts/git_commit.py |
