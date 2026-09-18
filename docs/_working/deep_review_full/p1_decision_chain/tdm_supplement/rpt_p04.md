---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——收盘复盘与明日边界（已审）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：收盘复盘与明日边界（P04）— GLM-5.3-Flash / st-deeprev-20260918

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash/st-deeprev-20260918
- 入口锚点: `src/zephyr/plan_engine/tomorrow_boundary_planner.py`
- TDM 节点: TDM-E-L0-03
- 生产调用方: boundary_revision_engine.py / batch_boundary_runner.py / closing_session_decision.py（活件）；下游 P02 消费 TomorrowBoundary
- 测试文件: tests/plan_engine/test_plan_engine.py（17 passed）

## 1 对象快照
MOD-PLAN-001 全文件（195 行）：TomorrowBoundary 数据契约 + apply_revision 盘中修正（过期/跨日拒发）+ MVP 箱体计算（close×(1±amplitude)）。排除项：boundary_revision_engine 内部（MOD-PLAN-006 域）。测试覆盖 happy path+close=0 拒发。

## 2 六轴审查日志表
| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 箱体数学平凡（close×(1±amp)）；**无箱体序校验**：amplitude=0→退化箱体（lower=upper）；amplitude<0→**箱体反转**（实测 amp=-0.05 → box_lower=10.5>box_upper=9.5）不报错——与自身"边界层坏=致命"哲学冲突；下游 P02 将按反转箱体生成 buy=10.5/必出=9.5 荒谬计划 | :180-184；实测见验证法 | **P2** | `python -c "import sys; sys.path.insert(0,'src'); from zephyr.plan_engine.tomorrow_boundary_planner import *; b=TomorrowBoundaryPlanner().compute_boundary('x',{'close':10.0,'amplitude':-0.05}); print(b)"` |
| A 深度 | apply_revision：shift≠0 缺 atr14 拒发（fail-closed 好）；但新 no_add_price 无序校验（大负 shift 可击穿 box_lower 甚至为负），修后边界不再自洽 | :127-133 | P3 | 造 shift=-3, atr14=1 看新 no_add |
| A 边界 | close 为 str 时 `close<=0` 抛 TypeError 而非 BoundaryComputeError——违反 ERROR_CONTRACT（ZA-PLAN-0001） | :175-178；实测 TypeError | P3 | `compute_boundary('x',{'close':'10.5'})` |
| A A股 | no_add=box_upper×0.98 对 3% 箱体≈+0.94% 合理；但默认 amplitude=0.03 未分板块口径（创业板/科创板 20cm 下箱体过窄，漏传时静默用 3%） | :182,191 | P3 | 传 300xxx 代码观察默认箱体 |
| B 上游 | market_state 纯鸭型无 schema：amplitude 键漏传→静默默认 0.03（轴 A 第 4 条）；close 漏传→0→拒发（好）；隐式契约（amplitude 须≥0 且为小数）未文档化 | :175-182 | P3 | 缺 amplitude 键调用看输出 |
| C 下游 | 消费方实存三处（grep 实证）+ P02；爆炸半径=单票边界（坏→该票计划失真，不炸全链） | grep "TomorrowBoundaryPlanner\|compute_boundary\|apply_revision" src/ | 已查无 | grep 命令复跑 |
| D 旁系 | BoundaryRevision 靠 runtime 鸭子类型读字段（TYPE_CHECKING-only import），字段改名=AttributeError 运行时炸——无契约测试锁定字段集 | :53-54,119-133 | P3 | 改 BoundaryRevision 字段名跑 test_boundary_revision_engine.py 与本件测试对照 |
| E 对抗 | 五问：①无吞异常（fail-closed 主导）②apply_revision 过期/跨日拒发防滞后污染（好，实测有测试）③无心跳（纯函数无此面）④纯函数幂等（computed_at 除外）⑤无时序死角（revision.trade_date≠on_date 拒发已防乱序） | :119-133 | 已查无 | 复用现有测试 17 passed |
| F 新鲜度 | 受阻：支撑/阻力箱体属传统技术分析内部裁量，本批未检索 | — | — | — |

## 3 SOTA 对照
受阻（见轴 F）。

## 4 缺陷清单
1. **P2 箱体序无校验（退化/反转静默通过）**：违反"边界层坏=致命"自设不变量，坏边界顺传 P02 生成荒谬计划。建议：__post_init__ 或 compute_boundary 尾部断言 0<box_lower<no_add≤must_exit=box_upper。验证法：上述 python 单行。
2. P3 TypeError 契约外异常（close 类型校验缺失）。
3. P3 apply_revision 修后无序校验。
4. P3 默认 amplitude 0.03 板块口径未分。
5. P3 测试缺口：负 amplitude/str close/退化箱体均未覆盖。

## 5 挂起疑问
- MVP 骨架注释称"实际算法待 BM-SEL-03/04/05/23 就绪后完善"（:171-173）——当前生产边界全部是 ±3% 机械箱体，决策层是否知情依赖此口径，需 Owner 确认 MVP 偏差可接受。

## 6 完备性自评
六轴全查。长尾：batch_boundary_runner/closing_session_decision 对坏边界的容错未深钻（属各自主件域）。
