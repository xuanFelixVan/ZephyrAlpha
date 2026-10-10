---
blueprint_id: MOD-SIG-096
module_id: MOD-SIG-096
module_name: relative_strength_screener
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

# MOD-SIG-096 relative_strength_screener 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B10-01365（模块9 多维度相对强弱筛选模型，
> 裁定=做 P1）+ 候选注册表 CAND-TESTB-011。
> 代码：`src/zephyr/signal_ashare/screening/relative_strength_screener.py`

## 0. 定位

短线强度引擎+IC 加权校准已有（MOD-SIG-034/strength_ic_weight_calibrator）；
52 周新高接近度（>0.95）+新高放量突破确认为缺口。本模块按 O'Neil RS 评级
口径合成多维相对强弱评分（0-100），产出供精筛选配（接入留集成批）。

与既有件边界（查重裁定）：
- MOD-SIG-034 quant_short_term_strength_engine：短线六维评分（RS 维=
  个股涨幅−大盘涨幅的短线口径）；本件为中长期区间 RS+52 周结构+突破确认，
  正交互补。
- strength_ic_weight_calibrator：IC 权重校准件，不覆盖 52 周新高维度。
- MOD-SIG-048 fine_scoring_engine：精筛消费方候选（鸭子类型接入，不 import）。

## 1. 接口

```python
@dataclass(frozen=True) class RelativeStrengthConfig   # 窗口/权重/阈值（构造即校验）
@dataclass(frozen=True) class RelativeStrengthScore    # 四维子分+合成+标记
class RelativeStrengthScreener:
    def score(self, symbol, close, high, volume,
              benchmark_close) -> RelativeStrengthScore
    def rank(self, bars, benchmark_close) -> list[RelativeStrengthScore]  # 降序
```

合成分 = 区间RS 40% + 结构强弱 25% + 52周接近度 20% + 放量突破 15%（可配）。
- 区间 RS：20/60/120 日个股−基准加权超额（0.5/0.3/0.2）→ clip(50+超额×200,0,100)。
- 结构强弱：close>MA20>MA50>MA120 四条件各 25 分。
- 52 周接近度：close/max(high,252)；≥0.95 → near_high_52w；子分 0.8→1.0 线性。
- 放量突破：收盘创前 52 周新高且量≥1.5×20 日均量→confirmed/100 分；
  新高无量→40 分；无新高→0 分。

## 2. 纪律

- 空序列/不等长/非正价格/非有限值/负量 → ValueError（fail-closed）。
- 配置构造即校验：区间窗与权重等长且各自和=1、四维权重和=1、阈值∈(0,1]、
  量比≥1、year_bars≥30。
- 历史不足 252 根 → degraded=True 显式降级（窗口自适应，不静默）。
- PIT：仅用序列末端及历史窗口；frozen dataclass、to_dict JSON 可序列化；
  不直连 DB、不荐股。

## 3. 依赖

- import：numpy、pandas（无 zephyr 内部 import 边）。
- 上游注入：D_DATA 个股日线+基准指数序列；下游候选：MOD-SIG-048 精筛/选股漏斗。

---

## 4. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 4.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/signal_ashare/screening/relative_strength_screener.py` | ✅ 已实现 | |

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
