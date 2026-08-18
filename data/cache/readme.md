---
blueprint_id: MOD-INF-005
ttl: permanent
doc_type: index
---

# data/cache/ — ZephyrAlpha Runtime Artifact Cache
#
# 此目录存储代码去重引擎运行时生成的缓存/报告文件。
# 文件名如 *_report.yaml / *_tracker.yaml / *_baseline.yaml 等
# 由对应的 Python 模块在运行时自动创建和更新。
# 手动创建无意义——请勿在此目录手工维护文件。
#
# 对应模块: MOD-INF-017 Code Dedup Engine
# 下游输出任务卡: TASK-INF-017-0008 ~ TASK-INF-017-0033
