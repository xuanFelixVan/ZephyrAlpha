---
module_id: KE-378
status: active
title: 原则 4：Contribute Back When Patched / 修改必反哺
category: documentation
ttl: permanent
---

# 原则 4：Contribute Back When Patched / 修改必反哺

原则 4：Contribute Back When Patched / 修改必反哺

> 对开源项目的 patch/fork 必须有明确记录；可贡献的改进优先提交 PR 而不是私有 fork。

**执行标准**：
- 每次对 OSS 库做 monkey-patch / fork 时 → 写入 `adr/` 记录原因 + 评估是否可提 PR
- 私有 fork 的生命周期 ≤ 3 个月——超过 3 个月未合并回上游 → 触发评估：是否应替换该 OSS 库
- 长期维护的私有 fork → 必须在 `technology_landscape.yaml` 中标注 `quadrant: hold`（警戒指標）

---
