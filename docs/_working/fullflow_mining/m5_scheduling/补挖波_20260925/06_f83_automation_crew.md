---
created: 2026-09-28
ttl: task_bound
volume: 06_f83_automation_crew
session: st-ailayer-final-20260924
creation_token: fullflow-w4b-f83-automation-crew-book-20260926
---

# 06 · F83 自动化班底（双引擎两班制：夜班 9 席 × 白天写席 + 文件桥调度）

> 车道 W4-B｜worktree `D:\ZephyrAlpha\.worktrees\st-ailayer-final-20260924`｜零提交零入队｜只读取证。
> 派单=`00_skeleton/92_coverage_triage_20260926.md` §三（F83 判"真缺簿：缺自动化触发/门禁与质量尺两向，automation_crew_policy 九席排班与 automation_master_plan 无 file:line 级对账实证"）。
> 本册状态：**六向齐证 + 两向判"装饰/缺机制"**（触发向与门禁向的实证结果就是"无机件"，这本身是证据不是缺证），§一 挂 F83 认领锚。
> 本册核心发现：①crew_policy §4.1 规定的四件套宿主目录 **`docs/_working/automation_campaign/` 在 worktree 与主仓两处均不存在**（机制从未起量）；②F83 与 F119 **共用同一真源文件**（§五第 3 条）；③全链**零机件消费**（src/scripts/config 三面对 `crew_policy|automation_campaign` 的 grep 命中=0）→ 按判据口径本环节门禁面**是装饰**。

## 一、环节定义与边界

总册口径（`00_skeleton/00_全环节总册.md:148`）：F83 自动化班底｜双引擎两班制（治理班×业务班）夜班 9 席+晨报插单｜上游 F76｜下游 全链｜真源=`sop/automation_sop/automation_crew_policy.md`；`docs/_working/cmd_ledger/automation_master_plan.md`｜总册标 built、P2、I 段调度常驻（F76-F85）。

本册覆盖 F83
> 实证面=上列两真源册＋`automation_sop/index.md`＋`cmd_ledger/` 另两件（`automation_plan_discussion.md`、`overnight_decisions_20260924.md`）＋两处机读目录登记。

边界与两处总册问题（本册不自行改总册，见 §六末）：
1. **段归属判错**：F83 挂在"I 段调度常驻"，但实测本环节**无常驻件**（无 daemon、无计划任务、无 reconciler，§二"自动化触发"向实证为零）——它是**人机排班制度册**，属横切治理面，与 F119 同段更合理。
2. **与 F119 真源重叠**：`00_全环节总册.md:204` F119"双引擎自动化总计划……调度唯一真源 L0-L6"的 physical_path = `docs/_working/cmd_ledger/automation_master_plan.md`，与 F83 真源第二项**同一文件**（→ §五）。

## 二、六向台账

