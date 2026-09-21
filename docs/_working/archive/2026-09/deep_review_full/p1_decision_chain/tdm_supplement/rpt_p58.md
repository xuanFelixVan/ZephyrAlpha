---
ttl: task_bound
title: 深度审查作业簿——升降级管线与退役评审
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：升降级管线与退役评审（P58）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/factor/governance/lifecycle_state_machine.py:52`（_build_config）/:112（create_factor_fsm）
- TDM 节点: TDM-F-C3-02（stage，config/trading_decision_map.yaml:3922）
- 生产调用方: `factor/governance/six_step_flow.py:96` 与 `factor/factor_factory.py:63,255`（create_factor_fsm 真实消费）——**FSM 本体非孤儿，但被消费的是因子生命周期骨架，不是节点声明的 sleeve 升降级管线**
- 测试文件: tests/factor/test_lifecycle_state_machine.py（92 passed 同批）

## 1 对象快照

- 范围：因子生命周期 FSM 全文件（121 行）——8 状态（research→development→backtest→paper→grayscale→production→deprecated→retired）+11 条转换（线性推进+灰度回退+两处异常回退），状态清单从 governance/_config.yaml 读、转换拓扑硬编码，复用项目级 StateMachine 泛型。
- 排除项：six_step_flow/factor_factory 的编排逻辑（各自对象）；项目级 StateMachine 基类（shared/lifecycle）。
- 测试覆盖概况：合法/非法转换覆盖存在；**无 YAML 自定义状态与硬编码转换的组合崩溃场景、无 register 幂等吞异常场景**。
- 材料包缺项声明：运行时证据包未取；数据画像不适用。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| D | **module_ref 语义错位（对账主发现）**：TDM-F-C3-02 声明的是 **sleeve 升降级评审管线**（月度 composite 60+120 双窗口评审/季度 verdict 四选一/THD-RETIRE 三线/sleeve 回撤 5% 减半 7.5% 冻结/DSR<0 连 8 周退役门/观察名单半仓缓刑/滞回带）——本模块实际承载的是**因子研发阶段流水线 FSM**（研究→退役 8 态），与 sleeve 业绩治理零交集：composite/THD-RETIRE/DSR/减半/冻结/verdict 全部零代码。且注释自称"红节点（评审编排面）"——节点语义整体未施工，module_ref 锚在了一个名字相似但职责不同的现成件上 | config/trading_decision_map.yaml:3922-3990（algo_note+D115/D86 注释） vs lifecycle_state_machine.py:16-26（8 态定义）；grep composite/THD-RETIRE/DSR/减半 于模块与 factor/governance 包零命中（engine.py/factor_pool_manager.py 无 sleeve 评审逻辑） | P1 | 对照 TDM 逐项 grep factor/governance 包；读模块 docstring 与 TDM algo_note 并排 |
| A | FSM 拓扑健康：线性主路径+GRAYSCALE→PAPER 回退+BACKTEST→RESEARCH/PAPER→BACKTEST 异常回退；RETIRED 终态不可逆；**但注释"任何非终态可回退到 research"与实现不符**——PAPER/GRAYSCALE 无直达 research 边，PRODUCTION 无任何回退边（只能 deprecated→retired 单向） | lifecycle_state_machine.py:84-87（注释）vs 75-87（实际边表） | P3 | 尝试 PRODUCTION→RESEARCH 转换看 InvalidTransitionError |
| B | 状态清单可配置+转换硬编码的分裂真源：若 _config.yaml 改状态名/增删状态，Transition 表仍引用默认常量 → 构建期崩溃或引用未注册状态——"参数从 YAML 读"的约定与结构性约束的边界声明（docstring :55-57）不足以防错，无启动期一致性校验 | lifecycle_state_machine.py:59-71,75-87；factor/governance/_config.yaml:13-23（当前值=默认值，暂未触发） | P3 | _config.yaml 临时改一个状态名跑 _build_config 看异常（读后还原） |
| E | register_factor_lifecycle 捕获**全部异常**静默 pass（:107-108 自注"幂等+注册表不可用不阻断"）——真实的注册冲突（如同名 FSM 拓扑不同）/注册表损坏被无声吞掉，后续 create_factor_fsm 绕过注册表直接新建实例：注册表语义空转的通道 | lifecycle_state_machine.py:97-109,120-121 | P3 | 预注册不同拓扑的同名 FSM 再调 register 看静默通过 |
| A | FSM 状态机数学：转换合法性由基类保证（InvalidTransitionError 契约）；8 态无环（除回退边）、终态唯一——拓扑本身无死角；无守卫条件/审批钩子（灰度→实盘无 gate 挂点，升级全凭调用方） | lifecycle_state_machine.py:52-94 | P3 | 读基类 Transition 校验+确认无 guard 参数 |
| C | 消费面真实（six_step_flow:96 每因子建实例/factor_factory:255 编排）——爆炸半径=因子治理编排，非 TDM 声明的组合 sleeve 层；sleeve 层真消费方不存在（联动 P57/P59 同批 C3 树枝全部无 sleeve 级承载） | six_step_flow.py:96；factor_factory.py:255 | —（判定用） | — |

## 3 SOTA 对照

- 因子生命周期 stage-gate 范式（研究→回测→纸面→灰度→实盘→退役）：**对等已有**——量化因子工厂标准流程（Alpha Architect 因子信息衰减与退役时机框架 alphaarchitect.com，2019-2026；FE Training 因子投资生命周期教材 fe.training，2026）；8 态划分与业界 stage-gate 同构，FSM 骨架选型合理。
- sleeve 升降级评审（composite/回撤减半冻结/DSR 门禁）：**对等已有（声明侧）**——multi-strategy 平台 sleeve 级 5%/7.5% 减半冻结为 Millennium 系事实标准（TDM 已引）；本侧结论与 P56/P57 一致：**声明有据、实现缺位**。
- 状态机模式复用泛型基类：**对等已有**——FSM 工程实践无争议项，无需外部源。

## 4 缺陷清单

1. **[P1] TDM-F-C3-02 module_ref 语义错位+sleeve 评审管线整体未施工**。现状：节点锚定因子研发 FSM，sleeve 升降级（composite/THD-RETIRE/DSR/减半冻结/verdict）全仓无承载；节点自注红节点但 module_ref 给人"骨架已建"错觉。建议修法：module_ref 置空或改挂真实的编排待建占位；节点保留红标并把 D86 四条实操（composite 公式/观察名单/滞回带/fail-safe）列为施工清单。验证法：§2 轴 D 并排读法。
2. **[P3] 注释与边表不符（"任何非终态可回退 research"未实现）**。建议修法：改注释或补边（若 PRODUCTion 回退确无需求则明示单向终局语义）。验证法：非法转换探针。
3. **[P3] YAML 状态可配置×转换硬编码的分裂真源+register 全量吞异常**。建议修法：_build_config 后加"转换边引用的状态必须∈states"断言；register 只吞"已注册"异常类、其他上抛。验证法：改配置探针/预注册冲突探针。
4. **[P3] 灰度→实盘无审批守卫挂点**。建议修法：转换加 guard 回调参数（对齐 ai_autonomy: auto 的门位要求），或文档声明 gate 在调用方。验证法：读基类签名。

## 5 挂起疑问

- sleeve 升降级评审的真承载应落哪（factor/governance 新件 vs pf_core sleeve 治理域）——TDM-F-C3-02/S2-06（M-39 sleeve 治理状态表待施工）两处欠账宜合并立项，请 Owner 定归属。
- factor 研发 FSM 与 sleeve 评审 FSM 是否需要互通（因子 production 降级→sleeve composite 输入）——接线设计时回答。

## 6 完备性自评

六轴全查（A 数学四问：拓扑无环/终态唯一/边界=非法转换/回退边全过（FSM 无统计公式）；B 上游=_config.yaml 读取链+基类契约已查；C 下游=消费方真实（six_step_flow/factor_factory）判定非孤儿；D=与 TDM 声明逐条对账（主发现）+与 engine.py/factor_pool_manager 分工抽查；E 五问：静默失败=register 吞异常、假阳性=注释过claim、断供=注册表不可用绕行（已声明）、重复触发=幂等注册、时序=无时钟依赖）。长尾：①StateMachine 基类（shared/lifecycle）内部未审；②six_step_flow/factor_factory 编排逻辑归各自对象；③engine.py 与 grayscale_rollout.py 的灰度放量逻辑未深查（可能与本 FSM 状态联动）。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
