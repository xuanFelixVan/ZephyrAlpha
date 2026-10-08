---
created: 2026-10-08
chief: st-acure-m1
ttl: task_bound
completes_when: close_lane.md L35 勘误行落 HEAD 并与晨会移交同步后归档
---

# P0-2 施工卡 · close_lane 错哈希假落地行 → E 勘误道

## ① 卡面处方（审计原文锚点）

总报告 §三 P0-2 + lane_h H-P0-1：close_lane.md §三在途袋表 L35 记 `| q-...-l6-0004 | 8 | 落地 45c1f0b224（signal_ashare 三件+测试+双册） |`——实证 45c1f0b224 实为 5 文件 docs 袋（34_trigger_surface/p2_card_ledger/L6 workbook/双注册表），三件 src/测试在任何分支全史从未 A 落地。处方=勘误该行（改"未落地，袋在 dead，处方=捞回重投或销账"），与晨会移交同步（lane_h P1-1）。

## ② HEAD 现状实证（挖矿时点新鲜复跑，HEAD=f82008eb25）

- `git show HEAD:docs/_working/master_tc_night/99_delivery/close_lane.md | sed -n '35p'` → **原失实行原位**：`| q-...-l6-0004 | 8 | 落地 45c1f0b224（signal_ashare 三件+测试+双册） |`。
- `git show --name-only 45c1f0b224` → 5 文件 docs 袋，无 src/无测试（与审计一致）。
- close_lane 末触=0d1d6d29a6（10-07 10:33），今夜未被他会话更新——行号有效。
- 袋现态：`.runtime/commit_queue/dead/` 无 l6-0004 残留核查点=l6-0001/0002/0004 系列均在 dead/（P0-1 卡已核 dead 目录在档）。

## ③ 上游依赖

无。P0-1 的清偿结果决定勘误行的最终形态（若 l6-0004 同内容物经 R 道复活落地，勘误行写"已由 R 道 <hash> 落地，原行错哈希"；若未落地，写"未落地，袋在 dead，处方=捞回重投或销账"）。

## ④ 下游消费者

晨会移交凭据（close_lane 是正式台账）；P0-6 桌面注记（G 道引用同叙事）；战役树归档批。

## ⑤ 冲突面

close_lane.md 今夜无他会话在途（已核 git status 无该文件）——E 道 claim 后可直改；写后 `git log -1 --name-only` 核归属。

## ⑥ 残余与移交

勘误不抹史：行内保留"原行错哈希勘误（#490 佐证面/审计 P0-2）"痕迹注记，禁静默改写（文档矛盾=事故红线的对称面：勘误也要留痕）。

## 自审闸三态

**GREEN（挖干）**——单行勘误+证据链闭合，E 道即行。
