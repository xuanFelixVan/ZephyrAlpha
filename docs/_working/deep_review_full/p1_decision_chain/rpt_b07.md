---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——CH Tick重放器
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：CH Tick重放器（B07）

- 状态: **已审**
- 级别: P1｜类型: 数据适配器
- 基线 commit: 2fa92002c3（对象文件基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/backtest/implementations/ch_tick_replay.py:60`（fetch_historical）
- 生产调用方: frontend/dashboard/app_panel.py、frontend/dashboard/components/tick_replay.py（tick 回放可视化）；event_driven 经 provider 注入点鸭子类型消费
- 测试文件: tests/zephyr/backtest/test_ch_tick_replay.py（102 行 5 测试，CH 全 mock，覆盖 SQL 形态/列契约/异常转换/鸭子类型签名——本批运行批全绿）
- 备注: miniQMT 退役（2026-09-18）后的 tick 断供替补件

## 1 对象快照

- 范围：fetch_historical（SQL 直取 c1_market.tick_data + 1 档→5 档降级填充 + 列契约对齐）。
- 排除项：tick_data 表入仓链路（miniqmt 囤货/qmt_bridge 归数据域）；TickReplayEngine 消费端（B06）。
- 材料包缺项声明：CH 真库连通性未实证（本环境 CH 不可达）——SQL 正确性仅静态+mock 审。
- 变更热力：1 commit（2026-09-10 一次性落地，未返工——新件低热力）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **OHLC/prev_close 全部伪造=last_price**（:124-127）：open=high=low=prev_close=last_price。1 档降级已在 docstring 如实登记，但 **prev_close 语义破坏未披露**——做T策略若消费 tick_data.prev_close 算涨速/涨跌幅→恒 0→信号静默退化；对照撮合侧 tick 模式不用 prev_close（暂无爆炸），但这是埋给策略层的静默陷阱 | ch_tick_replay.py:124-127 vs 模块 docstring:23-27（只登记 1 档降级未提 OHLC 伪造） | P2 | callback 里读 event.tick_data.prev_close 打日志看恒等于 last_price |
| A | **1 档降级→tick 撮合容量=单档 vol**：2-5 档填 0 后 matching_logic 逐档消化仅剩档 1 有效（零价档跳过），QMT 5 档时代同策略可成交量为 1/5——QMT 历史回测与 CH 回测同策略成交率/加权价不可比；降级已裁定登记（台账 §8.3.1 ①）但**无双源对账校验**（切源后回测结果变化无告警） | ch_tick_replay.py:116-121;matching_logic.py:483-491 | P2 | 同一策略日分别以 5 档 mock 与 1 档 mock 跑 run_tick 对比 trades |
| A | timestamp 以字符串直通（CH TSV 行未 parse datetime）：sort 靠字典序（ISO 格式碰巧正确）、TickEvent.timestamp=str 传入 Portfolio/账本（`_ledger_date_key` ISO 前缀归一兜住）——现链路成立但多层隐式契约叠加，脆 | ch_tick_replay.py:109-115（列直入 DF 无 to_datetime） vs tick_replay.py:329 | P3 | 静态审读；传非 ISO 时间格式数据看 sort 错序 |
| B | SQL 双约束（trade_date BETWEEN + toDateTime64 timestamp BETWEEN 'Asia/Shanghai' 显式时区）✓ 宪法 RULE-SCHEMA-TZ 合规；`price > 0` 过滤与引擎端 last_price<=0 跳过口径一致（双端防御一致） | ch_tick_replay.py:90-98 | 亮点 | — |
| B | 模块级 `get_registry().table("market_tick")`（:47）导入期副作用：registry 故障=import 即崩（fail-fast 可辩护，但 dashboard 面板 import 链被拖死） | ch_tick_replay.py:47 | P3 | 破坏 registry mock 看 import 行为 |
| B | symbol→裸码 split(".")[0] 无 zfill/白名单校验直拼 SQL（:83,93）——内部受控输入注入面低；QMT 形态约定靠 duck-type 测试锁定 ✓ | ch_tick_replay.py:83,93 | P3 | 传 "6" 看查询（空结果静默） |
| C | 消费方=dashboard 两处 + provider 注入点：CHBackfillReadError→TickReplayError 转换承诺需调用方捕（dashboard 是否捕未核，长尾） | ch_tick_replay.py:13,100-104 | P3 | grep dashboard 侧 except 链 |
| D | 与 MiniQmtQuoteProvider.fetch_historical 的 duck-type 契约有专测锁定（test_duck_type_matches_replay_engine_expectation）✓——接口等价性制度化，无双真源 | tests/zephyr/backtest/test_ch_tick_replay.py:86-102 | 亮点 | — |
| E | 空窗返回空 DF（TickReplayEngine 既有语义 warning+跳过）✓ 错误契约与消费方对齐（docstring :13 声明）；CH 异常转 CHBackfillReadError 不吞 ✓ | ch_tick_replay.py:13,106-107 | 通过 | test_ch_failure_raises_chbackfillreaderror |
| A.3 | 测试审查：5 测试断言 SQL 子串/列名/值——强度中上；缺口=OHLC 伪造只断言 open 未断言 prev_close/high/low（:76-77）；无真实 CH 集成 smoke | tests/zephyr/backtest/test_ch_tick_replay.py:56-77 | P3 | 补 prev_close 断言（勿动源） |

## 3 SOTA 对照

- 历史 tick 回放的 DB 直取代 replay SDK：**对等已有**——miniqmt 退役后 DB 直取是常规替补（对照 Nautilus 数据 catalog 惯例：历史数据与实时 SDK 解耦）。（来源：NautilusTrader docs, nautilustrader.io, 2026）
- 1 档降级如实登记：**对等已有（纪律项）**——"降级必须显影"与 A 股数据供应商多档分级现实一致；缺 prev_close 披露是登记不完整（见 §2 轴A）。（来源：SimTradeLab 等 A 股框架分档数据说明，github.com/topics/backtesting-engine, 2026）

## 4 缺陷清单

1. **[P2] prev_close 等 OHLC 伪造未披露**：建议修法：模块 docstring 补登记；或改填 NaN 强制消费方显式处理（优先，防静默退化信号）。验证法：§2 轴A。
2. **[P2] 双源容量不可比无对账**：建议修法：回测产物附"数据源+档位级别"字段（BacktestResult 或 artifact metrics），同策略跨源对比时可解释。验证法：§2 轴A。
3. **[P3] timestamp 字符串直通多层隐式契约**：建议修法：出口统一 pd.to_datetime。验证法：§2 轴A。
4. **[P3] import 期 registry 副作用、SQL 拼接、prev_close 断言缺口**。

## 5 挂起疑问

- tick_data 表在 CH 的实际覆盖（起止日期/连续性/停牌日有无行）未实证——1 档降级外的"数据断供=回放空转"风险依赖入仓链路健康（归数据域审计）。
- end 参数"当日则取当日全天"的边界（end 带 23:59 还是 00:00）对 BETWEEN 上界的实际影响未真库验证。

## 6 完备性自评

六轴全查。长尾：①CH 真库 smoke 未做（不可达）；②dashboard 消费链异常处理未逐行；③tick_data 入仓质量（qmt_bridge 侧）归数据域。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
