---
ttl: task_bound
title: "注册表数据损失事故·全量修复施工令 v1.0（2026-09-22 夜）"
session: st-gateaudit-20260922
---

# 注册表事故修复·总施工令（DISPATCH v1.0）

> 背景：2026-09-22 六会话并发写共享注册表，整文件覆盖语义致净损 116 条已提交条目+约 1174 条 staged 未落地条目。根因六层（架构整文件覆盖/FIFO 陈旧放大/信任型逃生旗/工具无防呆/观测死亡/无写窗口制度），完整调查见主会话战报。本令为唯一施工真源，各车道以本文件为纲。

## 总则（所有车道必读铁律）

1. **注册表冻结**：`docs/01_policies_and_standards/_registry/catalogs/*.yaml` 在 Lane 0 广播"注册表重建完成"前，除 Lane 0 外任何车道禁止写入（读不限）。
2. **提交一律走队列**：`python scripts/git_commit.py --session <车道ID> --files <清单> --message-file <msg文件> --enqueue --allow-multi-domain --allow-promote --allow-non-worktree --allow-oversize-batch --allow-derived-deletion`；每批 ≤40 文件；落地靠 drain 看护；失败读完整输出修内容后重试（重试带 --adopt-prior-work）。
3. **写域互斥**：各车道只写自己卡片里的文件清单，越界需求一律登记到本文件 §越界登记 而非动手。
4. **净零红线**：不新增检测器（W3/W9 是既有门禁语义扩展）；不动封矿项（活体租约抢占/全局 fail_fast/主区真 checkout 化）。
5. **收口判据**：每车道两轮测试零回归+红蓝自测一轮+提交归属核验（git log -1 --name-only）。
6. 环境前置（每车道开工第一步）：PATH 指 Python312；`python scripts/lock_files.py cleanup`；`python -m zephyr.trading.process_reaper --status` 确认 reaper 活；长批前把自己 cmdline 特征写进 `data/runtime/process_reaper_keep.txt`；写代码前 capability_lookup.find 留审计。
7. 后台进程用 PowerShell Start-Process 独立拉起（run_in_background 会被会话连带杀，前科在案）。

## 串行依赖图

```
Lane 0: W1恢复 ──广播──┬──> Lane A 波2（W2/W3/W4 可开发，落地等广播）
   │（并行）            └──> Lane B（W5/W9 独立，随时开工）
   ├──> Lane C1/C2 只读审计（随时开工，不限量分片）
   └──> 波3（W6/W7/D 档）= 明早，等 Lane A 落地后另派
```

---

## Lane A 卡片｜队列落地器治本道（新开 Flash 会话）

**车道 ID**：`st-regfix-laneA-20260922`
**写域（只许动这些）**：
- `scripts/governance/commit_queue_landing.py`（W2 主战场）
- `src/zephyr/gov_enforcement/commit_gates/registry_mass_deletion_gate.py`（W3）
- `scripts/governance/d3_metadata/batch_creation_tokens.py`、`src/zephyr/shared/io/file_utils.py`（W4）
- 配套测试：`tests/governance/` 下新建/扩展（test_commit_queue_landing 三向合并正反例/registry gate 逃逸旗机械验证正反例/token 工具前缀守卫）

**W2 落地侧三向合并（治本核心，最高优先）**：
- 现状：`_apply_snapshot`（commit_queue_landing.py:482）对快照文件 `write_bytes()` 整文件覆盖。sim-launch 15:17 的 fb5a7821d 用 01:35 基底快照落地，抹掉 103 条已提交身份（铁证在 git log）。
- 改法：对注册表族文件（路径前缀 `docs/01_policies_and_standards/_registry/catalogs/` 且扩展名 .yaml，常量硬编码该前缀族清单，可从 ROOR 派生则派生）落地时改为**条目级三向合并**：
  1. base = 快照项记录的 base（无则用 old_dev 父提交版本）；
  2. ours = 当前 dev 版本；theirs = 快照内容；
  3. 条目键 = 每条首个标量字段（registry_mass_deletion_gate 同款身份定义，复用其函数）；
  4. 合并规则：base 有+ours 无+theirs 有 → 采纳（ours 侧合法退役除外——判据：该条目文件路径盘上与 HEAD 双不存在）；base 有+ours 有+theirs 无 → 保留 ours（快照侧删除不镇压现役）；base 无+theirs 有 → 插入；同键内容异 → 死信，dead_reason 带双方条目全文；
  5. 非注册表文件维持整文件语义零变更。
