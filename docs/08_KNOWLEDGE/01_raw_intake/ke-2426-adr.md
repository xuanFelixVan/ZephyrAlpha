---
module_id: KE-2331---------adr-006
title: 6. 关键架构决策（ADR 级）
category: module_blueprint
---

# 6. 关键架构决策（ADR 级）

6. 关键架构决策（ADR 级）

| 决策 ID | 决策 | 依据 |
|---------|------|------|
| **D-026-01** | 四维分类（type/layer/status/priority） | ITIL ITAM 实践——多维交叉定位优于单维 |
| **D-026-02** | 全量发现 = 文件系统递归扫描 + ThreadPoolExecutor | 无外部依赖，Windows 兼容，RULE-SEVEN 合规 |
| **D-026-03** | 分类引擎 = 纯规则驱动，禁止 LLM | AI 判断不可复现——确定性 > 灵活性 |
| **D-026-04** | `unified_asset_index.yaml` = SSoT | YAML 可 Git diff + AI 零推理消费 + 人类可读——优于 SQLite |
| **D-026-05** | ORPHAN 自动修复仅限 .py 文件（scaffold 可处理），.md 需人工 | scaffold.py 无法判定 .md 应归入哪个模块目录 |
| **D-026-06** | 状态机 7 态 + 每次迁移触发审计 | MOD-INF-020 已有完整审计骨架——只消费不新建 |
| **D-026-07** | 盘点数据只存元数据不存内容——SHA256 为唯一内容指纹 | 安全性 + 存储效率——600 个 45MB 代码库的 SHA256 清单 < 100KB |
| **D-026-08** | 全量扫描 1 次/小时，增量对账实时（事件驱动） | 平衡新鲜度与资源消耗——10+ AI 并发写文件不宜扫描太频繁 |
| **D-026-09** | 五阶自举——从裸盘恢复完整索引 | Linux initramfs 哲学——最小可启动集 + 逐阶重建 |
| **D-026-10** | 乐观扫描 + Glide Window + 原子写入 | MVCC 无锁哲学——AI session 不应为盘点系统等待 |
| **D-026-11** | 注册表适配器模式（ABC + 7 格式） | ETL 管道——异构数据源统一为 `list[RegistryEntry]` |
| **D-026-12** | ast 提取依赖图 + 环路检测 | HRT Tangle Tools 经验——在 100 万行代码上验证过的方案 |
| **D-026-13** | CircuitBreaker + 6 组件退化矩阵 | Netflix Hystrix——熔断后快速失败，60s 自动恢复 |
| **D-026-14** | 六不得铁律——安全扫描边界 | 最小权限 + 防御性编程——不读取 .env / .ailocks / session-logs |
| **D-026-15** | MCP Server: 6 tool + 2 resource | IDE 内直接查询资产——AI agent 不需要离开 IDE |
| **D-026-16** | TIME-DECAY / ZERO-REF / DIR-CONVENTION | ITIL 自动化退役规则——从 active 到 archived 全自动 |
| **D-026-17** | 多 IDE 规则文件映射（5 IDE） | Trae .trae/rules/ + Cursor .cursor/rules/ + Claude CLAUDE.md |
| **D-026-18** | Git log/blame → GitAssetMetadata | CodePulse/GitPrime——代码考古学，第四维资产信息 |
| **D-026-19** | TripleTrustAnchorGate（Git+pytest+Audit） | TUF 信任根——3/3=FULL, 2/3=PARTIAL, ≤1/3=BROKEN |
| **D-026-20** | InventorySelfMetrics + 告警阈值 | OpenTelemetry 三支柱（Metrics/Traces/Logs） |
| **D-026-21** | Emergency Bypass + 自动过期 24h | IAM Break Glass——Owner 手动创建文件即可跳过所有 Gate |
| **D-026-22** | 6 产物保留策略 + 自动清理脚本 | Prometheus TSDB retention + S3 lifecycle——每个产物都有 TTL |
| **D-026-23** | KnowledgeTransferGate + 六种跨 session 知识 | Anthropic Artifact + LangChain Memory——index 文件 = 跨对话记忆 |
| **D-026-24** | CLI: `python -m zephyr.asset_inventory` 7 子命令 | kubectl 子命令模式——scan/classify/reconcile/dashboard/check/bootstrap/clean |
| **D-026-25** | 配置集中: `config/capacity/asset-inventory.yaml` | pyproject.toml 的工具配置节——scanner/classifier/reconciler 全套可配置 |
| **D-026-26** | Dry-run/P Preview 模式——Safe-by-Default | Terraform plan vs apply——所有变更操作默认预览，明确传 --apply 才执行 |
| **D-026-27** | Schema Evolution: AUTOMIGRATE + 迁移脚本 | Flyway/Liquibase——schema_version 递增 + 逐版本迁移脚本 |
| **D-026-28** | RenameDetector: SHA256 交叉匹配 Ghost vs Orphan | Git diff --find-renames——SHA256 一致 + mtime 接近 = 高置信度 RENAME |
| **D-026-29** | 三层通知: Passive/Semi-Active/Blocking | PagerDuty 告警分级——P3/P2 下次 session 见，P1/P0 立即阻断 CI |
| **D-026-30** | tags + custom_metadata 扩展四维分类 | AWS Tags + K8s Labels/Annotations——Owner 可自定义语义标签 |
| **D-026-31** | Blueprint Self-Asset Registration: 蓝图自身登记到 index | RULE-TWO 自我指涉——盘点系统通过盘点自己来证明自己存在 |
| **D-026-32** | 
