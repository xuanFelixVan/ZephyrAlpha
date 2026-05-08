---
module_id: KE-module_blu-2_17_________pre_post_onblocke-000
title: 2.17 权限钩子系统——Pre/Post/OnBlocked/OnKillSwitch 四类钩子（决策 D-018-15）
category: module_blueprint
---

# 2.17 权限钩子系统——Pre/Post/OnBlocked/OnKillSwitch 四类钩子（决策 D-018-15）

2.17 权限钩子系统——Pre/Post/OnBlocked/OnKillSwitch 四类钩子（决策 D-018-15）

> **决策 D-018-15**：引入四类权限钩子，为扩展性和自定义校验提供**不侵入核心代码**的注册入口。这是 Claude Code hooks 模式 + Terraform pre/post-conditions 的组合。
>
> **可信主体**：Claude Code hooks——`preToolUse` / `postToolUse` 钩子系统。Terraform preconditions/postconditions——在 plan/apply 前后执行自定义校验。Netflix ChAP——在混沌实验前后注入自定义监控脚本。

```python
