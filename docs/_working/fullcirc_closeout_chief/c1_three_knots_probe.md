---
ttl: task_bound
completes_when: c1 三死疙瘩只读排查结论被总筹消费（0105/0116/0104 处置裁定落账或归档）后随战役归档
---
# c1 三死疙瘩只读排查报告（F3R 重发车道）

> sid=st-tclose-c1probe2-20261004 ｜ 日期=2026-10-05 ｜ 性质=只读排查（唯一写=本报告）
> 底账=night_sweep/ledgers_archive/T1C1_ledger.md + W3C1_ledger.md（0105/0116/0104 三卡原始描述已对出）
> 关键前提：现势=PG 账本投影时代；涉注册册处置一律**走意图API**；数据面操作一律走 DatabaseService。

---

## ① 0105 · 七个 0 字节死库

### 证据（2026-10-05 实测）

全名单 7 个（`find data .runtime -maxdepth 4 -size 0 -name "*.db"`，与 W3C1"原 6+progress.db 新现"吻合），**全部 birth=mtime（创建后从未写入）、全部未被 git 跟踪、活代码零再造向量**：

| # | 路径 | 0 字节诞生时点 | 引用面现势（本车道复核） |
|---|------|--------------|------------------------|
| 1 | data/databases/depgraph.db | 2026-07-20 09:26 | census 31 .py 提及；现活面（src/scripts/tools 非 _archive）**19 文件**仍携字符串；真源已迁 PostgreSQL（`scripts/governance/_shared/constants.py:88`"P2迁移后：depgraph.db 已迁移到 PostgreSQL"；`DatabaseService.get_depgraph_conn()` 返 psycopg2；ROOR REG-ARCH-PANORAMA-001/REG-DEPGRAPH-001 physical_path=postgresql://localhost:5432/depgraph）；fms_deadref_baseline.yaml:2110 已立案 category D |
| 2 | data/depgraph.db | 2026-08-04 00:59 | 0 个带路径真指针＝与 #1 同名重复立案（census 同判） |
| 3 | data/databases/integrator_progress.db | 2026-07-24 02:38 | 唯一消费者 `src/zephyr/data/progress_store.py` 默认路径实为 `data/integrator_progress.db`（**41MB 活件，2026-10-05 仍在写**）＝历史路径残迹；fms_deadref:2194 已立案；另 config/data_supply_chain_map.yaml 有册面提及待同步 |
| 4 | data/databases/progress.db | 2026-07-24 14:03 | 精确路径活代码引用=0 |
| 5 | data/runtime/progress.db | 2026-09-15 23:50（"新现"件） | 精确路径活代码引用=0；盘面 09-15 疑似相对路径误解析产物，无再造向量 |
| 6 | data/databases/scheduler_progress.db | 2026-08-14 07:15 | census 判 retire：0 引用 0 消费者 0 规则指向 |
| 7 | data/zalpha_metadata.db | 2026-09-10 00:44 | **两处死指针均已治愈**：trae_034 :40/212/560 现指 governance.db（W3C1 消项属实，本车道复核）；`validate_cross_references.py:225-228` 已带 09-27 修正注释改指 governance.db；残余提及均为备份命名族（database_manager.py 的 `zalpha_metadata_*.db` 备份名）与注释/表名，非文件消费；fms_deadref:2938 已立案 |

前棒机生底账：`docs/_working/total_command_closeout/wave1a/store_liveness_census.md`（store_liveness_probe.py 产出，含逐库三态建议）与 `dead_store_triage.md` §6 补丁文本（trae_034/validate_cross_references 两补丁**均已落地**）。

### 定性

7 个全是**前时代 SQLite 残壳**：真源三向已迁干净（任务=governance.db、依赖图=PostgreSQL、进度=data/integrator_progress.db），死件无消费者、无再造向量、无 git 历史。0105 出口判据"0 字节库数→0"在数据面已**具备成立条件**，唯差删除/退役动作本身。trae_034 改指支已消，未竟项只剩两件：退役支（Owner 门位）+"34 处 depgraph 引用归属未登记"（现活面 19 文件清单+census jsonl 即归属底稿）。

### 处置建议

1. **7 个全部"冷库归档+删"**（按 INFRA-STORE-003 存储地图移 G:/backup 或 F:/zephyr_cold 留证后删工作区文件）；scheduler_progress.db 可免归档直删（三层双空）。删除前按 RULE-DATA-OPS 三步验证走一遍（必要性/真实性/可逆性——本报告即必要性证据）。
2. 同批登记：fms_deadref_baseline 已立案 3 件补处置批注，其余 4 件补立案后同批销案——**册面动作走意图API**。
3. "34 处 depgraph 引用归属"以 census jsonl+本车道 19 活文件清单为底稿落归属登记（归档件不改、活件确认真源已 PG 化，多数为注释/遗留字符串，逐条标注即可）。
4. **需 Owner 二次确认：是**（退役/删除支在 0105 卡面 approval_required=True，禁代做）。本报告已把确认成本压到"照单勾选"。

