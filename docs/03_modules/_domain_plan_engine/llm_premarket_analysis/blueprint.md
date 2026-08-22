---
blueprint_id: MOD-PLAN-007
module_name: llm_premarket_analysis
domain: D_PLAN
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: testing
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-22
last_updated: 2026-08-22
owner: ZephyrAlpha-Owner
---

# MOD-PLAN-007 llm_premarket_analysis 蓝图

> 紧凑版（92 号清单 §8.6 工单落地配套，SOP Step 4 补建）。设计真源：44号备忘 §9.14 M3-⑨ + §4 表 M3-⑨ 行。
> 代码：`src/zephyr/plan_engine/llm_premarket_analysis.py`

## 0. 定位

LLM 盘前综合复盘与当日情景分析核心件。定位铁律：**LLM 是"分析参考注解层"不是信号真源**——输出只进 M3 情景注解，不直接改边界档位（防幻觉直通交易，与 90号 §7"不预测"纪律一致）。运行时点=次日 8:00 盘前（昨日 A 股收盘+隔夜美股+A50 夜盘+夜间新闻齐备，DeepSeek 谷时窗口）。

## 1. 接口

```python
def build_premarket_package(trade_date, ch_client=None, config=None, *,
    asof_cutoff=None, injected: PremarketInjections | None = None) -> PremarketPackage

def run_llm_analysis(trade_date, llm_client=None, ch_client=None, config=None, *,
    db_path=None, asof_cutoff=None, injected=None) -> LlmRunResult
```

- `llm_client`：可调用对象 prompt→text（str 或 Mapping {text, tokens_in, tokens_out, cost_yuan} 计量形态）；**本模块不直连任何 LLM API**——阶段三 llm_runtime_gateway（09架构10号件）注入；None→status=skipped_not_wired 落库留痕不炸（本阶段常态）
- 七族输入：指数/情绪/板块/衍生/外盘/资金/日历（44号 §9.14，~8-15K token），CH 日频 + PremarketInjections（MOD-SIG-025/057/058/059/060 输出+BS-005，可缺省）
- v1 单调用 / v2 多空辩论三调用（config.debate_mode，默认 False；多-空-综合席编排，借鉴 TradingAgents 不引入框架本体）

## 2. 输出契约

- `PremarketPackage`：trade_date/asof_cutoff/families（七族载荷）/input_hash（canonical JSON SHA-256，铁律④）/rejected（PIT 拒收留痕）/built_at/trace
- `LlmDailyAnalysis`：date + model_version/prompt_version/input_hash（铁律②③④以运行侧权威值为准）+ scenarios{gap_up/flat/gap_down 各 {prob, key_levels, action_boundary}} + risk_points/watch_sectors/confidence_note
- `LlmRunResult`：status∈{success, invalid, skipped_not_wired} + analysis + 计量（tokens/cost/latency，v2=三调用合计）+ row_id/db_logged + errors + package
- 落库：governance.db `llm_daily_analysis` 表（92号 D2 授权，DDL-as-Code 本模块唯一真源，`ensure_llm_daily_analysis_table` 幂等建表）；UNIQUE(trade_date, model_version, prompt_version, input_hash) 同键跳过保首条
- 输出校验拒收规则：缺字段/三情景键不全/prob 越界 [0,1]/概率和偏离 1 超 ±0.02/date 不符/回显铁律字段不一致→标 invalid 落库留痕不炸

## 3. 不变量（头注 INVARIANTS 原文）

- PIT 铁律①全部输入须"T+1 日 08:00 前可见"（asof_cutoff 护栏：数据点时间戳>cutoff 拒绝入包+rejected 留痕，fail-closed；SQL 层 trade_date<cutoff 日双护栏）
- 铁律②③ model_version/prompt_version 冻结入库（版本漂移=新型 PIT 风险；v2 辩论有效版本串=+debate 后缀防幂等键碰撞）
- 铁律④ input_hash=输入数据包 canonical JSON 的 SHA-256（回测复现校验同源）
- LLM 是"分析参考注解层"不是信号真源——输出只进 M3 情景注解，不直接改边界档位
- 本模块不直连任何 LLM API（llm_client 注入；None→skipped_not_wired 落库留痕不炸）
- 落库幂等同键跳过保首条；SQL 参数化+常量（NO-BARE-SQL）；db_path 默认 None 走 DB_PATH SSoT；输出纯 dataclass JSON 可序列化

## 4. 降级行为

- trade_date/asof_cutoff 非法→ValueError fail-closed（唯一 fail-closed 口）
- CH 单族查询/解析异常→该族降级（字段 None+status 留痕）不炸整体
- llm_client 调用异常/返回类型非法/输出契约校验失败→status=invalid 落库留痕（raw_output 截断 8000 字符）
- DB 写失败 fail-open（db_logged=False+errors 留痕）
- 注入契约带各自产出时点，晚于 cutoff 整块拒入+rejected 留痕（PIT 逐点校验）

## 5. 边界（不做）

- 不直连 LLM API / 不改边界档位（注解层）/ 不做方向点预测
- 不改 scenario_planner 等既有五件（消费对接：将来按 (trade_date, model_version, prompt_version) 读 success 行作三情景"注解栏"，**不一致时以规则为准**，命中率>55% 才讨论升级加权且需 Owner 裁定）
- 不写注册表（登记去向=统筹裁定）

## 6. 测试

tests/plan_engine/test_llm_premarket_analysis.py
