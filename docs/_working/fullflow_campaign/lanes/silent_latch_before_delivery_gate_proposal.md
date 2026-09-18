---
ttl: task_bound
completes_when: 全流通战役收官且最终交付报告落盘
---

# 门禁候选提案 · 闩前置（latch-before-delivery）

> 提案车道：`st-ff-silent-20260918`。触发条件满足"出现 ≥3 次且判据可机械表达"：
> 本车道实测真病例 3 处（F1/F2/F3）+ 触发实例 1 处（R-023，z-failopen 已收口）
> + **正解样板 1 处**（`worktree_drift_watchdog.py` 注释明载"不更新 alerted…防吞"）
> → 同型构造 ≥4，且已有唯一正确写法可作对照。**只提一个 gate，不批量提。**

## 0. 宪法 §4.1 合规声明（规范总量净零增长）

**首选方案不是新 gate，而是扩档**：
z-failopen 已建 `scripts/governance/d7_code/generate_fail_open_register.py`
→ 派生册 `docs/01_policies_and_standards/_registry/catalogs/fail_open_register.yaml`，
并已有 `--check` 模式（派生册 `content_sha256` 与现扫不符即退出码 1）。

**提案 A（推荐，零新增 gate）**：在该生成器里新增一档
`latch_before_delivery: [<file:line>, …]`，复用既有 `--check` 与既有提交链挂载点。
- 净增：**0 个 gate、0 个注册表、0 条必读规则**；只多一档分类字段。
- 语义衔接：本档与既有 `hardcoded_default_permit` 同族（都是"看起来在防，实际不防"）。

**提案 B（若 Max 坚持独立 gate）**：则**必须声明替代对象**——
建议合并退役 `gate_registry.yaml` 中与"吞异常"语义重叠的那条（z-failopen 分档落册后，
若仍存在"仅 grep `except Exception` 次行 pass"的旧启发式 gate，应以本 AST 判据取代之，
因为 §1 的实测已证明次行口径漏计 31%~45%：P4 207→238、`except…pass` 144→261）。
说不出替代对象就不该立 gate —— 这也是本提案默认走 A 的原因。

## 1. 判据（可机械表达）

```
对每个 FunctionDef F：
  LATCH_W = { 行号, 目标 }  其中目标名命中
      alerted|latch|seen|dedup|already|warned|notified|last_*|_ts|_stamp|acknowledged|suppressed|reported
    形态 ∈ { Assign/AnnAssign/AugAssign 到该目标, 该目标的 .add()/.update()/.setdefault()/.append() }
  DELIV   = 行号集合，调用名命中 notify|send_*|dispatch|publish|deliver|alert|escalat|emit|post_*|write_alert
            且其返回值**未被消费**（不在 Assign.value / If.test / Return / BoolOp / UnaryOp 内）
  命中条件：∃ w ∈ LATCH_W, ∃ d ∈ DELIV，w.line < d.line，且
            （d 所在 try 的 handler 不重置 w 的目标）或（d 未被 try 包裹）
  白名单逃生：同一函数体内出现显式"防吞"注释锚（沿用 worktree_drift_watchdog 的措辞 `防吞`）
              或该闩目标在 w..d 区间之后被读回并据以回退（AST 级数据流，可先不做）
```

**own-diff 作用域**（宪法 §3.1）：只算本次 staged diff 新增/修改的函数体，存量 58 组 FP 与
他人 T3 面不连坐。触发面：`src/**/*.py` + `scripts/**/*.py`。

## 2. 误报控制（实测数据支撑）

| 项 | 值 |
|---|---|
| 全仓 AST 原始命中 | 78 |
| 按 (file,func,latch) 去重 | 61 |
| 人工判后真病例 | **3**（precision ≈ 5%，首版判据） |
| 主要 FP 族 | ①`alerted = <阈值比较>` 计算型判定标志；②日历/事件事实位；③名字命中 `_ts/last_` 的业务量变量 |

→ **直接以 AST 首版判据立 gate 会产生 95% 误报，不可接受。** 必须先在判据里剔 FP 族：
1. 排除"闩目标在同函数内被读回并参与阈值比较"的形态（`alerted = deviation > tol` 这种 **rvalue 含 Compare/BinOp** 的一律不算闩）；
2. 排除 rvalue 是 `time.time()/now_utc()` 之外的**纯业务量**（如 `max_ts`/`oldest_ts` 来自查询结果）；
3. 要求"投递返回值被丢弃"这一条为**必要条件**（已是，保留）。

按①②收敛后的预期 FP 率需 Max 用历史 20 个 commit 回测（本车道无预算做回测，如实标注）。

## 3. 迁移成本

- 提案 A：生成器加一档 + 派生册重跑 → 一次 `--force`，零代码迁移。
- 存量 3 处真病例已在本车道清零 → gate 上线即绿，不需要给历史欠账开豁免窗口。
- 非钱路径若被命中：改法是"送达成功才置闩"的两行样板（见 F1/F2/F3），不需要新抽象。

## 4. 是否属"门禁只许加严"（裁定#321）

是。本判据只**新增阻断面**，不放行任何现存行为；且其修复方向唯一（fail-toward-retry），
不存在"为过闸而放宽告警"的逃生路。**不触 flag 翻转、不触注册表净删**（提案 A）。

## 5. 与验收规范的接合

- §1 第⑥向"失败会响"新增一条必查子项：*投递返回值是否被消费；闩是否在送达之后*。
- §6 红蓝攻击面"假处置/静默放行"补一条打法：**把告警通道打成真落盘失败（如把 failures 目录父段做成普通文件），
  断言下一轮仍会重试**。本车道 12 条测试钉即该打法的固化。
