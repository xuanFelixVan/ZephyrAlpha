---
ttl: permanent
doc_type: architecture_view
title: 前端技术手册·加载与依赖（LOAD）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-31
topic: frontend_handbook_loading_vendor
scope: frontend
---

# 前端技术手册·加载与依赖（LOAD）

> 本册收录加载链路（loader/破缓存/vendor 库管理）的实证坑与正确做法。
> 条目四段式：触发词 → 想做什么 → 内置能否 → 坑 → 正确做法+代码锚点。编号永久稳定不回收。

---

### FEH-LOAD-001｜破缓存根治方案（Date.now() 版本参数）

- **触发词**：破缓存 / 版本参数 / cache busting / loader / Date.now
- **想做什么**：每次刷新页面都加载最新 CSS/JS，根治"改了看不到"
- **内置能否**：❌ 浏览器无内置机制，必须自己动手
- **坑**：只在 index.html 加版本参数不够——loader.js 动态加载的 JS/CSS 也要加；**此机制勿移除**（移除=缓存事故族复发）
- **正确做法**：index.html 和 loader.js 全部用 `Date.now()` 版本参数加载 CSS/JS（`src + '?v=' + Date.now()`）；每次刷新即最新
- **代码锚点**：`src/zephyr/frontend/dashboard/web/core/loader.js#L8`；入口 `src/zephyr/frontend/dashboard/web/index.html`
- **来源**：commit 51915c64a8（破缓存根治） · 2026-08-31

### FEH-LOAD-002｜同一文件禁止多个 Edit 并行

- **触发词**：Edit 覆盖 / 改动丢失 / 并行编辑 / 串行
- **想做什么**：对同一个前端文件（如 app1.js，6000+ 行）做多处修改
- **内置能否**：❌ 工具层面无防护
- **坑**：多个 Edit 并行调用同一文件会互相覆盖丢失改动——表现为"改了 A 处 B 处回退"，排查极难
- **正确做法**：同一文件的多处修改**必须串行**（一次一个 Edit，等返回再下一个）；或大改动直接整文件 Write 重写
- **代码锚点**：——（流程纪律，无代码锚点）
- **来源**：KLineChart 集成期实证 · 2026-08-31

---

## 修订记录

| 日期 | 版本 | 改动 | 为什么改 |
|---|---|---|---|
| 2026-08-31 | 1.0.0 | 建册，首批 2 条（LOAD-001~002） | 四件套施工第 1 步；破缓存是实证事故根治方案，串行编辑是实证返工根因 |
