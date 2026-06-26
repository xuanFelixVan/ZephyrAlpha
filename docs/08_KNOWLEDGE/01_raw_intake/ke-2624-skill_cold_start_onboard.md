---
module_id: KE-2529---onboard-001
status: active
title: 9.9 Skill Cold Start & Onboarding
category: module_blueprint
ttl: permanent
---

# 9.9 Skill Cold Start & Onboarding

9.9 Skill Cold Start & Onboarding

```yaml
skill_cold_start:
  description: "新 AI session 第一次遇到 ZephyrAlpha 时的加速路径"

  onboarding_skill:
    skill_id: "SKILL-DOM-onboarding"
    purpose: "当 AGENTS.md 检测到是首次 session → 优先加载此 Skill → 快速了解 ZephyrAlpha 的架构 + 如何触发其他 Skills"
    content:
      - "30 秒速览：项目是什么 + 核心约束"
      - "关键路径索引：去哪看代码、蓝图、日志"
      - "Skill 系统简介：什么是 Domain/Role Skill？怎么触发？"
      - "Build/Test/Lint 三命令速查"
    auto_load: "session 的前 3 次交互中自动加载 → 第 4 次起不再加载（标记 session 为 warmed）"

  session_warm_up:
    description: "非首次 session 的快速重连"
    previous_session_load: "AGENTS.md 自动加载上次 session 的 Session Resume → 了解进度 + last_loaded_skill"
    skip_onboarding: "session 标记为 warmed → 直接跳到触发表匹配 → 加载对应 Skill"
```
