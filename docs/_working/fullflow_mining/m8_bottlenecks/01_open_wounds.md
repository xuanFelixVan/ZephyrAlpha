---
ttl: task_bound
---

# M8 堵点深挖 · 开放伤口清单（01_open_wounds）

> 立册 2026-09-25 01:4x ｜ 车道 M8（会话 st-commitspeed-tbl-20260924）｜ 只读挖矿+本目录零 commit。
> 口径：汇总各战役卷宗/台账登记的**未修项**（grep 关键词=待裁/遗留/后续项/待 Owner，2 大 grep 批量取证 + 逐册核读），
> 按 **可机械施工 / 须Owner / 已过期失效（含已闭合）** 三档分类；每行带出处路径。HEAD=77129e94b1（2026-09-25 01:13）。
> 总计 **55 条**：可机械施工 22 ｜ 须Owner 24 ｜ 已过期失效/已闭合 9。

## 一、可机械施工（修法已知、无 Owner 门位，按依赖排序）

| # | 伤口 | 修法（已登记） | 出处 |
|---|---|---|---|
| A1 | W4 env 泄漏止血重投（q-0025 dead→0027 在队；HEAD `git_commit.py` grep prev_gateway_env=0 实证未落） | 从当前 dev 重拉 scratch，重贴 2 处还原（只加还原不删置位），复跑红/绿+ruff/format 后重投；补丁锚 `.runtime/tmp/csx_msg_w4.txt` | `docs/_working/commit_speedup_campaign/90_verification/HANDOFF_NEXT_SESSION.md` §D/§E.1 |
| A2 | 包3 完整性基线 HEAD 派生（MQ-1/2/3/4 已裁待执行；csx-p3b 在飞） | check() 读 HEAD blob 非滞后 json；CHANGING_IN_COMMIT 仅 own-scope+R-2/R-5 双哨兵同批；_GATES_DIR 指真身+空清单 stderr+低于阈值即红 | 同上 §E.2 ＋ `90_verification/MAX_RULINGS.md` ＋ `30_gate_census/P3_integrity_head_derivative_prep.md` |
| A3 | 包5 步2/3 删全局 env 写（前置=W4 落地；D1/D2 设计完未落） | 顺序铁律：先补 per-spawn 注入面，最后删 W1/W2/W3 写点（逆序=POST-COMMIT-GUARD 判 forged 吃掉已落提交） | 同上 §E.3 ＋ `10_d1_d2/D2_env_flag_leak.md` §4/§8 |
| A4 | replay 仪器 3 件停工未收口（`_tree_view.py`/`replay_gate_verdicts.py`/`test_gate_replay_harness.py` 已写、R1_design 未出；HEAD 无 derived_dirty_ledger 实证未落） | 先独立验证 3 件能红能绿 → 包8 三簇合并（重放 100→1000 笔 verdict 全等出厂判据）→ 包9 own-tree → 包7 缓存键；Owner 令：只合并/降档/diff 化，禁删 | 同上 §E.4 |
| A5 | 包10 止血（B5）：门前置短路红件 3 秒判死（现 218s）+attempts 退避移毒药队首 | commit_queue.py（已解锁） | 同上 §E.5 |
| A6 | 包11 合批去抖 | 判据见 00_MASTER_PLAN | 同上 §E.6 |
| A7 | 包13 余下：对账生成器+own_scope 机生补全（T14 批七遗留；gate_registry own_scope:true=33 实证未变） | 名册对账生成器+own_scope 机生补 53 条 | 同上 §E.6/§D「批七 T14」 |
| A8 | 包14 红蓝极限对抗（7 场景每把尺先证能红；前置=各功能包完工） | — | 同上 §E.7 |
| A9 | 包15 收尾：文档袋命名+token 落、**99_FINAL_REPORT.md 未建**（git ls-tree 实证 0）、清 csx_* 脚本/worktree/release claim | 0002/0006/0013/0014 文档袋死批按「整册回 HEAD 只注入本批条目+补 token」统一落 | 同上 §E.8/§D |
| A10 | p13 门禁时长 ms>=1.0 盲区过滤（q-0029 在队；HEAD `commit_gate_registry.py:111` 实证仍在，42-44% 门禁时长不可见） | 盲区过滤阈值修（0029 已在队） | `00_root_cause_synthesis.md` §1.4/RC-8 ＋ HANDOFF §D |
| A11 | RC-3 残余：belt 换血饿死（积压致 lease 不释放、安全点不到）机制未根治 | 每 N 件强制安全点（小改） | `00_root_cause_synthesis.md` RC-3 |
| A12 | f18d34c8 自动化 lifecycle 自相矛盾（completed/runCount=31 但 nextRunAt=18:00；已「不重建防双发」人工兜底，机制未修） | 一次性自动化终态后清 nextRunAt 或下架 | `docs/_working/cmd_ledger/overnight_decisions_20260924.md` R39 |
| A13 | classify_workspace_wip.py claim 归因读快照陈旧（判 library 四件 claim=st-ailayer，lock_files 实判 CLEAN） | 归因改读 lock_files 真源 | 同上 R40 勘误 |
| A14 | lib_assets 写授权误挂 depgraph_reader（writer 角色零授权，反直觉） | 授权位修正 | 同上 R41 新发现 |
| A15 | batch_creation_tokens.py 不支持「改名换绑」（file::token 键变更被判缺条，本次靠顺序编排绕开） | 工具改进候选：改名换绑原生支持 | `docs/_working/commit_speedup_campaign/90_verification/t13_rename_report.md` §五.3 |
| A16 | 主区暂存区残留 0006 死批旧路径 A 条目（本车道禁 git add 未清理） | 走 --enqueue 由 serializer worktree 干净暂存区落地/清理 | 同上 §五.4 |
| A17 | 清洗三引擎接线立项（cleaning_rule_engine/cleaning_anomaly_engine/data_anomaly_alerter 建成零调用、DSL 无 YAML 承载；09-24 grep 复核仍零调用） | 挂 supply_sentinel 同款宿主+config/ 规则 YAML，先 flag 后 block 灰度；报总筹排期（非真裁定） | `docs/_working/fullflow_mining/m1_data/pending_rulings.md` R-M1-06 |
| A18 | M1 补挖：冷库归档 3 环节未挖 | 补挖波作业 | `docs/_working/fullflow_mining/00_orchestration.md` §四 M1 行 |
| A19 | M2 活体假绿 2 处：kline_sector_intraday 假 SUCCESS 自 09-10；GPU 巡检口径矛盾 | 前者转 M1 波处置；后者 T1 完赛后修 | 同上 §四 M2 行 |
| A20 | M5 地雷 top3：PostSettlement 注册脚本被 bc76efe3bf 覆盖回退／tilib 夜回填住 tmp 夜夜 exit1／SimBridge 09-24 静默断链嫌疑 | 按 05_master_health_table 逐雷修复（施工 S123 已派，余量跟踪） | 同上 §四 M5 行 |
| A21 | order_daemon 建成未接线＝全流通缺口 | 接线施工 | 同上 §四 M5 行 |
| A22 | 各车道补挖项：M4 PG 图书馆确认+管线路由挖矿属性／M5 备份冷储 3-2-1、FBL、环境启动链、性能水位台账／M6 报告生成环节／管线路由 M4M5 属性 | 补挖波 | 同上 §四 M4/M5/M6 行 |

