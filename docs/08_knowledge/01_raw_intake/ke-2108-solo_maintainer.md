---
module_id: KE-2017
status: active
title: 3. Solo Maintainer 特异性设计
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3. Solo Maintainer 特异性设计

3. Solo Maintainer 特异性设计

> **决策 D-024-10（v0.7.0 修订）**：系统面向"1人+AI维护"运行。v0.7.0 核心补丁：作为唯一的人类 Owner，你持有的 Ed25519 密钥是 **整个预算体系的信任根**——没有你的签名，任何 AI agent 都不能修改预算策略、解除熔断、或绕过 fail_mode。这是"一个人的治理委员会"。

```yaml
solo_maintainer_optimizations:

  zero_toil:
    self_learning_thresholds:
      description: "预算阈值不是人工调的——基于过去 30 天的消耗自动调整"
      update_frequency: "每周一自动计算新阈值"
      method: "30d P90 × 安全系数 1.3"
      manual_override: "config/budget_overrides.yaml（Owner 手动锁定时读取）"

    auto_silence_alerts:
      description: "同类超预算告警 1 小时内最多发 1 次"
      grouping_key: "{budget_level}_{event_type}"
      cooldown: 3600

    weekly_auto_summary:
      description: "每周自动生成自然语言摘要——Owner 不需要读 JSONL"
      output: "docs/_working/audit/cost_reports/weekly-{date}.md"
      language: "zh"
      sections:
        - "总览：本周花了多少、比上周多还是少"
        - "异常：哪些时刻触发了降级/熔断"
        - "归因：钱花在了哪里（Agent/Tool/Activity/Outcome Top 3）"
        - "ROI：效率变化趋势"
        - "预测：下周预计消耗"
        - "建议：需要 Owner 关注的配置变更建议"
        - "新模型：本周发现的新模型及其性价比评估（v0.4.0 新增）"

  affordability_first:
    free_model_preference:
      description: "能用 Trae CN 免费模型完成的就不调付费 API——v0.4.0 模型路由反转后此为默认行为"
      tier_0_first: true
      escalate_rule: "仅当 tier_0 返回质量不达标（通过 output_validator 检测）才升级到 tier_1"

    cost_cap_per_task:
      description: "每任务最高成本硬封顶"
      default: "$0.50/task"      # solo maintainer 可承受的单任务成本
      overridable: true

    # ── v0.4.0 新增：环境感知 ──
    env_awareness:
      profile: "$ZEPHYR_ENV"      # development | staging | production
      dev_safety: "development 环境自动锁定在 tier_0_free，防止调试时烧预算"
      auto_revert_to_dev: "每次 IDE 重启后自动重置为 development profile"

  weekly_rhythm:
    description: "每周 2-5 小时施工 → 周预算比日预算更合理"
    budget_granularity: "weekly"
    daily_only_alert: "单日超过周预算 40% 时提醒"

  one_person_maintenance:
    description: "v0.4.0 新增——1 人维护下最需要自动化的事情"
    new_model_notification: "新模型出现时自动通知——你不会主动关注模型市场"
    cost_anomaly_highlights: "每周摘要中高亮最值得关注的 3 个异常——不需要手动翻日志"
    one_click_rollback: "zephyr budget policy rollback——策略改错了可以一键回滚"
    sandbox_guard: "修改 budget_policy.yaml 后自动 dry-run——上线前就知道有没有问题"
    data_auto_cleanup: "成本日志自动归档过期——不需要手动清理磁盘"
```

---
