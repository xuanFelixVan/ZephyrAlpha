---
ttl: permanent
doc_type: policy
rule_form: procedural
verifiability: manual
title: SOP-C 外部策略入库漏斗——盘点·粗筛·翻译·快筛·去重·入库挂图
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-09-11
topic: backtest_system_sop
scope: 07_trading_decision_architecture
related_issues:
  - "#ARCH-TRADING-DECISION-MAP-001"
---

# SOP-C 外部策略入库漏斗

> **定位**：外部策略源码（首批：`E:\数据下载\qmt聚宽策略\2020-2026聚宽600条源码`，聚宽社区 2020-2026 年度精选，.txt 为主）→ 本项目策略库 → 挂图 → 配比的标准通道。
> **铁律（INV-1）**：策略内容**禁止**复制进交易决策地图；地图只按 `strategy_ref` 引用 `strategy_registry.yaml`（REG-STR-001，STR-*）条目。本 SOP 全部产物都在策略库侧完成，挂图是最后一步。
> **总纲**：[README.md](README.md)。

## 0. 漏斗总览

```
600 条源码 → ①盘点归一 → ②粗筛出局（估余 ≈240）
         → ③翻译适配（估余 ≈150）→ ④快筛批测（估余 ≈60）
         → ⑤聚类去重+差异化论证（估余 ≈20）→ ⑥入库≈10 → 挂图 → PP-001 配比
```

数量为预估值，实际以各步盘点为准；每步产出统计并入批报告。

## 1. Step C1 盘点归一

- 遍历源目录，逐文件登记：编号 / 原文件名 / 来源年份 / 编码 / 是否含中文注释 / 行数 / 平台（聚宽 API 版本特征）；
- 统一转 UTF-8，落 `data/strategy_intake/raw_manifest.csv`（或等价清单）；
- 破损/空文件记 `unreadable`，不修复不猜测。

## 2. Step C2 粗筛出局（硬排除清单）

| 排除类别 | 判据 | 备注 |
|---|---|---|
| 非股票标的 | 期货、基金定投、可转债、港美股专用 | 本体系 A 股日线股票为主（crypto 另册） |
| 非日线级 | 分钟级/tick 级主逻辑 | 日线近似会失真，硬排除 |
| 结构不可迁移 | 配对交易、股指对冲、融券裸卖空 | 本体系暂无对应执行通道 |
| 演示/作业类 | 向导式生成器产物、明显教学作业 | 无独立策略思想 |

出局文件标记 `excluded:<类别>`，保留清单可追溯（不删除源文件）。

## 3. Step C3 翻译适配（工程大头，试点先行）

- 写**聚宽 API shim**：`get_price / get_fundamentals / order_target_value / set_benchmark ...` → 本地数据接口（westock/本地库）+ 本地执行语义（T+1、手数、涨跌停）；
- **试点先行（定稿决策 D3）**：按类别（打板/轮动/多因子/择时/做T）各抽 2 条、共约 10 条验证 shim 可行性，试点通过才全量批跑；
- 翻译失败（API 无对应/逻辑依赖聚宽专有数据）→ 记 `translate_failed:<原因>` 清单，**不硬翻**；
- 产出：shim 模块 + 翻译成功/失败双清单。

## 4. Step C4 快筛批测（多重检验是最大敌人）

- 统一口径：同区间（定稿 D1：IS 2019-2023 / OOS 2024-2026）、同成本（约束一五项）、同 T+1/手数规则、同一引擎（vectorized）；
- **Deflated Sharpe 强制**：把"600 条海选"的全部试验次数纳入多重检验校正，只看校正后仍显著的幸存者；
- 按年外样本检验：策略原生发布年份之后的区间表现单独列示（防止"策略拟合了自己发布前的行情"）；
- 产出：scoreboard（对象 × 校正后 Sharpe/回撤/换手/分状态表现）。

## 5. Step C5 聚类去重 + 差异化论证（约束五硬门）

