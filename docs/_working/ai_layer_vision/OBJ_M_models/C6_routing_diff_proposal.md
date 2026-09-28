---
ttl: task_bound
title: C6 M4 路由表增轨 diff 提案（AI 层轨 8 条+free_window_pref；Owner 终批前置 OBJ_M-#1）
owner: ZephyrAlpha-Owner
session: st-ailayer-p1-20260923
date: 2026-09-23
status: landed_20260927
---

# C6 M4 路由表增轨 diff 提案

> **落地记录（2026-09-27）**：Owner 终批（12 项已批项之1）后 diff 原样落
> `config/model_routing_policy.yaml`（既有 12 轨零改动，api_providers 零增删，OBJ_M-#1 计费线
> 前置零触碰——8 轨全用既有通道在册模型）。落地会话=st-ailayer-sx-20260927。

> **性质**：diff 提案，零落地。`config/model_routing_policy.yaml` 是产线路由面
> （P1_construction_plan.md 批次红线："C6 触碰既有路由表=产线路由面，Owner 终批前零改动，
> 只出 diff 提案"）；OBJ_M-#1（README §3.5 真待 Owner 表）=api_providers 增删+免费窗合规终批，
> 唯 Owner 可解（计费线/订阅=Owner 独占四类事③②）。
> Owner 批文后本提案 diff 原样落 config/model_routing_policy.yaml（施工约 15 分钟）。

## 1. 现状基线（2026-09-23 HEAD 核对）

- `config/model_routing_policy.yaml`：12 任务轨（risk_veto→cross_validation）+period_rules
  （盘中 restricted）+static_mapping+fusion 权重+通道分桶
  （local_providers=["ollama","local"]；api_providers=["zhipu","deepseek","openai_azure","anthropic"]）。
- **既有 12 轨零改动**（提案不动任何既有行）。

## 2. 提案 diff（新增两段，追加于 task_routes 段之后）

### 2.1 新字段：free_window_pref（route_entry 级可选字段）

```yaml
# AI 层轨新增字段（OBJ_M DESIGN §5.2）：免费窗偏好（M2 free_window.active 双闸后才生效）
# free_window_pref: {enabled: bool, window: '<expr>', quota_guard: '<说明>'}
```

### 2.2 AI 层轨 8 条（逐条带 evidence_ref，DESIGN §5.3 映射表照录）

```yaml
  # ---- AI 层轨（OBJ_M M4 v0；evidence_ref 逐条反提依据；Owner 终批 OBJ_M-#1 后生效）----
  mining_broad:            # AI-1 挖矿广度扫（ economy 档：免费/最低价优先）
    preferred: zhipu:glm-4.5-free
    fallbacks: ["zhipu:qwen-flash", "deepseek:deepseek-chat"]
    free_window_pref: {enabled: true, window: '00:30-08:30 UTC+8', quota_guard: '免费配额尽/上下文超限→谷时付费档'}
    period_constraint: inherit
    evidence_ref: 'OBJ_M DESIGN §5.3+挖矿SOP §2 二维法+2026-09-17 通宵班夜间 Flash 免费实战'
  mining_deep:             # AI-2 深读复现（premium 档：数学密度/长上下文）
    preferred: deepseek:deepseek-reasoner
    fallbacks: ["anthropic:claude-sonnet", "local:qwen3:8b"]
    free_window_pref: {enabled: true, window: '00:30-08:30 UTC+8 谷时半价', quota_guard: '>128k 上下文→长上下文档'}
    period_constraint: inherit
    evidence_ref: 'OBJ_M DESIGN §5.3+挖矿 SOP 二维法"最强模型"轴'
  cleaning_rewrite:        # AI-3 清洗规格化（standard 档）
    preferred: deepseek:deepseek-chat
    fallbacks: ["zhipu:glm-4-plus"]
    free_window_pref: {enabled: true, window: '00:30-08:30 UTC+8 谷时半价', quota_guard: ''}
    period_constraint: inherit
    evidence_ref: 'OBJ_M DESIGN §5.3+主文档 §一 L2=API 强模型执行'
  review_judge:            # AI-4 审查裁判（premium 档；裁判独立性>省钱，不用免费窗）
    preferred: anthropic:claude-sonnet
    fallbacks: ["deepseek:deepseek-reasoner"]
    free_window_pref: {enabled: false, window: '', quota_guard: '同源互判禁止（MCE RISK-3.2）'}
    period_constraint: inherit
    evidence_ref: 'OBJ_M DESIGN §5.3+MCE RISK-3.2 裁判解耦'
  translation_registry:    # AI-5 翻译/登记（economy 档）
    preferred: zhipu:glm-4.5-free
    fallbacks: ["zhipu:qwen-flash"]
    free_window_pref: {enabled: true, window: '00:30-08:30 UTC+8', quota_guard: '术语表命中失败→升 standard 复核'}
    period_constraint: inherit
    evidence_ref: 'OBJ_M DESIGN §5.3+三层翻译 loader 现状'
  daily_report:            # AI-6 日报/通知（economy 档：牌价最低档）
    preferred: zhipu:qwen-flash
    fallbacks: ["zhipu:glm-4-flash"]
    free_window_pref: {enabled: true, window: '00:30-08:30 UTC+8', quota_guard: ''}
    period_constraint: inherit
    evidence_ref: 'OBJ_M DESIGN §5.3+model_pricing.yaml 最低价档'
  overseer_dispatch:       # AI-7 总包派工/任务书（premium 档：裁定先行铁律）
    preferred: deepseek:deepseek-reasoner
    fallbacks: ["anthropic:claude-sonnet"]
    free_window_pref: {enabled: false, window: '', quota_guard: '派工裁定需强模型'}
    period_constraint: inherit
    evidence_ref: 'OBJ_M DESIGN §5.3+总令模板实践'
  budget_analysis:         # AI-8 预算分析/报表（economy 档：本地优先成本 0）
    preferred: local:qwen3:8b
    fallbacks: ["zhipu:glm-4-flash"]
    free_window_pref: {enabled: true, window: '本地优先（成本 0）', quota_guard: 'Ollama 忙（llm_local 组互斥）→落免费档'}
    period_constraint: inherit
    evidence_ref: 'OBJ_M DESIGN §5.3+数据不出域+成本 0'
```

## 3. 合规自查（Owner 终批关注点）

1. **计费线**：8 条轨引用的模型全部已在 `config/model_pricing.yaml` 牌价表或 local 通道在册
   （glm-4.5-free=0/qwen-flash/deepseek-chat 等）；**不新增任何订阅/付费通道**，api_providers
   四前缀零改动——OBJ_M-#1 的"api_providers 增删"本提案=零增删。
2. **免费窗合规**：free_window_pref 只是"偏好"标记，路由执行器消费 M2 free_window.active
   双闸后才放行（DESIGN §5.3 尾注）；免费窗=各厂官方公开活动（DeepSeek OFF-PEAK/智谱免费档），
   非灰产渠道。
3. **盘中约束**：全部 inherit period_rules（盘中 restricted 沿用既有），AI 层轨不放松任何
   交易时段限制。
4. **验收预演**：既有 12 轨零改动（diff 只增不改）；router 加载测试与既有测试全绿=落地时跑
   `python -m pytest tests/ -k routing -q` 复核。

## 4. Owner 动作项

- [ ] OBJ_M-#1 终批：本 diff 8 条轨映射逐条点头/删改（批文后 ai_layer 车道落地，预计一次提交）。
- [ ] 若某轨免费窗合规有疑（如 review_judge 禁免费窗已内置 enabled:false），批文时点名。
