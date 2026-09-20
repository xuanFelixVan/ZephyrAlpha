---
ttl: task_bound
completes_when: 全部条目终态（done/作废/归 Owner）并随战役收官归档
session: st-unified-plan-20260920
issue: UNIFIED-CAMPAIGN-001-P2-LEDGER
---

# 包②交付·四路遗留总台账 v1.0（st-unified-plan-20260920，2026-09-20）

> 定位（裁定#378①）：**台账真源**——四路遗留全量逐行盘点，含 v0.1 丢失的 D 路历史悬账。每行=来源/事项/真源指针/依赖/状态（本日验活）/归属（线·波·派工单）/工量/门位。处方细节在 `p3_db_repair_master_plan_v1_0.md`（包③分立件），执行细节在 `p2_workorders_v1_0.md`，本台账只管"有什么、归谁、何时序"。执行日逐条复现验活再动手（报告是死的库是活的）。

## §0 状态图例与验活基准

状态列=2026-09-20 本班实测验活结果：`活`=复现属实待办｜`核销`=已落地有 commit 凭证｜`陈旧作废`=前提已消失｜`Owner`=等签字。工量为 Flash 分包估时（含红证+提交，不含排队窗口）。

## §1 A 路·数据审计遗留（dataqa 四报告为病历，19 条）

| # | 事项 | 真源指针 | 依赖 | 状态（09-20 验活） | 归属 | 工量 | 门位 |
|---|---|---|---|---|---|---|---|
| A1 | index_valuation_daily 派生列 100% NULL（8125/8125）+同键双行 132 组复发（P0） | dataqa R2 §2.1 行1+R4 P0-1 | 签字③选型 | **活** | 甲·W1·WO-1 | 1-2 天 | Owner（表结构变更） |
| A2 | daily_valuation 价格腿 27 万行全 0+09-19 周六污染+mock 假绿（P0） | R2 §2.1 行2/3+R4 P0-2 | A1 联动（同根多写者） | **活**（零值仍在活体增长） | 甲·W1·WO-1 | 1-2 天 | Owner（A1/A2/A3 选型随签字③） |
| A3 | tick 09-17 双通道全黑=永久缺口（QMT 退役+bdpan 07-03 停更双实证） | R4 P1-3 | 无 | **活**（登记+合成评估） | 甲·W3·WO-3 | 0.5 天 | Owner（合成案=签字⑩，默认只登记） |
| A4 | index_quote 09-16 停（IndexMinuteEOD 随 miniQMT 死） | R2 N4+R4 P1-2 | 无 | **活** | 甲·W2·WO-2 | 0.5-1 天 | — |
| A5 | news_sentiment_window 09-14 停（run_nightly_sentiment 静默失败） | R2 N5+R4 P1-4 | 无 | **活** | 甲·W2·WO-2 | 0.5 天 | — |
| A6 | auction 09-17 停（桥派生 WinError 10038+ch_writer 连接冷却实锤） | R2 N6+R4 P1-2 | 无 | **活** | 甲·W2·WO-2 | 0.5 天 | — |
| A7 | crypto_kline_daily 09-19 全断（7×24 资产） | R2 N7+R4 P1-2 | 无 | **活** | 甲·W2·WO-2 | 0.5 天 | — |
| A8 | stock_indicator 09-18 半日（1000/5565，周一盘前消费受影响） | R2 W2+R4 P1-5 | 无 | **活** | 甲·W2·WO-2 | 0.5 小时 | — |
| A9 | 哨兵盲区：4 表无阈值行+max-date 对内部洞原理性失明 | R2 §4 盲区+R4 P1-1 | 无 | **活** | 甲·W3·WO-3 | 0.5-1 天 | tasks.yaml 挂接随签字⑨ |
| A10 | technical_indicator parts 治理（dataqa 时 1339→**本日实测 1181**，夜跑崩溃新增风险） | R1 §3.1+R4 P1-6 | C-5 夜跑修复+dwm 停+parts 回落 | **活**（观察中） | 乙·W-并入·WO-6 | 观察窗+1 独占窗 | 乙线（CH 重 IO） |
| A11 | CH 内备份/污染表 35.4G（17 张清单 R1 §5；与包④ W1 尸体表同一物，12vs17 执行日实测仲裁） | R1 §5+包④ §2 | 签字①；R1 基线 | **活** | 乙·W1·WO-6 | 1 独占窗 | **Owner**（drop 破坏性） |
| A12 | 1970 假日期 18 表 43.6 万行（大头 restricted_shares 34.3 万） | R1 §4+R4 P2-4 | 签字② | **活** | 乙·W-并入·WO-6 | 0.5 独占窗 | **Owner** |
| A13 | 12 小表 parts 爆炸（写入端攒批+OPTIMIZE，清单 R1 §3.3） | R1 §3.3 | 无 | **活** | 乙·W-并入·WO-6（攒批写入端改造归甲·W3 顺手） | 0.5 天 | — |
| A14 | 77 表未登记 data_asset_registry（生成器口径重建禁手工） | R1 §7+R4 P2-6 | 无 | **活** | 丙·W2·WO-13（注册表域归丙） | 0.5 天 | — |
| A15 | known_data_gaps 8 条改册（含 etf 时区已执行改 completed；+convertible_bond_list 1970 补登记+W1 stock_basic 缺日扩条目+W4/W5 etf_list/index_list 存活行） | R2 §2.1/§3 | 无 | **活** | 甲·W3·WO-3 | 0.5 天 | — |
| A16 | 周末写入卡交易日 gate（sector_fund_flow+daily_valuation 两任务） | R2 W3+R4 P2-7 | A2 联动 | **活** | 甲·W1·WO-1（随 A2） | 0.5 天 | — |
| A17 | 测试真账 32 条（D38 三未登记库+decision_map R24 复发+governance 9 文件等） | R3 §2 A 类+R4 P2-1 | 无（final3 已收官，独立批） | **活** | 丙·W2·WO-13（裁定#379③） | 1-2 天 | — |
| A18 | 疑似真 bug 14 条（SCD2×4 优先；全路径 R3 §2 C 类表） | R3 §2 C 类 | 无 | **活** | 丙·W1·WO-12 | 2-3 天 | — |
| A19 | 注册表漂移清理（research_report hot_value 列消失+consensus_daily_repaired 部分回填改册） | R2 §2.1 行6/7 | 无 | **活** | 甲·W3·WO-3（与 A15 同批改册） | 0.5 天 | — |

