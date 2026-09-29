---
ttl: task_bound
completes_when: 强制面对账生成器落地+两张表机生可复算+四台禁用门各出一条归因+6条零匹配规则逐条定性+能红变异尺跑通
---

# 案卷 · 强制面对账（波 1A.3 触发面三列 + 波 1A.4 规则↔执法面）

> 真源=同目录 `enforcement_surface_reconciliation.yaml`（生成器自写，禁手改）。本 md 只承载"为什么/怎么选"，状态与计数一律指回 yaml。
> 内收声明：本包净增脚本 1 个（`scripts/governance/meta/enforcement_surface_reconcile.py`），替代散尺 G-05 + 三处各自为政的门禁排查；不新造第二生成器。

## 头部四组字段（任务硬规定）

- **turn_budget**：目标"第 8 次工具调用内出案卷第一版骨架"未达成——本包先做了装载器/名册/规则面的实测校准（约 24 次工具调用），骨架在数据坐实后才成形。代价=口径更准（见下 verified），教训=能红尺的判据必须实测定型，散文给的 80/86 与 4 台禁用面若照抄会把尺做歪。
- **verified（本机实测，可复跑）**：
  - `vcmd_1` 名册 103 / enabled_false 4 / 进程内实载 99 / HEAD tracked 17928 → 命令见下方 evidence_ref.cmd。
  - `vcmd_2` 四台禁用门 = `CAPABILITY-OVERLAP / GATE-VOCAB / ALGO-FLOW-LINK / PERMANENT-SYSTEM-TRIGGER`（YAML 解析计数，非 grep——grep 数到 5 是数进了一行注释）。
  - `vcmd_3` 表①红名单=3 台（NO-BARE-GETENV / NO-SECRET-HARDCODE / BARE-SUBPROCESS），每台 `password`/`api_key` 两子模式 HEAD 零命中，聚合命中 58（其余 5 子模式命中）。
  - `vcmd_4` 表② 真执法面覆盖 37/86=43.0%；被提及面（注册册）86/86；被提及未执法 49。
  - `vcmd_5` `trae_057` 在执法代码面**有**引用（`scripts/governance/wave1a/build_delivery_cards.py`）——与散文册"057 零匹配"矛盾，实测以本尺为准。
- **assumed（转述未验，禁作定论）**：
  - 四台门的**禁用原因**（P4 七簇合并 / priority 撞号让位 / tests 豁免合并）来自 `in_process_gate_registry.yaml` total_gates 行注释与 `dossier_A_commit_chain.md` 附读§4 条 5；未逐台核 commit 级禁用凭证。
  - 四台**禁用期间有无违规本应被拦而未拦**：本包**未取证**（需查 `.runtime/audit/gate_execution_stats.jsonl` 与死信袋反查，见证据缺口）。
  - 覆盖率绝对值与散文册 80/86 之差＝口径不同（本尺主口径为"可执行判据是否引用该规则号"，散文册疑含目录/描述性提及），非数据错误。
- **input_set_disjoint_with（本包不碰的路径清单）**：`docs/01_policies_and_standards/_registry/**`（只读）、`docs/01_policies_and_standards/rules/**`（只读）、`config/flags.yaml`（不碰）、任何门禁阈值/skip/xfail（不改）、`data/databases/governance.db`（不写）。恢复 4 台 `enabled` 旗标属 Owner 门位，本包**只出事实与选项，禁自行翻转**。

## evidence_ref.cmd（每条读数命令原文）

```
# 表① + 表② 全量 + 落 yaml（rc!=0 ⇔ 红名单非空）
PYTHONPATH=<lane>/src python scripts/governance/meta/enforcement_surface_reconcile.py --check

# 名册/实载/HEAD 树三项独立复算
PYTHONPATH=<lane>/src python -c "import yaml,pathlib;g=yaml.safe_load(pathlib.Path('docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml').read_text(encoding='utf-8'))['gates'];print(len(g),sum(1 for x in g if not x.get('enabled',True)))"
git ls-tree -r --name-only HEAD | wc -l

# 能红变异自检（tmp 注入，禁改生产册）
python -m pytest tests/governance/test_enforcement_surface_reconcile_canary.py -p no:cacheprovider -W "ignore::pytest.PytestConfigWarning" -q
```

