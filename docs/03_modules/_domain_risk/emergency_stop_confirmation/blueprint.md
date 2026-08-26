---
module_id: MOD-RK-36
title: "紧急停止安全确认蓝图 — 紧急停止/强平双锁二次确认 + 确认留痕"
doc_type: blueprint
status: Active
version: "0.1.1"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-25"
last_updated: "2026-08-25"
priority: P0
blueprint_level: module
design_maturity: production
build_status: stable
responsibility_domain: 
---

# MOD-RK-36 Emergency Stop Confirmation — 紧急停止安全确认 蓝图

> **module_id**: MOD-RK-36 | **域**: D_RISK | **层**: L02 盘中实时监控
> **优先级**: P0 | **来源**: CAND-RSK-039（B10-02123，D-RISK-115，AUD-DRAFT-001 裁定=做）
> **SSoT**: depgraph MOD-RK-36

## 1. 定位

kill switch 本体（MOD-INF-016）已建，缺口是**紧急操作的二次确认与不可篡改留痕**：
紧急停止（EMERGENCY_STOP）与强制平仓（FORCED_LIQUIDATION）类高危操作，必须
两名不同授权操作人双锁确认才放行，且全程留痕入哈希链可离线校验。对标
vnpy/Lean kill switch 与运维 dead-man switch 的双人授权纪律。

本模块是 MOD-INF-049 VenraDoubleLockAnchor 的风险域应用层封装（复用优先，
不重造双锁/锚定机制），加：操作类型白名单、操作人身份核验（授权名册注入）、
确认留痕导出（供加密审计链接接，D_GOV_AUDIT 消费）。

## 2. 输入 / 输出

- 输入：action_type（EMERGENCY_STOP/FORCED_LIQUIDATION）、operator（提案人）、
  reason（非空理由）、payload（操作参数）；confirm(actor, approve)；
  authorized_operators（授权名册，构造注入，空名册=Fail-Closed 全拒）。
- 输出：EmergencyActionRequest（提案凭据）+ ConfirmationVerdict
  （confirmed/rejected/pending + 放行标记）+ audit_trail()（锚定记录导出）。

## 3. 核心规则

1. 动作白名单：仅 EMERGENCY_STOP/FORCED_LIQUIDATION 两类可提案（其他拒绝）。
2. 身份核验：提案人/确认人均须在授权名册内（Fail-Closed，未登记即拒）。
3. 双锁确认：两名**不同**操作人 approve 才 confirmed 放行；任一 approve=False
   即 rejected；复用 MOD-INF-049（同人重复加锁/终态后操作由其异常透传）。
4. 留痕：终态裁定落 VenraDoubleLockAnchor 哈希链（只追加、prev_hash 链式），
   audit_trail() 导出 + verify_audit_trail() 离线校验；理由与操作参数哈希入链。
5. Fail-Closed：空理由/空操作人/未授权/未知提案 → 拒绝，不放行。

## 4. 依赖前置

- MOD-INF-049 VenraDoubleLockAnchor（双锁+锚定链复用，唯一机制真源）
- MOD-INF-016 trading_kill_switch（确认放行后的执行体，编排层接线）
- D_GOV_AUDIT（确认留痕消费方）
- scripts/deadman_switch.ps1（联动演练，Owner 窗口另行演练留证）

## 5. 验收标准

- 单测全绿（白名单/身份核验/双锁放行/拒绝即终态/同人拒绝/留痕导出与哈希链校验/
  非法输入拒绝）；tests/risk 域集成零回归。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-36`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-36` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-36` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-36 | MOD-RK-36 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 6. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/risk/core/emergency_stop_confirmation.py` | ✅ 已实现 | |

### 6.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/core/test_emergency_stop_confirmation.py` | ✅ 已实现 | |

### 6.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §6（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
