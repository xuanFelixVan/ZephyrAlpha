---
ttl: task_bound
session: st-data-fix-20260921
title: 总包甲·数据正确性线 端到端交付报告（七分包全终态）
completes_when: Owner 验收后随战役归档
---

# 甲线端到端交付报告（2026-09-20 22:00 → 09-21 晚 · st-data-fix-20260921）

> 上位真源：unified_campaign v1.0 全家福 + 执行令 v2.1 + 裁定#380/#381/#382。
> 七分包全部交付；独立异眼验收=高可信零虚报；收官 R1 全量扫描 16/16 PASS。
> 证据等级：未标注者均为 [亲验]（DatabaseService reader 实测/git 实证）。

## §0 一句话总评

九项终态目标中七项全绿收官，两项如实挂账（批10 全市场回填等乙线W1、今日 tick/竞价实时源=Owner 门位）；每一项都有修前红证→修后绿证实测数字，全程零虚报、零绕门、零他域连坐。

## §1 交付总账（分包×commit×绿证）

| 分包 | 交付 | commit | 绿证核心数字（修前→修后） |
|---|---|---|---|
| 0 | 09-17 tick+五档找回+模拟盘评估 | 74ad6dfe4e/c65ffa5a06 | tick_data 09-17：0→**28,327,322 行/7,799 标的**（超邻日 09-16=23,908,666）；tick_depth_5：23,929→**28,819,429 行/7,844 标的**（2.4×邻日覆盖）；180 只源缺（退市/停牌/模拟源未收录）如实列 |
| 1 | 估值双修+红蓝对抗③项 | 226db0d2bc | A1 cape NULL(2015后)：8,125/8,125→**0/5,696**，dup FINAL=0；A2 close>0：0/271,266→**99.91%**；周末污染 82,344 行（周六43,510+周日38,834，比病历扩面）冷存后清零 |
| 2 | 断供止血六链+C-5 | 363e4fa1ed | index_quote max 09-16→**09-21 实弹**（akshare/sina 562 只链重建）；news 09-14→**09-21 08:00 晨跑落数**（根因=总闸 flag 09-12 落地+任务 Disabled 双杀）；crypto 09-19 补齐+09-20 自愈；stock_indicator 09-18 满日 5,565+周一触发链 03:00 实弹；auction 09-17=3,230+book 103,245 派生回补；TSV 风暴 18 毒文件隔离；dwm 58/58 片 exit=0，**gp_pred 0→1,570 万非零**（异眼验收时点实测，仍在增长） |
| 3 | 哨兵+改册+检查器 | a065f76ef1+两 token 批 | sentinel 55→**58 腿**；日历逐日 diff 检查器上线即抓真问题（daily_valuation 09-16~18 部分写入）；gaps 57→**60 条**账实一致；12 小表 60s 攒批 21 任务 |
| 4 | 批10 筹码族（代码层） | 7963211f1a+两 token 批 | 注册表 138→**141 v1.6.0**（CYQ4列/SCR/CYC4列）；CYQ 000852 复算 **20/20 偏差 0**；tests **1109 passed**；两票试跑 33/33 有数；量纲发现=volume 存"手"非"股"（CYC ÷100 修正） |
| 5 | SCD2×4 | cec6ec26b5+34e6cb8a43 | **4/4=测试病**（断言停在 08-30 前契约），src 无 bug；5 passed+4 项 mutation 再注入全红 |
| 6 | 1970 治本 | 3988001c3c/4ec4b1e13e | 来源清单 **12 表×19 列三层病根**；A 族 **398,740 格 NULL 化清零**（13 表 15 列 Nullable 化+10,927 空壳行实证删除）；写入端 scrub 守卫上线；B 族 46,905 键列（PARTITION/ORDER BY 键 CH 禁 Nullable，Code 524 实证）如实保留+补真渠道分级留档 |

总包亲历插曲：cffex 毒 TSV 2 件（分包2 误判"合法积压"，实为 09-18 列漂移同族）→补 variety 列修复→10:33 回灌成功 2/2，重试风暴（~8 次/秒空转）终结。

## §2 验收命令与实测数字（异眼复核+总包 R1 扫描 16/16 PASS）

```
SELECT countIf(cape_5y IS NULL),count() FROM c1_market.index_valuation_daily FINAL WHERE trade_date>='2015-01-01'  -- (0, 5696)
SELECT countIf(close>0),count() FROM c1_market.daily_valuation FINAL                                             -- 99.91%
SELECT countIf(trade_date='2026-09-17') FROM c1_market.tick_data                                                 -- 28,327,322
SELECT countIf(trade_date='2026-09-17') FROM c1_market.tick_depth_5                                              -- 28,819,429
SELECT max(trade_date) FROM c1_market.index_quote                                                                -- 2026-09-21
SELECT countIf(gp_pred!=0) FROM c1_market.technical_indicator WHERE trade_date>='2026-06-01'                     -- 15,570,061（验收时点）
SELECT countIf(trade_date='2026-09-18') FROM c1_market.stock_indicator                                           -- 5,565
```
pytest：SCD2 5 passed｜scrub 6 passed｜chips 抽类 10 passed｜checker 11 passed｜攒批 3 passed｜全量 1109 passed（分包4 落地时）。

## §3 红蓝对抗（收官轮 5+1，异眼代理执行）

