---
ttl: task_bound
title: L3 清洗段——强模型消化 真源设计稿 v1
owner: ZephyrAlpha-Owner
session: st-ailayer-20260917
date: 2026-09-17
status: design_v1
---

# L3 清洗段真源设计稿：强模型消化（API 判断质量环节）

> **本文性质**：骨架卡挖干产出=可直接施工的设计真源。上承骨架卡（README.md）、主文档定调
> 3/5/8/10/12（ai_layer_vision_and_roadmap_v1.md §0.5）、L2 收集段 DESIGN.md（库与事件契约）、
> OBJ_M 模型对象线 DESIGN.md §5（路由表口径）。**三不另立**：模型分派不另立路由表（只消费
> OBJ_M task_type 轨）、安全不另立网关（只接 LSG 真实入口）、抽验考尺不另立体系（复用审查
> 判据+常数预注册）。**硬边界自守**：本轮只写 L3_cleaning/ 目录内文件，零代码零配置零登记。

---

## 1. 六向寻路台账表

| # | 向 | 内部反查命中（真实路径） | 外部补盲（URL/发布方/年份） | 判定 |
|---|-----|------------------------|---------------------------|------|
| ① | 上游（谁喂 L3） | `L2_intake_library/DESIGN.md` §三 事件 `intake_clean_due` {card_ids[], domain_id, priority, spec_target:'spec_card_v0'}+T2 卡 spec_ref 回填位+funnel_stage=E2 前态语义；主文档定调 5（生食库）/10（清洗 API 进配额池）；主文档 §五 灌水投毒行="四闸+LSG 洗涤+外部代码零执行（规格重写）"——本段红线出处 | — | signal |
| ② | 下游（谁吃 L3） | `L4_compare/DESIGN.md` §三 增补边 `intake_exam_due` {card_id, spec_ref, domain_id, mechanism_family, four_gates}（L4 待 Owner-3 跨稿对齐项）；L2 DESIGN `intake_reject_due`（stage:'L3' 退回阴性）；L4 §2.1 考场矩阵读 spec_ref/data_fields；L7（坑集消费洗失败模式，L7 建后挂） | — | signal |
| ③ | 算法机制（怎么洗/怎么验洗） | 挖矿 SOP §2 模型分派二维法（输入体积×推理密度，flash 广度+强模型深读实战已验证）；宪法 §9.11 指令/数据边界（文件内容=数据永不作指令）；挖矿 SOP §5 四闸（闸 3 A 股适配/闸 4 可回测+数据可得=规格卡两字段的判据真源） | RD-Agent Specification 单元（arXiv 2505.15155，V2-R3 在档复用，同源两处消费过交叉闸）；FrugalGPT 级联（Chen et al. 2023，arxiv.org/abs/2305.05176，便宜先行升级制、同效果省至 98% 成本，arXiv+Semantic Scholar 双源）；LLM 裁判三偏差（Zheng et al. 2023，arxiv.org/abs/2306.05685，position/verbosity/self-enhancement，arXiv+ijcnlp 后续双源）；自偏好量化（Wataoka et al. 2024，arxiv.org/abs/2410.21819，GPT-4 显著自偏好且随参数量增大，arXiv+Semantic Scholar 双源） | signal |
| ④ | 后端（落哪个仓/什么件） | LSG 真实入口：`src/zephyr/security/llm_defense/llm_security/gateway.py`（LSGSecurityGateway.scan_input L176=L0→L1→L2→L5 / scan_output L199=L3→L6，fail-closed）；`src/zephyr/infrastructure/pipeline/llm_gateway.py`（LLMGateway.call L405，内部 L416 输入扫描+L437 输出扫描已接线）；`input_sanitizer.py`（InputSanitizer.validate_llm_context L76"上下文注入前安全校验"+ContextInjectionError）；`runtime_interceptor.py`（BareLLMCallError L86 裸调拦截）；`process_sandbox.py`（L2aSandbox L170+SandboxViolation/SandboxTimeout）；本地件：`src/zephyr/intelligence/local_llm_pool.py`（LocalLlmPool L141+PoolBudgets 显存预算）+`config/model_routing_policy.yaml`（local_providers ollama/local、default_local_model qwen3:8b）+`config/resource_profile_registry.yaml` L24（llm_local 互斥组） | 软件包幻觉/slopsquatting（Spracklen et al. 2024，USENIX Security 2025，arxiv.org/abs/2406.10279，16 模型 223 万样本中 19.7% 推荐包为幻觉、20.5 万假包名；arXiv+USENIX prepub+Socket.dev 多源）——零执行纪律的攻击面实证 | signal |
| ⑤ | 前端（怎么呈现） | `src/zephyr/frontend/dashboard/web/features/promotion/promotion.js`+api_server 只读路由（S13 建议卡先例，L2/L4 同款登记） | 同类呈现=清洗进度面板复刻 promotion 模式即可，内部先例已足 | signal（登记不施工） |
| ⑥ | 数据字段（记什么） | L2 T2 卡现成字段：spec_ref（回填指针）/four_gates/risk_flags/injection_probe/mechanism_family/domain_id；主文档附录 B 候选卡 schema v0；L4 实验卡 criteria_yaml/criteria_hash（抽验 rubric 同构先例）；OBJ_M M2 exam_suite_version+passport_version（washer 模型溯源字段先例）；挖矿 SOP §5 闸 4"字段在≠数据可得"（data_fields 必带质量画像） | 字段行业口径已由附录 B+L2 T2 覆盖，已查无必要 | signal |

