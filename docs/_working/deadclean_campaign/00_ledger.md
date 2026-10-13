---
ttl: task_bound
completes_when: 段三立法袋在 dev 复验落地＋九面全部"有主有据"＋Owner 对 §7 四件呈批逐条给裁
---
# 死信清零战役·账册（sid=st-deadclean-20261013，2026-10-13）

> 令据＝Owner 2026-10-13 直令「派工令 v2·死信清零战役班」＋四道追加裁：①50 袋先行 ②maint4/maint5 交本班判
> ③段三立法先落袋 ④九面基线三处纠偏采信（164 非 162／497 壳非 57 staging／11 枚悬空管理项）。
> 北极星＝九面附属物全部"有主有据"＋清理纪律入硬性规则＋存量归零，AI 幻觉源清除后不再堆积。

## 一、九面基线（进场重测，dev 锚 1e979418，扫耗时 309.8s）

| 面 | 令卡值 | 实测 | 备注 |
|---|---|---|---|
| ① dead 死信 | 1,591 | 1,598 袋 / 39.9 MB | 执行前复测 1,599（他班仍在死） |
| ② 工棚车道 | 162 | **164** 目录 / 530,429 件 / 53.4 GiB | 前五棵占 44.7 GiB＝84% |
| ③ worktree | 15＋13 | 磁盘 **16＋14**；`git worktree list`=42；`.git/worktrees`=41 | **11 枚悬空管理项**；两棵套在他车道内 |
| ④ 主区暂存/未跟踪 | 105＋165 | staged **106→117**；未跟踪展开 **547**（165 是目录折叠数）；工作区改动 485 | 令卡用折叠口径 |
| ⑤ quarantine | 6,572 | 6,581 项；drift_* 6,516；**非 drift 65 项 / 3,740 件 / 103 MB** | 本班面只含后者 |
| ⑥ sessions | 57 staging | **497 目录**（108 空／382 只剩心跳-pid／7 有实质面）；带 staging 仅 13 个 / 15 件 / 94 KB | 真正堆积是会话壳 |
| ⑦ blobs | 5.0 GB | 26,933 枚 / 5,057 MB | 分桶见 §4 |
| ⑧ gate_audit/audit | ~1.7 GB | 1.79 GiB（317 件 1.295 GB＋29 件 0.496 GB） | 轮转是否在转＝未核（§8） |
| ⑨ .runtime 根散件 | 22＋1 嵌套 | **23 枚**＋嵌套 `.runtime/.runtime` 实存 3 件 / 579 B | 波四"终清"未达成，反多 1 枚 |

## 二、死信四态分诊（内容级，禁按条数估）

尺＝袋内 blob 字节的 **git blob sha1** 对三层可达集比对：dev 现值（`ls-tree`）／dev 全史（`rev-list --objects dev`）／
任意 ref 可达（`rev-list --objects --all`）。正对照＝自算 sha1 与 `git rev-parse dev:<path>`、`ls-tree` 三方全等；
负对照＝改一字节必须不等。**尺的第一版是坏的**（把 `ls-tree` 的 `blob ` 前缀混进 sha 列 ⇒ IN_TIP 零命中假红），
修后才可用——形态同在册"零命中尺必跑正对照"。

| 态 | 袋数 | 含义与去向 |
|---|---|---|
| A_LANDED | **50** | 每件字节都在 git 对象面 ⇒ 可销（mv 归档） |
| B_UNIQUE_REQUEUEABLE | 91 | 有从未落地字节且基底==dev 现值 ⇒ 交 requeue，非销账面 |
| C_UNIQUE_WOULD_REGRESS | 1,455 | 有从未落地字节且 dev 已前进 ⇒ 盲重投即回退弹，须先救后清 |
| D_EVIDENCE_* | 2（含 45 袋部分） | blob 文件已不在盘／字节与袋记 sha256 不符 ⇒ 显式记"确认已失" |

