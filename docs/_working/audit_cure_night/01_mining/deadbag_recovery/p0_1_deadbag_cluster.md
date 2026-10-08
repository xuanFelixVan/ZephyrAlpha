---
created: 2026-10-08
chief: st-acure-m1
ttl: task_bound
completes_when: 8 卡死袋簇全部清偿（落地或三面台账同步改判）且 R 道 workbook 回填后归档
---

# P0-1 施工卡 · 死袋假完成簇（8 卡）→ R 恢复道

## ① 卡面处方（审计原文锚点）

总报告 §三 P0-1：C232/C234/C235/C75/C107/C233/C122/C452 在交付报告+环节总表标 DONE/G，承载字节 HEAD 全树零命中（含 --all 全史），袋位=死袋。处方=**二择一**：死袋清偿落地（MAP-MOUNTS 补挂面/CREATE-GUARD 补 token 等，处方已在死信袋内）或三面台账同步改判"施工完成/落地失败（死袋 qid）"；C452 另需 3 条悬空 token 撤号或落册。逐袋处方（lane_a E1/lane_c 证据块 8）：

| 卡 | 载体文件 | 死袋 | 死因/处方 |
|---|---|---|---|
| C232/C234/C235（+C252/C253） | src/zephyr/signal_ashare/{limit_up/event_axis,swing_sequence,resonance_pair}.py + 三单测 | recover-0005（四投四死：l6-0001→l6-0004→recover-0002→recover-0005） | CREATE-GUARD MAP-MOUNTS（新建 src .py 未申报挂图面）→补 map_mounts 或 no_mount_reason（引 rowvec 先例）；首投 GATE-ANY-ABUSE 已修 Any→object |
| C75 | src/zephyr/factor/analysis/tech_factor_pipeline.py + 测试 | recover-0003（原 l6-0002） | CREATE-GUARD 无 creation_token→token 先行登记 |
| C107 | scripts/start_paper_session.py 写者腿 _PaperFillJsonlWriter + 测试 | mini-0003 | GATE-PRECOMMIT-RUN/gate-naming→修命名重投 |
| C233 | tests/backtest/test_lookahead_injection_red_ruler.py | mini-0002 | ALGO-FLOW-LINK（恢复锚指向不存在 yaml）→**放弃恢复锚**（HEAD 现态=两引擎无锚一致性成立，lane_a §4）直接落测试件 |
| C122 | entity_graph_uscc_bridge.py（10 件 staged 面） | final-0001 | MAP-MOUNTS 同簇 |
| C452 | docs/_working/quant_methodology/07|08|12 三册 | 随 q-0004 死袋（L7 簿自认） | 三册落地（token 已在册 L45511/45516/45521）或撤号呈 Owner |

## ② HEAD 现状实证（挖矿时点新鲜复跑，HEAD=f82008eb25）

- `git ls-tree -r HEAD --name-only | grep -iE "event_axis|swing_sequence|resonance_pair|tech_factor"` → **零输出**（审计结论不变）。
- `git show HEAD:scripts/start_paper_session.py | grep -cE "_PaperFillJsonlWriter|fills_dir|process_fill"` → **0**。
- `git log --all --diff-filter=A -- "*test_lookahead_injection_red_ruler*"` / `"*entity_graph_uscc_bridge*"` → 均空。
- `git ls-tree --name-only HEAD docs/_working/quant_methodology/` → 仅 01-06+README+三附录，无 07/08/12。
- 六袋现态：`.runtime/commit_queue/dead/` 实测 recover-0002/0003/0005、mini-0002/0003、final-0001 **全部仍在 dead/**，pending/processing 无 st-mastertc 系——R 道今晚尚未取走。
- 台账三面现态（未被他会话更新）：交付报告 L72/73/74/82/86/93/61 仍标 DONE；00_环节总表 L97/98/101 仍标 G。

## ③ 上游依赖

无外部上游（本卡是全役第一上游）。工具面依赖：MAP-MOUNTS 补挂面通道=trae 判据内 map_mounts 或 no_mount_reason 字段；CREATE-GUARD token 批=scripts/governance/d3_metadata/batch_creation_tokens.py（本役 M 道已用同款）；队列正门=git_commit.py --enqueue。

## ④ 下游消费者

- **P0-7**（翻译册 4 幽灵条目随三模块+tech_factor 落地自然消除；token 册 3 悬空随 C452 清偿）。
- **P0-10**（fill 验收钉随 C107 写者腿落地转绿）。
- **P0-6/P0-9**（G 道桌面注记按 R 道终态写"已落地"或"死袋待取回"）。
- 120 卡挂接表/132 表状态轴、晨会读数。

## ⑤ 冲突面

- 六袋+final-0001 为 st-mastertc 系遗产，取走清偿前须登记 process_reaper keep 面（长批任务）。
- capability 册/翻译册今夜有他会话 stomper 在飞（git status=MM）——R 道写册必 safe_write_text CAS+写后进程外复核。
- 工作区存量 `??`/`A` 态（event_axis.py 等，lane_a E2）系他会话/前役在途面，R 道 claim 前先 `lock_files.py acquire`，外来 staged 不碰。

## ⑥ 残余与移交

- C452 撤号 vs 落册=Owner 择一（内收判据②正解=撤号），R 道择"落三册"则撤号面自动消失；择不动则登记呈报。
- C107 测试数口径矛盾（工作簿 8 vs 袋 16，lane_a P2）清偿时并案统一。
- 死信 blob 保全在案（blobs/ 24061 对象），整袋取回按袋 JSON 内 blob_ref+sha256 核对。

## 自审闸三态

**GREEN（挖干）**——处方门禁四族全有已知先例（MAP-MOUNTS rowvec/token 先例/gate-naming 修名/放弃锚），R 道可即行施工。