---

## ② 0116 · 两红蓝测试件"真死残件"

### 证据

- 波 1B.1.8 原始对象（10_wave_plan.md:57）：`test_redblue_governance.py` / `test_redblue_robust.py`，连同 dead_triage.yaml/r2 同列"从未入库件捞回"。
- W3C1（10-01）四态核对结论"真死、捞回无源"——**已被后续事实推翻**，完整反转链条：
  1. 封存副本先在：`docs/_working/total_command_closeout/wave1b/rescued/versions/test_redblue_governance_py.md` 内嵌整件原文（自称"捞回无源"不确切——封存即源）。
  2. **已救回落 HEAD**：commit `5462b60000b`（2026-09-27 11:27，"W-81 防伪可观测腿：钩子加 warn_only 留痕 + 两件红队测试回正位同批（Owner 10:1x 认证对话批准甲案）"），两件落真实位 `tests/governance/`，是 dev/HEAD 祖先。
  3. **逐字节同源**：现 HEAD 两件 sha256 前 16 位 `f8b182c4fbdff6d8` / `9ad47e4d4e95f000`，与 `.runtime/campaign_trash_20261001/worktree_salvage/.../tests/governance/` 捞回件完全一致；governance 件 546 行=封存副本记录的行数。
  4. 落地真实读数在册：`wave7/redblue_rescued_findings_20260927.md`＝governance 22 passed/1 failed（唯一红=真 P0 缺陷 P-1"冒充在活 sid 静默放行"，非测试缺陷）、robust 18 passed/0 failed。
  5. P-1 洞已补：`scripts/governance/git_hooks/reference_transaction_guard.sh:225-250` 现 `gw_sid_channel_unverifiable` 分支（总筹裁定 Z-F8 甲案，warn_only+审计留痕）——红件所攻防线已同批闭环。
- W3C1"①HEAD 无"疑为其检查时点/路径伪影（救回 commit 早其四天）；本车道按现势 HEAD 复核为准。

### 定性

0116 的"残件处置（补写/销账）须 Owner 定性"悬案**已被事件消化**：补写=已发生（Owner 批准甲案、字节同源、正位落地、配套钩子补丁同批）；销账对象不复存在。唯二残余：a) 两套件自 09-27 后的复跑绿证未见新记录（本车道只读纪律未跑 pytest——跑测会写 .pytest_cache，留落地车道复跑）；b) "四态核对表正式产出件未落册"——其结论已被本报告取代，无再产出价值。

### 处置建议

**判销账结案**：以本报告证据链（commit 5462b60000b + sha 同源 + Z-F8 甲案钩子补丁）作为 0116 残件处置的定性底稿，随 0104/0105 处置批一并呈 Owner 追认即可，**无须再开补写施工包**。落地车道补一步：两套件回正位复跑留绿证（只读结论的执行面补全）。
**需 Owner 二次确认：否**（追认性质，可并入批量核销；如 Owner 要独立红证可指定复跑窗口）。

**结案复跑绿证**：2026-10-05 落地车道 H8（sid=st-tclose-c1close-20261005）复跑 `pytest tests/governance/test_redblue_governance.py tests/governance/test_redblue_robust.py -q` = **41 passed 全绿**（governance 23 + robust 18；对照 09-27 wave7 底账 governance 22 passed/1 failed——唯一红 P-1 已随 Z-F8 甲案钩子补丁转绿，多出的 1 通过即红转绿实证）。

---

## ③ 0104 · ROOR 覆盖率派生字段通道

### 证据

