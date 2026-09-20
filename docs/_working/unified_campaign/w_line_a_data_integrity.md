---
ttl: task_bound
completes_when: 本线终验红蓝通过
---

# 【总包甲·数据正确性线】施工指令（自包含，新对话整贴即用）

# sid：st-data-fix-20260921 ｜ 落盘：docs/_working/data_fix_campaign/ ｜ 模型：Max 总包+Flash 分包
# 上位方案：docs/_working/unified_campaign/00_master_plan.md（§2 写域/§8 纪律）

## §0 使命
行情与基本面数据的正确性收尾：两个 P0（估值表派生列全空+价格腿全 0）→断供止血（5 条断供链）→哨兵补盲→登记收口。终态：估值消费方可信、每张核心表当日有数据有监控、known_data_gaps 册账实一致。

## §1 冷启动（每 shell 必做）
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"；python --version 须 3.12.x
python scripts/lock_files.py cleanup && python -m zephyr.trading.process_reaper --status
session_worktree_start("st-data-fix-20260921", allow_concurrent=True, allow_workspace_drift=True) + 心跳 daemon 30s（PowerShell Start-Process 独立进程）。
宪法 AGENTS.md 全程有效；裁号 re-find max+1 入 ruling_registry 同 commit 原子（当前 max=#377）。

## §2 真源读序
1. docs/_working/dataqa_audit/ 四报告（ch_health/gaps_registry_review/test_health/cross_findings——A 路 18 项全部细节与复验命令在此；**报告是死的库是活的，逐条先复现再修**）
2. src/zephyr/data/config/known_data_gaps.yaml + data_supply_sentinel.yaml（缺口/哨兵真源）
3. src/zephyr/data/implementations/akshare_provider.py（估值链病灶）
4. 修复红线参照：.runtime/sessions 下 X-2 复权链先例（072b2025——点乘子/真源表名/红证双向姿势）

## §3 任务波次

**W1（P0 估值双修，先行）**
- R1 index_valuation_daily 派生列 100% NULL+132 重复组复发：三选一（version 列单写者/internal_compute 接电唯一派生方/原始派生分表）——**推荐=version 列单写者**（爆炸半径最小+对齐 ReplacingMergeTree 语义）；修前估值消费禁用声明+修后 132 重复组清零红证
- R2 daily_valuation 价格腿 27 万行全 0+周六污染+mock 假绿：推荐=行情腿同步修（价格腿从 kline_daily 回填）+0 行成功告警+交易日 gate（A16 联动）；周六污染行按交易日判定清理（可逆：先冷存后删）
- R3 600016 缺 2026-09-15 除权事件：miniqmt 通道补采 ex_dividend_event → 复跑该样本红证（X-2 卡 §3 口径，应转绿）
- R4 老股复权偏差 0.2-0.4%：复核并按"深史链长>15 事件预算放宽至 5e-3"落进红证脚本注释（quantization 论证），或改中段窗口对齐
**W2（断供止血）**：R5 index_quote 9-16 停（采集链换桥重建）；R6 news_sentiment 9-14 停（静默失败排查+接心跳日志）；R7 auction 9-17 停（桥 socket 自愈重试，WinError 10038 实锤）；R8 crypto_kline 9-19 断排查；R9 stock_indicator 9-18 半日重跑补齐
**W3（哨兵+登记）**：R10 哨兵补 4 行盲表+新增交易日历逐日 diff 检查器（治"内部洞"原理性失明，事件触发禁 cron）；R11 known_data_gaps 8 条改册（etf 时区已执行改 completed 等）；R12 A3 tick 09-17 永久缺口登记留痕（禁再试补——QMT 退役+bdpan 停更双实证）

## §4 硬边界
- 只动写域：src/zephyr/data/**+config 数据侧+known_data_gaps/sentinel；**禁碰** CH 重 IO（OPTIMIZE/TRUNCATE/DROP/大回填全归乙线）、akshare_provider 以外的 provider、他会话在途件
- CH 访问只走 DatabaseService（execute() 方法）秒级读写；东财历史接口傍晚拒连→换 tushare daily_basic（token=secret_registry TUSHARE_TOKEN）
- 生产表只 append；破坏性行清理先冷存可逆；测试 tmp_path

## §5 验收与回执
每件：复现命令（修前红）→修复→复验命令（修后绿）+数字（行数/覆盖率/重复组数）；R1/R2 双 P0 出前后对照表。回执六要素（文件+commit/红证双向/验收命令实测数字/裁定号/证据等级/未完成原因）。自查循环两轮 0+红蓝抽 5 条反查四报告。

## §6 共享纪律（浓缩，全文=00_master_plan §8）
提交正门 git_commit.py --enqueue --files 白名单；死信读 dead json 修正后 requeue；新 md 先 token 载体先行批；热文件 CAS+git add 刷新 INDEX；金哈希滞后=validate_rules_integrity --fold；PROTECTED-PATHS Layer2=同 shell ZEPHYR_PROTECTED_PATHS_BYPASS=1+直连正门（Layer1 message 标记先行）；序列器残留四件=git -C .runtime/commit_queue/worktree checkout -- 还原；归档类改动 doc_type 剥离+危险 git 文本隔字；注册表净删带 [allow-mass-deletion:理由]；ttl: task_bound 禁 doc_type；dead_purged_20260920/ 勿 requeue；长脚本 Write 落文件再跑；禁把"没跑"写成"通过"。
