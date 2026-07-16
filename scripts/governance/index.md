---
blueprint_id: MOD-INF-005
ttl: task_bound
doc_type: index
---

# 审计脚本系统 — 快读索引

> **入口**：`scripts/governance/run_all.py`  |  **仪表盘**：`scripts/governance/status.py`  |  **报告**：`scripts/governance/reports/findings.jsonl`

## 一句话

`python scripts/governance/run_all.py` 跑全维度扫描（精确数量见 script_manifest.yaml），约 60 秒出报告。

## 常用命令

| 命令 | 用途 |
|------|------|
| `python scripts/governance/run_all.py` | 全维度扫描（阻断模式），生成 findings.jsonl |
| `python scripts/governance/run_all.py --warn-only` | 全维度扫描（非阻断模式），exit 0 |
| `python scripts/governance/run_all.py --list` | 列出所有注册脚本及维度映射 |
| `python scripts/governance/run_all.py --dry-run` | 预览维度覆盖（不执行脚本） |
| `python scripts/governance/run_all.py -d D6` | 只跑单个维度 |
| `python scripts/governance/status.py` | 健康仪表盘（脚本可执行性 + 严重度分布） |

## 脚本分布（12 维度）

> 精确脚本列表见 [script_manifest.yaml](script_manifest.yaml)（SSoT）。以下为维度结构概要：

<!-- TREE-AUTO-START -->
```
scripts/governance/
├── _shared/                        共用工具（5 文件）
├── d1_structure                   D1 结构完整性（22 脚本）
├── d2_links                       D2 链接完整性（3 脚本）
├── d3_metadata                    D3 元数据合规（23 脚本）
├── d4_paths                       D4 路径有效性（4 脚本）
├── d5_architecture                D5 架构合规（72 脚本）
├── d6_security                    D6 安全漏洞（13 脚本）
├── d7_code                        D7 代码质量（21 脚本）
├── d8_doc_sync                    D8 文档代码同步（4 脚本）
├── d9_knowledge                   D9 知识覆盖（2 脚本）
├── d10_performance                D10 性能容量（待建设）
├── d11_compliance                 D11 合规完整性（12 脚本）
├── d12_ai_hallucination           D12 AI 幻觉（4 脚本）
├── run_all.py                     全维度扫描入口
├── status.py                      健康仪表盘
├── check_registry_consistency.py  跨登记表一致性校验
├── script_manifest.yaml           脚本注册表（SSoT — 317 条目）
└── quality_standard.md            审计脚本质量标准
```
<!-- TREE-AUTO-END -->

## 维度覆盖率

<!-- COVERAGE-AUTO-START -->
```
已覆盖: ████████████████████████ 12/12 (100%)  [generated from manifest SSoT, auto-synced]
D1 结构完整性 ✓   D2 链接完整性 ✓   D3 元数据合规 ✓   D4 路径有效性 ✓
D5 架构合规 ✓   D6 安全漏洞 ✓   D7 代码质量 ✓   D8 文档代码同步 ✓
D9 知识覆盖 ✓   D10 性能容量 ✓   D11 合规完整性 ✓   D12 AI 幻觉 ✓
```
<!-- COVERAGE-AUTO-END -->

## Finding 严重度定义

| 严重度 | 含义 | 对 AI 行为的影响 |
|--------|------|----------------|
| CRITICAL | 安全红线或数据丢失 | 必须阻断，禁止继续 |
| HIGH | 明确违反 ABS 规则 | 修复后才能提交 |
| MEDIUM | COND 条件违规 | 排查后决定是否修复 |
| LOW | 信息提示 / 建议 | 参考，不阻塞 |

## AI 施工约定

1. **施工前**：跑 `run_all.py` 看当前基线
2. **施工中**：每改完一轮跑一次，确认没引入新问题
3. **施工后**：跑 `run_all.py` + `status.py` 确认最终状态，记入 Session Log
4. **发现 HIGH+ 违规**：先修再继续施工——不能带着红色告警写新代码
5. **创建新脚本工具**（AGENTS.md §6.5 — 入库强制约定）：

| 步骤 | 操作 | 验证方式 |
|:--:|------|------|
| A0 | **先查重复**：`python scripts/governance/run_all.py --list` 列出现有脚本 + 搜 `scripts/governance/` 下同名/类功能文件 | 确认无功能等价脚本；如有 → 扩展现有而非新建 |
| A | 脚本放入 `scripts/governance/{dimension}/`，命名 `validate_*` / `detect_*` / `audit_*` | 文件名匹配已有约定 |
| B | 在 `script_manifest.yaml` 添加注册条目（dimensions / priority / timeout / args / description） | YAML 语法有效 + dimensions 不为空 |
| C | 独立运行验证：`python scripts/governance/{dimension}/{script}.py --warn-only` | exit 0 + VS Code 诊断 0 |
| D | 全量回归：`python scripts/governance/run_all.py` | 新脚本出现在执行列表中 + 无新增异常 |

> **大白话**：做新脚本就像入库登记——A0 先看看图书馆有没有这本书 → A 放到正确书架 → B 填登记卡 → C 试运行 → D 全班验证。别重复买同一本书。
