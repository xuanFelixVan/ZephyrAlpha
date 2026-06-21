---
module_id: KE-742
status: active
title: 15. AI 可消费性声明
category: governance
---

# 15. AI 可消费性声明

15. AI 可消费性声明

> 对标 Anthropic CLAUDE.md——直接向 AI 说明如何解析和执行本文档。

**AI 可直接执行的规则**：
- IFC-001（§5）→ 7 个必填字段，机械化检查
- IFC-002（§5）→ contract_id 命名模板 `{provider_id}.{consumer_id}.{interface_name}`，可正则校验
- IFC-003（§7）→ 语义化版本号判定（MAJOR=破坏性、MINOR=新增兼容、PATCH=修复），确定性规则
- IFC-004（§10）→ 契约注册表为结构化 YAML，脚本同步
- IFC-006（§12）→ 一致性验证命令 `validate_module_schema.py --check-contracts`

**需人类判断的规则**：
- IFC-005 契约生命周期 → 状态转换需人类审批（draft→frozen→deprecated →archived）
- §8 破坏性变更流程 6 步 → 步骤 2（受影响方通知）和 6（清理决策）需人类判断
- §13 模块间交互规则 → 运行时行为判断依赖上下文

**最小必读路径**（全新 AI session）：
1. §1 目的与范围 → 知道管辖范围
2. §2 SSoT 声明 → 知道本文档权威边界
3. §3 受控枚举 → 知道契约状态的 3 个合法值
4. §5 接口定义要求 → 知道 IFC-001/002 必填字段
5. §6 禁止行为 → 知道不可触碰的红线及替代方案
6. §10 契约注册表 → 知道注册表结构和生消流程
7. §12 契约一致性验证 → 知道 IFC-006 验证命令

**Token 预算**：本文档约 2000 字（含 frontmatter），单次读取 ≤ 3000 tokens。
