---
ttl: task_bound
session: st-circ-a6-20260930
batch: 第4批/A6 挖矿簿 5/6
---

# S4-E 手术单 — B4 tracked 快照 4→1（硬阻断安全门指纹语义去重）

> 立档：2026-09-30 ｜ 车道：A6（design-only，不附代码）
> 真源文件：`src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py`、`gate_cache_preflight.py`
> 语义边界：B4 此处=第 4 批挂账项「tracked 快照 4→1」，非 commit_speedup_campaign 的「B4 排队键」（同名异指，勿混）

## 1. 现象量级（遥测实证）

- 一次标准提交（D2 出锁路径）对**同一批 own 文件的 tracked 面**做 **4 次独立捕获**：锁外 3 类 + 锁内 1 类，全部是 `run_git` 子进程批扫（200 文件/批）。本窗唯一绿样本通道 25.7s 中框架外 git 批扫占比虽小，但每次 spawn+全文件字节读在 10+ 文件、冷 OS 页缓存时是秒级票；且四处捕获口径相近、时刻不同步——**同一份 blob sha 被反复重算**。
- D2 出锁手术（2026-09-30 落地）后这是通道锁外段的主要残余重复 IO；E4 数据显示锁外段耗时直接叠加进等锁会话的等待面。

## 2. 机理锚点（四处写点全列）

| # | 位置 | 捕获 | 语义 |
|---|------|------|------|
| 1 | `git_commit_gateway.py:3565-3585`（调用 ：2749） | `git status --porcelain` 批扫 | head guard：本提交面相对 HEAD 零变化→跳过锁外通道（D2 矩阵7 守卫） |
| 2 | `:3587-3605`（调用 ：2750） | `git hash-object` 批扫 | 锁外内容快照 `{rel: blob_sha}`（删除=MARK），通道判定采信的根基 |
| 3 | `:3607-3624`（经 `:3626-3634` 指纹复核，调用 ：3992） | `git ls-files -s` 批扫 | 锁内 staged 指纹复核（TOCTOU 守卫本体）——**语义必保，不可合并** |
| 4 | `gate_cache_preflight.py:186-201`（锁外 ：2708 + 锁内重验 ：2786） | `git write-tree` + `rev-parse HEAD` | P2⑦ 预跑采信指纹 F/F′（全局面 staged 树+HEAD+flags mtime） |

**语义红线**：#3（锁内复核）与 #4（锁内 F′==F 重验）是「漂移→锁内重跑」安全语义的本体（:2740-2745 注记「判定零放松」）——**4→1 只能收敛锁外捕获面，锁内复核两次调用一次都不能少**。

## 3. 设计（意图，不附码）

**原则：锁外 3 次捕获→1 次统一快照；锁内复核原样保留。**

1. **统一快照对象**：锁外单次 `git hash-object` 批扫产出 own 面快照（#2 现物），其余锁外消费点全部改为从它派生：
   - #1 head guard：快照 vs `git ls-tree HEAD --`（同一批文件）比对判零变化——替代 status 扫。**边界保留**：status 面=staged∪工作树∪未跟踪∪ita，ls-tree 面只有 tracked HEAD——为不放松守卫，guard 改为「快照比对 HEAD 树 + 保留一次 status 兜底**仅当**快照比对判绿」（或施工时实测证明 own 面 ita 情形可由 :2777 ita 清扫覆盖后裁撤，二选一，宁保守）。
   - #4 P2⑦ 指纹：own 面分量由快照派生；`write-tree`/`HEAD_sha` 全局面分量**保留原公式不动**（Fingerprint.matches 采信语义零变化——gate_cache_preflight.py:70-72 明文「公式未动」边界）。净收益=write-tree 那次 spawn 保留、own 面重算消失；若派生后 :2708/:2786 两处 F/F′ 仍各自全算，属#4 内部的锁外/锁内对称（语义本体），不算重复。