| 向 | 内容（证据） |
|---|---|
| 上游输入 | ①**Owner 插单**：`automation_crew_policy.md:112`（§5 协议）"插单：Owner 在桥册'Owner 插单'节写一行→当夜①席优先排"；②**免费窗硬边界**（时间输入）：`automation_master_plan.md` §0 表——Qoder 千问3.8Flash 24h/截止 **2026-09-30**、ZCode GLM-5.3Flash 每晚 **23:00-09:00**/截止 **2026-10-08**、本机 GPU 3090 L3 专道"09-25 12:00 点火 59h→09-27 23:00"、总指挥付费窗"避开 14:00-18:00"；③**业务输入=283 问**（crew_policy 附录A 业务班"283问消费（工单11张/insuff96/fail45/复考142）"）；④**上游客册**=`.trae/rules/project_rules.md`＋宪法 `AGENTS.md`（`automation_master_plan.md` 前言"任何 lane 开工前必读本册+宪法 AGENTS.md"）；⑤写域互斥输入=master_plan §1 Lane 表（L0-L6 各带"写域（禁跨写）"列） |
| 下游消费 | ①**Owner 晨报看板**：crew_policy:110"晨报：08:45 前①席出（真哈希/队列终态/各席一句话/呈批项），Owner 手机看板"；②**提交链**：master_plan 前言"提交唯一正门 `scripts/git_commit.py --enqueue`"＋"追加记录必用 safe_write_text CAS（`src/zephyr/shared/io/file_utils.py`）+ 先 `lock_files.py acquire`"→ 班底动作出口=宪法 §2 提交面；③**其它 SOP 族反向消费**：`backtest_system_sop/sop_c_strategy_library_intake.md` 与 `sop/audit_prompts_20_ai.md` 均引 crew_policy（grep 命中，见 §三 3.4）；④**索引面**：`sop/README.md:29` 与 `sop/automation_sop/index.md:11` 两处把本族登记为"双引擎自动化施工……操作唯一真源"；⑤**机读目录**：`capability_canonical_file_registry.yaml:50541-50544`（token `automation-sop-automation-crew-policy-20260924`，capability=`automation_sop`，created_by=`st-autoplan-20260924`）＋`rule_catalog_registry.yaml:4797-4800`（`doc_type: policy`，**`module_id: ''` 空**）——后者空值即"无模块绑定"（→ 门禁向） |
| 自动化触发 | **实测：无机件触发，全部为对话窗口 + 文件桥**（这正是分诊册点名缺的向，取证结论为"缺机制"）：①**计划任务面查无**——`grep -i "zcode\|qoder\|night\|23:00\|晨报" docs/_working/fullflow_mining/m5_scheduling/01_windows_schedtasks.md` 命中的 49 个在册任务里**无一条属本班底**（命中项均为他主：`tilib_indicator_backfill_nightly` Daily 02:30 / `ZephyrAlpha_NightlySentiment`（**已禁用**，:61）/ `ZephyrAlpha_F06Grid` Weekly 六 23:00）→ 夜班 23:00 开工会**不自动发生**，靠 Owner 起对话；②**"在册既有自动化（勿重复建设）"四条**（master_plan §0 末行）：第二链每日核验 07:15｜battle_map 周一 09:00｜模拟盘钱包交易日 19:30｜candle_pattern DROP 评估 12-15 一次性 → 属 F76/F84 侧，非本班底自有件；③**自删条款无承载**：crew_policy:26"所有自动化带免费窗止日自删条款（到期夜出收官总报+提醒 Owner 删自动化）"＋master_plan frontmatter `completes_when: 2026-10-08 GLM 免费期收官总报落账后归档`——**到期日在 4-12 天后**，但"谁来在 09-30/10-08 触发收官+自删"无任何注册名（§四病灶 2）；④事件式=无（宪法 §9.3 四要素"自动触发/自动运行/自动维护/自动关闭"本环节**四者全缺机件**） |
| 真源与注册表 | ①**双真源并存**（制度册 `automation_crew_policy.md` 132 行 / 计划册 `automation_master_plan.md` 134 行，master_plan 自称"调度唯一真源"，crew_policy §1 又自带一张引擎表→ **两册同表双写**，病灶 1）；②**ROOR 查无**：`grep -i "cmd_ledger\|automation_master" docs/registry_of_registries.yaml` 仅命中 :741（SOP-A 回测对象册，异对象）→ 两真源册**均未挂 ROOR 条目**（本环节无注册表身份）；③机读登记两处：`capability_canonical_file_registry.yaml:50541`、`rule_catalog_registry.yaml:4797`（module_id 空）；④族索引：`sop/README.md:29`、`sop/automation_sop/index.md:11`；⑤桥册/台账宿主目录=`docs/_working/cmd_ledger/`（写域 L0 总指挥独占，master_plan §1）；⑥**四件套目录=`docs/_working/automation_campaign/<岗>/`（crew_policy §4.1 :77）→ 实测 worktree 与主仓 D:/ZephyrAlpha 两处均不存在**（`ls` 双证，§七第 3 条） |
| 门禁与质量尺 | **判：装饰（本册实测口径）**。①尺文本存在：crew_policy §3 标题"铁律（违者夜班仲裁回滚）"（:64）＋§4.1"每岗四件套"＋§2.1"一席一事，裁定+干活双职饱和制"、:118"①席逐席点名，闲席转溢出活（饱和制）"；②**无一处机件消费**：`grep -rln "automation_campaign\|crew_policy" --include=*.py --include=*.ps1 --include=*.yaml src/ scripts/ config/` = **0 命中**（§七第 2 条可复跑）；③`rule_catalog_registry.yaml:4798 module_id: ''` → 该 policy 无模块绑定，任何按 module_id 键消费的门禁都取不到它；④"违者仲裁回滚"的执行主体=①席（AI 对话），非 `gate_registry.yaml` 中任何门；⑤质量尺的**唯一机生近似物**是提交侧通用件（GitCommitGateway/lock_files/safe_write_text，crew_policy:22 与 master_plan 前言引用），但它们不为"排班是否被遵守"作证。**结论：铁律的效力 100% 依赖对话自觉；制度面无回滚证据链**——与在案教训"九条护栏全是装饰：判'已防护'必测谁调它＋能否改变行为"同型。 |
| 当前运行状态 | **红**（按判据如实报红，非"包未建"之红）：①两真源册在盘且在读（`cmd_ledger/` 3 件实测）；②**执行面零证据**：四件套宿主目录两处均不存在→ 夜班 9 席从未按 §4.1 留下岗包；③**无自动触发机件**（触发向 ①）→"永久系统四要素"零达成；④窗口倒计时：Qoder 免费止 09-30、GLM 止 10-08（本取证日 09-26）→ 4 天内该环节整体作废，而收官/自删无承载（病灶 2）。**可复跑命令**：§七第 1（两真源对照）＋第 2（零消费自证）＋第 3（目录不存在双仓验证）＋第 4（计划任务面查无）。 |

