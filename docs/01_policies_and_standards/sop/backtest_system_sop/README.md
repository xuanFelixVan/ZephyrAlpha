---
ttl: permanent
doc_type: policy
rule_form: procedural
verifiability: manual
title: 回测体系 SOP 总纲——分级回测金字塔 × AI 自驱循环 × 策略库入库漏斗
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-09-11
topic: backtest_system_sop
scope: 07_trading_decision_architecture
related_issues:
  - "#ARCH-TRADING-DECISION-MAP-001"
  - "TRAE-079"
---

# 回测体系 SOP 总纲

> **定位**：交易决策地图（TDMAP-001）全部打通后，从"回测什么"到"全图整装回测通过"的全链路标准流程。回答三个问题：**回测的顺序**（SOP-A）、**单个对象怎么回测**（SOP-B）、**外部策略怎么进来**（SOP-C）。
> **诞生背景**（2026-09-11 定稿讨论，见 `docs/_working/2026-09-11-backtest-system-sop-discussion.md`）：Owner 提出三问——①是否逐节点回测+分级回测；②AI 自驱回测需要完整 SOP（顺序/内容/修改）；③聚宽 600 条策略的植入路径。讨论定稿后固化为本文件夹三个 SOP。
> **核心原则**：AI 自驱执行，Owner 只看批次决策点；一切结论必须可归因、可复现、带证据；护栏比人工审查更重要。

## 1. 适用范围与触发条件

- **适用**：地图任意节点/环节/整层/全图的回测验证；外部策略源码（聚宽/QMT/社区等）入库与挂图。
- **触发**：地图施工完成一个环节、或 Owner 点名某对象需要回测、或 F-C3 归因反馈判定某节点需要重验。
- **不适用**：模拟盘/实盘对账（走 56 号方案）、日内 tick 级验证实施细则（V5 另有专门批次）。

## 2. 投资哲学五约束 → 回测投影（不可妥协）

| 约束（§3 方法论） | 在回测体系中的投影 |
|---|---|
| 约束一：成本模型必须完整 | 窄回测（SOP-B ⑥）强制五项成本：佣金+印花税+滑点+市场冲击+做T额外成本；费率读实际账户配置，禁硬编码。宽回测可用粗成本，但结论口径必须标注 |
| 约束二：统一框架派 | 回测对象是"地图上的行为"，不是孤立策略；一切回测结论服务于地图 confidence 升级 |
| 约束三：Regime Detection 生死线 | P0 优先级独占：L1-AGG 状态判定最先回测；所有回测结论按六段状态分档报告，禁跨状态平均 |
| 约束四：策略三维度解耦 | 选股信号 × 组合权重 × 执行方式分开回测（what=F-C1/L2/L3，how much=C1 配比，how=L4/X-S2），禁止耦合结论 |
| 约束五：少而精优于多而散 | SOP-C 差异化论证是入库硬门：信号源/持仓周期/市场状态适配三者须有差异，同类只留最优 |

## 3. 回测金字塔（五层，颗粒度由小到大）

```
L0 节点级      —— IC / 事件研究 / 分类准确率 / 消融（V1·V2）
L1 组件级      —— 同层树枝组装，合分消融：有它 vs 没它（V2·V3）
L2 层级        —— 整层策略 WF + Permutation Test（V3）
L3 流级        —— 建仓/持仓/离场/组合流端到端 + 完整成本（V4）
L4 全图整装级   —— 四流并发 × 六段状态矩阵 × PP-001 配比（V4+模拟盘）
```

- 推进顺序：先上游后下游（上游误差污染下游结论，无法归因）；先主链后树枝。
- 每层结论必须按六段状态（capitulation/accumulation/ignition/expansion/euphoria/distribution）分档报告。

## 4. 节点四类型 → 回测形态映射（SOP-A Step A1 的判据表）

| 节点类型 | 典型节点 | 回测形态 | 通过判据方向 |
|---|---|---|---|
| 传感器/因子类 | TDM-E-L1-S1~S5、板块强度子项、多维验证子项 | IC / 事件后收益分布 / 因子验证（V1/V2） | IC 显著且分状态稳定；事件后收益分布优于随机 |
| 闸门/判定类 | TDM-E-L1-AGG、TDM-E-L1、环境开关、水温档 | 分类准确率 × 错分代价矩阵 | 判对增益 > 判错损失；错分方向不对称分析 |
| 策略链类 | 打板链、多因子链、做T链、离场信号族 | 策略级 WF + Permutation（V3） | WFA/OOS 通过；过拟合门禁通过 |
| 聚合/执行类 | 双池合流、五路合分、分批建仓、执行算法选型 | 消融对比（增量贡献）/ 执行质量 TCA | 有它比没它（或换简单规则）增量显著；滑点/成交率达标 |

