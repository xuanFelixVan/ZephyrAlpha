---
ttl: task_bound
title: 总筹交接卡 波2 · 第四棒第一读（含归属图/未完成件/三把尺坐标/落地教训）
session: st-fflead-20260925
---

# 92 总筹交接卡 波2（第四棒从这里接）

> 上一棒＝st-fflead-20260925（第三棒总筹）。本卡只记**实测**，未验的标"未验"。
> 读序：本卡 → `fullflow_mining/00_orchestration.md`（编排册）→ `91_chief_command_wave1.md`（指挥册）→ `90_chief_rulings_wave1.md` §五（更正）。

## 一、归属图（09-26 02:19 实测 14 个活会话；派单前必读，防撞线）

| 线 | 主责会话 | 证据 |
|---|---|---|
| GPU T1/T0/成绩单 | `st-ddup-20260925` | task_files=`factory_grid_executor`/`_c4_engine`/`regime_validation`；2h 内 5 笔提交（最活跃） |
| 备份/DR/恢复演练/对账/锁测试 | `st-backup-cold-20260925-audit`＋`st-bca-c-drill`/`b-recon`/`f-dash`/`i-locktest` | 五子班同跑 |
| 供数链（假绿灯那批） | `st-ff-pipes-20260926` | 会话名即 pipes |
| 提交链失败诊断 | `st-ff-chfail-20260926` | 同上 |
| 阈值/会话注册表治理 | `st-ff-j-20260926` | task_files 含 `thresholds.py`/`session_concurrency` |
| 提交链提速（包8/9/7/14/15） | `st-commitspeed-tbl`＋`st-commitspeed-pkg8` | 02:05 落 T8 簇2+3 |
| AI 层 / QMine / 板块注册表 | `st-ailayer-final` / `st-qmine` / `st-metaq-gc` | 队列在飞袋归属计数 |

**⚠ 第三棒据此撤回过一份推荐**：曾推荐"先修备份可恢复性＋供数守恒"，实测这两条**都已有班在做**。
⇒ **铁律补一条：列清单之前先拿归属图。** 顺序倒了就是给项目派重复活。

## 二、已完成（可复核，勿重做）

| 件 | 凭据 |
|---|---|
| IBT 首跑 22 件复原入库 | commit `4c00b9607d`；HEAD 内 22 件 sha256 == 队列袋 `blob_sha256` 22/22 |
| N-16 提交面漏读自家真源 治本＋永久尺 | 同 commit；尺 `tests/governance/d3_metadata/test_n16_skip_working.py` 3 passed；命名全族 274 绿 |
| 118 本作业簿进 HEAD（原只挂主区 index） | `git ls-tree -r HEAD \| grep -c fullflow_mining` = 119；停抢后被他班吸收 |
| 热册被陈旧快照抹掉的 3 条 token 补回 | 复验"HEAD 有而 index 无"= 0；他班 687/700 行换绑未碰 |
| miniQMT 口径更正（案卷+裁定册） | `90_chief_rulings_wave1.md` §五 五条追加更正 |

## 三、**唯一未完成件**（第四棒第一件事，勿新开战场前先收这个）

`miniQMT 仅实盘退役、模拟盘在用为取数源`的**代码/配置/前端文案** 7 件修正：

- 清单：`src/zephyr/ex_core/miniqmt_channel_manager.py`、`src/zephyr/data/config/known_data_gaps.yaml`、`src/zephyr/backtest/implementations/ch_tick_replay.py`、`src/zephyr/data/config/data_supply_sentinel.yaml`、`src/zephyr/frontend/dashboard/web/features/bridge/br-page.js`、`src/zephyr/frontend/dashboard/web/pages/bridge.html`、`docs/_working/automation/campaign/HANDOFF_20260921_ab_league.md`
- 现况：**已改好、已验收**（AST×2＋YAML×2 进程外解析通过；被删行全为注释/文档串/前端文案，无逻辑）；**02:3x 提交时 exit=2＝全局锁超时**，文件已进暂存面（主区自动 add 机制），**很可能已被任一正门吸收**。
- **先跑这一条判定，别急着重做**：`git status --porcelain <上述7件>` → 干净且 `git show HEAD:src/zephyr/ex_core/miniqmt_channel_manager.py | grep -c 模拟端` > 0 ⇒ 已落，跳过；否则用 `--adopt-prior-work` 重投。
- 另有 2 件（`m1_data/01_ingest.md`、`m1_data/pending_rulings.md`）死于 `FOREIGN_CHANGE_VIOLATION`：**两车道写同名案卷**。第三棒选择**不吞他班在途件**、把它们从本批摘出。⇒ 第四棒须与 `st-ff-pipes` 定真源后再并（或各自追加段，互不覆盖）。

## 四、三把尺（第一性原理治本方案，尚未有人立）