去重后唯一待留证据面＝**5,881 枚 blob / 1.10 GB**（309 组同内容指纹覆盖 913 袋 ⇒ 一次存证服务一批）。
死因族现值：COMMIT_FAILED 309／landing 异常 300／无签名 261／ghost_session 235／cascade_stale 73／TAKEOVER-PENDING 43。

## 三、A 类试点袋账（Owner 裁①，实测不越闸）

执行通道＝在册正门 `dead_archive_letters`（三闸＋租约整体拒绝）。传送带守护 pid=34316 持租约时正门整体拒绝，
本班**不越闸**，改后台轮询抓空窗；第 33 轮抓到窗，dry-run 与 execute 各一次。

- 执行前实测 dead=1,599 → 执行后 **1,550**，归档 **49** 袋（`dead_archive_20261013/`，mv 非删可逆）。
- 计划 49 vs 期望 39：＋12（dev 在 15:2x→16:4x 间推进，更多袋转 A_LANDED）／−2（转 unlanded，处方已随台账留痕）。
- 进程外读回核实：manifest 49 行、verdict 全 `A_LANDED`、证据 sha 缺栏 **0**、
  49/49 袋在归档位重算 sha256 与台账记录**全等**（integrity＋可逆双证）。
- 属主仍活跃的 A 袋 11 只本轮不动（交其属主自处）；判活尺与执行工具同源（`SessionRegistry.list_active_readonly()`）。

## 四、blob 面（面 7）分桶与 phase2 定位

在册 `blob_gc.py` 干跑：A 活引 31／B 仅死信引 8,051（953 MB）／C2 仅 done 1,725／C1 混引 569／
**D 仅归档引 5,043（1,236 MB）＝令卡所说"未裁 phase2"那格**／Z 零引孤儿 6,142（2,320 MB）。

落差如实报：矿簿 §50 设计了 `--phase`（1=Z 类；2=+D 类逐袋核对归档 JSON 仍在），**代码里没有该旗**。
Owner 裁"phase2 本令一并裁＝随清袋走、当日不隔夜"的落地形态是给在册工具**加旗**（施工），不是跑一条命令。

## 五、maint4 / maint5 逐件判定（Owner 裁②，行集差法）

尺＝车道工作树字节 git blob sha1 对 dev 现值/全史；独有者再做**行多重集差**（lane_only／dev_only）。

| 档 | 件 | 处置 |
|---|---|---|
| 纯落后（dev 是超集） | maint4 9 件（含 `takeover_pending_gate.py` lane_only=0/dev_only=0＝仅行尾差、`commit_queue_landing.py`、`session_worktree.py`、`ch_writer.py`、`flags.yaml`…）；maint5 9 件（含 `test_batch_creation_tokens.py`） | 可复位，无字节可救 |
| 真独有—治理/维护线码面 | maint4：`thresholds.yaml` 8 行（**阈值数值**）／`ops_guard.py` 43 行／`git_commit_gateway.py` 33 行／`reconciliation_registry.py` 12 行（波四案卷点名=维护三班在途面）／`test_file_ops_enforcement.py` 100 行 | 本班**不自裁、不复位、不代签**；耐久存证＋移交（§7 呈批） |
| 真独有—册面 | maint5：`module_translation_registry.yaml` 38 行（dev_only=0＝纯追加） | 同上；热册整档快照随袋会吞他人面，禁直接搬 |
| 真独有—案卷 | maint4 `maint4_campaign/00_ledger.md` 146 行、maint5 `maint5_campaign/00_ledger.md` 361 行（**从未入库**） | 耐久存证＋移交；两班车道判死，归档会把它们丢进 24h TTL 的 rescue 面＝假留证 |

结论：这两棵车道**本班不归档**（判存疑回态④），等其属主/统筹认领；在册 archive 的 needs_rescue 处置会把未跟踪件放进
`.runtime/tmp/rescue/<sid>/`（24h TTL），正是波四"卡 A4"与在册"假留证"同病，故不当班裸清。

