---
ttl: task_bound
title: "NB1 B2 裁定卡：F128 data_security 三件——两接点落地方案（数据出口+LSG l1 前置）"
session: st-nightsweep2-nb1-20260930
updated: 2026-09-30
---

# B2 F128 data_security 三件 · 接线接法挖矿裁定卡

## 事项

Owner 问：接线的接法——"数据出口"+"LSG l1 前置"两接点的具体落点。对象=src/zephyr/data_security/ 三实体件（data_masking_engine 191 行/data_access_auditor 318 行/ai_masking_pipeline 215 行，测试 3 件全绿）。现状：F128 已落包级 [DEPRECATED]+"无直接继任/能力空缺转 known-gap"（794f16569b），净删挂 Owner 门 #42-44。本卡=按 Owner 本夜指令重新评估接线价值，供其翻案或维持。

## 六向台账快照

| 向 | 实测 |
|---|---|
| 通道 | F128 案卷（k_frontend_docs/12_f128_data_security_masking.md）→ SW5 退役标记（空缺转 known-gap）→ Owner 门 #42-44 |
| 原料 | 三件能力本夜现读：DataMaskingEngine（role×field 策略注册+格式保持加密 FPE fpe_encrypt/decrypt+Laplace 噪声）；DataAccessAuditor（AccessEvent/BaselineProfile/AccessAnomaly 基线偏离审计）；AiMaskingPipeline（**L1-L4 分级**：L4 禁原文仅统计摘要/L3 金额分桶+标的泛化/L2 保统计禁原值/L1 放行；purpose→MaskingPolicy 查表 Fail-Closed；逐次调用记脱敏前后对比审计回调——docstring 自述"Presidio 分级思想单机化"） |
| 状态 | PROD import=0、零 TC 腿、零挂载、零任务（F128 四态复核）；SourceType 消费腿=同名假阳性已拆；3 件测试绿（自洽） |
| 消费方 | 零。两处应然消费面现状：①LSG gateway（scan_input/scan_output/_init_layers，无任何脱敏前置）；②数据出口=dashboard api_server.py（QMT 桥 CSV 读入+账户/持仓接口回包）与各类导出，均未脱敏 |
| 缺口 | ①脱敏规则册（role→field→kind 清单）无 YAML 真源；②审计落盘真源未声明（F102 审计体系 vs 独立落盘）；③无效果型 gate 保证"该脱敏的被脱敏" |
| 处方 | 见下"两接点落地方案" |

## 三审结论

1. **价值审（通过——known-gap 应翻案为"值得接线"）**：本仓是个人量化系统但含**真实账户数据出口**（dashboard 持仓/资金接口、QMT 桥 Account.csv），且 LLM 调用面在产（LSG 必经）。ai_masking_pipeline 的 L1-L4 分级+purpose 查表+审计回调与**全网最佳实践吻合**（2026 业界口径：PII 在 gateway 前脱敏+双向（输入与输出）+**日志与导出也要脱敏否则日志即泄漏面**；分级可逆 placeholder vs 不可逆 redaction 按敏感级选择——L3 分桶泛化/L4 统计摘要正是该谱系）。设计先进度足够，不需要引 Presidio 新依赖。
2. **真源唯一性审（通过——不与 F88/F105 合并）**：F128 案卷已实核三向边界：F88=LSG LLM 出入口防御（无列级脱敏）、F105=密钥治理、F128=数据层列级脱敏+访问审计——跨域不同对象不并（宪法 §4.2）。仓内无第二套脱敏实现；全网 Presidio 是更重的外部栈，单机化现实现融合价值高于引入依赖。
3. **数据持续性审（不适用→事件面）**：脱敏无数据集依赖，审计事件随消费产生；不接线的代价=审计事件恒零（known-gap 永不收敛）。

## 两接点落地方案（供 NB2 施工，红样先行）

**接点① LSG l1 前置（AI 出入口）**：
- 落点=zephyr.security.llm_defense.llm_security.gateway.LSGSecurityGateway.scan_input 入口处（:214），在 _evaluate_chain 跑 l1_input **之前**插 AiMaskingPipeline.mask(purpose=request.purpose, text)——形态二选一：a)包装层（gateway 外部组合，零改 LSG）；b)注册为新前置 layer（实现 LLMSecurityProtocol 进 _init_layers，fail-closed 不入 fail_open_layers）。**推荐 a**（LSG 是门禁热区，零侵入对齐最小变更；purpose 缺省=最低级 L1 保持现行为）。
- 语义：脱敏产物再过 l1 注入检测（顺序=先脱敏后防御，防"密文绕过检测"与"原文喂模型"两头）；审计回调→DataAccessAuditor.log（SourceFile=LSG 通道），逐次记 before/after 摘要（L4 下 before 只落长度/实体计数，不落原文）。
- 输出侧（scan_output）复用同 policy 反查（FPE 可逆件凭 role 白名单还原，白名单真源=规则册 YAML）。

**接点② 数据出口（dashboard/导出面）**：
- 落点=frontend/dashboard/api_server.py 响应序列化层加一个装饰器/middleware：账户/持仓/成交流水类 endpoint（Account/PositionStatics 桥读出的字段）在返回前过 DataMaskingEngine.mask_field(role="dashboard_external", field, value)；字段清单来自新规则册 YAML（config/data_masking_policy.yaml：role→field→kindredact|fpe|bucket|laplace），此册同时是缺口①的真源落位。
- 导出/日志同步（全网教训：只挡请求不挡日志=白挡）：审计回调与访问日志落盘统一走 DataAccessAuditor 通道并声明真源（建议挂 F102 审计体系既有的 sink，回填 F128 缺口②）。
- 效果尺（回填 F128 缺口③）：新增 own-scope gate——扫描 api_server.py 出口 handler 是否存在未过 mask 层的敏感字段白名单命中（与 F126 字段字典敏感标记联动），登记 gate_registry。

**配套**：三件包级 [DEPRECATED] 若翻案须撤销（与 B1 同法：successor 改"接线复活"）；known_gap 条目改 in_progress；测试保持 tmp_path。

## 三态裁定建议

**【融合=接线复活】（两接点处方如上）**。若 Owner 权衡后仍判不接：则维持净删+归档 G:/zephyr_cold/retire_c267_20260930/F128_data_security/（MANIFEST 范式同 F130），known-gap 长期化；但鉴于真实资金账户数据出口在产，本车道**明确建议翻案接线**。

## 自审闸三态

**挖干（置信度=高，两落点行号级定位已给）**。可复算：三件类/方法清单现读+LSG gateway/l1_input 现读（scan_input:214/SourceType:29）+api_server 出口面现读（:361-454 QMT 桥）+F128 案卷刷新批注+全网最佳实践三源。未干残余：①api_server 全部 endpoint 清单未逐条过（敏感字段白名单属施工期活）；②F102 审计 sink 的具体挂点未核（处方给了方向未给行号）。
