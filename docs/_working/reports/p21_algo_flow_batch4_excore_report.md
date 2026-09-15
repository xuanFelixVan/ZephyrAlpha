---
ttl: task_bound
session: st-btfix-p15-20260915
date: 2026-09-15
---

# P2-1 ALGO_FLOW 逐域出仓批4 报告（ex_core 域 59 文件）

> 会话 st-btfix-p15-20260915 | 2026-09-15 | 承接批3 regime，commit d2a23ab9（121 文件）+ 报告本件

## 成果

| 项 | 数 | 说明 |
|---|---|---|
| 源码出仓 | 59 | src/zephyr/ex_core 全域，内联块换 external 锚，round-trip 逐项一致，零回滚 |
| 外部 yaml | 59 | docs/03_modules/_domain_execution_core/algo_flow/（ex_core 映射 execution_core） |
| creation_token | 59 | batch_creation_tokens.py 批量通道（锚点 btfix_p1p2） |
| TDM 补注 | 9 节点 | TDM-E-L4-01/03/05/07/09/10/11/12 + TDM-X-S2-04（local_order_queue 挂双节点） |
| 域测试 | 1205 passed + 1 xfailed | tests/ex_core 全绿 |

## 过程发现（后续班注意）

1. **CloneGuard 存量暴露面扩大**：本域 4 对同构（repo 工厂姊妹/mock 工厂姊妹/__str__/按市场镜像规则类）全部 HEAD 既有，触碰后首次暴露；echo-guard.yml acknowledged ×4（cg-excore-*-20260915）。后续每域出仓预计都要过一轮 CloneGuard 暴露→登记循环，建议预查（clone_guard check_before_write）先行。
2. **daemon auto-stage 吸收风险实证**：暂存区外来文件被自动暂存（62 件），git add -u 后 reset 单文件循环才剥离干净——commit 后 git log --name-only 对账必须做（本批 121=121 零吸收）。
3. **tests/ex_core 并发 flaky 1 例**：test_cancel_order_writes_instruction 首轮失败、隔离跑通过、复跑全绿；与批1/2 观测的 flaky 家族同源（文件锁/并发），非本批引入。
4. **registry 外来变更新形态**：f06dsr-shift2 的路径迁移型条目（-旧路径+新路径）混入——分离时需同时还原路径行并删新增块，纯加法剔除法不够用。

## 普查进度

全仓 3302 内联模块，已出仓 114+59=173（5.2%）。下一批建议：ml_train(43)。
