---
module_id: MOD-SIG-135
title: "日级市场条件传感器蓝图 — 11 信号五档水温聚合"
doc_type: blueprint
status: Active
version: "0.1.6"
design_maturity: production
ttl: permanent
layer: L01_market
layer_name: market
functional_domain: signal_ashare
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-09-10"
last_updated: "2026-09-10"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-SIG-135 Daily Condition Sensor — 日级市场条件传感器 蓝图

> **module_id**: MOD-SIG-135 | **域**: D_ASHARE_SIGNAL | **层**: L01 信号/大盘
> **优先级**: P0 | **成熟度**: L1 骨架 | **建设标记**: ✅可建
> **裁定真源**: 69 号备忘录 §2.11 D20（四层温度计架构）+ 地图节点 TDM-E-L1-S5
> **消费节点**: TDM-E-L1-S5（当日盘面骤变读数显示今天该多激进）→ L1-AGG / L2-05-1

## 1. 定位

日级水温是四层温度计（月 12 态/周六段/日 5 档/盘中预案）中唯一盘中可变的 L1 输入：
盘中 11 信号环比计票 → S0-S4 五档水温。水烫(S4)=当日可激进；水冰(S0)=当日只看不动。
9:35 首算，盘中可更新。

## 2. 11 信号（D20"先大而全"，D21 三防弹衣裁噪留灰度阶段）

| 组 | 信号 | 方向语义 | 警报线 |
|---|---|---|---|
| A① | 涨停家数环比 | 高=健康 | 环比 <0.90 偏空 |
| A② | 连板梯队环比 | 高=健康 | 环比 <0.90 偏空 |
| A③ | 炸板率 | 低=健康 | **>50% 警报偏空**（严格>） |
| A④ | 跌停+核按钮家数 | 低=健康 | >30 家偏空 |
| A⑤ | 昨日涨停溢价 | 高=健康 | **≤-5% 警报偏空** |
| A⑥ | 红盘家数 | 高=健康 | **<1500 警报偏空** |
| A⑦ | 量能匹配诱多识别 | 价升量缩=诱多偏空 | — |
| A⑧ | 板块联动混沌 | 低=健康 | >0.6 偏空 |
| B⑨ | 宽度领先（环比） | 对称带通 ±0.10 | — |
| B⑩ | 对坏消息的反应 | 抗跌=强 | 利空放大 <-0.10 偏空 |
| B⑪ | 市值分层宽度 | 普涨活跃=高 | <0.30 单层独撑偏空 |

## 3. 合成规则

1. 每信号三值计票（+1/0/-1）；缺数据计 0 票并记 missing（fail-open per-signal）。
2. 净分 net = 看多票数 − 看空票数；映射：≥+4→S4；+2~+3→S3；−1~+1→S2；−2~−3→S1；≤−4→S0。
3. **fail-closed 总闸**：可用信号 <6 → tier=None（INSUFFICIENT_DATA，不下激进结论）。
4. 环比类信号昨日基数缺失或为 0 → 按缺数据处理（防除零）。
5. 相关性去重（D20 裁噪预留）不在本件——灰度合成阶段做。

## 4. 输入 / 输出

| 方向 | 内容 |
|------|------|
| 输入 | DailyRawSignals（11 信号原始读数，调用方从 DS-082/DS-059/DS-150 算好注入；None=缺） |
| 输出 | DailyConditionVerdict：tier + net_score + 多空/缺票数 + 11 信号明细（可审计） |

纯函数核心，零 IO；阈值 config 注入（DailySensorThresholds，经验拍定=proposed，
回测校准后升级，holdout 纪律适用）。

## 5. 查重分工

- market_state_sensor（MOD-SIG-036）=日 BAR trend×vol 九网格，月/周级状态日度快照；
  本件=盘中环比骤变计票合成（S5 的合成核），互补不重叠。
- sector_gate.WaterTemp=水温档响应侧（本模块输出映射为其入参），本件不判响应。
- sentiment_cycle/情绪周期五态=情绪轴（28 号），与日级水温时间尺度不同。

---

## 6. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/signal_ashare/core/daily_condition_sensor.py` | ✅ 已实现 | |

### 6.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §6（本节）→ 知道「哪些已实现、在哪里」
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
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-135`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-135` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIG-135` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-135 | MOD-SIG-135 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