**429 受阻**：首波双搜工具超时×2→80s 退避后单发重试全部成功；FrugalGPT 轮内部限流×1 自愈。
最终受阻轮=0，全程未编引文（注意：slopsquatting 正确 ID=arXiv 2406.10279，搜索纠错留痕）。

---

## 2. 真源设计

### 2.1 规格卡 schema 定稿（spec_card_v0）

**存储裁定（D-L3-01）**：PG `ai_intake` schema（L2 同实例）新表 `ai_cleaning_spec`，读写经
`DatabaseService.get_depgraph_conn()`（禁裸连接），TIMESTAMPTZ。**卡与 L2 候选卡=1:N 版本化**
（重洗不覆盖旧版，status='superseded' 墓碑制；定调 #12 进化留痕可回滚；L2 T2.spec_ref 只指
active 版）。DDL 增补进 L2 施工项 1 的 apply_ai_intake_ddl.py，不另开登记器。

```yaml
spec_card_v0:
  spec_id: SP-<card_id>-v<n>            # PK；card_id FK→ai_intake_card
  mechanism_one_liner: '一句话机制'      # ≤80 字，禁空泛（机检：长度+禁占位词）
  mechanism_detail: '一段话机制'         # 洗后深化版（区别于 L2 生卡的 mechanism 原文）
  applicability:                         # 适用条件（结构化，禁散文）
    regime: '趋势|震荡|高波|事件驱动...'  # 受控词表
    universe: '适用股票域'; frequency: '日|周|月'
    preconditions: ['可枚举前置条件']
  ashare_precheck:                       # A股适配预检=L2 四闸闸3 的规格级细化（证据深化）
    t_plus_1: {verdict, note}            # T+1 约束下还成立吗
    price_limits: {verdict, note}        # 涨跌停/流动性约束
    retail_dominance: {verdict, note}    # 散户主导市场变形
    overall: pass | adapt_needed | reject
    adaptation_plan: '...'               # overall=adapt_needed 必填（四闸闸3 原语义）
  risk_flags: []                         # 受控词表：survivorship/overfit_history/lookahead/
                                          # too_good/injection_suspect/data_no_access
  data_fields:                           # 数据字段需求（L4 考场可得性核验的输入）
    - {field: ..., source_ref: ..., quality_note: ...}   # 可得≠可用：必带缺失率/断更画像
  reproduction_notes: '复现要点'         # 伪代码/公式/参数/数据窗——L4 据此搭考场、施工段据此重实现
  source: {name, url, publisher, year}   # 来源四件套（从 L2 卡继承只读，禁改写——闸1 防洗后断源）
  source_quotes: ['关键论断原文摘录']     # 忠实性核验锚：每个关键论断可回溯原文
  lsg: {input_scan: pass, output_scan: pass, request_id_ref}   # §2.4 接线留痕
  wash: {session, model_id, model_tier, task_type, prompt_template_ver, washed_at}
  review: {sampled: bool, verdict: pass|fail|rework, reviewer_session,
           reviewer_model, rubric_scores: {fidelity, completeness, reproducibility},
           reviewed_at}                  # §2.5 抽验回填
  status: active | superseded | rejected_wash
```

