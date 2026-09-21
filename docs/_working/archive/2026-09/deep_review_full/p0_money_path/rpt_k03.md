---
ttl: task_bound
title: 深度审查作业簿——交易总停止闸StopGate
owner: st-deeprev-20260918
created: 2026-09-18
reviewed: 2026-09-18
---

# 深度审查报告：交易总停止闸StopGate（K03）

- 状态: **已审**
- 级别: P0｜类型: 闸门（**实审后认定：非资金闸，见 P3-1 分级纠正**）
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/trading/stop_gate.py:40`
- 生产调用方（实测 grep）: 持有/初始化/ack 三类接线存在——`auto_runtime_core.py:137,318,556,623`（构造+属性暴露）、`lifecycle_manager.py:114`（initialize）、`lifecycle_manager.py:228`（acknowledge_shutdown）；**但决策入口 can_stop()/check() 在 src+scripts 生产代码零调用**（`auto_runtime_core.py:626` 的包装方法本身无人调）
- 测试文件: tests/trading/test_stop_gate.py（23 用例）
- 运行结果: `python -m pytest tests/trading/test_stop_gate.py -q` → 23 passed（Python 3.12.8）

## 1 对象快照

- **范围**：stop_gate.py 全文件 + 生产接线面（auto_runtime_core/lifecycle_manager）。
- **对象定性（关键）**：代码自述为"AI 不能空手退出"的会话质量闸门（stop_gate.py:19-26，借鉴 Claude Code 45 天自主实验），检查维度=AiAuditLogger 新条目/NightShift 未决/DreamCycle 未归档/Git 未提交/Session 预算——**无任何持仓/订单/资金/熔断维度，与"交易总停止"无关**。作业簿把它归入"P0 钱路径·风控"属清单分级漂移（本报告 §4 P3-1 正式提出纠正）。
- **材料缺项声明**：运行时证据包未取；auto_runtime 主进程是否经外部调度器（仓外）调 can_stop 无法从仓内证实（已 grep src+scripts 零命中）。
- **测试覆盖概况**：23 用例全绿；预算/日期/四条件逻辑覆盖充分（信任）；但生产"零咨询"状态测试无法暴露（测的是件不是链）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| C | **孤儿闸（决策入口零调用）**：StopGate 在生产被构造、被 initialize、被 acknowledge_shutdown，但 can_stop()/check() 全仓生产路径零调用——"AI 不能空手退出"的闸从未闸过任何一次退出；auto_runtime_core.py:626 包装方法同样零调用 | stop_gate.py:123-157；auto_runtime_core.py:626-632；grep "can_stop" src/scripts 非测试仅定义点命中 | **P1** | `grep -rn "can_stop" src/ scripts/ --include=*.py \| grep -v test`（仅 auto_runtime_core.py:626,627 定义侧命中） |
| D | 对象分级纠正：本闸无资金语义，入"P0 钱路径·风控/KillSwitch/合规闸"清单属分类漂移——建议清单维护方把它移出（真正的交易停止语义在 K01 validator/K02 系统开关/next-day 停机路径） | stop_gate.py:19-26 vs 作业簿备注"交易总停止闸" | P3 | 对照模块 docstring 与清单描述 |
| A | check() 四条件参数全 True 默认=默认放行（fail-open by construction）；生产包装方法只传 3/4 条件（不传 git_clean）——若未来接通，git 未提交不阻断退出 | stop_gate.py:123-130；auto_runtime_core.py:627-631 | P3 | check() 裸调→can_stop=True |
| A | 预算功能整体休眠：session_max_actions/minutes 生产构造不传（默认 None）+record_action/can_continue/budget_status 全仓零调用——双休眠（无人喂计数、无人设上限） | auto_runtime_core.py:137（无参构造）；grep record_action/can_continue 生产=0 | P3 | grep 验证 |
| A | budget_exceeded 类型边界：session_start 经公共 setter 注入 naive ISO 字符串时，`(now_utc() - start)` aware-naive 相减 TypeError 未捕获（try 只包 fromisoformat）→can_stop 向上抛异常 | stop_gate.py:84-87,110-116 | P3 | `g.session_start="2026-09-18T00:00:00"; g._session_max_minutes=1; g.budget_exceeded()`→TypeError |
| B | 三个条件上游（has_pending_flush/has_unresolved/needs_archival）抛异常时 can_stop 直接传播（无 try）——上游病=退出闸瘫痪（方向性：闸失效=能停机，属 fail-safe 方向，危害有限） | auto_runtime_core.py:627-631 | P3 | mock 任一上游抛异常→can_stop() 异常逃逸 |
| E | 五问：静默失败=不适用（无吞异常点，acknowledge_shutdown 失败入 report.errors 留痕 lifecycle_manager.py:229-232）；假阳性过关=见 C 轴孤儿闸（最大的"该拦没拦"）；重复触发=幂等（布尔判定）；时序攻击=不适用；断了没人知道=孤儿状态本身无人巡检（同 C 轴） | stop_gate.py 全文 | （并入 C 轴 P1） | 读码 |
| C | 生命周期收尾健壮性好：4 步清理各自 try/except 隔离+错误入 report（5.144.1 修复在案）——本对象相关面无新发现 | lifecycle_manager.py:206-233 | 已查无 | 读码 |

## 3 SOTA 对照

- **Stop Gate 概念**：代码自述借鉴 Anthropic Claude Code 45 天自主实验的"被动质量闸门"（stop_gate.py:22-23，内部知识来源，非外部 URL）；业界自主 agent 框架的 stop/termination gate 同构（agent 循环停止条件校验）。**对等已有**（设计借鉴自述+同构确认），无需外部检索立卡。
- 轴 F 检索：本对象无数学/监管语境，未单独 WebSearch（检索预算让渡给 K05/K06 数学对象），如实记录。

## 4 缺陷清单（按严重级排序）

1. **[P1] 决策入口生产零调用（孤儿闸）**：现状→initialize/ack 都接了，唯独 can_stop 没人问——自主 session 的"空手退出"防线不存在。影响→自主运行质量防线缺失（非资金风险）；爆炸半径=auto_runtime 自治循环质量。建议修法→在自治主循环的退出判定点接 `core.can_stop()`（拒绝退出时打印 reasons 继续），或正式退役本闸（规范预算净零：留着一个没人问的闸=假安全感）。验证法→在退出路径临时断点/日志确认零咨询。
2. **[P3] 对象分级纠正**：移出 P0 钱路径清单（无资金语义），清单描述"交易总停止闸"改为"会话质量闸"。
3. **[P3] check() 默认参数全 True + 生产接线缺 git_clean 维度**：接通时逐条件显式传参，勿依赖默认放行。
4. **[P3] 预算功能休眠+naive 时间戳崩溃边界**：接通预算前修 aware-naive（fromisoformat 后统一 `replace(tzinfo=UTC)` 或拒收 naive）。

## 5 挂起疑问

1. auto_runtime 生产进程是否经仓外调度器/前端（dashboard app_panel?）调 `can_stop`？仓内证据为零；若有仓外调用方，P1 降级为"仅仓内零调用"。需 Owner 确认。
2. 本对象与 K02 的"系统级停止"语义在运维剧本上是否有人为混淆（把 StopGate 当交易总闸用）？建议在 capability card 澄清。

## 6 完备性自评

- 六轴全查：A/B/C/D/E/F 均有结论；数学子问 N/A（纯布尔逻辑闸）；E 轴五问逐条处理。
- 长尾清单：① 上游三条件（audit/night_shift/dream_cycle）的实现正确性未深审（属 AI 自治域非钱路径）；② lifecycle_manager 全文未审（仅审 StopGate 相关步）；③ 仓外调用方无法证伪（挂起疑问 1）。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P1 can_stop/check生产零调用+实为会话质量闸: 挂起登记(重分类+接线裁定)。建议移出P0清单。
