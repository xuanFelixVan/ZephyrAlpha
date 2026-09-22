---
ttl: task_bound
completes_when: 整装回测首跑全链闭环（协议v1冻结→首跑→红蓝两轮0→交付报告在盘）
session: st-integrated-bt-20260922
issue: IBT-CAMPAIGN-001
---

# 整装回测首跑战役台账（st-integrated-bt-20260922）

目标：项目史第一次**协议治理下的**整装回测落地并过红蓝（组合层+个股层、成本/前视/T+1/PIT 全部红证）+进模拟盘准入判定。

## 0. 边界与避让

- 写域：`docs/_working/integrated_backtest/**` + 回测配置/脚本（.runtime/tmp 过渡）
- 不碰：scripts/ch、scripts/backup、disk_reorg_campaign（乙域）；daily_loop_campaign 只读（丁域）
- fw_backtest.py/framework_composer.py = 他会话在途件（MM 态）——**只读消费，禁修改**
- 时窗板：今日（09-22）无 active 声明窗；避开 02:30 tilib 夜跑带做重查询
- 不接实盘不下单；CH 只读探针走 DatabaseService

## 1. 真源吸收结论（§2 完成，2026-09-22 00:5x）

| 真源 | 关键结论 |
|---|---|
| fullflow_campaign | "整装回测"=fw/S11 链：framework_composer（唯一执行引擎）+fw_backtest.py（CLI `python -m zephyr.strategy_pipeline.fw_backtest run`，断桥③）；09-16 有一次 auto_mount 管道烟测（-18.5%，无协议无红蓝，不算正式首跑）；六向尺子②向从未真跑过回测引擎本体 |
| archive/2026-09 | TDM 回测协议 V0（TDMAP-001）：成本=CST-ASTOCK-001 实盘档（做T 另 CST-T0-001）；fill 三档敏感性；holdout 铁律=最近 12 月保密考卷、定稿锚 D=2026-09-09、定稿前不许跑回测；G4 无棘轮/无配对→强制折扣标注；窗口 B+C 混合 |
| data_fix_campaign | 数据地基：kline_daily 1990 起绿（复权走 D0=ex_dividend_event JOIN）；kline_daily_hfq 2019 起绿（5221 标的）；TI 143 族 2021-01 起可信；tick 2025-01 起 6 日永缺（做T 链已终结不消费）；600016 复权事件缺+老股深史 0.2-0.4% 偏差=登记级尾款 |
| 策略资产 | E4 存活 17 条（观察档，#326 冻结：C4 翻译件前视/幸存者污染未修）；死刑 2 条（FACT-4db4c41e beta 伪装、CAND-e2e7f033d97c 运气候选）组队时剔除；稳健组队口径 Sharpe 1.381（8d00/c4ec/e3da/4440）；卡1/卡2 均 FAIL 且 OOS 已烧禁重跑（只复用代码件） |
| trading_vision | 四层级联：L1 regime 厚（regime_snapshot_history 2019-04 起可回放，PIT 读法=trade_date<t 最近行；r4/r10 方向失真 caveat）；L2 板块薄（gate=stub→如实降级）；L3 个股=E4 队；L4 组合=compose_weight_panels（支持 regime 逐日查表） |
| 引擎 | DefaultBacktestEngine（向量化日频）：execution_lag_days=1 硬断言+开盘优先成交+PIT 池过滤+流动性约束+护栏全内建；面板行 t 用 ≤t 信息+T+1 执行=PIT 安全 |

## 2. 战役进度

- [x] §1 冷启动（reaper 活/心跳 daemon PID 21824/会话注册）
- [x] §2 真源读序（4 只读代理并行吸收）
- [x] 分包1① 数据完备性矩阵（ibt_data_matrix.yaml + IBT-DATA-MATRIX.md；无阻断缺口；FACT 族 IS 生效起点后移 2021-04）
- [x] 分包1② 首跑协议 v1 冻结（IBT-PROTOCOL-V1.md，frozen 2026-09-22T01:05）
- [x] 烟测：W_POSTD 8 日全链通（合成 9 参与/引擎/成交/护栏空跑拦截全正常；Sharpe=0 系样本<60 设计行为）
- [ ] 分包2 首跑（W_IS → W_OOS+敏感性 → W_HOLDOUT 单次 → W_POSTD 已跑）
- [ ] 分包3 红蓝四向（连续两轮 0）
- [ ] §6 收官

