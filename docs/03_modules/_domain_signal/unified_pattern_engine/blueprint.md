---
blueprint_id: MOD-SIG-091
module_id: MOD-SIG-091
module_name: unified_pattern_engine
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

# MOD-SIG-091 unified_pattern_engine 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B1-01010（统一图形识别引擎 D-FACTOR-97，裁定=做 P1）+
> 候选注册表 CAND-TESTB-006。代码：`src/zephyr/signal_ashare/strategy_signal/unified_pattern_engine.py`
> **canonical 声明**：本条目与 W-P1-04 的 B10-01391（模块58 统一技术图形识别引擎）
> 同名同源；本波先施工，本模块即 canonical 实现，B10-01391 由其波次裁定 REVIEW。

## 0. 定位

场内仅有缠论结构/席位形态/reversal 散件，无统一引擎；该引擎是 97 形态→信号转化
（B1-00849）的前置依赖（深挖裁定理由）。本模块落**统一图形识别引擎**：

    OHLCV 多级别输入 → 统一 PatternEvent 契约
    （图形类型+置信度+关键点位+预测方向+历史胜率）

- **六类图形封闭集**：反转/持续/趋势/支撑阻力/缠论/波浪（PatternClass）。
- **规则引擎优先**（MVP 主力）：缠论腿（收编 MOD-SIG-072 chanlun_structure：中枢/笔
  事件）、支撑阻力腿（收编 MOD-SIG-069 trendline_sr_detector：水平位/趋势线事件）、
  经典腿（双顶/双底反转 + 平台突破持续）。
- **DTW 模板匹配**：归一化序列 DTW 距离≤阈值→模板形态事件（模板库注入，
  距离越界不产出）。
- **历史胜率**：win_rate_provider 注入契约（None=无统计），引擎不自建统计。
- **CNN/Transformer 形态分类列后续档**（min_build_spec 明示），本波不施工。

收编边界说明：seat_pattern_analyzer（MOD-SIG-056）为披露席位数据（非 OHLCV 图形），
min_build_spec 虽列"收编"，其输入契约与本引擎正交，蓝图裁定**后续以适配器接入**
（记录为遗留项）；本波收编 chanlun_structure/trendline_sr_detector 两件 OHLCV 散件。

## 1. 接口

```python
class PatternClass(str, Enum)       # 6 类封闭集
class PatternDirection(str, Enum)   # 向上/向下/中性
@dataclass(frozen=True) class KeyPoint
@dataclass(frozen=True) class PatternEvent        # 统一契约
@dataclass(frozen=True) class PatternEngineConfig
@dataclass(frozen=True) class PatternScanResult
@dataclass(frozen=True) class PatternTemplate     # DTW 模板（归一化序列+类别+方向）
class UnifiedPatternEngine:
    def __init__(self, config=None, *, win_rate_provider=None, templates=())
    def recognize(self, symbol, highs, lows, closes, *, timeframe="1d") -> PatternScanResult
```

## 2. 纪律

- 输入等长/非空/正价 fail-closed（ValueError）；缠论/SR 腿内部降级不传染整引擎
  （腿级 notes 留痕）。
- 去重：同 (name, anchor_idx) 取置信度最高；输出按置信度降序。
- 置信度规则文档化（规则腿静态初拍值 + DTW 腿 1−距离/阈值），待回验标定批替换。
- frozen dataclass、to_dict JSON 可序列化；纯算法核，不直连 DB/行情。

---

## 3. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 3.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/signal_ashare/strategy_signal/unified_pattern_engine.py` | ✅ 已实现 | |

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
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-091`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-091` 的 2 个 file 节点 | design | `extract_depgraph.py --modules MOD-SIG-091` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-091 | MOD-SIG-091 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | planned | N/A | — |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
