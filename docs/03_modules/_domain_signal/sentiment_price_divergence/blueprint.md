---
blueprint_id: MOD-SIG-101
module_id: MOD-SIG-101
module_name: sentiment_price_divergence
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

# MOD-SIG-101 sentiment_price_divergence 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B10-01371（模块16 情绪-价格背离指数模型
> Sentiment-Price Divergence Index，裁定=做 P1）+ 候选注册表 CAND-TESTB-016。
> 代码：`src/zephyr/signal_ashare/sentiment/sentiment_price_divergence.py`

## 0. 定位

场内对账（查重铁律⑤分工在案）：
- sector_divergence（MOD-SIG-060）= 板块间分歧度与轮动速度（横截面板块生态）；
- multi_indicator_divergence（MOD-SIG-095）= RSI/MACD/CVD 技术指标峰谷背离
  （纯价格-指标对位，语义正交裁定 P1W02 fragment 在案）；
- **情绪-价格背离指数 SDI=ΔSentiment_z−ΔPrice_z 无实现**（深挖批 min_build_spec
  明示：核心类 SentimentPriceDivergence，输入情绪指数与价格 z 分差，输出 SDI 值
  +背离方向+置信度）。本模块落地，情绪指数序列由 MOD-SIG-025
  market_sentiment_analyzer 产出注入（鸭子类型，不 import）。

## 1. 接口

```python
@dataclass(frozen=True) class SentimentPriceDivergenceConfig  # 窗/滞后/阈值（构造即校验）
@dataclass(frozen=True) class DivergenceReading               # 单点读数（SDI/方向/置信度）
class SentimentPriceDivergence:
    def compute(self, sentiment_scores, prices) -> DivergenceReading   # 最新读数
    def scan(self, sentiment_scores, prices) -> list[DivergenceReading]  # 背离事件表
```

- **z 分差**：z_s =（情绪 − 滚动窗均值）/窗总体标准差（默认窗 60）；z_p 同口径；
  窗零方差 → z=0 + notes（恒定窗无信息，不伪造背离）。
- **SDI = ΔSentiment_z − ΔPrice_z**，Δ = 当前 z − lag 根前 z（默认 lag=5）。
- **方向**：SDI ≥ +threshold（默认 1.0）→ bullish（情绪改善显著快于价格，正向背离）；
  ≤ −threshold → bearish（情绪恶化显著快于价格，负向背离）；其间 → none。
- **置信度** = min(|SDI| / confidence_scale, 1.0)（scale 默认 2.0），direction=none 时
  置信度照算（幅度读数）但 divergence=False。
- **scan**：自首个可算根起逐根计算，仅收 direction≠none 的背离事件（带 bar_index）。

## 2. 纪律

- 序列等长/≥z_window+delta_lag/有限值/价格>0 校验；非法 → ValueError（fail-closed）。
- 配置构造即校验：z_window≥10、delta_lag≥1、threshold>0、confidence_scale>0。
- PIT：z/Δ 全部滚动窗前视；scan 逐根前视无未来信息。
- frozen dataclass asdict JSON 可序列化；纯内存统计不直连 DB、不荐股。

## 3. 依赖

- import：标准库（math/statistics/dataclasses）——无 zephyr 内部 import 边。
- 上游注入：market_sentiment_analyzer（MOD-SIG-025）情绪指数序列、指数/个股价格
  （D_DATA 装配层）；下游候选：情绪页背离告警、买入侧背离过滤装配层。

---

## 4. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 4.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/signal_ashare/sentiment/sentiment_price_divergence.py` | ✅ 已实现 | |

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
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-101`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-101` 的 2 个 file 节点 | design | `extract_depgraph.py --modules MOD-SIG-101` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-101 | MOD-SIG-101 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | planned | N/A | — |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