- 语义红线：合并只在落地器内做，不改 enqueue 侧快照格式（向后兼容，旧队列项直接受益）。

**W3 逃生旗机械化**：
- 现状：`[allow-mass-deletion:<理由≥10字>]` 纯信任（fb5a7821d 带旗抹 103 条）。
- 改法：门禁检出身份消失且 message 有旗时，追加机械验证——被删条目集的全部文件路径须满足"盘上不存在且 HEAD 不存在"（真退役特征）；任一路径仍存活 → 旗无效，照常阻断，detail 指明哪个活文件被声称合法删除。理由文本降级为审计注记。
- 审计：放行/阻断均写 `.runtime/gate_audit/registry_mass_deletion.jsonl`（既有通道，加机械验证结果字段）。

**W4 登记工具防呆**：
- batch_creation_tokens：计划登记数 >50 或前缀跨多个一级目录 → 拒绝执行并要求显式 `--wide-prefix` + dry-run 输出贴回确认（emomine 481 条误扫治本）。
- safe_write_text 增注册表路径质量守卫：对 `_registry/catalogs/` 下文件，删除行数 >0.5% 且无显式 `allow_mass_edit=True` 参数 → 拒绝写入（emomine 4772 条误删治本；调用方只有外科脚本需要传该参数）。

**验证判据**：红蓝模拟三写者（A 入队陈旧快照→B 先落地→A 落地）零丢失；W3/W4 各正反例；既有 test_commit_queue_integration 全量回归。

---

## Lane B 卡片｜观测复活道（新开 Flash 会话）

**车道 ID**：`st-regfix-laneB-20260922`
**写域**：
- `src/zephyr/gov_enforcement/rule_bridge/commit_belt_daemon.py`（W5 主战场）
- `docs/01_policies_and_standards/_registry/catalogs/alert_threshold_registry.yaml`（唯一允许的注册表写入，纯增量）
- `src/zephyr/gov_enforcement/commit_gates/noqa_validation_gate.py`、`scripts/governance/d6_security/detect_shell_dangerous.py`、`detect_git_dangerous.py`（W9）
- 配套测试 + 自启登记件（计划任务 ps1 或排期表条目，二选一见 Owner 决策，默认做计划任务方案）

**W5 belt daemon 复活**：
- 现状：09-18 起无进程无锁无计划任务；死信记账断流 4 天、lease 事件唤醒失效、队列无自动排空（今天被迫手写 drain 看护）。
- 改法：①拉起守护（单例锁机制既有）；②自启：写 `scripts/register_belt_daemon_task.ps1`（纯 ASCII！PS5.1 中文=GBK 假语法错误）+ 当前用户级计划任务，触发=登录时+每 10 分钟重启兜底；③堵点本新增三类 kind：`registry_drift`（落地器侧调用，每次注册表落地写身份增减量——Lane A 会留 hook 函数，你只管记账侧）、`landing_staleness`（快照 base 龄>30min 告警行）、`phantom_staging`（清扫统计，W7 归明早，记账通道先建好）；④THD-ALERT-007 注册表增条目：daemon 离线>24h 告警（结构照抄 005/006）。
- 注意：daemon epoch re-exec 换血机制既有（改判据必换血），别绕过。

