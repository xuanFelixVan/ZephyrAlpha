---
ttl: task_bound
---

> **文档性质**：stockq 页组件拆分清单 v2（按"单一功能=单一组件=积木"原则重盘）。
> **拆分铁律**：一个视觉区块 + 一种交互行为 + 一个功能语义 = 一个组件。数据源相同但功能不同也必须拆。

# 个股行情页（stockq）组件拆分清单 v2 —— 积木级粒度

## 拆分哲学（ Owner 2026-09-01 裁定）

**单一功能 = 单一组件**。判断标准：
1. **视觉区块独立**：页面上能看到一个独立块，就是一个组件
2. **交互行为独立**：点击/悬停/拖拽/右键菜单，不同交互 = 不同组件
3. **功能语义独立**："显示价格"和"显示估值"是不同功能，即使同数据源
4. **数据源独立**：不同数据源必须拆（兜底红线）
5. **跨页复用信号**：任何可能在其他页面复用的功能，必须独立组件

**反例（禁止）**：把"股票标题+关键数据+五档挂单+简介"糊成一个"资料面板组件"——改标题样式要测五档，改五档逻辑要测标题，回滚互相牵连。

---

## 一、页面骨架（pages/stockq.html）——只负责布局占位

| # | 区域 | 占位组件 | 说明 |
|---|---|---|---|
| 1 | 左栏 | `<div id="sq-sidebar">` | 容器：自选/持仓/搜索 |
| 2 | 中栏 | `<div id="sq-kline-area">` | 容器：K线+副图+时间轴+事件行 |
| 3 | 筹码峰 | `<div id="sq-chip">` | 独立模块容器 |
| 4 | 右栏 | `<div id="sq-info-panel">` | 容器：报价/挂单/数据/新闻... |