**行为合并规则**：子节点行为相同仅参数不同 → 合并为一次参数扫描，不单独开回测对象（D108 判据直接复用）。全图折算后约 40-60 个独立可回测行为。

## 5. 文件导航

| 文件 | 管什么 | 谁执行 |
|---|---|---|
| [sop_a_full_map_orchestration.md](sop_a_full_map_orchestration.md) | 全图编排：注册→分类→优先级→批次推进→归档升级 | AI 自驱，Owner 看批次决策点 |
| [sop_b_node_loop.md](sop_b_node_loop.md) | 单个回测对象的七步循环 + 三护栏 + 自检清单 | AI 自驱 |
| [sop_c_strategy_library_intake.md](sop_c_strategy_library_intake.md) | 外部策略源码（聚宽 600 条等）→ 策略库 → 挂图 → 配比 | AI 自驱 |
| [sop_d_run_archive_naming.md](sop_d_run_archive_naming.md) | 回测档案图书馆规范：run 目录位置/编号/结构/自动落盘/巡检/复现演练 | AI 自驱，落盘走 run_archive API |

**施工讨论记录**：`docs/_working/2026-09-11-backtest-system-sop-discussion.md`（三问三答原貌 + 定稿决策 D1-D4 + 七步打通顺序）。

## 6. 与既有验证体系的关系（禁第二套门控）

本 SOP 是**编排层**，不重造任何验证机制（52 号裁定：再建 V1-V6 门控 = 同一防线两套阈值，禁）：

| 既有资产 | 位置 | 本 SOP 用法 |
|---|---|---|
| V1-V6 分层验证 | §20.7.1 + `layered_validation_pipeline`（MOD-BT-027） | SOP-B ⑥ 按提交类型映射验证层；层层递进不可跳级 |
| 过拟合门禁 | OverfittingDetector 三阶段 + Deflated Sharpe（BM-BT-05-G） | SOP-B 护栏② 直接挂入 |
| IS→WFA→OOS 上线门控 | BM-BT-07 | SOP-B ⑥ 窄回测的通过标准 |
| 证据落库 | `decisiongraph_adapter`（MOD-BT-001）BacktestResult → decisiongraph L5 + evidence_hash | SOP-A Step A5 归档升级通道 |
| regime 回测先例 | 11 号 spec（G03，C1 四项验收） | L1-AGG P0 批次的方法论模板 |
| 知识漂移 | D118/D120/D122（`effective_from=2026-09-08` PIT 轴） | 回测区间早于生效日 → D120 标注放行 |

## 7. 全局护栏（所有 SOP 共用，违反任一 = 结论作废）

1. **预注册**：验收阈值、参数搜索空间在回测开始前写入回测对象注册条目；禁事后挪门柱。
2. **留痕**：每轮参数修改 diff + 理由 + 结果全留痕（`.runtime/gate_audit/` 或回测报告附录）——多重检验校正（Deflated Sharpe）的原料。
3. **分状态报告**：一切结论按六段状态分档；跨状态平均数在本文档体系内视为无效结论。
4. **PIT 铁律**：所有数据带时点可用性；禁用未来函数；禁幸存者样本（退市股须在池）。
5. **成本口径**：引用回测结论必须同时声明成本口径（粗/全）与区间（IS/OOS）。
6. **置信度语义**：`verified=回测归因支撑（必带 evidence）`、`proposed=主观假设待验证`、`untested=未填`——升级必须走 evidence 通道，禁止把 proposed 冒充 verified（地图 v1.2 D5）。

## 8. 术语表

| 术语 | 含义 |
|---|---|
| 宽回测 | 全量数据 + 全参数网格 + 粗成本，目的=判断信号存在性 |
| 窄回测 | 幸存配置 + 完整成本五项 + WFA/OOS，目的=可上线的结论 |
| 剪枝 | 按 IC/事件衰减、分状态稳定性、相关性三类规则剔除噪音数据与信号 |
| 消融对比 | 同一输入下"有该节点 vs 没该节点 vs 换简单规则"的增量对比 |
| 错分代价 | 状态判定错误的下游损失（用错误状态切错误策略的损失） |
| DATA-GAP | SOP-B ②产出的数据需求缺口清单 |
| 批次决策点 | SOP-A 每批结束时 Owner 需要确认的三问（见 SOP-A §5） |
