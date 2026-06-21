---
module_id: KE-850
status: active
title: 3. 检查结果记录
category: governance
---

# 3. 检查结果记录

3. 检查结果记录

每次会话开始时，在 Session Log 中记录门禁检查结果：

```yaml
gate_check:
  A1: pass  # 上下文加载
  A2: pass
  A3: pass
  B1: pass  # 规则确认
  B2: pass
  B3: pass
  B4: pass
  C1: pass  # 安全检查
  C2: pass
  C3: pass
  D1: pass  # 环境确认
  D2: pass
```

任何一项为 `fail` 时，必须先修复再开始操作。
