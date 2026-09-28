---
created: 2026-09-28
ttl: task_bound
volume: 95_declaration_pass_F2
session: st-ailayer-final-20260924
creation_token: fullflow-w4f2-declaration-pass-20260926
---

# 95 W4-F2 车道 · 正向声明施工记录（25 环节逐格二选一）

> 工作面=worktree `D:\ZephyrAlpha\.worktrees\st-ailayer-final-20260924`；零提交、零入队、零 claim、零改尺、零改生产码。
> 尺=`scripts/governance/fullflow/generate_fullflow_crosscheck.py`（判据定稿，本车道未动一字）。
> 认领判据（改尺后）＝三处正向声明位：文件名 `fnn`／`#` 标题行／行首 `本册覆盖 Fnn`（或 `covers:`）。

## 〇、开班实测（非记忆）

- 开簿尺读数：`links=122 covered=77 uncovered=45`。
- **本车道 25 格开簿全部 uncovered**：F76 F77 F78 F87 F90 F91 F92 F93 F97 F98 F99 F101 F102 F104 F105 F106 F108 F109 F110 F111 F113 F114 F117 F118 F119 均在 `uncovered_ids`。
- **重大发现：W4-A 补锚面集体为死锚（战役性缺陷，非本车道可修）**
  `m1_data/01_ingest.md:14` 等 **13 处**锚写作 `> 覆盖锚点：本册覆盖 Fnn（…）`——行首是 `>` 引用符，
  **不满足 `_claim_tokens()` 的 `s.startswith("本册覆盖")`** ⇒ 改尺后这批锚一律不判认领。
  实测佐证：`F09 F62 F64 F68 F69` 在他车道册内同样带死锚，至今仍列 uncovered。
  本车道做法：只对自己判"确属承载"的格，**新写行首声明**（不动他车道、不撤他人文字）；
  判"仅邻接/仅引用"的格**不予激活**（见 §三、`93_true_gap_list_20260926.md`）。

## 一、方法（每格两问，硬判据）

1. 该册主题/六向台账/子模块清单是否**确实承载**此环节对象（须指到册内实际引用的模块锚点/file:line/台账行），而非"提过一句"或"引用了别的战役"？
2. 承载 → A：§一 段内加行首 `本册覆盖 Fnn`＋逐环节"哪一节凭什么"理由；不承载 → B：只登记 `00_skeleton/93_true_gap_list_20260926.md`，**零声明零借用**。
3. 每格加行前均已 `grep` 该册标题行与 §一/§三 实际内容（理由列即核验产物）。

## 二、A 类 13 格（环节 → 册 → 凭什么覆盖）

| 环节 | 册（`docs/_working/fullflow_mining/` 下相对路径） | 凭什么覆盖（册内实际锚点） |
|---|---|---|
| F76 | m5_scheduling/01_windows_schedtasks.md | §二 总账（项目相关任务 49＋禁用 8＋快照 Running 6＋LastTaskResult 码表）、§四 A–E 五族任务全表、§五 注册脚本↔在册任务漂移净零；§一 上游=26 支 register_*.ps1 |
| F77 | m1_data/01_ingest.md | §二 "自动化触发"行 APScheduler 常驻＋ZephyrAlpha_DataScheduler 实测 Running＋schedule.yaml 29 槽；"真源"行 tasks.yaml 271 任务；"上游"行 tick_subscriber.py:1456 |
| F78 | m5_scheduling/02_inrepo_daemons.md | §一 即 commit_belt_daemon 专章（册题 `zephyr.gov_enforcement.rule_bridge.commit_belt_daemon`）＋§八 监护关系总图＋§九 自审闸三态 |
| F87 | m4_ai_layer/01_ai_layer_six_families.md | §三-8 redline 九件（negative_list NL-1..6／negative_list_gates／session_env_guard／sev_route／drop_gate／no_delete_manifest）＋10 模块 importlib 实测＋三 gate 挂载 in_process_gate_registry.yaml:707-725（149/150/151） |
| F91 | m4_ai_layer/02_capability_lookup.md | §一 capability_lookup.py 1672 行/MOD-INF-037 定义；§二 六向（真源 capability_canonical_file_registry.yaml、summary 实测 388/367/21/27/2、两 gate、.runtime/lookup_audit 审计面）；§四 卡片覆盖面 |
| F92 | m4_ai_layer/04_meta_question_pg.md | §一 PG meta_question 3 表＋写入唯一通道；§二 register 校验链（入库闸五要素机检/查重/净零/q_id 机生）＋snapshot FORBID_MANUAL_EDIT＋vocab gate；§三 逐问三态；§四 PQ-0099 机检 |
| F98 | m3_governance/03_registry_families.md | §三 gate 相关四册＋§四 gate 三册台账（180 机生／102/102 自洽／own_scope 33-80-67／REG-GATE-001=rule_enforcement/_registry.yaml 实测 91 与 ROOR 自洽）＋§二 下游 gate_auto_registrar 与两 reconciler |
| F104 | m3_governance/01_runtime_guards.md | §3.6 SessionRegistry/session_concurrency.py:295 与 :266/:786/:861/:108 逐入口＋lock_files.py 1659 行 claim/TTL/_is_stale:161/_claim_expired_and_idle:225/mutex:116 |
| F106 | m3_governance/03_registry_families.md | §四 术语三层三册实测行（279/94/7776）＋翻译 loader 三层消费＋TRANSLATION-COVERAGE Layer4 reconciler priority=951 |
| F108 | m3_governance/03_registry_families.md | §四 risk_tier_registry.yaml 行（tier_1_governance、tier high\|medium\|low＋default_tier: low）＋§二 下游"risk_tier 门位判定" |
| F109 | m3_governance/03_registry_families.md | 册题即注册表族治理；§三 ROOR 底数（77 个 registry_id 实测）＋§四 逐册台账（含 script-manifest 991）＋§四末卫生漂移＋§五 G1/G3 三口径漂移与 w5_1 净零判据 |
| F111 | m6_frontend/01_dashboard.md | §三 三行：旧 Panel 大屏 14 Tab（app_panel.py:19-27,457-486）／components 17 件（含 experiment_history lru_cache+reset）／services_registry 35 启动项四态灯+分级启停+审计；§四-4/5、§六 退役待裁 |
| F118 | m1_data/04_cold_storage.md | §一 D/F/G/离场 3-2-1 布局；§二 "真源与注册表"行 INFRA-STORE-003＋storage_map.md 手册、"自动化"行 :58、"门禁"行 :43 五重安全阀；§五 S2/S3/S5 对 :42/:44/:60-64 逐行核账 |

