---
module_id: KE-1638
title: 2. 技术选型表（真源锁定）
category: module_blueprint
ttl: permanent
---

# 2. 技术选型表（真源锁定）

2. 技术选型表（真源锁定）

| 组件 | 首选 | 备选 | 不推荐 | 选型理由 | 升级触发 | 相关 ADR |
|------|----------------|------|-------|---------|---------|----------|
| Prompt Injection 防护 | **System Prompt 隔离 + 输入分类 + Schema 验证** | 轻量规则引擎（补充） | 重型 NLP 分类器（误报 + 依赖重） | 确定性、可审计、零外部依赖 | bypass 率 > 5% | ADR-0020 |
| 输入分类 | **规则 + 来源标签（trusted/semi/untrusted）** | 轻量分类器 | 人工标注 | 规则足够应对前 80% 场景 | 规则漏报 > 10% | ADR-0020 |
| 输出 Schema | **Pydantic v2 + 严格模式（extra='forbid'）** | JSON Schema + jsonschema | 无 schema（危险） | 原生类型支持、错误消息友好 | - | ADR-0020 |
| 异常模式扫描 | **正则库 + 命名模式集（可扩展）** | 轻量 NER | 纯人工黑名单 | 可维护、高召回 | 攻击模式复杂化 | ADR-0020 |
| Secret 扫描（运行时） | **`detect-secrets` + 定制正则** | `trufflehog` | 字符串匹配 | Yelp 标准、精度高 | - | ADR-0020 |
| Secret 扫描（pre-commit） | **`git-secrets` + `detect-secrets`** | `gitleaks` | 无扫描 | 双工具互补 | - | ADR-0020 |
| 供应链扫描 | **`pip-audit` + `safety`** | Snyk | 无扫描 | 官方支持、开源 | 企业合规需要 | ADR-0020 |
| 策略存储 | **YAML 外置（热加载）** | SQLite | 硬编码 | 方便安全审计 / 红队调整 | - | ADR-0020 |
| 审计日志 | **结构化 JSON + 滚动归档** | syslog | 纯文本 | 易查询 + 机读 | SIEM 需要 | ADR-0020 |
| 进程内并发 | **`asyncio.Lock`** | - | `threading.Lock` | 项目全异步栈 | - | - |
| 跨进程并发 | **`filelock.FileLock`** | - | 全局单例 | pytest 并发 | - | - |

---
