---
ttl: task_bound
title: "F83 自动化班底（双引擎两班制：治理班×业务班）复飞扩卷案卷"
session: st-c7-mine-20260927
---

# F83 自动化班底（I 段 S8，总册行 `00_全环节总册.md:148`：F76｜全链｜P2｜S8）

> 本卷为**扩卷**（原 stub 1802 字符 < 2000 判据）。扩卷动因：独立普查测得本环节未达挖干标。
> **扩卷首要结论（红，两处）**：①本环节的编制真源册 `automation_crew_policy.md` 是 `ttl: permanent`，其 §4.1（:77）与执行序（:100）**把作业指令写向临时区 `docs/_working/automation_campaign/<岗>/`**，直接抵触根宪法 §9.4"永久区（ttl: permanent）禁引临时区"；②本环节两份载体的 TTL 属性相互矛盾（永久政策册 vs `completes_when: 2026-10-08` 的 task_bound 计划册），载体到期日即成本环节真源断链日。原 stub 判"挖干"，本卷改判 **未干**。

## 一、六向台账（2026-09-27 实证，基准=HEAD 3b4b1f86a1）

| 向 | 实测证据 |
|---|---|
| 实现件 | 载体二件，均在 HEAD（`git cat-file -e HEAD:` 双通过，§六 K1）：<br>①`docs/01_policies_and_standards/sop/automation_sop/automation_crew_policy.md`——frontmatter `doc_type: policy / ttl: permanent / status: active / version: 1.0.0 / date: '2026-09-24' / owner: ZephyrAlpha-Owner`；正文六节+两附录（§六 K2 实测锚点：:17 引擎与窗口、:28 两班编制、:64 铁律、:75 切碎四件套与重复指令、:108 协议、:115 附录A 任务清单、:121 附录B 业务全链挂点"挖→考→接→装→用→巡"）。<br>②`docs/_working/cmd_ledger/automation_master_plan.md`——frontmatter `ttl: task_bound / completes_when: 2026-10-08 GLM 免费期收官总报落账后归档 / session: st-autoplan-20260924 / date: 2026-09-24`；正文 :17 引擎与时间窗、:30 分工与写域互斥、:44 今晚关键路径、:52 真活清单、:72 日历逐日分派、:84 Qoder 白班任务卡、:109 铁律、:120 呈 Owner 裁定项。 |
| 在册态 | 政策册在权威三层：`docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml` 与 `capability_canonical_file_registry.yaml` 均点名 `automation_crew_policy`（§六 R1 两条 grep）；SOP 族索引在册=`sop/README.md`、`sop/automation_sop/index.md`；另被 `sop/audit_prompts_20_ai.md`、`sop/backtest_system_sop/sop_c_strategy_library_intake.md` 交叉引用。⇒ 在册面**满绿**（8 处引用，§六 R2 列表）。 |
| 消费者 | 无代码消费者（本环节性质=SOP/编制，非运行件）。M1 台账 dir4 `basis: none`、importers/config_readers/symbol_evidence 四列表全空（`.runtime/tmp/st-c7-m1-inbox/six_direction_ledger.yaml` environments.F83.dir4_consumer）⇒ 与定性一致，非漏采。真实"消费"=班前会话读册执行，**该消费不可机检**（§三.3）。 |
| 测试 | **0 件**（`git ls-tree -r --name-only HEAD \| grep -iE "test.*automation_crew\|automation_crew.*test"`，§六 T1）。SOP 类环节的测试替代物=可机检的编制一致性尺，本环节亦无（§六 G1）。 |
| 自动化触发 | 无（本环节自身即"编排版"，不持进程）。M1 dir6 wide=false/narrow=false 一致。班次落地借道 F76（计划任务群）与 F82（提交链队列）——该借道关系在总册 :148 行以"上游=F76"表达，但**F76 卷侧无对偶登记**（§四 缺 3）。 |
| 真源方向 | 冲突（本卷核心红判）：<br>①`automation_crew_policy.md` 头部自宣"操作唯一真源——编制、切碎机制、重复指令、铁律、协议"（§六 K3 原文行），<br>②同册 :14 净零声明="本册收拢 `docs/_working/cmd_ledger/automation_plan_discussion.md` 讨论册的口头机制成文，替代散落各包 LEDGER 的操作口径；不新增 gate/规则/注册表"——净零声明**合规**（明示替代，不新增真源），<br>③但编制载体的另一半 `automation_master_plan.md`（双引擎 L0-L6 排程）**同时是 F119 的实名实现件**（总册 :204 F119 行"双引擎自动化总计划…唯一真源 L0-L6｜上游=F83｜实现=`docs/_working/cmd_ledger/automation_master_plan.md`"）⇒ **两环节共指一册且互称唯一真源**（§四 缺 1）。 |
| 门禁与质量尺 | 册内铁律为人治条款（"违者夜班仲裁回滚"，§六 K4），**零 gate 支撑**：不存在"班次是否按编制执行""附录A 是否滚动"的机检尺（§六 G1）。 |
| 当前运行状态 | **黄偏红**：册在册、被 8 处引用、内容成文；但其作业指向的临时区路径合规性为红，且编制执行面完全无观测。 |

