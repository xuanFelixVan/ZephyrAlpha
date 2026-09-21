---
ttl: task_bound
title: 深度审查报告——晋升建议器（T06）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：晋升建议器（T06）

- 状态: **已审**
- 级别: P0｜类型: 晋升闸（sim→production Owner 门执行器）
- 基线 commit: 2fa92002c3（工作树 bf65648609；本文件自基线零变更，锚点双有效）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/strategy_pipeline/promotion_advisory.py:655(decide)/:614(_transition_lifecycle)/:341(evaluate_sim_preauthorization)`
- 生产调用方: pipeline_events OPTIONAL_DUE_KINDS（promotion_advisory_due lazy 派发）；sim_governance emit；**api_server POST /api/promotion-decide（api_server.py:4351-4375，token=None via=frontend）**；GET /api/promotion-advisories（只读）
- 测试文件: tests/strategy_pipeline/test_promotion_advisory.py（15 用例）
- 材料包缺项: sim_governance/SCR-DEV 档案生产者未深审；dashboard 前端页面未审

## 1 对象快照

- 范围：四路证据合流建包、PA-1 三条件实据评估、Owner 拍板执行器（FSM 流转+注册表手术写+台账+回执）、token 三态校验。排除：api_server 投影层（只审调用面）、alerter、screen_source/decay_ledger 生产者。
- PA-1 背景：本件旧版曾硬编码三条件为 True（机器自签晋升令），2026-09-17 治本回落只读实据——修复后首审。
- 测试覆盖概况：15 用例含 token 三态/kill_switch/demote 流转/幂等/降级；**"连续 vs 累计"月度口径与 decide 中途失败死态无测**。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| E | **Owner 门认证半径=网络可达性（drive-by 可批）**：`token=None→服务端自取密钥当有效凭据`（promotion_advisory.py:585-586）；API 端点零 HTTP 认证且 `token=None` 硬编码透传（api_server.py:4375）；叠加 `CORSMiddleware(allow_origins=["*"], allow_methods=["GET","POST"], allow_headers=["*"])`（api_server.py:57）——任意网页可在 Owner 浏览器内 preflight 通过并 POST 批准（GET 列表同样无认证可先取 advisory_id）。docstring 自认"S12 无签发体系前的最小半径"（已知债），但 CORS `*` 使半径从"前端页面"扩大到"任意网页"——超出预设 | promotion_advisory.py:576-591; api_server.py:57, :4351-4375 | **P1**（已知债+CORS 放大，v1 无实盘执行面故非 P0） | `curl -X POST http://127.0.0.1:<port>/api/promotion-decide -H "Content-Type: application/json" -d '{"advisory_id":"<id>","decision":"approve"}'` 在无任何凭据下返回 ok 与否 |
| A | **"连续 2 月"文档语义 vs "累计计数"实现口径**：`_decide_recommendation` 用累计 pass/breach 月数（promotion_advisory.py:383-387），:380 自述"规则真源=SOP-C §8 连续 2 月门槛"——breach≥2 累计判定比"连续 breach≥2"更激进（两次分散破口也降档）；promote 侧 breach==0 全绿反而更严。两方向不对称的口径漂移（checklist #1 同族） | promotion_advisory.py:378-387, :143-149 | **P2** | 造 months=[pass,breach,pass,breach] 判 demote；连续口径应 hold |
| A | PA-1 三条件实据链完整：双窗行在位/fdr_keep 名单在册/衰减台账无未决——**缺证据=不通过**且失败不写 decision 墓碑（可补证重试），每条件 {ok,reason,source} 三件套留痕（:341-375, :702-708）——治本兑现，机器自签通道已封 | promotion_advisory.py:292-338, :636-643 | 已查无（正面） | tests:278/313 |
| A | `_match_bothwin` 以 source_file **basename** 匹配双窗行（:267-275）——不同目录同名文件的两策略可互认对方双窗行（假放行向）；aliases 互认为第二路。当前翻译件命名唯一性靠约定 | promotion_advisory.py:261-275 | P3 | 同 basename 两条目构造 items 观察 cross-match |
| A | `_cond_bh_fdr` 回退键构造 `f"{CAND-*}@{首锚点}"`（:310-313）——与 intake fdr_keep 键格式的一致性依赖命名约定；不匹配=判不了不放行（fail-closed 向安全） | promotion_advisory.py:307-321 | 已查无（fail-closed） | — |
| A.3 | 15 用例覆盖 token 三态（服务端自取/显式对错/未配置 fail-closed）/kill_switch 拒绝/demote 流转/台账墓碑幂等/证据降级——主链信任；"累计 vs 连续"与中途失败死态无测 | test_promotion_advisory.py:200-396 | P3 | 补两用例 |
| B | 上游四路证据任一缺失=该路降级不抛（gov/dev/fw/memo，:116-183）；注册表读失败=空快照→lifecycle 校验拒绝（fail-closed）；fw 陈窗问题见 T05 P1-1（本件消费侧） | promotion_advisory.py:116-201 | 已查无（本件面） | — |
| C | 写链顺序=FSM 内存流转→注册表 CAS 手术→decision 台账：**台账写失败时注册表已改**→advisory 无墓碑+重试撞 invalid_lifecycle=死态（需手工修复目录） | promotion_advisory.py:693-726 | P3 | mock 台账写失败复演 |
| C | 注册表手术三重防护：文本级行定位（缩进感知 :501-513）+语义写前复核（yaml 比对仅两字段变化 :531-546）+safe_write_text CAS+写后磁盘复核（:561-570）——only-add 体系外的手术更新有完整护栏（**但语义复核用 assert，见缺陷 2**） | promotion_advisory.py:501-572 | 已查无（正面） | tests:344 |
| D | 建议词表双源（governance 映射+月度史兜底 :378-387）与 SOP-C §8 真源关系已声明；fw 组合级证据只披露不作 per-strategy 判据（:397-410）——"三路证据合流"实为两路判定+两路披露，命名与语义有落差 | promotion_advisory.py:390-412 | P3 | 读 _compose_advisory 判据面 |
| E | kill_switch 探针 fail-closed（:594-600）；token 明文零落盘（台账只存 sha256 前 12 位 :110-112, :718）；已决幂等墓碑（:678-679）；FSM 拒绝/非法转换原样上抛不吞（:651）——对抗面主链扎实 | promotion_advisory.py:594-600, :110-112, :678-679 | 已查无（正面） | — |
| E | demote 走 candidate→shelved 无守卫边**不造假凭据**（:644-647 注释明示"被晋升预授权卡住=反向 fail-open"）——降档风险收敛语义正确，与 T04 transition 表一致 | promotion_advisory.py:644-652 | 已查无（正面） | — |
| E | 建议包同日覆盖写 safe_write_text 无 expected sha（:437）——并发 builder 丢更新窗口；单写方（事件链）下实际关闭 | promotion_advisory.py:431-440 | P3 | 双线程同日 build |

