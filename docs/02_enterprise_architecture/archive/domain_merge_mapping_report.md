# 域归并映射报告

> **任务卡**: DM-100255
> **directive**: PANORAMA-REBUILD
> **源文档**: architecture_upgrade_discussion.md §2.1 / §17.6（39域方案）
> **数据源**: depgraph.db domains 表（52 D-XXX 域，DM-100253 清理后）
> **状态**: 只读分析，DB 归并操作在阶段4搬家对齐时执行

---

## 一、差异概述

| 项目 | 数量 | 说明 |
|------|:---:|------|
| DB domains 表 D-XXX 域 | 52 | DM-100253 清理小写域后 |
| 架构升级 39 域方案 | 39 | architecture_upgrade_discussion.md §17.6 |
| 差异域数 | 13 | 52 - 39 = 13 |
| 保留独立域 | 39 | 39 域方案中的域全部在 DB 中存在 |
| 合并域 | 12 | 不在 39 域方案中，合并到父域 |
| 删除域 | 1 | D-TEST（design_only，无实际模块） |
| 新建域 | 0 | 39 域方案中所有域均在 DB 中存在 |

**差异根因**：DB 中 8 个 D-GOV-* 子域 + 4 个 *-CONTRACTS/GATEWAY/LLM 子域为历史拆分，39 域方案裁定不再独立，需合并回父域；D-TEST 为测试域（design_only/unbuilt/current_modules=0），需删除。

---

## 二、归并映射表（全 52 域）

### 2.1 保留独立域（39 域）

以下 39 域在 39 域方案中存在，保留独立，无需归并。

| # | 域ID | 域名 | 分组 | 39域方案序号 |
|---|------|------|:---:|:---:|
| 1 | D-MKT_DATA | 行情数据(接入+存储) | 业务 | 1 |
| 2 | D-DATA_ENG | 数据工程(增值+融合+知识) | 业务 | 2 |
| 3 | D-DATA_GOV | 数据治理(质量+血缘+参考) | 业务 | 3 |
| 4 | D-DATA_SEC | 数据安全与契约 | 业务 | 4 |
| 5 | D-FACTOR | 因子 | 业务 | 5 |
| 6 | D-SIGNAL | 信号(技术+通用) | 业务 | 6 |
| 7 | D-SIGNAL_ASHARE | A股特色信号 | 业务 | 7 |
| 8 | D-SIGNAL_FUNDAMENTAL | 基本面信号 | 业务 | 8 |
| 9 | D-SIGNAL_QUALITY | 信号质量 | 业务 | 9 |
| 10 | D-PF_CORE | 组合核心 | 业务 | 10 |
| 11 | D-PF_ALLOC | 组合分配 | 业务 | 11 |
| 12 | D-SELL_DECISION | 卖出决策 | 业务 | 12 |
| 13 | D-POSITION | 仓位管理 | 业务 | 13 |
| 14 | D-EX_CORE | 执行核心 | 业务 | 14 |
| 15 | D-EX_SOR | 执行路由 | 业务 | 15 |
| 16 | D-REPORTING | 报告 | 业务 | 16 |
| 17 | D-RISK | 风控 | 业务 | 17 |
| 18 | D-ML_TRAIN | 训练 | 业务 | 18 |
| 19 | D-ML_SERVE | 推理 | 业务 | 19 |
| 20 | D-ALT_DATA | 另类数据 | 业务 | 20 |
| 21 | D-CROSS_ASSET | 跨资产 | 业务 | 21 |
| 22 | D-COMPLIANCE | 合规 | 业务 | 22 |
| 23 | D-TRADING | 交易运营 | 业务 | 23 |
| 24 | D-SIMULATION | 仿真核心 | 业务 | 24 |
| 25 | D-BACKTEST | 回测验证 | 业务 | 25 |
| 26 | D-EXEC_SIM | 执行仿真 | 业务 | 26 |
| 27 | D-DIGITAL_TWIN | 数字孪生 | 业务 | 27 |
| 28 | D-GOVERNANCE | 治理 | 平台 | 28 |
| 29 | D-SECURITY | 安全 | 平台 | 29 |
| 30 | D-AUTONOMY_CORE | 自治核心 | 平台 | 30 |
| 31 | D-AUTONOMY_PERM | 自治保护 | 平台 | 31 |
| 32 | D-INFRA_RUNTIME | 运行时基础设施 | 平台 | 32 |
| 33 | D-INFRA_OPS | 运维基础设施 | 平台 | 33 |
| 34 | D-OPS | 运维 | 平台 | 34 |
| 35 | D-INTEGRATION | 集成 | 平台 | 35 |
| 36 | D-KNOWLEDGE | 知识 | 平台 | 36 |
| 37 | D-INTELLIGENCE | 智能 | 平台 | 37 |
| 38 | D-FRONTEND | 前端 | 平台 | 38 |
| 39 | D-SHARED | 共享 | 横切 | 39 |

