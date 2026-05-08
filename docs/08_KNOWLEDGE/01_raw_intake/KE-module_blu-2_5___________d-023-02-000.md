---
module_id: KE-module_blu-2_5___________d-023-02-000
title: 2.5 自动对账策略（决策 D-023-02 / 增强）
category: module_blueprint
---

# 2.5 自动对账策略（决策 D-023-02 / 增强）

2.5 自动对账策略（决策 D-023-02 / 增强）

> **决策 D-023-02**（增强）：漂移检测后自动对账——可自动修复的漂移自动修，不可自动修复的生成修复建议。自动修复前拍 pre-fix 快照，修复失败触发 auto-rollback，**回滚后必须验证漂移是否真正消除**。

```yaml
reconciliation_strategy:
  pre_fix_snapshot:
    description: "自动修复前拍摄 pre-fix 快照——用于 rollback + diff trace"
    content: "受影响的文件 → temp backup + SHA256"
    retention: "修复验证通过后删除"

  auto_fixable:
    description: "可自动修复的漂移——脚本自动修复"
    examples:
      - "蓝图路径索引与磁盘不一致 → 自动更新路径索引"
      - "YAML 注册表缺少新模块 → 自动追加条目"
      - "blueprint-registry.yaml 统计数字不准 → 自动重新计算"
      - "requirements.txt 版本与 pip freeze 不一致 → 自动同步"
    action: "pre-fix 快照 → 自动修复 → 修复后验证 → 审计日志 → 通知 Owner"

  needs_suggestion:
    description: "不可自动修复的漂移——生成修复建议"
    examples:
      - "蓝图 §3 接口与代码实际接口不一致 → 生成结构化 diff"
      - "蓝图缺失章节 → 生成待补全模板"
      - "AI 幻觉引用不存在的模块 → 生成删除/替换建议"
      - "跨模块功能重复 → 生成合并建议 + 二选一推荐"
    action: "生成修复建议 → drift 状态 → NEEDS_SUGGESTION → 通知 Owner"

  auto_fix_failed:
    description: "自动修复失败 → 自动回滚 → 验证回滚结果"
    action:
      - "从 pre-fix 快照恢复文件"
      - "SHA256 校验恢复完整性"
      - "重新跑触发检测器 → 验证漂移是否回到修复前状态"
      - "若回滚验证失败（文件损坏/不一致）→ 升级为 P0 CRITICAL → 通知 Owner"
      - "审计日志记录全链路"
```
