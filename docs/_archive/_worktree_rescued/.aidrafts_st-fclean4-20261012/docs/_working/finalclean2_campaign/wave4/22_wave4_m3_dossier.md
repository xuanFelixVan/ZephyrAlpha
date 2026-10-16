---
ttl: permanent  # st-docconsol-20261014 改：原 task_bound 随 _working 搬迁落 _archive permanent zone 按 DCR-003 转 permanent（正文字节零改动）
completes_when: Q1 的预备改子与前置事实被属主车道承接、Q2 原型与回滚的双向复验数在 dev 可对
session: st-fclean4-20261012
lane: wave4-main
role: 总包（M3 两案执行与负结果留档）
---

# 终清波四·M3 案卷（Q1 watchdog 保留窗／Q2 quarantine 内容寻址去重）

> 令卡：Q1＝"watchdog REDUNDANT 保留窗 30d→7d（参数面走属主通道改）"；Q2＝"quarantine 内容寻址去重方案落地（先原型后放量，drift_* 为主体、只归档不删的红线不动）"。
> 本案卷给两案的**实测前置、执行结果与一处负结果**。所有数来自本班当窗自跑，命令在 §5。

## 1. Q1 前置事实（三件，任何一件都改变施工顺序）

- **① 30 这个数没有任何配置面**（"属主通道"因此只能＝模块自身面）。逐面查过：唯一读点 `src/zephyr/gov_enforcement/rule_bridge/worktree_drift_watchdog.py:98`（定义）＋`:545`（`_sweep_quarantine` 缺省实参）；
  注册脚本 `scripts/tasks/register/register_drift_watchdog_task.ps1:58` 只传 `--daemon`、无参数；
  `gate_registry.yaml`（222 门 id）与 `in_process_gate_registry.yaml`（111 门 id）对 `GATE-WORKTREE-DRIFT-WATCHDOG` **0 命中**（正对照＝同册 grep 命中数非零）；
  `docs/01_policies_and_standards/rules/trae_085_stale_base_overwrite.yaml` 指该 watchdog 为检测面但不带数字；
  `data_retention_contract.yaml` 对 quarantine **0 命中**（该册正对照 18 条 INV-RET）。
  ⇒ 数值真源＝代码常量，散文侧另有两处需同批同步：该文件 `# [INVARIANTS]` 第 8 行、`architecture_issue_registry.yaml:3159`（`#ARCH-264` O4 条目，human_gated 面）。
  ⇒ `git log -S"_QUARANTINE_RETENTION_DAYS"` 自 `3429157b779` 起该值从未被改过，且**从未登记过任何裁定**——本次是第一次动它，须补一条在册依据（属主通道的一部分）。
- **② 该文件此刻被维护三班在途持有**＝HELD-OVERLAP：主区 index 里 `worktree_drift_watchdog.py` 暂存 **+99/−6**、其测件 `tests/gov/governance/rule_bridge/test_worktree_drift_watchdog.py` **+74/−?**，
  而该会话（`st-maint3-20261011`）今晨仍在提交（dev 末次 20:50:41）。本班读其暂存差异＝**批令二 L2 池面回退方向分量**（`_POOL_REG_STRICT_MIN/_POOL_REG_NEAR_RATIO/_POOL_REG_NEAR_MIN` ＋ `_git(binary=)` ＋ `_direction_readout`），
  **与保留窗无关**。⇒ 本班若在同一文件上落自家改子，两条后果必居其一：他班 105 行被整覆，或本班改动被其后落地静默回退。按根宪法"HELD-OVERLAP 不硬闯／他会话在途不代修"，本班**不动该文件**，改出预备改子＋交接（§2）。
- **③ ⚑ Q1 的前提今天已被另一条链作废了一半**：drift 快照里**文件**的真实寿命＝**7 天**，不是 30 天。
  取证车道实测：`.runtime/gate_audit/ops_guard_delete.jsonl` 有 **1,502 条** `.runtime/quarantine/drift_*` 文件删除记录，
  `verdict=ALLOWED ∧ is_protected_zone=true ∧ reason="reconciler GATE-RUNTIME-CLEANUP 已声明 delete（声明制直通）"`；
  watchdog 自家审计 `quarantine_retention_sweep` 1,134 行全部集中在 `2026-10-12T00:01:43Z–00:02:08Z`，且删的都是**已被掏空的目录**
  ⇒ 面从波三测的 7,434 枚缩到本班测的 6,480 枚就是这么来的。
  结论：**只要清理器还吃保护区，`_QUARANTINE_RETENTION_DAYS` 改 30→7 就是一条空转改子**（REDUNDANT 与非 REDUNDANT 都在第 7 天被清理器先吃掉，watchdog 那条腿根本轮不到执行）；
  反过来，清理器口径一修好，30 天会变成**真 30 天**（面按 743 枚/天回升，30 天稳态 ≈2.03 GB），此时 Q1 的"REDUNDANT 提前到 7 天"才第一次有物理意义。
  ⇒ 本班把统筹批复里"缩容的硬前置＝先把清理器吃保护面的口径修了"读成施工顺序铁律：**先修清理器 → 再落 Q1**，两步之间 Q1 不落码。