- 1A.4 出口判据原文（10_wave_plan.md:38）：**"覆盖率进 ROOR 派生字段；6 条逐条定性（补执法面／改判据面／退役）"**；规则号别名归一后被提及面覆盖 80/86=93.0%，零匹配 6 条=trae_057/066/074/076/078/083。
- **ROOR 现状**（docs/registry_of_registries.yaml，1017 行，schema 1.1.0，头部 `ai_autonomy=human_gated`）：全文无 coverage/rule_face/覆盖率字段；summary 段由 `check_registry_consistency.py --refresh-summary` 机生、只含扫描覆盖注记。ROOR 处理派生数据的既有模式=**独立派生册+生成器+ROOR 条目**（先例 REG-STD-FAMILY-001：standard_family_registry.yaml ← generate_standard_family_registry.py，maintenance:auto）。
- **覆盖尺机械件现状**：表①（门禁触发面三列）已落地——`scripts/governance/generate_gate_face_reconciliation.py` + `docs/01_policies_and_standards/_registry/reports/gate_face_reconciliation.yaml`（RPT-GATE-FACE-RECONCILIATION，as_of 10-01，名册 104/实载 96）。**表②（规则↔执法面）生成器不在 HEAD、也不在盘面**（`meta/enforcement_surface_reconcile.py` 已消失）；其唯一产出遗存=staged 机生件 `docs/_working/total_command_closeout/wave1a/enforcement_surface_reconciliation.yaml`（as_of 09-26）。
- **"yaml 49 vs 散文 6"口径差破案**：两数测的不是同一面。staged yaml `table2_rule_enforcement.stats`：真执法面（门禁代码+checker 脚本 py）86 条中 code 零匹配 **49**、覆盖 43.0%；散文 80/86=93.0% 是**被提及面**（别名归一后任意文案提及）。yaml 内已自带"二者分列，勿与散文册的 80/86 混用"注记——**分立口径已自洽，未竟的只是把双口径正式落册+6 条短名单定性进正式通道**。
- 6 条零匹配现势：6 个规则 yaml 全在册（共 86 册）；按规则 id 反查执法面（src/gov_enforcement+scripts/governance 非 _archive）——trae_057 仅被建卡器字面提及，**其余 5 条（066/074/076/078/083）id 级引用仍为零**。注：worktree 基底新鲜度/提交持久化（074/076）在队列 preflight 有功能等价物（base_conflict/cascade_stale 检测），但未按规则 id 挂接——这正是 1A.4"被提及≠真执法"二级判定要逐条裁的形态。

### 定性

缺的不是"数据"而是**通道**：覆盖率双口径读数与 49 条长名单已有机生底稿，但没有 (a) 常设生成器把表②同表①一样落成 `_registry/reports/` RPT 件，(b) ROOR 派生条目使其可被发现，(c) 6 条（扩 49 条）逐条定性的正式呈裁通道。消费者=规则治理面（rule_catalog/in_process_gate 对账）、后续补执法面施工包、以及 1A.4 打标本卡。

### 处置建议（三选一）

- **推荐：登记生成器（b），按 ROOR 派生先例模式落地**——表②并入已落地的 `generate_gate_face_reconciliation.py`（同脚本双表，恰是 W3C1 原计划"表②覆盖尺同脚本"），产物落 `_registry/reports/rule_face_reconciliation.yaml`（双口径 stats 分列+零匹配名单），ROOR 增一条 `maintenance: auto` 条目指向该报告（即"覆盖率进 ROOR"的先例合pattern实现）。净零对价现成：替代归档 one_off `check_rule_coverage.py` + 替代 docs/_working 手工 staged yaml（两旧件登记退役）。
- 不选"字面进 ROOR 派生段"(a)：ROOR 是 human_gated 发现唯一真源，往条目里塞易变派生数据会污染发现面、且 ROOR 净增字段须 §4 净零等长对价，得不偿失；"进 ROOR"按先例=派生册/报告+ROOR 可发现条目即可满足判据本意。
- 不选 out-of-scope(c)：49 条零匹配长名单正是"声明面与强制面脱钩"病灶的存量清单，074/076 又是本战役反复失血域，弃之则 1A.4 出口判据永久半件。
- 6 条短名单逐条定性（补执法面/改判据面/退役）属施工包内容，**走意图API登记呈裁**；49 条长名单随 RPT 件常设可查，不逐条呈裁。
- **需 Owner 二次确认：建议是（轻量）**——ROOR 净增条目+两旧件退役对价声明按 §4/§5 走 Owner 门位点头，可与 0104 打标同批；生成器施工本身 medium/low 全自动。

---

## 附：本车道证据可复算命令锚

- 0 字节名单：`find data .runtime -maxdepth 4 -size 0 \( -name "*.db" -o -name "*.duckdb" \)`；时间：`stat -c '%n birth=%w mtime=%y'`
- ②反转链：`git show -s 5462b60000b`；`git merge-base --is-ancestor 5462b60000b dev`；`sha256sum tests/governance/test_redblue_{governance,robust}.py`；`wave7/redblue_rescued_findings_20260927.md`；`reference_transaction_guard.sh:225-250`
- ③口径差：`docs/_working/total_command_closeout/wave1a/enforcement_surface_reconciliation.yaml` table2 stats 段；ROOR 结构=docs/registry_of_registries.yaml（REG-STD-FAMILY-001 先例 :361，summary :995+）
- 底账对照：night_sweep/ledgers_archive/{T1C1,W3C1}_ledger.md；前棒普查=total_command_closeout/wave1a/{store_liveness_census,dead_store_triage}.{md,jsonl}
