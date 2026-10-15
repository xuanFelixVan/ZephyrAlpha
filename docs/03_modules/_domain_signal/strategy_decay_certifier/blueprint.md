---
blueprint_id: MOD-SIG-150
module_id: MOD-SIG-150
module_name: strategy_decay_certifier
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.1"
created: 2026-09-15
last_updated: 2026-09-15
owner: ZephyrAlpha-Owner
responsibility_domain: 
---

# MOD-SIG-150 strategy_decay_certifier 蓝图

> 设计真源：生命周期协议 v2.0 三域落地。策略域**衰减侧**（晋升侧 E0-E9 归属域管线不动）。

## 0. 定位
读 c1_backtest.backtest_strategy_screen 每策略最新行（FINAL）→ deflated_sharpe
三态判定 → 连周计数 → retired/复活建议台账（JSON）→ 策略域会话消费。
**退役=建议制**：状态翻转归策略域管线（边界）。

## 1. 阈值（预注册）
DS≥0.5 且 oos_tested→certified｜0≤DS<0.5→probation｜DS<0→failed｜
FAILED_WINDOWS=8 周扫 failed→retired 建议｜retired 后 DS 回升≥0.5→resurrected。

## 2. 边界
不翻转 strategy_registry 状态；不做晋升侧（工厂管线所有）；
复活闸不做序贯收紧（策略样本粒度粗，M=8 已保守，收紧待数据积累后裁定）。

---

## 3. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 3.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 3.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §3（本节）→ 知道「哪些已实现、在哪里」
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
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-150`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-150` 的 1 个 file 节点 | design | `extract_depgraph.py --modules MOD-SIG-150` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-150 | MOD-SIG-150 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