## §2 B 路·final3/maxexec 遗留（核销为主，git log 本日复核）

| # | 事项 | 真源指针 | 状态 | 归属 |
|---|---|---|---|---|
| B1 | szopen 一页纸（A 组 6 补订阅+B 组 23 复制地址） | p14_owner_szopen_onepager.md（50fc0d0f） | **Owner 今晚自办**（战役外） | Owner |
| B2 | 死信 q-0040 ALGO-FLOW 断锚（decisiongraph_adapter.yaml 已删有锚） | x1_dead_letter_report+final3 §四 | **活** | 丙·W5·WO-16 R9 |
| B3 | P9 池 2 小件：.pre-commit-config+gate_registry 的 GATE-21 已知限制文案对（mutation 连环坑） | final3 §四.2 | **活** | 丙·W5·WO-16 R8 |
| B4 | W7 股权穿透底座（设计100/施工0/原料60——只出施工派工单不施工） | altdata_line 全目录 | **活** | 丙·W5·WO-16 R11 |
| B5 | T1/W8/p14/代裁/队列终态五族 | 00_master_plan_v1_0 §2 核销表 | **核销**（本日 git log 逐条复核通过） | — |

## §3 C 路·tilib 清欠班遗留（6 项，勘误丢失项归位）

| # | 事项 | 真源指针 | 状态 | 归属 | 工量 | 门位 |
|---|---|---|---|---|---|---|
| C1 | tilib 三件套主体（34 指标+注册表 138+测试 1079+批9 数据批） | tilib_clear_a5（3424a718e7..509db008fb） | **核销**（本日 git log 复核五 commit 全在 HEAD） | — | — | — |
| C2 | stock_daily_basic 每日增量挂 tasks.yaml（`scripts/data/backfill_stock_daily_basic.py --source tushare`） | 交接包 §3 批9 配方（**新路径** archive/2026-09/c_class_scattered/2026-09-15-tilib-handoff.md） | **活** | 甲·W4·WO-4 | 0.5 天 | **Owner**（tasks.yaml=签字⑨） |
| C3 | 批10 筹码族三件套 CYQ/SCR/CYC（chips_winner/chips_avg_cost/chips_cost_5/chips_cost_95+SCR 集中度+CYC 成本均线；注册表 138→141）；【扩项 2026-09-21 tc_10 挂接】+chips_cost_15/chips_cost_85 两列+CHIP_CONC_90/CHIP_CONC_70 两指标（70%/90% 集中度），计数目标=基线日实测+5（09-21 夜实测 138→145） | 交接包 §3 批10（新路径同上）+design_memos/16 号 memo+docs/_working/collection_intake/factors/factor_spec_chip_concentration.md（扩项真源，Owner 今夜范围令第1波回写） | **活**（原料 stock_daily_basic 705 万行已就绪） | 甲·W4·WO-4 | 1-2 天 | — |
| C4 | reversal.py 行1 [BLUEPRINT] 计数散文 stale+旧路径 token 残留（无害小尾巴） | tilib_clear_a5 §5 登记债① | **活** | 丙·W5·WO-16 R10（顺手批） | 0.5 小时 | — |
| C5 | 210 列夜跑验收核销——**2026-09-20 实测升级**：02:30 夜跑 04:03 因 CH Code 241（内存总闸 7.05GiB）阵亡，BufferedWriter 缓冲 132,834 行丢失（fallback 目录空壳实证），最新学术列 gp_pred/gp_sig/continuation_40/highpass_40/supersmoother_10 近月 0% 回填 | .runtime/tmp/tilib-probe/backfill_night.log 尾部+本班 CH 探针 | **活（活体断供）** | 甲·W2·WO-2（断供止血族）→ 验收核销归甲·W4 R15 | 0.5-1 天（重跑+回灌+验收） | — |
| C6 | D 盘水位治理（28G→29G 实测；4T 冷搬/退役决策） | 交接包遗留①+包④ §2 | **活** | 乙线全线（W1/W5/W6 各波分担） | 见乙指令 | Owner（签字④⑥⑧） |