病根统一为一条：**"声称"没有独立反证通道**。已实测的同族病灶：`realtime_snapshot` 记 SUCCESS 5568 行而表内 0 行；`kline_sector_intraday` 自 09-10 假 SUCCESS；`process_reaper --status` 打 01:47 缓存快照而该任务每 5-6min fire 却 exit 1（台账失明 22h）；GATE-21 自洽台读盘不读 dev 册（`total_gates=174` vs 实 180 却报 PASS）；`reconciliation_differences` 两库皆空致"没跑过"与"无差异"不可分辨；备份 `last_backup_status=failed`＋`log_verified=False`＋可恢复性零实证。

1. **禁缓存背书**：凡给写操作开绿灯的读数必须现算，或标快照时刻且 age 超阈即报红。（**先做这条**——它是其余两条的验收前提）
2. **供数守恒断言**：落库后独立读最终真值与"任务自称"对账，不符即报红并让下游降级（＝EV-03 从提交链扩到数据链，**同一病同一药，勿造第二套**）。
3. **反事实控制组入判据模板**：每把新尺自带"喂错数据必须变红"的对照组；恒绿且无配对测试＝判"疑似判据失效"（项目已有此定档）。
业界同构做法（对表不引依赖）：`great_expectations`/`pandera` 断言即代码、`dbt tests`＋data-diff 把"跑过"与"结果变了"分开记账、QLib 把完整性校验做成供数硬前置。共性＝**声称与证据物理分两通道**。项目已有 sentinel/reconciler/自洽台这些"手"，**补判据不造框架**。
**代价照实**：这三件不产出任何新业务能力；买的是"系统说'好了'时你有权信"。

## 五、落地教训（今晚踩实，写给所有棒次）

1. 热册（capability/ruling/module_translation）多班共写：**读→写→提交必须同进程衔接**，跨一个对话回合必过期。第三棒 8 次 CAS 全被拒（`StaleWriteRefused`/`RegistryMassEditRefused`）——**守卫全对，是路子错**；被连拒就停手，别造第四套重放器。
2. **禁 `allow_mass_edit=True` 绕闸**，禁 `git checkout HEAD -- <热册>`（＝第二次蒸发）。
3. 计数用**键集合差**，不用 diff 的行数：把 `- created_by:` 行数当"被删条目数"曾致虚报 140 条（实际 3 条，47 倍）。
4. 起批前先读 `commit_pct`（09-26 复发新形态：**自造并发崩在 `git add`，退出码 0xC0000142**）。四批串行＋多子代理＝自己把机器推到临界。
5. 深队列（本棒 29→41 袋、约 2.5h）期间**停抢反而会被吸收**：118 本就是这么落的。
6. `--enqueue` 主区被他班活跃拦（WORKTREE-REQUIRED）、`git_commit.py --enqueue` 需 `commit_queue_interactive`（Owner 窗口）⇒ 直提走 `--allow-non-worktree --allow-multi-domain`，别绕门。
7. 会话判死＝claim 自动收回（心跳 90s 轨）；daemon 另有 idle 1800s 自退。**注册必 `pid=0`**。实测修正：**会话死、claim 没了，袋照样落**——claim 的价值在落地前的防连坐窗口，不在落地时点必须存活。

## 六、Owner 已拍、勿再议

- **miniQMT**：仅**实盘下单通道**退役；**模拟盘在用为分钟/tick 全域唯一被指派源**（`tasks.yaml` 实测：股票/ETF/LOF 全档分钟＋`tick_data`＋`l2_tick`＋期货 tick＋分钟宽度＝miniqmt；竞价＝qmt_watchdog 之外的 `qmt_bridge`）。
- **看门狗不必保护**：Owner 判——模拟盘须人工密码登录，自动恢复无价值。**此条已终局，勿再提恢复建议**；`RestartMiniQmt`/`TradingWatchdog` 转为"可进一次性删除清单"的低风险账面项（删除本身仍属 Owner 门）。
- 六段词表已裁 #398/#399，**勿重裁**；新废表只登记＋报警（#382-④）；16 库≠13 轴（量纲不同，勿立矛盾案）。
- T2 冻结至池基修好（R-M2-3 选①）；GPU 规模口径 T0 200/T1 3700/T2 900，"24990" 禁引。
- 环节真源＝F 编号；122 不完备（29 项候选漏项含 4 项 P0）；子类目成册改阈值制（≈160 册）。

## 七、终局判据（照抄编排册 §一.3，别自定）

循环检查至**连续两轮问题=0** → 红蓝极限对抗（出问题直接修）→ 零遗留/零待办/零待裁 → 全部走 GitCommitGateway 落地 → 暂存件清理 → 端到端交付报告。
**当前状态：远未达成。** 第三棒未开新战场即离场，理由是 14 条线在飞＋自身上下文归零，此时加并发只增碰撞（今晚已被 FOREIGN_CHANGE 与 0xC0000142 各证一次）。**第四棒的第一动作＝§三 那条判定，不是新开战场。**
