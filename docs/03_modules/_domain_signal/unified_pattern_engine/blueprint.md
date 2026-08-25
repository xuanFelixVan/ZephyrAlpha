---
blueprint_id: MOD-SIG-091
module_name: unified_pattern_engine
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
---

# MOD-SIG-091 unified_pattern_engine 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B1-01010（统一图形识别引擎 D-FACTOR-97，裁定=做 P1）+
> 候选注册表 CAND-TESTB-006。代码：`src/zephyr/signal_ashare/unified_pattern_engine.py`
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
