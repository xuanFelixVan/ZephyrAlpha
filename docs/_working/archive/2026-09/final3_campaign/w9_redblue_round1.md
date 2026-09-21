---
ttl: task_bound
completes_when: W8-2 四桶派发消化本件 ISSUE 后归档（最迟 2026-10-19）
title: W9 红蓝对抗 R1——st-final3 战役今日落地对抗验收（红队）
owner_session: st-final3-20260919
date: 2026-09-19
---

# w9_redblue_round1.md — 红蓝对抗 R1：st-final3 战役今日落地对抗验收

> session=st-final3-20260919（红队轮）｜性质：只攻击不修复，发现记档不代修。
> 对象：W5-1 审计（1848907185）/ W4-7 差距表（b7aeaa39f2）/ w9 台账 A14（1d68dd056c）/ 三批红证（9949f018b5、745d6491b0、1192d9cc8e）/ W2-BM3 件3（61cd32eae5）。
> 判定口径：**PASS=攻不倒**（攻击动作做实、判定存活）；**ISSUE=坐实问题**（证据链在案）。证据等级：A=本会话机读/代码直读/工具实跑；B=推断。

## 总评（先行）

**13 攻 2 倒**：攻击面一 3 抽样全卫（含 capacity_params 动态加载逃逸攻击不成立）；攻击面二 2 抽样全卫（非名字撞车）；**攻击面三倒 2 件**（resource_schedule=硬 ISSUE：在飞生成器输出区+33 处 truth_source 指针被判"已结案可归档"；pattern_line=软 ISSUE：8 处活引用未登记联动点）；clean_exam_e2e 卫。抽查四 3 红证复跑全卫、抽查五数字对账全卫（含一次自摆乌龙如实记录，见 §4②）。

## 攻击面一：W5-1 四簇审计"保留/退役"判定反证 —— PASS（3/3）

### ①a 抽"保留"件1：decisiongraph 消费门禁是否真读 decision_* 表
- 攻击动作：直读 `src/zephyr/gov_enforcement/commit_gates/panorama_alignment_gate.py` 全文 + `scripts/governance/d5_architecture/generators/align_panoramas.py`。
- 证据（A 级）：门禁真实存在且为 commit 硬门（GateSpec priority=830；`domain_mismatches` 三图内部不一致→`return False` 阻断，panorama_alignment_gate.py:234-249）；触发清单含 decisiongraph_schema.py/apply_decisiongraph.py（:66-78）。关键深挖一层：门禁调 `run_alignment()`，而 align_panoramas.py:811 `decision_conn = get_decisiongraph_pg_connection()`→`_fetch_decision_nodes()`（:422-423）**真实执行 `SELECT ... FROM decision_nodes` 与 `FROM decision_layers` SQL**（:430、:463）——不是仅"触发路径提及"，是门禁判定链真实读 decision_* 表。
- 判定：**PASS**（W5-1"保留"判定的门禁级消费方证据成立）。

### ①b 抽"保留"件2：resource_optimization.yaml 收敛方向唯一消费方
- 证据（A 级）：`ops_alert_feed.py:91`（`_RESOURCE_CFG_RELPATH="config/resource_optimization.yaml"` 真源注记+读键函数 :101）、`process_incubator.py:153,162`（读 pressure_thresholds）、`health_monitor.py:58`（_load_pressure_thresholds）、`resource_optimization.py:357`（engine 读 pressure_thresholds）。
- 判定：**PASS**（多活消费方逐一定位坐实）。

### ①c 抽"退役候选"：capacity_params 零消费判定找动态加载逃逸
- 攻击动作：四路逃逸搜索——①全仓 `capacity_params` 字符串（src/scripts/tests/config）；②动态拼接（`capacity.{0,4}_?params`、`_params.yaml` 模式）；③config 目录通用 glob 装载器（`glob("*.yaml")` 类）；④独有键反查（max_script_workers/global_max_concurrent/lsg_concurrent_max/shard_count）。
- 证据（A 级）：代码侧命中仅 `config_validator.py:78` 结构性必填键+自身测试；battle_map_diagram 的 design_capacity 为展示性读（:1734 实测在）；嫌疑件 `check_capacity_slo_ssot.py` 实读 **capacity_slo.yaml（另一文件）**，不构成本册消费方；独有键零代码命中（shard_count 命中为 `meta/_concurrency.py` 本地 ShardRouter 缺省参数，与容量册无关）；发现的 glob 装载器均作用于 catalogs/gates 目录非 config/ 容量册。
- 附带核实：W5-1 自引证据行号准确（generate_battle_map_diagram.py:1734 属实）；docs/03_modules 各蓝图大量"capacity_params=SSoT"表述均为死文字（无对应加载器），与审计"头部声明未找到加载器"结论一致。
- 判定：**PASS**（退役候选判定扛住动态加载/拼路径攻击）。