- 重放 5 条全部绿：病1/病2/病9/病3/病7 同命令复现全过。
- 假设性破坏 3 项注入全部真拦：⑥a scrub 守卫注入 1970→NULL 化（PIT 墓碑列按设计豁免）；⑥b 交易日 gate 周六行 2/3 拦+日历不可用 fail-closed 整批拦；⑥c 检查器 tmp_path 缺日注入抓到。
- 分包1 三项对抗记录完整（双写竞争/周六写入/0行告警各有红→绿→净零链）；分包6 对抗以 6 例 pytest 注入+修前修后 probe+bak 零误清核对形式存在（与 p1 格式不同但证据链完整，异眼已独立重放）。

## §4 09-17 找回量与五档界定（分包0 报告 p0_0917_tick_recovery_report.md 详版）

- tick_data 09-17=28,327,322 行/7,799 标的；tick_depth_5=28,819,429 行/7,844 标的，**五档历史实测可下且已全市场回补**（5 类代表标的 dry-run 5/5 含转债/京市）。
- 长尾：180 只 0 行（cb5/etf12/stock40/lof86/bj33，判退市/停牌/模拟源未收录）+4 只期货域外，如实登记。
- 09-18 竞价窗=源永缺（tick_depth_5 竞价窗仅 18-23 行），已登记 gaps。

## §5 模拟盘持续源评估结论（p0_sim_as_source_assessment.md 详版）

- 能力族实测：tick/五档/竞价/分钟/日线**全可下**（实时未测=约束声明）；tick 历史深度≈1 个月，分钟/日线数年；质量抽验逐位对齐 kline。
- 推荐：A=补数源（已实战验证）+C=大 QMT 沙箱主通道；B=实时复役**不推荐自行执行**——今日 tick/竞价实时断供的解锁钥匙在 Owner 手里（模拟盘客户端进程现存活 pid 19936，E:\国金QMT交易端模拟，接线决策=Owner 门位）。

## §6 1970 来源清单与治本原料使用记录（p6_1970_root_cure_report.md 详版）

- 三层病根：硬编码 1970 哨兵（7 处写入端）／空串 TSV 落默认值／列名漂移致 DEFAULT 1970（restricted_shares 列过期+equity_pledge 缺列，data_source='' 恰=unlock 1970 计数实锤）。
- 治本：写入端 scrub_1970_date_sentinels 守卫（write_result+BufferedWriter 双入口，PIT 墓碑豁免）+providers 哨兵改 None。
- 参照原料（裁定#382）：c3_fundamental 四张 *_bak_1970clean_20260914 核对结论=**零误清零价值**（全部行 report_period=1970+指标全空），处置移交乙线呈报。
- 可逆留痕：E:/{c1_market,c3_fundamental}/p6_1970_export/ 13 Parquet。

## §7 停手项与等待项（全部如实登记，非失败）

| # | 项 | 原因 | 恢复路径 |
|---|---|---|---|
| 1 | 批10 全市场回填 | 前置=乙线W1（时序板无 done 行，执行令明文） | `python scripts/data/backfill_technical_indicator_dwm.py --periods daily --end <T>`（先 --dry-run）+ 210 列验收 `scripts/audit_technical_indicator_columns.py --mode summary` |
| 2 | 今日 tick/竞价实时断供 | 源=已退役 miniQMT 桥；模拟盘实时接线=Owner 门位（分包0 报告选项 B） | Owner 批接线方案后改 subscriber 配置；qmt_bridge 熔断冷却为 64号Q17 正确行为 |
| 3 | scripts/data/p0_tick_backfill.py 改动滞暂存 | .gitignore 通配误伤 tracked 常驻件=受保护路径 Owner 门位 | Owner 批豁免后 `commit_queue.py requeue q-0015/0016` |
| 4 | 1970 B 族 46,905 行 | PARTITION/ORDER BY 键列 CH 结构性禁 Nullable | 补真渠道分级已留档（dividend/rights 可重拉；restricted_shares 解禁日 akshare 渠道验证可行） |
| 5 | tilib 夜跑恢复 | 分片 runner 在 .runtime/tmp（临时区）+连续3日观察未满 | 观察 3 日健康后：runner 提升到 tracked 路径（需 gitignore 豁免）→backfill_night.bat 改指→schtasks enable；现状=任务保持 Disabled（证据在案） |
| 6 | daily_valuation 09-16~18 部分写入 | 检查器上线抓出；full_refresh≈11h 级 | 已入册+工单，低峰窗跑 |
| 7 | turnover 源端缺口/cape 量纲/10Y 债 2010-12 稀疏 | 数据源端债，非本线可修 | 分包1 报告停手项已详列 |
| 8 | 乙线W1/尸体表/12小表 OPTIMIZE/TI OPTIMIZE | 乙线独占窗职权 | 时序板排队 |

## §8 遗留移交（他会话/维护班）

- module_translation 卫生块（他会话在途）隔离在 .runtime/tmp/st-data-fix-20260921/module_translation_registry.sibling_wip.bak.yaml。
- ROOR REG-IND-001 描述漂移（"41 条/58 列"旧数）——丙线持有不代修。
- gp_pred/批次计数随时间自然增长的口径差已在 §2 注明时点。

## §9 过程纪律自报

- 提交全走 GitCommitGateway 队列正门，死信逐条按 dead_reason 修正 requeue（分包4 一批 11 轮、分包3 一批 8 轮全留痕），零绕门零伪造标记。
- 会话心跳两次断线（注册 pid 病+daemon 失活）均当场复活；1302 限流假死 3 次均经现场核实避免重复派工。
- CH 全程 DatabaseService；零 OPTIMIZE/TRUNCATE/DROP；唯一删除=分包1 周末冷存后清（批文授权）+分包6 空壳行实证删除（可逆留痕）。
- 夜间 02:30 任务 disable 一次（防与 tick 重写入撞车，证据=09-20 04:03 Code 241 实证），本报告 §7.5 留恢复路径。