### 2.2 合并域（12 域）

以下 12 域不在 39 域方案中，需合并到对应父域。合并操作在阶段4搬家对齐时执行。

| # | 源域ID | 源域名 | 目标域ID | 目标域名 | 合并理由 |
|---|--------|--------|----------|----------|----------|
| 1 | D-GOV-AUDIT | 治理-审计 | D-GOVERNANCE | 治理 | D-GOV-* 为治理域历史子域拆分，39域方案裁定合并为单一 D-GOVERNANCE |
| 2 | D-GOV-DOCS | 治理文档 | D-GOVERNANCE | 治理 | 同上 |
| 3 | D-GOV-DRIFT | 治理-漂移检测 | D-GOVERNANCE | 治理 | 同上 |
| 4 | D-GOV-ENFORCEMENT | 治理-规则执行 | D-GOVERNANCE | 治理 | 同上 |
| 5 | D-GOV-REPAIR | 治理修复 | D-GOVERNANCE | 治理 | 同上 |
| 6 | D-GOV-SCRIPTS | 治理脚本 | D-GOVERNANCE | 治理 | 同上 |
| 7 | D-GOV-SCRIPTS-ARCH | 治理脚本-架构 | D-GOVERNANCE | 治理 | 同上 |
| 8 | D-GOV-SCRIPTS-META | 治理脚本-元数据 | D-GOVERNANCE | 治理 | 同上 |
| 9 | D-INTEGRATION-GATEWAY | 集成网关 | D-INTEGRATION | 集成 | 集成网关为集成域子功能，39域方案不独立 |
| 10 | D-SECURITY-LLM | 安全-LLM防御 | D-SECURITY | 安全 | LLM防御为安全域子功能，39域方案不独立 |
| 11 | D-SHARED-CONTRACTS | 共享-契约 | D-SHARED | 共享 | 契约为共享域子功能，39域方案不独立 |
| 12 | D-TRADING-CONTRACTS | 交易-契约 | D-TRADING | 交易运营 | 契约为交易运营域子功能，39域方案不独立 |

**合并操作说明**（阶段4执行）：
1. 将源域 nodes 表中所有节点的 domain_id 更新为目标域ID
2. 将源域 arch_domain_capacity 记录的 current_modules 累加到目标域
3. 将源域 arch_domain_layers 记录删除（目标域已有记录）
4. 将源域 domain_dependencies 中的 domain_id 更新为目标域ID
5. 删除源域 domains 表记录
6. 验证目标域 current_modules 不超过 max_modules（超容则触发拆分）

### 2.3 删除域（1 域）

以下 1 域不在 39 域方案中，且无实际模块，需删除。

| # | 域ID | 域名 | domain_group | current_modules | lifecycle | build_status | 删除理由 |
|---|------|------|:---:|:---:|------|------|----------|
| 1 | D-TEST | Test Domain | testing | 0 | design_only | unbuilt | 测试域，无实际模块，39域方案无此域 |

