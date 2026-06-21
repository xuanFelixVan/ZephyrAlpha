---
module_id: KE-3340
title: 5.2 src/zephyr/ 双轨结构
category: documentation
---

# 5.2 src/zephyr/ 双轨结构

5.2 src/zephyr/ 双轨结构

| 轨道 | 规范定义 | 实际状态 | 合规性 |
|------|---------|---------|--------|
| C 轨（14 层 L00-L13） | directory-structure-standard §三 | 14 个目录全部存在 | ✅ 合规（Python snake_case） |
| B 轨（10+ 独立包） | directory-structure-standard §三 | 14 个目录存在 | ⚠️ 部分合规（代码存在但 YAML 未定义） |
