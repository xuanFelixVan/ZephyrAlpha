---
module_id: KE-2216
title: 4.1 盘点数据安全
category: module_blueprint
ttl: permanent
---

# 4.1 盘点数据安全

4.1 盘点数据安全

| 风险 | 缓解 |
|------|------|
| 盘点扫描读取敏感文件内容 | 扫描器**只读元数据**（path/size/mtime/SHA256），**不读文件内容**——SHA256 通过 `hashlib.sha256(open(path,'rb').read())` 计算但结果只存哈希 |
| 盘点数据库被 AI 篡改 | `unified_asset_index.yaml` 为 SSoT——YAML 文本可 Git diff。每次覆盖前做 `os.replace(tmp, target)` 原子替换（RULE-ONE） |
| 扫描器自身成为孤儿 | 扫描器代码在 `src/zephyr/asset-inventory/` 下——自身也被扫描和登记。元盘点（meta-inventory）——谁盘点盘点器？答案：下一级扫描 |