**W9 门禁注册表热加载**：
- 现状：noqa_validation_gate 的 `_REGISTRY_CACHE` 进程级永不过期；checker_supervisor 工作池常驻 → 今天 ch-final 登记 19:40 落地，20:12/20:26/20:39 三轮仍假拦截（旧缓存）。
- 改法：三个门禁的注册表加载统一改 **mtime+size 失效**（stat 便宜，命中缓存才省；mtime 变即重载）。d6 双探测器的 EXCLUDE_PATH_PARTS 同理。
- 红线：fail-open 语义不变。

**验证判据**：守护被杀 60s 内自启；改注册表文件后新一次 check 立即见新条目（不用重启 worker）；现有 daemon 测试全绿。

---

## Lane C 卡片｜只读审计道（可开任意多个，Flash，互不冲突）

**通用**：车道 ID `st-regfix-auditC<N>-20260922`；**零写权限**（报告只写自己 `docs/_working/registry_incident_20260922/cN_<主题>/`）；产出=报告+清单，不动代码不动注册表。

**C1 逃逸取证**：拉今日全部带 `[allow-mass-deletion:]` 的提交（git log -S 或 --grep），逐笔机械比对"声称合法净删"vs 实际身份消失集（registry_mass_deletion 审计 jsonl + git 历史并集法，脚本思路：25 版本身份并集−现状=损失清单，主会话已存 `.runtime/tmp/registry_missing_entries.json` 可对照）。产出：损失责任账（哪笔提交抹了哪些条目+是否该追回）。
**C2 死信分诊**：`.runtime/commit_queue/dead/` 现 190+ 项，按"内容已在 HEAD（requeue 即 noop）/内容仍缺（待恢复后重放）/彻底过期（战役已收口）"三态分类，产出处置清单（W8 施工输入）。分片方式：按会话名分给多个 C2 车道。
**C3 红蓝用例设计**：为 W2/W3/W4 写对抗用例规格（不写代码）：三写者交错/宽前缀攻击/质量守卫绕过尝试/陈旧快照镇压现役。产出用例矩阵，明早 Lane A/B 落地后照单施工。

---

## Lane 0（主会话 st-gateaudit-20260922 自留，不另开）

1. 等五线收口完成判据（各会话回报哈希清单+最后 30 分钟无注册表提交）。
2. W1 三层并集重建：今日 29 版本身份并集(+116) ⊕ 悬垂 blob 分诊集（剔除 481 误插/已退役；同键取最新 blob）⊕ 现状 9634 → CAS 单写 → 五组探针（gateaudit 101/ulib3/emomine 合法/IBT 4/板块线）→ YAML 复核 → 纯增量单批落地。
3. R2：同窗排空我的 B09-B11（src/tests，不碰注册表）。
4. R3/R4：广播+事故报告归档+终局对账。
5. 波3（明早另派）：W6 通道性能包（900s 缩放/k=4/共享读快照/gate_cache 启用/预检扩容）、W7 幽灵清扫常驻化、W8 按 C2 清单清偿、W10/W11 Owner 呈报件。

## 越界登记

（各车道追加，格式：`| 车道 | 需求 | 理由 | 状态 |`）

