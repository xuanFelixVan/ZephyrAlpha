---
ttl: task_bound
completes_when: 本线终验红蓝通过
session: st-unified-plan-20260920
issue: UNIFIED-CAMPAIGN-001-V1-LINE-A
---

# 【总包甲·数据正确性线】施工指令 v1.0（自包含，新对话整贴即用）

# sid：st-data-fix-20260921 ｜ 落盘：docs/_working/data_fix_campaign/ ｜ 模型：Max 总包+Flash 分包（WO-1..4 领单）
# 上位方案：docs/_working/unified_campaign/00_master_plan_v1_0.md（§3 写域/§4 时序/§6 波次）；台账=ledger；处方=repair plan；派工单=workorders（三件同目录）

## §0 使命
行情与基本面数据正确性收尾：两个 P0（估值派生列全空+价格腿全 0）→断供止血（六链含 tilib 夜跑活体断供）→哨兵补盲→tilib 延续批（批10 筹码族+增量挂接+210 列验收）。终态：估值消费方可信、每张核心表当日有数据有监控、known_data_gaps 册账实一致、技术指标 210 列全部有数有验收。

## §1 冷启动（每 shell 必做）
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"；python --version 须 3.12.x
python scripts/lock_files.py cleanup && python -m zephyr.trading.process_reaper --status
session_worktree_start（allow_workspace_drift=True）+ SessionRegistry 注册+心跳 daemon 30s（PowerShell Start-Process 独立进程，配方=rule_audit_campaign/2026-09-19-construction-handover-prompt.md 纪律 8 条）。
宪法 AGENTS.md 全程有效；裁号 re-find max+1 入 ruling_registry 同 commit 原子（**开工时实测 max——本方案班已用到 #379**）。

## §2 真源读序
1. docs/_working/unified_campaign/p3_db_repair_master_plan_v1_0.md（病-1..19 复现/根因/处方/验收——本线施工病历）
2. docs/_working/unified_campaign/p2_backlog_master_ledger_v1_0.md（A/C 路条目+状态）+p2_workorders_v1_0.md（WO-1..4）
3. docs/_working/dataqa_audit/ 四报告（ch_health/gaps_registry_review/test_health/cross_findings——细节与复验命令真源；**报告是死的库是活的，逐条先复现再修**）
4. src/zephyr/data/config/known_data_gaps.yaml + data_supply_sentinel.yaml（缺口/哨兵真源）
5. tilib 延续批真源：docs/_working/archive/2026-09/c_class_scattered/2026-09-15-tilib-handoff.md §3（**批9/批10 配方，原件已归档勿按旧路径找**）+docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/16_technical_indicator_catalog.md（活真源）+tilib_clearance/ a5 交付报告
6. 修复红线参照：X-2 复权链先例（072b2025——点乘子/真源表名/红证双向姿势）
7. **CH 实况自查（勿信任何旧数）**：system.parts 水位（TI 当前 1181 parts 漂移中）/system.error_log 近 24h/D 盘 df -h/夜跑 log 尾部/t_timing_window_board.md 声明窗

## §3 任务波次（对应 WO-1..4）
**W1（P0 估值双修，WO-1，即刻——签字③未批先做无门位半）**：R1 index_valuation_daily（病-1，推荐=version 列单写者）；R2 daily_valuation（病-2，行情腿同步修+交易日 gate+0 行告警）；消费禁用声明先行。600016 除权补采与复权偏差注释（X-2 尾款）随批。
**W2（断供止血，WO-2）**：R5 index_quote 换桥重建（病-3）；R6 news_sentiment 静默失败+接痕（病-4）；R7 auction socket 自愈（病-5）；R8 crypto 排查（病-6）；R9 stock_indicator 重跑（病-7）；**R9b tilib 夜跑修复（病-8——09-20 实测活体断供：Code 241 阵亡+13.3 万行缓冲丢失+新列 0% 回填；低峰单进程重跑+连续 3 日健康观察）**。
**W3（哨兵+改册，WO-3）**：R10 哨兵补 4 行+日历逐日 diff 检查器（事件触发禁 cron，病-10）；R11 known_data_gaps 改册 8 条+漂移补登记（病-9/16/17）；R12 周末 gate（病-18，随 W1 联动）；R12b 12 小表写入端攒批（病-13 前半）。
**W4（tilib 延续批，WO-4——前置=乙 W1 落地+TI OPTIMIZE 互斥排队）**：R13 stock_daily_basic 增量挂 tasks.yaml（签字⑨）；R14 批10 筹码族 CYQ/SCR/CYC 三件套（注册表 138→141，配方=交接包 §3 批10+16 号 memo）；R15 210 列验收核销（audit_all_cols 思路全列台账）；R16 tushare 备胎优先级表注记（东财拒连风险）。

## §4 硬边界
- 写域：src/zephyr/data/**+src/zephyr/factor/technical_indicators/**（仅 W4）+config 数据侧+known_data_gaps/sentinel；**禁碰** CH 重 IO（OPTIMIZE/TRUNCATE/DROP/大回填全归乙线）、akshare_provider 以外 provider、他会话在途件、tasks.yaml 本体（未批⑨前）
- CH 访问只走 DatabaseService（reader=zephyr_reader）秒级读写；>30 分钟批次启动前查 t_timing_window_board.md 且禁横跨 active 窗
- 生产表只 append；破坏性行清理先冷存可逆；测试 tmp_path；东财拒连→tushare（TUSHARE_TOKEN=secret_registry）

## §5 验收与回执
每件：复现（修前红）→修复→复验（修后绿）+数字（行数/覆盖率/重复组数/max 日期）；R1/R2 双 P0 出前后对照表。回执六要素（文件+commit/红证双向/验收命令实测数字/裁定号/证据等级[亲验]/未完成原因）。自查循环连续两轮 0 问题+红蓝抽 5 条反查 repair plan/四报告。

## §6 共享纪律（浓缩，全文=00_master_plan_v1_0 §10）
提交正门 git_commit.py --enqueue --files 白名单+死信修正后 requeue（dead_purged_20260920/ 勿 requeue）；新 md 先 creation_token 同批；热文件 safe_write_text CAS+git add 刷新 INDEX；金哈希滞后=validate_rules_integrity --fold；PROTECTED-PATHS Layer2=同 shell ZEPHYR_PROTECTED_PATHS_BYPASS=1+直连正门；序列器残留四件=checkout 还原；归档类 doc_type 剥离+危险文本隔字；注册表净删带 [allow-mass-deletion:理由]；ttl: task_bound 禁 doc_type；基名全局唯一+目录禁数字后缀；长脚本 Write 落文件再跑；长批分片+幂等 resume（SIGTERM 七杀）；他会话在途件避让；禁虚报。
