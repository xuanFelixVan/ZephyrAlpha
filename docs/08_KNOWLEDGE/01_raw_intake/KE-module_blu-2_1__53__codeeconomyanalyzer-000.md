---
module_id: KE-module_blu-2_1__53__codeeconomyanalyzer-000
title: 2.1 #53: CodeEconomyAnalyzer——过度抽象检测
category: module_blueprint
---

# 2.1 #53: CodeEconomyAnalyzer——过度抽象检测

2.1 #53: CodeEconomyAnalyzer——过度抽象检测

- 函数平均 < 5 行 + 函数数 > 3 → 过度拆分
- 类数 > 函数数 → Factory/Builder 反模式
- 模块名含 `factory`/`builder`/`strategy` + 1类 ≤ 2函数 → 过度设计
- 评分：100(PASS) / 75(WARN) / 40(HINT)
