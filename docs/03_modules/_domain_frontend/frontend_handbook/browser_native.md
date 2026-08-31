---
ttl: permanent
doc_type: architecture_view
title: 前端技术手册·浏览器原生（NB）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-31
topic: frontend_handbook_browser_native
scope: frontend
---

# 前端技术手册·浏览器原生（NB）

> 本册收录浏览器原生行为（缓存/事件/DPR/canvas/控制台）的实证坑与正确做法。
> 条目四段式：触发词 → 想做什么 → 内置能否 → 坑 → 正确做法+代码锚点。编号永久稳定不回收。

---

### FEH-NB-001｜改了代码页面没变化（浏览器缓存）

- **触发词**：改了没生效 / 看不到更新 / 缓存 / 硬刷新 / 改了看不到
- **想做什么**：改完前端代码后刷新页面看到最新效果
- **内置能否**：❌ 浏览器缓存 CSS/JS 是默认行为，F5 普通刷新不够用
- **坑**：改了代码但浏览器用旧缓存，表现为"改了看不到"——本会话成本线/事件图标多次"改了没反应"事故的全部根因；AI 误判为代码没改对，反复返工
- **正确做法**：①根治=破缓存机制（见 FEH-LOAD-001，index.html/loader.js 用 Date.now() 版本参数）；②排查时先 Ctrl+F5 硬刷新排除缓存嫌疑，**再**怀疑代码
- **代码锚点**：破缓存 `src/zephyr/frontend/dashboard/web/core/loader.js#L8`
- **来源**：缓存事故族（Owner 实测"改了看不到"） · 2026-08-31

---

## 修订记录

| 日期 | 版本 | 改动 | 为什么改 |
|---|---|---|---|
| 2026-08-31 | 1.0.0 | 建册，首批 1 条（NB-001） | 四件套施工第 1 步；缓存事故族是前端返工最大根因之一 |