## 攻击面二：W4-7 TDM 吸收"已有"判定语义核验 —— PASS（2/2）

### ②a 抽 #9（遗产 4.10 最终综合评分 → TDM-E-L3-03/-05/-08）
- 攻击动作：只读解析 `config/trading_decision_map.yaml`（4533 行）逐块比对语义，并核 module_ref 文件在盘性。
- 证据（A 级）：TDM-E-L3-03（yaml:1454）decision_question="短线池和波段池分别怎么打分、怎么合流"+五分制双池打分（子节点 L3-03-1 module_ref=signal_ashare/fine_scoring_engine.py 五分制细则）；TDM-E-L3-05（:1605）顺位排序"活下来的候选按全市场顺位谁排最前"（module_ref=signal_fundamental/selection_confidence.py）；TDM-E-L3-08（:1785）"最终谁进买卖点环节（候选池+顺位排序+否决后清单=最终候选池 10-20 只）"（module_ref=signal_ashare/core/candidate_pool_aggregator.py）。遗产 #9 四要素（综合排序定买卖清单/历史因子分+前瞻合成/综合评分排序）中**决策问题与输出形态被三节点链完整承载**：打分→排序→终清单；"前瞻分布因子合成"子能力被如实降为车道 E 候选而非占"已有"。5 个 module_ref 文件全部在盘（ls 实测 OK）。
- 判定：**PASS**（语义真实覆盖，非名字撞车；判定介质差异按 D108 灰度/离散原则归"已有"成立）。

### ②b 抽 #10（遗产 L5 执行算法 → TDM-E-L4-06/-01/-14）
- 证据（A 级）：TDM-E-L4-06（yaml:2276）decision_question="大单怎么拆（EXA 六件选型：TWAP/VWAP/ICEBERG/IS/POV/ALT）"+algo_note 含">500 万单必拆；单笔≤盘口一档 50%；冲击成本预算 0.3%"——对遗产 #10"怎么分批下单最小化冲击（VWAP/TWAP 参数优化）"构成超集承载；module_ref=ex_sor/core/algo_selector 实件在盘。附带发现（不改判定）：TDM-E-L4-14 algo_note 自认执行质量反馈环断链（"选择器代码还没消费它，断链实证 2026-09-10"）——该断链属**遗产点之外的增强件**，不影响 #10"已有"判定（遗产仅要求 VWAP/TWAP+冲击成本）。
- 判定：**PASS**。

## 攻击面三：w9 台账 A14 目录"误埋活件"攻击 —— ISSUE×2 / PASS×1

### ③a resource_schedule/（判 A=已结案可归档）—— **ISSUE（硬，坐实）**
- 攻击动作：ls 目录+全仓 git grep 目录内文件名引用（排除自引用）+追引用消费链。
- 证据链（A 级）：
  1. `config/resource_profile_registry.yaml` 含 **33 处** `docs/_working/resource_schedule/...` 引用（`plan_ref:` ×1 @:49 + `schedule_truth_source:` ×32 @:671-966+），把战役件 `resource_schedule_panorama_plan_v1.md` 登记为排班真源；
  2. 该注册表是活件：消费方 `scripts/governance/apply_resource_plan.py`（:676 等 6 处读 `schedule_truth_source` 做 path 解析；:311 `方案文件不存在→PlanError` 硬失败）、`scripts/ops/schedule_overview.py`、`generate_resource_morning_report.py`/`generate_resource_week_view.py`，且有 2 个注册计划任务（register_resource_regen_check_task.ps1 / register_resource_sampler_scan_task.ps1）；
  3. **该目录今日仍在被写**：`generate_resource_morning_report.py` 头注（MOD-RESCHED-MORNING）"[CONSUMERS] 晨审 Owner/AI 会话（读 docs/_working/resource_schedule/morning_report/latest.md）"+"输出 markdown 到 docs/_working/resource_schedule/"——`morning_report/` 目录 mtime=2026-09-19 15:17（本审计当日）。
