---
module_id: KE-documentat-2_2_______56___yaml____vs-000
title: 2.2 模块级对齐（56 个 YAML 模块 vs 代码实现）
category: documentation
---

# 2.2 模块级对齐（56 个 YAML 模块 vs 代码实现）

2.2 模块级对齐（56 个 YAML 模块 vs 代码实现）

| 对齐状态 | 数量 | 占比 | 说明 |
|---------|------|------|------|
| 完全对齐 | 8 | 14% | L12 的 4 个子目录 + shared 的 contracts/ 和 runtime_plane_tag.py + 部分 C 轨占位 |
| 形态不一致 | 6 | 11% | YAML 预期子目录，代码为单文件 |
| 代码缺失（planned） | 42 | 75% | YAML 中 status: planned，属于"先设计后实现"预期状态 |

**形态不一致详情**（YAML 预期目录 vs 代码为单文件）：

| YAML 预期目录 | 代码实际文件 | 层 |
|---|---|---|
| `l00_data_source/connectors/` | `connectors.py` | L00 |
| `l00_data_source/normalizers/` | `normalizers.py` | L00 |
| `l00_data_source/storage/` | `storage.py` | L00 |
| `l00_data_source/quality/` | `quality.py` | L00 |
| `l01_infrastructure/config/` | `config.py` | L01 |
| `l04_risk_management/stop_loss/` | `stop_loss.py` | L04 |
