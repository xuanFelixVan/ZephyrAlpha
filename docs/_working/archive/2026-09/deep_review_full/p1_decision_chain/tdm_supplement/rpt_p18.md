---
ttl: task_bound
title: 深度审查作业簿——扩散指标进度追踪（已审）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：扩散指标进度追踪（P18）— GLM-5.3-Flash / st-deeprev-20260918

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash/st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/adjustment_cycle_tracker.py`
- TDM 节点: TDM-E-L2-03-1
- 生产调用方: **零真实调用方**（全仓 grep 仅 core/analysis_utils.py 注释级引用；CONSUMERS"待 BM-BUY-04"未接线）——孤儿。注意 MATURITY 标 **production** 与零调用矛盾
- 测试文件: tests/signal_ashare/test_adjustment_cycle_tracker.py（27 passed）

## 1 对象快照
MOD-SIG-040 扩展（401 行）：市场级调整周期追踪（自动找峰+三维进度+相位门控）+ C6 扩散指标进度（站上 20 日线占比交叉信号）。计算/loader 分离。测试 27 passed。

## 2 六轴审查日志表
| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 找峰（trailing lookback，并列取最早）正确；最大回撤 running-peak 算法正确；COMPLETE 判定（新高+曾有≥5%回撤）语义自洽；confidence=0.4 样本因子+0.6 clarity 声明与实现一致 | :128-136,168-185,221-222 | 已查无 | 手算 V 型序列对拍 |
| A 深度 | `prev_peak = max(closes[start:-1])`（:178）排除末元素——若峰恰在 n-2 且当前 n-1 微跌，at_new_high=False 正常；但 n-1=start（min_history 边界）时切片[start:-1] 为空 → max(空) ValueError——min_history=30 且 lookback=250 下 start=0，n-1>start 恒真，实际不可达（守卫 :178 有 `if n-1>start else peak_close`，实现含守卫——已查无） | :178 | 已查无 | n=min_history 边界跑 |
| A 边界 | nh 序列长度不一致 fail-closed；扩散占比 NaN（r!=r）/越界 fail-closed（:384 r!=r 防御到位——族内最佳实践）；空序列拒 | :158-159,379-385 | 已查无 | 传 NaN 占比应抛 |
| A 深度 | 交叉信号只认"首谷/首峰"：窗口覆盖两轮调整周期时第二轮谷/峰信号不触发（两段式 next(first)）——长窗口复用场景漏检 | :388-401 | P3 | 造双谷序列看第二轮上穿不触发 |
| A A股 | 沪深300 代理（000300）；20 日线占比/30-50-80 带为项目裁量口径（C6 节点语义） | :71,310-316 | 已查无 | — |
| B 上游 | load_index_closes：TSV 逐行解析坏行 warning 跳过；**SQL f-string .format 插值 symbol/start/end**（与 P10/P15 的参数化 %(x)s 约定不一致，同仓两种 SQL 传参范式并存；本件值均内部默认故风险低，但 symbol 可由调用方注入=注入面） | :81-86,271 | P3 | 读 SQL 模板与 P10 SQL_LHB 对比 |
| C 下游 | **孤儿**：grep 全仓无真实 import（analysis_utils 为注释引用）；BM-BUY-04 市场级门控未接线——MATURITY=production 失真（checklist #8：空转+状态标错双犯） | grep 实证；:7 | **P2** | `grep -rln "AdjustmentCycleTracker\|track_adjustment_cycle" --include="*.py" src/ scripts/` |
| D 旁系 | 与 sector_adjustment 公式同源复用（import compute_adjustment_progress，不重复实现——正例）；扩散维缺省时 0.4:0.3 重归一声明与实现一致 | :46-51,208-211 | 已查无 | 对读两件 |
| E 对抗 | 五问：①loader 坏行降级 warning（好）②NO_ADJUSTMENT→EARLY 相位跳变无迟滞（drawdown 在 5% 邻域抖动→相位翻转，无确认天数——P16 whipsaw 防抖在此缺席，P3）③无监控面（孤儿）④纯函数幂等（loader 每次读库）⑤无时序面 | :186-191 | P3 | 造回撤 4.9%/5.1% 交替序列看相位抖动 |
| F 新鲜度 | 受阻/不适用：扩散指标（% above MA20）为经典 breadth 指标变体（Investopedia/AAII 有标准定义）——本批未做独立检索，如实记受阻；项目 C6 带阈值（30/50/80）为裁量参数 | — | — | — |

## 3 SOTA 对照
受阻（% above moving average breadth 定义业界标准，本批未检索；项目带阈值为裁量）。

## 4 缺陷清单
1. **P2 孤儿+MATURITY 失真**：production 标签与零调用方矛盾（建议降 testing 或接线）。验证法：grep。
2. P3 相位判定无迟滞（5% 门槛邻域抖动无确认机制，对比 P16 whipsaw 设计）。
3. P3 SQL .format 插值范式不一致（低危注入面）。
4. P3 双周期窗口首谷/首峰漏检。

## 5 挂起疑问
- 扩散序列注入源"板块广度链路"未见落码——nh_ratios 常态 None 时广度维退化为重归一（声明友好），但 C6 节点（TDM-E-L2-03-1）的核心扩散信号实际无数据源，需 Owner 定注入方。

## 6 完备性自评
六轴全查。长尾：market_index_kline 表数据质量未画像（孤儿降义）。
