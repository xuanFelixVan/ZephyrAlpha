---
blueprint_id: MOD-SIG-108
module_id: MOD-SIG-108
module_name: multi_factor_timing_overlay
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: production
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.1"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
responsibility_domain: 
---

# MOD-SIG-108 multi_factor_timing_overlay 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B10-01482（模块57 多因子叠加择时模型，裁定=做 P1）+ 候选注册表 CAND-TESTB-025。
> 代码：`src/zephyr/signal_ashare/multi_factor_timing_overlay.py`

## 0. 定位

场内对账（查重铁律⑤⑥探查在案）：

- timing_analyst_agent（MOD-AU-010）= 择时 **Agent 裁决层**（状态×预测×做T点
  →时机与执行建议，L1 建议级+人工确认回路）；本件=决策编排器上游**信号合成
  层**（6 源叠加+共振检测），为其供给合成读数，不替代其裁决；
- strength_ic_weight_calibrator = 短线强度 6 维**子分** IC 校准（维度族正交）；
  bma_signal_weighter（MOD-L02-001，D_FACTOR）= 信号级 BMA 后验权重**生产方**
  （其 CONSUMERS 在案预留本件装配批）——本件消费 IC/BMA 权重注入，不自建
  校准/后验；
- 各择时单件（MOD-SIG-099 情绪反转/MOD-SIG-039 体制转换/波动突破/日历/
  量能/北向）= 单源**生产方**（本件上游，读数鸭子类型注入）；
- **6 源择时信号库 + IC 加权或 BMA 叠加 + ≥3 同向共振高置信标记无实现**
  （深挖批 min_build_spec 明示缺口，Rapach&Zhou 2013 组合预测），本模块落地。

## 1. 接口

```python
TIMING_SOURCES  # 6源封闭集（sentiment_reversal 情绪反转 / regime_shift 体制转换 /
                # volatility_breakout 波动突破 / calendar 日历 / volume 量能 / northbound 北向）
@dataclass(frozen=True) class TimingSignal        # source+direction(-1/0/1)+strength[0,1]
@dataclass(frozen=True) class TimingOverlayConfig # 共振阈≥3/方向阈±0.10/权重下限
@dataclass(frozen=True) class TimingOverlayResult # 合成分+方向+共振计数+高置信+权重归因
class MultiFactorTimingOverlay:
    def overlay(self, signals, *, ic_weights=None, bma_weights=None) -> TimingOverlayResult
```

- **加权叠加**：composite=Σw_i×direction_i×strength_i；权重优先级
  bma_weights>ic_weights>等权兜底（均按非负 clip 后 Σ=1 归一；全零/缺失维
  回退等权+fallback_used 留痕，语义对齐 IC 加权工程修正惯例）。
- **方向判定**：composite>+0.10 bullish / <−0.10 bearish / 其余 neutral
  （文档化 MVP 初拍阈值，待回验标定批替换）。
- **共振检测**（min_build_spec 既定）：≥3 独立源同向（非零）→
  high_confidence=True + resonance_direction；反向混杂按多数向计数。
- 输入源缺漏（<6 源）不阻断：按在场源归一化加权 + notes 留痕（降级不抛）。

## 2. 纪律

- 未知 source/重复 source/direction 非 {-1,0,1}/strength 越界/非有限/非法
  配置 → ValueError（fail-closed）；空信号序列 → ValueError。
- 合成语义非异常：neutral/低置信经返回值表达，不抛错。
- frozen dataclass asdict JSON 可序列化；不做 Agent 裁决（MOD-AU-010 职责）、
  不自建 IC 校准或 BMA 后验（上游注入）、不荐股。

## 3. 依赖

- 无 zephyr import（纯函数核，与 MOD-SIG-089/092~107 同构纪律）。
- 语义上游（鸭子类型注入，生产接线留集成批）：6 源择时生产方（MOD-SIG-099
  情绪反转/MOD-SIG-039 体制转换/波动突破/日历/量能/北向读数）；
  strength_ic_weight_calibrator IC 口径 / bma_signal_weighter（MOD-L02-001）
  BMA 后验权重（TSV dependencies 在案）。
- 下游候选：决策编排器（注册表归属"决策编排器模块57"）与 MOD-AU-010 裁决层。

## 4. 测试

`tests/signal_ashare/test_multi_factor_timing_overlay.py`：
6 源封闭集、IC/BMA/等权权重优先级与归一、负权重 clip、合成分与方向阈、
≥3 同向共振高置信（含反向混杂）、缺源降级、非法输入 fail-closed、
frozen/JSON 契约。

---

## 5. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 5.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 5.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §5（本节）→ 知道「哪些已实现、在哪里」
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
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-108`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-108` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIG-108` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-108 | MOD-SIG-108 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