- 结论：台账把一个**在飞生成器的输出区+活注册表的 truth_source 指针区**判为 A 类"W8-1 归档批"，归档即产生 33 处悬空真源指针+生成器输出路径断裂。台账行未登记任何联动点（对比 W5-1 对 capacity_params 备料 4 处联动点的做法）。**坐实 ISSUE**：A 判定误标，或至少 W8-1 前必须先完成指针迁改+输出区外移。
- 修复建议（记档不执行）：morning_report 输出区迁 `.runtime` 外常驻位或 docs 非归档域；registry 33 处 truth_source 改指迁移后路径；之后再判 A。

### ③b pattern_line/（判 A）—— **ISSUE（软，联动点未清点）**
- 证据（A 级）：`capability_canonical_file_registry.yaml` 5 条目直指本目录（:5107/:5151/:5159/:5163/:5187）；3 个常驻模块蓝图声明"设计真源"在本目录（docs/03_modules/.../factor_lifecycle_runner/blueprint.md:19、pattern_evidence_certifier/blueprint.md:19、pattern_lifecycle/blueprint.md:19）；**production 代码头** `src/zephyr/signal_ashare/strategy_signal/pattern_lifecycle.py:5` [CONSUMERS] 行写明"协议文档=docs/_working/pattern_line/resurrection-protocol.md"。
- 结论：目录内容归档不丢（移 archive/ 保留），但 8 处来自永久件/活登记册/production 代码头的引用在台账行零登记，归档后全部悬空。按 W5-1 自立的"联动点备料"标准衡量，A 判定依据不足。**坐实软 ISSUE**。

### ③c clean_exam_e2e/（判 A，短名 clean_exam）—— PASS（含编排器工单移交专项核）
- 证据（A 级）：战役已真实收口——`00_master_ledger.md` status=closing + `2026-09-18-campaign-final-report.md` status=final（端到端结论/关键数字/事故四件全留痕）；**编排器工单移交证据成立**：遗留清单 #1"断点 E4：execution_report 生产者接线……编排器'出手'前置工单，下一班"已转入活台账 `final3_campaign/w8_3_owner_signature_book.md`（git grep 实锤），断点事实亦在 production 代码 `ex_core/execution_report_producer.py:20` docstring 双保险留痕，归档不灭失。
- 残留小刺（不构成 ISSUE）：该目录两处 production 代码引文（execution_report_producer.py:20、cleanup_runtime_tmp_residue.py:69 判据出处）归档后路径悬空，属 provenance 注记级。
- 判定：**PASS**。

## 抽查四：规则审计批红证真实性复跑 —— PASS（3/3，全带命令+退出码）

### ④① W1-A0（9949f018b5）generate_missing_index_md 隐藏目录修后行为
```
mkdir -p .worktrees/redblue_r1_a0/docs/redproof && 造 2 个 .md（无 index.md）
python scripts/governance/d1_structure/generate_missing_index_md.py --root .worktrees/redblue_r1_a0/docs/redproof --dry-run
→ "扫描 1 个目录，1 个缺失 index.md: 缺失: ./" exit=1
```
- 判定：**PASS**（checked=1>0=修后行为；修前该场景按 commit 记载为"扫描 0 个目录"恒假绿 exit 0）。工棚即造即撤（rm -rf 实测）。

### ④② W1-B #352（745d6491b0）编码 fail-closed
- 第一次复跑（自摆乌龙，如实记录）：GBK 样本放 `.runtime/tmp/*.md`（未跟踪）→ exit=0。**经查这是设计内行为非缺陷**：裁定#352 明文"非 tracked 文件维持现行为"，commit message 红证配方即为"未跟踪 GBK 样本 exit 0"。红队首攻姿势错，攻的是设计允许面。
- 按原配方复跑（tracked 面）：
```
T=scripts/governance/_archive/one_off/oneoff_commit_audit02.py（tracked 归档件，字节级替换 GBK 注入）
python scripts/governance/d7_code/check_encoding.py --file $T
→ "INJ-007 FAIL: ... is not valid UTF-8 (tracked source file, must re-encode as UTF-8) — 'utf-8' codec can't decode byte 0xba" exit=1
字节级还原 → sha256 一致（sha-equal=YES）→ 同命令 exit=0；git status 该件 clean
```
- 判定：**PASS**（红/绿双向与申报一致；未跟踪面 exit 0 与裁定口径一致）。

