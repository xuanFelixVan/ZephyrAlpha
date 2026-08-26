---
blueprint_id: MOD-INF-081
module_name: reproducibility_packager
domain: D_INFRA_TELEMETRY
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
domain_id: D_INFRA_TELEMETRY
path: src/zephyr/infrastructure/system_telemetry/reproducibility_packager.py
granularity: file
---

# MOD-INF-081 reproducibility_packager 蓝图（可复现性包生成器）

> **module_id**: MOD-INF-081 | **域**: D_INFRA_TELEMETRY | **优先级**: P2
> **来源**: B1-00401（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-INFRATEL-001，C2）
> 代码：`src/zephyr/infrastructure/system_telemetry/reproducibility_packager.py`

## 0. 定位

实验一键打包：代码commit+参数+数据快照指针+依赖锁→可回放包（manifest.json+hash校验），打包/校验/回放指针解析三接口，mlflow Projects思想。包目录经注入root（默认.runtime/repro_packages），不触网。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/infrastructure/test_reproducibility_packager.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
