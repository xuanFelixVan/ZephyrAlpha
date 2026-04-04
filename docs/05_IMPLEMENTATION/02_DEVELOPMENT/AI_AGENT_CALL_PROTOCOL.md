---
standard_type: 技术文?
applicable_scope: 系统实施
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
owner: 实施负责?
version: 1.0.0
module_id: IMP_AI_AGENT_CALL_PROTOC
created_date: 2026-04-02
last_updated: 2026-04-02
---
# 智能体间调用协议 v1.0

## 1. 概述

本文档定义了清风量化系统中各AI智能体之间的标准化调用协议，确保智能体协作高效、数据传递规范、错误处理统一。协议遵?*职责驱动、接口明确、数据标准化**的原�?

## 2. 智能体角色定?

| 智能体标识名 | 中文名称 | 核心职责 | 所属架构层 |
|--------------|----------|----------|------------|
| `blueprint-architect` | 蓝图架构?| 负责系统蓝图设计、架构规划、模块职责定?| Layer 0-11 架构设计?|
| `spec-approver` | 审批智能?| 负责技术规格书撰写、方案评审、技术可行性评?| 技术评审层 |
| `development-agent` | 开发智能体 | 负责代码实现、模块开发、测试编?| 开发实施层 |
| `audit-sentinel` | 审计哨兵 | 负责系统审计、代码质量检查、安全扫?| 质量监控?|

## 3. 调用触发条件

### 3.1 蓝图架构??审批智能?
- **触发条件**：蓝图设计完成，需要进行技术规格书撰写和方案评?
- **传递数?*：蓝图文档路径、设计概要、关键需求点
- **预期输出**：技术规格书、技术评审报?

### 3.2 审批智能??开发智能体
- **触发条件**：技术评审通过，需要开始代码实?
- **传递数?*：技术规格书路径、评审报告、实施约束条?
- **预期输出**：代码实现、模块文档、测试用?

### 3.3 开发智能体 ?审计哨兵
- **触发条件**：代码开发完成，需要进行质量检?
- **传递数?*：代码路径、测试报告、构建结?
- **预期输出**：审计报告、质量评分、改进建?

## 4. 数据传递格?

### 4.1 通用请求格式
所有智能体调用必须使用以下JSON格式?

```json
{
  "request_id": "uuid-v4-生成唯一标识",
  "timestamp": "ISO 8601时间?,
  "source_agent": "调用方智能体标识?,
  "target_agent": "被调用方智能体标识名",
  "operation": "操作类型",
  "parameters": {
    // 操作特定参数
  },
  "context": {
    "project_root": "项目根目录绝对路?,
    "current_phase": "当前开发阶?,
    "priority": "优先级（high/medium/low?
  }
}
```

### 4.2 操作类型定义

| 操作类型 | 说明 | 源智能体 | 目标智能?|
|----------|------|----------|------------|
| `convert_blueprint_to_spec` | 蓝图转技术规格书 | blueprint-architect | spec-approver |
| `review_technical_spec` | 评审技术规格书 | spec-approver | spec-approver |
| `generate_implementation` | 生成代码实现 | spec-approver | development-agent |
| `audit_code_quality` | 审计代码质量 | development-agent | audit-sentinel |
| `assess_technical_feasibility` | 评估技术可�?| spec-approver | spec-approver |
| `analyze_risk` | 分析风险 | spec-approver | spec-approver |
| `calculate_implementation_complexity` | 计算实施复杂?| spec-approver | spec-approver |

### 4.3 特定操作参数

#### 4.3.1 convert_blueprint_to_spec（蓝图转技术规格书?
```json
{
  "parameters": {
    "blueprint_path": "蓝图文档绝对路径",
    "output_dir": "技术规格书输出目录",
    "template_path": "技术规格书模板路径（可选）",
    "generate_review_report": true
  }
}
```

#### 4.3.2 review_technical_spec（评审技术规格书?
```json
{
  "parameters": {
    "spec_path": "技术规格书绝对路径",
    "blueprint_path": "关联的蓝图文档路径（可选）",
    "assessment_tools": ["technical_feasibility", "risk_analysis", "implementation_complexity"],
    "output_dir": "评审报告输出目录"
  }
}
```

#### 4.3.3 generate_implementation（生成代码实现）
```json
{
  "parameters": {
    "spec_path": "技术规格书绝对路径",
    "review_report_path": "评审报告路径",
    "output_dir": "代码输出目录",
    "module_name": "模块名称",
    "programming_language": "python"
  }
}
```

## 5. 响应格式

### 5.1 成功响应
```json
{
  "response_id": "与request_id对应",
  "timestamp": "ISO 8601时间?,
  "status": "success",
  "execution_time": "执行时间（秒?,
  "results": {
    "output_files": [
      {
        "path": "输出文件路径",
        "type": "文件类型",
        "description": "文件描述"
      }
    ],
    "summary": {
      "score": "评分?-100?,
      "level": "等级",
      "recommendation": "建议"
    }
  },
  "next_steps": [
    {
      "agent": "下一个智能体标识?,
      "operation": "建议的操?,
      "description": "操作描述"
    }
  ]
}
```

