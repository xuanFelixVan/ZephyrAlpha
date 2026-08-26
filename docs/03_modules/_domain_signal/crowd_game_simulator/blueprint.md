---
blueprint_id: MOD-SIG-114
module_name: crowd_game_simulator
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
path: src/zephyr/signal_ashare/crowd_game_simulator.py
granularity: file
---

# MOD-SIG-114 crowd_game_simulator 蓝图（群体博弈模拟器）

> **module_id**: MOD-SIG-114 | **域**: D_ASHARE_SIGNAL | **优先级**: P2
> **来源**: B1-00169（AUD-DRAFT-001-DIGEST P2 波 P2-W05，CAND-TESTB-031，C2 C-036）
> 代码：`src/zephyr/signal_ashare/crowd_game_simulator.py`

## 0. 定位

轻量博弈推演：四类玩家（北向/公募/游资/散户词表闭合）行为规则库（历史统计先验参数注入）+合力方向（加权净方向）/分歧度（方向熵）输出+盘后运行语义+输出标注推断性质仅作信号输入。ABM思想规则库版。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/signal_ashare/test_crowd_game_simulator.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