**字段衔接（对账表）**：

| 对端 | 消费的 spec 字段 | 衔接语义 |
|------|----------------|---------|
| L2 候选卡（上） | card_id FK；source 四件套从 T2 只读继承 | 洗完回填 T2.spec_ref=active spec_id + funnel_stage 推进（经 card_store.transition，E2 前态）；洗不动→`intake_reject_due` 退阴性 |
| L4 考场（下） | mechanism_one_liner/applicability/ashare_precheck.overall/data_fields/reproduction_notes/risk_flags | `intake_exam_due` payload（L4 §三）；data_fields 供公平性"可得≠可用"核验；reproduction_notes 供考场搭建；risk_flags 供 too-good 三查先验；mechanism_family 沿 L2 卡不变（L3 无权改格坐标） |
| L2 四闸（校验） | ashare_precheck/data_fields | 是闸 3/闸 4 verdict 的证据深化；L3 有权**升级否决**（预检 reject→退回），无权降级放行 |

### 2.2 模型分派矩阵（对齐 OBJ_M 口径，不另立轨）

**裁定（D-L3-02）**：L3 全部工序映射到 OBJ_M §5.3 路由表**既有 AI 层 task_type 轨**，不新建
task_type、不内置模型名——模型/价格/档位真源=OBJ_M M2/M4（model_registry+model_routing_policy），
本矩阵只声明"工序→轨"映射。档位词表（economy/standard/premium）与时段策略（免费窗/谷时半价）
原样继承。成本/质量曲线依据：挖矿 SOP §2 二维法（输入体积×推理密度）+ FrugalGPT 级联实证
（便宜先行、判据触发才升级，arXiv 2305.05176）。

| L3 工序 | 二维法坐标 | OBJ_M 轨（task_type） | 档/时段策略（随 OBJ_M 轨演化，此处不锁模型名） |
|---------|-----------|----------------------|---------------------------------------------|
| ①本地预洗：取回物解析/分块/token 计量/模板字段预填/查重预检/清单式机械核对 | 不耗 API | 无（本地 qwen3:8b 可选+纯规则；走 LocalLlmPool，受 llm_local 互斥组与显存预算约束） | 本地优先（定调：量的环节本地） |
| ②长文深读消化（论文/仓库全文→结构化笔记） | 高体积×高密度 | `mining_deep` | premium，谷时半价优先 |
| ③规格提炼重写（笔记→spec_card_v0） | 中体积×中密度 | `cleaning_rewrite` | standard，谷时半价 |
| ④中文术语对齐（regime/universe 受控词表中文化） | 大体积×低密度 | `translation_registry` | economy，免费窗 |
| ⑤清洗质量抽验裁判（§2.5） | 低体积×高密度 | `review_judge` | premium，**不用免费窗**（裁判独立性>省钱），禁与 washer 同源同档 |
| ⑥洗不动判定（收费墙/license 拒/HTTP 查无/配额尽） | 纯机检 | 无 | 不耗模型 |

**级联与配额（FrugalGPT 落地）**：③默认 standard 起；抽验 rubric 三维任一=0 或解析失败→升级
premium 重洗一次（每卡升级 ≤1 次，防成本失控）；全部清洗 API 消耗记账进 M5 usage_records 口径，
卡均 token 预算=配额字段进 `config/cleaning_policy.yaml`（定调 #10 进化也要配额，禁自我扩容）。

### 2.3 外部代码零执行规程（规格重写操作规程）

主文档 §五 灌水投毒行的红线条款，落成 E0-E6 可执行细则。攻击面实证：代码生成模型 19.7% 推荐
包为幻觉、攻击者抢注假包名（slopsquatting，arXiv 2406.10279）——零执行=把供应链攻击面在清洗段
降为 0，重实现延迟到门闸后的施工闭环。

