---
module_id: MOD-POS-026
title: "护盘资产定向加仓白名单蓝图 — 熔断期窄门三重门"
doc_type: blueprint
status: Active
version: "0.1.3"
design_maturity: production
ttl: permanent
layer: L03_position
layer_name: position
functional_domain: position
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-09-10"
last_updated: "2026-09-10"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-POS-026 Defensive Asset Whitelist — 护盘资产定向加仓白名单 蓝图

> **module_id**: MOD-POS-026 | **域**: D_POSITION | **层**: L03 仓位管理
> **优先级**: P0 | **成熟度**: L1 骨架（默认休眠）| **建设标记**: ✅可建
> **裁定真源**: 69 号备忘录 §2.33 D114（proposed 假说，Owner"熔断可加仓国家队护盘资产"）+ 地图节点 TDM-X-R1-03
> **消费节点**: TDM-X-R1-03（熔断期窄门：开不开、买什么、买多少）

## 1. 定位

熔断期（L2/L3）唯一允许的**买入**通道：三重门全过才开窄门，只买白名单内护盘资产，
金字塔法分批，仓位受 D107 尾部弹药预算约束（上限总资金 5-10%）。

**休眠铁律（D114）**：回测验证前整节点休眠——`enabled` 默认 False，任何调用返回
DISALLOWED（fail-closed），杜绝未验证假说带病入市。

**风险声明（D114 原文）**：政策底≠市场底（历史滞后 40 天~半年：2008 滞后 40 天 /
2015 滞后半年 / 2018 滞后 2.5 月，财联社复盘）——分批+确认信号是铁律，严禁一次到位。

## 2. 三重门（全过才开窄门）

| 门 | 判据 | 依据 |
|---|---|---|
| ①状态门 | 熔断级 ∈ {L2 禁开仓, L3 减仓}（drawdown_state_machine 五级） | X-R1-01 |
| ②信号门 | D110 超跌反转信号（KDJ J<-10 + 量能>20 日均量 2 倍 + 无系统性利空）**或** 国家队明牌信号（ETF 天量成交 / 官方增持公告） | D110+D114 |
| ③分批门 | 金字塔法：首笔 1/3 预算；第 2/3 笔须"确认收复"（三重门再次全过）才放行 | D114 |

## 3. 白名单（方向=买入核对，来源固化）

| 层 | 资产（代码为经验拍定默认值，config 可注入） |
|---|---|
| T1 宽基 ETF（优先） | 510300 沪深300ETF / 510500 中证500ETF / 512100 中证1000ETF / 510880 红利ETF |
| T2 银行/高股息（次之） | 512800 银行ETF / 512890 红利低波ETF |

## 4. 输入 / 输出

| 方向 | 内容 |
|------|------|
| 输入 | 熔断级、D110 信号（含 KDJ J 值/量比/系统性利空布尔）、国家队信号、标的、方向、尾部弹药预算、总资金、已投额、已加分笔数、确认收复旗标 |
| 输出 | DefensiveVerdict：allowed + reason_codes + tier + 分笔计划（Decimal 金额） |

纯函数核心（同输入必同输出），零 IO；预算计算 Decimal-only 拒 float（对标
plan_deviation_monitor 口径）。

## 5. 不变量

1. `enabled=False`（默认）→ 恒 DISALLOWED（DORMANT），fail-closed。
2. 方向非 BUY → DISALLOWED（DIRECTION_NOT_BUY）——白名单语义只买不卖。
3. 状态门/信号门/分批门逐门短路，首败即拒并留 reason_code（可审计）。
4. 计划总投额 ≤ min(尾部弹药预算, 总资金×上限比例)；上限默认 10%（5-10% 区间上限）。
5. 分笔上限 3 笔；第 2/3 笔无确认收复旗标 → 拒（CONFIRMATION_REQUIRED）。

## 6. 消费方

TDM-X-R1-03 节点（决策地图）；未来由 X-R1-01 drawdown_state_machine 在 L2/L3 转入时调用。

---

## 7. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 7.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/position/core/defensive_asset_whitelist.py` | ✅ 已实现 | |

### 7.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/position/test_defensive_asset_whitelist.py` | ✅ 已实现 | |

### 7.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §7（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-POS-026`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-POS-026` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-POS-026` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-POS-026 | MOD-POS-026 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
