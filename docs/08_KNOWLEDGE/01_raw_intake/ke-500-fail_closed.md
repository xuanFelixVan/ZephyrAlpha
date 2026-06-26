---
module_id: KE-449------fail-closed-000
status: active
title: 6.2 三道防线（fail-closed）
category: documentation
ttl: permanent
---

# 6.2 三道防线（fail-closed）

6.2 三道防线（fail-closed）

```
Dev-Time                     Commit-Time                  Runtime
─────────                    ───────────                  ────────
L1: .env + .gitignore   →   L2: git-secrets    →        L3: LSG Output Scanner
    开发时本地保存            pre-commit hook              AI 输出过滤
    [ 基础约束 ]              [ 阻止提交 ]                  [ 防 AI 生成密钥 ]

                                      │
                                      ▼
                              L2-CI: trufflehog           L3-Audit: Secret
                              Scan on PR                   Leak Weekly Scan
                              [ 追赶漏网 ]                 [ 历史库扫描 ]
```

**fail-closed 语义**：任何一道防线检测到潜在泄露 → 阻塞下游流程（commit rejected / CI failed / AI response dropped），**不允许"记录下来但继续"**。
