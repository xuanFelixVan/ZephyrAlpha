---
ttl: task_bound
---

# 图形库缺数据补扫 · 159 条清册与归因（st-bizmine-pb-20260919）

> 数据锚点：prereview.csv（P 车道 dbdef721，commit 3f01d058ea，2026-09-17）图形库段 verdict=缺数据 共 159 条；
> 真源表=c1_market.market_pattern_event（本会话查询时点 2026-09-19 ~05:3x UTC+8 前）；注册表真源=REG-PAT-001
> chart_pattern_registry.yaml（287 条）。配套明细=同目录 pattern_backfill_inventory.csv（159 行全字段）。

## 1. 一句话结论

159 条"缺数据"中 **26 条系预审误判**（英文名/entry_id 与表内中文名、TA-Lib 截断名映射断链——表内实际已有 2021-09 起全窗数据，
可直接进考试）；**5 条为真·可补扫**（检测器在、历史未跑）；**32 条为数据债**（非日线 timeframe，源数据不可达）；
**96 条待查**（注册表有定义、引擎无检测器，含 8 个 DL 套件）；**3 条部分覆盖**（有数据但密度/窗口存疑）。
"引擎没跑过历史"的病根经查**已在 2026-09-13 修复过一轮**（scan_run_id=pb-2021-09-01-2026-09-13 全窗回填 219 万行），
剩余缺口主因是**名称映射断链**与**检测器未实现**，而非引擎未跑。

## 2. 归因计数（159 = 23+3+5+32+96）

| 归因 | 条数 | 判定依据 |
|------|------|----------|
| 已覆盖（预审误判） | 23 | 映射到表内形态名，行数≥500 且最早锚日≤2021-12-31（全窗在库） |
| 部分覆盖 | 3 | 有数据但单行/密度/映射近似存疑（CDL3STARSINSOUTH 仅 1 行；缠论向下笔 2022-03 才起；压力位作 Breakout Failure 近似） |
| (a) 可补扫 | 5 | 检测器在（candlestick_scanner extras 078..083 批），但仅 2026-08-31 起增量 15 日窗数据，历史未跑 |
| (b) 数据债 | 32 | 注册表 timeframe=intraday/weekly 非日线（分钟线 2021-09 起、分时盘口/成分快照缺） |
| (c) 待查 | 96 | 注册表有定义、market_pattern_event 写入链无对应检测器（引擎缺实现） |

## 3. (a) 可补扫 5 条（本车道任务 B 对象；补扫覆盖含表内 PAT-CANDLE-078 内包日等全部 98 名）

| entry_id | 英文名 | 表内名 | 现状 |
|----------|--------|--------|------|
| PAT-CANDLE-079 | Weekly Reversals | 周线反转 | 13777 行，仅 2026-08-31..09-18 |
| PAT-CANDLE-080 | Open-Close Reversal | 开收反转 | 4718 行，同窗 |
| PAT-CANDLE-081 | Hook Reversal | 钩形反转 | 8111 行，同窗 |
| PAT-CANDLE-082 | Pivot Point Reversal | 枢轴点反转 | 7967 行，同窗 |
| PAT-CANDLE-083 | Shark-32 | 鲨鱼32 | 140 行，同窗 |

病因：六名（含 PAT-CANDLE-078 内包日 22108 行）属扫描器 09-13 全窗回填**之后**新增的 Bulkowski 小形态批
（078..083），增量任务每轮只产出 --emit-from=now-15d 窗口，历史段从未扫过 → 重跑全窗回填即可补齐。

## 4. 预审误判 23+3 条（建议 P 车道/考试方直接按表内名取数考试）

candlestick 11+1：Three-Line Strike→CDL3LINESTRIKE(9766)、Stick Sandwich(5462)、Stalled(11205)、
Rising/Falling Three Methods→CDLRISEFALL3METHODS(1949)、Long Line(1242638)、Tweezer Bottom→镊子底(704066)、
Key Reversal→关键反转日(1411813)、Oops→Oops跳空反向陷阱(471473)、Three Gaps→三空(29027)、
Tower Top/Bottom→塔形顶(364069)/塔形底(292427)、NR7→窄幅整理日(1143161)、
Three Stars in the South→CDL3STARSINSOUTH(仅1行,部分)。
chart/structure 7：Double Top→双顶(767805)、Big W→双底、Big M→双顶、Adam&Eve→双底、Wedge Breakdown→上升楔形(56764)、
Wyckoff Upthrust 近似双顶对偶等 4 条 structure 经别名落双顶/双底族。
chanlun 2：Upward Bi→缠论向上笔(8711)、Downward Bi→缠论向下笔(11628,部分)。
support_resistance 1：Breakout Failure→压力位(25632,近似映射,部分)。

