---
ttl: task_bound
---
# L4 静态清单计数失真修齐（尺Q/尺R 对症）· 挖矿簿

> 环节=E08 ｜ 子环节=4（分母复算 / 检测器半盲 / 落地通道自锁 / 修齐与判据）｜ 状态=封矿·已施工·worktree 已 GATE-21 PASS

## 子环节 1｜分母复算（本包亲算，不抄案卷）

`git show HEAD:<册>` → `yaml.safe_load` → 声明标量 vs 同名段长度：

| 册 | 声明 | 实际 | status 子集 | 定性 |
|---|---|---|---|---|
| `gate_registry.yaml` | `total_gates: 174` | `gates` 180 | active 169 / deprecated 11（169+11=180）；source 维 pre-commit 55 / commit-gate 113 / manual 12 | 174 **不等于任何子集** ⇒ 纯陈旧标量（非"声明的是子集"） |
| `rule_catalog_registry.yaml` | `total_files: 274` | `files` 292 | 条目 status：active 164 / '' 113 / draft 10 / archived 5 | 同为陈旧标量 |

成因链（`git log -L10,10:gate_registry.yaml` 逐笔核标量）：`9b0c31ab12` 起 174/174 自洽 →
`7e9083ff9e`（09-23 11:50，袋 `st-gslim-20260923-0016`，袋内 theirs 本身 **180/180 自洽**）落地后变 **174/180**，
其后 `a52cd5f466`/`5c1107db84`/`48acb99c46`/`906496b808`/`b88b8fec5d`/`b9c60ef24b` **同一签名反复复发**。
⇒ 结论=队列合并器每次都推进 `gates` 段而把标量钉在 ours 旧值——**不是人Write错，是通道必然产出**。

## 子环节 2｜检测器半盲（这才是"带病 2 天不愈"的真根因）

`generate_gate_registry.py --check`（:680-686）只比 **`existing["total_gates"] != output["total_gates"]`**，
从不比 **`declared vs len(磁盘 gates)`** ⇒ 生成器与磁盘段一致而标量单独烂掉时**恒绿**。
本包实测该形态：`generate()` 内存重算=180，且 180 条与 HEAD 段**逐条 dict 全等**（`gen-only=[] disk-only=[] dicts differing=0`）
⇒ 磁盘唯一差异就是 `-total_gates: 174 / +total_gates: 180`（+时间戳），**"生成 vs 磁盘"这一半永远看不见它**。

同族第二实例（案卷未载，本包新发现）：`rule_catalog_registry.yaml` 的失真**根本不在检测面里**——
`validate_static_manifest_drift.CHECKS` 只列 script_manifest / gate_registry / .importlinter 三台。

## 子环节 3｜落地通道自锁（尺R 复核 + 一处比案卷更狠的实测）

`is_registry_mergeable`（`landing:197-201`）= `catalogs/` 前缀 ∧ `.yaml` ⇒ 两册皆在条目级合并作用域。
合并器只重排**条目块**，非列表头部/标量行**逐字取 ours**（`:687 merged 由 ours_text.splitlines() 组装`）。
本包把尺R 的两条分支各测一遍：

1. theirs 只改标量 → `merged==ours` → `_merge_registry_file` 返回 None → noop/"ok"（**尺R 结论复证**）；
2. **theirs 同时改标量 + 新增一条族内条目 → 条目落地、标量仍 174**（案卷未载，比"单行必被吞"更狠：
   ⇒ 案卷给的处方 (i)"和族内改动同批"**不成立**，不能作为绕行通道）。

各通道判定：队列（含 `--from-bag`）＝结构上永远送不进标量；
会话工作树 `session_worktree_commit` 的 index 以**会话分支 HEAD** 为 base → 提交本身带标量，但 merge 回 dev 要**裸 `git merge`（禁）**；
**唯一在册可审计通道＝`scripts/git_commit.py` 直提模式（无 `--enqueue`）**，
先例=`21c1aa5d61`（09-24 08:55，`in_process_gate_registry total_gates 99→102`，numstat `19 1`，
尾注 `[GW:st-library-final-20260924]` 无 `:q-` ⇒ 走的正是网关直提）。
⇒ 本包按该先例落地，并留判据"HEAD 侧标量必须==实际段长度"。

## 子环节 4｜修齐动作（全部生成器产出，零手写数字）

1. `validate_static_manifest_drift.py` 补**册内自洽**检查（声明标量 vs 同名段长度），并把
   `rule_catalog_registry.yaml` 纳入 CHECKS（作用域本包先只点这两台——尺Q 实测出的两台；
   扩到全 catalogs 是加文件名一行的事，**本窗刻意不扩面**：其他会话批次在飞，避免把无关提交打红）。
