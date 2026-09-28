---
ttl: task_bound
---

# 叶簿 W-21 · 门禁 priority：真源是 GateSpec，补「聚合台与吸收台不得同号」断言尺

> 族 2（提交链解锁与治本）· 骨架行锚=`00_master_skeleton.md` L65（态 ⬜，出处「灾备令结案项；全流通§6-T8（口径经 X-13 修正）」，案卷 A）
> 编译：2026-09-28，会话 st-zcloseout-20260928（Agent-H），lane=`.worktrees/st-zcloseout-leaves`，编译时 HEAD=`325b69a193`。
> 状态标记：⬜ 未开工（处方=断言尺，检索无落地证据）；历史撞号回执 6 封已随 BLUEPRINT-FORMAT 让位闭合。
> 素材真源：`dossier_A_commit_chain.md` §1 条 5a-5f、§4b；`wave1b/chain_detox_report.md` verified 段。

## 1. 六向台账（对象=GateSpec priority 的唯一性）

| 向 | 内容 | 锚 |
|---|---|---|
| 上游供数 | priority 唯一真源=代码 `GateSpec(...)` 实参；两本名册（gate_registry 181 条 / in_process 103 条）**均无 priority 字段**（0 命中） | dossier_A §1-5b；`gate_auto_registrar.py:54-55`（本会话 HEAD 直读同文：「priority 从 GateSpec 读取…YAML 的 priority 字段仅 informational」） |
| 下游消费 | 注册台按 priority 排序装链；撞号时抛 `GateRegistrationError: priority=… 冲突`（历史死信 6 封即此因） | dossier_A §4b 末段（dead_reason 原文引） |
| 名册声明 | gate_registry 条目键集含 gate_id/name/entry/files_trigger/own_scope/always_run 等，无 priority | dossier_A §1-4a/§4 附读 |
| 读声明的代码 | 装载器读 GateSpec 不读名册；名册 priority 列仅展示面 | `gate_auto_registrar.py:54-55` |
| 覆盖测试 | 未检索到「聚合台与吸收台不得同号」断言尺（本会话 `git grep -ln "同号\|priority_conflict\|unique_priority" -- src scripts tests` 命中均为无关文件；检索面有限，落地前须按 §5 复跑） | 本会话直读 |
| 执法门禁 | 撞号只在**装载期**以注册失败变现（6 封死信为账）；**无登记期/静态期尺**提前拦 | dossier_A §1-5c/5f |

## 2. 现状实测（历史基线 → 本会话 HEAD=`325b69a193` 直读）

| # | 断言 | 基线读数（锚） | 本会话复读 |
|---|---|---|---|
| M1 | 代码层 priority 撞号 6 簇 | 70=[DANGLING-REFERENCE,REFERENCE-INTEGRITY]、79=[BLUEPRINT-AMODULE-CONSISTENCY,BLUEPRINT-HEADER]、80=[GATE-VOCAB,VOCAB-HARDCODE]、82=[PERM-TRIGGER,PERMANENT-SYSTEM-TRIGGER]、92=[COMPLEXITY-GUARD,NO-HIGH-COMPLEXITY]、113=[DEPGRAPH-ENFORCEMENT,DEPGRAPH-PRE-REGISTRATION]；每簇两台**同处一个文件**（源台+聚合台 `_union_check` 模式） | dossier_A §1-5c/§4b 表（枚举自 122 个 gate .py 的 GateSpec） |
| M2 | 70/80/82/92/113 五簇仍在 HEAD | 同上 | ✅ 本会话逐文件 `git show HEAD:<gate>.py \| grep priority=` 复读同值（dangling_reference_gate.py:218/223/257、vocab_hardcode_gate.py:212/244、perm_trigger_gate.py:382/414、high_complexity_gate.py:197/231、depgraph_pre_registration_gate.py:318/372） |
| M3 | 77/130 历史撞点已让位闭合 | BLUEPRINT-FORMAT 现 130（原 77 让位 DOC-HEADER-SUITE），头注原文「原 77 让位给 DOC-HEADER-SUITE 聚合门（后到者让位先例）」 | dossier_A §1-5a；本会话复读 `blueprint_format_gate.py:184` 仍 =130 |
| M4 | 实载层撞号=0 簇 | 进程内装载 99/103，跳过 4 台 disabled（CAPABILITY-OVERLAP/GATE-VOCAB/PERMANENT-SYSTEM-TRIGGER/ALGO-FLOW-LINK）；6 簇中 80/82 两簇因成员 disabled 未同台并存 | dossier_A §1-5d |
| M5 | 撞号历史回执=6 封死信 | 4 封 priority=77（DOC-HEADER-SUITE×BLUEPRINT-FORMAT）+ 2 封 priority=110（CAPABILITY-LOOKUP-REQUIRED×BLUEPRINT-FORMAT）；并列历史先例「DATA-TASK 78→41」等 5 条 | dossier_A §1-5f/§4b（队列回执类证据，不作落地判据，仅作病史） |
| M6 | 文档串与代码不同值一处 | `registry_code_anchor_gate.py` L177 文档串写 priority=106，L251 实代码=129 | dossier_A §6 第 6 条（名册/人工读注释会取到不存在的 106） |
| M7 | 处方（断言尺）未落地 | — | 本会话检索无命中（§1 执法向），判 ⬜ 不变 |