## 六、段三立法落点（改动即法，逐条给可复算证）

| 要写的纪律 | 落点 | 形态 |
|---|---|---|
| 死信当日四态分诊不隔夜 | `commit_queue.py` 头册 dead/ 段＋AGENTS.md §2 第 6 条 | 注释入册＋并句 |
| 删袋必留处置台账行（qid/判定/证据 sha，机生） | `dead_archive_letters` manifest | 代码：`_archive_ledger_evidence` 三栏（袋体 sha／blob 集摘要／件数），取证时刻必须在 mv 之前 |
| 内容级判定禁按条数估 | 同上＋CLI `--content-level` | 代码：`make_dead_letter_content_gate` 三态可达集门，fail-closed；默认 None 时现行行为逐字不变 |
| 收班即清 | AGENTS.md §2 第 9 条＋政策册 §2.3 新表＋`session_worktree.py` | 代码：`_prune_session_shell`（三谓词：sid 形状白名单／父目录恰为 sessions／文件全集⊆机制件集），有实质面保留并点名 |
| 主区暂存区禁无主 staged 残留 | AGENTS.md §9 第 4 条 | 并句（巡检发现即按 dev 现值复位＋留存证） |
| blob 与袋绑定清＋孤儿 GC 当日走 | `commit_queue.py` 头册 blobs/ 段 | 注释入册，指 blob_gc 单口 |
| 复发熔断 7 天衰减窗 | `commit_queue.py` 熔断实现处 | 代码：`_RECURRENCE_DECAY_DAYS=7.0`＋`window_count` 裁决面（`count` 终身累计留审计不清零）＋requeue 读实时探针 `_recurrence_fuse_hot`（袋上冻结位不再单独裁决）；**阈值 3 未改** |
| 车道内跑队列测试的隔离缺陷 | AGENTS.md §9 第 6 条 | 新红线：MUST 带仓外 `--basetemp`（见 §8 自犯②） |

等长自证：AGENTS.md 140 → **140 行**，节数 11/11、编号条目 40/40 不变（压缩 §2 第 2/3/8 条换行以并句承接新纪律）；
政策册 354 → 368 行，h2 12/12、h3 18/18、代码围栏 20/20 配对、分隔线 12/12 不变，表行 +6＝本班新表。
测试＝`test_commit_queue.py` 8 支新案＋`test_session_worktree_archive.py` 6 支新案；
**反向自证**＝同一测试文件在装主区未改码面时 8＋6 全红（AttributeError/断言），装车道码面 13＋28 passed；
`ruff check`/`format` 净。

## 七、呈批与移交（AI 不代签面）

1. **maint4/maint5 真独有 8 件**：阈值数值面（`thresholds.yaml` 8 行）与两册战役台账属"先救"，
   请统筹/维护线定 merge-or-abandon；本班只出判定与存证，不代落。
2. **面 1 执行通道与提交链结构性互斥**：`dead-archive` 要 serializer 租约空闲，而传送带守护常驻
   ⇒"当日分诊不隔夜"只能靠轮询抓窗（本次第 33 轮）。要么立法"死信归档走独立轻量锁"，要么认下"抓窗"为常态形态。
3. **blob_gc `--phase` 旗缺失**：phase2 已裁，落地需给在册工具加旗（含"D 类逐袋核对归档 JSON 仍在"判据）＋配套测试。
4. **B 类（仅 dead 引用）953 MB 体积上限**：dead 永不清理不变量下，只要死信在 dead/ 里，其 blob 就禁碰；
   销账走归档后转 D/Z 才可回收。体积归零的路径是"清袋"，不是"清 blob"。

## 八、本班自犯（全留案，不遮蔽）