> **退役标注（2026-09-15，净零声明兑现）**：本节人工流程已由 `zephyr.strategy_pipeline.intake`
> （MOD-BT-189）机械化接管——ρ>0.6 聚类（簇首=证据最强者）、三轴字段级+指标信号指纹差异化论证、
> family_redundancy 结构化块。机器判定与人工批一致率 8/8（回放证据=
> `docs/_working/pipeline-research/acceptance6-replay.md`）。本节散文降级为**人工兜底通道**
> （管线停用时按本节手工执行），语义真源不变。

- 按三个轴聚类：信号源 / 持仓周期 / 市场状态适配；
- 同簇只留校正后表现最优的 1-2 条；
- 每条拟入库策略写《差异化论证》：与库内既有策略（含 8 个实盘 sleeve）逐轴对比，三轴全无差异 = 拒绝入库（少而精，禁堆砌相似策略制造多策略假象）。

## 6. Step C6 入库 → 挂图 → 配比

> **退役标注（2026-09-15，净零声明兑现）**：本节①入库=`zephyr.strategy_pipeline.registry_writer`
> （MOD-BT-192，safe_write CAS+only-add 断言+确定性 STR-* 编号）；②挂图=`scripts/backtest/auto_mount.py`
> （MOD-BT-171，--apply 语义门+38 规则校验+报告落盘）；编排入口=intake.run_intake_auto（事件驱动，
> 全程零人工至 candidate/sim）。本节散文降级为人工兜底通道；映射表（§6.2）真源已固化进 auto_mount
> `CLASS_NODE_MAP`（SOP-C §6.2 五行规则表逐字承接）。**配比（③）与 sim→production 仍为 Owner 门。**

1. **入库**：`strategy_registry.yaml` 新增 STR-* 条目（id / name / 信号源 / 持仓周期 / 状态适配 / 翻译来源溯源 / 校正后指标引用）；
2. **挂图**：按类别挂到对应节点与 state_matrix 格子（`mounted` 数组），映射表：

   | 策略类别 | 挂载去向 |
   |---|---|
   | 大盘择时类 | L1 总闸（TDM-E-L1） |
   | 板块轮动类 | L2 对应树枝 |
   | 打板/个股选股类 | L3 策略专属链（如 TDM-E-L3-07-1） |
   | 做T类 | TDM-P-P2 |

3. **配比**：挂图策略与既有 8 sleeves 一起进入 PP-001 组合优化；配比由回测归因决定（风险调整后最优 + 相关性互补），**禁止按绝对收益最大选配比**（会精准选出过拟合冠军）；权重升级走 PP-001 逐 sleeve 归因语义。

## 7. 验收清单（入库前强制）

- [ ] 溯源完整：STR-* 条目能追溯到原始文件与翻译产物；
- [ ] 快筛口径统一，Deflated Sharpe 已过；
- [ ] 按年外样本无显著衰减；
- [ ] 差异化论证三轴齐备；
- [ ] 挂图位置有对应 state_matrix 格子且格子状态适用（如打板只进点火后三档）；
- [ ] INV-1 自检：策略内容没有以任何形式复制进地图文件。


## 8. 双窗口及格门槛（C4/C5 验收土规，2026-09-13 Owner 批准立规）

**门槛定义**：外部策略进入 sim/paper（模拟盘/纸面）候选前，必须同时满足：
1. IS 窗口（冻结 2020-2023）Sharpe > 0；
2. 每一段样本外复测窗口（OOS 2024-2026、2016-2019、及未来新增段）Sharpe > 0；
3. 年衰减率 oos_years_decay < 0.5（>=0.5 判存疑，土规真源=schemas/categories/backtest/backtest_strategy_screen.py DDL 注释）。

**净零声明**：本条非新增规范对象——是 backtest_strategy_screen DDL `oos_years_decay` 存疑土规（>=0.5）
与 BT-P0-002 decay_watch 框架在策略入库线的显式化合并；执行工具=strategy_screen_query.py bothwin
子命令（只读判定，结果可检索）；lifecycle 变更（candidate→sim）仍走规则册治理动作留痕。