## 二、子模块三级枚举

1. **编制族**（政策册 §2 :28 起）
   - 二级=三席：Qoder（千问白班）｜ZCode（GLM 夜班）｜Owner 插单席
   - 三级=窗口与截止（表驱动，§六 K5 实测"席"字 22 处）：骨架口径"夜班 9 席+晨报插单"在本册 §2 编制表内实证；F119 侧另有 L0-L6 六级排程口径 ⇒ **同一编制两处成文（S8 席表 vs L0-L6 层级）**，是否同物两述未证（§四 缺 1 的一部分）
2. **机制族**（政策册 §4 :75 起）
   - 二级=切碎四件套：`docs/_working/automation_campaign/<岗>/` 每岗四件（册 :77 点名）
   - 三级=checkpoint 协议：册 :100 执行序第 2 步"读 `docs/_working/automation_campaign/<岗>/checkpoint.md`；已 DONE 则短报退出" ⇒ **permanent 册把幂等判定写成读 _working 文件**（合规红点本体，非引用而是执行指令）
   - 二级=重复指令处理、铁律（§3 :64）、协议（§5 :108）
3. **任务清单族**：附录A（册 :115）自述"随桥册滚动，本册只载编制与机制骨架"⇒ 清单不固化（设计正确，但使"班底实际跑过什么"无落点）
4. **业务挂点族**：附录B（册 :121）"挖→考→接→装→用→巡"六挂点 ⇒ 本环节与 F13-F29（考/装）链的挂点关系在此声明，是 L00 段"名义-内容错位"警示的落点之一（`00_skeleton_verified.md:104`：段目录非语义真源）。

## 三、接线四态独立复核

四态口径同批（已接线／半接线／装饰／死）。SOP 类环节的"接线"判据须替换为：**被引用（在册可达）+ 被执行（有观测）+ 自洽（无二真源）** 三腿。

1. **被引用腿=通（唯一确证腿）**：8 处在 HEAD 引用（§六 R2），含权威册 `rule_catalog_registry.yaml` 与 `capability_canonical_file_registry.yaml` 两处 ⇒ 名实可达。
2. **被执行腿=无观测（判装饰的关键）**：编制的执行证据应由 checkpoint 文件承担，但 checkpoint 在 `docs/_working/automation_campaign/` 临时区且**本卷实测该目录在 HEAD 内不存在**（§六 E1）。⇒ 无 checkpoint ⇒ 无"谁在何时跑了哪席"的落地面 ⇒ 三腿中第二腿为空。**按本仓纪律（在册≠在用、被引用≠被执行），本环节判：半接线偏装饰**。
3. **自洽腿=红**：与 F119 共指 `automation_master_plan.md` 且各自册头均含"唯一真源"字样（§一 真源方向行三条证据）⇒ 违反根宪法 §4.2"同真源可派生→必并／同域重复簇→收敛唯一"，须收敛为单一环节载体。本卷**不自行判定删哪一个**（属注册表/政策净删，Owner 门位）。
4. **TTL 矛盾腿（新发现）**：permanent 政策册的实体内容依赖一个 `completes_when: 2026-10-08` 的 task_bound 计划册；到期归档后政策册的"夜班 9 席"窗口口径将指向已归档件 ⇒ **可预见的断链**，且 §六 E2 可在归档前后各跑一次自证。
5. **死链检验**：本卷所有引用路径经 `git cat-file -e HEAD:` 实核；唯一不存在项是 checkpoint 目录，已作为**缺证据**而非**死链**记账（措辞区分有意为之）。

## 骨架勘误