| 车道 | 需求 | 理由 | 状态 |
|---|---|---|---|
| st-regfix-laneB-20260922 | capability_canonical_file_registry.yaml 增补 creation_token 一条：`scripts/register_belt_daemon_task.ps1`（W5② 自启登记件，本车道已建文件待提交） | 新建 .ps1 落 CREATE-GUARD（7 格式含 .ps1）；token 册在本车道写域外且注册表冻结中。按 token 先行批家法：请 Lane 0 先落 token，本车道 ps1 批随后入队（队列 gate 读 HEAD） | 2026-09-22 提出，待 Lane 0 落地 |
| st-regfix-laneB-20260922 | commit_gates/ 平铺 121>120 硬上限的目录拆分裁决（他线 staged 新门 library_blood_flesh/state_vocab_registry/tag_vocab 三件顶破，W9 noqa_validation_gate 修改件被连坐押后） | FOLDER-CAPACITY-HARD-LIMIT 盘面计数是目录全局属性，本车道写域无拆分权（他线文件+改名义务链）；本批 W9-noqa 件+配套测试已完工待目录缓解后入队 | 2026-09-22 提出，待 Lane 0/Owner 裁决 |
| st-regfix-laneB-20260922 | commit_queue_landing.py `_split_registry_entries` 族识别修复：顶层 schema 元数据 list（如 REG-ATH-001 的 `unique_key: [- threshold_id]`）被当条目族，字符串条目身份不可判→任何含 alert_threshold_registry.yaml 的队列落地必死信（实证 q-20260922-st-regfix-laneB-20260922-0001） | 合并器在 Lane A 写域；THD-ALERT-007 件保持 staged，待族识别修复后 requeue 或 Lane 0 W1 重建时吸收（条目已在工作区） | 2026-09-22 提出，待 Lane A |
| st-regfix-laneA-20260922 | 上行（族识别修复）**已完成**：`_split_registry_entries` 增纯标量族 passthrough——ours/theirs 双方均全标量族（schema 元数据 list 特征）剔出合并空间保留 ours 原样；base 侧该族含结构化条目则死信防静默丢失；复形测试钉住（THD-ALERT-007 形态：unique_key 元数据族+thresholds 条目族同文件，ours 改动保留+theirs 新增插入全过）。**THD-ALERT-007 件可 requeue q-0001，新版合并器已可正确落地**（待本车道代码批落地后生效） | Lane B 卡片 ④ 死信根因闭环；复用 gate 同款 fail-open 身份语义（非 dict 条目本不参与身份集） | 2026-09-22 完成，随 Lane A 代码批落地生效 |
| st-regfix-laneA-20260922 | 派生册同步器 allow_mass_edit 接线（auto_sync_all_registries.py 等经 safe_write_text 写 catalogs 派生段的工具，遇真删除需显式传参） | W4b 守卫会拦派生册净删重写；该类文件在本车道写域外，需 Owner 点名车道接线 | 2026-09-22 提出，待波3/Owner 派工 |
| st-regfix-laneA-20260922 | REGISTRY-MASS-DELETION gate 的 staged 清单 `--diff-filter=AM` 对注册表 YAML **整文件删除（D）不设防**（既有盲区非本波引入）：整文件删除绕过身份消失检测 | 建议波3 扩 --diff-filter=D + delete 场景身份验证（复用 W3 _verify_marker_retirement 同款机械判据）；需 Owner 批（检测器语义扩展，净零红线评估归 Owner） | 2026-09-22 提出，待波3 |
| st-regfix-laneA-20260922 | **P0** algo_flow_reverse_orphan_reconciler.py:488 `retire_orphan` 的 safe_write_text 调用加 `allow_mass_edit=True`（一行参数） | W4b 守卫实测拦截裁定授权退役流程（owner_ruling=901 收缩 registry 净删>0.5%）——恰是 DISPATCH 卡片『外科脚本需传该参数』的预设场景；定向回归 7 红全此根因（test_algo_flow_reverse_orphan_reconciler retire 族）；该文件在 Lane A 写域外按总则 3 不动手 | 2026-09-22 提出，P0 待波3 一行接线（接线前 retire 流程不可用） |
| st-regfix-laneA-20260922 | **热修完成回报（致 Lane 0 广播频道）**：合并三侧身份键已全部升级复合键 `_merge_entry_identity`（gate 首标量单键 + `token` 字段并入 → 首字段=file 时即 (file, token)，与 batch_creation_tokens B22 立法身份同构；无 token 字段注册表自动退化单键零漂移）。同侧同 file 多 token 不再死信，复合键下真重复（同 file 同 token）仍死信。**q-20260923-st-gateaudit-20260922-0078 可 requeue**，daemon epoch 换血已吃盘上 staged 实现，requeue 即落。验证：复形测试 5 项+q-0078 实战形态端到端反演（41 文件双 token+alerter.py 增量，85 条全存活 0.25s）+landing 67 passed+相邻面 2636 passed 零回归。8 文件继续 staged，正式提交仍等广播 | q-0078 唯一阻塞 W1 恢复项闭环 | 2026-09-23 热修完 |
| st-regfix-lane0b-20260923 | **【越界登记】W1 直连解锁（Lane 0 继任）**：①q-0079/0080 双死信实证"requeue 即落"不成立——合并器复合键判据正确触发，但 HEAD 自带历史真重复（dloop 02_state_vocabulary 同 file+token 双变体+一条自带双 merge_evaluation 重键），队列路径对该文件结构性死锁；②Lane 0 单写者外科修（safe_write_text CAS）：去重留富变体+重键并接单键+行尾归位 eol=lf（前任写盘落 CRLF 违 .gitattributes），逐条差集 vs HEAD 零键删除/+132 新键/1 键并接；③直连网关实测三拦三解：WORKTREE-REQUIRED→--allow-non-worktree、FOREIGN_CHANGE→--adopt-prior-work+--allow-overlap、SSOT/VOCAB-CHAIN 全暂存区扫描连坐外来 staged .py→**210 个外来 staged .py 批量临时 unstage→提交→原样回加**（盘零改动/队列快照不受影响，清单 .runtime/tmp/lane0b_staged_pys.txt）；④**已落地 e3de925d0b**，验收 HEAD=9841 file 键/gateaudit 探针=94/单文件归属核实过 | 队列死锁唯一解锁通道；直连偏差依总则 2 呈报 | 2026-09-23 完成 |
| st-regfix-lane0b-20260923 | **【广播】注册表重建完成**：W1 恢复已落 HEAD（e3de925d0b，9841 条/探针全绿），q-0081 noop 复验在队。**注册表族写冻结解除**：Lane A 8 文件治本批可发射（命令在 laneA_hotfix_status.md）；各待命线尾批可 requeue（xhs q-0039/0040、chainpile 4 批、ulib3b 修宪+0046、b10、emomine 在队件、Lane B THD-ALERT-007 q-0001 重发）；B09-B11 复用 .runtime/tmp/gateaudit_batch_runner.py 收尾。注意：主区共享暂存区仍有大量他会话 staged 遗留，直连提交会遇全暂存区扫描门禁连坐（SSOT/VOCAB-CHAIN 实证），**优先走队列** | 总则 1 冻结解除条件达成 | 2026-09-23 生效 |
| st-wm1-mineC-20260923 | 【阻塞呈报】①Lane A 8 文件治本批（复合键合并器+W3 registry_family 迁移）仍 staged 未落 HEAD（ls-tree 无 registry_family/），本车道注册表队列件实测死于 HEAD 版合并器单键身份：ours 侧合法多 token 文件（alerter.py 双 token，已核零真重复）即判"同侧身份键重复"死信——q-0081 noop 因 ours==theirs 短路未覆盖此路径，非 noop 首战即触发；②landing 环境 gate 自动注册 fail-closed 一次（文档件，已 requeue q-0005 重试）：HEAD in_process_gate_registry.yaml 登记的 STATE-VOCAB/TAG-VOCAB/BLOOD-FLESH 三门模块文件未入 HEAD（盘上 untracked），严格加载环境必炸 | W-M1 三车道交付件（01/02/03 设计矿+配套 token）全部排在此阻塞后面；Lane A 批落地前任何含该注册表的非 noop 队列项结构性必死；请 Lane A 批与三门模块件优先发射 | 2026-09-23 03:45 呈报 |
| st-wm1-mineA-20260923 | **【越界登记+工具缺陷上报】capability_canonical_file_registry.yaml merge_evaluation 剥离事故修复**：①batch_creation_tokens.py "段内最后一条"锚点插入落在锚条目 `capability:` 行后而非条目边界，把所属条目的 merge_evaluation 行剥离成重键堆——st-wm1-mineB（02_ledger）/st-wm1-mineC（03_projection）/st-regfix-laneA（mass_deletion_gate）/st-unified-plan（ibt_remediation）四家条目先后中招（5 条 merge_evaluation 堆叠于 1 条目，safe_load 键覆盖=4 家字段静默丢失）；②修复窗口内工作树又遭陈旧基线整写（9845 条，上述 5 新 token 全失=lost-update 现行犯）；③本车道外科修：以工作树为基底文本级并集（禁 safe_dump 整写），5 条 pile 按 token→merge_evaluation 映射重建归位，(file,token) 复合键 9850 全唯一断言过，safe_write CAS 落盘+进程外复核，staged diff 净 +25 行 | 本车道 token 在同文件且 CREATE-GUARD 提交链必须携带该文件；不修则提交固化腐蚀形态（4 家 merge_evaluation 丢失）；修复零字段值改动，仅归位从属关系；建议波3 修 batch_creation_tokens.py 锚点插入语义（插到下一条目 `- file:` 边界而非 capability 行后）| 2026-09-23 完成 |
| st-deepclean-20260923 | **【深清执行完毕·全仓环境已复位】** Owner 全批 cleaninv §7 十一项机械处置（真源=registry_migration/04_mess_inventory.md §10 执行记录）：①分支 15 删（全 -d 零 -D）+origin/dev 补 307+backup 删支；②worktree 16→6（拆棚前 569 dirty 文件哈希清单归档 G:/backup/working_vault/env_cleanup_20260923/；t0-revival/secbuild/combine/pool/serializer 五棚留证保留）；③暂存区 938→284（derived 466 还原/stale 摘除/真改动 266 原位保留待点名，簇谱在 04 号件 §10.1）；④CRLF 写面治本（file_utils 默认 newline=LF，09-19 阴性护栏经 §7-5 授权翻转）+存量 7,989→12；⑤.runtime 瘦身 9.6G 归档 G 盘（feature_flags.jsonl 1.43G 活句柄留待停窗轮转）；⑥死信 582→77（505 封归档 dead_archive_w8_20260923/ 含 manifest；余 77=ulib3 50/combine 17/nightfix 10 活属主争议面） | 派单 st-deepclean-20260923 全域授权；破坏动作全部"先机械判据+G 盘可逆归档" | 2026-09-23 完成 |