## §4 D 路·历史悬账（v0.1 丢失项，验活归丙）

| # | 事项 | 真源指针 | 状态（09-20 实测） | 归属 | 工量 |
|---|---|---|---|---|---|
| D1 | staged 未提交件 **179 件**（包②原文记 189，本日实测 179；构成=pipeline-research/reports 17+final3 p6_shed_salvage 14+unified_campaign 4+rule_audit a2 4+disk_reorg 3+cold_backup 3+注册表 2+tilib 残留 MM 族+散件）——逐条判归属：已落地核销/真未落地评估入册 | `git diff --cached --name-only` | **活**（本批收编 6 件=unified_campaign 4+两注册表，余约 173；执行日以复测为准） | 丙·W4·WO-15 | 1 天 |
| D2 | 判定台账 42 行 pending（PG 查询） | forecast_ledger 体系 | **活**（执行日 PG 验活） | 丙·W4·WO-15 | 0.5 天 |
| D3 | backtest backlog 140 条 B0 决策 | backlog 台账 | **活**（抽验活死） | 丙·W4·WO-15 | 0.5 天 |
| D4 | 哨兵 allow_empty 白名单 12 表收口（BRK-046） | R2 §4 | **活** | 丙·W4·WO-15（与甲 W3 哨兵批对齐口径） | 0.5 天 |
| D5 | 死信稳态 62（61 历史留档+1 tilib 活件）+dead_purged_20260920/ 勿 requeue | x1_dead_letter_report | **稳态**（只读观察，新死信按纪律 requeue） | 各线自责 | — |

## §5 执行波次总览（与 00_master_plan_v1_0 §6 对齐；本表=台账视角）

波1（即刻）：WO-1（甲 P0，签字③未批先做无门位半）/WO-12（丙 bug）/WO-15（丙悬账，只读）∥乙 W2 方案
波2（闪断窗）：WO-5（乙 W2 重启）
波3（签字后独占窗）：WO-6（乙 W1+W-并入）
波4（W1 后解锁）：WO-4（甲 W4 tilib 延续批——批10+增量挂接+验收核销）
波5（第2-3天）：WO-2（甲断供止血含 C-5 夜跑修复）/WO-3（甲哨兵+改册）∥WO-13（丙测试真账+A14+A17）
波6：WO-14（丙包①归置）
波7（周末夜）：WO-7（乙 W3）→WO-8（乙 W4）→WO-9（乙 W5 滚动）
波8（Owner 在场）：WO-10（乙 W6 全局冻结）
波9（终局）：WO-11（乙 W7 五盘终验）+三线各自红蓝收官

## §6 验活复核命令（执行日重跑）

```bash
# A1/A2 P0 复现
python -c "import sys; sys.path.insert(0,'src'); from zephyr.infrastructure.database_service import get_db_service; c=get_db_service().get_clickhouse_conn(role='reader'); print(c.execute(\"SELECT countIf(cape_5y IS NULL), count() FROM c1_market.index_valuation_daily FINAL\"))"
# A10 TI parts
# SELECT count() FROM system.parts WHERE active AND table='technical_indicator'
# D1 staged 计数
git diff --cached --name-only | wc -l
# C5 夜跑健康
tail -20 .runtime/tmp/tilib-probe/backfill_night.log
# 活会话
python -c "import sys; sys.path.insert(0,'src'); from zephyr.security.access_control.session_concurrency import SessionRegistry; print([s.session_id for s in SessionRegistry().list_active()])"
```
