---
blueprint_id: MOD-SEC-026
module_name: supply_chain_security_scanner
domain: D_SECURITY
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
domain_id: D_SECURITY
path: src/zephyr/security/supply_chain_security_scanner.py
granularity: file
---

# MOD-SEC-026 supply_chain_security_scanner 蓝图（供应链安全扫描器）

> **module_id**: MOD-SEC-026 | **域**: D_SECURITY | **优先级**: P2
> **来源**: B12-03993（AUD-DRAFT-001-DIGEST P2 波 P2-W15，CAND-SEC-007，B12 §15.1）
> 代码：`src/zephyr/security/supply_chain_security_scanner.py`

## 0. 定位

供应链安全三件套：CycloneDX JSON SBOM生成器（从requirements锁文件解析注入reader）+许可证扫描（GPL/AGPL传染性告警规则表）+SBOM与CVE扫描结果关联（注入cve_scanner回调，CVE→组件映射报告）。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/security/test_supply_chain_security_scanner.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
