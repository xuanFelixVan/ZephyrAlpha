---
blueprint_id: MOD-SIG-090
module_id: MOD-SIG-090
module_name: t0_trading_pipeline
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: H
ai_autonomy: ai_modifiable
version: "0.1.1"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
responsibility_domain: 
---

# MOD-SIG-090 t0_trading_pipeline 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B1-00191（C-012 做T日内套利，裁定=做 P1）+
> 候选注册表 CAND-TESTB-005。代码：`src/zephyr/signal_ashare/intraday_t0/t0_trading_pipeline.py`

## 0. 定位

做T信号点（MOD-SIG-068 t0_point_analyzer）与 t_trade_coordinator（MOD-SELL-018）
在，独立做T信号管线与盘中即时反应决策引擎未收口（深挖裁定理由）。本模块落
**做T全链路管线**：

    信号（MOD-SIG-068 复用）→ 决策（底仓/价差/次数硬约束过滤）
    → 执行（注入 executor，生产侧由集成批接 MOD-SELL-018）
    → 当日复盘（轮次价差/命中/延迟留痕）

- **硬约束**：底仓自平衡（单轮买量=卖量、当日净持仓变动=0）、单腿股数手数对齐、
  当日轮次上限、单轮最小价差、信号置信度下限。
- **延迟预算**：全链路累计延迟超预算→不再开新轮（轮内平衡腿仍须闭合，
  平衡不变量优先于预算，违例留 notes）。
- **失败回滚**：平衡腿执行失败→反向腿回滚恢复底仓；回滚再失败→升级 notes
  （fail-closed 留痕，不静默）。
- **尾盘强制平衡**：EOD 未闭合轮按末 bar 价强制闭合，保底仓不变量。

与既有件边界：MOD-SIG-068 只做点位信号与回验（非交易执行）；MOD-SELL-018
t_trade_coordinator 是单腿计划件，本模块经 **executor 注入契约**挂接（生产接线
留集成批，本模块不 import 跨域 sell_decision——signal_ashare→sell_decision
无 import 先例，保持域方向纪律）。

## 1. 接口

```python
@dataclass(frozen=True) class T0PipelineConfig   # 底仓/价差/次数/手数/延迟预算
@dataclass(frozen=True) class T0OrderIntent      # 执行意图（symbol/side/volume/price）
@dataclass(frozen=True) class T0Fill             # 执行回报（filled/price/latency_ms）
@dataclass(frozen=True) class T0RoundResult      # 单轮结果（含回滚标记）
@dataclass(frozen=True) class T0DayReport        # 当日复盘
class T0TradingPipeline:
    def __init__(self, config, executor: Callable[[T0OrderIntent], T0Fill])
    def run_day(self, bars, context, analyzer_config=None) -> T0DayReport
```

## 2. 纪律

- 底仓自平衡为最高不变量：任何路径（含失败/EOD/超预算）结束时当日净腿量=0，
  破坏即升级 notes。
- 配置校验 fail-closed：单腿股数≤底仓、手数对齐、轮次≥1、价差阈值>0、预算>0。
- frozen dataclass、to_dict JSON 可序列化；本模块为决策编排非券商直连，
  成交成本口径归执行层/宪章§3约束一。

---

## 3. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 3.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/signal_ashare/intraday_t0/t0_trading_pipeline.py` | ✅ 已实现 | |

### 3.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/research/research/signal_ashare/intraday_t0/test_t0_trading_pipeline.py` | ✅ 已实现 | |

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
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-090`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-090` 的 3 个 file 节点 | design | `extract_depgraph.py --modules MOD-SIG-090` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-090 | MOD-SIG-090 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | planned | N/A | — |
| file_count | 3 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