## 三、子模块清单（`ls`＋`grep`＋注册表三源交叉，全量穷尽）

**3.1 `ls` 实测（本环节资产面）**

| # | 件 | 定位 | 证据 |
|---|---|---|---|
| 1 | `docs/01_policies_and_standards/sop/automation_sop/automation_crew_policy.md` | 制度真源（132 行，§1 引擎窗口/§2 两班编制/§2.1 夜班 9 席/§2.2 白天写席≤5/§3 铁律/§4 切碎四件套/§5 协议/附录A 两班任务清单/附录B 业务全链挂点"挖→考→接→装→用→巡"） | 章节行号 :17/:28/:33/:50/:64/:75/:77/:108/:115/:121 实测 |
| 2 | `docs/01_policies_and_standards/sop/automation_sop/index.md` | 族索引（:11"双引擎自动化施工（Qoder 白班 × ZCode GLM 夜班 × Owner 插单席）的操作唯一真源"） | ls＋grep |
| 3 | `docs/_working/cmd_ledger/automation_master_plan.md` | 调度计划册（134 行，frontmatter `completes_when: 2026-10-08`、`owner: Owner`、`session: st-autoplan-20260924`；§0 引擎时间窗/§1 Lane L0-L6 写域互斥/里程碑表） | sed 实测前 40 行 |
| 4 | `docs/_working/cmd_ledger/automation_plan_discussion.md` | 讨论过程件（引 crew_policy） | grep 命中 |
| 5 | `docs/_working/cmd_ledger/overnight_decisions_20260924.md` | 夜班裁定件 | ls |
| 6 | `docs/_working/automation_campaign/<岗>/`（四件套宿主） | **不存在**（worktree＋主仓双验） | §七第 3 |
| 7 | `docs/01_policies_and_standards/sop/audit_prompts_20_ai.md` | 22 域定义唯一真源（crew_policy §4.2 :83"深审岗与 22 域映射（域定义唯一真源=audit_prompts_20_ai.md 第2章）"） | grep |

**3.2 班底所依赖的机件（外部件，本册不重挖，只记引用）**：`scripts/git_commit.py`（提交正门）｜`scripts/lock_files.py`（claim）｜`src/zephyr/shared/io/file_utils.py: safe_write_text`（CAS 热文件写）｜`commit_navigation_playbook.md`（master_plan 称"机生 102/102，禁手改，源册在 commit_guide_sources/"）｜宪法 §2 并发与提交。