## 3. 批次记录（append-only）

| ts | 批 | 动作 | 结果 |
|---|---|---|---|
| 00:31 | 冷启动 | PATH/reaper/注册/心跳 | 7 死锁清理，daemon 21824 |
| 00:5x | 真源 | 4 代理并行吸收+CH 探针 | 见 §1 |
| 01:0x | 分包1 | 矩阵挖掘 279s + 协议冻结 | FACT 起点=2021-04 处置；7 文件 token 落册 |
| 01:0x | 烟测 | W_POSTD 全链 8 日 | 通过（B≡A 因全 r3 满配，正常） |
| 00:58+ | 分包2 | W_IS 正式跑 | 在飞 |
| 01:16 | 缺陷 | **FACT 面板符号带后缀（000002.SZ）vs 引擎 data 裸码 → FACT 六 sleeve 全程不可成交死权重**（首版 IBT-A +3.77%/IBT-B -12.32% 系缺 FACT 版本，作废） | 杀批+runner 补符号归一（split('.')[0]）+清面板缓存重跑；W_POSTD 烟测版同病，待终批重跑 |
| 01:25-02:40 | 分包2 | W_IS 终版重跑（1156 日/15 员/1667 标的） | IBT-A -12.14%/Sharpe -0.117/DD 35.3%；IBT-B -27.71%（节流三窗皆负）；15 员单跑全落盘 |
| 02:43-03:00 | 分包2 | W_OOS+敏感性 | IBT-A +11.93%/Sharpe 0.336/DD 16.0%（基准 000300 +31.9%）；敏感五档 0.475→-1.226 严格单调 |
| 03:02-03:10 | 缺陷 | OOS 敏感性跨批重算 sharpe 漂移（02:30 夜跑带推进 hfq 表） | 同批六档全量重算定稿（zero_cost 0.837 严格最优） |
| 03:10-03:20 | 分包2 | W_HOLDOUT 保密考卷单次烧毁 | **IBT-A -12.24%/Sharpe -1.389**（C 门不过）；成员 4/15 微正 |
| 03:20-03:29 | 分包2 | W_POSTD 终版 | -2.14%/194 笔（符号修复生效：73→194 笔） |
| 03:30-03:56 | 分包3 | 红蓝 round1（W_OOS） | **8/8 PASS red=0**（前视 lag0 raise/行内位移注入 +0.072/T+1 审计 13935 fills 0 违例/regime PIT 键 1565 全合规/退市注入被剔/成本单调/零成本最优） |
| 03:56-04:22 | 分包3 | 红蓝 round2（W_IS） | 6/7 PASS +1 RED=W_IS 敏感性缺件（覆盖面非防线） |
| 04:22+ | 分包3 | W_IS 敏感性补跑→round3/4 连续两轮 0 | 在飞 |
| 04:22-05:3x | 分包3 | W_IS 敏感性补跑（六档同批） | 0bp -0.114→40bp -2.308 严格单调；零成本 Sharpe 0.248/ret +26.5%（成本拖累 38.6pct 实锤） |
| 05:0x-06:0x | 分包3 | 红蓝 round3（W_IS）+round4（W_OOS） | **8/8+8/8 全 PASS，连续两轮 0，红蓝闭环** |
| 05:48 | 收官 | enqueue q-0001（39 件） | 死于 DIRECTORY-CONTRACT：docs/_working 禁 .json（DCR-005/008，36 发现） |
| 06:0x | 收官 | json 迁址 data/backtest_artifacts/ibt-20260922/+报告路径同步+enqueue q-0002（38 件） | 在 serializer 链中（worktree 已展开）；另：ulib2 挂死提交进程占 lease 2.4h 阻塞全队列，机械判死（CPU 双采样零增长+超时 48 倍）后 taskkill 解锁 |
