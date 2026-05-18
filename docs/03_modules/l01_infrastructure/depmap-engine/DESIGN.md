# DepMap Engine 设计方案 v2.0

## 一、定位

DepMap Engine 是 ZephyrAlpha 的**核心基础设施**，替代现有 project-entity-depgraph.yaml 成为全项目依赖关系的**唯一真源（SSoT）**。

职责：AST扫描全项目文件依赖 → 精确解析到文件级 → 分层存储 → 违规检测 → 孤儿编目

只存**current状态**（实际扫描结果）。未来28域1500模块架构搬入时，current状态用于"填空"到新结构中。

## 二、存储结构

```
data/depmap/
├── _meta.yaml                    ← 元数据（版本/生成时间/统计摘要）~2KB
├── _package_graph.json           ← 包级依赖图 ~10KB，AI冷启动必读
├── _violation_report.json        ← 违规报告（B→C/双向/循环）~20KB
├── _orphan_catalog.json          ← 孤儿编目 ~200KB
├── packages/                     ← 按包拆分的文件级依赖
│   ├── _index.json               ← 包索引（哪个包在哪个文件里）
│   ├── shared.json               ← 每包5-50KB
│   ├── gates.json
│   └── ...（30+个文件）
└── adjacency/                    ← 全量邻接表
    ├── forward.json              ← 正向（A依赖谁）~200KB
    └── reverse.json              ← 反向（谁依赖A）~200KB
```

AI冷启动只读 _meta.yaml + _package_graph.json = ~12KB。

1500模块规模：packages/下约60个文件，每个10-100KB，总计<5MB，按需加载。

## 三、迁移方案

| 阶段 | 旧depgraph | DepMap Engine |
|------|-----------|--------------|
| Phase A 建成 | 保留，双写 | 新格式生成 |
| Phase B 迁移 | 停止更新 | 5个消费脚本改为读depmap |
| Phase C 清理 | 删除 | 唯一真源 |

旧depgraph相关文件清理清单：
- data/asset_index/project-entity-depgraph.yaml → 删除
- data/asset_index/dependency_graph.json → 删除
- data/asset_index/depgraph-diagnosis.yaml → 删除
- data/asset_index/cross_pkg_imports_scan.json → 删除
- data/asset_index/ground_truth_*.json → 删除
- docs/02_enterprise_architecture/system-dependency-map.md → 删除（信息在depmap中）
- docs/02_enterprise_architecture/target-architecture/architecture-model/layers/*.yaml → 删除（信息在depmap中）

## 四、蓝图

module_id: MOD-INF-040
位置: docs/03_modules/l01_infrastructure/depmap-engine/blueprint.md
优先级: P1

不变量：
- 每次文件变更后必须重新生成
- 0个unresolved内部import
- _package_graph.json <= 20KB
- 所有数据文件JSON格式（_meta.yaml除外）

核心脚本：
- scripts/governance/generate_depmap.py（主生成脚本）
- scripts/governance/scan_ground_truth_deps.py（AST扫描引擎）

## 五、AI冷启动集成

project_rules.md 新增：
| 进入新Session | 读 data/depmap/_meta.yaml + _package_graph.json | 不知道依赖结构 = 盲目施工 |
| 任何文件变更后 | python scripts/governance/generate_depmap.py | depmap过时 = 幻觉温床 |

冷启动序列新增 STEP 4.15 — DepMap 加载

门禁：G6_PT扩展为G6_DEPMAP，检查depmap新鲜度