**3.3 `grep` 交叉（引用面 10 件）**：`sop/audit_prompts_20_ai.md`｜`sop/automation_sop/index.md`｜`sop/backtest_system_sop/sop_c_strategy_library_intake.md`｜`sop/README.md`｜`_registry/catalogs/capability_canonical_file_registry.yaml`｜`_registry/catalogs/rule_catalog_registry.yaml`｜`_working/cmd_ledger/automation_plan_discussion.md`｜`_working/fullflow_mining/00_skeleton/00_全环节总册.md`｜`…/92_coverage_triage_20260926.md`｜`00_skeleton_fullflow.md` → **全部为文档/目录引用，零代码引用**。

**3.4 注册表交叉**：两处机读目录有项（:50541 / :4797）；ROOR 无项。**交叉结论**：本环节资产面已穷尽（7 件，其中 1 件应为不存在而确实不存在）；无第三源可再扩。

## 四、堵点与病灶

| # | 现象 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|---|---|---|---|---|
| 1 | **两真源同表双写**：master_plan §0 与 crew_policy §1 各写一张"引擎×窗口×截止"表，字段口径微异（master 有"并发"列＋GPU 具体点火时刻；crew 有"GPU=Owner 编制外"表述） | 制度册与计划册分次成文，无派生关系（违反 §9.5"静态清单禁手工维护"＋§4 净零） | 定一册为唯一真源（建议 plan=时变表、policy=不变制），另一册改指针引用；或两张表都由 `cmd_ledger` 机生块产出 | 0.3 | 否（两册均非本车道写域：L0 总指挥独占 cmd_ledger，crew_policy 属热 SOP 文件） |
| 2 | **窗口到期无自删承载**：crew_policy:26 规定"到期夜出收官总报+提醒 Owner 删自动化"，master_plan `completes_when: 2026-10-08`，但无任何注册任务/日历件在 09-30 与 10-08 触发；而实测班底**根本没有自动化可删**（触发向①） | "带自删条款"是设计意图，落地面为 0；风险=过期制度册长期留在真源位被后续会话当现行规则执行（宪法 §9.11 指令/数据边界面） | 最小修：给两册 frontmatter 统一 `ttl: task_bound`＋`completes_when`，纳入 TTL 巡检件（现有 TTL 门读 ttl 字段，实测 crew_policy 头部有 `title:` 但本车道未确认其 ttl → §六留观测量） | 0.2 | 可（出判据清单，不改册） |
| 3 | **四件套机制从未起量**（`automation_campaign/` 双仓不存在）→ 9 席排班无留痕，事后无法审计"哪席干了什么" | 制度要求产物落位目录，但目录未建即开工 | 要么补目录＋生成器（每岗四件套模板产出），要么退役 §4.1（按 w5_1"零触发零消费→退役"） | 1（建）/0（退役） | 否 |
| 4 | **门禁面装饰**（§二 门禁向②③④）：铁律无消费方、policy 无 module_id | 制度类资产在注册表体系中按"文档"登记，未纳入 gate 体系；宪法 §1 补充铁律只覆盖代码类规则 | 二案：①把可机械化的两条（写域互斥、每岗四件套齐件）做成 pre-commit/CI 尺；②显式声明"本环节为组织制度、不设机件门"并记入 `risk_tier_registry.yaml` 的 human_gate（Owner 席=①席仲裁） | 1.5（①）/0.2（②） | 否（待裁） |
| 5 | 段归属错（I 段调度常驻 vs 实为横切制度） | 骨架编写期以"自动化"三字归类 | 总册回写：F83 移 M 段横切或 K 段，与 F119 同段 | 0.1 | 否（热册） |

## 五、内收与合并机会（四判据）