无对骨架的否证：总册 :148 判 `built`、P2、S8、上游 F76/下游全链 —— 载体在盘、编制成文，`built` 成立。本卷的改判发生在**接线四态**与**挖干三态**两个层面（由 stub 的"挖干"改判为"未干"），不改骨架态。补一处细化：总册 F83 实现件列两册，未标注第二册是 F119 的实现件（交叠未在册面声明），建议随 §四 缺 1 处置一并补注。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | F83 与 F119 共指 `automation_master_plan.md`，两侧均称"唯一真源"（总册 :148 vs :204） | Owner 门位：同域重复簇的收敛方向（并环 or 分载体内字段）属环节净删/净改面，根宪法 §5 明列 high；本卷只交判据，不代裁 | P1 |
| 2 | permanent 政策册 :77/:100 把作业指令与幂等判定写向 `docs/_working/`（根宪法 §9.4 禁） | 施工：二选一——(a) 政策册改 `ttl: task_bound`；(b) checkpoint 落点迁至永久区（`docs/_working/` 之外的真源位）并把 :77/:100 改指新位。方向须与生命周期隔离条款的立法者确认，本卷不擅自改政策册 | P1 |
| 3 | F76↔F83 借道关系为单向登记（总册 F83 行有、F76 侧无对偶） | 施工：F76 卷补下游注记；若 F76 卷在他道在途则交其 owner（根宪法 §3.4 不代修） | P2 |
| 4 | 编制执行面零观测（checkpoint 目录不在 HEAD，无班后落账尺） | 施工：与 F119 的排程账本合并设计一次性落账件（生成器产出，禁手工清单，根宪法 §9.5） | P1 |
| 5 | 测试与机检尺双零（§六 T1/G1） | 挂起：SOP 类环节是否强制配尺属判据立法面；本卷提出需求不自行立尺 | P2 |
| 6 | task_bound 计划册 2026-10-08 归档后 permanent 政策册口径悬空 | 施工：归档批附带迁移政策册 §2 窗口表（可预见的机械改注） | P2 |

## 五、自审闸三态

**未干（并明确否证原 stub 的"挖干"自审）。**
理由逐条：①原 stub §五 写"挖干（册面两册实存+分工条款实证）✅"，但**未测三腿中的"被执行腿"**，也未发现与 F119 的二真源冲突与 §9.4 的 permanent→_working 违规，其"无悬空：未发现引用本册的死链"一句只做了死链检验、不等于执行面检验；②本卷新暴露的缺 1（重复簇）与缺 2（生命周期违规）任一未闭，都不允许称已挖干；③缺 4 的执行观测面需要设计落账件，超出挖矿车道权限。
本卷的诚实边界：`automation_campaign/` 是否曾在历史 HEAD 存在、以及是否被 `.gitignore`/清理策略排除，本卷**未做全史检索**，故"零观测"仅指"HEAD 无 + 无在册尺"，不引申为"从未跑过班"。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
cd /d/ZephyrAlpha
# K1 双载体在 HEAD
for p in docs/01_policies_and_standards/sop/automation_sop/automation_crew_policy.md \
         docs/_working/cmd_ledger/automation_master_plan.md \
         docs/_working/cmd_ledger/automation_plan_discussion.md; do git cat-file -e HEAD:$p && echo "OK $p"; done
# K2 政策册骨架（期望六节+两附录）
grep -n "^## \|^### " docs/01_policies_and_standards/sop/automation_sop/automation_crew_policy.md
# K3/K4 唯一真源自宣与铁律条款
sed -n '12,16p;64,70p' docs/01_policies_and_standards/sop/automation_sop/automation_crew_policy.md
# K5 席位数（原 stub 记"夜班 9 席+晨报插单"，此处为可复算字面计数）
grep -c "席" docs/01_policies_and_standards/sop/automation_sop/automation_crew_policy.md
# E1 执行面零观测自证（期望：HEAD 内无该目录）
git ls-tree -r --name-only HEAD docs/_working/automation_campaign/ | wc -l
git grep -ln "automation_campaign" HEAD | head -5
# E2 permanent 册指向临时区的两条（期望 14/77/100 三处，其中 77/100 为指令级）
grep -n "docs/_working" docs/01_policies_and_standards/sop/automation_sop/automation_crew_policy.md
# T1 测试面（期望 0）
git ls-tree -r --name-only HEAD | grep -iE "test.*automation_crew|automation_crew.*test" | wc -l
# R1/R2 在册与引用面
grep -ln "automation_crew_policy" docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml
git grep -ln "automation_crew_policy" HEAD
# X1 F83/F119 共指同一册（两条总册行对照，判重复簇的原始证据）
grep -n "^| F83 \|^| F119 " docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md
# G1 机检尺缺位（期望零命中）
grep -in "automation_crew\|checkpoint" docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | head
```