2. 把 `--auto-fix` 从"被忽略的参数"改成**真跑各台的 fix 命令**：
   `reconciler._fix_yaml_append`（:246）一直按这个契约传 `--auto-fix`，而脚本 `main()` 写死
   "--check 是唯一模式…忽略其他参数" ⇒ **映射到空操作**，这正是案卷第三态问题
   （"在册＋能红＋有 auto_fix 映射却带漂移 2 天"）的判别答案＝处方 (b)：auto_fix 与失真类型不匹配。
3. `python …validate_static_manifest_drift.py --auto-fix` 重算并写入两册 + script_manifest + .importlinter。

## 判据（worktree 实测已达成，E11 在主区复跑）

- `… --check` 修前 rc=1 报 **5** 项（含新立的 2 项自洽 DRIFT：`total_gates=174≠180`、`total_files=274≠292`）；
  修后 `--check` **rc=0，GATE-21 PASS** ⇒ 同一把尺既能红又能绿（非恒红非恒绿）。
- 逐字段差分零净损：`gate_registry` 条目 180→180 变化 0 字段净损 0；`rule_catalog` 292→292 同上；
  `script_manifest` 452→448，消失 4 条**全部 NOT_IN_HEAD 幻影**（见 L3 §子环节 4），真实资产零损。
- 消费面自愈：`scripts/context/generate_architecture_context.py:132` 与
  `sync_audit_protocol_numbers.py:75,102-106` 读的是该标量 ⇒ 修前把"少 6"印进生成上下文与合规散文，修后自动正。

## 落地凭据（实测）

- `gate_registry total_gates 174→180` 已由网关直提落地＝`052c2817f4`；
  复核=`git show HEAD:...gate_registry.yaml` 解析后 `total_gates==len(gates)==180`【亲验】。
- 通道结论已由实物证实：同一内容的队列袋 `0006`（被全局锁改道产生的无基底袋）与直提 `052c2817f4` 并存，
  只有后者改变了 HEAD ⇒ "标量经队列送不进"不是推断而是实测。
- `rule_catalog total_files 274→292`＝由属主批在主区重生成到位（本包让路不投，见 R-7），
  本包贡献的是**让它从此可被检测**（GATE-21 新立 selfcheck 台）；HEAD 面归零随该会话落地。


## 子环节 5｜派生计数标量在**落地侧自愈**（④ 号任务从"能报红"升级到"不再需要谁直提"）

- 为什么"再跑一次生成器 / 再直提一次"不是解法：注册表族经队列时走条目级三向合并，
  该合并器对**标量与头部行恒取 ours（dev 侧）**——这是防热册头部被陈旧快照吃掉的正确设计，
  代价是 `total_gates`/`total_files` 这类**派生值永远进不来**。实测：本包 052c2817f4 把
  total_gates 直提成 180，随后被两只陈旧袋压回 174；rule_catalog 停在 274 而实际 292。
  只要还依赖"某人恰好拿最新基底直提"，失真就会周期性复发（事实复发了一次）。
- 治本（`commit_queue_landing._heal_derived_totals`）：条目合并完成后，按段实际长度就地
  重算声明标量 ⇒ 任何一只碰这两册的袋都会顺手把标量修对，热册标量从此不需要直提。
  行级改写不用正则：只认"顶层『键: 整数』"且原样保留行尾（CRLF 仓里把一行改成 LF＝
  制造混合行尾，是另一种失真）。
- 口径同源：配对表 `_DERIVED_TOTAL_PAIRS` ＝ GATE-21 selfcheck 的 `pairs`（检测器判红、
  落地侧改对，两份配置各写一次必漂移）；一致性由永久尺
  `test_landing_pairs_agree_with_gate21_selfcheck` 断言，`validate_static_manifest_drift.py`
  新增 `derived_total_pairs()` 读口。
- 保守面（红队 C7）：顶层同名标量**必须恰好一行**，多行/缺位一律不动（YAML 重复键
  `safe_load` 取后者、改写取前者 ⇒ 会把错值写进非权威行、让 GATE-21 永红并振荡）；
  段不是集合、标量不是整数、计数已一致 ⇒ 不动；YAML 解析失败 ⇒ 只 log 不抛
  （自愈是附加收益，绝不因此把本来可落地的袋变成死信）。
- 遗留约束（红队 C8，登记不自行扩面）：若某标量同时有"生成器扫描数"与"条目列表长度"
  两个权威，今日相等（gate_registry 180==180）故 latent；日后不等则自愈会把生成器台判红
  并触发 `--auto-fix` 整册再生。真解＝在 registry_family 册内显式声明"该标量唯一权威＝段长度"，
  属跨包改造（要动他包在飞的生成器），本夜不做。