## 二、须Owner（净删面/资金面/门禁语义/修宪/跨域口径，AI 禁自裁）

| # | 伤口 | 门位与建议 | 出处 |
|---|---|---|---|
| B1 | rules_integrity_db.json 出库净删（MQ-1 已裁 HEAD 派生制，DB 降观测件；出库动作单列） | tracked 文件净删=high tier 门位；终报单列一行，获批后随收尾批出库并撤 `commit_derived_sync.py:24/:49` 白名单条目 | `docs/_working/commit_speedup_campaign/90_verification/MAX_RULINGS.md` MQ-1 |
| B2 | F2 k=4 通道开工签批（S18-R3/裁定#320） | 前置①②③④全绿；⑤「7 天>40 车道」观察窗口径请裁定 | `docs/_working/flash_speedup/90_report.md` §5 P-1 |
| B3 | F5 DC 白名单净增 .json | AI 建议**不净增**（.json 证据归宿=.runtime/data） | 同上 §5 P-2 ＋ `91_fresh_triage_and_rulings.md` §3 P-2 |
| B4 | 门禁退役+进程级 YAML 解析缓存同批（§4.2 触发率审计） | 真 100/h 杠杆；CREATE-GUARD P50 40-41s（1.67MB 册重复解析）=TOP 阻断 | 同上 §5 P-4 ＋ `91_fresh_triage_and_rulings.md` §3 P-4 |
| B5 | N-1 BLUEPRINT-FORMAT own-scope 化（一个外来占位 .py 挡全场直连；gate_registry own_scope:true=33 实证未变） | 对齐宪法 §3.1，或按 §3.3 登记全仓扫描理由；禁 AI 自动门禁语义 | 同上 §5 P-5 ＋ `91_fresh_triage_and_rulings.md` §2.10 |
| B6 | N-2 共享 index 无已落地路径保护（刚落地内容被陈旧 bulk-add 回退/落地新文件被 staged 成 D） | bulk-add 前置校验或 POST-COMMIT 守护扩展（新增守护=flag 门位） | 同上 §5 P-6 ＋ §2.11 |
| B7 | N-4 pid=0 心跳 90s 窗口竞态根治 | 心跳窗口参数化/预检前自动续心跳（触 SessionRegistry 语义，AI 禁自裁） | 同上 §5 P-7 ＋ §2.13 |
| B8 | cleanup-final 遗留修复包九件（Owner 全批）：①翻译 dedupe ②克隆对退役 ③fail_open 重投 ④审查器失明×6 修复 ⑤凭据占位 ⑥裁定册确认 ⑦模拟盘 17 件终批 ⑧压测 Phase B 30 路 ⑨板块分钟K 回补 | 逐件批 | `docs/_working/cmd_ledger/overnight_decisions_20260924.md`「遗留修复包任务清单」 |
| B9 | Owner 待定三件：Tushare key 轮换／修宪挂图书馆入口／12 项 AI 层批文（已登记不阻塞） | — | 同上「Owner 待定事项」 |
| B10 | R-M1-01 CH 影子/隔离表退役（8+ 张留观表占 c1_market；留观无 TTL） | ①archiver 正门 export→verify→drop 进冷库后净删 ②RENAME 归 _retired 库；建议①+7 天留观计时器；0.5 天/表 | `docs/_working/fullflow_mining/m1_data/pending_rulings.md` R-M1-01 |
| B11 | R-M1-02 daily_valuation 幽灵行+零值行清理（77,668/259,238 行落 14 周末幽灵日+全 0 行） | 破坏性 DB 操作三步验证；建议 trade_calendar NOT IN 出 dry_run 清单→批→删，写侧日历闸同批立项 | 同上 R-M1-02 |
| B12 | R-M1-03 rate_decision_calendar 435 行 epoch 残留（decision_date<1990 占 14%） | 随 R-M1-02 同批出 dry_run 清单 | 同上 R-M1-03 |
| B13 | R-M1-04 l2_tick 空表（0 行）退役评审 | 先跑 waste_table_scanner 出证据再裁 | 同上 R-M1-04 |
| B14 | R-M1-05 宪法/骨架册「16 表交叉轴」口径修正（代码真源 _XREF_SPECS=13 轴） | 修宪面：等长替换改「13 轴」+基准注；#ARCH-351「哨兵 16 表」旧口径另立注 | 同上 R-M1-05 |
| B15 | R-M1-07 TradingWatchdog/RestartMiniQmt 计划任务退役或换道（两任务 Disabled 长期挂册） | 走 D2 退役登记；若 tick 桥需看门狗则立桥版新件 | 同上 R-M1-07 |
| B16 | R-M1-08 #ARCH-351 退役映射表优先序（miniQMT 清退 24 任务无退路，open P1，裁定#376 已授权设计） | TF02 16 全裸任务最险优先，走 01 册 B1 修法 | 同上 R-M1-08 |
| B17 | R-M2-1 GPU 规模口径三套并存（总筹已裁选①勘误为 T0 200/T1 3700/T2 900，留晨报请 Owner 确认；「24990格」全仓零命中） | 晨报确认，防下班会按 24990 验收 | `docs/_working/fullflow_mining/m2_backtest_sim/pending_rulings.md` R-M2-1 ＋ `00_orchestration.md` §四 M2 行 |
| B18 | R-M2-2 成本两真相分裂（考尺 5bp vs ADV 分层；已裁文档口径采纳+毕业生复考双口径披露，动考尺路线留晨报） | 晨报 | 同上 R-M2-2 ＋ orchestration M2 行 |
| B19 | R-M2-4 六段词表三套映射两套冲突（产线 r4/r2 反向，同闸宽差 75%；Owner 在案） | 维持双轨+披露；切词表=生产挂图与 GPU 条件轴两边同批 | 同上 R-M2-4 |
| B20 | R-M2-5 模拟盘订单语义映射扩面（已裁维持只防御至 GPU 毕业生产真实候选） | Owner 定扩面优先级（现建议=不扩） | 同上 R-M2-5 |
| B21 | R-M2-6 配比真源双头（auto_mount PP-001 vs pf_alloc 都动 sleeve 权重；已裁选①，留晨报） | 裁 pf_alloc 为唯一配比真源、auto_mount 只提名 | 同上 R-M2-6 ＋ orchestration M2 行 |
| B22 | M3 三项 Owner 门位待裁：KillSwitch 持久化／env 单因子信任绑定／死工厂+75% 手工册净删内收 | — | `docs/_working/fullflow_mining/00_orchestration.md` §四 M3 行 ＋ `m3_governance/` 各分册 |
| B23 | 门禁退役三候选（PURE-SHIM/STASH-ACCUMULATION/RECONCILER-FILE-OPS）+PANORAMA legacy 位挂起 | Owner 净删门位 | `m8_bottlenecks/00_root_cause_synthesis.md` RC-4 |
| B24 | 09-11 死信清零收口的遗留 P1⑤/⑥ 未结案（「根因已修」三次证旧账） | 复核后结案或立案 | `docs/_working/2026-09-11-commit-queue-dead-zero-closure.md`（00 册 §四 引） |

