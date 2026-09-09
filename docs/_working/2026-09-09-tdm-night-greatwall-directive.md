---
ttl: task_bound
---

# TDM 缺失模块夜班长城任务指令（2026-09-09 23:00 → 09:00）

> **性质**：今晚施工的**执行指令**（怎么干）；配套清单见 [2026-09-09-tdm-missing-modules-construction.md](2026-09-09-tdm-missing-modules-construction.md)（干什么）。两文档同 commit 归档。
> **签发**：Owner 2026-09-09 晚口头裁定+本会话细化 ｜ **执行方**：夜班 AI session（模型分工见 §0）
> **完成定义**：清单 C/B/A 三表清账（打勾+commit hash）或到期挂起交接（§7），不以时间论完成。

## §0 模型与角色分工（Owner 方案，已确认可行）

| 角色 | 模型 | 职责 | 边界 |
|---|---|---|---|
| 夜班施工+自审 | **GLM 5.3 Flash**（夜间免费） | 全部 C/B 类落码、A 类回填、自测、红蓝对抗、双审循环（§3） | 见 §8 禁令；失败 3 轮挂起不硬过 |
| 晨审签收 | **GLM 5.3**（09:00 后） | ①CORE-ALGORITHM 清单（§5）逐个复审 ②红蓝对抗记录抽验≥3 项 ③R1/R21 清零核对+验收签收 | 只审不改——发现问题开新工单，不亲手修 |

**为什么可行**：①"反复审查直到连续两次 0 问题"=项目既有循环验收口径（trae_035 CIRCULAR_ACCEPTANCE_ROUNDS=2），不是新发明；②Flash 的质量风险由三层防线兜底——模块级双审循环（§3）→ commit 门禁硬闸（绕不过）→ 晨审 GLM5.3 终审；③核心算法夜班照建（带 CORE 标记），晨审重点盯——避免"Flash 不敢碰核心"导致夜里窝工。
**Session 约定**：夜班 session_id 前缀 `night-gw-`（如 night-gw-2300），开工第一命令先 `rule_discovery` 留审计；晨审 session 前缀 `morning-review-`。

## §1 开工序列（23:00，顺序执行）

1. 环境对齐+守卫检查（清单 §一第 1 条命令原文）
2. 读三件：本文档 → 施工清单文档（§〇~§三）→ AGENTS.md RULE 区
3. **拍板项回读**：§7 待拍板两项目前默认"流根节点=待 Owner 放行、改名拆细=不动"——开工前查 Owner 是否已批流根；未批则波次 0 跳过该步
4. **波次 0 反查定界**（清单 §三 C 类 12 项逐条三重反查，命中→降 B/A，回填清单文档表格）：反查命令模式 `CapabilityLookup().find("<关键词>")` + `Grep "<符号名>" src/zephyr/`
5. 批量登记：本轮确定要新建的全部文件，CREATE-GUARD token 一次性登记进登记表（同 commit）；depgraph 设计态批量 `--add-design-node`
6. 按清单 §八波次顺序进入 §2 微循环

## §2 单模块施工微循环（每个 C/B 模块走一遍，8 步）

```
①反查定界（已由波次0覆盖则跳） → ②depgraph 设计态登记（--add-design-node，先于写码）
→ ③蓝图（新建模块按 blueprint_construction_template；扩展现有模块豁免）
→ ④落码（15 字段文件头；CORE 模块头部加 [CORE-ALGORITHM] 标记行）
→ ⑤自测：tests/<域>/test_<模块>.py 先红后绿（断言含边界值/空输入/异常路径）
→ ⑥红蓝对抗（§4 手法≥3 种，结果记入清单文档台账列）
→ ⑦双审循环（§3：连续两轮 0 问题才放行）
→ ⑧提交：网关 --files 含代码+测试+地图 module_ref 回填（同一 commit）+30 分钟纪律
```

## §3 审查循环协议（核心质量闸，机械执行不裁量）

- **审查范围**（每轮过一遍）：长清单 14 节的适用子集（A.0.5 改动分类先行）+ §4 红队手法 + 门禁三关（validate/双测试/align_all）+ `ast.parse` 语法 + 文件头 15 字段齐性
- **连续性语义**：第 1 轮发现问题→修复→**计数清零**重来；连续 2 轮 0 问题→放行
- **问题台账**：记在施工清单文档对应行（轮次/问题数/一句话问题/状态），**禁止新建审查报告文件**（审查结论对话内给+清单打勾，Step 1 纪律）
- **熔断**：同一模块连续 3 轮循环仍有问题 → 状态=BLOCKED-晨审，跳下一模块，**禁带病提交、禁降低验收标准**
- 每模块全部验收命令必须真实执行并留输出，**禁止"应该能过"式跳过**（Flash 过度自信是对抗重点）

## §4 红蓝对抗与极限对抗（每模块 ≥3 种红队手法，留痕于台账）

