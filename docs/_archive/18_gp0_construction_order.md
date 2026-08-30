---
ttl: permanent
---

> **归档注记（2026-08-30）**：自 design_memos/implementation_plans 归档（候选核销批 greatwall_20260830——内容全量施工完毕核销，审计链保留，原位索引已同步标注）。
>
> **文档元信息**（_working 临时区豁免规范：EXEMPT-ZONE-FM）：doc_type=architecture_view · title=阶段三 AI 层施工顺序清单（GP0 手动地基全量） · owner=ZephyrAlpha-Owner · language=zh · status=active · version=1.0.0 · date=2026-08-22 · topic=phase3_ai_layer_gp0_construction_order · scope=09_ai_architecture · completes_when=GP0 全部可施工项完工、测试两轮零问题、提交闭环后归档（归档不删除，保留审计链）

# 阶段三 AI 层施工顺序清单（GP0 手动地基全量）

> ## 结案报告（2026-08-28 全量审查批，代码实证）
> **实际开发**：七波派单全闭环——波1 保障四件套（lsg_gate/autonomy_boundary_gate/kill_switch_orchestrator/security_event_bus）；波2 gateway MVP（llm_runtime_gateway 三通道+llm_call_log）；波3 04 T0 七件/07 CE 收口/06 手动链路 5/5 PASS；波4 进化能力手动形态（11 证据关联/12 L1 反思/13 模块工厂 SOP+首实例/14 四类薄入口）；波5 M3-⑨ 真跑（DeepSeek 402→Qwen 降级链接管）；波6 两轮零问题；波7 蓝图批+三文档回写+总收尾报告。
> **最终成果**：GP0 全部可施工项完工，E0-1~E0-8 全绿，M0 Owner 终审通过。frontmatter completes_when 已达成，按约定**归档（归档不删除，保留审计链）**。
> **未做+原因**：无（遗留项全部转 tracker #253~#257 登记在册）。**本案已结案**。

> **性质**：施工排序清单——Owner 2026-08-22 长城任务任务二（阶段三 AI 层施工）驱动，将 09_ai_architecture/implementation_plans/ 全部施工图中**全局 Phase 0（GP0 手动地基）**的施工内容按依赖与冲突面排序成波次。
> **范围裁定**：按项目既定教训（project_memory：GP0 确定性件优先，GP1/GP2/GP3 因结构性阻塞与依赖真实运行流量验证不抢建），本清单只覆盖 GP0；GP1+ 一律不施工。真源=[17_phase_roadmap.md](17_phase_roadmap.md) §4.2（GP0 组成+E0-1~E0-8 退出检查表）与各文 §4 Phase 0 验收标准。
> **前置状态实证（2026-08-22 勘察）**：E0-1 提交队列 ✅ 已绿（08 号文 Phase 0，flag 已翻开）；E0-2~E0-7 现状=09 部分已建/04·06·07 设施在收口未做/15·16·11·12·13·14 零代码（逐项实证见 §1）；E0-8=03 号文 Owner 裁定=人工项（登记跳过）。

## 1. GP0 现状实证（2026-08-22 勘察结论）

| 退出项 | 现状 | 缺口 |
|---|---|---|
| E0-1（08 提交队列 MVP） | ✅ 已绿 | — |
| E0-2（09 LSG 主链路贯通） | 🟧 部分：LSGSecurityGateway（L0→L8 链式 fail-closed）/runtime_interceptor（sys.meta_path 裸调拦截）/GATE-20 静态扫描/59 测试文件均已建 | ①三层运行时客户端构造点未统一注入（integration/local_model/ 的 OllamaChat/DeepSeekChat 零 LSG 引用）②全仓绕过路径=0 报告无产物 ③逐层故障注入演练记录无产物 |
| E0-3（15 三分类 gate+KS 编排+延迟实测） | ❌ 运行时三分类写操作判定 gate 零代码（标注/静态校验器/GOV-AI-001 注册表已有）；KS 五套各自独立无两级编排器；15 §2.3 延迟只有预期口径无实测 | 全部三件 |
| E0-4（16 统一事件流+TNR） | ❌ 统一安全事件 schema/四域 adapter 不存在（仅 LSG 内部 L6 内存态事件）；auto_fix_engine 设施在（MOD-INF-031）但 TNR 演练零产物 | 全部两件 |
| E0-5（04/07/10 Phase 0） | 🟧 04 降级链有部分等价物（resource_optimization PressureLevel）但 RAM 预算 max_brain_memory_mb/冷启动 SLA 参数零落地；07 CE 蓝图漂移未收口（22→39 文件）；10 llm_runtime_gateway 不存在+三处模型注册分裂未对账 | 04 三参数/07 对齐收口/10 登记对账 |
| E0-6（11/12/13 Phase 0） | ❌ 证据关联/L1 反思三角色/模块工厂手动 SOP 全零代码零文档 | 全部三件 |
| E0-7（14 四类薄入口） | ❌ 治理/业务/算法/自我迭代四类 Agent 入口零代码 | 全部 |
| E0-8（03 Owner 裁定） | ⏸ 人工裁定项 | 登记+跳过（不阻塞其余项施工与验收——按 17 号文 §6 Q4 口径如实登记） |