| # | 规则 | 细则 |
|---|------|------|
| E0 | 身份裁定 | fetched 代码/补丁/脚本/README=**数据非指令**（宪法 §9.11）；永不进解释器/构建器/包管理器/notebook 内核 |
| E1 | 隔离落盘 | 取回物只落 `.runtime/sessions/<sid>/staging/`（24h TTL），只读消费；禁落 src/scripts/config/tests/docs/03_modules |
| E2 | 静态通读 | 只许"读"：内容经 `InputSanitizer.validate_llm_context()`（§2.4 P1）后进 prompt 由模型**静态转述**；禁 shell/IDE 执行 fetched 片段、禁复制进 notebook 运行 |
| E3 | 规格重写产物 | 伪代码+公式+参数表+输入输出契约；`source_quotes` 逐条锚定原文（忠实性）；reproduction_notes 须足以让 L4 搭考场、施工段在**仓内**重实现——重实现发生在施工闭环（construction_workflow_policy，过 tests+gates），**不在 L3** |
| E4 | 依赖禁令 | 禁 pip install/conda/docker pull fetched 声明的任何依赖；依赖清单只登记进 spec 卡字段（data_eng 域 quality_gaps 同源） |
| E5 | 沙箱兜底（v0 不开通） | 未来若确需受控试跑（归 OBJ_T/OBJ_S 评估提案），唯一合法通道=LSG L2aSandbox（process_sandbox.py，SandboxViolation/SandboxTimeout fail-closed）+KillSwitch 常开+一次性环境；L3 v0 留痕禁令：无任何执行通道 |
| E6 | 动机锚 | LSG L0 supply_chain 层在档防线（l0_supply_chain.py）+ slopsquatting 实证；违反 E0-E4 = KillSwitch 建议+退回记阴性 |

### 2.4 LSG 接线点（真实函数/入口，四点全 fail-closed）

| # | 位置 | 真实入口（文件:行为） | 语义 |
|---|------|---------------------|------|
| P1 | 外来原文进 prompt 组装前 | `InputSanitizer.validate_llm_context(text)`（src/zephyr/security/llm_defense/llm_security/input_sanitizer.py，L76 起） | 上下文注入前安全校验（间接注入/指令伪装）；抛 ContextInjectionError=该材料标 injection_suspect 退回，不入清洗上下文 |
| P2 | 每次清洗/抽验 API 调用 | `LLMGateway.call(messages, provider=...)`（src/zephyr/infrastructure/pipeline/llm_gateway.py L405；内部 L416 调 LSGSecurityGateway.scan_input=L0→L1→L2→L5，L437 调 scan_output=L3→L6） | **L3 零裸调**：所有模型调用必经此入口，输入输出双扫描已内建；绕开者被 GATE-20+运行时拦截器双捕（BareLLMCallError，runtime_interceptor.py L86；宪法 §9.2） |
| P3 | 模型输出回填 spec 卡前 | LLMResponse 判定：error 非空/`[BLOCKED BY LSG]`/JSON 解析失败→拒收 | 输出层 LSG 拒绝或结构破损=该卡 wash_failed（重洗一次或退回），破损输出禁入库 |
| P4 | 审计留痕 | LSG request_id 记入 spec 卡 lsg 字段；LSG 判决经 behavior_audit_logger 进审计链 | 定调 #12 进化留痕：每次洗可回溯"哪道闸放行" |

### 2.5 清洗质量抽验协议（谁验清洗工）

**裁定（D-L3-03）**：抽验=审查判定的一种，**裁判走 OBJ_M `review_judge` 轨**（premium+异厂+与
washer 异档，MCE RISK-3.2"运动员不兼任裁判"复用）。裁判偏差的机制化防御（外部实证）：自偏好随
参数量增大（arXiv 2410.21819）→异厂异档硬性；position/verbosity 偏差（arXiv 2306.05685）→
**单卡绝对评分制**（禁 pairwise 对比打分）+字段锚定 rubric（逐字段有客观锚，禁整体印象分）。

