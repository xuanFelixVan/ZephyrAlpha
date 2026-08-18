---
module_id: MOD-INF-045
submodule_path: scripts/ops/download_models.py
title: "嵌入模型下载器蓝图 — HuggingFace模型按需下载，永不入库，YAML动态加载(SSoT)"
doc_type: blueprint
template_for: blueprint
status: Active
version: "1.0.1"
layer: L0_infrastructure
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-08-03"
ttl: permanent
design_maturity: production
actual_disk_path: "scripts/ops/download_models.py"
last_updated: "2026-08-03"
last_verified: "2026-08-03"
generation: 1
functional_domain: operations
summary: "嵌入模型文件下载器（ARCH-MODEL-LIFECYCLE-001 Phase 3）——从HuggingFace Hub下载嵌入模型到data/models/local_model/（git-ignored永不入库）。模型清单SSoT=config/embedding_model_registry.yaml，脚本启动时动态加载、零硬编码，新增/移除模型只改YAML。CLI支持--list/--verify/--dry-run/--force/--model，覆盖3个需手动下载模型（bge-m3 2.2GB/bge-small-zh 92MB/paraphrase-multilingual-MiniLM-L12-v2 465MB）。"
tags: [model-download, huggingface, embedding-model, lifecycle, ssoT, gitignore, arch-model-lifecycle]
priority: P2
belongs_to: MOD-MASTER_BLUEPRINT
parent_module: ""
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
depends_on:
  - target: MOD-INF-002
    at: "§models"
    why: "模型注册表YAML真源——download_models.py启动时从config/embedding_model_registry.yaml动态加载模型清单(name/hf_repo_id/local_path/file_size_mb/required_files)"
references:
  - "ARCH-MODEL-LIFECYCLE-001（三阶段治本：filter-repo清历史→gitignore排除→本脚本获取）"
  - "AGENTS.md §6.1 data/models/ 目录生命周期"
codification_level: L2
codification_at: "2026-08-03"
responsibility_domain: 
build_status: generated
design_maturity: production
---
> module_id: MOD-INF-045 | version: 1.0.1 | status: active | layer: L0_infrastructure

## 1. 定位与痛点

**解决痛点**：嵌入模型文件（bge-m3 2.2GB 等）体积巨大，入库会导致仓库膨胀、Trae 索引 OOM、克隆缓慢。历史教训：bge-m3 曾入库（含 LFS），Phase 1 已用 `git filter-repo` 从全部分支历史清除。

**定位**：模型文件**永不入库**（`.gitignore` 排除 `data/models/`），本脚本提供唯一获取途径——按需从 HuggingFace Hub 下载到本地 `data/models/local_model/`。

## 2. 三阶段治本（ARCH-MODEL-LIFECYCLE-001）

| Phase | 动作 | 状态 |
|---|---|---|
| Phase 1 | `git filter-repo` 从 git 历史移除大模型对象（bge-m3 2.2GB） | ✅ 完成 |
| Phase 2 | `.gitignore` 排除 `data/models/` + `.gitattributes` 移除全部 LFS 死规则 | ✅ 完成 |
| Phase 3 | 本脚本提供模型获取途径（永不入库，按需下载） | ✅ 完成（本模块） |

## 3. SSoT 机制（P2 治本，零硬编码）

**真源**：`config/embedding_model_registry.yaml`（MOD-INF-002）是模型清单的唯一真源。

**动态加载**：脚本启动时调 `_load_models_from_registry()` 从 YAML 读取，过滤出 `local_path` + `hf_repo_id` 均存在的模型（需手动下载），构建 `MODELS` 列表。脚本内**零硬编码**模型数据——新增/移除模型只需改 YAML，无需同步脚本，消除多真源漂移。

**自动下载模型**：无 `local_path` 的模型（all-MiniLM-L6-v2、text2vec-base-chinese）由 sentence-transformers 首次使用时自动下载，不经本脚本。

## 4. CLI 接口

```
python scripts/ops/download_models.py              # 下载所有缺失模型
python scripts/ops/download_models.py --force       # 强制重新下载
python scripts/ops/download_models.py --model bge-m3 # 单模型
python scripts/ops/download_models.py --list        # 列出状态
python scripts/ops/download_models.py --verify      # 验证完整性
python scripts/ops/download_models.py --dry-run     # 预览（不下载）
```

## 5. 不变量（INVARIANTS）

- **INV-1**：模型文件永不入库（`.gitignore` 的 `data/models/` 规则保证）
- **INV-2**：MODELS 从 YAML 动态加载，禁止硬编码模型清单（SSoT 唯一）
- **INV-3**：下载后必须验证（required_files 存在 + 大小合理 >50% 预期）
- **INV-4**：`.gitignore`/`.gitattributes` 修改须经 ARCH-MODEL-LIFECYCLE-001 流程（IRN-010 受保护路径）

## 6. 依赖

| 依赖 | 类型 | 用途 |
|---|---|---|
| `config/embedding_model_registry.yaml` (MOD-INF-002) | 数据真源 | 模型清单（name/hf_repo_id/local_path/file_size_mb/required_files） |
| `huggingface_hub` | Python 库 | `snapshot_download()` 下载模型 |
| `PyYAML` | Python 库 | 解析 YAML 注册表 |

## 7. 错误契约（ERROR_CONTRACT）

| 场景 | 退出码 | 处理 |
|---|---|---|
| YAML 注册表缺失 | exit 2 | 提示 SSoT 文件路径 |
| PyYAML 未安装 | exit 2 | 提示 pip install pyyaml |
| huggingface_hub 未安装 | exit 1 | 提示安装（sentence-transformers 传递依赖） |
| 下载失败 | exit 1 | 提示网络/代理/Token 排查 |
| 验证失败（文件缺失/大小异常） | exit 1 | 提示 --force 重下 |
| 全部成功 | exit 0 | — |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-INF-045`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-INF-045` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-INF-045` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-INF-045 | MOD-INF-045 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | generated | ✅ |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 8.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §8（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
