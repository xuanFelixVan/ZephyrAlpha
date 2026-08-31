---
ttl: permanent
doc_type: architecture_view
title: 前端技术手册·KLineChart 图表库（KLC）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-31
topic: frontend_handbook_klinecharts
scope: frontend
---

# 前端技术手册·KLineChart 图表库（KLC）

> 本册收录 KLineChart v10.0.3（`src/zephyr/frontend/dashboard/web/klinecharts.min.js`）的实证坑与正确做法。
> 条目四段式：触发词 → 想做什么 → 内置能否 → 坑 → 正确做法+代码锚点。编号永久稳定不回收。
> 积累纪律：踩坑解决即入册（试了两次以上才解决的问题，解决当次 commit 必须带条目）。只增改不删，过时做法改原文+留痕。

---

### FEH-KLC-001｜价格横线类 overlay（priceLine 价签删不掉）

- **触发词**：成本线 / 价格线 / priceLine / overlay 横线 / 价签 / 水平线
- **想做什么**：画一条横跨主图的价格水平线，不要任何价签/文字
- **内置能否**：❌ 内置 priceLine 模板的蓝底价签删不掉（实证：3 小时试错后放弃——模板部件不可单独隐藏）
- **坑**：①内置模板部件不可单独隐藏；②points 传 timestamp 会锚定异常不渲染，**只传 `{value}`**
- **正确做法**：自注册纯横线模板 `plainLine`（无文字/价签部件），然后 `createOverlay({name:'plainLine', groupId:'cost', lock:true, points:[{value: 成本价}]})`
- **代码锚点**：模板注册 `src/zephyr/frontend/dashboard/web/core/app1.js#L5934`；成本线创建 `app1.js#L6229`（klpRenderCostLine）
- **来源**：commit 51915c64a8 · 2026-08-31

### FEH-KLC-002｜初始化与数据加载顺序契约

- **触发词**：init / setSymbol / setPeriod / setDataLoader / 数据加载 / 卡死 / 无限加载
- **想做什么**：初始化 K 线图并接入数据源
- **内置能否**：✅ 但必须按契约顺序
- **坑**：①顺序错会导致图表不渲染或数据异常；②forward/backward 回调若返回非空数组，库会**无限向前加载卡死**
- **正确做法**：严格 `init → setSymbol → setPeriod → setDataLoader`；数据契约：init 返回全量数据，forward/backward **必须返回空数组**
- **代码锚点**：初始化 `src/zephyr/frontend/dashboard/web/core/app1.js#L5948` 附近
- **来源**：KLineChart 集成交接文档 · 2026-08-31

### FEH-KLC-003｜overlay 取值必须在 K 线价格域内

- **触发词**：overlay 不显示 / 成本线不显示 / 值异常 / 价格域
- **想做什么**：让 overlay（如成本线）正常渲染
- **内置能否**：✅ 但有隐含约束
- **坑**：overlay 的值若超出当前 K 线可视价格域（如直接用了页面展示价/账户成本价而非近期价格域内的值），线会不渲染或飞到图外
- **正确做法**：overlay 取值用 K 线价格域内的值（用近期均价换算/夹取），不能用页面展示价直接喂
- **代码锚点**：成本线取值逻辑 `src/zephyr/frontend/dashboard/web/core/app1.js#L6229`（klpRenderCostLine）
- **来源**：筹码峰平均成本线不显示事故（参数错误导致） · 2026-08-31

### FEH-KLC-004｜事件行（klp-evtrow）与时间轴分离

- **触发词**：事件图标 / 新闻标记 / 时间轴 / klp-evtrow / 事件行收展
- **想做什么**：在 K 线图下方显示事件图标行（新闻/公告），可收展
- **内置能否**：❌ 库内置 xAxis 不支持图标行——已 `show:false` 隐藏内置时间轴，页面底部自定义 `klp-timeline` 为唯一时间轴
- **坑**：事件图标塞时间轴轨道里会挤占刻度空间；收展若影响时间轴会导致 K 线区抖动
- **正确做法**：事件行=独立模块 `klp-evtrow`（高 24px 紧贴时间轴，间距 3px），⚑ 开关控制整行收展（收掉高度归零、K 线变大），时间轴常显不受影响；图标=白色线条新闻 SVG+灰色小数字（11px）
- **代码锚点**：DOM `src/zephyr/frontend/dashboard/web/pages/stockq.html#L49`；渲染 `app1.js#L6326`（klpTimelineRender）；开关逻辑 `app1.js#L6147`（klpRefreshMarks）
- **来源**：commit 1f368b2db1（事件行独立布局）+ 51915c64a8（收展） · 2026-08-31

---

## 修订记录

| 日期 | 版本 | 改动 | 为什么改 |
|---|---|---|---|
| 2026-08-31 | 1.0.0 | 建册，首批 4 条（KLC-001~004） | 四件套施工第 1 步；收录 KLineChart 集成期实证坑 |
