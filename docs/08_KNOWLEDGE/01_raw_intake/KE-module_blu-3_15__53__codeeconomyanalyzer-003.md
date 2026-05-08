---
module_id: KE-module_blu-3_15__53__codeeconomyanalyzer-003
title: 3.15 #53: CodeEconomyAnalyzer
category: module_blueprint
---

# 3.15 #53: CodeEconomyAnalyzer

3.15 #53: CodeEconomyAnalyzer

文件：`D:\ZephyrAlpha\src\zephyr\shared\code_economy_analyzer.py`

- 检测规则：
  - 函数平均<5行+函数数>3→过度拆分
  - 类数>函数数→Factory/Builder反模式
  - 模块名含factory/builder/strategy等+1类≤2函数→过度设计
- 评分：100(PASS) / 75(WARN) / 40(HINT)