### ④③ W1-C2 #353③（1192d9cc8e）中文路径 AD 幻影清扫
```
造 .runtime/tmp/redblue_红队幻影样本.py → git add -f → rm（成 AD 态）
git -c core.quotepath=true status --porcelain=v1 | grep ^AD
→ AD ".runtime/tmp/redblue_\347\272\242\351\230\237\345\271\273\345\275\261\346\240\267\346\234\254.py"（带引号八进制转义=修前逃逸形态）
裸实例调真实 _sweep_phantom_staged_adds('st-final3-20260919', set())
→ SWEPT: ['.runtime/tmp/redblue_红队幻影样本.py'] exit=0（_unquote_git_path 解码成功）
复核：AD 残留=0；git ls-files --cached 无该件；盘上无该件
```
- 附带安全核查：清扫前 `git status --porcelain` AD 计数=0，本次清扫零误伤他会话条目。
- 判定：**PASS**（修后行为坐实：中文路径幻影被解码并 SWEPT）。

## 抽查五：W2-BM3 件3（61cd32eae5）B-15 数字防伪 —— PASS（2/2）

### ⑤a 门值一致性（卡↔报告）
- 预注册卡 `prereg_card_b15_bucket_switch.md` §7（frozen）：存活门=前向窗净 Sharpe **≥1.4** 且复利 maxDD **>−20%**；1.4=裁定#361 原文，−20% 声明为卡自冻结值。报告（b15_bucket_switch_narrow_test_report.md）门值、0/9 判定、"唯一拦截项=Sharpe 门"与卡完全一致；报告 §4.4 对 B 变体在场期 Sharpe 1.458 的"条件读数不满足门"防误读声明与卡 §7"门=全窗净 Sharpe"冻结口径一致。
- 判定：**PASS**。

### ⑤b 数字对账（报告↔results csv）
- 落盘件 `.runtime/tmp/bizmine/b15/combos.csv`（eng 主判口径 9 行）逐位核对：
  - 抽查组合 进攻×B：csv `sharpe=0.939, sharpe_on=1.458, ann_ret=0.1413, maxdd=-0.0796, days_on=106` ↔ 报告表 `0.939 / 1.458 / +14.13% / −8.0% / 106`——**逐位一致**；
  - 旁证组合 稳健×A：csv `-0.635/-0.635/-0.0832/-0.116/256` ↔ 报告 `-0.635/−0.635/−8.32%/−11.6%/256` 一致；
  - 全表机械判定：eng 主判最大净 Sharpe=0.939<1.4 → **0/9 成立**；Owner-001（o1）口径最大=0.958<1.4 ↔ 报告"最佳仍为进攻×B=0.958"一致；10bp 敏感性拉低幅度 0.045-0.078 落在报告声称的 0.02-0.10 区间。
- 判定：**PASS**。

## 回执（六要素）

1. **对抗结论**：13 攻 2 倒——攻击面一（3/3 PASS）、攻击面二（2/2 PASS）、攻击面三（2 ISSUE：resource_schedule 硬 / pattern_line 软；clean_exam_e2e PASS）、抽查四（3/3 PASS）、抽查五（2/2 PASS）。
2. **证据等级**：全部 A 级（代码直读/yaml 只读解析/工具实跑带退出码/csv 逐位机对）；唯一 B 级推断=③b"归档后引用悬空"的影响面估计（引用为 provenance 性还是 load-bearing 未逐一运行验证）。
3. **未完成+原因**：A14 其余 11 个 A 目录未抽样（Owner 指定抽 3）；ISSUE 修复不在本轮授权（只攻不修）；W4-7 其余 9 个"已有"判定未抽（指定抽 2）。
4. **红线遵守**：只读攻击零修复；红证样本即造即撤（工棚 rm -rf、GBK 件 sha256 一致还原、幻影件 SWEPT+盘净）；未触碰他会话在途件（workspace 其余脏件零接触）；写前 reaper 存活已核（last_run=2026-09-18 19:10:55）；capability_lookup 反查已留审计。
5. **防误杀/防吞**：capability_canonical_file_registry.yaml 工作区曾有同 SID 死会话 abort 造成的 MM 漂移（staged −20/unstaged +20 镜像）——实测 HEAD 本就含那 5 条 token、工作区与 HEAD 逐字节一致，未吸收任何外来差异；本次载体批净增=本件 token 一条。
6. **查询复用**：本轮全部探针命令与退出码已内嵌 §4 各节；combos.csv 校验脚本为一次性内联（.runtime/tmp，不入库）。