## 三、已过期失效／已闭合（留档防复发，勿再施工）

| # | 原伤口 | 闭合证据 | 出处 |
|---|---|---|---|
| C1 | P-3：S18-R1~R4 四张裁定书待签 | **已闭合**：#333 签署四裁定生效+#334/#320 修订前提，P0 复核四条通过（tc_04 卡 D4 行 A 级取证，2026-09-21 刷新） | `flash_speedup/91_fresh_triage_and_rulings.md` §3 P-3 ＋ `flash_speedup/00_master_ledger.md` |
| C2 | N-3 预检逃生旗映射漏配 | **已治本** `be934b079d`（4 测全绿；HEAD commit_preflight.py escape 探针=14 复测一致） | `flash_speedup/90_report.md` §4/91_fresh §2.12 |
| C3 | flash 战役 7 件交付件卡 capability 册（token 无法登记+注册表被外来连续占用） | **已落 HEAD**：git ls-tree 实证 flash_speedup 90_report/91_fresh/F2-F9 DESIGN×14 件在库 | `flash_speedup/91_fresh_triage_and_rulings.md` §4（实测反证闭合） |
| C4 | M0 骨架三项待裁 | 总筹已裁（研究域不编入/管线路由 M4M5 互引） | `00_orchestration.md` §四 M0 行 |
| C5 | M2 待裁 6 案 | 总筹已裁：②⑤文档口径采纳、③池基悬空=T2 冻结至池基修复；①④⑥转晨报（移 B17-B21，原案不再独立挂账） | 同上 M2 行 ＋ `m2_backtest_sim/pending_rulings.md` |
| C6 | st-library-final 死会话遗物（#410 执行态悬空） | R40 代投 q-0002（5 件 288 行）+R41 增枝五步全通+E2E 实证，图书馆班收官；R42 clobber 缺陷修复+回填防护落地 | `cmd_ledger/overnight_decisions_20260924.md` R40/R41/R42 |
| C7 | flash 遗留 3 死信 q-0001/0002 判定 | **有意不复 requeue**（reconciler/integrity 派生批=requeue 会复活旧屎+快照陈旧），处置已定 | `flash_speedup/90_report.md`:98 |
| C8 | t13 遗留⑤ scratch 内 3 件卷宗副本（untracked） | 随 scratch 一次性处置，不入队 | `commit_speedup_campaign/90_verification/t13_rename_report.md` §五.5 |
| C9 | commit_system_opt 战役遗留 | **全部有主，零悬案**（06_final_report §五 实证） | `docs/_working/commit_system_opt/06_final_report.md` §五 |