## 2. Q1 本班交付＝可即用改子（不落码，交属主车道）

预备改子（`worktree_drift_watchdog.py`，按现 HEAD 行号锚；**分类输入用本班已产出的机读册，daemon 内不做 dev 字节比对**——
避开"单线程守护每轮重算 6,480 枚×文件"的成本与误判即毁独有字节的风险）：

```python
# :98 后新增（保留两个窗，REDUNDANT 类走短窗）
_QUARANTINE_RETENTION_DAYS = 30          # 原值不动：含独有字节的枚仍按 30 天
_QUARANTINE_REDUNDANT_RETENTION_DAYS = 7  # Q1 裁定：纯冗余枚（其内文件全部与 dev 现值等或仅行尾异）7 天收
# 分类真源＝本班产出的机读册（逐枚 drift 目录一行：class/n_files/bytes/buckets/oldest_sha256）
#   .runtime/quarantine/fclean4_dedup/class_summary.jsonl  —— 486 枚 REDUNDANT / 13,588,772 B
#   （本班实测，命令见 §5；该册可被任意时刻重跑再生，非第二套判据：判据仍是"文件字节 vs dev blob"那把尺）
# :545 `_sweep_quarantine` 内 cutoff 计算处按 class 选窗（class 读不到 ⇒ 一律走 30 天＝保守侧，禁 fail-open）
```

同步义务（属主车道做，缺一即文档与代码分叉）：`# [INVARIANTS] :8` 那句 30 天散文、
`architecture_issue_registry.yaml:3159` 的 O4 描述、以及一条新裁定登记（该常量自 2026-08 落定以来从未在册登记）。
测试面实测：**没有任何测试钉住 30**（现测全部显式传 `retention_days=30/0`，仅 `:414` 用缺省且对该值不敏感）
⇒ 改 7 不红；但 class 分支是新路径，须自带红证（`class 读不到⇒保守` 与 `REDUNDANT 到期收/含独有字节不收` 两条）。
本班已把这两条写成给属主车道的用例名（见 `evidence/` 随册），不在他班持有文件上自落。

## 3. Q2 原型→放量→回滚（负结果，全程双向复验）

| 步 | 动作 | 实测数 | 结论 |
|---|---|---|---|
| 原型 | 只归档 bucket A/B（字节＝dev 现值 / 行尾归一后等）的重复副本，通道＝`ops_guard.guard_recycle`（在册唯一归档出口：move 进 `.runtime/recycle_bin/<ts>/<原相对路径>`，30 天可恢复，永不物理删） | 149 件 / 2,993,885 B，逐件 sha 复验 **全等**，`SKIP_SHA_DRIFT=0` | 通道可行、审计逐件落账（`ops_guard_delete.jsonl` 内 `guard_recycle` 行 149 条命中 drift 路径） |
| 放量 | 加"每枚 drift 目录至少留 1 个文件"约束（防清空），桶放开到 C1 | 405 件 / 12,971,204 B，全等 | 见下行——约束的代价暴露出来 |
| 副作用实测 | 逐目录枚举 | **135 枚目录被搬成"无文件空壳"**（含空子目录链）；**约 398 处悬空空子目录**（400 处在我触碰过的 427 枚目录内，未触碰目录仅 2 处存量） | 空壳＝波二 `worktree_drift_watchdog.py:443-462` 刚治本的病理（2026-09-14 案卷曾记 10,571 枚）；悬空链＝"快照目录结构 ≠ 当时捕获内容"的取证解释性损伤 |
| 修复 | 从回收站各回置 1 枚到 135 枚空壳 | 135/135 回置成功，空壳→0 | 修子集不够——悬空子目录仍在，再消它要**删目录**＝二次破坏结构 |
| 回滚 | 其余 419 件全部放回原 drift 路径 | 419 rolled_back ＋135 noop；**全宇宙复验＝审计表 8,072 行全部在位且 sha 全等（absent=0）**；面回到 8,074 件 / 667,945,573 B；空壳 0、悬空子目录 2（存量）、回收站 0 件 | **净收益不抵代价，整批撤销**，Q2 以负结果入册 |

