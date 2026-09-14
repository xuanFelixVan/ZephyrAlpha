---
blueprint_id: MOD-GOV-INDUSAGE
module_name: indicator_usage_audit
domain: D_GOV
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-09-15
last_updated: 2026-09-15
owner: ZephyrAlpha-Owner
---

# MOD-GOV-INDUSAGE indicator_usage_audit 蓝图

> 设计真源：生命周期协议 v2.0 三域落地。指标域=退化生命周期（正确性+消费活性，
> 不上统计闸——指标是变换不是信号）。

## 0. 定位
静态扫描仓库源码/配置对 technical_indicator_registry 全部 IND-* 的消费引用
（连字符/下划线双形式匹配；排除目录按相对扫描根 parts）→ 台账
active（消费者≥1）/ zero（零消费→退役建议）。退役建议供指标域会话消费。

## 1. 阈值与边界
无统计阈值（无预测力语义）。零消费≠必删——退役建议需指标域会话核实
（如桥接/动态引用场景）。扫描范围与排除目录注入可测（tmp_path）。