| 项 | 裁定 v0（常数进 config/cleaning_policy.yaml，预注册+OBJ_R 提案通道） |
|----|------------------------------------------------------------------|
| 抽验比例 | 冷启动期（前 2 周/前 100 张先到者）100% 复核；此后每 washer 会话抽 20% + **高影响卡强制全检**（four_gates.cross_validation=pass 的信号卡） |
| rubric（预注册三维，各 0-2，禁有 0 分通过） | ①忠实性：mechanism/reproduction 每个关键论断能在 source_quotes 找到锚（防模型发明）；②完整性：七组字段全非占位、机检 schema 过；③可复现性：L4 拿 reproduction_notes+data_fields 能直接搭考场（防"看着对、用不了"） |
| 机检前置（裁判前零成本） | 字段非空+受控词表值域+source 四件套与 L2 卡一致+禁占位词（"待填/略/同上"）——机检不过直接 rework，不耗裁判 |
| 退回机制 | rubric fail→**升级换档重洗一次**（standard→premium，级联唯一出口）→再 fail→`intake_reject_due` {stage:'L3', rejection_reason:'wash_failed'（受控词表）, evidence_ref=review 记录}→L2 阴性视图；injection_suspect→另加 LSG 审计标记+该 source 源头进 L1 待观察 |
| 裁判质变监控 | 周度：复核不通过率 >10% → 该 washer 档位降级建议挂 OBJ_M 双跑复核；裁判与 washer 同源检测=机检（reviewer_model 与 wash.model_id 同厂即拒绝判卷） |
| 独立性 | reviewer_session ≠ wash.session（会话互斥，L4 §2.6 同款机检第一道的清洗段实例） |

### 2.6 本地优先-API 分界清单（量本地、判断 API）

定调原文（骨架卡）："量的环节本地、判断质量环节 API"。逐工序裁清单（★=不可逾越的分界判据：
**该步骤是否需要跨材料综合判断**——不需要=本地，需要=API）：

| 本地做（量） | API 做（判断质量） |
|-------------|-------------------|
| 取回物格式解析（PDF/HTML→文本块、代码块提取） | 机制一句话提炼（跨段落综合） |
| license/标题/作者/年份等元数据抽取与校验 | 适用条件归纳（regime/universe 判定） |
| 精确+simhash 查重预检（复用 L2 dedup.py，不重算） | A 股适配裁定（T+1/涨跌停改造方案） |
| 模板字段预填+token 计量+长文分块 | 风险旗标判定（投毒嫌疑/幸存者偏差需要语境判断） |
| 清单式 A 股预检的机械核对项（可枚举字段映射） | 规格重写（fetched 代码→伪代码的语义转换） |
| spec 卡骨架生成（空表+待填标记+受控词表展开） | 抽验裁判（§2.5 全部） |

本地执行件=`LocalLlmPool`（local_llm_pool.py：PoolBudgets 显存预算/LoadDecision），排班受
resource_profile_registry 的 llm_local 互斥组（qwen3:8b 单实例）；本地不可用→该工序排队不升级
API（本地优先是成本铁律非偏好，定调 OBJ_M budget_analysis 轨同款）。API 侧免费窗/谷时偏好随
OBJ_M 轨；成本审计按 OBJ_M §4.3 时段加权口径（谷时×0.5、免费窗×0 单列）。

---

## 3. 接线图（四契约）

| 对端 | 契约 | 方向 | 载荷/语义 |
|------|------|------|----------|
| **L2 收集库** | 领洗：消费 `intake_clean_due` {card_ids[], domain_id, priority, spec_target:'spec_card_v0'}（L2 §三 原文，零改动） | L2→L3 | L3 领取后逐卡本地预洗→规格重写→机检→（抽验） |
| **L2 收集库** | 回写/退回：①成功=T2.spec_ref=active spec_id+funnel_stage 经 transition 推进（E2 前态）；②不可洗（收费墙/查无/wash_failed/预检 reject）=emit `intake_reject_due` {card_id, stage:'L3', rejection_reason(受控词表: paywalled/not_found/wash_failed/ashare_precheck_reject/injection_suspect), evidence_ref} | L3→L2 | 阴性卡入 V2 视图，同 simhash 换皮被 L2 闸拦截（L2 既有语义复用） |
| **L4 对比考场** | 规格卡供考：`intake_exam_due` {card_id, spec_ref, domain_id, mechanism_family, four_gates}（L4 §三 增补边，跨稿对齐=L4 待 Owner-3，本稿不重复立项）；spec 卡另供 data_fields/reproduction_notes/risk_flags 作考场搭设与三查先验 | L2/L3→L4 | L3 只保证 spec 卡字段完备，emit 权在 L2（库主），L3 经回写触发 |
| **OBJ_M 模型对象线** | 分派契约：L3 五工序→既有 task_type 轨（§2.2 矩阵）；washer/reviewer 模型档案（model_id+passport_version+exam_suite_version）记进 spec 卡 wash/review 字段；清洗 API 消耗进 usage_records 供 M5/M2 实测成本回写 | L3↔OBJ_M | OBJ_M 换档/换模型=L3 零改动（只认轨不认模型） |
| **LSG 安全网关** | 四接线点（§2.4）：P1 validate_llm_context→P2 LLMGateway.call（内嵌 scan_input/scan_output）→P3 输出判收→P4 request_id 留痕 | L3→LSG | fail-closed：任一点拒=该材料/该卡走退回路径 |

