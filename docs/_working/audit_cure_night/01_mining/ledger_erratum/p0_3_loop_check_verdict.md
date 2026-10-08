---
created: 2026-10-08
chief: st-acure-m1
ttl: task_bound
completes_when: conftest.py 正门入库且交付报告 §六/§八 两处表述更正落 HEAD 后归档
---

# P0-3 施工卡 · 循环检查终判定失真 → E 勘误道

## ① 卡面处方（审计原文锚点）

总报告 §三 P0-3 + lane_b P0-B1（E11/E12/E13）：终判定"own-diff 连续两轮零失败成立"一半依赖未入库的 tests/gov/rollback/conftest.py（HEAD 检出即 fixture 收集错误：test_rollback_verifier_unit.py:188 签名 `(self, live_gates_ddl, live_tasks_projection_ddl)` 两夹具唯一定义在该 conftest），另一半依赖不存在的 rule_red_blue 预算放宽（自述 300→540+420→620，HEAD/工作区双 clean 无 540/620）。处方=①conftest 走正门入库；②rule_red_blue"已落"表述查灭失环节或更正交付报告 §六/§八.4；③§八.6 加 scope 限定声明（lane_b P1-1/P2-3）。

## ② HEAD 现状实证（挖矿时点新鲜复跑，HEAD=f82008eb25）

- `git status --porcelain -- tests/gov/rollback/conftest.py` → **`??` 未跟踪**；`git ls-tree HEAD --` 该路径 → 0 条——仍未入库。
- `git show HEAD:tests/gov/rule/test_rule_red_blue.py | grep -nE "timeout=300|timeout\(420\)|timeout\(540\)"` → **L210 timeout=300、L337 timeout(420)，无 540/620**——表述失实仍在。
- 交付报告（HEAD L 埠）§六/§八.4/§八.6 三处自述未被他会话更正（末触仍=de50314561 v2）。
- 工作区 conftest 字节与自述 DDL 相符（lane_b：CREATE TABLE gates migration 34 逐字+tasks 投影+insert_live_gate_row 3 夹具）——入库即修复收集错误。

## ③ 上游依赖

conftest 入库无上游（文件在工作区现成，正门 claim+commit 即可）；表述更正无上游。注意：conftest 新建 .py 若入队需 CREATE-GUARD token（tests/ 豁免——按 gate_registry files_trigger 注记 tests/ 豁免面，走 --allow 路径如实申报）。

## ④ 下游消费者

- W3 循环检查基线（conftest 入库后 rollback 测试面才可收集，"两轮零失败"才有可复现判据）。
- P0-10 同理（全量基线读数清洁）。

## ⑤ 冲突面

conftest.py 现为 `??` 未跟踪——**属前役会话遗产面**，E 道 claim 前按 RULE-WORKSPACE-WIP 先跑 classify_workspace_wip.py 判读，确认无主后收编（lane_b 已证其内容与自述一致，收编=转正非代修）。

## ⑥ 残余与移交

- rule_red_blue 预算放宽"灭失环节"追查（队列袋/stash/未写盘三处，lane_b P1-1）：若查无实据则以"表述更正"收口——交付报告 §八.6 加"本判定 scope=own-diff 子集，总判仍=§七 ISSUES"一行（lane_b P2-3 原文处方）。
- stash 面：编辑"消失"先查 `.runtime/workspace_alerts/stash_notice.json`（宪法 §2.8）。

## 自审闸三态

**GREEN（挖干）**——两处方均机械可执行：入库（字节现成）+两处表述更正（一行 scope 声明）。
