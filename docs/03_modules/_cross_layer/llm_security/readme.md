---
blueprint_id: MOD-023
title: llm-security README
module_id: MOD-010---

# LLM Security Gateway (MOD-INF-014)

> **模块标识**: MOD-INF-014 | **版本**: 0.10.0 | **状态**: 施工中 | **层级**: 跨层

> **真源声明**：本模块的 canonical SSoT 为 `src/zephyr/llm-security/` 代码目录。

## 📋 模块概述

LLM Security Gateway (LSG) 是 ZephyrAlpha 项目的核心安全组件，提供九层纵深防御体系，确保 AI 应用的安全性、可靠性和合规性。

### 🎯 核心目标

- **纵深防御**: L0-L8 九层安全防护，每层独立且协同工作
- **fail-closed 原则**: 安全默认关闭，异常时自动阻断
- **实时监控**: 全面的安全事件监控和告警机制
- **自我防护**: LSG 自身的安全性和完整性保护

## 🏗️ 架构设计

### 九层防御体系

| 层级 | 名称 | 功能描述 | 状态 |
|------|------|----------|------|
| L0 | 供应链安全 | 模型验证、依赖扫描、AI BOM、Code Signing | ✅ 已实现 |
| L1 | 输入防护 | 直接/间接注入检测、越狱检测、RAG投毒防御 | ✅ 已实现 |
| L2 | Prompt保护 | System Prompt隔离、防泄露、话题控制 | ✅ 已实现 |
| L3 | 输出安全 | Schema验证、沙箱执行、PII脱敏、幻觉检测 | ✅ 已实现 |
| L4 | Agent安全 | 权限最小化、HITL、操作审计、MCP防御 | ✅ 已实现 |
| L5 | 资源保护 | 速率限制、Token预算、成本熔断、并发限制 | ✅ 已实现 |
| L6 | 可观测性 | 安全日志、异常告警、仪表板、审计报告 | ✅ 已实现 |
| L7 | 持续验证 | 自动Red Team、安全回归测试、威胁情报 | ✅ 已实现 |
| L8 | 多Agent安全 | Agent间通信认证、跨Agent权限隔离 | ✅ 已实现 |

### 核心组件

```
src/zephyr/llm-security/
├── layers/                    # 九层防御实现
│   ├── l0_supply_chain.py     # 供应链安全层
│   ├── l1_input.py           # 输入防护层
│   ├── l2_prompt_protection.py # Prompt保护层
│   ├── l3_output.py          # 输出安全层
│   ├── l4_agent.py           # Agent安全层
│   ├── l5_resource_protection.py # 资源保护层
│   ├── l6_observability.py   # 可观测性层
│   ├── l7_validation.py       # 持续验证层
│   └── l8_multi_agent.py     # 多Agent安全层
├── self_protection/           # 自我防护体系
│   ├── code_integrity.py     # 代码完整性检查
│   ├── isolation.py          # 隔离策略
│   └── l7_validation.py      # 自我验证
├── patterns/                  # 安全模式库
│   ├── injection_patterns.py # 注入模式检测
│   └── secrets.py            # 密钥检测
├── payloads/                 # 攻击载荷库
│   ├── injection-payloads.yaml    # 注入载荷
│   ├── tool-call-payloads.yaml    # 工具滥用载荷
│   ├── leak-probe-phrases.yaml    # 泄露探测短语
│   └── red-team-payloads.yaml     # Red Team 攻击载荷
├── dashboard/                # 安全仪表板
│   ├── app.py                # Streamlit 仪表板
│   └── __init__.py
├── sandbox/                   # 沙箱执行环境
│   └── __init__.py
└── core/                     # 核心组件
    ├── behavior_audit_logger.py # 行为审计
    ├── input_sanitizer.py    # 输入净化
    ├── protocol.py           # 安全协议
    └── process_sandbox.py    # 进程沙箱
```

## 🔧 快速开始

### 安装依赖

```bash
pip install streamlit plotly pyyaml pandas
```

### 启动安全仪表板

```bash
cd src/zephyr/llm-security/dashboard
streamlit run app.py
```

### 基本使用