---

## 4. 施工项清单

| # | 项 | 文件（新增/修改） | 验收标准 |
|---|----|------------------|---------|
| C1 | 清洗策略常数 | `config/cleaning_policy.yaml`（新增，带治理锚定头）：抽验比例/冷启动阈值/rubric 三维判据/受控拒因与 risk_flags 词表/卡均 token 预算/级联升级上限 | 全部常数预注册；Owner 点头记录；改动走 OBJ_R 流水线 |
| C2 | DDL 增补 | L2 的 `scripts/ai_layer/apply_ai_intake_ddl.py` 增 `ai_cleaning_spec` 表（§2.1 全字段+索引 card_id/status） | 幂等两次零错；TIMESTAMPTZ；全经 DatabaseService |
| C3 | 规格卡库服务 | 新 `src/zephyr/ai_layer/cleaning/spec_store.py`：CRUD+版本 supersede+active 指针回写 | 重洗不覆盖旧版有测试；禁占位词/值域机检；零裸连接 |
| C4 | 清洗执行器 | 新 `src/zephyr/ai_layer/cleaning/washer.py`：领 intake_clean_due→本地预洗→工序②③④调 LLMGateway（task_type 由 OBJ_M 轨解析）→spec 卡解析落库 | 零裸 LLM 调用（拦截器测试证伪）；E1 隔离落盘路径校验；解析失败走 P3 拒收 |
| C5 | 本地预洗器 | 新 `src/zephyr/ai_layer/cleaning/local_prefill.py`：解析/分块/预填/查重预检调 L2 dedup_query | 纯本地可跑通（可选 LocalLlmPool）；不耗 API 配额；分块计量准确 |
| C6 | 抽验审计器 | 新 `src/zephyr/ai_layer/cleaning/auditor.py`：采样器（冷启动 100%→20%+高影响全检）+review_judge 单卡绝对评分+rubric 判分+退回流转 | 裁判与 washer 同源同档被拒有测试；fail→重洗→reject 两级流转留痕；采样比例读 C1 非硬编码 |
| C7 | 测试 | 新 `tests/ai_layer/cleaning/`（test_spec_store/test_washer/test_auditor/test_local_prefill） | 全绿；零生产路径写入（tmp_path）；进回归批 |
| C8 | 登记套件 | 施工班走 15 步闭环时办：add_module_translation ×新模块、apply_depgraph --add-design-node、capability card、creation_token | 全部登记器零报错；TRANSLATION-COVERAGE/CREATE-GUARD/DEPGRAPH gate 全绿 |

依赖序：C1→C2→C3→C5→C4→C6→（C7 随项并行）→C8。外部依赖：L2 库施工先行（事件/表/闸是真源）；
OBJ_M C6 路由增轨先行（task_type 轨存在才可解析）；LSG 零新增依赖（全部入口已在库 production）。

---

## 5. 挖矿日志表+自审闸

### 5.1 挖矿日志

