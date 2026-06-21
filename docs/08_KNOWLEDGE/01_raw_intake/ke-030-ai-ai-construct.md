---
module_id: KE-030------ai-------ai-construct-000
status: active
title: 6.4 最有利于 AI 施工的选择（AI-Construction-Friendliest Selection）
category: agent_instruction
---

# 6.4 最有利于 AI 施工的选择（AI-Construction-Friendliest Selection）

6.4 最有利于 AI 施工的选择（AI-Construction-Friendliest Selection）

当多个方案在专业性和成本上等价时，选择**对 AI 后续施工最友好的那个**。

- **判定维度**（按优先级排序）：
  1. **机器可读性**：结构化格式（YAML/JSON）优于自然语言 prose。AI 解析 YAML 零歧义，解析 prose 需要推理
  2. **声明式优于命令式**：声明"期望状态"（declarative）优于描述"执行步骤"（imperative）——AI 自治需要知道目标状态，不需要知道每一步怎么走
  3. **显式优于隐式**：显式注册（如受控词表中的枚举值）优于隐式约定（如"遵循惯例即可"）。约定会漂移，枚举不会
  4. **单一责任优于分散定义**：一个概念只在一个文件中定义（SSoT），其他文件仅引用。避免"A 文件说 X 是 A，B 文件说 X 是 B"
- **专业参考**：Kubernetes → Declarative Configuration（声明式配置优于命令式操作）/ Terraform → Provider Contract（每个模块暴露标准接口才能被外部驱动）/ AWS CloudFormation → Infrastructure as Code（基础设施代码化——声明目标状态，引擎计算路径）
