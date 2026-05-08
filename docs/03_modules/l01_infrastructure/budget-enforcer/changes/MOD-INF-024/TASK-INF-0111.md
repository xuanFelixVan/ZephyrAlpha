---
task_id: "TASK-INF-0111"
module_id: "MOD-INF-024"
title: "Pricing Sync — LiteLLM 价格同步 + New Model Discovery + Token Normalization + Long Context Pricing（§2.11）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P1
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: experimental
blueprint_section: "§2.11"
estimated_tokens: 4500
estimated_time_minutes: 120
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\pricing_sync.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\.audit_cache\\model_pricing_cache.json"
acceptance_criteria:
  - "AC-01: PricingSync 每日 02:00 UTC 从 LiteLLM model_prices_and_context_window.json 拉取最新定价"
  - "AC-02: fallback 使用本地缓存的上一次成功同步数据——sync 失败不中断系统"
  - "AC-03: 连续 3 天同步失败 → 通知 Owner"
  - "AC-04: New Model Discovery——sync 检测到本地缓存中不存在的 model_id → 三步评估（拉取能力画像/计算成本排名/生成评估建议）"
  - "AC-05: auto_adopt=false——不自动替换，由 Owner 审阅后手动更新 budget_policy.yaml"
  - "AC-06: Token Normalization——四 Provider 归一化到 cl100k_base 等效 token 数（anthropic×1.05, google×0.92, deepseek×0.98）"
  - "AC-07: Long Context Pricing——Anthropic > 200K input 溢价 1.5×-2× 检测 + OpenAI 128K potential trap 监控"
  - "AC-08: 长上下文溢价自动纳入成本预估——Pre-flight 时检查 estimated_input_tokens 是否超过阈值"
  - "AC-09: 终端显示 '⚠ 长上下文溢价: +50% (320K > 200K 阈值)'"
  - "AC-10: 本地缓存路径 .audit_cache/model_pricing_cache.json，TTL 86400s"
  - "AC-11: 提供 get_model_pricing(model_id) → ModelPricing 精确查询接口"
  - "AC-12: 价格同步也同步定价策略（非仅价格数字）——检测 provider 的 pricing strategy 变更"
rollback_instructions: "删除 pricing_sync.py + .audit_cache/model_pricing_cache.json。系统回退到硬编码模型价格（budget_policy.yaml 中的 static_pricing 段）"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L670-L716 (§2.11 Pricing Sync)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [pricing-sync, litellm, model-discovery, token-normalization, long-context-pricing, experimental]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0111: Pricing Sync — 价格自动同步 + 新模型发现 + Token 归一化

## 1. 任务目标

实现模型价格自动同步系统——每日从 LiteLLM registry 拉取最新定价，发现新模型并评估性价比，归一化跨 Provider token 定义差异，感知长上下文隐藏定价陷阱。

## 2. 背景

蓝图 §2.11：模型价格是动态变化的——不能硬编码。LiteLLM 维护业界最完整的模型定价清单。v0.4.0 新增新模型自动发现、Token 计数归一化。v0.5.0 新增长上下文隐藏定价感知。

## 3. 实施步骤

### Step 1: PricingSync 核心
```python
class PricingSync:
    LITELLM_URL = "https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json"

    def __init__(self, cache_path: str):
        self.cache = PricingCache(cache_path)
        self.normalizer = TokenNormalizer()
        self.discoverer = NewModelDiscoverer()

    def sync(self) -> SyncResult:
        raw = self._fetch_from_litellm()
        normalized = self.normalizer.normalize_all(raw)
        discovered = self.discoverer.check_new(normalized, self.cache)
        self.cache.update(normalized)
        return SyncResult(normalized, discovered)
```

### Step 2: TokenNormalizer
```python
class TokenNormalizer:
    BASE_TOKENIZER = "cl100k_base"
    FACTORS = {
        "anthropic": 1.05,
        "google": 0.92,
        "deepseek": 0.98,
        "openai": 1.00,
    }
    def normalize(self, provider: str, tokens: int) -> int:
        return int(tokens * self.FACTORS.get(provider, 1.0))
```

### Step 3: NewModelDiscoverer
- 对比 sync 结果 vs 本地缓存
- 发现新 model_id → 三步评估（能力画像/成本排名/生成建议）
- auto_adopt=false → 输出到 Weekly Showback '新模型' 段

### Step 4: LongContextPricingDetector
- 已知陷阱：Anthropic > 200K input → 1.5×-2× price
- OpenAI 128K potential trap
- 同步时更新 pricing strategy（非仅价格数字）
- Pre-flight 检查 estimated_input_tokens 是否触达阈值

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/pricing_sync.py` | 新建 |
