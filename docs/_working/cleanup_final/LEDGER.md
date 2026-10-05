---
ttl: task_bound
title: "遗留修复收尾总包 — 台账 LEDGER（st-cleanup-final-20260924）"
---

# 遗留修复收尾总包 — 台账 LEDGER

- 会话：st-cleanup-final-20260924 · 开工 2026-09-24 · Owner 全批六件
- 通宵判据：六件全落地 + 连续两轮零 + 红蓝一轮 + 终报 + 清临时 + 自动化核删
- 实盘四禁常效；提交一律 git_commit.py --enqueue；热文件 safe_write_text。

## 任务面

| # | 任务 | 裁定 | 状态 | 落地证据 |
|---|------|------|------|---------|
| ① | 翻译册 6 组重复 dedupe（7712→7706） | #411 | 死信待 requeue（首投死于 CREATE-GUARD：token 批被 q-0001 蒸发事故拖住，token 重投=0005 落地后即 requeue） | q-0002 |
| ② | akshare 克隆对退役（94 vs 4 引用计数，退役 akshare_quote_provider.py） | #412 | 已入队（实物+algo_flow yaml 删、两 import 改指、注册表四处摘除） | q-0004 |
| ③ | fail_open_register 悬空 14 处清零 | — | 生成器现产（1776/310，悬空 grep=0）待直连落地（requeue 前提实测不成立，见过程记录） | 待直连 |
| ④ | 六处审查器假绿修复（a-f，红测 19 例新增） | — | a-f 全完工，四批入队（0006/0007/0008/0009）；七套件 205 passed | q-0006~0009 |
| ⑤ | 凭据明文→"[已轮换 2026-09-24]"（正本+archive，四处值+注记） | — | ✅ 已落 HEAD | cb6b4bfc0e |
| ⑥ | 裁定册 related_arch 三悬空清零 | — | 已并入 q-0009（三值实证=数据错误：议题册+depgraph 皆无真身；audit-all-0011 并非解药）；align layer2 治理双向 18/18 转绿 | q-0009 |

## 过程记录（追加式）

- 冷启动三步全绿；能力反查留审计。现存自动化 4 条全属他会话，本会话零新建→终局核删=确认零新增。
- token 先行批 q-0001 蒸发（非 pending/processing/dead/done 四态全无，HEAD 无 token）——今日蒸发事故族再一例；重投=q-0005。
- q-0002 如预期死于 CREATE-GUARD（token 未在 HEAD）；q-0005 落地后 requeue 即活。
- ③ 死因勘定：袋 0042→requeue 0056 两度死于合并器「身份判不了的条目（非 dict/首字段非标量）」——passthrough 修只覆盖纯标量族，本册大 dict 族身份仍不可判。Owner 前提「合并器 passthrough 修好后应能过」实测不成立。按 align_dirty 台账 R2 处方改道：生成器现产+直连单件（现产=1776/310，含两日代码漂移正当刷新）。
- ③ 直连首试被 BLUEPRINT-FORMAT 连坐拦（外来 staged 三件 registry_ledger WIP 头注坏，非我方文件）→ 按 W1 处方三件临时 unstage→提交→回加；二试被 GATE-WORKTREE-DRIFT-WATCHDOG 拦（本会话 ④ 批文件在 worktree 未落 HEAD 的正当漂移在告警面）→ 等 ④ 批落 HEAD 自愈后三试。
- ④ 拆四批过域门：0006=④ab（工厂图连通性 DFS+data_refs 校验+真图三断供处置）、0007=④c（R9 死检查复活：file_path 真列+ProgrammingError 必抛）、0008=④d（fs_collector 裸词 models→_SKIP_PATHS 显式前缀）、0009=④ef+⑥（REGISTRY_SPECS 纳入 DS 册+inputs 闭包+related_arch 清零；PROTECTED-PATHS 走 [ARCH-APPROVAL:ARCH-AUDIT-BLIND-08] 审批标记，授权链=Owner 全批原文，议题册登记列为后续项）。
- 红测资产：工厂图 10 例（孤立 built/partial/断连分量必拦+坏路径/坏表必拦+待定仅警+真图绿控）、R9 3 例（垃圾必 False/真锚必 True/列名错必抛）、图书馆 1 例（真包必收+vendored 必跳）、align layer2 3 例（DS 重复 id/缺 module_id 必拦+spec_path 解析）、anchor gate 3 例（junk inputs 必拦/id·name 双口径过/tombstone 豁免）。七套件合计 205 passed（含既有回归）。
- 真图真册伴随修正（检查器收紧的诚实闭环）：strategy_production_map 三断供（news_data 待定化+chainmap 补真身路径+ig_fact 落非可校警告面）；data_sources_registry 23 条补 module_id=MOD-L00-001；裁定册三悬空 related_arch 净删。
