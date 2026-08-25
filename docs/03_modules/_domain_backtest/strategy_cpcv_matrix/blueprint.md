---
blueprint_id: MOD-BT-028
module_name: strategy_cpcv_matrix
domain: D_BACKTEST
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_BACKTEST
path: src/zephyr/backtest/core/strategy_cpcv_matrix.py
granularity: file
---

# MOD-BT-028 strategy_cpcv_matrix 蓝图（第五层：多策略交叉验证）

> **module_id**: MOD-BT-028 | **域**: D_BACKTEST | **优先级**: P1
> **来源**: B10-01272（AUD-DRAFT-001-DIGEST P1 波 W-P1-19，CAND-WFO-003，A1交易决策架构 §1.1）
> 代码：`src/zephyr/backtest/core/strategy_cpcv_matrix.py`
> **改铸注记**：初铸 MOD-BT-027 与并行会话 W-P1-18（B1-00258 C-003
> layered_validation_pipeline）撞车，本波按可逆原则改铸 MOD-BT-028（2026-08-25）。

## 0. 定位

第五层多策略交叉验证的**离线回测验证层**：策略级 CPCV 打分矩阵 → 多策略交集
筛选 ~30 只候选。TSV 施工形态：策略级CPCV打分矩阵→多策略交集筛选~30只候选；
依赖前置 cpcv(已有)+策略池(已有)。

查重分工（W-P1-19 铁律①细读两份 TSV 裁定=**异→分工论证**，非撞名 REVIEW）：

| 条目 | 域/层 | 语义 | 边界 |
|---|---|---|---|
| B10-01272（本件） | D_BACKTEST 离线验证层 | 多策略交叉**验证**=CPCV(Combinatorial Purged CV, Lopez de Prado) 策略级打分 | 离线批量回测方法论，输入=历史性能矩阵，产出=稳健策略交集候选 |
| B10-01504（W-P1-05 另波） | D_ASHARE_SIGNAL 在线信号层 | 筛选漏斗第五层多策略交叉（60秒级）三席 YES/NO 投票+市场状态否决门 | 在线实时信号合成，输入=各策略实时信号，产出=~30 投票候选 |

同名"第五层"源于 A1 漏斗架构同一层号的离线/在线双视图，方法论与数据平面
均不同；W-P1-05 施工 B10-01504 时各自 canonical，无归并关系。

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| cpcv | MOD-BT-001 | CPCV 切分生成+PBO 计算（样本级） | 本模块**复用**其 generate_cpcv_splits 不重造 |
| strategy_validation_pipeline | MOD-BT-001 | 单策略 IS→WFA→OOS 三阶段门控编排 | 管单策略上线门控，不做跨策略矩阵 |
| overfitting_adjudicator | MOD-BT-001 | DSR/过拟合裁决 | 不管多策略交集筛选 |

不做什么：不跑真实回测（性能矩阵调用方注入）、不做在线投票（归 W-P1-05
B10-01504）、不产出下单信号（只出候选名单与打分矩阵）。

## 1. 规则（确定性，纯函数）

- **打分矩阵**：n_strategies 策略 × n_samples 样本性能矩阵（调用方注入，
  行=策略列=样本）→ 复用 MOD-BT-001 generate_cpcv_splits 生成切分 → 每折
  计算各策略 IS/OOS 均值 → score_matrix[split][strategy]=(is_mean, oos_mean)。
- **稳健秩**：各折内按 OOS 均值降序秩（秩 1=最优），策略稳健分=
  mean(oos_rank)/n_strategies（∈(0,1]，越小越稳健）；PBO 口径对照
  compute_pbo 同族（秩/(M+1)）。
- **交集筛选**：稳健分 ≤ robust_threshold（默认 0.5，即 OOS 中位秩以上）的
  策略进入稳健池；候选=稳健池中 ≥min_votes（默认 2）策略共同提名
  （candidate_votes 注入）的标的，按提名数降序+稳健分升序取
  max_candidates（默认 30）。
- Fail-Closed：矩阵形状不齐/含非有限值/阈值越界 → StrategyCPCVError；
  稳健池为空 → 空候选 + degraded 留痕（不伪造放行）。

## 2. 接口

```python
@dataclass(frozen=True)
class StrategyCPCVConfig: n_groups / k_test / t1 / embargo / robust_threshold / min_votes / max_candidates
@dataclass(frozen=True)
class SplitScore: split_id / test_groups / is_means / oos_means
@dataclass(frozen=True)
class StrategyCPCVReport: split_scores / robust_scores / robust_pool / selected_candidates / degraded
class StrategyCPCVError(Exception)  # error_code 待登记
def build_score_matrix(performance, config) -> list[SplitScore]
def compute_robust_scores(split_scores) -> dict[str, float]
def select_candidates(robust_scores, candidate_votes, config) -> StrategyCPCVReport
```

## 3. 依赖前置

- MOD-BT-001 cpcv（切分生成复用，node 10617388）。
- MOD-BT-001 strategy_validation_pipeline（单策略门控哲学对齐：只编排不重造，
  node 10617402）。
- 策略池：candidate_votes 由调用方注入（D_ASHARE_SIGNAL 各策略候选名单）。

## 4. 验收标准

- 单测全绿（切分复用组合数正确/打分矩阵逐折对齐/稳健秩口径/交集筛选票数门
  槛与 30 封顶/空稳健池 degraded/非法输入 Fail-Closed）；tests/backtest 零回归。
