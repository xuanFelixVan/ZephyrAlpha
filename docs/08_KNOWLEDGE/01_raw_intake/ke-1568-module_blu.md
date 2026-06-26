---
module_id: KE-1478
title: 13.3 绝对禁止（反孤儿铁律）
category: module_blueprint
ttl: permanent
---

# 13.3 绝对禁止（反孤儿铁律）

13.3 绝对禁止（反孤儿铁律）

| # | 行为 | 后果 |
|---|------|------|
| ❌ | **创建盘点系统但不更新冷启动序列** | 新 AI session 不知道有这个功能 → 孤儿 |
| ❌ | **只注册到 module-registry 但不加到 Phase Manager** | 门禁不检查 → CI 永远 GREEN → 假门禁 |
| ❌ | **unified_asset_index.yaml 不包含自身条目** | 盘点系统自己成为孤儿 → 元盘点失败 |
| ❌ | **盘点脚本不在 script-manifest.yaml 中** | `run_all.py` 不会调用盘点扫描 → 运行时不可见 |

---