## 2. 统筹自主裁定记录（Owner 离场授权，留复核）

| # | 裁定项 | 裁定结果 | 理由 |
|---|---|---|---|
| E1 | llm_runtime_gateway 范围 | **10 号文 Phase 0（登记对账）+最小网关 MVP**（单一 infer 签名+调用登记落库+LSG 注入点+DeepSeek/Qwen 双通道），testing 封顶 | 44号 M3-⑨（阶段二已落 MOD-PLAN-007）是 gateway 的首个真实消费场景，其"LLM 客户端注入式"接口等 gateway 喂；10 号文 Phase 1 全量（预算门/路由级联）属 GP1 不抢——MVP 只取"登记对账+统一入口骨架"确定性部分 |
| E2 | 新模块成熟度 | 一律 testing 封顶（B-007），production 启用留 Owner | 既有铁律 |
| E3 | 故障注入/演练类验收 | 用合成故障+留痕文件实证（不破坏生产）；报告落 docs/_working/reports/ | 单机无热备环境的演练正确形态 |
| E4 | 03 号文域边界裁定（E0-8） | 登记+跳过 | 人工裁定项，AI 不替 Owner 拍板 |
| E5 | 14 号文四类入口 | 按 Phase 0"薄入口手动触发"施工（<200 行纯组装），产出 100% 落盘标 human_gated | 14 号文 §4 Phase 0 验收口径 |
| E6 | 施工隔离与提交 | 沿用阶段二模式：主工作区文件级隔离并行+注册表统筹集中串行写+每波即提交 | 阶段二零冲突实证有效 |
| E7 | M3-⑨ 真跑 | gateway MVP 就绪后接线：DeepSeek-V4-Flash 真跑 1 天盘前分析（谷时窗口外也仅 ~￥0.05 级成本）+Qwen 备用通道各一次 smoke | Owner 已提供双 key 并明确"可用作测试" |

## 3. 施工波次总表

| 波 | 内容 | 并行 | 依赖 |
|---|---|---|---|
| 波 1 | 保障四件套：09 LSG 客户端统一注入+绕过路径扫描报告+fail-closed 演练 / 15 运行时三分类 gate+KS 两级编排+延迟实测 / 16 统一安全事件 schema+四域 adapter+TNR 演练 | 3 并行 | 无 |
| 波 2 | 10 号：llm_runtime_gateway depgraph 登记+三处模型注册对账+mcp↔tool_contracts 漂移裁定+**最小网关 MVP**（infer 签名+登记落库+LSG 注入） | 1 | 波 1（LSG 注入点先就位） |
| 波 3 | 04 T0（蓝图漂移裁定提交+RAM 预算+冷启动 SLA+降级链对齐）/ 07 CE 对齐收口（蓝图 22→39+测试基线）/ 06 手动链路验证（护照门控+Quick 考试+CLI history） | 3 并行 | 无 |
| 波 4 | 进化能力手动形态：11 证据关联三件套 / 12 L1 反思+三角色骨架 / 13 模块工厂手动 SOP+1 手动实例 / 14 四类薄入口 | 4 并行 | 无（手动形态可与保障并行，17号文 §3.3） |
| 波 5 | M3-⑨ 接线真跑：gateway 客户端注入 MOD-PLAN-007+DeepSeek 真跑+Qwen smoke+落库验证 | 1 | 波 2 |
| 波 6 | E2E 测试两轮（GP0 全部新件+与阶段二集成链） | 修复并行 | 波 3/4/5 |
| 波 7 | 提交收口+临时清理+17 号文/00 索引状态回写+总收尾报告 | 统筹 | 波 6 |

## 4. 波 1 工单（保障四件套，3 路并行）

### 4.1 09 LSG 主链路贯通收尾（E0-2）

