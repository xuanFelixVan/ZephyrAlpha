---
module_id: KE-2956----healt-000
status: active
title: thematic_summary.yaml —— health-monitor.py + prioritizer.py 联合产出
category: module_blueprint
ttl: permanent
---

# thematic_summary.yaml —— health-monitor.py + prioritizer.py 联合产出

thematic_summary.yaml —— health-monitor.py + prioritizer.py 联合产出
thematic_summary:
  total_duplicate_groups: 47
  themes: 3
  themes_explain_pct: 68                    # 3 个主题解释了68%的重复

  themes:
    - theme: "时间/日期工具类"
      explanation: "7个文件各自实现时间戳/格式化/ISO字符串转换"
      duplicate_groups: 12
      affected_files: 18
      root_cause: "AI session 间无共享时间工具记忆"
      one_fix_solves_groups: 10             # 提取一个 shared time_utils 可消除 10 组
      # 重复了 10 个组的根本原因被提炼出来了

    - theme: "import 块重复"
      explanation: "23个文件开头有几乎相同的 import datetime/json/os/pathlib/logging 组合"
      duplicate_groups: 9
      affected_files: 23
      root_cause: "没有 shared import 预置模板"
      one_fix_solves_groups: 9              # 一个公共导入块解决所有

    - theme: "错误处理模板"
      explanation: "11 个模块各有自己的 try/log/raise 包装模式——结构相同但异常类型不同"
      duplicate_groups: 11
      affected_files: 11
      root_cause: "无统一错误处理装饰器/上下文管理器"
      one_fix_solves_groups: 8              # 共享错误装饰器可解决大部分
```

**主题摘要的使用方式**：
- Wave 1 的 Health Score 旁增加一行：`themes: "时间工具 (12组) + import块 (9组) + 错误处理 (11组)"`
- Owner 只需看这一行，不需要看 47 组
