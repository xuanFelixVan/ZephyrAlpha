---
module_id: KE-309------gov-sec-001--3-000
title: 4.1 密钥泄露（GOV-SEC-001 §3）
category: documentation
ttl: permanent
---

# 4.1 密钥泄露（GOV-SEC-001 §3）

4.1 密钥泄露（GOV-SEC-001 §3）

| Step | 操作 | 验证 |
|------|------|------|
| 1 | 立即停止当前 session 所有文件操作 | 无新文件写入 |
| 2 | 触发 kill switch（PS-STD-003 ABS-47） | 交易已停止 |
| 3 | 执行密钥泄露响应：撤销→生成新密钥→搜索残留→通知→记录→复盘 | 新密钥已生效，无残留 |
| 4 | 通知 Owner（GOV-SEC-003 COND-001） | Owner 已知悉 |