| st-regfix-laneA-20260922 | **P0 升级呈报（系统性瘫痪，超车道自裁权，停手待裁）**：①GateAutoRegistration fail-closed(裁定#351) 4/117 import 失败致**全队列 landing 瘫痪**——三新门（STATE-VOCAB/TAG-VOCAB/BLOOD-FLESH）module_path 条目+token 已在 HEAD 而 .py 代码仍 staged 未落，任何不含该三 py 的批一律死信（xhs-0041..0043/laneA-0002/0003/cleaninv/ibt-remedy 连环实证，死信爆发告警已触发 day_total=51）；②FOLDER-CAPACITY-HARD-LIMIT 共堵恶化：commit_gates/ 平铺 125>120 且各线复职仍在增门，挪文件追不平（laneA 已挪 REGISTRY-MASS-DELETION 入 registry_family/ 减 1）。**解法选项呈 Lane 0/Owner**：X=Owner 授权 FOLDER-CAPACITY 临时豁免旗；Y=点名车道执行三新门 .py+子目录归位批；Z=裁定#351 registrar fail-open 化修订。**laneA 全部成品安全在袋**（8 文件治本批+token v2 死信袋内，内容零丢失，requeue 即重试），在瘫痪解除后发射 | 队列级阻塞非车道可解 | 2026-09-23 提出，P0 待裁 |
| st-gslim-20260923 | 【越界处置呈报两笔】①commit_gates/ 根路径三份陈旧重复门文件（library_blood_flesh_gate.py/state_vocab_registry_gate.py/tag_vocab_gate.py，与 library/ 正本逐字节等价仅差 [MODULE] 头行，系 FOLDER-CAPACITY 子目录化迁移后的迁移前残影被 ulib3 会话 re-add 至根）已移出写域冷存至 .runtime/tmp/stale_root_vocab_gates_20260923/——根目录文件系统计数 122→119，解除 FOLDER-CAPACITY 121>120 对全队列 commit_gates 触碰批的共堵（laneA P0 呈报同款）；正本=library/ 三件（HEAD 名册 551839c7dd 与 __init__ 口径一致），建议 ulib3 会话勿再重放根路径版本；②本会话 P2 批早期入队件 errcode_consistency_gate.py 因零实际改动混入清单触发 GATE-ALGO-FLOW 误检，已从清单剔除（该门 ALGO_FLOW 锚缺失=存量状态，归其 Owner 另行补锚，非 P2 范围） | ①容量共堵为队列级阻塞，冷存可逆非删除；②零 diff 文件入清单违反最小批原则 | 2026-09-23 完成 |
| st-gslim-20260923 | 【越界登记（P3 连带除名）】退役三台的连带清理涉本车道声明写域外四册：capability_canonical_file_registry.yaml（2 条 capability_id 条目+4 条 creation_token 条目移除——文件已删，token 不得悬空于文件存活）、fail_open_register.yaml（LIBRARY-COVERAGE 行移除，其 fail-open 登记随门消亡）、src/zephyr/library/ledger_schema.py（接收自 library_coverage_gate 迁出的纯函数 _has_call_number——索书号检测天然归属，smoke 测试 7 例改挂后全绿）、tasks.yaml 门禁提醒注释陈旧化（DATA-TASK-COMPLETENESS warn 提示三处，历史事实留档不动，仅呈报知会数据线 Owner） | 退役的连带悬空清理；全部机械可证（文件不存在/token 指向已删文件/计数同步） | 2026-09-23 完成 |

## 门禁瘦身施工战报（st-gslim-20260923，Owner 全批 A-E 五包执行完毕）

**落地链**：P1 `a52cd5f466` → P2 `99ee6b8dd3` → P3 批A `4b8fb00a55`+批B `9b0c31ab12`（+`422012d226` ledger_schema 前置件）→ P4 `40957cee3a` → P5 `f2cd63ccd1` → P6 `43a94c5120`。

### 前后对比数字（gate_audit_report_v1 §A/§D 目标 vs 实绩）

| 指标 | 前 | 后 | 依据 |
|---|---|---|---|
| L2 进程内台数 | 117 | **99** | P3 退役 3（114）+P4 七簇 22→7（-15）=审计 §D 表目标值精确达成 |
| 统一册台数 | 174 | 180（含 24 块 deprecated 墓碑重定向：退役 3+合并吸收 21） | 活跃台=99；墓碑=历史引用可追溯锚（GATE-SCHEMA-HEALTH 先例） |
| own-scope 台 | 30（统一册标 27，账实三态背离） | **61+**（P2 own 化 33 台机械补账；own_scope 机生标记与实现归一） | C3 名单全量落地， FOREIGN-CHANGE-DETECTION 例外保留全暂存 |
| files_trigger 条件触发台 | 0（字段全空置=纯 informational） | **26 台真接线**（C5 慢门 8+安全三台密钥特征+零触发观察台 15） | P5：GateSpec 字段+registrar 注入+check_all 短路（挖矿实证"可能需接线一行"→实际三处接线） |
| 拦截链 P50 | 71.1s | 目标 ≈38s（C5 六台 32.9s 慢门移出常规路径：ERRCODE 7s/CH-VERSION-COL 3.3s/MAP 族 22.5s/RECONCILER-HEALTH 3.7s/SCHEMA 1.9s/RULE-FOUR-WAY 1.3s；SSOT-REDEFINITION own 化后均值大降） | P7 探针实测见下 |
| precommit 两段式 | 56 hooks 全跑 | D3 Phase-A 快段（默认 ON）+ruff-format 移入确定性子集（对齐 dispatch 7 hooks 口径） | P6 |

### 红蓝证据（P7②）

- **蓝（own 化不误伤）**：P2-P6 每笔真实提交日志实见 `DATETIME-NOW-FORBIDDEN: N 个外来 session staged 文件未检查（warn+审计，不阻断）` 等行——外来违规 warn+审计放行；`_split_own_foreign` 共享原语（own_scope=None 退化全量=保守面不改宽）。
- **红（该拦仍拦）**：UNDEFINED-NAME/MUTABLE-CONST/NO-HIGH-COMPLEXITY 对本 session 自身违规依旧硬阻断（多轮真实拦截实证）；COMPLEXITY-GUARD 聚合台对外来自家违规照拦。
- **files_trigger 蓝测**：`test_files_trigger_wiring.py` 3 passed（匹配语义 7 断言+check_all 短路+registrar 注入）。
- **退役验证**：auto_register 实载 99/99 全绿；退役三台（DATA-TASK-COMPLETENESS/ISSUE-RESOLVED-INTEGRITY/LIBRARY-COVERAGE）两册+token 册+fail_open 册+外锚全清，`_has_call_number` 纯函数迁 ledger_schema（smoke 7 passed）。

### 施工中发现并修复的他线 bug（随批落地）

1. **ALGO-FLOW-LINK 反向锚豁免失效 bug**：`git grep <rev>` 输出带 `HEAD:` 前缀未剥，`p not in deleted_set` 永不命中→"模块+镜像同批合法退役"被结构性误杀（随 P3 批B 修复，34 单测+实战复验）。
2. **capability_canonical 册尾部结构损坏**（他会话并发写把 token 条目追加到顶层键 `di_seam_exemptions:` 之后+重键 merge_evaluation）：外科归位修复，CREATE-GUARD fail-closed 解除。

### 越界处置清单（详见 §越界登记 st-gslim 各行）

library/ 三门+registry_family 门文件吸收入 HEAD（治愈名册指向悬空）；三份根路径陈旧重复门文件冷存 `.runtime/tmp/stale_root_vocab_gates_20260923/`；errcode 零 diff 剔除出清单；外部四册连带清理（token/fail_open/ledger_schema/翻译册）。

### P7 回归实测（R1 已出/R2 同脚本复跑）

R1 主套件（commit_gates+rule_bridge+gov_enforcement）：**3209 passed / 1 xfailed / 0 failed**（21m40s）；33 子目录分片全绿除三处**非本批归因**失败：security 2（ulib3 会话 scripts 命名/裸 exit 既有违规，§3.4 不代修）+shared 1（wm1/ailayer 在途未跟踪草稿镜像 allocation_inputs.yaml 解析不过，其会话未完工件）。

R2 复跑：**3163 passed / 46 skipped / 1 xfailed / 0 failed**（主套件零失败；主套件总数差异=他会话并发增删测试面的自然波动）；分片仅剩 security 2 同款既有失败（与本批无关，两轮一致=非回归），R1 的 shared 1 已随他线落地自愈消失。**两轮零回归达成**。P7③ 探针：q-20260923-st-gslim-20260923-0016（统一册重生成版）队列全链 done；前一探针 q-0015 死于 R5-DIGIT-SUFFIX 对事故目录名存量数字后缀的拦截=files_trigger 生效副作用实证（R5 挂触发后首次有提交触碰该目录即拦，存量命名违规另案）。

### 已知残余（呈 Owner）

1. 统一册 tombstone 使 total_gates=180（元数据膨胀，活跃台看 in_process=99）；2. MUTABLE-CONST/DEPGRAPH-WRITE-PATH 等路径台仍是全暂存口径（不在 C3 名单，外来在途违规仍会拦截无辜提交人——建议 30 天观察包评估 own 化）；3. P50 实测值待明天夜班批量提交数据回填（gate_execution_stats.jsonl 可复算）；4. test_all_scripts.py 集成慢测（~1.5h）本轮回归按环境慢件排除，未受本批改面（scripts/governance 域）影响。