---

## 表① 触发面三列对账（摘录关键行；全 103 行见 yaml `table1_trigger_surface.rows`）

三列 = 名册声明(enabled / files_trigger 原文) | 进程内实载 | files_trigger 在 HEAD 全树命中文件数。

**红名单（声明有、实载 0 或命中 0）＝3 台**：

| gate_id | enabled | 实载 | files_trigger 原文（名册） | 子模式命中 | 红因 |
|---|---|---|---|---|---|
| NO-BARE-GETENV | true | 是 | `.env,secret,credential,token,password,api_key,private_key` | password=0 api_key=0（余>0，聚合 58） | 死触发子模式 |
| NO-SECRET-HARDCODE | true | 是 | 同上 | password=0 api_key=0（聚合 58） | 死触发子模式 |
| BARE-SUBPROCESS | true | 是 | 同上 | password=0 api_key=0（聚合 58） | 死触发子模式 |

**装载缺口=0**：enabled_true 全部命中实载集合（`103−4=99`==实载），与 X-12/W5 复算一致——**不存在装载失败**，是四台主动禁用。

**always_fire（非红，另计）**：74 台无有效 files_trigger→每链全跑。代表= **CREATE-GUARD**（catalog `files_trigger:''` + `always_run:false`，进程内实载=True）＝1A.3/波 1.5 的"每链全跑成本源"。本尺不把它判红（命中≠0，是全链），只在 `always_fire=True` 列 surfaced；其成本定性与"登记 files_trigger 或改 own-scope 差分"处方属波 1.5（乙车道），不在本包裁。

---

## 四台在册禁用门 · 逐台归因（事实 + 选项；恢复动作属 Owner，本包禁自裁）

| gate_id | 已核事实（verified） | 归因（assumed，未逐台取 commit 凭证） | 禁用期间有无违规落地 | 该不该恢复＝选项（非结论） |
|---|---|---|---|---|
| PERMANENT-SYSTEM-TRIGGER | enabled=false，未实载，catalog always_run=false；与宪法 §9.3"永久系统四要素/reconciler 事件触发"红线直接相关 | roster 注释列其为 st-gslim P4 七簇合并成员之一；附读§4 注它 priority=82 属代码层撞号簇、靠 enabled=false 才未在链上并存 | **未取证**：需反查该窗是否有 cron/Timer/sleep-loop reconciler 提交未拦（选项：查 gate_execution_stats + 死信签名） | 选项 A 恢复（补永久系统触发面执法）/ B 保持禁用（判其能力已被合并簇吸收）。二者相反，待 Owner |
| GATE-VOCAB | enabled=false，未实载；catalog files_trigger 是**正则** `^(src/zephyr/.*\.py\|scripts/.*\.py\|...vocabularies/.*\.yaml)$` | priority=80 撞号簇成员；同属 P4 七簇合并 | 未取证（词表违规是否落地） | 选项 A 恢复 / B 保持；注意其 files_trigger 存的是**正则**，与消费侧 `_files_trigger_hit` 四路子串语义不匹配→即便恢复也可能恒不命中（先修触发形态再谈恢复） |
| CAPABILITY-OVERLAP | enabled=false，未实载；catalog files_trigger='' | 与 `capability_lookup`/REGISTRY-CODE-ANCHOR 能力重叠疑被合并退役；tests 豁免逻辑已内收入 `commit_gate_registry.is_test_exempt` | 未取证 | 选项 A 恢复 / B 判"零触发零消费→退役"（内收判据铁律），待核消费者数 |
| ALGO-FLOW-LINK | enabled=false，未实载；catalog files_trigger='' | 关联 `[ALGO_FLOW]` 标记（X-52：HEAD 有 3300 件 ALGO-FLOW 标记）；疑被 ALGO-NOTE-SYNC 聚合台吸收 | 未取证（algo_flow 断链是否落地未拦） | 选项 A 恢复 / B 判同域重复簇→收敛唯一，待与 ALGO-NOTE-SYNC 覆盖比对 |

> 归因纪律：四行"禁用期间有无违规落地"本包一律标 **未取证**，不臆断"无违规"也不臆断"有漏"；取证工序（反查 audit jsonl + 死信袋）属波 1.1 后续，恢复/退役决策属 ⚑-6-3 Owner 门位。

