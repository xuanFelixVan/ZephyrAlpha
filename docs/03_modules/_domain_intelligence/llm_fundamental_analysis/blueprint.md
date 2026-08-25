---
blueprint_id: MOD-INT-LLM-FUND
module_name: llm_fundamental_analysis
domain: D_INTELLIGENCE
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_INTELLIGENCE
path: src/zephyr/intelligence/llm_fundamental_analysis.py
granularity: file
---

# MOD-INT-LLM-FUND llm_fundamental_analysis 蓝图（LLM Agent 基本面分析）

> **module_id**: MOD-INT-LLM-FUND | **域**: D_INTELLIGENCE | **优先级**: P1
> **来源**: B10-01840（AUD-DRAFT-001-DIGEST P1 波 W-P1-10，§29.11）
> 代码：`src/zephyr/intelligence/llm_fundamental_analysis.py`

## 0. 定位

多 Agent 基本面分析（业界对标 FinGPT/FinRobot 多 Agent 财报分析）：三 Agent
——财报质量 Agent（营收增速/利润质量/现金流）、新闻政策 Agent（政策利好/
行业风险）、综合裁决 Agent（多空建议+置信度）——LLM 定性与模型定量加权
融合；4 融合点留痕（C-014 情感/C-016 事件注入/筛选漏斗第四层/C-013 自然
语言指令解析）；部署双模（本地 Qwen2.5 量化版盘后离线 + API 盘中 <5s）；
**结论仅作信号输入不直接下单**。

与既有族分工（查重裁定）：
- MOD-INT-MKT-INTERPRETER llm_market_interpreter：新闻/研报/社媒三路统一
  市场解读引擎（主题/情感/影响标的），无财报质量 Agent、无多 Agent 裁决、
  无定性定量加权融合——本模块新闻政策 Agent 可经注入 callable 复用其解读
  产物，不复制三路解读逻辑。
- MOD-PLAN-007 llm_premarket_analysis：盘前综合复盘单点（七族输入→情景
  注解层），非基本面多 Agent 架构。
- MOD-INT-AISA news_sentiment_analyzer：单路新闻情感打分+窗口聚合。
- 本模块判定核心纯内存，LLM 能力经注入 callable 消费（本地盘后/API 盘中
  双模各一 callable），零密钥零直连。

## 1. 判定核心（纯内存，无 IO）

- `analyze(bundle, mode)`：三路 Agent 判定——`report_agent`（财报质量）/
  `news_agent`（新闻政策）/`verdict_agent`（综合裁决）callable 按 mode
  （local/api）解析注入；任一 Agent 输出结构非法（非 JSON 四字段/置信度
  越界/方向值域外）→ `FundamentalAnalysisError`（Fail-Closed，不放行伪
  结构）。
- `fuse(verdicts, quantitative, weights)`：定性定量加权融合——定性裁决
  （方向×置信度）与定量分（quantitative_score ∈ [-1,1]）按声明式权重
  （qualitative_weight + quantitative_weight = 1，非法 → ValueError）
  融合出最终 `FundamentalVerdict`（direction bullish/neutral/bearish +
  confidence ∈ [0,1] + fused_score）。
- 4 融合点：`fusion_channels` 声明（c014_sentiment/c016_event/funnel_l4/
  c013_directive），实际消费的非空通道落 `fusion_points_used` 留痕。
- 双模：mode=local（盘后离线）/api（盘中 <5s）；未知 mode → ValueError；
  对应 callable 未注入 → ValueError（Fail-Closed）。
- 审计：每次分析产 `audit_record`（输入指纹/三路裁决/融合结果/融合点/
  mode），经注入 `audit_sink` 外发；sink 异常不阻断（sink_errors 留痕）。

## 2. 接口

```python
@dataclass(frozen=True) AgentVerdict: agent/direction/confidence/rationale
@dataclass(frozen=True) FundamentalInputBundle: symbol/financial_report/news_policy/quantitative_score/fusion_channels/as_of
@dataclass(frozen=True) FundamentalVerdict: symbol/direction/confidence/fused_score/agent_verdicts/fusion_points_used/mode
@dataclass(frozen=True) FusionWeights: qualitative_weight/quantitative_weight
class LlmFundamentalAnalysis(weights=None, agents=None, audit_sink=None):
    analyze(bundle, mode) -> FundamentalVerdict
class FundamentalAnalysisError(ZephyrBaseError)
```

## 3. 不变量

- 判定核心纯内存无 IO；LLM 调用全经注入 callable；零密钥字段。
- LLM 输出须为合法 JSON（direction/confidence/rationale 等字段值域强
  校验），否则 `FundamentalAnalysisError`（Fail-Closed）。
- 置信度恒 ∈ [0,1]；定量分恒 ∈ [-1,1]；权重和恒 = 1（容差 1e-6）。
- 仅信号输入：输出无下单语义，结论经 audit_sink 入审计链。

## 4. 依赖

- MOD-INT-MKT-INTERPRETER llm_market_interpreter（设计边：新闻政策解读
  语义对齐）
- MOD-INT-API-LLM-POOL api_llm_pool（设计边：盘中 API 模式池治理对齐）
- MOD-PLAN-007 llm_premarket_analysis（设计边：盘前 LLM 分析单点对齐）

## 5. MVP 边界

- 运行时接线（report/news/verdict 三 Agent callable 接本地池/API 池、
  C-014/C-016/漏斗第四层/C-013 四融合点真实输入装配、audit_sink 接审计
  链）留运行时装配批；本模块交付三 Agent 判定核心 + 定性定量加权融合 +
  融合点留痕 + 双模契约。