| 轮次 | 矿脉 | 内/外 | 判定 | 关键产出 |
|------|------|-------|------|---------|
| L3-R1 | ①上游：L2 事件契约与 spec_ref 位 | 内 | signal | intake_clean_due/spec_ref/E2 前态语义现成——契约半数已被 L2 预留 |
| L3-R2 | ②下游：L4 考场字段需求 | 内 | signal | intake_exam_due+data_fields/reproduction_notes/risk_flags 三消费点反推出 spec 卡必填 |
| L3-R3 | ④LSG 真实入口反查 | 内 | signal | scan_input(L176)/scan_output(L199)/LLMGateway.call(L405,L416,L437)/validate_llm_context/BareLLMCallError/L2aSandbox 六入口全部在库 production |
| L3-R4 | ④本地模型件反查 | 内 | signal | LocalLlmPool+model_routing local_providers+llm_local 互斥组——本地优先有现成执行件 |
| L3-R5 | ③成本/质量曲线 | 外 | signal | FrugalGPT（arXiv 2305.05176，Chen 2023，级联省至 98% 同效果）——级联升级制+Economy-first 依据 |
| L3-R6 | ③裁判可靠性 | 外 | signal | MT-Bench 三偏差（arXiv 2306.05685）+自偏好量化（arXiv 2410.21819）——异厂异档+单卡绝对评分制依据 |
| L3-R7 | ③零执行依据 | 外 | signal | 软件包幻觉/slopsquatting（Spracklen，USENIX Sec 2025，arXiv 2406.10279，19.7% 幻觉包）——E0-E6 攻击面实证；ID 经搜索纠错（2406.01079 为误） |
| L3-R8 | ③RD-Agent Specification 单元 | 复用 | signal（在档） | arXiv 2505.15155（V2-R3 同源两处消费，交叉闸满足）——规格提炼工序的业界同名物 |
| L3-R9 | ⑤清洗进度呈现 | 内 | signal（登记不施工） | promotion 先例复刻即可，归 L2/L4 呈现件，本段零前端施工 |
| L3-R10 | ③自动清洗管线开源件引入评估 | 外 | noise（归因：零执行红线+LSG 强耦合，外引管线反而要拆安全边界） | 不引依赖；RD-Agent 思想内化不引代码 |

### 5.2 挖后自审闸三态裁定：**施工**

- **主判据（一票放行）**：消灭三段人工——①人工深读论文/仓库并手写规格笔记（现散在挖矿会话）；
  ②人工判断"这方法 A 股能不能用"（现凭直觉）；③人工复核 AI 笔记质量（现状=无复核）。全部转
  机检+异档复核协议。
- **终局全貌位置**：进化循环七段的第 3 段，L2 库→L4 考场之间无它则断链；业界同名物=RD-Agent
  Specification 单元，非中间件不会被替代。主文档 §五 灌水投毒行点名本段两件套（LSG 洗涤+零执行）。
- **反驳者三问**：①与 L2 四闸重复？——L2 管入库真伪与查重（卡级），L3 管内容标准化与适配裁定
  （机制级），ashare_precheck 是闸 3 verdict 的证据深化而非重判，分层不重复。②清洗 API 成本失控
  ？——本地优先清单+工序⑤⑥零模型+级联升级 ≤1 次+卡均 token 预算配额（定调 #10）+谷时/免费窗
  轨偏好，五重成本闸。③spec 卡并进 L2 T2 一列了事？——版本化审计（重洗留痕/定调 #12）+抽验记录
  挂卡需要 1:N 结构，单列 JSONB 必然被并发覆写病案重演（candidate_registry 前科）。
- **反省**：抽验比例（100%→20%）、rubric 0-2 三值、卡均 token 预算是**设计定值非实测标定**，全部
  收进 config/cleaning_policy.yaml 预注册+OBJ_R 提案通道，首轮数据回来后修订——不在本轮拍死。

### 5.3 待 Owner（2 项）

1. **清洗考尺初值点头**：config/cleaning_policy.yaml 全部常数（抽验比例/rubric 判据/预算/受控
   词表）——尺子归治理层，AI 只有提案权（README §1.6），本稿 §2.5 即提案。
2. **creation_token 补登**：本班硬边界禁登记 token，DESIGN.md 的 creation_token 由主会话/Owner
   补登（L4 稿同款先例）。

---

## 修订记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-09-17 | design_v1 | 初稿：六向台账（8 signal+1 复用+1 noise/0 受阻）+spec_card_v0 schema（ai_cleaning_spec 表）+模型分派矩阵（五工序对齐 OBJ_M 既有轨）+零执行规程 E0-E6+LSG 四接线点+抽验协议+本地优先分界清单+四契约接线+8 施工项+自审闸=施工 |
