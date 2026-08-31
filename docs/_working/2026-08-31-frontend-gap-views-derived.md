---
ttl: task_bound
---

> **派生物声明**：本文件由 `scripts/governance/d5_architecture/generators/generate_frontend_gap_views.py` 自动生成，**禁止手工修改**（手改会被下次派生覆盖）。真源=frontend_map.yaml + depgraph nodes 前端覆盖三字段。取代对象：两本手工缺口总账（2026-08-22 正向/反向账）——过渡期双跑对照，Owner 裁定后总账停手工维护。

# 前端缺口视图（派生活账） · 2026-09-01 01:57 中国标准时间

## A. 前端有 → 后端没有（318 项：frontend_map 功能点 backend_ref 空）

| 功能点 | 页面 | 名称 | 状态 |
|---|---|---|---|
| F-STOCKQ-COSTLINE | P-STOCKQ | 持仓成本线 | 已建 |
| F-STOCKQ-MARKS | P-STOCKQ | 量化买卖点标注 | 已建 |
| F-STOCKQ-TRADES | P-STOCKQ | 真实成交买卖点 | 已建 |
| F-STOCKQ-DRAW | P-STOCKQ | 画线工具 | 已建 |
| F-STOCKQ-INDICATORS | P-STOCKQ | 指标系统 | 已建 |
| F-STOCKQ-EVTROW | P-STOCKQ | 事件图标行 | 已建 |
| F-STOCKQ-TIMELINE | P-STOCKQ | 自定义时间轴 | 已建 |
| F-STOCKQ-CHIP | P-STOCKQ | 筹码峰分布 | 已建 |
| F-STOCKQ-WATCHLIST | P-STOCKQ | 自选列表 | 已建 |
| F-STOCKQ-INFO | P-STOCKQ | 右栏资料面板 | 已建 |
| F-OVW-LAYOUT | P-OVERVIEW | 布局管理 | 已建 |
| F-OVW-ICONBAR | P-OVERVIEW | 竖排图标栏 | 已建 |
| F-OVW-POS-A | P-OVERVIEW | A股持仓 | 已建 |
| F-OVW-POS-C | P-OVERVIEW | 币圈持仓 | 已建 |
| F-OVW-INDEX-CARDS | P-OVERVIEW | 指数卡片 | 已建 |
| F-OVW-TICKER | P-OVERVIEW | ticker-bar | 已建 |
| P-AICHAT-AUTO-01 | P-AICHAT | 对话 | 已建 |
| P-AICHAT-AUTO-02 | P-AICHAT | 能干什么 | 已建 |
| P-AICHAT-AUTO-03 | P-AICHAT | 不能干什么 | 已建 |
| P-AITASK-AUTO-01 | P-AITASK | 任务流水 | 已建 |
| P-AITASK-AUTO-02 | P-AITASK | ReAct 研究助手 | 已建 |
| P-AITASK-AUTO-03 | P-AITASK | 情景记忆 | 已建 |
| P-AITASK-AUTO-04 | P-AITASK | GPU 共识调度 | 已建 |
| P-BACKTEST-AUTO-01 | P-BACKTEST | 绩效指标明细 Performance Metrics Detail | 已建 |
| P-BACKTEST-AUTO-02 | P-BACKTEST | 持仓明细 Position Details | 已建 |
| P-BACKTEST-AUTO-03 | P-BACKTEST | 月度收益率热力图 Monthly Returns | 已建 |
| P-BACKTEST-AUTO-04 | P-BACKTEST | 当日资金 Daily Capital (2019-01-02) | 已建 |
| P-BACKTEST-AUTO-05 | P-BACKTEST | 当日持仓 Daily Positions (2019-01-02) | 已建 |
| P-BACKTEST-AUTO-06 | P-BACKTEST | 当日委托 Daily Orders (2019-01-02) | 已建 |
| P-BACKTEST-AUTO-07 | P-BACKTEST | 交易明细 Trade Details | 已建 |
| P-BACKTEST-AUTO-08 | P-BACKTEST | 新建回测 | 已建 |
| P-CALENDAR-AUTO-01 | P-CALENDAR | 2026 年 8 月 | 已建 |
| P-CALENDAR-AUTO-02 | P-CALENDAR | 当日清单 · | 已建 |
| P-CALENDAR-AUTO-03 | P-CALENDAR | 数据源与纪律 | 已建 |
| P-CHAINMAP-AUTO-01 | P-CHAINMAP | 产业链浏览 | 已建 |
| P-CHAINMAP-AUTO-02 | P-CHAINMAP | 个股落位查询 | 已建 |
| P-CHAINMAP-AUTO-03 | P-CHAINMAP | 供应链指标 | 已建 |
| P-CHAINMAP-AUTO-04 | P-CHAINMAP | 说明与边界 | 已建 |
| P-CHAINMAP-AUTO-05 | P-CHAINMAP | 规划内容（待与 Owner 对齐后细化） | 已建 |
| P-CHAINMAP-AUTO-06 | P-CHAINMAP | 与现有页面的边界 | 已建 |
| P-CRYPTOBT-AUTO-01 | P-CRYPTOBT | 净值曲线（演示） | 已建 |
| P-CRYPTOINFO-AUTO-01 | P-CRYPTOINFO | 链上数据（待接入占位） | 已建 |
| P-CRYPTOMARKET-AUTO-01 | P-CRYPTOMARKET | 永续合约行情 | 已建 |
| P-CRYPTOMARKET-AUTO-02 | P-CRYPTOMARKET | 资金费率热力（8h） | 已建 |
| P-CRYPTOMARKET-AUTO-03 | P-CRYPTOMARKET | BTC 持仓量 OI（24h） | 已建 |
| P-CRYPTOMARKET-AUTO-04 | P-CRYPTOMARKET | 爆仓地图（24h 待清算密集区） | 已建 |
| P-CRYPTOMARKET-AUTO-05 | P-CRYPTOMARKET | 多空比 + 标记/指数价差 | 已建 |
| P-CRYPTOPOS-AUTO-01 | P-CRYPTOPOS | 合约仓位 | 已建 |
| P-CRYPTOPOS-AUTO-02 | P-CRYPTOPOS | 强平预警带 | 已建 |
| P-CRYPTOPOS-AUTO-03 | P-CRYPTOPOS | 资金费累计 + 风控规则 | 已建 |
| P-CRYPTOSTRAT-AUTO-01 | P-CRYPTOSTRAT | 网格交易 | 已建 |
| P-CRYPTOSTRAT-AUTO-02 | P-CRYPTOSTRAT | 资金费套利 | 已建 |
| P-CRYPTOSTRAT-AUTO-03 | P-CRYPTOSTRAT | 趋势跟踪 | 已建 |
| P-CRYPTOSTRAT-AUTO-04 | P-CRYPTOSTRAT | 与 A 股策略的关系 | 已建 |
| P-DATAINFO-AUTO-01 | P-DATAINFO | 八表资产地图 | 已建 |
| P-DATAINFO-AUTO-02 | P-DATAINFO | 规划深页 | 已建 |
| P-DATASRC-AUTO-01 | P-DATASRC | 源清单 | 已建 |
| P-DATASRC-AUTO-02 | P-DATASRC | SLA burn-rate | 已建 |
| P-DATASRC-AUTO-03 | P-DATASRC | 主备切换+告警流水 | 已建 |
| P-DESIGN-AUTO-01 | P-DESIGN | 底色族（5+4）——结构色，不可用于文字/数据；v7（2026-08-30）：一级卡片底=半透明叠层 --card7（S | 已建 |
| P-DESIGN-AUTO-02 | P-DESIGN | 文字灰阶（3+1）——全部文字只许这几级；v7 新增 --label=卡标题/表头/分区标专用标签灰（宽字距语法见 DS | 已建 |
| P-DESIGN-AUTO-03 | P-DESIGN | 功能色（6+3）——色系 v6 极简功能主义延续：图表坐标系外一律灰阶，彩色只给功能；v7 新增提亮族与信息蓝（Shar | 已建 |
| P-DESIGN-AUTO-04 | P-DESIGN | 透明度族（颜色收敛规则——所有"底色强调"一律透明化，禁实色块） | 已建 |
| P-DESIGN-AUTO-05 | P-DESIGN | OKX 清单照抄记录（2026-08-27，markets/favorite 页 getComputedStyle 全量 | 已建 |
| P-DESIGN-AUTO-06 | P-DESIGN | 刻意超越包（OKX 没有的 4 处微细节——"高级感=纹理不是颜色"） | 已建 |
| P-DESIGN-AUTO-07 | P-DESIGN | 色彩秩序 v6 极简功能主义（2026-08-28 Owner 裁定：除必要颜色能不用就不用——K线涨跌红绿/进度条蓝/ | 已建 |
| P-DESIGN-AUTO-08 | P-DESIGN | 禁色清单（已废止，合规审查见即改） | 已建 |
| P-DESIGN-AUTO-09 | P-DESIGN | 4.1 卡片（信息容器唯一形态） | 已建 |
| P-DESIGN-AUTO-10 | P-DESIGN | 4.2 KPI 指标卡（核心数字=锚点） | 已建 |
| P-DESIGN-AUTO-11 | P-DESIGN | 4.3 badge 六族（语义映射唯一表） | 已建 |
| P-DESIGN-AUTO-12 | P-DESIGN | 4.4 alert-row 族（v6 去框化：err/warn/info + .bad=err 别名，Owner 202 | 已建 |
| P-DESIGN-AUTO-13 | P-DESIGN | 4.5 表格 | 已建 |
| P-DESIGN-AUTO-14 | P-DESIGN | 4.6 tab / 按钮 / 输入 | 已建 |
| P-DESIGN-AUTO-15 | P-DESIGN | 4.7 顶栏导航与下拉 | 已建 |
| P-DESIGN-AUTO-16 | P-DESIGN | 4.8 ⓘ 注解悬浮组件（版面简洁化核心） | 已建 |
| P-DESIGN-AUTO-17 | P-DESIGN | 4.9 ticker 横条 / toast / 状态灯 | 已建 |
| P-DESIGN-AUTO-18 | P-DESIGN | 4.10 chip 胶囊族（v7 新增，SharpLink 徽章语法） | 已建 |
| P-DESIGN-AUTO-19 | P-DESIGN | 4.11 合并模块族（v7 新增·终版样板实证——同类低密度卡片合一，消灭卡内留白） | 已建 |
| P-DESIGN-AUTO-20 | P-DESIGN | 4.12 决策卡 dc-card（R18 划重点例外件——全站唯一大字彩色强调） | 已建 |
| P-DESIGN-AUTO-21 | P-DESIGN | K 线视图 5 档尺寸标准（2026-08-27 Owner 方向：多档标准+全主图滚轮缩放） | 已建 |
| P-DESIGN-AUTO-22 | P-DESIGN | 进度条标准（.pbar 族——马上多功能上线，统一此规格） | 已建 |
| P-DESIGN-AUTO-23 | P-DESIGN | K 线规范图（标准蓝图——真实引擎渲染+元素标注；验收对照用） | 已建 |
| P-DESIGN-AUTO-24 | P-DESIGN | 合规审查记录 | 已建 |
| P-DESIGN-AUTO-25 | P-DESIGN | DS-1 色彩系统 | 已建 |
| P-DESIGN-AUTO-26 | P-DESIGN | DS-2 字体系统 | 已建 |
| P-DESIGN-AUTO-27 | P-DESIGN | DS-3 间距与圆角 | 已建 |
| P-DESIGN-AUTO-28 | P-DESIGN | DS-4 组件规范 | 已建 |
| P-DESIGN-AUTO-29 | P-DESIGN | DS-5 K 线与图表专项 | 已建 |
| P-DESIGN-AUTO-30 | P-DESIGN | DS-6 语义色宪章 | 已建 |
| P-DESIGN-AUTO-31 | P-DESIGN | DS-7 图标与装饰规则 | 已建 |
| P-DESIGN-AUTO-32 | P-DESIGN | DS-8 负反馈与待接入规范 | 已建 |
| P-DESIGN-AUTO-33 | P-DESIGN | DS-9 组件→页面适用索引 | 已建 |
| P-DESIGN-AUTO-34 | P-DESIGN | DS-10 模块缩放规范 | 已建 |
| P-DESIGN-AUTO-35 | P-DESIGN | DS-11 模块拆件标准 | 已建 |
| P-EXPERIMENT-AUTO-01 | P-EXPERIMENT | Runs | 已建 |
| P-EXPERIMENT-AUTO-02 | P-EXPERIMENT | c1_mock_20260819_sector · 详情 | 已建 |
| P-FACTOR-AUTO-01 | P-FACTOR | 因子看板 | 已建 |
| P-FACTOR-AUTO-02 | P-FACTOR | 反转因子 · 分组净值 | 已建 |
| P-FACTOR-AUTO-03 | P-FACTOR | IC 滚动稳定 + 衰减 | 已建 |
| P-FITNESS-AUTO-01 | P-FITNESS | 近 30 次趋势 | 已建 |
| P-GOVANA-AUTO-01 | P-GOVANA | 状态 | 已建 |
| P-INDEX-AUTO-01 | P-INDEX | 阶段状态标注 | 已建 |
| P-LIVE-AUTO-01 | P-LIVE | 逐笔回报时序 | 已建 |
| P-LIVE-AUTO-02 | P-LIVE | 市场 Regime | 已建 |
| P-LIVE-AUTO-03 | P-LIVE | 情绪温度 | 已建 |
| P-LIVE-AUTO-04 | P-LIVE | 接力情绪周期 | 已建 |
| P-LIVE-AUTO-05 | P-LIVE | 极端预警 | 已建 |
| P-LIVE-AUTO-06 | P-LIVE | 决策链 | 已建 |
| P-LIVE-AUTO-07 | P-LIVE | 风控实时 | 已建 |
| P-LIVE-AUTO-08 | P-LIVE | 今日交易计划 | 已建 |
| P-LIVE-AUTO-09 | P-LIVE | 当日委托 / 成交 | 已建 |
| P-LIVE-AUTO-10 | P-LIVE | 系统运行日志 | 已建 |
| P-LIVE-AUTO-11 | P-LIVE | 下单 | 已建 |
| P-LIVE-AUTO-12 | P-LIVE | 上证指数 i主版面 · 分钟级 | 已建 |
| P-LIVE-AUTO-13 | P-LIVE | 副指数 · 深证 / 创业板 / 科创 | 已建 |
| P-LIVE-AUTO-14 | P-LIVE | 市场统计 | 已建 |
| P-LIVE-AUTO-15 | P-LIVE | 风格分化 i | 已建 |
| P-LIVE-AUTO-16 | P-LIVE | 涨跌分档分布 i | 已建 |
| P-LIVE-AUTO-17 | P-LIVE | 涨停强度 · 今昨对比 i | 已建 |
| P-LIVE-AUTO-18 | P-LIVE | 成交额 · 分时累计 i | 已建 |
| P-LIVE-AUTO-19 | P-LIVE | 大盘状态 · 因子构成面板 i | 已建 |
| P-MACRO-AUTO-01 | P-MACRO | 规划内容（待与 Owner 对齐后细化） | 已建 |
| P-MACRO-AUTO-02 | P-MACRO | 与现有页面的边界 | 已建 |
| P-MACRO-AUTO-03 | P-MACRO | 天气数据（40 城市） | 已建 |
| P-MODELS-AUTO-01 | P-MODELS | 模型注册表 | 已建 |
| P-MODELS-AUTO-02 | P-MODELS | 训练态质量 | 已建 |
| P-MODELS-AUTO-03 | P-MODELS | 服务态四维漂移+影子部署 | 已建 |
| P-MODELS-AUTO-04 | P-MODELS | 学习效果回喂 | 已建 |
| P-MODELS-AUTO-05 | P-MODELS | 决策解释+人工干预留痕 | 已建 |
| P-MODELS-AUTO-06 | P-MODELS | 压缩验证三阶段 | 已建 |
| P-MODELS-AUTO-07 | P-MODELS | 因子×模型双向利用度 | 已建 |
| P-MODELS-AUTO-08 | P-MODELS | 本页结论怎么来的 · 证据链 | 已建 |
| P-MODLEDGER-AUTO-01 | P-MODLEDGER | 全模块清单 | 已建 |
| P-MODLEDGER-AUTO-02 | P-MODLEDGER | 口径与数据源说明 | 已建 |
| P-MODLIB-AUTO-01 | P-MODLIB | 一、容器类 信息的外壳 | 已建 |
| P-MODLIB-AUTO-02 | P-MODLIB | 二、表格类 列数定族：≤5 列窄表 / ≥7 列宽表 | 已建 |
| P-MODLIB-AUTO-03 | P-MODLIB | 三、图表类 统一铁律：数据驱动 fluid 重绘（page:show/resize），禁 viewBox-none 拉伸 | 已建 |
| P-MODLIB-AUTO-04 | P-MODLIB | 四、交互控件 小件族：全部耐宽、不参与拉宽 | 已建 |
| P-MODLIB-AUTO-05 | P-MODLIB | 五、信息流 时间线/新闻/日志/辩论/矩阵 | 已建 |
| P-MODLIB-AUTO-06 | P-MODLIB | 六、专用模块 各自有明确宽度姿态 | 已建 |
| P-MODLIB-AUTO-07 | P-MODLIB | 七、网格画廊 auto-fill 结论卡阵——一句一行，依据收 ⓘ | 已建 |
| P-MODLIB-AUTO-08 | P-MODLIB | 八、补件 盘点缺口补样 | 已建 |
| P-MODLIB-AUTO-09 | P-MODLIB | 九、停靠布局试点 Docking Layout · 同花顺式手感验证区——拖标题栏到任意模块四向分裂；拖分隔缝调宽高（联 | 已建 |
| P-MODLIB-AUTO-10 | P-MODLIB | 十、模块拆件契约试点 Module Contract · features/&lt;id&gt;.js 单文件功能模块— | 已建 |
| P-MODLIB-AUTO-11 | P-MODLIB | 卡片标题 i演示数据 | 已建 |
| P-MODLIB-AUTO-12 | P-MODLIB | 地缘政治风险 待接入 | 已建 |
| P-MODLIB-AUTO-13 | P-MODLIB | 副指数 · 深证 / 创业板 / 科创 | 已建 |
| P-MODLIB-AUTO-14 | P-MODLIB | 涨停强度 · 今昨对比 | 已建 |
| P-MODLIB-AUTO-15 | P-MODLIB | 持仓明细（宽表节选） | 已建 |
| P-MODLIB-AUTO-16 | P-MODLIB | 任务清单 · 动态表 | 已建 |
| P-MODLIB-AUTO-17 | P-MODLIB | 策略定义 | 已建 |
| P-MODLIB-AUTO-18 | P-MODLIB | 阶段盈亏 | 已建 |
| P-MODLIB-AUTO-19 | P-MODLIB | 个股行情 · K线工作台 i日K分时 | 已建 |
| P-MODLIB-AUTO-20 | P-MODLIB | 上证指数 | 已建 |
| P-MODLIB-AUTO-21 | P-MODLIB | 迷你走势 | 已建 |
| P-MODLIB-AUTO-22 | P-MODLIB | 权益分时 vs 回测包络 i | 已建 |
| P-MODLIB-AUTO-23 | P-MODLIB | 涨跌分档分布 | 已建 |
| P-MODLIB-AUTO-24 | P-MODLIB | 营收 / 归母净利 · 8 季 | 已建 |
| P-MODLIB-AUTO-25 | P-MODLIB | 风险预算 | 已建 |
| P-MODLIB-AUTO-26 | P-MODLIB | 长任务进度 | 已建 |
| P-MODLIB-AUTO-27 | P-MODLIB | 月度收益热力 · 2026 | 已建 |
| P-MODLIB-AUTO-28 | P-MODLIB | 事件日历 · 本周 | 已建 |
| P-MODLIB-AUTO-29 | P-MODLIB | 情绪温度 | 已建 |
| P-MODLIB-AUTO-30 | P-MODLIB | 相对强度光谱 · 行业 | 已建 |
| P-MODLIB-AUTO-31 | P-MODLIB | 市场相位带 · 近一年 | 已建 |
| P-MODLIB-AUTO-32 | P-MODLIB | 明日 8 态推演 | 已建 |
| P-MODLIB-AUTO-33 | P-MODLIB | 模块布局 i | 已建 |
| P-MODLIB-AUTO-34 | P-MODLIB | 逐笔回报时序 | 已建 |
| P-MODLIB-AUTO-35 | P-MODLIB | 新闻清单 · 两天滚动窗 | 已建 |
| P-MODLIB-AUTO-36 | P-MODLIB | 系统运行日志 | 已建 |
| P-MODLIB-AUTO-37 | P-MODLIB | 多方 · 交易员 i | 已建 |
| P-MODLIB-AUTO-38 | P-MODLIB | 空方 · 风控官 i | 已建 |
| P-MODLIB-AUTO-39 | P-MODLIB | 实时情景矩阵 i | 已建 |
| P-MODLIB-AUTO-40 | P-MODLIB | AI 助手 本地 qwen3:8b | 已建 |
| P-MODLIB-AUTO-41 | P-MODLIB | 下单 human_gated | 已建 |
| P-MODLIB-AUTO-42 | P-MODLIB | 决策链 · 漏斗 | 已建 |
| P-MODLIB-AUTO-43 | P-MODLIB | 73 域骨架 · 数据流 | 已建 |
| P-MODLIB-AUTO-44 | P-MODLIB | 架构全景 · 嵌入 8765 未启动 | 已建 |
| P-NEWS-AUTO-01 | P-NEWS | 新闻清单 | 已建 |
| P-NEWS-AUTO-02 | P-NEWS | 预期差分析 | 已建 |
| P-NEWS-AUTO-03 | P-NEWS | 可预测性分布 | 已建 |
| P-NEWS-AUTO-04 | P-NEWS | 情绪聚合分析 | 已建 |
| P-NEWS-AUTO-05 | P-NEWS | 公告流 | 已建 |
| P-NEWS-AUTO-06 | P-NEWS | 当日新闻清单 | 已建 |
| P-NEWS-AUTO-07 | P-NEWS | 情绪分析 | 已建 |
| P-NEWS-AUTO-08 | P-NEWS | 今日热点 | 已建 |
| P-NEWS-AUTO-09 | P-NEWS | 公司公告 | 已建 |
| P-OVERSEAS-AUTO-01 | P-OVERSEAS | 整体分析 | 已建 |
| P-OVERSEAS-AUTO-02 | P-OVERSEAS | 美债利率深区 | 已建 |
| P-PANO-AUTO-01 | P-PANO | 功能域 | 已建 |
| P-PANO-AUTO-02 | P-PANO | 嵌入查看 | 已建 |
| P-POLICY-AUTO-01 | P-POLICY | 板块维度（季度净变动，推导） | 已建 |
| P-POLICY-AUTO-02 | P-POLICY | 个股维度（2026Q2 十大股东推导） | 已建 |
| P-POLICY-AUTO-03 | P-POLICY | 政策流 | 已建 |
| P-POLICY-AUTO-04 | P-POLICY | 国家队持仓变动（社保/汇金） | 已建 |
| P-POLICY-AUTO-05 | P-POLICY | 宽基 ETF 份额异动 | 已建 |
| P-POLICY-AUTO-06 | P-POLICY | 地缘政治 / 战争风险 | 已建 |
| P-POSITION-AUTO-01 | P-POSITION | 个股贡献（正前 3 / 负前 2） | 已建 |
| P-POSITION-AUTO-02 | P-POSITION | 按板块汇总 | 已建 |
| P-POSITION-AUTO-03 | P-POSITION | 按因子汇总 | 已建 |
| P-POSITION-AUTO-04 | P-POSITION | 合并持仓（3 账户） | 已建 |
| P-POSITION-AUTO-05 | P-POSITION | 盈亏日历 | 已建 |
| P-POSITION-AUTO-06 | P-POSITION | 资金流动 | 已建 |
| P-POSITION-AUTO-07 | P-POSITION | 阶段盈亏 | 已建 |
| P-POSITION-AUTO-08 | P-POSITION | 收益分析 | 已建 |
| P-POSITION-AUTO-09 | P-POSITION | 持仓明细 | 已建 |
| P-POSITION-AUTO-10 | P-POSITION | 持仓盈亏归因 | 已建 |
| P-POSITION-AUTO-11 | P-POSITION | 相关性净额 | 已建 |
| P-POSITION-AUTO-12 | P-POSITION | 组合政策容忍带 | 已建 |
| P-POSITION-AUTO-13 | P-POSITION | 风险告警条 | 已建 |
| P-PROJMAP-AUTO-01 | P-PROJMAP | 真源与现状 | 已建 |
| P-PROJMAP-AUTO-02 | P-PROJMAP | 73 域骨架预览 | 已建 |
| P-PROJMAP-AUTO-03 | P-PROJMAP | 当前可用替代 | 已建 |
| P-RATING-AUTO-01 | P-RATING | 评级变动流 | 已建 |
| P-RATING-AUTO-02 | P-RATING | 金股池 | 已建 |
| P-RATING-AUTO-03 | P-RATING | AI 深研 | 已建 |
| P-REVIEW-AUTO-01 | P-REVIEW | 交易统计（实盘） 口径随上方周期切换 · trades/journal 聚合，多口径聚合管线落地后转真（I-2） | 已建 |
| P-REVIEW-AUTO-02 | P-REVIEW | 打板复盘 复盘统计语境（晋级率/收益统计，回答"今天打板生态能不能赚钱"）；盘中实时梯队结构 → 「板块全景」；数据：l | 已建 |
| P-REVIEW-AUTO-03 | P-REVIEW | Brinson 拆解 | 已建 |
| P-REVIEW-AUTO-04 | P-REVIEW | 因子暴露拆解 | 已建 |
| P-REVIEW-AUTO-05 | P-REVIEW | 今日执行回看 | 已建 |
| P-REVIEW-AUTO-06 | P-REVIEW | PnL 对账 + 归因 | 已建 |
| P-REVIEW-AUTO-07 | P-REVIEW | 按情景胜率 | 已建 |
| P-REVIEW-AUTO-08 | P-REVIEW | 按板块胜率 | 已建 |
| P-REVIEW-AUTO-09 | P-REVIEW | 连板梯队晋级明细 | 已建 |
| P-REVIEW-AUTO-10 | P-REVIEW | 打板收益统计 | 已建 |
| P-REVIEW-AUTO-11 | P-REVIEW | 因子级归因 | 已建 |
| P-REVIEW-AUTO-12 | P-REVIEW | 压力测试盘后验证 | 已建 |
| P-REVIEW-AUTO-13 | P-REVIEW | 预案回看 | 已建 |
| P-REVIEW-AUTO-14 | P-REVIEW | 因子健康 | 已建 |
| P-REVIEW-AUTO-15 | P-REVIEW | 龙虎榜 · 席位"谁在买" | 已建 |
| P-REVIEW-AUTO-16 | P-REVIEW | 隔夜外盘 | 已建 |
| P-REVIEW-AUTO-17 | P-REVIEW | 明日预案 | 已建 |
| P-REVIEW-AUTO-18 | P-REVIEW | 📜 今日战报 | 已建 |
| P-SCREENER-AUTO-01 | P-SCREENER | ① 选股宇宙 | 已建 |
| P-SCREENER-AUTO-02 | P-SCREENER | ② 添加条件 | 已建 |
| P-SCREENER-AUTO-03 | P-SCREENER | ③ 条件列表 OR ▾ | 已建 |
| P-SCREENER-AUTO-04 | P-SCREENER | 条件面板 | 已建 |
| P-SCREENER-AUTO-05 | P-SCREENER | 选股结果 | 已建 |
| P-SECTOR-AUTO-01 | P-SECTOR | 成分股全表 | 已建 |
| P-SECTOR-AUTO-02 | P-SECTOR | 板块资金流历史 | 已建 |
| P-SECTOR-AUTO-03 | P-SECTOR | 板块舆情 | 已建 |
| P-SECTOR-AUTO-04 | P-SECTOR | 相对强度光谱地图 当前：领涨视角 | 已建 |
| P-SECTOR-AUTO-05 | P-SECTOR | 抗跌榜 | 已建 |
| P-SECTOR-AUTO-06 | P-SECTOR | 领涨榜 | 已建 |
| P-SECTOR-AUTO-07 | P-SECTOR | 证据链 · 怎么算出"资金去了哪" | 已建 |
| P-SECTOR-AUTO-08 | P-SECTOR | 主线候选 Top10 | 已建 |
| P-SECTOR-AUTO-09 | P-SECTOR | 产业链联动日报 | 已建 |
| P-SECTOR-AUTO-10 | P-SECTOR | 主线候选 Top 10 | 已建 |
| P-SECTOR-AUTO-11 | P-SECTOR | 板块梯队明细 | 已建 |
| P-SECTOR-AUTO-12 | P-SECTOR | 板块档案下钻 | 已建 |
| P-SECTOR-AUTO-13 | P-SECTOR | 大盘分时贡献度拆解 | 已建 |
| P-SECTOR-AUTO-14 | P-SECTOR | 分钟级逆势上涨 | 已建 |
| P-SECTOR-AUTO-15 | P-SECTOR | 下跌段资金流入 | 已建 |
| P-SECTOR-AUTO-16 | P-SECTOR | 率先反弹 | 已建 |
| P-SECTOR-AUTO-17 | P-SECTOR | 最抗跌 | 已建 |
| P-SECTOR-AUTO-18 | P-SECTOR | 盘后板块总结 | 已建 |
| P-SENTIMENT-AUTO-01 | P-SENTIMENT | 涨停强度 · 今 vs 昨 | 已建 |
| P-SENTIMENT-AUTO-02 | P-SENTIMENT | 涨停质量三维 | 已建 |
| P-SENTIMENT-AUTO-03 | P-SENTIMENT | 连板天梯 | 已建 |
| P-SENTIMENT-AUTO-04 | P-SENTIMENT | 市场宽度 | 已建 |
| P-SENTIMENT-AUTO-05 | P-SENTIMENT | 两融情绪 | 已建 |
| P-SENTIMENT-AUTO-06 | P-SENTIMENT | 情绪是怎么算出来的 · 构成因子 | 已建 |
| P-SENTIMENT-AUTO-07 | P-SENTIMENT | 情绪运行阶段 | 已建 |
| P-SENTIMENT-AUTO-08 | P-SENTIMENT | 涨跌停全景 | 已建 |
| P-SENTIMENT-AUTO-09 | P-SENTIMENT | 情绪温度 · 近 20 日时序 | 已建 |
| P-SENTIMENT-AUTO-10 | P-SENTIMENT | 市场宽度 · 近 20 日时序 | 已建 |
| P-SENTIMENT-AUTO-11 | P-SENTIMENT | 盘中异动流 | 已建 |
| P-STOCK-AUTO-01 | P-STOCK | 档案头 | 已建 |
| P-STOCK-AUTO-02 | P-STOCK | 行情边界 | 已建 |
| P-STOCK-AUTO-03 | P-STOCK | 前十大股东 | 已建 |
| P-STOCK-AUTO-04 | P-STOCK | 董监高 | 已建 |
| P-STOCK-AUTO-05 | P-STOCK | 财务概况 | 已建 |
| P-STOCK-AUTO-06 | P-STOCK | 筹码与股东户数 | 已建 |
| P-STOCK-AUTO-07 | P-STOCK | 主营构成 + 同行比较 | 已建 |
| P-STOCK-AUTO-08 | P-STOCK | 资金流向 | 已建 |
| P-STOCK-AUTO-09 | P-STOCK | 近期公告 | 已建 |
| P-STOCK-AUTO-10 | P-STOCK | 研报评级 | 已建 |
| P-STOCK-AUTO-11 | P-STOCK | 关联跳转 | 已建 |
| P-STRATEGY-AUTO-01 | P-STRATEGY | 策略看板 | 已建 |
| P-STRATEGY-AUTO-02 | P-STRATEGY | 当前框架状态 | 已建 |
| P-STRATEGY-AUTO-03 | P-STRATEGY | regime 适用性核对 | 已建 |
| P-STRATEGY-AUTO-04 | P-STRATEGY | 主线龙头回踩 | 已建 |
| P-SYSSTATUS-AUTO-01 | P-SYSSTATUS | 10 层数据分布 | 已建 |
| P-SYSSTATUS-AUTO-02 | P-SYSSTATUS | 已知问题 | 已建 |
| P-SYSSTATUS-AUTO-03 | P-SYSSTATUS | 调度时段 | 已建 |
| P-SYSSTATUS-AUTO-04 | P-SYSSTATUS | 券商连接 | 已建 |
| P-SYSSTATUS-AUTO-05 | P-SYSSTATUS | 熔断开关（Kill Switch） | 已建 |
| P-SYSSTATUS-AUTO-06 | P-SYSSTATUS | QMT 文件桥健康 | 已建 |
| P-SYSSTATUS-AUTO-07 | P-SYSSTATUS | 备份健康 Backup Health | 已建 |
| P-SYSSTATUS-AUTO-08 | P-SYSSTATUS | 性能监控 | 已建 |
| P-SYSSTATUS-AUTO-09 | P-SYSSTATUS | 资源水位 | 已建 |
| P-T0-AUTO-01 | P-T0 | 近 20 日命中率趋势 | 已建 |
| P-T0-AUTO-02 | P-T0 | 分桶校准 | 已建 |
| P-T0-AUTO-03 | P-T0 | 今日做T信号回验 | 已建 |
| P-TASK-AUTO-01 | P-TASK | 各阶段进度（现有内容保留） | 已建 |
| P-TASK-AUTO-02 | P-TASK | 最近完成 | 已建 |
| P-TASK-AUTO-03 | P-TASK | 失败任务 | 已建 |
| P-TASK-AUTO-04 | P-TASK | 全量任务清单 | 已建 |
| P-TASK-AUTO-05 | P-TASK | 长任务进度 | 已建 |
| P-WARROOM-AUTO-01 | P-WARROOM | 校准度 · 概率分桶 vs 实际命中率 | 已建 |
| P-WARROOM-AUTO-02 | P-WARROOM | W2 明日情景矩阵 3×3 | 已建 |
| P-WARROOM-AUTO-03 | P-WARROOM | 实时情景跟踪 | 已建 |
| P-WARROOM-AUTO-04 | P-WARROOM | 明日推演 | 已建 |
| P-WARROOM-AUTO-05 | P-WARROOM | 四指数状态 | 已建 |
| P-WARROOM-AUTO-06 | P-WARROOM | W2b 持仓股明日边界 | 已建 |
| P-WARROOM-AUTO-07 | P-WARROOM | W3 开盘观察哨 | 已建 |
| P-WARROOM-AUTO-08 | P-WARROOM | 打板实时监控 | 已建 |
| P-WARROOM-AUTO-09 | P-WARROOM | W0 昨日预案验证 | 已建 |
| P-WARROOM-AUTO-10 | P-WARROOM | W4 多空辩论台 | 已建 |
| P-WARROOM-AUTO-11 | P-WARROOM | 多头研究员 | 已建 |
| P-WARROOM-AUTO-12 | P-WARROOM | 空头研究员 | 已建 |
| P-WARROOM-AUTO-13 | P-WARROOM | 交易员综合 | 已建 |
| P-WARROOM-AUTO-14 | P-WARROOM | 风控官 | 已建 |
| P-WARROOM-AUTO-15 | P-WARROOM | W5 风险预算表 | 已建 |
| P-WARROOM-AUTO-16 | P-WARROOM | 预算分配 | 已建 |
| P-WARROOM-AUTO-17 | P-WARROOM | ⚔ 纪律铁律 | 已建 |
| P-WARROOM-AUTO-18 | P-WARROOM | 系统审计日志 | 已建 |

## B. 后端有 → 前端没有（1 项：has_frontend=yes/planned 但 frontend_ref 空）

| 模块 | has_frontend | 说明 |
|---|---|---|
| MOD-SIG-110 | yes | 声明有前端但未挂功能点 |

## C. 悬空引用（0 项：frontend_ref 指向 frontend_map 不存在的功能点）

| 模块 | 悬空引用 |
|---|---|

## D. 对账异常（0 项：has_frontend=no 但未填理由）


## 统计

- frontend_map 功能点总数: 319
- depgraph 已声明前端覆盖模块数: 20
- A/B/C/D 四类缺口: 318 / 1 / 0 / 0