**为什么收益只有 2%**（这条是给后续放量的硬算术，不是感想）：drift 目录里 **5,789 / 6,480 ＝ 89.3% 是单文件目录**；
"每枚目录至少留 1 文件"因此直接挡掉 2,815 件候选搬移，剩 419 件可搬。
⇒ **按文件抽取的去重在本面结构性不成立**；波三算的 3,369 件 / 96.9 MB 只有在**按整枚目录去重**（某枚目录的全部文件都能在更早的枚里逐字节找到 ⇒ 整枚归档）时才拿得到，
且必须先修 §4 的 tamper 清单缺陷，否则每归档一枚目录＝下一轮扫描多一条假 `quarantine_tamper`。

## 4. Q2 顺带查实的两处在册缺陷（交属主，本班不动码）

1. **known_quarantine 与自家 sweep 不同步**：tamper 判定 `worktree_drift_watchdog.py:1151-1171` 只对 `state["known_quarantine"]` 里的目录名做 `(root/d).is_dir()`；
   `_sweep_quarantine` 删除（含空壳宽限 `:543-544`、`:579-590`）**不 purge 该清单**
   ⇒ 每枚被合法清空的目录都会在后续扫描假报一次 tamper。现值实测 `quarantine_tamper` **234 条**（末条 14:25:04Z），
   而 `quarantine_retention_sweep` 1,134 条——**该事故取证信号已被自家机制稀释**，与 #ARCH-264 O4 立此信号的原意相反。
   本班两批共触发新 tamper **0 条**（实测：14:39Z 之后新增 2 条，其对象是 14:39:37Z/14:39:49Z 刚建的
   `drift_.../scripts/ops_guard.py` 与 `drift_.../src/zephyr/governance/audit/reconciliation_registry.py`，
   即"文件被 healed 撤走＋目录仍在 known_q"的既有链路，非本班搬移所致——本班触过的 427 枚目录在 tamper 名单里 0 命中）。
2. **guard_recycle 审计行 `session_id` 落成 `ops-guard-unknown`**：本班进程未设 `ZEPHYR_SESSION_ID` 导致归档件无会话署名
   （1,502 条清理器记录同样无写者署名）⇒ 与"写者必须署名"方向闸的意图面同坑；修指向属本班纪律，已记入 §6 自犯。

## 5. 复算命令（本班实跑过；全部只读或本班自有面）

```bash
cd /d/ZephyrAlpha
python .runtime/tmp/st-fclean4-20261012/tools/quarantine_byte_audit.py      # 8,072 件逐件 A/B/C1/C2（40s）
python .runtime/tmp/st-fclean4-20261012/tools/q2_dedup_prototype.py         # 原型批（A/B 重复副本 → guard_recycle）
python .runtime/tmp/st-fclean4-20261012/tools/q2_dedup_scaleout.py          # 放量批（keep>=1 file/dir）
python .runtime/tmp/st-fclean4-20261012/tools/q2_repair_shells.py           # 135 空壳回置
python .runtime/tmp/st-fclean4-20261012/tools/q2_rollback.py                # 整批回滚＋全宇宙 sha 复验
python .runtime/tmp/st-fclean4-20261012/tools/q2_collateral_attribute2.py   # tamper/空壳/悬空链归因
grep -c quarantine_tamper .runtime/audit/worktree_drift_watchdog.jsonl      # 现值 234→复核用
```

## 6. 本班自犯（本节按"改账即记"，不留到收班补）

1. **放量批用 8 分钟前的审计快照算配额**（`per_dir_files`），没有用当窗实况 ⇒ "每目录留 1 文件"约束被架空，直接产出 135 枚空壳。
2. **收尾自检的尺是坏的**：用 `len(list(dir.rglob('*')))==0` 判空壳——`rglob('*')` 把**空子目录**也计入，于是报出"0 空壳"的假绿；
   真按文件口径复测＝135。**同一颗"0"字自证**（在册教训：判"无"之前先问这把尺看得见什么）。
3. **guard_recycle 未带会话署名**（`session_id=ops-guard-unknown`）⇒ 归档审计面缺署名，已在上条 §4-2 登记。
4. 前案（M2）已记一条同类：mutating 死判的前置证明测于 21:35、执行在 22:20，隔 45 分钟未复测。