## 3 SOTA 对照

1. **人工审批门数字化（立卡候选）**：四眼原则/审批链数字化要求"拍板动作绑定可认证身份"（业界 MRM 审批流：ValidMind SR 11-7 合规四支柱之 governance，2024，https://validmind.com/blog/sr-11-7-model-risk-management-compliance/；新版 SR 26-2 同要求，Federal Reserve，2026，https://www.federalreserve.gov/supervisionreg/srletters/SR2602.pdf）。本件"前端点击即授权+无 HTTP 认证"距离"身份可认证"有明确差距——立卡项：最小改造=decide 端点加会话/令牌认证或 bastion 白名单（与 api_server 域联合施工）。
2. **晋级评审证据包（对等已有）**：多路证据（策略级月度偏离+组合级回测+治理建议）合流供 Owner 决策与业界模型晋升评审包（model validation package）同构；"缺证据不放行"与 SR 26-2 的 evidence-first 口径一致。
3. 结论：证据合流**对等已有**；门位认证为立卡待改项（见缺陷 1）。

## 4 缺陷清单

1. **[P1] Owner 门认证半径=网络可达性（token=None 自取密钥×CORS `*`）**
   - 现状：decide 端点无 HTTP 认证、硬编码 token=None（api_server.py:4375）；_token_check 对 None 发放服务端密钥为有效凭据（promotion_advisory.py:585-586）；CORS 全放开（api_server.py:57）。
   - 证据：见 §2 E 首行锚点；docstring 自认"最小半径"已知债，但 CORS `*` + GET 列表无认证的组合超出"前端拍板"预设——任何 Owner 浏览器内网页可 drive-by 完成批准。
   - 影响：production 流转（宪法 §5 high 域 Owner 门位）可被非 Owner 触发；当前 v1 无实盘执行面（裁定#305 第 6 点）故非 P0，但晋升链真源状态可被污染。
   - 建议修法：①端点加认证（会话/反代 basic auth/本地令牌头）；②CORS 收紧同源；③或 decide 强制显式 token（前端存 secret 于服务端环境注入而非放行 None）。
   - 验证法：见 §2 E 首行 curl 命令（对测试环境执行）。