2. **消费面改动收敛为两函数**：`_run_precommit_channel` 调用点（:2746-2754）与 gate 预跑编排（:2702-2739）共享同一个快照捕获结果，一次捕获一参透传。
3. **不动面**：#3 锁内 `ls-files -s` 复核、#4 锁内 F′ 重验、指纹失配→锁内重跑、快照设施故障→None 回退（:3591/:3599-3603）、200/批分批、删除文件 MARK 语义。

## 4. 红测两针

- **R-E1 锁外捕获次数断言**：monkeypatch `run_git` 按子命令计数。一次绿路径提交（out-of-lock 开启）锁外段 `hash-object` 捕获必须=1、且 #1 的重复全面扫描不再出现——**现码 status+hash-object 双扫（各≥1 次独立批扫），对「锁外 own 面捕获总数=1」断言必红**。
- **R-E2 漂移必重跑锚（语义不放松）**：锁外快照捕获后、锁内复核前注入 staged 漂移（改写同批文件内容）→ 提交必须走锁内全量重跑通道且终局判定与现行逐字段一致——**现码绿（此测是 4→1 合并的等价性锚：任何把锁内复核也合并掉的实现在此必红）**。

## 5. 差分矩阵

1. 快照设施故障（hash-object 非 0）→None 回退锁内全量；2. count≠batch 数→None（:3602-3603）；3. 删除文件→MARK 语义逐字节等；4. >200 文件分批边界；5. 锁内 staged 漂移→重跑（R-E2）；6. 他人推进 HEAD（F′ 失配→重跑）；7. 零变化守卫真阴（真零变化→跳通道）与真阳（有变化→跑通道）两向；8. 含 ita 残留文件集（guard 保守分支）；9. merge_finalize 跳过（:2747）；10. own 集为空（:3686-3687 提前 return）；11. flags.yaml 变更（P2⑦ mtime 分量）；12. `ZEPHYR_PRECOMMIT_OUT_OF_LOCK=0` 回退路径全绿。

## 6. 风险与回滚

| # | 风险 | 缓解 | 残余 |
|---|------|------|------|
| 1 | head guard 换面后未跟踪/ita 情形漏判→跳过本该跑的通道（**放水方向**） | §3.1 保守分支：判绿后保留 status 兜底一次（净省的仍是 hash-object 重算）；红测例 7/8 双向覆盖 | 全裁撤 status 留待 ita 清扫覆盖证明后另裁 |
| 2 | 快照捕获与通道执行之间文件被改（锁外窗口固有） | 锁内 #3 复核语义原样——本单不触碰该窗口 | 既有窗口，零新增 |
| 3 | P2⑦ 指纹派生改公式 | 全局面分量公式不动，own 分量只换数据来源；`Fingerprint.matches` 不改；矩阵例 6/11 | 低 |

回滚：改动集中于 `_run_precommit_channel` 调用编排与 guard 函数，单 commit revert 净退；`ZEPHYR_PRECOMMIT_OUT_OF_LOCK=0` 整体回锁内路径兜底。

## 7. 估时

| 步 | 内容 | 估时 |
|---|------|-----|
| 1 | R-E1/R-E2 红测先跑（E1 现码取红，E2 现码定绿基线） | 0.5 h |
| 2 | 统一快照捕获+两消费点透传 | 1.0 h |
| 3 | head guard 保守分支改造 | 0.5 h |
| 4 | 差分矩阵 12 例全绿+真实提交计时对照 | 1.0 h |
| 合计 | | **3.0 h** |

## 8. 执行留痕（施工车道 G1 · st-circ-g1-20260930 · 2026-09-30/10-01）

**状态：已施工落地。** 改动面=`git_commit_gateway.py`（守卫函数+编排点两处）+`tests/governance/test_precommit_channel_out_of_lock.py`（+7 例）；`gate_cache_preflight.py` 零改动（见边界裁决②）。