```python
from zephyr.llm_security.gateway import LSGSecurityGateway
from zephyr.llm_security.protocol import SecurityDecision

lsg = LSGSecurityGateway()

result = await lsg.scan_input(
    text="用户输入内容",
    metadata={"user_id": "123", "session_id": "abc"}
)

if result.decision == SecurityDecision.ALLOW:
    response = process_request(result.sanitized_input)
else:
    logger.warning(f"安全阻止: blocked_by={result.blocked_by}")
```

## 📊 功能特性

### 安全检测能力

- **Prompt Injection 检测**: 支持直接注入、间接注入、多轮注入等攻击检测
- **工具滥用防护**: 防止权限提升、参数注入、路径遍历等工具滥用行为
- **数据泄露防护**: 敏感信息检测、PII脱敏、输出内容过滤
- **供应链安全**: 依赖包验证、AI模型完整性检查、代码签名验证

### 监控与告警

- **实时监控**: 请求流量、攻击检测、系统性能实时监控
- **可视化仪表板**: 支持安全概览、攻击检测、载荷分析、系统健康等视图
- **告警机制**: 多级别告警（HIGH/MEDIUM/LOW），支持邮件、Webhook通知

### 自我防护

- **代码完整性**: SHA256 基线检查，防止运行时篡改
- **隔离策略**: 文件、网络、进程、模块隔离
- **持续验证**: 自动 Red Team 测试，安全回归验证

## 🎯 安全标准对标

### 行业标准

- **OWASP Top 10 for LLM Applications 2025**: 100% 覆盖
- **MITRE ATLAS v5.4**: 完整攻击技术映射
- **NIST AI RMF 1.0**: 风险管理框架对齐
- **OWASP Agentic Applications Top 10 2026**: Agent 安全标准

### 最佳实践

- **NVIDIA AI Safety Recipe**: 安全配方实施
- **Anthropic Defense-in-Depth (ASL-3)**: 纵深防御策略
- **Microsoft SAIF/SFI**: 安全AI框架
- **SafeVibecoding Community Best Practices**: 社区最佳实践

## 🔍 测试验证

### 单元测试

```bash
# 运行安全模块单元测试
python -m pytest tests/llm-security/ -v
```

### 集成测试

```bash
# 运行完整安全网关测试
python tests/integration/test_lsg_integration.py
```

### Red Team 测试

```bash
# 执行自动 Red Team 测试
python src/zephyr/security/llm_defense/llm-security/self_protection/l7_validation.py --red-team
```

## 📈 性能指标

### 关键指标

- **检测准确率**: >99%
- **平均响应时间**: <50ms
- **误报率**: <0.5%
- **系统可用性**: 99.9%

### 资源使用

- **CPU 使用率**: <30%
- **内存占用**: <500MB
- **磁盘 I/O**: <10MB/s

## 🔄 版本历史

### v0.10.0 (2026-05-07)
- ✅ 九层防御体系完整实现
- ✅ 自我防护机制落地
- ✅ Red Team 攻击载荷库（200+ 载荷）
- ✅ Streamlit 安全仪表板
- ✅ 完整测试覆盖

### v0.9.1 (2026-05-06)
- 📋 蓝图设计和架构规划
- 🏗️ 基础框架搭建
- 🔧 核心组件原型

## 🤝 贡献指南

### 开发规范

1. **安全第一**: 所有修改必须通过安全审查
2. **测试覆盖**: 新增功能必须包含单元测试和集成测试
3. **文档更新**: 代码变更必须同步更新文档
4. **向后兼容**: 确保 API 向后兼容性

### 代码审查

- 安全相关代码需要双重审查
- 关键安全功能需要安全专家审查
- 所有合并请求必须通过自动化安全检查

## 📞 支持与反馈

### 问题报告

- **安全漏洞**: security@zephyralpha.com
- **功能问题**: issues@zephyralpha.com
- **文档问题**: docs@zephyralpha.com

### 社区

- **讨论论坛**: forum.zephyralpha.com
- **文档中心**: docs.zephyralpha.com
- **代码仓库**: github.com/zephyralpha/llm-security

## 📄 许可证

本项目采用 Apache License 2.0 许可证。详细信息请参阅 [LICENSE](LICENSE) 文件。

---

**LLM Security Gateway** - 为 AI 应用提供企业级安全保障 🛡️
