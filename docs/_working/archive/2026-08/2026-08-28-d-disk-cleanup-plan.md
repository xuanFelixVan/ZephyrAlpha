---
ttl: task_bound
---

# D 盘空间清理方案（待执行）

> 创建：2026-08-28 ｜ 状态：**已批准，择期执行**（用户确认三项都做，但不是现在）
>
> **结案审查（2026-08-28 复核）**：状态属实、未执行——`models/qwen25-7b-base`（14.2GB）与 `qwen25-7b-sft-v1` 仍在 D 盘原位，`.git.backup.20260803` 仍存在；三项均待 Owner 择期窗口，执行后本篇可结案删除。
>
> 背景：D 盘空闲 77.7GB 偏紧。已否决"语料迁入 PG 压缩"方案——P1归一/P2语料在 E 盘（空闲 303GB），
> PG 数据目录在 C 盘（`C:/Program Files/PostgreSQL/16/data`），迁移对 D 盘零帮助，且 PDF 原件压不动。

## 预期收益合计：约 22 GB

| # | 项 | 释放空间 | 风险 |
|---|----|---------|------|
| 1 | `models/qwen25-7b-base` 移到 E 盘 | 14.2 GB | 低（无代码引用） |
| 2 | 删 `.git.backup.20260803`（或移 E 盘） | 6.3 GB | 低（需先验证当前 .git 健康） |
| 3 | 清 `tmp` 旧备份/日志 + `.echo-guard` | 1.5 GB | 中（tmp 有活动锁文件，需选择性清） |

## 执行步骤

### 1. models → E 盘（省 14.2 GB）

- 对象：`D:\ZephyrAlpha\models\qwen25-7b-base`（14.2GB）+ `qwen25-7b-sft-v1`（0.09GB）
- 已验证：全仓库 grep 无任何代码引用该路径（embedding 模型在 `data/models/local_model/`，不在此目录，**不要动**）
- 操作：
  ```powershell
  robocopy "D:\ZephyrAlpha\models" "E:\模型仓库\ZephyrAlpha-models" /E /MOVE /MT:8
  ```
- 移动后在未来需要使用 7B 模型的脚本中记录新路径（当前无引用，无需改代码）

### 2. 删 .git.backup.20260803（省 6.3 GB）

- 前置检查（必须通过）：
  ```powershell
  cd D:\ZephyrAlpha
  git fsck --full          # 当前 .git 完整无损
  git status               # 工作区状态正常
  ```
- 保险做法（推荐）：先移到 E 盘观察 1-2 周再删
  ```powershell
  robocopy "D:\ZephyrAlpha\.git.backup.20260803" "E:\备份\git.backup.20260803" /E /MOVE /MT:8
  ```
- 直接删除：确认 fsck 通过后 `Remove-Item -Recurse -Force .git.backup.20260803`

### 3. 清 tmp + .echo-guard（省 1.5 GB）

**tmp（0.79GB）——选择性清，勿整目录删：**
- 可删：`tmp\pg_backups`、`tmp\runtime_backups` 中除最新一份外的旧备份；
  `scheduler_run.log.1` ~ `.4` 等日志轮转；`tmp\data_gap_check` 旧产物
- **禁止删**：`*.heartbeat`、`*.lock`（scheduler/ch_health_probe 活动中的心跳与锁）、
  `scheduler_run.log`（当前日志）、`.gitkeep`

**.echo-guard（0.72GB）——注意会重建：**
- 内容是 echo-guard 的向量索引（`embeddings.npy` + `index.duckdb`）
- 删除后下次 rescan 会自动重建，**重建后仍占 D 盘**，除非先把 echo-guard 索引路径配置改到 E 盘
- 执行顺序：先查 echo-guard 是否支持索引路径配置 → 支持则改 E 盘后删；不支持则跳过本项（省了也会回来）

## 附带决议

- RAG 索引（`E:\数据下载\产业链数据_P2语料\chunks.sqlite` + `embeddings.npy`）**留在 E 盘**，
  取消原"索引移到 D 盘"计划，rag_build_index.py / rag_query.py 路径无需改动
- E 盘 `产业链数据_P1归一`（2.81GB）与 `_P2语料`（0.35GB）保留现状——E 盘空间充裕，
  且 P1归一是 PDF 原件唯一副本（E:\数据下载 源压缩包删除前的兜底）

## 执行后验证

```powershell
Get-PSDrive D | Select-Object Used,Free   # 空闲应 ≥ 99 GB
git -C D:\ZephyrAlpha status              # 仓库正常
python scripts/industry_graph/rag_query.py --help  # RAG 路径未受影响
```
