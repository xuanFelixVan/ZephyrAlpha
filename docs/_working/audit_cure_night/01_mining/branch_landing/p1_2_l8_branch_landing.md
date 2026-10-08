---
created: 2026-10-08
chief: st-acure-m1
ttl: task_bound
completes_when: l8 分支 6 文件 +242/-1 内容等价落地 dev 且交付报告 C136/C394 披露注记更新后归档
---

# P1②③ 合并施工卡 · l8 分支内容落地 + 在分支披露补记 → B 分支道

## ① 卡面处方（审计原文锚点）

总报告 §四 P1②③ + lane_e §5 + lane_h E14：l8 分支（tip=cf5b6ddcf7）内容面=恰好 6 文件 +242/-1（L8_retire_ai/00_workbook.md +112、b_class_map.md +39、HANDOFF_wave2_closeout.md +50、strategy_registry.yaml C84 lifecycle_status_values 九态块 +15/-1、migration_registry.yaml C394 windows_service_file_retire 行 +11、capability 册 C314 token +15），零内容风险；三次 DEFERRED 未并致 13 张 L8 卡中 7 张 DONE 在 HEAD 无落地面（C136/C394 未按 C84/C314 标准披露"在分支"，P1③）。orchestration §二处方：**内容等价落地（队列袋落 dev），披露替代 merge；branch 后续归档**。

## ② HEAD 现状实证（挖矿时点新鲜复跑，HEAD=f82008eb25）

- `git branch | grep l8` → session/st-mastertc-l8 在；`git merge-base --is-ancestor cf5b6ddcf7 HEAD` → **NOT-MERGED**（审计结论不变）。
- `git diff --stat cd6ad4f7d0..session/st-mastertc-l8 | tail -3` → **6 files changed, 242 insertions(+), 1 deletion(-)**（差异面与审计零漂移）。
- 关键注册表面 HEAD 现态：strategy_registry.yaml 无九态块（HEAD 仅 src registry_state_vocab.py:72 字段名引用+内置回退表兜底 shelved——lane_e §5"双真源窗口期"仍开放）；migration_registry 无 windows_service_file_retire 行。
- 落地通道启示（同构先例）：d553b160eb（今夜 G6 P12A 复活袋）已演示"死袋 blob sha 自校验物化重投"配方——B 道可直接从分支 tree 读内容物化队列袋，等价披露。

## ③ 上游依赖

- 队列正门+干净暂存区（serializer）；CREATE-GUARD：capability 册 C314 token 已在分支版块内（落地时随块并入，token 面自洽）；两注册表文件（strategy_registry/migration_registry）今夜 git status 无他会话 staged——claim 后可改。
- 注册表写面纪律：safe_write_text CAS+写后进程外复核（热册）。

## ④ 下游消费者

- **P1③**：落地后交付报告 C136/C394 卡面"在分支"注记失效→改"已落地 <hash>"（或披露替代 merge 的等价声明）；lane_g 对账表 C84 注记"①已落 HEAD+②块随本卡落地"。
- 7 张 L8 过渡卡（C84/C314/C136/C394/C96/C301/C412/C462 中 DONE 面）状态轴收敛；132 表/桌面注记同步。
- C84 机读九态块落地后，tests/meta/shared/lifecycle/test_registry_state_vocab.py 的整文件 pytest.skip 可评估摘帽（st-chiefzc-rescue 捞回袋标注"模块 ORPHAN 缓袋"——落地即有守护对象；摘帽须测试面回归）。

## ⑤ 冲突面

- branch 归档前禁删分支（orchestration：branch 后续归档——落地验收后另批）。
- 注册表双文件若与他会话注册表袋撞车走队列串行；l8 分支本体只读（禁 checkout 到主区——用 git show session/st-mastertc-l8:<path> 读内容物化）。

## ⑥ 残余与移交

- merge 本体（真 merge commit）不做——orchestration 明示"内容等价落地，披露替代 merge"；分支归档登记移交 W5 收尾批。
- C96/C301/C462 的 .runtime/tmp 侧凭据（NB2 删除回执/248 件清单）本就非持久，落地卡面注记"凭据非 HEAD 性"如实带过。

## 自审闸三态

**GREEN（挖干）**——6 文件内容现成（分支 tree 可读）、注册表面无在途冲突、先例配方在（d553b160eb），B 道即行。
