---
created: 2026-10-08
chief: st-acure-m1
ttl: task_bound
completes_when: test_fill_jsonl_single_writer 随 C107 写者腿落地转绿（或降级申报入册）后归档
---

# P0-10 施工卡 · HEAD 结构性红测试钉（fill 验收钉）→ R 恢复道

## ① 卡面处方（审计原文锚点）

总报告 §三 P0-10：test_fill_jsonl_single_writer.py（他队件，st-cure-p05b 85896a0485 早于夜战落地）无 skip/xfail，静态尺自述"同时构造 FillHandler(fills_dir=…) 且调用 process_fill 的文件必须恰好一个=scripts/start_paper_session.py"——HEAD 写者腿为零，按其判据对 HEAD 必红。处方=**随 C107 落地转绿，或临时降级申报**，防污染下一轮全量基线读数（lane_d P0-2）。

## ② HEAD 现状实证（挖矿时点新鲜复跑，HEAD=f82008eb25）

- `git ls-tree HEAD -- tests/trade/ex_core/test_fill_jsonl_single_writer.py` → blob 24577df1ec **在 HEAD**（结构性红位不变）。
- `git show HEAD:scripts/start_paper_session.py | grep -cE "_PaperFillJsonlWriter|fills_dir|process_fill"` → **0**（写者腿仍缺席）。
- 该文件今夜未被他会话触碰（git status 干净）。

## ③ 上游依赖

**P0-1 中 C107（mini-0003）清偿**是唯一转绿路径：写者腿落地→验收钉自绿。无其他上游。

## ④ 下游消费者

W3 循环检查全量基线读数（若钉保持红且未申报，全量读数被污染，own-diff 零失败判定失真——正是 P0-3 教训的镜像）。

## ⑤ 冲突面

mini-0003 死袋属 st-mastertc 遗产，R 道取走时注意袋内 gate-naming 命名处方（死因修复）；测试文件本体为他队件（st-cure-p05b），**禁代修测试判据**——只许让它转绿（落地写者）或按流程降级申报，不许改断言放水。

## ⑥ 残余与移交

若 R 道 C107 本夜未清偿：E/G 道交付面须把"该钉结构性红"如实写入循环检查基线披露（申报面），并在 R 道 workbook 登记 WAIT 态移交晨会。

## 自审闸三态

**WAIT（依赖）**——唯一上游=C107 清偿（P0-1）；R 道清偿顺序应把 mini-0003 排前，使 P0-10 自然闭合；清偿不动则降级申报，禁裸红过夜不计。