> 归并注记：原「文档袋 0002/0006/0013/0014 死批」伤口已并入 A9（包15 收尾）统一施工，不独立挂账。

## 四、复核命令（5 分钟口径）

```bash
# 1) 三档计数自证
grep -c "^| A" docs/_working/fullflow_mining/m8_bottlenecks/01_open_wounds.md   # 22
grep -c "^| B" docs/_working/fullflow_mining/m8_bottlenecks/01_open_wounds.md   # 24
grep -c "^| C" docs/_working/fullflow_mining/m8_bottlenecks/01_open_wounds.md   # 9
# 2) 未落抽验（应非 0/33/0）
git show HEAD:scripts/git_commit.py | grep -c prev_gateway_env        # 0=W4 未落
git show HEAD:docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | grep -c "own_scope: true"  # 33=包13 未落
git ls-tree -r HEAD --name-only | grep -c 99_FINAL_REPORT             # 0=包15 未开工
# 3) 已闭合抽验
git ls-tree -r HEAD --name-only | grep -cE "flash_speedup/(90_report|F2_prereq)"  # >=2=C3 闭合
# 4) 出处抽读
sed -n '/遗留修复包任务清单/,+2p' docs/_working/cmd_ledger/overnight_decisions_20260924.md
sed -n '110,125p' docs/_working/flash_speedup/91_fresh_triage_and_rulings.md
```

## 五、三态自审

**挖干可施工**：55 条均有出处路径+闭合/未落双态实证（git show HEAD 探针 12 枚复测），A 档按依赖成链可直接派工。
**待挖**：M4/M5/M6/M7 车道补挖项完成后其 pending_rulings 尚未立册（m3-m7 无 pending_rulings.md，M3 三项 Owner 待裁暂寄 orchestration §四 行内）——补挖波收口时归册。
**待裁**：B 档 24 条全部已有一行一案建议，归 Owner 晨报批量批；本车道不再新增裁量。