**删除操作说明**（阶段4执行）：
1. 确认 nodes 表无 domain_id='D-TEST' 的节点（current_modules=0）
2. 删除 arch_domain_layers 中 domain_id='D-TEST' 的记录
3. 删除 arch_domain_capacity 中 domain_id='D-TEST' 的记录
4. 删除 domain_dependencies 中 domain_id='D-TEST' 的记录
5. 删除 domains 表中 domain_id='D-TEST' 的记录

---

## 三、归并后预期状态

| 项目 | 归并前 | 归并后 | 变化 |
|------|:---:|:---:|:---:|
| domains 表域数 | 52 | 39 | -13 |
| arch_domain_layers 表域数 | 52 | 39 | -13 |
| arch_domain_capacity 表域数 | 52 | 39 | -13 |
| D-GOVERNANCE current_modules | (现有) | (现有+8个子域) | +8个子域模块 |
| D-INTEGRATION current_modules | (现有) | (现有+D-INTEGRATION-GATEWAY) | +网关模块 |
| D-SECURITY current_modules | (现有) | (现有+D-SECURITY-LLM) | +LLM防御模块 |
| D-SHARED current_modules | (现有) | (现有+D-SHARED-CONTRACTS) | +契约模块 |
| D-TRADING current_modules | (现有) | (现有+D-TRADING-CONTRACTS) | +契约模块 |

---

## 四、容量风险预警

归并后需检查目标域是否超容（max_modules 上限）。以下为需关注的域：

| 目标域 | max_modules | 预计归并后 current_modules | 风险等级 | 处置建议 |
|--------|:---:|:---:|:---:|----------|
| D-GOVERNANCE | (待查) | (现有+8子域) | 高 | 若超 80 需按 §17.5 拆分 |
| D-INTEGRATION | (待查) | (现有+网关) | 低 | 单子域合并，风险小 |
| D-SECURITY | (待查) | (现有+LLM防御) | 低 | 单子域合并，风险小 |
| D-SHARED | (待查) | (现有+契约) | 低 | 单子域合并，风险小 |
| D-TRADING | (待查) | (现有+契约) | 低 | 单子域合并，风险小 |

> **注**：D-GOVERNANCE 合并 8 个子域后可能超容，阶段4搬家对齐时需优先检查。若超容，按 architecture_upgrade_discussion.md §17.5 裁定（>80 必须拆分）处理。

---

## 五、执行时机

| 阶段 | 操作 | 说明 |
|:---:|------|------|
| 阶段3（本批次） | 仅分析输出本报告 | DM-100255 只读 DB，不修改 |
| 阶段4（搬家对齐） | 执行归并操作 | 域归并需与目录搬家同步，避免域归属混乱 |
| 阶段4后 | 容量复查 | 归并后检查目标域是否超容，超容则拆分 |

---

## 六、数据来源验证

| 数据 | 来源 | 验证方式 |
|------|------|----------|
| 52 D-XXX 域清单 | depgraph.db domains 表 | `SELECT domain_id, domain_name, domain_group FROM domains ORDER BY domain_id` |
| 39 域方案 | architecture_upgrade_discussion.md §17.6 | 逐域对照表格 |
| D-TEST 状态 | depgraph.db domains 表 | current_modules=0, lifecycle=design_only, build_status=unbuilt |
| D-GOV-* 子域 | depgraph.db domains 表 | 8 个 D-GOV-* 域（AUDIT/DOCS/DRIFT/ENFORCEMENT/REPAIR/SCRIPTS/SCRIPTS-ARCH/SCRIPTS-META） |

---

## 七、验收检查

| 验收项 | 状态 | 说明 |
|--------|:---:|------|
| 覆盖全部 52 D-XXX 域 | ✅ | 39 保留 + 12 合并 + 1 删除 = 52 |
| 每个域有明确归并去向 | ✅ | 保留/合并/删除 三类明确 |
| 39 域方案全覆盖 | ✅ | 39 域方案中所有域均在 DB 中存在 |
| 差异数 = 13 | ✅ | 12 合并 + 1 删除 = 13 |
| 合并目标域明确 | ✅ | 每个合并域有唯一目标父域 |
| 删除理由充分 | ✅ | D-TEST 无模块、design_only、unbuilt |
