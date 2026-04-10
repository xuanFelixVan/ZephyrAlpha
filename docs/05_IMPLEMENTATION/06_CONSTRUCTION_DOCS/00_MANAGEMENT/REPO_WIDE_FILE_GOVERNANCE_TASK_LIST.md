---
module_id: REPO_WIDE_FILE_GOVERNANCE_TASK_LIST_001
version: 1.0.0
status: Active
created_date: 2026-04-10
last_updated: '2026-04-10'
owner: 文档负责人（可指定）
responsibility:
  - 全仓库已跟踪文件的清点、去重与索引可达性（与蓝图任务清单并列，不限于蓝图目录）
standard_type: 任务清单
applicable_scope: 本 Git 仓库；以 `git ls-files` 为权威清单来源
---

# 全仓库文件治理 — 任务清单（总图）

> **用途**：回答「是否要先扫全树再建任务清单」——**要先有基线清单与统计，再分波次治理**；本文件给出**口径、基线数字、可勾选波次**，避免无控制面的大扫除。  
> **与蓝图清单的关系**：与 [全库蓝图终稿任务清单](./BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md) **并列**；蓝图清单偏**终稿与施工门禁**，本清单偏**整仓文件体量、重复与导航**。  
> **权威 Playbook**：[孤儿与重复文档治理](./../../../09_AUDIT/STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md)、[仓库根治理](./REPO_ROOT_GOVERNANCE_PLAYBOOK.md)。

---

## 0. 是否要先做「全系统树状」扫描？

**需要。** 推荐顺序为：

1. **基线快照**：导出当前 **Git 已跟踪**路径全表（与协作真源一致）+ 按目录/扩展名聚合统计。  
2. **口径冻结**：定义何为「多余」、何为「重复」、何为「已索引」。  
3. **分波次执行**：先门禁与明显垃圾，再内容哈希重复，最后语义/功能重复（需 Owner 裁决）。

> **说明**：若「整个系统」指 **本机磁盘或操作系统级**，已超出单仓库职责，需在备份与合规策略下**另立项目**；本清单**默认仅覆盖本仓库**。

---

## 1. 基线快照（2026-04-10，可复跑更新）

| 指标 | 数值 | 备注 |
|------|------|------|
| **已跟踪文件总数** | **4369** | `git ls-files` 行数 |
| **Markdown** | 3176 | 体量最大，索引策略必须分层，避免「逐文件手打链接」 |
| **Python** | 736 | 含 `scripts/` 为主 |
| **JSON** | 314 | 含审计状态、配置片段等 |
| **`.diff` 跟踪文件** | 50 | 适合统一归档/剔除策略评审 |
| **`.bak2` / `.bak3` 等备份扩展名（已跟踪）** | 至少 2 | 见下文 P2，宜迁出主树或进 archive |
| **一级目录体量（已跟踪）** | `docs/` 3523，`scripts/` 670，`src/` 65 | 治理重心在 `docs/` 与 `scripts/` |

**深度 2 目录聚合（节选，文件数 Top）**

| 前缀 | 约文件数 |
|------|-----------|
| `docs/09_AUDIT` | 1012 |
| `docs/05_IMPLEMENTATION` | 880 |
| `docs/06_ARCHIVE` | 644 |
| `docs/01_FRAMEWORK` | 338 |
| `docs/02_FACTOR_LIBRARY` | 144 |
| `docs/08_HUMAN_AI_INTERFACE` | 107 |

**全量路径平面清单（可检索、可 diff）**  
路径：`docs/09_AUDIT/STATE/REPO_GIT_TRACKED_FILES_20260410.txt`  

> **注意**：若清单中出现带引号或 `\346` 这类八进制转义片段，通常表示 **Git 索引里记录了异常/转义形式的路径**（与正常 UTF-8 中文路径并存时尤需警惕）；处置见 **P2** 路径规范化。

**复跑导出命令（仓库根，PowerShell）**

```powershell
# 推荐用 Python 导出 UTF-8，避免 PowerShell 对部分路径的转义差异：
python -c "import subprocess; p=subprocess.check_output(['git','ls-files'],text=True); lines=sorted(p.splitlines()); open(r'docs/09_AUDIT/STATE/REPO_GIT_TRACKED_FILES_YYYYMMDD.txt','w',encoding='utf-8',newline='\n').write('\n'.join(lines)+'\n')"
```

**复跑统计命令（仓库根，PowerShell）**

```powershell
(git ls-files).Count
git ls-files | ForEach-Object { if ($_ -match '\.([^./\\]+)$') { $matches[1].ToLower() } else { '(noext)' } } | Group-Object | Sort-Object Count -Descending
```

