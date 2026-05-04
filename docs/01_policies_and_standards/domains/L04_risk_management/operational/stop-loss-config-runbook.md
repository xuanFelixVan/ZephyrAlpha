---
module_id: DOM-L04-002
title: 止损配置操作手册
doc_type: operational_rule
status: draft
version: "0.1.0"
layer: l04_risk_management
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-01"
ttl: permanent
summary: "定义配置止损规则的完整操作步骤——参数验证、回测确认、上线监控。"
depends_on:
  - {target: DOM-L04-001, at: "§2", why: "风控限额策略——止损配置执行其限额标准"}
tags: [risk_management, operational, stop_loss]
rule_form: procedural
scope: domain
stability: evolving
verifiability: manual
ai_autonomy: human_gated
---

# 止损配置操作手册

> module_id: DOM-L04-002 | version: 0.1.0 | status: draft | layer: l04_risk_management

---

## 1. 目的

本手册定义配置止损规则的完整操作步骤。

## 2. 操作步骤

### Step 1：确认策略信息

1. 确认策略 ID 和策略类型
2. 确认策略当前持仓和敞口
3. 确认策略历史最大回撤

### Step 2：设置止损参数

1. 参照 DOM-L04-001 §2 设置止损限额
2. 在 `risk-config.yaml` 中配置止损参数：

```yaml
strategy_id: {STRATEGY_ID}
stop_loss:
  max_drawdown: 0.05          # 策略最大回撤（亏损 ≤ 5%）
  hard_stop: 0.08             # 硬止损线（亏损 ≤ 8%）
  trailing_stop: 0.03         # 追踪止损（从最高点回落 ≤ 3%）
  time_stop:                  # 时间止损（可选，持仓时间限制）
    max_hold_days: 30
  position_limit: 0.05        # 单标的最大仓位
  sector_limit: 0.20          # 单行业最大敞口
  net_exposure_limit: 0.30    # 多空净敞口限制
  kill_switch:
    global_drawdown: 0.02     # 全局回撤触发 kill switch
    consecutive_triggers: 3   # 连续触发 3 次止损 → kill switch
```

### Step 3：参数验证

1. 验证止损参数不超过 DOM-L04-001 §2 规定的阈值
2. 验证止损触发动作可执行（减仓/清仓/ kill switch）
3. 验证止损计算逻辑正确
4. **边界值防御检查**：
   - 如 max_drawdown = 0（不设止损）→ **拒绝**，必须设置止损（DOM-L04-001 ABS-001）
   - 如 max_drawdown = 1.0（亏损 100% 才触发）→ **拒绝**，止损无实际意义
   - 如 hard_stop ≤ trailing_stop → **拒绝**，追踪止损不能严于硬止损
5. 边界检查不通过 → 返回 Step 2

### Step 3.5：确认 Kill Switch 配置

根据 DOM-L04-001 §4，必须确认 Kill Switch 参数已正确配置：

1. 全局回撤触发线（默认 2%，参见 DOM-L04-001 ABS-001）
2. 连续止损触发次数上限（默认 3 次 → 触发 kill switch）
3. Kill Switch 触发后的恢复流程（需要 Owner 手动解除）
4. 确认 kill switch 与交易所接口联通（下单阻塞 + 平仓指令可送达）

### Step 4：回测确认

1. 使用历史数据模拟止损触发场景
2. 确认止损动作在预期时间点触发
3. 确认止损后持仓符合预期
4. 如有异常：调整参数，返回 Step 2

### Step 5：上线监控

1. 在 dev 环境运行 5 个交易日
2. 监控止损触发事件
3. 确认无误触发
4. Owner 审批后切换到 prod 环境

## 3. 验证清单

| # | 检查项 | 通过条件 |
|---|--------|---------|
| 1 | 止损参数在限额范围内 | 参见 DOM-L04-001 §2 |
| 2 | 止损触发动作可执行 | 模拟测试通过 |
| 3 | 回测无异常 | 止损在预期时间点触发 |
| 4 | dev 环境无误触发 | 5 个交易日无异常 |

## 4. 回滚方案

如果止损配置异常：

1. 立即恢复为默认止损参数
2. 通知 Owner：Kill Switch 已激活，风控系统已介入

## 5. AI自治权限标注

| 步骤 | 操作内容 | AI权限 | 说明 |
|------|---------|:------:|------|
| Step 1 | 确定止损策略类型（固定/移动/时间/组合） | ⚠️ 需确认 | AI 展示策略选项，Owner 选择 |
| Step 2 | 生成 `trailing_stop` / `time_stop` YAML 配置 | ✅ 可自动 | 根据 Owner 指定的参数生成配置 |
| Step 2.5 | 边界值防御（参数合法性检查 + 防御性默认值） | ✅ 可自动 | 自动校验并添加防御层 |
| Step 3 | 部署配置 + 沙箱环境执行风控回放 | ⚠️ 需确认 | AI 部署到 staging，执行回放，结果由 Owner 确认 |
| Step 3.5 | Kill Switch 配置（极端回撤触发条件 + 动作） | ⚠️ 需确认 | AI 生成配置，Owner 确认触发阈值 |
| Step 4 | 上线监控 — 确认监控就绪 + 告警通道配置 | ⚠️ 需确认 | AI 配置监控，Owner 确认上线 |
| §3 验证清单 | 逐项执行验证清单 | ⚠️ 需确认 | AI 逐项检查并输出结果，Owner 最终确认 |
| §4 回滚方案 | 还原配置 + 通知风控系统 | ❌ 禁止自动 | 涉及生产风控配置，必须 Owner 手动执行 |

## 6. TTL与生命周期

- **有效期**：版本 0.1.0 有效期至 2026-07-30
- **失效条件**：(1) 风控限额策略发生重大变更，(2) 风控引擎升级导致配置格式不兼容，(3) 新增止损策略类型需要新步骤
- **过期后动作**：本文件标记 `status: deprecated` + `superseded_by` 指向新版，旧版保留 90 天后归档
- **审查触发**：每次创建新止损配置时→审查本文件步骤是否仍适用；每 60 天→例行有效期审查；止损事件触发后→回溯审查操作流程是否有遗漏

## 7. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 0.1.0 | 2026-04-30 | 初始草案——创建止损配置流程，含 5 个 Step + 验证清单 + 回滚方案 |
| 0.1.1 | 2026-05-01 | 元规则合规对齐。(1) frontmatter 补 `ai_autonomy`。(2) 补齐 PS-STD-002 L3 模板缺失章节：§5 AI自治权限标注、§6 TTL与生命周期、§7 变更记录 |