> 骨架只负责 CSS 布局和容器 id，**所有逻辑下沉到 features/**。

---

## 二、功能模块（features/stockq/）——积木级，每个视觉块一个

### 左栏区域（3 个组件）

| # | 组件名 | 文件 | 功能语义 | 数据源 | 交互行为 | 验收单 |
|---|---|---|---|---|---|---|
| 1 | **sq-fav-list** | `features/stockq/sq-fav-list.js` | 自选股票列表（增删改排序） | localStorage + 价格推送 | 点击切换股票、拖拽排序、右键菜单 | ACC-F-STOCKQ-FAV-LIST |
| 2 | **sq-position-list** | `features/stockq/sq-position-list.js` | 持仓列表（实盘同步） | QMT 持仓接口 | 点击切换、显示盈亏、刷新状态 | ACC-F-STOCKQ-POSITION-LIST |
| 3 | **sq-search-box** | `features/stockq/sq-search-box.js` | 股票搜索框 | stock_basic 表 | 输入联想、回车选股、历史记录 | ACC-F-STOCKQ-SEARCH-BOX |

### 中栏 K 线区域（10 个组件）

| # | 组件名 | 文件 | 功能语义 | 数据源 | 交互行为 | 验收单 |
|---|---|---|---|---|---|---|
| 4 | **sq-kline-main** | `features/stockq/sq-kline-main.js` | K线主图（蜡烛图+MA/BOLL/SAR） | CH.kline_* | 滚轮缩放、拖拽平移、十字光标 | ACC-F-STOCKQ-KLINE-MAIN |
| 5 | **sq-kline-volume** | `features/stockq/sq-kline-volume.js` | 成交量副图 | CH.kline_* (volume) | 无（纯展示） | ACC-F-STOCKQ-KLINE-VOLUME |
| 6 | **sq-kline-macd** | `features/stockq/sq-kline-macd.js` | MACD 副图 | CH.kline_* (计算) | 无 | ACC-F-STOCKQ-KLINE-MACD |
| 7 | **sq-kline-kdj** | `features/stockq/sq-kline-kdj.js` | KDJ 副图 | CH.kline_* (计算) | 无 | ACC-F-STOCKQ-KLINE-KDJ |
| 8 | **sq-draw-tools** | `features/stockq/sq-draw-tools.js` | 画线工具（趋势/斐波那契/水平线） | none（纯前端） | 点击选工具、拖拽画线、双击编辑 | ACC-F-STOCKQ-DRAW-TOOLS |
| 9 | **sq-marks-bs** | `features/stockq/sq-marks-bs.js` | 量化买卖点标注（▲买▼卖灰框） | 后端信号接口 | ⇅ 开关控显隐 | ACC-F-STOCKQ-MARKS-BS |
| 10 | **sq-marks-trade** | `features/stockq/sq-marks-trade.js` | 真实成交标注（红B绿S） | QMT 成交接口 | ◍ 开关控显隐 | ACC-F-STOCKQ-MARKS-TRADE |
| 11 | **sq-marks-chip** | `features/stockq/sq-marks-chip.js` | 筹码峰标注（48桶分布+POC线） | CH.chip_distribution | ▤ 开关控显隐 | ACC-F-STOCKQ-MARKS-CHIP |
| 12 | **sq-cost-line** | `features/stockq/sq-cost-line.js` | 持仓成本线（黄虚线） | chip-peak.avgCost | ¥ 开关控显隐、悬停提示 | ACC-F-STOCKQ-COST-LINE ✅ |
| 13 | **sq-event-row** | `features/stockq/sq-event-row.js` | 事件时间行（财报/解禁/宏观） | CH.calendar_event | ⚑ 开关控整行收展、点击弹详情 | ACC-F-STOCKQ-EVENT-ROW |
| 14 | **sq-timeline** | `features/stockq/sq-timeline.js` | 底部时间轴 | none（纯前端） | 拖拽调整高度 | ACC-F-STOCKQ-TIMELINE |

### 筹码峰独立区域（1 个组件）

| # | 组件名 | 文件 | 功能语义 | 数据源 | 交互行为 | 验收单 |
|---|---|---|---|---|---|---|
| 15 | **sq-chip-peak** | `features/stockq/sq-chip-peak.js` | 筹码峰主图（48桶+成本线+获利比例） | CH.chip_distribution | 悬停显示桶详情、光标联动重算 | ACC-F-STOCKQ-CHIP-PEAK |

### 右栏资料面板（11 个组件）——按用户要求拆到最细

| # | 组件名 | 文件 | 功能语义 | 数据源 | 交互行为 | 验收单 |
|---|---|---|---|---|---|---|
| 16 | **sq-stock-header** | `features/stockq/sq-stock-header.js` | 股票标题（名称+代码+价格+涨跌幅+状态灯） | CH.daily_valuation + stock_basic | 无（纯展示） | ACC-F-STOCKQ-STOCK-HEADER |
| 17 | **sq-sector-tags** | `features/stockq/sq-sector-tags.js` | 行业归属标签（白酒/沪深300/中证50...） | stock_basic.sector / index_constituent | 点击跳转板块页 | ACC-F-STOCKQ-SECTOR-TAGS |
| 18 | **sq-company-intro** | `features/stockq/sq-company-intro.js` | 公司简介文本 | stock_basic.intro / 后端文本接口 | 展开/收起长文本 | ACC-F-STOCKQ-COMPANY-INTRO |
| 19 | **sq-order-book** | `features/stockq/sq-order-book.js` | 五档挂单（买1-5/卖1-5） | QMT l2_tick / 实时推送 | 无（纯展示） | ACC-F-STOCKQ-ORDER-BOOK |
| 20 | **sq-key-data** | `features/stockq/sq-key-data.js` | 关键数据表（最高/最低/开盘/昨收/量比/换手/市盈/市净） | CH.daily_valuation | 无 | ACC-F-STOCKQ-KEY-DATA |
| 21 | **sq-financial-read** | `features/stockq/sq-financial-read.js` | 财务解读（收入/利润/ROE 趋势） | CH.finance 表 / 后端接口 | 点击切换报告期 | ACC-F-STOCKQ-FINANCIAL-READ |
| 22 | **sq-related-news** | `features/stockq/sq-related-news.js` | 相关新闻列表 | CH.news / 后端新闻接口 | 点击弹详情、滚动加载 | ACC-F-STOCKQ-RELATED-NEWS |
| 23 | **sq-quant-analysis** | `features/stockq/sq-quant-analysis.js` | 量化分析（因子评分/模型信号） | 后端量化接口 | 点击展开详细分析 | ACC-F-STOCKQ-QUANT-ANALYSIS |
| 24 | **sq-fair-value** | `features/stockq/sq-fair-value.js` | 合理估值（DCF/PE/PS 估值区间） | 后端估值接口 | 点击切换估值模型 | ACC-F-STOCKQ-FAIR-VALUE |
| 25 | **sq-limit-up-gene** | `features/stockq/sq-limit-up-gene.js` | 涨停基因（近一年涨停统计） | CH.limit_up_pool / 后端接口 | 无 | ACC-F-STOCKQ-LIMIT-UP-GENE |
| 26 | **sq-data-source-badge** | `features/stockq/sq-data-source-badge.js` | 数据源状态灯（DS-12 四态） | 各组件数据状态聚合 | 无（纯展示） | ACC-F-STOCKQ-DATA-SOURCE-BADGE |

**右栏总计 11 个组件**。之前糊成"资料面板"，现在拆成：标题/标签/简介/挂单/关键数据/财务/新闻/量化/估值/涨停基因/状态灯。

---

## 三、纯 UI 展示件（widgets/）——无数据无行为，仅渲染样式

| # | 组件名 | 文件 | 功能 | 复用范围 |
|---|---|---|---|---|
| 1 | **w-price-tag** | `widgets/w-price-tag.js` | 价格标签（红涨绿跌/精度处理） | 全站 |
| 2 | **w-pct-badge** | `widgets/w-pct-badge.js` | 涨跌幅徽章（红/绿/灰三色） | 全站 |
| 3 | **w-data-table** | `widgets/w-data-table.js` | 键值对数据表格（通用） | 全站 |
| 4 | **w-mini-chart** | `widgets/w-mini-chart.js` | 迷你走势图 | 自选列表/板块页 |
| 5 | **w-icon-toggle** | `widgets/w-icon-toggle.js` | 图标开关（¥/⇅/◍/▤/⚑） | 全站标注层 |
| 6 | **w-status-light** | `widgets/w-status-light.js` | 状态灯（DS-12 四态样式） | 全站数据功能 |

---

## 四、数据服务层（services/）——按数据源域分文件

| # | 服务名 | 文件 | 职责 | 对接后端 |
|---|---|---|---|---|
| 1 | **svc-market** | `services/svc-market.js` | K线/分时/报价/五档 | api_server.py (8890) |
| 2 | **svc-stock-info** | `services/svc-stock-info.js` | 公司资料/财务/关键数据 | api_server.py |
| 3 | **svc-events** | `services/svc-events.js` | 日历事件/财报/解禁/公告 | api_server.py |
| 4 | **svc-chip** | `services/svc-chip.js` | 筹码分布/成本/获利比例 | api_server.py |
| 5 | **svc-fav** | `services/svc-fav.js` | 自选增删改/排序/同步 | 后端用户服务 |
| 6 | **svc-position** | `services/svc-position.js` | 持仓查询/盈亏计算 | QMT 接口 |
| 7 | **svc-news** | `services/svc-news.js` | 新闻列表/详情 | 后端新闻服务 |
| 8 | **svc-quant** | `services/svc-quant.js` | 量化信号/因子/模型 | 后端量化服务 |

---

## 五、拆分后文件结构

```
web/
  pages/
    stockq.html           # 骨架：26 个组件的容器占位
  features/
    stockq/               # 个股行情页专属功能模块（26 个）
      sq-fav-list.js
      sq-position-list.js
      sq-search-box.js
      sq-kline-main.js
      sq-kline-volume.js
      sq-kline-macd.js
      sq-kline-kdj.js
      sq-draw-tools.js
      sq-marks-bs.js
      sq-marks-trade.js
      sq-marks-chip.js
      sq-cost-line.js ✅
      sq-event-row.js
      sq-timeline.js
      sq-chip-peak.js
      sq-stock-header.js
      sq-sector-tags.js
      sq-company-intro.js
      sq-order-book.js
      sq-key-data.js
      sq-financial-read.js
      sq-related-news.js
      sq-quant-analysis.js
      sq-fair-value.js
      sq-limit-up-gene.js
      sq-data-source-badge.js
  widgets/                # 纯 UI 件（6 个，全站复用）
  services/               # 数据服务（8 个，按域分）
  core/
    app1.js               # 拆分后 ≤500 行：初始化+模块注册+事件分发
```

---

## 六、数据接通优先级（逐项闭环）

| 序 | 组件 | 理由 | 后端依赖 |
|---|---|---|---|
| 1 | **sq-stock-header** | 最容易：名称+价格+涨跌，daily_valuation 已有 | CH 已就绪 |
| 2 | **sq-key-data** | 同表扩展（最高/最低/开盘/昨收...） | CH 已就绪 |
| 3 | **sq-sector-tags** | stock_basic 有 sector 字段 | CH 已就绪 |
| 4 | **sq-fav-list** | localStorage 已有，补实时价格 | 需价格推送通道 |
| 5 | **sq-event-row** | calendar_event 表已有 | CH 已就绪 |
| 6 | **sq-order-book** | 需 L2 实时 | QMT 通道（延后） |
| 7 | **sq-position-list** | 需 QMT 实盘 | QMT 接口（延后） |
| 8 | **sq-chip-peak** | 需确认筹码表 | CH 表核实/后端接口 |
| 9+ | 其余 | 逐步推进 | 按后端就绪顺序 |

---

## 七、manifest 表头字段（统一 14 字段）

```yaml
id: sq-<name>                   # kebab-case
name: 中文名                     # 显示用
file: features/stockq/<name>.js # 单文件全包
page: stockq                    # 所属页面
domain: <数据域>                 # market/stock_info/events/chip/fav/position/news/quant/none
depends: [id1, id2]             # 显式依赖（如 cost-line 依赖 chip-peak）
toggle: "开关图标/文字"          # 工具栏开关（无开关则空）
styles: self-injected            # 样式自注入
acceptance: ACC-F-STOCKQ-XXX    # 验收单
handbook: [FEH-xxx]             # 手册条目
data_source: "CH.table / QMT / localStorage / none"
update_frequency: "实时/分钟/日/不适用"
user_action: "点击/悬停/拖拽/右键/无"
fallback_behavior: "后端挂了显示什么"
screenshot_ref: "tests/frontend/baselines/xxx.png"
```

---

## 八、待 Owner 裁定

1. **26 个 features + 6 个 widgets + 8 个 services 命名是否采用？**
2. **右栏拆到 11 个是否够细？** 还有没有遗漏的功能块？
3. **manifest 14 字段（新增 domain 数据域）** 是否够用？
4. **先做 sq-stock-header（右栏标题）当首个测试？** 最容易：读 daily_valuation 表，显示名称+价格+涨跌幅+DS-12 状态灯。
5. **拆完后 app1.js 目标 ≤500 行**，是否接受骨架只留事件分发？
