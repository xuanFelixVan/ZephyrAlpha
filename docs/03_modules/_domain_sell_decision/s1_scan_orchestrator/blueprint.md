---
module_id: MOD-SELL-016
title: "S1 信号扫描编排器蓝图 — 事件触发单次扫描串S1族至S2-01路由口"
doc_type: blueprint
status: Active
version: "0.1.1"
ttl: permanent
design_maturity: production
layer: L03_sell_decision
layer_name: sell_decision
functional_domain: sell_decision
responsibility_domain: 
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-09-28"
last_updated: "2026-09-28"
priority: P0
blueprint_level: module
---

# MOD-SELL-016 | S1 Signal Scan Orchestrator 信号扫描编排器

> **域**: D_SELL_DECISION | **层**: L03 卖出决策 | **优先级**: P0 | **safety**: L | **ai_autonomy**: ai_modifiable
> **状态**: testing | **版本**: 0.1.0 | **SSoT**: depgraph MOD-SELL-016
> **真源案卷**: docs/_working/fullconnect_campaign/e_decision_chain/09_f45_s1_sell_signal.md §四 G45-1

## 1. 模块定位

G45-1 治缺口件——09_f45 案卷实证 S1 全族纯库挂机（`from zephyr.sell_decision` 包外零消费者，
离场实际靠人）。本模块把 TDM-X-S1 六节点串成**一次可被事件/既有槽位触发的扫描**：
providers 产信号 → S1-05 融合出 willingness → 紧迫度评分 → 结构化信封投递 S2-01 路由口
（f46 卷 S2-01 入口的消费契约）。无常驻线程，无 cron/sleep-loop（宪法 §9.3）。

## 2. 不变量 (INVARIANTS)

- **单次触发语义**: `scan_once` 纯编排无内部循环；节拍责任在槽位持有方。
- **共享单循环（D104）**: `triage_levels` 必须来自与 P1-02 position_triage 同一扫描循环，
  本模块只随信封留痕不二次判定——防两套 ticker。
- **paper 档硬默认**: 构造期禁 live（G45-1 处方先 paper 档）；live 须 `scan_once(allow_live=True)`
  单次显式解锁。
- **诚实空跑**: 零 provider/零信号 → `empty_run=True`，不伪造信号不假装消费。
- **显式跳过留痕**: 未接线节点（provider 未注册/触发扫描件未建）逐节点 `NodeTrace` 留痕。
- **验证态如实披露**: 18 节点台账（VAL-20260909-164042）全 `pending` 以常量携带，
  刻意不连业务库（宪法 §9.1），不升格不猜测。
- **分工红线（09_f45 勘误 3）**: KillSwitch 组合级熔断归 X-R1/F47 既有横切线；
  本模块 S1-06 侧只收单仓强清触发（黑天鹅/K≥3/主力弃庄）。
- **故障隔离**: 单 provider/触发源/sink 故障隔离为 trace，不阻断其余节点（同 collector 契约）。

## 3. S2-01 路由口契约

`S1RouteEnvelope` schema=`TDM-X-S2-01_INBOX/v1`：scan_id/node_id/symbol/mode/willingness/
urgency/execution_strategy/validation_state/reason/contributing_signal_count/created_at/payload
（triage 留痕）。`S2RouteSink` 协议三实现：InMemorySink（默认/影子）、FileOutboxSink
（paper 档 JSONL append-only，默认落 `data/runtime/s1_scan_outbox/`）、f46 卷 S2-01 执行器
（未来替换实现，编排器零改动）。

## 4. 就绪面（机生勿抄）

`readiness()` 六节点盘点：code_ready（module_ref 在盘，S1-06 真身在 src/zephyr/trading/）、
validation_state（全 pending）、wired（结构位常在/provider 已注册）。缺省构造=诚实空跑：
结构位（S1-01/S1-05）在但无信号源，判定族与绕过通道显式跳过。

## 5. 上下游

- **上游**: S1-01 collector providers；S1-02/03/04 node providers；S1-06 bypass triggers。
- **下游**: S2-01 路由口（f46 卷 TDM-X-S2-01 执行方式路由）。

## 6. 测试面

tests/sell_decision/test_s1_scan_orchestrator.py（18 用例）：档位硬锁/诚实空跑/就绪面披露/
显式跳过留痕/投递 mock+tmp_path 落盘/sink 故障隔离/绕过通道/共享 triage 留痕/报告可序列化。

---

## 7. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 7.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/sell_decision/core/s1_scan_orchestrator.py` | ✅ 已实现 | |

### 7.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/sell_decision/test_s1_scan_orchestrator.py` | ✅ 已实现 | |

### 7.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §7（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SELL-016`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SELL-016` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-SELL-016` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SELL-016 | MOD-SELL-016 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
