---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——回测数据装配器
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：回测数据装配器（B04）

- 状态: **已审**
- 级别: P1｜类型: 数据装配
- 基线 commit: 2fa92002c3（对象文件基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/backtest/core/data_handler.py:68`（BacktestDataHandler）；:496（MultiSourceDataHandler）
- 生产调用方: **零**（grep 全仓 src/：BacktestDataHandler/MultiSourceDataHandler 仅本文件自引；头注释声称 CONSUMERS=vectorized/event_driven 两引擎与事实不符——vectorized 自带 _get_day_* 取数、event_driven 走 TickReplayEngine）
- 测试文件: tests/backtest/test_data_handler_pit.py（存在；本报告未逐断言审——长尾登记）；头注释 [TESTS] 空
- 备注: —

## 1 对象快照

- 范围：BacktestDataHandler（bar 迭代/get_bar/get_history/PIT 财务 AS OF 合并/from_clickhouse）+ MultiSourceDataHandler（tick/batch 双源切换）。
- 排除项：ch_reader.inject_final 内部（引用不审）；pit_query.resolve_table 白名单（归数据域）。
- 材料包缺项声明：CH 真库表结构（daily_kline 是否存在）未实证——默认表名嫌疑只能静态判断；运行时证据包缺。
- 变更热力：20 commits，末次 2026-09-15。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| C | **孤儿死码（pattern #8）**：两类 Handler 生产调用方=0，模块头 CONSUMERS 声明（:5）与事实不符；整装回测不走此件。空转期间 PIT AS OF 合并、多源切换等能力零实战检验 | data_handler.py:5;grep BacktestDataHandler src/ 仅自身 | P2 | `grep -rn "BacktestDataHandler\|MultiSourceDataHandler" src/ --include="*.py" \| grep -v core/data_handler` |
| A | **PIT 财务 AS OF 合并多表冲突静默任意取版本**：多表 frame concat 后同 symbol-report_period 出现多行（income+balance 各一行，SELECT 只拉 eps 两列），tail(1) 按 sort(["symbol","report_period","announce_date"]) 稳定序取最后——跨表重复行谁最后谁赢，eps 相互矛盾时静默选错版本；report_period 跨表格式不一致时（"2024Q1" vs "20240331"）排序语义错乱 | data_handler.py:221-245,444-493 | P2 | 造两表同 symbol-period 不同 eps_basic 的 frame 传入 get_bar 看选中值 |
| A | announce_date 以**字符串**比较（`fund["announce_date"] <= date_str`，:217）：TSV 链路下 ISO 字符串字典序=时间序成立；但 DataFrame 模式调用方传 datetime64/Timestamp 列时与 str 比较行为随 pandas 版本漂移（隐式契约未文档化） | data_handler.py:214-217 | P3 | 传 announce_date=datetime64 的 fundamental_data 看比较是否生效 |
| B | from_clickhouse 默认 `table="daily_kline"` 裸字符串：全仓表注册走 get_registry().table()（对照 ch_tick_replay.py:47 用 "market_tick"），"daily_kline" 疑为不存在/漂移的表名——用默认参数即查空抛 DataHandlerError | data_handler.py:335,379-386 vs ch_tick_replay.py:47 | P3 | `grep -rn "daily_kline" src/zephyr/data/table_registry*` 对照注册表 |
| B | SQL f-string 拼接 symbols/table（:378,454）——内部受控输入，注入面低但违反参数化惯例（%(start)s 参数化只用于日期） | data_handler.py:377-386,454-461 | P3 | 代码审读 |
| A | MultiIndex 轴序隐式契约：本件假设 level0=date（get_bar xs(level=0)、get_history IndexSlice、symbols 属性 level=1）；vectorized_engine 同期支持 (date,symbol)/(symbol,date) 两序（vectorized_engine.py:529-541）——同仓两套取数器轴序契约不一致；错序时 symbols 属性静默返回日期集合=垃圾输出（get_bar 则 loud fail） | data_handler.py:183-189,267-270,279-284 | P3 | (symbol,date) 序面板调 .symbols 属性看返回 |
| B/E | PIT 财务可见性=announce_date<=当日（含当日）：盘后公告当日即可见，无 embargo 接线（pit_manager.apply_embargo 存在但本件未消费）；对 T+1 开盘成交链路无害（信号 T 收盘算、T+1 执行），对当日收盘前决策的分钟级策略是窄前视窗口 | data_handler.py:217;pit_manager.py:221-271（未接线） | P3 | Owner 裁定当日公告可见性口径（对照 pit_query 默认 embargo=0 的同族口径） |
| C | next_tick 返回裸单行 DataFrame（:715-730），无 TickSnapshot 构造——消费方需自行重造 _row_to_tick_snapshot 逻辑（与 tick_replay 重复职责，D 轴旁系第三份 tick 行处理） | data_handler.py:715-730 | P3 | grep next_tick 消费方（=0） |
| E | `_load_tick_data` 与 TickReplayEngine._load_and_merge_ticks 双份承载（同 sort_values("timestamp") 非稳定排序同病，见 B06） | data_handler.py:635-665 vs tick_replay.py:296-333 | P3 | diff 两方法 |
| A(亮点) | get_history PIT 语义正确（含当日回看）；from_clickhouse 走 DatabaseService 禁裸连接（宪法 §9.1 合规）；inject_final 按 #ARCH-CH-007 注入 | data_handler.py:247-270,36-49,388 | — | — |

## 3 SOTA 对照

- AS OF JOIN / PIT 财务数据合并：**对等已有**——announce_date 截止+版本对齐与 Dolt/feature-store 类 PIT 语义一致；多版本取最新可用版本实现正确（单表情形）。（来源：Purged K-Fold CV / PIT 语义面 paperswithbacktest.com, 2026）
- 双源数据处理器（tick+batch 统一接口）：**立卡候选**——类似 Nautilus 的多源 data engine 抽象，但本实现零消费方，建议先裁决去留再谈对标。（来源：NautilusTrader docs, nautilustrader.io, 2026）

## 4 缺陷清单

1. **[P2] 孤儿死码+声明失实**：两类 Handler 零生产调用方，头注释 CONSUMERS 失真。建议修法：要么接线（整装回测收编 _get_day_* 为 get_bar 路径），要么退役登记（规范预算净零）；最少改头注释如实声明。验证法：§2 轴C。
2. **[P2] 多表 PIT 版本冲突静默任意取**：建议修法：concat 前加表名列，tail(1) 改按 (announce_date, 表优先级) 稳定 tie-break，或同 symbol-period 多表冲突时 warn。验证法：§2 轴A。
3. **[P3] 默认表名 "daily_kline" 漂移嫌疑/SQL 拼接/轴序契约不一致/当日公告无 embargo**：逐条见 §2。

## 5 挂起疑问

- "daily_kline" 在 CH 是否真实存在（决定 P3 还是 P2）——需 CH 侧实证（本环境不可达）。
- 本件与 vectorized 内嵌取数（_get_day_field）职责重叠：合并方向需 Owner 裁定（先修孤儿状态再议）。

## 6 完备性自评

六轴全查。长尾：①test_data_handler_pit.py 逐断言审未做；②CH 真库表名/表结构实证缺；③fundamental_data 在真实财务表（eps 列是否全表齐备）上的画像缺。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