## 3. 缺口与根因（全部转述自锚面，无新裁）

- 根因：聚合台（`_union_check` 薄工厂）与被聚合源台**各自声明 GateSpec**，同文件内顺手写同号（M1 六簇全为同文件对）——无任何尺在登记/静态期拦「同号不同台」。
- wave1b 1.3 包已逐台复读 6 簇现值并如实登记「DOC-HEADER-SUITE↔BLUEPRINT-FORMAT 他道已修、本包未碰」（`wave1b/chain_detox_report.md` verified 段），断言尺不在其五包落盘件内（§一 清单无该尺）。
- 残余面：M4 的 0 撞号依赖 disabled 恰好遮住 80/82 两簇——任一台翻 `enabled:true`（Owner 门位，骨架册 W-114）即同台并存，装载立死。

## 4. 施工项（按骨架处方，每项带锚）

1. 补「聚合台与吸收台不得同号」断言尺：对 122 个 gate .py 枚举 `(gate_id,priority)`（复用 dossier_A probe_C 口径，`.runtime/tmp/total_command_closeout/gate_priority_head.json` 为其落盘样例），断言同 priority 集合的台数=1；现 HEAD 必红 5 簇（M2）＝尺的自证反例。出处=dossier_A §1-5c 枚举法。
2. 处置 REGISTRY-CODE-ANCHOR 文档串 106≠代码 129（M6，改注释或改值=他册断言，留 Owner）。
3. 翻 disabled 前置依赖本项：W-114 四台归因（骨架册 L172）与本项串行。

## 5. 复验命令（可重跑）

```bash
cd /d/ZephyrAlpha/.worktrees/st-zcloseout-leaves
# 中心命题复验：五簇同号仍在 HEAD（每行应输出同号两台）
for f in dangling_reference_gate vocab_hardcode_gate perm_trigger_gate high_complexity_gate depgraph_pre_registration_gate; do
  git show HEAD:src/zephyr/gov_enforcement/commit_gates/$f.py | grep -oE 'gate_id="[A-Z-]+", check=_[a-z_]+, priority=[0-9]+' | sort -t= -k3 -n;
done
```

## 6. 自审闸三态

- **挖干**：已干——两册无名册字段、代码真源 6 簇、实载 0 撞、回执 6 封、断言尺缺位，五面各有锚（M1-M7），无第三面待挖。
- **施工中**：无——断言尺无人开工（M7 检索零命中）；wave1b 1.3 只做了复读枚举（`wave1b/chain_detox_report.md` verified 段）。
- **未开工**：断言尺本体（§4-1）、文档串 106/129 对齐（§4-2）——均 ⬜，证据=M7+§4 条目无在 HEAD 载体。