- **红测先行实录**：施工前 R-E1+分批边界例=红（现码 guard status 扫在案 `guard_status_calls==1`）；R-E2 漂移重跑锚+保守分支双向+设施故障+删除面=绿基线（14 绿 2 红）。施工后 **16/16 绿**（本文件套件）+回归 `test_commit_chain_campaign_20260922.py`(38)+`test_gate_cache_preflight.py`(13)+`test_gate_cache_key_isolation.py`(6) 全绿=**57 绿**；ruff 0.15.10 双净（format+check，只净己行；:2349/:4611 noqa 警告为存量非本袋）。
- **实现形态**：①编排点快照先捕获单点化（`_precommit_snapshot_blob_shas` 唯一 own 面内容捕获），guard 改 `_precommit_head_guard_skip(existing, snapshot=…)`；②新增 `_snapshot_differs_from_head`：`git ls-tree -r HEAD` 单次元数据扫+casefold 映射派生零变化判定（ls-tree 不支持 `:(icase)` 魔法 rc128 实证→Python 侧 casefold 对齐原 icase 语义）；③快照判绿保留一次 status 兜底（簿 §3.1 保守分支，index 漂移面=兜底存在本体证明，红测 `test_m_e_guard_conservative_status_fallback_on_snapshot_green` 双向锚）；④快照 None（设施故障）→本块整体跳过=锁内全量，守卫扫描一并省去（判定等价）。
- **边界裁决**：①锁内两次复核原样（#3 `ls-files -s` step5.5、P2⑦ F′==F），R-E2 注入点改用锁内首个 own 面清扫 `_sweep_intent_to_add_residue`（严格晚于快照/早于复核，`calls==["run","run"]` 锚在案）；②#4「own 面分量由快照派生」裁决为零改动——现 `compute_fingerprint` 公式=write-tree+HEAD+flags mtime，**无 own 面分量可派生**（簿自引 gate_cache_preflight.py:70-72「公式未动」边界优先），F/F′ 锁外/锁内对称按簿原文「不算重复」保留；簿 §3.2「预跑编排共享快照」落实为：预跑块与通道块共同上游只此一次快照捕获，透传经 `precommit_preflight` 元组。
- **差分矩阵落点**：1→`test_m_e_snapshot_facility_failure_falls_back_to_in_lock`（rc128 非异常形态新增）；3→`test_m_e_guard_deleted_face_conservative`；4→`test_m_e_batching_over_200_files_snapshot_vs_head`（201 文件跨批双向，ls-tree 单扫天然免分批）；5→R-E2；7 双向→`test_m_e_guard_true_zero_change_skips_channel`+conservative 兜底例；8→conservative 兜底例（ita/index 漂移面）；9/10/12→D2 既有例承载（merge 跳过/空集/回退手柄，全绿复验）；2/6/11→既有窗口与 P2⑦ 未触面（preflight 套件 19 绿复验）。
- **真实计时对照（本仓 18959 tracked 实测，best-of-3）**：`ls-tree -r HEAD`=83.7ms 恒定（单 spawn 元数据）；`status --porcelain` icase×3 路径=35.4ms（随 own 面分批线性涨）。净收益本体=own 面全字节读 2 次→1 次（status 内容扫退役）+大 own 面 spawn 数 O(n/200)→O(1)；小面单看 spawn 持平略换手，符合簿 §1「同一 blob sha 反复重算」主攻向。
- **让位/偏离登记**：①CapabilityLookup 反查失败——`capability_canonical_file_registry.yaml`:57789 YAML 断裂（`di_seam_exemptions: []` 后裸 list 项，st-matrix-final-20260930 在飞 MM 态），非本车道文件不代修，按宪法走 no-lookup 逃生登记此处；②`git_commit_gateway.py` 发现 st-circ-a2-20260930 过期 claim（夜战 A2 debt 棘轮 192 行 staged 在案、无在飞心跳）——lock_files 自动回收后本会话 reclaim，A2 内容随本袋提交按调度指令 FOREIGN→adopt 通道收编（归属披露于 commit message）；③基线 66 绿（含 A2 staged 内容）先验证后收编。
- **提交通道实录（2026-10-01 00:5x→02:0x）**：①直连首投被 CREATE-GUARD 假红拦（簿 token 已由 st-circ-a2 登记入册 creation_tokens 精确匹配实测 True，但预检落地仿真读 HEAD 版册无此 token——token 批滞留 index 未落地）；lookup 册修复后补做正式反查 4 关键词留审计过 CAPABILITY-LOOKUP 门。②直连 FOREIGN_CHANGE（A2 内容在案）按处方 --adopt-prior-work——发现 adopt 只在**新鲜 claim** 生效（claim 快照磁盘持久化+幂等跳过重捕获），按 §2.3 release→re-claim→adopt 三步走通（gate 放行附 adopted 审计）。③直连再被 DOC-HEADER-SUITE 拦：st-menu-t1b5-20260930 在飞件 macro_regime_sensor.py BLUEPRINT 头 token 误植（他会话在途不代修，§3.4），该门 own_scope:False 全暂存面扫描=连坐——按宪法 §2.6 改走提交队列（serializer 干净落地面对共享暂存面结构性免疫）。④SESSION-REQUIRED 补注册（pid=0+心跳 daemon 30s 在案）后 q-20261001-st-circ-g1-20260930-0001 入队（码+测两件；手术簿留痕件因 token 滞留 index 与码分离后投，落地后核对归属）。

