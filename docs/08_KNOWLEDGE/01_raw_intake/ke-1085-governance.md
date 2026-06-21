---
module_id: KE-1000------------7--5-000
status: active
title: 7.1 功能域重叠判定流程（§7 #5 执行细则）
category: governance
---

# 7.1 功能域重叠判定流程（§7 #5 执行细则）

7.1 功能域重叠判定流程（§7 #5 执行细则）

> 本流程是 §7 #5 否决条件的操作化执行指南。

**四步判定**：

```
Step 1：关键词交集扫描
  └── 新模块 summary + title 中的核心名词 vs 所有现有模块 summary + title
  └── 判定：交集 ≥ 60% → 🔴 标记"高风险重叠"，跳 Step 4
         交集 30%~60% → 🟡 标记"疑似重叠"，跳 Step 2
         交集 < 30% → ✅ 跳过 #5，进入后续筛选

Step 2：responsibility_domain 精确匹配
  └── 新模块声明的 responsibility_domain 是否已被任何现有模块的 responsibility_domain 完全覆盖？
  └── 是 → 🔴 否决——创建新蓝图
         否 → 🟡 跳 Step 3

Step 3：covers[] 子域交叉
  └── 新模块的 covers[] 是否与任何现有模块的 covers[] 存在交集？
  └── 是 → 🔴 否决——子域被覆盖 → 应升级原蓝图（version bump + changelog）
         否 → ✅ 通过 #5

Step 4：输出否决建议
  └── 不创建新模块。建议路径（优先级递减）：
      ① 升级已有蓝图 {module_id}：version bump + changelog 记录新增节
      ② 若新责任无法归入任何已有蓝图 → 提交 Owner 裁定
      ③ 禁止：创建平行蓝图覆盖已有子域
```

**自动化潜力**：Step 1（关键词扫描）可脚本化；Step 2-3（responsibility_domain + covers[]）需该字段落地后自动化。当前阶段：AI 手动执行四步判定，每次创建新模块时记录判定过程于 Session Log。