1. **A/B 换面备份顺序做反**：为做反向自证，把主区 `session_worktree.py` 字节盖进车道，先存的却是"主区那份"，
   车道立法（`_prune_session_shell`＋teardown 调用）被覆掉。当窗按原文重放并复跑 13 passed 才算数。
   教训形态＝换面必须"先存 edited，再装 pristine"，且两份 sha 都打在输出里。
2. **车道内跑 pytest 把产物写进主区**：`_strip_lane_prefix` 对显式传入的 tmp 路径同样生效，含 `.worktrees/`
   的 basetemp 被截到主区同构面 ⇒ 14 支既有测试集体假红（一度被我误判成自己改坏），并在主区 `.runtime/tmp/`
   造出 `pytest_25332`/`pytest_36620` 两枚污染目录。诊断法＝同环境只换模块面做 A/B；处置=两目录已 mv 到
   本班存证区（未裸删），正解＝跑队列类测试带仓外 `--basetemp`，已写进 §9 第 6 条红线。
3. **尺第一版坏而未自知**：`ls-tree` 解析把 `blob ` 前缀当进 sha 列 ⇒ "内容已在 dev"零命中。若没加正对照就会当结论上报。
4. **能力反查留审计但晚于首行代码**，且本域四次反查全零命中；正对照（历史 12,809 行审计里 2,833 行非零）证明尺能响
   ⇒ 结论＝能力卡面对治理/队列/worktree 域失明（78% 历史反查亦零命中），属观测性缺口，不在本战役面内自修。
5. **令卡两处路径不实**：`scripts/governance/session_worktree.py` 实为 `scripts/session_worktree.py`
   （另有 `scripts/governance/session_worktree_cli.py`）；政策册实为 `docs/01_policies_and_standards/policies/`
   而非 `.../sop/governance_sop/`。均按核到为准改写，未凭卡面路径新建第二真源。

## 九、残面清单（本班未动，交下一班或统筹）

- 面 1 余量：B 类 91 袋（requeue 通道）／C 类 1,455 袋（先救后清，需墓园 30 天窗落码）／D 类 2 袋＋45 袋部分（确认已失）。
- 面 2/3 未清：164 工棚车道、20 棵死车道在册计划（7 zero_loss 直清＋13 needs_rescue）、14 棵活跃硬拒。
- 面 5/6/8/9 未逐判：quarantine 非 drift 65 项、497 会话壳（立法已给拆壳通道，存量未跑）、轮转是否在转、23 枚根散件。
- 段二未落码：当日分诊的**自动**触发腿（事件驱动，禁 cron）与主区暂存区巡检器。

## 十、复算入口（全部只读，逐条自跑过）

```bash
ls /d/ZephyrAlpha/.runtime/commit_queue/dead/q-*.json | wc -l          # 期望 1550
ls /d/ZephyrAlpha/.runtime/commit_queue/dead_archive_20261013/q-*.json | wc -l   # 期望 49
wc -l < /d/ZephyrAlpha/.runtime/commit_queue/dead_archive_20261013/manifest.jsonl  # 期望 49
wc -l /d/ZephyrAlpha/AGENTS.md                                          # 落地后期望 140
grep -c "_RECURRENCE_DECAY_DAYS" /d/ZephyrAlpha/scripts/commit_queue.py  # 落地后期望 ≥2
grep -c "_prune_session_shell" /d/ZephyrAlpha/scripts/session_worktree.py  # 落地后期望 2
```

```bash
cd /d/ZephyrAlpha && python - <<'PY'
import hashlib, json, pathlib
q = pathlib.Path(r"D:/ZephyrAlpha/.runtime/commit_queue/dead_archive_20261013")
rows = [json.loads(l) for l in (q/"manifest.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
bad = [r["qid"] for r in rows if hashlib.sha256((q/f"{r['qid']}.json").read_bytes()).hexdigest() != r["bag_json_sha256"]]
print("台账行", len(rows), "| 归档位 sha 不符", len(bad), "| verdict", {r["verdict"] for r in rows})
PY
```
