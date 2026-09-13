---
ttl: permanent
doc_type: architecture_view
title: 前端技术手册·详情抽屉模板（DDT）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-09-08
topic: frontend_handbook_detail_drawer_template
scope: frontend
---

# 前端技术手册·详情抽屉模板（DDT）

> 全景图/树图类页面「点节点开右侧抽屉看详情」的统一设计模式。
> 实证来源 = 交易决策全景（tdm 页）抽屉 v2（b20260908-10，commit 062975c7）。
> 目标：其他全景图页（depgraph/frontend_map/battle_map 等）做节点详情抽屉时照此复用，不再各自发明。

---

## 一、适用场景

| 场景 | 用本模板 |
|---|---|
| 画布/树/图节点，点击看完整档案 | ✅ |
| 详情含混合内容：长文+键值+引用列表+关联节点 | ✅（本模板的核心价值=混合内容分区） |
| 纯表单/纯表格详情 | ❌ 用 w-data-table 等现成件 |
| 需要弹窗交互 | ❌ 项目禁弹窗，抽屉即弹窗替代 |

## 二、结构契约（分区顺序固定）

```
标题区（名称 + ID·元信息行 + 三态状态徽标 + 父节点行）
  → 问（决策问题，提亮一档）
  → 机制（长文，行高≥1.6）
  → 治理（键值网格，禁长句拼接）
  → 模块锚（chip / 空态说明）
  → 策略挂载（chip 流 / 空态说明）
  → 依据锚（八轴分组：轴名+计数一行，chip 流另起一行，禁顿号长串）
  → 上游 / 下游（节点导航行，点击跳选）
  → 设计备注（卡片化引用块，行高 1.65 保长文可读）
```

分区标题统一 `.sec`：蓝色小标题 + `::after` 右延发丝线（替代纯文字堆叠的分区感）。

## 三、视觉语义（禁发明新色）

| 元素 | 语义 | 色 |
|---|---|---|
| 状态徽标 📄paper | 实盘执行档 | 绿系 `#2e7d32` 边 / `#0e2612` 底 |
| 状态徽标 实锚 | 已接模块 | 蓝系 `#1e5a8f` 边 / `#0f2740` 底 |
| 状态徽标 🔴红节点 | 设计态未锚 | 橙虚线 `#8a4a12` 边 / `#2a1c0e` 底 |
| 分区标题 | — | 强调蓝 `#3d8bff` |
| 发丝线/边框 | — | `#263042`（sec 延线 `#1c2534`） |
| chip 编号 | 引用 ID | `#5b8fd6` |
| 空值/空态 | `—` 留位不塌行 | `#525d70` |

铁律：抽屉徽标三态色必须与画布节点卡片**同语义同色号**——用户在画布认的颜色，进抽屉不许变。

## 四、CSS 类清单（照搬即可）

| 类 | 用途 |
|---|---|
| `.dr-name` / `.dr-id` / `.dr-par` | 标题区：名称 16px 粗 / ID 元信息 11px 暗 / 父节点行 |
| `.dr-badges` + `.bdg` `.bdg-paper` `.bdg-prod` `.bdg-design` | 状态徽标行 |
| `.sec`（含 `.cnt` 计数） | 分区标题 + 右延发丝线 |
| `.txt` / `.txt.q` | 长文（行高 1.7）/ 问提亮 |
| `.kgrid` + `.k` `.v` `.v.na` | 治理键值网格（44px 标签列+值列，空值 `.na` 暗色 `—`） |
| `.chips` + `.chip`（`i`=编号 `b`=中文名） | 引用 chip 流，hover 亮边 + title 全称 |
| `.axis` + `.axis-h` | 依据锚轴分组头 |
| `.nl` + `.dot-prod/paper/design` `.nl-n` `.nl-t` `.nl-i` | 节点导航行（状态点+名称+边型 glyph+ID），`data-jump` 点击跳选 |
| `.cm` | 设计备注卡片块（左边条+暗底） |
| `.empty` | 空态说明 |

完整 CSS 锚点：`src/zephyr/frontend/dashboard/web/pages/tdm.html` style 块「右侧详情抽屉 v2」段（b20260908-10 起）。

## 五、JS 契约（drawer() 骨架，六个助手函数）

```javascript
function esc(s) { /* 真源文本进 innerHTML 必须转义——防 YAML 内容断标签/注入 */ }
function zh(id) { return RN[id] ? id + ' ' + RN[id] : id; }   /* 注册表中文名翻译，未命中回退编号原文 */
function chip(id) { /* <span class="chip" title="全称"><i>编号</i><b>中文名</b></span> */ }
function nlink(x, t) { /* 节点导航行：data-jump=id，点击 TDM.sel=id → render() → drawer() 跳选 */ }
function kv(k, v) { /* 治理网格一行：空值 <span class="v na">—</span> */ }
function sec(t) { /* 分区标题 */ }
```

行为细节（全是实证坑，别丢）：

1. **esc() 强制**——真源 YAML/DB 文本含 `<>&"'` 直接拼 innerHTML 必断。
2. **空值显式 `—` 留位**——治理四键全空的节点（样例 TDM-E-L1-S1）网格不许塌行。
3. **轮询重绘保持滚动位置**——`var scroll = box.scrollTop; …; box.scrollTop = scroll;`，否则 30s 轮询把用户阅读位置冲掉。
4. **导航行点击跳选闭环在 drawer() 内**——`box.querySelectorAll('[data-jump]')` 绑 click，不动画布交互函数。
5. **边型 glyph 固定**：sequence `→` / feed `⇢` / broadcast `⇉` / feedback `↩`。
6. **AXES 顺序硬编码**（factor/data/cost_model/risk_limit/threshold/event/algo）——呈现顺序稳定，不随对象键序飘。

完整 JS 锚点：`src/zephyr/frontend/dashboard/web/features/tdm.js` `drawer()`（v2，b20260908-10 起）。

## 六、移植检查单（新页做抽屉时逐条过）

- [ ] 抽屉宽度/开合逻辑不动宿主页面既有值（tdm=400px）
- [ ] 分区顺序按 §二，缺内容的分区给 `.empty` 空态而非删除分区（结构稳定=用户肌肉记忆）
- [ ] 三态色与画布卡片逐色号对齐
- [ ] 所有真源文本过 esc()
- [ ] 长文行高 ≥1.6（机制/备注）
- [ ] 引用列表一律 chip 流，禁顿号长串
- [ ] 治理类字段一律键值网格，禁 `激活=x ｜ 档位=y` 拼接
- [ ] 验收基准节点=边界最全的那个（空值/长文/多引用/多上下游），截图目检
- [ ] ZK_BUILD 末位 +1，页头品牌行见 `b<新版本>` 才算生效（FEH-PC-009 版本戳排查法）

## 七、关联

- FEH-PC-009 版本戳排查法（改了看不到先查 b 戳）
- FEH-PC-012 registerFeature 只登记不初始化（抽屉若拆为独立组件，样式注入必须文件顶层做）
- 拆件 SOP：`docs/01_policies_and_standards/sop/construction_sop/frontend_component_split_sop.md`（抽屉够「单一功能+独立样式+跨页复用」三条判据，新页应直接拆为 sq-<page>-drawer 组件而非内联）

---

## 修订记录

| 日期 | 版本 | 改动 | 为什么改 |
|---|---|---|---|
| 2026-09-08 | 1.0.0 | 建册，tdm 抽屉 v2 实证沉淀 | Owner 裁定模板化，供其他全景图页复用 |