2. **[P2] "连续 2 月"真源语义 vs 累计计数实现**——证据 promotion_advisory.py:378-387；影响：分散双破口触发降档（若真源=连续则误杀）/全绿非连续月触发晋升（promote 侧因 breach==0 实际无害）；建议：与 SOP-C §8 对齐——连续窗口判定或修订注释为累计口径；验证法：造 [pass,breach,pass,breach] 月序列判 demote。
3. **[P2] 注册表手术语义复核用 `assert`**（:538-546）——`python -O` 下复核静默消失（CAS 仍在但"仅两字段变化"校验失效）；建议：改显式 raise（同 T02/intake 家族缺陷）；验证法：python -O 跑手术路径。
4. **[P3] decide 中途失败死态**（:693-726）——注册表已写、台账未写→重试撞 invalid_lifecycle 且无墓碑；建议：台账先写（墓碑含 pending 态）或失败补偿提示；验证法：mock 台账写失败。
5. **[P3] basename 匹配可跨策略误认双窗行**（:261-275）——建议：全相对路径匹配或 path+alias 双锚必中一；验证法：同名异径条目构造。
6. **[P3] fw 组合级证据不参与 promote 判据**（:390-412）——建议：至少 panel_ok=false 时降级为 hold 或注释明示"仅披露"；验证法：读判据面。
7. **[P3] 建议包覆盖写无 CAS**（:431-440）；验证法：并发 build。

## 5 挂起疑问

1. Owner 是否知悉并接受"无签发体系前的最小半径"为**当前生产态**？若是，建议在 risk_tier_registry 把 promotion-decide 端点登记为 high 域已知例外+加固期限。
2. SOP-C §8"连续 2 月"的真源原文口径（连续/累计）——决定缺陷 2 修法方向。
3. `_read_deviation_months` 的 ok 缺失行计 breach（fail-closed）——数据缺月与真实破月同罪，是否会系统性压低 promote 通过率（保守向误伤）？

## 6 完备性自评

- 六轴全查：是。A（月度口径/匹配锚点/键构造/阈值数学）、A.3（15 用例映射+两漏测点）、B（四路证据+注册表断供行为）、C（写链顺序死态+手术三重护栏）、D（词表双源+披露/判定落差）、E（drive-by/token 卫生/幂等/demote 不造假凭据五问）。
- 长尾：①api_server 投影层整体（P2 域，仅审了本端点调用面与 CORS 行）；②SCR-SIMGOV/SCR-DEV 档案生产者数学（判定台账域）；③alerter 通道内部降级行为。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
