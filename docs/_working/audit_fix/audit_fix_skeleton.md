---
ttl: task_bound
---
# 审计遗留修复总包 · 骨架（环节普查与封矿判据）

> sid=st-audit-fix-20260924 ｜ 立项 2026-09-24 14:3x ｜ 真源=docs/_working/audit_all/audit_fix_ledger.md（1368 行，第 1–9 轮）
> 本文=施工前"挖环节"的收口件：**先量分母，再逐环节挖子文档，全数封矿才进施工 SOP**。

## 0. 为什么先挖环节（本包的立项判断）

审计班第 9 轮把病案立到 6 个案号（QUEUE-04 / BLIND-02 / EVAP-02 / MERGE-02 / LAND-01 / GOMAP-INFLIGHT），
但"修 5 件"的清单是**按现象列的**，不是按链路列的。按现象修会漏两类东西：
① 同一病灶的不同面（例：QUEUE-04 既是热册被吃，也是任意文件被整覆盖，也是 §6.4 重校验空转）；
② 修完无法证明修好了（无判据=没修）。
所以本包先把**从立项到交付的整条链路**切成环节，每环节配"可重放判据"，再进施工。

## 1. 环节总表（分母=12 个主环节，实测口径见各行）

| # | 环节 | 一句话职责 | 子环节数 | 挖矿文档 | 状态 |
|---|------|-----------|---------|---------|------|
| E01 | 冷启动与环境前置 | RULE-ENV/GUARDIAN/WORKTREE/CAPABILITY-LOOKUP 四闸先过 | 4 | 本文件 §2 | 封矿 |
| E02 | 真源采集与案卷复测 | 审计案卷引述→本包亲验（三态：HEAD/盘/袋） | 6 案号 | lanes/*/*_mining.md | 封矿 |
| E03 | 骨架挖矿与封矿判据 | 环节/子环节穷尽＋每子环节配判据 | 本文件 | — | 封矿 |
| E04 | 施工位与写域纪律 | worktree/claim/CREATE-GUARD/depgraph/克隆预查 | 4 | cross/00 §一 + 本文件 §2 | 封矿 |
| E05 | L1 提交链基底修复 | QUEUE-04 治本（最急，其余四件的防护前提） | 4 | lanes/L1_commit_base/lane_l1_commit_base.md | 封矿·施工中 |
| E06 | L2 裁定册复燃清除 | 尺S HEAD 面 3 硬归零 | 3 | lanes/L2_ruling_resurrection/lane_l2_ruling_resurrection.md | 封矿·施工中 |
| E07 | L3 三件悬空 .py 与 GOMAP | 图有物无的生成侧根因（+同族第三例） | 4 | lanes/L3_dangling_py_gomap/lane_l3_dangling_py_gomap.md | 封矿·已双证 |
| E08 | L4 注册表计数失真 | 尺Q 两册 + 尺R 自锁通道 + 检测器半盲 | 4 | lanes/L4_registry_counts/lane_l4_registry_counts.md | 封矿·worktree 已 PASS |
| E09 | L5 align 读数 HEAD 锚定 | BLIND-02 治本（双锚并报） | 5 | lanes/L5_align_head_anchor/lane_l5_align_head_anchor.md | 封矿·已双证 |
| E10 | 落地通道与门位 | 队列/直连/merge-relay 三通道选型与高危门位自裁 | 3 | cross/00_channels_and_rulers §一 | 封矿 |
| E11 | 循环检查与红蓝对抗 | 连续两轮零 + 尺册复跑 + 自否证 | 4 | cross/00 §二（尺册）＋ LEDGER §复跑 | 在跑 |
| E12 | 收官与交付 | 终报/三清单/清临时/自删自动化 | 5 | audit_fix_ledger.md | 在跑 |

**每 lane 的子环节穷尽度**：lane 文档内 §子环节N 即该 lane 的子孙模块清单（L1=4、L2=3、L3=4、L4=4、L5=5，
合计 20 个子环节），每个子环节一律带"现状三态实测 / 代码位 file:line / 可重放判据"三件，缺一不施工（§3）。

**分母自证**：E01–E12 由"Owner 令的五个动作面（① ② ③ ④ ⑤）+ 立项必做的四道前置（环境/真源/骨架/施工位）+ 收尾必做的三面（落地通道/验证/交付）"穷尽枚举；
反证=若漏一个动作面，则 `grep -c "audit_fix" docs/_working/audit_fix/lanes/ -r` 无法覆盖 Owner 令的五件；本包已按五件逐一建 lane，无第 6 件（Owner 令文实测 5 件，逐字对齐见 lanes 目录）。

## 2. E01 冷启动实测读数（2026-09-24 14:3x，本包亲验）

1. **RULE-ENV**：`python --version` = 3.12.8（PATH 前置 `%LOCALAPPDATA%\Programs\Python\Python312`）。
2. **RULE-GUARDIAN**：`lock_files.py cleanup` 清 14 个死锁；`process_reaper --status` → last_run=14:27:23、
   killed=0、reported=24、`drift.worktree_changes=915`、commit_pct=65.48、degraded=False ⇒ 计划任务存活=允许写。
3. **RULE-WORKTREE**：`session_worktree_start('st-audit-fix-20260924', allow_workspace_drift=True)` →
   `.aidrafts/st-audit-fix-20260924`，branch `session/st-audit-fix-20260924`，心跳 PID 27136，ok=True。
   `allow_workspace_drift=True` 的原因=主区 915 脏文件全属他包在途（非本包残留），实测清单见 cross/01。
4. **RULE-CAPABILITY-LOOKUP**：4 次 `CapabilityLookup.find` 留审计（.runtime/lookup_audit/st-audit-fix-20260924.jsonl）
   ——结论=「入队基底/快进冲突」「git show 批量取 blob」两题**无现成能力**（故 E05 新建、E09 复用现成 `GitCommandBatcher`）。

## 3. 封矿判据（每本子环节三件齐才算封，缺一不施工）

1. **现状三态实测**＝同一事实在 HEAD / 工作树 / 队列袋三处的读数（本包所有结论只认这三态，不认案卷引述）；
2. **代码位指针**＝根因所在 file:line，且该指针由本包重新算过分母（审计班 R56 已示范"盘读点 6 处"实为 5→本包复算为 8 处读字节/6 处路径构造，见 L5）；
3. **可重放判据**＝一条命令能红能绿（阳性=构造违规必报，阴性=合规必不报），且判据写进 lanes 文档，落地后由 E11 复跑。

## 4. 与审计班案号的对应（不重复立案，净零）

| 本包 lane | 审计案号 | 关系 |
|---|---|---|
| L1 | F-AUDIT-QUEUE-04 / F-EVAP-ROOTCAUSE-0752 / F-AUDIT-MERGE-01 | 对症修闸，不另立案 |
| L2 | F-AUDIT-RULING-02 / 尺S / 热文件复燃 dated 实例 | 落 HEAD 面 + 记加害批 |
| L3 | F-AUDIT-GOMAP-INFLIGHT / 尺O | 判据收窄（治生成侧），非等窗自愈 |
| L4 | 尺Q / 尺R / F-AUDIT-MERGE-02 枝2 | 改 --check 判据 + 通道选型 |
| L5 | F-AUDIT-BLIND-02 | 首次派到真属主（0009 袋实测不覆盖失明面） |
