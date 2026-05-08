---
module_id: KE-session_lo-strategybase___strategyregist-000
title: 类名安全提取（处理 "StrategyBase + StrategyRegistry"）
category: session_log
---

# 类名安全提取（处理 "StrategyBase + StrategyRegistry"）

类名安全提取（处理 "StrategyBase + StrategyRegistry"）
import re
raw_name = contract_name.split(" / ")[0].strip()
match = re.match(r"[A-Za-z_][A-Za-z0-9_]*", raw_name)
class_name = match.group(0) if match else "UnknownContract"
```
