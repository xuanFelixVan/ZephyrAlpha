---
task_id: "TASK-INF-0203"
source_blueprint: "MOD-INF-014"
source_section: "蓝图 §3 L0 供应链安全"
title: "L0 供应链安全层完整实现——模型验证+依赖扫描+MCP验证+Prompt模板审计"
description: |
  按照蓝图 §3.2~§3.5 实现 L0 SupplyChainGuard 类。
  包含五个子模块：模型来源验证（SHA256对比+许可审计）、依赖安全扫描（pip-audit/safety/npm audit集成）、
  MCP服务器身份验证+工具描述审计、Prompt模板版本控制审计、Slopsquatting幻觉包存在性验证。
  集成 Rules File 完整性保护（蓝图 §25.3 盲点三）。
priority: "P0"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\protocol.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\l0_supply_chain.py"
    description: "L0 SupplyChainGuard 类——模型验证+依赖扫描+MCP验证+Prompt模板审计"
  - path: "D:\\ZephyrAlpha\\tests\\llm_security\\test_l0_supply_chain.py"
    description: "L0 供应链安全单元测试"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\l0_supply_chain.py"
  - "D:\\ZephyrAlpha\\tests\\llm_security\\test_l0_supply_chain.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\input_sanitizer.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式 TASK-INF-{NNNN}"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2——禁止 dataclass"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
    reason: "本蓝图——§3 L0 供应链安全完整接口定义+工具链+施工状态"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\protocol.py"
    reason: "LSG 抽象基类——L0 需继承的接口契约"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 60
acceptance_criteria:
  - "SupplyChainGuard 类含 verify_model() / scan_dependencies() / verify_mcp_server() / audit_prompt_template() / record_model_provenance() 全部 5 个方法"
  - "verify_model() 实现 SHA256 哈希对比逻辑"
  - "scan_dependencies() 调用 pip-audit 或 safety CLI"
  - "verify_mcp_server() 包含 MCP 工具描述审计——检测隐藏指令/异常描述"
  - "audit_prompt_template() 检查 prompt 模板来源（Git 版本控制）+ 内容安全性"
  - "包含 RulesFileSecurityGuard 类（蓝图 §25.3）——规则文件 SHA256 基线验证"
  - "包含 Slopsquatting AI 幻觉包存在性验证——五步审计流水线（蓝图 §37）"
  - "包含 MCP STDIO RCE 检测 pattern + Cross-Server 攻击图（蓝图 §57）"
  - "Pydantic V2 BaseModel——VerifyResult/ScanResult/AuditResult 模型"
  - "15 条单元测试覆盖全部方法"
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\llm_security\layers\l0_supply_chain.py
  2. 删除 D:\ZephyrAlpha\tests\llm_security\test_l0_supply_chain.py
depends_on:
  - "TASK-INF-0201"
blocked_by: []
status: "done"
tags_fn:
  - "security"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-014"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# 目标

实现 LSG L0 供应链安全层——确保 LLM 应用的所有外部组件来源可信、完整性可验证、安全状态已知。覆盖模型验证、依赖扫描、MCP 服务器审计、Prompt 模板版本控制、AI BOM 生成、Rules File 完整性保护、Slopsquatting 防御、MCP STDIO RCE 检测。

## 触发条件

- TASK-INF-0201（模块骨架搭建）已通过
- 蓝图 §3 已定义完整接口 + 蓝图 §24/§25.3/§37/§57 已定义扩展子模块

## 执行步骤

### 读
- `D:\ZephyrAlpha\docs\03_modules\_cross_layer\llm-security\blueprint.md` §3 + §24 + §25.3 + §37 + §57
- `D:\ZephyrAlpha\src\zephyr\llm_security\protocol.py`

### 做
1. 实现 `SupplyChainGuard` 类——蓝图 §3.3 的 5 个核心方法
2. 实现 `RulesFileSecurityGuard` ——蓝图 §25.3 的 rules file 基线哈希验证
3. 实现 `SlopsquattingDetector` ——蓝图 §37 的五步审计流水线
4. 实现 `MCPDeepSupplyChainScanner` ——蓝图 §57 的 MCP STDIO RCE + Cross-Server 攻击图检测
5. 编写 15 条单元测试覆盖所有方法

### 产
- `l0_supply_chain.py`
- `test_l0_supply_chain.py`

### 检
```bash
pytest tests/llm_security/test_l0_supply_chain.py -v
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | coverage | SupplyChainGuard 5/5 方法有测试 |  
| 2 | lint | 0 errors, 0 warnings |
| 3 | files | deliverables 全部存在 + UTF-8 |