| 手法 | 打法 |
|---|---|
| 红-边界 | 空输入/None/极值/空列表/除零路径（传感器类必测：无数据日、停牌日） |
| 红-竞态 | 双线程/双调用同抢状态（条件队列、订单状态机类必测） |
| 红-故障 | DB/CH 断连、超时、返回垃圾数据时的降级路径（fail-open 还是 fail-closed 要显式选择） |
| 红-前视 | 数据右移 1 个交易日重算，成绩异常=有前视（PB-16，传感器/信号类必测） |
| 红-契约 | 改动函数签名/返回结构→Grep 全部调用方逐一核对（A.6.1 最高危项） |
| 红-地图 | 动 YAML 后 adversarial 套件 f4 锚断言不消失；R37 algo_note 非空 |
| 蓝-防御 | 门禁三关全绿+双测试+ast.parse+15 字段齐+CREAT token/depgraph 登记闭环 |
| 极限 | 全部 C 类完成后：跨模块串联冒烟（传感器→水温→传导链路 dry-run 数据贯通），假数据标注 [ASSUMPTION] 禁冒充 verified |

## §5 CORE-ALGORITHM 标记清单（晨审 GLM5.3 优先复审，夜班头部加标记行）

| 模块 | 对应节点 | 晨审重点 |
|---|---|---|
| risk/core/drawdown_state_machine | X-R1-01 熔断五级 | 状态迁移完整性/迟滞解除/禁 V 型回满 |
| sell_decision/core/stop_loss_strategy | X-S1-02 止损族 | 止损价计算/移动止损不回退 |
| sell_decision/core/t_trade_coordinator | P2-02 做T调度 | 做T闭环配对/成功率口径 |
| position/core/pyramiding_rules（夜班新建 C9/C10） | P3-01/02 | 金字塔递减比例/总上限 |
| position/core/defensive_asset_whitelist（新建 C11） | X-R1-03 | 白名单来源固化/方向=买入核对 |
| ex_core/pricing_policy | L4-03 价格锚定 | 锚价 tick 逻辑/市价应急触发条件 |
| ex_core/order_manager | L4-10 订单状态机 | 状态迁移禁跳态/撤改竞态 |
| pf_alloc/core/multi_strategy_capital_allocator | F-C1 预算切分 | 权重归一/预算带封顶 |

## §6 提交与队列纪律

- 网关提交：`python scripts/git_commit.py --session night-gw-2300 --files "<逐一列出>" --message-file <msg> --allow-overlap`；**禁 --no-verify / 禁 --allow-multi-domain / 禁裸 git commit**
- **暂存区预警**：截至 21:00 共享暂存区有 sess-26548 + worker-69d94 两活会话 7 件在途 WIP（框架编排器特性），gate 扫到它们的违规会拦所有人——提交被外来违规阻断时：**排队重试（≥5 分钟间隔，省 allow_overlap 额度 30/7d），禁清禁改别人 staged 文件**（判读器已定性 active_wip）
- 每波次收尾提交一次（同波次多模块可合并 commit，但地图 YAML+对应代码必须同 commit）
- allow_overlap 用量自知：本循环已用 ~8 次/30（7 天窗口），夜班按"窗口探测通过才尝试"省着用

## §7 早 9 点交接包（08:30 前写完）

1. `.runtime/handoffs/handoff_night-gw-2300.json`：pending_tasks（BLOCKED 项+原因）/warnings/已完成清单（含 commit hash 对照）
2. 施工清单文档三表全部打勾/改判/挂起状态更新——**台账即交接**
3. 晨审 GLM5.3 复核清单（按序）：§5 CORE 8 项逐个复审 → 红蓝对抗台账抽验 ≥3 项复跑 → validate warn 中 R1=0 与 R21 欠账核对 → 双测试/align_all 复跑确认 → BLOCKED 项逐个开新工单
4. 验收签收标准：CORE 复审零 P0/P1 问题 + 抽验复现通过 + R1 清零 → Owner 放行收工；有问题→工单进白天场

## §8 夜班禁令（红线，违反即停）

1. 禁 `--no-verify`、`--allow-multi-domain`、裸 git commit、改门禁/规则真源本身（Gate 行为问题→挂起记台账）
2. 禁碰：validation/ 四件套（st-xflow）、前端三件套+api_server 样式、他会话 7 件 staged WIP、chainmap
3. 禁新建顶层包/禁 governance/ 根平铺/禁 EOF 盲插 token
4. 禁把 [ASSUMPTION] 假数据冒充 verified、禁跳过循环验收宣称完成
5. 失败 3 轮挂起（§3 熔断）——**宁可少交，不可交坏的**（Owner 原则：防亏钱>进度）
6. ABS-01~08（trae_018）全程有效：禁删文档/禁裁规则冲突/禁忽略高优先级规则