### 5.2 错误响应
```json
{
  "response_id": "与request_id对应",
  "timestamp": "ISO 8601时间?,
  "status": "error",
  "error_code": "错误代码",
  "error_message": "错误描述",
  "error_details": "详细错误信息",
  "suggested_recovery": "建议的恢复措?
}
```

## 6. 错误代码定义

| 错误代码 | 说明 | 处理建议 |
|----------|------|----------|
| `AGENT_NOT_FOUND` | 目标智能体不存在 | 检查智能体标识名是否正?|
| `INVALID_PARAMETERS` | 参数格式错误 | 检查参数是否符合要?|
| `FILE_NOT_FOUND` | 文件不存?| 检查文件路径是否正?|
| `PERMISSION_DENIED` | 权限不足 | 检查文件读写权?|
| `EXECUTION_FAILED` | 执行过程失败 | 查看详细错误信息，重新执?|
| `TIMEOUT` | 执行超时 | 增加超时时间或优化处理逻辑 |

## 7. 调用示例

### 7.1 蓝图转技术规格书完整流程

**请求示例**?
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-04-02T01:30:12Z",
  "source_agent": "blueprint-architect",
  "target_agent": "spec-approver",
  "operation": "convert_blueprint_to_spec",
  "parameters": {
    "blueprint_path": "d:/ZephyrAlpha/docs/02_FACTOR_LIBRARY/FACTOR_BACKTEST_INTEGRATION_BLUEPRINT.md",
    "output_dir": "d:/ZephyrAlpha/docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS",
    "template_path": "d:/ZephyrAlpha/docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/TECHNICAL_SPECIFICATION_TEMPLATE.md",
    "generate_review_report": true
  },
  "context": {
    "project_root": "d:/ZephyrAlpha",
    "current_phase": "blueprint_to_spec",
    "priority": "high"
  }
}
```

**响应示例**?
```json
{
  "response_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-04-02T01:35:45Z",
  "status": "success",
  "execution_time": 333,
  "results": {
    "output_files": [
      {
        "path": "d:/ZephyrAlpha/docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/FACTOR_BACKTEST_INTEGRATION_SPEC_v1.0.md",
        "type": "technical_specification",
        "description": "因子库与回测集成技术规格书"
      },
      {
        "path": "d:/ZephyrAlpha/docs/05_IMPLEMENTATION/07_OPERATIONS/review_reports/FACTOR_BACKTEST_INTEGRATION_REVIEW_20260402.md",
        "type": "review_report",
        "description": "技术评审报?
      }
    ],
    "summary": {
      "score": 46.6,
      "level": "中等风险",
      "recommendation": "[WARNING] 综合评估中等，需要关注风险点和复杂度"
    }
  },
  "next_steps": [
    {
      "agent": "development-agent",
      "operation": "generate_implementation",
      "description": "根据技术规格书开始代码实?
    }
  ]
}
```

## 8. 实施要求

### 8.1 智能体实现要?
1. **输入解析**：每个智能体必须能够解析标准请求格式
2. **输出生成**：必须生成标准响应格?
3. **错误处理**：必须捕获异常并生成标准错误响应
4. **日志记录**：必须记录调用日志，包括请求、响应、执行时?

### 8.2 工具集成要求
1. **评估工具**：spec-approver必须集成三个评估工具（technical_feasibility_assessor.py, risk_analyzer.py, implementation_complexity_calculator.py?
2. **模板使用**：必须使用标准模板生成技术规格书和评审报?
3. **文件管理**：必须遵循系统的文件路径标准

### 8.3 质量保证
1. **协议版本管理**：协议版本必须明确标识，支持向后兼容
2. **测试验证**：必须定期进行协议兼容性测?
3. **文档更新**：协议变更必须及时更新本文档

## 9. 版本历史

| 版本 | 日期 | 说明 | �?|
|------|------|------|------|
| v1.0 | 2026-04-02 | 初始版本，定义基础调用协议 | 审批智能?(Spec-Approver) |

## 10. 附录

### 10.1 智能体标识名规范
- 必须使用小写字母、数字和连字?
- 格式：`[角色]-[功能]`，如 `blueprint-architect`, `spec-approver`
- 长度不超?0个字?

### 10.2 文件路径规范
- 必须使用绝对路径
- Windows系统使用正斜杠或反斜杠，建议统一使用正斜杠（`d:/ZephyrAlpha/docs/...`?
- 路径中不得包含中文字?

### 10.3 时间戳格?
- 必须使用ISO 8601格式：`YYYY-MM-DDTHH:MM:SSZ`
- 时区统一使用UTC（Z表示UTC时间?