- **终投落定与运维留痕（2026-10-01 04:5x，补记）**：④后半程队列三连死信（q-0001 SESSION-REQUIRED=心跳 daemon 对 legacy 册 Permission denied 即退+会话被 watchdog 收割；q-0002 WinError 233 管道断裂疫 env_retry 耗尽；q-0003 CAPABILITY-OVERLAP=收编内容携 A2 `_precommit_debt_ratchet_enabled` extract 级克隆债，干净落地面上 CloneGuard 仍命中袋内容）——A2 会话心跳停滞 70min+、8 袋全死=收编债无主，按宪法 RULE-CLONEGUARD 合理重复通道（84 条 acknowledged 先例同型：env 开关读取惯用样板）echo-guard.yml 登记 2 对（cg-gw-debt-ratchet-outoflock/shards-20261001，verdict=intentional，追责/复议面注记 A2 复活续作）随码同 commit 原子落地。再清三处收编内容落地阻（均 A2 原作零语义机械修：a. ruff UP012 `encode("utf-8")`→`encode()`；b. RELATIVE-PATH-LITERAL 对 lstrip 字符集裸 `"./"` 字面量误报→提常量 `_DEBT_ANCHOR_STRIP_CHARS`；c. A2 自设 debt-ratchet 棘轮冷启动洞=基线 0 键入册（precommit_global_debt_baseline.json updated=2026-09-30T20:56Z 空种子），vendor/Kronos 存量债全判净增——按该门自附处方「回退手柄 env ZEPHYR_PRECOMMIT_DEBT_RATCHET=0（须运维登记留痕）」**进程级单次**使用（仅本次 commit 进程，棘轮对他会话保持 ON），登记=本条。终局：commit `04a30978`（full=04a309786995a9a26bd0b7c43ef761993d7c3b8f）五件套落地（码+测+echo-guard+两簿），git log -1 --name-only 核归属=恰 5 文件无连坐；post-commit 复验 35 绿（本簿套件+preflight+key_isolation）+A2 棘轮自测 13 绿（机械修语义零变化实证）。工作面 03:4x-04:4x 间遭整面 stash（455 文件，stash@{0} 无 notice，违 §2.8 告知义务），本会话五文件按 §2.8 按文件 checkout 恢复后终投；stash@{0} 遗留他会话 450+ 文件待其本人处置，本会话未 pop。