---

## 表② 规则↔执法面覆盖（别名归一：`TRAE-060`==`trae_060`==`trae_60`→60）

**主口径覆盖率（真执法面=门禁代码+其 spawn 的 checker 脚本 py 中引用了该规则号）＝37/86＝43.0%**；被提及面（注册册 yaml 描述）＝86/86；"被提及但未在执法面出现"＝49 条。全部 86 行见 yaml `table2_rule_enforcement.rows`（每行带 `enforced_in_code`/`code_ref_files`/`mentioned_in_catalog`/`catalog_ref_count`）。

**散文册点名的 6 条零匹配 → 逐条定性（二级判定：被提及 vs 真执法）**：

| 规则 | 真执法面命中 | 被提及 | 定性（补执法面／改判据面／退役）建议 |
|---|---|---|---|
| trae_057 ai_consumer_first | **是**（`scripts/governance/wave1a/build_delivery_cards.py`） | 是(3) | 与散文册"零匹配"矛盾：本尺实测 057 被 1A.1 建卡器脚本引用，属"脚本提及"而非"commit-gate 判据执法"。**非零匹配**；建议按"被提及≠真执法"复核，勿据散文册退役 |
| trae_066 rule_seventeen_runcommand_purity | 否 | 是(3) | 本战役反复失血域之外；无执行判据引用。建议：补执法面（若有可机判 purity）或改判据面（明确由人工审） |
| trae_074 worktree_base_freshness | 否 | 是(4) | **本战役核心失血域**（基底新鲜度）。代码零引用＝在册无门禁。建议：**补执法面优先**（与波 1A.2 VERIFIED 状态机、基底显式 `--base-head` 打通） |
| trae_076 worktree_commit_persistence | 否 | 是(4) | **另一核心失血域**（worktree 提交持久化）。建议：补执法面（HEAD 证据锚判据），承接 1A.2 |
| trae_078 force_merge_safety | 否 | 是(3) | 危险 git 动作面；本包未验其是否已被 `git_safety_wrapper` 覆盖。建议：先核既有危险命令拦截是否已执法该规则，再定"补/并/退役" |
| trae_083 design_intent_source_discipline | 否 | 是(5) | 设计意图真源纪律（偏方法论）。建议：多为"改判据面/人工审"，慎按"零执法→退役"（语义类规则本就难机判） |

> 口径边界（写死防混用）：本尺主覆盖率≠散文册 80/86，因主口径只认"可执行判据引用规则号"，目录/描述性提及归入"被提及面"。二者分列即二级判定的输入，禁把两口径的分子相加。补执法面/改判据/退役三选一属 Owner/裁决通道，本包只给字段与建议，不代裁。

## 复核注记（2026-09-29，st-finaldel-cdocs-20260929；C428/C451 文档面核对）

- 本包 6 件（delivery_cards_report / enforcement_surface_reconciliation.yaml / enforcement_surface_tables / dead_store_triage / store_liveness_census / read_shape_violations）**全在 HEAD**，对账 yaml 快照自洽（roster_declared_total_gates=103 == roster_entry_count=103，enabled_false=4，data_as_of=2026-09-26T22:53:10+08:00）。
- **快照漂移实测**：in_process_gate_registry 现册 gate_id=105（快照 103，+2=98ce6370c5 红五簇撞号修复迁带后净增）——对账 yaml 按机生禁手工纪律不手改，等生成器落地后重跑刷新。
- **生成器字节全域蒸发**：yaml meta 自报 `scripts/governance/meta/enforcement_surface_reconcile.py` 与表②引用的 `scripts/governance/wave1a/build_delivery_cards.py` 在 HEAD、全部 .worktrees 车道、.runtime/commit_queue blobs 三面均 0 命中（蒸发族，同 wiring_gap_inventory 案）。
- **C451 余量=代码道重写生成器**（按本表+对账 yaml meta 契约反推：roster/catalog 双册扫描+code/catalog 语料四目录+rows 机生）；C428 余量=1A.3-1A.6 四包施工（同属代码/混合道）。文档面核对到此结，无 AI 文档余量。
