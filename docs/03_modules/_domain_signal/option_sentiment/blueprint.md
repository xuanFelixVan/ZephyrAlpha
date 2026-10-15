---
blueprint_id: MOD-SIG-059
module_id: MOD-SIG-059
module_name: option_sentiment
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: production
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.1"
created: 2026-08-22
last_updated: 2026-08-22
owner: ZephyrAlpha-Owner
responsibility_domain: 
---

# MOD-SIG-059 option_sentiment 蓝图

> 紧凑版（SOP Step 4 补建）。设计真源：44号备忘录 §9.9（华泰 2026-03 机构范式），M1-⑨ 情绪注解维度⑨。
> 代码：`src/zephyr/signal_ashare/sentiment/option_sentiment.py`

## 0. 定位

期权情绪三件套——A 股单边做多市场衍生品"少而精"只取 PCR+IV 两指标最有效，加 Skew 尾部偏度作机构行为佐证，合成"情绪注解维度⑨"（候选消费方 MOD-SIG-025 综合分，权重 ≤0.10 纪律由下游控制）。主标的=300ETF 期权（510300.SH），50ETF/500ETF/科创同算法可经 config.underlying 扩展。

## 1. 接口

```python
def compute_option_sentiment(
    trade_date: str | date | datetime | None = None,  # None=主标的 iv_surface 最新数据日（PIT 数据日口径）
    ch_client: Any | None = None,                     # None=延迟取 ch_writer.get_client，不可得→degraded
    config: OptionSentimentConfig | None = None,      # None=44号 §9.9 + 2026-08-22 数据实证默认口径
) -> OptionSentimentResult
```

只读四表：option_iv_surface / option_kline / option_greeks / calendar_event。

## 2. 输出契约

`OptionSentimentResult`（frozen dataclass，asdict JSON 可序列化）：

- F1 `pcr` / `pcr_basis` / `pcr_percentile`：成交量 PCR=Σ认沽 volume/Σ认购 volume（无任何表含 open_interest 持仓列→实证降级成交量口径留痕；OI 回填后自动切持仓口径）；分位 <20%=过度乐观反向风险，>80%=恐慌过度底部区（pcr_min_periods=20 守卫）
- F2 `iv_rank` / `iv_jump_flag`：平值 IV 分位（最近月 strike≈中位数选约，atm_basis="strike_median" 留痕；min_periods=60 守卫）；IV 单日跳升 >+3σ→避险急增
- F3 `skew_norm` / `skew_extreme` / `divergence_warning`：skew=IV(25Δ沽)−IV(25Δ购) 经 greeks.delta 选约（|delta∓0.25| 最近者）JOIN iv_surface 取 IV；归一 skew>90% 分位=极端左偏；PCR 低分位×Skew 极端背离=多空分歧最大警示
- `composite_score ∈ [-1,1]`（可用子分均值，缺项不累及）+ `annotation` 中文注解文本链（维度⑨直接可消费）
- `m1_threshold_scale`：期权到期日（calendar_event index_option_expiry 当日）=0.8（防伽马挤压假情绪），否则 1.0

## 3. 不变量（头注 INVARIANTS 原文）

- m1_threshold_scale ∈ {1.0, 0.8}
- pcr_basis ∈ {"volume", "open_interest"}（当前实证恒为 "volume"）
- 无数据/查询异常/客户端不可用 MUST 返回 degraded=True 空结果不炸
- 各字段独立降级互不累及
- iv_surface.delta 全 0 实证不可用，禁止以该列选约

## 4. 降级行为

- ERROR_CONTRACT：查询异常/客户端不可用→degraded=True 不抛；trade_date 格式非法→ValueError（fail-closed）
- 分位窗样本不足（pcr<20 / iv_rank<60 / skew<10 守卫）→对应字段 None 降级
- iv_surface data_source 08-14 切换（miniqmt 4 到期月→akshare_sina 仅最近月）→统一限定"最近月"跨源一致口径
- option_greeks option_type 空串→由 delta 符号推断（>0=call，<0=put）
- calendar_event 查询失败→fail-open m1_threshold_scale=1.0 留痕

## 5. 边界（不做）

- MVP 阶段无消费方（候选：MOD-SIG-025 情绪注解维度⑨ 经输入契约注入，权重≤0.10；M1 阈值缩放因子消费方）
- 本模块只出分数与注解文本，权重由下游控制

## 6. 测试

tests/signal_ashare/sentiment/test_option_sentiment.py

---

## 7. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 7.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/signal_ashare/sentiment/option_sentiment.py` | ✅ 已实现 | |

### 7.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §7（本节）→ 知道「哪些已实现、在哪里」
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
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-059`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-059` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIG-059` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-059 | MOD-SIG-059 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
