---
blueprint_id: MOD-SIG-098
module_id: MOD-SIG-098
module_name: sector_momentum_persistence
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

# MOD-SIG-098 sector_momentum_persistence 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B10-01367（模块11 动量层级与板块持续性模型，
> 裁定=做 P1）+ 候选注册表 CAND-TESTB-013。
> 代码：`src/zephyr/signal_ashare/sector/sector_momentum_persistence.py`

## 0. 定位

场内对账：mainline_probability（MOD-SIG-064）= 主线概率四因子合成评分（RRG 象限/
接力阶段/资金持续性/梯队完整度，管"谁是主线"）；**动量广度判定/连板梯队层级稳定性
CV/Momentum Persistence Score/分歧恢复速度/板块-指数共振度为缺口**（深挖批
min_build_spec+注册表 problem 明示，管"主线能持续多久"）。本模块为纯统计核：
板块日收益/资金流/连板梯队/指数收益全部鸭子类型注入，不直连 DB。

与既有件边界：
- MOD-SIG-064：主线"评分"（候选榜相对强弱）；本件"持续性度量"（时间轴维度），
  上下游候选关系（064 输出板块名单 → 本件度量其持续性），语义正交。
- sector_rotation_state/sector_divergence（MOD-SIG-060）：5 状态分类与分歧度
  横截面快照；本件为单板块时序持续分+市场动量广度二态，正交。
- 资金持续性子分公式对齐 MOD-SIG-064 F3 口径（0.6×正流入日占比+0.4×尾部连正占比），
  避免同域双口径。

## 1. 接口

```python
@dataclass(frozen=True) class SectorMomentumInput   # 板块窗输入（日收益/资金流/梯队/当日梯队分布）
@dataclass(frozen=True) class MomentumPersistenceConfig  # 阈值+权重（构造即校验，权重和=1）
@dataclass(frozen=True) class SectorPersistenceScore     # 单板块持续分输出
@dataclass(frozen=True) class MarketBreadthRegime        # 市场动量广度二态输出
class SectorMomentumPersistence:
    def score_sector(self, sector, index_returns) -> SectorPersistenceScore
    def market_breadth(self, sectors) -> MarketBreadthRegime
```

单板块五维持续分（缺维按可用权重重归一，同 MOD-SIG-064 缺维先例）：
- **MPS**（Momentum Persistence Score）= 窗口正收益日占比；≥0.7 → persistent 标记。
- **资金流持续性** = 0.6×正流入日占比 + 0.4×min(尾部连续正流入天数/3, 1)。
- **梯队层级稳定性**：日最高连板高度序列 CV=σ/μ；CV≤0.3→1.0 / ≤0.5→0.7 /
  ≤0.8→0.4 / >0.8→0.1（查表）；窗内零涨停（μ=0）→ 该腿降级 None。
- **板块-指数共振度** = Pearson ρ（板块日收益 vs 指数日收益）；零方差 → None。
- **分歧恢复速度**：窗内最近分歧日（日收益≤−2% 默认）后累计收益收复所需天数，
  1d→1.0 / 2d→0.8 / 3d→0.6 / 4-5d→0.4 / >5d 或未收复→0.1；窗内无分歧 → 该腿降级。

合成：composite = Σw_i·s_i / Σw_i(可用) × 100（默认权重 mps 0.30/资金 0.25/
梯队 0.20/共振 0.15/恢复 0.10，构造校验和=1）。

市场动量广度：窗口动量（复利窗收益）>0 的板块占比；≥0.6→mainline（主线生态），
≤0.3→speculative（投机生态），其间→balanced；空板块列表 → ValueError。

## 2. 纪律

- 输入等长/≥min_window/有限值校验；梯队高度≥0；非法 → ValueError（fail-closed）。
- 配置构造即校验：阈值∈(0,1)、min_window≥5、权重键封闭集且和=1（±1e-9）。
- 缺维腿重归一不出伪分；全腿缺 → composite=None+degraded=True。
- PIT：窗口序列全部为 ≤ 当日观测；frozen dataclass asdict JSON 可序列化；
  纯内存统计不直连 DB、不荐股。

## 3. 依赖

- import：标准库（math/statistics/dataclasses）——无 zephyr 内部 import 边。
- 上游注入：mainline_candidates（MOD-SIG-061）板块名单、data/market_breadth_collector
  广度数据、c1_market.money_flow 板块资金流（D_DATA 装配层）；下游候选：
  主线持续性页签/买入侧持续性门槛。

---

## 4. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 4.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/signal_ashare/sector/sector_momentum_persistence.py` | ✅ 已实现 | |

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
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-098`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-098` 的 2 个 file 节点 | design | `extract_depgraph.py --modules MOD-SIG-098` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-098 | MOD-SIG-098 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | planned | N/A | — |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