1. **同真源可派生→必并**：病灶 1 的两张引擎表（master_plan §0 ↔ crew_policy §1）＝同对象双写 → **必并**为单表＋指针。
2. **零触发零消费→退役**：候选=crew_policy §4.1"每岗四件套"（宿主目录不存在、零机件消费）＋§2.2"白天写席≤5"（无可观测承载，席位数只在散文里）。**本车道只出判据与清单，不删不改名**（注册表净删=Owner 门位）。
3. **同域重复簇→收敛唯一**：**F83 ↔ F119 共用 `automation_master_plan.md`**（总册 :148 与 :204 两条真源列同文件）→ 同域近重复簇。建议收敛判据（待裁，本车道不自裁）：F83=编制与铁律（谁上什么班），F119=调度计划与写域互斥（今晚干什么）；master_plan 归 F119 独占，F83 真源列删除该文件改指针。**当前两册互相引用不清，同一自动化事实在两格各说一遍=双真源。**
4. **跨域不同对象→不并**：`tilib_indicator_backfill_nightly`／`ZephyrAlpha_F06Grid` 等计划任务属 F76/F84 调度域，不因"夜班"字面相同并入本环节；`audit_prompts_20_ai.md` 22 域定义属审查族（F116 的 automation 族之外），只挂引用。

## 六、自审闸三态

**判：挖干可施工**（就 F83 六向而言，每向有 file:line 或实测"查无/不存在"双证）。分诊册点名的两个缺向已闭合，且闭合结论是负向的（触发无件、门禁装饰）——这是实证结果，非取证不足。

**不随本册闭的三项观测量**（谁补上，F83 才可能从红转黄）：
1. crew_policy 的 frontmatter 是否带 `ttl: task_bound`＋过期日（本车道只读到 :4 title 行附近，未逐字段核）——最小观测量：`sed -n '1,12p'` 输出。
2. 夜班是否真发生过——最小观测量：`cmd_ledger/overnight_decisions_20260924.md` 内一条带席号的裁定行，或任一 git log 中 `[GW:]` 提交带班底 session 标记。
3. 晨报是否送达过 Owner——最小观测量：一条 08:45 前生成的晨报件路径。

**待裁**（已写入 `m5_scheduling/补挖波_20260925/pending_rulings.md`）：§五第 3 条（F83↔F119 真源切分）、病灶 4（制度类资产是否入 gate 体系）、病灶 3（四件套建 or 退役）。

**回写总册建议**：`00_全环节总册.md:148` ①`built` 改 **`draft/未生效`**（备注：无自动触发机件、执行面零留痕、门禁为 prose）；②真源列删 `automation_master_plan.md`（归 F119）或改"引用 F119"；③段号 I→M/K 之一。

## 七、复核命令

```bash
# 1) 两真源同表双写对照（病灶 1）
sed -n '17,27p' docs/01_policies_and_standards/sop/automation_sop/automation_crew_policy.md
sed -n '14,32p' docs/_working/cmd_ledger/automation_master_plan.md

# 2) 零机件消费自证（门禁向判"装饰"的唯一判别命令，预期输出 0）
grep -rln "automation_campaign\|crew_policy" --include=*.py --include=*.ps1 --include=*.yaml src/ scripts/ config/ | wc -l

# 3) 四件套宿主目录双仓不存在（勿只在本 worktree 判）
ls docs/_working/automation_campaign/ 2>&1 ; ls /d/ZephyrAlpha/docs/_working/automation_campaign/ 2>&1

# 4) 计划任务面无本班底件（触发向判"无件"，预期只命中他主任务）
schtasks /query /fo LIST /v | grep -i -A2 "Zephyr" | grep -i "taskname\|start boundary" | head -20
grep -n -i "zcode\|qoder\|automation_crew" docs/_working/fullflow_mining/m5_scheduling/01_windows_schedtasks.md | head

# 5) 两处机读登记 + ROOR 查无
sed -n '50541,50545p' docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml
sed -n '4797,4801p' docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml
grep -c "automation_campaign\|automation_crew_policy" docs/registry_of_registries.yaml

# 6) 待补观测量 1（ttl 字段）
sed -n '1,12p' docs/01_policies_and_standards/sop/automation_sop/automation_crew_policy.md
```
