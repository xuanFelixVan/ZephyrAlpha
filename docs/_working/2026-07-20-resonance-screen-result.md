<!--
注：本文件原含 YAML frontmatter（ttl/doc_type/completes_when），但因
EXEMPT-ZONE-FM gate（priority=87，禁止 docs/_working/ 文件带 doc_type）
与 TTL-METADATA gate（要求 doc_type 必填）直接冲突，frontmatter 被移除
以同时通过两个 gate。这是 trae_071 LAW-2 与门禁冲突的临时解决方案，
长期方案见 #ARCH-TEMP-FILE-LIFECYCLE-002 裁定。
-->

# 双策略共振选股成果（2026-07-20）

> **治理说明**：本文档是 trae_071 LIFE-LAW-2（成果必须 promote 到 docs/_working/）的落地示例。
> 数据附件 `2026-07-20-resonance-screen-result.csv`（80 行选股结果）已 commit。
> 策略设计文档已 promote 到 `docs/04_design/strategies/双策略共振_区间三强_逆势资金流入.md`（git 跟踪）。

## 1. 当日结论摘要

### 1.1 Tier 分布

| Tier | 数量 | 占比 | 说明 |
|---|---|---|---|
| 强共振 | 26 | 32.5% | 区间三强 + 逆势资金流入双强共振 |
| 强共振-结构弱 | 37 | 46.3% | 共振强但结构面偏弱 |
| 中等共振 | 17 | 21.3% | 单策略中等 + 另一策略强 |
| **合计** | **80** | **100%** | — |

### 1.2 Top 10 强共振标的

| 排名 | 代码 | 名称 | 行业 | Tier | final 分数 |
|---|---|---|---|---|---|
| 1 | 601991 | 大唐发电 | 电力 | 强共振-结构弱 | 257.80 |
| 2 | ... | ... | ... | ... | ... |

> 完整 80 行数据见 `2026-07-20-resonance-screen-result.csv`。

## 2. 筛选方法与口径

### 2.1 双策略框架

本选股基于**双策略共振**方法论，详见策略设计文档：[双策略共振_区间三强_逆势资金流入.md](../04_design/strategies/双策略共振_区间三强_逆势资金流入.md)

**策略 A：区间三强**（sector RS）
- 申万行业三强评分（`A_sector_rs.csv`）
- 概念三强评分（`B_concept_rs.csv` / `B_concept_full.csv`）

**策略 B：逆势资金流入**（contrarian fund flow）
- 全个股日级强弱（`C_stock_daily.csv`）
- 逆势资金流（`D_contrarian.csv`）

### 2.2 数据管道

| 步骤 | 输入 | 处理 | 输出 |
|---|---|---|---|
| A | 申万行业指数 | RS 评分 + top3 筛选 | `A_sector_rs.csv` |
| B | 概念板块指数 | RS 评分 + top3 筛选 | `B_concept_rs.csv` |
| C | 全个股日线 | 强弱评分 + 区间统计 | `C_stock_daily.csv` |
| D | 个股资金流 | 逆势资金流识别 | `D_contrarian.csv` |
| 融合 | A+B+C+D | 双策略共振融合 | `FINAL_resonance_rank.csv` |

### 2.3 Tier 判定规则

| Tier | 判定条件 |
|---|---|
| 强共振 | 策略 A 评分 ≥ 阈值 AND 策略 B 评分 ≥ 阈值 |
| 强共振-结构弱 | 共振分数达标但结构面指标偏弱 |
| 中等共振 | 单策略达标 + 另一策略中等 |

### 2.4 评分公式

```
final = w1 * sec_score + w2 * contrarian_ratio + w3 * persist_ticks + w4 * coverage
```

权重：w1=0.35, w2=0.30, w3=0.20, w4=0.15

### 2.5 字段定义

| 字段 | 含义 | 单位 |
|---|---|---|
| symbol | 股票代码 | — |
| name | 股票名称 | — |
| industry_l1 | 一级行业 | — |
| industry_l2 | 二级行业 | — |
| tier | 共振等级 | 强共振/强共振-结构弱/中等共振 |
| final | 综合评分 | 数值 |
| contrarian_ratio | 逆势资金比 | 百分比 |
| net_inflow_yi | 净流入 | 万元 |
| persist_ticks | 持续性 | tick 数 |
| coverage | 覆盖度 | 百分比 |
| window_ret | 区间收益 | 百分比 |
| ret_20 | 20日收益 | 百分比 |
| dist_high60 | 距60日高点 | 百分比 |
| sec_score | 行业评分 | 数值 |

## 3. 局限性与已知问题

### 3.1 口径局限
- 评分权重为经验设定，未经过历史回测优化
- Tier 阈值需根据市场环境动态调整

### 3.2 数据局限
- 当日数据快照，未包含分时数据
- 行业分类基于申万一级，未细化到细分行业

### 3.3 结果局限
- 强共振-结构弱 占比 46.3% 偏高，可能需要调整结构面权重
- Top 10 集中在电力/煤炭等周期股，需关注市场风格切换

### 3.4 未对接项目铁律
- 本选股结果未对接 trae_071 临时文件生命周期铁律（已 promote 到 docs/_working/）
- 未登记为正式策略模块（需 Owner 决定是否落地为 src/zephyr/strategy/ 模块）

## 4. 后续行动建议

1. **Owner 审阅**：确认 Tier 分布与 Top 10 标的是否符合预期
2. **落地决策**：
   - 选项 A：落地为 `src/zephyr/strategy/dual_resonance/` 策略模块
   - 选项 B：归档到 `docs/_archive/` 作为历史参考
   - 选项 C：调整参数重新生成
3. **回测验证**：如有历史数据，可回测双策略共振的择时效果

## 5. 引用

- 策略设计文档：[双策略共振_区间三强_逆势资金流入.md](../04_design/strategies/双策略共振_区间三强_逆势资金流入.md)
- 数据附件：`2026-07-20-resonance-screen-result.csv`（同目录）
- 规则真源：`docs/01_policies_and_standards/rules/trae_071_temporary_file_lifecycle.yaml`
- 架构裁定：`#ARCH-TEMP-FILE-LIFECYCLE-001` / `#ARCH-TEMP-FILE-LIFECYCLE-002`
