---
module_id: KE-1722---------------------------003
status: active
title: 2.16 孤儿资源检测——磁盘有、注册表无、代码不引用（决策 D-023-25）
category: module_blueprint
ttl: permanent
---

# 2.16 孤儿资源检测——磁盘有、注册表无、代码不引用（决策 D-023-25）

2.16 孤儿资源检测——磁盘有、注册表无、代码不引用（决策 D-023-25）

> **决策 D-023-25**：文件中三种情况：(a) 注册表有、磁盘有 → 正常；(b) 注册表有、磁盘无 → 漂移（已检测）；(c) 磁盘有、注册表无、代码不引用 → **孤儿资源**——无人知晓但占用磁盘空间。定期扫描并生成清理建议。
>
> **决策依据**：AI 施工会产生大量临时文件、中间产物、重命名残留。孤儿文件积累会污染目录结构 + 增加扫描时间 + 增大基线快照体积。

```yaml
orphan_detection:
  scope: "docs/03_modules/ + scripts/governance/ + src/zephyr/（排除 .git/ + data/ + __pycache__/ + *.pyc）"

  classification:
    true_orphan:
      description: "文件不在任何 YAML 注册表中、不被任何 import 引用、不在 .gitignore 豁免列表中"
      action: "生成清理建议——> 7 天未修改 → 建议删除"

    undocumented_asset:
      description: "文件被代码 import 引用但不在此模块的 YAML 注册表中"
      action: "标记为 UNDOCUMENTED——生成 YAML 注册补全建议"

    stale_artifact:
      description: "文件最后修改日期 > 90 天且不在注册表中"
      action: "标记为 STALE——建议归档或删除"

  safeguards:
    - "清理建议永远只是建议——不自动删除任何文件"
    - "Owner 必须显式确认后才能删除"
    - "删除前自动备份到 data/orphan_archive/<timestamp>/"
```
