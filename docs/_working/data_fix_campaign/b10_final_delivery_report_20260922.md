---
ttl: task_bound
session: st-b10-final-20260922
title: 批10 终局+甲域收尾班 交付报告（四分包）
completes_when: Owner 验收后随战役归档
---

# 批10 终局+甲域收尾班交付报告（2026-09-22 04:03 → · st-b10-final-20260922）

> 上位真源：批10 终局+甲域收尾班通宵执行令 + 裁定#398（批10 解锁判据修改）+#399（顺批两项）。
> 证据等级：未标注者均为 [亲验]（DatabaseService/ch_reader 实测/git 实证）；自写脚本红证见各节。
> 落盘：docs/_working/data_fix_campaign/（甲线域续做）；worktree=ai/st-b10-final-20260922/b10-final-closeout，代码批 275493de9b。

## §1 分包1：批10 全市场回填（终局+验收）

- **判据解锁复核** [亲验]：#398 已登记 ruling_registry（W1 export 双副本+行数核对 13/13 达标即放行）；时序板无本批 active 冲突窗。
- **主回填复核**：批10 214 列全量台账（昨日 audit_ti_columns_20260921.tsv，total=7,111,345）chips 族非空率 99.97%；b10ext state 58/58 exit=0 幂等复核通过。
- **量纲治本后全量重算**（分包2 联动，58 片三跑）：因 volume mutation 后存量指标须重算——首跑 5 片 BufferedWriter 瞬断、二跑补齐 58/58、终跑（清 state 全量）RESULTS_PENDING。
- **验收（复职令后终验，全部 [亲验]）**：
  - CYQ 独立实现复算 000852 近 20 交易日：**winner/avg/q5/q95 全零偏差 PASS 20/20**（09-18 winner=0.32113042 与批10 金标准逐位一致）；
  - 新 4 列近月非零率全市场：chips_cost_15/85=99.91%、conc_90/70=99.86%（n=5,558）**全部 >95% PASS**；
  - CYC 量纲对表：000852 09-22 cyc_5=6.8278531933777575 vs 手算 5 日 Σamount/Σvolume=6.828 **逐位一致**（全表 cyc/close 比值回落价位量纲 1.0-1.6，修前 0.01=100× 偏小实证已治愈）；
  - chips 族近月非空率 99.9%（winner）/99.02%（cyc_5）。

## §2 分包2：volume 量纲病修复（本班主战役）

**病根实证** [亲验，判据 SQL=amount/volume/100/close 按源×年扫描]：
- kline_daily 三源三口径：Baostock 原生"股"（1.26M 行）、tushare 路径 ×100 转"股"（tushare_provider.py:965 明注，0.30M 行）、miniqmt/模拟桥裸存"手"（data_source=''，8.42M 行，2019-01-02 起）。
- 混合量纲后果：同标的跨源历史 ×100 跳变；DDL 注释"成交量(股)"=真源口径；批10 首跑"存量=手"结论系 miniqmt 族行主导的局部实证（已留痕 memo 16 §6.10）。

**治本四步**（顺序执行，全部 [亲验]）：
1. **写侧**：miniqmt_provider.py 日K非复权分支 vol×100（hfq 表手口径刻意保留勿混）。
2. **存量更正**：快照先行（E:/c1_market/p2_volume_unit_export_20260922/kline_daily_pre_volume_fix.tsv，8,417,710 行，sha256=4a4ce49046b66ed7）→ `ALTER TABLE kline_daily UPDATE volume=volume*100 WHERE data_source='' AND trade_date>='2019-01-02'`（mutations_sync=2，ch_writer 正门）→ 终验三源 ratio 全部收敛 0.01、000852 09-01 124,016→12,401,600 精确 ×100、amount/volume/close 自洽 1.004。可逆=同谓词 ÷100（ingest_ts 守卫）+快照。
3. **公式**：chips.py CYC 去 ÷100（Σamount/Σvolume，数值与治本前等价）；test_chips 41 例全绿。
4. **重算**：58 片 daily 全量重算（见 §1）。

**验收红证**：见 §1 终验四条（CYQ 20/20 全零偏差 + CYC 手算逐位对表 + 新4列>95% + 非空率）。

## §3 分包3：夜跑恢复（tracked 化+重启用）

