---
blueprint_id: MOD-INF-019
---

# LSG Security Specialist — LLM Security Gateway (MOD-INF-014)

## 模块概览

LLM Security Gateway (LSG) 是 ZephyrAlpha 的九层纵深防御系统，覆盖 LLM 交互全生命周期的安全防护。

## 统一入口

```python
from zephyr.llm_security.gateway import LSGSecurityGateway, ScanMode

gw = LSGSecurityGateway()

# 输入扫描（L0→L1→L2→L5）
result = await gw.scan_input("user prompt", source="direct_input")
if result.decision == SecurityDecision.DENY:
    # 拒绝该请求

# 输出扫描（L3→L6）
result = await gw.scan_output("model output", source="model_output")

# Agent 动作扫描（L4→L5→L8）
result = await gw.scan_agent_action("action text", tool_name="write_file")

# 全链路扫描（L0→L1→...→L8）
result = await gw.full_scan("text")
```

## 九层防御架构

| 层 | 名称 | 核心能力 | 源文件 |
|----|------|---------|--------|
| L0 | 供应链安全 | 模型验证/依赖扫描/MCP验证/Slopsquatting检测 | `layers/l0_supply_chain.py` |
| L1 | 输入防护 | 直接注入+间接注入+越狱+ToolResultTransform+编码逃逸 | `layers/l1_input.py` |
| L2 | Prompt保护 | 防泄露/话题边界控制/四段式模板 | `layers/l2_prompt_protection.py` |
| L2a | 进程沙箱 | 独立进程隔离执行 | `layers/l2a_process_sandbox.py` |
| L3 | 输出安全 | Schema验证/PII脱敏/幻觉检测/代码信任边界 | `layers/l3_output.py` |
| L4 | Agent安全 | 权限最小化/HITL/金融合规/长时域/冒充防御 | `layers/l4_agent.py` |
| L5 | 资源保护 | Token预算/速率限制/成本熔断/模型提取防御 | `layers/l5_resource_protection.py` |
| L6 | 可观测性 | 安全日志/异常告警/Promptware Kill Chain/侧信道 | `layers/l6_observability.py` |
| L7 | 持续验证 | 代码完整性/DeepSeek风险/供应商隔离/安全回归 | `self_protection/l7_validation.py` |
| L8 | 多Agent安全 | 信任评分/身份验证/跨Agent权限/通信隔离 | `layers/l8_multi_agent.py` |

## 关键原则

- **fail-closed**: LSG 不可用 → 拒绝所有流量（L6/L7 除外为 fail-open）
- **不确定性阈值**: score < 0.5 → 视为不确定 → 默认 DENY
- **链式短路**: 任一层 DENY → 后续层不再执行

## Pipeline 集成

PipelineOrchestrator 已集成 LSG：
- `_lsg_sanitize_input()`: 输入扫描（L0→L1→L2→L5）
- `_lsg_sanitize_output()`: 输出扫描（L3→L6）

## 模式库

- `patterns/injection_patterns.py`: 5类直接注入 + 5类间接注入 + 5类越狱 + 6类编码逃逸
- `patterns/secrets.py`: 28种密钥/PII/凭证扫描模式

## 测试

```bash
python -m pytest tests/llm_security/ -q --tb=line  # 180 个测试
```

## 对标标准

OWASP Top 10 for LLM 2025 · MITRE ATLAS v5.1 · NIST AI RMF 1.0 · NVIDIA AI Safety Recipe · Anthropic ASL-3
