---
blueprint_id: MOD-SIG-095
module_id: MOD-SIG-095
module_name: multi_indicator_divergence
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

# MOD-SIG-095 multi_indicator_divergence 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B10-01363（模块7 多指标背离检测模型，裁定=做
> P1）+ 候选注册表 CAND-TESTB-010。
> 代码：`src/zephyr/signal_ashare/multi_indicator_divergence.py`

## 0. 定位

卖出侧量价背离已有（sell_signal_collector）；RSI/MACD/CVD 系统背离检测+
多级别级联为缺口。本模块落地峰谷对位背离检测器：指标核自算（RSI Wilder/
MACD DIF）+CVD 注入腿，背离程度量化，次数→反转概率与多级别级联概率查表，
并支持背离化解标记。

与既有件边界（查重裁定）：
- MOD-SELL sell_signal_collector：卖出侧量价背离聚合，非 RSI/MACD 系统化检测。
- sentiment_cycle 顶背离（情绪/炸板率口径）、t0_point_analyzer（做T 日内量价）、
  sector_divergence（板块间）、MOD-SIG-093 CVD 背离（本件 CVD 腿生产方，
  注入消费）——语义均正交或上下游关系。
- factor 指标库无 RSI/MACD 实现可查（grep 仅中 ml_train/meta_learning_rsi，
  D_ML_TRAIN 域专用），故指标核自算不 import。

## 1. 接口

```python
@dataclass(frozen=True) class DivergenceConfig      # 周期/lookback/两张概率表
@dataclass(frozen=True) class DivergenceEvent       # indicator/direction/magnitude/resolved
@dataclass(frozen=True) class DivergenceScanResult  # 全指标扫描+次数概率
@dataclass(frozen=True) class CascadeResult         # 级联对齐数+概率
class MultiIndicatorDivergenceDetector:
    def rsi(self, close, period=None) -> pd.Series               # Wilder
    def macd(self, close, fast=None, slow=None, signal=None)     # DIF/DEA/HIST
    def detect(self, close, indicator_series, *, indicator,
               lookback=None) -> list[DivergenceEvent]           # 峰谷对位
    def reversal_probability(self, count) -> float               # 次数查表
    def cascade_probability(self, directions_by_tf, *, direction) -> CascadeResult
    def scan(self, close, cvd=None) -> DivergenceScanResult      # 全指标扫描
```

峰谷对位：居中 lookback 窗口确认局部峰/谷（回溯检测语义），连续两峰/两谷
配对；magnitude=价格腿幅度+指标腿幅度（std 归一）。
默认概率表：次数 {1:35%/2:55%/3:72%}（3 次顶背离>70% 口径）；级联
{1:35%/2:50%/3:62%/4:70%}（满级≥60%）；次数越界钳制表尾。
化解：背离后指标反超前峰（bearish）/前谷（bullish）水平 → resolved=True。

## 2. 纪律

- 指标（rsi/macd/cvd）与方向（bullish/bearish）封闭集；未知指标/非法方向/
  短序列/内部非有限值/非法配置 → ValueError（fail-closed）。
- 概率表构造即校验：键≥1 整数、值∈[0,1]、随键非递减。
- RSI warmup NaN 仅允许头部（detect 跳过）；scan 计数剔除已化解事件。
- frozen dataclass、to_dict JSON 可序列化；不直连 DB、不荐股。

## 3. 依赖

- import：numpy、pandas（无 zephyr 内部 import 边）。
- 上游注入：D_DATA OHLC 行情、MOD-SIG-093 CVD 序列（鸭子类型）。
- 下游候选：买入/卖出侧装配层、MOD-SIG-086 漏斗骨架。

---

## 4. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 4.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

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
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-095`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-095` 的 2 个 file 节点 | design | `extract_depgraph.py --modules MOD-SIG-095` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-095 | MOD-SIG-095 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | planned | N/A | — |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
