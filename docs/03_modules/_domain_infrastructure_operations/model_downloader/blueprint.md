---
module_id: MOD-INF-045
submodule_path: scripts/ops/download_models.py
title: "嵌入模型下载器蓝图 — HuggingFace模型按需下载，永不入库，YAML动态加载(SSoT)"
doc_type: blueprint
template_for: blueprint
status: Active
version: "1.0.0"
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
responsibility_domain: D_INFRA_OPS
build_status: generated
design_maturity: production
---
> module_id: MOD-INF-045 | version: 1.0.0 | status: active | layer: L0_infrastructure

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