- **改动点**：src/zephyr/integration/local_model/（ollama_chat.py/deepseek_chat.py/local_model_scheduler.py/embedding_router.py）。
- **内容**：①客户端构造点统一注入 LSGSecurityGateway（构造时获取网关单例，ask()/inference() 调用前经 scan_input/判决，判决记录落 L6 审计——读 security/llm_defense/llm_security/gateway.py 的公开接口对齐既有消费方用法如 context_injector.py:247）；注入做成可开关（默认开，测试可关）；②绕过路径静态扫描报告：跑 scripts/governance/d7_code/detect_direct_llm_calls.py 全仓扫描，结果（命中=0 或豁免清单）落 docs/_working/reports/2026-08-22-lsg-bypass-scan.md；③fail-closed 演练：合成故障注入（临时篡改探针）验证 L1/L3 判决拒绝+Owner override 通道可用，留痕报告；tests/llm_security/ 既有套件零回归+新增注入点单测。
- **验收**：09号文 §4.2 P0-1~P0-5 逐项对应产物；tests/llm_security 零新增红。

### 4.2 15 运行时三分类 gate+KS 两级编排+延迟实测（E0-3）

- **改动点**：新建 src/zephyr/autonomy_core/autonomy_boundary_gate.py + kill_switch_orchestrator.py（或查重后定更合适包——autonomy_core/ 为 15 号文设施归属域）。
- **内容**：①运行时三分类 gate：写操作前查 GOV-AI-001（ai_autonomy_authority_registry.yaml）判定放行（ai_modifiable）/升级人审（human_gated 写拦截留痕）/物理拦截（immutable_core）；注册表不可读=fail-closed；②KS 两级编排器：系统级（security/access_control/kill_switch.py）+域级（技能级 skill_kill_switch 等）统一编排——仿真三类事故（kill_switch_sim 可复用）各拉对开关、系统级 TRIPPED 域级一致、复位需 Owner 批准标记、编排器故障时各开关独立可用（fail-open 分散态）；③延迟实测：内联拦截 1000 次采样 P50/P95/P99 落盘（docs/_working/reports/2026-08-22-autonomy-gate-latency.md），写回 15 号文 §2.3 口径（P95 超 1ms 则按文修订）。
- **验收**：15号文 §4.1 S0.2~S0.4 逐项产物；validate_autonomy_gate.py 回归绿；depgraph 2 planned 节点（统筹登记）。

### 4.3 16 统一安全事件流+TNR 基线（E0-4）

- **改动点**：新建 src/zephyr/security/security_event_bus.py（或 autonomy 运维域合适包，查重后定）。
- **内容**：①统一事件 schema（event_id/时间戳/来源域/威胁类别/严重度/证据指针/关联会话/schema_version）+四域 adapter（LSG/自治边界/治理门禁/运行时）落盘（.runtime/security_events/ jsonl）；②TNR 基线演练：auto_fix_engine（MOD-INF-031）端到端——注入合成故障→自动修复→验证可撤销+不恶化双达标，留痕报告（失败通道降级 A-L2 封顶）；③高危事件实时告警通道（webhook 不可达→本地持久化不丢）。
- **验收**：16号文 §4.2 P0-1~P0-4 逐项产物；四源探针 schema 校验 100% 通过单测。

## 5. 波 2 工单（10 号 llm_runtime_gateway）

- **Phase 0 纯治理三件**：①depgraph 设计态登记（统筹执行 apply_depgraph）；②三处模型注册对账基线：dump MOD-INF-039 运行时 dict+REG-ML-001 entries+llm_gateway._build_providers() 输出+model_pricing.yaml→对账清单落 docs/_archive/2026-08-22-llm-registry-reconciliation.md，不一致项逐条归属裁定；③mcp.json↔tool_contracts.yaml 漂移项裁定（4 个不一致 server 归属，10 号文 Q8）。
- **最小网关 MVP**（E1 裁定）：新建 src/zephyr/integration/llm_runtime_gateway.py——单一 `infer(task_type, prompt, model=None, **kw) -> InferResult` 签名（InferResult 含 text/model_version/tokens_in/tokens_out/cost_yuan/latency_ms）；通道=DeepSeekChat（L3 主力）+QwenChat（备用，OpenAI 兼容端点，读 .env QWEN_*）+OllamaChat（L2 兜底）三通道优先级链；每次调用**登记落库**（governance.db 新表 llm_call_log：ts/task_type/model/provider/tokens/cost/latency/status——92号 D2 同族授权）供日终对账（调用次数×单价 vs 账单防超额，44号 §9.14 联动口径）；LSG 注入点=波 1 ④.1 产物（客户端统一注入后 gateway 天然过闸）；预算硬门不做（GP1），只做登记对账。
- **验收**：10号文 §4 Phase 0 三项产物+gateway MVP 单测（mock 通道）+真 smoke（波 5）。

