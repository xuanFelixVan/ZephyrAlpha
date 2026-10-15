---
blueprint_id: MOD-SIG-097
module_id: MOD-SIG-097
module_name: limit_up_ecosystem_leadership
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.1"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
responsibility_domain: 
---

# MOD-SIG-097 limit_up_ecosystem_leadership 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B10-01366（模块10 动量领导因子与涨停板生态模型，
> 裁定=做 P1）+ 候选注册表 CAND-TESTB-012。
> 代码：`src/zephyr/signal_ashare/limit_up/limit_up_ecosystem_leadership.py`

## 0. 定位

场内对账：limit_up_followthrough（MOD-SIG-078）已覆盖炸板率+昨涨停今表现、
lhb_premium_analyzer（MOD-SIG-057）已覆盖龙虎榜溢价；**连板高度因子/封板时间因子/
梯队断层检测/Granger 领导-跟随系数为缺口**（深挖批 min_build_spec 明示）。
本模块为纯统计核：上游连板梯队快照与个股收益序列鸭子类型注入，不直连 DB。

与既有件边界：
- MOD-SIG-078：双池（封板/炸板）次日表现统计——管"昨天涨停的今天怎样"；
  本件管"今天涨停板生态结构"（梯队高度/封板时间/断层）+ 个股间领导-跟随，正交。
- MOD-SIG-057：席位溢价（谁在买→次日溢价系数），正交。
- cross_market_conduction_sensor：跨市场指数间 Granger 传导；本件为个股对个股
  领导-跟随 Granger，粒度与语义正交。
- Granger F 检验右尾 p 值纯 Python 正则化不完全贝塔实现——零 scipy
  （pyproject 幽灵依赖纪律，#ARCH-235 在案，与 MOD-SIG-094 同构）。

## 1. 接口

```python
@dataclass(frozen=True) class LimitUpStock          # 单票快照（symbol/consec_limit/first_seal_minute/amount）
@dataclass(frozen=True) class LadderEcosystemConfig # 阈值+查表（构造即校验）
@dataclass(frozen=True) class LadderSnapshot        # 梯队生态输出（高度/分布/断层/封板时间统计）
@dataclass(frozen=True) class LeadershipCoefficient # 领导-跟随系数输出（granger_f/p/leadership/方向）
class LimitUpEcosystemLeadership:
    def ecosystem_snapshot(self, stocks, *, trade_date=None) -> LadderSnapshot
    def leadership(self, leader_returns, follower_returns, *, max_lag=5) -> LeadershipCoefficient
```

梯队生态：
- 连板高度 = max(consec_limit)；梯队分布 = 各连板高度计数（1板/2板/…/≥height_cap板归并）。
- 梯队断层：高度≥2 的梯队中某层计数=0 而其上仍有更高层 → fault 层清单；
  断层严重度 = 断层层数/(max_height−1)。
- 封板时间因子：first_seal_minute（自 9:30 起分钟数）分布——均值/中位/
  早盘封板占比（≤seal_early_minute，默认 60 分钟即 10:30 前）；越早越强。
- 晋级成功率查表：从相邻两日梯队分布推 h→h+1 晋级率（2进3 成功率<30% → 断层预警，
  阈值可配置）；单日快照无相邻日 → promotion_rates=None 显式降级。

领导-跟随系数：
- Δleader/Δfollower 收益序列滞后 OLS F 检验（max_lag 默认 5，PIT：仅 leader 滞后项
  解释 follower 当期，无未来信息）；F 右尾 p<significance（默认 0.05）且
  leadership=Σ|β_lag|>threshold（默认 0.3）→ 领导关系成立。
- 样本 < min_samples（默认 30）→ checked=False 显式降级不阻断。

## 2. 纪律

- 梯队高度/断层层/封板分钟非法（负值/非单调）→ ValueError（fail-closed）；
  配置构造即校验（阈值>0、概率∈[0,1]、cap≥2）。
- 空梯队（当日零涨停）→ 合法空快照（max_height=0/degraded=True+notes）。
- frozen dataclass asdict JSON 可序列化；纯内存统计，不直连 DB、不荐股。

## 3. 依赖

- import：标准库（math/statistics/dataclasses）——无 zephyr 内部 import 边
  （MOD-SIG-089/092~096 同构纪律）。
- 上游注入：c1_market.limit_up_down 连板梯队快照（D_DATA 装配层）、个股收益序列
  （D_DATA/D_FACTOR）；下游候选：买入侧信号装配层/情绪页生态卡。

---

## 4. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 4.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/signal_ashare/limit_up/limit_up_ecosystem_leadership.py` | ✅ 已实现 | |

### 4.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/research/research/signal_ashare/limit_up/test_limit_up_ecosystem_leadership.py` | ✅ 已实现 | |

### 4.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §4（本节）→ 知道「哪些已实现、在哪里」
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
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-097`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-097` 的 3 个 file 节点 | design | `extract_depgraph.py --modules MOD-SIG-097` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-097 | MOD-SIG-097 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | planned | N/A | — |
| file_count | 3 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