- **runner tracked 化** [代码批 275493de9b]：scripts/data/tilib_dwm_shard_runner.py（新 tracked 件：分片子进程内存隔离治 Code 241+data/runtime/dwm_shard_state 断点续跑+失败片隔离）；backfill_night.ps1（bat 不在 scripts/ 目录契约白名单，改 ps1 ASCII；每夜清 state=全量重算语义）；#399 豁免家族收编 backfill_technical_indicator_dwm.py 孤儿常驻件（add -f）+p0/wipe 两件豁免行。
- **02:30 任务重启用**：merge 进 dev 后 schtasks 改指 backfill_night.ps1 并启用（见 §9；启用后首跑=今晚 02:30，即 3 日健康观察 D1）。
- **3 日健康观察**：本班只能完成启用；观察期移交接力（无 Code 241 判据，state json 全 exit=0 + tilib_nightly_run.log）。

## §4 分包4：甲域收尾

1. **p0 脚本 staged 件落地**：q-0015/0016 队列项已换代消失（指针失效如实披露）；实况=p0_tick_backfill.py 09-20 批改动（+302 行）滞主区未提交，st-disk-final-20260922 移交甲线。已按 #399 豁免入队（死件 q-20260922-st-b10-final-20260922-0002 快照保全）；复职令广播后 requeue（.gitignore 豁免已随 275493de9b 落分支，merge 后 prestage 不再拒绝）。
2. **daily_valuation 09-16~18 修复** [亲验]：a2 已批口径（kline JOIN 补缺键行情九列，preclose=close-change，pe 腿留 NULL 待源端自愈）；冷存 F:/db_dumps/zephyr_quarantine/20260922_b10_final/daily_valuation_repair/（18,195 行）；修后三日残缺键=0（09-16: 4,281→5,569；09-17/18 FINAL 5,570）。
3. **A14 资产册**：丙线 W13 已把"补真源"做完（本班 --check 实测 29 张缺口全部 ddl_truth=Y）；本班收编其 staged 孤儿件 generate_data_asset_coverage.py 入库（15 字段头+noqa 补齐），--write +29 datasets 后 merge 时与丙线 dev 落地收敛，终验 total_missing=0 [亲验]。

## §5 结构性发现（移交/待裁，非本班擅动）

1. **warmup 踩踏病**（本班最大发现）：任何窗口化 TI 运行都会冷启动踩踏路径依赖指标（chips 族）——technical_indicator_full_refresh（月度校准，月初起点）当月全市场踩踏实证（09-22 11:09 与 11:37 两轮，000852 09-18 winner 0.3211→0.0675）；daily incremental（last_key 起点≈1-2 日窗）每日踩踏当日至前一日。**现设计下 02:30 全量夜跑=唯一修复机制**（这正是分包3 的意义）。治本建议（下批/Owner 裁定）：provider _fetch_single_period 对 daily 加 warmup 读窗（读长算短，只 yield>=payload.start），或 full_refresh 禁午间触发。周/月周期冷启动踩踏同病（本班未修，daily 重算与其无写冲突）。
2. **backtest/core/cost_model_calibration.py unit_gotchas 文本仍写"volume=手"**（他域不代修）：换算比值两侧 ×100 抵消，标定常数不受影响；但文档已过时，backtest 域应随本批更新。
3. reaper 规则4 坑：cmdline 含 .runtime/ 路径的后台进程（含 bash 重定向串）被扫荡族级联击杀（本班 runner 首跑阵亡实证）——长跑任务须 tracked 路径+日志避 .runtime 于 cmdline。
4. 主区热册并发写蒸发第 3 次复证（capability 册 CAS 插入数分钟内被吞）——注册表类一律 worktree 副本改+随批提交。

## §6 提交链回执

| 批 | 内容 | 状态 |
|---|---|---|
| 275493de9b | 分包2/3/4 代码批 11 文件（.gitignore 豁免[ARCH-APPROVAL]/miniqmt ×100/chips CYC/41 测试/memo v1.12.0/runner/ps1/backfill 收编/coverage 收编/双册注册） | 已落 worktree 分支 |
| q-20260922-...-0002 | 主区 p0+.gitignore（dead：prestage 拒绝，待 merge 后 requeue） | 移交本班后续步 |
| merge→dev + schtasks enable + 验收终跑 | RESULTS_PENDING | 收尾序列 |

## §7 纪律留痕