映射断链三类技术成因：①注册表 zh 与表名同义不同词（双头/双顶、上升笔/向上笔）；②TA-Lib 官方函数名截断/保留介词
（LINESTRIKE、HIKKAKEMOD、3STARSINSOUTH、XSIDEGAP3METHODS）；③扫描器 extras 批 PAT-CANDLE-062..083 中文直名未进映射表。

## 5. (b) 数据债 32 条（今日不施工，登记缺口）

structure 22（Wyckoff 分时判读/SMC 订单流/ORB/盘口 9 件套等）+ support_resistance 7（Intraday Breakout/Stop、
Pivot Points 经典/斐波、前日高低、Murrey、Camarilla）+ chart_pattern 3（Broken Board Re-Seal、Late-Day Sneak Board、
Brooks H2/L2）。共性=注册表 timeframe 非日线，依赖 1 分钟线（2021-09 起）或 tick/盘口（tick_depth_5 仅近期）/
成分快照（仅 2 天）。补齐需分钟级引擎施工+源数据扩窗，属数据平台债。

## 6. (c) 待查 96 条（引擎缺检测器，非本车道可补）

chart_pattern 48（旗形/杯柄/V形/岛反/死猫跳/反包涨停/双响炮/黄金坑/TD 序列/Wolfe/Quasimodo/扇贝/牛角/量度移动等——
多为 rule_based/regression 定义但无 market_pattern_event 生产者）+ structure 31（Wyckoff 文本 5/SMC 9/VSA 7/
MatrixProfile 2/量学 2/供需区等）+ trendline_channel 8（通道 3/金叉死叉/速度阻力线/江恩摆动/均线排列）+
chanlun 6（顶底分型/三类买卖点/趋势·盘整背驰——引擎仅产出中枢与笔，分型与买卖点未单列）+
support_resistance 2（Volume Profile、Murrey 日线版）+ candlestick 1（Side-by-side White Lines：扫描器全窗已跑、
零事件）+ PAT-DL 套件 8（YOLOv8/多模态 LLM/扩散/Chart-RVR/VLM/GAF-CNN/ElliottAgents/wave-alpha——研究型，无落地检测器）。

## 7. 补扫执行（任务 B）与考后登记

- **执行结果（2026-09-19 收口，详见同目录 pattern_backfill_execution.md）**：试扫 1 年×500 股（427,775 事件/0 错误）
  放行后全窗 `pb-2021-09-01-2026-09-19` 扫 5,766 股、写 24,428,254 事件、0 错误、42 分钟。
  六名（含表内 PAT-CANDLE-078 内包日）全部回到 2021-09 全窗：内包日 826,259 行/周线反转 566,645/钩形反转 377,335/
  枢轴点反转 312,048/开收反转 217,819/鲨鱼32 6,330。清册 CSV 已加 backfill_status 列（5 条=backfilled）。
- 快考（筛≠考）：开收反转/向上（ex10=+29.6bp、分年 6/6 正、高波桶 +50.3）与枢轴点反转/向下（+20.8bp、6/6 正）
  为首轮亮点；毛口径 close 锚未计成本，正考须走 PATX 窄考卡协议（T+1 开盘+成本+NW/bootstrap）。
- 验收：补后按 name 六名最早锚日均回到 2021-09/2022 段 ✓；生产表只 append（ReplacingMergeTree 幂等）✓。

## 8. 复现

- 覆盖查询/归因脚本：.runtime/tmp/bizmine/pb/build_inventory.py（读 prereview+REG-PAT-001+coverage_by_name.csv）。
- coverage_by_name.csv=market_pattern_event GROUP BY name 全量快照（本会话产出）。
- 表内形态名全集=104（引擎 21 名+K 线扫描 77 名+增量窗新名）；注册表 287 条 → 未物化 183 条为 §5/§6 主体。