---

## 2. 口径：何为「干净」「重复」「有索引」

### 2.1 「没有多余文件」

| 层级 | 含义 | 典型动作 |
|------|------|----------|
| **A. 门禁** | 无密钥、无本机绝对路径、无应忽略的大二进制误提交 | `.gitignore`、pre-commit、密钥扫描（可选） |
| **B. 结构垃圾** | 明确备份/中间产物（`.bak*`、部分 `.diff`）是否允许留在主树 | 归档目录或删除 |
| **C. 内容重复** | 相同或近似相同字节内容 | SHA256 分组，保留 canonical |
| **D. 功能重复** | 两套文档/脚本描述同一职责 | **仅 Owner/架构裁决**，不可自动化硬删 |

### 2.2 「每个文件都能迅速定位」

**目标不是**为 4369 个路径各维护一条人工索引行（不可持续）。**目标是**分层可达：

- **L1**：仓库根 `README.md`、`docs/INDEX.md`、建设文档 [`INDEX.md`](../INDEX.md)。  
- **L2**：各业务域 `INDEX.md`（仓库内已有大量分布，需治理**孤岛**与**上级链接**）。  
- **L3**：[`docs/SITEMAP.md`](../../../SITEMAP.md)、[`docs/System_Manifest.md`](../../../System_Manifest.md) 等**总账类**文档（职责以各文件前言为准）。  
- **L4（推荐）**：对 `scripts/`、`tools/` 等增加**生成型清单**（脚本扫描目录 → Markdown/JSON），与手写 INDEX **互补**。

---

## 3. 任务波次（勾选进度）

### P0 — 基线与自动化（本轮已部分完成）

- [x] 导出全量 `git ls-files` 平面清单至 `docs/09_AUDIT/STATE/`（见上文文件名）。  
- [x] 记录扩展名与目录聚合统计（见 §1）。  
- [ ] 约定**更新频率**（例如每次大版本或每季度）并写入 [项目办公室 README](./README.md) 或本文件版本记录。

### P1 — 重复与冗余（机器可做部分）

- [ ] **同名不同路径**：对 basename 碰撞做报表（脚本或 `git ls-files` 后处理），人工判 canonical。  
- [ ] **同内容**：对文本类做 SHA256 分组（可排除 `docs/06_ARCHIVE` 等只读归档区策略另定）。  
- [ ] 将结果与 [孤儿与重复 Playbook](../../../09_AUDIT/STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md) 对齐，**先归并再删**。

### P2 — 明显「多余」扩展名与审计衍生物

- [ ] 评审 **50** 个已跟踪 `.diff`：保留标准、迁 archive、或从跟踪中移除。  
- [ ] 评审 `.bak2` / `.bak3` 等：是否应仅存于 archive 或本地（不进 Git）。  
- [ ] 对 `review_materials_package` 等路径中异常引号/命名（Windows 下曾出现统计异常）做**路径规范化**（若仍存在）。

### P3 — 索引可达性（导航）

- [ ] 从 `docs/INDEX.md` 与 [`../INDEX.md`](../INDEX.md) 出发做**抽样反向检查**：随机/分层抽样未出现在任何 INDEX/SITEMAP 的 `docs/` 文件比例（目标：持续下降）。  
- [ ] `scripts/`：在 [scripts/README.md](../../../../scripts/README.md) 或生成清单中补齐**分类导航**（与脚本数量匹配）。  
- [ ] `src/`：在根 README 或 `src/` 下 INDEX 中保证模块入口**可跳转**。

### P4 — 与现有门禁脚本对齐

- [ ] 将本清单 P1～P3 的产出与现有 `scripts/verify_*`、`sentinel_l1_*` 等**能衔接的检查项**列成表（避免重复造轮子）。  
- [ ] 可选：新增「重复内容报表」脚本，输出到 `docs/09_AUDIT/STATE/`，CI 仅告警不阻断（先软后硬）。

---

## 4. 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-04-10 | 首版：基线统计、口径、P0～P4 波次；附全量路径导出文件 |

---

## 5. 推荐阅读入口

| 说明 | 路径 |
|------|------|
| 全量已跟踪路径清单 | [`docs/09_AUDIT/STATE/REPO_GIT_TRACKED_FILES_20260410.txt`](../../../09_AUDIT/STATE/REPO_GIT_TRACKED_FILES_20260410.txt) |
| 蓝图阶段任务（并列） | [BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md](./BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md) |
| 孤儿与重复治理 | [DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md](../../../09_AUDIT/STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md) |
