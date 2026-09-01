---
ttl: task_bound
---

> **文档性质**：stockq 页组件拆分清单（Owner 审前稿）。审完定稿后：组件按清单拆分 → manifest 登记 → 数据逐项接通。
> **原则**：组件=数据+行为（进 features/）；纯展示=无数据无行为（进 widgets/）；数据服务=API 调用层（进 services/）。

# 个股行情页（stockq）组件拆分清单 v0.1

## 一、页面骨架（pages/stockq.html）——不拆，留 pages/

| # | 区域 | 说明 | 归属 |
|---|---|---|---|
| 1 | 左栏抽屉 | 自选列表+搜索+持仓（可隐藏） | pages/stockq.html |
| 2 | 中栏 K 线区 | K 线主图+副图指标+时间轴+事件行 | pages/stockq.html |
| 3 | 筹码峰模块 | K 线与右栏之间的独立模块 | pages/stockq.html |
| 4 | 右栏资料面板 | 公司信息+五档挂单+关键数据（可隐藏） | pages/stockq.html |

> 页面骨架只负责布局和模块占位，**逻辑全部下沉到 features/ 和 widgets/**。

---

## 二、功能模块（features/stockq/）——有数据有行为，拆件判据满足任一即拆

| # | 组件名 | 文件 | 当前状态 | 拆件判据命中 | 数据源 | update_frequency | 验收单 |
|---|---|---|---|---|---|---|---|
| 1 | **kline-data** | `features/stockq/kline-data.js` | 部分真源（K 线已接 CH，指标/标注内建） | ①反复改 ②有独立数据源 ⑤独立数据 | CH.c1_market.kline_* | 随周期 | ACC-F-STOCKQ-KLINE-DATA ✅ |
| 2 | **chip-peak** | `features/stockq/chip-peak.js` | 演示（前端模拟计算） | ①反复改（筹码峰是核心卖点）⑤独立数据 | CH.c1_market.chip_distribution（待建/核实） | 日级 | ACC-F-STOCKQ-CHIP-PEAK |
| 3 | **cost-line** | `features/stockq/cost-line.js` | 已拆 ✅ | ①反复改七返工 | 依赖 chip-peak.avgCost | 随 chip-peak | ACC-F-STOCKQ-COSTLINE ✅ |
| 4 | **event-row** | `features/stockq/event-row.js` | 演示（假事件） | ①反复改 ③独立样式 ⑤独立数据 | CH.c1_market.calendar_event + 财报/解禁表（待核实） | 日级 | ACC-F-STOCKQ-EVENT-ROW |
| 5 | **draw-tools** | `features/stockq/draw-tools.js` | 纯前端（KLineChart overlay） | ①反复改（画线工具常调）④跨页可复用 | none（纯前端逻辑） | 不适用 | ACC-F-STOCKQ-DRAW-TOOLS |
| 6 | **quote-panel** | `features/stockq/quote-panel.js` | 演示（STOCKQ_D 假数据） | ⑤独立数据 | CH.c1_market.daily_valuation + stock_basic | 日级 | ACC-F-STOCKQ-QUOTE-PANEL |
| 7 | **order-book** | `features/stockq/order-book.js` | 演示（五档挂单假数据） | ⑤独立数据（L2 实时） | QMT 实时 / CH.l2_tick（待核实） | 实时 | ACC-F-STOCKQ-ORDER-BOOK |
| 8 | **fav-list** | `features/stockq/fav-list.js` | 半真（localStorage 存，价格假） | ①反复改 | localStorage + 实时行情推送 | 实时 | ACC-F-STOCKQ-FAV-LIST |

### manifest 表头字段（每个模块统一 13 字段）

```yaml
id: stockq-<name>              # kebab-case，与文件名一致
name: 中文名                    # 模块样板/全景图显示用
file: features/stockq/<name>.js # 单文件全包
page: stockq                    # 所属页面
depends: [klinecharts, ...]     # 显式依赖声明
toggle: "开关名（如有）"         # 工具栏开关文字/图标
styles: self-injected            # 样式自注入（模块内建 style 标签）
acceptance: ACC-F-STOCKQ-XXX    # 挂验收单
handbook: [FEH-xxx]             # 挂手册条目
data_source: "CH.c1_market.xxx / QMT / none"  # 真源表/接口/无
update_frequency: "实时/秒级/分钟级/日级/不适用"
user_action: "用户能干什么（点击/悬停/拖拽/右键）"
fallback_behavior: "后端挂了显示什么（占位符/隐藏/红色提示）"
screenshot_ref: "tests/frontend/baselines/xxx.png"  # 基准截图
```

---

## 三、纯 UI 展示件（widgets/）——无数据无业务行为，仅渲染

| # | 组件名 | 文件 | 说明 |
|---|---|---|---|
| 1 | **price-tag** | `widgets/price-tag.js` | 价格标签（红涨绿跌/精度处理） |
| 2 | **badge-pct** | `widgets/badge-pct.js` | 涨跌幅徽章（红/绿/灰三色） |
| 3 | **data-table** | `widgets/data-table.js` | 关键数据表格（通用，右栏复用） |
| 4 | **mini-chart** | `widgets/mini-chart.js` | 迷你走势图（自选列表右侧小图） |
| 5 | **icon-toggle** | `widgets/icon-toggle.js` | 图标开关（¥/⇅/◍/▤/⚑ 等标注层开关） |

> widgets 不挂 manifest（无数据无行为），但进 design.html DS 规范登记（尺寸/颜色/用法）。

---

## 四、数据服务层（services/）——API 调用/格式化/缓存，按域分文件

| # | 服务名 | 文件 | 职责 |
|---|---|---|---|
| 1 | **market-api** | `services/market-api.js` | 行情数据：K 线/分时/报价/五档（对接 api_server.py / ws） |
| 2 | **stock-info** | `services/stock-info.js` | 股票资料：公司基本信息/财务/关键数据（对接 api_server.py） |
| 3 | **event-api** | `services/event-api.js` | 事件数据：财报/解禁/宏观/公告（对接后端事件服务） |
| 4 | **chip-api** | `services/chip-api.js` | 筹码分布：成本分布/平均成本/获利比例（对接后端筹码服务） |
| 5 | **fav-api** | `services/fav-api.js` | 自选同步：增删改/排序/持久化（对接后端用户数据） |

> services 不挂 manifest（无 UI），但进 frontend_map 的 `data_flow` 字段锚定。

---

## 五、拆分后 app1.js 应该只剩什么

```javascript
// app1.js 拆分后只负责：
// 1. 页面初始化（sqInit）
// 2. 各功能模块按 manifest 注册顺序 init
// 3. 全局事件（切票/切周期/窗口 resize）分发到各模块
// 4. 不再包含任何具体功能的业务逻辑
```

目标：app1.js 从 ~6200 行 → ≤500 行（骨架+分发器）。

---

## 六、数据接通优先级（逐项闭环顺序）

| 序 | 组件 | 理由 | 后端依赖 |
|---|---|---|---|
| 1 | **quote-panel** | 最容易：daily_valuation + stock_basic 已确认有表 | 后端已就绪（CH 只读） |
| 2 | **fav-list** | localStorage 已有，补实时价格推送即可 | 需行情推送通道（ws/poll） |
| 3 | **chip-peak** | 核心卖点，但需确认后端是否有筹码分布表 | 需核实 CH 表或后端接口 |
| 4 | **event-row** | 日历事件表已有，需格式化 | 后端已就绪 |
| 5 | **order-book** | L2 实时数据，需 QMT/交易所通道 | 需实盘通道（延后） |

---

## 七、待 Owner 裁定

1. **组件命名**：上表 8 个 features + 5 个 widgets + 4 个 services 命名是否采用？
2. **manifest 13 字段**：是否够用？还需加什么？
3. **拆分粒度**：fav-list 和 draw-tools 是否拆？（fav 跨页复用=强信号；draw 纯前端但反复改=中信号）
4. **数据接通突破口**：quote-panel（右栏关键数据）最容易，先做它当测试？
5. **筹码峰数据源**：CH 里是否有筹码分布相关表？没有的话需后端建接口。