改后尺实测：`covered 77 → 90`、`uncovered 45 → 32`，且每格 workbooks 归属**唯一且等于上表指定册**（无串认领、无夹带他环节）。

## 三、B 类 12 格（拒绝认领＝本车道成绩单核心）

F90 F93 F97 F99 F101 F102 F105 F110 F113 F114 F117 F119
逐格理由/要开哪本/建议车道＝`00_skeleton/93_true_gap_list_20260926.md`（本车道建册并追加 12 行）。

其中 **4 格是"本可刷绿而主动拒绝"**（W4-A 已留有死锚文本，激活即变绿）：

| 环节 | 拒绝激活的死锚位置 | 拒绝理由（一句话） |
|---|---|---|
| F97 | m3_governance/01_runtime_guards.md:15 | 真源在他营（commit_speedup C1 卷宗），引用面≠承载面，W4-A 自己亦判"勿放宽" |
| F99 | m3_governance/02_reconcilers.md:13 | gov_drift 30 检测器本体零簿，册内只有 drift_* reconciler 邻接面 |
| F105 | m3_governance/04_coverage_gaps.md:12 | secrets.py 本体零簿，册内只有真空矩阵一行（且门侧亦系引用 C1） |
| F114 | m6_frontend/02_api_server.md:11 | 真源 notification_router.py 实测存在却全仓零引用，册内仅 `/api/ops-notifications` 端点一行 |

另 1 格为**不越界代他车道认领**：F119（W4-B 的 `m5_scheduling/补挖波_20260925/06_f83_automation_crew.md` §一 自设边界只声明 F83、§五-3 把 F83↔F119 真源切分提交待裁）。

## 四、已认领域的残余面（登记不改判，供后续取证派单）

- F98：03 册承载"91 门禁 canonical＋gate 三册台账"面，**GatePipeline 执行序与 MAD 准入算法**未展开 → 残余取证向。
- F108：03 册为门位册台账级（结构+默认档+消费方），**18 条域分级逐条与四类 Owner 门位映射**未展开。
- F111：01 册承载旧 Panel/组件族/服务注册；宪法口径"app_panel 退役时点"仍在他册待裁（§六）。
- 以上均属"册已承载该环节对象，个别子面未穷尽"，与"沾边册"（§三 四格）不同层，故判 A 并如实标价。

## 五、文件清单（本车道全部改动）

改（各加 1 行声明，正文零改）：`m5_scheduling/01_windows_schedtasks.md`、`m1_data/01_ingest.md`、
`m5_scheduling/02_inrepo_daemons.md`、`m4_ai_layer/01_ai_layer_six_families.md`、`m4_ai_layer/02_capability_lookup.md`、
`m4_ai_layer/04_meta_question_pg.md`、`m3_governance/01_runtime_guards.md`、`m3_governance/03_registry_families.md`、
`m6_frontend/01_dashboard.md`、`m1_data/04_cold_storage.md`（共 10 册 10 行，含 4 行多环节并写）。
新建：`00_skeleton/93_true_gap_list_20260926.md`、`00_skeleton/95_declaration_pass_F2.md`（本件）。
派生件（尺自动写）：`00_skeleton/91_machine_crosscheck.yaml`。

⚠ 待总筹处置的两项（本车道不越权）：
1. 本件与 93 册**未列入生成器 `NON_WORKBOOK_RELS`**——现判据下行首声明/标题行不含 F 号，实测未自认领（13 格归属逐条已验），但为长期卫生建议登记为非作业簿面（只加排除条目，不动判据）。
2. §〇 的死锚残留文本（13 处）与他车道 5 格（F09/F62/F64/F68/F69）账面未覆盖，须由归属车道或总筹决定"规范化为行首声明"或"改措辞为邻接面"，本车道未代改。

## 九、复核命令

```bash
python scripts/governance/fullflow/generate_fullflow_crosscheck.py --quiet
python -c "import yaml;d=yaml.safe_load(open('docs/_working/fullflow_mining/00_skeleton/91_machine_crosscheck.yaml',encoding='utf-8'));print(d['coverage_matrix']['totals'])"
# 逐格归属（应只见 §二 指定的那册）
python -c "import yaml;d=yaml.safe_load(open('docs/_working/fullflow_mining/00_skeleton/91_machine_crosscheck.yaml',encoding='utf-8'));rs={r['id']:r for s in d['coverage_matrix']['segments'].values() for r in s['rows']};[print(f,rs[f]['status'],rs[f]['workbooks']) for f in 'F76 F77 F78 F87 F90 F91 F92 F93 F97 F98 F99 F101 F102 F104 F105 F106 F108 F109 F110 F111 F113 F114 F117 F118 F119'.split()]"
grep -rn "^本册覆盖" docs/_working/fullflow_mining/ | grep -c .   # 新增声明行计数
```
