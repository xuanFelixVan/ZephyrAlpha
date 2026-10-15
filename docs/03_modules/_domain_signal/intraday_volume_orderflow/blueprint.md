---
blueprint_id: MOD-SIG-093
module_id: MOD-SIG-093
module_name: intraday_volume_orderflow
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

# MOD-SIG-093 intraday_volume_orderflow 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B10-01361（模块5 日内量能结构与订单流分析模型，
> 裁定=做 P1）+ 候选注册表 CAND-TESTB-008。
> 代码：`src/zephyr/signal_ashare/intraday_t0/intraday_volume_orderflow.py`

## 0. 定位

日内连续竞价（9:30–15:00）量能结构三件套（VP/CVD/VPIN）为 L2-A 信号缺口，
tick 数据链路已具备（深挖裁定理由）。本模块纯函数核对注入分钟K计算：
Volume Profile（POC/VA70%）+ CVD 背离追踪 + 50 桶 VPIN 日频输出。

与既有件边界（查重裁定）：
- MOD-SIG-089 auction_microstructure_analyzer：**盘前竞价**（9:15–9:25 七族特征）；
  本件为**日内连续竞价**量能结构，时段与口径正交（查重纪律④分工）。
- intelligence/event_score.py 内嵌 CVD 助手：PEAD 卖压吸收专用局部计算，非
  可复用信号件，不收编。
- 上游 D_DATA tick_subscriber（MOD-L00-001）/tick_redis_cache：数据注入位；
  本模块保持纯函数零 import 边（与 MOD-SIG-089 同构），生产接线留集成批。
- CVD 序列为本模块对外契约：MOD-SIG-094（Wyckoff 吸筹买点 CVD 确认）与
  MOD-SIG-095（多指标背离 CVD 腿）按鸭子类型消费，不反向 import。

## 1. 接口

```python
@dataclass(frozen=True) class IntradayOrderflowConfig   # n_bins/VA比例/lookback/桶参
@dataclass(frozen=True) class VolumeProfile             # poc/VA/total/bin_count
@dataclass(frozen=True) class CvdDivergence             # direction/bar_index/magnitude
@dataclass(frozen=True) class VpinResult                # vpin/bucket_count/degraded
class IntradayVolumeOrderflowAnalyzer:
    def volume_profile(self, bars, n_bins=None) -> VolumeProfile
    def cvd(self, bars) -> pd.Series                     # 对外 CVD 契约
    def cvd_divergences(self, bars, lookback=None) -> list[CvdDivergence]
    def vpin(self, bars, n_buckets=None, window=None) -> VpinResult
```

- VP：典型价 (H+L+C)/3 分 n_bins 桶；POC=最大量能桶中心；VA 自 POC 向量能
  大侧扩展至覆盖≥70%（可配）。
- CVD：Σ sign(close−open)×volume（BVC 简化口径，PIT 严格）；背离峰谷对位
  （价窗口新高/新低 vs CVD 不配合），magnitude=价格腿−CVD 腿（窗口量能归一）。
- VPIN：等量 50 桶（默认）|净 delta|/桶量，尾窗均值∈[0,1]；跨桶 bar 按量
  比例拆分；桶数<window → degraded=True。

## 2. 纪律

- 缺列/空表/负量/非法 n_bins/非法桶参/总量为零 → ValueError（fail-closed）。
- VPIN degraded 不静默（显式标记）；背离方向 bullish/bearish 封闭集。
- frozen dataclass、to_dict JSON 可序列化；纯函数不直连 DB、不荐股。

## 3. 依赖

- import：numpy、pandas（无 zephyr 内部 import 边）。
- 上游注入：D_DATA 分钟K（tick_subscriber/tick_redis_cache 聚合，集成批接线）。
- 下游候选：MOD-SIG-094 CVD 确认腿、MOD-SIG-095 CVD 背离腿、精筛装配层。

---

## 4. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 4.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/signal_ashare/intraday_t0/intraday_volume_orderflow.py` | ✅ 已实现 | |

### 4.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/research/research/signal_ashare/intraday_t0/test_intraday_volume_orderflow.py` | ✅ 已实现 | |

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
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-093`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-093` 的 4 个 file 节点 | design | `extract_depgraph.py --modules MOD-SIG-093` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-093 | MOD-SIG-093 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | planned | N/A | — |
| file_count | 4 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