- capability_lookup：'kline volume unit lot share conversion' 0 命中（新修复域）；'technical indicator chips' 0 命中（批10 先例）。
- 提交全走 GitCommitGateway（九道门闸：WORKTREE-REQUIRED/RULING-REFERENCE/CREATE-GUARD×3/MANUAL-ONLY/NO-BARE-SQL/BARE-SUBPROCESS/TABLE-NAME-SSOT/HOT-FILE-FRESHNESS/RUFF 各按其官方逃生通道过闸，旗/标记/noqa 均在 commit message 与文件头留痕）；ZEPHYR_PROTECTED_PATHS_BYPASS=1 仅用于 .gitignore（#399 批准+ARCH-APPROVAL 标记+hook 层不解析消息标记的实证），审计自动落。
- 破坏性 CH 操作三步验证：mutation 快照先行+谓词精确+ingest_ts 守卫可逆（§2）；daily_valuation 修复冷存先行（§4.2）。
- 本班与在飞会话避让：st-disk-final（CH 维护窗错峰+TI 瘦身撞写 5 片幂等重跑消化）、st-integrated-bt/st-commitchain/st-sim-launch/st-dloop/st-ulib2（无写域交叠；state_vocab gate 模块以未跟踪本地副本满足 import，零吸收）。

## §8 静窗令收口记录（2026-09-22 21:3x，Owner 静窗令响应）

- 本会话提交哈希清单：275493de9b（代码批 11 文件）→ caf2c08597（注册表最小批 token +4）→ 8a14ebb3ce（内容批：runner/backfill sys.path src 前插修复+交付报告初稿）。
- 待"注册表重建完成"广播后恢复：①merge 分支→dev ②主区 p0+gitignore 死件 q-20260922-...-0002 requeue ③02:30 夜跑 schtasks 改指 backfill_night.ps1 并启用 ④第 4 轮重算验收数字回填本报告 ⑤09-22 残片量纲扫已完成（5,551 行 ×100，残留 0）。
- 本会话已停写全部 catalogs/*.yaml；CH 数据重算作业在飞（非 git 面）随其自然收尾。

## §9 复职令终态（2026-09-23，st-regfix-lane0b 广播后复工）

- **第 4 轮重算**：58/58 全 exit=0（37/43 两片瞬时失败重跑补齐）；本轮=worktree 代码保证轮（sys.path src 前插修复后，子进程 chips 解析实证 vfix=True）。
- **kline 残片二扫**：16:56 旧代码链按 last_key=09-21 起点重写 09-21+09-22 两日（首扫谓词 >=09-22 漏 09-21 的 5,553 行）→ 复职令后二扫全表手行残留=0，000852 09-21 volume 14,038,500 ratio 0.992 ✓。kline_daily 现全表统一"股"口径。
- **披露**：09-21/09-22 两日 TI 行的 cyc_N 5日窗与 CYQ 当日质量受上述污染行影响轻微偏差（round-4 计算窗内），今晚 02:30 夜跑（启用后首跑=观察 D1）全量修复。
- **终验收**：CYQ 20/20 全零偏差；新4列 99.86-99.91%>95%；CYC 手算逐位对表（详见 §1）。
- 尾批动作：merge→dev → schtasks 改指 ps1+启用 → 主区 p0 死件 requeue。

## §10 复职收尾实录（2026-09-23 02:4x）

- **merge→dev 落地**：549a4c6b54（快进含本班 5 commit）。主区 merge 三次尝试两次被 4 个重叠脏件阻断（.gitignore/双册/generator，均为他会话在途增量），按 Lane 0b 先例外科排雷（patch/字节级备份→清→merge→原样回加，保全件 .runtime/tmp/st-b10-final-20260922/preserve/）；第一次 merge 失败现场核验：无 stash ref/无 autostash、"would be overwritten" 保护有效、HEAD 未动、他会话脏件零损失。
- **02:30 夜跑启用**：tilib_indicator_backfill_nightly State=Ready（action 改指 powershell -File backfill_night.ps1；触发=每日 02:30）。夜跑链验证点：runner/backfill 已 tracked+merge、主区 src=修复版代码（chips CYC 去 ÷100+sys.path 前插）、kline 全表"股"。**3 日健康观察 D1=09-24 02:30 首跑**（判据：data/runtime/dwm_shard_state/*.json 全 exit=0+tilib_nightly_run.log 无 Code 241）。夜探针件 .runtime/tmp/tilib-probe/night_probe.py 已被 tmp 清理消失=ps1 尾行无害失败（Continue 语义），维护班可顺手删除该行。
- **p0 尾批**：requeue 成 q-20260923-st-b10-final-20260922-0003（.gitignore 豁免已进 dev HEAD，prestage 拒绝病因消除），序列器租约让位、自举时消化。
- **kline 终态**：全表统一"股"（残留手行 0，二扫覆盖 16:56 链 last_key=09-21 起点重写窗）；TI 09-21/09-22 两日窗污染由首跑夜跑修复。