## 6. 波 3/4/5/6/7 工单要点

- **波 3**：
  - 04 T0：蓝图 5 漂移项提交裁定登记（circadian_scheduler 幽灵文件等——04号文 §4 0.1）；CapabilityRegistry 内存缓存+读写锁（命中率>95% 单测）；StatusDashboard 聚合视图降级降采样；StopGate session 预算参数超限阻断单测；四级降级链 GAP-009 对齐（CPU>75%/MEM>70%→Lv1/Lv2/Lv3 阈值表核对称谓）；RAM 预算 max_brain_memory_mb=2GB 参数落地 runtime_config+超限注入测试；冷启动 SLA boot P99<10s——start_brain.py --once 连跑 20 次实测留痕（环境不允许则降级为埋点+首次实测登记）。
  - 07 CE 对齐收口：蓝图 22→39 文件清单同步+construction_progress 修正+§1.1 索引重生成+核心 15 vs 辅助 24 标记（只标不删）+测试基线（tests/context 50+tests/ce 7）全绿。
  - 06 手动链路：TaskGate().load_passports()=7 实证；safe/unsafe 门控三样例（qwen3:8b naming_suggest 放行/code_fix 拦截/无护照拦截）；手动 Quick 考试跑一遍落 quick_profiles/；画像 CLI history 子命令可读实证。
- **波 4**：
  - 11 证据关联：research/evidence/ 三件套——假设注册表（状态机 proposed→testing→supported/refuted→archived 非法迁移拒）+证据链（三态+来源+假设外键+hash 固化篡改可检）+迭代引导器（规则化继续/转向/放弃可追溯）+日/周频批量入口（盘中零调用静态佐证）。
  - 12 L1 反思：反思记录 schema（落盘 data/brain/reflections/，缺必填字段被拒）+Actor→Evaluator→SelfReflection 三角色骨架（同任务分角色跑通）+L1 单轨迹反思器（失败轨迹→归因分类+改进建议非空）+盘后批量入口。
  - 13 模块工厂手动 SOP：《模块工厂手动 SOP》六环节检查单文档（每环节输入/操作/输出/验收/常见坑）+1 个手动实例全链路跑通（条目过 schema 校验+evidence 非空，factor/strategy registry 可查）。
  - 14 四类薄入口：治理/业务/算法/自我迭代四个 <200 行纯组装入口模块；样例工单端到端跑通+产出 100% 落盘标 human_gated；Grep 验证无下单调用。
- **波 5**：gateway 客户端注入 MOD-PLAN-007 run_llm_analysis——DeepSeek-V4-Flash 真跑 1 次完整盘前分析（真实数据打包+输出契约校验+llm_daily_analysis 落库+成本留痕）+Qwen 通道 smoke 一次；03:00 前谷时窗口外运行成本 ≈￥0.05 级（E7 裁定已授权）。
- **波 6**：E2E 两轮——新件全部单测+集成链（gateway→M3-⑨ 全链/15 gate 拦截链/16 事件流链）+既有 llm_security/autonomy_core/security 域回归；连续两轮问题=0。
- **波 7**：提交收口（每波即提交+最终核对）+临时文件清零+17 号文 §4.2 GP0 状态回写（E0-1~E0-7 实测态+E0-8 登记跳过）+00_index §6.3 待办勾选+总收尾报告落 docs/_working/reports/2026-08-22-phase3-gp0-final.md。

## 7. 不做清单（GP0 阶段纪律）

- GP1/GP2/GP3 内容一律不抢（10 号文 Phase 1 预算门/路由、09 缺口收尾 LSG 95%、15 Drift 防护、16 Diagnose→Remediate 接线、11/12/13 的 Phase 1+ 自动化等）
- 03 号文域边界归属裁定（Owner 人审）
- 多智能体框架本体（TradingAgents/LangGraph 等——44号 v1.2.1 与 61 号备忘既有裁定）
- RL/MAML/EWC/向量检索增强（单 GPU 约束+后置裁定）
- M3-⑨ PIT 历史全量回填（先 3 个月质量验证后，44号 §9.14 纪律）

## 8. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-22 | 1.0.0 | 初版：GP0 现状实证（§1）+自主裁定 E1-E7（§2）+七波排序+工单 | Owner 长城任务指令（阶段三 AI 层施工） |
