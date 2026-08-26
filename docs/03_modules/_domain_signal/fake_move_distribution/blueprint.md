---
blueprint_id: MOD-SIG-124
module_name: fake_move_distribution
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-26
last_updated: 2026-08-26
owner: ZephyrAlpha-Owner
priority: P2
blueprint_level: module
domain_id: D_ASHARE_SIGNAL
path: src/zephyr/signal_ashare/fake_move_distribution.py
granularity: file
---

# MOD-SIG-124 fake_move_distribution 蓝图（主力假动作与筹码派发识别）

> **module_id**: MOD-SIG-124 | **域**: D_ASHARE_SIGNAL | **优先级**: P2
> **来源**: B10-01425（AUD-DRAFT-001-DIGEST P2 波 P2-W05，CAND-TESTB-044，A1 模块27）
> 代码：`src/zephyr/signal_ashare/fake_move_distribution.py`

## 0. 定位

假动作6模式规则库（假拉升真出货/假突破真派发/假吸筹真对倒/假洗盘真出货/假护盘真诱多/假反弹真派发词表闭合，各含表面行为+底层矛盾信号）+7维信号打分（主动买入占比/大单净流入/量能持续/板块跟涨率/拉升时段/底部筹码/龙虎榜注入数据）+>85%暂停追涨输出FakeMoveWarning。canonical承接TESTB-056归并。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/signal_ashare/test_fake_move_distribution.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
