---
module_id: KE-module_blu-3_13_grandfather______________-001
title: 3.13 Grandfather 三定律——引擎安装前的古老纠缠（v0.7.0 终极审视 #2）
category: module_blueprint
---

# 3.13 Grandfather 三定律——引擎安装前的古老纠缠（v0.7.0 终极审视 #2）

3.13 Grandfather 三定律——引擎安装前的古老纠缠（v0.7.0 终极审视 #2）

**发现**：蓝图假设去重引擎安装于项目初期。但外部审计师会问：**引擎安装时项目已有大量"古老"的重复代码——它们可能已经被测试了 6 个月，多个模块深度依赖，提取 = 灾难**。

**Grandfather 三定律**（超过 30 天的重复代码适用）：

| 定律 | 内容 | 实现 |
|:---:|------|------|
| **第一定律：永不自动修复** | 任何在 `function_cache.json` 中首次记录时间 ≥ 30 天前（即引擎安装前就存在的重复），默认 `auto_fix = false`——**只能 manually reviewed** | `grandfather_check()`——检测 `first_detected_at` 字段 → 距今 > 30 天 → 自动标记 `grandfather: true` + `auto_fix: false` |
| **第二定律：化石记录** | ≥ 60 天的古老重复进入"化石记录"——保留在报告中但降级为 informational（exit code 0），不再作为 WARN/ERROR。它们被认定为"architecture-as-is"——不是债务而是地质层 | `fossilize()`——距今 > 60 天 → 报告中 `severity: informational` → 不参与 Health Score 减值 → 保留 `function_cache.json` 中的 `grandfather_record` 用于历史追溯 |
| **第三定律：考古豁免** | 移除一个 Grandpa 重复前必须先通过"考古测试"：①该重复首次出现的 commit 能找到（git log -S）②该重复的所有 caller 有独立测试覆盖 ③该重复的修复有 rollback plan（一个 `git revert` 命令）。三点全部满足 → Owner 可手动 `--override-grandfather DUP-xxx` | `archaeology_check()` → 生成考古报告 → 不满足则拒绝提取 |

```yaml
